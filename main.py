import math
from os import sys
from pprint import pprint
from collections import namedtuple
from panim import *

# भास्कर - A Math and Logic DSL
# Parser and Evaluator uses Precedence Climbing LR(1) Algorithm
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

bools = ["T","F","N","B"]
N = None
B = (True,False)
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
            i -= 1
            return (createKeyword(buff),i)
    return (Token("IDEN",buff),i)

ops = [
        "+","-","/","*","(",")","^","=","|","&","~","@",
        "#","==",">","<",">=","<=","~=","[","]","{","}",
        ",","->","%","!",":"
    ]
keywords = ["true","false","niether","both","if","then","else","def"]
token_name = {
    "+":"ADD",
    "-":"SUBS",
    "/":"DIV",
    "*":"MUL",
    "%":"MOD",
    "(":"LPAREN",
    ")":"RPAREN",
    "^":"EXP",
    "|":"OR",
    "&":"AND",
    "~":"NOT",
    "->":"IMP",
    "=":"ASGN",
    ">":"GT",
    "<":"LT",
    "==":"EQ",
    ">=":"GTEQ",
    "<=":"LTEQ",
    "~=":"NOTEQ",
    "if":"IF",
    "then":"THEN",
    "else":"ELSE",
    "def":"DEF",
    ",":"SEP",
    ";":"SEMI",
    "@":"FORALL",
    "#":"EXISTS",
    "[":"LSQB",
    "]":"RSQB",
    "{":"LCURL",
    "}":"RCURL",
    ":=":"VAR",
    "//":"COMM"
}

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

Token = namedtuple("Token",["type","val"])
def tokenize(str):
    tokens = []
    i = 0
    l = len(str)
    buff = ""
    while i < l:
        c = str[i]
        if isNumber(c):
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
            elif c == "/" and isNext("/",str,i):
                i += 2
                c = str[i]
                while not(isWhite(c)) and i < l:
                    i += 1
                    c = str[i]
            else:
                tokens.append(Token(token_name[c],c))
        elif isIdentifier(c):
            t,i = parseIdentifier(str,i,l)
            tokens.append(t)
        elif c == "\n" or c == ";":
            tokens.append(Token("LINEEND",c))            
        i+=1
    # tokens.append(Token("EOF",""))
    return tokens

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

binaryops = [
                "ADD","SUBS","DIV","MUL","EXP","OR","AND",
                "LT","GT","EQ","IMP","NOTEQ","LTEQ","GTEQ",
                "VAR","ASGN"
            ]
unaryops = ["SUBS","ADD","NOT"]
opconfig = {
    "VAR":(0,0),
    "ASGN":(0,0),
    "OR":(1,1),
    "AND":(2,1),
    "IMP":(2,1),
    "EQ":(3,1),
    "NOTEQ":(3,1),
    "LT":(4,1),
    "LTEQ":(4,1),
    "GTEQ":(4,1),
    "GT":(4,1),
    "ADD":(5,1),
    "SUBS":(5,1),
    "MUL":(6,1),
    "MOD":(6,1),
    "DIV":(6,1),
    "EXP":(7,0),
    "NEG":(8,0),
    "POS":(8,0),
    "NOT":(8,0)
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

FLAG_IGNORE_LN = False

def verify(op,lhs,rhs):
    if op.type == "VAR" or op.type == "ASSGN":
        if not(lhs["type"] == "Atom"):
            print("Expected Identifier")
            sys.exit(1)

def exp(min,tokens):
    lhs = term(tokens)
    lookahead = peekNext(tokens)
    while (lookahead != None) and (lookahead.val != "\n") and (lookahead.type in binaryops) and (opconfig[lookahead.type][0] >= min):
        op = getNext(tokens)
        n = opconfig[op.type][0]
        if opconfig[op.type][1] == 1:
            n += 1
        lhs = BinOp(op.type,lhs,exp(n,tokens))
        lookahead = peekNext(tokens)
    if (lookahead != None) and (lookahead.type == "LINEEND"):
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
    if current == None:
        return
    elif current.type == 'LPAREN':
        getNext(tokens)
        out = exp(0,tokens)
        print(out)
        print(peekNext(tokens))
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
    elif current.type == "DEF":
        getNext(tokens)
        name = None
        params = []
        if peekNext(tokens).type == "IDEN":
            name = getNext(tokens).val
        if getNext(tokens).type != "LPAREN":
            pass
        current = getNext(tokens)
        while current.type != "RPAREN":
            if current.type != "IDEN":
                pass
            params.append(getNext(tokens).val)
            current = getNext(tokens)
        body = None
        if peekNext(tokens).type == "ASGN" or peekNext(tokens).type == "LCURL":
            getNext(tokens)
            body = exp(0,tokens)
        else:
            pass
        return Func(name,params,body)
    elif current.type == "LCURL":
        getNext(tokens)
        block = []
        current = peekNext(tokens)
        while current.type != "RCURL":
            block.append(exp(0,tokens))
            current = peekNext(tokens)
        getNext(tokens)
        print(block)
        return Block(block)
    elif current.type == "LSQB":
        pass
    elif current.type == "NUM":
        getNext(tokens)
        return current.val
    elif current.type == "BOOL":
        getNext(tokens)
        return current.val
    elif current.type == "IDEN":
        return Atom(getNext(tokens).val)
    elif current.type == "LINEEND":
        getNext(tokens)
    else:
        print(tokens)
        print("Unexpected Error")
        sys.exit(1)

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
    "EXP": math.pow
}

