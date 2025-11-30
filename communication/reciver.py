from fastapi import FastAPI, UploadFile, File, Form, Body
from fastapi.responses import JSONResponse
import vlc
import threading
import uvicorn
import os
import sys
from dsp.main_dsp import dsp 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DSP_DIR = os.path.join(BASE_DIR, "dsp")
AUDIO_DIR = os.path.join(DSP_DIR, "audio_files")
os.makedirs(AUDIO_DIR, exist_ok=True)

app = FastAPI(title="Audio Receiver API")

player = None
isPlaying = False
player_lock = threading.Lock()
received_file = os.path.join(AUDIO_DIR, "song_compensated.mp3")

player = vlc.MediaPlayer(received_file)
isPlaying = False

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    global player, isPlaying

    with player_lock:
        if isPlaying and player is not None:
            player.stop()

        # Zapisz plik na dysk
        with open(received_file, "wb") as f:
            f.write(await file.read())

        #start processing the file - do sprawdzenia czy na linuxie dziala bez tego importa
        dsp(record_seconds=5, music_path=received_file)

        #play processed file
        player = vlc.MediaPlayer(received_file)
        #player.play()
        #isPlaying = True

    return {"status": "ok", "message": f"Odebrano i odtwarzam {file.filename}"}


@app.post("/command")
async def command(cmd: str = Body(..., media_type="text/plain")):

    if player is None:
        return JSONResponse(status_code=400, content={"error": "Brak aktywnego odtwarzacza"})

    komenda = cmd.strip().lower()

    #komendy idą z androida jako małe litery
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
        else:
            return JSONResponse(status_code=400, content={"error": "Nieznana komenda"})


@app.get("/status")
async def status():
    global player, isPlaying
    if player is None:
        return {"playing": False}
    return {
        "playing": isPlaying,
        "position_ms": player.get_time(),
        "length_ms": player.get_length(),
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
