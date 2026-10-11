# Named empty classes and object identity

The source compiler records named empty class declarations with their checked
origin, resolved name, flags and line. Early declarations become active before
the first statement; conditional and function-local declarations publish only
when execution reaches them. A normalized active-name table keeps declaration
timing separate from compiled source. Redeclaration reports the original name
and location; occupied internal class, interface and enum names follow the
pinned CLI `-n` catalogue of 166 names. Enum kinds use
`ReflectionClass::isEnum()`. The catalogue supplies names and diagnostic kinds,
not internal bodies. Its key/display names are literal byte vectors, preserving
all 166 ordered values while avoiding repeated ASCII conversion. Complete
old/new value equality and the pinned native catalogue are recorded in the
[catalogue review](../../coverage/semantics/internal-class-catalogue-review.json).

`new` resolves a named, concrete user class before allocating an object in the
existing owned heap. The current admitted form has no constructor arguments or
members. Copies preserve object identity; two distinct empty instances of the
same class compare loosely equal, while strict comparison uses identity.
Literal `instanceof` tests the active source class or an existing `Closure`
object; missing class names and scalar left operands return false. Undefined
variables still issue their usual warning. Class-typed parameters and returns
accept the exact nominal source class, with case-insensitive spelling.
An empty instance is noncallable in direct, first-class and pipe calls and in
`callable` type checks. Its array cast is empty; Closure keeps its separate
array-cast behavior. Object key, offset and conversion errors use the source
class name.

Source origins authenticate descriptors, active bindings, class/new/instanceof
tasks and paused `instanceof` results. Owned objects remain live through arrays
and are released after their final owner. The pinned engine routes are `zend_compile_class_decl`,
`zend_compile_new` and `zend_compile_instanceof` in
`vendor/php-src/Zend/zend_compile.c`, and the `ZEND_NEW` and `ZEND_INSTANCEOF`
handlers in `Zend/zend_vm_def.h`.

The rules are in `126-class-compiler.watsup` and `127-class-runtime.watsup`.
[The review](../../coverage/semantics/object-classes-review.json) records the
source and paused-state checks. Other internal-class construction, constructor
arguments, inheritance, properties, methods, dynamic class names, late-bound
`self`/`parent`/`static`, array and class-method callback invocation, and
lifecycle protocols remain separate obligations.

A single zero-argument builtin `#[AllowDynamicProperties]` resolves through the
class declaration's actual namespace/import scope. Named nonreadonly classes and
their published source descendants permit dynamic-property creation without
minting a deprecation handler owner. The capability uses authenticated source,
compiled names and parent links, with no additional owning field. Trait, interface
and readonly targets fail before interface/body checks; attributed trait/interface
diagnostics use the token-derived declaration keyword line. Mixed/repeated/argument
and user attributes, anonymous/enum targets and wider attribute protocols remain
Unsupported. The [attribute review](../../coverage/semantics/allow-dynamic-properties-review.json)
separates ten source agreements from genuine write/history/link checks.

Ordinary anonymous `new class` expressions use source-authenticated class headers
and publish a parentless class before the first runtime visit. The compiled name
is `class@anonymous`, NUL, the original filename, start line and a hexadecimal
uint32 suffix. The suffix follows actual compiler RTD-key consumption; it is not a
runtime visit count. Namespace scope does not prefix the name, and distinct sites
on one physical line remain distinct. Each visit allocates a fresh object from
the same class, with independent property storage and the real lexical scope.

