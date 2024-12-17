from redshot import Client
from redshot.auth import LocalProfileAuth

import numpy as np
import asyncio
import cv2
import os

class Whatsapp:

    def __init__(self):

        auth = LocalProfileAuth(os.path.abspath("./data_dir"))
        self.client = Client(auth=auth)
        self.qr_task = None

        self.client.event("on_loading")(self.on_loading)
        self.client.event("on_qr")(self.on_qr)
        self.client.event("on_qr_change")(self.on_qr_change)
        self.client.event("on_logged_in")(self.on_logged_in)

    def on_loading(self, loading_chats):
        if loading_chats:
            self.close_qr_window()

    def on_qr(self, qr):
        if self.qr_task is None or self.qr_task.done():
            self.qr_task = asyncio.create_task(self.display_qr_window(qr))

    def on_qr_change(self, new_qr):
        if self.qr_task is None or self.qr_task.done():
            self.qr_task = asyncio.create_task(self.display_qr_window(new_qr))
        else:
            image = cv2.imdecode(np.frombuffer(new_qr, np.uint8), 1)
            cv2.imshow("Scan in Whatsapp", image)

    def on_logged_in(self):
        print("Successfully logged in!")
        if self.qr_task is not None:
            self.close_qr_window()
        messages = self.client.get_recent_messages("test")
        for message in messages:
            print(message.as_string())
        self.client.stop()

    async def display_qr_window(self, qr):

        image = cv2.imdecode(np.frombuffer(qr, np.uint8), 1)
        cv2.imshow("Scan in Whatsapp", image)
        cv2.setWindowProperty("Scan in Whatsapp", cv2.WND_PROP_TOPMOST, 1)

        while self.qr_task is not None:
            cv2.waitKey(100)
            await asyncio.sleep(0.1)

        cv2.destroyAllWindows()

    def close_qr_window(self):
        if self.qr_task is not None:
            self.qr_task.cancel()
            self.qr_task = None
        cv2.destroyAllWindows()

if __name__ == "__main__":

    whatsapp = Whatsapp()
    whatsapp.client.run()