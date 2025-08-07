from flask import Flask, request, jsonify
from datetime import datetime
import random

app = Flask(__name__)

# All Quotex Pairs
ALL_PAIRS = [
    "EUR/USD", "GBP/USD", "CHF/JPY", "USD/JPY", "CAD/JPY", "AUD/USD", "NZD/USD",
    "EUR/GBP", "GBP/CHF", "USD/CHF", "CAD/CHF", "AUD/CHF", "NZD/CHF", "EUR/CHF",
    "GBP/JPY", "USD/CAD", "AUD/JPY", "NZD/JPY", "EUR/JPY", "GBP/CAD", "AUD/NZD",
    "BTC/USD", "ETH/USD", "LTC/USD", "XRP/USD", "EOS/USD", "BNB/USD",
    "DOW", "NASDAQ", "S&P500", "FTSE100", "NIKKEI"
]

# Dummy Strategy Score (Replace with your real logic)
def get_strategy_score(pair, timeframe):
    random.seed(hash(pair + timeframe + datetime.utcnow().strftime("%Y-%m-%d %H:%M")))
    return random.randint(50, 100)

# Dummy Prediction (Replace with your real logic)
def get_prediction_result(pair, timeframe):
    random.seed(hash(pair + timeframe + datetime.utcnow().strftime("%Y-%m-%d %H:%M")))
    return random.choice(["CALL", "PUT"])

# Dummy Error Analysis (Replace with your real logic)
def analyze_error(pair, timeframe):
    return f"Strategy mismatch due to volume exhaustion or late entry on {pair} in {timeframe}."

@app.route("/get_pairs", methods=["GET"])
def get_pairs():
    timeframe = request.args.get("timeframe", "1m")
    eligible_pairs = []

    for pair in ALL_PAIRS:
        score = get_strategy_score(pair, timeframe)
        if score >= 60:
            eligible_pairs.append(pair)

    return jsonify({"pairs": eligible_pairs})


@app.route("/get_prediction", methods=["GET"])
def get_prediction_get():
    pair = request.args.get("pair")
    timeframe = request.args.get("timeframe", "1m")

    if not pair:
        return jsonify({"error": "Pair is required"}), 400

    score = get_strategy_score(pair, timeframe)
    if score < 60:
        return jsonify({
            "prediction": "Not eligible",
            "score": score,
            "error_analysis": analyze_error(pair, timeframe)
        })

    prediction = get_prediction_result(pair, timeframe)
    return jsonify({
        "prediction": prediction,
        "score": score,
        "error_analysis": None
    })

@app.route("/get_prediction", methods=["POST"])
def get_prediction_post():
    data = request.get_json()
    pair = data.get("pair")
    timeframe = data.get("timeframe", "1m")

    if not pair:
        return jsonify({"error": "Pair is required"}), 400

    score = get_strategy_score(pair, timeframe)
    if score < 60:
        return jsonify({
            "prediction": "Not eligible",
            "score": score,
            "error_analysis": analyze_error(pair, timeframe)
        })

    prediction = get_prediction_result(pair, timeframe)
    return jsonify({
        "prediction": prediction,
        "score": score,
        "error_analysis": None
    })

if __name__ == "__main__":
    app.run(debug=True)

