import matplotlib.pyplot as plt
import numpy as np 
from scipy.signal import find_peaks

"""
Contains all of the plotting utilities for the signal analysis workflow 
"""

def plot_wavfile(data, ax, samplerate, title):
    """
    plots the regular wavfile data, as it is resampled but not smoothed. 

    [Array] data: .wav file data
    [Axis] ax: axis of plot
    [Int] samplerate: samples per second 
    """
    time = np.linspace(0., data.shape[0] / samplerate, data.shape[0])
    ax.plot(time, data)
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Amplitude")
    ax.grid()
    ax.set_title(f"{title} Signal")

def spectrogram(spc, samplerate, fig, ax):
    """
    plots the spectrogram (freq vs time with intensity)

    [SPC] spc: spectrogram data
    [Int] samplerate: samples per second
    [Figure] fig: matplotlib figure
    [Axis] ax: axis of plot 
    """
    pcm = ax.pcolormesh(spc.times, spc.frequencies, 10 * np.log10(spc.spectrogram), shading='auto')  # Use logarithmic scale for better visualization
    fig.colorbar(pcm, label='Power Spectral Density [dB]', ax=ax)
    ax.set_ylabel('Frequency [Hz]')
    ax.set_xlabel('Time [s]')
    ax.set_title(f'Spectrogram {samplerate}hz')

def psd(spc, ax):
    """
    Plots the processed power spectral density with the detected signal freq 

    [SPC] spc: spectrogram data
    [Axis] ax: axis of plot 
    """
    psd = spc.psd
    ax.grid()
    # Plot the PSD
    ax.plot(spc.frequencies, psd)  # Use logarithmic scale for better visualization
    ax.plot(spc.max_freq, spc.max_psd, 'ro', label=f"{spc.max_freq}")  # 'ro' stands for red circles
    ax.legend()
    # Set labels and title
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Power Spectral Density (dB/Hz)')
    ax.set_title(f'Power Spectral Density')

def plot_match_filter(data, percentile, ax):
    """
    plots the resulting filtered data, as well as peaks if any are detected 

    [Array] data: .wav file data
    [Float] percentile: percentile of best detection
    [Axis] ax: axis of plot
    """
    ax.plot(np.abs(data)) 
    ax.grid()

    if not np.isnan(percentile):
        min_height = np.percentile(data, percentile)
        peaks, properties = find_peaks(data, height=min_height, threshold=None, distance=5000, prominence=None, width=None,
                                        wlen=None, rel_height=None, plateau_size=None)
    
        ax.plot(peaks,properties["peak_heights"],marker='*')
        ax.axhline(min_height, color="red", label=f"{min_height}")
    ax.set_title("Match Filter") 
    ax.set_xlabel('Sample Index') 
    ax.set_ylabel('Amplitude') 

def plot_results(stats, output_path):
    """
    plots a pi chart of detection accuracy- only used for static analysis 

    [DataFrame] stats: dataframe of all signals and results. Used during static analysis only, so data is pre-labeled
    [String] output_path: output path to store plot 
    """
    fig, ax = plt.subplots()
    labels = ['positive', 'negative', 'false_positive', "false_negative"]  # Example labels
    colors = {'positive': 'green', 'negative': 'blue', 'false_positive': 'red', "false_negative": "orange"}
    s = stats['return'].value_counts()
    ax.pie(s,labels = s.index, startangle=90,  colors=[colors[label] for label in labels], autopct='%.2f')
    ax.set_title(f"Signal Detection Accuracy Analysis 1 Peak")
    fig.savefig(output_path)

def plot_psd(data, freq, index, height, output_path, m1, m2, file):
    """
    plots all PSD peaks detected given parameters. typically not used. selected peak in red (m1, m2) 

    [Array] data: PSD intensity, y axis
    [Float] freq: frequencies, x axis
    [Array] index: indexes of all detected peaks
    [Array] height: height of all detected peaks 
    [String] output_path: save plot here 
    [Float (?)] m1: index of selected frequency 
    [Float (?)] m2: height of selected frequency 
    """
    fig, ax = plt.subplots()
    ax.plot(freq, data)
    #ax.plot(index, height, marker='*')
    ax.plot(index,height,marker='*')
    ax.plot(m1,m2,marker='*', color="red")
    ax.set_title("Power Spectral Density Peaks") 
    ax.set_xlabel('data') 
    fig.savefig(f"{output_path}psd/psd_{file}.jpg", bbox_inches="tight") 