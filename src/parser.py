from pprint import pprint
from ast import *
from tokens import *
from lexer import Tokenizer
from error import parse_error

# !! Improve \n handling, currently it is very simplistic 
    # 1. (Create a language level standard for handling \n like Go or Swift etc.) 
    # 2. (Or implement Automatic semicolon insertion like Javascript or Kotlin) 
        # Good docs and resources -
            #  https://tc39.es/ecma262/#sec-automatic-semicolon-insertion
            # https://temperlang.dev/design-sketches/parsing-program-structure.html#asi    
    # 3. (To write an algorithm based on hueristics and language constructs to best improve DX)
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
    "RANGE": (4, 1),
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
                parse_error("{} not {}".format(msg,taken.val))
            else:
                parse_error("Expected token {} not {}".format(token,taken.val))
        return taken

    def eatWhitespace(self):
        while self.tokenizer.peek().type == "LINEEND": 
            self.tokenizer.consume()

    def afterWhitespace(self):
        current = 0
        while self.tokenizer.tokens[current].type == "LINEEND": 
            current += 1
        return self.tokenizer.tokens[current]

    def parse(self, code):
        self.tokenizer.tokenize(code)
        exps = []
        while self.tokenizer.hasNext() and self.tokenizer.peek().type != "EOF":
            out = self.exp(0)
            if out: exps.append(out)
            end = self.tokenizer.peek()
            if end and end.type != "EOF":
                self.expect("LINEEND","`\\n` or `;`")
            self.eatWhitespace()
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
        # In progress --
        other = []
        while t != None and t.type == "ELIF":
            self.tokenizer.consume()
            econd = self.exp(0)
            if self.tokenizer.peek().type != "LCURL":
                self.expect("THEN", "Expected `then`")
            d = self.exp(0)
            other.append((econd,d))
            t = self.tokenizer.peek()
        if t != None and t.type == "ELSE":
            self.tokenizer.consume()
            b2 = self.exp(0)
        return CondOp(cond, b1, b2, other)

    def parseMCase(self):
        # Currently implementing basic literal case
        # Later on will implement more novel patterns e.g. 
        # Structural matching based on objects and lists
        self.expect("OR","Expected `|`")
        checker = []
        n = self.tokenizer.peek()
        while True:
            # Add more cases for other patterns
            if n.type == "NUM" or n.type == "BOOL" or n.type == "STR":
                self.tokenizer.consume()
                checker.append(Literal(n.val))
            elif n.type == "IDEN":
                if n.val == "_":
                    self.tokenizer.consume()
                    checker.append(True)
                    break
                else:
                    # This part will become more complex after the addition 
                    # of list matching, sum type matching etc.. 

                    # if variable type pattern matcher
                    self.tokenizer.consume()
                    checker.append(Atom(n.val))
                    break
            else:
                parse_error("Unknown pattern {}".format(n.val))
            n = self.tokenizer.peek()
            if n.type == "OR":
                self.tokenizer.consume()
                n = self.tokenizer.peek()
            elif n.type == "AND":
                self.tokenizer.consume()
                n = self.tokenizer.peek()
            else: break
        # Guard
        guard = None
        n = self.tokenizer.peek()
        if n.type == "WHEN":
            self.tokenizer.consume()
            guard = self.exp(0)
        if len(checker) == 1:
            checker = checker[0]
        return (checker,guard)

    def parseMatch(self):
        flg = True
        self.tokenizer.consume()
        matched = self.exp(0)
        if self.tokenizer.peek().type == "WITH":
            flg = False
        else:
            self.expect("LCURL", "Expected `{`")
        self.tokenizer.consume()
        cases = []
        self.eatWhitespace()
        t = self.tokenizer.peek()
        # t.type != "RCURL" and
        while t != None and t.type == "OR":
            self.eatWhitespace()
            checker,guard = self.parseMCase()
            self.expect("ARROW","Expected `=>`")
            do = self.exp(0)
            cases.append((checker,guard,do))
            t = self.afterWhitespace()
        if flg:
            self.expect("RCURL", "Expected `}`")
        # else:
        #     # This is very bad but currently rigging it up 
        #     # will change later
        #     self.tokenizer.tokens.insert(0,Token("LINEEND","\n"))
        return Match(matched,cases)

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
        self.tokenizer.consume()
        dec = self.exp(0)
        # Currently patched this together but think about it's implication!
        self.eatWhitespace()
        base = self.exp(0)
        return DecApply(dec,[base])

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
        if current.type == "ASGN" or current.type == "ARROW" or current.type == "LCURL":
            if current.type == "ASGN" or current.type == "ARROW":
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

    def rsexpr(self):
        self.expect("LPAREN","Expected `(`")
        container = []
        current = self.tokenizer.peek()
        while current != None and current.type != "RPAREN":
            if current.type == "LPAREN":
                container.append(self.rsexpr())
            else:
                if current.type == "NUM" or current.type == "STR" or current.type == "BOOL":
                    container.append(Literal(current.val))
                else:
                    container.append(Atom(current.val))
                self.tokenizer.consume()
            current = self.tokenizer.peek()
        self.expect("RPAREN","Unmatched `(`")
        return container

    def parseSexpr(self):
        self.tokenizer.consume()
        self.tokenizer.ignore(True)
        exp = SExpr(self.rsexpr())
        self.tokenizer.ignore(False)
        return exp

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
        elif current.type == "MATCH":
            return self.parseMatch()
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
        elif current.type == "FORALL":
            return self.parseDecorator()
        elif current.type == "EXISTS":
            return self.parseSexpr()
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
	# Add logic for auto application of functions to increase the dsl features 
	# Allowing something like repeat 5 { print <| "repeating this!" } 
        return lhs


# p = Parser(Tokenizer())
# pprint(p.parse(
# """
# match x {
#     | 2 => print(2**2)
#     | v when v > 5 => print(10*v)
#     | _ => print(x)
# }
# """),indent=4)
# match x with
#     | 1 when true & false => 1*10
#     | 2 => 20/2
#     | _ => 0
# pprint(p.parse(
# """
# #(
#     (archan patkar jagrat patkar 10 20 30 40 50 60 70)
#     (match x (10 (print "this")) (20 (print "this2")))
#     (defmacro cond(x,y) !())
#     (defun archan(x,y,z)
#         (if (< x y) (print x) (print y))
#     )
#     (archan 10 20 30)
# )
# """),indent=4)
