from record_audio import record_audio
from analyze_noise import analyze_noise
from speech_boost import speech_boost
from plot_spectrogram import plot_spectrogram

def process_audio_with_dynamic_compensation(record_seconds=5):
    """Pełny pipeline: nagranie → analiza → dynamiczna korekcja → zapis"""
    input_file = record_audio(record_seconds)
    band_info, sr, xf, yf, yf_clean, diff = analyze_noise(input_file)
    output_file = speech_boost(input_file, band_info)
    plot_spectrogram(xf, yf, yf_clean, diff)
    print(" Przetwarzanie zakończone.")
    return output_file, band_info

if __name__ == "__main__":
    process_audio_with_dynamic_compensation(record_seconds=5)