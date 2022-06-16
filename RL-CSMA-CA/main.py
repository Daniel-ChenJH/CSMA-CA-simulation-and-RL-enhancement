import simpy
import random

import node
import phy
import ether
import parameters
import stats
import os
import sys
import datetime

class Logger(object):
    # CJH 2022/5/11
    def __init__(self, fileN=''):
        os.mkdir(fileN)
        fileN = os.path.join(fileN,"simulation.log" )
        self.terminal = sys.stdout
        self.log = open(fileN, "a+",encoding='utf-8')
 
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.flush() #每次写入后刷新到文件中，防止程序意外结束
    def flush(self):
        self.log.flush()


def main():
    # CJH 2022/5/11    

    file='results_'+datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    sys.stdout = Logger(file)
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"-sim.log\n\n"+parameters.s+'\nLog starting\n------------------------\n')
    # CJH 2022/5/11

    # 创建仿真环境
    env = simpy.Environment()
    eth = ether.Ether(env)
    statistics = stats.Stats(file)

    nodes = []

    for i in range(0, parameters.NUMBER_OF_NODES):
        name = "Node" + str(i)
        nodes.append(node.Node(env, name, eth, random.randint(0,40), random.randint(0,40), statistics))

    for i in range(0, parameters.NUMBER_OF_NODES):
        destinations = []
        for j in range(0, parameters.NUMBER_OF_NODES):
            if i != j:
                destinations.append(nodes[j].name)
        # 设定节点事件
        env.process(nodes[i].keepSendingIncreasing(parameters.STARTING_RATE, parameters.TARGET_RATE, destinations))
        #env.process(nodes[i].keepSending(parameters.TARGET_RATE, destinations))

    if not parameters.PRINT_LOGS:
        env.process(printProgress(env))

    # 开始运行
    env.run(until=parameters.SIM_TIME)

    #作图
    statistics.plotCumulativePackets()
    # statistics.plotThroughput()
    statistics.plotDelays()
    statistics.plotRetransmissions()
    statistics.plotfailedPacket()
    statistics.plotRewards()


def printProgress(env):
    while True:
        print('Progress: %d / %d' % (env.now * 1e-9, parameters.SIM_TIME * 1e-9))
        yield env.timeout(1e9)


if __name__ == '__main__':
    main()
