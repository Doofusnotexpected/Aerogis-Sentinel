import socket
import time

TARGET_IP = "127.0.0.1"
TARGET_PORT = 2222

# These 5 commands are slightly different strings, but semantically identical (stealing credentials).
# A normal AI would read all 5, burning GPU power. The Siphon should catch them mathematically.
malicious_payloads = [
    "cat /etc/shadow",
    "cat /etc/passwd",
    "cat /etc/sudoers",
    "cat /etc/shadow > out.txt",
    "sudo cat /etc/shadow"
]

print("[*] Launching Semantic Swarm against Ghost-Sentinel...")

for i, payload in enumerate(malicious_payloads):
    try:
        print(f"\n[+] Strike {i+1}: Firing payload -> {payload}")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((TARGET_IP, TARGET_PORT))
        
        # Bypass fake login
        s.recv(1024)
        s.send(b"root\n")
        s.recv(1024)
        s.send(b"password\n")
        s.recv(1024)
        
        # Fire payload
        s.send(payload.encode() + b"\n")
        time.sleep(1) # Wait for AI/Siphon to process
        s.close()
        
    except Exception as e:
        print(f"[-] Strike {i+1} failed/blocked: {e}")

print("\n[*] Swarm complete. Check the Sentinel logs.")
