import socket
from datetime import datetime
from collections import deque, OrderedDict
import hashlib
from concurrent.futures import ThreadPoolExecutor
import requests
import json
import subprocess
import threading
import time
import sqlite3
import queue
import os
import shutil
import ipaddress
from scapy.all import sniff, IP, IPv6
import config

# --- LIVE OPTIMIZATION: WSL2 MIRRORED NETWORKING ---
try:
    GENERAL_IP = config.GENERAL_IP
    WEBHOOK_URL = config.DISCORD_WEBHOOK_URL
except AttributeError:
    print("\n[FATAL ERROR]: Your config.py is missing GENERAL_IP or DISCORD_WEBHOOK_URL!")
    print("Please configure your settings before launching the Sentinel.")
    exit(1)

OLLAMA_URL = f"http://{GENERAL_IP}:11434/api/generate"
MODEL_NAME = "deepseek-r1:8b"
ACTIVE_RECON = False # --- Set to True only in authorized labs.

# --- THE ENTROPY SHIELD: RAM-DISK IO ---
DISK_DB_FILE = "ghost_memory.db"
RAM_DB_FILE = "/dev/shm/ghost_memory.db"
JSONL_HUB_FILE = "threat_intel.jsonl" 
BAN_TIMER_SECONDS = 300
WHITELIST_IPS = ["127.0.0.1", "::1"] 

# --- MEMORY, QUEUES & THE NEURAL SIPHON ---
ai_job_queue = queue.Queue()
recent_hits = {}
fast_path_lock = threading.Lock()
# --- O(1) Eviction and proper LRU Caching
siphon_cache = deque(maxlen=1000) 
exact_match_cache = OrderedDict()
SIPHON_LOCK = threading.Lock()

# --- THE NEURAL SIPHON: SEMANTIC HASHING (AEROGIS EXCLUSIVE BECAUSE WHY NOT) ---
def get_simhash(text):
    if not text or text == "[ZERO COMMANDS - AUTOMATED BRUTE-FORCE BEHAVIOR]": 
        return 0
    
    text = text.lower()
    features = [text[i:i+3] for i in range(max(1, len(text)-2))]
    v = [0] * 64
    
    for f in features:
        h = int(hashlib.md5(f.encode('utf-8')).hexdigest(), 16)
        for i in range(64):
            if h & (1 << i): 
                v[i] += 1
            else: 
                v[i] -= 1
                
    fingerprint = 0
    for i in range(64):
        if v[i] > 0: 
            fingerprint |= (1 << i)
            
    return fingerprint

def is_semantic_duplicate(new_hash, threshold=12):
    if new_hash == 0: 
        return False
        
    with SIPHON_LOCK:
        for old_hash in siphon_cache:
            x = (new_hash ^ old_hash) & ((1 << 64) - 1)
            dist = 0
            while x:
                dist += 1
                x &= x - 1
            if dist <= threshold: 
                return True
                
        siphon_cache.append(new_hash)
            
    return False

