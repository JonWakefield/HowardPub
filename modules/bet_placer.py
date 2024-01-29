"""
    Class that...
        1. logs user into websites
        2. places prospective bets

"""
from seleniumbase import Driver
from seleniumbase.common.exceptions import NoSuchElementException, ElementNotVisibleException
from settings import MAX_BET_SIZE, PP_BASE_URL, GOOGLE_URL
from math import ceil

# max number of times to try to place a bet before moving on
MAX_TRY_ATTEMPTS = 3

class BetPlacer():


    max_bet_size = float(MAX_BET_SIZE)

    # Prizepicks simulate interaction element x-paths:
    pp_my_entries = '//*[@id="my-entries-nav-btn"]'
    pp_past_entries = '//*[@id="entries"]/div/div[2]/div[1]/a[2]'
    pp_board_button = '//*[@id="header"]/div/div[1]/div[2]/ul/li[1]/a'
    pp_to_win_label = '//*[@id="to-win-input"]'

    # Prize Pick XPATH elements 
    pp_base_url = PP_BASE_URL
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
        self.sim_num = 0 # simulate num to "randomize" actions
        

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
        
    def simulate_user_interaction(self):
        """
            simulatse user interaction on prize picks to make it look like real person

            Two different page interactions depending on if `self.sim_num` is odd or even
        """
        print("Simulating user page interaction...")
        try:
            # First return to base url
            self.driver.uc_open_with_tab(self.pp_base_url)

            self.driver.uc_click(self.pp_my_entries)

            self.driver.sleep(0.55)

            self.driver.uc_click(self.pp_past_entries)

            self.driver.sleep(0.75)

            self.driver.uc_click(self.pp_board_button)

            self.driver.sleep(.66)

            # Leave website after actions
            self.driver.uc_open_with_tab(GOOGLE_URL)

            self.sim_num = not self.sim_num

            return True
        except Exception as err:
            print("received an error trying to simulate user interaction")
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
        


    def place_pp_bet(self, url: str, unit_size: str) -> str:
        """
            PrizePicks method for navigating the prizepicks DOM 

            return value: think of it as a status code: -> 1 -> successful placement
            @type: str                                  -> 2 -> player line bumped, stop retrying
                                                        -> 3 -> Retry placement
        """

        # Open up the URL:
        self.driver.uc_open_with_tab(url)

        # Check if bet is still placeable:
        if not self.is_pp_valid_bet(): return "2"

        # Enter unit size:
        self.driver.type(self.pp_bet_field, unit_size)

        # Wait small time amount:
        self.driver.sleep(0.231)

        # NOTE: added on 01/27/2024: having issues with prizepicks not letting me place the bet
        try:
            self.driver.uc_click(self.pp_to_win_label, timeout=0.33)
        except(NoSuchElementException, ElementNotVisibleException) as err:
            print(f"PrizePicks not letting bet be placed, retrying...")
            return "3"
        
        # Click button to place bet
        self.driver.uc_click(self.pp_place_bet_field)

        return "1"
    

    def extract_pp_bet(self, message: dict):
        """

        """
        # Extract the url:
        urls = message['url']
        url = urls[0]
        
        # Get our unit size:
        unit_size = str(ceil(message['unit_size']))

        if(float(unit_size) > self.max_bet_size):
            # log here
            print("Bet size too large!")
            return False
        

        # keep track of the number of times the bets been tried to place:
        bet_try_counter = 0
        while bet_try_counter < MAX_TRY_ATTEMPTS:
            bet_result = self.place_pp_bet(url, unit_size)
            if bet_result == "1":
                # bet was successfully placed:
                # leave page and go to google
                self.driver.uc_open_with_tab(GOOGLE_URL)
                return True
            elif bet_result == "2":
                # player line bumped stop retrying
                self.driver.uc_open_with_tab(GOOGLE_URL)
                return False
            else:
                # only using else for readable
                # unsuccessful placement, need to retry
                bet_try_counter += 1


        # bet was not able to be placed:
        self.driver.uc_open_with_tab(GOOGLE_URL)        
        return False


    def close_driver(self):
        self.driver.quit()



