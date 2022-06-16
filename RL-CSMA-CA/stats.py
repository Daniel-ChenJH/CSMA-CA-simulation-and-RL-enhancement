import matplotlib.pyplot as plt
import numpy as np
from numpy import mean, std
from scipy import misc

import parameters

class Stats(object):
    def __init__(self,file):
        self.generatedPacketsTimes = {}     # packet id - timestamp of generation
        self.deliveredPacketsTimes = {}    # packet id - timestamp of delivery
        self.failedRetransmissionTimes = {} # packet id - timestamp of failed retransmission attempt
        self.retransmissionTimes = []   # timestamps of retransmissions
        self.filename=file
        self.rewards = []
        self.rewardstime = []

    def logGeneratedPacket(self, id, timestamp):
        self.generatedPacketsTimes[id] = timestamp


    def logDeliveredPacket(self, id, timestamp):
        self.deliveredPacketsTimes[id] = timestamp


    def logRetransmission(self,sender,timestamp):
        self.retransmissionTimes.append([sender,timestamp])
    
    def logfailedRetransmission(self, id, timestamp):
        self.failedRetransmissionTimes[id] = timestamp
        
    def logrewards(self, reward, time):
        self.rewards.append(reward)
        self.rewardstime.append(time)


    def printGeneratedPacketTimes(self):
        for generatedPacket in self.generatedPacketsTimes:
            print (self.generatedPacketsTimes[generatedPacket])


    def printDeliveredPacketTimes(self):
        for deliveredPacket in self.deliveredPacketsTimes:
            print (self.deliveredPacketsTimes[deliveredPacket])

    def plotfailedPacket(self):
        plt.figure()
        milliseconds = np.arange(0, int(parameters.SIM_TIME * 1e-6), 1)
        failedPacketEveryMillisecond = []
        for i in range(int(parameters.SIM_TIME * 1e-6)):
            failedPacketEveryMillisecond.append(0)
        for packet in self.failedRetransmissionTimes:
            failedPacketEveryMillisecond[int(self.failedRetransmissionTimes[packet]*1e-6)] += 1

        for i in range(len(failedPacketEveryMillisecond)-1):
            failedPacketEveryMillisecond[i+1] += failedPacketEveryMillisecond[i]
        plt.plot(milliseconds, failedPacketEveryMillisecond, 'r:', label='Failed Packets')

        plt.legend()
        plt.xlabel('Time (ms)')
        plt.ylabel('Failed Packets')
        plt.legend()
        file = self.filename+'/failed_packets_' + str(parameters.MAX_RETRANSMITION_TIME) + '.pdf'
        plt.savefig(file, bbox_inches='tight', dpi=250)
        print("Total number failed packets: {}".format((failedPacketEveryMillisecond[-1])))

        for j in range(parameters.NUMBER_OF_NODES):
            plt.figure()
            failedPacketEveryMillisecond = []
            for i in range(int(parameters.SIM_TIME * 1e-6)):
                failedPacketEveryMillisecond.append(0)
            for packet in self.failedRetransmissionTimes:
                if int(packet.split('_')[1].replace('Node','')) != j : continue
                failedPacketEveryMillisecond[int(self.failedRetransmissionTimes[packet]*1e-6)] += 1

            for i in range(len(failedPacketEveryMillisecond)-1):
                failedPacketEveryMillisecond[i+1] += failedPacketEveryMillisecond[i]
            plt.plot(milliseconds, failedPacketEveryMillisecond, 'r:', label='Failed Packets of Node '+str(j))

            plt.legend()
            plt.xlabel('Time (ms)')
            plt.ylabel('Failed Packets')
            plt.legend()
            file = self.filename+'/failed_packets_' + str(parameters.MAX_RETRANSMITION_TIME) + '_Node_'+str(j) + '.pdf'
            plt.savefig(file, bbox_inches='tight', dpi=250)


    def plotCumulativePackets(self):
        plt.figure()

        cumulativeGeneratedPackets = [1]
        generatedPacketsTimes = []
        i = 0
        for packet in self.generatedPacketsTimes:
            if i != 0:
                cumulativeGeneratedPackets.append(cumulativeGeneratedPackets[i-1] + 1)
            generatedPacketsTimes.append(self.generatedPacketsTimes[packet] * 1e-9)
            i += 1

        cumulativeDeliveredPackets = [1]
        deliveredPacketsTimes = []
        i = 0
        for packet in self.deliveredPacketsTimes:
            if i != 0:
                cumulativeDeliveredPackets.append(cumulativeDeliveredPackets[i-1] + 1)
            deliveredPacketsTimes.append(self.deliveredPacketsTimes[packet] * 1e-9)
            i += 1

        plt.plot(generatedPacketsTimes, cumulativeGeneratedPackets, 'r-', label='Generated')
        plt.plot(deliveredPacketsTimes, cumulativeDeliveredPackets, 'g:', label='Delivered')

        plt.legend()
        plt.xlabel('Time (s)')
        plt.ylabel('Packets')
        plt.legend()
        file = self.filename+'/packets' + str(parameters.TARGET_RATE) + '.pdf'
        plt.savefig(file, bbox_inches='tight', dpi=250)
        print("Total number of generated packets: {}".format(len(generatedPacketsTimes)))
        print("Total number of delivered packets: {}".format(len(deliveredPacketsTimes)))


        for j in range(parameters.NUMBER_OF_NODES):
            try:
                plt.figure()

                cumulativeGeneratedPackets = [1]
                generatedPacketsTimes = []
                i = 0
                for packet in self.generatedPacketsTimes:
                    if int(packet.split('_')[1].replace('Node',''))!=j:continue
                    if i != 0:
                        cumulativeGeneratedPackets.append(cumulativeGeneratedPackets[i-1] + 1)
                    generatedPacketsTimes.append(self.generatedPacketsTimes[packet] * 1e-9)
                    i += 1

                cumulativeDeliveredPackets = [1]
                deliveredPacketsTimes = []
                i = 0
                for packet in self.deliveredPacketsTimes:
                    if int(packet.split('_')[1].replace('Node',''))!=j:continue # 此节点发出的包中被接收的
                    if i != 0:
                        cumulativeDeliveredPackets.append(cumulativeDeliveredPackets[i-1] + 1)
                    deliveredPacketsTimes.append(self.deliveredPacketsTimes[packet] * 1e-9)
                    i += 1

                plt.plot(generatedPacketsTimes, cumulativeGeneratedPackets, 'r-', label='Generated')
                plt.plot(deliveredPacketsTimes, cumulativeDeliveredPackets, 'g:', label='Delivered')

                plt.legend()
                plt.xlabel('Time (s)')
                plt.ylabel('Packets of Node '+str(j))
                plt.legend()
                file = self.filename+'/packets' + str(parameters.TARGET_RATE) +'_Node_'+str(j) + '.pdf'
                plt.savefig(file, bbox_inches='tight', dpi=250)
            except:pass

    def plotThroughputMs(self):
        plt.figure()
        packetsGeneratedEveryMillisecond = []
        packetsDeliveredEveryMillisecond = []
        for i in range(int(parameters.SIM_TIME * 1e-6)):
            packetsGeneratedEveryMillisecond.append(0)
            packetsDeliveredEveryMillisecond.append(0)
    
        for packet in self.generatedPacketsTimes:
            packetsGeneratedEveryMillisecond[int(self.generatedPacketsTimes[packet] * 1e-6)] += 1
    
        for packet in self.deliveredPacketsTimes:
            packetsDeliveredEveryMillisecond[int(self.deliveredPacketsTimes[packet] * 1e-6)] += 1
    
        milliseconds = np.arange(0, int(parameters.SIM_TIME * 1e-6), 1)
    
        plt.plot(milliseconds, packetsGeneratedEveryMillisecond, 'r:', label='Generated')
        plt.plot(milliseconds, packetsDeliveredEveryMillisecond, 'g:', label='Delivered')
        plt.hlines(mean(packetsGeneratedEveryMillisecond), 0, milliseconds[-1], colors='black', label='Generated mean')
        plt.hlines(mean(packetsDeliveredEveryMillisecond), 0, milliseconds[-1], colors='yellow', label='Delivered mean')
    
        plt.legend()
        plt.xlabel('Time (ms)')
        plt.ylabel('Throughput (packets/ms)')
        plt.legend()
        file = self.filename+'/throughput' + str(parameters.TARGET_RATE) + '.pdf'
        plt.savefig(file, bbox_inches='tight', dpi=250)
        print("Average number of packets genetated every millisecond: {}".format(mean(packetsGeneratedEveryMillisecond)))
        print("Average number of packets delivered every millisecond: {}".format(mean(packetsDeliveredEveryMillisecond)))
        print("Standard deviation of packets genetated every millisecond: {}".format(std(packetsGeneratedEveryMillisecond)))
        print("Standard deviation of packets delivered every millisecond: {}".format(std(packetsDeliveredEveryMillisecond)))
        

    def plotThroughput(self):
        plt.figure()
        packetsGeneratedEverySecond = []
        packetsDeliveredEverySecond = []
        for i in range(int(parameters.SIM_TIME * 1e-9)):
            packetsGeneratedEverySecond.append(0)
            packetsDeliveredEverySecond.append(0)
    
        for packet in self.generatedPacketsTimes:
            packetsGeneratedEverySecond[int(self.generatedPacketsTimes[packet] * 1e-9)] += 1
    
        for packet in self.deliveredPacketsTimes:
            packetsDeliveredEverySecond[int(self.deliveredPacketsTimes[packet] * 1e-9)] += 1
    
        seconds = np.arange(0, int(parameters.SIM_TIME * 1e-9), 1)
    
        plt.plot(seconds, packetsGeneratedEverySecond, 'r:', label='Generated')
        plt.plot(seconds, packetsDeliveredEverySecond, 'g:', label='Delivered')
        plt.hlines(mean(packetsGeneratedEverySecond), 0, seconds[-1], colors='black', label='Generated mean')
        plt.hlines(mean(packetsDeliveredEverySecond), 0, seconds[-1], colors='yellow', label='Delivered mean')
    
        plt.legend()
        plt.xlabel('Time (s)')
        plt.ylabel('Throughput (packets/s)')
        plt.legend()
        file = self.filename+'/throughput' + str(parameters.TARGET_RATE) + '.pdf'
        plt.savefig(file, bbox_inches='tight', dpi=250)
        print("Average number of packets genetated every second: {}".format(mean(packetsGeneratedEverySecond)))
        print("Average number of packets delivered every second: {}".format(mean(packetsDeliveredEverySecond)))
        print("Standard deviation of packets genetated every second: {}".format(std(packetsGeneratedEverySecond)))
        print("Standard deviation of packets delivered every second: {}".format(std(packetsDeliveredEverySecond)))


    def plotDelays(self):
        plt.figure()
        delays = []
        deliveredPacketsTimes = []

        for packet in self.deliveredPacketsTimes:
            deliveredPacketsTimes.append(self.deliveredPacketsTimes[packet] * 1e-9)
            delays.append(self.deliveredPacketsTimes[packet] * 1e-6 - self.generatedPacketsTimes[packet] * 1e-6)

        plt.plot(deliveredPacketsTimes, delays, 'b:', label='Delays')
        plt.hlines(mean(delays), 0, deliveredPacketsTimes[-1], colors='red', label='Delays mean')

        plt.legend()
        plt.xlabel('Time (s)')
        plt.ylabel('Delay (ms)')
        plt.legend()
        file = self.filename+'/delays' + str(parameters.TARGET_RATE) + '.pdf'
        plt.savefig(file, bbox_inches='tight', dpi=250)
        print("Average delay: {}".format(mean(delays)))
        print("Standard deviation of delay: {}".format(std(delays)))
        print("Minimum delay: {}".format(min(delays)))
        print("Maximum delay: {}".format(max(delays)))
        
        
    def plotRewards(self):
        plt.figure()
        plt.plot(self.rewardstime, self.rewards, 'r:', label='reward')

        plt.legend()
        plt.xlabel('Time (s)')
        plt.ylabel('positive rewards')
        plt.legend()
        file = self.filename+'/rewards' + str(parameters.TARGET_RATE) + '.pdf'
        plt.savefig(file, bbox_inches='tight', dpi=250)


    def plotRetransmissions(self):
        plt.figure()
        retransmissionsEveryMillisecond = []
        for i in range(int(parameters.SIM_TIME * 1e-6)):
            retransmissionsEveryMillisecond.append(0)

        cumulative = 0
        for timestamp in self.retransmissionTimes:
            cumulative = cumulative + 1
            retransmissionsEveryMillisecond[int(timestamp[1] * 1e-6)] = cumulative

        for i in range(1, len(retransmissionsEveryMillisecond)):
            if retransmissionsEveryMillisecond[i] == 0:
                retransmissionsEveryMillisecond[i] = retransmissionsEveryMillisecond[i - 1]

        milliseconds = np.arange(0, int(parameters.SIM_TIME * 1e-6), 1)

        plt.plot(milliseconds, retransmissionsEveryMillisecond, 'r:', label='Retransmissions')

        plt.legend()
        plt.xlabel('Time (ms)')
        plt.ylabel('Retransmissions')
        plt.legend()
        file = self.filename+'/retransmissions' + str(parameters.TARGET_RATE) + '.pdf'
        plt.savefig(file, bbox_inches='tight', dpi=250)
        print("Total number of retransmissions: {}".format(cumulative))

        for j in range(parameters.NUMBER_OF_NODES):
            plt.figure()
            retransmissionsEveryMillisecond = []
            for i in range(int(parameters.SIM_TIME * 1e-6)):
                retransmissionsEveryMillisecond.append(0)

            cumulative = 0
            for timestamp in self.retransmissionTimes:
                if int(timestamp[0].replace('Node',''))!= j : continue
                cumulative = cumulative + 1
                retransmissionsEveryMillisecond[int(timestamp[1] * 1e-6)] = cumulative

            for i in range(1, len(retransmissionsEveryMillisecond)):
                if retransmissionsEveryMillisecond[i] == 0:
                    retransmissionsEveryMillisecond[i] = retransmissionsEveryMillisecond[i - 1]

            milliseconds = np.arange(0, int(parameters.SIM_TIME * 1e-6), 1)

            plt.plot(milliseconds, retransmissionsEveryMillisecond, 'r:', label='Retransmissions of Node '+str(j))

            plt.legend()
            plt.xlabel('Time (ms)')
            plt.ylabel('Retransmissions')
            plt.legend()
            file = self.filename+'/retransmissions' + str(parameters.TARGET_RATE)+'_Node_'+str(j) + '.pdf'
            plt.savefig(file, bbox_inches='tight', dpi=250)
