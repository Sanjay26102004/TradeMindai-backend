from flask import Flask, request, jsonify
import datetime

app = Flask(__name__)

# Dummy strategy score function
def get_strategy_score(pair, timeframe):
    return 65  # Dummy static score for now

# Dummy error analysis
def analyze_error(pair, timeframe):
    return f"No clear signal for {pair} at {timeframe} timeframe."

# All supported Quotex pairs (example)
ALL_PAIRS = [
    "EUR/USD", "GBP/USD", "CHF/JPY", "USD/JPY", "CAD/JPY", "AUD/USD", "NZD/USD",
    "EUR/GBP", "GBP/CHF", "USD/CHF", "CAD/CHF", "AUD/CHF", "NZD/CHF", "EUR/CHF",
    "GBP/JPY", "USD/CAD", "AUD/JPY", "NZD/JPY", "EUR/JPY", "GBP/CAD", "AUD/NZD"
]

@app.route("/")
def home():
    return "TradeMind AI Backend is live!"

@app.route("/get_pairs", methods=["GET"])
def get_pairs():
    timeframe = request.args.get("timeframe", "1m")
    eligible_pairs = []

    for pair in ALL_PAIRS:
        score = get_strategy_score(pair, timeframe)
        if score >= 60:
            eligible_pairs.append(pair)

    return jsonify({"pairs": eligible_pairs})

@app.route("/get_prediction", methods=["POST"])
def get_prediction():
    data = request.get_json()
    pair = data.get("pair")
    timeframe = data.get("timeframe", "1m")
    score = get_strategy_score(pair, timeframe)

    if score < 60:
        return jsonify({
            "prediction": "Not eligible",
            "score": score,
            "error_analysis": analyze_error(pair, timeframe)
        })

    # Else return prediction
    prediction = "CALL" if datetime.datetime.now().second % 2 == 0 else "PUT"
    return jsonify({
        "prediction": prediction,
        "score": score,
        "error_analysis": None
    })

if __name__ == "__main__":
    app.run(debug=True)

