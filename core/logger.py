from datetime import datetime

class Log:
    def __init__(self, file) -> None:
        self.file = file
    
    def write(self, text):
        with open(self.file, "a") as f:
            f.write(
                f"[{datetime.now()}]--[{text}]\n"
            )