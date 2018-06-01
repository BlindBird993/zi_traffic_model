from mesa import Agent, Model
import random
import numpy as np

class RoadInterface(Agent):
    def __init__(self,unique_id, model):
        super().__init__(unique_id, model)

        self.buyers = []
        self.sellers = []
        self.waitCars = []

        self.timestep = 0
        self.timebin = []

        self.demands = []
        self.productions = []
        self.demandPrice = []
        self.supplyPrice = []

        self.historyDemands = []
        self.historyProductions = []

        self.testListOfWaitingCars = []
        self.listOfTotalDistribution = []

        self.gateDistribution = []
        self.bar1Distribution = []
        self.bar2Distribution = []

        self.distributedDemands = []
        self.summedDemands = []

        self.buyerPriceList = []
        self.clearPriceList = []
        self.satisfiedDemands = []

        self.demandCount = 0
        self.dealCount = 0
        self.noDealCount = 0

        self.dealsList = []
        self.noDealsList = []

        self.amountOfCars = []
        self.amountOfFerries = []
        self.amountOfEmergensies = []
        self.totalCarAmounts = []

        self.buyerPrices = []
        self.sellerPrices = []

        self.pricesListCar = []
        self.pricesListlorry = []

        self.commonPrice = 0
        self.clearPrice = 0

        self.currentSeller = 0
        self.currentBuyer = 0

        self.numberOfBuyers = 0
        self.numberOfSellers = 0
        self.numberOfWaitingCars = 0

        self.waitList = []

        self.hour = 0
        self.day = 0
        self.week = 0
        self.price = 0

    def getCarTypes(self):
        car_count = 0
        lorry_count = 0
        emergency_count = 0
        for agent in self.model.schedule.agents:
            if (isinstance(agent, CarAgent) and agent.readyToBuy is True):
                if agent.type == 'car':
                    car_count += 1
                elif agent.type == 'lorry':
                    lorry_count += 1
                elif agent.type == 'emergency':
                    emergency_count += 1
                self.totalCarAmounts.append(agent.type)
        self.amountOfCars.append(car_count)
        self.amountOfFerries.append(lorry_count)
        self.amountOfEmergensies.append(emergency_count)

    def getWaitingCars(self):
        self.numberOfWaitingCars = 0
        self.waitCars = []
        for agent in self.model.schedule.agents:
            if (isinstance(agent, CarAgent) and agent.isWaiting):
                print("Agent {} status {}".format(agent.unique_id,agent.isWaiting))
                self.numberOfWaitingCars += 1
                self.waitCars.append(agent.unique_id)
        self.testListOfWaitingCars.append(self.numberOfWaitingCars)
        print("List of Cars Waited {}".format(self.waitCars))
        print("Number of Cars Waited {}".format(self.numberOfWaitingCars))

    def getSellers(self):
        self.numberOfSellers = 0
        self.sellers = []
        for agent in self.model.schedule.agents:
            if (isinstance(agent, GateAgent) or isinstance(agent,BarAgent)):
                print("Agent {} ready to Sell {}".format(agent.unique_id,agent.readyToSell))
                if agent.readyToSell is True:
                    self.numberOfSellers += 1
                    self.sellers.append(agent.unique_id)
        print("List of sellers {}".format(self.sellers))
        print("Number of sellers {}".format(self.numberOfSellers))

    def getAvailableCapacity(self):
        capacityValue = 0
        for agent in self.model.schedule.agents:
            if (isinstance(agent, GateAgent) or isinstance(agent, BarAgent)):
                if agent.readyToSell is True:
                    capacityValue += agent.maxCapacity
        self.historyProductions.append(capacityValue)
        return capacityValue

    def getBuyres(self):
        self.numberOfBuyers = 0
        self.buyers = []
        for agent in self.model.schedule.agents:
            if (isinstance(agent, CarAgent)):
                if agent.readyToBuy is True:
                    self.numberOfBuyers += 1
                    self.buyers.append(agent.unique_id)
        self.historyDemands.append(self.numberOfBuyers)
        print("List of buyers {}".format(self.buyers))
        print("Number of buyers {}".format(self.numberOfBuyers))


    def updatePrice(self, new_price,buyer_type):
        for agent in self.model.schedule.agents:
            if (isinstance(agent, BarAgent) or isinstance(agent,GateAgent)):
                if agent.open is True:
                    if buyer_type == 'car':
                        agent.price = new_price
                    elif buyer_type == 'lorry':
                        agent.pricelorry = new_price

    def chooseSeller(self, buyer, price, amount=None):
        if len(self.sellers) > 0:
            seller = np.random.choice(self.sellers)
        for agent in self.model.schedule.agents:
            if (isinstance(agent, BarAgent) or isinstance(agent,GateAgent)):
                if agent.readyToSell is True and agent.unique_id == seller:
                    seller_price = 0
                    if buyer.type == 'car':
                        seller_price = agent.price
                    elif buyer.type == 'lorry':
                        seller_price = agent.pricelorry
                    elif buyer.type == 'emergency':
                        seller_price = 0

                    print("Seller {}".format(agent.unique_id))
                    print("Seller price {}".format(seller_price))

                    if buyer.price >= seller_price:
                        print("Deal !")
                        self.dealCount += 1
                        agent.queue.append(buyer.unique_id)
                        agent.density += 1
                        agent.maxCapacity -= 1
                        print("Agent density {}".format(agent.density))
                        print("Agent capacity {}".format(agent.maxCapacity))

                        buyer.readyToBuy = False
                        buyer.isWaiting = False
                        buyer.waitingTime = 0
                        print("Buyer {} Waiting {}".format(buyer.unique_id,buyer.isWaiting))
                        self.buyers.remove(buyer.unique_id)

                        if agent.maxCapacity <= 0:
                            agent.readyToSell = False
                            self.numberOfSellers -= 1
                            self.sellers.remove(agent.unique_id)

                        if (isinstance(agent, BarAgent) and agent.open is False):
                            agent.checkMainGate()
                            agent.checkIfOpen(agent.mainGatedensity, agent.mainGateCapacity)

                        if buyer.type != 'emergency':
                            new_price = round(np.mean([seller_price, buyer.price]), 1)
                            if buyer.type == 'car':
                                agent.price = new_price
                            elif buyer.type == 'lorry':
                                agent.pricelorry = new_price

                        self.pricesListCar.append(agent.price)
                        self.pricesListlorry.append(agent.pricelorry)

                        self.numberOfBuyers -= 1
                        if self.numberOfWaitingCars > 0:
                            self.numberOfWaitingCars -= 1
                        self.demandCount += 1

                        print("Number of sellers {}".format(self.numberOfSellers))
                        print("Number of buyers {}".format(self.numberOfBuyers))
                        print("Number of waiting cars {}".format(self.numberOfWaitingCars))
                    else:
                        print('No deal')
                        self.noDealCount += 1
                        seller_price = 0
                        if buyer.type == 'car':
                            seller_price = agent.price
                            agent.price = round(np.mean([seller_price, buyer.price]), 1)
                        elif buyer.type == 'lorry':
                            seller_price = agent.pricelorry
                            agent.pricelorry = round(np.mean([seller_price, buyer.price]), 1)
                        elif buyer.type == 'emergency':
                            seller_price = 0
                        buyer.calculatePrice()

    def getRoadCarsDistribution(self):
        sellerDistributionList = []
        for agent in self.model.schedule.agents:
            if (isinstance(agent, GateAgent) or isinstance(agent,BarAgent)):
                if agent.unique_id == 'Gate 0':
                    self.gateDistribution.append(len(agent.queue))
                elif agent.unique_id == 'Bar 0':
                    self.bar1Distribution.append(len(agent.queue))
                elif agent.unique_id == 'Bar 1':
                    self.bar2Distribution.append(len(agent.queue))
        return self.gateDistribution,self.bar1Distribution,self.bar2Distribution

    def distributeCars(self):

        self.getAvailableCapacity()

        self.sellPrice = 0
        self.buyPrice = 0
        self.demandCount = 0
        self.dealCount = 0
        self.noDealCount = 0
        print("Available sellers {}".format(self.sellers))
        if self.numberOfWaitingCars > 0:
            while (not (self.numberOfSellers <= 0 or self.numberOfWaitingCars <= 0)):
                for agent in self.model.schedule.agents:
                    if (isinstance(agent, CarAgent) and agent.isWaiting is True):
                        self.buyPrice = agent.price
                        print("Buyer {} Type {}".format(agent.unique_id, agent.type))
                        print("Buy price {}".format(agent.price))
                        self.chooseSeller(agent, self.buyPrice)

        while (not (self.numberOfSellers <= 0 or self.numberOfBuyers <= 0)):
            buyer_id = np.random.choice(self.buyers)
            print("Car Random ID {}".format(buyer_id))
            for agent in self.model.schedule.agents:
                if (isinstance(agent, CarAgent) and agent.readyToBuy is True):
                    if agent.unique_id == buyer_id:
                        self.buyPrice = agent.price
                        print("Buyer {} Type {}".format(agent.unique_id, agent.type))
                        print("Buy price {}".format(agent.price))
                        self.chooseSeller(agent, self.buyPrice)

        self.satisfiedDemands.append(self.demandCount)

        if self.numberOfBuyers > 0 and self.numberOfSellers == 0:
            print("Not enough place")
            self.waitList = []
            for agent in self.model.schedule.agents:
                if (isinstance(agent, CarAgent) and agent.readyToBuy is True):
                        agent.isWaiting = True
                        self.waitList.append(agent.unique_id)
            print("Cars left {}".format(self.waitList))

        elif self.numberOfBuyers == 0 and self.numberOfSellers > 0:
            print("Place left")
            for agent in self.model.schedule.agents:
                if (isinstance(agent, GateAgent) or isinstance(agent,BarAgent)):
                    if agent.open is True:
                        print("Agent {} Queue {}\nNumber of cars {}".format(agent.unique_id,agent.queue,len(agent.queue)))
        else:
            print("No sellers and No buyers")
        self.dealsList.append(self.dealCount)
        self.noDealsList.append(self.noDealCount)

    def step(self):
        print("Trade!\nhour {}\nday {}\nweek {}".format(self.hour,self.day,self.week))

        self.getCarTypes()

        self.getWaitingCars()
        self.getSellers()
        self.getBuyres()
        self.distributeCars()

        self.timebin.append(self.timestep)
        self.timestep += 1

        self.hour += 1

        if self.hour > 23:
            self.day += 1
            self.hour = 0

        if self.day > 7:
            self.week += 1
            self.day = 0

