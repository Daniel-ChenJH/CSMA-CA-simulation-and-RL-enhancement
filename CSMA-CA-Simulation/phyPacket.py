class PhyPacket(object):
    def __init__(self, power, corrupted, macPkt):
        self.power = power
        self.corrupted = corrupted
        self.macPkt = macPkt
        self.interferingSignals = {}
