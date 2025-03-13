from selenium.webdriver import Chrome, ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

import asyncio
import time
import re

from redshot.constants import Locator, State
from redshot.event import EVENT_LIST, EventHandler
from redshot.auth import NoAuth
import redshot.utils as utils

class Client(EventHandler):

    def __init__(self, auth=None, poll_freq=0.25, unread_messages_sleep=0.5, headless=True):

        super().__init__()

        for event_type in EVENT_LIST:
            self.add_event(event_type)

        self.auth = auth if auth is not None else NoAuth()
        self.poll_freq = poll_freq
        self.headless = headless

        self.unread_messages_sleep = unread_messages_sleep

        self.running = False
        self.quited = False
        self._driver = None

        # sort by translateY i.e. in order of how the results show up
        self.search_sort_key = lambda i: int(re.findall(r"\d+", i.value_of_css_property("transform"))[-1])

    def _init_driver(self):

        options = Options()

        if self.headless:
            options.add_argument("--headless")
        self.auth.add_arguments(options)

        return Chrome(options=options)

    async def main_loop(self):
        """
        Asynchronously monitors the WhatsApp Web page and triggers events
        based on changes in the page state.

        Workflow:
        1. Initializes the web driver and navigates to the WhatsApp Web URL.
        2. Triggers an "on_start" event indicating the start of the monitoring loop.
        3. Enters a continuous loop (while self.running) to:
            a. Check the current state of the page using self._get_state().
            b. If the state is not available, wait for a short period before polling again.
            c. If the state changes from the previously recorded state, perform actions 
                based on the new state:
                    - For AUTH state: trigger the "on_auth" event.
                    - For QR_AUTH state: extract the QR code image from the canvas and trigger
                    the "on_qr" event with the QR image.
                    - For LOADING state: detect if chats are loading and trigger the "on_loading"
                    event.
                    - For LOGGED_IN state: trigger the "on_logged_in" event.
            d. If in QR_AUTH state and the QR code changes, trigger an "on_qr_change" event.
            e. If logged in, check for unread chats, extract details from them, and trigger an
                "on_unread_chat" event for each unread chat.
        4. On each iteration, trigger an "on_tick" event to denote a loop iteration.
        5. Wait for a defined polling frequency (self.poll_freq) before the next iteration.

        Exceptions:
        - Catches StaleElementReferenceException and NoSuchElementException during QR extraction,
            which may occur if the relevant HTML element is no longer available.

        Event Triggering:
        - "on_start": Signifies the beginning of the monitoring process.
        - "on_auth": Signifies that an authentication state has been detected.
        - "on_qr": Provides the QR code image extracted during the QR authentication state.
        - "on_qr_change": Indicates that the displayed QR code has changed.
        - "on_loading": Indicates that chat loading is in progress.
        - "on_logged_in": Signifies the completion of the login process.
        - "on_unread_chat": Provides details about an unread chat.
        - "on_tick": Fired at the end of each loop iteration.
        """

        # Initialize the web driver and navigate to WhatsApp Web
        self._driver = self._init_driver()
        self._driver.get("https://web.whatsapp.com")

        qr_binary = None
        state = None

        self.trigger_event("on_start")

        # Main monitoring loop
        while self.running:

            curr_state = self._get_state()

            if curr_state is None:
                await asyncio.sleep(self.poll_freq)
                continue

            # If the state has changed, handle state-specific events
            elif curr_state != state:

                match curr_state:

                    case State.AUTH:
                        self.trigger_event("on_auth")

                    case State.QR_AUTH:
                        # Locate the QR code element and extract its image as binary data
                        qr_code_canvas = self._driver.find_element(*Locator.QR_CODE)
                        qr_binary = utils.extract_image_from_canvas(self._driver, qr_code_canvas)

                        self.trigger_event("on_qr", qr_binary)

                    case State.LOADING:
                        # Check if chats are loading and trigger event with the status
                        loading_chats = utils.is_present(self._driver, Locator.LOADING_CHATS)
                        self.trigger_event("on_loading", loading_chats)

                    case State.LOGGED_IN:
                        self.trigger_event("on_logged_in")

                state = curr_state

            else:

                # If the state is same as previous and is QR_AUTH, check for QR code changes
                if curr_state == State.QR_AUTH:

                    try:

                        qr_code_canvas = self._driver.find_element(*Locator.QR_CODE)
                        curr_qr_binary = utils.extract_image_from_canvas(self._driver, qr_code_canvas)

                        if curr_qr_binary != qr_binary:
                            qr_binary = curr_qr_binary
                            self.trigger_event("on_qr_change", qr_binary)

                    except (StaleElementReferenceException, NoSuchElementException):
                        # If the QR code element is not found or has changed before extraction,
                        # ignore and continue (we will try again on the next poll).
                        pass

                # When logged in, check for unread chats
                elif curr_state == State.LOGGED_IN:

                    unread_chats = []

                    # Click the button showing unread chats
                    self._driver.find_element(*Locator.UNREAD_CHATS_BUTTON).click()
                    time.sleep(self.unread_messages_sleep)

                    # Retrieve unread chat elements and parse them
                    chat_list = self._driver.find_elements(*Locator.UNREAD_CHAT_DIV)
                    if len(chat_list) != 0:
                        chats = chat_list[0].find_elements(*Locator.SEARCH_ITEM)
                        for chat in chats:
                            chat_result = utils.parse_search_result(chat, "CHATS")
                            if chat_result is not None:
                                unread_chats.append(chat_result)

                    # Return to the view containing all chats
                    self._driver.find_element(*Locator.ALL_CHATS_BUTTON).click()

                    for chat in unread_chats:
                        self.trigger_event("on_unread_chat", chat)

            self.trigger_event("on_tick")
            await asyncio.sleep(self.poll_freq)

    def run(self):
        """
        Starts the main event loop in parallel with asyncio. This non-blocking
        behavior ensures that time.sleep-like delays (e.g., await asyncio.sleep)
        do not freeze the entire application.
        """
        self.running = True
        asyncio.run(self.main_loop())

    def stop(self):
        """
        Stops the main event loop and cleans up resources.
        """
        self.running = False
        self.quited = True
        self._driver.quit()

    def _get_state(self):

        if utils.is_present(self._driver, Locator.LOGGED_IN):
            return State.LOGGED_IN
        elif utils.is_present(self._driver, Locator.LOADING):
            return State.LOADING
        elif utils.is_present(self._driver, Locator.QR_CODE):
            return State.QR_AUTH
        elif utils.is_present(self._driver, Locator.AUTH):
            return State.AUTH

        return None

    def _click_search_button(self):
        """
        Attempts to click the search button on the page."

        The function uses ActionChains to simulate the mouse movement and click
        with an offset (10, 10) relative to the element's top-left corner. For
        some reason, Whatsapp Web wasn't registering clicking the buttom normally
        so this is a sloppy fix.
        """

        inactive_search_button = self._driver.find_elements(*Locator.SEARCH_BUTTON_INACTIVE)
        if len(inactive_search_button) != 0:
            ActionChains(self._driver).move_to_element_with_offset(inactive_search_button[0], 10, 10).click().perform()
            return True

        active_search_button = self._driver.find_elements(*Locator.SEARCH_BUTTON_ACTIVE)
        if len(active_search_button) != 0:
            ActionChains(self._driver).move_to_element_with_offset(active_search_button[0], 10, 10).click().perform()
            return True
        
        return False


    def get_recent_messages(self, search_field, sleep=1):
        """
        Searches for recent messages in a chat based on a provided search term.

        This function automates the process of clicking the search button, entering
        the search_field text, navigating within the search results, and extracting
        recent messages from the chat component.

        Workflow:
        1. Activate the search field by clicking the search button.
        2. Enter the provided search_field text into the search bar.
        3. Wait until the cancel search button is present, indicating that the search 
            has finished loading.
        4. Send a DOWN arrow keystroke to navigate to the first result.
        5. Wait until the chat div appears and retrieve its children.
        6. Pause for a specified duration (sleep) to allow chat items to load.
        7. Within the chat div, find all chat components.
            For each component:
                - Check for the presence of messages.
                - If a message element exists, parse it using utils.parse_message and add 
                the result to the messages list.
        8. Send an ESCAPE key to exit the search page.
        9. Click the search button again to reset the search view.
        10. Return the list of parsed messages.

        Notes:
        - The function relies on many helper utils and is very susceptible to bugs.
        - It doesn't handle many message types (e.g. polls, documents, etc) nor does
        it handle info messages (e.g. x has left the chat).
        """

        # Activate the search field by clicking the search button
        self._click_search_button()
        self._driver.switch_to.active_element.send_keys(search_field)

        # Wait until the cancel search button appears, i.e. results have loaded
        utils.await_exists(self._driver, Locator.CANCEL_SEARCH_BUTTON)
        self._driver.switch_to.active_element.send_keys(Keys.DOWN)

        messages = []
        chat_div = utils.await_exists(self._driver, Locator.CHAT_DIV)[0]

        # Pause briefly to allow messages to load - there may be a better way?
        time.sleep(sleep)

        chat_items = chat_div.find_elements(*Locator.CHAT_COMPONENT)
        for item in chat_items:
            
            # may want to consider other elements e.g. today/yesterday notifs etc
            message = item.find_elements(*Locator.CHAT_MESSAGE)
            if len(message) != 0:

                parsed_message = utils.parse_message(self._driver, message[0])
                messages.append(parsed_message)

        # Close the search by sending ESCAPE
        self._driver.switch_to.active_element.send_keys(Keys.ESCAPE)
        self._click_search_button()

        return messages

    def send_message(self, search_field, message):
        """
        Sends a message to a chat located via a search query.

        Workflow:
        1. Activates the search field and inputs the search query.
        2. Waits for the search to finish loading and navigates to the first chat.
        3. Clicks on the chat input box and sends the message followed by RETURN and ESCAPE keys.
        """

        self._click_search_button()
        self._driver.switch_to.active_element.send_keys(search_field)

        # Wait for the search to finish loading
        utils.await_exists(self._driver, Locator.CANCEL_SEARCH_BUTTON)
        self._driver.switch_to.active_element.send_keys(Keys.DOWN)

        # Send the message and then close the search page with ESCAPE
        utils.await_exists(self._driver, Locator.CHAT_INPUT_BOX)[0].click()
        self._driver.switch_to.active_element.send_keys(message, Keys.RETURN, Keys.ESCAPE)

    def search(self, search_field, sleep=1):
        """
        Searches for items using the given search_field and returns the parsed search results.

        Workflow:
        1. Activates the search field and inputs the search query.
        2. Waits for the search to finish loading and collects the search result container.
        3. Sleeps briefly to allow results to populate.
        4. Sorts the search items by their y positione, updates the current result type
            when a header-like item is detected, and parses each search result.
        5. Closes the search page and returns the list of parsed results.
        """

        self._click_search_button()
        self._driver.switch_to.active_element.send_keys(search_field)

        # Wait until the cancel search button is present, i.e. the search is loading
        utils.await_exists(self._driver, Locator.CANCEL_SEARCH_BUTTON)
        result = self._driver.find_elements(*Locator.SEARCH_RESULT)[0]

        results = []
        curr_type = None

        # Wait for a short period to allow search results to load
        time.sleep(sleep)

        result_items = result.find_elements(*Locator.SEARCH_ITEM)
        sorted_result_items = sorted(result_items, key=self.search_sort_key)

        for result in sorted_result_items:

            child_divs = result.find_elements(By.XPATH, "./div")

            if len(child_divs) == 1 and len(child_divs[0].find_elements(By.XPATH, "./*")) == 0:
                curr_type = child_divs[0].text

            else:

                search_result = utils.parse_search_result(result, curr_type)
                if search_result is not None:
                    results.append(search_result)

        # Close the search by sending ESCAPE
        self._click_search_button()

        return results
