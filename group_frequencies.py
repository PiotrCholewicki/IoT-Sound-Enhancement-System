import numpy as np
def group_frequencies(freqs, gap=50):
    """
    Group frequencies into bands where consecutive frequencies differ by less than 'gap' Hz.
    """
    if len(freqs) == 0:
        return []

    freqs = np.sort(freqs)  # sort frequencies in ascending order
    bands = []
    start = freqs[0]
    prev = freqs[0]

    for f in freqs[1:]:
        if f - prev > gap:
            bands.append((start, prev))
            start = f
        prev = f

    bands.append((start, prev))  # add the last band
    return bands