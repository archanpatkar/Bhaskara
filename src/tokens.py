from collections import namedtuple
ops = [
        "+","-","/","*","(",")","^","=","|","&","~","@",
        "#","==",">","<",">=","<=","~=","[","]","{","}",
        ",","->","%","!",":","$","'",'"',".","?"
    ]
keywords = [
                "true","false","neither","both","if","then",
                "else","def","unit","do","while","for","in",
                "lazy","force","assert","go","break","continue"
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
    "**":"EXP",
    "|":"OR",
    "v":"OR",
    "&":"AND",
    "^":"AND",
    "~":"NOT",
    "->":"IMP",
    "=":"ASGN",
    ">":"GT",
    "<":"LT",
    "==":"EQ",
    ">=":"GTEQ",
    "<=":"LTEQ",
    "~=":"NOTEQ",
    "<-":"CONST",
    "if":"IF",
    "then":"THEN",
    "else":"ELSE",
    "def":"DEF",
    "while":"WHILE",
    "for":"FOR",
    "in":"IN",
    "do":"DO",
    "lazy":"LAZY",
    "force":"FORCE",
    "go":"GO",
    "!":"FORCE",
    "!!": "ASSERT",
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
    "/*":"LCOMM",
    "*/":"RCOMM",
    "|>":"LPIPE",
    "<|":"RPIPE",
    ".":"DOT",
    "?.":"OPDOT",
    ":":"COLON",
    "??":"NULLISH"
}
binaryops = [
                "ADD","SUBS","DIV","MUL","EXP","OR","AND",
                "LT","GT","EQ","IMP","NOTEQ","LTEQ","GTEQ",
                "VAR","ASGN","LPIPE","RPIPE","DOT","OPDOT",
                "NULLISH","LPAREN", "LSQB"
            ]
unaryops = ["SUBS","ADD","NOT"]
Token = namedtuple("Token",["type","val"])