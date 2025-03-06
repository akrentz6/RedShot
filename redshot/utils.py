from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

import base64
import re

from redshot.object import Message, MessageInfo, MessageQuote, MessageLink, MessageImage, SearchResult
from redshot.constants import Locator

def format_locators(locators):
    if len(locators) == 2 and isinstance(locators[0], str) and isinstance(locators[1], str):
        return [locators]
    else:
        return locators

def is_present(parent, locators):
    locators_list = format_locators(locators)
    return all(len(parent.find_elements(*locator)) for locator in locators_list)

def _handle_await(parent, locators, timeout, poll_freq, reverse):

    expected_conditions = [EC.presence_of_all_elements_located(locator) for locator in locators]
    if reverse:
        expected_condition = EC.none_of(*expected_conditions)
    else:
        expected_condition = EC.all_of(*expected_conditions)

    try:
        return WebDriverWait(parent,
                             timeout,
                             poll_frequency=poll_freq
                             ).until(expected_condition)[0]

    except TimeoutException:
        return None

def await_exists(parent, locators, timeout=0, poll_freq=0.05, reverse=False):

    locators_list = format_locators(locators)

    if timeout == 0:
        while True:
            res = _handle_await(parent, locators_list, timeout, poll_freq, reverse)
            if res is not None:
                return res
    else:
        return _handle_await(parent, locators_list, timeout, poll_freq, reverse)

def extract_image_from_canvas(driver, canvas):

    canvas_url = driver.execute_script("return arguments[0].toDataURL('image/png');", canvas)
    canvas_base64 = re.search(r"base64,(.*)", canvas_url).group(1)

    return base64.b64decode(canvas_base64)

def parse_message_info(message):

    message_info_text = message.get_attribute("data-pre-plain-text")
    message_info_comps = re.search(r"(\d{2}:\d{2}).*?(\d{1,2}/\d{1,2}/\d{4})\] (.*?):", message_info_text)

    if message_info_comps is not None:
        return MessageInfo(*message_info_comps.groups())

    return MessageInfo(None, None, None)

get_base64_img_js = """
var img = arguments[0];
var canvas = document.createElement('canvas');
canvas.width = img.naturalWidth;
canvas.height = img.naturalHeight;
var ctx = canvas.getContext('2d');
ctx.drawImage(img, 0, 0);
return canvas.toDataURL('image/png');
"""

def parse_message_image(driver, message):

    message_images = message.find_elements(*Locator.CHAT_MESSAGE_IMAGE)
    if len(message_images) != 0:
        
        message_image_elements = message_images[0].find_elements(*Locator.CHAT_MESSAGE_IMAGE_ELEMENT)
        if len(message_image_elements) != 0:
            
            img_url = driver.execute_script(get_base64_img_js, message_image_elements[0])
            img_base64 = re.search(r'base64,(.*)', img_url).group(1)

            return MessageImage(img_base64)

    return None

def parse_message_quote(quote_text):

    quote_comps = quote_text.split("\n")

    try:
        quote_user_comp = quote_comps[0]
        quote_text_comp = "\n".join(quote_comps[1:])
        return MessageQuote(quote_user_comp, quote_text_comp)

    except IndexError:
        return None

def parse_message_link(link_text):

    link_comps = link_text.split("\n")

    try:
        link_title_comp = link_comps[0]
        link_desc_comp = "\n".join(link_comps[1:-1])
        link_url_comp = link_comps[-1]
        return MessageLink(link_title_comp, link_desc_comp, link_url_comp)

    except IndexError:
        return None

def parse_message(driver, message):

    message_children = message.find_elements(By.XPATH, "./div")
    message_quote = message.find_elements(*Locator.CHAT_MESSAGE_QUOTE)
    message_info = parse_message_info(message)
    message_image = parse_message_image(driver, message)
    
    # len(message_quote) != 0 should be redundant
    if len(message_children) == 3 and len(message_quote) != 0:

        quote_text = message_quote[0].text
        quote = parse_message_quote(quote_text)

        link_text = message_children[1].text
        link = parse_message_link(link_text)

        message_text = message.text.replace(quote_text, "").replace(link_text, "").lstrip("\n")
        return Message(message_info, message_text, quote=quote, link=link, image=message_image)

    elif len(message_quote) != 0:

        quote_text = message_quote[0].text
        quote = parse_message_quote(quote_text)

        message_text = message.text.replace(quote_text, "").lstrip("\n")
        return Message(message_info, message_text, quote=quote, image=message_image)

    elif len(message_children) == 2:

        link_text = message_children[0].text
        link = parse_message_link(link_text)

        message_text = message.text.replace(link_text, "").lstrip("\n")
        return Message(message_info, message_text, link=link, image=message_image)

    else:
        message_text = message.text
        return Message(message_info, message_text, image=message_image)

def parse_search_result(search_result, search_type):

    result_comps = search_result.find_elements(*Locator.SEARCH_ITEM_COMPONENTS)
    unread_messages = search_result.find_elements(*Locator.SEARCH_ITEM_UNREAD_MESSAGES)
    unread_count = unread_messages[0].text if len(unread_messages) != 0 else 0

    # for chats with group
    if len(result_comps) == 3:

        result_group = result_comps[0].find_element(*Locator.SPAN_TITLE).get_attribute("title")
        result_datetime = result_comps[0].find_elements(By.XPATH, "./*")[1].text
        result_title = result_comps[1].find_element(*Locator.SPAN_TITLE).get_attribute("title")
        result_info = result_comps[2].text.replace("\n", "")  # add support for emojis via img alt attribute

        return SearchResult(search_type, result_title, result_datetime, result_info, unread_count, group=result_group)

    elif len(result_comps) == 2:

        result_title = result_comps[0].find_element(*Locator.SPAN_TITLE).get_attribute("title")
        result_datetime = result_comps[0].find_elements(By.XPATH, "./*")[1].text
        result_info = result_comps[1].find_elements(By.XPATH, "./*")[0].text.replace("\n", "")  # add support for emojis via img alt attribute

        return SearchResult(search_type, result_title, result_datetime, result_info, unread_count)

    return None