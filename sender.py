import socket
import os

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
except Exception as e:
    print(f"❌ Błąd połączenia: {e}")
    exit()

# Zapytanie o wysłanie pliku
if not os.path.exists(NAZWA_PLIKU):
    print(f"❌ Plik '{NAZWA_PLIKU}' nie istnieje!")
    tcp_sock.close()
    exit()

wyslac = input(f"📤 Czy chcesz wysłać plik '{NAZWA_PLIKU}'? (t/n): ").strip().lower()
if wyslac != 't':
    print("❌ Wysyłanie anulowane.")
    tcp_sock.close()
    exit()

# Wyślij plik: najpierw długość, potem zawartość
with open(NAZWA_PLIKU, 'rb') as f:
    zawartosc = f.read()
    tcp_sock.sendall(len(zawartosc).to_bytes(4, 'big'))
    tcp_sock.sendall(zawartosc)

print("✅ Plik został wysłany.")
tcp_sock.close()
