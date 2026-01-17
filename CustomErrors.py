class NotEnoughSpellSlots(Exception):

    def init(self, message):
        self.message = message
        super().init(self.message)

class NotUniqueMatching(Exception):

    def init(self, message):
        self.message = message
        super().init(self.message)


class NotExistingMatching(Exception):

    def init(self, message):
        self.message = message
        super().init(self.message)


class CustomCommandEnd(Exception):

    def init(self, message):
        self.message = message
        super().init(self.message)


class TooManyInputs(Exception):

    def init(self, message):
        self.message = message
        super().init(self.message)