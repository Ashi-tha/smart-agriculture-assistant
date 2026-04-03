"""
AgriSense — Crop Health Analytics Engine.
Ported and enhanced from CROPIC.
Handles Image Quality Assessment and Health Classification.
"""
import cv2
import numpy as np
import os
import io
from PIL import Image
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model

class AnalyticsEngine:
    def __init__(self, target_size=(224, 224)):
        self.target_size = target_size
        self.model = None
        self.weights_path = os.path.join("models", "crop_analytics_model.h5")
        self.class_names = ['Healthy', 'Pests & Diseases', 'Flood Damage', 'Drought Stress']

    def validate_quality(self, image_bytes):
        """Perform OpenCV-based quality checks."""
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img_array = np.array(img)
        
        results = {
            'is_valid': True,
            'issues': [],
            'metrics': {}
        }
        
        # 1. Size
        h, w = img_array.shape[:2]
        results['metrics']['width'] = w
        results['metrics']['height'] = h
        if w < 224 or h < 224:
            results['is_valid'] = False
            results['issues'].append("Image resolution is too low (min 224x224).")
            
        # 2. Blur (Laplacian variance)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        results['metrics']['blur_score'] = float(blur_score)
        if blur_score < 100:
            results['issues'].append("Image is blurry. Please hold the camera steady.")
            
        # 3. Brightness
        brightness = np.mean(gray)
        results['metrics']['brightness'] = float(brightness)
        if brightness < 50:
            results['issues'].append("Image is too dark. Increase lighting.")
        elif brightness > 200:
            results['issues'].append("Image is too bright (overexposed).")
            
        # 4. Contrast
        contrast = np.std(gray)
        results['metrics']['contrast'] = float(contrast)
        if contrast < 30:
            results['issues'].append("Low contrast. Detail might be lost.")
            
        # 5. Overall Quality Score (0-100)
        q_score = min(100, (
            (min(blur_score, 500) / 500 * 40) +
            (min(contrast, 100) / 100 * 30) +
            (30 if 50 <= brightness <= 200 else 10)
        ))
        results['metrics']['quality_score'] = round(float(q_score), 1)
        
        return results

    def _load_model(self):
        """Lazy load the classification model."""
        if self.model is not None:
            return True
        
        if not os.path.exists(self.weights_path):
            return False
            
        try:
            base = MobileNetV2(weights=None, include_top=False, input_shape=(224, 224, 3))
            x = GlobalAveragePooling2D()(base.output)
            x = Dense(256, activation='relu')(x)
            x = Dropout(0.5)(x)
            out = Dense(len(self.class_names), activation='softmax')(x)
            model = Model(inputs=base.input, outputs=out)
            model.load_weights(self.weights_path)
            self.model = model
            return True
        except Exception:
            return False

    def predict_health(self, image_bytes):
        """Classify health status using AI or Demo Fallback."""
        if self._load_model():
            # Real Prediction
            img = Image.open(io.BytesIO(image_bytes)).convert("RGB").resize(self.target_size)
            arr = np.array(img, dtype=np.float32) / 255.0
            arr = np.expand_dims(arr, 0)
            
            preds = self.model.predict(arr, verbose=0)[0]
            top_idx = int(np.argmax(preds))
            
            return {
                'status': self.class_names[top_idx],
                'confidence': float(preds[top_idx]) * 100,
                'is_demo': False,
                'distribution': {self.class_names[i]: float(preds[i]) for i in range(len(self.class_names))}
            }
        else:
            # Demo Fallback (Deterministic based on image data)
            np.random.seed(int.from_bytes(image_bytes[:4], "little") % (2**31))
            status_idx = np.random.choice(len(self.class_names), p=[0.7, 0.1, 0.1, 0.1]) # Slight bias to Healthy
            confidence = 70 + np.random.uniform(0, 25)
            
            return {
                'status': self.class_names[status_idx],
                'confidence': round(float(confidence), 1),
                'is_demo': True,
                'distribution': {self.class_names[i]: float(min(1.0, np.random.uniform(0, 1))) for i in range(len(self.class_names))}
            }
