from tokens import *

# Capture col and line number as well in the tokens
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
        # print('Unmatched string `"`')
        except Exception('Unmatched string `"`')
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
