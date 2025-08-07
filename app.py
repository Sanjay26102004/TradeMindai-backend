from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import datetime

app = Flask(__name__)
CORS(app)  # Allow frontend to access API

# ✅ All Quotex forex, crypto, and index pairs
ALL_PAIRS = [
    # Forex
    "EUR/USD", "GBP/USD", "CHF/JPY", "USD/JPY", "CAD/JPY", "AUD/USD", "NDZ/USD",
    "EUR/GBP", "GBP/CHF", "USD/CHF", "CAD/CHF", "AUD/CHF", "NZD/CHF",
    "EUR/CHF", "GBP/JPY", "USD/CAD", "AUD/JPY", "NZD/JPY", "EUR/JPY", "GBP/CAD", "AUD/NZD",
    # Crypto
    "BTC/USD", "ETH/USD", "LTC/USD", "XRP/USD", "SOL/USD",
    # Indices
    "US100", "US500", "UK100", "JPN225"
]

# ✅ Simulated strategy scoring logic
def get_strategy_score(pair, timeframe):
    random.seed(hash(pair + timeframe + datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M')))
    return random.randint(50, 100)

# ✅ Simulated prediction logic
def generate_prediction(pair, timeframe):
    choices = ["CALL", "PUT"]
    random.seed(hash(pair + timeframe + datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M')))
    return random.choice(choices)

# ✅ Simulated error analysis
def analyze_error(pair, timeframe):
    return f"{pair} failed due to weak confirmation at support/resistance or liquidity exhaustion."

# ✅ GET all eligible pairs
@app.route("/get_pairs", methods=["GET"])
def get_pairs():
    timeframe = request.args.get("timeframe", "1m")
    threshold = int(request.args.get("threshold", 60))
    eligible_pairs = []

    for pair in ALL_PAIRS:
        score = get_strategy_score(pair, timeframe)
        if score >= threshold:
            eligible_pairs.append(pair)

    return jsonify({"pairs": eligible_pairs})

# ✅ GET prediction for specific pair
@app.route("/get_prediction", methods=["GET"])
def get_prediction():
    pair = request.args.get("pair")
    timeframe = request.args.get("timeframe", "1m")
    threshold = int(request.args.get("threshold", 60))

    score = get_strategy_score(pair, timeframe)

    if score < threshold:
        return jsonify({
            "prediction": "Not eligible",
            "score": score,
            "error_analysis": analyze_error(pair, timeframe)
        })

    prediction = generate_prediction(pair, timeframe)

    return jsonify({
        "prediction": prediction,
        "score": score,
        "error_analysis": ""  # No error if eligible
    })

# ✅ Root route (optional)
@app.route("/", methods=["GET"])
def home():
    return "TradeMind AI backend is running."

# ✅ Run server
if __name__ == "__main__":
    app.run(debug=True)

