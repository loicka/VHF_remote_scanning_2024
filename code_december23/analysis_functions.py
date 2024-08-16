def amdemod(xx):
    ''' AMDEMOD Demodulate an amplitude modulated waveform
      using a simple scheme consisting of a rectifier
      followed by a leaky first-order hold scheme.
              dd = amdemod(xx,fc,fs,tau)
where
      xx = the input AM waveform to be demodulated
      fc = carrier frequency (not used)
      fs = sampling frequency (not used)
      tau = time constant of the RC circuit (OPTIONAL)
           (default value is tau=0.97)
      dd = demodulated message waveform'''
    import numpy as np
    import matplotlib.pyplot as plt

    tau = 0.97
    #-- Set up a vector for the demodulated waveform
    dd = np.zeros(xx.shape)
    dd[0] = xx[0]
    for j in np.arange(1,len(xx),1):            #- loop and hit each peak
        dd[j] = dd[j-1] * tau                   #- model resister leakage
        dd[j] = max(xx[j],dd[j])                #-  and  diode capacitor charging
    #plot
    plt.plot(dd)
    plt.ylabel("Amplitude")
    plt.xlabel("Time (s)")
    plt.title('Demodulated signal')
    plt.grid()
    plt.show()

    return dd

def peak_analysis(data,samplerate):
    from scipy.signal import find_peaks, medfilt
    import matplotlib.pyplot as plt
    import numpy as np
    hitsExpected=7
    # Extract peak info
    data=abs(medfilt(data,kernel_size=11)) #taking the absolute of a median filtered raw signal
    peaks, properties = find_peaks(data, height=0, threshold=None, distance=samplerate, prominence=0.7, width=None,
                                   wlen=None, rel_height=0.7, plateau_size=None)
    number_peaks = len(peaks)
    #print('npeaks',number_peaks)
    #print('peaks',peaks)
    if number_peaks>2:
        meanPulseLength = np.mean(np.diff(peaks / samplerate))
        stdPulseLength = np.std(np.diff(peaks / samplerate))

    else:
        meanPulseLength =0
        stdPulseLength = 0
    peak_heights = properties['peak_heights']
    prominences = properties['prominences']
    score=number_peaks/hitsExpected
    #print('score', score)
    
    #plt.plot(data)
    #plt.plot(peaks,peak_heights,marker='*')
    #plt.ylabel("Amplitude")
    #plt.xlabel("Time (s)")
    #plt.grid()
    #plt.show(block=True)
    
    
    
    return peaks,number_peaks,peak_heights,prominences,meanPulseLength,stdPulseLength,score

def send_info_to_webpage(meanPulseLength,number_peaks,score,stdPulseLength,samplerate,duration_signal,date_time,transmitterName):
    from influxdb import InfluxDBClient
    from datetime import datetime
    import numpy as np

    # READ & EXTRACT CONFIG FILE INFO
    import yaml
    from yaml import CLoader as Loader, CDumper as Dumper
    with open("config.yaml") as fh:
        config = yaml.load(fh, Loader=Loader)

    for t in np.arange(0,len(config)):
        if config['transmitters'][t]['name']==transmitterName:
            pulse=config['transmitters'][t]['pulse']
            break
        #else:
        #    print('pulse missing', transmitterName)
        #    pulse=0.0 
            
    ts = datetime.strptime(date_time, '%Y%m%d_%H%M%S')

    receiverName=config['receivers'][0]['name'] #extract receiver name
    timeFormat = "%Y-%m-%dT%H:%M:%S.%fZ"

    point = {
        "measurement": "run_acc",
        "time": ts.strftime(timeFormat),
        "tags": {
            "receiver": receiverName,
            "transmitter": transmitterName,
        },
        "fields": {
            "meanPulseLength": float(meanPulseLength),
            "nHits": int(number_peaks),
            "hitsExpected": int(7),
            "score": float(score),
            "stdPulseLength": float(stdPulseLength),
            "targetPulseLength": float(pulse),
            "inputLength": float(duration_signal), #secs
            "inputSampleRate": float(samplerate),
        }
    }
    #print(point)
  #  print(ts.strftime(timeFormat))
    client = InfluxDBClient(host="spot-nm2.awi-neumayer.de", port=8086, database="vhf")
    res=client.write_points([point])
    print('Successfully written on database')

