"""
Room module

Implements Room class and its State
"""
from enum import Enum
from queue import Queue
class Room:
    """
    Room class 

    Provides some abstraction for Room object, used by the Server
    Attributes:
        number          room number
        players         players in the room
        participants    participants of the current roll
        results         results in the room
        values          values in the room
        state           current room state
        messageQueue    queue of messages awaiting to be sent in the room
        nextRollAfter   next roll delay in seconds
        problem         whether there was a problem with the last roll
    """
    def __init__(self, number):
        """
        Room constructor
        Input:
            number   room number
        """
        self.number = number
        self.players = []
        self.participants = []
        self.results = {}
        self.values = {}
        self.state = State.IDLE
        self.messageQueue = Queue()
        self.nextRollAfter = 0
        self.problem = False

    def addPlayer(self, player):
        """
        Adds a player to the room
        Input:
            player    player to be added
        """
        self.players.append(player)

    def removePlayer(self, player):
        """
        Removes a player from the room
        Input:
            player    player to be removed
        """
        if player in self.results.keys():
            del self.results[player]
        if player in self.values.keys():
            del self.values[player]
        if player in self.participants:
            self.participants.remove(player)
        self.players.remove(player)

    def getPlayers(self):
        """
        Returns list of players from the room
        Output:
            list of players
        """
        return self.players

    def startAction(self, participants=None):
        """
        Begins an action with a given set of participants
        Input:
            participants(optional)  list of participants. If empty, all players in the room are participants
        """
        if participants is None:
            self.participants = self.players.copy()
        else:
            self.participants = participants

    def getParticipants(self):
        """
        Returns a list of participants in the room
        Output:
            list of participants
        """
        return self.participants

    def clearParticipants(self):
        """
        Clears list of participants
        """
        self.participants = []

    def addResult(self, player, result):
        """
        Assigns a result to a given player
        Input:
            player      target player
            result      result to assign
        """
        self.results[player] = result
    
    def clearResults(self):
        """
        Clears list of results
        """
        self.results = {}

    def getResults(self):
        """
        Returns results of the players
        Output:
            list of results
        """
        return list(self.results.values())

    def addValue(self, player, value):
        """
        Assigns a value to a given player
        Input:
            player      target player
            value      value to assign
        """
        self.values[player] = value

    def clearValues(self):
        """
        Clears list of values
        """
        self.values = {}

    def getValues(self):
        """
        Returns values of the players
        Output:
            list of values
        """
        return list(self.values.values())
    
    def clear(self):
        """
        Clears previous roll values in the room
        """
        self.clearResults()
        self.clearValues()
        self.clearParticipants()

    def getNumber(self):
        """
        Room number getter
        Output:
            room number
        """
        return self.number

    def getState(self):
        """
        Room state getter
        Output:
            room state
        """
        return self.state
    
    def setState(self, state):
        """
        Room state sette
        Input:
            state    desired state
        """
        self.state = state

class State(Enum):
    """
    Small enum for room states
    """
    IDLE = 1
    ROLL = 2
    RESULT = 3