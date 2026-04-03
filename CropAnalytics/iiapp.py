"""
CROPIC - Crop Insurance Analytics System
Full Version: Farmer + Official Login, Farmer Profile, Printable Reports
"""

import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import folium
from streamlit_folium import st_folium
from datetime import datetime
import json, os, hashlib, base64
from pathlib import Path

from image_preprocessor import ImagePreprocessor
from model_training import CropHealthModel

st.set_page_config(
    page_title="Agrisense– Crop Insurance System",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600;700&display=swap');
*,*::before,*::after{box-sizing:border-box}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif;background:#f4f6f0}
.sec-head{font-family:'DM Serif Display',serif;font-size:1.2rem;color:#2e7d32;
  border-bottom:2px solid #e8f5e9;padding-bottom:5px;margin:1rem 0 0.7rem 0}
.card{background:#fff;border-radius:12px;padding:1.2rem 1.4rem;
  box-shadow:0 2px 10px rgba(0,0,0,0.07);margin-bottom:0.8rem}
.card-green {border-left:5px solid #4caf50}
.card-orange{border-left:5px solid #ff9800}
.card-red   {border-left:5px solid #f44336}
.card-blue  {border-left:5px solid #2196f3}
.badge{display:inline-block;border-radius:20px;padding:2px 12px;font-size:0.78rem;font-weight:600}
.badge-ts  {background:#e3f2fd;color:#1565c0}
.badge-loc {background:#f3e5f5;color:#6a1b9a;margin-left:7px}
.upload-placeholder{text-align:center;padding:3rem 1rem;background:#f9fbe7;
  border-radius:14px;border:2px dashed #aed581;color:#558b2f}
.rec-box{background:#f9fbe7;border-left:4px solid #8bc34a;border-radius:8px;
  padding:10px 14px;margin-top:8px;font-size:0.9rem}
</style>
""", unsafe_allow_html=True)

# ── Data paths ────────────────────────────────────────────────────────────────
DATA_DIR      = Path("cropic_data"); DATA_DIR.mkdir(exist_ok=True)
USERS_FILE    = DATA_DIR / "users.json"
ANALYSES_FILE = DATA_DIR / "analyses.json"

SEED_USERS = [
    {"username":"farmer1","password":hashlib.md5(b"farmer123").hexdigest(),"role":"farmer",
     "full_name":"Rajesh Kumar","phone":"9876543210",
     "address":"45 Paddy Lane, Thanjavur, Tamil Nadu - 613001",
     "land_acres":"4.5","bank_account":"SBI-XXXX-4521","crop_types":"Rice, Sugarcane"},
    {"username":"farmer2","password":hashlib.md5(b"farmer456").hexdigest(),"role":"farmer",
     "full_name":"Meena Devi","phone":"9123456780",
     "address":"12 Green Fields Rd, Coimbatore, Tamil Nadu - 641001",
     "land_acres":"2.8","bank_account":"PNB-XXXX-8834","crop_types":"Wheat, Cotton"},
    {"username":"official1","password":hashlib.md5(b"official123").hexdigest(),"role":"official",
     "full_name":"Dr. S. Venkatesh","phone":"9988776655",
     "department":"Agriculture Insurance Division, Govt of Tamil Nadu",
     "designation":"Senior Inspector"},
    {"username":"official2","password":hashlib.md5(b"official456").hexdigest(),"role":"official",
     "full_name":"Mrs. P. Lakshmi","phone":"9877665544",
     "department":"District Agricultural Office, Madurai","designation":"Field Officer"},
]

def load_json(p,d):
    return json.load(open(p)) if p.exists() else d

def save_json(p,d):
    with open(p,"w") as f: json.dump(d,f,indent=2,default=str)

def init_db():
    if not USERS_FILE.exists(): save_json(USERS_FILE, SEED_USERS)

def hash_pw(pw): return hashlib.md5(pw.encode()).hexdigest()

def authenticate(u,p):
    for x in load_json(USERS_FILE,[]):
        if x["username"]==u and x["password"]==hash_pw(p): return x
    return None

def load_analyses():  return load_json(ANALYSES_FILE,[])
def save_analysis(r):
    d=load_analyses(); d.append(r); save_json(ANALYSES_FILE,d)

# ── Session state ─────────────────────────────────────────────────────────────
for k,v in [("logged_in",False),("user",None),("last_analysis",None),
            ("model",None),("geo_lat",11.3410),("geo_lon",77.7172)]:
    if k not in st.session_state: st.session_state[k]=v

# ── Model ─────────────────────────────────────────────────────────────────────
def load_model():
    m=CropHealthModel(num_classes=4)
    if os.path.exists("crop_health_model.h5"):
        try: m.load_model("crop_health_model.h5"); return m,True
        except: pass
    m.build_model(); m.compile_model(); return m,False

# ── Analysis ──────────────────────────────────────────────────────────────────
def run_analysis(image,crop_type,growth_stage,lat,lon,farmer_user):
    pre  = ImagePreprocessor()
    val  = pre.validate_image_quality(image)
    proc = pre.preprocess_image(image,enhance=True)
    mdl  = st.session_state.model
    if mdl and mdl.model:
        pred=mdl.predict(proc)
    else:
        import random
        classes=['Healthy','Pest_Disease','Flood_Damage','Drought_Stress']
        ch=random.choice(classes); cf=round(random.uniform(0.70,0.94),4)
        rest=round((1-cf)/3,4); pr={c:(cf if c==ch else rest) for c in classes}
        sp=sorted(pr.items(),key=lambda x:x[1],reverse=True)
        pred={'predicted_class':ch,'confidence':cf,
              'top_3_predictions':[{'class':k,'confidence':v} for k,v in sp[:3]],
              'all_probabilities':pr}
    rules={
        'Healthy'       :('No damage detected','No payout recommended','#2e7d32'),
        'Pest_Disease'  :('Pest/Disease damage detected','Partial payout (40-60%) recommended','#e65100'),
        'Flood_Damage'  :('Flood damage detected','Full payout (80-100%) recommended','#1565c0'),
        'Drought_Stress':('Drought stress detected','Partial payout (30-50%) recommended','#e65100'),
    }
    verdict,ins_rec,color=rules[pred['predicted_class']]
    return {
        'record_id'        :f"REC-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        'timestamp'        :datetime.now().strftime("%Y-%m-%d  %H:%M:%S"),
        'farmer_username'  :farmer_user['username'],
        'farmer_name'      :farmer_user.get('full_name','—'),
        'farmer_phone'     :farmer_user.get('phone','—'),
        'farmer_address'   :farmer_user.get('address','—'),
        'farmer_land'      :farmer_user.get('land_acres','—'),
        'farmer_bank'      :farmer_user.get('bank_account','—'),
        'crop_types'       :farmer_user.get('crop_types','—'),
        'crop_analyzed'    :crop_type,
        'growth_stage'     :growth_stage,
        'location'         :[lat,lon],
        'validation'       :val,
        'prediction'       :pred,
        'verdict'          :verdict,
        'insurance_rec'    :ins_rec,
        'verdict_color'    :color,
        'image_size'       :list(image.size),
        'official_reviewed':False,
        'official_notes'   :'',
        'approved_amount'  :'',
    }

# ── Report HTML ───────────────────────────────────────────────────────────────
def build_report_html(rec):
    cls=rec['prediction']['predicted_class']; conf=rec['prediction']['confidence']*100
    qs=rec['validation']['metrics'].get('quality_score',0)
    lat,lon=rec['location']; color=rec['verdict_color']
    probs="".join(
        f"<tr><td style='padding:4px 8px;border:1px solid #ddd'>{k.replace('_',' ')}</td>"
        f"<td style='padding:4px 8px;border:1px solid #ddd;text-align:right'>{v*100:.1f}%</td></tr>"
        for k,v in rec['prediction']['all_probabilities'].items())
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
body{{font-family:'Segoe UI',Arial,sans-serif;margin:0;padding:24px;color:#222}}
.hdr{{display:flex;justify-content:space-between;border-bottom:3px solid #3a7d44;padding-bottom:12px;margin-bottom:16px}}
.logo{{font-size:1.6rem;font-weight:800;color:#3a7d44}}
.meta{{font-size:0.8rem;color:#666;text-align:right;line-height:1.7}}
h2{{font-size:1rem;color:#3a7d44;border-bottom:1px solid #c8e6c9;padding-bottom:3px;margin:14px 0 8px}}
table.info{{width:100%;border-collapse:collapse;font-size:0.88rem;margin-bottom:10px}}
table.info td{{padding:5px 8px}}
.lbl{{color:#888;width:160px}}.val{{font-weight:600}}
.vbox{{border-radius:8px;padding:12px 16px;margin:14px 0;border:2px solid {color}}}
.vbig{{font-size:1.35rem;font-weight:800;color:{color}}}
table.prob{{border-collapse:collapse;font-size:0.83rem;width:100%}}
.sig{{border-top:1px solid #333;width:180px;text-align:center;padding-top:5px;
      font-size:0.8rem;color:#555;margin-top:40px}}
.footer{{margin-top:24px;border-top:1px dashed #ccc;padding-top:10px;
         font-size:0.75rem;color:#999;display:flex;justify-content:space-between}}
@media print{{button{{display:none}}}}
</style></head><body>
<div class="hdr">
  <div><div class="logo">🌾 CROPIC</div>
       <div style="font-size:0.78rem;color:#666">Crop Insurance Analytics System</div></div>
  <div class="meta"><b>Report ID:</b> {rec['record_id']}<br>
    <b>Date &amp; Time:</b> {rec['timestamp']}<br>
    <b>GPS:</b> {lat:.4f}, {lon:.4f}</div>
</div>
<h2>👤 Farmer Details</h2>
<table class="info">
<tr><td class="lbl">Full Name</td><td class="val">{rec['farmer_name']}</td>
    <td class="lbl">Contact Number</td><td class="val">{rec['farmer_phone']}</td></tr>
<tr><td class="lbl">Address</td><td class="val" colspan="3">{rec['farmer_address']}</td></tr>
<tr><td class="lbl">Land Holding</td><td class="val">{rec['farmer_land']} acres</td>
    <td class="lbl">Bank Account</td><td class="val">{rec['farmer_bank']}</td></tr>
<tr><td class="lbl">Registered Crops</td><td class="val">{rec['crop_types']}</td>
    <td class="lbl">Farmer ID</td><td class="val">{rec['farmer_username']}</td></tr>
</table>
<h2>🌾 Crop Details</h2>
<table class="info">
<tr><td class="lbl">Crop Analyzed</td><td class="val">{rec['crop_analyzed']}</td>
    <td class="lbl">Growth Stage</td><td class="val">{rec['growth_stage']}</td></tr>
<tr><td class="lbl">Image Quality</td><td class="val">{qs:.0f}/100</td>
    <td class="lbl">Image Size</td><td class="val">{rec['image_size'][0]}x{rec['image_size'][1]} px</td></tr>
</table>
<h2>🤖 AI Analysis Result</h2>
<div class="vbox">
  <div class="vbig">{cls.replace('_',' ')}</div>
  <div style="margin:5px 0;font-size:0.92rem">
    <b>Confidence:</b> {conf:.1f}% &nbsp;|&nbsp; <b>Finding:</b> {rec['verdict']}</div>
  <div style="font-size:1rem;font-weight:700;color:{color}">
    Insurance Recommendation: {rec['insurance_rec']}</div>
</div>
<div style="display:flex;gap:2rem">
  <div style="flex:1">
    <b style="font-size:0.85rem">Class Probabilities</b>
    <table class="prob" style="margin-top:6px">
      <tr style="background:#f5f5f5">
        <th style="padding:4px 8px;border:1px solid #ddd;text-align:left">Condition</th>
        <th style="padding:4px 8px;border:1px solid #ddd;text-align:right">Probability</th></tr>
      {probs}</table></div>
  <div style="flex:1">
    <b style="font-size:0.85rem">Image Quality Metrics</b>
    <table class="prob" style="margin-top:6px">
      <tr><td style="padding:4px 8px;border:1px solid #ddd">Blur Score</td>
          <td style="padding:4px 8px;border:1px solid #ddd;text-align:right">{rec['validation']['metrics'].get('blur_score',0):.0f}</td></tr>
      <tr><td style="padding:4px 8px;border:1px solid #ddd">Brightness</td>
          <td style="padding:4px 8px;border:1px solid #ddd;text-align:right">{rec['validation']['metrics'].get('brightness',0):.0f}</td></tr>
      <tr><td style="padding:4px 8px;border:1px solid #ddd">Contrast</td>
          <td style="padding:4px 8px;border:1px solid #ddd;text-align:right">{rec['validation']['metrics'].get('contrast',0):.0f}</td></tr>
      <tr><td style="padding:4px 8px;border:1px solid #ddd">Quality Score</td>
          <td style="padding:4px 8px;border:1px solid #ddd;text-align:right"><b>{qs:.0f}/100</b></td></tr>
    </table></div>
</div>
<h2>✍️ Official Review</h2>
<table class="info">
<tr><td class="lbl">Reviewed By</td>
    <td class="val">{rec.get('reviewed_by','____________________________')}</td>
    <td class="lbl">Review Date</td>
    <td class="val">{rec.get('review_date','____________________________')}</td></tr>
<tr><td class="lbl">Approved Amount</td>
    <td class="val">{rec.get('approved_amount','Rs. ____________________')}</td>
    <td class="lbl">Status</td>
    <td class="val">{'Approved' if rec.get('official_reviewed') else 'Pending Review'}</td></tr>
<tr><td class="lbl">Official Notes</td>
    <td class="val" colspan="3">{rec.get('official_notes','—') or '—'}</td></tr>
</table>
<div style="display:flex;justify-content:space-between">
  <div class="sig">Farmer Signature</div>
  <div class="sig">Official Signature</div>
  <div class="sig">Department Stamp</div>
</div>
<div class="footer">
  <span>Generated by CROPIC Crop Insurance Analytics System | Confidential</span>
  <span>Report ID: {rec['record_id']}</span>
</div>
<script>window.onload=function(){{window.print()}}</script>
</body></html>"""

# ═══════════════════════════════════════════════════════════════════════════════
# LOGIN PAGE
# ═══════════════════════════════════════════════════════════════════════════════
def show_login():
    init_db()
    st.markdown("""
    <div style="text-align:center;padding:2rem 0 0.5rem">
      <div style="font-family:'DM Serif Display',serif;font-size:2.8rem;color:#3a7d44;font-weight:700">🌾 CROPIC</div>
      <div style="color:#666;font-size:1rem;margin-top:4px">Crop Insurance Analytics System</div>
    </div>""", unsafe_allow_html=True)

    _,col,_ = st.columns([1,1.5,1])
    with col:
        st.markdown("---")
        st.markdown("#### 🔐 Sign In to Your Account")
        role = st.radio("I am a:", ["🧑‍🌾  Farmer","🏛️  Official"], horizontal=True)
        username = st.text_input("Username", placeholder="Enter username")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        if st.button("Sign In →", type="primary", use_container_width=True):
            user = authenticate(username.strip(), password.strip())
            if not user:
                st.error("❌ Incorrect username or password.")
            else:
                expected = "farmer" if "Farmer" in role else "official"
                if user["role"] != expected:
                    st.error(f"❌ This account is a '{user['role']}'. Please select the correct role.")
                else:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.rerun()
        st.markdown("---")
        st.markdown("""<div style="font-size:0.8rem;color:#aaa;text-align:center">
        <b>Demo Credentials</b><br>
        Farmer &nbsp;→&nbsp; <code>farmer1</code> / <code>farmer123</code><br>
        Official &nbsp;→&nbsp; <code>official1</code> / <code>official123</code>
        </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TOP BAR
# ═══════════════════════════════════════════════════════════════════════════════
def show_topbar():
    u = st.session_state.user
    rl = "🧑‍🌾 Farmer" if u["role"]=="farmer" else "🏛️ Official"
    c1,c2,c3 = st.columns([2,5,2])
    with c1:
        st.markdown(f'<div style="font-family:DM Serif Display,serif;font-size:1.5rem;color:#3a7d44;font-weight:700;padding-top:6px">🌾 CROPIC</div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div style="text-align:center;padding-top:9px;color:#555;font-size:0.9rem">Crop Insurance Analytics System</div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div style="text-align:right;padding-top:5px;font-size:0.82rem;color:#444">{u["full_name"]} &nbsp;<span style="background:#e8f5e9;color:#2e7d32;border-radius:12px;padding:2px 10px;font-weight:600;font-size:0.75rem">{rl}</span></div>', unsafe_allow_html=True)
    if st.button("🚪 Logout", key="logout_btn"):
        for k in ["logged_in","user","last_analysis"]:
            st.session_state[k] = False if k=="logged_in" else None
        st.rerun()
    st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════════════
# FARMER PORTAL
# ═══════════════════════════════════════════════════════════════════════════════
def farmer_portal():
    u = st.session_state.user
    if st.session_state.model is None:
        with st.spinner("Loading AI engine..."):
            m,_ = load_model(); st.session_state.model = m

    tab1,tab2,tab3 = st.tabs(["📸  Analyze My Crop","📋  My Reports","👤  My Profile"])

    # TAB 1 ── Analyze
    with tab1:
        st.markdown('<div class="sec-head">Upload Crop Image for Analysis</div>', unsafe_allow_html=True)
        uploaded = st.file_uploader("Choose a crop image (JPG/PNG)", type=['jpg','jpeg','png'])
        if not uploaded:
            st.markdown('<div class="upload-placeholder"><div style="font-size:3rem">📷</div><div style="font-size:1.05rem;font-weight:600;margin-top:0.5rem">Upload a Crop Photo to Begin</div><div style="font-size:0.85rem;color:#777;margin-top:4px">Take a clear, well-lit photo of your crop field</div></div>', unsafe_allow_html=True)
        else:
            image = Image.open(uploaded)
            ci,cf = st.columns([1,1])
            with ci:
                st.image(image, caption="Uploaded image", use_container_width=True)
                st.caption(f"{image.size[0]}×{image.size[1]} px · {image.mode}")
            with cf:
                st.markdown('<div class="sec-head">Crop & Location Details</div>', unsafe_allow_html=True)
                crop_type    = st.selectbox("Crop Type", ["Rice","Wheat","Maize","Cotton","Sugarcane","Tomato","Potato","Other"])
                growth_stage = st.selectbox("Growth Stage", ["Seedling","Vegetative","Flowering","Fruiting","Maturity"])
                st.markdown("**📍 GPS Location**")
                st.caption("Tip: Google Maps → right-click field → 'What's here?' → copy coordinates")
                g1,g2 = st.columns(2)
                with g1:
                    lat = st.number_input("Latitude",  value=st.session_state.geo_lat, format="%.6f", step=0.0001)
                    st.session_state.geo_lat = lat
                with g2:
                    lon = st.number_input("Longitude", value=st.session_state.geo_lon, format="%.6f", step=0.0001)
                    st.session_state.geo_lon = lon
                st.caption(f"📍 ({lat:.6f}, {lon:.6f})")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🔍  Analyze Crop Health", type="primary", use_container_width=True):
                    with st.spinner("Analysing..."):
                        rec = run_analysis(image, crop_type, growth_stage, lat, lon, u)
                        st.session_state.last_analysis = rec
                        save_analysis(rec)
                    st.success(f"✅ Saved! Record ID: **{rec['record_id']}**")

            if st.session_state.last_analysis:
                rec  = st.session_state.last_analysis
                cls  = rec['prediction']['predicted_class']
                conf = rec['prediction']['confidence']*100
                qs   = rec['validation']['metrics'].get('quality_score',0)
                st.markdown("---")
                st.markdown('<div class="sec-head">📊 Analysis Result</div>', unsafe_allow_html=True)
                st.markdown(f'<span class="badge badge-ts">🕐 {rec["timestamp"]}</span><span class="badge badge-loc">📍 {rec["location"][0]:.4f}, {rec["location"][1]:.4f}</span>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                cc = "card-green" if "Healthy" in cls else ("card-red" if "Flood" in cls else "card-orange")
                ic = "✅" if "Healthy" in cls else ("🌊" if "Flood" in cls else "⚠️")
                r1,r2,r3 = st.columns(3)
                with r1:
                    st.markdown(f'<div class="card {cc}"><div style="font-size:0.72rem;color:#888;margin-bottom:3px">CONDITION</div><div style="font-size:1.4rem;font-weight:700">{ic} {cls.replace("_"," ")}</div><div style="color:#555;font-size:0.85rem">Confidence: <b>{conf:.1f}%</b></div></div>', unsafe_allow_html=True)
                with r2:
                    st.markdown(f'<div class="card card-blue"><div style="font-size:0.72rem;color:#888;margin-bottom:3px">IMAGE QUALITY</div><div style="font-size:1.4rem;font-weight:700">{qs:.0f}<span style="font-size:0.9rem">/100</span></div><div style="color:#555;font-size:0.85rem">{"Good ✅" if qs>=70 else "Acceptable ⚠️" if qs>=50 else "Poor ❌"}</div></div>', unsafe_allow_html=True)
                with r3:
                    st.markdown(f'<div class="card {cc}"><div style="font-size:0.72rem;color:#888;margin-bottom:3px">INSURANCE REC.</div><div style="font-size:0.9rem;font-weight:700;margin-top:4px">{rec["insurance_rec"]}</div></div>', unsafe_allow_html=True)
                st.markdown('<div class="sec-head" style="margin-top:1rem">Prediction Breakdown</div>', unsafe_allow_html=True)
                for p in rec['prediction']['top_3_predictions']:
                    st.progress(float(p['confidence']), text=f"{p['class'].replace('_',' ')}: {p['confidence']*100:.1f}%")

    # TAB 2 ── My Reports
    with tab2:
        st.markdown('<div class="sec-head">My Analysis Reports</div>', unsafe_allow_html=True)
        my_recs = [r for r in load_analyses() if r.get('farmer_username')==u['username']]
        if not my_recs:
            st.info("No reports yet. Go to 'Analyze My Crop' to submit your first image.")
        else:
            rows=[]
            for r in reversed(my_recs):
                rows.append({'Record ID':r['record_id'],'Date & Time':r['timestamp'],
                    'Crop':r['crop_analyzed'],'Stage':r['growth_stage'],
                    'Condition':r['prediction']['predicted_class'].replace('_',' '),
                    'Confidence':f"{r['prediction']['confidence']*100:.1f}%",
                    'Quality':f"{r['validation']['metrics']['quality_score']:.0f}/100",
                    'Reviewed':'✅ Yes' if r.get('official_reviewed') else '⏳ Pending',
                    'Amount':r.get('approved_amount','—')})
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # TAB 3 ── Profile
    with tab3:
        st.markdown('<div class="sec-head">My Profile</div>', unsafe_allow_html=True)
        p1,p2 = st.columns(2)
        with p1:
            st.markdown(f"**Full Name:** {u.get('full_name','—')}")
            st.markdown(f"**Phone:** {u.get('phone','—')}")
            st.markdown(f"**Address:** {u.get('address','—')}")
        with p2:
            st.markdown(f"**Land Holding:** {u.get('land_acres','—')} acres")
            st.markdown(f"**Bank Account:** {u.get('bank_account','—')}")
            st.markdown(f"**Registered Crops:** {u.get('crop_types','—')}")
        st.info("Contact your district office to update profile information.")

# ═══════════════════════════════════════════════════════════════════════════════
# OFFICIAL PORTAL
# ═══════════════════════════════════════════════════════════════════════════════
def official_portal():
    u = st.session_state.user
    tab1,tab2,tab3 = st.tabs(["📋  All Analyses","🗺️  Map View","👤  My Profile"])

    # TAB 1 ── All Analyses
    with tab1:
        st.markdown('<div class="sec-head">All Submitted Crop Analyses</div>', unsafe_allow_html=True)
        all_recs = load_analyses()
        if not all_recs:
            st.info("No analyses submitted yet."); return

        # Filters
        fc1,fc2,fc3 = st.columns(3)
        farmers = list(set(r['farmer_username'] for r in all_recs))
        with fc1: f_filter = st.selectbox("Filter by Farmer",["All"]+farmers)
        with fc2: c_filter = st.selectbox("Filter by Condition",["All","Healthy","Pest_Disease","Flood_Damage","Drought_Stress"])
        with fc3: r_filter = st.selectbox("Filter by Status",["All","Pending","Reviewed"])

        filtered = all_recs
        if f_filter!="All": filtered=[r for r in filtered if r['farmer_username']==f_filter]
        if c_filter!="All": filtered=[r for r in filtered if r['prediction']['predicted_class']==c_filter]
        if r_filter=="Pending": filtered=[r for r in filtered if not r.get('official_reviewed')]
        elif r_filter=="Reviewed": filtered=[r for r in filtered if r.get('official_reviewed')]

        # Summary metrics
        m1,m2,m3,m4 = st.columns(4)
        m1.metric("Total Records", len(all_recs))
        m2.metric("Pending Review", sum(1 for r in all_recs if not r.get('official_reviewed')))
        m3.metric("Reviewed", sum(1 for r in all_recs if r.get('official_reviewed')))
        m4.metric("Damage Cases", sum(1 for r in all_recs if r['prediction']['predicted_class']!='Healthy'))

        st.caption(f"Showing **{len(filtered)}** of **{len(all_recs)}** records")
        st.markdown("---")

        for rec in reversed(filtered):
            cls      = rec['prediction']['predicted_class']
            conf     = rec['prediction']['confidence']*100
            reviewed = rec.get('official_reviewed',False)
            cc       = "card-green" if "Healthy" in cls else ("card-red" if "Flood" in cls else "card-orange")

            with st.expander(
                f"🆔 {rec['record_id']}  |  👤 {rec['farmer_name']}  |  "
                f"🌾 {rec['crop_analyzed']}  |  {cls.replace('_',' ')} ({conf:.0f}%)  |  "
                f"{'✅ Reviewed' if reviewed else '⏳ Pending'}  |  🕐 {rec['timestamp']}"
            ):
                left,right = st.columns([3,2])

                with left:
                    # Farmer info
                    st.markdown('<div class="sec-head">👤 Farmer Information</div>', unsafe_allow_html=True)
                    i1,i2 = st.columns(2)
                    with i1:
                        st.markdown(f"**Name:** {rec['farmer_name']}")
                        st.markdown(f"**Phone:** {rec['farmer_phone']}")
                        st.markdown(f"**Land:** {rec['farmer_land']} acres")
                    with i2:
                        st.markdown(f"**Bank A/C:** {rec['farmer_bank']}")
                        st.markdown(f"**Crops:** {rec['crop_types']}")
                        st.markdown(f"**GPS:** {rec['location'][0]:.4f}, {rec['location'][1]:.4f}")
                    st.markdown(f"**Address:** {rec['farmer_address']}")

                    # AI Result
                    st.markdown('<div class="sec-head">🤖 AI Analysis</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="card {cc}"><b>{cls.replace("_"," ")}</b> — Confidence: {conf:.1f}%<br><span style="font-size:0.87rem">{rec["verdict"]}</span><br><b>Recommendation:</b> {rec["insurance_rec"]}</div>', unsafe_allow_html=True)
                    for p in rec['prediction']['top_3_predictions']:
                        st.progress(float(p['confidence']), text=f"{p['class'].replace('_',' ')}: {p['confidence']*100:.1f}%")

                with right:
                    # Official review
                    st.markdown('<div class="sec-head">✍️ Official Review</div>', unsafe_allow_html=True)
                    uid   = rec['record_id']
                    notes = st.text_area("Reviewer Notes", value=rec.get('official_notes',''),
                                         key=f"notes_{uid}", placeholder="Field visit findings, observations…")
                    amt   = st.text_input("Approved Amount (₹)", value=rec.get('approved_amount',''),
                                          key=f"amt_{uid}", placeholder="e.g. 25000")
                    appr  = st.checkbox("Mark as Reviewed / Approved",
                                        value=rec.get('official_reviewed',False), key=f"appr_{uid}")

                    if st.button("💾 Save Review", key=f"save_{uid}", use_container_width=True):
                        all_data = load_analyses()
                        for r in all_data:
                            if r['record_id']==uid:
                                r['official_notes']   = notes
                                r['approved_amount']  = amt
                                r['official_reviewed']= appr
                                r['reviewed_by']      = u.get('full_name','Official')
                                r['review_date']      = datetime.now().strftime("%Y-%m-%d %H:%M")
                                rec.update(r); break
                        save_json(ANALYSES_FILE, all_data)
                        st.success("✅ Review saved!"); st.rerun()

                    st.markdown("---")
                    st.markdown("**🖨️ Print Report**")
                    html  = build_report_html(rec)
                    b64   = base64.b64encode(html.encode()).decode()
                    st.markdown(
                        f'<a href="data:text/html;base64,{b64}" download="{uid}_report.html" '
                        f'style="display:block;text-align:center;background:#3a7d44;color:#fff;'
                        f'padding:10px 0;border-radius:8px;text-decoration:none;font-weight:600;'
                        f'margin-bottom:6px">📄 Download &amp; Print Report</a>',
                        unsafe_allow_html=True)
                    st.caption("Click → Opens in browser → Ctrl+P (or Cmd+P on Mac) to print / save as PDF.")

    # TAB 2 ── Map
    with tab2:
        st.markdown('<div class="sec-head">🗺️ Geographic Distribution</div>', unsafe_allow_html=True)
        all_recs = load_analyses()
        if not all_recs:
            st.info("No data to show on map."); return
        lats=[r['location'][0] for r in all_recs]; lons=[r['location'][1] for r in all_recs]
        m=folium.Map(location=[np.mean(lats),np.mean(lons)],zoom_start=10)
        cmap={'Healthy':'green','Pest_Disease':'orange','Flood_Damage':'blue','Drought_Stress':'red'}
        for rec in all_recs:
            lat,lon=rec['location']; cls=rec['prediction']['predicted_class']
            popup=f"""<div style="min-width:200px;font-size:0.85rem;font-family:sans-serif">
              <b>{rec['farmer_name']}</b> ({rec['farmer_username']})<br>
              📞 {rec['farmer_phone']}<hr style="margin:4px 0">
              <b>Crop:</b> {rec['crop_analyzed']} · {rec['growth_stage']}<br>
              <b>Condition:</b> {cls.replace('_',' ')}<br>
              <b>Confidence:</b> {rec['prediction']['confidence']*100:.1f}%<br>
              <b>Rec:</b> {rec['insurance_rec']}<hr style="margin:4px 0">
              <span style="color:#888">🕐 {rec['timestamp']}</span><br>
              <span style="color:{'green' if rec.get('official_reviewed') else 'orange'}">
                {'✅ Reviewed' if rec.get('official_reviewed') else '⏳ Pending'}</span></div>"""
            folium.Marker(location=[lat,lon],popup=folium.Popup(popup,max_width=260),
                tooltip=f"{rec['farmer_name']} – {cls.replace('_',' ')}",
                icon=folium.Icon(color=cmap.get(cls,'gray'),icon='leaf',prefix='fa')).add_to(m)
        st_folium(m,width=None,height=520,returned_objects=[])
        st.markdown("**Legend:**  🟢 Healthy &nbsp; 🟠 Pest/Disease &nbsp; 🔵 Flood &nbsp; 🔴 Drought")

    # TAB 3 ── Profile
    with tab3:
        st.markdown('<div class="sec-head">Official Profile</div>', unsafe_allow_html=True)
        st.markdown(f"**Name:** {u.get('full_name','—')}")
        st.markdown(f"**Designation:** {u.get('designation','—')}")
        st.markdown(f"**Department:** {u.get('department','—')}")
        st.markdown(f"**Phone:** {u.get('phone','—')}")

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    init_db()
    if not st.session_state.logged_in:
        show_login(); return
    show_topbar()
    if st.session_state.user['role']=='farmer':
        farmer_portal()
    else:
        official_portal()

if __name__=="__main__":
    main()
