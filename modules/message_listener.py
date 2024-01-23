"""
    Discord Websocket communication.
    Listens for messages posted in discord, puts messages in queue

"""
import json
from time import sleep
import websocket
from websocket._exceptions import WebSocketConnectionClosedException
from settings import KEYWORDS, DISCORD_GATEWAY
import string




class MessageListener():

    def __init__(self, token: str, payload: dict):

        self.token = token
        self.payload = payload
        # Connect to websocket
        self._connect_websocket()

    def _connect_websocket(self):
        """"""
        self.ws = websocket.WebSocket()

        self.ws.connect(DISCORD_GATEWAY)

    def _heartbeat(self, interval: float, logger):
        """"""
        logger.info(f"Heartbeat started")
        print(f"interval is: {interval}")
        try:
            while True:
                sleep(interval)
                heartbeatJSON = {
                    "op": 1,
                    "d": "null"
                }
                self.send_json_request(heartbeatJSON)
                # print("heartbeat sent")
        except (WebSocketConnectionClosedException) as err:
            logger.info(f"Websocket connection lost. {err}")


    def send_json_request(self, request: str):
        """"""
        self.ws.send(json.dumps(request))


    def recieve_json_response(self):
        """"""
        try:
            response = self.ws.recv()
            if response:
                return json.loads(response)
        except (WebSocketConnectionClosedException) as err:
            print("websocket connection lost, restarting...")
            return None


    def receive_and_enqueue(self, response_queue, logger):
        """"""
        while True:
            response = self.recieve_json_response()
            if response is None:
                # Reconnect websocket()
                self._connect_websocket()

                # Get new event:
                event = self.recieve_json_response()

                if event is not None:
                    self.send_json_request(self.payload)
                    logger.info("Connection re-established...")

                else:
                    logger.info("Re-stablished failed!")

            elif response:
                response_queue.put(response)  # Put the received response into the queue

    
    def convert_unit_size(self, unit_size_list: str) -> float:
        """
            Extract correct unit size & convert to float
            Logic:
                - Messages that contain unit sizes come in of the formats:
                    1.  x.y units
                    2.  x.yU
                    3.  x.yu
                    4. X U
                    5. XU
                - 1st Remove the letter U
                - Try to convert to float
        """
        # If no unit size multiplier found -> default to 1
        unit_size_multiplier = 1

        # Remove the letter u or U:
        units_mod_list = [word.replace('u', '').replace('U', '') for word in unit_size_list]

        for unit in units_mod_list:
            # Try to convert to type float (if unable -> not a number)
            try:
                unit_size_multiplier = float(unit)
                # im returning the first valid occurance of a unit size.
                return unit_size_multiplier
            except (ValueError) as v_err:
                pass

        return unit_size_multiplier
    
    def valid_message_content(self, word_list: list) -> bool:
        """
            Check if message contained any 'banned' words
        """
        for word in word_list: 
            if any(keyword in word.lower() for keyword in KEYWORDS):
                return False
            
        return True
    
    
    def parse_role(self, content: str, roles: dict) -> str:
        """"""
        
        # create a set of digits
        digits = set(string.digits)

        # Extract just the numbers from the role
        parsed_content = ''.join(char for char in content if char in digits)

        # Make sure role is in approved list
        if parsed_content in roles:
            # Role found
            print("Found role")
            return roles[parsed_content]
    
        print("Did not find role")
        return -1


    def parse_message_content(self, message: str, author: str, unit_size: str, roles: dict, sharps:dict) -> dict|bool:
        """ Parse message for:
                - URL
                - unit size (if it exists)
                - Canceler: Something inside of the message indicate the play should not be placed or should be manually reviewed
            
            PARSING NOTES:
                - Most messages look the same
                - Most follow the format of:
                    - <unit size> url
                    - url <unit size>
                    - url

                - Message won't contain a URL if the message...
                    - Doesn't have a play 
                    - Screenshot of play (requires manual entry)
        """
        
        # create a set of digits
        digits = set(string.digits)
        
        parsed_msg_dict = {}
        parsed_msg_dict['role'] = -1
        additional_words = []

        url_list = []
        unit_size_list = []


        # Split the message at each word
        msg_split_list = message.split()

        # Iterate through message:
        for word in msg_split_list:
            
            # Check if word is a URL:
            if 'https' in word:

                # Make sure URl is for prizepicks or underdog 
                if 'priz' in word:
                    # Prizepicks link:
                    url_list.append(word)
                    print("Msg contains prize picks URL...")
                    parsed_msg_dict["url"] = url_list

                elif 'dog' in word:
                    # underdog link.
                    url_list.append(word)
                    print("Msg contains Underdog URL...")
                    parsed_msg_dict["url"] = url_list


            # the characters '<@&' are used by discord to prefix a role, if a word contains these characters it is a role
            elif '<@&' in word:
                # Sometimes messages contain multiple roles, check if we already found an approved role:
                if parsed_msg_dict['role'] == -1:
                    # determine which role the message was assigned too:
                    parsed_msg_dict['role'] = self.parse_role(word, roles)

            # Look for unit size
            # Most messages format a unit size using a '.' character or just a number. (ie. 1)
            elif (('.' in word) or (word in digits)):
                # Create unit-size key-value pair:
                unit_size_list.append(word)
                parsed_msg_dict["unit_size"] = unit_size_list

            else:
                # Keep track of all additional words in message:
                additional_words.append(word)


        # Check if we found a URL in the received msg
        if 'url' not in parsed_msg_dict: return False 

        # Check if message contained multiple URLS:
        if len(parsed_msg_dict['url']) > 1: return False
            
        # Check to ensure message does not contain any 'banned words'
        if not self.valid_message_content(additional_words): return False
            

        # Check if message contains a unit size indicator:
        if 'unit_size' in parsed_msg_dict:
            # Convert unit size to value
            parsed_msg_dict['unit_size'] = (self.convert_unit_size(parsed_msg_dict['unit_size']) * float(unit_size))

        # If no unit size found in message, check for unit size by author
        elif author in sharps:
            parsed_msg_dict['unit_size'] = (sharps[author] * float(unit_size))

        # Else, unit size is 1.0
        else:
            parsed_msg_dict['unit_size'] = unit_size

        
        print(f"Parsed message dict: {parsed_msg_dict}")

        return parsed_msg_dict