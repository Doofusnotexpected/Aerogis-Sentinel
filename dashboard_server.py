from flask import Flask, render_template, jsonify
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)
JSONL_FILE = "threat_intel.jsonl"

def get_threat_data():
    threats = []
    if not os.path.exists(JSONL_FILE):
        return []
    
    try:
        with open(JSONL_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    threats.append(json.loads(line))
    except Exception as e:
        print(f"Dashboard Error: {e}")
        
    return threats[::-1]

@app.route('/')
def index():
    return render_template('index.html') 

@app.route('/api/threats')
def api_threats():
    threat_list = get_threat_data()
    
    # FIX BUG 7: Dynamic, Time-Based Sin Score (The Cooldown Effect)
    recent_threat_count = 0
    ten_mins_ago = datetime.now() - timedelta(minutes=10)
    
    for t in threat_list:
        try:
            # Parse the timestamp from the JSON log (Format: YYYY-MM-DD HH:MM:SS)
            hit_time = datetime.strptime(t['timestamp'], "%Y-%m-%d %H:%M:%S")
            if hit_time > ten_mins_ago:
                recent_threat_count += 1
        except Exception:
            pass # Ignore malformed timestamps
            
    # Calculate load: 5 hits in 10 minutes = 100% Load
    sin_load = min(recent_threat_count * 20, 100) 
    
    return jsonify({
        "threats": threat_list,
        "sin_load": sin_load
    })

if __name__ == '__main__':
    print("[*] Glass Aegis v1.2 (JSONL Compatible) starting on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=False)
