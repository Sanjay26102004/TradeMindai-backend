from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import random
import time
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

prediction_locks = {}

PAIRS_STRATEGIES = {
    'EUR/USD': 8,
    'GBP/USD': 10,
    'USD/JPY': 6,
    'AUD/USD': 9,
    'USD/CAD': 7
}

TOTAL_STRATEGIES = 10

def predict_next_candle(pair, timeframe, candle_data, previous_candles):
    checklist = {
        "Near Key Level": random.choice([True, False]),
        "Domination Candle": random.choice([True, False]),
        "Exhaustion Candle": random.choice([True, False]),
        "Saturation Zone": random.choice([True, False]),
        "RSI Valid": random.choice([True, False]),
        "Volume Spike": random.choice([True, False]),
        "Wick Rejection": random.choice([True, False]),
        "Fake Breakout Trap": random.choice([True, False]),
        "Domination After Trap": random.choice([True, False]),
        "Range Rejection": random.choice([True, False]),
        "Clean Breakout": random.choice([True, False]),
        "Microstructure Confirmed": random.choice([True, False])
    }

    checklist_score = (sum(checklist.values()) / len(checklist)) * 100

    if checklist_score < 80:
        return None, checklist, checklist_score

    prediction = random.choice(["CALL", "PUT"])
    return prediction, checklist, checklist_score

def log_trade_decision(log_entry):
    log_folder = "trade_logs"
    os.makedirs(log_folder, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = os.path.join(log_folder, f"trade_{timestamp}.json")

    with open(log_file, 'w') as f:
        json.dump(log_entry, f, indent=4)

def analyze_trade_error(log_entry):
    if log_entry['actual_outcome'] != 'LOSS':
        return None

    failed_conditions = [key for key, value in log_entry['checklist'].items() if not value]
    passed_conditions = [key for key, value in log_entry['checklist'].items() if value]

    analysis = {
        "failed_conditions": failed_conditions,
        "passed_conditions": passed_conditions,
        "primary_reason": None,
        "suggestions": []
    }

    if 'Volume Spike' in failed_conditions or 'Microstructure Confirmed' in failed_conditions:
        analysis['primary_reason'] = 'Weak Internal Strength (Volume/Volatility Missing)'
        analysis['suggestions'].append('Ensure Volume Confirmation is prioritized in volatile markets.')

    if 'Wick Rejection' in failed_conditions and 'Near Key Level' in passed_conditions:
        analysis['primary_reason'] = 'False Key Level Rejection'
        analysis['suggestions'].append('Consider tightening wick ratio filter.')

    if 'RSI Valid' in failed_conditions:
        analysis['primary_reason'] = 'RSI Filter Ignored'
        analysis['suggestions'].append('Recheck RSI thresholds in ranging markets.')

    if not analysis['primary_reason']:
        analysis['primary_reason'] = 'Market Noise or External Factor'
        analysis['suggestions'].append('Check economic calendar for news events.')

    return analysis

@app.route('/get_pairs', methods=['POST'])
def get_pairs():
    data = request.json
    timeframe = data.get('timeframe', '')

    eligible_pairs = []
    for pair, implemented_strategies in PAIRS_STRATEGIES.items():
        checklist_score = int((implemented_strategies / TOTAL_STRATEGIES) * 100)
        if checklist_score >= 80:
            eligible_pairs.append(pair)

    return jsonify({'pairs': eligible_pairs})

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    pair = data.get('pair')
    timeframe = data.get('timeframe')
    candle_data = data.get('candle_data', {})
    previous_candles = data.get('previous_candles', [])
    actual_outcome = data.get('actual_outcome', None)

    timeframe_seconds = {'30s': 30, '1m': 60, '5m': 300}.get(timeframe, 60)
    current_time = datetime.utcnow()
    candle_start_time = current_time - timedelta(seconds=current_time.second % timeframe_seconds, microseconds=current_time.microsecond)
    candle_lock_expiry = candle_start_time + timedelta(seconds=timeframe_seconds)
    lock_key = f"{pair}_{timeframe}"

    if lock_key in prediction_locks and prediction_locks[lock_key] > current_time:
        return jsonify({
            'status': 'locked',
            'message': 'Prediction already made for this candle.',
            'lockDuration': (prediction_locks[lock_key] - current_time).seconds
        })

    prediction_locks[lock_key] = candle_lock_expiry

    elapsed_since_candle_start = (current_time - candle_start_time).seconds
    if elapsed_since_candle_start < 5:
        time.sleep(5 - elapsed_since_candle_start)

    prediction, checklist, checklist_score = predict_next_candle(pair, timeframe, candle_data, previous_candles)

    if not prediction:
        return jsonify({
            "status": "no_trade",
            "message": "Checklist accuracy below 80%.",
            "checklist_score": checklist_score,
            "checklist": checklist
        })

    log_entry = {
        "timestamp": current_time.isoformat(),
        "pair": pair,
        "timeframe": timeframe,
        "candle_data": candle_data,
        "previous_candles": previous_candles,
        "prediction": prediction,
        "checklist": checklist,
        "checklist_score": checklist_score,
        "actual_outcome": actual_outcome
    }

    log_trade_decision(log_entry)

    error_analysis = analyze_trade_error(log_entry) if actual_outcome == 'LOSS' else None

    return jsonify({
        "status": "success",
        "prediction": prediction,
        "checklist": checklist,
        "checklist_score": checklist_score,
        "error_analysis": error_analysis,
        "lockDuration": (candle_lock_expiry - current_time).seconds
    })

@app.route('/')
def home():
    return "TradeMind AI Backend is Live!"

if __name__ == '__main__':
    app.run(debug=True)
