import os 
import sys
import pandas as pd 
import time
import yaml
from signals.signal_obj import Signal
from signals.signal_plot_utils import plot_results
"""
script to analyze prerecorded signal files with truth values assigned. needs an input folder that is sorted into
yes_signal and no_signal files

python static_analysis.py "project name" "signal_folder_path"

"""
#check if inputs (project name, signal folder location) is valid: 
try: 
    path = f"../mnt/data/local/{sys.argv[2]}/"
    project = sys.argv[1]
    directory = os.listdir(f"{path}")
    print ('Running signal analysis on : ', path, "into project folder: ", project)
except: 
    print(f"Input path is not valid. Please rerun with valid path.")

#create output path for project: 
output_path = f"../output/project/{project}"
if not os.path.exists(f"{output_path}"):
    os.makedirs(output_path)
    os.makedirs(f"{output_path}/plots/panels/no_signal/")
    os.makedirs(f"{output_path}/plots/panels/yes_signal/")
    os.makedirs(f"{output_path}/plots/panels/yes_signal/psd/")
    os.makedirs(f"{output_path}/plots/panels/no_signal/psd/")


#get config: 
with open("../config.yaml") as stream:
    try:
        #read the config- contains info about transmitters 
        config = pd.DataFrame(yaml.safe_load(stream)["transmitters"])
        #print(config)
    except yaml.YAMLError as exc:
        print(exc)

#create DF to store signal analysis results
stats = pd.DataFrame()
#iterate through files with signal and without signal (no_signal and yes_signal): 
for signal_type in directory: 
    #choose current subdirectory (no_signal or yes_signal)
    current_path = f'{path}/{signal_type}/'
    #for every file in this directory: 
    for filename in os.listdir(f'{current_path}'):
        #run main analysis on the signal: 
        #this signal will be analyzed and relevant output will be stored 
        signal = Signal(current_path+filename, config, f"{output_path}/plots/panels/{signal_type}/", signal_type)
        #append signal.outputs to stats dataframe for storage 
        stats = pd.concat([stats, pd.DataFrame([signal.output])], ignore_index = True)
        #read final detection: true or false
        detection = signal.output["detection"]
        print(f"{filename} analysis completed with {detection} detection.")
#after completion, print all signals have been analyzed and store final .csv information 
print("All signals analyzed.")
stats.to_csv(f"{output_path}/signal_analysis.csv")
plot_results(stats, f"{output_path}/signal_analysis.jpg")



