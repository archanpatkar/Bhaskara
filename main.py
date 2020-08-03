import math
from os import sys
from pprint import pprint
from collections import namedtuple
from panim import *
from src.tokens import *
from src.ast import *
from src.parser import *
from src.interpreter import *
from src.runtime.pool import Pool
import json

# भास्कर - A Math and Logic DSL
# Parser and Evaluator uses Precedence Climbing LR(1) Algorithm
# Based on: http://www.engr.mun.ca/~theo/Misc/exp_parsing.htm
def isWhite(str):
    if str in white:
        return True
    return False

def isNumber(str):
    if str in digits:
        return True
    return False 

def parseNum(str,i,l):
    decimal = False
    buff = "" + str[i]
    i += 1
    while i < l:
        c = str[i]
        if isNumber(c):
            buff += c
            i += 1
        elif c == "." and not(decimal):
            decimal = True
            buff += c
            i += 1
        else:
            i -= 1
            break
    if decimal:
        buff = float(buff)
    else:
        buff = int(buff)
    return (Token("NUM",buff),i)

def isBool(str):
    if str in bools:
        return True
    return False

def isIdentifier(str):
    n = ord(str)
    if  (n >= ord('a') and n <= ord('z')) or (n >= ord('A') and n <= ord('Z')) or str == "_":
        return True
    return False

def isKeyword(str):
    if str in keywords:
        return True
    return False

def createKeyword(buff):
    if buff == "true":
        return Token("BOOL",True)
    elif buff == "false":
        return Token("BOOL",False)
    elif buff == "unit":
        return Token("UNIT","unit")
    else:
        return Token(token_name[buff],buff)

def parseIdentifier(str,i,l):
    buff = "" + str[i]
    i += 1
    while i < l:
        c = str[i]
        if isIdentifier(c) or isNumber(c):
            buff += c
            i += 1
        else:
            i -= 1
            break
    if isKeyword(buff):
        return (createKeyword(buff),i)
    return (Token("IDEN",buff),i)

def parseString(str,i,l):
    buff = ""
    i += 1
    c = ""
    while i < l:
        c = str[i]
        if c != '"':
            buff += c
            # print(c)
            i += 1
        else:
            break
    if c != '"':
        print('Unmatched string `"`')
        sys.exit(0)
    return (Token("STR",buff),i)


def isNext(ch,str,i):
    if len(str) > i+1:
        if callable(ch):
            return ch(str[i+1])
        if str[i+1] == ch:
            return True
    return False
    
def joinNext(ch,str,i,tokens):
    j = ch+str[i+1]
    tokens.append(Token(token_name[j],j))

def tokenize(str):
    tokens = []
    i = 0
    l = len(str)
    buff = ""
    while i < l:
        c = str[i]
        # print(c)
        # print(tokens)
        if c == "/" and isNext("/",str,i):
            i += 2
            c = str[i]
            while c != "\n":
                i += 1
                if i < l:
                    c = str[i]
                else: break
        elif c == '"':
            t,i = parseString(str,i,l)
            # print(t)
            tokens.append(t)
        elif isNumber(c):
            num,i = parseNum(str,i,l)
            tokens.append(num)
        elif isBool(c) and not(isNext(isIdentifier,str,i)) and not(isNext(isNumber,str,i)):
            if c == "T":
                tokens.append(Token("BOOL",True))
            else:
                tokens.append(Token("BOOL",False))
        elif c in ops:
            if c == "=" and isNext("=",str,i):
                joinNext(c,str,i,tokens)
                i += 1
            elif c == ">" and isNext("=",str,i):
                joinNext(c,str,i,tokens)
                i += 1
            elif c == "<" and isNext("=",str,i):
                joinNext(c,str,i,tokens)
                i += 1
            elif c == "~" and isNext("=",str,i):
                joinNext(c,str,i,tokens)
                i += 1
            elif c == "-" and isNext(">",str,i):
                joinNext(c,str,i,tokens)
                i += 1
            elif c == ":" and isNext("=",str,i):
                joinNext(c,str,i,tokens)
                i += 1
            elif c == "|" and isNext(">",str,i):
                joinNext(c,str,i,tokens)
                i += 1
            elif c == "<" and isNext("|",str,i):
                joinNext(c,str,i,tokens)
                i += 1
            elif c == "*" and isNext("*",str,i):
                joinNext(c,str,i,tokens)
                i += 1
            elif c == "<" and isNext("-",str,i):
                joinNext(c,str,i,tokens)
                i += 1
            elif c == "?" and isNext(".",str,i):
                joinNext(c,str,i,tokens)
                i += 1
            elif c == "<" and isNext("-",str,i):
                joinNext(c,str,i,tokens)
                i += 1
            else:
                tokens.append(Token(token_name[c],c))
        elif isIdentifier(c):
            t,i = parseIdentifier(str,i,l)
            tokens.append(t)
        elif c == "\n" or c == ";":
            tokens.append(Token("LINEEND",c))            
        i+=1
    tokens.append(Token("EOF",""))
    return tokens

