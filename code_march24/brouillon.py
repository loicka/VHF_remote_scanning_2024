import matplotlib.pyplot as plt
import numpy as np
from scipy.io import wavfile
import scipy.signal as signal
import noisereduce as nr

def plot_wav_spectrogram_psd(filename):
    # Read the WAV file
    framerate, signal_data = wavfile.read(filename)

    # Check if stereo and take one channel
    if signal_data.ndim > 1:
        signal_data = signal_data[:, 0]

    # Apply noise reduction
    reduced_signal = nr.reduce_noise(y=signal_data, sr=framerate)

    # Calculate time vector for waveforms
    time = np.linspace(0, len(signal_data) / framerate, num=len(signal_data))

    # Set parameters for the spectrogram
    n_fft = int(3 * framerate)  # window size of 3 seconds
    hop_length = int(n_fft * 0.01)  # 99% overlap

    # Generate a spectrogram for the original signal
    freqs_orig, times_orig, S_orig = signal.spectrogram(signal_data, fs=framerate, nperseg=n_fft, noverlap=hop_length)
    S_orig_db = 10 * np.log10(S_orig)

    # Generate a spectrogram for the noise-reduced signal
    freqs_reduced, times_reduced, S_reduced = signal.spectrogram(reduced_signal, fs=framerate, nperseg=n_fft, noverlap=hop_length)
    S_reduced_db = 10 * np.log10(S_reduced)

    # Create a figure with six subplots
    fig, axs = plt.subplots(3, 2, figsize=(18, 15))

    # Plot original signal
    axs[0, 0].plot(time, signal_data)
    axs[0, 0].set_title('Original Waveform')
    axs[0, 0].set_xlabel('Time [s]')
    axs[0, 0].set_ylabel('Amplitude')

    # Plot noise-reduced signal
    axs[0, 1].plot(time, reduced_signal)
    axs[0, 1].set_title('Noise-Reduced Waveform')
    axs[0, 1].set_xlabel('Time [s]')
    axs[0, 1].set_ylabel('Amplitude')

    # Plot spectrogram of original signal
    axs[1, 0].pcolormesh(times_orig, freqs_orig, S_orig_db)
    axs[1, 0].set_title('Spectrogram of Original Signal')
    axs[1, 0].set_xlabel('Time [s]')
    axs[1, 0].set_ylabel('Frequency [Hz]')
    axs[1, 0].set_ylim(0, 2000)  # Limit frequency axis to 2000 Hz

    # Plot spectrogram of noise-reduced signal
    axs[1, 1].pcolormesh(times_reduced, freqs_reduced, S_reduced_db)
    axs[1, 1].set_title('Spectrogram of Noise-Reduced Signal')
    axs[1, 1].set_xlabel('Time [s]')
    axs[1, 1].set_ylabel('Frequency [Hz]')
    axs[1, 1].set_ylim(0, 2000)  # Limit frequency axis to 2000 Hz

    # Plot PSD of original signal
    freqs_orig_psd, Pxx_orig = signal.welch(signal_data, fs=framerate, nperseg=2048)
    axs[2, 0].plot(freqs_orig_psd, 10 * np.log10(Pxx_orig), color='blue')
    axs[2, 0].set_title('PSD of Original Signal')
    axs[2, 0].set_xlabel('Frequency [Hz]')
    axs[2, 0].set_ylabel('Power/Frequency [dB/Hz]')
    axs[2, 0].set_xlim(0, 2000)

    # Plot PSD of noise-reduced signal
    freqs_reduced_psd, Pxx_reduced = signal.welch(reduced_signal, fs=framerate, nperseg=2048)
    reduced_peaks, _ = signal.find_peaks(Pxx_reduced, width=5)  # Adjust parameters as needed
    axs[2, 1].plot(freqs_reduced_psd[reduced_peaks], 10 * np.log10(Pxx_reduced[reduced_peaks]), 'x', color='red')
    axs[2, 1].plot(freqs_reduced_psd, 10 * np.log10(Pxx_reduced), color='blue')
    axs[2, 1].set_title('PSD of Noise-Reduced Signal')
    axs[2, 1].set_xlabel('Frequency [Hz]')
    axs[2, 1].set_ylabel('Power/Frequency [dB/Hz]')
    axs[2, 1].set_xlim(0, 2000)

    # Display the plots
    plt.tight_layout()
    plt.show()

# Example usage
path = '/Users/loickabaille/Desktop/20240412_163832_150.4290_48_36.wav'
plot_wav_spectrogram_psd(path)
