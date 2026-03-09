🛡️ Ghost-Sentinel v12.1: Autonomous AI Defense Cell

Ghost-Sentinel is a high-performance, asynchronous cybersecurity honeypot and active defense system. Engineered to run locally on high-end hardware, it utilizes a tiered defense architecture to neutralize automated brute-force attacks in real-time while performing AI-driven behavioral forensics.

⚔️ Combat-Proven Metrics (The RockYou Benchmark)

During a "Stress-to-Failure" test utilizing a 16-threaded Hydra attack and the 14.3M RockYou.txt wordlist, the Sentinel achieved:

Neutralization Rate: 100%
Initial Response Latency: < 1 second (Fast-Path)
Total Sin Score Accumulated: 84+ (Attacker Exiled)
Hardware Impact: Negligible CPU/VRAM usage via VRAM Shield job-queuing.

⚙️ Core Architecture The system operates on a three-layer logic gate:

1. The Reflex (Layer 1: Fast-Path): A high-speed pattern matcher that identifies swarm behavior (5+ hits in < 2s). It bypasses AI processing to fire an immediate Kernel-level iptables drop.
2. The General (Layer 2: AI Forensics): Utilizing a locally hosted DeepSeek-R1 (8B) model via Ollama, the Sentinel analyzes captured specimen actions asynchronously.
3. The Long Memory (Layer 3: Persistence): A stateful SQLite3 database that tracks threat history, ensuring temporary bans are upgraded to permanent blacklists.

📡 Hunter-Sense & Telemetry

Hunter-Sense: Automated Nmap reconnaissance triggered upon threat neutralization.
Ghost-Hub: Real-time telemetry relayed to Discord HQ via encrypted webhooks.
Architect's Pass: Hardcoded whitelist overrides to prevent accidental lockouts.

🛠️ Installation & Deployment

Prerequisites:
- Ubuntu (WSL2 supported)
- Python 3.10+
- Ollama (DeepSeek-R1:8B)
- Nmap

Setup:
1. Clone the Repository: git clone https://github.com/Doofusnotexpected/Aerogis-Sentinel.git
2. cd ~/Ghost-Sentinel
