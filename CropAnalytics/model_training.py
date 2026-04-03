"""
AI Model Training Module - Transfer Learning for Crop Health Classification
Uses MobileNetV2 for efficient mobile deployment
"""

import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import numpy as np
import json

class CropHealthModel:
    def __init__(self, num_classes=4, img_size=224):
        """
        Initialize the crop health classification model
        
        Args:
            num_classes: Number of crop health categories
            img_size: Input image size (224x224 for MobileNetV2)
        """
        self.num_classes = num_classes
        self.img_size = img_size
        self.model = None
        self.class_names = ['Healthy', 'Pest_Disease', 'Flood_Damage', 'Drought_Stress']
        
    def build_model(self):
        """Build the transfer learning model using MobileNetV2"""
        # Load pre-trained MobileNetV2 without top layers
        base_model = MobileNetV2(
            weights='imagenet',
            include_top=False,
            input_shape=(self.img_size, self.img_size, 3)
        )
        
        # Freeze base model layers
        base_model.trainable = False
        
        # Add custom classification head
        x = base_model.output
        x = GlobalAveragePooling2D()(x)
        x = Dense(256, activation='relu')(x)
        x = Dropout(0.5)(x)
        x = Dense(128, activation='relu')(x)
        x = Dropout(0.3)(x)
        predictions = Dense(self.num_classes, activation='softmax')(x)
        
        # Create final model
        self.model = Model(inputs=base_model.input, outputs=predictions)
        
        return self.model
    
    def compile_model(self, learning_rate=0.001):
        """Compile the model with optimizer and loss function"""
        self.model.compile(
            optimizer=Adam(learning_rate=learning_rate),
            loss='categorical_crossentropy',
            metrics=['accuracy', tf.keras.metrics.TopKCategoricalAccuracy(k=2, name='top_2_accuracy')]
        )
        
    def train(self, train_dir, val_dir, epochs=20, batch_size=32):
        """
        Train the model using data augmentation
        
        Args:
            train_dir: Directory containing training images organized by class
            val_dir: Directory containing validation images
            epochs: Number of training epochs
            batch_size: Batch size for training
        """
        # Data augmentation for training
        train_datagen = ImageDataGenerator(
            rescale=1./255,
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            horizontal_flip=True,
            zoom_range=0.2,
            fill_mode='nearest'
        )
        
        # Only rescaling for validation
        val_datagen = ImageDataGenerator(rescale=1./255)
        
        # Load training data
        train_generator = train_datagen.flow_from_directory(
            train_dir,
            target_size=(self.img_size, self.img_size),
            batch_size=batch_size,
            class_mode='categorical'
        )
        
        # Load validation data
        val_generator = val_datagen.flow_from_directory(
            val_dir,
            target_size=(self.img_size, self.img_size),
            batch_size=batch_size,
            class_mode='categorical'
        )
        
        # Save class names
        self.class_names = list(train_generator.class_indices.keys())
        
        # Callbacks
        callbacks = [
            EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True),
            ModelCheckpoint('best_crop_model.h5', monitor='val_accuracy', save_best_only=True)
        ]
        
        # Train the model
        history = self.model.fit(
            train_generator,
            epochs=epochs,
            validation_data=val_generator,
            callbacks=callbacks
        )
        
        return history
    
    def fine_tune(self, train_dir, val_dir, epochs=10, batch_size=32):
        """
        Fine-tune the model by unfreezing top layers of base model
        """
        # Unfreeze top layers
        base_model = self.model.layers[0]
        base_model.trainable = True
        
        # Freeze all layers except the last 20
        for layer in base_model.layers[:-20]:
            layer.trainable = False
        
        # Recompile with lower learning rate
        self.compile_model(learning_rate=0.0001)
        
        # Continue training
        return self.train(train_dir, val_dir, epochs, batch_size)
    
    def save_model(self, filepath='crop_health_model.h5'):
        """Save the trained model"""
        self.model.save(filepath)
        
        # Save class names
        with open('class_names.json', 'w') as f:
            json.dump(self.class_names, f)
        
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath='crop_health_model.h5'):
        """Load a trained model"""
        self.model = tf.keras.models.load_model(filepath)
        
        # Load class names
        try:
            with open('class_names.json', 'r') as f:
                self.class_names = json.load(f)
        except FileNotFoundError:
            print("Warning: class_names.json not found, using default class names")
        
        print(f"Model loaded from {filepath}")
    
    def predict(self, image_array):
        """
        Make prediction on a single image
        
        Args:
            image_array: Preprocessed image array (224, 224, 3)
        
        Returns:
            dict: Prediction results with class and confidence
        """
        # Ensure correct shape
        if len(image_array.shape) == 3:
            image_array = np.expand_dims(image_array, axis=0)
        
        # Make prediction
        predictions = self.model.predict(image_array, verbose=0)
        predicted_class_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_class_idx])
        
        # Get top 3 predictions
        top_3_idx = np.argsort(predictions[0])[-3:][::-1]
        top_3_predictions = [
            {
                'class': self.class_names[idx],
                'confidence': float(predictions[0][idx])
            }
            for idx in top_3_idx
        ]
        
        return {
            'predicted_class': self.class_names[predicted_class_idx],
            'confidence': confidence,
            'top_3_predictions': top_3_predictions,
            'all_probabilities': {
                self.class_names[i]: float(predictions[0][i]) 
                for i in range(len(self.class_names))
            }
        }


# Example usage and training script
if __name__ == "__main__":
    # Initialize model
    model = CropHealthModel(num_classes=4)
    
    # Build and compile
    model.build_model()
    model.compile_model()
    
    print("Model Summary:")
    model.model.summary()
    
    # Note: For actual training, you need organized dataset:
    # train/
    #   Healthy/
    #   Pest_Disease/
    #   Flood_Damage/
    #   Drought_Stress/
    # val/
    #   Healthy/
    #   Pest_Disease/
    #   Flood_Damage/
    #   Drought_Stress/
    
    # Example training (uncomment when data is ready):
    # history = model.train('data/train', 'data/val', epochs=20, batch_size=32)
    # model.save_model()
    
    print("\nModel architecture created successfully!")
    print("To train: Organize your dataset and uncomment the training code above")
