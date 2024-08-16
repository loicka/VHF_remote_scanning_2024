import serial
from serial import PARITY_NONE,EIGHTBITS,STOPBITS_ONE
import time


def set_and_check_frequency(ser,goal_frequency):
    from reset_biotrack import reset_biotrack
    import time
    # Check if frequency is within 148 and 152 Mhz
    if 148 <= float(goal_frequency) <= 152:

    # -------------------SET FREQUENCY---------------------------------------------------
        # Clean serial buffer (so previous command replies are not concatenated togeteher)
        ser.flushInput()
        ser.flushOutput()

        # Convert frequency to be written on receiver
        freq = 'sf' + goal_frequency + 'x'  # sf***.****x format
        freq_b = str.encode(freq)  # encode string into bytes

        attempt = 0

        while attempt <= 2:
            ser.write(freq_b)  # send to receiver to change the frequency
            print('Attempt to change Frequency to: ', goal_frequency)

            # PAUSE code to enable enough time between two commands
            time.sleep(2)

    # -------------------CHECK FREQUENCY--------------------------------------------
            #Clean serial buffer (so previous command replies are not concatenated togeteher)
            ser.flushInput()
            ser.flushOutput()

            #Check if goal frequency matches with tracker current frequency
            ser.write(b'qfx') # query tracker current frequency
            current_frequency=ser.readline().decode('utf-8') #decode bytes response into decimal

            if current_frequency==goal_frequency:
                print('Successful Frequency change!')
                check=1
                return check
                #attempt=4
            else:
                attempt=attempt+1
                print('ATTEMPT FAILED {}/3: Tracker frequency ({}) vs. Goal Frequency ({}) Incoherence'.format(attempt,current_frequency,goal_frequency))
                time.sleep(5)
                # Clean serial buffer (so previous command replies are not concatenated together)
                ser.flushInput()
                ser.flushOutput()
                if attempt >= 3:
                    reset_biotrack()
                    print('Cannot set proper frequency, restarting the machine and trying again...')
                    attempt = 0
    else: #given frequency isn't within 148-152Mhz
        check=0
        print('ERROR: Given FREQUENCY ({}) NOT IN RANGE (148-152 MHz)'.format(goal_frequency))
        print('Skipping to the next frequency...')
        return check






# #----------------------------------------------------------------------------------------------------------------
#
# #Set serial configuration + Open serial port
# ser = serial.Serial(port='/dev/ttyUSB0',baudrate=1200,bytesize=EIGHTBITS,parity=PARITY_NONE,stopbits=STOPBITS_ONE,
#                     timeout=5, xonxoff=False, rtscts=False, write_timeout=None, dsrdtr=False, inter_byte_timeout=None, exclusive=None)
#
# # Send commands to serial port
# # INPUT:
# frequency=150.6000
# frequency="{:.4f}".format(frequency)
#
# # 1 FUNCTION FOR SET + CHECK
# set_and_check_frequency(ser,frequency)
