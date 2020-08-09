import json
from os import sys
from pprint import pprint
from util.panim import *
from lexer import Tokenizer
from parser import Parser
from interpreter import *

# भास्कर - An Object-Functional programming language
parser = Parser(Tokenizer())

def run(code):
    return eval(parser.parse(code))

def repl():
    foreground(GREEN) 
    print(bold("Bhaskara 0.0.1"))
    print("Type 'help' for more information") 
    foreground(WHITE)
    read = input(">>> ") 
    while read != "q" and read != "quit" and read != "exit" and read != "bye": 
        if(read == "help"):
            pass
        if(read == "clear"):
            clrscr()
            gotoxy(0,0)
        else:
            print(run("{}\n".format(read))[-1])
        read = input(">>> ") 
    print("") 

if __name__ == "__main__":
    if len(sys.argv) > 1:
        code = open(sys.argv[1],"r").read()
        if len(sys.argv) > 2:
            if sys.argv[2] == "--compile":
                jast = json.dumps(parse(tokenize(code)))
                open(sys.argv[1].split(".")[0]+".json","w").write(jast)
        else:
            if sys.argv[1].split(".")[1] == "json":
                eval(json.dumps(code))
            else:
                # print(code)
                # print(tokenize(code))
                run(code)
                while not GLOBAL_POOL.jobs.isEmpty():
                    pass
    else:
        # pass
        repl()