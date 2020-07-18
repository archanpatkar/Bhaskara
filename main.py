import math
from os import sys
from pprint import pprint
from collections import namedtuple

### Precedence Climbing LR(1) Math expression parser and evaluator
empty = [" ","\n","\r","\t"]
def isWhite(str):
    if str in empty:
        return True
    return False

digits = ["0","1","2","3","4","5","6","7","8","9"]
def isNumber(str):
    if str in digits:
        return True
    return False 

def parseNum(str,i,l):
    buff = "" + str[i]
    i += 1
    while i < l:
        c = str[i]
        if isNumber(c):
            buff += c
            i += 1
        else:
            i -= 1
            break
    return (int(buff),i,l)

ops = ["+","-","/","*","(",")","^"]
opsname = {
    "+":"ADD",
    "-":"SUBS",
    "/":"DIV",
    "*":"MUL",
    "(":"LPAREN",
    ")":"RPAREN",
    "^":"EXP"
}

Token = namedtuple("Token",["type","val"])
def tokenize(str):
    tokens = []
    i = 0
    l = len(str)
    while i < l:
        c = str[i]
        if isNumber(c):
            num,i,l = parseNum(str,i,l)
            tokens.append(Token("NUM",num))
        elif c in ops:
            tokens.append(Token(opsname[c],c))
        elif isWhite(c):
            tokens.append(Token("WHITE",c))
        i+=1
    return tokens

def BinOp(op,left,right):
    return { "type":"Binary", "left":left, "op":op, "right":right, "reduced":False }

def UnOp(op,value):
    return { "type":"Unary", "op":op, "right":value, "reduced":False }

binaryops = ["ADD","SUBS","DIV","MUL","EXP"]
unaryops = ["SUBS"]
opconfig = {
    "ADD":(1,1),
    "SUBS":(1,1),
    "NEG":(2,0),
    "POS":(2,0),
    "MUL":(3,1),
    "DIV":(3,1),
    "EXP":(4,0)
}

swap = {
    "SUBS":"NEG",
    "ADD":"POS"
}

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
    # assert getNext(tokens) == None
    return exps

def exp(min,tokens):
    lhs = term(tokens)
    lookahead = peekNext(tokens)
    while (lhs.type == "WHITE" and lhs.val != "\n") and (lookahead != None) and (lookahead.type in binaryops) and (opconfig[lookahead.type][0] >= min):
        op = getNext(tokens)
        n = opconfig[op.type][0]
        if opconfig[op.type][1] == 1:
            n += 1
        lhs = BinOp(op.type,lhs,exp(n,tokens))
        lookahead = peekNext(tokens)
    return lhs

def term(tokens):
    current = peekNext(tokens)
    if current.type == 'LPAREN':
        getNext(tokens)
        out = exp(0,tokens)
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
    elif current.type == "NUM":
        getNext(tokens)
        return current.val
    elif current.type == "WHITE":
        return current
    else:
        print("Unexpected Error")
        sys.exit(1)

opmap = {
    "ADD": lambda x,y: x + y,
    "SUBS": lambda x,y: x - y,
    "MUL": lambda x,y: x * y,
    "DIV": lambda x,y: x / y,
    "NEG": lambda x: -x,
    "POS": lambda x: +x,
    "EXP": math.pow
}

def eval(ast):
    if isinstance(ast,list):
        outcome = []
        for exp in ast:
            outcome.append(eval(exp))
    if isinstance(ast,dict):
        if ast["reduced"]:
            return ast
        if ast["type"] == "Binary":
            ast["left"] = eval(ast["left"])
            ast["right"] = eval(ast["right"])
            ast["reduced"] = True
            return opmap[ast["op"]](ast["left"],ast["right"])
        elif ast["type"] == "Unary":
            ast["right"] = eval(ast["right"])
            ast["reduced"] = True
            return opmap[ast["op"]](ast["right"])
    else:
        return ast

tokens = tokenize("(-500)*500+6")
print(tokens)
ast = parse(tokens)
pprint(ast,indent=4)
print(eval(ast))