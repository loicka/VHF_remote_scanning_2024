from signals.signal_obj import Signal
import os 
import yaml
import time
import pandas as pd
from upload.data_upload_functions import send_info_to_lora_gateway

"""
Script that analyzes and uploads recorded files in "tmp" (temporary) dir
Running constantly. While there are files in the 
tmp folder, analyze them and report the results to the database 

"""
# Create mp3s folder if doesnt exist already
if not os.path.exists(f"../mp3s"):
    os.makedirs(f"../mp3s/")

def check_dir(directory, config):
    """
    method that analyzes and uploads all files in the tmp directory to the DB

    [Array] directory: directory that contains files to be uploaded 
    [DataFrame] config: dataframe of configuration information 
    """
    #for each file in the given directory 
    for file in directory:
            print("Analyzing: ", file)
            #analyze that file (through signal creation) 
            signal = Signal(path+"/"+file, config)
            #wait 2 seconds to avoid overwrite 
            time.sleep(2)
            #push analyzed signal info to database 
            send_info_to_webpage(signal)
            #move file to "completed" file directory 
            os.remove(path+"/"+file)
        
        



"""
Initializing database with datapoints to be visible...
"""
#print("initializing database")
#initialize_database("config.yaml")

"""
ANALYSIS: Loop that analyzes signal and uploads to DB. Runs forever. 
"""
#get config: 
with open("../config.yaml") as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

"""
Path where recorded files are stored 
"""
path = config["temporary_path"]
print(path)
directory = os.listdir(f"{path}")

while True: 
    directory = os.listdir(f"{path}")
    #If files exist in the directory 
    if len(directory) > 0: 
        #upload files in directory:
        check_dir(directory, pd.DataFrame(config["transmitters"]))
    else: 
        #if directory is empty, sleep for five seconds, and check again: 
        print("sleeping ... (_ _ ')<(Zzz)   ｡-ᆺ-｡ <(Zzz)")
        time.sleep(5)
        


