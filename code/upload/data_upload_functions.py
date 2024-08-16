import os 
import base64 as base64 
import psycopg2
from influxdb import InfluxDBClient
from datetime import datetime

def send_info_to_webpage_parsed(date_time,transmitterName,receiverName,decision):
    """
    Method to send info to webpage without creating a whole signal object. Used for initializing the database, which
    sends dummy points to the webpage. 

    [String] date_time: datetime to upload signal to. 
    [String] transmitterName: Name of transmitter for signal 
    [String] receiverName: Name of receiver for signal 
    [Integer] decision: Decision to be uploaded. 
    """
    
    # READ & EXTRACT CONFIG FILE INFO
    ts = datetime.strptime(date_time, '%Y%m%d_%H%M%S')

    #receiverName = config['receivers'][0]['name']  # extract receiver name
    timeFormat = "%Y-%m-%dT%H:%M:%S.%fZ"

    #organize point to be uploaded to influxDB 
    point = {
        "measurement": "presence_analysis",
        "time": ts.strftime(timeFormat),
        "tags": {
            "receiver": receiverName,
            "transmitter": transmitterName,
        },
        "fields": {
            "decision":decision
        }
    }
    #upload to Influx 
    client = InfluxDBClient(host="128.128.198.57", port=8089, database="vhf")
    res = client.write_points([point])
    print('Successfully written on database')

def send_info_to_webpage(signal):
    """
    Uploads information from signal analysis to DB/webpage for a particular signal. 

    [Signal] signal: Analyzed signal to be uploaded 
    """
    from influxdb import InfluxDBClient
    from datetime import datetime
    import numpy as np
    import yaml
    from yaml import CLoader as Loader, CDumper as Dumper

    ts = datetime.strptime(signal.dttm, '%Y%m%d%H%M%S')
    timeFormat = "%Y-%m-%dT%H:%M:%S.%fZ"
    
    #get detection in int
    if signal.score >= 70:
        d = 1
    else: 
        d = 0 
    
    # Export as .mp3
    signal.audio.export(f"../mp3s/{signal.file}.mp3", format="mp3")
    #load as MP3 and store as a base64 encoded string for Postgresql 
    with open(f"../mp3s/{signal.file}.mp3", "rb") as file:
        encoded_string = base64.b64encode(file.read()).decode('utf-8')
        encoded_string = "data:audio/mp3;base64," + encoded_string 

    #create datapoint 
    point = {
        "measurement": "presence_analysis",
        "time": ts.strftime(timeFormat),
        "tags": {
            "receiver": signal.receiver,
            "transmitter": signal.transmitter_name,
            "detection": d, 
            "score": signal.score
        },
        "fields": {
            "decision": d,
            "score": signal.score, 
            "b64_file": encoded_string,
            "filepath": signal.file
        }
    }

    #Send info to InfluxDB database
    client = InfluxDBClient(host="deep2.whoi.edu", port=8089, database="vhf_influxdb")
    res = client.write_points([point])
    print('Successfully written on InfluxDB database')

    # Prepare SQL and data for PostgreSQL
    insert_sql = """INSERT INTO presence_analysis (time, receiver, transmitter, decision, base64_data, filepath)
    VALUES (%s, %s, %s, %s, %s,%s);"""
    print(type(encoded_string))

    data_tuple = (ts.strftime(timeFormat), signal.receiver, signal.transmitter_name,  d, encoded_string, f'{signal.file}')
    # Connect and write to PostgreSQL
    try:
        with psycopg2.connect(
                host="deep2.whoi.edu",
                port="5432",
                dbname="vhf_postgres",
                user="admin",  # Replace with your PostgreSQL username
                password="admin"  # Replace with your PostgreSQL password
        ) as conn:
            with conn.cursor() as cur:
                cur.execute(insert_sql, data_tuple)
                conn.commit()  # Make sure to commit the transaction
                print('Successfully written to PostgreSQL')
    except Exception as e:
        print(f"An error occurred: {e}")

    os.remove(f"../mp3s/{signal.file}.mp3")



def initialize_database(config_file_path):
    '''For grafana display to start displaying as programmed, it needs 2 data points for each receiver/transmitter.
    This function initializes the display by sending 2 test values to the databases.
    Need to have 1min interval between 2 runs in order to have a different timestamp, otherwise write over point if same timestamp
    
    [String] config_file_path: path to config file 
    '''
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
                send_info_to_webpage_parsed(date_time, transmitterName, receiverName, decision)

        print('Pausing for 1 minute, before sending next test run...')
        # Pause for 1 minute
        time.sleep(60)



def send_info_to_lora_gateway(signal):

    # Configure LORA

    # V3.0.x firmware
    import logging
    from random import randint
    from sys import exit
    from time import sleep
    from timeit import default_timer as timer
    from traceback import print_exc
    from datetime import datetime
    import os

    from rak811.rak811_v3 import Rak811, Rak811ResponseError

    # Get the current directory
    current_directory = os.getcwd()
    log_file_path = os.path.join(current_directory, f"lora_logfile.log")
    # Set up logging configuration
    logging.basicConfig(level=logging.INFO,
                        handlers=[logging.FileHandler(log_file_path),
                                  logging.StreamHandler()])

    lora = Rak811()
    # Perform a hard reset to ensure the module is in a known state
    lora.hard_reset()

    # Most of the setup should happen only once...
   # print("Setup")
    lora.set_config("lora:work_mode:0")  # LoRaWan mode
    lora.set_config("lora:class:0")  # Class: A:0, B:1, C:2
    lora.set_config("lora:join_mode:0")  # Select OTAA
    lora.set_config("lora:region:US915")  # Select region
    lora.set_config("lora:dr:0")  # Data rate/frequency
    lora.set_config("lora:tx_power:0")  # Power transmission
    lora.set_config("lora:adr:0")  # Adaptative data rate
    # Set keys
    lora.set_config("lora:app_eui:AC1F09FFF8680811")  # App_EUI
    lora.set_config("lora:app_key:AC1F09FFFE03DF10AC1F09FFF8680811")  # App_Key
    # lora.set_config=("lora:tx_power:0") #tx power
    # Print config
    # for line in lora.get_config("lora:status"):
    #     logging.info(f"    {line}")

    # Joining server
    print("Joining LORA Server")
    try:
        # Sending packet
        start_time = timer()
        sendtime = datetime.now().strftime("%H%M%S")
    # Messsage to send to gateway
        message=f"{111},{2222}"
    #     message = f"{signal.transmitter_name},{signal.score}"
    # Attempt to Join lora server
        lora.join()
        update_message=f"{sendtime} - Joined in {timer() - start_time:.2f} secs"
        logging.info(update_message)
        try:
            lora.send(message)
            update_message = f"{sendtime} - Packet sent in {timer() - start_time:.2f} secs"
            #  print(update_message)
            logging.info(update_message)
            logging.info(message)

        except Rak811ResponseError as e:
            error_message = f"{sendtime} - Failed to send packet to server: {e}"
            #print(error_message)
            logging.error(error_message)

    except Rak811ResponseError as e:
        error_message = f"{sendtime} - Failed to join LoRa server: {e}, trying again..."
        #print(error_message)
        logging.error(error_message)

