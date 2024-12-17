from redshot.auth import AuthBase

class NoAuth(AuthBase):

    def __init__(self):
        super().__init__()

    def add_arguments(self, options):
        pass