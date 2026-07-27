# 🛡️ GHOST-SENTINEL v12.1
### Local-Perimeter AI Honeypot & Active Defense Cell

Ghost-Sentinel is a multi-threaded active defense cell built to solve a specific problem: running local LLM forensics without bottlenecking a host firewall. It uses a multi-stage logic gate and a local DeepSeek-R1 model to neutralize, analyze, and exile malicious actors in real-time.

---

## ⚔️ STRESS TEST BENCHMARKS
This architecture was built and audited against three distinct threat vectors:

* **High-Volume Swarms (Telnet):** Successfully neutralized a 16-threaded Hydra attack against the 14.3M RockYou wordlist. The kernel-level block triggers fast enough to collapse the automated tool's child processes.
* **Automated Recon (SSH):** Identified `libssh` automated reconnaissance probes without overreacting, avoiding false-positive bans on standard network scanners.
* **Manual Breaches (Netcat):** Safely trapped manual injections, harvesting payloads like `cat /etc/shadow` and issuing intelligent, context-aware database bans based on the attacker's intent.

---

## 🏛️ ARCHITECTURE OVERVIEW
The Sentinel operates on a highly optimized four-layer grid:

* **Layer 1 (The Reflex):** Kinetic Fast-Path. Detects high-velocity swarms (**5+ hits in < 5s**) and drops an instant kernel-level `iptables` block before the AI even wakes up.
* **Layer 2 (The Dollhouse):** Protocol-Agnostic Low-Interaction Trap. Mimics an Ubuntu 22.04 LTS shell on Port 2222. Uses a **Multi-Threaded Receptionist** to instantly hand off massive connection floods without bottlenecking the main loop.
* **Layer 3 (The General):** Asynchronous AI Forensics. **DeepSeek-R1 (8B)** sits behind a Python `queue.Queue()`, forensically analyzing harvested keystrokes to determine human intent vs. automated noise. Authorizes permanent exiles to a SQLite database.
* **Layer 4 (Glass Aegis):** Command & Control. Executes resilient automated `nmap` reconnaissance and beams formatted strike reports directly to a Discord webhook.

---

## ⚙️ ENVIRONMENT & HARDWARE BENCHMARKS
* **Environment:** Ubuntu 22.04 LTS (Tested natively and via WSL2 Bridge).
* **AI Inference (Tested Hardware):** Benchmarked on an NVIDIA RTX 5060 (8GB VRAM) running CUDA 13.2. *(Note: Any CUDA-compatible GPU with ~8GB VRAM is recommended to run the 8B model smoothly without latency).*
* **State Management:** SQLite persistence engineered with `timeout=10` to prevent database locking during heavy multi-threaded botnet swarms.

---

## 🚀 INSTALLATION & DEPLOYMENT

### 1. Critical Prerequisites
This system interacts directly with the Linux kernel and requires strict environment setup.
* **Core:** Python 3.10+ & Ollama (DeepSeek-R1:8B).
* **System Binaries:** Nmap and Iptables **must** be installed at the root system level.
```bash
sudo apt update && sudo apt install nmap iptables
```

### 2. Initial Setup & Configuration
Clone the repository and isolate the environment:
```bash
git clone [https://github.com/Doofusnotexpected/Aerogis-Sentinel.git](https://github.com/Doofusnotexpected/Aerogis-Sentinel.git)
cd Aerogis-Sentinel
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Create the Configuration File:**
You must create a `config.py` file in the project root to securely hold your variables.
```bash
nano config.py
```
*Add the following lines:*
```python
# config.py
GENERAL_IP = "127.0.0.1" # The script will auto-detect if you are running WSL!
DISCORD_WEBHOOK_URL = "[https://discord.com/api/webhooks/your_webhook_here](https://discord.com/api/webhooks/your_webhook_here)"
```

### 3. The Launch Sequence
For maximum stability, the architecture should be launched across multiple terminal threads:
```bash
# Thread 1: Wake the Neural Engine
ollama run deepseek-r1:8b

# Thread 2: Start the Glass Aegis Command Center
cd ~/Aerogis-Sentinel && source venv/bin/activate && python3 dashboard_server.py 

# Thread 3: Arm the Kinetic Sentinel (Requires Root)
cd ~/Aerogis-Sentinel && source venv/bin/activate && sudo python3 ghost_honeypot_v2.py
```

### 4. The Amnesia Protocol (Resetting the Trap)
To clear the Sentinel's memory and unban yourself after testing manual breaches, flush the firewall and wipe the local data vault:
```bash
sudo iptables -F
sudo rm -f ghost_memory.db threat_intel.json
```

### 5. Public Dashboard Tunnel (Zrok Automation)
To expose the Glass Aegis live threat feed to the public internet securely (runs silently in the background):
```bash
nohup zrok share reserved <your-share-token> > /dev/null 2>&1 &
```
Access the dashboard via `http://localhost:5555` locally or through your Zrok URL.

---

## ⚠️ SECURITY ARCHITECT'S NOTICE
**The Whitelist Paradox:** This repository strictly excludes `config.py`, `ghost_memory.db`, and raw intel logs via `.gitignore` to maintain operational security. You **must** configure the Architect's Pass (Whitelist) locally in the master script with your own IP address (e.g., `127.0.0.1`). Failure to do so will result in the Sentinel permanently banning your own devices during testing.

---

## ⚖️ LICENSING
**Ghost-Sentinel v12.1** operates under a dual-license architecture:
* **Open Source:** Available under the **GPL-3.0 License** for community review and transparency.
* **Enterprise/Proprietary:** For use in proprietary, closed-source, or for-profit environments, a separate commercial license is required. 
