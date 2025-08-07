from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import random
import time

app = Flask(__name__)
CORS(app)

# Your TwelveData API key
TWELVE_DATA_API_KEY = 'd43b61ca625243c99a9273dc13ce4a5d'

# Simulated full list of Quotex forex pairs
QUOTEX_FOREX_PAIRS = [
    "EUR/USD", "GBP/USD", "AUD/USD", "USD/JPY", "USD/CAD", "USD/CHF",
    "NZD/USD", "EUR/GBP", "EUR/JPY", "GBP/JPY", "AUD/JPY", "CAD/JPY",
    "CHF/JPY", "EUR/AUD", "GBP/CAD", "AUD/CAD", "NZD/JPY", "EUR/NZD"
]

# Prediction lock system to prevent multiple predictions in same candle
last_prediction_time = {}
prediction_lock_seconds = 60  # Adjust per timeframe

def fetch_latest_candle(pair, timeframe):
    symbol = pair.replace("/", "")
    interval = timeframe
    url = f'https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&apikey={TWELVE_DATA_API_KEY}&outputsize=2'
    response = requests.get(url)
    data = response.json()
    if 'values' in data:
        return data['values'][0]  # latest candle
    return None

@app.route('/get_pairs', methods=['POST'])
def get_pairs():
    data = request.get_json()
    timeframe = data.get('timeframe')

    eligible_pairs = []
    for pair in QUOTEX_FOREX_PAIRS:
        checklist_score = random.randint(75, 100)  # Simulate
        if checklist_score >= 80:
            eligible_pairs.append(pair)

    return jsonify({'pairs': eligible_pairs})

@app.route('/predict', methods=['POST'])
def predict():
    global last_prediction_time

    data = request.get_json()
    pair = data.get('pair')
    timeframe = data.get('timeframe')

    now = time.time()
    key = f"{pair}_{timeframe}"
    if key in last_prediction_time:
        elapsed = now - last_prediction_time[key]
        if elapsed < prediction_lock_seconds:
            return jsonify({
                'status': 'locked',
                'lockDuration': int(prediction_lock_seconds - elapsed)
            })

    candle = fetch_latest_candle(pair, timeframe)
    if not candle:
        return jsonify({'status': 'no_trade', 'message': 'Live candle not available'})

    # Simulated prediction logic
    prediction = random.choice(['CALL', 'PUT'])
    checklist = {
        "Wick Rejection at S/R": random.choice([True, False]),
        "Candle Body Strength": random.choice([True, False]),
        "Volume Confirmation": random.choice([True, False]),
        "Domination Confirmation": random.choice([True, False])
    }

    score = (sum(checklist.values()) / len(checklist)) * 100

    error_analysis = None
    if score < 80:
        error_analysis = {
            "primary_reason": "Strategy conditions not fully met",
            "suggestions": [
                "Wait for stronger rejection candle",
                "Confirm with volume spike",
                "Ensure domination confirmation is present"
            ]
        }

    last_prediction_time[key] = now

    return jsonify({
        'status': 'ok',
        'prediction': prediction,
        'checklist': checklist,
        'checklist_score': score,
        'error_analysis': error_analysis
    })

@app.route('/')
def home():
    return "TradeMind AI Backend is Live"

if __name__ == '__main__':
    app.run(debug=True)