class CarAgent(Agent):
    def __init__(self,unique_id, model):
        super().__init__(unique_id, model)
        self.hour = 0
        self.day = 0
        self.week = 0
        self.statusPriority = None

        self.price = 0

        self.traided = None

        self.goingToPass = None
        self.choice = None

        self.isWaiting = False
        self.waitingTime = 0

        self.priceHistory = []
        self.priorityHistorySell = []
        self.priorityHistoryBuy = []

        self.type = None

        self.readyToSell = False
        self.readyToBuy = True

    def checkWaitingTime(self):
        if self.waitingTime > 0:
            self.isWaiting = True
            print("Waiting time {}".format(self.waitingTime))
            self.waitingTime -= 1

    def name_func(self):
        print("Agent {}".format(self.unique_id))

    def getType(self):
        if not self.isWaiting:
            self.type = np.random.choice(['car','lorry','emergency'],p=[0.6,0.3,0.1])
        print("Type {}".format(self.type))

    def getPassStatus(self):
        if self.hour >= 7 and self.hour <= 9:
            self.goingToPass = np.random.choice([True,False],p=[0.9,0.1])
        elif self.hour >= 15 and self.hour <= 17:
            self.goingToPass = np.random.choice([True, False], p=[0.9, 0.1])
        else:
            self.goingToPass = np.random.choice([True, False])
        print("Status {}".format(self.goingToPass))

    def checkIfWaiting(self):
        if self.isWaiting:
            self.goingToPass = True
        print("Waiting {}".format(self.isWaiting))
        print("Going to Pass {}".format(self.goingToPass))

    def getTradeStatus(self):
        if self.goingToPass:
            self.readyToBuy = True
        else:
            self.readyToBuy = False

    def calculatePrice(self):
        if self.type == 'car':
            self.price = round(random.uniform(46,56),1)
        elif self.type == 'lorry':
            self.price = round(random.uniform(132, 162), 1)
        else:
            self.price = 0
        print("Price {}".format(self.price))

    def step(self):
        self.name_func()
        self.getType()
        self.getPassStatus()
        self.checkIfWaiting()
        self.getTradeStatus()
        self.calculatePrice()
        self.hour += 1

        if self.hour > 23:
            self.day += 1
            self.hour = 0

        if self.day > 7:
            self.week += 1
            self.day = 0

