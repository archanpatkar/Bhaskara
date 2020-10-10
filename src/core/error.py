import sys

# Printing with topological location
def topo_loc(line,lineno,colno,msg=False):
    buff = ""
    buff += "{}| {}\n".format(lineno,line)
    pad = len(str(lineno))+colno+2
    buff += "^\n".rjust(pad)
    if msg:
        buff += msg + "\n"
    buff += "colno {}, lineno {}\n".format(colno,lineno)
    return buff

def lexing_error(msg):
    print(msg)
    sys.exit("Lexing Error")

def parse_error(msg):
    print(msg)
    sys.exit("Parsing Error")