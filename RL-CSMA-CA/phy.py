import simpy

import phyPacket
import parameters

class Phy(object):
    def __init__(self, mac):
        self.mac = mac
        self.env = self.mac.env
        self.name = self.mac.name
        self.ether = self.mac.ether
        self.latitude = self.mac.latitude
        self.longitude = self.mac.longitude
        self.listen = self.env.process(self.listen())
        self.receivingPackets = []
        self.isSending = False  # keep radio state (Tx/Rx)
        self.transmission = None    # keep the transmitting process


    def send(self, macPkt):
        if not self.isSending:  # I do not send if I'm already sending
            self.listen.interrupt(macPkt)


    def encapsulateAndTransmit(self, macPkt):   # 封装和传输
        self.receivingPackets.clear() # I switch to transmitting mode, so I drop all ongoing receptions
        yield self.env.timeout(parameters.RADIO_SWITCHING_TIME) # simulate time of radio switching
        self.ether.removeInChannel(self.inChannel, self)
        yield self.env.timeout(parameters.RADIO_SWITCHING_TIME) # simulate time of radio switching
        if parameters.PRINT_LOGS:
            print('Time %d: %s stops listening' % (self.env.now, self.name))
        phyPkt = phyPacket.PhyPacket(parameters.TRANSMITTING_POWER, False, macPkt) # start of packet

        # if not macPkt.ack:
        #     if parameters.PRINT_LOGS:
        #         print('Time %d: %s sends RTS signal to %s' % (self.env.now, self.name, phyPkt.macPkt.id.split('_')[-1]))
        #     yield self.env.timeout(parameters.RADIO_SWITCHING_TIME) # simulate time of radio switching
        #     if parameters.PRINT_LOGS:
        #         print('Time %d: %s receives CTS signal from %s' % (self.env.now, self.name, phyPkt.macPkt.id.split('_')[-1]))

        if macPkt.ack:
            if parameters.PRINT_LOGS:
                print('Time %d: %s PHY starts transmission of %s ACK' % (self.env.now, self.name, phyPkt.macPkt.id))
        else:
            if parameters.PRINT_LOGS:
                print('Time %d: %s PHY starts transmission of %s' % (self.env.now, self.name, phyPkt.macPkt.id))
        self.ether.transmit(phyPkt, self.latitude, self.longitude, True, False) # beginOfPacket=True, endOfPacket=False

        duration = macPkt.length * parameters.BIT_TRANSMISSION_TIME + parameters.PHY_HEADER_LENGTH

        while True:
            if duration < parameters.SLOT_DURATION:
                yield self.env.timeout(duration)    # wait only remaining time
                break
            yield self.env.timeout(parameters.SLOT_DURATION) # send a signal every slot
            self.ether.transmit(phyPkt, self.latitude, self.longitude, False, False)  # beginOfPacket=False, endOfPacket=False
            duration -= parameters.SLOT_DURATION

        self.ether.transmit(phyPkt, self.latitude, self.longitude, False, True)  # beginOfPacket=False, endOfPacket=True
        if macPkt.ack:
            if parameters.PRINT_LOGS:
                print('Time %d: %s PHY ends transmission of %s ACK' % (self.env.now, self.name, phyPkt.macPkt.id))
        else:
            if parameters.PRINT_LOGS:
                print('Time %d: %s PHY ends transmission of %s' % (self.env.now, self.name, phyPkt.macPkt.id))

        self.inChannel = self.ether.getInChannel(self)
        yield self.env.timeout(parameters.RADIO_SWITCHING_TIME) # simulate time of radio switching
        if parameters.PRINT_LOGS:
            print('Time %d: %s starts listening' % (self.env.now, self.name))


    def listen(self):
        self.inChannel = self.ether.getInChannel(self)
        yield self.env.timeout(parameters.RADIO_SWITCHING_TIME) # simulate time of radio switching
        if parameters.PRINT_LOGS:
            print('Time %d: %s starts listening' % (self.env.now, self.name))

        while True:
            try:
                (phyPkt, beginOfPacket, endOfPacket) = yield self.inChannel.get()

                # the signal just received will interfere with other signals I'm receiving (and vice versa)
                for receivingPkt in self.receivingPackets:
                    if receivingPkt != phyPkt:
                        receivingPkt.interferingSignals[phyPkt.macPkt.id] = phyPkt.power
                        phyPkt.interferingSignals[receivingPkt.macPkt.id] = receivingPkt.power

                #print('Time %d: %s receives signal %s from %s with power %.15f' % (self.env.now, self.name, phyPkt.macPkt.id, phyPkt.macPkt.source, phyPkt.power))

                if self.mac.isSensing:  # interrupt mac if it is sensing for idle channel
                    self.mac.sensing.interrupt()

                if phyPkt.power > parameters.RADIO_SENSITIVITY: # decodable signal
                    if beginOfPacket:  # begin of packet
                        self.receivingPackets.append(phyPkt)
                    elif endOfPacket:   # end of packet
                        if phyPkt in self.receivingPackets: # in consider is only if I received the begin of the packet, otherwise I ignore it, as it is for sure corrupted
                            self.receivingPackets.remove(phyPkt)
                            if not phyPkt.corrupted:
                                sinr = self.computeSinr(phyPkt)
                                if sinr > 10:    # signal greater than noise and inteference
                                    self.env.process(self.mac.handleReceivedPacket(phyPkt.macPkt))

            except simpy.Interrupt as macPkt:        # listening can be interrupted by a message sending
                self.isSending = True
                self.transmission = self.env.process(self.encapsulateAndTransmit(macPkt.cause))
                yield self.transmission
                self.isSending = False


    def computeSinr(self, phyPkt):
        interference = 0
        for interferingSignal in phyPkt.interferingSignals:
            interference += float(phyPkt.interferingSignals[interferingSignal])
        return phyPkt.power/(interference + parameters.NOISE_FLOOR)
