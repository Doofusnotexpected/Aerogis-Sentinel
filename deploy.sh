#!/bin/bash
GREEN='\033[0;32m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${GREEN}[*] Initiating Aerogis v13.5.2 Deployment Sequence...${NC}\n"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[!] Python 3 is not installed.${NC}"
    exit 1
fi

if [ ! -d "venv" ]; then
    echo -e "${CYAN}[*] Creating isolated Python virtual environment (venv)...${NC}"
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
if [ -f "requirements.txt" ]; then
    echo -e "${CYAN}[*] Installing core dependencies...${NC}"
    pip install -r requirements.txt
fi

echo -e "${CYAN}[*] Executing Amnesia Wipe (clearing stale state)...${NC}"
rm -f /dev/shm/ghost_memory.db ghost_memory.db threat_intel.jsonl

echo -e "\n${GREEN}[+] Aerogis v13.5.2 Environment Ready.${NC}"
