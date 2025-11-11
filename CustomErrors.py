class NotUniqueMatching(Exception):

    def init(self, message):
        self.message = message
        super().init(self.message)
    
class NotExistingMatching(Exception):

    def init(self, message):
        self.message = message
        super().init(self.message)