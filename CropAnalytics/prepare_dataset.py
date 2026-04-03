"""
Data Preparation Script
Helps organize crop images into training and validation datasets
"""

import os
import shutil
from pathlib import Path
import random

def create_dataset_structure(base_dir='crop_dataset'):
    """
    Create the required directory structure for training
    
    Structure:
    crop_dataset/
        train/
            Healthy/
            Pest_Disease/
            Flood_Damage/
            Drought_Stress/
        val/
            Healthy/
            Pest_Disease/
            Flood_Damage/
            Drought_Stress/
    """
    classes = ['Healthy', 'Pest_Disease', 'Flood_Damage', 'Drought_Stress']
    splits = ['train', 'val']
    
    base_path = Path(base_dir)
    
    for split in splits:
        for class_name in classes:
            dir_path = base_path / split / class_name
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"Created: {dir_path}")
    
    print(f"\n✅ Dataset structure created at: {base_path}")
    print(f"\nNext steps:")
    print(f"1. Add crop images to each class folder")
    print(f"2. Aim for at least 100-200 images per class")
    print(f"3. Maintain 80-20 split between train and val folders")
    
    return base_path

def organize_images(source_dir, dataset_dir='crop_dataset', val_split=0.2):
    """
    Organize images from a flat directory into train/val split
    
    Args:
        source_dir: Directory containing all images with labels in filename
                   e.g., "healthy_001.jpg", "pest_disease_002.jpg"
        dataset_dir: Target dataset directory
        val_split: Fraction of data to use for validation
    """
    source_path = Path(source_dir)
    
    if not source_path.exists():
        print(f"❌ Source directory not found: {source_dir}")
        return
    
    # Get all image files
    image_files = []
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']:
        image_files.extend(source_path.glob(ext))
    
    if not image_files:
        print(f"❌ No images found in {source_dir}")
        return
    
    print(f"Found {len(image_files)} images")
    
    # Group by class (assuming filename starts with class name)
    class_mapping = {
        'healthy': 'Healthy',
        'pest': 'Pest_Disease',
        'disease': 'Pest_Disease',
        'flood': 'Flood_Damage',
        'drought': 'Drought_Stress',
        'stress': 'Drought_Stress'
    }
    
    grouped_images = {
        'Healthy': [],
        'Pest_Disease': [],
        'Flood_Damage': [],
        'Drought_Stress': []
    }
    
    for img_file in image_files:
        filename = img_file.name.lower()
        
        # Determine class from filename
        matched = False
        for key, class_name in class_mapping.items():
            if key in filename:
                grouped_images[class_name].append(img_file)
                matched = True
                break
        
        if not matched:
            print(f"⚠️ Could not determine class for: {img_file.name}")
    
    # Create dataset structure
    dataset_path = create_dataset_structure(dataset_dir)
    
    # Copy files with train/val split
    for class_name, images in grouped_images.items():
        if not images:
            continue
        
        # Shuffle images
        random.shuffle(images)
        
        # Calculate split point
        val_count = int(len(images) * val_split)
        train_count = len(images) - val_count
        
        # Split into train and val
        train_images = images[:train_count]
        val_images = images[train_count:]
        
        # Copy train images
        for img in train_images:
            dest = dataset_path / 'train' / class_name / img.name
            shutil.copy2(img, dest)
        
        # Copy val images
        for img in val_images:
            dest = dataset_path / 'val' / class_name / img.name
            shutil.copy2(img, dest)
        
        print(f"\n{class_name}:")
        print(f"  Train: {len(train_images)} images")
        print(f"  Val: {len(val_images)} images")
    
    print(f"\n✅ Dataset organized successfully!")

def check_dataset(dataset_dir='crop_dataset'):
    """
    Check the dataset and print statistics
    """
    dataset_path = Path(dataset_dir)
    
    if not dataset_path.exists():
        print(f"❌ Dataset directory not found: {dataset_dir}")
        return
    
    print(f"\n📊 Dataset Statistics - {dataset_dir}")
    print("="*60)
    
    for split in ['train', 'val']:
        split_path = dataset_path / split
        if not split_path.exists():
            continue
        
        print(f"\n{split.upper()} SET:")
        total = 0
        
        for class_dir in split_path.iterdir():
            if class_dir.is_dir():
                count = len(list(class_dir.glob('*.[jp][pn][g]')))
                total += count
                print(f"  {class_dir.name}: {count} images")
        
        print(f"  TOTAL: {total} images")
    
    print("="*60)

def download_sample_dataset_info():
    """
    Provide information about available crop disease datasets
    """
    print("\n📚 Sample Dataset Sources:")
    print("="*60)
    
    datasets = [
        {
            'name': 'PlantVillage Dataset',
            'url': 'https://www.kaggle.com/datasets/emmarex/plantdisease',
            'description': '54,000+ images of healthy and diseased crop leaves',
            'crops': 'Tomato, Potato, Apple, Grape, etc.'
        },
        {
            'name': 'Plant Disease Recognition Dataset',
            'url': 'https://www.kaggle.com/datasets/vipoooool/new-plant-diseases-dataset',
            'description': '87,000+ RGB images of healthy and diseased plants',
            'crops': 'Multiple crops with 38 classes'
        },
        {
            'name': 'Crop Disease Dataset',
            'url': 'https://github.com/spMohanty/PlantVillage-Dataset',
            'description': 'Open source plant disease dataset',
            'crops': 'Various crops'
        },
        {
            'name': 'Rice Disease Dataset',
            'url': 'https://www.kaggle.com/datasets/minhhuy2810/rice-diseases-image-dataset',
            'description': 'Rice-specific disease images',
            'crops': 'Rice'
        }
    ]
    
    for i, dataset in enumerate(datasets, 1):
        print(f"\n{i}. {dataset['name']}")
        print(f"   URL: {dataset['url']}")
        print(f"   Description: {dataset['description']}")
        print(f"   Crops: {dataset['crops']}")
    
    print("\n" + "="*60)
    print("\n💡 Tips for Using Datasets:")
    print("1. Download dataset from Kaggle or GitHub")
    print("2. Extract and organize into train/val folders")
    print("3. Rename folders to match our classes:")
    print("   - Healthy")
    print("   - Pest_Disease")
    print("   - Flood_Damage")
    print("   - Drought_Stress")
    print("4. Run: organize_images() to split automatically")

if __name__ == "__main__":
    print("🌾 Crop Dataset Preparation Tool")
    print("="*60)
    
    # Create basic structure
    print("\n1. Creating dataset structure...")
    create_dataset_structure()
    
    print("\n2. Checking for existing dataset...")
    check_dataset()
    
    print("\n3. Dataset download information:")
    download_sample_dataset_info()
    
    print("\n" + "="*60)
    print("\n📝 Usage Examples:")
    print("\nTo organize images from a flat directory:")
    print(">>> organize_images('path/to/your/images')")
    print("\nTo check dataset statistics:")
    print(">>> check_dataset('crop_dataset')")
