class NotUniqueMatching(Exception):
    def __init__(self, attr):
        self.message = "Attribut Eingabe nicht eindeutig."
        super().__init__(self.message)
        self.attr = attr

class NotExistingMatching(Exception):
    def __init__(self, attr):
        self.message = "Attribut Eingabe existiert nicht."
        super().__init__(self.message)
        self.attr = attr

class AlreadyExisistingError(Exception):
    def __init__(self, attr):
        self.message = "Das Attribut existiert bereits."
        super().__init__(self.message)
        self.attr = attr

class TooManyInputs(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class SpecificError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class CustomCommandEnd(Exception):
    def __init__(self, message="Attribut Eingabe existiert nicht."):
        self.message = message
        super().__init__(self.message)
