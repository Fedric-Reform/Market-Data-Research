# DEX VOLUME #

import requests
import pandas as pd
import matplotlib.pyplot as plt
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- RATE LIMIT HANDLING SETUP (Recommended to keep) ---
retry_strategy = Retry(
    total=3, 
    backoff_factor=0.5, 
    status_forcelist=[429, 500, 502, 503, 504],
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)
http.mount("http://", adapter)
# --- END RATE LIMIT SETUP ---


# Set dark theme for charts
plt.style.use("dark_background")

# CoinGecko API endpoint and parameters
# 🔑 KEY CHANGE: Added 'per_page=100' to the URL
url = "https://api.coingecko.com/api/v3/exchanges/decentralized"
params = {"per_page": 100} # ⬅️ Limit to top 100

try:
    print("⏳ Waiting 1.5s to respect CoinGecko API rate limit...")
    time.sleep(1.5)
    
    # 💥 USE THE SESSION and pass parameters
    response = http.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    
    # 🚨 Verification: Check how many items were actually returned
    print(f"✅ Successfully fetched data for {len(data)} decentralized exchanges.")
    
except requests.exceptions.RequestException as e:
    print(f"❌ Error fetching data from CoinGecko: {e}")
    exit()

# Extract and prepare data
exchanges = []
volumes = []
trust_scores = []
coins = []
pairs = []

for item in data:
    exchanges.append(item.get("name", "Unknown"))
    volumes.append(item.get("trade_volume_24h_btc", 0))  # BTC volume
    trust_scores.append(item.get("trust_score", 0))
    # CoinGecko DEX endpoint uses 'year_established' and 'country' for CEX data,
    # but for DEXs, these fields are often unused or repurposed, 
    # so keeping the original column mapping for now:
    coins.append(item.get("year_established", 0)) 
    pairs.append(item.get("country", "Unknown"))

# Convert BTC to USD (approx.)
BTC_PRICE = 110000  # Adjust based on real-time price if needed
volume_usd = [v * BTC_PRICE / 1e9 for v in volumes]  # USD billions

# Create DataFrame
df = pd.DataFrame({
    "Exchange": exchanges,
    "24h Volume (B USD)": volume_usd,
    "Trust Score": trust_scores,
    "Founded Year": coins,
    "Country": pairs
})

# Save to CSV
df.to_csv("DEX_Volume.csv", index=False)
print("✅ Data saved to 'DEX_Volume.csv'.")
