# 🌾 CROPIC-Inspired Crop Image Analytics System

An AI-powered crop health monitoring system using deep learning for automated classification of crop conditions and damage detection. Built with TensorFlow and Streamlit for rapid deployment and demonstration.

## 🎯 Features

### 1. Mobile Application Interface
- 📸 Easy image upload interface
- 📍 Geo-location recording (latitude/longitude)
- 🌱 Crop type and growth stage selection
- ✅ Image quality guidance and validation

### 2. AI/ML Analytics Engine
- 🧠 Transfer learning with MobileNetV2
- 🔄 Automated image preprocessing
- ✨ Image quality validation (blur, brightness, contrast)
- 🎯 Multi-class classification:
  - Healthy crops
  - Pest/Disease damage
  - Flood damage
  - Drought stress
- 📊 Confidence scores and top-3 predictions

### 3. Web Dashboard
- 📈 Analysis results visualization
- 🗺️ Interactive map with geo-tagged data
- 📜 Historical analysis tracking
- 💾 Export data in JSON format
- 📊 Summary statistics and metrics

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit Web App                     │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │   Capture   │  │   Dashboard  │  │     About     │  │
│  │  & Analyze  │  │   & History  │  │  Information  │  │
│  └─────────────┘  └──────────────┘  └───────────────┘  │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│              Image Preprocessor Module                   │
│  • Quality validation (blur, brightness, contrast)      │
│  • Image enhancement (CLAHE)                            │
│  • Resizing and normalization                           │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│              AI Model (Transfer Learning)                │
│  • Base: MobileNetV2 (ImageNet pre-trained)            │
│  • Custom classification head                           │
│  • Input: 224×224×3 RGB images                         │
│  • Output: 4 classes with confidence scores             │
└─────────────────────────────────────────────────────────┘
```

## 📋 Requirements

### System Requirements
- Python 3.8 - 3.11
- 4GB RAM minimum (8GB recommended)
- 2GB free disk space

### Python Dependencies
See `requirements.txt` for complete list. Key packages:
- TensorFlow 2.15.0
- Streamlit 1.28.0
- OpenCV 4.8.1
- Pillow 10.0.0
- Folium 0.14.0

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project
cd crop-analytics-system

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Prepare Dataset (For Training)

```bash
# Run dataset preparation script
python prepare_dataset.py

# This creates the following structure:
# crop_dataset/
#   train/
#     Healthy/
#     Pest_Disease/
#     Flood_Damage/
#     Drought_Stress/
#   val/
#     Healthy/
#     Pest_Disease/
#     Flood_Damage/
#     Drought_Stress/
```

**Dataset Sources:**
- [PlantVillage Dataset](https://www.kaggle.com/datasets/emmarex/plantdisease) - 54,000+ images
- [New Plant Diseases Dataset](https://www.kaggle.com/datasets/vipoooool/new-plant-diseases-dataset) - 87,000+ images
- [Rice Disease Dataset](https://www.kaggle.com/datasets/minhhuy2810/rice-diseases-image-dataset)

### 3. Train the Model (Optional)

```bash
# Edit model_training.py to specify your dataset path
# Then run:
python model_training.py
```

Or use in Python:
```python
from model_training import CropHealthModel

# Initialize and build model
model = CropHealthModel(num_classes=4)
model.build_model()
model.compile_model()

# Train model
history = model.train('crop_dataset/train', 'crop_dataset/val', epochs=20)

# Save trained model
model.save_model('crop_health_model.h5')
```

### 4. Run the Application

```bash
# Start Streamlit app
streamlit run app.py

# The app will open in your browser at http://localhost:8501
```

## 📱 Usage Guide

### Capturing and Analyzing Images

1. **Navigate to "Capture & Analyze" tab**
   - Upload a crop image (JPG, PNG)
   - Select crop type (Rice, Wheat, Maize, etc.)
   - Select growth stage (Seedling, Vegetative, etc.)
   - Enter location (latitude/longitude)

2. **Click "Analyze Crop Health"**
   - System validates image quality
   - AI model processes the image
   - Results displayed with confidence scores

3. **Review Results**
   - Image quality metrics
   - Predicted condition
   - Confidence scores
   - Recommendations

### Viewing Dashboard

1. **Navigate to "Dashboard" tab**
   - View summary statistics
   - See all analyses on interactive map
   - Browse historical data
   - Export data as JSON

### 📸 Best Practices for Image Capture

✅ **DO:**
- Take photos in good natural lighting
- Ensure crop is in focus
- Fill frame with the crop
- Capture from 1-2 feet distance
- Use landscape orientation
- Take multiple angles if unsure

❌ **DON'T:**
- Use flash (causes glare)
- Include too much background
- Take blurry photos
- Capture in very low light
- Include multiple crops in one image

## 🔧 Configuration

### Model Configuration

Edit `model_training.py` to customize:

```python
# Number of classes
num_classes = 4

# Input image size
img_size = 224

# Training parameters
epochs = 20
batch_size = 32
learning_rate = 0.001
```

### Class Names

Modify in `model_training.py`:

```python
self.class_names = [
    'Healthy', 
    'Pest_Disease', 
    'Flood_Damage', 
    'Drought_Stress'
]
```

### Image Quality Thresholds

Edit `image_preprocessor.py`:

```python
# Blur threshold
if blur_score < 100:  # Adjust this value

