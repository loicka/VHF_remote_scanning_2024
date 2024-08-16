import numpy as np 
import datetime 
import pandas as pd
import matplotlib.pyplot as plt
import noisereduce as nr
import yaml
from pydub import AudioSegment
from scipy.signal import lfilter
from scipy.io import wavfile
from .signal_utils import resample_signal, generate_signal, peaks_by_percentile, match
from .signal_plot_utils import plot_wavfile, spectrogram, plot_match_filter, psd
from .spc import SPC


class Signal:
    """
    Object that is created each time a signal file is uploaded. In the creation of a signal object, 
    all relevant information is parsed or created, and signal analysis is performed. 
    """ 
    def __init__(self, path, config, output_path=None, truth=None):
        """ Initializes the signal object 
        [String] path: 
        [DataFrame] config: Configuration information
        [String] output_path: Optional parameter for local storage of plots
        [String] truth: Optional parameter for labeled data stating if a signal is known to exist. 
        """
        #parse string info about signal: 
        self.path = path #path to signal 
        self.output_path = output_path #optional storage path 
        self.truth = truth #optional, states if file is known to contain a signal 
        self.config = config #dataframe of relevant configuration info

        #parse information (i.e gain, transmitter) out of the filename 
        self.file, self.dttm, self.gain, self.receiver, self.pulse, self.transmitter_name = self.parse_file() 

        #create signal data 
        self.samplerate = 10000 #CHANGE RESAMPLE RATE HERE
        
        #read wav file- load data, resample, and apply noise reduction
        self.data, self.audio = self.create_wav_data()
        #find frequency of file 
        self.spc, self.freq = self.find_freq()

        #create template for this file: 
        self.template = self.create_template()
        #apply match filter 
        self.match_filter()
        #complete peak detection
        self.percentile, self.detection, self.score = self.detect_peak()
        #generate output dictionary: detection, return
        self.output = self.generate_output()

        if output_path is not None: 
            #if we're reading from prerecorded files, generate and save plots in local dir 
            self.plot()

    def create_wav_data(self):
        """
        Load wav file data. Remove first second, convert to mono, 
        and resample to 10kz.
        """
        rec_sr, data = wavfile.read(self.path) #read .wav file into data
        audio = AudioSegment.from_wav(self.path) #read .wav file into data

        data=data[44100:] #cut away the first second

        #make audio monochannel if bichannel 
        try: 
            data = data[:,0] 
        except:
            pass

        #resample signal to desired samplerate (set in init). Makes processing quicker at lower samplerate. 
        data = resample_signal(data, rec_sr, self.samplerate)
        data = pd.DataFrame({"raw": data})
        data["noise_reduction"] = nr.reduce_noise(y=data["raw"].to_numpy(), sr=self.samplerate)

        #return data as dataframe. 
        return data, audio
    
    
    def create_template(self):
        """
        Generate the template signal for this signal, given the freq and samplerate 
        """
        return generate_signal(self.freq, self.samplerate)

    def find_freq(self):
        """
        generate spectrogram for this signal. detect signal from resulting spectrogram 
        """

        #generate spectrogram information for this signal  
        spc = SPC(self.data["noise_reduction"].to_numpy(), self.samplerate, self.output_path)
        return spc, spc.max_freq

    def parse_file(self): 
        """
        Parse filename into relevant data
        """
        filename= self.path.split("/")[-1] #get whole filename of signal 
        file = filename.split("_") #split into informational parts
        dttm = file[0] + file[1] #grab DTTM, first two sections 
        transmitter = file[2] + "00" #grab transmitter number, third section. 
        gain = file[4].split(".")[0] #grab gain, fifth section 
        #change made on 5/1/24 added receiver name to filepaths
        #this handles files created before and after this date
        if len(file) > 5:
            receiver = file[-1].split(".")[0] #get receiver name 
        else: 
            receiver = "UNKNOWN"
        #select pulse (space between signals) from config file as dependent on transmitter name
        try: 
            pulse = self.config.loc[self.config.frequency == int(transmitter.replace(".", ""))].iloc[0]["pulse"]
            if pulse == "NA":
                pulse = 1.3
                print(f"PULSE FOR TRANSMITTER {transmitter} IS NOT FOUND. USING DEFAULT 1.3s. ADD TRANSMITTER TO CONFIG.YAML FOR ACCURACY.")
        except: 
            pulse = 1.3
            print(f"PULSE FOR TRANSMITTER {transmitter} IS NOT FOUND. USING DEFAULT 1.3s. ADD TRANSMITTER TO CONFIG.YAML FOR ACCURACY.")
        try: 
            transmitter_name = self.config.loc[self.config.frequency == int(transmitter.replace(".", ""))].iloc[0]["name"]
        except: 
            transmitter_name = file[3]
        #fine the name of the transmitter

        return filename, dttm, gain, receiver, pulse, transmitter_name

    def match_filter(self):
        """
        Apply match filter using pregenerated template to signal 
        """
        fir_coeff = self.template[::-1]
        convolved_signal = lfilter(fir_coeff, 1, self.data["noise_reduction"].to_numpy())
        convolved_signal = convolved_signal * convolved_signal
        self.data["match_filter"] = convolved_signal.ravel()

    def detect_peak(self):
        """
        With filtered data, perform peak detection and generate score. Return percentile with highest score, 
        and if that score is > 70, and therefore passing. 
        """
        return peaks_by_percentile(self.data["match_filter"].to_numpy(), self.pulse, self.samplerate, self.output_path)
    
    def generate_output(self):
        """
        create output dictionary with object information for the webpage/file system
        """
        output = {
            "filename": self.file, 
            "dttm": self.dttm, 
            "transmitter": self.transmitter_name, 
            "receiver": self.receiver,
            "gain": self.gain, 
            "samplerate": self.samplerate, 
            "true_signal": self.truth, 
            "detection": self.detection,
            "percentile": self.percentile, 
            "score": self.score,
            "peak_width": self.spc.peak_width,
            "return": match(self.truth, self.detection)
        }
        return output

    def plot(self): 
        """
        create six panel plot! 
        """
        fig, axs = plt.subplots(3, 2, figsize=(15, 18))

        #raw and reduced signal: 
        plot_wavfile(self.data["raw"].to_numpy(), axs[0,0], self.samplerate, "Raw Recorded")
        plot_wavfile(self.data["noise_reduction"].to_numpy(), axs[0, 1], self.samplerate, "Noise Reduced Recorded")
        plot_wavfile(self.template, axs[2, 1], self.samplerate, "Template")

        #spectrogram and PSD: 
        spectrogram(self.spc, self.samplerate, fig, axs[1, 0])
        psd(self.spc, axs[1, 1])

        plot_match_filter(self.data["match_filter"].to_numpy(), self.percentile, axs[2, 0])

        fig.suptitle(f"Analysis of {self.truth}: {self.file}")
        plt.tight_layout()
        fig.savefig(f"{self.output_path}/panel_{self.file}.jpg", bbox_inches="tight")
        plt.close('all')

