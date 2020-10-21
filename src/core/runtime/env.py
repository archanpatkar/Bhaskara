import math
from object import Object
from channel import Channel

class Env(object):
    def __init__(self, outer = None):
        super().__init__()
        self["__proto__"] = outer

def std_env():
    env = Env()
    env.update(vars(math))
    env.update({
        "print":print,
        "len":len,
        "range":range,
        "channel": Channel
    })
    return env