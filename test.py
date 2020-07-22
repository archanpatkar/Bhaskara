def test(str):
    tokens = tokenize(str)
    print("printing")
    pprint(tokens,indent=4)
    ast = parse(tokens)
    pprint(ast,indent=4)
    eval(ast)

# test("""
# def test2(a,b,c,d)
# {
#     print <| "Welcome to test2!!!" 
#     a + b + c + d
# }

# test2(10,20,400,-555) |> print
# """)

# test(
# """
# z := if(true & false) {
#     x := 5
#     x
# } else (y := 10)

# def f1(x) = x*3

# def f2(x,y) {
#     x + y
# }

# f1(10)

# f2(1,f1(2))

# print(10)

# z
# """
# )

# test("if true & (x := 5) then x + 10 else x")
# print(eval(parse(tokenize(
# """
# z := if(true & false) {
#     x := 5
#     x
# } else (y := 10)

# z
# """
# ))))

# test('x := "one"')