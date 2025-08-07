from flask import Flask, request, jsonify
from datetime import datetime
import pytz

app = Flask(__name__)

# Placeholder list of pairs (add more as needed)
ALL_PAIRS = [
    "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "NZD/USD", "USD/CAD",
    "USD/CHF", "EUR/JPY", "GBP/JPY", "AUD/JPY", "NZD/JPY", "CAD/JPY",
    "CHF/JPY", "EUR/GBP", "EUR/CHF", "GBP/CHF", "CAD/CHF", "AUD/CHF",
    "NZD/CHF", "GBP/CAD", "AUD/NZD"
]

# Placeholder function to simulate strategy score
def get_strategy_score(pair, timeframe):
    # Simulate score with hash for stable dummy output
    return abs(hash(pair + timeframe)) % 100

# Placeholder function to simulate error analysis
def analyze_error(pair, timeframe):
    return f"Strategy failed due to low momentum or weak wick structure on {pair} ({timeframe})"

# ✅ GET route for eligible pairs
@app.route("/get_pairs", methods=["GET"])
def get_pairs():
    timeframe = request.args.get("timeframe", "1m")
    eligible_pairs = []

    for pair in ALL_PAIRS:
        score = get_strategy_score(pair, timeframe)
        if score >= 60:  # 60% threshold
            eligible_pairs.append(pair)

    return jsonify({"pairs": eligible_pairs})

# ✅ GET route for prediction (URL usage)
@app.route("/get_prediction", methods=["GET"])
def get_prediction():
    pair = request.args.get("pair")
    timeframe = request.args.get("timeframe", "1m")
    score = get_strategy_score(pair, timeframe)

    if score < 60:
        return jsonify({
            "prediction": "Not eligible",
            "score": score,
            "error_analysis": analyze_error(pair, timeframe)
        })

    prediction = "CALL" if score % 2 == 0 else "PUT"

    return jsonify({
        "prediction": prediction,
        "score": score,
        "error_analysis": ""
    })

# ✅ POST route for prediction (JSON body usage)
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    pair = data.get("pair")
    timeframe = data.get("timeframe", "1m")

    if not pair:
        return jsonify({"error": "Missing 'pair' in request"}), 400

    score = get_strategy_score(pair, timeframe)

    if score < 60:
        return jsonify({
            "prediction": "Not eligible",
            "score": score,
            "error_analysis": analyze_error(pair, timeframe)
        })

    prediction = "CALL" if score % 2 == 0 else "PUT"

    return jsonify({
        "prediction": prediction,
        "score": score,
        "error_analysis": ""
    })

# 🟢 Root route to test server is alive
@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "TradeMind AI backend is live!"})

if __name__ == "__main__":
    app.run(debug=True)

