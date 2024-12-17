

class MessageInfo:

    def __init__(self, time, date, user):

        self.time = time
        self.date = date
        self.user = user

    def as_string(self):
        return f"[{self.time} {self.date}] {self.user}:".replace("\n", "\\n")

class MessageQuote:

    def __init__(self, user, text):

        self.user = user
        self.text = text

    def as_string(self):
        return f"Quote ({self.user}): {self.text}".replace("\n", "\\n")

class MessageLink:

    def __init__(self, title, description, url):

        self.title = title
        self.description = description
        self.url = url

    def as_string(self):
        return f"Link ({self.title} - {self.url}): {self.description}".replace("\n", "\\n")

class Message:

    def __init__(self, info, text, quote=None, link=None):

        self.info = info
        self.text = text
        self.quote = quote
        self.link = link

    def has_quote(self):
        return self.quote is not None

    def has_link(self):
        return self.link is not None

    def as_string(self):

        string = (f"{self.info.as_string()}"
                  f"\n  Text: {self.text.replace("\n", "\\n")}")

        if self.has_quote():
            string += f"\n  {self.quote.as_string()}"
        if self.has_link():
            string += f"\n  {self.link.as_string()}"

        return string