def getNext(tokens):
    if len(tokens) > 0:
        return tokens.pop(0)
    return None

def peekNext(tokens):
    if len(tokens) > 0:
        return tokens[0]
    return None

def parse(tokens):
    exps = []
    while len(tokens) > 0:
        out = exp(0,tokens)
        if isinstance(out,dict):
            exps.append(out)
        # if out == None:
            # break
    return exps

FLAG_IGNORE_LN = False

def verify(op,lhs,rhs):
    if op.type == "VAR" or op.type == "ASSGN":
        if not(lhs["type"] == "Atom"):
            print("Expected Identifier")
            sys.exit(1)

def exp(min,tokens):
    lhs = term(tokens)
    lookahead = peekNext(tokens)
    while (lookahead != None) and (lookahead.val != "\n" and lookahead.type != "EOF") and (lookahead.type in binaryops) and (opconfig[lookahead.type][0] >= min):
        op = getNext(tokens)
        n = opconfig[op.type][0]
        if opconfig[op.type][1] == 1:
            n += 1
        lhs = BinOp(op.type,lhs,exp(n,tokens))
        lookahead = peekNext(tokens)
    if lookahead != None and (lookahead.type == "LINEEND" or lookahead.type == "EOF"):
        getNext(tokens)
    return lhs

def expect(ttype,tokens):
    if peekNext(tokens).type == ttype:
        return getNext(tokens)
    foreground(RED) 
    print("Expected {}".format(ttype))
    foreground(WHITE) 

