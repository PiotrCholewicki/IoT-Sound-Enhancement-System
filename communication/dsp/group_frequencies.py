import numpy as np

def group_frequencies(freqs, gap=80, min_bandwidth=100):
    """
    Grupuje częstotliwości w pasma, gdzie kolejne punkty są bliżej niż `gap` Hz.
    Wymusza też minimalną szerokość pasma `min_bandwidth`.
    """
    if len(freqs) == 0:
        return []

    freqs = np.sort(freqs)
    bands = []
    start = freqs[0]
    prev = freqs[0]

    for f in freqs[1:]:
        # jeśli przerwa większa niż 'gap' -> kończymy bieżące pasmo
        if f - prev > gap:
            # wymuszamy minimalną szerokość
            if prev - start < min_bandwidth:
                prev = start + min_bandwidth
            bands.append((start, prev))
            start = f
        prev = f

    # dodaj ostatnie pasmo
    if prev - start < min_bandwidth:
        prev = start + min_bandwidth
    bands.append((start, prev))

    # Usuwamy duplikaty i sortujemy
    bands = sorted(set(bands))
    return bands
