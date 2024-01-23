"""
    Class that...
        1. logs user into websites
        2. places prospective bets

"""
from seleniumbase import Driver
from seleniumbase.common.exceptions import NoSuchElementException, ElementNotVisibleException
from settings import MAX_BET_SIZE
from math import ceil


class BetPlacer():


    max_bet_size = float(MAX_BET_SIZE)

    # Prize Pick XPATH elements 
    pp_email_field = "//input[@id='email-input']"
    pp_password_field = "//input[@type='password']"
    pp_login_button = "//button[@id='submit-btn']"
    pp_bet_field = "//input[@id='entry-input']" 
    pp_place_bet_field = "//*[@id='board']/div[2]/div[2]/div[2]/div[3]/div/form/div[2]/button"
    pp_edit_entry_field = "/html/body/div[2]/div[3]/div/div[2]/button"

    # Underdog elements

    def __init__(self, email: str, password: str, unit_size: str, headless: bool) -> None:
        """"""

        # Create undetected chrome driver 
        self.driver = Driver(uc=True, headless=headless)
        self.email = email
        self.password = password
        self.unit_size = unit_size
        

    def login_prize_picks(self, url: str) -> bool:
        """
            Login to prize picks website
            (This is only done once on startup so time-to-login is not a constraint)
             Can modify sleep values as needed
        """
        
        try:
            # Naviage to the url:
            self.driver.get(url)
            self.driver.sleep(2.31) # make sure website loads in 
            # Type email in email field
            self.driver.type(self.pp_email_field, self.email)
            # Wait
            self.driver.sleep(0.731)
            # Type password in password field
            self.driver.type(self.pp_password_field, self.password)
            # Wait 
            self.driver.sleep(0.861)
            self.driver.uc_click(self.pp_login_button)

            print("Logged into prizepicks...")

            return True
        except Exception as err:
            print("Failed to loggin to prizepicks")
            print(err)
            return False

    def is_pp_valid_bet(self):
        """
            Check if prizepicks bet is still valid:
            - IF A SLIP HAS A PLAYER WITH A CHANGED VALUE THIS ELEMENT WILL APPEAR:
            - /html/body/div[2]/div[3]/div/div[2]/button text="The projection has changed for the player listed above:
            - Or this whole div will appear : //div[@class='MuiBox-root css-htqn7v']
        """
        # Look for an element on the screen:
        try:
            self.driver.uc_click(self.pp_edit_entry_field, timeout=0.271)
            # If ^ doesn't throw error -> bet is invalid. dont place
            print("Bet is Invalid!")
            return False

        except(NoSuchElementException, ElementNotVisibleException) as err:
            # Valid bet!
            print("Bet is Valid!")
            return True
        

    def place_pp_bet(self, message: dict):
        """
            PrizePicks method for navigating the prizepicks DOM 
        """

        # Extract the url:
        urls = message['url']
        url = urls.pop()
        
        # Get our unit size:
        unit_size = str(ceil(message['unit_size']))

        if(float(unit_size) > self.max_bet_size):
            # log here
            print("Bet size too large!")
            return False

        # Open up the URL:
        self.driver.uc_open_with_tab(url)

        # Check if bet is still placeable:
        if not self.is_pp_valid_bet(): return False
            

        # Enter unit size:
        self.driver.type(self.pp_bet_field, unit_size)

        # Wait small time amount:
        self.driver.sleep(0.231)
        
        # Click button to place bet
        self.driver.uc_click(self.pp_place_bet_field)

        return True

    def close_driver(self):
        self.driver.quit()



