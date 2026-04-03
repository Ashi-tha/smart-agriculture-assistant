"""
CROPIC-Inspired Crop Health Analytics System
Main Streamlit Application - FIXED VERSION
Fixes:
  1. Results no longer disappear after analyze
  2. Timestamp shown on result card
  3. Geo-location stays stable (no reset on button click)
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

from image_preprocessor import ImagePreprocessor
from model_training import CropHealthModel

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CROPIC - Crop Analytics",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CSS ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Header ── */
    .main-header {
        font-size: 2.4rem;
        color: #2E7D32;
        font-weight: 800;
        text-align: center;
        padding: 0.8rem 0 0.2rem 0;
        letter-spacing: -0.5px;
    }
    .sub-title {
        text-align: center;
        color: #6c757d;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }

    /* ── Result card ── */
    .result-card {
        background: linear-gradient(135deg, #f8fff8 0%, #e8f5e9 100%);
        border: 1.5px solid #4CAF50;
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
        margin: 0.5rem 0;
    }
    .result-card-warn {
        background: linear-gradient(135deg, #fffdf5 0%, #fff3e0 100%);
        border: 1.5px solid #FF9800;
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
        margin: 0.5rem 0;
    }
    .result-card-danger {
        background: linear-gradient(135deg, #fff8f8 0%, #ffebee 100%);
        border: 1.5px solid #f44336;
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
        margin: 0.5rem 0;
    }

    /* ── Timestamp badge ── */
    .timestamp-badge {
        display: inline-block;
        background: #e3f2fd;
        color: #1565C0;
        border-radius: 20px;
        padding: 2px 12px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-bottom: 0.6rem;
    }
    .location-badge {
        display: inline-block;
        background: #f3e5f5;
        color: #6A1B9A;
        border-radius: 20px;
        padding: 2px 12px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-bottom: 0.6rem;
        margin-left: 6px;
    }

    /* ── Quality bar ── */
    .quality-row {
        display: flex;
        align-items: center;
        margin: 4px 0;
        font-size: 0.88rem;
    }
    .quality-label {
        width: 100px;
        color: #555;
    }
    .quality-bar-bg {
        flex: 1;
        height: 10px;
        background: #e0e0e0;
        border-radius: 5px;
        overflow: hidden;
        margin: 0 8px;
    }
    .quality-bar-fill {
        height: 100%;
        border-radius: 5px;
        background: #4CAF50;
    }

    /* ── Geo input styling ── */
    .geo-box {
        background: #f5f5f5;
        border-radius: 10px;
        padding: 10px 14px;
        margin-top: 6px;
    }

    /* ── Section divider ── */
    .section-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #2E7D32;
        margin: 1rem 0 0.4rem 0;
        border-left: 4px solid #4CAF50;
        padding-left: 10px;
    }

    /* ── History table ── */
    .stDataFrame { border-radius: 10px; overflow: hidden; }

    /* ── Recommendation box ── */
    .rec-box {
        background: #f9fbe7;
        border-left: 4px solid #8bc34a;
        border-radius: 8px;
        padding: 10px 14px;
        margin-top: 10px;
        font-size: 0.92rem;
    }
</style>
""", unsafe_allow_html=True)

# ─── Session State Init ──────────────────────────────────────────────────────
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []

if 'preprocessor' not in st.session_state:
    st.session_state.preprocessor = ImagePreprocessor()

if 'model' not in st.session_state:
    st.session_state.model = None

# FIX 1: Store the last analysis result in session state
#         so it persists after Streamlit re-render
if 'last_analysis' not in st.session_state:
    st.session_state.last_analysis = None

# FIX 2: Store geo values in session state so they don't reset
if 'geo_lat' not in st.session_state:
    st.session_state.geo_lat = 11.3410
if 'geo_lon' not in st.session_state:
    st.session_state.geo_lon = 77.7172

DATA_DIR = Path("crop_data")
DATA_DIR.mkdir(exist_ok=True)

# ─── Model Loader ────────────────────────────────────────────────────────────
def load_or_create_model():
    model = CropHealthModel(num_classes=4)
    if os.path.exists('crop_health_model.h5'):
        try:
            model.load_model('crop_health_model.h5')
            return model, True
        except Exception as e:
            st.warning(f"Could not load saved model: {e}")
    model.build_model()
    model.compile_model()
    return model, False

