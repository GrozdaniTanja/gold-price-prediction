import requests
import csv
import os
from datetime import datetime

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, '..', '..', 'data')
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(RAW_DATA_DIR, exist_ok=True)

API_KEY = "goldapi-fd3p6tslwqv3gdr-io"
SYMBOL = "XAU"
# CURRENCIES = ["USD", "EUR", "GBP", "AUD", "CHF", "CAD"]
CURRENCY = "EUR"


def make_gapi_request(symbol, curr, date=""):
    url = f"https://www.goldapi.io/api/{symbol}/{curr}{date}"
    headers = {
        "x-access-token": API_KEY,
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        result = response.json()

        return {
            "timestamp": datetime.now().isoformat() if not date else datetime.fromtimestamp(result["timestamp"]).isoformat(),
            "price": result["price"],
            "currency": curr,
            "prev_close_price": result.get("prev_close_price", None),
            "open_price": result.get("open_price", None),
            "low_price": result.get("low_price", None),
            "high_price": result.get("high_price", None),
            "ch": result.get("ch", None),
            "chp": result.get("chp", None),
            "ask": result.get("ask", None),
            "bid": result.get("bid", None),
            "price_gram_24k": result.get("price_gram_24k", None),
            "price_gram_22k": result.get("price_gram_22k", None),
            "price_gram_21k": result.get("price_gram_21k", None),
            "price_gram_20k": result.get("price_gram_20k", None),
            "price_gram_18k": result.get("price_gram_18k", None),
            "price_gram_16k": result.get("price_gram_16k", None),
            "price_gram_14k": result.get("price_gram_14k", None),
            "price_gram_10k": result.get("price_gram_10k", None)
        }
    except requests.exceptions.RequestException as e:
        print("Error:", str(e))
        return None


def save_data_to_csv(data, filename):
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)


def fetch_and_save_real_time_data():
    data = make_gapi_request(SYMBOL, CURRENCY)
    if data:
        data_file = os.path.join(
            RAW_DATA_DIR, f"{CURRENCY}-gold-price-data.csv")
        save_data_to_csv(data, data_file)
        print(f"Real-time data saved for {CURRENCY}: {data}")


if __name__ == "__main__":
    fetch_and_save_real_time_data()