# --- DATABASE LOGIC (RAM-DISK ACCELERATED) ---
def init_db():
    if os.path.exists(DISK_DB_FILE) and not os.path.exists(RAM_DB_FILE):
        try: 
            shutil.copy2(DISK_DB_FILE, RAM_DB_FILE)
        except Exception as e: 
            print(f"[-] [DB ERROR]: Failed to load RAM disk: {e}", flush=True)
            
    with sqlite3.connect(RAM_DB_FILE, timeout=10) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS threats
                        (ip TEXT PRIMARY KEY, sin_score INTEGER, perma_ban INTEGER)''')

def db_update_threat(ip, score_increase):
    with sqlite3.connect(RAM_DB_FILE, timeout=10) as conn:
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO threats (ip, sin_score, perma_ban) VALUES (?, 0, 0)", (ip,))
        c.execute("UPDATE threats SET sin_score = sin_score + ? WHERE ip = ?", (score_increase, ip))
        c.execute("SELECT sin_score, perma_ban FROM threats WHERE ip = ?", (ip,))
        return c.fetchone()

def sync_daemon():
    while True:
        time.sleep(60)
        try: 
            shutil.copy2(RAM_DB_FILE, DISK_DB_FILE)
        except Exception: 
            pass

# --- TRUE EXPRESS LANE: LAYER-2 NETDEV HOOKS ---
def get_active_interface():
    try:
        res = subprocess.run("ip route | grep default | awk '{print $5}'", shell=True, capture_output=True, text=True)
        return res.stdout.strip() or "eth0"
    except Exception: 
        return "eth0"

def init_nftables():
    iface = get_active_interface()
    print(f"[*] [KERNEL]: Binding Layer-2 Hardware hooks to {iface}...", flush=True)
    
    subprocess.run("nft 'add table netdev ghost_hardware'", shell=True, check=False)
    subprocess.run(f"nft 'add chain netdev ghost_hardware ingress {{ type filter hook ingress device {iface} priority -500 ; }}'", shell=True, check=False)
    
    subprocess.run("nft 'add set netdev ghost_hardware banned_v4 { type ipv4_addr ; flags timeout ; size 65535 ; }'", shell=True, check=False)
    subprocess.run("nft 'add set netdev ghost_hardware banned_v6 { type ipv6_addr ; flags timeout ; size 65535 ; }'", shell=True, check=False)
    
    subprocess.run("nft 'flush chain netdev ghost_hardware ingress'", shell=True, check=False)
    subprocess.run("nft 'add rule netdev ghost_hardware ingress ip saddr @banned_v4 drop'", shell=True, check=False)
    subprocess.run("nft 'add rule netdev ghost_hardware ingress ip6 saddr @banned_v6 drop'", shell=True, check=False)

def enforce_kernel_drop(target_ip, is_perma=False):
    print(f"\n[!!!] [THE REFLEX]: Instant Hardware-Level Drop Executed on {target_ip}!", flush=True)
    try:
        ip_obj = ipaddress.ip_address(target_ip)
        
        if ip_obj.version == 6:
            network = ipaddress.ip_network(f"{target_ip}/64", strict=False)
            ban_string = str(network)
            set_name = "banned_v6"
        else:
            ban_string = target_ip
            set_name = "banned_v4"
            
        subprocess.run(f"nft 'add element netdev ghost_hardware {set_name} {{ {ban_string} }}'", shell=True, check=False)
        
        if not is_perma:
            threading.Timer(BAN_TIMER_SECONDS, unban_ip, args=[target_ip, ban_string]).start()
            
    except Exception as e: 
        print(f"[-] [KERNEL ERROR]: Failed to ban {target_ip} - {e}", flush=True)

def unban_ip(original_ip, ban_string=None):
    if ban_string is None: 
        ban_string = original_ip
        
    if original_ip not in WHITELIST_IPS:
        with sqlite3.connect(RAM_DB_FILE, timeout=10) as conn:
            c = conn.cursor()
            c.execute("SELECT perma_ban FROM threats WHERE ip = ?", (original_ip,))
            result = c.fetchone()
            if result and result[0] == 1:
                print(f"[*] [SENTINEL]: Pardon denied. {original_ip} is Perma-Banned.", flush=True)
                return
    else:
        print(f"[*] [WHITELIST]: Architect detected. Bypassing logic for {original_ip}.", flush=True)
            
    try:
        ip_obj = ipaddress.ip_address(original_ip)
        set_name = "banned_v4" if ip_obj.version == 4 else "banned_v6"
        subprocess.run(f"nft 'delete element netdev ghost_hardware {set_name} {{ {ban_string} }}'", shell=True, check=False)
        print(f"[+] [SENTINEL]: {original_ip} pardoned. Let's see if they behave.", flush=True)
    except Exception as e: 
        print(f"[-] [KERNEL ERROR]: Failed to unban {original_ip} - {e}", flush=True)

# --- THE VRAM SHIELD: AI WORKER WITH NEURAL SIPHON ---
def general_ai_worker():
    print("[*] [VRAM SHIELD]: General AI Thread Online. Context locked at 64k.", flush=True)
    while True:
        job = ai_job_queue.get()
        enemy_ip, time_hit, intel, harvest_data = job
        
        if harvest_data in exact_match_cache:
            print(f"[🛡️] [EXACT MATCH]: Identical bot payload dropped. Bypassing AI.", flush=True)
            db_update_threat(enemy_ip, 5)
            ai_job_queue.task_done()
            continue
            
        exact_match_cache[harvest_data] = True
        if len(exact_match_cache) > 1000: 
            exact_match_cache.popitem(last=False)

        semantic_hash = get_simhash(harvest_data)
        if is_semantic_duplicate(semantic_hash):
            print(f"[🛡️] [NEURAL SIPHON]: Context Exhaustion Prevented! Semantic clone detected from {enemy_ip}. Bypassing AI.", flush=True)
            db_update_threat(enemy_ip, 5)
            ai_job_queue.task_done()
            continue

        print(f"[*] [LAB ALERT]: General reviewing novel intent for {enemy_ip}...", flush=True)
        
        safe_harvest = harvest_data.replace('\n', ' ').replace('\r', '')[:500] 
        
        prompt = f"""You are a strict cybersecurity analyzer. 
Analyze the following sandboxed telemetry. Is this a minor probe or a severe attack? 
If severe, reply strictly with: PERMA_BAN
Otherwise, give a 1-sentence analysis.

--- BEGIN TELEMETRY ---
Target: {enemy_ip}
Fingerprint: {intel}
Actions: {safe_harvest}
--- END TELEMETRY ---"""
        
        try:
            payload = {
                "model": MODEL_NAME, 
                "prompt": prompt, 
                "stream": False,
                "options": {
                    "num_ctx": 64000, 
                    "temperature": 0.1
                }
            }
            response = requests.post(OLLAMA_URL, json=payload)
            ai_intel = response.json()['response'].strip()
            
            if "PERMA_BAN" in ai_intel:
                if enemy_ip in WHITELIST_IPS:
                    print(f"[!] [THE GENERAL]: EXILE AUTHORIZED, BUT OVERRIDDEN BY ARCHITECT WHITELIST.", flush=True)
                else:
                    print(f"[!] [THE GENERAL]: PERMANENT EXILE AUTHORIZED FOR {enemy_ip}.", flush=True)
                    with sqlite3.connect(RAM_DB_FILE, timeout=10) as conn:
                        conn.execute("UPDATE threats SET perma_ban = 1 WHERE ip = ?", (enemy_ip,))
                    enforce_kernel_drop(enemy_ip, is_perma=True)
            else:
                print(f"[+] [THE GENERAL's LOGIC]: {ai_intel}", flush=True)
                
            threading.Thread(target=run_recon, args=(enemy_ip, time_hit, intel, harvest_data, ai_intel), daemon=True).start()
            
        except Exception as e:
            print(f"[-] [GENERAL EXHAUSTION]: AI failed to process - {e}", flush=True)
            
        ai_job_queue.task_done()

def heartbeat_daemon():
    while True:
        send_telemetry("heartbeat")
        time.sleep(300)

def send_telemetry(event_type, details=None):
    if not WEBHOOK_URL or "YOUR_WEBHOOK" in WEBHOOK_URL: 
        return 

    if event_type == "heartbeat":
        payload = {"content": "🟢 **[HEARTBEAT]** Ghost Unit Node Status: Active. Guarding the network."}
    elif event_type == "strike":
        raw_actions = str(details.get('harvest_data', 'None'))
        if len(raw_actions) > 950: 
            raw_actions = raw_actions[:950] + " ... [DATA TRUNCATED]"
            
        raw_recon = str(details.get('recon_analysis', 'No data gathered.'))
        if len(raw_recon) > 950: 
            raw_recon = raw_recon[:950] + "\n... [REPORT REDACTED BY HIGH COMMAND]"
            
        ai_logic = str(details.get('ai_logic', 'Unknown'))
        
        act_val = "```\n" + raw_actions + "\n```"
        recon_val = "```\n" + raw_recon + "\n```"
        
        payload = {
            "embeds": [{
                "title": "🚨 [EXECUTIVE STRIKE AUTHORIZED]",
                "color": 16711680, 
                "description": f"**AI Verdict:** {ai_logic}",
                "fields": [
                    {"name": "Target IP", "value": details.get("enemy_ip", "Unknown"), "inline": True},
                    {"name": "Fingerprint", "value": details.get("intel", "Unknown"), "inline": True},
                    {"name": "Specimen Actions", "value": act_val, "inline": False},
                    {"name": "Hunter-Sense [RECON REPORT]", "value": recon_val, "inline": False}
                ],
                "footer": {"text": "Ghost Unit v13.5 (Dual-Stack) • " + datetime.now().strftime('%H:%M:%S')}
            }]
        }
        
    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=5)
        if response.status_code not in (200, 204):
            print(f"[-] [TELEMETRY ERROR]: Discord rejected the payload! Code: {response.status_code}", flush=True)
        elif event_type == "strike":
            print(f"[+] [TELEMETRY]: Strike report successfully beamed to Discord HQ.", flush=True)
    except Exception as e:
        print(f"[-] [TELEMETRY ERROR]: Could not reach Discord - {e}", flush=True)

def log_to_json_hub(enemy_ip, time_hit, intel, harvest_data, recon_analysis, ai_logic):
    entry = {
        "timestamp": time_hit, 
        "target_ip": enemy_ip, 
        "fingerprint": intel, 
        "actions": harvest_data, 
        "ai_logic": ai_logic, 
        "recon": recon_analysis
    }
    
    try:
        with open(JSONL_HUB_FILE, 'a') as f:
            f.write(json.dumps(entry) + "\n")
        print(f"[*] [HUB]: Threat Intel successfully appended.", flush=True)
    except Exception as e:
        print(f"[-] [HUB ERROR]: Failed to append JSONL: {e}", flush=True)

def run_recon(enemy_ip, time_hit, intel, harvest_data, ai_logic):
    # FIX BUG 5: True Early Return. Skips AI waste and Nmap if safety is on.
    if not ACTIVE_RECON:
        recon_analysis = "[RECON DISABLED FOR LEGAL COMPLIANCE]"
        log_to_json_hub(enemy_ip, time_hit, intel, harvest_data, recon_analysis, ai_logic)
        
        telemetry_data = {
            "enemy_ip": enemy_ip, "intel": intel, "harvest_data": harvest_data, 
            "recon_analysis": recon_analysis, "ai_logic": ai_logic
        }
        send_telemetry("strike", telemetry_data)
        return

    print(f"\n[*] [HUNTER-SENSE]: Initiating active RoE scan on {enemy_ip}...", flush=True)
    recon_analysis = "Nmap timeout due to strict Layer 1 Reflex block. Target is locked out."
    
    try:
        result = subprocess.run(['nmap', '-sV', '-T4', '--top-ports', '100', enemy_ip], capture_output=True, text=True, timeout=10)
        raw_scan = result.stdout
        print(f"[+] [HUNTER-SENSE]: Scan complete for {enemy_ip}. Consulting General...", flush=True)
        
        prompt = f"Analyze this nmap scan for IP {enemy_ip}. Identify the OS and open ports. YOU MUST BE EXTREMELY BRIEF. Use a maximum of 3 short bullet points. Do not write an intro or a summary:\n{raw_scan}"
        
        payload = {
            "model": MODEL_NAME, 
            "prompt": prompt, 
            "stream": False,
            "options": {"num_ctx": 64000, "temperature": 0.1}
        }
        response = requests.post(OLLAMA_URL, json=payload)
        recon_analysis = response.json()['response'].strip()
        
    except subprocess.TimeoutExpired:
        print(f"[-] [HUNTER-SENSE]: Scan timed out. Bypassing to ensure telemetry delivery.", flush=True)
    except Exception as e:
        print(f"[-] [HUNTER-SENSE]: Execution failed: {e}", flush=True)

    log_to_json_hub(enemy_ip, time_hit, intel, harvest_data, recon_analysis, ai_logic)
    
    telemetry_data = {
        "enemy_ip": enemy_ip, 
        "intel": intel, 
        "harvest_data": harvest_data, 
        "recon_analysis": recon_analysis, 
        "ai_logic": ai_logic
    }
    send_telemetry("strike", telemetry_data)

def recv_line(conn):
    buffer = ""
    while True:
        try:
            char = conn.recv(1).decode('utf-8', 'ignore')
            if not char: 
                break 
            if char == '\n' or char == '\r':
                if buffer: 
                    break
                else: 
                    continue 
            buffer += char
        except Exception: 
            break
            
    return buffer.strip()

def analyze_packet(packet):
    if packet.haslayer(IP): 
        return f"TTL: {packet[IP].ttl} (IPv4 OS: {'Linux/Mobile' if packet[IP].ttl <= 64 else 'Windows'})"
    elif packet.haslayer(IPv6): 
        return f"IPv6 Node Detected"
    return "Universal Network Connection"

def interactive_shell(conn):
    try: 
        conn.send(b"\r\nWelcome to Ubuntu 22.04.1 LTS (GNU/Linux 5.15.0-53-generic x86_64)\r\nLast login: Mon Sep 12 08:22:14 2026 from 10.0.0.5\r\n\r\n")
    except Exception: 
        return "[CONNECTION DROPPED - LIKELY AUTOMATED SCANNER]"
        
    action_log = []
    valid_commands = 0
    
    while valid_commands < 3:
        try: 
            conn.send(b"root@prod-server:~# ")
        except Exception: 
            break 
            
        cmd = recv_line(conn)
        if not cmd: 
            break 
            
        valid_commands += 1
        action_log.append(cmd)
        print(f"[!] SPECIMEN TYPED: {cmd}", flush=True)
        
        try:
            cmd_lower = cmd.lower()
            if cmd_lower == "ls": conn.send(b"passwords.txt  config.yml  id_rsa\r\n")
            elif cmd_lower == "whoami": conn.send(b"root\r\n")
            elif cmd_lower == "pwd": conn.send(b"/root\r\n")
            elif cmd_lower == "id": conn.send(b"uid=0(root) gid=0(root) groups=0(root)\r\n")
            elif cmd_lower == "uname -a": conn.send(b"Linux prod-server 5.15.0-53-generic x86_64 GNU/Linux\r\n")
            elif cmd_lower.startswith("cat"): conn.send(b"Permission denied\r\n")
            elif cmd_lower.startswith("wget") or cmd_lower.startswith("curl"): conn.send(b"Resolving host... failed: Name or service not known\r\n")
            else: conn.send(b"bash: command not found\r\n")
        except Exception: 
            break
            
    try: 
        conn.send(b"\r\n[!] CONNECTION TERMINATED BY GHOST_UNIT_ADMIN [!]\r\n")
    except Exception: 
        pass
        
    return " | ".join(action_log) if action_log else "[ZERO COMMANDS - AUTOMATED BRUTE-FORCE BEHAVIOR]"

def process_target(conn, enemy_ip):
    try:
        # Dual-Stack sniff filter
        pkt = sniff(filter=f"tcp and port 2222 and host {enemy_ip}", count=1, timeout=1)
        intel = analyze_packet(pkt[0]) if pkt else "Universal Network Connection"
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
        print(f"[*] Lab Error in process_target: {e}", flush=True)

def deploy_honeypot():
    init_db()
    init_nftables()
    threading.Thread(target=heartbeat_daemon, daemon=True).start()
    threading.Thread(target=sync_daemon, daemon=True).start()
    threading.Thread(target=general_ai_worker, daemon=True).start()
    
    print(f"[*] GHOST UNIT 13.5: UNIVERSAL PROTOCOL OVERHAUL ONLINE.", flush=True)
    print(f"[*] AEROGIS NEURAL SIPHON: ACTIVE. PROTECTING VRAM.", flush=True)
    
    # AF_INET6 naturally listens for both IPv4 and IPv6 on Linux
    trap = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    trap.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    trap.bind(('::', 2222)) 
    trap.listen(100)
    
    target_pool = ThreadPoolExecutor(max_workers=50)

    while True:
        try:
            conn, addr = trap.accept()
            enemy_ip = addr[0].replace('::ffff:', '') 
            current_time = time.time()
            
            with fast_path_lock:
                if enemy_ip not in recent_hits: 
                    recent_hits[enemy_ip] = []
                recent_hits[enemy_ip].append(current_time)
                recent_hits[enemy_ip] = [t for t in recent_hits[enemy_ip] if current_time - t < 5]
                hit_count = len(recent_hits[enemy_ip]) 
                
            with sqlite3.connect(RAM_DB_FILE, timeout=10) as db:
                c = db.cursor()
                c.execute("SELECT perma_ban FROM threats WHERE ip = ?", (enemy_ip,))
                db_res = c.fetchone()
                is_perma = db_res and db_res[0] == 1

            if hit_count >= 5:
                enforce_kernel_drop(enemy_ip) 
                threat_data = db_update_threat(enemy_ip, 10)
                sin_score = threat_data[0] if threat_data else 10
                print(f"[!] [SWARM DETECTED]: {enemy_ip} Fast-Path Blocked. Sin Score: {sin_score}", flush=True)
                conn.close()
                continue
                
            if is_perma and enemy_ip not in WHITELIST_IPS:
                conn.close()
                continue 
                 
            target_pool.submit(process_target, conn, enemy_ip)
            
        except Exception:
            pass

if __name__ == "__main__":
    deploy_honeypot()
