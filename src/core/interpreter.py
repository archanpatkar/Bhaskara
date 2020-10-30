# !! Improvements needed
# Code smell very bad
# No concretely defined abstractions
# Ad-hoc evaluation

# Currently many aspects of the interpreter are metacircular in nature
# will shift to a completely independent implementation.
import sys
from runtime.pool import Pool
from runtime.object import Object
from runtime.ops import biopmap, unopmap
from runtime.env import Env, std_env
from protocol import overload_sig

# Prev. version working now ->
# WIP: Currently refactoring to CPS style
# Dependancies
ROOT = std_env()
GLOBAL_POOL = Pool(daemon=False)

class BFunction():
    def __init__(self, params, body, name, env):
        self.lexical_scope = env
        self.param_name = params
        self.body = body
        self.name = name

    def __call__(self, *actual, this=None, dyn=False):
        # if len(actual) < len(self.param_name):
        #     self.prev = {}
        #     for var in range(len(self.param_name)):
        #         prev[self.param_name[var]] = actual[var]
        #     curr = BFunction()
        # less = False
        outer = self.lexical_scope
        if dyn: outer = dyn
        frame = Env(outer=outer)
        frame.update({
            "args": actual,
            "this": this
        })
        for var in range(len(self.param_name)):
            frame.update({self.param_name[var]: actual[var]})
        return eval(self.body, frame)


class Thunk():
    def __init__(self, exp, env):
        self.exp = exp
        self.env = env
        self.reduced = False

    def __call__(self):
        if self.reduced:
            return self.exp
        else:
            self.reduced = True
            self.exp = eval(self.exp, self.env)
        return self.exp

# class Interpreter(object):
#     def __init__(self):
#         self.trace = []
#         self.current = None
#         pass

# def handleException(ast, env, cont):
#     pass

# def evalAsync(ast, env, cont):
#     pass

def evalLazy(ast, env, abort, next):
    return Thunk(ast["exp"], env)

def evalForce(ast, env, abort, next):
    exp = eval(ast["exp"], env)
    if isinstance(exp, Thunk):
        return exp()
    return exp

def evalBlock(ast, env, abort, next):
    outcome = []
    for exp in ast["exp"]:
        temp = eval(exp, env)
        if temp != '\n':
            outcome.append(temp)
        return outcome[-1]


def defFunction(ast, env, abort, next):
    f = None
    if ast["scope"] == "dyn":
        f = BFunction(ast["params"], ast["body"], ast["name"], None)
    else:
        f = BFunction(ast["params"], ast["body"], ast["name"], env)
    if ast["name"] != None:
        env.update({ast["name"]: f})
    return f


def evalMatch(ast, env, abort, next):
    obj = eval(ast["obj"], env)
    for case in ast["cases"]:
        if eval(case[0], env) == obj:
            if (not case[1]) or eval(case[1], env):
                return eval(case[2], env)
            elif case[0] == True:
                return eval(case[2], env)
    return None


def evalApply(ast, env, abort, next):
    obj = None
    func = eval(ast["iden"], env)
    if (not callable(func)) and (not (isinstance(func, dict) or isinstance(func, Object)) and func.get(overload_sig["CALL"]) == None):
        print("Function required")
        sys.exit(1)
    elif isinstance(func, Object) and func.get(overload_sig["CALL"]) != None:
        obj = func
        func = func.get(overload_sig["CALL"])
        params = [eval(e, env) for e in ast["actual"] if e != None]
        if func.lexical_scope:
            if obj and not(obj.native):
                return func(*params, this=obj)
            return func(*params)
        else:
            if obj and not(obj.native):
                return func(*params, this=obj, dyn=env)
            return func(*params, dyn=env)

def evalDecApply(ast, env, abort, next):
    func = eval(ast["iden"], env)
    if not callable(func):
        print("Function required")
        sys.exit(0)
    params = [eval(ast["actual"][0], env)]
    r = func(*params)
    if isinstance(r, BFunction) and params[0].name:
        r.name = params[0].name
        env.update({r.name: r})
    return r


def evalGo(ast, env, abort, next):
    func = eval(ast["ap"]["iden"], env)
    if not callable(func):
        print("Function required")
        sys.exit(1)
    params = [eval(e, env) for e in ast["ap"]["actual"] if e != None]
    o = GLOBAL_POOL.execute(func, params)
    if ast["chain"]:
        o["chain"](eval(ast["chain"]), o)
    return o


def evalWhile(ast, env, abort, next):
    cond = eval(ast["cond"], env)
    out = None
    while cond:
        out = eval(ast["body"], env)
        cond = eval(ast["cond"], env)
    return out


def evalFor(ast, env, abort, next):
    t = Env(outer=env)
    iter = eval(ast["iter"], env)
    out = None
    for val in iter:
        t.update({
            ast["var"]: val
        })
        out = eval(ast["body"], t)
    return out


def evalCond(ast, env, abort, next):
    if eval(ast["cond"], env):
        return eval(ast["b1"], env)
    elif ast["b2"] != None:
        return eval(ast["b2"], env)


