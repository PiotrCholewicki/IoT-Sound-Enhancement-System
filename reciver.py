import socket
import threading
import time
import vlc

NAZWA_SERWERA = "SerwerPliku9999"
PORT_TCP = 9999
PORT_BROADCAST = 8888

player = None
isPlaying = False

# --- Funkcja obsługi klienta TCP ---
def obsluz_klienta(conn, addr):
    global player
    global isPlaying
    print(f"📥 Połączenie z {addr}")

    try:
        total_length = int.from_bytes(odbierz_pelne(conn, 4), 'big')
        msg_type = odbierz_pelne(conn, 1)
        payload = odbierz_pelne(conn, total_length - 1)

        if msg_type == b'F':
            if isPlaying:
                player.stop()
            with open("odebrany_plik.mp3", 'wb') as f:
                f.write(payload)
            print(f"✅ Odebrano plik ({len(payload)} bajtów) i zapisano jako 'odebrany_plik.mp3'")
            player = vlc.MediaPlayer("odebrany_plik.mp3")
            player.play()
            isPlaying = True
            time.sleep(1)
        elif msg_type == b'C':
            komenda = payload.decode()
            
            cmd = komenda.strip().lower()

            if cmd == "p":
                player.pause()
                print("⏸️ Pauza")

            elif cmd == "r":
                player.play()
                print("▶️ Wznowiono")

            elif cmd.startswith("f "):  # forward
                try:
                    seconds = int(cmd.split()[1])
                    player.set_time(player.get_time() + seconds * 1000)
                    print(f"⏩ Do przodu o {seconds} sekund")
                except:
                    print("Błąd: użyj 'f 10'")

            elif cmd.startswith("b "):  # backward
                try:
                    seconds = int(cmd.split()[1])
                    player.set_time(max(0, player.get_time() - seconds * 1000))
                    print(f"⏪ Do tyłu o {seconds} sekund")
                except:
                    print("Błąd: użyj 'b 10'")

            elif cmd == "q":
                player.stop()
                print("🛑 Zatrzymano")
    except Exception as e:
        print(f"❌ Błąd podczas odbioru: {e}")
    finally:
        conn.close()

    
def odbierz_pelne(conn, n):
    dane = b''
    while len(dane) < n:
        pakiet = conn.recv(n - len(dane))
        if not pakiet:
            break
        dane += pakiet
    return dane

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
