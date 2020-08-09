from pprint import pprint
from ast import *
from tokens import *
from lexer import Tokenizer
from error import parse_error

# !! Improve \n handling, currently it is very simplistic 
    # 1. (Create a language level standard for handling \n like Go or Swift etc.) 
    # 2. (Or implement Automatic semicolon insertion like Javascript or Kotlin) 
        # Good docs and resource -
            # https://tc39.es/ecma262/#sec-automatic-semicolon-insertion
            # https://temperlang.dev/design-sketches/parsing-program-structure.html#asi    
# !! Add more error checks
# !! Handle unexpected ends
# !! Handle parsing edge cases

# Parser uses Precedence Climbing/Pratt parser Algorithm
# Based on: http://www.engr.mun.ca/~theo/Misc/exp_parsing.htm
prectable = {
    "VAR": (0, 0),
    "ASGN": (0, 0),
    "LPIPE": (0, 1),
    "RPIPE": (0, 0),
    "OR": (1, 1),
    "AND": (2, 1),
    "IMP": (2, 1),
    "EQ": (3, 1),
    "NOTEQ": (3, 1),
    "LT": (4, 1),
    "LTEQ": (4, 1),
    "GTEQ": (4, 1),
    "GT": (4, 1),
    "ADD": (5, 1),
    "SUBS": (5, 1),
    "MUL": (6, 1),
    "MOD": (6, 1),
    "DIV": (6, 1),
    "EXP": (7, 0),
    "NEG": (8, 0),
    "POS": (8, 0),
    "NOT": (8, 0),
    "DOT": (9, 1),
    "LSQB": (9, 1),
    "OPDOT": (9, 1),
    "LPAREN": (10,1)
}