# ─── Analysis Logic ───────────────────────────────────────────────────────────
def run_analysis(image, crop_type, growth_stage, lat, lon):
    """Run analysis and return structured result dict."""
    preprocessor = st.session_state.preprocessor
    validation  = preprocessor.validate_image_quality(image)
    processed   = preprocessor.preprocess_image(image, enhance=True)

    model = st.session_state.model
    if model and model.model is not None:
        prediction = model.predict(processed)
    else:
        # Demo predictions – slightly randomised so it feels real
        import random
        classes = ['Healthy', 'Pest_Disease', 'Flood_Damage', 'Drought_Stress']
        chosen  = random.choice(classes)
        conf    = round(random.uniform(0.72, 0.94), 4)
        rest    = round((1 - conf) / 3, 4)
        probs   = {c: (conf if c == chosen else rest) for c in classes}
        sorted_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)
        prediction = {
            'predicted_class'  : chosen,
            'confidence'       : conf,
            'top_3_predictions': [{'class': k, 'confidence': v} for k, v in sorted_probs[:3]],
            'all_probabilities': probs
        }

    record = {
        'timestamp'   : datetime.now().strftime("%Y-%m-%d  %H:%M:%S"),
        'crop_type'   : crop_type,
        'growth_stage': growth_stage,
        'location'    : (lat, lon),
        'validation'  : validation,
        'prediction'  : prediction,
        'image_size'  : image.size
    }
    return record

# ─── Result Display ───────────────────────────────────────────────────────────
def display_result(analysis):
    """Render the full result panel for one analysis."""
    pred       = analysis['prediction']
    cls        = pred['predicted_class']
    conf       = pred['confidence'] * 100
    metrics    = analysis['validation']['metrics']
    qs         = metrics.get('quality_score', 0)
    ts         = analysis['timestamp']
    lat, lon   = analysis['location']

    # ── Header badges ──────────────────────────────────────────────────
    st.markdown(
        f'<span class="timestamp-badge">🕐 {ts}</span>'
        f'<span class="location-badge">📍 {lat:.4f}, {lon:.4f}</span>',
        unsafe_allow_html=True
    )

    col_q, col_p = st.columns(2)

    # ── Left: Image Quality ─────────────────────────────────────────────
    with col_q:
        st.markdown('<div class="section-title">🖼️ Image Quality</div>', unsafe_allow_html=True)

        if qs >= 70:
            st.markdown(
                f'<div class="result-card">✅ <b>Quality Score: {qs:.1f} / 100</b><br>'
                f'<span style="color:#555;font-size:0.85rem">Good quality image</span></div>',
                unsafe_allow_html=True)
        elif qs >= 50:
            st.markdown(
                f'<div class="result-card-warn">⚠️ <b>Quality Score: {qs:.1f} / 100</b><br>'
                f'<span style="color:#555;font-size:0.85rem">Acceptable, but could be better</span></div>',
                unsafe_allow_html=True)
        else:
            st.markdown(
                f'<div class="result-card-danger">❌ <b>Quality Score: {qs:.1f} / 100</b><br>'
                f'<span style="color:#555;font-size:0.85rem">Low quality – retake photo</span></div>',
                unsafe_allow_html=True)

        # Metric grid
        m1, m2 = st.columns(2)
        m1.metric("Blur Score",  f"{metrics.get('blur_score', 0):.0f}")
        m1.metric("Brightness",  f"{metrics.get('brightness', 0):.0f}")
        m2.metric("Contrast",    f"{metrics.get('contrast', 0):.0f}")
        m2.metric("Resolution",  f"{metrics.get('width',0)}×{metrics.get('height',0)}")

        issues = analysis['validation'].get('issues', [])
        if issues:
            with st.expander("⚠️ Quality issues detected"):
                for i in issues:
                    st.write(f"• {i}")

    # ── Right: AI Prediction ────────────────────────────────────────────
    with col_p:
        st.markdown('<div class="section-title">🤖 AI Prediction</div>', unsafe_allow_html=True)

        if 'Healthy' in cls:
            card_cls = "result-card"
            icon     = "✅"
        elif 'Flood' in cls:
            card_cls = "result-card-danger"
            icon     = "🌊"
        else:
            card_cls = "result-card-warn"
            icon     = "⚠️"

        st.markdown(
            f'<div class="{card_cls}">'
            f'{icon} <b style="font-size:1.15rem">{cls.replace("_"," ")}</b><br>'
            f'<span style="font-size:0.9rem;color:#333">Confidence: <b>{conf:.1f}%</b></span>'
            f'</div>',
            unsafe_allow_html=True
        )

        st.markdown("**Top 3 Predictions**")
        for i, p in enumerate(pred['top_3_predictions'], 1):
            label = f"{i}. {p['class'].replace('_',' ')}  –  {p['confidence']*100:.1f}%"
            st.progress(float(p['confidence']), text=label)

        with st.expander("📊 All class probabilities"):
            prob_df = pd.DataFrame([
                {'Class': k.replace('_', ' '), 'Probability': f"{v*100:.2f}%"}
                for k, v in pred['all_probabilities'].items()
            ])
            st.dataframe(prob_df, use_container_width=True, hide_index=True)

    # ── Recommendations ─────────────────────────────────────────────────
    st.markdown('<div class="section-title">💡 Recommendations</div>', unsafe_allow_html=True)

    recs = {
        'Healthy': [
            "Crop appears healthy. Continue regular monitoring.",
            "Maintain current irrigation and fertiliser schedule.",
            "Schedule next inspection in 7–10 days."
        ],
        'Pest_Disease': [
            "Possible pest or disease detected.",
            "Consult an agricultural extension officer immediately.",
            "Apply appropriate pesticides or fungicides.",
            "Monitor spread to neighbouring plants."
        ],
        'Flood_Damage': [
            "Flood damage indicators detected.",
            "Improve field drainage where possible.",
            "Apply growth promoters after water recedes.",
            "Monitor for secondary fungal infections."
        ],
        'Drought_Stress': [
            "Drought stress detected.",
            "Increase irrigation frequency.",
            "Apply mulching to retain soil moisture.",
            "Consider foliar spray of water-retention products."
        ]
    }

    tips = recs.get(cls, recs['Healthy'])
    rec_html = "".join(f"<li>{t}</li>" for t in tips)
    st.markdown(
        f'<div class="rec-box"><ul style="margin:0;padding-left:18px">{rec_html}</ul></div>',
        unsafe_allow_html=True
    )

