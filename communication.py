"""
Communication Module

A module with definitions required for bilateral client-server communication.
It contains constants, functions, and documentation.
If the protocol changes, only this file needs to be altered.
"""


from Crypto.Cipher import Salsa20

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

HEADERS = [INIT_HEADER, ROLL_HEADER, CHAT_HEADER, RESULT_HEADER, VAL_HEADER, INFO_HEADER, NEW_USER_HEADER, DROPPED_USER_HEADER,
USER_LIST_HEADER, ERROR_HEADER]

VALUE_OMITTED_ERROR = 'VOE'       #Client -> server -> client
                                  # message = value

RESULT_DIFFERS_ERROR = 'RDE'      #Client -> server -> client
                                  # message = result

ROLL_TOO_SOON_ERROR = 'RTSE'      #Only server -> client
                                  #message = time

ROOM_FULL_ERROR = 'RFE'           #Only server -> client

INPUT_TOO_LONG_ERROR = 'ITLE'     #Only server -> client

def compose(header, args, key=None):
    """
    Create a message given its content
    Input
        header          message header
        args            message arguments   
        key (optional)  encryption key
    Output: 
        composed message
    """
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
    """
    Tokenize a message
    Input
        message         received message  
        key (optional)  encryption key
    Output: 
        tokenized message
    """
    messages = list(filter(None, message.split(MESSAGE_END.encode())))
    decomposed = []
    for msg in messages:
        if key:
            contents = decrypt(msg, key)
        contents = contents.decode()
        decomposed.append(contents)
    return decomposed
    
def encrypt(message, key):
    """
    Encrypt a message using Salsa20
    Input
        message      message to encrypt  
        key          encryption key
    Output: 
        encrypted message
    """
    cipher = Salsa20.new(key)
    return cipher.nonce + cipher.encrypt(message.encode())

def decrypt(message, key):
    """
    Decrypt an encrypted message
    Input
        message      message to decrypt  
        key          encryption key
    Output: 
        decrypted message
    """
    nonce, secret = message[:8], message[8:]
    cipher = Salsa20.new(key, nonce=nonce)
    return cipher.decrypt(secret)

class UndefinedHeaderException(Exception):
    """Raised when the message header is not in HEADERS"""
    pass