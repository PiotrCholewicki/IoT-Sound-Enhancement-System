import os
import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display

def plot_spectrogram(y, y_clean, sr, save_path=None):
    """Wyświetla i zapisuje spektrogram szumu (oryginał, po filtrze, różnica)"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    audio_dir = os.path.join(base_dir, "audio_files")
    os.makedirs(audio_dir, exist_ok=True)

    if save_path is None:
        save_path = os.path.join(audio_dir, "noise_spectrum.png")

    S_orig = np.abs(librosa.stft(y))
    S_clean = np.abs(librosa.stft(y_clean))
    S_diff = np.clip(S_orig - S_clean, 0, None)

    plt.figure(figsize=(12, 10))

    plt.subplot(3, 1, 1)
    librosa.display.specshow(librosa.amplitude_to_db(S_orig, ref=np.max), sr=sr,
                             x_axis="time", y_axis="log", cmap="magma")
    plt.title("Oryginalny szum")
    plt.colorbar(format="%+2.0f dB")

    plt.subplot(3, 1, 2)
    librosa.display.specshow(librosa.amplitude_to_db(S_clean, ref=np.max), sr=sr,
                             x_axis="time", y_axis="log", cmap="magma")
    plt.title("Po odfiltrowaniu szumu")
    plt.colorbar(format="%+2.0f dB")

    plt.subplot(3, 1, 3)
    librosa.display.specshow(librosa.amplitude_to_db(S_diff, ref=np.max), sr=sr,
                             x_axis="time", y_axis="log", cmap="coolwarm")
    plt.title("Różnica – usunięty szum")
    plt.colorbar(format="%+2.0f dB")

    plt.tight_layout()
    plt.savefig(save_path)
    plt.show()
    plt.close()
    print(f"Spektrogram zapisany: {save_path}")
