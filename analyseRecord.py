import numpy as np
import librosa 
import matplotlib.pyplot as plt
import soundfile as sf
import scipy.fftpack as fft
import subprocess
from scipy.signal import medfilt
from group_frequencies import group_frequencies


y, sr = librosa.load('output.mp3', sr=None) #loading file

S_full, phase = librosa.magphase(librosa.stft(y)) #calculating the short time fourier transform of the signal

noise_power = np.mean(S_full[:, :int(sr*0.5)], axis=1) #calculating the noise power from first 0.5 seconds of the signal

mask = S_full > noise_power[:, None] #creating a mask to filter out the noise. The mask is a boolean array that is True where the signal is greater than the noise power

mask = mask.astype(float) #converting the mask to float

mask = medfilt(mask, kernel_size=(1, 5)) #applying median filter to the mask to remove small noise spikes. It smooths the mask by replacing each value with the median of its neighbors in the kernel size of (1, 5). This helps to remove small noise spikes and smooth out the mask.

S_clean = S_full * mask #applying the mask to the signal to filter out the noise. The clean signal is obtained by multiplying the original signal with the mask. This removes the noise from the signal.

y_clean = librosa.istft(S_clean * phase) #calculating the inverse short time fourier transform to get the clean signal back in time domain

sf.write('filtered.mp3', y_clean, sr) #saving the clean signal to a file

# Plotting the original and clean signals
n = len(y) 
yf = fft.fft(y) 
yf_clean = fft.fft(y_clean) 
xf = np.linspace(0, sr / 2, n // 2)

difference = np.abs(yf[:n // 2]) - np.abs(yf_clean[:n // 2]) #calculating the difference between the original and clean signals in frequency domain

threshold = np.max(difference) * 0.5
high_noise_indices = np.where(difference > threshold)[0]
high_noise_freqs = xf[high_noise_indices]

bands = group_frequencies(high_noise_freqs, gap=50)  # set gap = 50 Hz


#PRINTING THE BANDS

print("Bands to be enhanced:")
for band in bands:
    print(f"{band[0]:.1f} Hz to {band[1]:.1f} Hz")
plt.figure(figsize=(12, 9))

plt.subplot(3, 1, 1)
plt.plot(xf, 2.0 / n * np.abs(yf[:n // 2]))
plt.title('Original Signal')

plt.xlabel('Frequency (Hz)')
plt.ylabel('Amplitude')
plt.grid()

plt.subplot(3, 1, 2)
plt.plot(xf, 2.0 / n * np.abs(yf_clean[:n // 2]))
plt.title('Cleaned Signal')

plt.xlabel('Frequency (Hz)')
plt.ylabel('Amplitude')
plt.grid()

plt.subplot(3, 1, 3)
plt.plot(xf, difference)
plt.title('Difference (Noise Removed)')

plt.xlabel('Frequency (Hz)')
plt.ylabel('Amplitude')
plt.grid()

plt.tight_layout()
plt.show()