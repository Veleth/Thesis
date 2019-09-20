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
                        # client -> server ['INIT', '{room_number}', '{name}']
                        # server -> client ['INIT', '{room_number}', '{name}', '{isGM}']
                        #TODO: confirmation on client side

ROLL_HEADER = 'ROLL'    # For server: Call to roll by a GM, for client: Call to send their randomness   
                        # server -> client ['ROLL', '{timeout}', '{max}'] 
                        # client -> server ['ROLL', '{value}']
                        #TODO: Handle d/c

CHAT_HEADER = 'CHAT'    # For server: relay the message to others in the room, for client: get chat message
                        # both ways ['CHAT', '{name}', '{message}']  on server

RESULT_HEADER = 'RES'   # For server: result from a player, for client: result from other players
                        # server -> client ['RES', '{result1}', '{result2}', ...] 
                        # client -> server ['RES', '{result}']                    

TRACE_HEADER = 'TRC'    # For server: trace from a player, for client: trace from others
                        # server -> client ['TRC', '{trace1}', '{trace2}'] (log) 
                        # client -> server ['ROLL', '{trace}']

VAL_HEADER = 'VAL'      # For server: Random value from the user, for client: Random values from all the users
                        # client -> server ['VAL', {value}]
                        # server -> client ['VAL', '{value1}', '{value2}', ...]

INFO_HEADER = 'INFO'    # Only client - Info from server, like chat
                        # server -> client ['INFO', '{message}']

NEW_USER_HEADER = 'NUSR' # Only server -> client, like info 
                         # ['NUSR', '{username}']

DROPPED_USER_HEADER = 'DUSR' # Only server -> client, like info
                             # ['DUSR', '{username}']

USER_LIST_HEADER = 'LIST' # For client : user list from the server, for server: list request from the client
                          # client -> server ['LIST']
                          # server -> client ['LIST', '{username1}', '{username2}', ...]

HEADERS = [INIT_HEADER, ROLL_HEADER, CHAT_HEADER, RESULT_HEADER, 
TRACE_HEADER, VAL_HEADER, INFO_HEADER, NEW_USER_HEADER, DROPPED_USER_HEADER,
USER_LIST_HEADER]

IPADDR='127.0.0.1'#TODO: Remove IP

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