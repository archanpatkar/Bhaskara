from pprint import pprint
from tokens import *
from error import lexing_error

# Store column number and line number in the token
# store lines sep. for good error messages for both the parser and the lexer
# Something like -

# 1| 1+3  5-3
#         ^
# Expect `\n` or `;` not number literal `5`

# Explore the possibility of making the tokenizer lazy, implementing 
# the iterator protocol defering the creation of tokens until needed

# Capture col and line number as well in the tokens
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

def createKeyword(buff):
    if buff == "true" or buff == "T":
        return Token("BOOL", True)
    elif buff == "false" or buff == "F":
        return Token("BOOL", False)
    else:
        return Token(token_name[buff], buff)

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
        self.len = len(self.str)

    def ignore(self, v):
        self.ignoreNL = v

    def hasNext(self):
        return len(self.tokens) > 0

    def peek(self):
        if self.ignoreNL:
            while self.tokens[0].type == "LINEEND":
                self.tokens.pop(0)
        return self.tokens[0]

    def consume(self):
        if self.ignoreNL:
            while self.tokens[0].type == "LINEEND":
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
            elif c == "." and not(decimal):
                decimal = True
                buff += c
                self.current += 1
            else:
                self.current -= 1
                break
        if decimal:
            buff = float(buff)
        else:
            buff = int(buff)
        self.tokens.append(Token("NUM", buff))

    def parseIdentifier(self):
        buff = "" + self.str[self.current]
        self.current += 1
        while self.current < self.len:
            c = self.str[self.current]
            if isIdentifier(c) or isNumber(c):
                buff += c
                self.current += 1
            else:
                self.current -= 1
                break
        if isKeyword(buff):
            self.tokens.append(createKeyword(buff))
        else:
            self.tokens.append(Token("IDEN", buff))

    def parseString(self):
        buff = ""
        self.current += 1
        c = ""
        while self.current < self.len:
            c = self.str[self.current]
            if c != '"' and c != "'":
                buff += c
                self.current += 1
            else:
                break
        if c != '"' and c != "'":
            lexing_error('Unmatched string quote')
        self.tokens.append(Token("STR", buff))

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

    def tokenize(self, code):
        if code:
            self.setup(code)
        buff = ""
        while self.current < self.len:
            c = self.str[self.current]
            if isWhite(c):
                self.eatWhitespace()
            elif c == "/" and self.isNext("/"):
                self.handleComment()
            elif c == '"' or c == "'":
                self.parseString()
            elif isNumber(c):
                self.parseNum()
            elif c in ops:
                done = False
                if c in double:
                    if isinstance(double[c], list):
                        for ch in double[c]:
                            if self.isNext(ch):
                                done = True
                                self.current += 1
                                n = c+self.str[self.current]
                                self.tokens.append(Token(token_name[n], n))
                                break
                    elif self.isNext(double[c]):
                        done = True
                        self.current += 1
                        n = c+self.str[self.current]
                        self.tokens.append(Token(token_name[n], n))
                if not done:
                    self.tokens.append(Token(token_name[c], c))
            elif isIdentifier(c):
                self.parseIdentifier()
            elif c in lineend:
                self.tokens.append(Token("LINEEND", c))
            else:
                lexing_error(c)
            self.current += 1
        self.tokens.append(Token("EOF", "\0"))
