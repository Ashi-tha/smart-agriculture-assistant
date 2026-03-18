"""
Train Crop Recommendation Model (Random Forest Classifier)
Dataset schema matches Kaggle "Crop Recommendation Dataset"
Features: N, P, K, temperature, humidity, ph, rainfall
Labels: 22 crops
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

# ─── Synthetic dataset matching Kaggle Crop Recommendation Dataset schema ──────
# 22 crops, realistic ranges for Indian agriculture
np.random.seed(42)

crop_profiles = {
    "rice":        {"N":(80,100),"P":(40,60), "K":(40,50),"temp":(20,27),"hum":(80,90),"ph":(5.5,7.0),"rain":(200,300)},
    "maize":       {"N":(70,90), "P":(45,65), "K":(40,55),"temp":(18,27),"hum":(55,70),"ph":(5.5,7.5),"rain":(55,100)},
    "chickpea":    {"N":(35,50), "P":(65,80), "K":(75,90),"temp":(15,25),"hum":(14,25),"ph":(5.5,7.0),"rain":(45,65)},
    "kidneybeans": {"N":(15,25), "P":(55,70), "K":(15,25),"temp":(15,22),"hum":(18,24),"ph":(5.5,7.0),"rain":(100,115)},
    "pigeonpeas":  {"N":(15,25), "P":(65,75), "K":(30,40),"temp":(25,35),"hum":(40,50),"ph":(5.0,7.0),"rain":(145,160)},
    "mothbeans":   {"N":(15,25), "P":(40,50), "K":(15,25),"temp":(24,32),"hum":(44,52),"ph":(3.5,6.5),"rain":(45,55)},
    "mungbean":    {"N":(15,25), "P":(45,60), "K":(15,25),"temp":(25,38),"hum":(80,90),"ph":(6.2,7.2),"rain":(40,55)},
    "blackgram":   {"N":(35,45), "P":(60,70), "K":(15,25),"temp":(25,35),"hum":(63,70),"ph":(6.0,7.5),"rain":(65,75)},
    "lentil":      {"N":(15,25), "P":(60,70), "K":(15,25),"temp":(17,23),"hum":(63,70),"ph":(6.0,7.5),"rain":(40,50)},
    "pomegranate": {"N":(15,25), "P":(15,25), "K":(195,210),"temp":(18,27),"hum":(88,95),"ph":(5.5,7.2),"rain":(105,125)},
    "banana":      {"N":(95,110),"P":(70,80), "K":(48,58),"temp":(25,35),"hum":(78,87),"ph":(5.5,7.0),"rain":(90,110)},
    "mango":       {"N":(15,25), "P":(15,25), "K":(15,25),"temp":(24,30),"hum":(47,57),"ph":(5.5,7.5),"rain":(90,110)},
    "grapes":      {"N":(15,25), "P":(15,25), "K":(15,25),"temp":(8,30), "hum":[15,25], "ph":(5.5,7.0),"rain":[65,75]},
    "watermelon":  {"N":(99,110),"P":(15,25), "K":[48,58],"temp":(24,30),"hum":(80,90),"ph":(5.5,7.5),"rain":(45,55)},
    "muskmelon":   {"N":(99,110),"P":[15,25], "K":[47,57],"temp":(28,32),"hum":(90,95),"ph":(6.0,7.0),"rain":(24,30)},
    "apple":       {"N":[15,25], "P":[125,140],"K":[195,210],"temp":(20,24),"hum":(90,95),"ph":(5.5,6.5),"rain":[110,125]},
    "orange":      {"N":[15,25], "P":[15,25], "K":[8,25],  "temp":(10,15),"hum":(90,100),"ph":(6.0,7.5),"rain":[100,115]},
    "papaya":      {"N":[48,58], "P":[58,68], "K":[48,58], "temp":(33,38),"hum":(90,95),"ph":(6.5,7.5),"rain":[140,155]},
    "coconut":     {"N":[15,25], "P":[15,25], "K":[28,38], "temp":(25,28),"hum":(90,98),"ph":(5.5,7.0),"rain":[140,155]},
    "cotton":      {"N":[115,130],"P":[45,60],"K":[40,55], "temp":(23,37),"hum":[75,85],"ph":(5.8,7.0),"rain":[60,75]},
    "jute":        {"N":[68,82],  "P":[45,55],"K":[38,48], "temp":(24,37),"hum":[70,90],"ph":(6.0,7.5),"rain":[160,200]},
    "coffee":      {"N":[98,108], "P":[28,38],"K":[28,38], "temp":(22,28),"hum":[55,65],"ph":(6.0,6.5),"rain":[150,175]},
}

def sample_crop(name, profile, n_samples=100):
    rows = []
    for _ in range(n_samples):
        rows.append({
            "N": np.random.uniform(*profile["N"]),
            "P": np.random.uniform(*profile["P"]),
            "K": np.random.uniform(*profile["K"]),
            "temperature": np.random.uniform(*profile["temp"]),
            "humidity": np.random.uniform(*profile["hum"]),
            "ph": np.random.uniform(*profile["ph"]),
            "rainfall": np.random.uniform(*profile["rain"]),
            "label": name,
        })
    return rows

all_rows = []
for crop, profile in crop_profiles.items():
    all_rows.extend(sample_crop(crop, profile, 100))

df = pd.DataFrame(all_rows)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

X = df[["N","P","K","temperature","humidity","ph","rainfall"]].values
y = df["label"].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s  = scaler.transform(X_test)

model = RandomForestClassifier(n_estimators=200, max_depth=15, random_state=42, n_jobs=-1)
model.fit(X_train_s, y_train)

preds = model.predict(X_test_s)
acc = accuracy_score(y_test, preds)
print(f"Crop Recommendation Model Accuracy: {acc*100:.2f}%")
print(classification_report(y_test, preds))

os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/crop_model.pkl")
joblib.dump(scaler, "models/crop_scaler.pkl")
print("✅ Saved: models/crop_model.pkl, models/crop_scaler.pkl")
