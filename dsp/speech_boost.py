import numpy as np
from pydub import AudioSegment
import os

def speech_boost(input_file, band_info):
    """Wzmacnia pasma w zależności od wykrytego szumu"""
    audio = AudioSegment.from_file(input_file)
    
    # Ustal ścieżkę do folderu audio_files
    base_dir = os.path.dirname(os.path.abspath(__file__))
    audio_dir = os.path.join(base_dir, "audio_files")
    os.makedirs(audio_dir, exist_ok=True)
    
    output_file = os.path.join(audio_dir, "output_speech_boosted.mp3")
    result = audio

    print(" Wzmacnianie pasm w zależności od szumu:")
    for b in band_info:
        low, high = b["range"]
        intensity = b["intensity"]

        # Mapowanie intensywności szumu na dB (skalowanie logarytmiczne)
        boost_db = min(10, max(2, 10 * np.log10(intensity + 1e-6)))

        print(f"  • {low:.0f}–{high:.0f} Hz → +{boost_db:.1f} dB")

        filtered = audio.low_pass_filter(high).high_pass_filter(low)
        boosted = filtered + boost_db
        result = result.overlay(boosted - 3)

    result.export(output_file, format="mp3")
    print(f" Plik z korekcją zapisany: {output_file}")
    return output_file
