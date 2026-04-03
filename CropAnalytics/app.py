"""
CROPIC-Inspired Crop Health Analytics System
Main Streamlit Application - Mobile Interface + Dashboard
"""

import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import folium
from streamlit_folium import st_folium
from datetime import datetime
import json
import os
from pathlib import Path

# Import custom modules
from image_preprocessor import ImagePreprocessor
from model_training import CropHealthModel

# Page configuration
st.set_page_config(
    page_title="CROPIC - Crop Analytics",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E7D32;
        font-weight: bold;
        text-align: center;
        padding: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #558B2F;
        font-weight: 600;
        margin-top: 1rem;
    }
    .metric-card {
        background-color: #E8F5E9;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .warning-box {
        background-color: #FFF3E0;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #FF9800;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #E8F5E9;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #4CAF50;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []

if 'preprocessor' not in st.session_state:
    st.session_state.preprocessor = ImagePreprocessor()

if 'model' not in st.session_state:
    st.session_state.model = None

# Initialize data directory
DATA_DIR = Path("crop_data")
DATA_DIR.mkdir(exist_ok=True)

def load_or_create_model():
    """Load existing model or create demo model"""
    model = CropHealthModel(num_classes=4)
    
    # Try to load existing model
    if os.path.exists('crop_health_model.h5'):
        try:
            model.load_model('crop_health_model.h5')
            return model, True
        except Exception as e:
            st.warning(f"Could not load existing model: {e}")
    
    # Build new model for demonstration
    model.build_model()
    model.compile_model()
    return model, False

def get_geolocation():
    """Simulate getting geolocation (in real app, use JS geolocation API)"""
    # In production, you would use JavaScript geolocation API
    # For demo, we'll use manual input
    col1, col2 = st.columns(2)
    with col1:
        lat = st.number_input("Latitude", value=11.3410, format="%.4f", help="Enter field latitude")
    with col2:
        lon = st.number_input("Longitude", value=77.7172, format="%.4f", help="Enter field longitude")
    
    return lat, lon

def analyze_image(image, crop_type, growth_stage, location):
    """Analyze crop image and return results"""
    preprocessor = st.session_state.preprocessor
    
    # Validate image quality
    validation_results = preprocessor.validate_image_quality(image)
    
    # Preprocess image
    processed_image = preprocessor.preprocess_image(image, enhance=True)
    
    # Get prediction
    model = st.session_state.model
    if model and model.model is not None:
        prediction = model.predict(processed_image)
    else:
        # Demo prediction when model is not trained
        prediction = {
            'predicted_class': 'Healthy',
            'confidence': 0.85,
            'top_3_predictions': [
                {'class': 'Healthy', 'confidence': 0.85},
                {'class': 'Pest_Disease', 'confidence': 0.10},
                {'class': 'Drought_Stress', 'confidence': 0.05}
            ],
            'all_probabilities': {
                'Healthy': 0.85,
                'Pest_Disease': 0.10,
                'Flood_Damage': 0.0,
                'Drought_Stress': 0.05
            }
        }
    
    # Create analysis record
    analysis_record = {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'crop_type': crop_type,
        'growth_stage': growth_stage,
        'location': location,
        'validation': validation_results,
        'prediction': prediction,
        'image_shape': image.size
    }
    
    return analysis_record

def display_analysis_results(analysis):
    """Display analysis results in a structured format"""
    st.markdown("---")
    st.markdown('<p class="sub-header">📊 Analysis Results</p>', unsafe_allow_html=True)
    
    # Image quality metrics
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("**Image Quality Assessment**")
        metrics = analysis['validation']['metrics']
        
        quality_score = metrics.get('quality_score', 0)
        if quality_score >= 70:
            st.markdown(f'<div class="success-box">✅ Quality Score: {quality_score:.1f}/100 - Good quality image</div>', 
                       unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="warning-box">⚠️ Quality Score: {quality_score:.1f}/100 - Image quality could be improved</div>', 
                       unsafe_allow_html=True)
        
        # Display metrics
        met_col1, met_col2 = st.columns(2)
        with met_col1:
            st.metric("Blur Score", f"{metrics.get('blur_score', 0):.0f}")
            st.metric("Brightness", f"{metrics.get('brightness', 0):.0f}")
        with met_col2:
            st.metric("Contrast", f"{metrics.get('contrast', 0):.0f}")
            st.metric("Resolution", f"{metrics.get('width', 0)}×{metrics.get('height', 0)}")
        
        # Display issues if any
        if analysis['validation']['issues']:
            st.warning("**Quality Issues Detected:**")
            for issue in analysis['validation']['issues']:
                st.write(f"• {issue}")
    
    with col2:
        st.markdown("**Crop Health Classification**")
        prediction = analysis['prediction']
        
        predicted_class = prediction['predicted_class']
        confidence = prediction['confidence'] * 100
        
        # Display main prediction
        if 'Healthy' in predicted_class:
            st.markdown(f'<div class="success-box">✅ <strong>{predicted_class}</strong><br>Confidence: {confidence:.1f}%</div>', 
                       unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="warning-box">⚠️ <strong>{predicted_class}</strong><br>Confidence: {confidence:.1f}%</div>', 
                       unsafe_allow_html=True)
        
        # Display top predictions
        st.markdown("**Top 3 Predictions:**")
        for i, pred in enumerate(prediction['top_3_predictions'], 1):
            conf_pct = pred['confidence'] * 100
            st.progress(pred['confidence'], text=f"{i}. {pred['class']}: {conf_pct:.1f}%")
    
    # Detailed probabilities
    with st.expander("📈 View All Class Probabilities"):
        prob_df = pd.DataFrame([
            {'Class': k, 'Probability': f"{v*100:.2f}%"} 
            for k, v in prediction['all_probabilities'].items()
        ])
        st.dataframe(prob_df, use_container_width=True, hide_index=True)
    
    # Recommendations
    st.markdown("**💡 Recommendations:**")
    if 'Healthy' in predicted_class and confidence > 80:
        st.success("Crop appears healthy. Continue regular monitoring and maintenance.")
    elif 'Pest_Disease' in predicted_class:
        st.warning("Possible pest or disease detected. Consider:")
        st.write("• Consult with agricultural extension officer")
        st.write("• Apply appropriate pesticides/fungicides")
        st.write("• Monitor spread to neighboring plants")
    elif 'Flood_Damage' in predicted_class:
        st.warning("Flood damage detected. Consider:")
        st.write("• Improve drainage systems")
        st.write("• Apply growth promoters")
        st.write("• Monitor for secondary infections")
    elif 'Drought_Stress' in predicted_class:
        st.warning("Drought stress detected. Consider:")
        st.write("• Increase irrigation frequency")
        st.write("• Apply mulching to retain moisture")
        st.write("• Use water-retention products")

def display_map_view():
    """Display map with analysis locations"""
    st.markdown('<p class="sub-header">🗺️ Geographic Distribution</p>', unsafe_allow_html=True)
    
    if not st.session_state.analysis_history:
        st.info("No analysis data available yet. Upload images to see locations on map.")
        return
    
    # Create base map centered on average location
    locations = [record['location'] for record in st.session_state.analysis_history]
    avg_lat = np.mean([loc[0] for loc in locations])
    avg_lon = np.mean([loc[1] for loc in locations])
    
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=10)
    
    # Add markers for each analysis
    for record in st.session_state.analysis_history:
        lat, lon = record['location']
        prediction = record['prediction']['predicted_class']
        confidence = record['prediction']['confidence'] * 100
        
        # Color based on health status
        color = 'green' if 'Healthy' in prediction else 'orange' if 'Drought' in prediction or 'Pest' in prediction else 'red'
        
        popup_html = f"""
        <div style="width:200px">
            <b>{record['crop_type']}</b><br>
            Stage: {record['growth_stage']}<br>
            Status: {prediction}<br>
            Confidence: {confidence:.1f}%<br>
            Time: {record['timestamp']}
        </div>
        """
        
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.Icon(color=color, icon='leaf', prefix='fa')
        ).add_to(m)
    
    # Display map
    st_folium(m, width=1200, height=500)

