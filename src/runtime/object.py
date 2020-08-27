# Start defining the Object system 
# The object system should in it itself be complete and serializable to JSON
class Object:
    # Native flag is temp patch will improve this
    def __init__(self,native=False):
        # self.writable = True
        self.native = native
        self.props = {}

    def update(self,d):
        self.props.update(d)

    def get(self,key):
        return self[key]

    def __srt__(self):
        return self.props

    def __getitem__(self,key):
        if key in self.props:
            return self.props.get(key)
        elif self.props.get("__proto__"):
            print(self.props.get("__proto__"))
            return self.props.get("__proto__")[key]
        elif self.native:
            return self.__getattribute__(key)
        return None

    def __setitem__(self,key,val):
        if self.native:
            self.__setattr__(key,val)
            return self.__getattribute__(key)
        self.props.update({key: val})
        return self.props[key]

