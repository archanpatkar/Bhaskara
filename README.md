### भास्कर - A Dynamic object functional programming language

Bhaskara is an object functional language inspired by Javascript, Self, Python, Go and F# (generally from ML and Haskell family of languages). It is an expression oriented language where everything is an expression. The language supports prototypal object system with multiple inheritance. The language also has functional features like Auto-currying, pattern matching, sum types, lazy expressions, pipe operator etc. The language also provides Go like concurrency primitives i.e. Goroutines and Channels.

#### Example code
```
def fac(n) = if n == 0 then 1 else n * fac(n-1)

for i in 1..13 do (go fac(i) then def(v) => v |> print)

result := (4 |> fac)

result |> print

result = result/2

result |> print

printFac <- def(n) { n |> fac |> print }

def log(f) {
    def() {
        print("Entering")
        f(*args)
        print("Exiting")
    }
}

@log
def demo() => print("demo!")

for i in range(10) {
    demo()
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
    * if-elif-else
    * for loop
    * while loop
* Functions
    * Normal functions
    * Lambdas and Closures
    * Decorators
* Object
    * Object literals
    * List literals
    * Indexing `name[exp]` syntax
    * Dot syntax `obj.prop`
    * Optional chaining
    * Method invocation
* Concurrency
    * `go` syntax supported (internally uses a custom thread pool)
    * `go` returns an Async Future/Promise which is fulfilled with the return value of routine which was executed by the thread
    * Syntactic support using `then`(sugar created over the promise returned) for chaining of continuation/lambda after `go` expression.
* Lazy expressions supported
* Basic embedded S-Expression support

## Under implementation
> This also includes long term goals
* Pattern matching
* Protypal inheritance (single & multiple)
* Protocol based operator overloading
* Sum types (Disjoint union types)
* Module system
* Python FFI
* In built testing
* Channels
* Spreading and Destructuring
* Optimized Goroutine scheduler
* Tagged string literals
* Haskell style List Comprehensions
* Lisp style Macros
* Code quotations
* Proxy and AOP
* Sugar syntax based on AOP for DbC (Design by Contract)
* Monadic bind operator and Do notation
* Dynamically scoped functions
* Coroutines and generators
* Homoiconic transforms(?)
* Self hosted transpiler to Javascript (with Javascript FFI)
* Gradual typing
* Runtime persistance to JSON or Custom image format