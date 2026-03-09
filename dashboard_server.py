from flask import Flask, render_template, jsonify
import json
import os

app = Flask(__name__)

JSON_PATH = os.path.expanduser("~/Ghost-Sentinel/threat_intel.json")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/threats')
def get_threats():
    try:
        if os.path.exists(JSON_PATH):
            with open(JSON_PATH, 'r') as f:
                data = json.load(f)
                return jsonify(data[::-1]) # Show newest first
        return jsonify([])
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    # Running on port 5000, listening to all interfaces
    app.run(host='0.0.0.0', port=5000, debug=True)
