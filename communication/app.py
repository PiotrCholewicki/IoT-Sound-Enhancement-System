from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import subprocess
import shlex
import time
import re
import os

print("start")

app = FastAPI()
templates = Jinja2Templates(directory="communication/templates")

#Funkcja skanująca sieci przez wlan1, aż znajdzie jakieś sieci
def scan_networks():
    try:
        networks = []
        while not networks:  # dopóki lista jest pusta
            cmd = shlex.split("sudo iwlist wlan1 scan")
            result = subprocess.run(cmd, capture_output=True, text=True)
            output = result.stdout

            networks = re.findall(r'ESSID:"(.*?)"', output)
            networks = [n for n in networks if n]  # usuń puste ESSID

            if not networks:
                print("Nie znaleziono sieci, ponowne skanowanie za 2 sekundy...")
                time.sleep(2)  # poczekaj chwilę przed kolejnym skanowaniem

        return sorted(list(set(networks)))
    except Exception as e:
        return [f"Błąd: {e}"]


#SSID
CONNECTION_NAME = "Raspi_WPA_Profile" 

def get_nm_logs(ifname: str) -> str:
    """Pobiera ostatnie logi NetworkManager dotyczące danego interfejsu."""
    try:
        #Dostęp do dziennika systemowego
        log_command = [
            "sudo", "journalctl", 
            "-u", "NetworkManager", 
            "--since", "1 minute ago", 
            "--no-pager"
        ]
        result = subprocess.run(log_command, capture_output=True, text=True, check=False)
        
        # Logi interfejsu i błędy
        filtered_logs = [
            line.strip() 
            for line in result.stdout.splitlines() 
            if ifname in line or "error" in line.lower() or "fail" in line.lower() or "4way" in line.lower()
        ]
        return "\n".join(filtered_logs)
    except Exception as e:
        return f"Nie udało się pobrać logów systemowych: {e}"


def connect_to_wifi(ssid: str, password: str, ifname: str = "wlan1") -> bool:
    print(f"Próba konfiguracji stabilnego połączenia WPA/WPA2-PSK dla SSID: {ssid}")
    
    # Krok 0: Usunięcie starego profilu, aby zapewnić czystą konfigurację
    try:
        # Usuń, aby wymusić czysty start
        subprocess.run(["sudo", "nmcli", "connection", "delete", CONNECTION_NAME], 
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        print(f"-> Usunięto stary profil: {CONNECTION_NAME} (jeśli istniał).")
    except Exception:
        pass

    # Lista argumentów dla tworzenia nowego połączenia (nmcli connection add)
    command_add = [ 
        "nmcli", 
        "device",
        "wifi",
        "connect", 
        ssid,                      # Rzeczywista nazwa sieci               
        "password", 
        password,                  # Jawne zapisanie hasła                  
    ]

    try:
        # Krok 1: Dodanie/Modyfikacja profilu połączenia
        print("-> 1. Tworzenie profilu WPA/WPA2-PSK (bez WPA3)...")
        subprocess.run(command_add, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"-> Profil '{CONNECTION_NAME}' utworzony pomyślnie.")
        
        # Krok 2: Aktywacja profilu
        command_up = [
            "sudo",
            "nmcli",
            "connection",
            "up",
            CONNECTION_NAME,
            "ifname",
            ifname,
            "--ask"
        ]
        
        print("-> 2. Aktywacja połączenia...")
        subprocess.run(command_up, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Oczekiwanie i weryfikacja
        time.sleep(12) 
        
        # Krok 3: Weryfikacja adresu IP
        ip_check = subprocess.run(["ip", "a", "show", ifname], capture_output=True, text=True, check=False)
        if "inet " in ip_check.stdout:
            print("SUKCES: Połączenie aktywne i interfejs ma adres IP.")
            return True
        else:
            print("BŁĄD: Połączenie się nie powiodło (Brak adresu IP po 12s).")
            print("   --- LOGI NETWORKMANAGER (OSTATNIA MINUTA) ---")
            print(get_nm_logs(ifname))
            print("   ---------------------------------------------")
            return False

    except subprocess.CalledProcessError as e:
        print(f"BŁĄD NMCLI. Polecenie '{' '.join(e.cmd)}' nie powiodło się.")
        print(f"   STDERR: {e.stderr.decode().strip()}")
        print("   --- LOGI NETWORKMANAGER (OSTATNIA MINUTA) ---")
        print(get_nm_logs(ifname))
        print("   ---------------------------------------------")
        return False
    except Exception as e:
        print(f"Nieoczekiwany błąd: {e}")
        return False

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
    print("Nerworks: " , networks)
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
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("communication.app:app", host="0.0.0.0", port=8002)

