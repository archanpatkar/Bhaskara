import sys

def lexing_error(token):
    print("Unexpected character -> {}".format(token))
    sys.exit("Lexing Error")

def parse_error(msg):
    print(msg)
    sys.exit("Parsing Error")