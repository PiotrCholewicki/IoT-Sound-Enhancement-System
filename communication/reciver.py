from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
import vlc
import threading
import uvicorn
import os
import asyncio
from typing import Optional
import traceback # Dodane dla lepszego debugowania
from pathlib import Path # Dodane do zarządzania ścieżkami
from fastapi import FastAPI, UploadFile, File, Form, Body
import sys
import subprocess
import re
import time
from .dsp.main_dsp import dsp 
from .dsp.calibrate_microphone import calibrate_microphone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DSP_DIR = os.path.join(BASE_DIR, "dsp")
AUDIO_DIR = os.path.join(DSP_DIR, "audio_files")
CALIBRATION_FILE = os.path.join(DSP_DIR, "mic_calibration.txt")
os.makedirs(AUDIO_DIR, exist_ok=True)

HOME_DIR = Path.home()
AUDIO_FILE_PATH = HOME_DIR / "temp_audio_receiver.mp3"

app = FastAPI(title="Audio Receiver API")

instance = vlc.Instance('--aout=pulse')  
player = instance.media_player_new()

is_playing: bool = False
player_lock = threading.Lock()
received_file = os.path.join(AUDIO_DIR, "song_adaptive.wav")

def initialize_vlc_player(filepath: str):
    """Stops the current player (if active) and starts a new one."""
    global player, is_playing, instance

    if player is not None:
        player.stop()
        player = None

    try:
        media = instance.media_new(str(filepath))
        player = instance.media_player_new()
        player.set_media(media)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="VLC Player initialization failed")

@app.post("/upload")
async def upload_audio(file: UploadFile = File(...)):
    """Receives an audio file, saves it, processes with DSP, and begins playback."""
    global player, is_playing

    try:
        file_content = await file.read()
        with open(AUDIO_FILE_PATH, "wb") as f:
            f.write(file_content)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error saving file: {e}")

    processed_file = os.path.join(AUDIO_DIR, "song_adaptive.wav")
    try:
        dsp(record_seconds=2, music_path=str(AUDIO_FILE_PATH))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"DSP processing failed: {e}")

    with player_lock:
        try:
            initialize_vlc_player(processed_file)
            player.play()
            is_playing = True
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"VLC playback error: {e}")

    return {"status": "success", "message": f"Received and playing: {file.filename}"}


@app.post("/command")
async def command(cmd: str = Body(..., media_type="text/plain")):

    if player is None:
        return JSONResponse(status_code=400, content={"error": "Brak aktywnego odtwarzacza"})

    komenda = cmd.strip().lower()

    with player_lock:
        if komenda == "p":
            player.pause()
            return {"status": "paused"}
        elif komenda == "r":
            player.play()
            return {"status": "resumed"}
        elif komenda.startswith("f "):
            try:
                sec = int(komenda.split()[1])
                player.set_time(player.get_time() + sec * 1000)
                return {"status": f"skipped forward {sec}s"}
            except:
                return JSONResponse(status_code=400, content={"error": "Niepoprawny format komendy f"})
        elif komenda.startswith("b "):
            try:
                sec = int(komenda.split()[1])
                player.set_time(max(0, player.get_time() - sec * 1000))
                return {"status": f"skipped backward {sec}s"}
            except:
                return JSONResponse(status_code=400, content={"error": "Niepoprawny format komendy b"})
        elif komenda == "q":
            player.stop()
            isPlaying = False
            return {"status": "stopped"}
        elif komenda =="c":
            
            print("[DSP] Żądanie kalibracji mikrofonu")

            if os.path.exists(CALIBRATION_FILE):
                os.remove(CALIBRATION_FILE)
                print("[DSP] Usunięto stary plik kalibracji")

            calibrate_microphone()

            return JSONResponse(
                content={"status": "ok", "message": "Kalibracja mikrofonu wykonana"}
            )

        else:
            return JSONResponse(status_code=400, content={"error": "Nieznana komenda"})


@app.get("/status")
async def get_status():
    """Returns the current playback status."""
    global player, is_playing
    
    if player is None:
        return {"is_active": False, "message": "No media loaded."}

    with player_lock:
        current_time_ms = player.get_time() if player else 0
        total_length_ms = player.get_length() if player else 0
        
        player_state = player.get_state()
        
        if player_state in (vlc.State.Stopped, vlc.State.Ended, vlc.State.Error):
             is_playing = False
        
        is_actually_playing = player_state == vlc.State.Playing

        return {
            "is_active": True,
            "is_playing": is_playing and is_actually_playing, 
            "vlc_state": str(player_state),
            "position_ms": current_time_ms,
            "length_ms": total_length_ms,
        }
    
def bt_scan_worker(scan_time: int = 10) -> dict:
    devices = {}
    stop_event = threading.Event()

    regex = re.compile(r"Device ([0-9A-F:]{17}) (.+)")

    def reader(proc):
        while not stop_event.is_set():
            line = proc.stdout.readline()
            if not line:
                break

            match = regex.search(line.strip())
            if match:
                mac, name = match.groups()
                if mac not in devices:
                    devices[mac] = name.strip()

    process = subprocess.Popen(
        ["bluetoothctl"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1
    )

    t = threading.Thread(target=reader, args=(process,), daemon=True)
    t.start()

    # inicjalizacja
    process.stdin.write("power on\n")
    process.stdin.write("agent on\n")
    process.stdin.write("default-agent\n")
    process.stdin.write("scan on\n")
    process.stdin.flush()

    time.sleep(scan_time)

    stop_event.set()
    process.stdin.write("scan off\n")
    process.stdin.write("quit\n")
    process.stdin.flush()

    process.terminate()
    t.join(timeout=1)

    return devices

def bt_connect_worker(mac: str, timeout: int = 15) -> bool:
    process = subprocess.Popen(
        ["bluetoothctl"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1
    )

    cmds = [
        "power on",
        "agent on",
        "default-agent",
        f"trust {mac}",
        f"pair {mac}",
        f"connect {mac}"
    ]

    for cmd in cmds:
        process.stdin.write(cmd + "\n")
        process.stdin.flush()
        time.sleep(1)

    start = time.time()
    connected = False

    while time.time() - start < timeout:
        line = process.stdout.readline()
        if not line:
            break

        line = line.lower()

        if "connection successful" in line or "connected" in line:
            connected = True
            break

        if "failed" in line or "error" in line:
            break

    process.stdin.write("quit\n")
    process.stdin.flush()
    process.terminate()

    return connected

@app.post("/bt/scan")
async def bt_scan_endpoint():
    devices = await asyncio.to_thread(bt_scan_worker, scan_time=10)
    return {
        "count": len(devices),
        "devices": devices
    }

@app.post("/bt/connect")
async def bt_connect(mac: str = Body(..., embed=True)):
    success = bt_connect_worker(mac)

    if success:
        return {"status": "connected", "mac": mac}

    raise HTTPException(status_code=500, detail="Nie udało się połączyć z urządzeniem")

@app.on_event("shutdown")
def shutdown_event():
    global player
    print("Shutting down player and cleaning up...")
    if player is not None:
        player.stop()
        player = None

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
