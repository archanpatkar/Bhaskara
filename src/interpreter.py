import math
# from env import *
import sys
from runtime.pool import Pool
from runtime.object import Object
from runtime.channel import Channel
# from parser import Parser
# from lexer import Tokenizer

# Currently many aspects of the interpreter are metacircular in nature
# will shift to a completely independent implementation.

# Refactor to CPS style
# !! Improvements needed
# Code smell very bad 
# No concretely defined abstractions 
# Ad-hoc evaluation
biopmap = {
    "ADD": lambda x,y: x + y,
    "SUBS": lambda x,y: x - y,
    "MUL": lambda x,y: x * y,
    "MOD": lambda x,y: x % y,
    "DIV": lambda x,y: x / y,
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
    "RPIPE": lambda x,y: x(y),
    "RANGE": lambda x,y: list(range(x,y))
}

overload_sig = {
    "ADD":"__add__",
    "SUBS":"__sub__",
    "MUL":"__mul__",
    "DIV":"__div__",
    "LT":"__lt__",
    "GT":"__gt__",
    "AND":"__and__",
    "OR":"__or__",
    "EQ":"__eq__",
    "SHIFT":"__compose__",
    "CALL":"__call__"
}

unopmap = {
    "SUBS": lambda x: -x,
    "ADD": lambda x: +x,
    "NOT": lambda x: not(x)
}


class Env(dict):
    def __init__(self , params = () , args = () , outer = None):
        self.update(zip(params,args))
        self.outer = outer
    
    def find(self,var):
        if var in self:
            return self[var]
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
        "len":len,
        "range":range,
        "channel": Channel
    })
    return env

ROOT = std_env()
GLOBAL_POOL = Pool(daemon=False)

class BFunction(dict):
    def __init__(self, params,body,name,env):
        self.lexical_scope = env
        self.param_name = params
        self.body = body
        self.name = name

    def __call__(self,*actual,this=None):
        if len(actual) < len(self.param_name):
            self.prev = {}
            for var in range(len(self.param_name)):
                prev[self.param_name[var]] = actual[var]
            curr = BFunction()
        frame = Env(outer=self.lexical_scope)
        less = False
        frame.update({
            "args":actual,
            "this":this
        })

        for var in range(len(self.param_name)):
            frame.update({self.param_name[var]:actual[var]})
        return eval(self.body,frame)

class Thunk(dict):
    def __init__(self,exp,env):
        self.exp = exp
        self.env = env
        self.reduced = False
    
    def __call__(self):
        if self.reduced:
            return self.exp
        else:
            self.reduced = True
            self.exp = eval(self.exp,self.env)
        return self.exp

