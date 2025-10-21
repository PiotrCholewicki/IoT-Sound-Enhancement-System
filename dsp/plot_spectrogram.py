from matplotlib import pyplot as plt
import numpy as np
import os

def plot_spectrogram(xf, yf, yf_clean, diff, save_path=None):
    # Ustal ścieżkę do folderu dsp/audio_files (niezależnie od miejsca uruchomienia)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    audio_dir = os.path.join(base_dir, "audio_files")
    os.makedirs(audio_dir, exist_ok=True)

    if save_path is None:
        save_path = os.path.join(audio_dir, "spectrum_plot.png")

    plt.figure(figsize=(12, 8))

    # 1. Oryginalny sygnał
    xf_y = np.linspace(0, len(xf), len(yf)//2)
    plt.subplot(3, 1, 1)
    plt.plot(xf_y, 2.0 / len(yf) * np.abs(yf[:len(yf)//2]))
    plt.title("Oryginalny sygnał")
    plt.xlabel("Częstotliwość [Hz]")
    plt.ylabel("Amplituda")

    # 2. Po filtracji
    xf_clean = np.linspace(0, len(xf), len(yf_clean)//2)
    plt.subplot(3, 1, 2)
    plt.plot(xf_clean, 2.0 / len(yf_clean) * np.abs(yf_clean[:len(yf_clean)//2]))
    plt.title("Po odfiltrowaniu szumu")
    plt.xlabel("Częstotliwość [Hz]")
    plt.ylabel("Amplituda")

    # 3. Różnica (poziom szumu)
    plt.subplot(3, 1, 3)
    plt.plot(xf[:len(diff)], diff)
    plt.title("Różnica (poziom szumu w paśmie)")
    plt.xlabel("Częstotliwość [Hz]")
    plt.ylabel("Amplituda")

    plt.tight_layout()
    plt.savefig(save_path)
    print(f" Wykres zapisany: {save_path}")

    # 💡 Pokaż wykres w trakcie działania
    plt.show()
    plt.close()
