import numpy as np
import librosa
import os

def calibrate_microphone(record_seconds=3, output_file="communication/dsp/audio_files/mic_calibration.txt"):

    from .record_audio import record_audio
    
    print("Kalibracja mikrofonu – nagrywam ciszę...")
    noise_file = record_audio(record_seconds)
    y, sr = librosa.load(noise_file, sr=None, mono=True)
    
    rms_db = 20 * np.log10(np.sqrt(np.mean(y**2)) + 1e-12)
    print(f"RMS mikrofonu w ciszy: {rms_db:.2f} dB")
    
    with open(output_file, "w") as f:
        f.write(str(rms_db))
    
    print(f"Kalibracja zapisana w: {output_file}")
    return rms_db

def get_mic_reference(calibration_file="communication/dsp/audio_files/mic_calibration.txt"):

    if os.path.exists(calibration_file):
        with open(calibration_file, "r") as f:
            rms = float(f.read())
            print(f"[DSP] RMS mikrofonu z kalibracji: {rms:.2f} dB")
            return rms
    else:
        print("[DSP] Brak pliku kalibracji – wykonuję nagranie ciszy...")
        rms = calibrate_microphone()
        return rms
    
