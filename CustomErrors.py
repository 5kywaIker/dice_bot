class NotUniqueMatching(Exception):

    def init(self, message):
        self.message = message
        super().init(self.message)
    
class NotExistingMatching(Exception):

    def init(self, message):
        self.message = message
        super().init(self.message)

class Custom_Command_End(Exception):

    def init(self, message):
        self.message = message
        super().init(self.message)

class Too_Many_Inputs(Exception):

    def init(self, message):
        self.message = message
        super().init(self.message)
