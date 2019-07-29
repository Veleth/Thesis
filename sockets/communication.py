MESSAGE_END = ";"
MESSAGE_DELIMITER = ":"

ROLL_COMMAND = "!roll"
TRACE_COMMAND = "!trace"
HELP_COMMAND = "!help"
COMMANDS = [ROLL_COMMAND, TRACE_COMMAND, HELP_COMMAND]

INIT_HEADER = "INI"
ROLL_HEADER = "ROL"
CHAT_HEADER = "CHT"
RESULT_HEADER = "RES"
TRACE_HEADER = "TRC"
VAR_HEADER = "VAR"      #Only client
INFO_HEADER = "INF"     #Only server
HEADERS = [INIT_HEADER, ROLL_HEADER, CHAT_HEADER, RESULT_HEADER, 
TRACE_HEADER, VAR_HEADER, INFO_HEADER]

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