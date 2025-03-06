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

        self._driver = self._init_driver()
        self._driver.get("https://web.whatsapp.com")

        qr_binary = None
        state = None

        self.trigger_event("on_start")

        while self.running:

            curr_state = self._get_state()

            if curr_state is None:
                await asyncio.sleep(self.poll_freq)
                continue

            elif curr_state != state:

                match curr_state:

                    case State.AUTH:
                        self.trigger_event("on_auth")

                    case State.QR_AUTH:

                        qr_code_canvas = self._driver.find_element(*Locator.QR_CODE)
                        qr_binary = utils.extract_image_from_canvas(self._driver, qr_code_canvas)

                        self.trigger_event("on_qr", qr_binary)

                    case State.LOADING:
                        loading_chats = utils.is_present(self._driver, Locator.LOADING_CHATS)
                        self.trigger_event("on_loading", loading_chats)

                    case State.LOGGED_IN:
                        self.trigger_event("on_logged_in")

                state = curr_state

            else:

                if curr_state == State.QR_AUTH:

                    try:

                        qr_code_canvas = self._driver.find_element(*Locator.QR_CODE)
                        curr_qr_binary = utils.extract_image_from_canvas(self._driver, qr_code_canvas)

                        if curr_qr_binary != qr_binary:
                            qr_binary = curr_qr_binary
                            self.trigger_event("on_qr_change", qr_binary)

                    except (StaleElementReferenceException, NoSuchElementException):
                        pass

                elif curr_state == State.LOGGED_IN:

                    unread_chats = []
                    self._driver.find_element(*Locator.UNREAD_CHATS_BUTTON).click()

                    time.sleep(self.unread_messages_sleep)

                    chat_list = self._driver.find_elements(*Locator.UNREAD_CHAT_DIV)
                    if len(chat_list) != 0:

                        chats = chat_list[0].find_elements(*Locator.SEARCH_ITEM)

                        for chat in chats:

                            chat_result = utils.parse_search_result(chat, "CHATS")
                            if chat_result is not None:
                                unread_chats.append(chat_result)

                    self._driver.find_element(*Locator.ALL_CHATS_BUTTON).click()

                    for chat in unread_chats:
                        self.trigger_event("on_unread_chat", chat)

            self.trigger_event("on_tick")
            await asyncio.sleep(self.poll_freq)

    def run(self):

        self.running = True
        asyncio.run(self.main_loop())

    def stop(self):

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

        self._click_search_button()
        self._driver.switch_to.active_element.send_keys(search_field)

        utils.await_exists(self._driver, Locator.CANCEL_SEARCH_BUTTON)
        self._driver.switch_to.active_element.send_keys(Keys.DOWN)

        messages = []
        chat_div = utils.await_exists(self._driver, Locator.CHAT_DIV)[0]

        time.sleep(sleep)

        chat_items = chat_div.find_elements(*Locator.CHAT_COMPONENT)
        for item in chat_items:
            
            # may want to consider other elements e.g. today/yesterday notifs etc
            message = item.find_elements(*Locator.CHAT_MESSAGE)
            if len(message) != 0:

                parsed_message = utils.parse_message(self._driver, message[0])
                messages.append(parsed_message)

        self._driver.switch_to.active_element.send_keys(Keys.ESCAPE)
        self._click_search_button()

        return messages

    def send_message(self, search_field, message):

        self._click_search_button()
        self._driver.switch_to.active_element.send_keys(search_field)

        utils.await_exists(self._driver, Locator.CANCEL_SEARCH_BUTTON)
        self._driver.switch_to.active_element.send_keys(Keys.DOWN)

        utils.await_exists(self._driver, Locator.CHAT_INPUT_BOX)[0].click()
        self._driver.switch_to.active_element.send_keys(message, Keys.RETURN, Keys.ESCAPE)

    def search(self, search_field, sleep=1):

        self._click_search_button()
        self._driver.switch_to.active_element.send_keys(search_field)

        utils.await_exists(self._driver, Locator.CANCEL_SEARCH_BUTTON)
        result = self._driver.find_elements(*Locator.SEARCH_RESULT)[0]

        results = []
        curr_type = None

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

        self._click_search_button()

        return results
