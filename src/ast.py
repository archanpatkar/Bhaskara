# import uuid
import random

counter = 1

# Convert to the Object system after it is fully defined
def BinOp(op,left,right):
    global counter
    counter += 1
    return { "id": counter, "type":"Binary", "left":left, "op":op, "right":right }

def UnOp(op,value):
    global counter
    counter += 1
    return { "id": counter, "type":"Unary", "op":op, "right":value }

def Block(exps):
    global counter
    counter += 1
    return { "id": counter, "type":"Block", "exp":exps }

def CondOp(cond,b1,b2,other=None):
    global counter
    counter += 1
    return { "id": counter, "type":"Cond", "cond": cond, "b1":b1, "other":other ,"b2":b2 }

def Func(name,params,body):
    global counter
    counter += 1
    return { "id": counter, "type":"Func", "name":name, "params":params, "body":body }

def Atom(value):
    global counter
    counter += 1
    return { "id": counter, "type":"Atom", "value":value }

def Apply(iden,actual):
    global counter
    counter += 1
    return { "id": counter, "type":"Apply", "iden":iden, "actual":actual }

def DecApply(iden,actual):
    global counter
    counter += 1
    return { "id": counter, "type":"DecApply", "iden":iden, "actual":actual }

def Spread(iter):
    global counter
    counter += 1
    return { "id": counter, "type":"Spread", "iter":iter }

def While(cond,body):
    global counter
    counter += 1
    return { "id": counter, "type":"While", "cond":cond, "body":body }

def For(var,iter,body):
    global counter
    counter += 1
    return { "id": counter, "type":"For", "var":var, "iter":iter, "body":body }

def List(con): 
    global counter
    counter += 1
    return { "id": counter, "type":"List", "con":con }

def SAccessor(iden,index):
    global counter
    counter += 1
    return { "id": counter, "type":"SAcc", "iden":iden, "index":index }

def ObjectLit(kv):
    global counter
    counter += 1
    return { "id": counter, "type":"Obj", "kv":kv }

def Go(ap,then=None):
    global counter
    counter += 1
    return { "id": counter, "type":"Go", "ap":ap, "chain": then }

def Lazy(exp):
    global counter
    counter += 1
    return { "id": counter, "type":"Lazy", "exp": exp }

def Force(exp):
    global counter
    counter += 1
    return { "id": counter, "type":"Force", "exp":exp }

def Literal(v):
    global counter
    counter += 1
    return { "id": counter, "type":"Lit", "val":v }

def SExpr(l):
    global counter
    counter += 1
    return { "id":counter, "type":"SExpr", "l":l }

def Match(obj,cases):
    global counter
    counter += 1
    return { "id": counter, "type":"Match", "obj":obj , "cases":cases}

# Add Pattern Matcher, Sum types etc.