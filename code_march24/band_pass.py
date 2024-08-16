import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, spectrogram
from scipy.io import wavfile
from scipy.signal import welch, find_peaks

def apply_bandpass_filter(data, frequency, f_window, fs, order):
    """
    Designs a Butterworth band-pass filter.

    Parameters:
    - data= raw signal
    - frequency= singular peak frequency (hz) from psd
    - f_window: how wide (in hertz) to create band filter
    - fs: Sampling frequency (Hz)
    - order: Order of the filter

    Returns:
    - filtered raw signal with only frequencies that are within range
    """
    nyquist = 0.5 * fs
    low = (frequency - f_window) / nyquist
    high = (frequency + f_window) / nyquist
    b, a = butter(order, [low, high], btype='band')
    # Apply the filter using filtfilt to avoid phase distortion
    filtered_data = filtfilt(b, a, data)

    return filtered_data

path = '/Users/loickabaille/Desktop/20240412_164527_150.4290_48_36.wav'

# Read the WAV file
fs, signal = wavfile.read(path)

# Check if stereo and take one channel
if signal.ndim > 1:
    signal = signal[:, 0]

# Generate a spectrogram for the original signal
n_fft = int(3 * fs)  # window size of 3 seconds
hop_length = int(n_fft * 0.01)  # 99% overlap
frequencies, times, S_orig = spectrogram(signal, fs=fs, nperseg=n_fft, noverlap=hop_length)
S_orig_db = 10 * np.log10(S_orig)
times=np.arange(len(signal)) / fs
# Compute the Power Spectral Density
frequencies_psd, power_spectral_density = welch(signal, fs, nperseg=fs)

# Find the indices corresponding to frequencies between 0 and 00 Hz
indices = np.where((frequencies_psd >= 0) & (frequencies_psd <= 1900))

# Slice the frequencies and power spectral density arrays
frequencies_psd = frequencies_psd[indices]
power_spectral_density = power_spectral_density[indices]

# Find peaks in the PSD
peaks, _ = find_peaks(power_spectral_density, height=0.0000000001)

#input
freq_peak=frequencies[peaks][0]
f_window=100 #hz
order=5
#Run band pass filter on raw data
filtered_signal= apply_bandpass_filter(signal,freq_peak, f_window, fs, order) #==> new raw data!

#Next step: create template file with peak frequency
#Next step: apply 6 peak match filter
#Next step: do peak analysis (w/ percentiles and such) ==> display plot
#Next step: get score






#
# # Plotting the signal and its PSD with peaks
# plt.figure(figsize=(12, 6))
#
# plt.subplot(2, 1, 1)
# plt.plot(times, signal)
# plt.title('Time Domain Signal')
# plt.xlabel('Time [seconds]')
# plt.ylabel('Amplitude')
#
# plt.subplot(2, 1, 2)
# plt.plot(frequencies_psd, power_spectral_density)
# plt.plot(frequencies_psd[peaks], power_spectral_density[peaks], 'x')
# plt.title('Power Spectral Density')
# plt.xlabel('Frequency [Hz]')
# plt.ylabel('Power')
#
# plt.tight_layout()
# plt.show()
