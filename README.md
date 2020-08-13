### भास्कर - A Dynamic object functional programming language

Bhaskara is an experimental interpreted object functional language focused towards flexibility with it's dynamic nature and expression of metalinguistic abstractions(trying to facilitate language oriented programming), and  the eventual goal of creating a powerful reflective/meta-reflective system with the capabilities of self-modifying(homoiconic) code, surface level dynamic AOP using Proxies and more powerful substratum of dynamically changing runtime semantics(using a Metaobject Protocol which allows to blur the boundaries of things, action and interpretation creating a strange loop). The language is inspired by Javascript, Self, Python, Go, Smalltalk, F# (generally from ML and Haskell family of languages) and Lisp(and CLOS,Scheme,Clojure...). It is also an expression oriented language where everything is an expression. The language has a prototypal object system with multiple inheritance, has functional features like Auto-currying, pattern matching, sum types, lazy expressions, pipe operator etc. The language provides Go like concurrency primitives i.e. Goroutines and Channels.

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
    * pattern matching with guards
        1. Literal based 
        2. Variable based
        3. Wildcard based
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
    * Basic operator overloading
* Concurrency
    * `go` syntax supported (internally uses a custom thread pool)
    * `go` returns an Async Future/Promise which is fulfilled with the return value of routine which was executed by the thread
    * Syntactic support using `then`(sugar created over the promise returned) for chaining of continuation/lambda after `go` expression.
* Lazy expressions supported
* Basic embedded S-Expression support

## Under implementation
> This also includes long term goals
* Protypal inheritance (single & multiple)
* Sum types (Disjoint union types)
* Module system
* Python FFI
* Tail call optimization
* In built testing
* Channels
* Spreading and Destructuring
* Optimized Goroutine scheduler
* Tagged string literals
* Scala like `_` based lambda literals
* Haskell style List Comprehensions
* Lisp style Macros
* Code quotations
* Proxy and AOP
* Sugar syntax based on AOP for DbC (Design by Contract)
* Monadic bind operator and Do notation
* Dynamically scoped functions
* Coroutines, generators and async-await(more specific form of do notation?) / Fibers(with first class continuations?)
* Homoiconic transforms
* Self hosted transpiler to Javascript (with Javascript FFI)
* Gradual typing
* Runtime persistance to JSON or Custom image format