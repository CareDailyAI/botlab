"""
BotError exception class for botlab
"""

class BotError(Exception):
    """BotEngine exception to raise and log errors."""

    def __init__(self, msg, code):
        super(BotError).__init__(type(self))
        self.msg = msg
        self.code = code

    def __str__(self):
        return self.msg

    def __unicode__(self):
        return self.msg