def term(tokens):
    current = peekNext(tokens)
    # print("*********************************************")
    # pprint(current,indent=4)
    # pprint(tokens,indent=4)
    if current == None or current.type == "EOF":
        return
    elif current.type == 'LPAREN':
        getNext(tokens)
        out = exp(0,tokens)
        # print(out)
        # print(peekNext(tokens))
        if getNext(tokens).type != "RPAREN":
            print("Unmatched paren '('")
            sys.exit(1)
        return out
    elif current.type in unaryops:
        getNext(tokens)
        ch = swap.get(current.type)
        if ch:
            return UnOp(ch,exp(opconfig[current.type][0],tokens))
        else:
            return UnOp(current.type,exp(opconfig[current.type][0],tokens))
    elif current.type == "IF":
        getNext(tokens)
        cond = exp(0,tokens)
        if peekNext(tokens).type == "LCURL":
            pass
        elif getNext(tokens).type != "THEN":
            print("Expected 'then'")
            sys.exit(1)
        b1 = exp(0,tokens)
        b2 = None
        t = peekNext(tokens)
        if t != None and t.type == "ELSE":
            getNext(tokens)
            b2 = exp(0,tokens)
        return CondOp(cond,b1,b2)
    elif current.type == "FOR":
        getNext(tokens)
        if peekNext(tokens).type != "IDEN":
            print("Expected an identifier")
            sys.exit(1)
        iden = getNext(tokens).val
        if peekNext(tokens).type != "IN":
            print("Expected an `in`")
            sys.exit(1)
        getNext(tokens)
        if peekNext(tokens).type != "IDEN":
            print("Expected an identifier")
            sys.exit(1)
        iter = exp(0,tokens)
        if peekNext(tokens).type == "LCURL":
            pass
        elif getNext(tokens).type != "DO":
            print("Expected 'do'")
            sys.exit(1)
        body = exp(0,tokens)
        return For(iden,iter,body)
    elif current.type == "WHILE":
        getNext(tokens)
        cond = exp(0,tokens)
        if peekNext(tokens).type == "LCURL":
            pass
        elif getNext(tokens).type != "DO":
            print("Expected 'do'")
            sys.exit(1)
        body = exp(0,tokens)
        return While(cond,body)
    elif current.type == "GO":
        getNext(tokens)
        ap = exp(0,tokens)
        # if peekNext(tokens).type == "LCURL":
        #     pass
        # print(ap)
        if not (ap["type"] == "Apply" or ap["op"] == "DOT" or ap["op"] == "OPDOT"):
            print("Expected a function or method application")
            sys.exit(1)
        return Go(ap)
    elif current.type == "DEF":
        getNext(tokens)
        name = None
        params = []
        if peekNext(tokens).type == "IDEN":
            name = getNext(tokens).val
        if getNext(tokens).type != "LPAREN":
            pass
        # print(name)
        current = getNext(tokens)
        while current != None and current.type != "RPAREN":
            if current.type == "IDEN":
                params.append(current.val)
                current = getNext(tokens)
            elif current.type == "SEP":
                current = getNext(tokens)
                continue
            else:
                print("Expected Identifiers")
                sys.exit(0)
                # break
        body = None
        n = peekNext(tokens)
        while n.val == "\n":
            n = getNext(tokens)
            n = peekNext(tokens)
        if n.type == "ASGN" or n.type == "LCURL":
            if n.type == "ASGN":
                getNext(tokens)
            body = exp(0,tokens)
        else:
            pass
        # print(name)
        # print(params)
        # print(body)
        return Func(name,params,body)
    elif current.type == "LCURL":
        getNext(tokens)
        block = []
        objLit = False
        lit = []
        # print("-------------Parsing Block-----------------")
        # print(tokens)
        current = peekNext(tokens)
        while current.type != "RCURL":
            # if current.val == "\n":
            #     getNext(tokens)
            t = exp(0,tokens)
            if peekNext(tokens).type == "COLON":
                getNext(tokens)
                if not objLit:
                    lit = []
                objLit =  True
                if len(block) > 0:
                    # generate error for mixing of block and object literal  
                    pass
                value = exp(0,tokens)
                n = peekNext(tokens)
                if n.type != "RCURL" and n.val != "\n":
                    # print(n)
                    assert getNext(tokens).type == "SEP"
                elif n.val == "\n":
                    getNext(tokens)
                lit.append((t,value))
            elif objLit and isinstance(t,dict) and t["type"] == "Func":
                if t["name"] == None:
                    print("Function name required in object literal");
                    sys.exit(1)
                name = t["name"]
                t["name"] = None
                n = peekNext(tokens)
                if n.type != "RCURL" and n.val != "\n":
                    # print(n)
                    assert getNext(tokens).type == "SEP"
                elif n.val == "\n":
                    getNext(tokens)
                lit.append((name,t))
            else:
                block.append(t)
            current = peekNext(tokens)
        getNext(tokens)
        # print(block)
        if objLit:
            return ObjectLit(lit)
        return Block(block)
    elif current.type == "LSQB":
        getNext(tokens)
        l = []
        current = peekNext(tokens)
        while current.type != "RSQB":
            l.append(exp(0,tokens))
            current = peekNext(tokens)
            if current.type == "SEP":
                getNext(tokens)
                current = peekNext(tokens)
        getNext(tokens)
        return List(l)
    elif current.type == "NUM":
        getNext(tokens)
        return current.val
    elif current.type == "BOOL":
        getNext(tokens)
        return current.val
    elif current.type == "STR":
        getNext(tokens)
        return current.val
    elif current.type == "UNIT":
        getNext(tokens)
        return current.val
    elif current.type == "IDEN":
        i = Atom(getNext(tokens).val)
        n = peekNext(tokens).type
        if n == "LPAREN":
            # print("----Here----")
            # print(tokens)
            getNext(tokens)
            params = []
            n = peekNext(tokens)
            # print(n)
            while n.type != "RPAREN":
                if n.type == "SEP":
                    # print("passing by")
                    getNext(tokens)
                    n = peekNext(tokens)
                    continue
                e = exp(0,tokens)
                if e != None:
                    params.append(e)
                n = peekNext(tokens)
                # print(n)
            getNext(tokens)
            return Apply(i,params)
        elif n == "LSQB":
            getNext(tokens)
            # params = []
            index = exp(0,tokens)
            # print(n)
            if getNext(tokens).type != "RSQB":
                print("Unmatched paren ']'")
                sys.exit(1)
            return SAccessor(i,index)
        return i
    elif current.type == "LINEEND":
        return getNext(tokens).val
    else:
        print(tokens)
        print("Unexpected Error")
        sys.exit(1)

ROOT = std_env()
GLOBAL_POOL = Pool(daemon=False)

class BFunction(dict):
    def __init__(self, params, body, env):
        self.lexical_scope = env
        self.param_name = params
        self.body = body

    def __call__(self,*actual,this=None):
        frame = Env(outer=self.lexical_scope)
        less = False
        frame.update({
            "args":actual,
            "this":this
        })
        for var in range(len(self.param_name)):
            if var > len(actual):
                less = True
                frame.update({self.param_name[var]:None})
            else:
                frame.update({self.param_name[var]:actual[var]})
        if less:
            print("Warning: fewer parameters passed")
        return eval(self.body,frame)

