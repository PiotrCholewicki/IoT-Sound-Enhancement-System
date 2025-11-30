import numpy as np
import librosa
import soundfile as sf
from scipy.signal import medfilt
from .group_frequencies import group_frequencies
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "audio_files")
def analyze_noise(file_path):
    """Analizuje plik audio, wykrywa pasma z szumem i zwraca ich intensywność"""
    y, sr = librosa.load(file_path, sr=None)
    S_full, phase = librosa.magphase(librosa.stft(y))
    noise_power = np.mean(S_full[:, :int(sr * 0.5)], axis=1)
    mask = S_full > noise_power[:, None]
    mask = medfilt(mask.astype(float), kernel_size=(1, 5))
    S_clean = S_full * mask
    y_clean = librosa.istft(S_clean * phase)
    #sf.write(os.path.join(AUDIO_DIR, "filtered.wav"), y_clean, sr)

    n = len(y)
    yf = np.fft.fft(y)
    yf_clean = np.fft.fft(y_clean)
    xf = np.linspace(0, sr / 2, n // 2)
    diff = np.abs(yf[:n // 2]) - np.abs(yf_clean[:n // 2])
    diff = np.clip(diff, 0, None)

    # Wyznacz progi i pasma
    threshold = np.max(diff) * 0.5
    high_noise_indices = np.where(diff > threshold)[0]
    high_noise_freqs = xf[high_noise_indices]
    bands = group_frequencies(high_noise_freqs, gap=50)

    # Oblicz względny poziom szumu w pasmach
    band_info = []
    for b in bands:
        idx = np.logical_and(xf >= b[0], xf <= b[1])
        intensity = np.mean(diff[idx])
        band_info.append({"range": b, "intensity": intensity})

    return band_info, sr, xf, yf, yf_clean, diff, y, y_clean