class GateAgent(Agent):
    def __init__(self,unique_id, model,max_capacity=None):
        super().__init__(unique_id, model)
        self.queue = []
        self.open = True
        self.readyToSell = True

        self.roadLength = 0
        self.speedLimit = 0

        self.hour = 0
        self.day = 0
        self.week = 0

        self.price = 0 # group 1
        self.pricelorry = 0 #group 2

        self.rushHour = False
        self.number_of_cars = 0
        self.density = 0
        self.max = max_capacity
        self.maxCapacity = max_capacity

    def checkIfReadyToSell(self):
        if self.open:
            self.readyToSell = True
        print("Ready to Sell {}".format(self.readyToSell))
        print("Capacity {}".format(self.maxCapacity))

    def updateQueue(self):
        self.queue = []
        self.density = 0
        self.maxCapacity = self.max

    def checkIfRushHour(self):
        if self.hour >= 7 and self.hour <= 9:
            self.rushHour = True
        elif self.hour >= 15 and self.hour <= 17:
            self.rushHour = True
        else:
            self.rushHour = False
        print("Rush Hour {}".format(self.rushHour))

    def setPrice(self):
        if self.rushHour:
            self.price = 56
            self.pricelorry = 162
        else:
            self.price = 46
            self.pricelorry = 132

    def name_func(self):
        print("Agent {}".format(self.unique_id))

    def step(self):
        self.name_func()
        self.updateQueue()
        self.checkIfReadyToSell()
        self.checkIfRushHour()
        self.setPrice()
        self.hour += 1

        if self.hour > 23:
            self.day += 1
            self.hour = 0

        if self.day > 7:
            self.week += 1
            self.day = 0

