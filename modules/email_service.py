"""
    Email service that sends emails to n recipients.
    Emails are sent for:
                    1. successful bid placement
                    2. unsuccessful bid placement
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class EmailMessenger():

    def __init__(self, email: str, password: str, recipients: list ,server: str="smtp.gmail.com", port: int=587):

        self.email = email
        self.password = password
        self.server = server
        self.port = port
        self.recipients = recipients


    def bet_placed_message_formatter(self, message: dict, subject, role_name: str=None) -> str:
        """
        """
        # Get the current time
        current_time = datetime.now()

        # Format the time in 12-hour format
        time_12hour = current_time.strftime("%I:%M:%S %p")

        # Format the date in Month Day Year format
        date_formatted = current_time.strftime("%B %d, %Y")

        body = f"""
                Bet Placed on {subject}
                Time: {time_12hour} 
                Date: {date_formatted}
                Role: {role_name}


                Amount Wagered: {message['unit_size']}

                Slip: {message['url']}

                Sent via Python
        """       

        return body


    def no_bet_message_formatter(self, message: dict, channel_name: str=None, role_name: str=None) -> str:
        """"""

        # Get the current time
        current_time = datetime.now()

        # Format the time in 12-hour format
        time_12hour = current_time.strftime("%I:%M:%S %p")

        # Format the date in Month Day Year format
        date_formatted = current_time.strftime("%B %d, %Y")

        # Unpack message:
        author = message['d']['author']['username']
        content = message['d']['content']
        channel = channel_name

        body = f"""
                Discord Message Received at:
                Time: {time_12hour} 
                Date: {date_formatted}

                Author: {author}
                Channel: {channel}
                Role: {role_name}

                Content: {content}

                Sent via Python
        """

        subject = "Unable to place bet"


        return body, subject



    def send_email(self, 
                   message: dict, 
                   subject: str='', 
                   channel_name: str=None, 
                   bet_placed: bool=False, 
                   role_name: str=None,
                   attachments=None) -> bool:
        """
        """
        # Format message correctly.
        if bet_placed:
            body = self.bet_placed_message_formatter(message, subject=subject, role_name=role_name)
            subject = "Bet Successfully Placed On " + subject
        else:
            body, subject = self.no_bet_message_formatter(message, channel_name=channel_name, role_name=role_name)

        # Create a MIME object to define parts of the email:
        msg = MIMEMultipart()
        msg['From'] = self.email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        try:
            # Establish a connection to the server
            # smtp_client = smtplib.SMTP(self.server, self.port, start_tls=True)
            smtp_client = smtplib.SMTP(self.server, self.port)
            smtp_client.starttls()

            # Login to the SMTP server:
            smtp_client.login(self.email, self.password)
            


            for recipient in self.recipients:
                
                # Set up message recipient:
                msg['To'] = recipient
                text = msg.as_string()

                smtp_client.sendmail(self.email, recipient, text)


            print("Emails successfully sent.")

            return True

        except Exception as e:
            print(f"Failed to send email. {e}")
            return False

        finally:
            # Close connection
            smtp_client.quit()


