from runtime.object import Object
import threading

# Will shift this to a new module later on
class TSQueue:
    def __init__(self):
        self.q = [];
        self.monitor = threading.Condition();

    def enqueue(self,msg):
        with self.monitor:
            self.q.append(msg)
            self.monitor.notify()

    def dequeue(self):
        with self.monitor:
            if(self.isEmpty()):
                self.monitor.wait()
            msg = self.q[0]
            self.q.pop(0)
            return msg
 
    def isEmpty(self):
        return (len(self.q) == 0);

class Channel(Object):
    def __init__(self):
        super().__init__(native=True)
        self.buff = TSQueue()

    # This is intentional due to the current execution style of interpreter 
    def send(self,msg,this):
        print("-------channel--------")
        print(msg)
        print(self)
        self.buff.enqueue(msg)

    def recv(self,this):
        # print("-------channel--------")
        # print(temp)
        # print(this)
        return this.buff.dequeue()
