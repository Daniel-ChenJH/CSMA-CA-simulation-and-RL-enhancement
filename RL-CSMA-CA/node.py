import simpy
import random

import mac
import parameters

class Node(object):
    def __init__(self, env, name, ether, latitude, longitude, stats):
        self.env = env
        self.name = name
        self.ether = ether
        self.latitude = latitude
        self.longitude = longitude
        self.stats = stats
        self.mac = mac.Mac(self)
        print('%s created with coordinates %d %d' % (self.name, self.latitude, self.longitude))


    def send(self, destination, length, id):
        if self.name == "Node 2":
            yield self.env.timeout(2000)
        if parameters.PRINT_LOGS:
            print('Time %d: %s sends %s to %s' % (self.env.now, self.name, id, destination))
        yield self.env.process(self.mac.send(destination, length, id, self.env.now))


    def receive(self, id, source):
        if parameters.PRINT_LOGS:
            print('Time %d: %s receives %s from %s' % (self.env.now, self.name, id, source))


    def keepSending(self, rate, destinationNodes):
        while True:
            yield self.env.timeout(round(random.expovariate(rate) * 1e9))  # inter-messages time is a poisson process
            # NB: inter-message time start after mac has served previous message, to make sure that mac does not handle multiple messages concurrently

            destination = destinationNodes[random.randint(0, len(destinationNodes)-1)]
            length = random.randint(0, parameters.MAX_MAC_PAYLOAD_LENGTH)
            id = str(self.env.now) + '_' + self.name + '_' + destination
            if parameters.PRINT_LOGS:
                print('Time %d: %s sends %s to %s' % (self.env.now, self.name, id, destination))
            yield self.env.process(self.mac.send(destination, length, id))


    def keepSendingIncreasing(self, startingRate, finalRate, destinationNodes):
        rate = startingRate
        increasingSpeed = (finalRate - startingRate) / parameters.SIM_TIME
        while True:
            yield self.env.timeout(round(random.expovariate(startingRate + increasingSpeed * self.env.now) * 1e9))  # inter-messages time is a poisson process

            destination = destinationNodes[random.randint(0, len(destinationNodes)-1)]
            length = random.randint(0, parameters.MAX_MAC_PAYLOAD_LENGTH)       # PAYLOAD_LENGTH
            id = str(self.env.now) + '_' + self.name + '_' + destination
            if parameters.PRINT_LOGS:
                print('Time %d: %s sends %s to %s' % (self.env.now, self.name, id, destination))
            yield self.env.process(self.mac.send(destination, length, id, self.env.now))
