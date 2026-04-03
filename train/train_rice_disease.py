"""
Train rice-only disease classifier (MobileNetV2 transfer learning).

Expected folder layout under --data_dir (one subfolder per class name):

  data/rice_disease/
    Rice___Brown_spot/   *.jpg, *.png, ...
    Rice___Leaf_blast/
    Rice___Neck_blast/
    Rice___healthy/

Class order is fixed by utils.rice_disease_config.RICE_DISEASE_CLASSES (not alphabetical).

Outputs:
  models/disease_model.h5   — weights compatible with routes/disease.py
  models/rice_disease_meta.json — class list and training metadata
"""
from __future__ import annotations

import argparse
import json
import os
import sys

# Project root = parent of train/
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from utils.rice_disease_config import RICE_DISEASE_CLASSES


def _build_model(num_classes: int):
    from tensorflow.keras.applications import MobileNetV2
    from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D
    from tensorflow.keras.models import Model

    base = MobileNetV2(
        weights="imagenet",
        include_top=False,
        input_shape=(224, 224, 3),
    )
    x = GlobalAveragePooling2D()(base.output)
    x = Dropout(0.3)(x)
    out = Dense(num_classes, activation="softmax")(x)
    model = Model(inputs=base.input, outputs=out)
    return model, base


def main():
    parser = argparse.ArgumentParser(description="Train rice disease MobileNetV2 model")
    parser.add_argument(
        "--data_dir",
        type=str,
        default=os.path.join(ROOT, "data", "rice_disease"),
        help="Directory with Rice___* class subfolders",
    )
    parser.add_argument("--epochs", type=int, default=25)
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--learning_rate", type=float, default=1e-4)
    parser.add_argument("--fine_tune_epochs", type=int, default=8)
    parser.add_argument("--fine_tune_lr", type=float, default=1e-5)
    parser.add_argument(
        "--weights_out",
        type=str,
        default=os.path.join(ROOT, "models", "disease_model.h5"),
    )
    args = parser.parse_args()

    data_dir = os.path.abspath(args.data_dir)
    if not os.path.isdir(data_dir):
        print(f"Data directory not found: {data_dir}")
        print("Create it and add subfolders:", ", ".join(RICE_DISEASE_CLASSES))
        sys.exit(1)

    import tensorflow as tf
    from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
    from tensorflow.keras.callbacks import EarlyStopping
    from tensorflow.keras.optimizers import Adam

    seed = 42
    val_split = 0.2

    train_ds = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        validation_split=val_split,
        subset="training",
        seed=seed,
        image_size=(224, 224),
        batch_size=args.batch_size,
        class_names=RICE_DISEASE_CLASSES,
    )
    val_ds = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        validation_split=val_split,
        subset="validation",
        seed=seed,
        image_size=(224, 224),
        batch_size=args.batch_size,
        class_names=RICE_DISEASE_CLASSES,
    )

    autotune = tf.data.AUTOTUNE
    train_ds = train_ds.map(
        lambda x, y: (preprocess_input(tf.cast(x, tf.float32)), y),
        num_parallel_calls=autotune,
    )
    val_ds = val_ds.map(
        lambda x, y: (preprocess_input(tf.cast(x, tf.float32)), y),
        num_parallel_calls=autotune,
    )
    train_ds = train_ds.cache().prefetch(autotune)
    val_ds = val_ds.cache().prefetch(autotune)

    num_classes = len(RICE_DISEASE_CLASSES)
    model, base_model = _build_model(num_classes)
    base_model.trainable = False

    model.compile(
        optimizer=Adam(learning_rate=args.learning_rate),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    os.makedirs(os.path.dirname(os.path.abspath(args.weights_out)), exist_ok=True)

    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=args.epochs,
        callbacks=[EarlyStopping(monitor="val_accuracy", patience=6, restore_best_weights=True)],
    )

    # Fine-tune last ~40 layers of MobileNetV2
    base_model.trainable = True
    fine_tune_at = len(base_model.layers) - 40
    for layer in base_model.layers[:fine_tune_at]:
        layer.trainable = False

    model.compile(
        optimizer=Adam(learning_rate=args.fine_tune_lr),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=args.fine_tune_epochs,
        callbacks=[
            EarlyStopping(monitor="val_accuracy", patience=4, restore_best_weights=True),
        ],
    )

    model.save_weights(args.weights_out)

    meta_path = os.path.join(os.path.dirname(os.path.abspath(args.weights_out)), "rice_disease_meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "classes": RICE_DISEASE_CLASSES,
                "data_dir": data_dir,
                "epochs": args.epochs,
                "fine_tune_epochs": args.fine_tune_epochs,
            },
            f,
            indent=2,
        )

    print("Saved weights to", args.weights_out)
    print("Metadata:", meta_path)


if __name__ == "__main__":
    main()
