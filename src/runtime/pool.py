import threading
import inspect
import os

class TSQueue:
    def __init__(self):
        self.q = [];
        self.monitor = threading.Condition();

    def enqueue(self,msg):
        with self.monitor:
            self.q.append(msg)
            self.monitor.notify(1)

    def dequeue(self):
        with self.monitor:
            if(self.isEmpty()):
                self.monitor.wait()
            msg = self.q[0]
            self.q.pop(0)
            return msg
 
    def isEmpty(self):
        return (len(self.q) == 0);

class Pool:
    def __init__(self,workers = os.cpu_count(),daemon=True):
        self.workers = []
        self.jobs = TSQueue()
        for i in range(workers):
            worker = Worker(self)
            self.workers.append(worker)
            worker.setDaemon(daemon)
            worker.start()

    def execute(self,job,args=None):
        if callable(job):
            p = Outcome()
            self.jobs.enqueue((job,args,p))
            return p

class Worker(threading.Thread):
    def __init__(self,pool):
        super().__init__()
        self.pool = pool

    def run(self):
        while True:
            job,args,p = self.pool.jobs.dequeue()
            if inspect.isgeneratorfunction(job):
                if args != None:
                    job = job(*args)
                else:
                    job = job()
                self.pool.jobs.enqueue((job,args,p))
            elif inspect.isgenerator(job):
                try:
                    if not next(job): self.pool.jobs.enqueue((job,args,p))
                except StopIteration:
                    p.resolve()
            else:
                try:
                    if args != None:
                        p.resolve(job(*args))
                    else:
                        p.resolve(job())
                except Exception as e:
                    print(e)
                    p.reject(e)

# TODO:
    # Allow recursive chaining of Outcomes
    # Follow Promise/A+ spec
class Outcome:
    def __init__(self,executor=None):
        self.state = 0
        self.success = []
        self.failure = []
        if executor != None: executor(self.resolve,self.reject)

    def resolve(self,value=None):
        if self.state == 0:
            self.value = value
            self.state = 1
            for handler in self.success:
                handler(self.value)

    def reject(self,err=None):
        if self.state == 0:
            self.value = err
            self.state = -1
            for handler in self.failure:
                handler(self.value)

    def __getitem__(self,str):
        if str == "chain" or str == "after":
            return lambda x,this=None: this.then(x)

    def then(self,success,failure=None):
        if callable(success): self.success.append(success)
        if callable(failure): self.failure.append(failure)
        return self        