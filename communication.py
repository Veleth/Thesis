from Crypto.Cipher import Salsa20

"""
Module with definitions required for bilateral client-server communication.
It contains constants, functions, and documentation.
If the protocol changes, only this file needs to be altered.
"""

MESSAGE_END = ';;;'
MESSAGE_DELIMITER = '|'

INIT_HEADER = 'INIT'    # For server: Initialization request, for client: confirmation and response
                        # client -> server ['INIT', '{room_number}', '{name}']
                        # server -> client ['INIT', '{room_number}', '{name}', '{isGM}']

ROLL_HEADER = 'ROLL'    # For server: Call to roll by a GM, for client: Call to send their randomness   
                        # server -> client ['ROLL', '{timeout}', '{max}'] 
                        # client -> server ['ROLL', '{timeout}', '{max}']

CHAT_HEADER = 'CHAT'    # For server: relay the message to others in the room, for client: get chat message
                        # server -> client ['CHAT', '{name}', '{message}']
                        # client -> server ['CHAT', '{name}', '{message}']

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

ERROR_HEADER = 'ERR'    # For client : notification when their input is not accepted, for server : client-reported errors
                        # client -> server ['ERR' '{error_type}', '{message}']
                        # server -> client ['ERR' '{error_type}', '{message}']

HEADERS = [INIT_HEADER, ROLL_HEADER, CHAT_HEADER, RESULT_HEADER, 
TRACE_HEADER, VAL_HEADER, INFO_HEADER, NEW_USER_HEADER, DROPPED_USER_HEADER,
USER_LIST_HEADER, ERROR_HEADER]

VALUE_OMITTED_ERROR = 'VOE'       #Client -> server -> client
                                  # message = value

RESULT_DIFFERS_ERROR = 'RDE'      #Client -> server -> client
                                  # message = result

VALUE_NOT_ACCEPTED_ERROR = 'VNAE' #Only server -> client

ROLL_TOO_SOON_ERROR = 'RTSE'      #Only server -> client
                                  #message = time
                                  
ROOM_FULL_ERROR = 'RFE'           #Only server -> client


IPADDR='127.0.0.1'#TODO: Remove IP / config?

def compose(header, args, key=None):
    message = header
    for arg in args:
        message += MESSAGE_DELIMITER
        message += str(arg)
    if key:
        message = encrypt(message, key)
        message += MESSAGE_END.encode()
    else:
        message += MESSAGE_END
    return message

def decompose(message, key=None):
    #TODO: Decomposition when there's no encryption
    messages = list(filter(None, message.split(MESSAGE_END.encode())))
    decomposed = []
    for msg in messages:
        if key:
            contents = decrypt(msg, key)
        contents = contents.decode()
        decomposed.append(contents)
    return decomposed
    
def encrypt(message, key):
    cipher = Salsa20.new(key)
    return cipher.nonce + cipher.encrypt(message.encode())

def decrypt(message, key):
    nonce, secret = message[:8], message[8:]
    cipher = Salsa20.new(key, nonce=nonce)
    return cipher.decrypt(secret)

class UndefinedHeaderException(Exception):
    """Raised when the message header is not in HEADERS"""
    pass