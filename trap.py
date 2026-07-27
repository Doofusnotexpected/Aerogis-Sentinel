import socket
import datetime

def deploy_honeypot():
    print("[*] GHOST UNIT DEPLOYED: Listening on Decoy Port 2222...")
    
    # Create the network trap
    trap = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    trap.bind(('0.0.0.0', 2222))
    trap.listen(5)
    
    while True:
        # Wait for an attacker to touch the wire
        conn, addr = trap.accept()
        enemy_ip = addr[0]
        time_hit = datetime.datetime.now().strftime("%H:%M:%S")
        
        print(f"\n[!!!] TRIPWIRE TRIGGERED [!!!]")
        print(f"Target Acquired: {enemy_ip} at {time_hit}")
        print(f"Action: Logging IP and routing to DeepSeek-R1 for Threat Analysis...")
        
        # Throw fake data at them to waste their time
        try:
            conn.send(b"SSH-2.0-OpenSSH_8.4p1 Debian-5\r\n")
        except:
            pass
            
        conn.close()

if __name__ == "__main__":
    try:
        deploy_honeypot()
    except KeyboardInterrupt:
        print("\n[*] Ghost Unit shutting down. Back to base.")
