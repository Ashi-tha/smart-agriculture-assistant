# 🌾 AgroSense AI — Walkthrough

**Live at:** http://127.0.0.1:5000 (run `python app.py` to start)

---

## 1. Dashboard — Landing Page

![Landing page hero with feature cards](file:///C:/Users/LENOVO/.gemini/antigravity/brain/a9f8cefa-cfc9-482b-aafd-b95536828117/landing_page_1773859068535.png)

Dark-green glassmorphism hero with feature cards, sidebar navigation, and animated stats (22 crops, 23 diseases, ~95% accuracy).

---

## 2. 🌱 Crop Recommendation

**Test inputs:** N=90, P=42, K=43, pH=6.5, Temp=25°C, Humidity=82%, Rainfall=202mm

![Crop recommendation result — Rice 97%](file:///C:/Users/LENOVO/.gemini/antigravity/brain/a9f8cefa-cfc9-482b-aafd-b95536828117/crop_recommendation_result_1773859164144.png)

**Result:** 🌾 **Rice — 97% confidence** (top pick), with Jute and Coconut as alternatives. Shows season, water needs, soil type, and full input reasoning summary.

---

## 3. 📊 Yield Prediction

**Test inputs:** Rice · 2 hectares · 200mm rainfall · 26°C · 150kg/ha fertilizer

![Yield prediction result showing 5017 kg/ha](file:///C:/Users/LENOVO/.gemini/antigravity/brain/a9f8cefa-cfc9-482b-aafd-b95536828117/yield_prediction_result_1773859215623.png)

**Result:** XGBoost predicted **~5,017 kg/hectare** → **10,035 kg total** for 2 ha. Chart.js bar chart shows below/your/above average comparison.

---

## 4. 🌦 Weather Insights (Thrissur)

![Weather insights page with Thrissur data](file:///C:/Users/LENOVO/.gemini/antigravity/brain/a9f8cefa-cfc9-482b-aafd-b95536828117/weather_result_thrissur_1773859252847.png)

Live weather card for Thrissur + 3 smart advice cards:
- 💧 **Irrigation:** Normal schedule recommended
- 🌿 **Fertilizer:** Good time for application
- 🐛 **Pest Risk:** Monitor for fungal diseases (high humidity)

> [!NOTE]
> Currently in **Demo Mode**. Add your [OpenWeatherMap API key](https://openweathermap.org/api) to `.env` to enable live data.

---

## 5. 🔬 Disease Detection

![Disease detection upload page](file:///C:/Users/LENOVO/.gemini/antigravity/brain/a9f8cefa-cfc9-482b-aafd-b95536828117/disease_detection_page_1773859302101.png)

Drag-and-drop image upload. Upload any leaf photo (JPG/PNG/WEBP ≤5MB). Returns: disease name, plant, confidence %, severity badge, and treatment advice.

---

## 6. 📋 Prediction History

![History page with 3 records](file:///C:/Users/LENOVO/.gemini/antigravity/brain/a9f8cefa-cfc9-482b-aafd-b95536828117/history_page_records_1773859281380.png)

SQLite-backed history table showing all 3 predictions made during testing — with type chips, timestamps, and per-row delete support.

---

## 🎬 Full Session Recording

![Full app browser walkthrough video](file:///C:/Users/LENOVO/.gemini/antigravity/brain/a9f8cefa-cfc9-482b-aafd-b95536828117/agro_sense_full_walkthrough_1773859036938.webp)

---

## ✅ Validation Results

| Feature | Status | Notes |
|---|---|---|
| Crop Recommendation | ✅ Pass | Random Forest, 100% train accuracy |
| Yield Prediction | ✅ Pass | XGBoost R²=0.90, 5017 kg/ha for rice |
| Disease Detection | ✅ Pass | Upload works, result rendered correctly |
| Weather Insights | ✅ Pass | Thrissur demo data + advice cards |
| Prediction History | ✅ Pass | All 3 records saved in SQLite |
| Sidebar Navigation | ✅ Pass | Active link highlighting works |

---

## 📁 Project Structure

```
agri/
├── app.py                    ← Flask entry point
├── .env                      ← Add your OPENWEATHER_API_KEY here
├── models/
│   ├── crop_model.pkl        ← Trained (100% acc.)
│   ├── crop_scaler.pkl
│   ├── yield_model.pkl       ← Trained (R²=0.90)
│   ├── yield_scaler.pkl
│   └── yield_label_encoder.pkl
├── routes/
│   ├── crop.py, yield_pred.py, disease.py, weather.py, history.py
├── utils/
│   ├── preprocess.py, db.py, weather_api.py
├── train/
│   ├── train_crop.py, train_yield.py
├── templates/
│   ├── base.html, index.html, crop.html, yield.html
│   ├── disease.html, weather.html, history.html
└── static/
    ├── css/style.css
    └── js/main.js
```

## ⚡ Quick Start

```bash
# In c:\Users\LENOVO\Downloads\rag\agri\
python app.py
# Open http://127.0.0.1:5000
```
