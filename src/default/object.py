# Start defining the Object system 
# The object system should in it itself be complete and serializable to JSON

class Object(dict):
    def __init__(self):
        self.writable = True

    def get(self,key):
        pass

    def set(self,key):
        pass