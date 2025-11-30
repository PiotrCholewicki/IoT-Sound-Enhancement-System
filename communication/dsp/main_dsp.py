from .record_audio import record_audio
from .analyze_noise import analyze_noise
from .audio_compensation import audio_compensation
from .plot_spectrogram import plot_spectrogram


def dsp(record_seconds=5, music_path="odebrany_plik.mp3"):
    """
    Pipeline:
    1. Nagrywa szum otoczenia
    2. Analizuje pasma szumu
    3. Wzmacnia zewnętrzny plik muzyczny na podstawie szumu
    """
    noise_file = record_audio(record_seconds)

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


