from .record_audio import record_audio
from .agc import adaptive_gain_control
from .calibrate_microphone import calibrate_microphone, get_mic_reference
import librosa
import numpy as np
import os

def dsp(record_seconds=2, music_path="odebrany_plik.mp3"):
    # 1️⃣ Kalibracja mikrofonu (tylko raz w aplikacji)
    rms_ref_db = get_mic_reference()
    if rms_ref_db is None:
        print("[DSP] Brak kalibracji – wykonuję nagranie ciszy...")
        rms_ref_db = calibrate_microphone(record_seconds=2)
    # 2️⃣ Przed odtworzeniem muzyki nagrywamy 0.5–1 s szumu
    noise_file = record_audio(2.0)  # Twój moduł
    y_noise, sr = librosa.load(noise_file, sr=None, mono=True)
    noise_rms = 20 * np.log10(np.sqrt(np.mean(y_noise**2)) + 1e-12)  # RMS w dBFS

    # 3️⃣ Adaptive gain
    music_file = "odebrany_plik.mp3"
    base_dir = os.path.dirname(os.path.abspath(__file__))
    audio_dir = os.path.join(base_dir, "audio_files")
    output_file = os.path.join(audio_dir, "song_adaptive.wav")

    adaptive_gain_control(music_file, noise_rms, rms_ref_db, output_file)



if __name__ == "__main__":
    print("Uruchamiam DSP...")
    output, bands = dsp()
    print("Zakończono DSP.")