def mobile_interface():
    """Mobile-style interface for image capture and upload"""
    st.markdown('<p class="main-header">🌾 CROPIC Crop Analytics</p>', unsafe_allow_html=True)
    st.markdown("**AI-Powered Crop Health Monitoring System**")
    
    tab1, tab2, tab3 = st.tabs(["📸 Capture & Analyze", "📊 Dashboard", "ℹ️ About"])
    
    with tab1:
        st.markdown('<p class="sub-header">Capture Crop Image</p>', unsafe_allow_html=True)
        
        # Image upload
        uploaded_file = st.file_uploader(
            "Upload crop image", 
            type=['jpg', 'jpeg', 'png'],
            help="Take a clear photo of the crop in good lighting"
        )
        
        if uploaded_file:
            # Display uploaded image
            image = Image.open(uploaded_file)
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.image(image, caption="Uploaded Image", use_container_width=True)
            
            with col2:
                st.markdown("**📋 Field Information**")
                
                # Crop selection
                crop_type = st.selectbox(
                    "Crop Type",
                    ["Rice", "Wheat", "Maize", "Cotton", "Sugarcane", "Tomato", "Potato", "Other"],
                    help="Select the type of crop"
                )
                
                # Growth stage
                growth_stage = st.selectbox(
                    "Growth Stage",
                    ["Seedling", "Vegetative", "Flowering", "Fruiting", "Maturity"],
                    help="Select the current growth stage"
                )
                
                # Location
                st.markdown("**📍 Location**")
                lat, lon = get_geolocation()
                location = (lat, lon)
                
                # Analyze button
                if st.button("🔍 Analyze Crop Health", type="primary", use_container_width=True):
                    with st.spinner("Analyzing image..."):
                        # Perform analysis
                        analysis = analyze_image(image, crop_type, growth_stage, location)
                        
                        # Add to history
                        st.session_state.analysis_history.append(analysis)
                        
                        # Display results
                        display_analysis_results(analysis)
                        
                        st.success("✅ Analysis complete! Check the Dashboard tab for historical data.")
    
    with tab2:
        st.markdown('<p class="sub-header">Analysis Dashboard</p>', unsafe_allow_html=True)
        
        if not st.session_state.analysis_history:
            st.info("📭 No analysis data yet. Upload and analyze images to see results here.")
        else:
            # Summary statistics
            col1, col2, col3, col4 = st.columns(4)
            
            total_analyses = len(st.session_state.analysis_history)
            healthy_count = sum(1 for a in st.session_state.analysis_history if 'Healthy' in a['prediction']['predicted_class'])
            avg_quality = np.mean([a['validation']['metrics']['quality_score'] for a in st.session_state.analysis_history])
            
            with col1:
                st.metric("Total Analyses", total_analyses)
            with col2:
                st.metric("Healthy Crops", f"{healthy_count}/{total_analyses}")
            with col3:
                st.metric("Avg Image Quality", f"{avg_quality:.1f}/100")
            with col4:
                health_rate = (healthy_count / total_analyses * 100) if total_analyses > 0 else 0
                st.metric("Health Rate", f"{health_rate:.1f}%")
            
            st.markdown("---")
            
            # Map view
            display_map_view()
            
            st.markdown("---")
            
            # History table
            st.markdown("**📜 Analysis History**")
            
            history_data = []
            for record in st.session_state.analysis_history:
                history_data.append({
                    'Timestamp': record['timestamp'],
                    'Crop': record['crop_type'],
                    'Stage': record['growth_stage'],
                    'Status': record['prediction']['predicted_class'],
                    'Confidence': f"{record['prediction']['confidence']*100:.1f}%",
                    'Quality': f"{record['validation']['metrics']['quality_score']:.0f}/100",
                    'Location': f"({record['location'][0]:.4f}, {record['location'][1]:.4f})"
                })
            
            df = pd.DataFrame(history_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Download data
            if st.button("📥 Download Analysis Data (JSON)"):
                json_data = json.dumps(st.session_state.analysis_history, indent=2)
                st.download_button(
                    label="Download JSON",
                    data=json_data,
                    file_name=f"crop_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
    
    with tab3:
        st.markdown('<p class="sub-header">About CROPIC System</p>', unsafe_allow_html=True)
        
        st.markdown("""
        ### 🌾 Crop Image Analytics System
        
        
        #### 🎯 Key Features:
        
        1. **Mobile Image Capture**
           - Upload crop images from smartphone
           - Automatic geo-location recording
           - Crop type and growth stage selection
           - Image quality guidance
        
        2. **AI/ML Analytics**
           - Transfer learning with MobileNetV2
           - Automated image preprocessing
           - Quality validation
           - Multi-class classification:
             * Healthy crops
             * Pest/Disease damage
             * Flood damage
             * Drought stress
           - Confidence scores for predictions
        
        3. **Web Dashboard**
           - View analysis results
           - Map-based visualization
           - Historical data tracking
           - Export analysis data
        
        #### 🔬 Technical Stack:
        
        - **Deep Learning**: TensorFlow, MobileNetV2 (Transfer Learning)
        - **Web Framework**: Streamlit
        - **Image Processing**: OpenCV, PIL
        - **Visualization**: Folium (Maps), Matplotlib
        
        #### 📊 Model Architecture:
        
        - Base: MobileNetV2 (pre-trained on ImageNet)
        - Custom classification head with dropout
        - Input size: 224×224×3
        - Output: 4 classes with softmax activation
        
        #### 🚀 Quick Start:
        
        1. Go to "Capture & Analyze" tab
        2. Upload a crop image
        3. Fill in crop details and location
        4. Click "Analyze Crop Health"
        5. View results and recommendations
        
        #### 💡 Tips for Best Results:
        
        - Take photos in good natural lighting
        - Ensure the crop is in focus
        - Fill the frame with the crop
        - Avoid shadows and glare
        - Capture from 1-2 feet distance
        
        ---
        
        
        """)
        
        # System status
        st.markdown("### 🔧 System Status")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Model Status**: {'✅ Loaded' if st.session_state.model and st.session_state.model.model else '⚠️ Demo Mode'}")
            st.info(f"**Analysis Count**: {len(st.session_state.analysis_history)}")
        with col2:
            st.info(f"**Image Preprocessor**: ✅ Active")
            st.info(f"**Geo-location**: ✅ Enabled")

def main():
    """Main application entry point"""
    
    # Load model on first run
    if st.session_state.model is None:
        with st.spinner("Loading AI model..."):
            model, loaded = load_or_create_model()
            st.session_state.model = model
            
            if not loaded:
                st.sidebar.warning("⚠️ Running in demo mode. Train the model for accurate predictions.")
            else:
                st.sidebar.success("✅ Model loaded successfully!")
    
    # Display interface
    mobile_interface()
    
    # Sidebar information
    with st.sidebar:
        st.markdown("### 🎛️ System Controls")
        
        if st.button("🗑️ Clear History"):
            st.session_state.analysis_history = []
            st.rerun()
        
        st.markdown("---")
        
        st.markdown("### 📚 Model Information")
        st.write(f"**Architecture**: MobileNetV2")
        st.write(f"**Input Size**: 224×224×3")
        st.write(f"**Classes**: 4")
        
        if st.session_state.model and st.session_state.model.model:
            total_params = st.session_state.model.model.count_params()
            st.write(f"**Parameters**: {total_params:,}")
        
        st.markdown("---")
        st.markdown("### 🔗 Quick Links")
        st.markdown("- [TensorFlow Docs](https://tensorflow.org)")
        st.markdown("- [Streamlit Docs](https://docs.streamlit.io)")
        st.markdown("- [CROPIC Initiative](https://example.com)")

if __name__ == "__main__":
    main()
