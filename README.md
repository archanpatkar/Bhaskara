<img src="Bhaskara.png" height="110em" width="125em"/>

### भास्कर - A Dynamic object functional programming language

Bhaskara is an experimental interpreted object functional language focused towards extreme flexibility, expression of metalinguistic abstractions(converging towards language oriented programming) and the eventual goal of creating a powerful reflective/meta-reflective system with the capabilities of self-modifying(homoiconic) code, Aspect Oriented Programming and dynamically changing runtime semantics(by providing a Metaobject Protocol). 

This project serves as an explorational workbench for experimenting and testing idiosyncratic linguistic abstractions and language constructs, design patterns, dsls, runtime semantics etc. 

##### Influenced directly or indirectly by
Javascript, Self, Python, Go, Smalltalk, F#, OCaml, Haskell, Scala, Lisp, CLOS, Scheme, Clojure, Lua, C, Wolfram Language

#### Example code
```
def fac(n) = if n == 0 then 1 else n * fac(n-1)

pfac <- fac >> print

for i in 1..13 do go pfac(i)

def fib(n) => match n with
                  | 0 => 0
                  | 1 => 1
                  | _ => fib(n-1) + fib(n-2)

8 |> fib |> print

def cons(car, cdr) => [car, cdr]
def car(l) => force l[0]
def cdr(l) => force l[1]

def add1(n) {
    cons(n,lazy add1(n+1))
}

def map(fn, l) {
    cons(fn(car(l)), lazy map(fn,cdr(l)))
}

n := map(add1(0), def(v) => v**2)
for i in 0..20 {
    print <| car(n)
    n = cdr(n)
}
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
* Lazy expressions are supported
* Embedded S-Expression support
    * Allowed to pass around as literals
    * Working on allowing templatization
* String templates
    * Currently working on templatization
    * Next will be allowing tagging template literals

## Under implementation
> This also includes long term goals
* Prototypal inheritance (single & multiple)
* Sum types (Disjoint union types)
* Module system
* Python FFI
* Tail call optimization
* In built testing
* Channels
* Destructuring
* Optimized Goroutine scheduler
* Tagged string literals
* Scala like `_` based lambda literal transformations
* Haskell style List Comprehensions
* Lisp style Macros
* Code quotations
* RegExp Literals
* Proxy and AOP
* Sugar syntax based on AOP for DbC (Design by Contract e.g preconditions, postconditions etc.)
* Monadic bind operator and Do notation
* Additonal call by name eval strategy for thunks
* Dynamically scoped functions/thunks
* Coroutines, async-await(more specific form of do notation?) and First Class Continuations?
* Homoiconic transforms
* Self hosted transpiler to Javascript (with Javascript FFI)
* Gradual typing (Based on gradually typed hindley-milner with dynamic type inference: [ref](https://dl.acm.org/doi/10.1145/3290331))
* Runtime persistance to JSON or Custom image format
* Unicode support
