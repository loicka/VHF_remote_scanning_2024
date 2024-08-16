from wav_file_functions import load_plot_wav_file
from analysis_functions import amdemod, peak_analysis,send_info_to_webpage


from scipy.signal import find_peaks
import os
import time

# RUNNING
import numpy as np
path='/home/spot/tmp/' #temporary file folder
#filenames=os.listdir(path)
#print(filenames)


for filename in os.listdir(path):
    #filename=filenames[n]
    directory=path+filename

    date_time=filename[:-21] #extract date/time from filename: yymmdd_hhmmss
    #print(date_time, filename)
    transmitterName=filename[-11:-7] #extract transmitter name/ID from filename
    #TODO might need to add receiver name to filename and extract it as well

    # Read, extract, plot .wav data
    samplerate,data,gain,=load_plot_wav_file(directory)
    duration_signal=len(data)/samplerate

    # Extract peaks info
    peaks,number_peaks,peak_heights,prominences,meanPulseLength,stdPulseLength,score=peak_analysis(data,samplerate)
    #print(meanPulseLength,number_peaks,score,stdPulseLength,samplerate,duration_signal,date_time,transmitterName)

    # Send info to webpage
    send_info_to_webpage(meanPulseLength,number_peaks,score,stdPulseLength,samplerate,duration_signal,date_time,transmitterName)

    # Delete file that was analysed
    os.remove(directory)
    print(directory, 'Tmp file successfully deleted')
    
time.sleep(60)

#for n in np.arange(0,len(filenames),1):
    # Extract filename
    # filename=filenames[n]
    # directory=path+filename

    # date_time=filename[:-21] #extract date/time from filename: yymmdd_hhmmss
    # print(n, date_time, filename)
    # transmitterName=filename[-11:-7] #extract transmitter name/ID from filename

    # # Read, extract, plot .wav data
    # samplerate,data,gain,=load_plot_wav_file(directory)
    # duration_signal=len(data)/samplerate

    # # Extract peaks info
    # peaks,number_peaks,peak_heights,prominences,meanPulseLength,stdPulseLength,score=peak_analysis(data,samplerate)

    # # Send info to webpage
    # send_info_to_webpage(meanPulseLength,number_peaks,score,stdPulseLength,samplerate,duration_signal,date_time,transmitterName)

    # # Delete file that was analysed
    # os.remove(directory)
    # print(directory, 'Tmp file successfully deleted')

