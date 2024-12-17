from redshot.auth import AuthBase

class LocalProfileAuth(AuthBase):

    def __init__(self, data_dir, profile="selenium"):

        super().__init__()

        self.data_dir = data_dir
        self.profile = profile

    def add_arguments(self, options):

        options.add_argument(f"--user-data-dir={self.data_dir}")
        options.add_argument(f"--profile-directory={self.profile}")


