#!/usr/bin/python3
from recording.set_frequency import set_and_check_frequency
from recording.set_gain import set_and_check_gain
from recording.wav_file_functions import audio_recording,create_copy_tmp_folder, remove_files
import numpy as np
import serial
from serial import PARITY_NONE,EIGHTBITS,STOPBITS_ONE
import time
import datetime
from datetime import timezone
import serial.tools.list_ports
#READ & EXTRACT FREQUENCIES AND GAINS FROM CONFIG FILE
import yaml
from yaml import CLoader as Loader, CDumper as Dumper

"""
Main_recording.py: a script that utilizes modules from recording/ to iterate through frequencies and gains 
established in the config file and record a .wav file for each combination. 
Loads config file, establishes connection with the biotracker, and proceeds 
to loop through defined freq/gains, saving .wav files continuously
"""

"""
SETUP: reading config file, establishing conncetion to biotracker, defining receiver and transmitters, filepaths, etc. 
"""
#open config file (contains freq, gains, receivers, transmitters, etc.)
with open("../config.yaml") as fh:
   config=yaml.load(fh, Loader=Loader)

transmitters=config['transmitters'] #dictionaries w/ keys
temporary = config["temporary_path"]
# Extract gains from config file
gains=np.array(config['gains'])
#Set serial configuration + Open serial port, check thru all USBtty available ports
ser = serial.Serial(port='/dev/ttyUSB0',baudrate=1200,bytesize=EIGHTBITS,parity=PARITY_NONE,stopbits=STOPBITS_ONE,
                    timeout=10, xonxoff=False, rtscts=False, write_timeout=None, dsrdtr=False, inter_byte_timeout=None, exclusive=None)
duration=10 #seconds of audio recording

#filename: datetime_frequency_gain_biotrack.wav where datetime yyyymmdd-hhmmss
prefix=config['wavFilePath']
receiverName=config['receivers'][0]['name'] #extract receiver name
count_uploaded = 0 #keep track of number of uploaded files 

"""
RECORDING: This loop continues until user stops code manually. It iterates through transmitters, freq, and gains defined 
in config files, reads a recording from the biotracker, and saves it. Additionally, it wipes old files 
to prevent storage errors. 
"""
while True:
      #for each transmitter in the config file
      for n in np.arange(0,len(transmitters),1):
            # Extract frequency and transmitter ID from dictionary
            frequency=transmitters[n]['frequency'] #get the int. frequency info of the n_th dictionary
            frequency=str(frequency)[0:3]+'.'+str(frequency)[3:7] #convert frequency to str of format xxx.xxxx
            transmitter_ID = transmitters[n]['name'] #get transmitter ID 

            freq_check=set_and_check_frequency(ser,frequency) #set biotracker to current frequency, return 1 if successful 

            if freq_check==1: #if frequency was set successfully, vary gain
                  for gain in gains: #for each gain in config file
                        gain_check = set_and_check_gain(ser, gain) #set biotracker to current gain, return 1 if successful 

                        filename = datetime.datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S") + '_' + str(frequency) + '_' +str(transmitter_ID)+'_'+ str(
                              gain)+'_'+receiverName+'.wav' #create filename for this signal 

                        now = datetime.datetime.now(timezone.utc) #get time 
                        path=prefix+'/'+str(now.year)+'/'+str(now.month)+'/'+'vhf_'+str(receiverName)+'/'+str(now.day)+'/'+str(now.hour)+'/' #parse into storage path 

                        if gain_check==1:#if gain was set successfully, record file
                              audio_recording(duration,path,filename) #record file here
                              #Copy audio record to tmp folder
                              file_path=path+filename
                              target_folder=temporary
                              create_copy_tmp_folder(file_path,target_folder) 
                              count_uploaded += 1 #add 1 to total number of files uploaded
                              time.sleep(10) #wait...
                              
                        #to prevent storage errors, every 150 uploads the code clears files >2days old
                        if count_uploaded > 150:
                              num = remove_files() #run remove files greater than two days old 
                              print(f"Successfully cleared {num} files") #print number of files deleted
                              count_uploaded = 0 #reset count 
                              