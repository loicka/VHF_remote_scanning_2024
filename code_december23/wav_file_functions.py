
def detect_audio_device():
    import sounddevice as sd
    import numpy as np
    list=sd.query_devices()
    for d in np.arange(0, len(list)):
        if 'USB Audio Device' in list[d]['name']:
            position=d
            break
    return position

def audio_recording(duration,path,filename):
    #Create wav file

    import sounddevice as sd
    from scipy.io.wavfile import write
    import os

    fs = 44100 # Sample rate
    sd.default.device=str(detect_audio_device())
    myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()  # Wait until recording is finished
    #check if directory exist:
    isExist = os.path.exists(path)
    if not isExist: #if doesnt exists, create it
        os.makedirs(path) #create folder to store file

    write(path+filename, fs, myrecording)  # Save as WAV file
    print(filename, 'Audio file saved!')

# Load wav file
def load_plot_wav_file(path):
    '''
    - Load wav
    - remove 1sec of recording
    - plot .wav file with filename as title
    - extract gain from filename

    Returns
    - sample rate
    - audio data of 1 channel with 1st sec cut away'''

    from scipy.io import wavfile
    import matplotlib.pyplot as plt

    gain=int(path[-6:-4]) #extract gain from .wav filename
    samplerate, data = wavfile.read(path)
    audio=data[44100:] #cut away the first second
    audio=audio/max(audio)
    # plt.plot(audio)
    # plt.ylabel("Amplitude")
    # plt.xlabel("Time (s)")
    # plt.title(path[-31:])
    # plt.grid()
    # plt.show(block=True)

    # plt.show(block=False)
    # plt.pause(3)
    # plt.close('all')
    return samplerate,audio,gain

def create_copy_tmp_folder(file_path,target_folder):
    import os
    import shutil
    isExist = os.path.exists(target_folder)
    if not isExist:  # if doesn't exist, create it
        os.makedirs(target_folder)  # create folder to store file
    shutil.copy(file_path,target_folder)
    print(file_path,'Audio file copied to tmp folder!')

# # RUNNING
# import numpy as np
#
# path='/home/loicka/Dropbox_MIT/RESEARCH/Antarctica/VHF_remote_scanning/mnt/data/local/2022/12/vhf_756w/12/15/20221212_150122_150.5000_68.wav'
# samplerate,data,gain,=load_plot_wav_file(path)
#
# # Run cross correlation on signal
# corr=np.correlate(data[:,0],data[:,0])
# print(corr)
#

