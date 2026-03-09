import socket
from datetime import datetime
import requests
import re
import csv
import json
import subprocess
import threading
import time
import sqlite3
import queue
from scapy.all import *
import config  

# --- AUTO-CONFIGURATION ---
GENERAL_IP = config.GENERAL_IP
OLLAMA_URL = f"http://{GENERAL_IP}:11434/api/generate"
WEBHOOK_URL = config.DISCORD_WEBHOOK_URL
MODEL_NAME = "deepseek-r1:8b"
LOG_FILE = "/home/aerogis/tachyon_lab_results.csv"
JSON_HUB_FILE = "/home/aerogis/threat_intel.json"
DB_FILE = "/home/aerogis/ghost_memory.db"
BAN_TIMER_SECONDS = 300 

# --- THE ARCHITECT's PASS ---
WHITELIST_IPS = ["127.0.0.1"] 

# --- V12 ARCHITECTURE: MEMORY & QUEUES ---
ai_job_queue = queue.Queue()
recent_hits = {}  
fast_path_lock = threading.Lock()

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS threats
                        (ip TEXT PRIMARY KEY, sin_score INTEGER, perma_ban INTEGER)''')

def db_update_threat(ip, score_increase):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO threats (ip, sin_score, perma_ban) VALUES (?, 0, 0)", (ip,))
        c.execute("UPDATE threats SET sin_score = sin_score + ? WHERE ip = ?", (score_increase, ip))
        c.execute("SELECT sin_score, perma_ban FROM threats WHERE ip = ?", (ip,))
        return c.fetchone()

def enforce_kernel_drop(target_ip, is_perma=False):
    print(f"\n[!!!] [THE REFLEX]: Instant Kernel Drop Executed on {target_ip}!", flush=True)
    subprocess.run(f"iptables -A INPUT -s {target_ip} -j DROP", shell=True, check=False)
    if not is_perma:
        threading.Timer(BAN_TIMER_SECONDS, unban_ip, args=[target_ip]).start()

def unban_ip(target_ip):
    # If it's the Boss, skip the Perma-Ban check and just pardon them!
    if target_ip not in WHITELIST_IPS:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute("SELECT perma_ban FROM threats WHERE ip = ?", (target_ip,))
            result = c.fetchone()
            if result and result[0] == 1:
                print(f"[*] [SENTINEL]: Pardon denied. {target_ip} is Perma-Banned.", flush=True)
                return
    else:
        print(f"[*] [WHITELIST]: Architect detected. Bypassing Perma-Ban logic for {target_ip}.", flush=True)

    subprocess.run(f"iptables -D INPUT -s {target_ip} -j DROP", shell=True, check=False)
    print(f"[+] [SENTINEL]: {target_ip} pardoned. Let's see if they behave.", flush=True)

# --- THE VRAM SHIELD: ASYNCHRONOUS AI WORKER ---
def general_ai_worker():
    print("[*] [VRAM SHIELD]: General AI Thread Online. Awaiting queue...", flush=True)
    while True:
        job = ai_job_queue.get()
        enemy_ip, time_hit, intel, harvest_data = job
        
        print(f"[*] [LAB ALERT]: General reviewing backlog for {enemy_ip}...", flush=True)
        prompt = f"""
        Experimental Data: Target {enemy_ip} | Fingerprint: {intel} | Actions: {harvest_data}
        Analyze intent. Is this a minor probe or a severe attack? 
        If severe, reply strictly with: PERMA_BAN
        Otherwise, give a 1-sentence analysis.
        """
        try:
            response = requests.post(OLLAMA_URL, json={"model": MODEL_NAME, "prompt": prompt, "stream": False})
            ai_intel = response.json()['response'].strip()
            
            if "PERMA_BAN" in ai_intel:
                if enemy_ip in WHITELIST_IPS:
                    print(f"[!] [THE GENERAL]: PERMANENT EXILE AUTHORIZED FOR {enemy_ip}, BUT OVERRIDDEN BY ARCHITECT WHITELIST.", flush=True)
                else:
                    print(f"[!] [THE GENERAL]: PERMANENT EXILE AUTHORIZED FOR {enemy_ip}.", flush=True)
                    with sqlite3.connect(DB_FILE) as conn:
                        conn.execute("UPDATE threats SET perma_ban = 1 WHERE ip = ?", (enemy_ip,))
            else:
                print(f"[+] [THE GENERAL's LOGIC]: {ai_intel}", flush=True)
                
            # Trigger Recon & Discord post-analysis
            threading.Thread(target=run_recon, args=(enemy_ip, time_hit, intel, harvest_data), daemon=True).start()
            
        except Exception as e:
            print(f"[-] [GENERAL EXHAUSTION]: AI failed to process - {e}", flush=True)
            
        ai_job_queue.task_done()

def send_telemetry(event_type, details=None):
    if not WEBHOOK_URL or "YOUR_WEBHOOK" in WEBHOOK_URL: return 

    if event_type == "heartbeat":
        payload = {"content": "🟢 **[HEARTBEAT]** Ghost Unit Node Status: Active. Guarding the network."}
    elif event_type == "strike":
        raw_actions = str(details.get('harvest_data', 'None'))
        if len(raw_actions) > 950: raw_actions = raw_actions[:950] + " ... [DATA TRUNCATED]"
            
        raw_recon = str(details.get('recon_analysis', 'No data gathered.'))
        if len(raw_recon) > 950: raw_recon = raw_recon[:950] + "\n... [REPORT REDACTED BY HIGH COMMAND]"
        
        payload = {
            "embeds": [{
                "title": "🚨 [EXECUTIVE STRIKE AUTHORIZED]",
                "color": 16711680, 
                "description": "The General has banished a malicious specimen and completed active reconnaissance.",
                "fields": [
                    {"name": "Target IP", "value": details.get("enemy_ip", "Unknown"), "inline": True},
                    {"name": "Fingerprint", "value": details.get("intel", "Unknown"), "inline": True},
                    {"name": "Specimen Actions", "value": f"```{raw_actions}```", "inline": False},
                    {"name": "Hunter-Sense [RECON REPORT]", "value": f"```{raw_recon}```", "inline": False}
                ],
                "footer": {"text": f"Ghost Unit v12.1 • {datetime.now().strftime('%H:%M:%S')}"}
            }]
        }
    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=5)
        if response.status_code not in (200, 204):
            print(f"[-] [TELEMETRY ERROR]: Discord rejected the payload! Code: {response.status_code}", flush=True)
        else:
            print(f"[+] [TELEMETRY]: Strike report successfully beamed to Discord HQ.", flush=True)
    except Exception as e:
        print(f"[-] [TELEMETRY ERROR]: Could not reach Discord - {e}", flush=True)

def log_to_json_hub(enemy_ip, time_hit, intel, harvest_data, recon_analysis):
    new_entry = {
        "timestamp": time_hit,
        "target_ip": enemy_ip,
        "fingerprint": intel,
        "specimen_actions": harvest_data,
        "hunter_recon_analysis": recon_analysis
    }
    try:
        try:
            with open(JSON_HUB_FILE, 'r') as f: db = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError): db = [] 
        db.append(new_entry)
        with open(JSON_HUB_FILE, 'w') as f: json.dump(db, f, indent=4)
        print(f"[*] [HUB]: Threat Intel successfully archived to JSON.", flush=True)
    except Exception as e:
        print(f"[-] [HUB ERROR]: Failed to write JSON: {e}", flush=True)

def run_recon(enemy_ip, time_hit, intel, harvest_data):
    print(f"\n[*] [HUNTER-SENSE]: Initiating active RoE scan on {enemy_ip}...", flush=True)
    try:
        result = subprocess.run(['nmap', '-sV', '-T4', '--top-ports', '100', enemy_ip], capture_output=True, text=True, timeout=60)
        raw_scan = result.stdout
        print(f"[+] [HUNTER-SENSE]: Scan complete for {enemy_ip}. Consulting General...", flush=True)
        
        prompt = f"Analyze this nmap scan for IP {enemy_ip}. Identify the OS and open ports. YOU MUST BE EXTREMELY BRIEF. Use a maximum of 3 short bullet points. Do not write an intro or a summary:\n{raw_scan}"
        response = requests.post(OLLAMA_URL, json={"model": MODEL_NAME, "prompt": prompt, "stream": False})
        recon_analysis = response.json()['response'].strip()
        
        log_to_json_hub(enemy_ip, time_hit, intel, harvest_data, recon_analysis)
        telemetry_data = {"enemy_ip": enemy_ip, "intel": intel, "harvest_data": harvest_data, "recon_analysis": recon_analysis}
        send_telemetry("strike", telemetry_data)
    except Exception as e:
        print(f"[-] [HUNTER-SENSE]: Execution failed: {e}", flush=True)

def heartbeat_daemon():
    while True:
        send_telemetry("heartbeat")
        time.sleep(300)

def recv_line(conn):
    buffer = ""
    while True:
        try:
            char = conn.recv(1).decode('utf-8', 'ignore')
            if not char: break 
            if char == '\n' or char == '\r':
                if buffer: break
                else: continue 
            buffer += char
        except Exception: break
    return buffer.strip()

def analyze_packet(packet):
    if packet.haslayer(IP): return f"TTL: {packet[IP].ttl} (Target OS: {'Linux/Mobile' if packet[IP].ttl <= 64 else 'Windows'})"
    return "No IP Layer Detected"

def interactive_shell(conn):
    try: conn.send(b"\r\nWelcome to Ubuntu 22.04.1 LTS (GNU/Linux 5.15.0-53-generic x86_64)\r\nLast login: Mon Sep 12 08:22:14 2026 from 10.0.0.5\r\n\r\n")
    except Exception: return "[CONNECTION DROPPED - LIKELY AUTOMATED SCANNER]"
    action_log = []
    valid_commands = 0
    while valid_commands < 3:
        try: conn.send(b"root@prod-server:~# ")
        except Exception: break 
        cmd = recv_line(conn)
        if not cmd: break 
        valid_commands += 1
        action_log.append(cmd)
        print(f"[!] SPECIMEN TYPED: {cmd}", flush=True)
        try:
            if cmd == "ls": conn.send(b"passwords.txt  config.yml  id_rsa\r\n")
            elif cmd == "whoami": conn.send(b"root\r\n")
            elif cmd == "pwd": conn.send(b"/root\r\n")
            else: conn.send(b"bash: command not found\r\n")
        except Exception: break
    try: conn.send(b"\r\n[!] CONNECTION TERMINATED BY GHOST_UNIT_ADMIN [!]\r\n")
    except: pass
    return " | ".join(action_log) if action_log else "[ZERO COMMANDS - AUTOMATED BRUTE-FORCE BEHAVIOR]"

def deploy_honeypot():
    init_db()
    threading.Thread(target=heartbeat_daemon, daemon=True).start()
    threading.Thread(target=general_ai_worker, daemon=True).start()
    print(f"[*] GHOST UNIT 12.1: TIERED DEFENSE + WHITELIST ONLINE. LISTENING ON 0.0.0.0", flush=True)
    
    trap = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    trap.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    trap.bind(('0.0.0.0', 2222))
    trap.listen(5)
    
    while True:
        try:
            conn, addr = trap.accept()
            enemy_ip = addr[0]
            current_time = time.time()
            
            # --- THE REFLEX (LAYER 1) ---
            with fast_path_lock:
                if enemy_ip not in recent_hits: recent_hits[enemy_ip] = []
                recent_hits[enemy_ip].append(current_time)
                recent_hits[enemy_ip] = [t for t in recent_hits[enemy_ip] if current_time - t < 2]
                
                with sqlite3.connect(DB_FILE) as db:
                    c = db.cursor()
                    c.execute("SELECT perma_ban FROM threats WHERE ip = ?", (enemy_ip,))
                    db_res = c.fetchone()
                    is_perma = db_res and db_res[0] == 1

            if is_perma and enemy_ip not in WHITELIST_IPS:
                conn.close()
                continue 

            if len(recent_hits[enemy_ip]) >= 5:
                enforce_kernel_drop(enemy_ip) 
                sin_score, _ = db_update_threat(enemy_ip, 10) 
                print(f"[!] [SWARM DETECTED]: {enemy_ip} Fast-Path Blocked. Sin Score: {sin_score}", flush=True)
                
                ai_job_queue.put((enemy_ip, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Fast-Path Block", "SWARM ATTACK"))
                conn.close()
                continue
                
            pkt = sniff(filter=f"tcp and port 2222 and host {enemy_ip}", count=1, timeout=1)
            intel = analyze_packet(pkt[0]) if pkt else "Network Connection"
            print(f"\n[!!!] SPECIMEN ENGAGED: {enemy_ip} | {intel}", flush=True)
            
            try:
                conn.send(b"login: ")
                user = recv_line(conn)
                conn.send(b"password: ")
                pw = recv_line(conn)
                harvested_commands = interactive_shell(conn)
            except Exception:
                user, pw, harvested_commands = "[DROPPED]", "[DROPPED]", "[BRUTE-FORCE DISCONNECT]"
            finally:
                conn.close()
            
            full_harvest = f"Login: {user}/{pw} | Commands: {harvested_commands}"
            db_update_threat(enemy_ip, 1) 
            
            ai_job_queue.put((enemy_ip, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), intel, full_harvest))
            
        except Exception as e:
            print(f"[*] Lab Error: {e}", flush=True)

if __name__ == "__main__":
    deploy_honeypot()