def eval(ast,env=ROOT):
    # print("-----------------Eval-----------------")
    # pprint(ast,indent=4)
    if isinstance(ast,list):
        outcome = []
        for exp in ast:
            outcome.append(eval(exp,env))
        return outcome
    elif isinstance(ast,dict) or isinstance(ast,Object):
        if ast["type"] == "Lit":
            return ast["val"]
        if ast["type"] == "SExpr":
            return ast["l"]
        if ast["type"] == "Lazy":
            return Thunk(ast["exp"],env)
        if ast["type"] == "Force":
            exp = eval(ast["exp"],env)
            if isinstance(exp,Thunk):
                return exp()
            return exp
        if ast["type"] == "Block":
            outcome = []
            for exp in ast["exp"]:
                temp = eval(exp,env)
                if temp != '\n':
                    outcome.append(temp)
            # print(outcome)
            return outcome[-1]
        elif ast["type"] == "Func":
            f = BFunction(ast["params"],ast["body"],ast["name"],env)
            if ast["name"] != None:
                env.update({ast["name"]:f})
            return f
        elif ast["type"] == "Match":
            obj = eval(ast["obj"],env)
            for case in ast["cases"]:
                if eval(case[0],env) == obj:
                    if (not case[1]) or eval(case[1],env):
                        return eval(case[2],env)
                elif case[0] == True:
                   return eval(case[2],env) 
            return None
        elif ast["type"] == "Apply":
            obj = None
            func = eval(ast["iden"],env)
            # print(ast["iden"])
            # print(func)
            if (not callable(func)) and (not (isinstance(func,dict) or isinstance(func,Object)) and func.get(overload_sig["CALL"]) == None) :
                # print(dir(func))
                # print(func.keys())
                # print(func[overload_sig["CALL"]])
                print("Function required")
                return
                # sys.exit(0)
            if isinstance(func,Object) and func.get(overload_sig["CALL"]) != None:
                obj = func
                # print(func)
                func = func.get(overload_sig["CALL"])
            # print(ast["actual"])
            params = [eval(e,env) for e in ast["actual"] if e != None]
            # print("lalalal")
            # print(ast["iden"])
            # r = None
            if obj and not(obj.native): 
                return func(*params,this=obj)
            return func(*params)
            # print(r)
            # return r
        elif ast["type"] == "DecApply":
            func = eval(ast["iden"],env)
            if not callable(func):
                print("Function required")
                sys.exit(0)
            # print(ast["actual"])
            params = [eval(ast["actual"][0],env)]
            # print(params)
            # print("lalalal")
            # print(ast["iden"])
            # print(func)
            # print(ast)
            r = func(*params)
            # print(params)
            if isinstance(r,BFunction) and params[0].name:
                r.name = params[0].name
                env.update({r.name: r})
            return r
        elif ast["type"] == "Go":
            # print(ast)
            func = eval(ast["ap"]["iden"],env)
            if not callable(func):
                print("Function required")
                sys.exit(0)
            # print(ast["actual"])
            params = [eval(e,env) for e in ast["ap"]["actual"] if e != None]
            # print(params)
            # print("lalalal")
            # print(ast["iden"])
            # r = 
            # print("here")
            o = GLOBAL_POOL.execute(func,params)
            if ast["chain"]:
                o["chain"](eval(ast["chain"]),o)
            return o
        elif ast["type"] == "Binary":
            if ast["op"] == "VAR":
                name = ast["left"]["value"]
                val = eval(ast["right"],env)
                env.update({name:val})
                return val
            elif ast["op"] == "ASGN":
                name = ast["left"]
                if (isinstance(name,dict) or isinstance(name,Object)) and name["type"] == "SAcc":
                    obj = eval(name["iden"],env)
                    index = eval(name["index"],env)
                    val = eval(ast["right"],env)
                    if isinstance(obj,list):
                        obj[index] = val
                    else:
                        obj.update({index: val})
                    return obj[index]
                elif (isinstance(name,dict) or isinstance(name,Object)) and (name.get("op") == "DOT" or name.get("op") == "OPDOT"):
                    obj = eval(name["left"],env)
                    index = name["right"]["value"]
                    # print("this is here!")
                    # print(obj)
                    # print(index)
                    val = eval(ast["right"],env)
                    # print(val)
                    obj.update({index: val})
                    return obj[index]
                else:
                    val = eval(ast["right"],env)
                    return env.updateVar(name["value"],val)
            elif ast["op"] == "DOT":
                # print(ast)
                obj = eval(ast["left"],env)
                if ast["right"]["type"] == "Apply":
                    func = obj[ast["right"]["iden"]["value"]]
                    if not callable(func):
                        print("Function required")
                        sys.exit(0)
                    params = [eval(e,env) for e in ast["right"]["actual"] if e != None]
                    print("here---->method execution")
                    print(params)
                    print(obj)
                    if obj.native:
                        return func(*params)
                    return func(*params,this=obj)
                else:
                    index = ast["right"]["value"]
                    # print("Accessing!")
                    # print(obj)
                    # print(index)
                    return obj[index]
            elif ast["op"] == "OPDOT":
                obj = eval(ast["left"],env)
                if ast["right"]["type"] == "Apply":
                    func = obj.get(ast["right"]["iden"]["value"])
                    if func is None:
                        return False 
                    if not callable(func):
                        print("Function required")
                        sys.exit(0)
                    params = [eval(e,env) for e in ast["right"]["actual"] if e != None]
                    return func(*params,this=obj)
                else:
                    index = ast["right"]["value"]
                    if obj.get(index):
                        return obj[index]
                    return False
            else:
                # print(ast)
                # ast["left"] = eval(ast["left"],env)
                # ast["right"] = eval(ast["right"],env)
                # print(ast["left"])
                # print(ast["right"])
                left = eval(ast["left"],env)
                right = eval(ast["right"],env)
                if isinstance(left,Object) and ast["op"] != "LPIPE" and ast["op"] != "RPIPE":
                    f = left[overload_sig[ast["op"]]]
                    if not callable(f):
                        print("Function required")
                        sys.exit(0)
                    r = f(right,this=left)
                    return r
                return biopmap[ast["op"]](left,right)
        elif ast["type"] == "Unary":
            if ast["op"] == "PANIC":
                print(eval(ast["right"],env))
                sys.exit(1)
            # ast["right"] = eval(ast["right"],env)
            return unopmap[ast["op"]](eval(ast["right"],env))
        elif ast["type"] == "While":
            cond = eval(ast["cond"],env)
            out = ""
            while cond:
                out = eval(ast["body"],env)
                cond = eval(ast["cond"],env)
            # print(out)
            return out
        elif ast["type"] == "For":
            t = Env(outer=env)
            iter = eval(ast["iter"],env)
            for val in iter:
                t.update({
                    ast["var"]:val
                })
                out = eval(ast["body"],t)
            # print(out)
            return out
        elif ast["type"] == "Cond":
            # ast["cond"] = 
            if eval(ast["cond"],env):
                return eval(ast["b1"],env)
            elif ast["b2"] != None:
                return eval(ast["b2"],env)
        elif ast["type"] == "Atom":
            # print(ast["value"])
            return env.find(ast["value"])
        elif ast["type"] == "List":
            l = [eval(e,env) for e in ast["con"]]
            return l
        # elif ast["type"] == "Go":
        #     l = [eval(e,env) for e in ast["con"]]
        #     return l
        elif ast["type"] == "Obj":
            obj = Object()
            for e in ast["kv"]:
                if isinstance(e[0],str) or e[0]["type"] == "Atom":
                    key = None
                    if (not isinstance(e[0],str)) and e[0]["type"] == "Atom":
                        key = e[0]["value"]
                    else:
                        key = e[0]
                    obj.update({
                        key:eval(e[1],env)
                    })
                else:
                    print("Expected identifier or string")
                    sys.exit(1)
            # l = [obj.update({eval(e,env) for e in ast["kv"]]
            return obj
        elif ast["type"] == "SAcc":
            obj = eval(ast["iden"],env)
            return obj[eval(ast["index"],env)]
    else:
        return ast

# def run(str):
#     tokens = tokenize(str)
#     ast = parse(tokens)
#     return eval(ast)