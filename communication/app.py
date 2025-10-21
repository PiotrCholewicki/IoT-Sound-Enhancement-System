from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import subprocess
import shlex
import re
import os

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# 🔍 Funkcja skanująca sieci przez wlan1
def scan_networks():
    try:
        cmd = shlex.split("sudo iwlist wlan1 scan")
        result = subprocess.run(cmd, capture_output=True, text=True)
        output = result.stdout

        networks = re.findall(r'ESSID:"(.*?)"', output)
        return sorted(list(set([n for n in networks if n])))
    except Exception as e:
        return [f"Błąd: {e}"]

# 📡 Połączenie z siecią
def connect_to_wifi(ssid, password):
    try:
        wpa_conf = "/etc/wpa_supplicant/wpa_supplicant-wlan1.conf"
        wpa_content = f"""
network={{
    ssid="{ssid}"
    psk="{password}"
}}
"""
        with open(wpa_conf, "w") as f:
            f.write(wpa_content)

        # Restart interfejsu
        subprocess.run(["sudo", "wpa_cli", "-i", "wlan1", "reconfigure"], check=False)
        subprocess.run(["sudo", "dhclient", "-r", "wlan1"], check=False)
        subprocess.run(["sudo", "dhclient", "wlan1"], check=False)

        return True
    except Exception as e:
        return str(e)

# 🔧 Pobranie aktualnego statusu
def get_wifi_status():
    try:
        ssid = subprocess.run(["iwgetid", "-r", "wlan1"], capture_output=True, text=True).stdout.strip()
        ip_out = subprocess.run(["ip", "addr", "show", "wlan1"], capture_output=True, text=True).stdout
        ip_match = re.search(r"inet (\d+\.\d+\.\d+\.\d+)", ip_out)
        ip = ip_match.group(1) if ip_match else "Brak adresu IP"

        signal_out = subprocess.run(["iwconfig", "wlan1"], capture_output=True, text=True).stdout
        signal_match = re.search(r"Signal level=(-?\d+) dBm", signal_out)
        signal = f"{signal_match.group(1)} dBm" if signal_match else "Nieznany"

        return {"ssid": ssid or "Niepołączony", "ip": ip, "signal": signal}
    except Exception as e:
        return {"ssid": "Błąd", "ip": str(e), "signal": "-"}

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    networks = scan_networks()
    status = get_wifi_status()
    return templates.TemplateResponse("index.html", {"request": request, "networks": networks, "status": status})

@app.post("/connect")
def connect(request: Request, ssid: str = Form(...), password: str = Form(...)):
    result = connect_to_wifi(ssid, password)
    if result is True:
        return JSONResponse({"status": "OK", "message": f"Połączono z {ssid}"})
    else:
        return JSONResponse({"status": "ERROR", "message": str(result)})

@app.get("/status")
def status():
    return JSONResponse(get_wifi_status())
