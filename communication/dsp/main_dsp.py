from .record_audio import record_audio
from .agc import adaptive_gain_control
from .calibrate_microphone import calibrate_microphone, get_mic_reference
from .dsp_visualize import plot_audio_comparison
import librosa
import numpy as np
import os

def dsp(record_seconds=3, music_path="odebrany_plik.mp3"):
    rms_ref_db = get_mic_reference()
    if rms_ref_db is None:
        print("[DSP] Brak kalibracji - wykonuję nagranie ciszy...")
        rms_ref_db = calibrate_microphone(record_seconds=3)


    base_dir = os.path.dirname(os.path.abspath(__file__))
    audio_dir = os.path.join(base_dir, "audio_files")
    output_file = os.path.join(audio_dir, "song_adaptive.wav")

    noise_file = record_audio(2.0)# nagranie szumu
    y_noise, sr = librosa.load(noise_file, sr=None, mono=True)
    noise_rms = 20 * np.log10(np.sqrt(np.mean(y_noise**2)) + 1e-12)

    adaptive_gain_control(music_path, noise_rms, rms_ref_db, output_file)

    #plot_audio_comparison(music_path, output_file)

    return output_file 

if __name__ == "__main__":
    print("Uruchamiam DSP...")
    output, bands = dsp()
    print("Zakończono DSP.")


