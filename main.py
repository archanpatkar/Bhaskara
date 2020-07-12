from collections import namedtuple
from pprint import pprint

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
        if isNumber(c) and not(isWhite(str[i])):
            buff += c
            i += 1
        else:
            break
    return (int(buff),i,l)

ops = ["+","-","/","*","(",")","^"]

Token = namedtuple("Token",["type","val"])
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
            tokens.append(Token(c,c))
        i+=1
    return tokens

Atom = namedtuple("Atom",["value"])
BinOp = namedtuple("Binary",["left","op","right"])
UnOp = namedtuple("Unary",["op","value"])

binaryops = ["+","-","*","/","^"]
unaryops = ["-","+"]
premap = {
    "+":1,
    "-":1,
    "*":2,
    "/":2,
    "^":3
}

def getNext(tokens):
    if len(tokens) > 0:
        return tokens.pop(0)
    return None

def parse(tokens):
    token = getNext(tokens)
    prev = None
    while token != None:
        current = None
        if token.type == 'num':
            current = Atom(token.val)
        elif token.type in binaryops and prev != None:
            current = {"type":"B", "left":prev, "op":token.type}
        elif token.type in unaryops and prev == None:
            current = {"type":"U", "op":token.type}
        elif token.type == '(':
            subt = []
            token = getNext(tokens)
            while token != None and token.type != ')':
                subt.append(token)
                token = getNext(tokens)
            current = parse(subt)
        if isinstance(prev,dict):
            if prev["type"] == "B":
                prev = BinOp(prev["left"],prev["op"],current)
            elif prev["type"] == "U":
                prev = UnOp(prev["op"],current)
        else:
            prev = current
        token = getNext(tokens)
    return prev

# def parse(tokens):
#     return parseRec(tokens.pop(0),0)

# def parseRec(lhs,min,tokens):
#     lookahead = tokens[0]
#     while lookahead.type in binaryops and premap[lookahead.type] > min:
#         op = lookahead
#         rhs = tokens.pop(0)
#         lookahead = tokens[0]
#         while lookahead.type in binaryops and premap[lookahead.type] > premap[op.type]:
#             rhs = parseRec(rhs, premap[lookahead.type])
#             lookahead = tokens[0]
#         lhs = BinOp(lhs,op,rhs)
#     return lhs

print(parse((tokenize("-500 + (500 * 6)"))))