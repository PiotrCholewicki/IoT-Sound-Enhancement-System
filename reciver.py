import socket
import threading
import time

NAZWA_SERWERA = "SerwerPliku9999"
PORT_TCP = 9999
PORT_BROADCAST = 8888

# --- Funkcja obsługi klienta TCP ---
def obsluz_klienta(conn, addr):
    print(f"📥 Połączenie z {addr}")
    try:
        size = int.from_bytes(conn.recv(4), 'big')
        data = conn.recv(size)
        with open("odebrany_plik.mp3", 'wb') as f:
            f.write(data)
        print(f"✅ Odebrano plik od {addr} ({len(data)} bajtów)")
    except Exception as e:
        print(f"❌ Błąd odbioru pliku: {e}")
    conn.close()

# --- Wątek: serwer TCP ---
def uruchom_tcp_server():
    tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_server.bind(('', PORT_TCP))
    tcp_server.listen()
    print("🧲 Serwer TCP nasłuchuje...")

    while True:
        conn, addr = tcp_server.accept()
        threading.Thread(target=obsluz_klienta, args=(conn, addr)).start()

# --- Wątek: broadcast co 5 sekund ---
def wysylaj_broadcast():
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    while True:
        wiadomosc = f"{NAZWA_SERWERA}|{PORT_TCP}"
        udp_sock.sendto(wiadomosc.encode(), ('192.168.100.255', PORT_BROADCAST))
        print("📡 Wysłano broadcast...")
        time.sleep(5)

# --- Start ---
if __name__ == "__main__":
    threading.Thread(target=uruchom_tcp_server, daemon=True).start()
    wysylaj_broadcast()
