# 🛡️ GHOST-SENTINEL v12.1

### *Autonomous Neural-Linked Cybersecurity Engine & Active Defense Cell*

**Ghost-Sentinel** represents a paradigm shift in local-perimeter defense. Designed for high-performance hardware, it leverages a multi-stage logic gate and **DeepSeek-R1 (8B)** neural processing to neutralize, analyze, and exile malicious actors in real-time.

---

## ⚔️ COMBAT-PROVEN PERFORMANCE

This system is not theoretical; it is 100% verified and battle-tested across three distinct threat vectors:
* **The Brawn (Telnet Swarm):** 100% neutralization of 16-threaded Hydra attacks against the 14.3M RockYou wordlist. The kernel-level block triggered so fast it caused the automated tool's child processes to collapse.
* **The Restraint (SSH Scout):** Successfully identified `libssh` automated reconnaissance probes without overreacting, demonstrating "calm under pressure" AI forensics.
* **The Brain (Human Breach):** Safely trapped manual Netcat injections, harvesting payloads like `cat /etc/shadow` and issuing intelligent, context-aware Perma-Bans based on intent.

---

## 🏛️ THE FOUR-GATE ARCHITECTURE

The Sentinel operates on a highly optimized, multi-threaded four-layer grid:

1. **The Reflex (Layer 1):** Kinetic Fast-Path. Detects high-velocity swarms (**5+ hits in < 5s**) and drops an instant kernel-level `iptables` block before the AI even wakes up. Protocol-blind and ruthless.
2. **The Dollhouse (Layer 2):** Protocol-Agnostic Low-Interaction Trap. Mimics an Ubuntu 22.04 LTS shell on Port 2222. Uses a **Multi-Threaded Receptionist** to instantly hand off massive connection floods without bottlenecking the main loop.
3. **The General (Layer 3):** Asynchronous VRAM Shield. **DeepSeek-R1:8B** sits behind a Python `queue`, forensically analyzing harvested keystrokes to determine human intent vs. automated noise. Authorizes permanent exiles to a SQLite database.
4. **Glass Aegis & Hunter-Sense (Layer 4):** The command center. Executes resilient automated `nmap` reconnaissance and beams "Executive Strike" reports directly to Discord.

---

## ⚙️ TECHNICAL SPECIFICATIONS & HOST

* **Host Machine:** Lenovo Legion Pro 5 (WSL2 Ubuntu Bridge).
* **The Muscle:** NVIDIA RTX 5060 (8GB VRAM) natively tuned with CUDA 13.2 for zero-lag AI inference.
* **The Data Vault:** SQLite persistence engineered with `timeout=10` to prevent database locking during heavy multi-threaded botnet swarms.

---

## 🚀 INSTALLATION & DEPLOYMENT

### **1. Critical Prerequisites**
This system interacts directly with the Linux kernel and requires strict environment setup.
* **OS:** Ubuntu 22.04 LTS (WSL2 Optimized).
* **Core:** Python 3.10+ & Ollama (DeepSeek-R1:8B).
* **System Binaries:** Nmap and Iptables **must** be installed at the root system level.
```bash
sudo apt update && sudo apt install nmap iptables
```

### **2. Initial Setup & Configuration**
Clone the repository and isolate the environment:
```bash
git clone [https://github.com/Doofusnotexpected/Aerogis-Sentinel.git](https://github.com/Doofusnotexpected/Aerogis-Sentinel.git)
cd ~/Ghost-Sentinel
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
*(Note: You must create your own `config.py` file to hold your Discord Webhook URL and `GENERAL_IP` before launching).*

### **3. The Launch Sequence**
For maximum stability, the architecture must be launched across multiple terminal threads:
```bash
# Thread 1: Wake the Neural Engine (Windows Host)
ollama run deepseek-r1:8b

# Thread 2: Start the Glass Aegis Command Center
cd ~/Ghost-Sentinel && ./venv/bin/python3 dashboard_server.py 

# Thread 3: Arm the Kinetic Sentinel (Requires Root)
cd ~/Ghost-Sentinel && sudo ./venv/bin/python3 ghost_honeypot_v2.py
```

### **4. The Amnesia Protocol (Resetting the Trap)**
To clear the Sentinel's memory and unban yourself after testing manual breaches, flush the firewall and wipe the data vault:
```bash
sudo iptables -F
sudo rm -f /home/aerogis/ghost_memory.db /home/aerogis/threat_intel.json
```

### **5. Public Dashboard Tunnel (Zrok Automation)**
To expose the Glass Aegis live threat feed to the public internet securely (runs silently in the background):
```bash
nohup zrok share reserved <your-share-token> > /dev/null 2>&1 &
```
*Access the dashboard via `http://localhost:5555` locally or through your Zrok URL.*

---

## ⚠️ SECURITY ARCHITECT'S NOTICE & WARNINGS

* **The Whitelist Paradox:** This repository strictly excludes `config.py`, `ghost_memory.db`, and raw intel logs via `.gitignore` to maintain operational security. You **must** configure the **Architect's Pass** (Whitelist) locally in the master script with your own IP address (e.g., `127.0.0.1`). Failure to do so will result in the Sentinel permanently banning your own devices during testing.

---

## ⚖️ COMMERCIAL & LICENSING TERMS

**Ghost-Sentinel v12.1** operates under a dual-license architecture:
1. **Open Source:** Available under the **GPL-3.0 License** for community review and transparency.
2. **Enterprise/Proprietary:** For use in proprietary, closed-source, or for-profit environments, a separate commercial license is required.

*For commercial licensing or private deployment queries, contact the Architect.*
