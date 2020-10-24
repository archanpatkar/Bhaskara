from collections import namedtuple
# Shift the whole thing to json

ops = [
        "+","-","/","*","(",")","^","=","|","&","~","@",
        "#",">","<","[","]","{","}",",","%","!",":",
        "$","'",'"',".","?","`"
    ]
keywords = [
                "T","F","N","B","true","false","neither","both","if","then",
                "else","def","unit","do","while","for","in","match","quote",
                "macro", "unquote", "lazy","force","assert","go","break","continue",
                "type","do","elif","panic","when","type","with","to","yield","dyn",
                "is","class","enum"
        ]
white = [" ","\r","\t"]
digits = ["0","1","2","3","4","5","6","7","8","9"]
lineend = ["\n",";"]

# Create the double dict on the fly after loading the json 
# from the compound ops field 
double = {
    "=":["=",">"],
    ">":["=",">"],
    "<":["=","|","-","@"],
    "~":"=",
    "-":">",
    ":":"=",
    "|":">",
    "*":"*",
    "?":".",
    ".":".",
    "@":">"
}

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
    "&":"AND",
    "~":"NOT",
    "->":"IMP",
    "=":"ASGN",
    ">":"GT",
    "<":"LT",
    "==":"EQ",
    ">=":"GTEQ",
    "<=":"LTEQ",
    "=>":"ARROW",
    "~=":"NOTEQ",
    "<-":"CONST",
    "if":"IF",
    "then":"THEN",
    "else":"ELSE",
    "elif":"ELSEIF",
    "def":"DEF",
    "when":"WHEN",
    "is":"IS",
    "while":"WHILE",
    "for":"FOR",
    "in":"IN",
    "do":"DO",
    "match":"MATCH",
    "lazy":"LAZY",
    "assert":"ASSERT",
    "force":"FORCE",
    "type":"TYPE",
    "panic":"PANIC",
    "go":"GO",
    "with":"WITH",
    "dyn":"DYN",
    "enum":"ENUM",
    "!":"FORCE",
    "!!": "ASSERT",
    ",":"SEP",
    ";":"SEMI",
    "@":"FORALL",
    "#":"EXISTS",
    "[":"LSQB",
    "]":"RSQB",
    "<@":"QUOS",
    "@>":"QUOE",
    "{":"LCURL",
    "}":"RCURL",
    "$":"EMBED",
    ":=":"VAR",
    "//":"COMM",
    "/*":"LCOMM",
    "*/":"RCOMM",
    "|>":"LPIPE",
    "<|":"RPIPE",
    ">>":"SHIFT",
    ">>=":"BIND",
    ".":"DOT",
    "?.":"OPDOT",
    ":":"COLON",
    "??":"NULLISH",
    "..":"RANGE",
    "`":"TEMP"
}
binaryops = [
                "ADD","SUBS","DIV","MUL","EXP","OR","AND",
                "LT","GT","EQ","IMP","NOTEQ","LTEQ","GTEQ",
                "VAR","ASGN","LPIPE","RPIPE","DOT","OPDOT",
                "NULLISH","LPAREN","LSQB","MOD","RANGE","IS"
            ]
unaryops = ["SUBS","ADD","NOT","ASSERT","PANIC"]
Token = namedtuple("Token",["type","val","line","col"])