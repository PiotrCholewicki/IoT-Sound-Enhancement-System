#!/usr/bin/env python31

import subprocess
import time
import re
import threading

SCAN_TIME = 10  # sekundy
devices = {}
stop_event = threading.Event()


def reader(process):
    regex = re.compile(r"Device ([0-9A-F:]{17}) (.+)")

    while not stop_event.is_set():
        line = process.stdout.readline()
        if not line:
            continue

        line = line.strip()
        match = regex.search(line)
        if match:
            mac, name = match.groups()
            if mac not in devices:
                devices[mac] = name.strip()
                print(f"[FOUND] {mac} | {name}")


def bluetooth_scan():
    print("[BT] start skanowania")

    process = subprocess.Popen(
        ["bluetoothctl"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    t = threading.Thread(target=reader, args=(process,), daemon=True)
    t.start()

    process.stdin.write("power on\n")
    process.stdin.write("scan on\n")
    process.stdin.flush()

    time.sleep(SCAN_TIME)

    print("[BT] stop skanowania")
    stop_event.set()

    process.stdin.write("scan off\n")
    process.stdin.write("quit\n")
    process.stdin.flush()

    process.terminate()
    t.join(timeout=1)


def main():
    bluetooth_scan()

    print("\n============================")
    print(" ZNALEZIONE URZĄDZENIA")
    print("============================")

    if not devices:
        print("Brak urządzeń")
        return

    for i, (mac, name) in enumerate(devices.items(), 1):
        print(f"{i}. {name} [{mac}]")


if __name__ == "__main__":
    main()
