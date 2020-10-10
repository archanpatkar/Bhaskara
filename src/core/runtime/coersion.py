# Add coersion rules for primitives

# bool_ops = ["NOT","AND","OR",""]
# num_ops = ["ADD","SUBS","DIV","MUL","EXP","NEG","POS"]
# def coerse(op,*params):
#     temp = []
#     if op in bool_ops:
#         for p in params:
#             if isinstance(p,int) or isinstance(p,float):
#                 if p > 0:
#                     temp.append(True)
#                 elif p == 0:
#                     temp.append(False)
#             else:
#                 temp.append(p)
#     elif op in num_ops:
#         for p in params:
#             if isinstance(p,bool):
#                 if p:
#                     temp.append(1)
#                 else:
#                     temp.append(0)
#             else:
#                 temp.append(p)
#     return temp

# def astToExp(ast):
#     pass