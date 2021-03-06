<div align="center">
<img src="Bhaskara.png" height="280em" width="400em"/>
</div>

### भास्कर - A Dynamic object functional programming language

Bhaskara is an experimental interpreted object functional language focused towards extreme flexibility, expression of metalinguistic abstractions(trying to support language oriented programming) and the eventual goal of creating a powerful reflective/meta-reflective system with the capabilities of self-modifying(homoiconic) code, Aspect Oriented Programming and dynamically changing runtime semantics(by providing a Metaobject Protocol).

This project serves as an explorational workbench for experimenting and testing idiosyncratic linguistic abstractions and language constructs, design patterns, dsls, runtime/operational semantics etc. 

##### Influenced directly or indirectly by
Javascript, Self, F#, Python, Go, Smalltalk, OCaml, Haskell, Kotlin, Scala, Lisp, CLOS, Scheme, Clojure, Lua, C, Wolfram Language, Racket

#### Example code
```
def fac(n) = if n == 0 then 1 else n * fac(n-1)

pfac <- fac >> print

for i in 1..13 do go pfac(i)

def fib(n) => match n with
                  | x when x <= 1 => x
                  | _ => fib(n-1) + fib(n-2)

8 |> fib |> print

def cons(head, tail) => [head, tail]
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

def reader(ch) => while true do ch.recv() |> print
def writer(ch,n) => for i in 0..n do ch.send(i)

ch1 := channel()
go reader(ch1)
writer(ch1,100)
```

## Currently supports
> The codebase is under heavy developement(Features may break!) and constantly updated
* Control Flow
    * if-elif-else
    * for loop
    * while loop
    * pattern matching with guards
        1. Literal based 
        2. Variable based
        3. Wildcard based
* Functions
    * Functions and Lambdas 
        1. Lexically Scoped (with Closures)
        2. Dynamically Scoped
    * Decorators
* Object
    * Object literals
    * List literals
    * Indexing `name[exp]` syntax
    * Dot syntax `obj.prop`
    * Optional chaining
    * Method invocation
    * Basic operator overloading
    * Prototypal Inheritance
* Concurrency
    * `go` syntax supported (currently assigns a thread from a thread pool)
    * `go` expression returns an Async Future/Promise which is fulfilled with the return value of routine
    * `channel` currently supported through objects(will give syntactic support through operator overloading in the future)
* Lazy expressions
* Basic Code Quotations
* Haskell style List Comprehensions (WIP - alpha)
* Embedded S-Expression support
    * Allowed to pass around as literals
    * Working on allowing templatization

## Under implementation
> This also includes long term goals
* Multiple prioritized inheritance & Sender path tie breaker resolution
* Sum types (Disjoint union types)
* First Class Continuations (call/cc)
* Exception Handling
* Module system
* Tail call optimization
* Optimized Goroutine scheduler
* String templates and Tagged string literals
* Scala like `_` based lambda literal sugar
* RegExp Literals
* Proxy and AOP 
* Syntactic and semantic support for Design by Contract(which is inspired Hoare Triples) e.g preconditions, postconditions.
* Monadic bind operator and Do notation
* Dynamically scoped thunks(delayed expressions) and call by name eval strategy for thunks
* Coroutines, async-await(more specific form of do notation?) 
* Delimited Continuations
* Homoiconic transforms
* Lisp style Macros
* Code quotations
* Self hosted transpiler to Javascript
* Gradual typing
* Runtime persistance to JSON or Custom image format
* Unicode support
