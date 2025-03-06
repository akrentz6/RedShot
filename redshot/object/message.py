from dataclasses import dataclass
from typing import Optional

@dataclass
class MessageInfo:

    time: str
    date: str
    user: str

    def as_string(self):
        return f"[{self.time} {self.date}] {self.user}:".replace("\n", "\\n")

@dataclass
class MessageQuote:

    user: str
    text: str

    def as_string(self):
        return f"Quote ({self.user}): {self.text}".replace("\n", "\\n")

@dataclass
class MessageLink:

    title: str
    description: str
    url: str

    def as_string(self):
        return f"Link ({self.title} - {self.url}): {self.description}".replace("\n", "\\n")

@dataclass
class MessageImage:

    binary: str

    def _file_size(self):
        
        y = 2 if self.binary.endswith("==") else (1 if self.binary.endswith("=") else 0)
        return int((len(self.binary) * (3/4))) - y

    def _format_size(self):

        size_bytes = self._file_size()

        for unit in ["B", "KB", "MB"]:
            
            if size_bytes < 1024:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024

        return f"{size_bytes:.2f}{unit[-1]}"

    def as_string(self):
        return f"Image: {self.binary[:10]}... ({self._format_size()})"

@dataclass
class Message:

    info: MessageInfo
    text: str
    quote: Optional[MessageQuote] = None
    link: Optional[MessageLink] = None
    image: Optional[MessageImage] = None

    def has_quote(self):
        return self.quote is not None

    def has_link(self):
        return self.link is not None
    
    def has_image(self):
        return self.image is not None

    def as_string(self):

        string = (f"{self.info.as_string()}"
                  f"\n  Text: {self.text.replace("\n", "\\n")}")

        if self.has_quote():
            string += f"\n  {self.quote.as_string()}"
        if self.has_link():
            string += f"\n  {self.link.as_string()}"
        if self.has_image():
            string += f"\n  {self.image.as_string()}"

        return string