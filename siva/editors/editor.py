

class Editor:
    def __init__(self):
        self._menu = {}

    def save(self):
        raise NotImplementedError

    def save_as(self):
        raise NotImplementedError

    def close(self):
        print("Closing ", self)
        raise NotImplementedError


