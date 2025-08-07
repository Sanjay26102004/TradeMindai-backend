from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import datetime

app = Flask(__name__)
CORS(app)

TWELVE_DATA_API_KEY = "d43b61ca625243c99a9273dc13ce4a5d"  # Replace with your actual API key

# Full list of Quotex Forex pairs
QUOTEX_FOREX_PAIRS = [
    "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD",
    "EUR/JPY", "GBP/JPY", "NZD/USD", "USD/CHF", "EUR/GBP",
    "EUR/AUD", "AUD/JPY", "GBP/CAD", "CHF/JPY", "EUR/NZD",
    "NZD/JPY", "CAD/CHF", "AUD/CHF", "GBP/NZD", "NZD/CAD"
]

def fetch_latest_candle(pair, timeframe):
    symbol = pair.replace("/", "")
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={timeframe}&outputsize=2&apikey={TWELVE_DATA_API_KEY}"
    response = requests.get(url)
    data = response.json()
    if "values" in data:
        return data["values"][0]  # Most recent closed candle
    return None

def evaluate_strategy(candle):
    try:
        open_price = float(candle['open'])
        close_price = float(candle['close'])
        high = float(candle['high'])
        low = float(candle['low'])

        body = abs(close_price - open_price)
        wick_top = high - max(open_price, close_price)
        wick_bottom = min(open_price, close_price) - low

        score = 0

        # Basic candle psychology rules
        if body > wick_top and body > wick_bottom:
            score += 30
        if wick_bottom > body:
            score += 20
        if wick_top > body:
            score += 20
        if body > 0.5 * (high - low):
            score += 20
        if abs(open_price - close_price) / open_price < 0.005:
            score += 10  # small body = indecision

        return score
    except:
        return 0

@app.route('/')
def index():
    return "TradeMind AI Backend Running"

@app.route('/get_pairs', methods=['POST'])
def get_eligible_pairs():
    content = request.get_json()
    timeframe = content.get("timeframe", "1m")

    eligible_pairs = []
    for pair in QUOTEX_FOREX_PAIRS:
        candle = fetch_latest_candle(pair, timeframe)
        if candle:
            score = evaluate_strategy(candle)
            if score >= 70:
                eligible_pairs.append(pair)

    return jsonify({"pairs": eligible_pairs})

@app.route('/predict', methods=['POST'])
def predict():
    content = request.get_json()
    pair = content.get("pair")
    timeframe = content.get("timeframe", "1m")

    candle = fetch_latest_candle(pair, timeframe)
    if not candle:
        return jsonify({"error": "Candle data not available"})

    score = evaluate_strategy(candle)
    direction = "CALL" if float(candle['close']) > float(candle['open']) else "PUT"

    if score >= 70:
        return jsonify({
            "pair": pair,
            "timeframe": timeframe,
            "prediction": direction,
            "score": score,
            "status": "Eligible"
        })
    else:
        return jsonify({
            "pair": pair,
            "timeframe": timeframe,
            "prediction": direction,
            "score": score,
            "status": "Not Eligible"
        })

if __name__ == '__main__':
    app.run(debug=True)

