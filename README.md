### भास्कर - A Dynamic object functional programming language

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

```
pg1 := {
    balance:0,
    lt:0,
    def deposit(v) {
        if v > 0 {
            this.balance = this.balance + v
            this.lt = v
        }
    },
    def withdraw(v) {
        if v <= this.balance {
            this.balance = this.balance - v
            this.lt = -v
        }
    },
    def statement() {
        this.balance |> print
        this.lt |> print
    }
}

pg1.deposit(10)
pg1.withdraw(3)
pg1.statement()

pg1?.transaction(1000)
```

## Currently supports
* Control Flow
    * if-else
    * for loop
    * while loop
* Functions
    * Normal functions
    * Lambdas and Closures
* Object
    * Object literals
    * List literals
    * Indexing `name[exp]` sytax
    * Dot syntax `obj.prop`
    * Optional chaining
    * Method invocation
* Concurrency
    * `go` syntax supported (internally uses a custom thread pool)

## Under implementation
> This also includes long term goals
* Pattern matching
* Protypal inheritance (single & multiple)
* Protocol based operator overloading
* Sum types (Disjoint union types)
* Module system
* Python FFI
* In built testing
* Lazy expressions
* Optimized Goroutine scheduler and Channels
* Tagged string literals
* Code quotations
* Proxy and AOP
* Sugar syntax based on AOP for DbC (Design by Contract)
* Monadic bind operator and Do notation
* Dynamically scoped functions
* Coroutines and generators
* Homoiconic transforms(?)
* Self hosting
* Runtime persistance to JSON or Custom image format
