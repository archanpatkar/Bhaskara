from pprint import pprint
from tokens import *
from error import lexing_error, topo_loc

# TODO: Optimize and clean up the code
# Store column number and line number in the token
# store lines sep. for good error messages for both the parser and the lexer
# Something like -

# 1| 1+3  5-3
#         ^
# Expected `\n` or `;` not number literal `5`

# Make the tokenizer lazy, implementing defering the creation of tokens until needed

# Add embedded S-expression pre-parsing support at the lexer level which will lead to
# potentially endless possibilities for creating DSLs(without using the tokenization of 
# the language itself).

def isWhite(str):
    if str in white:
        return True
    return False

def isNumber(str):
    if str in digits:
        return True
    return False

def isIdentifier(str):
    n = ord(str)
    if (n >= ord('a') and n <= ord('z')) or (n >= ord('A') and n <= ord('Z')) or str == "_":
        return True
    return False

def isKeyword(str):
    if str in keywords:
        return True
    return False

def getKeyword(buff):
    if buff == "true" or buff == "T":
        return ("BOOL", True)
    elif buff == "false" or buff == "F":
        return ("BOOL", False)
    else:
        return (token_name[buff], buff)

class Tokenizer:
    def __init__(self, code=None):
        if code:
            self.setup(code)
            self.tokenize()

    def setup(self, code):
        self.current = 0
        self.tokens = []
        self.str = code
        self.ignoreNL = False
        self.lineno = 1
        self.colno = 1
        # Temp will optimized later
        self.lines = self.str.split('\n')
        self.len = len(self.str)

    def ignore(self, v=True):
        self.ignoreNL = v

    def hasNext(self):
        if len(self.tokens) == 0: self.tokenize()
        return len(self.tokens) > 0

    def genNext(self):
        self.tokenize()

    def peek(self):
        if len(self.tokens) == 0: self.tokenize()
        if self.ignoreNL:
            while self.hasNext() and self.tokens[0].type == "LINEEND":
                self.tokens.pop(0)
        return self.tokens[0]

    def consume(self):
        if len(self.tokens) == 0: self.tokenize()
        if self.ignoreNL:
            while self.hasNext() and self.tokens[0].type == "LINEEND":
                self.tokens.pop(0)
        return self.tokens.pop(0)

    def parseNum(self):
        decimal = False
        buff = "" + self.str[self.current]
        self.current += 1
        while self.current < self.len:
            c = self.str[self.current]
            if isNumber(c):
                buff += c
                self.current += 1
                self.colno += 1
            elif c == "." and (self.str[self.current+1] != "." or isNumber(self.str[self.current+1])) and not(decimal):
                decimal = True
                buff += c
                self.current += 1
                self.colno += 1
            else:
                self.current -= 1
                self.colno -= 1
                break
        if decimal:
            buff = float(buff)
        else:
            buff = int(buff)
        self.makeTok("NUM", buff)

    def parseIdentifier(self):
        buff = "" + self.str[self.current]
        self.current += 1
        self.colno += 1
        while self.current < self.len:
            c = self.str[self.current]
            if isIdentifier(c) or isNumber(c):
                buff += c
                self.current += 1
                self.colno += 1
            else:
                self.current -= 1
                self.colno -= 1
                break
        if isKeyword(buff):
            self.makeTok(*getKeyword(buff))
        else:
            self.makeTok("IDEN", buff)

    def parseString(self):
        buff = ""
        self.current += 1
        self.colno += 1
        c = ""
        while self.current < self.len:
            c = self.str[self.current]
            if c != '"' and c != "'":
                buff += c
                self.current += 1
                self.colno += 1
                if c in lineend:
                    self.lineno += 1
                    self.colno = 1
            else:
                break
        if c != '"' and c != "'":
            lexing_error(topo_loc(self.lines[self.lineno-1],self.lineno,self.colno,'Unmatched string quote'))
        self.makeTok("STR", buff)

    def handleComment(self):
        self.current += 2
        c = self.str[self.current]
        while c != "\n":
            self.current += 1
            if self.current < self.len:
                c = self.str[self.current]
            else:
                break

    def eatWhitespace(self):
        c = self.str[self.current+1]
        while isWhite(c):
            self.colno += 1
            self.current += 1
            c = self.str[self.current+1]

    def isNext(self, ch):
        if len(self.str) > self.current+1:
            if callable(ch):
                return ch(self.str[self.current+1])
            if self.str[self.current+1] == ch:
                return True
        return False

    def multiCharOps(self):
        # Parse arbitarily complex n char ops defined from the double dict in the tokes
        pass

    def makeTok(self,name,ch):
        return self.tokens.append(Token(name,ch,self.lineno,self.colno))

    def tokenize(self, code=False):
        if code:
            self.setup(code)
        buff = ""
        while self.current < self.len:
            c = self.str[self.current]
            if isWhite(c):
                self.eatWhitespace()
            elif c == "/" and self.isNext("/"):
                self.handleComment()
                # print("handling comments")
                self.lineno += 1
                self.colno = 1
            elif c == '"' or c == "'":
                self.parseString()
                self.current += 1
                self.colno += 1
                break
            elif isNumber(c):
                self.parseNum()
                self.current += 1
                self.colno += 1
                break
            elif c in ops:
                done = False
                if c in double:
                    if isinstance(double[c], list):
                        for ch in double[c]:
                            if self.isNext(ch):
                                done = True
                                self.current += 1
                                n = c+self.str[self.current]
                                self.colno += 2
                                self.makeTok(token_name[n], n)
                                self.current += 1
                                break
                    elif self.isNext(double[c]):
                        done = True
                        self.current += 1
                        n = c+self.str[self.current]
                        self.colno += 2
                        self.makeTok(token_name[n], n)
                        self.current += 1
                if not done:
                    self.makeTok(token_name[c], c)
                    self.current += 1
                    self.colno += 2
                break
            elif isIdentifier(c):
                self.parseIdentifier()
                self.current += 1
                self.colno += 1
                break
            elif c in lineend:
                self.makeTok("LINEEND", c)
                self.current += 1
                self.lineno += 1
                self.colno = 1
                break
            else:
                lexing_error(topo_loc(self.lines[self.lineno],self.lineno,self.colno,"Unexpected character -> {}".format(token.val)))
            self.current += 1
            self.colno += 1
        if len(self.tokens) == 0 and self.len == self.current:
            self.makeTok("EOF", "\0")
        # else:
        #     self.tokens.append(None)
# t = Tokenizer("5   +  archan")
# print(t)
# print(t.hasNext())
# print(t.consume())
# printTopoLoc(t.consume(),t.lines)
# print(t.hasNext())
# print(t.consume())
# printTopoLoc(t.consume(),t.lines)
# print(t.hasNext())
# print(t.consume())
# printTopoLoc(t.consume(),t.lines)