# This is temporary will be replaced by objects and protocols
biopmap = {
    "ADD": lambda x,y: x + y,
    "SUBS": lambda x,y: x - y,
    "MUL": lambda x,y: x * y,
    "MOD": lambda x,y: x % y,
    "DIV": lambda x,y: x / y,
    "AND": lambda x,y: x and y,
    "OR": lambda x,y: x or y,
    "LT": lambda x,y: x < y,
    "GT": lambda x,y: x > y,
    "EQ": lambda x,y: x == y,
    "GTEQ":lambda x,y: x >= y,
    "LTEQ":lambda x,y: x <= y,
    "NOTEQ": lambda x,y: x != y,
    "IMP": lambda x,y: not(x) or y,
    "EXP": math.pow,
    "LPIPE": lambda x,y: y(x),
    "RPIPE": lambda x,y: x(y),
    "RANGE": lambda x,y: list(range(x,y)),
    "SHIFT": lambda f1,f2: lambda *params: f2(f1(*params))
}

unopmap = {
    "SUBS": lambda x: -x,
    "ADD": lambda x: +x,
    "NOT": lambda x: not(x)
}
