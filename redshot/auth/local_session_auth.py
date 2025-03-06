from redshot.auth import AuthBase

class LocalSessionAuth(AuthBase):

    # Work in progress - uses the extract_session.js and inject_session.js files

    def extract_session(self, driver, session_file):

        js_code = open("auth/extract_session.js", "r").read()
        session_data = driver.execute_script(js_code, "wawc", "user")

        if session_data is None:
            return False

        with open(session_file, "w", encoding="utf-8") as file:
            file.write(str(session_data))

        return True

    def inject_session(self, driver, session_file):

        js_code = open("auth/inject_session.js", "r").read()
        with open(session_file, "r", encoding="utf-8") as file:
            driver.execute_script(js_code, "wawc", "user", file.read())

        driver.refresh()