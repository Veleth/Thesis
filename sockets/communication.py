MESSAGE_END = "\\"
MESSAGE_DELIMITER = "|"

ROLL_COMMAND = "!roll"      #Call to roll (GM only), for example roll d6 username username username
TRACE_COMMAND = "!trace"    #See the calculation trace (user) and compare with others
LIST_COMMAND = "!list"      #List the room members
HELP_COMMAND = "!help"      #See available commands
COMMANDS = [ROLL_COMMAND, TRACE_COMMAND, HELP_COMMAND]

INIT_HEADER = "INIT"     #For server: Initialization request, for client: confirmation and response
                        #TODO: confirmation on client's side
ROLL_HEADER = "ROLL"     #For server: Call to roll by a GM, for client: Call to send their randomness   
                        #TODO: Implement
CHAT_HEADER = "CHAT"     #For server: relay the message to others in the room, for client: get chat message
                        #TODO: adapt to GUI
RESULT_HEADER = "RES"   #For server: result from a player, for client: result from other players
                        #TODO: Implement
TRACE_HEADER = "TRC"    #For server: trace from a player, for client: trace from others
                        #TODO: Implement
VAL_HEADER = "VAL"      #For server - Random values from users, for client: Random values from all the users
                        #TODO: Implement
INFO_HEADER = "INFO"     #Only client - Info from server, like chat
                        #TODO: adapt to GUI


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