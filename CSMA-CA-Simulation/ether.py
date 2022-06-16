import simpy
import math
from scipy.constants import c, pi
import random

import parameters

class Ether(object):
    def __init__(self, env, capacity=simpy.core.Infinity):
        self.env = env
        self.capacity = capacity
        self.channels = []
        self.listeningNodes = []


    def computeDistance(self, senderLatitude, senderLongitude, receiverLatitude, receiverLongitude):
        return math.sqrt(pow(senderLatitude - receiverLatitude, 2) + pow(senderLongitude - receiverLongitude, 2))


    def latencyAndAttenuation(self, phyPkt, sourceLatitude, sourceLongitude, destinationChannel, destinationNode, beginOfPacket, endOfPacket):
        # 延迟和衰减
        distance = self.computeDistance(sourceLatitude, sourceLongitude, destinationNode.latitude, destinationNode.longitude) + 1e-3 # add 1mm to avoid distance=0
        delay = round((distance / c) * pow(10, 9), 0)
        yield self.env.timeout(delay)
        receivingPower = parameters.TRANSMITTING_POWER * pow(parameters.WAVELENGTH/(4 * pi * distance), 2) # NB. used FSPL propagation model with isotropic antennas
        phyPkt.power = receivingPower

        if endOfPacket:
            if random.randint(0,100) < parameters.PACKET_LOSS_RATE * 100:
                phyPkt.corrupted = True

        return destinationChannel.put((phyPkt, beginOfPacket, endOfPacket))


    def transmit(self, phyPkt, sourceLatitude, sourceLongitude, beginOfPacket, endOfPacket):
        events = [self.env.process(self.latencyAndAttenuation(phyPkt, sourceLatitude, sourceLongitude, destinationChannel, destinationNode, beginOfPacket, endOfPacket)) for destinationChannel, destinationNode in zip(self.channels, self.listeningNodes)]
        return self.env.all_of(events)


    def getInChannel(self, node):
        channel = simpy.Store(self.env, capacity=self.capacity)
        self.channels.append(channel)
        self.listeningNodes.append(node)
        return channel


    def removeInChannel(self, inChannel, node):
        self.channels.remove(inChannel)
        self.listeningNodes.remove(node)

