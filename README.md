### भास्कर - A Functional Programming Language

Bhaskara is an object functional language inspired by Javascript, Self, Python, Go and F# (generally from ML family of languages). It is an expression oriented language where everything is an expression. The language supports prototypal object system with multiple inheritance. The language also has functional features like Auto-currying, pattern matching, sum types, lazy expressions, pipe operator etc. The language also provides Go like concurrency primitives i.e. Goroutines and Channels.

#### Example code
```
def fac(n) = if n == 0 then 1 else n * fac(n-1)

result := (4 |> fac)

result |> print

result = result/2

result |> print

printFac <- def(n) { n |> fac |> print }

for i in range(10) {
    go printFac(i)
}
```

## Currently supports


## Under implementation
