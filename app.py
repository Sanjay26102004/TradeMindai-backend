from flask import Flask, jsonify, request
import requests
from datetime import datetime
import pytz

app = Flask(__name__)

# All Quotex Forex pairs
ALL_PAIRS = [
    "EUR/USD", "GBP/USD", "CHF/JPY", "USD/JPY", "CAD/JPY", "AUD/USD", "NDZ/USD",
    "EUR/GBP", "GBP/CHF", "USD/CHF", "CAD/CHF", "AUD/CHF", "NZD/CHF",
    "EUR/CHF", "GBP/JPY", "USD/CAD", "AUD/JPY", "NZD/JPY", "EUR/JPY",
    "GBP/CAD", "AUD/NZD"
]

# Example strategy checklist (replace with real logic later)
def get_strategy_score(pair, timeframe):
    # Dummy score generation logic (replace with real one)
    score = hash(pair + timeframe) % 100
    return score

# Simulate prediction logic
def make_prediction(pair, timeframe):
    current_time = datetime.now(pytz.timezone("UTC"))
    minute = current_time.minute
    if minute % 2 == 0:
        return "CALL"
    else:
        return "PUT"

def analyze_error(pair, timeframe):
    return f"The market structure for {pair} on {timeframe} may not match the expected wick exhaustion or domination."

@app.route("/get_pairs", methods=["GET"])
def get_pairs():
    timeframe = request.args.get("timeframe", "1m")
    eligible_pairs = []

    for pair in ALL_PAIRS:
        score = get_strategy_score(pair, timeframe)
        if score >= 60:  # Eligibility 60%
            eligible_pairs.append(pair)

    return jsonify({"pairs": eligible_pairs})

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

    prediction = make_prediction(pair, timeframe)

    return jsonify({
        "pair": pair,
        "timeframe": timeframe,
        "prediction": prediction,
        "score": score,
        "error_analysis": "" if prediction else analyze_error(pair, timeframe)
    })

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "TradeMind AI Backend is live!"})

if __name__ == "__main__":
    app.run(debug=True)

