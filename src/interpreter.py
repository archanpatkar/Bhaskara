import math

opmap = {
    "ADD": lambda x,y: x + y,
    "SUBS": lambda x,y: x - y,
    "MUL": lambda x,y: x * y,
    "MOD": lambda x,y: x % y,
    "DIV": lambda x,y: x / y,
    "NEG": lambda x: -x,
    "POS": lambda x: +x,
    "NOT": lambda x: not(x),
    "AND": lambda x,y: x and y,
    "OR": lambda x,y: x or y,
    "LT": lambda x,y: x < y,
    "GT": lambda x,y: x > y,
    "EQ": lambda x,y: x == y,
    "GTEQ":lambda x,y: x >= y,
    "LTEQ":lambda x,y: x <= y,
    "NOTEQ": lambda x,y: x != y,
    "IMP": lambda x,y: not(x) or y,
    "EXP": math.pow,
    "LPIPE": lambda x,y: y(x),
    "RPIPE": lambda x,y: x(y)
}

class Env(dict):
    def __init__(self , params = () , args = () , outer = None):
        self.update(zip(params,args))
        self.outer = outer
    
    def find(self,var):
        if var in self:
            return self[var];
        elif self.outer != None:
            return self.outer.find(var)
        return None
    
    def updateVar(self,var,value):
        if var in self:
            self[var] = value
            return value
        elif self.outer != None:
            return self.outer.updateVar(var,value)
        else:
            print("Error: Cannot update non-existant variable -->",var)
            # sys.exit(1)


def std_env():
    env = Env()
    env.update(vars(math))
    env.update({
        "print":print,
        "abs":abs
    })
    return env