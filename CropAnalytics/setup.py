#!/usr/bin/env python3
"""
Automated Setup Script for CROPIC Crop Analytics System
Run this script to set up the entire system automatically
"""

import subprocess
import sys
import os
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def print_success(text):
    """Print success message"""
    print(f"✅ {text}")

def print_error(text):
    """Print error message"""
    print(f"❌ {text}")

def print_info(text):
    """Print info message"""
    print(f"ℹ️  {text}")

def check_python_version():
    """Check if Python version is compatible"""
    print_header("Checking Python Version")
    
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 8:
        print_success("Python version is compatible")
        return True
    else:
        print_error("Python 3.8 or higher is required")
        return False

def install_dependencies():
    """Install required Python packages"""
    print_header("Installing Dependencies")
    
    packages = [
        "tensorflow==2.15.0",
        "streamlit==1.28.0",
        "opencv-python==4.8.1.78",
        "Pillow==10.0.0",
        "folium==0.14.0",
        "streamlit-folium==0.15.0",
        "numpy==1.24.3",
        "pandas==2.1.0",
        "scikit-image==0.21.0",
        "matplotlib==3.7.2",
        "scikit-learn==1.3.0"
    ]
    
    print_info(f"Installing {len(packages)} packages...")
    
    try:
        for package in packages:
            print(f"  Installing {package}...")
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package, "-q"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        print_success("All dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install dependencies: {e}")
        print_info("Try manual installation: pip install -r requirements.txt")
        return False

def create_directory_structure():
    """Create necessary directories"""
    print_header("Creating Directory Structure")
    
    directories = [
        "crop_data",
        "crop_dataset/train/Healthy",
        "crop_dataset/train/Pest_Disease",
        "crop_dataset/train/Flood_Damage",
        "crop_dataset/train/Drought_Stress",
        "crop_dataset/val/Healthy",
        "crop_dataset/val/Pest_Disease",
        "crop_dataset/val/Flood_Damage",
        "crop_dataset/val/Drought_Stress",
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  Created: {directory}")
    
    print_success("Directory structure created")
    return True

def verify_files():
    """Verify that all necessary files exist"""
    print_header("Verifying Project Files")
    
    required_files = [
        "app.py",
        "model_training.py",
        "image_preprocessor.py",
        "prepare_dataset.py",
        "requirements.txt",
        "README.md"
    ]
    
    all_present = True
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} - MISSING")
            all_present = False
    
    if all_present:
        print_success("All required files present")
    else:
        print_error("Some required files are missing")
    
    return all_present

def test_imports():
    """Test if all imports work"""
    print_header("Testing Imports")
    
    imports = [
        ("tensorflow", "TensorFlow"),
        ("streamlit", "Streamlit"),
        ("cv2", "OpenCV"),
        ("PIL", "Pillow"),
        ("folium", "Folium"),
        ("numpy", "NumPy"),
        ("pandas", "Pandas")
    ]
    
    all_successful = True
    for module, name in imports:
        try:
            __import__(module)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ✗ {name} - FAILED")
            all_successful = False
    
    if all_successful:
        print_success("All imports successful")
    else:
        print_error("Some imports failed")
    
    return all_successful

def test_model_creation():
    """Test if model can be created"""
    print_header("Testing Model Creation")
    
    try:
        from model_training import CropHealthModel
        
        print("  Creating model instance...")
        model = CropHealthModel(num_classes=4)
        
        print("  Building model architecture...")
        model.build_model()
        
        print("  Compiling model...")
        model.compile_model()
        
        print_success("Model created successfully")
        
        # Print model summary
        print("\nModel Summary:")
        print(f"  Total parameters: {model.model.count_params():,}")
        
        return True
    except Exception as e:
        print_error(f"Model creation failed: {e}")
        return False

def create_demo_script():
    """Create a simple demo script"""
    print_header("Creating Demo Script")
    
    demo_script = """#!/usr/bin/env python3
'''Quick demo script to test the system'''

from model_training import CropHealthModel
from image_preprocessor import ImagePreprocessor
import numpy as np

print("🌾 CROPIC System Demo\\n")

# Test 1: Image Preprocessor
print("1. Testing Image Preprocessor...")
preprocessor = ImagePreprocessor()
print(f"   Target size: {preprocessor.target_size}")
print("   ✅ Preprocessor ready\\n")

# Test 2: Model Architecture
print("2. Testing Model Architecture...")
model = CropHealthModel(num_classes=4)
model.build_model()
print(f"   Classes: {', '.join(model.class_names)}")
print(f"   Parameters: {model.model.count_params():,}")
print("   ✅ Model ready\\n")

# Test 3: Sample Prediction
print("3. Testing Prediction Pipeline...")
dummy_image = np.random.rand(224, 224, 3)
prediction = model.predict(dummy_image)
print(f"   Predicted: {prediction['predicted_class']}")
print(f"   Confidence: {prediction['confidence']:.2%}")
print("   ✅ Prediction works\\n")

print("="*50)
print("All systems operational! 🚀")
print("Run 'streamlit run app.py' to start the web interface")
print("="*50)
"""
    
    with open("demo.py", "w") as f:
        f.write(demo_script)
    
    print_success("Demo script created: demo.py")
    return True

def display_next_steps():
    """Display next steps for the user"""
    print_header("Setup Complete! 🎉")
    
    print("Next Steps:\n")
    
    print("1. 🚀 Quick Start (Test the app immediately)")
    print("   streamlit run app.py\n")
    
    print("2. 🧪 Run Demo Script (Test all components)")
    print("   python demo.py\n")
    
    print("3. 📊 Prepare Dataset (For training)")
    print("   python prepare_dataset.py\n")
    
    print("4. 🧠 Train Model (After preparing dataset)")
    print("   python model_training.py\n")
    
    print("5. 📚 Read Documentation")
    print("   - README.md - Complete documentation")
    print("   - QUICK_START.md - Quick start guide\n")
    
    print("="*60)
    print("\n✨ System is ready to use!")
    print("\nFor a quick test, run:")
    print("  streamlit run app.py")
    print("\nThe app will open at: http://localhost:8501")
    print("="*60 + "\n")

def main():
    """Main setup function"""
    print("\n")
    print("="*60)
    print("  🌾 CROPIC Crop Analytics System - Setup Script")
    print("="*60)
    print("\n")
    
    # Run setup steps
    steps = [
        ("Checking Python version", check_python_version),
        ("Verifying project files", verify_files),
        ("Installing dependencies", install_dependencies),
        ("Creating directories", create_directory_structure),
        ("Testing imports", test_imports),
        ("Testing model creation", test_model_creation),
        ("Creating demo script", create_demo_script),
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        if not step_func():
            failed_steps.append(step_name)
    
    # Display results
    print("\n")
    print("="*60)
    print("  Setup Summary")
    print("="*60 + "\n")
    
    if not failed_steps:
        print("✅ All steps completed successfully!\n")
        display_next_steps()
    else:
        print(f"⚠️  Setup completed with {len(failed_steps)} issue(s):\n")
        for step in failed_steps:
            print(f"  • {step}")
        print("\nPlease resolve these issues before proceeding.")
        print("Check README.md for troubleshooting tips.\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Setup failed with error: {e}")
        sys.exit(1)
