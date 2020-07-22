### भास्कर - A Functional Programming Language

## Introduction

### `Small canonical code example`

```
def cube(x) = x^3
def fac(n) = if n == 0 then 1 else n * fac(n-1)

print(fac <| 3)
4 |> fac |> print

def test(a,b,c,d) 
{
    print <| "Welcome to test!!!" 
    a + b + c + d
}

test2(10,2000,400,-555) |> print

if(true ~= true == false) {
    print("Booleans!")
}
else {
    print("Not so correct!")
}

// This is a mutable variable
res := (cube(3) |> fac)

// This is a constant variable
j <- (res |> cube)

def server(cb) = cb("I called you back!")

server(def (str) { str |> print })

def(str){ str+"!!!" |> print } |> server
```