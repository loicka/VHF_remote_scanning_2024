#!/usr/bin/python3
from set_frequency import set_and_check_frequency
from set_gain import set_and_check_gain
from wav_file_functions import audio_recording,create_copy_tmp_folder


import numpy as np
import serial
from serial import PARITY_NONE,EIGHTBITS,STOPBITS_ONE
import time
import datetime
from datetime import timezone

#READ & EXTRACT FREQUENCIES AND GAINS FROM CONFIG FILE
import yaml
from yaml import CLoader as Loader, CDumper as Dumper
with open("config.yaml") as fh:
   config=yaml.load(fh, Loader=Loader)

transmitters=config['transmitters'] #dictionaries w/ keys

# Extract gains from config file
gains=np.array(config['gains'])
#Set serial configuration + Open serial port
ser = serial.Serial(port='/dev/ttyUSB0',baudrate=1200,bytesize=EIGHTBITS,parity=PARITY_NONE,stopbits=STOPBITS_ONE,
                     timeout=10, xonxoff=False, rtscts=False, write_timeout=None, dsrdtr=False, inter_byte_timeout=None, exclusive=None)

duration=10 #seconds of audio recording

#filename: datetime_frequency_gain_biotrack.wav where datetime yyyymmdd-hhmmss
prefix=config['wavFilePath']
receiverName=config['receivers'][0]['name'] #extract receiver name

for n in np.arange(0,len(transmitters),1):
      # Extract frequency and transmitter ID from dictionary
      frequency=transmitters[n]['frequency'] #get the int. frequency info of the n_th dictionary
      frequency=str(frequency)[0:3]+'.'+str(frequency)[3:7] #convert frequency to str of format xxx.xxxx
      transmitter_ID = transmitters[n]['name']

      freq_check=set_and_check_frequency(ser,frequency)
      # freq_check=1
      if freq_check==1: #if frequency was set successfully, vary gain
            for gain in gains:
                 # gain_check = set_and_check_gain(ser, gain)

                  filename = datetime.datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S") + '_' + str(frequency) + '_' +str(transmitter_ID)+'_'+ str(
                        gain)+'.wav'

                  now = datetime.datetime.now(timezone.utc)
                  path=prefix+'/'+str(now.year)+'/'+str(now.month)+'/'+'vhf_'+str(receiverName)+'/'+str(now.day)+'/'+str(now.hour)+'/'

                  if gain_check==1:#if gain was set successfully, record file
                        audio_recording(duration,path,filename)
                        #Copy audio record to tmp folder
                        file_path=path+filename
                        target_folder='/home/spot/tmp/'
                        create_copy_tmp_folder(file_path,target_folder)

                        time.sleep(10)



