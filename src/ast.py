def BinOp(op,left,right):
    return { "type":"Binary", "left":left, "op":op, "right":right }

def UnOp(op,value):
    return { "type":"Unary", "op":op, "right":value }

def Block(exps):
    return { "type":"Block", "exp":exps }

def CondOp(cond,b1,b2):
    return { "type":"Cond", "cond": cond, "b1":b1, "b2":b2 }

def Func(name,params,body):
    return { "type":"Func", "name":name, "params":params, "body":body }

def Atom(value):
    return { "type":"Atom", "value":value }

def Apply(iden,actual):
    return { "type":"Apply", "iden":iden, "actual":actual }

# Add functions Loop, While Loop, Pattern Matcher etc.