def eval(ast,env=ROOT):
    # print("-----------------Eval-----------------")
    # pprint(ast,indent=4)
    if isinstance(ast,list):
        outcome = []
        for exp in ast:
            outcome.append(eval(exp,env))
        return outcome
    elif isinstance(ast,dict):
        if ast["type"] == "Block":
            outcome = []
            for exp in ast["exp"]:
                temp = eval(exp,env)
                if temp != '\n':
                    outcome.append(temp)
            # print(outcome)
            return outcome[-1]
        elif ast["type"] == "Func":
            f = BFunction(ast["params"],ast["body"],env)
            if ast["name"] != None:
                env.update({ast["name"]:f})
            return f
        elif ast["type"] == "Apply":
            func = eval(ast["iden"],env)
            if not callable(func):
                print("Function required")
                sys.exit(0)
            # print(ast["actual"])
            params = [eval(e,env) for e in ast["actual"] if e != None]
            # print(params)
            # print("lalalal")
            # print(ast["iden"])
            r = func(*params)
            # print(r)
            return r
        elif ast["type"] == "Go":
            print(ast)
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
            # print(r)
            return GLOBAL_POOL.execute(func,params)
        elif ast["type"] == "Binary":
            if ast["op"] == "VAR":
                name = ast["left"]["value"]
                val = eval(ast["right"],env)
                env.update({name:val})
                return val
            elif ast["op"] == "ASGN":
                name = ast["left"]
                if isinstance(name,dict) and name["type"] == "SAcc":
                    obj = eval(name["iden"],env)
                    index = eval(name["index"],env)
                    val = eval(ast["right"],env)
                    if isinstance(obj,list):
                        obj[index] = val
                    else:
                        obj.update({index: val})
                    return obj[index]
                elif isinstance(name,dict) and (name.get("op") == "DOT" or name.get("op") == "OPDOT"):
                    obj = eval(name["left"],env)
                    index = name["right"]["value"]
                    obj.update({index: eval(ast["right"],env)})
                    return obj[index]
                else:
                    val = eval(ast["right"],env)
                    return env.updateVar(name["value"],val)
            elif ast["op"] == "DOT":
                obj = eval(ast["left"],env)
                if ast["right"]["type"] == "Apply":
                    func = obj[ast["right"]["iden"]["value"]]
                    if not callable(func):
                        print("Function required")
                        sys.exit(0)
                    params = [eval(e,env) for e in ast["right"]["actual"] if e != None]
                    return func(*params,this=obj)
                else:
                    index = ast["right"]["value"]
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
                return opmap[ast["op"]](eval(ast["left"],env),eval(ast["right"],env))
        elif ast["type"] == "Unary":
            # ast["right"] = eval(ast["right"],env)
            return opmap[ast["op"]](eval(ast["right"],env))
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
        elif ast["type"] == "Go":
            l = [eval(e,env) for e in ast["con"]]
            return l
        elif ast["type"] == "Obj":
            obj = {}
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

def run(str):
    tokens = tokenize(str)
    ast = parse(tokens)
    return eval(ast)


# t = tokenize("""
# def circum(r) = 2*pi*r
# i := 0
# j := while i < 10 {
#     print(i)
#     i = i + 1
#     unit
# }
# print(circum(3))
# print(j)
# """)
# pprint(t,indent=4)
# ast=parse(t)
# pprint(ast,indent=4)
# eval(ast)

# t = tokenize("""
# l1 := [10,20,30,40]
# print(l1)
# l1[0]
# print(l1[1])

# for i in l1 {
#     i |> print
# }
# """)
# pprint(t,indent=4)
# ast=parse(t)
# pprint(ast,indent=4)
# eval(ast)

# eval(json.loads(open("factorial.json","r").read()))

def repl():
    foreground(GREEN) 
    print(bold("Bhaskara 0.0.1"))
    print("Type 'help' for more information") 
    foreground(WHITE)
    read = input(">>> ") 
    while read != "q" and read != "quit" and read != "exit" and read != "bye": 
        if(read == "help"):
            pass
        if(read == "clear"):
            clrscr()
            gotoxy(0,0)
        else:
            print(run(read)[-1])
        read = input(">>> ") 
    print("") 

if __name__ == "__main__":
    if len(sys.argv) > 1:
        code = open(sys.argv[1],"r").read()
        if len(sys.argv) > 2:
            if sys.argv[2] == "--compile":
                jast = json.dumps(parse(tokenize(code)))
                open(sys.argv[1].split(".")[0]+".json","w").write(jast)
        else:
            if sys.argv[1].split(".")[1] == "json":
                eval(json.dumps(code))
            else:
                # print(code)
                # print(tokenize(code))
                run(code)
                while not GLOBAL_POOL.jobs.isEmpty():
                    pass
    else:
        # pass
        repl()