from enum import Enum
from queue import Queue
class Room:
    def __init__(self, number):
        self.number = number
        self.players = []
        self.participants = []
        self.results = {}
        self.values = {}
        self.traces = {}
        self.missing = 0
        self.state = State.IDLE
        self.messageQueue = Queue()

    def add_player(self, player):
        self.players.append(player)

    def remove_player(self, player):
        if player in self.results.keys():
            del self.results[player]
        if player in self.values.keys():
            del self.values[player]
        if player in self.traces.keys():
            del self.traces[player]
        if player in self.participants:
            self.participants.remove(player)
        self.players.remove(player)

    def get_players(self):
        return self.players

    def start_action(self, participants=None):
        if participants is None:
            self.participants = self.players.copy()
        else:
            self.participants = participants

    def get_participants(self):
        return self.participants

    def clear_participants(self):
        self.participants = []

    def add_result(self, player, result):
        self.results[player] = result
    
    def clear_results(self):
        self.results = {}

    def get_results(self):
        return list(self.results.values())

    def add_value(self, player, value):
        self.values[player] = value

    def clear_values(self):
        self.values = {}

    def get_values(self):
        return list(self.values.values())

    def add_trace(self, player, trace):
        self.traces[player] = trace

    def clear_traces(self):
        self.traces = {}

    def get_traces(self):
        return list(self.traces.values())
    
    def clear(self):
        self.clear_results()
        self.clear_traces()
        self.clear_values()
        self.clear_participants()

    def get_number(self):
        return self.number

    def get_state(self):
        return self.state
    
    def set_state(self, state):
        self.state = state

class State(Enum):
    IDLE = 1
    ROLL = 2
    RESULT = 3
    TRACE = 4