"""
Train Yield Prediction Model (XGBoost Regressor)
Features: crop (encoded), area (hectares), rainfall, temperature, fertilizer_used
Target: yield_kg_per_hectare
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
import xgboost as xgb
import joblib
import os

np.random.seed(42)

# Realistic yield ranges (kg/hectare) for Indian agriculture
crop_yield = {
    "rice":        (2500, 6000),
    "maize":       (2000, 5500),
    "chickpea":    (800,  2000),
    "kidneybeans": (600,  1800),
    "pigeonpeas":  (700,  1500),
    "mothbeans":   (400,  1200),
    "mungbean":    (600,  1400),
    "blackgram":   (500,  1200),
    "lentil":      (700,  1800),
    "pomegranate": (8000, 20000),
    "banana":      (20000,45000),
    "mango":       (5000, 15000),
    "grapes":      (8000, 25000),
    "watermelon":  (15000,35000),
    "muskmelon":   (10000,25000),
    "apple":       (5000, 20000),
    "orange":      (8000, 20000),
    "papaya":      (20000,40000),
    "coconut":     (5000, 12000),
    "cotton":      (400,  1200),
    "jute":        (1500, 3000),
    "coffee":      (600,  1500),
}

rows = []
for crop, (ymin, ymax) in crop_yield.items():
    for _ in range(200):
        area        = np.random.uniform(0.5, 10)
        rainfall    = np.random.uniform(40, 300)
        temperature = np.random.uniform(15, 40)
        fertilizer  = np.random.uniform(50, 300)  # kg/hectare

        # yield influenced by all features
        base = np.random.uniform(ymin, ymax)
        rain_factor  = 1 + 0.001 * (rainfall - 100)
        temp_factor  = 1 - 0.003 * abs(temperature - 25)
        fert_factor  = 1 + 0.0005 * fertilizer
        yield_val = base * rain_factor * temp_factor * fert_factor
        yield_val = max(yield_val, ymin * 0.5)

        rows.append({
            "crop":        crop,
            "area":        area,
            "rainfall":    rainfall,
            "temperature": temperature,
            "fertilizer":  fertilizer,
            "yield":       yield_val,
        })

df = pd.DataFrame(rows).sample(frac=1, random_state=42).reset_index(drop=True)

le = LabelEncoder()
df["crop_enc"] = le.fit_transform(df["crop"])

features = ["crop_enc","area","rainfall","temperature","fertilizer"]
X = df[features].values
y = df["yield"].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s  = scaler.transform(X_test)

model = xgb.XGBRegressor(n_estimators=300, max_depth=6, learning_rate=0.05,
                          subsample=0.8, colsample_bytree=0.8, random_state=42)
model.fit(X_train_s, y_train, eval_set=[(X_test_s, y_test)], verbose=False)

preds = model.predict(X_test_s)
mae = mean_absolute_error(y_test, preds)
r2  = r2_score(y_test, preds)
print(f"Yield Model — MAE: {mae:.2f} kg/ha, R²: {r2:.4f}")

os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/yield_model.pkl")
joblib.dump(scaler, "models/yield_scaler.pkl")
joblib.dump(le, "models/yield_label_encoder.pkl")
print("✅ Saved: models/yield_model.pkl, models/yield_scaler.pkl, models/yield_label_encoder.pkl")
