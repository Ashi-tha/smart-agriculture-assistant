"""
Real-time Market Data API for Indian Agricultural Crops.
Integrates with Data.gov.in (OGD Platform India).
"""
import os
import random
import requests
from datetime import datetime, timedelta

# Map app internal names to Agmarknet commodity names
COMMODITY_MAPPING = {
    "rice": "Rice",
    "maize": "Maize",
    "chickpea": "Bengal Gram(Gram)(Whole)",
    "kidneybeans": "Arhar (Tur/Red Gram)",
    "pigeonpeas": "Arhar (Tur/Red Gram)",
    "mothbeans": "Moth Beans",
    "mungbean": "Moong (Green Gram)(Whole)",
    "blackgram": "Urd Beans(Whole)",
    "lentil": "Lentil (Masur)(Whole)",
    "pomegranate": "Pomegranate",
    "banana": "Banana",
    "mango": "Mango",
    "grapes": "Grapes",
    "watermelon": "Watermelon",
    "muskmelon": "Muskmelon",
    "apple": "Apple",
    "orange": "Orange",
    "papaya": "Papaya",
    "coconut": "Coconut",
    "cotton": "Cotton",
    "jute": "Jute",
    "coffee": "Coffee"
}

# Base prices for fallback
BASE_PRICES = {
    "rice": 2200, "maize": 2090, "chickpea": 5335, "kidneybeans": 6500,
    "pigeonpeas": 7000, "mothbeans": 5500, "mungbean": 8550, "blackgram": 6950,
    "lentil": 6000, "pomegranate": 7500, "banana": 1500, "mango": 4500,
    "grapes": 6000, "watermelon": 1200, "muskmelon": 1800, "apple": 8000,
    "orange": 3500, "papaya": 2200, "coconut": 3000, "cotton": 6620,
    "jute": 5050, "coffee": 15000
}

def get_market_data(crop_name: str, state: str) -> dict:
    """Fetch live market data from Data.gov.in or fallback to simulation."""
    api_key = os.getenv("DATA_GOV_API_KEY", "")
    crop_internal = crop_name.lower()
    commodity = COMMODITY_MAPPING.get(crop_internal, crop_name.title())
    
    # Try Live API if key is provided and not "placeholder"
    if api_key and "your_copied_api_key" not in api_key:
        try:
            # Resource ID from user's Agmarknet dashboard (Variety-wise Daily Market Prices)
            RESOURCE_ID = "35985678-0d79-46b4-9ed6-6f13308a1d24"
            url = f"https://api.data.gov.in/resource/{RESOURCE_ID}"
            params = {
                "api-key": api_key,
                "format": "json",
                "filters[commodity]": commodity,
                "limit": 10
            }
            if state:
                params["filters[state]"] = state.title()
                
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                records = data.get("records", [])
                
                if records:
                    # Take the modal price of the first record (usually the most recent)
                    record = records[0]
                    current_price = int(record.get("modal_price", 0))
                    mandi = record.get("market", "Local Mandi")
                    
                    return _format_result(crop_internal, state, current_price, True, mandi)
        except Exception:
            pass # Fallback to mock on any API error

    # Fallback to realistic simulation
    base_price = BASE_PRICES.get(crop_internal, 3000)
    state_multiplier = random.uniform(0.9, 1.15)
    current_price = int(base_price * state_multiplier)
    return _format_result(crop_internal, state, current_price, False)

def _format_result(crop_name: str, state: str, current_price: int, is_live: bool, mandi: str = None) -> dict:
    """Consolidated formatter for both live and simulated results."""
    base_price = BASE_PRICES.get(crop_name, current_price)
    
    # History simulation (since API usually returns daily, not historical timeline)
    history = []
    months = []
    curr_date = datetime.now()
    for i in range(5, -1, -1):
        month_date = curr_date - timedelta(days=30 * i)
        months.append(month_date.strftime("%b %Y"))
        variation = random.uniform(0.85, 1.2)
        history.append(int(base_price * variation))
    
    history[-1] = current_price
    last_month_price = history[-2]
    change_pct = ((current_price - last_month_price) / last_month_price) * 100
    
    trend = "up" if change_pct > 0 else "down"
    source_tag = f"LIVE: {mandi or 'Agmarknet'}" if is_live else "DEMO: Simulated Trends"
    
    insight = (
        f"Prices for {crop_name.title()} are {'rising' if change_pct > 0 else 'cooling'}. "
        f"Current market rate in {state.title()} is ₹{current_price:,} per Quintal. "
        f"{'Demand is high, consider selling.' if change_pct > 5 else 'Market is stable.'}"
    )

    return {
        "success": True,
        "crop": crop_name.title(),
        "state": state.title(),
        "current_price": current_price,
        "unit": "INR / Quintal",
        "change_pct": round(change_pct, 1),
        "trend": trend,
        "insight": insight,
        "history_labels": months,
        "history_data": history,
        "is_live": is_live,
        "source": source_tag
    }

