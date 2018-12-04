from enum import Enum, unique
@unique
class MessageType(Enum):
    PRIVATE = 1
    LOGOUT = 2
    ALIAS = 3
    TEST = 4
    ALIAS_ASSERTION = 5
    PUBLIC = 6
    ERROR = 7

class Message():
    def __init__(self, messageType, content=None, targetName=None): 
        self.type = messageType
        self.content = content
        self.targetName = targetName

    def __str__(self):
        return self.content