#!/usr/bin/env python3
"""
ESP32 Shelf-Light Beacon Terminal Simulator
Track 3 — Amber Box Tracker (Yashwant)

Simulates the physical ESP32-C3 NeoPixel beacon by long-polling:
  GET /api/devices/{DEVICE_ID}/commands?wait=20&battery=..&rssi=..

Provides rich colored ANSI terminal rendering:
  - [BLINK BLUE 30s] : Find / Locate target beacon
  - [BLINK RED 20s]  : Wrong-shelf misplacement alert
  - [ACK GREEN 2s]   : Confirmed put-away
  - [OFF]            : Clear strip

Usage:
  python firmware/shelf-light/sim.py --device shelf-light-01 --server http://localhost:8000
  python firmware/shelf-light/sim.py --demo
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.request

# ANSI Color Codes
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
WHITE = "\033[97m"

BG_BLUE = "\033[44m"
BG_RED = "\033[41m"
BG_GREEN = "\033[42m"


def enable_windows_ansi():
    """Enables virtual terminal processing on Windows if supported."""
    if sys.platform == "win32":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except (AttributeError, OSError) as e:
            log(f"ANSI setup skipped: {e}", DIM)


def log(msg: str, color: str = WHITE):
    ts = time.strftime("%H:%M:%S")
    print(f"{DIM}[{ts}]{RESET} {color}{msg}{RESET}")


def render_light_action(cmd: str, color: str, seconds: int):
    """Renders visual animation block in terminal."""
    if cmd == "blink" or (cmd == "blink_blue" or color == "blue"):
        header = f"{BG_BLUE}{WHITE}{BOLD} [BLINK BLUE - TARGET SHELF] {RESET}"
        bar = f"{BLUE}{BOLD}● ● ● ● ● ● ● ● ● ● ● ●{RESET}"
        log(f"{header} {BLUE}Locate beacon pulsing for {seconds}s{RESET}")
        print(f"       Light Strip: {bar}  {CYAN}*BEEP*{RESET}")
    elif cmd == "blink_red" or color == "red":
        header = f"{BG_RED}{WHITE}{BOLD} [BLINK RED - WRONG SHELF ALERT] {RESET}"
        bar = f"{RED}{BOLD}▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲ ▲{RESET}"
        log(f"{header} {RED}Infraction alarm active for {seconds}s{RESET}")
        print(f"       Light Strip: {bar}  {RED}{BOLD}*ALARM CHIRP*{RESET}")
    elif cmd == "ack" or color == "green":
        header = f"{BG_GREEN}{WHITE}{BOLD} [ACK - CONFIRMED PUT-AWAY] {RESET}"
        bar = f"{GREEN}{BOLD}✔ ✔ ✔ ✔ ✔ ✔ ✔ ✔ ✔ ✔ ✔ ✔{RESET}"
        log(f"{header} {GREEN}Carton correctly stored. Beacon solid green for {seconds}s{RESET}")
        print(f"       Light Strip: {bar}")
    elif cmd == "off":
        log(f"{DIM}[OFF] Strip cleared. Standby.{RESET}")
        print(f"       Light Strip: {DIM}○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○ ○{RESET}")
    else:
        log(f"[COMMAND: {cmd}] color={color} duration={seconds}s", YELLOW)


def run_demo_mode():
    """Cycles through all simulated shelf light modes for instant demo evaluation."""
    log(f"{BOLD}Starting Shelf-Light Demonstration Loop...{RESET}", CYAN)
    time.sleep(1)

    print("\n1. Simulating Carton Locate Request ('Light it up' for BV2401 on L2-B2):")
    render_light_action("blink", "blue", 15)
    time.sleep(2)

    print("\n2. Simulating Wrong Shelf Infraction Alert (Box resting on L3-A1):")
    render_light_action("blink_red", "red", 20)
    time.sleep(2)

    print("\n3. Simulating Confirmed Put-Away (Operator corrected to L2-B2):")
    render_light_action("ack", "green", 2)
    time.sleep(2)

    print("\n4. Reset to Standby:")
    render_light_action("off", "none", 0)
    log(f"\n{GREEN}Demo sequence verified successfully!{RESET}\n")


def poll_server(server: str, device_id: str, wait_sec: int):
    """Long-polls the backend device command queue."""
    url = f"{server.rstrip('/')}/api/devices/{device_id}/commands?wait={wait_sec}&battery=3.98&rssi=-54"
    log(f"Connecting simulator for {BOLD}{device_id}{RESET} -> {CYAN}{url}{RESET}")

    consecutive_errors = 0

    while True:
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": f"ESP32-ShelfLight-Sim/{device_id}", "Accept": "application/json"}
            )
            # Timeout set slightly higher than server wait parameter
            with urllib.request.urlopen(req, timeout=wait_sec + 5) as resp:
                if resp.status == 200:
                    consecutive_errors = 0
                    raw_data = resp.read().decode("utf-8")
                    data = json.loads(raw_data)
                    commands = data.get("commands", [])

                    if commands:
                        for c in commands:
                            cmd = c.get("cmd", "off")
                            color = c.get("color", "blue")
                            seconds = c.get("seconds", 30)
                            render_light_action(cmd, color, seconds)
                    else:
                        # Empty response on timeout (normal long poll heartbeat)
                        log("Long-poll ping ok. Waiting for next event...", DIM)

        except urllib.error.URLError as e:
            consecutive_errors += 1
            if consecutive_errors == 1:
                log(f"Server offline or unreachable ({e.reason}). Retrying every 3s...", YELLOW)
            time.sleep(3)
        except KeyboardInterrupt:
            print("\n")
            log("Simulator stopped by user.", YELLOW)
            break
        except (urllib.error.HTTPError, OSError, TimeoutError, json.JSONDecodeError, KeyError, ValueError) as ex:
            log(f"Poll error: {ex}", RED)
            time.sleep(2)


def main():
    enable_windows_ansi()

    parser = argparse.ArgumentParser(description="ESP32-C3 Shelf-Light Terminal Simulator")
    parser.add_argument("--device", default="shelf-light-01", help="Target device ID (e.g. shelf-light-01)")
    parser.add_argument("--server", default="http://localhost:8000", help="FastAPI backend host")
    parser.add_argument("--wait", type=int, default=20, help="Long poll wait seconds (default: 20)")
    parser.add_argument("--demo", action="store_true", help="Run standalone animation demo loop")

    args = parser.parse_args()

    print(f"""
{CYAN}================================================================={RESET}
{BOLD}{YELLOW}  AMBER BOX TRACKER — ESP32 SHELF LIGHT TERMINAL SIMULATOR{RESET}
{CYAN}  Device ID  : {WHITE}{args.device}{RESET}
{CYAN}  Target Host: {WHITE}{args.server}{RESET}
{CYAN}================================================================={RESET}
""")

    if args.demo:
        run_demo_mode()
    else:
        poll_server(args.server, args.device, args.wait)


if __name__ == "__main__":
    main()
