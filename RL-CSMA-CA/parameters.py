from scipy.constants import c
# c为光速

# NB: sim time are nanoseconds, distances are in meters, powers in watt

# 802.11g parameters. 802.11g is the last standard not adopting MIMO. MIMO boost bitrate
# using concurrent transmissions and other techniques. Values from wikipedia
# https://en.wikipedia.org/wiki/IEEE_802.11
# https://en.wikipedia.org/wiki/DCF_Interframe_Space
# https://en.wikipedia.org/wiki/Short_Interframe_Space
# Freq: 2.4 GHz, OFDM, 20 MHz bandwidth, 54 Mbit/s

### SIMULATION PARAMETERS
SIM_TIME = 100*1e9

PRINT_LOGS = True
NUMBER_OF_NODES = 4
STARTING_RATE = 5
TARGET_RATE = 5

### RADIO PARAMETERS
TRANSMITTING_POWER = 0.1 # Watt, legal limit in EU for EIRP
RADIO_SWITCHING_TIME = 100
RADIO_SENSITIVITY = 1e-10 # power under which signal is not sensed


### SIGNAL PARAMETERS
FREQUENCY = 2400000000 # 2.4 GHz
WAVELENGTH = c/FREQUENCY

### PHY PARAMETERS
BITRATE = 54000000 # 54 Mbit/s, 802.11g 20 MHz channels
BIT_TRANSMISSION_TIME = 1/BITRATE * 1e9
NOISE_FLOOR = 1e-9
PHY_HEADER_LENGTH = 128
PACKET_LOSS_RATE = 0.01 # 1% of packets are corrupted
 
### MAC PARAMETERS
SLOT_DURATION = 20000 # 20 microseconds, 802.11g 2.4 GHz
SIFS_DURATION = 10000 # 10 microseconds, 802.11g 2.4 GHz
DIFS_DURATION = SIFS_DURATION + (2 * SLOT_DURATION)
MAC_HEADER_LENGTH = 34*8 # 34 byte fixed fields of a mac packet
MAX_MAC_PAYLOAD_LENGTH = 2312*8
ACK_LENGTH = MAC_HEADER_LENGTH
CW_MIN = 16
CW_MAX = 1024
MAX_RETRANSMITION_TIME = 5
# ack timeout = transmission time of biggest possible pkt + rtt for 300m distance + sifs + ack transmission time
ACK_TIMEOUT = (MAX_MAC_PAYLOAD_LENGTH + MAC_HEADER_LENGTH + PHY_HEADER_LENGTH) * BIT_TRANSMISSION_TIME + 2 * round((300 / c) * pow(10, 9), 0) + SIFS_DURATION + ACK_LENGTH * BIT_TRANSMISSION_TIME
# RL
action_space = ['0','1','2','4','8','16','32','64','128','256']#,'512']
learning_rate = 0.01
reward_decay = 0.9
e_greedy = 0.9
REWARD_of_ackfailing = -5
REWARD_of_transmissionfailing = -20

# CJH 2022/5/11
def get_attrs(li):
    attrs = []
    s='Parameters of this simulation:\n*****\n\n'
    for attr in li:
        if attr.isupper():
            attrs.append(attr)
    for attr in attrs:
        s+=attr+' = '+str(eval(attr))+'\n'
    return attrs,s+'*****\n'

attrs,s=get_attrs(dir())
# CJH 2022/5/11