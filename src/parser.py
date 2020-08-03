from ast import *

# Parser uses Precedence Climbing/Pratt parser LR(1) Algorithm
# Based on: http://www.engr.mun.ca/~theo/Misc/exp_parsing.htm

opconfig = {
    "VAR":(0,0),
    "ASGN":(0,0),
    "LPIPE":(0,1),
    "RPIPE":(0,0),
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
    "NOT":(8,0),
    "DOT":(9,1),
    "OPDOT":(9,1)
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
        # if out == None:
            # break
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
    while (lookahead != None) and (lookahead.val != "\n" and lookahead.type != "EOF") and (lookahead.type in binaryops) and (opconfig[lookahead.type][0] >= min):
        op = getNext(tokens)
        n = opconfig[op.type][0]
        if opconfig[op.type][1] == 1:
            n += 1
        lhs = BinOp(op.type,lhs,exp(n,tokens))
        lookahead = peekNext(tokens)
    if lookahead != None and (lookahead.type == "LINEEND" or lookahead.type == "EOF"):
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
    # print("*********************************************")
    # pprint(current,indent=4)
    # pprint(tokens,indent=4)
    if current == None or current.type == "EOF":
        return
    elif current.type == 'LPAREN':
        getNext(tokens)
        out = exp(0,tokens)
        # print(out)
        # print(peekNext(tokens))
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
    elif current.type == "FOR":
        getNext(tokens)
        if peekNext(tokens).type != "IDEN":
            print("Expected an identifier")
            sys.exit(1)
        iden = getNext(tokens).val
        if peekNext(tokens).type != "IN":
            print("Expected an `in`")
            sys.exit(1)
        getNext(tokens)
        if peekNext(tokens).type != "IDEN":
            print("Expected an identifier")
            sys.exit(1)
        iter = exp(0,tokens)
        if peekNext(tokens).type == "LCURL":
            pass
        elif getNext(tokens).type != "DO":
            print("Expected 'do'")
            sys.exit(1)
        body = exp(0,tokens)
        return For(iden,iter,body)
    elif current.type == "WHILE":
        getNext(tokens)
        cond = exp(0,tokens)
        if peekNext(tokens).type == "LCURL":
            pass
        elif getNext(tokens).type != "DO":
            print("Expected 'do'")
            sys.exit(1)
        body = exp(0,tokens)
        return While(cond,body)
    elif current.type == "GO":
        getNext(tokens)
        ap = exp(0,tokens)
        # if peekNext(tokens).type == "LCURL":
        #     pass
        # print(ap)
        if not (ap["type"] == "Apply" or ap["op"] == "DOT" or ap["op"] == "OPDOT"):
            print("Expected a function or method application")
            sys.exit(1)
        return Go(ap)
    elif current.type == "DEF":
        getNext(tokens)
        name = None
        params = []
        if peekNext(tokens).type == "IDEN":
            name = getNext(tokens).val
        if getNext(tokens).type != "LPAREN":
            pass
        # print(name)
        current = getNext(tokens)
        while current != None and current.type != "RPAREN":
            if current.type == "IDEN":
                params.append(current.val)
                current = getNext(tokens)
            elif current.type == "SEP":
                current = getNext(tokens)
                continue
            else:
                print("Expected Identifiers")
                sys.exit(0)
                # break
        body = None
        n = peekNext(tokens)
        while n.val == "\n":
            n = getNext(tokens)
            n = peekNext(tokens)
        if n.type == "ASGN" or n.type == "LCURL":
            if n.type == "ASGN":
                getNext(tokens)
            body = exp(0,tokens)
        else:
            pass
        # print(name)
        # print(params)
        # print(body)
        return Func(name,params,body)
    elif current.type == "LCURL":
        getNext(tokens)
        block = []
        objLit = False
        lit = []
        # print("-------------Parsing Block-----------------")
        # print(tokens)
        current = peekNext(tokens)
        while current.type != "RCURL":
            # if current.val == "\n":
            #     getNext(tokens)
            t = exp(0,tokens)
            if peekNext(tokens).type == "COLON":
                getNext(tokens)
                if not objLit:
                    lit = []
                objLit =  True
                if len(block) > 0:
                    # generate error for mixing of block and object literal  
                    pass
                value = exp(0,tokens)
                n = peekNext(tokens)
                if n.type != "RCURL" and n.val != "\n":
                    # print(n)
                    assert getNext(tokens).type == "SEP"
                elif n.val == "\n":
                    getNext(tokens)
                lit.append((t,value))
            elif objLit and isinstance(t,dict) and t["type"] == "Func":
                if t["name"] == None:
                    print("Function name required in object literal");
                    sys.exit(1)
                name = t["name"]
                t["name"] = None
                n = peekNext(tokens)
                if n.type != "RCURL" and n.val != "\n":
                    # print(n)
                    assert getNext(tokens).type == "SEP"
                elif n.val == "\n":
                    getNext(tokens)
                lit.append((name,t))
            else:
                block.append(t)
            current = peekNext(tokens)
        getNext(tokens)
        # print(block)
        if objLit:
            return ObjectLit(lit)
        return Block(block)
    elif current.type == "LSQB":
        getNext(tokens)
        l = []
        current = peekNext(tokens)
        while current.type != "RSQB":
            l.append(exp(0,tokens))
            current = peekNext(tokens)
            if current.type == "SEP":
                getNext(tokens)
                current = peekNext(tokens)
        getNext(tokens)
        return List(l)
    elif current.type == "NUM":
        getNext(tokens)
        return current.val
    elif current.type == "BOOL":
        getNext(tokens)
        return current.val
    elif current.type == "STR":
        getNext(tokens)
        return current.val
    elif current.type == "UNIT":
        getNext(tokens)
        return current.val
    elif current.type == "IDEN":
        i = Atom(getNext(tokens).val)
        n = peekNext(tokens).type
        if n == "LPAREN":
            # print("----Here----")
            # print(tokens)
            getNext(tokens)
            params = []
            n = peekNext(tokens)
            # print(n)
            while n.type != "RPAREN":
                if n.type == "SEP":
                    # print("passing by")
                    getNext(tokens)
                    n = peekNext(tokens)
                    continue
                e = exp(0,tokens)
                if e != None:
                    params.append(e)
                n = peekNext(tokens)
                # print(n)
            getNext(tokens)
            return Apply(i,params)
        elif n == "LSQB":
            getNext(tokens)
            # params = []
            index = exp(0,tokens)
            # print(n)
            if getNext(tokens).type != "RSQB":
                print("Unmatched paren ']'")
                sys.exit(1)
            return SAccessor(i,index)
        return i
    elif current.type == "LINEEND":
        return getNext(tokens).val
    else:
        print(tokens)
        print("Unexpected Error")
        sys.exit(1)