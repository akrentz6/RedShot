from enum import Enum

class State(Enum):

    LOGGED_IN = "logged_in"
    LOADING = "loading"
    QR_AUTH = "qr_auth"
    AUTH = "auth"