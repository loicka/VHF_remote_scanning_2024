

def initialize_database(config_file_path):
    '''For grafana display to start displaying as programmed, it needs 2 data points for each receiver/transmitter.
    This function initializes the display by sending 2 test values to the databases.
    Need to have 1min interval between 2 runs in order to have a different timestamp, otherwise write over point if same timestamp'''
    import yaml
    from yaml import CLoader as Loader, CDumper as Dumper
    from datetime import datetime
    import time

    # READ & EXTRACT CONFIG FILE INFO
    with open(config_file_path) as fh:
        config = yaml.load(fh, Loader=Loader)

    # Extract receiver names
    receiver_names = [receiver['name'] for receiver in config['receivers']]
    # Extract transmitter names
    transmitter_names = [transmitter['name'] for transmitter in config['transmitters']]

    #For each receiver/transmitter combination, send 2 test values to database
    for i in [0,1]: # iterate over loop twice
        date_time = datetime.now().strftime('%Y%m%d_%H%M%S')

        decision=5 # for testing/intializing database
        for receiverName in receiver_names:
            for transmitterName in transmitter_names:
                send_info_to_webpage(date_time, transmitterName, receiverName, decision)

        print('Pausing for 1 minute, before sending next test run...')
        # Pause for 1 minute
        time.sleep(60)

def send_info_to_webpage(date_time,transmitterName,receiverName,decision):
    from influxdb import InfluxDBClient
    from datetime import datetime
    import numpy as np

    # READ & EXTRACT CONFIG FILE INFO
    ts = datetime.strptime(date_time, '%Y%m%d_%H%M%S')

    #receiverName = config['receivers'][0]['name']  # extract receiver name
    timeFormat = "%Y-%m-%dT%H:%M:%S.%fZ"

    point = {
        "measurement": "presence_analysis",
        "time": ts.strftime(timeFormat),
        "tags": {
            "receiver": receiverName,
            "transmitter": transmitterName,
        },
        "fields": {
            "decision":decision,
            # "meanPulseLength": float(meanPulseLength),
            # "nHits": int(number_peaks),
            # "hitsExpected": int(7),
            # "score": float(score),
            # "stdPulseLength": float(stdPulseLength),
            # "targetPulseLength": float(pulse),
            # "inputLength": float(duration_signal),  # secs
            # "inputSampleRate": float(samplerate),
        }
    }
    client = InfluxDBClient(host="10.1.3.211", port=8089, database="vhf")
    res = client.write_points([point])
    print('Successfully written on database')


#TEST FUNCTION
config_file_path='config.yaml'
# Initialization of database for grafana display
config_file_path='config.yaml'
initialize_database(config_file_path)

#send_info_to_webpage(date_time,transmitterName,receiverName,decision)