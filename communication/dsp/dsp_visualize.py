import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np

def plot_audio_comparison(original_file, processed_file, output_png="dsp_comparison.png"):
    y1, sr1 = librosa.load(original_file, sr=None, mono=True)
    y2, sr2 = librosa.load(processed_file, sr=None, mono=True)

    if sr1 != sr2:
        print("[WARN] Sampling rates differ!")

    # wyrównanie długości
    min_len = min(len(y1), len(y2))
    y1 = y1[:min_len]
    y2 = y2[:min_len]

    t = np.arange(min_len) / sr1
    diff = y2 - y1   # ⭐ różnica sygnałów

    plt.figure(figsize=(15,9))

    # 1️⃣ oryginał
    plt.subplot(3,1,1)
    plt.title("Oryginalny plik audio")
    plt.plot(t, y1)
    plt.ylabel("Amplituda")

    # 2️⃣ po DSP
    plt.subplot(3,1,2)
    plt.title("Plik po DSP / AGC")
    plt.plot(t, y2)
    plt.ylabel("Amplituda")

    # 3️⃣ różnica
    plt.subplot(3,1,3)
    plt.title("Różnica sygnałów (DSP − oryginał)")
    plt.plot(t, diff)
    plt.xlabel("Czas [s]")
    plt.ylabel("Δ Amplituda")

    plt.tight_layout()
    plt.savefig(output_png)
    print(f"[VIS] Wykres zapisany w: {output_png}")
    plt.close()