# ─── Map View ─────────────────────────────────────────────────────────────────
def display_map():
    history = st.session_state.analysis_history
    if not history:
        st.info("No analyses yet. Upload images to see locations here.")
        return

    lats = [r['location'][0] for r in history]
    lons = [r['location'][1] for r in history]
    m    = folium.Map(location=[np.mean(lats), np.mean(lons)], zoom_start=11)

    color_map = {
        'Healthy'       : 'green',
        'Pest_Disease'  : 'orange',
        'Flood_Damage'  : 'blue',
        'Drought_Stress': 'red'
    }

    for rec in history:
        lat, lon  = rec['location']
        cls       = rec['prediction']['predicted_class']
        conf      = rec['prediction']['confidence'] * 100
        color     = color_map.get(cls, 'gray')

        popup_html = f"""
        <div style="min-width:180px;font-family:sans-serif">
          <b style="font-size:1rem">{rec['crop_type']}</b><br>
          <span style="color:#555">Stage: {rec['growth_stage']}</span><hr style="margin:4px 0">
          <b>Status:</b> {cls.replace('_',' ')}<br>
          <b>Confidence:</b> {conf:.1f}%<br>
          <b>Quality:</b> {rec['validation']['metrics']['quality_score']:.0f}/100<br>
          <hr style="margin:4px 0">
          <span style="color:#888;font-size:0.8rem">🕐 {rec['timestamp']}</span><br>
          <span style="color:#888;font-size:0.8rem">📍 {lat:.4f}, {lon:.4f}</span>
        </div>
        """

        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=260),
            tooltip=f"{rec['crop_type']} – {cls.replace('_',' ')}",
            icon=folium.Icon(color=color, icon='leaf', prefix='fa')
        ).add_to(m)

    st_folium(m, width=None, height=480, returned_objects=[])

