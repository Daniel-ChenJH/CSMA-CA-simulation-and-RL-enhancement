class MacPacket(object):
    def __init__(self, source, destination, length, id, ack):
        self.source = source
        self.destination = destination
        self.length = length    # in bit
        self.id = id
        self.ack = ack  # bool
        self.retransmitiontimes = 1  # 初始传输第一次可以看做重传
