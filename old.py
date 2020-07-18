# Atom = namedtuple("Atom",["value"])
# BinOp = namedtuple("Binary",["left","op","right"])
# UnOp = namedtuple("Unary",["op","value"])

# def parse(tokens):
#     token = getNext(tokens)
#     prev = None
#     while token != None:
#         current = None
#         if token.type == 'num':
#             current = Atom(token.val)
#         elif token.type in binaryops and prev != None:
#             current = {"type":"B", "left":prev, "op":token.type}
#         elif token.type in unaryops and prev == None:
#             current = {"type":"U", "op":token.type}
#         elif token.type == '(':
#             subt = []
#             token = getNext(tokens)
#             while token != None and token.type != ')':
#                 subt.append(token)
#                 token = getNext(tokens)
#             current = parse(subt)
#         if isinstance(prev,dict):
#             if prev["type"] == "B":
#                 prev = BinOp(prev["left"],prev["op"],current)
#             elif prev["type"] == "U":
#                 prev = UnOp(prev["op"],current)
#         else:
#             prev = current
#         token = getNext(tokens)
#     return prev