# Brightness thresholds
if brightness < 50 or brightness > 200:  # Adjust these

# Contrast threshold
if contrast < 30:  # Adjust this value
```

## 📊 Model Performance

### Expected Performance (with adequate training data):

| Metric | Target |
|--------|--------|
| Training Accuracy | > 90% |
| Validation Accuracy | > 85% |
| Inference Time | < 200ms |
| Model Size | ~15 MB |

### Improving Model Performance:

1. **Increase dataset size**
   - Aim for 500+ images per class
   - Ensure balanced class distribution

2. **Data augmentation**
   - Already implemented in training script
   - Rotation, flipping, zoom, shift

3. **Fine-tuning**
   - Unfreeze more base layers
   - Use lower learning rate

4. **Ensemble methods**
   - Combine multiple models
   - Voting or averaging predictions

## 🧪 Testing

### Test Image Quality Validation

```python
from image_preprocessor import ImagePreprocessor
from PIL import Image

preprocessor = ImagePreprocessor()
image = Image.open('test_image.jpg')

# Validate quality
results = preprocessor.validate_image_quality(image)
print(results)
```

### Test Model Prediction

```python
from model_training import CropHealthModel
from image_preprocessor import ImagePreprocessor
from PIL import Image

# Load model
model = CropHealthModel()
model.load_model('crop_health_model.h5')

# Preprocess image
preprocessor = ImagePreprocessor()
image = Image.open('test_crop.jpg')
processed = preprocessor.preprocess_image(image)

# Predict
prediction = model.predict(processed)
print(f"Predicted: {prediction['predicted_class']}")
print(f"Confidence: {prediction['confidence']:.2%}")
```

## 🐛 Troubleshooting

### Common Issues

**1. Model not loading**
```
Error: Model file not found
Solution: Ensure 'crop_health_model.h5' is in the project directory
or train a new model using model_training.py
```

**2. Import errors**
```
Error: No module named 'tensorflow'
Solution: Ensure virtual environment is activated and 
pip install -r requirements.txt has been run
```

**3. Memory errors during training**
```
Error: OOM when allocating tensor
Solution: Reduce batch_size in model.train() function
```

**4. Streamlit not opening**
```
Error: Port already in use
Solution: Use: streamlit run app.py --server.port 8502
```

## 📁 Project Structure

```
crop-analytics-system/
├── app.py                      # Main Streamlit application
├── model_training.py           # AI model training script
├── image_preprocessor.py       # Image validation & preprocessing
├── prepare_dataset.py          # Dataset organization tool
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── crop_dataset/              # Training data (create this)
│   ├── train/
│   │   ├── Healthy/
│   │   ├── Pest_Disease/
│   │   ├── Flood_Damage/
│   │   └── Drought_Stress/
│   └── val/
│       ├── Healthy/
│       ├── Pest_Disease/
│       ├── Flood_Damage/
│       └── Drought_Stress/
├── crop_health_model.h5       # Trained model (after training)
└── class_names.json           # Class labels (after training)
```

## 🎓 Academic Context

This system demonstrates:

1. **Transfer Learning**: Using pre-trained MobileNetV2 on ImageNet
2. **Computer Vision**: Image preprocessing and quality validation
3. **Web Application Development**: Streamlit for rapid prototyping
4. **Geospatial Visualization**: Folium for mapping
5. **Data Management**: Pandas for analysis tracking

### Suitable for:
- Final year projects
- Computer vision courses
- Machine learning applications
- Agricultural technology demonstrations

## 🔮 Future Enhancements

- [ ] Real-time camera integration
- [ ] Mobile app (React Native/Flutter)
- [ ] Multi-language support
- [ ] Cloud deployment (AWS/GCP/Azure)
- [ ] API for third-party integration
- [ ] Advanced damage localization (object detection)
- [ ] Time-series analysis for crop monitoring
- [ ] Weather data integration
- [ ] Expert system for treatment recommendations
- [ ] Farmer community features

## 📚 References

1. **MobileNetV2**: [Sandler et al., 2018](https://arxiv.org/abs/1801.04381)
2. **Transfer Learning**: [Pan & Yang, 2010](https://ieeexplore.ieee.org/document/5288526)
3. **Plant Disease Recognition**: [Mohanty et al., 2016](https://arxiv.org/abs/1604.03169)
4. **CROPIC Initiative**: Agricultural AI applications

## 📄 License

This project is created for educational and demonstration purposes.
Modify and use as needed for your academic requirements.

## 🤝 Contributing

Suggestions for improvements:
1. Fork the repository
2. Create feature branch
3. Make improvements
4. Submit pull request

## 📧 Support

For questions or issues:
- Check troubleshooting section
- Review code comments
- Consult TensorFlow/Streamlit documentation

## 🙏 Acknowledgments

- TensorFlow team for transfer learning models
- Streamlit for rapid web development
- OpenCV for image processing capabilities
- Agricultural research community for datasets

---

**Note**: This is a prototype system for academic demonstration. 
For production use, extensive testing and model training with 
representative datasets is required.

**Good luck with your project! 🌾🚀**
