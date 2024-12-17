

class SearchResult:

    def __init__(self, result_type, title, datetime, info, unread_messages, group=None):

        self.result_type = result_type
        self.title = title
        self.datetime = datetime
        self.info = info
        self.unread_messages = unread_messages
        self.group = group

    def has_group(self):
        return self.group is not None

    def as_string(self):

        string = (f"{self.result_type}:"
                  f"\n  Title: {self.title}"
                  f"\n  Datetime: {self.datetime}"
                  f"\n  Info: {self.info}"
                  f"\n  Unread Messages: {self.unread_messages}")

        if self.has_group():
            string += f"\n  Group: {self.group}"

        return string