class BarAgent(Agent):
    def __init__(self,unique_id, model, max_capacity = None):
        super().__init__(unique_id, model)
        self.open = True
        self.queue = []
        self.readyToSell = True

        self.emergencyOpen = False

        self.roadLength = 0
        self.speedLimit = 0

        self.hour = 0
        self.day = 0
        self.week = 0

        self.price = 0
        self.pricelorry = 0

        self.number_of_cars = 0
        self.density = 0
        self.max = max_capacity
        self.maxCapacity = max_capacity

        self.mainGatedensity = 0
        self.mainGateCapacity = 0

    def checkMainGate(self):
        for agent in self.model.schedule.agents:
            if (isinstance(agent, GateAgent)):
                self.mainGatedensity = agent.density
                self.mainGateCapacity = agent.max

    def checkIfOpen(self,density,max_capacity):
        self.open = np.random.choice([True,False],p=[density/max_capacity,1-(density/max_capacity)])
        self.emergencyOpen = self.open
        self.readyToSell = self.open
        print("Agent {} is open: {}".format(self.unique_id,self.readyToSell))

    def checkIfReadyToSell(self):
        if self.open:
            self.readyToSell = True
        print("Ready to Sell {}".format(self.readyToSell))
        print("Capacity {}".format(self.maxCapacity))

    def updateQueue(self):
        self.queue = []
        self.density = 0
        self.maxCapacity = self.max

    def calculatePrice(self):
        self.price = round(random.uniform(0,100),1)
        print("Price {}".format(self.price))

    def setStatus(self):
        if self.hour >= 7 and self.hour <= 9 and self.emergencyOpen is False:
            self.open = False
            self.readyToSell = False
        else:
            self.open = True
            self.readyToSell = True
            self.emergencyOpen = False
        print("Status {}".format(self.open))

    def checkIfRushHour(self):
        if self.hour >= 7 and self.hour <= 9:
            self.rushHour = True
        elif self.hour >= 15 and self.hour <= 17:
            self.rushHour = True
        else:
            self.rushHour = False
        print("Rush Hour {}".format(self.rushHour))

    def setPrice(self):
        if self.rushHour:
            self.price = 56
            self.pricelorry = 162
        else:
            self.price = 46
            self.pricelorry = 132

    def name_func(self):
        print("Agent {}".format(self.unique_id))

    def step(self):
        self.name_func()
        self.updateQueue()
        self.setStatus()
        self.checkIfReadyToSell()
        self.checkIfRushHour()
        self.setPrice()

        self.hour += 1

        if self.hour > 23:
            self.day += 1
            self.hour = 0

        if self.day > 7:
            self.week += 1
            self.day = 0