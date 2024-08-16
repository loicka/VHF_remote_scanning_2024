"""
Contains methods for recording and storing the signal from the biotracker. 
"""

def detect_audio_device():
    """
    Detect the port on the pi that is connected to the biotracker audio

    RETURN: 
    - [] position: port of audio connection 
    """
    import sounddevice as sd
    import numpy as np
    list=sd.query_devices() #get all devices 
    for d in np.arange(0, len(list)): # go through devices
        if  'USB Audio' in list[d]['name']: #if named Audio Device
            position=d  #save as position 
            break
        else:
            print('no audio port found')
            position=np.nan
    return position #return audio port, or nan if none 

def audio_recording(duration,path,filename):
    """
    Record and save audio file from biotracker

    [] duration: Desired length of recording
    [String] path: path to save recording to locally
    [String] filename: name of this audio recording 

    """
    import sounddevice as sd
    from scipy.io.wavfile import write
    import os

    fs = 44100 # Sample rate
    sd.default.device=int(detect_audio_device())
    myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()  # Wait until recording is finished
    #check if directory exist:
    isExist = os.path.exists(path)
    print(path)
    if not isExist: #if doesnt exists, create it
        os.makedirs(path) #create folder to store file

    write(path+filename, fs, myrecording)  # Save as WAV file
    print(filename, 'Audio file saved!')

def create_copy_tmp_folder(file_path,target_folder):
    """
    Copy audio file to temporary folder (tmp) for upload

    [String] filepath: path to audio file to be copied 
    [String] target_folder: name of folder 

    """
    import os
    import shutil
    isExist = os.path.exists(target_folder)
    if not isExist:  # if doesn't exist, create it
        os.makedirs(target_folder)  # create folder to store file
    shutil.copy(file_path,target_folder)
    print(file_path,'Audio file copied to tmp folder!')

def remove_files():
    """
    Removes files that are older than 2 days from the VHF_data directory. 
    Does this to prevent running out of memory 

    RETURN:
    - [Int] count: number of files that were deleted 
    """
    from datetime import datetime, timedelta, timezone
    import os
    import pytz
    data_storage = f"/home/mars/vhf_data/"
    delete = datetime.now(timezone.utc) - timedelta(days=2)
    count = 0
    for root, dirs, files in os.walk(os.path.abspath("/home/mars/vhf_data/")):
        for file in files:                                
        #parse dttm: 
            file_dttm = datetime.strptime(file[:14], "%Y%m%d_%H%M%S") 
            file_dttm = pytz.utc.localize(file_dttm)
            
            #less than current -2?
            if file_dttm < delete:
                print("deleting", file_dttm)
                os.remove(os.path.join(root, file))
                count += 1
    return count