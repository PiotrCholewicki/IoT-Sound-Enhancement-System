#testcommit
import pyaudio
import wave
import io
import subprocess

FRAMES_PER_BUFFER = 3200
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 41000

p = pyaudio.PyAudio()
stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=FRAMES_PER_BUFFER
)

print("Start...")

seconds = 5
frames = []

for _ in range(0, int(RATE / FRAMES_PER_BUFFER * seconds)):
    data = stream.read(FRAMES_PER_BUFFER)
    frames.append(data)

stream.stop_stream()  # Poprawka
stream.close()
p.terminate()

# Zapis tymczasowego pliku WAV w pamięci
buffer = io.BytesIO()
wf = wave.open(buffer, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()

buffer.seek(0)  # Przesuń wskaźnik na początek bufora

# Zapisz jako tymczasowy plik WAV
filename_wav = "output.wav"
wf = wave.open(filename_wav, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()

# Użyj ffmpeg do konwersji WAV -> MP3
subprocess.call(["ffmpeg", "-i", filename_wav, "output.mp3"])