bool_ops = ["NOT","AND","OR",""]
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

def astToExp(ast):
    pass

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
    # env.update(vars(math))
    env.update({
        # "print":print,
        # "abs":abs
    })
    return env

ROOT = std_env()

def eval(ast,env=ROOT):
    if isinstance(ast,list):
        outcome = []
        for exp in ast:
            outcome.append(eval(exp))
        return outcome
    elif isinstance(ast,dict):
        if ast["type"] == "Block":
            outcome = []
            for exp in ast["exp"]:
                temp = eval(exp)
                if temp != None:
                    outcome.append(temp)
            return outcome[-1]
        if ast["type"] == "Binary":
            if ast["op"] == "VAR":
                name = ast["left"]["value"]
                val = eval(ast["right"])
                env.update({name:val})
                return val
            if ast["op"] == "ASGN":
                name = ast["left"]["value"]
                val = eval(ast["right"])
                return env.updateVar(name,val)
            else:
                ast["left"] = eval(ast["left"])
                ast["right"] = eval(ast["right"])
                return opmap[ast["op"]](ast["left"],ast["right"])
        elif ast["type"] == "Unary":
            ast["right"] = eval(ast["right"])
            return opmap[ast["op"]](ast["right"])
        elif ast["type"] == "Cond":
            ast["cond"] = eval(ast["cond"])
            if ast["cond"]:
                return eval(ast["b1"])
            elif ast["b2"] != None:
                return eval(ast["b2"])
        elif ast["type"] == "Atom":
            return env.find(ast["value"])
    else:
        return ast

def run(str):
    tokens = tokenize(str)
    ast = parse(tokens)
    return eval(ast)

def test(str):
    tokens = tokenize(str)
    pprint(tokens,indent=4)
    ast = parse(tokens)
    pprint(ast,indent=4)
    pprint(eval(ast),indent=4)

test("if true & (x := 5) then x + 10 else x")
print(eval(parse(tokenize(
"""
z := if(true & false) {
    x := 5
    x
} else (y := 10)

z
"""
))))

def repl():
    foreground(GREEN) 
    print(bold("Bhaskara 0.0.1"))
    print("Type 'help' for more information") 
    foreground(WHITE)
    read = input(">>> ") 
    while read != "q" and read != "quit" and read != "exit" and read != "bye": 
        if(read == "help"):
            pass
        else:
            print(run(read)[-1])
        read = input(">>> ") 
    print("") 

if __name__ == "__main__":
    if len(sys.argv) > 1:
        code = open(sys.argv[1],"r").read()
        print(code)
        print(run(code))
        # interpreter.execute(code)
    else:
        pass
        # repl()