# ─── Main Interface ───────────────────────────────────────────────────────────
def main_interface():
    st.markdown('<div class="main-header">🌾 CROPIC Crop Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">AI-Powered Crop Health Monitoring System</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📸  Capture & Analyze", "📊  Dashboard", "ℹ️  About"])

    # ══════════════════════════════════════════════════════════════════════
    # TAB 1 – Capture & Analyze
    # ══════════════════════════════════════════════════════════════════════
    with tab1:
        uploaded = st.file_uploader(
            "Upload a crop image (JPG / PNG)",
            type=['jpg', 'jpeg', 'png'],
            help="Take a clear, well-lit photo of the crop"
        )

        if uploaded:
            image = Image.open(uploaded)

            left, right = st.columns([1, 1])

            # ── Image preview ───────────────────────────────────────────
            with left:
                st.image(image, caption="Uploaded Image", use_container_width=True)
                st.caption(f"Size: {image.size[0]}×{image.size[1]} px  |  Mode: {image.mode}")

            # ── Field form ──────────────────────────────────────────────
            with right:
                st.markdown('<div class="section-title">📋 Field Information</div>', unsafe_allow_html=True)

                crop_type    = st.selectbox("Crop Type",
                    ["Rice","Wheat","Maize","Cotton","Sugarcane","Tomato","Potato","Other"])
                growth_stage = st.selectbox("Growth Stage",
                    ["Seedling","Vegetative","Flowering","Fruiting","Maturity"])

                # ── FIX 3: Geo-tagging stays stable ─────────────────────
                # Store lat/lon in session_state BEFORE the button press.
                # Use on_change callbacks so values survive re-runs.
                st.markdown('<div class="section-title">📍 Geo-location</div>', unsafe_allow_html=True)

                st.markdown(
                    '<div style="font-size:0.82rem;color:#888;margin-bottom:6px">'
                    'Tip: Right-click any location on Google Maps → "What\'s here?" to get coordinates.'
                    '</div>',
                    unsafe_allow_html=True
                )

                g1, g2 = st.columns(2)
                with g1:
                    lat = st.number_input(
                        "Latitude",
                        value=st.session_state.geo_lat,
                        format="%.6f",
                        step=0.0001,
                        key="lat_input",
                        help="North–South coordinate (e.g. 11.3410)"
                    )
                    st.session_state.geo_lat = lat   # persist immediately

                with g2:
                    lon = st.number_input(
                        "Longitude",
                        value=st.session_state.geo_lon,
                        format="%.6f",
                        step=0.0001,
                        key="lon_input",
                        help="East–West coordinate (e.g. 77.7172)"
                    )
                    st.session_state.geo_lon = lon   # persist immediately

                st.caption(f"📍 Current: ({lat:.6f}, {lon:.6f})")

                st.markdown("<br>", unsafe_allow_html=True)
                analyze_clicked = st.button(
                    "🔍  Analyze Crop Health",
                    type="primary",
                    use_container_width=True
                )

            # ── FIX 1: Analyze and save to session_state ─────────────────
            if analyze_clicked:
                with st.spinner("Analysing image..."):
                    result = run_analysis(image, crop_type, growth_stage, lat, lon)
                    st.session_state.last_analysis = result          # ← persist result
                    st.session_state.analysis_history.append(result) # ← save to history

            # ── FIX 1: Always render last result (survives re-runs) ──────
            if st.session_state.last_analysis is not None:
                st.markdown("---")
                st.markdown("### 📊 Analysis Result")
                display_result(st.session_state.last_analysis)

                # ── FIX 2: Timestamp prominently shown ──────────────────
                ts = st.session_state.last_analysis['timestamp']
                st.success(f"✅ Analysis complete  |  🕐 Analysed at: {ts}")

        else:
            # Friendly placeholder when no image is uploaded
            st.markdown("""
            <div style="
                text-align:center;padding:3rem 1rem;
                background:#f9fbe7;border-radius:14px;
                border:2px dashed #aed581;color:#558B2F">
              <div style="font-size:3rem">📷</div>
              <div style="font-size:1.1rem;font-weight:600;margin-top:0.5rem">Upload a Crop Image to Begin</div>
              <div style="font-size:0.9rem;color:#777;margin-top:0.4rem">
                Supported formats: JPG, JPEG, PNG
              </div>
            </div>
            """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════
    # TAB 2 – Dashboard
    # ══════════════════════════════════════════════════════════════════════
    with tab2:
        st.markdown("### 📊 Analysis Dashboard")

        history = st.session_state.analysis_history

        if not history:
            st.info("📭 No data yet. Go to 'Capture & Analyse' to analyse your first image.")
        else:
            total   = len(history)
            healthy = sum(1 for r in history if 'Healthy' in r['prediction']['predicted_class'])
            avg_q   = np.mean([r['validation']['metrics']['quality_score'] for r in history])
            h_rate  = healthy / total * 100

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Analyses",  total)
            c2.metric("Healthy Crops",   f"{healthy}/{total}")
            c3.metric("Avg Image Quality", f"{avg_q:.1f}/100")
            c4.metric("Health Rate",     f"{h_rate:.1f}%")

            st.markdown("---")
            st.markdown("### 🗺️ Geographic Distribution")
            display_map()

            st.markdown("---")
            st.markdown("### 📜 Analysis History")

            # Build table – FIX 2: include timestamp column
            rows = []
            for r in reversed(history):   # newest first
                rows.append({
                    '🕐 Date & Time'  : r['timestamp'],
                    '🌾 Crop'         : r['crop_type'],
                    '🌱 Stage'        : r['growth_stage'],
                    '📍 Location'     : f"{r['location'][0]:.4f}, {r['location'][1]:.4f}",
                    '🤖 Status'       : r['prediction']['predicted_class'].replace('_', ' '),
                    '💯 Confidence'   : f"{r['prediction']['confidence']*100:.1f}%",
                    '🖼️ Quality'      : f"{r['validation']['metrics']['quality_score']:.0f}/100"
                })

            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Export
            st.markdown("---")

            def make_serializable(obj):
                if isinstance(obj, tuple): return list(obj)
                raise TypeError

            json_str = json.dumps(history, default=make_serializable, indent=2)
            st.download_button(
                label="📥 Download Full Report (JSON)",
                data=json_str,
                file_name=f"cropic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

    # ══════════════════════════════════════════════════════════════════════
    # TAB 3 – About
    # ══════════════════════════════════════════════════════════════════════
    with tab3:
        st.markdown("### 🌾 About CROPIC Crop Analytics System")

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("""
**Inspired by the CROPIC Initiative**, this prototype demonstrates AI-powered
crop health monitoring using deep learning and transfer learning.

#### 🎯 Key Modules
1. **Mobile Capture Module** – upload images, record geo-location, select crop & stage
2. **AI/ML Analytics** – MobileNetV2 transfer learning, 4-class classification
3. **Web Dashboard** – map visualisation, history, data export

#### 🔬 Technical Stack
| Component | Technology |
|-----------|-----------|
| Deep Learning | TensorFlow 2.15 · MobileNetV2 |
| Web Framework | Streamlit |
| Image Processing | OpenCV · Pillow |
| Maps | Folium |
| Language | Python 3.9+ |

#### 📊 Model Architecture
- **Base:** MobileNetV2 (ImageNet pre-trained)
- **Head:** GlobalAvgPool → Dense(256) → Dropout → Dense(4/Softmax)
- **Input:** 224 × 224 × 3 RGB
- **Classes:** Healthy · Pest/Disease · Flood · Drought
""")

        with col_b:
            st.markdown("""
#### 💡 Tips for Best Results
- 📸 Good natural daylight
- 🎯 Crop fills the frame
- 🔍 Photo in focus (not blurry)
- 📐 1–2 feet from the crop
- ☀️ Avoid harsh shadows / glare

#### 📍 How to Get GPS Coordinates
1. Open **Google Maps**
2. Right-click your field location
3. Click **"What's here?"**
4. Copy the numbers (e.g. `11.3410, 77.7172`)
5. Paste into the Latitude / Longitude fields

#### 🚀 Getting Real Predictions
Currently running in **demo mode**.  
To enable real AI predictions:
1. Collect crop images per class
2. Run `python train_my_model.py`
3. Restart this app — model loads automatically!
""")

        st.markdown("---")
        st.markdown("### 🔧 System Status")
        s1, s2 = st.columns(2)
        model_ok = st.session_state.model and st.session_state.model.model
        s1.info(f"**AI Model:** {'✅ Trained model loaded' if model_ok else '⚠️ Demo mode (no trained model)'}")
        s1.info(f"**Analyses done:** {len(st.session_state.analysis_history)}")
        s2.info("**Image Preprocessor:** ✅ Active")
        s2.info("**Geo-tagging:** ✅ Enabled (manual entry)")

# ─── Entry Point ─────────────────────────────────────────────────────────────
def main():
    # Load model once
    if st.session_state.model is None:
        with st.spinner("Loading system..."):
            model, loaded = load_or_create_model()
            st.session_state.model = model

    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/180x60/2E7D32/ffffff?text=CROPIC", use_container_width=True)
        st.markdown("---")

        model_ok = st.session_state.model and st.session_state.model.model
        if model_ok:
            st.success("✅ Trained model active")
        else:
            st.warning("⚠️ Demo mode\n\nTrain a model for real predictions.")

        st.markdown("---")
        st.markdown("### 🎛️ Controls")
        if st.button("🗑️ Clear All History", use_container_width=True):
            st.session_state.analysis_history = []
            st.session_state.last_analysis    = None
            st.rerun()

        st.markdown("---")
        st.markdown("### 📚 Model Info")
        st.write("**Architecture:** MobileNetV2")
        st.write("**Input:** 224 × 224 × 3")
        st.write("**Classes:** 4")
        if model_ok:
            st.write(f"**Parameters:** {st.session_state.model.model.count_params():,}")

    main_interface()

if __name__ == "__main__":
    main()
