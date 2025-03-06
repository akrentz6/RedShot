from dataclasses import dataclass
from typing import Optional

@dataclass
class SearchResult:

    result_type: str
    title: str
    datetime: str
    info: str
    unread_messages: int
    group: Optional[str] = None

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