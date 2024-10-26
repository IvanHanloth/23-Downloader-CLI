class NoInputError(Exception):
    def __init__(self, message="No input provided"):
        self.message = message
        super().__init__(self.message)
                         
class NotValidURL(Exception):
    def __init__(self, message="Not a valid URL"):
        self.message = message
        super().__init__(self.message)

