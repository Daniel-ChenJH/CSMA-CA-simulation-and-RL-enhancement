import simpy
import random

import phy
import macPacket
import parameters
import stats

class Mac(object):
    def __init__(self, node):
        self.node = node
        self.env = self.node.env
        self.name = self.node.name
        self.ether = self.node.ether
        self.latitude = self.node.latitude
        self.longitude = self.node.longitude
        self.stats = self.node.stats
        self.phy = phy.Phy(self)
        self.pendingPackets = {}    # associate packets I'm trying to transmit and timeouts for retransmissions
        self.retransmissionCounter = {}     # associate packets I'm trying to transmit and transmission attempts
        self.isSensing = False
        self.packetsToSend = []
        self.sensing = None  # keep sensing process

    def send(self, destination, payloadLength, id):
        length = payloadLength + parameters.MAC_HEADER_LENGTH
        macPkt = macPacket.MacPacket(self.name, destination, length, id, False)
        self.stats.logGeneratedPacket(id, self.env.now)
        self.retransmissionCounter[macPkt.id] = 0

        # sensing phase
        if self.phy.isSending:   # I cannot sense while sending
            yield self.phy.transmission   # wait for my phy to finish sending other packets

        if self.isSensing: # I'm sensing for another packet, I wait
            yield self.sensing

        self.sensing = self.env.process(self.waitIdleAndSend(macPkt))
        yield self.sensing


    def handleReceivedPacket(self, macPkt):
        # 成功收到信息
        if macPkt.destination == self.name and not macPkt.ack:  # send ack to normal packets
            if parameters.PRINT_LOGS:
                print('Time %d: %s MAC receives packet %s from %s and sends ACK' % (self.env.now, self.name, macPkt.id, macPkt.source))
            self.node.receive(macPkt.id, macPkt.source)
            self.stats.logDeliveredPacket(macPkt.id, self.env.now)
            ack = macPacket.MacPacket(self.name, macPkt.source, parameters.ACK_LENGTH, macPkt.id, True)
            yield self.env.timeout(parameters.SIFS_DURATION)
            self.phy.send(ack)
        elif macPkt.destination == self.name:
            if parameters.PRINT_LOGS:
                print('Time %d: %s MAC receives ACK %s from %s' % (self.env.now, self.name, macPkt.id, macPkt.source))
            if macPkt.id in self.pendingPackets:    # packet could not be in pendingPackets if timeout has expired but ack still arrive
                self.pendingPackets[macPkt.id].interrupt()


    def waitAck(self, macPkt): # 重传
        try:
            yield self.env.timeout(parameters.ACK_TIMEOUT)  
            # timeout expired, resend
            if macPkt.retransmitiontimes > parameters.MAX_RETRANSMITION_TIME:
                if parameters.PRINT_LOGS:
                    self.stats.logfailedRetransmission(macPkt.id,self.env.now)
                    print('Time %d: %s %s transmit to %s fails finally' % (self.env.now, self.name, macPkt.id, macPkt.destination))
            else:    
                macPkt.retransmitiontimes += 1
                if parameters.PRINT_LOGS:
                    print('Time %d: %s %s transmit timeout without ACK from %s' % (self.env.now, self.name, macPkt.id, macPkt.destination))
                    print('Time %d: %s MAC retransmit %s to %s' % (self.env.now, self.name, macPkt.id, macPkt.destination))
                self.pendingPackets.pop(macPkt.id)
                self.retransmissionCounter[macPkt.id] += 1

                # sensing phase
                if self.phy.isSending:   # I cannot sense while sending
                    yield self.phy.transmission   # wait for my phy to finish sending other packets
                if self.isSensing: # I'm sensing for another packet, I wait
                    yield self.sensing

                self.stats.logRetransmission(self.name,self.env.now)
                self.sensing = self.env.process(self.waitIdleAndSend(macPkt))
        except simpy.Interrupt:
            # ack received
            self.pendingPackets.pop(macPkt.id)
            self.retransmissionCounter.pop(macPkt.id)


    def waitIdleAndSend(self, macPkt): 
        # 闲置等待并发送
        self.isSensing = True
        timeout = parameters.DIFS_DURATION
        backoff = 0
        if self.retransmissionCounter[macPkt.id] != 0:  # add backoff in case of retransmission
            backoff = random.randint(0, min(pow(2,self.retransmissionCounter[macPkt.id]-1)*parameters.CW_MIN, parameters.CW_MAX)-1) * parameters.SLOT_DURATION
            timeout += backoff
        while True:
            try:
                while timeout > 0:
                    yield self.env.timeout(1)
                    timeout -= 1

                    # sensing phase
                    if self.phy.isSending:   # I cannot sense while sending
                        yield self.phy.transmission   # wait for my phy to finish sending other packets 
                        timeout = parameters.DIFS_DURATION + backoff    # if a trasmission occours during the sensing I restart the sensing phase from scratch

                self.phy.send(macPkt)
                self.pendingPackets[macPkt.id] = self.env.process(self.waitAck(macPkt))
                self.isSensing = False
                return
            except simpy.Interrupt:
                if backoff == 0:    # need to add backoff, even if this is not a retransmission
                    backoff = random.randint(0, parameters.CW_MIN-1) * parameters.SLOT_DURATION
                    timeout = parameters.DIFS_DURATION + backoff
                elif timeout > backoff: # backoff has not been consumed, new timeout is DIFS + backoff
                    timeout = parameters.DIFS_DURATION + backoff
                else:   # backoff has been partially consumed, new timeout is DIFS + remaining backoff
                    backoff = timeout
                    timeout = parameters.DIFS_DURATION + backoff
                continue
