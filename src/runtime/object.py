# Start defining the Object system 
# The object system should in it itself be complete and serializable to JSON
class Object:
    def __init__(self):
        self.writable = True
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
        return None

    def __setitem__(self,key,val):
        self.props.update({key: val})
        return self.props[key]

