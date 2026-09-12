# 🛡️ GHOST-SENTINEL v13.5.2
### Dual-Stack AI Active Defense Cell & Neural Siphon Architecture

> A single-operator active defense system, engineered to run enterprise-grade AI threat analysis on consumer laptop hardware.
>
> A Layer-2 kernel firewall with an embedded DeepSeek-R1 LLM and a mathematical RAM-shield, built to survive brute-force swarms and prevent LLM context exhaustion locally.

![Glass Aegis Dashboard](assets/dashboard.png)


Ghost-Sentinel is a multi-threaded active defense cell built to solve a specific problem: running local LLM forensics without bottlenecking a host firewall. It uses a tiered logic gate, `nftables` high-speed sets, and a local AI to neutralize, analyze, and exile malicious actors in real-time.

---

## ⚙️ THE "CONTEXT EXHAUSTION" PROBLEM
Standard LLM-based honeypots have a fatal flaw: **Context Window Exhaustion**. A red-teamer or automated botnet can essentially DDoS the AI by sending thousands of payloads with slight textual variations. The AI attempts to process every log, rapidly exhausting its VRAM and causing systemic crashes.

**The Aerogis Solution: The Neural Siphon**
Ghost-Sentinel solves this using a dual-cache mathematical pre-filter before the AI is ever queried:
1. **O(1) Exact Match (LRU):** A native Python `OrderedDict` immediately catches and drops perfectly identical botnet payloads.
2. **Semantic Clustering (SimHash):** The system applies MD5-deterministic hashing to the payload, extracting 3-gram features into a 64-bit integer. It then calculates the Hamming distance against a deque cache (`maxlen=1000`). If an attacker slightly alters a few bytes to bypass basic filters, the Siphon recognizes the near-identical intent and drops the job from the AI queue, saving compute cycles.

---

## ⚔️ STRESS TEST RESULTS
This architecture has been tested against the following threat vectors:
* **High-Volume Swarms (Telnet & SSH):** Neutralized Hydra attacks (16 parallel threads) against the 14.3M RockYou wordlist across both Telnet and SSH. The `nftables` kernel-level block triggers fast enough to choke the tool, forcing its child processes to crash via connection timeouts.
* **Automated Recon (libssh/Nmap SSH Enumeration):** Correctly classified as reconnaissance rather than active exploitation by DeepSeek-R1 — no false-positive ban triggered.
* **Manual Breaches (Netcat):** Trapped manual injections, logging payloads like `cat /etc/shadow` and issuing context-aware perma-bans based on attacker intent.

---

## 🏛️ THE FIVE-LAYER DEFENSE MATRIX

* **Layer 1 (The Reflex):** Kinetic Fast-Path. Detects high-velocity swarms (5+ hits in < 5s). Drops hostile packets at the network card level via Layer-2 `netdev` hooks. Handles IPv4 and IPv6 `/64` prefix subnet exiling in O(1) constant time.
* **Layer 2 (The Concurrency Shield):** Replaces infinite threading with a strict `ThreadPoolExecutor(max_workers=50)` to prevent CPU context-switching explosions. SQLite databases and JSONL telemetry are hosted in `/dev/shm` (Linux RAM-disk) for high-speed, lock-free I/O.
* **Layer 3 (The Dollhouse):** Protocol-agnostic low-interaction trap. Mimics an Ubuntu 24.04 LTS shell on Port 2222. Spoofs `passwords.txt`, kernel data (`uname`), and blocks binary downloads (`wget`/`curl`) with realistic "Permission denied" errors to keep attackers engaged.
* **Layer 4 (The Neural Siphon):** The MD5-deterministic SimHash interceptor protecting the AI's VRAM.
* **Layer 5 (The General & Glass Aegis):** **DeepSeek-R1 (8B)** asynchronously analyzes sanitized keystrokes to determine intent. Glass Aegis acts as the C2 dashboard, calculating dynamic "Sin Scores" based on time-decaying metrics (last 10 minutes) and sending strike reports to Discord.

---

## ⚙️ ENVIRONMENT & HARDWARE
* **Environment:** Ubuntu 24.04 LTS (tested natively and via WSL2 mirrored networking).
* **AI Inference (Tested Hardware):** Lenovo Legion RTX 5060 Laptop GPU (8GB VRAM) via Ollama's bundled CUDA runtime, with 24GB DDR5 system RAM.
* **State Management:** SQLite persistence configured with `timeout=10` to prevent database locking during heavy multi-threaded botnet swarms.

---

## 🚀 INSTALLATION & DEPLOYMENT

### 1. Prerequisites
This system interacts directly with the Linux kernel and requires a specific environment setup.
* **Core:** Python 3.10+ and Ollama (DeepSeek-R1:8B must be pulled locally).
* **System Binaries:** `nmap` and `nftables` must be installed at the root level.
* **Network (Windows/WSL2 users):** Enable Mirrored Networking (`networkingMode=mirrored` in `.wslconfig`).

    sudo apt update && sudo apt install nmap nftables python3-venv

### 2. Setup
Clone the repository and isolate the environment:

    git clone https://github.com/Doofusnotexpected/Aerogis-Sentinel.git
    cd Aerogis-Sentinel
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

Create a `config.py` file in the project root with your environment variables:

    GENERAL_IP = "127.0.0.1"  # Auto-detects WSL host IP
    DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/your_webhook_here"

### 3. Launch
Run across separate terminals:

    # Terminal 1: Start the local model
    ollama run deepseek-r1:8b

    # Terminal 2: Clear old state
    sudo nft flush ruleset && sudo rm -f /dev/shm/ghost_memory.db ghost_memory.db threat_intel.jsonl

    # Terminal 3: Start the dashboard
    source venv/bin/activate
    python3 dashboard_server.py

    # Terminal 4: Start the honeypot (requires root for nftables)
    sudo ./venv/bin/python ghost_honeypot_v2.py

### 4. Resetting State
To clear the RAM-disk memory and unban yourself after manual testing:

    sudo nft flush ruleset
    sudo rm -f /dev/shm/ghost_memory.db ghost_memory.db threat_intel.jsonl

---

## 🛡️ RULES OF ENGAGEMENT
Ghost-Sentinel includes a modular legal/ethical toggle (`ACTIVE_RECON`) in the master script:
* **Passive Defense (default, False):** Silently logs, drops the connection, and sends telemetry. Suitable for public internet deployments.
* **Active Defense (True):** Intended for internal LANs or authorized CTF ranges only. Fires an `nmap` port-scan back at the attacker's IP to map their OS and open services.

## ⚠️ NOTICE ON WHITELISTING
This repository excludes `config.py` and data vaults via `.gitignore`. You must configure your own whitelist locally in the master script with your own IP address (`127.0.0.1` and `::1` are the defaults). Skipping this will result in the Sentinel banning your own devices.

## ⚖️ LICENSING
Ghost-Sentinel v13.5.2 is dual-licensed:
* **Open source:** available under GPL-3.0 for community review.
* **Commercial:** a separate commercial license is required for for-profit use.
