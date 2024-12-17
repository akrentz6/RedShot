from redshot import Client
from redshot.auth import LocalProfileAuth

import numpy as np
import asyncio
import cv2
import os

auth = LocalProfileAuth(os.path.abspath("./data_dir"))
client = Client(auth)

async def display_image(qr):
    image = cv2.imdecode(np.frombuffer(qr, np.uint8), 1)
    cv2.imshow("Scan in Whatsapp", image)
    while cv2.getWindowProperty('Scan in Whatsapp', 0) >= 0:
        cv2.waitKey(100)
        await asyncio.sleep(0.1)

@client.event("on_start")
def on_start():
    print("Client has started.")

@client.event("on_qr")
def on_qr(qr):
    print("QR scan is required to sign in.")
    asyncio.create_task(display_image(qr))

@client.event("on_logged_in")
def on_logged_in():
    print("Client has successfully logged in!")
    cv2.destroyAllWindows()
    messages = client.get_recent_messages("test")
    for message in messages:
        print(message.as_string())
    client.stop()

client.run()
