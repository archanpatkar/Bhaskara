from collections import namedtuple
ops = [
        "+","-","/","*","(",")","^","=","|","&","~","@",
        "#","==",">","<",">=","<=","~=","[","]","{","}",
        ",","->","%","!",":","$"
    ]
keywords = [
                "true","false","neither","both","if","then",
                "else","def","unit","do","while","for","in"
        ]
white = [" ","\r","\t"]
digits = ["0","1","2","3","4","5","6","7","8","9"]
bools = ["T","F","N","B"]
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
    "while":"WHILE",
    "for":"FOR",
    "in":"IN",
    "do":"DO",
    ",":"SEP",
    ";":"SEMI",
    "@":"FORALL",
    "#":"EXISTS",
    "[":"LSQB",
    "]":"RSQB",
    "{":"LCURL",
    "}":"RCURL",
    ":=":"VAR",
    "//":"COMM",
    "|>":"LPIPE",
    "<|":"RPIPE"
}
binaryops = [
                "ADD","SUBS","DIV","MUL","EXP","OR","AND",
                "LT","GT","EQ","IMP","NOTEQ","LTEQ","GTEQ",
                "VAR","ASGN","LPIPE","RPIPE"
            ]
unaryops = ["SUBS","ADD","NOT"]
Token = namedtuple("Token",["type","val"])