def defList(ast, env, abort, next):
    return [eval(e, env) for e in ast["con"]]


def defObject(ast, env, abort, next):
    obj = Object()
    for e in ast["kv"]:
        if isinstance(e[0], str) or e[0]["type"] == "Atom":
            key = None
            if (not isinstance(e[0], str)) and e[0]["type"] == "Atom":
                key = e[0]["value"]
            else:
                key = e[0]
                obj.update({
                    key: eval(e[1], env)
                })
        else:
            abort("Expected identifier or string")
    return obj


def evalSAcc(ast, env, abort, next):
    obj = eval(ast["iden"], env)
    return obj[eval(ast["index"], env)]


def evalUnOp(ast, env, abort, next):
    if ast["op"] == "PANIC":
        print(eval(ast["right"], env))
        sys.exit(1)
    return unopmap[ast["op"]](eval(ast["right"], env))


def evalAssign(ast, env, abort, next):
    name = ast["left"]
    if (isinstance(name, dict) or isinstance(name, Object)) and name["type"] == "SAcc":
        obj = eval(name["iden"], env)
        index = eval(name["index"], env)
        val = eval(ast["right"], env)
        if isinstance(obj, list):
            obj[index] = val
        else:
            obj.update({index: val})
        return obj[index]
    elif (isinstance(name, dict) or isinstance(name, Object)) and (name.get("op") == "DOT" or name.get("op") == "OPDOT"):
        obj = eval(name["left"], env)
        index = name["right"]["value"]
        val = eval(ast["right"], env)
        obj.update({index: val})
        return obj[index]
    else:
        val = eval(ast["right"], env)
        env[name["value"]] = val
        return val


def evalDot(ast, env, abort, next):
    obj = eval(ast["left"], env)
    if ast["right"]["type"] == "Apply":
        func = obj[ast["right"]["iden"]["value"]]
        if not callable(func):
            print("Function required")
            sys.exit(1)
        params = [eval(e, env) for e in ast["right"]["actual"] if e != None]
        if obj.native:
            return func(*params)
        return func(*params, this=obj)
    else:
        index = ast["right"]["value"]
        return obj[index]


def evalOpDot(ast, env, abort, next):
    obj = eval(ast["left"], env)
    if ast["right"]["type"] == "Apply":
        func = obj.get(ast["right"]["iden"]["value"])
        if func is None:
            return False
        if not callable(func):
            print("Function required")
            sys.exit(1)
        params = [eval(e, env) for e in ast["right"]["actual"] if e != None]
        return func(*params, this=obj)
    else:
        index = ast["right"]["value"]
        if obj.get(index):
            return obj[index]
        return False


def evalBinOp(ast, env, abort, next):
    if ast["op"] == "VAR":
        name = ast["left"]["value"]
        val = eval(ast["right"], env)
        env.update({name: val})
        return val
    elif ast["op"] == "ASGN":
        return evalAssign(ast, env, abort, next)
    elif ast["op"] == "DOT":
        return evalDot(ast, env, abort, next)
    elif ast["op"] == "OPDOT":
        return evalOpDot(ast, env, abort, next)
    else:
        left = eval(ast["left"], env, abort, next)
        right = eval(ast["right"], env, abort, next)
        if isinstance(left, Object) and ast["op"] != "LPIPE" and ast["op"] != "RPIPE":
            f = left[overload_sig[ast["op"]]]
            if not callable(f):
                abort("Function required")
            r = f(right, this=left)
            return r
        return biopmap[ast["op"]](left, right)

eval_map = {
    "Lazy":evalLazy,
    "Force":evalForce,
    "Block":evalBlock,
    "Func":defFunction,
    "Match":evalMatch,
    "Apply":evalApply,
    "DecApply":evalDecApply,
    "Go":evalGo,
    "Binary":evalBinOp,
    "Unary":evalUnOp,
    "While":evalWhile,
    "For":evalFor,
    "Cond":evalCond,
    "List":defList,
    "Obj":defObject,
    "SAcc":evalSAcc
}

def I(x): return x
def Error(msg):
    if(isinstance(msg,Object)):
        pass
    else:
        print(msg)
        sys.exit(1)

def eval(ast, env=ROOT, abort=Error, next=I):
    if isinstance(ast, list):
        outcome = []
        for exp in ast:
            outcome.append(eval(exp, env, abort, next))
        return next(outcome)
    elif isinstance(ast, dict) or isinstance(ast, Object):
        if ast["type"] == "Lit":
            return next(ast["val"])
        elif ast["type"] == "SExpr":
            return next(ast["l"])
        elif ast["type"] == "Atom":
            return next(env[ast["value"]])
        else:
            eval_func = eval_map.get(ast["type"])
            if eval_func: 
                return next(eval_func(ast, env, abort, next))
            else:
                abort("Unrecognizable AST Node")
    else:
        abort("Unrecognizable AST Node")
