"""
CROPIC AI - Comprehensive Agricultural Intelligence Platform
Integrates: Crop Insurance + Climate Modeling + Disease Management + 
           Soil Analysis + Market Forecasting + Crop Recommendations
"""

import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import json, os, hashlib, base64
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px

from image_preprocessor import ImagePreprocessor
from model_training import CropHealthModel

st.set_page_config(
    page_title="Agrisense - Agricultural Intelligence",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ═══════════════════════════════════════════════════════════════════════════════
# ENHANCED CSS - Modern Agricultural Tech Theme
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');

*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html,body,[class*="css"]{font-family:'Outfit',sans-serif;background:#0a1612;color:#e8f5e9}

/* ── Main container ── */
.main-wrap{
  background:linear-gradient(135deg,#0a1612 0%,#1a2e23 100%);
  min-height:100vh;
}

/* ── Header nav ── */
.main-nav{
  background:linear-gradient(135deg,#1e4d2b,#2e7d32);
  padding:0.9rem 2rem;display:flex;align-items:center;justify-content:space-between;
  border-bottom:3px solid #4caf50;box-shadow:0 6px 30px rgba(76,175,80,0.4);
  position:sticky;top:0;z-index:999;
}
.nav-logo{font-family:'Space Grotesk',monospace;font-size:1.7rem;
  font-weight:800;color:#fff;letter-spacing:-0.5px}
.nav-user{color:#c8e6c9;font-size:0.88rem}
.nav-badge{background:rgba(255,255,255,0.15);border-radius:20px;
  padding:3px 12px;font-size:0.75rem;font-weight:700;color:#fff;margin-left:8px}

/* ── Dashboard cards ── */
.dash-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));
  gap:1.2rem;margin:1.5rem 0}
.dash-card{background:linear-gradient(145deg,#1a2e23,#0f1f17);
  border:1px solid #2e7d3280;border-radius:16px;padding:1.4rem 1.6rem;
  transition:all 0.3s;position:relative;overflow:hidden}
.dash-card:hover{border-color:#4caf50;box-shadow:0 8px 30px rgba(76,175,80,0.3);
  transform:translateY(-4px)}
.dash-card::before{content:'';position:absolute;top:-50%;right:-50%;
  width:200%;height:200%;background:radial-gradient(circle,rgba(76,175,80,0.1),transparent);
  opacity:0;transition:opacity 0.5s}
.dash-card:hover::before{opacity:1}
.card-icon{font-size:2.5rem;margin-bottom:0.7rem;
  filter:drop-shadow(0 4px 12px rgba(76,175,80,0.5))}
.card-title{font-family:'Space Grotesk',sans-serif;font-size:1.1rem;
  font-weight:600;color:#81c784;margin-bottom:0.4rem}
.card-value{font-size:2.2rem;font-weight:800;color:#fff;
  background:linear-gradient(135deg,#4caf50,#81c784);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent}
.card-desc{font-size:0.82rem;color:#9ccc65;margin-top:0.5rem}

/* ── Module cards (larger feature cards) ── */
.module-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:1.5rem}
.module-card{background:linear-gradient(145deg,#1a3a2e,#112317);
  border:2px solid #2e7d3280;border-radius:20px;padding:2rem 2.2rem;
  cursor:pointer;transition:all 0.4s;position:relative;overflow:hidden}
.module-card::after{content:'';position:absolute;bottom:0;left:0;right:0;
  height:4px;background:linear-gradient(90deg,#4caf50,#8bc34a);
  transform:scaleX(0);transition:transform 0.4s;transform-origin:left}
.module-card:hover{border-color:#4caf50;transform:translateY(-6px);
  box-shadow:0 12px 40px rgba(76,175,80,0.4)}
.module-card:hover::after{transform:scaleX(1)}
.module-icon{font-size:3.5rem;margin-bottom:1rem;
  filter:drop-shadow(0 6px 16px rgba(139,195,74,0.6))}
.module-title{font-family:'Space Grotesk',sans-serif;font-size:1.4rem;
  font-weight:700;color:#fff;margin-bottom:0.8rem}
.module-desc{font-size:0.95rem;color:#aed581;line-height:1.6;margin-bottom:1.2rem}
.module-features{list-style:none;padding:0}
.module-features li{font-size:0.85rem;color:#c5e1a5;padding:0.3rem 0;
  padding-left:1.5rem;position:relative}
.module-features li::before{content:'✓';position:absolute;left:0;
  color:#4caf50;font-weight:700}

/* ── Section headers ── */
.sec-head{font-family:'Space Grotesk',sans-serif;font-size:1.5rem;
  font-weight:700;color:#fff;margin:2rem 0 1rem;
  padding-bottom:0.6rem;border-bottom:3px solid #4caf50;
  background:linear-gradient(90deg,#4caf50,transparent);
  padding-left:1rem}

/* ── Info panels ── */
.info-panel{background:linear-gradient(135deg,#1a2e23,#0f1f17);
  border-left:4px solid #4caf50;border-radius:12px;
  padding:1.2rem 1.5rem;margin:1rem 0}
.info-panel.warning{border-left-color:#ff9800}
.info-panel.danger{border-left-color:#f44336}
.info-panel.info{border-left-color:#2196f3}

/* ── Charts container ── */
.chart-container{background:linear-gradient(145deg,#1a2e23,#0f1f17);
  border:1px solid #2e7d3280;border-radius:16px;padding:1.5rem;margin:1rem 0}

/* ── Tabs styling ── */
.stTabs [data-baseweb="tab-list"]{gap:1rem;background:transparent}
.stTabs [data-baseweb="tab"]{background:linear-gradient(135deg,#1a2e23,#0f1f17);
  border:1px solid #2e7d3280;border-radius:12px 12px 0 0;color:#81c784;
  font-weight:600;padding:0.8rem 1.5rem}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,#2e7d32,#388e3c);
  border-color:#4caf50;color:#fff}

/* ── Button enhancements ── */
.stButton>button{background:linear-gradient(135deg,#2e7d32,#388e3c);
  color:#fff;border:none;border-radius:10px;padding:0.7rem 1.8rem;
  font-weight:600;font-size:0.95rem;transition:all 0.3s;
  box-shadow:0 4px 16px rgba(76,175,80,0.3)}
.stButton>button:hover{background:linear-gradient(135deg,#388e3c,#4caf50);
  box-shadow:0 6px 24px rgba(76,175,80,0.5);transform:translateY(-2px)}

/* ── Metric displays ── */
.metric-box{background:linear-gradient(135deg,#1a3a2e,#0d1f14);
  border:1px solid #4caf5080;border-radius:14px;padding:1.2rem 1.4rem;
  text-align:center}
.metric-label{font-size:0.78rem;color:#81c784;margin-bottom:0.4rem;
  text-transform:uppercase;letter-spacing:1px}
.metric-value{font-size:2rem;font-weight:800;color:#fff;
  background:linear-gradient(135deg,#4caf50,#8bc34a);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent}
.metric-change{font-size:0.8rem;margin-top:0.4rem}
.metric-change.up{color:#4caf50}
.metric-change.down{color:#f44336}

/* ── Recommendation cards ── */
.rec-card{background:linear-gradient(145deg,#1e3a2f,#132619);
  border-left:4px solid #8bc34a;border-radius:14px;
  padding:1.2rem 1.5rem;margin:0.8rem 0}
.rec-title{font-weight:700;color:#aed581;margin-bottom:0.6rem;font-size:1.05rem}
.rec-content{color:#c5e1a5;line-height:1.6;font-size:0.92rem}

/* ── Progress bars ── */
.progress-container{background:#0d1f14;border-radius:20px;overflow:hidden;height:12px}
.progress-bar{height:100%;background:linear-gradient(90deg,#4caf50,#8bc34a);
  border-radius:20px;transition:width 0.6s ease}

/* ── Loading animation ── */
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.5}}
.loading{animation:pulse 2s infinite}

/* ── Tooltips ── */
.tooltip{position:relative;display:inline-block;cursor:help}
.tooltip .tooltiptext{visibility:hidden;background:#2e7d32;color:#fff;
  text-align:center;border-radius:8px;padding:6px 12px;position:absolute;
  z-index:1;bottom:125%;left:50%;transform:translateX(-50%);
  font-size:0.8rem;white-space:nowrap;opacity:0;transition:opacity 0.3s}
.tooltip:hover .tooltiptext{visibility:visible;opacity:1}

/* ── Tables ── */
.stDataFrame{border-radius:12px;overflow:hidden}
table{background:linear-gradient(145deg,#1a2e23,#0f1f17)!important}
th{background:linear-gradient(135deg,#2e7d32,#388e3c)!important;
  color:#fff!important;font-weight:600!important}
td{border-color:#2e7d3240!important;color:#c8e6c9!important}
tr:hover{background:#1a3a2e40!important}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# DATA & UTILITIES (same as before)
# ═══════════════════════════════════════════════════════════════════════════════
DATA_DIR = Path("cropic_data"); DATA_DIR.mkdir(exist_ok=True)
USERS_FILE = DATA_DIR/"users.json"; ANALYSES_FILE = DATA_DIR/"analyses.json"

SEED_USERS = [
    {"username":"farmer1","password":hashlib.md5(b"farmer123").hexdigest(),"role":"farmer",
     "full_name":"Rajesh Kumar","phone":"9876543210",
     "address":"45 Paddy Lane, Thanjavur, TN-613001","land_acres":"4.5",
     "bank_account":"SBI-XXXX-4521","crop_types":"Rice, Sugarcane"},
    {"username":"official1","password":hashlib.md5(b"official123").hexdigest(),"role":"official",
     "full_name":"Dr. S. Venkatesh","phone":"9988776655",
     "department":"Agriculture Insurance Division","designation":"Senior Inspector"},
]

def load_json(p,d): return json.load(open(p)) if p.exists() else d
def save_json(p,d):
    with open(p,"w") as f: json.dump(d,f,indent=2,default=str)
def init_db():
    if not USERS_FILE.exists(): save_json(USERS_FILE,SEED_USERS)
def hash_pw(pw): return hashlib.md5(pw.encode()).hexdigest()
def username_exists(u): return any(x["username"]==u for x in load_json(USERS_FILE,[]))
def authenticate(u,p):
    for x in load_json(USERS_FILE,[]):
        if x["username"]==u and x["password"]==hash_pw(p): return x
    return None
def register_user(data):
    users=load_json(USERS_FILE,[])
    if any(u["username"]==data["username"] for u in users):
        return False,"Username exists"
    data["password"]=hash_pw(data["password"])
    data["registered_on"]=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    users.append(data); save_json(USERS_FILE,users)
    return True,"Account created!"

for k,v in [("logged_in",False),("user",None),("model",None),
            ("geo_lat",11.3410),("geo_lon",77.7172),("current_module","dashboard")]:
    if k not in st.session_state: st.session_state[k]=v

# ═══════════════════════════════════════════════════════════════════════════════
# AI SIMULATION ENGINES (Demo implementations - replace with real APIs in production)
# ═══════════════════════════════════════════════════════════════════════════════

def simulate_climate_forecast(lat, lon, days=7):
    """Simulate climate/weather forecast using simple patterns"""
    base_temp = 28 + np.random.uniform(-3,3)
    base_rain = 2 + np.random.uniform(0,8)
    
    dates = [(datetime.now() + timedelta(days=i)).strftime("%d %b") for i in range(days)]
    temps = [round(base_temp + np.random.normal(0,2),1) for _ in range(days)]
    rainfall = [round(max(0, base_rain + np.random.normal(0,3)),1) for _ in range(days)]
    humidity = [round(65 + np.random.uniform(-10,15),1) for _ in range(days)]
    
    return {
        "dates": dates,
        "temperature": temps,
        "rainfall": rainfall,
        "humidity": humidity,
        "alerts": [
            {"type":"Heavy Rain","desc":"Expected rainfall >50mm on Day 4-5","severity":"warning"},
            {"type":"Optimal Sowing","desc":"Days 1-3 ideal for planting","severity":"success"}
        ] if rainfall[3]>7 else []
    }

def simulate_soil_analysis(lat, lon):
    """Simulate soil testing results"""
    return {
        "ph": round(6.2 + np.random.uniform(-0.5,0.8),2),
        "nitrogen": round(180 + np.random.uniform(-40,60),0),
        "phosphorus": round(25 + np.random.uniform(-10,15),0),
        "potassium": round(210 + np.random.uniform(-50,70),0),
        "organic_matter": round(2.8 + np.random.uniform(-0.5,1.0),2),
        "moisture": round(22 + np.random.uniform(-5,8),1),
        "ec": round(0.4 + np.random.uniform(-0.1,0.2),2),
        "texture": np.random.choice(["Loam","Clay Loam","Sandy Loam"]),
        "health_score": round(72 + np.random.uniform(-10,18),0),
        "recommendations": [
            {"nutrient":"Nitrogen","status":"Moderate","action":"Apply 20kg/acre urea before sowing"},
            {"nutrient":"Phosphorus","status":"Low","action":"Apply 15kg/acre DAP"},
            {"nutrient":"pH","status":"Optimal","action":"Maintain current levels"}
        ]
    }

def simulate_disease_risk(crop, weather_data):
    """Simulate disease risk assessment based on crop and weather"""
    diseases = {
        "Rice": [
            {"name":"Blast","risk":65,"conditions":"High humidity + temp 25-28°C"},
            {"name":"Sheath Blight","risk":45,"conditions":"Waterlogged conditions"},
            {"name":"Brown Spot","risk":30,"conditions":"Nutrient deficiency"}
        ],
        "Wheat": [
            {"name":"Rust","risk":55,"conditions":"Moderate temp + high moisture"},
            {"name":"Powdery Mildew","risk":40,"conditions":"Cool humid weather"}
        ],
        "Cotton": [
            {"name":"Bollworm","risk":70,"conditions":"Warm weather + flowering stage"},
            {"name":"Wilt","risk":35,"conditions":"Poor drainage"}
        ]
    }
    return diseases.get(crop, diseases["Rice"])

def simulate_market_forecast(crop):
    """Simulate market price forecast"""
    base_price = {"Rice":2200,"Wheat":2100,"Cotton":5800,"Sugarcane":3100,
                  "Maize":1800,"Tomato":1200}.get(crop,2000)
    
    months = [(datetime.now() + timedelta(days=30*i)).strftime("%b %Y") for i in range(6)]
    prices = [base_price]
    for i in range(5):
        change = np.random.uniform(-8,12)
        prices.append(round(prices[-1] * (1 + change/100),-1))
    
    return {
        "months": months,
        "prices": prices,
        "current": base_price,
        "forecast_3m": prices[2],
        "forecast_6m": prices[5],
        "trend": "Rising" if prices[5]>prices[0] else "Falling",
        "confidence": round(65 + np.random.uniform(0,25),0),
        "insights": [
            f"Expected demand surge during {months[2]} festival season",
            f"Weather patterns may impact supply in {months[4]}",
            "Government MSP likely to increase by 4-6% next quarter"
        ]
    }

def simulate_crop_recommendation(soil_data, climate_data, location):
    """AI-driven crop recommendation based on conditions"""
    crops = [
        {"name":"Rice","suitability":88,"reason":"Optimal pH, sufficient moisture, good climate",
         "yield_potential":"3.5-4.2 tonnes/acre","water_req":"High","duration":"120-150 days"},
        {"name":"Sugarcane","suitability":82,"reason":"Good soil health, adequate rainfall expected",
         "yield_potential":"35-45 tonnes/acre","water_req":"High","duration":"12-18 months"},
        {"name":"Cotton","suitability":75,"reason":"Suitable temperature, moderate water available",
         "yield_potential":"12-18 quintals/acre","water_req":"Medium","duration":"150-180 days"},
        {"name":"Maize","suitability":70,"reason":"Balanced nutrients, good for rotation",
         "yield_potential":"25-32 quintals/acre","water_req":"Medium","duration":"90-110 days"},
    ]
    return sorted(crops, key=lambda x:x["suitability"], reverse=True)

def simulate_irrigation_plan(crop, soil_moisture, weather_forecast):
    """Generate smart irrigation recommendations"""
    return {
        "method": "Drip irrigation recommended",
        "schedule": [
            {"day":"Mon, Wed, Fri","time":"6:00 AM","duration":"45 min","volume":"800 L/acre"},
            {"day":"Sat","time":"6:00 AM","duration":"60 min","volume":"1000 L/acre"}
        ],
        "weekly_volume": "3200 L/acre",
        "efficiency": "85%",
        "cost_saving": "₹450/week vs flood irrigation",
        "alerts": [
            "Rain expected Day 4 - skip Friday irrigation",
            "Soil moisture at 68% - reduce duration by 10 min"
        ]
    }

# ═══════════════════════════════════════════════════════════════════════════════
# NAVIGATION BAR
# ═══════════════════════════════════════════════════════════════════════════════
def show_navbar():
    u = st.session_state.user
    role_label = "🧑‍🌾 Farmer" if u["role"]=="farmer" else "🏛️ Official"
    
    st.markdown(f"""
    <div class="main-nav">
      <div class="nav-logo">🌾 CROPIC AI</div>
      <div style="flex:1;text-align:center;color:#c8e6c9;font-size:0.9rem">
        Comprehensive Agricultural Intelligence Platform
      </div>
      <div class="nav-user">
        {u['full_name']}
        <span class="nav-badge">{role_label}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚪 Logout", key="nav_logout"):
        for k in ["logged_in","user"]: st.session_state[k] = False if k=="logged_in" else None
        st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# MODULE: DASHBOARD (Overview)
# ═══════════════════════════════════════════════════════════════════════════════
def module_dashboard():
    st.markdown('<div class="sec-head">🏠 Dashboard Overview</div>', unsafe_allow_html=True)
    
    # Quick stats
    st.markdown('<div class="dash-grid">', unsafe_allow_html=True)
    cols = st.columns(4)
    stats = [
        ("🌡️","28.5°C","Current Temperature","Optimal for most crops"),
        ("💧","68%","Soil Moisture","Good hydration level"),
        ("🌾","4.5","Land (acres)","Total farmland"),
        ("📊","₹2,200","Market Price","Rice per quintal")
    ]
    for col,(icon,val,label,desc) in zip(cols,stats):
        with col:
            st.markdown(f"""
            <div class="dash-card">
              <div class="card-icon">{icon}</div>
              <div class="card-title">{label}</div>
              <div class="card-value">{val}</div>
              <div class="card-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Feature modules grid
    st.markdown('<div class="sec-head">🎯 AI-Powered Modules</div>', unsafe_allow_html=True)
    st.markdown('<div class="module-grid">', unsafe_allow_html=True)
    
    modules = [
        {
            "icon":"🌦️","title":"Climate Intelligence",
            "desc":"7-day weather forecast, rainfall prediction, temperature trends, and climate-based alerts",
            "features":["Weather Forecast","Rainfall Alerts","Temperature Trends","Climate Risk Assessment"]
        },
        {
            "icon":"🧪","title":"Soil Analysis",
            "desc":"Comprehensive soil health testing with NPK levels, pH balance, and nutrient recommendations",
            "features":["NPK Analysis","pH Testing","Moisture Levels","Fertilizer Recommendations"]
        },
        {
            "icon":"🦠","title":"Disease Management",
            "desc":"AI-powered disease detection, risk assessment, and treatment recommendations",
            "features":["Disease Detection","Risk Prediction","Treatment Plans","Pest Management"]
        },
        {
            "icon":"📈","title":"Market Insights",
            "desc":"Real-time and forecasted crop prices, demand trends, and optimal selling windows",
            "features":["Price Forecast","Demand Analysis","Best Selling Time","Market Trends"]
        },
        {
            "icon":"🌱","title":"Crop Advisor",
            "desc":"AI recommendations for best crops based on soil, climate, and market conditions",
            "features":["Crop Selection","Yield Prediction","Rotation Planning","Variety Selection"]
        },
        {
            "icon":"💧","title":"Irrigation Planner",
            "desc":"Smart irrigation scheduling based on soil moisture, weather, and crop water requirements",
            "features":["Watering Schedule","Drip/Sprinkler Plans","Water Conservation","Cost Optimization"]
        }
    ]
    
    cols = st.columns(3)
    for idx, mod in enumerate(modules):
        with cols[idx % 3]:
            st.markdown(f"""
            <div class="module-card" onclick="alert('Module: {mod['title']}')">
              <div class="module-icon">{mod['icon']}</div>
              <div class="module-title">{mod['title']}</div>
              <div class="module-desc">{mod['desc']}</div>
              <ul class="module-features">
                {"".join(f"<li>{f}</li>" for f in mod['features'])}
              </ul>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# MODULE: CLIMATE INTELLIGENCE
# ═══════════════════════════════════════════════════════════════════════════════
def module_climate():
    st.markdown('<div class="sec-head">🌦️ Climate Intelligence & Weather Forecast</div>', unsafe_allow_html=True)
    
    lat,lon = st.session_state.geo_lat, st.session_state.geo_lon
    forecast = simulate_climate_forecast(lat, lon)
    
    # Current conditions
    st.markdown("### 📍 Current Location Weather")
    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(f'<div class="metric-box"><div class="metric-label">Temperature</div><div class="metric-value">{forecast["temperature"][0]}°C</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="metric-box"><div class="metric-label">Rainfall (Today)</div><div class="metric-value">{forecast["rainfall"][0]}mm</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="metric-box"><div class="metric-label">Humidity</div><div class="metric-value">{forecast["humidity"][0]}%</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="metric-box"><div class="metric-label">Location</div><div class="metric-value" style="font-size:1.2rem">{lat:.2f}, {lon:.2f}</div></div>', unsafe_allow_html=True)
    
    # 7-day forecast charts
    st.markdown("### 📊 7-Day Forecast")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=forecast["dates"], y=forecast["temperature"],
                             mode='lines+markers', name='Temperature (°C)',
                             line=dict(color='#ff9800', width=3),
                             marker=dict(size=8)))
    fig.add_trace(go.Bar(x=forecast["dates"], y=forecast["rainfall"],
                         name='Rainfall (mm)', marker_color='#2196f3', opacity=0.6))
    fig.update_layout(
        plot_bgcolor='#0a1612', paper_bgcolor='#0a1612',
        font=dict(color='#e8f5e9'), hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Alerts
    if forecast["alerts"]:
        st.markdown("### ⚠️ Climate Alerts")
        for alert in forecast["alerts"]:
            severity_class = "warning" if alert["severity"]=="warning" else "info"
            st.markdown(f'<div class="info-panel {severity_class}"><b>{alert["type"]}</b><br>{alert["desc"]}</div>', unsafe_allow_html=True)
    
    # Agricultural advisories
    st.markdown("### 🌾 Agricultural Advisories")
    st.markdown(f"""
    <div class="rec-card">
      <div class="rec-title">Sowing Recommendation</div>
      <div class="rec-content">
        Based on forecast, Days 1-3 are optimal for planting operations. 
        Expected rainfall on Day 4-5 will provide good moisture for germination.
      </div>
    </div>
    <div class="rec-card">
      <div class="rec-title">Irrigation Planning</div>
      <div class="rec-content">
        Reduce irrigation by 40% on Days 4-6 due to expected rainfall. 
        Resume normal schedule from Day 7.
      </div>
    </div>
    <div class="rec-card">
      <div class="rec-title">Pest Risk</div>
      <div class="rec-content">
        High humidity (>70%) combined with moderate temperatures may increase 
        fungal disease risk. Monitor crops closely and apply preventive fungicides if needed.
      </div>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# MODULE: SOIL ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
def module_soil():
    st.markdown('<div class="sec-head">🧪 Soil Health Analysis</div>', unsafe_allow_html=True)
    
    soil = simulate_soil_analysis(st.session_state.geo_lat, st.session_state.geo_lon)
    
    # Overall health score
    st.markdown(f"""
    <div style="text-align:center;margin:2rem 0">
      <div style="font-size:1.2rem;color:#81c784;margin-bottom:0.5rem">Overall Soil Health Score</div>
      <div style="font-size:4rem;font-weight:800;background:linear-gradient(135deg,#4caf50,#8bc34a);
                  -webkit-background-clip:text;-webkit-text-fill-color:transparent">
        {soil['health_score']}/100
      </div>
      <div style="font-size:1rem;color:#aed581;margin-top:0.5rem">
        {'Excellent' if soil['health_score']>=80 else 'Good' if soil['health_score']>=60 else 'Moderate'}
      </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Key parameters
    st.markdown("### 📊 Soil Parameters")
    c1,c2,c3,c4 = st.columns(4)
    params = [
        (c1, "pH Level", soil['ph'], "6.0-7.0", soil['ph']>=6.0 and soil['ph']<=7.0),
        (c2, "Nitrogen (kg/ha)", soil['nitrogen'], "150-220", soil['nitrogen']>=150),
        (c3, "Phosphorus (kg/ha)", soil['phosphorus'], "20-40", soil['phosphorus']>=20),
        (c4, "Potassium (kg/ha)", soil['potassium'], "180-250", soil['potassium']>=180)
    ]
    
    for col, label, value, optimal, is_good in params:
        status = "✅ Optimal" if is_good else "⚠️ Attention"
        color = "#4caf50" if is_good else "#ff9800"
        col.markdown(f"""
        <div class="metric-box">
          <div class="metric-label">{label}</div>
          <div class="metric-value" style="font-size:1.8rem">{value}</div>
          <div style="color:{color};font-size:0.75rem;margin-top:0.4rem">{status}</div>
          <div style="color:#81c784;font-size:0.7rem">Optimal: {optimal}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("### 🔬 Additional Properties")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Organic Matter", f"{soil['organic_matter']}%")
    c2.metric("Moisture Content", f"{soil['moisture']}%")
    c3.metric("Electrical Conductivity", f"{soil['ec']} dS/m")
    c4.metric("Soil Texture", soil['texture'])
    
    # Recommendations
    st.markdown("### 💡 Nutrient Management Recommendations")
    for rec in soil['recommendations']:
        status_color = {"Optimal":"#4caf50","Moderate":"#ff9800","Low":"#f44336"}.get(rec['status'],"#2196f3")
        st.markdown(f"""
        <div class="rec-card">
          <div class="rec-title">
            <span style="color:{status_color}">●</span> {rec['nutrient']} - {rec['status']}
          </div>
          <div class="rec-content">{rec['action']}</div>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# MODULE: DISEASE MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════
def module_disease():
    st.markdown('<div class="sec-head">🦠 Disease Risk Management</div>', unsafe_allow_html=True)
    
    crop = st.selectbox("Select Crop", ["Rice","Wheat","Cotton","Maize","Sugarcane"], key="disease_crop")
    weather = simulate_climate_forecast(11.34, 77.71)
    diseases = simulate_disease_risk(crop, weather)
    
    st.markdown("### ⚠️ Disease Risk Assessment")
    
    for disease in diseases:
        risk_level = "High" if disease['risk']>=60 else "Medium" if disease['risk']>=40 else "Low"
        risk_color = "#f44336" if disease['risk']>=60 else "#ff9800" if disease['risk']>=40 else "#4caf50"
        
        st.markdown(f"""
        <div class="rec-card">
          <div class="rec-title">{disease['name']} - <span style="color:{risk_color}">{risk_level} Risk ({disease['risk']}%)</span></div>
          <div class="rec-content">
            <b>Favorable Conditions:</b> {disease['conditions']}<br><br>
            <b>Symptoms to Watch:</b> Check for discoloration, spots, wilting in affected areas<br>
            <b>Action:</b> {'Immediate preventive spray recommended' if disease['risk']>=60 else 'Monitor closely, prepare treatment' if disease['risk']>=40 else 'Regular monitoring sufficient'}
          </div>
          <div style="margin-top:0.8rem">
            <div class="progress-container">
              <div class="progress-bar" style="width:{disease['risk']}%;background:{risk_color}"></div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Treatment guidelines
    st.markdown("### 💊 Integrated Pest Management (IPM)")
    st.markdown("""
    <div class="info-panel info">
      <b>Preventive Measures:</b>
      <ul style="margin-top:0.5rem;margin-bottom:0;padding-left:1.5rem">
        <li>Use disease-resistant varieties</li>
        <li>Maintain proper plant spacing for air circulation</li>
        <li>Avoid excess nitrogen fertilization</li>
        <li>Remove and destroy infected plant debris</li>
        <li>Rotate crops to break disease cycles</li>
      </ul>
    </div>
    <div class="info-panel warning" style="margin-top:1rem">
      <b>Chemical Control (if disease risk > 60%):</b><br><br>
      <b>Fungicides:</b> Mancozeb (2g/L), Carbendazim (1g/L), or Tricyclazole (0.6g/L)<br>
      <b>Application:</b> Spray at 10-day intervals during high-risk periods<br>
      <b>Safety:</b> Follow label instructions, use protective equipment, observe harvest intervals
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# MODULE: MARKET INSIGHTS
# ═══════════════════════════════════════════════════════════════════════════════
def module_market():
    st.markdown('<div class="sec-head">📈 Market Intelligence & Price Forecast</div>', unsafe_allow_html=True)
    
    crop = st.selectbox("Select Crop", ["Rice","Wheat","Cotton","Sugarcane","Maize","Tomato"], key="market_crop")
    market = simulate_market_forecast(crop)
    
    # Current price + forecast
    c1,c2,c3,c4 = st.columns(4)
    trend_icon = "📈" if market['trend']=="Rising" else "📉"
    trend_color = "#4caf50" if market['trend']=="Rising" else "#f44336"
    
    c1.markdown(f'<div class="metric-box"><div class="metric-label">Current Price</div><div class="metric-value">₹{market["current"]}</div><div style="font-size:0.75rem;color:#81c784">per quintal</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="metric-box"><div class="metric-label">3-Month Forecast</div><div class="metric-value">₹{market["forecast_3m"]}</div><div class="metric-change up" style="color:{trend_color}">{trend_icon} {abs(market["forecast_3m"]-market["current"]):.0f}</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="metric-box"><div class="metric-label">6-Month Forecast</div><div class="metric-value">₹{market["forecast_6m"]}</div><div class="metric-change up" style="color:{trend_color}">{trend_icon} {abs(market["forecast_6m"]-market["current"]):.0f}</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="metric-box"><div class="metric-label">Forecast Confidence</div><div class="metric-value" style="font-size:1.8rem">{market["confidence"]:.0f}%</div><div style="font-size:0.75rem;color:#81c784">AI Prediction</div></div>', unsafe_allow_html=True)
    
    # Price trend chart
    st.markdown("### 📊 6-Month Price Forecast")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=market['months'], y=market['prices'],
                             mode='lines+markers', name=f'{crop} Price',
                             line=dict(color='#4caf50', width=4),
                             marker=dict(size=10, color='#8bc34a'),
                             fill='tozeroy', fillcolor='rgba(76,175,80,0.2)'))
    fig.update_layout(
        plot_bgcolor='#0a1612', paper_bgcolor='#0a1612',
        font=dict(color='#e8f5e9'), hovermode='x unified',
        yaxis_title="Price (₹/quintal)", xaxis_title="Month",
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Market insights
    st.markdown("### 💡 Market Intelligence Insights")
    for insight in market['insights']:
        st.markdown(f'<div class="rec-card"><div class="rec-content">• {insight}</div></div>', unsafe_allow_html=True)
    
    # Best selling strategy
    st.markdown("### 🎯 Recommended Selling Strategy")
    if market['trend'] == "Rising":
        st.markdown(f"""
        <div class="info-panel info">
          <b>Strategy: HOLD & SELL LATER</b><br><br>
          Prices are forecasted to rise by {((market['forecast_6m']/market['current']-1)*100):.1f}% over 6 months.
          Consider holding produce for 3-4 months for better returns.<br><br>
          <b>Storage required:</b> Ensure proper warehousing to maintain quality<br>
          <b>Estimated gain:</b> ₹{market['forecast_6m']-market['current']:.0f} per quintal
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="info-panel warning">
          <b>Strategy: SELL EARLY</b><br><br>
          Prices may decline. Consider selling within 1-2 months to lock in current rates.
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# MODULE: CROP ADVISOR
# ═══════════════════════════════════════════════════════════════════════════════
def module_crop_advisor():
    st.markdown('<div class="sec-head">🌱 AI Crop Recommendation Advisor</div>', unsafe_allow_html=True)
    
    st.markdown("### 📍 Input Your Farm Conditions")
    c1,c2 = st.columns(2)
    with c1:
        season = st.selectbox("Season", ["Kharif (Jun-Sep)","Rabi (Oct-Mar)","Zaid (Mar-Jun)"])
        irrigation = st.selectbox("Irrigation Availability", ["Abundant","Moderate","Limited","Rainfed"])
    with c2:
        budget = st.selectbox("Investment Capacity", ["High (>₹50k/acre)","Medium (₹25-50k/acre)","Low (<₹25k/acre)"])
        goal = st.selectbox("Primary Goal", ["Maximum Profit","Food Security","Crop Rotation","Low Risk"])
    
    if st.button("🤖 Get AI Recommendations", type="primary"):
        soil = simulate_soil_analysis(11.34, 77.71)
        climate = simulate_climate_forecast(11.34, 77.71)
        crops = simulate_crop_recommendation(soil, climate, (11.34, 77.71))
        
        st.markdown("### 🏆 Top Recommended Crops")
        
        for idx, crop in enumerate(crops[:4], 1):
            suit_color = "#4caf50" if crop['suitability']>=80 else "#ff9800" if crop['suitability']>=70 else "#f44336"
            st.markdown(f"""
            <div class="rec-card" style="border-left-color:{suit_color}">
              <div class="rec-title">
                #{idx} {crop['name']} 
                <span style="float:right;color:{suit_color};font-size:1.2rem">{crop['suitability']}% Suitable</span>
              </div>
              <div class="rec-content">
                <b>Why this crop:</b> {crop['reason']}<br><br>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-top:0.8rem">
                  <div>
                    <span style="color:#81c784">📊 Yield Potential:</span><br>{crop['yield_potential']}
                  </div>
                  <div>
                    <span style="color:#81c784">💧 Water Requirement:</span><br>{crop['water_req']}
                  </div>
                  <div>
                    <span style="color:#81c784">⏱️ Duration:</span><br>{crop['duration']}
                  </div>
                  <div>
                    <span style="color:#81c784">🎯 Suitability:</span><br>
                    <div class="progress-container" style="margin-top:4px">
                      <div class="progress-bar" style="width:{crop['suitability']}%;background:{suit_color}"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Additional considerations
        st.markdown("### 🔍 Additional Factors to Consider")
        st.markdown("""
        <div class="info-panel info">
          <b>Market Linkage:</b> Ensure you have buyers or nearby mandis for your chosen crop<br>
          <b>Storage Facilities:</b> Some crops require immediate sale or cold storage<br>
          <b>Labor Availability:</b> Cotton and sugarcane are labor-intensive crops<br>
          <b>Input Availability:</b> Check availability of seeds, fertilizers in your area<br>
          <b>Government Schemes:</b> Check for MSP, subsidies, crop insurance for selected crops
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# MODULE: IRRIGATION PLANNER
# ═══════════════════════════════════════════════════════════════════════════════
def module_irrigation():
    st.markdown('<div class="sec-head">💧 Smart Irrigation Management</div>', unsafe_allow_html=True)
    
    crop = st.selectbox("Crop Type", ["Rice","Wheat","Cotton","Sugarcane","Maize"], key="irrig_crop")
    stage = st.selectbox("Growth Stage", ["Seedling","Vegetative","Flowering","Fruiting","Maturity"])
    
    soil_data = simulate_soil_analysis(11.34, 77.71)
    weather = simulate_climate_forecast(11.34, 77.71)
    plan = simulate_irrigation_plan(crop, soil_data['moisture'], weather)
    
    # Current status
    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(f'<div class="metric-box"><div class="metric-label">Soil Moisture</div><div class="metric-value">{soil_data["moisture"]}%</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="metric-box"><div class="metric-label">Weekly Requirement</div><div class="metric-value">{plan["weekly_volume"]}</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="metric-box"><div class="metric-label">Efficiency</div><div class="metric-value">{plan["efficiency"]}</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="metric-box"><div class="metric-label">Cost Saving</div><div class="metric-value" style="font-size:1.4rem">{plan["cost_saving"]}</div></div>', unsafe_allow_html=True)
    
    # Recommended method
    st.markdown("### 💡 Recommended Method")
    st.markdown(f"""
    <div class="info-panel info">
      <div style="font-size:1.2rem;font-weight:700;margin-bottom:0.8rem">
        {plan['method']}
      </div>
      <b>Benefits:</b> Higher efficiency, reduced water wastage, better nutrient delivery, lower labor cost<br>
      <b>Installation:</b> ₹15,000-25,000/acre (one-time) with government subsidy of 40-60%
    </div>
    """, unsafe_allow_html=True)
    
    # Weekly schedule
    st.markdown("### 📅 This Week's Irrigation Schedule")
    for sched in plan['schedule']:
        st.markdown(f"""
        <div class="rec-card">
          <div class="rec-title">{sched['day']}</div>
          <div class="rec-content">
            <b>Time:</b> {sched['time']} &nbsp;|&nbsp; 
            <b>Duration:</b> {sched['duration']} &nbsp;|&nbsp; 
            <b>Volume:</b> {sched['volume']}
          </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Alerts
    if plan['alerts']:
        st.markdown("### ⚠️ Smart Alerts")
        for alert in plan['alerts']:
            st.markdown(f'<div class="info-panel warning">{alert}</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN APP ROUTER
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    init_db()
    
    if not st.session_state.logged_in:
        # Login page (simplified - keep from previous version)
        st.markdown("""
        <div style="text-align:center;padding:3rem 0 1rem">
          <div style="font-family:'Space Grotesk',sans-serif;font-size:3.5rem;
                      font-weight:800;background:linear-gradient(135deg,#4caf50,#8bc34a);
                      -webkit-background-clip:text;-webkit-text-fill-color:transparent">
            🌾 CROPIC AI
          </div>
          <div style="color:#81c784;font-size:1.1rem;margin-top:0.5rem">
            Comprehensive Agricultural Intelligence Platform
          </div>
        </div>
        """, unsafe_allow_html=True)
        
        _,col,_ = st.columns([1,1.6,1])
        with col:
            st.markdown("### 🔐 Sign In")
            role = st.radio("I am a:", ["🧑‍🌾 Farmer","🏛️ Official"], horizontal=True)
            username = st.text_input("Username", placeholder="Enter username")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            
            if st.button("Sign In →", type="primary", use_container_width=True):
                user = authenticate(username.strip(), password.strip())
                if user:
                    expected = "farmer" if "Farmer" in role else "official"
                    if user["role"] == expected:
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.rerun()
                    else:
                        st.error(f"❌ Account is {user['role']}, not {expected}")
                else:
                    st.error("❌ Invalid credentials")
            
            st.markdown("---")
            st.caption("Demo: `farmer1` / `farmer123` or `official1` / `official123`")
        return
    
    # Main application
    show_navbar()
    st.markdown('<div style="padding:2rem 2.5rem">', unsafe_allow_html=True)
    
    # Module navigation tabs
    if st.session_state.user['role'] == 'farmer':
        tab1,tab2,tab3,tab4,tab5,tab6,tab7 = st.tabs([
            "🏠 Dashboard","🌦️ Climate","🧪 Soil","🦠 Disease",
            "📈 Market","🌱 Crop Advisor","💧 Irrigation"
        ])
        
        with tab1: module_dashboard()
        with tab2: module_climate()
        with tab3: module_soil()
        with tab4: module_disease()
        with tab5: module_market()
        with tab6: module_crop_advisor()
        with tab7: module_irrigation()
    else:
        st.info("Official portal modules (Insurance review) - refer to previous app version")
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
