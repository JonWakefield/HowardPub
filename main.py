import settings
import websocket
import threading
import settings
from modules.message_listener import MessageListener
from modules.bet_placer import BetPlacer
from websocket._exceptions import WebSocketException
from modules.email_service import EmailMessenger
from queue import Queue
import sys, os, random
import time

# Setup our logger:
logger = settings.logging.getLogger()

def run(token: str, 
            payload: dict, 
            channels: dict, 
            urls: list, 
            email: str, 
            password: str,
            unit_size: str,
            role_ids: dict,
            sharps: dict,
            email_sender: str,
            email_password: str,
            email_recipients: list,
            headless: bool=False) -> None:
    """
    
    """

    # Set up a resposne queue:
    response_queue = Queue()

    # Create an email messenger obj:
    email_service = EmailMessenger(email_sender, email_password, email_recipients)

    # PHASE 1: Establish connection to Discord gateway

    # Create a discord message listener instance:
    listener = MessageListener(token, payload)

    event = listener.recieve_json_response()

    # extract heartbeat interval to keep ws connection alive
    heartbeat_interval = event['d']['heartbeat_interval'] / 1000

    # Start heartbeat on a new thread to keep it running
    threading._start_new_thread(listener._heartbeat, (heartbeat_interval, logger))

    # Start a new thread to capture messages and store them in the queue:
    threading._start_new_thread(listener.receive_and_enqueue, (response_queue, logger))

    listener.send_json_request(payload)
    
    # PHASE 2: Establish connection to websites using seleniumbase:

    # Create our web driver
    web_driver = BetPlacer(email, password, unit_size, headless)

    # Connect webdriver to URLS:
    login_result = web_driver.login_prize_picks(urls['prize_picks'])
    if not login_result: return False # If login fails, end program

    # simulate user interaction on prize picks:
    success = web_driver.simulate_user_interaction()
    if not success: logger.info("Failed To simulate user interaction")

    # get random time interval to simulate user interactions
    time_interval = random.randint(37, 51) * 60 
    # print(f"Time interval is {time_interval} minutes")
    start_time = time.time()

    # continues loop of reading in messages and taken actions based on message
    try:
        while True:

            # Recent var:
            bet_placed = False

            # Check if we need to simulate some random actions before getting next message:
            cur_time = time.time()
            elapsed_time = cur_time - start_time
            if elapsed_time >= time_interval:
                # simulate some user action:
                success = web_driver.simulate_user_interaction()
                if not success: logger.info("Failed To simulate user interaction")

                # Get new time interval and starting time
                time_interval = random.randint(37, 51) * 60 
                # print(f"Time interval is {time_interval} minutes")
                start_time = time.time()

            
            # pop most recent message from queue
            event = response_queue.get()

            try:
                # Get the discord event type
                event_type = event['t']

                # Make sure the event type is message_create
                if (str(event_type) == "MESSAGE_CREATE"):

                    # Get the channel id from the message
                    event_channel = event['d']['channel_id']

                    # Check if the channel from the incoming event is in the channel_id list:
                    if str(event_channel) in channels:

                        # Get the name of the channel for logging & email:
                        channel_name = channel_ids[event_channel]

                        # Extract msg content and author
                        msg_content = event['d']['content']
                        msg_author = event['d']['author']['username']

                        # Log Message info
                        logger.info(f"Message Content: {msg_content} From: {event['d']['author']['username']} Channel Name: {channel_name}")

                        # Parse data:
                        parsed_message = listener.parse_message_content(msg_content, msg_author, unit_size, role_ids, sharps)


                        try:
                            # Check if prizepicks link in message
                            if 'url' in parsed_message:
                                # Check to make sure the correct role is found in the message:
                                # NOTE: since roles are no longer relavent, ignore check (channels still matteer)
                                # if parsed_message['role'] != -1:
                                # Place bet:
                                logger.info("Placing prizepicks bet...")
                                bet_placed = web_driver.extract_pp_bet(parsed_message)
                                if bet_placed:
                                    logger.info("Prize picks bet successfully placed")

                        except (TypeError) as t_err:
                            pass


                        # Send email:
                        if bet_placed:
                            email_service.send_email(message=parsed_message, 
                                                     subject="PrizePicks",
                                                     bet_placed=True,
                                                     role_name=parsed_message['role'])
                        else:
                            email_service.send_email(message=event, bet_placed=False, channel_name=channel_name)


                op_code = event('op')
                if op_code == 11:
                    logger.info("Heartbeat recieved")

            except (TypeError) as err:
                # Note this error occurs all the time (and is natural), ignore it 
                pass

            except (websocket.WebSocketConnectionClosedException) as err:
                logger.info("websocket exception in main")


            except (Exception) as err:
                logger.error(err, exc_info=True)

    finally:
        web_driver.close_driver()
        logger.info("Shutting down web drivers")
        pass





if __name__ == "__main__":

    # My token:
    token = settings.DISCORD_TOKEN

    # Load in example payload
    payload = settings.PAYLOAD

    # Load in our channel IDs
    channel_ids = settings.CHANNEL_IDS

    # load in role IDs:
    role_ids = settings.ROLE_IDS

    # Import betting website credientials:
    email = settings.EMAIL
    password = settings.PASSWORD

    unit_size = settings.UNIT_SIZE

    urls = settings.URLS

    sharps = settings.SHARPS

    # Email Credentials:
    email_sender = settings.EMAIL_SENDER
    email_password = settings.EMAIL_PASSWORD
    email_recipients = settings.EMAIL_RECIPIENTS

    try:
        run(token, 
            payload, 
            channel_ids, 
            urls,
            email, 
            password,
            unit_size,
            role_ids,
            sharps,
            email_sender,
            email_password,
            email_recipients,
            headless=True)        
        
    except KeyboardInterrupt:
        # Could do something here: ... 
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
        
    
    finally:
        pass
