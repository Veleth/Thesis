"""
Module with definitions required for bilateral client-server communication.
It contains constants, rudimentary functions, and documentation.
If the protocol changes, only this file needs to be altered.
"""

MESSAGE_END = '\\'
MESSAGE_DELIMITER = '|'

ROLL_COMMAND = '!roll'      # Call to roll (GM only), for example `roll d6 username username username`
TRACE_COMMAND = '!trace'    # See the calculation trace (user) and compare with others
LIST_COMMAND = '!list'      # List the room members
HELP_COMMAND = '!help'      # See available commands

COMMANDS = [ROLL_COMMAND, TRACE_COMMAND, HELP_COMMAND]

INIT_HEADER = 'INIT'    # For server: Initialization request, for client: confirmation and response
                        # server -> client - Automatic call upon successful connection
                        # client -> server ['INIT', '{room_number}', '{name}']
                        #TODO: confirmation on client side

ROLL_HEADER = 'ROLL'    # For server: Call to roll by a GM, for client: Call to send their randomness   
                        # server -> client ['ROLL', '{timeout}', '{max}'] #TODO: Implement
                        # client -> server ['ROLL', '{value}']
                        #TODO: Implement, handle D/C

CHAT_HEADER = 'CHAT'    # For server: relay the message to others in the room, for client: get chat message
                        # both ways ['CHAT', '{name}', '{message}'] #TODO: Implement on server
                        #TODO: adapt to GUI

RESULT_HEADER = 'RES'   # For server: result from a player, for client: result from other players
                        # server -> client ['RES', '{result1}', '{result2}', ...] #TODO: Implement
                        # client -> server ['RES', '{result}']                    #TODO: Implement

TRACE_HEADER = 'TRC'    # For server: trace from a player, for client: trace from others
                        # server -> client ['TRC', '{trace1}', '{trace2}'] (log) #TODO: Implement
                        # client -> server ['ROLL', '{trace}']
                        #TODO: Implement

VAL_HEADER = 'VAL'      # For client: Random values from all the users
                        # server -> client ['VAL', '{value1}', '{value2}', ...] #TODO: Implement
                        # client -> server ['VAL', '{value}']                   #TODO: Implement

INFO_HEADER = 'INFO'    # Only client - Info from server, like chat
                        # server -> client ['INFO', '{message}']

HEADERS = [INIT_HEADER, ROLL_HEADER, CHAT_HEADER, RESULT_HEADER, 
TRACE_HEADER, VAL_HEADER, INFO_HEADER]

def compose(header, args):
    msg = header
    for arg in args:
        msg += MESSAGE_DELIMITER
        msg += str(arg)
    msg += MESSAGE_END
    return msg.encode()

def decompose(message):
    message = message.decode()
    return list(filter(None, message.split(MESSAGE_END)))

class UndefinedHeaderException(Exception):
    """Raised when the message header is not in HEADERS"""
    pass