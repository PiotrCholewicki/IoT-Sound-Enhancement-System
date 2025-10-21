import requests
import os

SERVER_URL = "http://127.0.0.1:8000"  # ← adres RPi/serwera
NAZWA_PLIKU = "gorila.mp3"

def wyslij_plik(nazwa_pliku):
    if not os.path.exists(nazwa_pliku):
        print(f"❌ Plik {nazwa_pliku} nie istnieje")
        return
    files = {"file": open(nazwa_pliku, "rb")}
    resp = requests.post(f"{SERVER_URL}/upload", files=files)
    print(resp.json())

def wyslij_komende(komenda):
    data = {"cmd": komenda}
    resp = requests.post(f"{SERVER_URL}/command", data=data)
    print(resp.json())

def pokaz_status():
    resp = requests.get(f"{SERVER_URL}/status")
    print(resp.json())

while True:
    opcja = input("📁 'p' - wyślij plik, 'k' - komenda, 's' - status, 'q' - zakończ: ").strip().lower()
    if opcja == 'p':
        wyslij_plik(NAZWA_PLIKU)
    elif opcja == 'k':
        komenda = input("💬 Podaj komendę (p, r, f 10, b 10, q): ")
        wyslij_komende(komenda)
    elif opcja == 's':
        pokaz_status()
    elif opcja == 'q':
        wyslij_komende("q")
        break
    else:
        print("❌ Nieznana opcja")
