
import serial
from serial import PARITY_NONE,EIGHTBITS,STOPBITS_ONE
import time


def set_and_check_gain(ser,goal_gain):
    import time
    
    from reset_biotrack import reset_biotrack
    # Check if frequency is within 148 and 152 Mhz
    if 0 <= float(goal_gain) <= 99:

        # -------------------SET GAIN---------------------------------------------------
        #Clean serial buffer (so previous command replies are not concatenated togeteher)
        ser.flushInput()
        ser.flushOutput()

        #Convert gain to be written on receiver
        gain_ascii = chr(goal_gain)         # convert string gain into ascii
        gain='sg'+gain_ascii+'x'              # sg#ASCIIx format
        gain_b=str.encode(gain)           # encode string into bytes

        attempt = 0

        while attempt <= 2:
            ser.write(gain_b)                 # send to receiver to change the gain
            print('Attempt to change Gain to:',goal_gain)

            # PAUSE code to enable enough time between two commands
            time.sleep(2)

    # -------------------CHECK GAIN--------------------------------------------
            # Clean serial buffer (so previous command replies are not concatenated togeteher)
            ser.flushInput()
            ser.flushOutput()

            # Check if goal gain matches with tracker current gain
            ser.write(b'qgx')  # query tracker current gain
            current_gain_ascii= ser.readline()  # receive query response in ascii format
            current_gain = ord(current_gain_ascii) #translates from ascii to decimal

            if current_gain == goal_gain:
                print('Successful Gain change!')
                check = 1
                return check
            else:
                attempt=attempt+1
                print('ATTEMPT FAILED {}/3: Tracker gain {} vs. Goal gain {} Incoherence'.format(attempt,current_gain, goal_gain))
                time.sleep(5)
                # Clean serial buffer (so previous command replies are not concatenated together)
                ser.flushInput()
                ser.flushOutput()
                if attempt>=3:
                    reset_biotrack()
                    print*('Cannot set proper gain, restarting the machine and trying again...')
                    attempt=0
                    
    else:  # given gain isn't within 0-99
        check = 0
        print('ERROR: Given GAIN ({}) NOT IN RANGE (0-99)'.format(goal_gain))
        print('Skipping to the next gain...')
        return check


#
# # #----------------------------------------------------------------------------------------------------------------
#
# #Set serial configuration + Open serial port
# ser = serial.Serial(port='/dev/ttyUSB0',baudrate=1200,bytesize=EIGHTBITS,parity=PARITY_NONE,stopbits=STOPBITS_ONE,
#                     timeout=10, xonxoff=False, rtscts=False, write_timeout=None, dsrdtr=False, inter_byte_timeout=None, exclusive=None)
#
# # Send commands to serial port
# # INPUT:
# gain=32
#
# # 1 FUNCTION FOR SET + CHECK
# set_and_check_gain(ser,gain)
