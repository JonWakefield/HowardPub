from dotenv import load_dotenv
import os
import logging
from logging.config import dictConfig

# load in environment variables
load_dotenv()

UNIT_SIZE = os.getenv("UNIT_SIZE") # standard size of 1 bet (unit: $)
MAX_BET_SIZE = os.getenv("MAX_BET_SIZE") # maximum allowable bet size (unit: $)
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN") # Your respective discord token

# discord websocket gateway
DISCORD_GATEWAY = "wss://gateway.discord.gg/?v=6&encording=json" 


EMAIL = os.getenv("EMAIL") # LOGIN EMAIL FOR FANTASY SPORTS SITE 
PASSWORD = os.getenv("PASSWORD") # login password for fantasy sports site

EMAIL_SENDER = os.getenv("EMAIL_SENDER") # email for email messenger service
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD") # password for email messenger service


# list of email recipients (add as many as needed)
EMAIL_RECIPIENTS = [
    os.getenv("EMAIL_RECIPIENT_01")
]

# Starting payload (can be modified or kept the same)
PAYLOAD = {
    'op': 2,
    "d": {
        "token": DISCORD_TOKEN,
        "properties": {
            "$os": "windows",
            "$browser": "chrome",
            "$device": "pc"
        }
    }
}


# NOTE: as of 01/16/2024 they changed discord channel format... all prize picks related slips are posted in the prizepicks channel
CHANNEL_IDS = {
    '1171626406241914890': 'test_channel',
    '1131035315067433061': 'prize_picks',
    # '1131035354602950778': 'underdog',
    # '1150850418700726272': 'football',
    # '1161787993540010006': 'hockey',
    # '1171844189399547934': 'soccer',
    # '1166404192743731360': 'basketball',
    # '1164705710089715762': 'esports' 
}

# Ensure message posted in a specific channel is for the correct role
# NOTE: as of 01/16/2024 roles are no longer useful. (keeping them here incase they get brought back)
ROLE_IDS = {
    '1150867043147595859': 'nfl',
    '1166682605513621575': 'cfb',
    '1172416078601801759': 'soccer',
    '1163558565563334716': 'hockey',
    '1131326230470340700': 'prizepicks'
}

# key: sharps, value: unit_size 
# Some sharps have different base unit sizes 
# (NOTE: This will only take effect if the parsed message does not contain a unit size. See message_listener.py 244-251 for reference)
SHARPS = {
    'evbetsks': 1.25,
    'mitch': 1.0,
    'brianstephens318': 1.0,
    'WinningEV': 1.0
}


# login urls for all websites to place bets on 
URLS = {
    "prize_picks": "https://app.prizepicks.com/login",
    "underdog": "https://underdogfantasy.com/"
}

# prize picks base url 
PP_BASE_URL = "https://app.prizepicks.com/"
GOOGLE_URL = "https://www.google.com/"
    

# SET UP LOGGIN CONFIGURATION
# Can be ommitted if loggin is not important to you
LOGGING_CONFIG = {
    "version": 1,
    "disabled_existing_loggers": False,
    "formatters": {
        "verbose":{
            "format": "%(levelname)-5s - %(asctime)-5s - %(module)-5s : %(message)s",
            "datefmt": "%Y-%m-%d %I:%M:%S %p"
        }
    },
    "handlers": {
        "console": {
            'level': "DEBUG",
            'class': "logging.StreamHandler",
            'formatter': "verbose"
        },
        "console2": {
            'level': "WARNING",
            'class': "logging.StreamHandler",
            'formatter': "verbose"
        },
        "file_handler": {
            'level': "INFO",
            'class': "logging.FileHandler",
            'filename': "logs\info.log",
            'mode': "w",
            "formatter": "verbose"
        },
    },
    'loggers': {
        '': {
            'handlers': ['file_handler', 'console2'],
            'level': "INFO",
            'propagate': False
        }
    }
}

dictConfig(LOGGING_CONFIG)



# Keywords: set of "cautionary" words the bot looks for before placing a bet. 
# (Ex: If a message contains the word 'cancel' no bet will be placed and an email will be sent)
# Feel free to modify the set as needed (use all lowercase)
KEYWORDS = {
    "void",
    "delete",
    "cancel",
    "canceling",
    "power",
    'overexposure',
    'pass'
}