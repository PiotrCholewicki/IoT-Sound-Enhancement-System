import numpy as np
from pydub import AudioSegment
import os

def audio_compensation(input_file, band_info):
    """Wzmacnia pasma w zależności od wykrytego szumu"""
    audio = AudioSegment.from_file(input_file)
    
    # Ustal ścieżkę do folderu audio_files
    base_dir = os.path.dirname(os.path.abspath(__file__))
    audio_dir = os.path.join(base_dir, "audio_files")
    os.makedirs(audio_dir, exist_ok=True)
    
    output_file = os.path.join(audio_dir, "output_speech_boosted.mp3")
    result = audio

    total_intensity = np.mean([b["intensity"] for b in band_info]) if band_info else 0
    if total_intensity < 0.001:
        print("Cisza w otoczeniu – pomijam wzmocnienie.")
        return input_file
    
    print("Wzmacnianie pasm w zależności od szumu:")
    max_intensity = np.max([b["intensity"] for b in band_info]) + 1e-6

    for b in band_info:
        low, high = b["range"]

        intensity = b["intensity"]
        if intensity < 0.01:  # zbyt niski poziom szumu → pomiń
            continue


        # Mapowanie intensywności szumu na dB (skalowanie liniowe)
        boost_db = 2 + 8 * (intensity / max_intensity)
        boost_db = np.clip(boost_db, 0, 10)

        print(f"  • {low:.0f}–{high:.0f} Hz → +{boost_db:.1f} dB")

        try:
            filtered = audio.low_pass_filter(high).high_pass_filter(low)
            boosted = filtered + boost_db
            result = result.overlay(boosted - 3)
        except Exception as e:
            print(f"Pominięto pasmo {low}-{high} Hz z powodu błędu: {e}")

    result.export(output_file, format="mp3")
    print(f"Plik z korekcją zapisany: {output_file}")
    return output_file