class Parser:
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer

    def expect(self, token, msg):
        taken = self.tokenizer.consume()
        if taken.type != token:
            if msg:
                parse_error("Expected token {} not {}".format(msg,taken.val))
            else:
                parse_error("Expected token {} not {}".format(token,taken.val))
        return taken

    def parse(self, code):
        self.tokenizer.tokenize(code)
        exps = []
        while self.tokenizer.hasNext() and self.tokenizer.peek().type != "EOF":
            out = self.exp(0)
            if isinstance(out, dict):
                exps.append(out)
            self.expect("LINEEND","`\\n` or `;`")
        return exps

    def unary(self):
        current = self.tokenizer.consume()
        return UnOp(current.type, self.exp(prectable[current.type][0]))

    def parenExp(self):
        self.tokenizer.consume()
        self.tokenizer.ignore(True)
        out = self.exp(0)
        self.expect("RPAREN", "Unmatched paren `(`")
        self.tokenizer.ignore(False)
        return out

    def parseIF(self):
        self.tokenizer.consume()
        cond = self.exp(0)
        if self.tokenizer.peek().type != "LCURL":
            self.expect("THEN", "Expected `then`")
        b1 = self.exp(0)
        b2 = None
        t = self.tokenizer.peek()
        if t != None and t.type == "ELSE":
            self.tokenizer.consume()
            b2 = self.exp(0)
        return CondOp(cond, b1, b2)

    def parseMatch(self):
        pass

    def parseFor(self):
        self.tokenizer.consume()
        iden = self.expect("IDEN", "Expected an identifier").val
        self.expect("IN", "Expected an `in`")
        iter = self.exp(0)
        if self.tokenizer.peek().type != "LCURL":
            self.expect("DO", "Expected `do`")
        body = self.exp(0)
        return For(iden, iter, body)

    def parseWhile(self):
        self.tokenizer.consume()
        cond = self.exp(0)
        if self.tokenizer.peek().type != "LCURL":
            self.expect("DO", "Expected `do`")
        body = self.exp(0)
        return While(cond, body)

    def parseDecorator(self):
        pass

    def parseFunction(self):
        self.tokenizer.consume()
        name = None
        params = []
        if self.tokenizer.peek().type == "IDEN":
            name = self.tokenizer.consume().val
        self.expect("LPAREN", "expected `(`")
        current = self.tokenizer.peek()
        while current != None and current.type != "RPAREN":
            if current.type == "IDEN":
                self.tokenizer.consume()
                params.append(current.val)
                current = self.tokenizer.peek()
            elif current.type == "SEP":
                self.tokenizer.consume()
                current = self.tokenizer.peek()
            else:
                parse_error("Expected identifier not {}".format(current.val))
        self.expect("RPAREN", "expected `)`")
        body = None
        current = self.tokenizer.peek()
        while current.val == "\n":
            current = self.tokenizer.consume()
            current = self.tokenizer.peek()
        if current.type == "ASGN" or current.type == "LCURL":
            if current.type == "ASGN":
                self.tokenizer.consume()
            body = self.exp(0)
        else:
            parse_error("Expected `=` or block")
        return Func(name, params, body)

    def parseCurl(self):
        self.tokenizer.consume()
        objLit = False
        block = []
        lit = []
        current = self.tokenizer.peek()
        while current.type != "RCURL":
            if(current.type == "LINEEND"):
                self.tokenizer.consume()
                current = self.tokenizer.peek()
                continue
            t = self.exp(0)
            if self.tokenizer.peek().type == "COLON":
                self.tokenizer.consume()
                objLit = True
                if len(block) > 0:
                    parse_error("Cannot mix normal code with an object literal")
                value = self.exp(0)
                current = self.tokenizer.peek()
                if current.type != "RCURL" and current.val != "\n":
                    self.expect("SEP", "Expected `,`")
                elif current.val == "\n":
                    self.tokenizer.consume()
                else:
                    parse_error("Unexpected token `{}`".format(current.val))
                lit.append((t, value))
            elif objLit and isinstance(t, dict) and t["type"] == "Func":
                if t["name"] == None:
                    parse_error("Function name required in object literal")
                name = t["name"]
                current = self.tokenizer.peek()
                if current.type != "RCURL" and current.val != "\n":
                    self.expect("SEP", "Expected `,`")
                elif current.val == "\n":
                    self.tokenizer.consume()
                else:
                    parse_error("Unexpected token `{}`".format(current.val))
                lit.append((name, t))
            else:
                block.append(t)
            current = self.tokenizer.peek()
        self.expect("RCURL", "Expected `}`")
        if objLit:
            return ObjectLit(lit)
        return Block(block)

    def parseList(self):
        self.tokenizer.consume()
        l = []
        current = self.tokenizer.peek()
        while current.type != "RSQB":
            l.append(self.exp(0))
            current = self.tokenizer.peek()
            if current.type == "SEP":
                self.tokenizer.consume()
                current = self.tokenizer.peek()
        self.expect("RSQB", "Expected `[`")
        return List(l)

    def parseLazy(self):
        self.tokenizer.consume()
        exp = self.exp(0)
        return Lazy(exp)

    def parseForce(self):
        self.tokenizer.consume()
        exp = self.exp(0)
        return Force(exp)

    def parseGo(self):
        self.tokenizer.consume()
        ap = self.exp(0)
        chain = None
        if not (ap["type"] == "Apply" or ap["op"] == "DOT" or ap["op"] == "OPDOT"):
            parse_error("Expected a function or method application")
        if self.tokenizer.peek().type == "THEN":
            self.tokenizer.consume()
            chain = self.exp(0)
        return Go(ap,chain)

    def parseApp(self,lhs):
        params = []
        t = self.tokenizer.peek()
        while t.type != "RPAREN":
            if t.type == "SEP":
                if len(params) == 0:
                    parse_error("Expected `)`")
                self.tokenizer.consume()
            else:
                e = self.exp(0)
                if e != None:
                    params.append(e)
            t = self.tokenizer.peek()
        self.expect("RPAREN", "Expected `)`")
        return Apply(lhs, params)

    def parseAcc(self,lhs):
        index = self.exp(0)
        self.expect("RSQB", "Unmatched paren `]`")
        return SAccessor(lhs, index)

    # Make this hashed(dict) based and dynamic according to the token type
    # For both the term(prefix), exp(infix) also add support for postfix in exp
    def term(self):
        current = self.tokenizer.peek()
        if current.type == "EOF" or current.type == "LINEEND":
            return
        elif current.type in unaryops:
            return self.unary()
        elif current.type == 'LPAREN':
            return self.parenExp()
        elif current.type == "IF":
            return self.parseIF()
        elif current.type == "FOR":
            return self.parseFor()
        elif current.type == "WHILE":
            return self.parseWhile()
        elif current.type == "DEF":
            return self.parseFunction()
        elif current.type == "LCURL":
            return self.parseCurl()
        elif current.type == "LSQB":
            return self.parseList()
        elif current.type == "GO":
            return self.parseGo()
        elif current.type == "LAZY":
            return self.parseLazy()
        elif current.type == "FORCE":
            return self.parseForce()
        elif current.type == "IDEN":
            return Atom(self.tokenizer.consume().val)
        elif current.type == "NUM" or current.type == "BOOL" or current.type == "STR":
            return Literal(self.tokenizer.consume().val)
        else:
            parse_error("Unexpected token `{}`".format(current.val))

    def exp(self, min):
        lhs = self.term()
        lookahead = self.tokenizer.peek()
        while lhs != None and (lookahead.type in binaryops) and (prectable[lookahead.type][0] >= min):
            op = self.tokenizer.consume()
            n = prectable[op.type][0]
            if prectable[op.type][1] == 1:
                n += 1
            if op.type == "LPAREN":
                lhs = self.parseApp(lhs)
            elif op.type == "LSQB":
                lhs = self.parseAcc(lhs)
            else:
                lhs = BinOp(op.type, lhs, self.exp(n))
            lookahead = self.tokenizer.peek()
        return lhs