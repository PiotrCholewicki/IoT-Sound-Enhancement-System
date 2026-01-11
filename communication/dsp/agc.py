import numpy as np
import soundfile as sf

# -----------------------------
# Parametry systemu
# -----------------------------
MAX_GAIN_DB = 4.0        # maksymalny wzrost w dB
MIN_DELTA_DB = 5.0       # minimalna różni`ca` do reakcji
FULL_NOISE_DB = 30.0   # szum typu odkurzacz


def adaptive_gain_control(music_file, noise_rms_db, rms_ref_db, output_file):
    """
    AGC działający względem RMS szumu:
    - gain jest obliczany na podstawie różnicy RMS szumu do referencji
    - limiter działa tylko gdy próbki przekraczają TARGET_PEAK
    """

    # 1️⃣ Wczytanie muzyki
    y, sr = sf.read(music_file)
    if y.ndim > 1:
        y = np.mean(y, axis=1)  # konwersja do mono

    # 2️⃣ Obliczenie RMS muzyki
    rms_music = 20 * np.log10(np.sqrt(np.mean(y**2)) + 1e-12)
    peak_before = np.max(np.abs(y))

    # 3️⃣ Różnica RMS szumu
    delta_db = noise_rms_db - rms_ref_db
    
    if delta_db < MIN_DELTA_DB:
        gain_db = 0.0
        print(f"[AGC] Szum niski ({delta_db:.1f} dB) → brak wzmocnienia")
    else:

        # nieliniowa krzywa (łagodna)
        x = np.clip(delta_db / FULL_NOISE_DB, 0.0, 1.0)
        gain_db = MAX_GAIN_DB * np.log10(1 + 9 * x)

        print(
            f"[AGC] Szum: {noise_rms_db:.1f} dB | "
            f"Δ={delta_db:.1f} dB | "
            f"gain: +{gain_db:.2f} dB | "
            f"x={x:.2f}%"
        )

    # 4️⃣ Przeliczenie gain na wartość liniową
    gain_lin = 10 ** (gain_db / 20)
    y = y * gain_lin


    # 6️⃣ Zapis pliku
    sf.write(output_file, y, sr)
    print(f"[AGC] Zapisano wynik: {output_file}")
    peak_final = np.max(np.abs(y))
    print(f"[AGC] Peak przed korekcją: {peak_before:.3f}")
    print(f"[AGC] Peak po korekcji:    {peak_final:.3f}\n")

    return output_file
