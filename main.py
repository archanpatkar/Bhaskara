from collections import namedtuple

### Precedence Climbing LR(1) Math expression parser

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
        if isNumber(c) and not(isWhite(str[i])):
            buff += c
            i += 1
        else:
            break
    return (int(buff),i,l)

ops = ["+","-","/","*","(",")"]
opsmap = {
    "+":"add",
    "-":"subs",
    "*":"mul",
    "/":"div",
    "(":"lp",
    ")":"rp"
}
Token = namedtuple("Token",["type","ch"])
def tokenize(str):
    tokens = []
    i = 0
    l = len(str)
    while i < l:
        c = str[i]
        if isNumber(c):
            num,i,l = parseNum(str,i,l)
            tokens.append(Token("num",num))
        elif c in ops:
            tokens.append(Token(opsmap[c],c))
        i+=1
    return tokens

Atom = namedtuple("Atom",["value"])
BinOp = namedtuple("Binary",["left","op","right"])
UnOp = namedtuple("Unary",["op","value"])

def parse(tokens):
    return parseRec(tokens,0)

def parseRec(tokens,min):
    for t in tokens:
        print(t)


parse((tokenize("500 + 500 * 6")))
