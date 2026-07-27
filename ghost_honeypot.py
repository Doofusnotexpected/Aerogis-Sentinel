import socket
from datetime import datetime
import requests
import json
import re
import csv
from scapy.all import *

# --- CONFIGURATION ---
# Replace with your Windows IP from 'ip route | grep default'
OLLAMA_URL = "http://172.28.144.1:11434/api/generate"
MODEL_NAME = "deepseek-r1:8b"
LOG_FILE = "tachyon_lab_results.csv"

def analyze_packet(packet):
    """The 'Microscope' function to extract hidden features."""
    if packet.haslayer(IP):
        ttl = packet[IP].ttl
        # TTL 64 is usually Linux/Android/iOS; 128 is Windows.
        os_guess = "Linux/Mobile" if ttl <= 64 else "Windows"
        return f"TTL: {ttl} (Target OS: {os_guess})"
    return "No IP Layer Detected"

def consult_general(enemy_ip, time_hit, packet_intel):
    print(f"[*] [LAB ALERT]: New specimen acquired from {enemy_ip}!")
    
    prompt = f"""
    Experimental Data:
    - Target IP: {enemy_ip} 
    - Timestamp: {time_hit}
    - Packet Fingerprint: {packet_intel}
    
    Tachyon Analysis Request: 
    1. Determine if this is a bot, a mobile device, or a workstation.
    2. Provide ONLY the 'iptables' command to drop this specific IP in a bash block.
    """
    
    try:
        response = requests.post(OLLAMA_URL, json={"model": MODEL_NAME, "prompt": prompt, "stream": False})
        ai_intel = response.json()['response']
        
        # PERSISTENT LAB LOGS
        with open(LOG_FILE, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([time_hit, enemy_ip, packet_intel, ai_intel.replace('\n', ' ')])
        
        print(f"\n[GENERAL'S ANALYSIS]:\n{ai_intel}\n")
        
        # AGENTIC EXTRACTION
        match = re.search(r'```bash\n(.*?)\n```', ai_intel, re.DOTALL)
        if match:
            weapon = match.group(1).strip()
            print(f"[!] LETHAL WEAPON EXTRACTED: {weapon}")
            if enemy_ip == "127.0.0.1":
                print("[!] SAFETY CATCH: Loopback detected. Fire suppressed.")
            else:
                print(f"[!] AUTHORIZED: Simulation mode—Command would execute now.")
                
    except Exception as e:
        print(f"[-] Comms failure: {e}")

def deploy_honeypot():
    print(f"[*] GHOST UNIT 5.1: TACHYON LAB ONLINE (Legion Pro 5)")
    print(f"[*] Monitoring Port 2222 for specimens...")
    
    # Setup the trap
    trap = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    trap.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    trap.bind(('0.0.0.0', 2222))
    trap.listen(5)
    
    while True:
        try:
            conn, addr = trap.accept()
            enemy_ip = addr[0]
            
            # SNIFF THE SPECIMEN (Capture the handshake packet)
            # This requires 'sudo' to work!
            pkt = sniff(filter=f"tcp and port 2222 and host {enemy_ip}", count=1, timeout=1)
            intel = analyze_packet(pkt[0]) if pkt else "Local Loopback (No Headers)"
            
            print(f"\n[!!!] SPECIMEN TRAPPED: {enemy_ip} | {intel}")
            
            # Send fake SSH banner to bait the attacker
            conn.send(b"SSH-2.0-OpenSSH_8.4p1 Debian-5\r\n")
            conn.close()
            
            # Consult the AI
            consult_general(enemy_ip, datetime.now().strftime("%H:%M:%S"), intel)
            
        except Exception as e:
            print(f"[*] Lab Error: {e}")

if __name__ == "__main__":
    try:
        deploy_honeypot()
    except KeyboardInterrupt:
        print("\n[*] Lab shutting down. Securing specimens.")
