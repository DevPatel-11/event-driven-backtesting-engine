"""Web dashboard for backtesting engine."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Mock data for demonstration (in production, connect to actual database)
MOCK_BACKTEST_RUNS = [
    {
        'id': 1,
        'name': 'AAPL Buy & Hold Strategy',
        'strategy': 'BuyAndHold',
        'symbol': 'AAPL',
        'start_date': '2023-01-01',
        'end_date': '2023-12-31',
        'initial_capital': 100000,
        'final_value': 125000,
        'total_return': 25.0,
        'sharpe_ratio': 1.5,
        'max_drawdown': -8.5,
        'trades': 1,
        'win_rate': 100.0
    },
    {
        'id': 2,
        'name': 'MSFT Momentum Strategy',
        'strategy': 'Momentum',
        'symbol': 'MSFT',
        'start_date': '2023-01-01',
        'end_date': '2023-12-31',
        'initial_capital': 100000,
        'final_value': 115000,
        'total_return': 15.0,
        'sharpe_ratio': 1.2,
        'max_drawdown': -12.3,
        'trades': 25,
        'win_rate': 60.0
    }
]

@app.route('/')
def index():
    """Render main dashboard page."""
    return render_template('index.html')

@app.route('/api/backtests')
def get_backtests():
    """Get list of all backtest runs."""
    return jsonify(MOCK_BACKTEST_RUNS)

@app.route('/api/backtests/<int:backtest_id>')
def get_backtest(backtest_id):
    """Get details of a specific backtest run."""
    backtest = next((b for b in MOCK_BACKTEST_RUNS if b['id'] == backtest_id), None)
    if backtest:
        return jsonify(backtest)
    return jsonify({'error': 'Backtest not found'}), 404

@app.route('/api/performance/<int:backtest_id>')
def get_performance(backtest_id):
    """Get performance data for charting."""
    # Mock equity curve data
    equity_curve = [
        {'date': '2023-01-01', 'value': 100000},
        {'date': '2023-03-01', 'value': 105000},
        {'date': '2023-06-01', 'value': 112000},
        {'date': '2023-09-01', 'value': 118000},
        {'date': '2023-12-31', 'value': 125000}
    ]
    return jsonify(equity_curve)

if __name__ == '__main__':
    print('Starting Backtesting Dashboard...')
    print('Access at: http://localhost:5000')
    app.run(host='0.0.0.0', port=5000, debug=True)
