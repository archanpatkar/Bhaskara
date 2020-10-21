# Basic implementation
# Next one will be written in Bhaskara itself (self hosted)
# Compiler to Javascript
def createFile(filename, content):
    open(filename,"w").write(content)

def evalLazy(ast, buff):
    return Thunk(ast["exp"], buff)

def evalForce(ast, buff):
    exp = compile(ast["exp"], buff)
    if isinstance(exp, Thunk):
        return exp()
    return exp

def evalBlock(ast, buff):
    outcome = []
    for exp in ast["exp"]:
        temp = compile(exp, buff)
        if temp != '\n':
            outcome.append(temp)
        return outcome[-1]


def defFunction(ast, buff):
    f = None
    if ast["scope"] == "dyn":
        f = BFunction(ast["params"], ast["body"], ast["name"], None)
    else:
        f = BFunction(ast["params"], ast["body"], ast["name"], buff)
    if ast["name"] != None:
        buff.update({ast["name"]: f})
    return f


def evalMatch(ast, buff):
    obj = compile(ast["obj"], buff)
    for case in ast["cases"]:
        if compile(case[0], buff) == obj:
            if (not case[1]) or compile(case[1], buff):
                return compile(case[2], buff)
            elif case[0] == True:
                return compile(case[2], buff)
    return None


def evalApply(ast, buff):
    obj = None
    func = compile(ast["iden"], buff)
    if (not callable(func)) and (not (isinstance(func, dict) or isinstance(func, Object)) and func.get(overload_sig["CALL"]) == None):
        print("Function required")
        sys.exit(1)
    elif isinstance(func, Object) and func.get(overload_sig["CALL"]) != None:
        obj = func
        func = func.get(overload_sig["CALL"])
        params = [compile(e, buff) for e in ast["actual"] if e != None]
        if func.lexical_scope:
            if obj and not(obj.native):
                return func(*params, this=obj)
            return func(*params)
        else:
            if obj and not(obj.native):
                return func(*params, this=obj, dyn=buff)
            return func(*params, dyn=buff)

def evalDecApply(ast, buff):
    func = compile(ast["iden"], buff)
    if not callable(func):
        print("Function required")
        sys.exit(0)
    params = [compile(ast["actual"][0], buff)]
    r = func(*params)
    if isinstance(r, BFunction) and params[0].name:
        r.name = params[0].name
        buff.update({r.name: r})
    return r


def evalGo(ast, buff):
    func = compile(ast["ap"]["iden"], buff)
    if not callable(func):
        print("Function required")
        sys.exit(1)
    params = [compile(e, buff) for e in ast["ap"]["actual"] if e != None]
    o = GLOBAL_POOL.execute(func, params)
    if ast["chain"]:
        o["chain"](compile(ast["chain"]), o)
    return o


def evalWhile(ast, buff):
    cond = compile(ast["cond"], buff)
    out = None
    while cond:
        out = compile(ast["body"], buff)
        cond = compile(ast["cond"], buff)
    return out


def evalFor(ast, buff):
    t = buff(outer=buff)
    iter = compile(ast["iter"], buff)
    out = None
    for val in iter:
        t.update({
            ast["var"]: val
        })
        out = compile(ast["body"], t)
    return out


def evalCond(ast, buff):
    if compile(ast["cond"], buff):
        return compile(ast["b1"], buff)
    elif ast["b2"] != None:
        return compile(ast["b2"], buff)


def defList(ast, buff):
    return [compile(e, buff) for e in ast["con"]]


def defObject(ast, buff):
    obj = Object()
    for e in ast["kv"]:
        if isinstance(e[0], str) or e[0]["type"] == "Atom":
            key = None
            if (not isinstance(e[0], str)) and e[0]["type"] == "Atom":
                key = e[0]["value"]
            else:
                key = e[0]
                obj.update({
                    key: compile(e[1], buff)
                })
        else:
            print("Expected identifier or string")
            sys.exit(1)
    return obj


def evalSAcc(ast, buff):
    obj = compile(ast["iden"], buff)
    return obj[compile(ast["index"], buff)]


def evalUnOp(ast, buff):
    if ast["op"] == "PANIC":
        print(compile(ast["right"], buff))
        sys.exit(1)
    return unopmap[ast["op"]](compile(ast["right"], buff))


def evalAssign(ast, buff):
    name = ast["left"]
    if (isinstance(name, dict) or isinstance(name, Object)) and name["type"] == "SAcc":
        obj = compile(name["iden"], buff)
        index = compile(name["index"], buff)
        val = compile(ast["right"], buff)
        if isinstance(obj, list):
            obj[index] = val
        else:
            obj.update({index: val})
        return obj[index]
    elif (isinstance(name, dict) or isinstance(name, Object)) and (name.get("op") == "DOT" or name.get("op") == "OPDOT"):
        obj = compile(name["left"], buff)
        index = name["right"]["value"]
        val = compile(ast["right"], buff)
        obj.update({index: val})
        return obj[index]
    else:
        val = compile(ast["right"], buff)
        buff[name["value"]] = val
        return val


def evalDot(ast, buff):
    obj = compile(ast["left"], buff)
    if ast["right"]["type"] == "Apply":
        func = obj[ast["right"]["iden"]["value"]]
        if not callable(func):
            print("Function required")
            sys.exit(1)
        params = [compile(e, buff) for e in ast["right"]["actual"] if e != None]
        if obj.native:
            return func(*params)
        return func(*params, this=obj)
    else:
        index = ast["right"]["value"]
        return obj[index]


def evalOpDot(ast, buff):
    obj = compile(ast["left"], buff)
    if ast["right"]["type"] == "Apply":
        func = obj.get(ast["right"]["iden"]["value"])
        if func is None:
            return False
        if not callable(func):
            print("Function required")
            sys.exit(1)
        params = [compile(e, buff) for e in ast["right"]["actual"] if e != None]
        return func(*params, this=obj)
    else:
        index = ast["right"]["value"]
        if obj.get(index):
            return obj[index]
        return False


def evalBinOp(ast, buff):
    if ast["op"] == "VAR":
        name = ast["left"]["value"]
        val = compile(ast["right"], buff)
        buff.update({name: val})
        return val
    elif ast["op"] == "ASGN":
        return evalAssign(ast, buff)
    elif ast["op"] == "DOT":
        return evalDot(ast, buff)
    elif ast["op"] == "OPDOT":
        return evalOpDot(ast, buff)
    else:
        left = compile(ast["left"], buff)
        right = compile(ast["right"], buff)
        if isinstance(left, Object) and ast["op"] != "LPIPE" and ast["op"] != "RPIPE":
            f = left[overload_sig[ast["op"]]]
            if not callable(f):
                print("Function required")
                sys.exit(1)
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

def compile(ast, buff=[]):
    if isinstance(ast, list):
        outcome = []
        for exp in ast:
            outcome.append(compile(exp, buff))
        return outcome
    elif isinstance(ast, dict) or isinstance(ast, Object):
        if ast["type"] == "Lit":
            if isinstance(ast["val"],bool):
                if ast["val"]: buff.append("true")
                else: buff.append("false")
            else: 
                buff.append("{}".format(ast["val"]))
        elif ast["type"] == "SExpr":
            return ast["l"]
        elif ast["type"] == "Atom":
            return buff[ast["value"]]
        else:
            func = eval_map.get(ast["type"])
            if func: return func(ast,buff)
            else:
                print("Unrecognizable AST Node")
                sys.exit(1)
    else:
        print("Unrecognizable AST Node")
        sys.exit(1)
