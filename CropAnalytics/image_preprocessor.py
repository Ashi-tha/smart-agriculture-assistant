"""
Image Preprocessing and Quality Validation Module
Handles image quality checks, preprocessing, and enhancement
"""

import cv2
import numpy as np
from PIL import Image
import io

class ImagePreprocessor:
    def __init__(self, target_size=(224, 224)):
        """
        Initialize image preprocessor
        
        Args:
            target_size: Target size for model input (width, height)
        """
        self.target_size = target_size
        
    def validate_image_quality(self, image):
        """
        Validate image quality based on multiple criteria
        
        Args:
            image: PIL Image or numpy array
        
        Returns:
            dict: Validation results with quality metrics
        """
        # Convert to numpy array if PIL Image
        if isinstance(image, Image.Image):
            img_array = np.array(image)
        else:
            img_array = image
        
        results = {
            'is_valid': True,
            'issues': [],
            'metrics': {}
        }
        
        # 1. Check image size
        height, width = img_array.shape[:2]
        results['metrics']['width'] = width
        results['metrics']['height'] = height
        
        if width < 224 or height < 224:
            results['is_valid'] = False
            results['issues'].append(f"Image too small: {width}x{height}. Minimum 224x224 required.")
        
        # 2. Check blur (Laplacian variance)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY) if len(img_array.shape) == 3 else img_array
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        results['metrics']['blur_score'] = float(blur_score)
        
        if blur_score < 100:
            results['issues'].append(f"Image is blurry (score: {blur_score:.2f}). Try taking a clearer photo.")
        
        # 3. Check brightness
        brightness = np.mean(gray)
        results['metrics']['brightness'] = float(brightness)
        
        if brightness < 50:
            results['issues'].append(f"Image is too dark (brightness: {brightness:.2f}). Needs better lighting.")
        elif brightness > 200:
            results['issues'].append(f"Image is too bright (brightness: {brightness:.2f}). Reduce exposure.")
        
        # 4. Check contrast
        contrast = np.std(gray)
        results['metrics']['contrast'] = float(contrast)
        
        if contrast < 30:
            results['issues'].append(f"Low contrast (score: {contrast:.2f}). Image may lack detail.")
        
        # 5. Overall quality score (0-100)
        quality_score = min(100, (
            (min(blur_score, 500) / 500 * 40) +  # Blur contributes 40%
            (min(contrast, 100) / 100 * 30) +     # Contrast contributes 30%
            (30 if 50 <= brightness <= 200 else 10)  # Brightness contributes 30%
        ))
        results['metrics']['quality_score'] = float(quality_score)
        
        return results
    
    def preprocess_image(self, image, enhance=True):
        """
        Preprocess image for model input
        
        Args:
            image: PIL Image or numpy array
            enhance: Whether to apply image enhancement
        
        Returns:
            numpy array: Preprocessed image ready for model
        """
        # Convert to PIL if numpy array
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)
        
        # Resize to target size
        image = image.resize(self.target_size, Image.Resampling.LANCZOS)
        
        # Convert to array
        img_array = np.array(image)
        
        # Ensure RGB format
        if len(img_array.shape) == 2:  # Grayscale
            img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2RGB)
        elif img_array.shape[2] == 4:  # RGBA
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
        
        # Optional enhancement
        if enhance:
            img_array = self._enhance_image(img_array)
        
        # Normalize to [0, 1]
        img_array = img_array.astype(np.float32) / 255.0
        
        return img_array
    
    def _enhance_image(self, img_array):
        """
        Apply image enhancement techniques
        
        Args:
            img_array: numpy array of image
        
        Returns:
            Enhanced image array
        """
        # Convert to LAB color space for better enhancement
        lab = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to L channel
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        # Merge channels
        enhanced_lab = cv2.merge([l, a, b])
        
        # Convert back to RGB
        enhanced = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2RGB)
        
        return enhanced
    
    def extract_metadata(self, image_file):
        """
        Extract metadata from image file
        
        Args:
            image_file: File-like object or path
        
        Returns:
            dict: Image metadata
        """
        try:
            img = Image.open(image_file)
            
            metadata = {
                'format': img.format,
                'mode': img.mode,
                'size': img.size,
                'width': img.width,
                'height': img.height,
            }
            
            # Extract EXIF data if available
            exif_data = img.getexif()
            if exif_data:
                metadata['exif'] = {
                    'DateTime': exif_data.get(306, 'N/A'),
                    'Make': exif_data.get(271, 'N/A'),
                    'Model': exif_data.get(272, 'N/A'),
                }
            
            return metadata
        except Exception as e:
            return {'error': str(e)}
    
    def crop_to_square(self, image):
        """
        Crop image to square aspect ratio (center crop)
        
        Args:
            image: PIL Image
        
        Returns:
            PIL Image: Square cropped image
        """
        width, height = image.size
        
        if width == height:
            return image
        
        # Determine crop size
        crop_size = min(width, height)
        
        # Calculate crop box (center crop)
        left = (width - crop_size) // 2
        top = (height - crop_size) // 2
        right = left + crop_size
        bottom = top + crop_size
        
        return image.crop((left, top, right, bottom))
    
    def resize_for_display(self, image, max_size=800):
        """
        Resize image for display purposes while maintaining aspect ratio
        
        Args:
            image: PIL Image
            max_size: Maximum dimension
        
        Returns:
            PIL Image: Resized image
        """
        width, height = image.size
        
        if width <= max_size and height <= max_size:
            return image
        
        # Calculate new dimensions
        if width > height:
            new_width = max_size
            new_height = int(height * (max_size / width))
        else:
            new_height = max_size
            new_width = int(width * (max_size / height))
        
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)


# Test the preprocessor
if __name__ == "__main__":
    print("Image Preprocessor Module - Ready")
    preprocessor = ImagePreprocessor()
    print("Target size:", preprocessor.target_size)
    print("\nQuality validation metrics:")
    print("- Blur detection (Laplacian variance)")
    print("- Brightness check")
    print("- Contrast analysis")
    print("- Overall quality score (0-100)")
