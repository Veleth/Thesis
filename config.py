"""
Configuration

All configurable variables for server and client. Adjustable within reasonable limits.
"""
#GUI data validation
MIN_USERNAME_CHARS = 2
MAX_USERNAME_CHARS = 32

MIN_ROOM_NUMBER_CHARS = 1
MAX_ROOM_NUMBER_CHARS = 20


""""
Server config
"""
#Server IP address depending on scope (WAN, LAN, or localhost)
IPADDR='127.0.0.1'

#Max number of players in one room
MAX_PLAYERS_PER_ROOM = 20

#Max room number or username length (server)
MAX_STRING_LENGTH = 100