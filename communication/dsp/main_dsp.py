from .record_audio import record_audio
from .analyze_noise import analyze_noise
from .audio_compensation import audio_compensation
from .plot_spectrogram import plot_spectrogram
from pathlib import Path

def dsp(record_seconds=5, music_path="odebrany_plik.mp3"):
    """
    Pipeline:
    1. Nagrywa szum otoczenia
    2. Analizuje pasma szumu
    3. Wzmacnia zewnętrzny plik muzyczny na podstawie szumu
    """
    BASE_DSP_DIR = Path(__file__).parent
    noise_file = str(BASE_DSP_DIR / "audio_files" / "output.mp3")

    #noise_file = "./dsp/audio_files/output.mp3"
    print("Analiza szumu...")
    band_info, sr, xf, yf, yf_clean, diff, y, y_clean = analyze_noise(noise_file)

    print("Wzmacnianie zewnętrznego pliku muzycznego na podstawie szumu...")
    output_file = audio_compensation(music_path, band_info)

    print("Rysowanie spektrogramu szumu...")
    plot_spectrogram(y, y_clean, sr)

    print(f"Gotowe! Nowy plik zapisany: {output_file}")
    return output_file, band_info

if __name__ == "__main__":
    print("Uruchamiam DSP...")
    output, bands = dsp()
    print("Zakończono DSP.")


