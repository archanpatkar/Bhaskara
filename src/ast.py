# Convert to the Object system after it is fully defined
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

def While(cond,body):
    return { "type":"While", "cond":cond, "body":body }

def For(var,iter,body):
    return { "type":"For", "var":var, "iter":iter, "body":body }

def List(con): 
    return { "type":"List", "con":con }

def SAccessor(iden,index):
    return { "type":"SAcc", "iden":iden, "index":index }

def ObjectLit(kv):
    return { "type":"Obj", "kv":kv }

def Go(ap,then=None):
    return { "type":"Go", "ap":ap, "chain": then }

def Lazy(exp):
    return { "type":"Lazy", "exp": exp }

def Literal(v):
    return { "type":"Lit", "val":v }

def Match(obj,cases,wild):
    return { "type":"Match", "obj":obj , "cases":cases, "wild":wild }

# Add Pattern Matcher, Sum types etc.