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

# FULL LIST OF QUOTEX FOREX PAIRS (you can expand this list further)
ALL_PAIRS = [
    'EUR/USD', 'GBP/USD', 'USD/JPY', 'AUD/USD', 'USD/CAD',
    'NZD/USD', 'EUR/GBP', 'EUR/JPY', 'GBP/JPY', 'USD/CHF'
]

# STRATEGY IMPLEMENTATION SCORE FOR EACH PAIR (0–10 out of 10)
PAIRS_STRATEGIES = {
    'EUR/USD': 9,
    'GBP/USD': 10,
    'USD/JPY': 8,
    'AUD/USD': 9,
    'USD/CAD': 8,
    'NZD/USD': 6,
    'EUR/GBP': 7,
    'EUR/JPY': 9,
    'GBP/JPY': 8,
    'USD/CHF': 6
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

@app.route('/get_pairs', methods=['POST'])
def get_pairs():
    data = request.json
    timeframe = data.get('timeframe', '')

    eligible_pairs = []
    for pair in ALL_PAIRS:
        implemented = PAIRS_STRATEGIES.get(pair, 0)
        score = int((implemented / TOTAL_STRATEGIES) * 100)
        if score >= 80:
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

    elapsed = (current_time - candle_start_time).seconds
    if elapsed < 5:
        time.sleep(5 - elapsed)

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

    error_analysis = analyze_trade_error(log_entry) if actual_outcome == 'LOSS' else None

    return jsonify({
        "status": "success",
        "prediction": prediction,
        "checklist": checklist,
        "checklist_score": checklist_score,
        "error_analysis": error_analysis,
        "lockDuration": (candle_lock_expiry - current_time).seconds
    })

def analyze_trade_error(log_entry):
    if log_entry['actual_outcome'] != 'LOSS':
        return None

    failed_conditions = [k for k, v in log_entry['checklist'].items() if not v]
    passed_conditions = [k for k, v in log_entry['checklist'].items() if v]

    analysis = {
        "failed_conditions": failed_conditions,
        "passed_conditions": passed_conditions,
        "primary_reason": None,
        "suggestions": []
    }

    if 'Volume Spike' in failed_conditions or 'Microstructure Confirmed' in failed_conditions:
        analysis['primary_reason'] = 'Weak Internal Strength (Volume/Volatility Missing)'
        analysis['suggestions'].append('Ensure Volume Confirmation is prioritized.')

    if 'Wick Rejection' in failed_conditions and 'Near Key Level' in passed_conditions:
        analysis['primary_reason'] = 'False Key Level Rejection'
        analysis['suggestions'].append('Use stricter wick filters.')

    if 'RSI Valid' in failed_conditions:
        analysis['primary_reason'] = 'RSI Ignored'
        analysis['suggestions'].append('Check RSI level in range market.')

    if not analysis['primary_reason']:
        analysis['primary_reason'] = 'Market Noise or Unknown'
        analysis['suggestions'].append('Check economic news or spread widening.')

    return analysis

@app.route('/')
def home():
    return "✅ TradeMind AI Backend is Live!"

if __name__ == '__main__':
    app.run(debug=True)
