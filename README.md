# 🛡️ GHOST-SENTINEL v12.1
### *Autonomous Neural-Linked Cybersecurity Engine & Active Defense Cell*

**Ghost-Sentinel** represents a paradigm shift in local-perimeter defense. Designed for high-performance hardware, it leverages a multi-stage logic gate and **DeepSeek-R1 (8B)** neural processing to neutralize, analyze, and exile malicious actors in real-time.

## ⚔️ COMBAT-PROVEN PERFORMANCE
This system is not theoretical; it is battle-tested. During a **"Stress-to-Failure"** audit utilizing a 16-threaded **Hydra attack** against the **14.3M RockYou.txt** wordlist, the Sentinel achieved:
* **Neutralization Rate:** 100% (Zero breaches recorded).
* **Initial Response Latency:** < 1 second (Fast-Path Reflex).
* **VRAM Shielding:** Successfully offloaded high-velocity traffic to an asynchronous queue, maintaining system stability during massive swarm attacks.
* **The Dollhouse Effect:** Automated attackers were successfully trapped in a simulated environment, wasting compute resources while the AI performed deep-packet forensics.

## 🏛️ GLASS AEGIS v1.0 (Command & Control)
The **Glass Aegis** is the visual heart of the Sentinel, providing a military-grade telemetry hub for the Architect.
* **Live Threat Feed:** Real-time data visualization of the "Sin Score" and incoming targets.
* **Hunter-Sense:** Automated **Nmap** reconnaissance triggered instantly upon threat detection.
* **Neural Analysis:** Direct integration with DeepSeek-R1 for intelligent behavioral verdicts on every captured specimen.

## ⚙️ TECHNICAL ARCHITECTURE
The Sentinel operates on a three-tier logic gate:
1.  **The Reflex (Layer 1):** Kinetic pattern matching (5+ hits in < 2s). Triggers an immediate **Kernel-level iptables drop**.
2.  **The General (Layer 2):** Asynchronous AI forensics via **Ollama**. Determines intent without slowing down the firewall.
3.  **The Long Memory (Layer 3):** Stateful **SQLite3** persistence. Upgrades temporary blocks to permanent exiles.

## 🚀 INSTALLATION & DEPLOYMENT
**1. Prerequisites**
* **OS:** Ubuntu (WSL2 Optimized)
* **Core:** Python 3.10+ & Ollama (DeepSeek-R1:8B)
* **Network:** Nmap & iptables

**2. Launch Sequence**
\`\`\`bash
git clone https://github.com/Doofusnotexpected/Aerogis-Sentinel.git
cd ~/Ghost-Sentinel
source venv/bin/activate
python3 dashboard_server.py # Start Glass Aegis
python3 ghost_honeypot_v2.py # Arm the Sentinel
\`\`\`

## ⚠️ SECURITY ARCHITECT'S NOTICE
This repository **strictly excludes** \`config.py\`, \`ghost_memory.db\`, and raw intel logs via \`.gitignore\` to maintain operational security. The **Architect's Pass** (Whitelist) must be configured locally to prevent self-exile during testing.

---
*For commercial licensing or private deployment queries, contact the Architect.*
