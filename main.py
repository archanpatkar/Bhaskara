import math
from os import sys
from pprint import pprint
from collections import namedtuple

# Math and Logic DSL
# Parser and Evaluator based on Precedence Climbing LR(1) Algorithm
# Based on: http://www.engr.mun.ca/~theo/Misc/exp_parsing.htm
empty = [" ","\r","\t"]
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

bools = ["T","F"]
def isBool(str):
    if str in bools:
        return True
    return False

ops = [
        "+","-","/","*","(",")","^","=","|","&","~","@",
        "#","==",">","<",">=","<=","~=","[","]","{","}",
        ",","->",";"
    ]
keywords = ["true","false","if","then","else","def","U","B"]
token_name = {
    "+":"ADD",
    "-":"SUBS",
    "/":"DIV",
    "*":"MUL",
    "(":"LPAREN",
    ")":"RPAREN",
    "^":"EXP",
    "|":"OR",
    "&":"AND",
    "~":"NOT",
    "=":"ASGN",
    ">":"GT",
    "<":"LT",
    "if":"IF",
    "then":"THEN",
    "else":"ELSE",
    "def":"DEF",
    ",":"SEP",
    ";":"SEMI"
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
        elif isBool(c):
            if c == "T":
                tokens.append(Token("BOOL",True))
            else:
                tokens.append(Token("BOOL",False))
        elif c in ops:
            tokens.append(Token(token_name[c],c))
        elif c in keywords:
            tokens.append(Token(token_name[c],c))
        elif c == "\n" or c == ";":
            tokens.append(Token("LINEEND",c))
        i+=1
    # tokens.append(Token("EOF",""))
    return tokens

def BinOp(op,left,right):
    return { "type":"Binary", "left":left, "op":op, "right":right, "reduced":False }

def UnOp(op,value):
    return { "type":"Unary", "op":op, "right":value, "reduced":False }

binaryops = ["ADD","SUBS","DIV","MUL","EXP","OR","AND","LT","GT"]
unaryops = ["SUBS","ADD","NOT"]
opconfig = {
    "OR":(1,1),
    "AND":(2,1),
    "LT":(3,1),
    "GT":(3,1),
    "ADD":(4,1),
    "SUBS":(4,1),
    "MUL":(5,1),
    "DIV":(5,1),
    "EXP":(6,0),
    "NEG":(7,0),
    "POS":(7,0),
    "NOT":(7,0)
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
    return exps

def exp(min,tokens):
    print(tokens)
    lhs = term(tokens)
    lookahead = peekNext(tokens)
    while (lookahead != None) and (lookahead.val != "\n") and (lookahead.type in binaryops) and (opconfig[lookahead.type][0] >= min):
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
    elif current.type == "BOOL":
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
    "NOT": lambda x: not(x),
    "AND": lambda x,y: x and y,
    "OR": lambda x,y: x or y,
    "LT": lambda x,y: x < y,
    "GT": lambda x,y: x > y,
    "EXP": math.pow
}

bool_ops = ["NOT","AND","OR"]
num_ops = ["ADD","SUBS","DIV","MUL","EXP","NEG","POS"]

def coerse(op,*params):
    temp = []
    if op in bool_ops:
        for p in params:
            if isinstance(p,int) or isinstance(p,float):
                if p > 0:
                    temp.append(True)
                elif p == 0:
                    temp.append(False)
            else:
                temp.append(p)
    elif op in num_ops:
        for p in params:
            if isinstance(p,bool):
                if p:
                    temp.append(1)
                else:
                    temp.append(0)
            else:
                temp.append(p)
    return temp

def eval(ast):
    if isinstance(ast,list):
        outcome = []
        for exp in ast:
            outcome.append(eval(exp))
        return outcome
    elif isinstance(ast,dict):
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

tokens = tokenize("(T | F) & ~F & 5 > 5")
print(tokens)
ast = parse(tokens)
pprint(ast,indent=4)
print(eval(ast))

# tokens = tokenize("(-500)*500+6")
# print(tokens)
# ast = parse(tokens)
# pprint(ast,indent=4)
# print(eval(ast))