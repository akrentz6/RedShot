from typing import List
from selenium.webdriver.common.by import By

class Locator:

    AUTH = (By.XPATH, "//div[contains(text(), 'Use WhatsApp on your computer')]")
    QR_CODE = (By.XPATH, "//canvas[@aria-label='Scan this QR code to link a device!']")
    LOADING = (By.XPATH, "//div[//span[@data-icon='lock'] and contains(text(), 'End-to-end encrypted') and //progress]")
    LOADING_CHATS = (By.XPATH, "//div[text()='Loading your chats']")
    LOGGED_IN = (By.XPATH, "//div[@title='Chats']")

    CHATS_BUTTON = (By.XPATH, "//div[@aria-label='Chats']")
    STATUS_BUTTON = (By.XPATH, "//div[@aria-label='Status']")
    CHANNELS_BUTTON = (By.XPATH, "//div[@aria-label='Channels']")
    COMMUNITIES_BUTTON = (By.XPATH, "//div[@aria-label='Communities']")

    ALL_CHATS_BUTTON = (By.XPATH, "//div[text()='All']")
    UNREAD_CHATS_BUTTON = (By.XPATH, "//div[text()='Unread']")
    FAVOURITES_CHATS_BUTTON = (By.XPATH, "//div[text()='Favourites']")
    GROUPS_CHATS_BUTTON = (By.XPATH, "//div[text()='Groups']")

    SEARCH_BUTTON_INACTIVE = (By.XPATH, "//button[@aria-label='Search or start new chat']")
    SEARCH_BUTTON_ACTIVE = (By.XPATH, "//button[@aria-label='Chat list']")
    CANCEL_SEARCH_BUTTON = (By.XPATH, "//button[@aria-label='Cancel search']")

    CHAT_INPUT_BOX = (By.XPATH, "//div[@aria-placeholder='Type a message']")

    SEARCH_RESULT = (By.XPATH, "//div[@aria-label='Search results.']")
    SEARCH_ITEM = (By.XPATH, "//div[@role='listitem']")
    SEARCH_ITEM_COMPONENTS = (By.XPATH, ".//div[@role='gridcell' and @aria-colindex='2']/parent::div/div")
    SEARCH_ITEM_UNREAD_MESSAGES = (By.XPATH, ".//span[contains(@aria-label, 'unread message')]")
    SPAN_TITLE = (By.XPATH, ".//span[@title]")

    CHAT_DIV = (By.XPATH, "//div[@role='application']")
    UNREAD_CHAT_DIV = (By.XPATH, "//div[@aria-label='Chat list']")
    CHAT_COMPONENT = (By.XPATH, ".//div[@role='row']")
    CHAT_MESSAGE_DATA_ID = (By.XPATH, ".//div[@data-id]")
    CHAT_MESSAGE = (By.XPATH, ".//div[@data-pre-plain-text]")
    CHAT_MESSAGE_QUOTE = (By.XPATH, ".//div[@aria-label='Quoted message']")
    CHAT_MESSAGE_IMAGE = (By.XPATH, ".//div[@aria-label='Open picture']")
    CHAT_MESSAGE_IMAGE_ELEMENT = (By.XPATH, ".//img[starts-with(@src, 'blob:https://web.whatsapp.com')]")

    @classmethod
    def set_locator(cls, locator_name: str, locator: tuple) -> bool:
        """
        Sets a specific locator to a new value.

        Parameters:
            locator_name (str): The name of the locator you want to update.
            locator (tuple): The new locator tuple (e.g., (By.ID, "new_id_value")).
        """
        name = locator_name.upper()

        if hasattr(cls, name):
            setattr(cls, name, locator)
            return True
        
        return False

    @classmethod
    def set_locators(cls, locators: dict) -> List[bool]:
        """
        Bulk-updates multiple locators.

        Parameters:
            locators (dict): A dictionary where keys are locator names (str) and values are the new locator tuples.
        """
        return [cls.set_locator(key, value) for key, value in locators.items()]
        
    @classmethod
    def get_locator(cls, locator_name: str):
        """
        Retrieves a locator tuple by name.

        Parameters:
            locator_name (str): The name of the locator.

        Returns:
            tuple: The locator tuple if found, else None.
        """
        return getattr(cls, locator_name.upper(), None)
    