import pyaudio
import wave
import subprocess
import os
        
FRAMES_PER_BUFFER = 3200
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
def record_audio(seconds):

    p = pyaudio.PyAudio()
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        input_device_index=1,  
        frames_per_buffer=FRAMES_PER_BUFFER
    )

    print("Start...")
    frames = []

    for _ in range(0, int(RATE / FRAMES_PER_BUFFER * seconds)):
        data = stream.read(FRAMES_PER_BUFFER)
        frames.append(data)

    stream.stop_stream()  
    stream.close()
    p.terminate()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    audio_dir = os.path.join(base_dir, "audio_files")
    wav_path = os.path.join(audio_dir, "temp.wav")
    mp3_path = os.path.join(audio_dir, "output.mp3")


    with wave.open(wav_path, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    subprocess.call(["ffmpeg", "-y", "-i", wav_path, mp3_path],
                    stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    print(f" Zapisano nagranie: {mp3_path}")
    return mp3_path
