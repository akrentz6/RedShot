# RedShot

`RedShot` is an event-based Python package that provides a Selenium wrapper for automating WhatsApp Web workflows. It allows you to interact with WhatsApp Web to send and receive messages, search chats, and more.

Whatsapp Web is constantly changing so this library is very susceptible to breaking and bugs. I'll do my best to fix these as soon as possible. Also, expect much more functionality in future updates.

**Note:** Use this library at your own risk. Whatsapp does not allow the unauthorised use of automated or bulk messaging. 

## Table of Contents

- [Installation](#installation)

- [Quick Start](#quick-start)

- [Authentication](#authentication)

- [Client Initialisation](#client-initialisation)

- [Events](#events)

- [Client Functions](#client-functions)

- [Objects](#objects)

- [To Do List](#to-do-list)

## Installation

```bash
pip install redshot
```

## Quick Start

See the examples folder for more.

```python
from redshot import Client

client = Client()

@client.event("on_start")
def on_start():
    print("Client has started")
    client.stop()

client.run()
```

## Authentication

Whatsapp Web allows users to connect their whatsapp web to their phone via by scanning a QR code in the app. To allow for this session data to persist between script executions, we can implement different authentication strategies.

Currently, there is two working authentication strategies: `LocalProfileSession` that uses the chrome user data directory and `NoAuth` which saves no information between sessions:

`redshot.auth.LocalProfileSession(data_dir, profile="selenium")`

Parameters:
- data_dir: The chrome user data directory to be used
- profile: The chrome profile to be used

`redshot.auth.NoAuth()`

## Client Initialisation

`redshot.Client(auth=None, poll_freq=0.25, unread_messages_sleep=0.5, headless=True)`

Parameters:
- auth: An authentication strategy (if None this defaults to `NoAuth`)
- poll_freq: Time between polls of the whatsapp webpage
- unread_messages_sleep: Time waited for the unread messages section to load
- headless: If true, the chrome UI interface won't be displayed

## Events

Events listeners are instantiated using the `redshot.Client.event` decorator as follows:

```python
@client.event("on_event")
def on_event(*event_args):
    print("Event triggered!")
```

Event types:
- `on_start`: Called once the chrome driver object has been created and has opened https://web.whatsapp.com/
- `on_auth`: Called when the authentication screen appears
- `on_qr`: Called when the qr code has loaded in the authentication screen
  - Arguments:
<br />`qr` - the QR code image's binary string
- `on_qr_change`: Called when a new qr code is generated in the authentication screen (if the old qr code wasn't scanned in time)
  - Arguments:
<br />`new_qr` - The new QR code image's binary string
- `on_loading`: Called when a loading screen appears:
  - Arguments:
<br />`loading_chats`: True if the loading screen appears as a result of the qr code being scanned
- `on_logged_in`: Called when the client successfully logs in
- `on_unread_chat`: Called on each poll of the mainloop with an unread chat
  - Arguments:
<br />`chat`: A `SearchResult` object containing information about the unread chat
- `on_tick`: Called at the end of each tick of the mainloop

## Client Functions

`redshot.Client.run()`: Begins the client main loop (in an `asyncio` thread).

`redshot.Client.stop()`: Stops the client's main loop once the current tick of the main loop is complete.
<br />Note that the `stop` method should be run within the main loop's thread i.e. in an event listener.
<br />Also, calling `stop` too soon after `send_message` may cause the message not to be sent (depending on internet speeds).

`redshot.Client.get_recent_messages(search_field, sleep=1)`: Get's the recent messages from the first chat in the search results.

Parameters:
- `search_field`: Used in the whatsapp searchbar to find the given chat

`redshot.Client.send_message(search_field, message)`: Sends a message to the first chat in the search results.

Parameters:
- `search_field`: Used in the whatsapp searchbar to find the given chat
- `message`: The message to be sent to the given chat

`redshot.Client.search(search_field)`: Returns a list of `SearchResult` containing: chats, groups in common, contacts, messages.

Parameters:
- `search_field`: Used in the whatsapp searchbar to obtain the search results

## Objects

Class `redshot.object.Message`:

- `info`: A `MessageInfo` object
- `text`: A string containing the message's text
- `quote`: A `MessageQuote` object
- `link`: A `MessageLink` object
- `has_quote()`: True if the `Message` contains a quote
- `has_link()`: True if the `Message` contains a link
- `as_string()`: A formatted string of the message contents

Class `redshot.object.MessageInfo`:

- `time`: The time the message was sent
- `date`: The date the message was sent
- `user`: The user who sent the message
- `as_string()`: A formatted string of the message info contents

Class `redshot.object.MessageQuote`:

- `user`: The user who sent the quoted message
- `text`: The text in the quoted message
- `as_string()`: A formatted string of the message quote contents

Class `redshot.object.MessageLink`:

- `title`: The title of the linked url
- `description`: The description of the linked url
- `url`: The linked url
- `as_string()`: A formatted string of the message link contents

Class `redshot.object.MessageImage`:

- `binary`: The base64 string of the image
- `as_string()`: A formatted string of the message image contents

Class `redshot.object.SearchResult`:

- `result_type`: The search result type
- `title`: The search result's time
- `datetime`: The search result's datetime (either a date or a time)
- `info`: The search result's info section
- `unread_messages`: The number of unread messages
- `group`: The group the search result is in (if the search result is a chat)

## To Do List

- [x] ~~Add a `MessageImage` class and parse images in messages~~
- [ ] Parse emojis within messages and other contexts
- [ ] Add support for users to override locators in case of bugs
- [ ] Replace `time.sleep` for waiting for messages or search results to load
- [ ] Implement better error handling
- [ ] Add support for more features - chat descriptions/info, polls, images, files etc
- [ ] Find a way to save data between sessions without using a user data directory. See [here](https://stackoverflow.com/questions/79154388/how-to-inject-whatsapp-web-session-to-stay-logged-in-with-selenium) (suggestions are more than welcome). Also look at `redshot.auth.LocalSessionAuth` for updates.