Module383 admits authentic unit0 contexts with plain empty named classes globally
or in valid named namespace sections (bracketed or unbracketed), including an
unnamed bracketed global namespace body.
Eligible root declarations bind early and consume no RTD key; deferred declarations
consume one even when their branch never executes. The compiler folds descriptors
in its actual walk order, authenticating source, name, line and derived early binding
rather than counting descriptors. Whole-source projection and declaration history
retain compiler order; the counter helper alone is not a general ordering certificate.
Standalone global blocks preserve early eligibility through nested blocks. The
placement helper authenticates every actual `NStmtBlock` ancestor; matching
field/index paths beneath conditionals or other control statements stay deferred.
An earlier deferred same-name declaration does not block a later eligible early
declaration. The [block-class review](../../coverage/semantics/anonymous-block-rtd-review.json)
separates native originals, real no-op/publication/allocation frontiers and pure
ancestry/receipt queries. Namespace bodies qualify declaration names and
retain root eligibility through actual block ancestors. Conditional declarations
keep the namespace prefix while consuming a deferred key. Full qualified names
separate same-short-name declarations and namespace-local internal-looking names;
anonymous names remain unqualified and use the shared unit counter. The namespace
context helper supplies the prefix; exact class occurrence and terminal ancestry
checks remain separate. The [namespace-class review](../../coverage/semantics/anonymous-namespace-rtd-review.json)
separates native/source agreements, qualified publication and early no-op frontiers
from pure placement/descriptor/receipt queries. Repeated unbracketed sections
retain qualified ownership and share the unit counter; methods keep their declaring
namespace after caller namespace switches. The
[unbracketed review](../../coverage/semantics/anonymous-unbracketed-rtd-review.json)
separates actual compiled constant reads/method frames from pure admission queries.
ABSENT namespace bodies still require bracketed style. Plain empty named declarations
inside direct root or valid namespace-body noarg by-value untyped named functions
are deferred and consume one key. Per-occurrence admission authenticates the actual
function placement and signature; named descendants in nested, conditional or
block-contained functions remain Unsupported. Direct root or namespace-body variable
assignments to static no-capture noarg by-value untyped Closures also admit plain
empty named descendants. Admission authenticates the actual expression statement,
by-value assignment, ordinary variable target and Closure signature; other targets,
placements, captures and signatures remain Unsupported. Runtime publication appends a
source-bound PDRCLASS cause with the function or Closure/callsite, preserving the saved caller
frame. Reversed calls publish in call order, and a guarded repeat preserves one
publication while returning independent defaults. The
[named-factory review](../../coverage/semantics/anonymous-named-factory-rtd-review.json)
separates actual publication/allocation frontiers from pure admission/cause queries.
The [named-Closure review](../../coverage/semantics/anonymous-named-closure-rtd-review.json)
also checks anonymous allocation before Closure creation, genuine capture/call frames,
and second-call fatal redeclaration before another publication or allocation.
Other named bodies/modifiers, interfaces/traits/enums and nested class bodies remain
Unsupported. Anonymous forms are parentless, without
interfaces, attributes or constructor arguments; public untyped property defaults
use the existing literal/constant-concat parser, and public noarg by-value nonmagic
methods use existing body compilation. Plain global noarg/by-value/untyped named
functions and static no-capture Closures can contain these anonymous classes.
The compiler records only the authentic class checkpoint while inside the factory, then saves
the image after restoring the containing unit scope. This publishes the class
before any call and preserves compilation order independently of call order.
Ordinary function/Closure declarations do not consume the RTD counter. Wider
factory contexts and incomplete containing-scope images remain Unsupported;
include/eval units, inheritance, attributes, wider members/defaults
and wider RTD ordering remain required. The
[mixed-class review](../../coverage/semantics/anonymous-mixed-rtd-review.json)
separates early/deferred name consumption from runtime publication and factory call order.

Public zero-parameter by-value untyped `__construct` methods use the ordinary
constructor protocol, including default-public and case-insensitive spelling.
Authenticated anonymous source/name receipts select the method after allocation;
property defaults precede the body, and automatic `new` ignores its return value.
Explicit constructor calls retain ordinary method return behavior. Throws retain
the original Throwable, execute ordinary `finally` blocks and leave caller
assignment untouched. Ordinary ownership retires unescaped failed receivers and
preserves escaped receivers. Constructor arguments,
parameters/types, nonpublic constructors and broader lifecycle interactions remain
required. The [constructor review](../../coverage/semantics/anonymous-constructors-review.json)
separates original-source agreement, actual call/unwind states and pure receipt queries.

Raw `getTrace()['class']` retains the entire generated name. The shared trace
renderer applies `c_string` only to the displayed CLASS bytes, matching Zend's
`TRACE_APPEND_KEY`; `getTraceAsString()` therefore prints `class@anonymous`.
Stored names and trace arrays remain intact. The
[anonymous class review](../../coverage/semantics/anonymous-classes-review.json)
keeps five exact originals and publication/allocation, factory and trace frontiers
at their distinct cuts. Pure formatter/domain/display and compiler-context queries
are separated from reached states; earlier failures retain zero credit.
