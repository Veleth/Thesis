from enum import Enum
from queue import Queue
class Room:
    def __init__(self, number):
        self.number = number
        self.players = []
        self.participants = []
        self.results = {}
        self.values = {}
        self.missing = 0
        self.state = State.IDLE
        self.messageQueue = Queue()
        self.nextRollAfter = 0
        self.problem = False

    def addPlayer(self, player):
        self.players.append(player)

    def removePlayer(self, player):
        if player in self.results.keys():
            del self.results[player]
        if player in self.values.keys():
            del self.values[player]
        if player in self.participants:
            self.participants.remove(player)
        self.players.remove(player)

    def getPlayers(self):
        return self.players

    def startAction(self, participants=None):
        if participants is None:
            self.participants = self.players.copy()
        else:
            self.participants = participants

    def getParticipants(self):
        return self.participants

    def clearParticipants(self):
        self.participants = []

    def addResult(self, player, result):
        self.results[player] = result
    
    def clearResults(self):
        self.results = {}

    def getResults(self):
        return list(self.results.values())

    def addValue(self, player, value):
        self.values[player] = value

    def clearValues(self):
        self.values = {}

    def getValues(self):
        return list(self.values.values())
    
    def clear(self):
        self.clearResults()
        self.clearValues()
        self.clearParticipants()

    def getNumber(self):
        return self.number

    def getState(self):
        return self.state
    
    def setState(self, state):
        self.state = state

class State(Enum):
    IDLE = 1
    ROLL = 2
    RESULT = 3