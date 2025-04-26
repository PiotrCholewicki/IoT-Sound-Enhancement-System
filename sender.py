import socket
import threading
import os
import match

NAZWA_PLIKU = "gorila.mp3"
PORT_BROADCAST = 8888

# Tworzymy socket UDP do nasłuchiwania broadcastu
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', PORT_BROADCAST))

print("🔎 Nasłuchiwanie na broadcast...")

# Odbierz dane od serwera (nazwa i port TCP)
data, addr = sock.recvfrom(1024)
sock.close()

nazwa_serwera, port_tcp = data.decode().split('|')
port_tcp = int(port_tcp)
adres_serwera = addr[0]
connectionState = False

print(f"\n🛰️  Wykryto serwer: {nazwa_serwera} na {adres_serwera}:{port_tcp}")

# Zapytanie o połączenie
decyzja = input("❓ Czy chcesz połączyć się z tym serwerem? (t/n): ").strip().lower()
if decyzja != 't':
    print("❌ Anulowano.")
    exit()

# Połącz się z serwerem
try:
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.connect((adres_serwera, port_tcp))
    print("✅ Połączono z serwerem.")
    connectionState = True
except Exception as e:
    print(f"❌ Błąd połączenia: {e}")
    exit()

# Zapytanie o wysłanie pliku
if not os.path.exists(NAZWA_PLIKU):
    print(f"❌ Plik '{NAZWA_PLIKU}' nie istnieje!")
    tcp_sock.close()
    exit()

def wyslij_plik(sock, NAZWA_PLIKU):
    with open(NAZWA_PLIKU, 'rb') as f:
        dane = f.read()

    wiadomosc = b'F' + dane
    sock.sendall(len(wiadomosc).to_bytes(4, 'big'))
    sock.sendall(wiadomosc)
    print("✅ Plik został wysłany.")
    
def wyslij_komende(sock, komenda):
    wiadomosc = b'C' + komenda.encode()
    sock.sendall(len(wiadomosc).to_bytes(4, 'big'))
    sock.sendall(wiadomosc)
    print(f"✅ Komenda '{komenda}' została wysłana.")

while True:    
    opcje = input("📁 Wpisz 'p' aby wysłać plik, 'k' aby wysłać komendę: ").strip().lower()

    if opcje == 'p':
        wyslij_plik(tcp_sock, NAZWA_PLIKU)
    elif opcje == 'k':
        komenda = input("💬 Wpisz komendę do wysłania: ")
        wyslij_komende(tcp_sock, komenda)
    else:
        print("❌ Nieznana opcja.")
    tcp_sock.close()
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.connect((adres_serwera, port_tcp))


