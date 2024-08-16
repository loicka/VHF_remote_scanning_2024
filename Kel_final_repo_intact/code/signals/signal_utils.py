import numpy as np 
import pandas as pd 
from scipy.signal import find_peaks
from scipy.signal import resample

"""
This file contains the technical work for signal processing. it's separated out to be more readable. all functions here 
are called by the signal object
"""

def resample_signal(data, rec_sr, des_sr): 
    """
    given a signal, the current samplerate, and the desired samplerate, resample signal to desired samplerate. 

    [Array] data: .wav file data
    [Int] rec_sr: recorded samplerate (something around 44khz historically)
    [Int] des_sr: desired samplerate (typically set to 10khz)
    """
    secs = len(data)/rec_sr #number of seconds in recording
    samps = secs * des_sr #new num of samples is number of seconds * desired samplerate
    samps = np.round(samps, 0).astype(int) #rounding and casting
    data = resample(data, samps) #resample data
    return data #returned resampled data 

def generate_signal(freq, samplerate):
    """
    given a frequency ans amplerate, generate a template signal of 0.025s length, given freq, given samplerate, normalized around 0 

    [Float] freq: Frequency of signal  
    [Int] samplerate: samplerate of signal (num of samples per second)
    """
    from sklearn.preprocessing import MinMaxScaler

    #generate the sin wave (actual signal part) of certain length and frequency
    signal = pd.DataFrame({"data": np.sin(2 * np.pi * freq * 
                                     np.linspace(0, 0.025, int(samplerate * 0.025), endpoint=False))})

    #scale between -1.0 and 1.0
    model= MinMaxScaler().fit(signal[["data"]])
    signal[["normalized"]]= model.transform(signal[["data"]])
    signal = signal.drop(columns=["data"])

    #fill NAN with 0.5
    signal["normalized"] = signal["normalized"].fillna(0.5)
    signal = signal[["normalized"]]

    #center around 0, between -1 and 1 
    signal["normalized"] = signal["normalized"] * 2 
    signal["normalized"] = signal["normalized"] - 1

    #save as numpy array and return 
    signal = signal[["normalized"]].to_numpy().ravel()

    return signal 

def peaks_by_percentile(data, pulse, samplerate, output_path):
    """
    detect peaks in match filter data. for each percentile, detect peaks and calculate score for that detection

    [Array] data: .wav file data
    [Float] pulse: Configured time between signals (i.e, signal beeps regularly every 1.3s)
    [Int] samplerate: number of samples per second 
    [String] output_path: filepath for outputs 

    RETURN: 
    - [Float, Boolean, Float] see check_detection
    """
    #define percentiles for height data. Note: if this are altered to be too high (like a percentile over 99.75),
    #noise is likely to be picked up as the tight constraint causes the tops of even the noisiest signals to appear
    #alone. 
    percentiles = [80, 90, 92.5, 93, 93.5, 94, 94.5, 95, 95.5, 96, 96.5, 97, 97.5, 98, 98.5, 99, 99.25, 99.5, 99.75]
    peak_percents = pd.DataFrame()

    #for each percentile, calculate min height, find peaks, 
    for p in percentiles: 
        peaks, properties = find_peaks(data, height=np.percentile(data, p), threshold=None, 
                                distance=5000, prominence=None, width=None,
                                    wlen=None, rel_height=None, plateau_size=None)
        #array of time (secs) between peaks 
        peaks = np.diff(peaks / samplerate) 
        #calculate score 
        score = np.average(np.abs(peaks - pulse)) 
        score = score / pulse
        score = 1 - score
        #if the score is sub-zero (peaks were so far apart the numerator is multiple * denominator), assume to 0 
        score = max(score, 0)
        score = score * 100
        #add info about current percentile and score to DF 
        peak_percents = pd.concat([peak_percents, 
                                   pd.DataFrame({"percentile":p, 
                                            "num_peaks": len(peaks), "score": score}, index=[0])])
    #after all percentiles are processed, select best peak
    return check_detection(peak_percents)

def check_detection(percentiles):
    """
    selects and returns best detection, as well as the final detection=true or detection=false 

    [DataFrame] percentiles: results from calculating peaks by percentile.

    RETURN: 
    - [Float] percentile: percentile of chosen detection
    - [Boolean] detection: if the chosen detection has a score of 70+
    - [Float] score: score of chosen detection, between 0 to 100
    """
    #locate percentiles that contain between 4 to 6 peaks: 
    percentiles = percentiles[(percentiles.num_peaks >= 4) & (percentiles.num_peaks < 7)]
    #if there exist detections with between 4 and 6 peaks: 
    if len(percentiles) > 0:
        #get maximum score 
        maximum_passing = percentiles.score.max()
        #get final percentile to return- data where score is maximum 
        detection = percentiles[percentiles.score == maximum_passing]
        #print the score and number of peaks of best detection 
        print(f"Peak is returning with score of {maximum_passing} and num peaks {detection.num_peaks.iloc[0]}")
        #if the score is above min passing threshold of 70, return that percentile, passing=True, and the score 
        if maximum_passing > 70.0: 
            return detection.iloc[0]["percentile"], True, maximum_passing
        #if the score is not above min passing threshold of 70, return no percentile, passing=False, and the best score
        else: 
             return np.nan, False, maximum_passing
    #if there are no signals with btwn 4 and 6 peaks, there is no detection, return no percentile, passing=false, and score=0
    else: 
        return np.nan, False, 0.0 

def match(signal_type, signal_detected):

    """
    used for static analysis final results

    [String] signal_type: known value for if the recording contains a signal. prelabeled
    [Boolean] signal_detected: If a signal was detected durign signal analysis. 

    RETURN: 
    - [STRING] : if this yielded a positive, false positive, false negative, or negative 
    """
    if signal_detected:
            if signal_type == "yes_signal":
                return "positive"
            else:
                return "false_positive"
    else: 
            if signal_type == "yes_signal":
                return "false_negative"
            else:
                return"negative"   