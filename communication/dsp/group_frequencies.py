import numpy as np

def group_frequencies(freqs, gap=80, min_bandwidth=100):

    if len(freqs) == 0:
        return []

    freqs = np.sort(freqs)
    bands = []
    start = freqs[0]
    prev = freqs[0]

    for f in freqs[1:]:
        if f - prev > gap:
            if prev - start < min_bandwidth:
                prev = start + min_bandwidth
            bands.append((start, prev))
            start = f
        prev = f

    if prev - start < min_bandwidth:
        prev = start + min_bandwidth
    bands.append((start, prev))

    bands = sorted(set(bands))
    return bands
