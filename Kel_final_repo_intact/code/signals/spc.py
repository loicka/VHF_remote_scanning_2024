import numpy as np 
from scipy.signal import find_peaks
import numpy as np
import pandas as pd 
from scipy import signal
from scipy.ndimage import gaussian_filter

class SPC:
    """
    SPC: this class represents a spectrogram. it is used internally in Signal to store information about the spectrogram, PSD, 
    and signal frequency selection process. 
    """
    def __init__(self, data, samplerate, output_path):
        """
        Initializes a spectrogram object. 
        [DataFrame] data: dataframe of .wav data. Includes column of noise reduced data.
        [String] output_path: path saved in case of any internal plot generation. 
        """
        self.data = data 
        self.samplerate = samplerate
        self.output_path = output_path
        #generate spectrogram information: 
        self.frequencies, self.times, self.spectrogram = self.generate_spectrogram()
        #calcualte PSD: log of mean of spectrogram 
        self.psd = self.generate_psd()
        #signal frequency selection: 
        self.max_freq, self.max_psd, self.prominence, self.peak_width = self.calc_max_psd()


    def generate_spectrogram(self):
        """
        Creates spectrogram and associated data. 

        [SPC] self: spectrogram object. 
        """
        frequencies, times, spectrogram = signal.spectrogram(self.data, self.samplerate, nperseg=self.samplerate, 
                                                    nfft=self.samplerate, noverlap=self.samplerate // 2)  # Assuming mono audio, if stereo, choose a channel (data[:,0] or data[:,1])
        frequencies_mask = np.logical_and(frequencies >= 400, frequencies <= 2000)
        frequencies = frequencies[frequencies_mask]
        spectrogram = spectrogram[frequencies_mask, :]

        return frequencies, times, spectrogram

    def generate_psd(self):
        """
        Applies smoothing techniques to the spectrogram to reduce noise. Includes gaussian blur and averaging over windows of 20.
        Returns PSD of smoothed data. 

        [SPC] self: spectrogram object. 

        RETURN:
        - [Array] psd: Array of power spectral density data. Frequency by intensity.
        """
        #smooth spectrogram with gaussian filter:
        self.spectrogram = gaussian_filter(self.spectrogram, sigma=1)

        #create spectrogram by pean of spectrogram. filter out NAN 
        psd = 10 * np.log10(np.mean(self.spectrogram, axis=1))
        psd = np.array([0 if x is None else x for x in psd])

        #average PSD with windows of 20 
        window = np.ones(int(20))/float(20)
        psd = np.convolve(psd, window, 'same')

        return psd


    def calc_max_psd(self): 
        """
        this code completes the signal frequency selection process. given a PSD, it detects peaks, filters by width>30, and 
        selects the most prominent remaining peak as the freq of the signal 

        [SPC] self: spectrogram to detect signal frequency of. 

        Return: 
        - [Int] max_freq: Detected frequency of signal
        - [Float] max_height: The height of the detected frequency
        - [Int] peak_width: The peak width of the detected frequency
        - [Float] max_prominence: The prominence of the detected frequency
        """
        #detect all peaks in PSD 
        peaks, properties = find_peaks(self.psd, width = 0, prominence=0, height=-1000000000)
        #if peaks are found: 
        if len(peaks) > 0: 
            data = pd.DataFrame(properties) #create df of peaks 
            data["peaks"] = peaks   
            #Filter out electrical noise by selecting noise > 30 
            data = data.loc[data.widths >= 30]
            #if there are still remaining peaks: 
            if len(data) > 0:
                #select most prominent entry from remaining 
                max_prom_row = data.loc[data.prominences ==  max(data.prominences)]
                #get frequency of that peak
                max_freq = max_prom_row["peaks"].iloc[0]
                max_prominence = max_prom_row["prominences"].iloc[0] #get prominence of the detected peak 
                max_height = max_prom_row["peak_heights"].iloc[0] #get height of the detected peak 
                peak_width = max_prom_row["widths"].iloc[0] #get width of the detected peak 
            else: 
                #if no peaks above width of 30, no signal is detected: 
                print("NO PEAK DETECTED OVER WIDTH OF 30")
                max_freq = 0
                max_height = 0 
                peak_width = 0 
                max_prominence = 0
        else: 
            #if no peaks detected, set all to 0
            print("NO PEAKS DETECTED")
            max_freq = 0
            max_height = 0 
            peak_width = 0 
            max_prominence = 0
        #store relevant freq information: the maximum freq (x axis), the peak width and the max psd 
        return max_freq + 400, max_height, max_prominence, peak_width