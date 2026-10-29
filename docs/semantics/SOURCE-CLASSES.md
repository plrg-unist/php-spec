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

Dynamic RHS `instanceof` accepts ordinary CVs and zero-argument named by-value
producers. It captures the class of a live source object or `stdClass` without
calling `__toString`, then releases an RHS temporary before reading a delayed left CV.
An owned left temporary remains live until matching caches the Boolean, which
survives its destructor. Runtime string names use case-insensitive fully qualified
lookup, strip one leading backslash and do not expand imports or invoke autoload.
An invalid nonowning RHS errors before even an undefined left is read. A scanner
int/float/string literal left folds false and skips compiling/executing the RHS. The
[dynamic review](../../coverage/semantics/dynamic-instanceof-review.json) separates
four source agreements from 335 focused premises and the earlier fixture failures.
Other operand expressions/object kinds, reference-return producers, owning invalid
RHS cleanup and wider throwing-destructor histories remain partial.

An owning dynamic `new` selector now finishes ordinary disposal before allocation,
constructor access and argument evaluation. Captured class history owns no selector
and remains valid after its retirement. A supplied selector-destructor Exception
cancels construction without acquiring a premature private-access Error as `Previous`;
a retained selector instead permits the access Error before its later destruction.
Public construction reads argument 99 after the selector changes the live CV.
The [selector review](../../coverage/semantics/dynamic-new-selector-review.json)
separates four source agreements from 370 focused premises and earlier fixture
failures. A derived nonowning-operand bridge preserves the existing route without
renewing its source credit. Wider selector/constructor/autoload and reference-return
lifetimes retain their separate partial boundaries.

Source origins authenticate descriptors, active bindings, class/new/instanceof
tasks and paused `instanceof` results. Owned objects remain live through arrays
and are released after their final owner. The pinned engine routes are `zend_compile_class_decl`,
`zend_compile_new` and `zend_compile_instanceof` in
`vendor/php-src/Zend/zend_compile.c`, and the `ZEND_NEW` and `ZEND_INSTANCEOF`
handlers in `Zend/zend_vm_def.h`.

The rules are in `126-class-compiler.watsup` and `127-class-runtime.watsup`.
[The review](../../coverage/semantics/object-classes-review.json) records the
source and paused-state checks. Other internal-class construction, constructor
arguments, inheritance, properties, methods, wider dynamic class-name forms, late-bound
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

Later include/eval units derive their starting suffix from authenticated completed
compilations, beginning with unit0 and preserving chronological source history.
Compiler-derived class descriptors determine each unit's cost; functions, Closures
and arrows do not themselves consume class RTD keys. Recompilation gets a new
name, repeated execution shares its compiled class, and include_once skips preserve
the image. The original parentless checks remain in the
[dynamic-unit review](../../coverage/semantics/anonymous-dynamic-units-review.json);
the dependency extension is described below.

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
inside noarg by-value untyped named functions declared at root or a valid namespace
body, including standalone Block chains, are deferred and consume one key. Per-occurrence
admission authenticates the actual function signature and every Block ancestor.
Eligible functions are callable before their blocks; the later function statement
preserves state apart from consuming its task. Named descendants in nested
or other unsupported function ancestors remain Unsupported. The
[block-factory review](../../coverage/semantics/anonymous-block-factory-rtd-review.json)
separates publication, no-op and allocation frontiers from pure ancestry queries.
Exact named functions directly in actual `if` main,
`elseif` or `else` bodies also admit plain empty named descendants. Anonymous
names are already live while
the function remains unavailable; its executed statement appends one source-bound
CALLABLES/PDRFUNCTION entry, and later calls publish its named classes. A skipped
declaration stays unavailable. Branch admission checks the actual If and ElseIf/Else
ancestors; equal path lengths do not identify a namespace host. Mutually exclusive
same-name declarations call the published origin, preserving its class and anonymous
site rather than selecting the first compiled descriptor. The
[branch-factory review](../../coverage/semantics/anonymous-branch-factory-rtd-review.json)
separates real callable/class publication and saved-frame allocations from pure
placement/signature/receipt queries. Two executed case-insensitive same-name declarations
fail at the second statement, retaining the first callable and history before either
body runs. The [conditional-factory review](../../coverage/semantics/anonymous-conditional-factory-rtd-review.json)
separates these real publication/allocation/fatal steps from pure placement queries.
The If host may lie at root or a valid namespace body through authenticated
standalone Block chains and mixed If/While ancestry. Admission checks every actual host ancestor
and the actual main/elseif/else suffix; path lengths are checked before slicing.
Standalone Block chains inside the branch body are also admitted. A shrinking
path rule authenticates each actual parent Block and child before reaching the
source-authenticated If/ElseIf/Else branch; same-shaped Do or other-loop paths fail.
The [branch-body Block review](../../coverage/semantics/anonymous-branch-block-rtd-review.json)
separates these real Block entries and publication/allocation frontiers from pure
ancestry and receipt queries.
The [Block-branch review](../../coverage/semantics/anonymous-block-branch-rtd-review.json)
separates authentic mixed function/Closure frontiers from pure path/receipt queries.
The [nested-host review](../../coverage/semantics/anonymous-nested-branch-rtd-review.json)
adds strictly shrinking source-authenticated If ancestry. Genuine nested If/CHOOSE
steps consume each condition once before selected publication or creation; skipped
outer hosts retain live anonymous names without callable publication.
Exact named functions also admit plain empty named descendants in authentic
`while` bodies through authenticated standalone Block chains. The host must occur at root or a valid namespace body
through authenticated standalone Block, existing If main/elseif/else ancestry or
actual nested While hosts.
Anonymous names preexist false
loops, while selected function statements publish only when executed.
Named descendants under unsupported loop or function ancestors remain Unsupported.
Variable assignments to static no-capture noarg by-value untyped Closures at root
or a valid namespace body, through authenticated standalone Block chains or
in actual `if` main, `elseif` or `else` bodies through authenticated branch-body
Block chains and the same mixed Block/If/While host ancestry, or in authentic `while`
bodies through standalone Block chains with the same root/namespace/Block/If or
authenticated nested While host ancestry,
admit plain empty named descendants.
Admission authenticates the expression statement, by-value assignment, ordinary
variable target, exact Closure signature and actual Block, conditional, While or Do ancestors.
Anonymous names exist before creation; skipped assignments preserve their variables.
The [conditional-Closure review](../../coverage/semantics/anonymous-conditional-closure-rtd-review.json)
separates real creation/capture, named publication and fresh allocations from pure
placement/signature/receipt queries. The [While review](../../coverage/semantics/anonymous-while-factory-rtd-review.json)
checks false LOOP_TEST/CHOOSE skipping, real selection/publication, two distinct
REALCLOSURE instances from one unchanged template, guarded defaults and the
same-source function redeclaration fatal on its second iteration before any factory
body call in that probe. The
[While body-Block review](../../coverage/semantics/anonymous-while-block-rtd-review.json)
checks authentic Block entry and real publication/creation/allocation frontiers,
retaining old/current Closure receivers from one template and fresh defaults.
The [If-hosted While review](../../coverage/semantics/anonymous-conditional-while-rtd-review.json)
checks genuine If/CHOOSE selection before selected factory publication or creation,
then authentic targets, saved frames, class history and first allocations.
The [nested-While review](../../coverage/semantics/anonymous-nested-while-rtd-review.json)
authenticates both actual While ancestors and intervening/body Blocks, selected
publication and genuine function or old/current Closure allocation targets.
The [While-hosted If review](../../coverage/semantics/anonymous-while-if-rtd-review.json)
authenticates each actual If/While host and selected branch, with genuine If/CHOOSE
transitions before publication or creation and saved-frame allocations.
Both exact factory forms also admit Do bodies through standalone Block chains at
root or a valid namespace body, with standalone Block hosts, existing authenticated
If/While/Block conditional ancestry, direct authentic While hosts or nested Do hosts.
The existing Do and While host ancestry remains admissible. Actual Do/While and
each parent Block, terminal occurrences and complete factory guards stay mandatory.
If main/elseif/else bodies now accept actual Do ancestry through these Block
chains. The [Do-hosted If review](../../coverage/semantics/anonymous-do-if-rtd-review.json)
records selected branches, reverse publication, retained Closure receivers and
fresh defaults, including a Do→If→While function host. Each actual If/ElseIf/Else
wrapper and complete factory guard remains required.
The [nested-Do review](../../coverage/semantics/anonymous-nested-do-rtd-review.json)
authenticates both actual Do hosts and body Blocks before publication or creation,
reverse class publication and old/current Closure saved-frame allocations.
The [While-hosted Do review](../../coverage/semantics/anonymous-while-do-rtd-review.json)
authenticates selected body-Block entries, callable publication, reverse class
publication and old/current Closure saved-frame allocations with fresh defaults.
The [If-hosted Do review](../../coverage/semantics/anonymous-conditional-do-rtd-review.json)
checks genuine If/CHOOSE selection before publication or creation, reverse class
publication and old/current saved-frame allocations, including While→If→Do hosts.
The [Do body-Block review](../../coverage/semantics/anonymous-do-block-rtd-review.json)
authenticates real body-Block entries before publication or creation/capture, reverse
class publication and old/current saved-frame allocations. The earlier
[direct-Do review](../../coverage/semantics/anonymous-do-rtd-review.json) retains
body-before-false-condition and LOOP_NEXT/CHOOSE stopping/repeat checks without replay.
Direct While hosts beneath Do, other intervening loop nodes,
nested functions or nested Closures, other targets,
captures and signatures remain Unsupported by this Do context.
The [block-Closure review](../../coverage/semantics/anonymous-block-closure-rtd-review.json)
separates real Block/creation/publication/allocation steps from pure admission queries.
Runtime publication appends a
source-bound PDRCLASS cause with the function or Closure/callsite, preserving the saved caller
frame. Reversed calls publish in call order, and a guarded repeat preserves one
publication while returning independent defaults. The
[named-factory review](../../coverage/semantics/anonymous-named-factory-rtd-review.json)
separates actual publication/allocation frontiers from pure admission/cause queries.
The [named-Closure review](../../coverage/semantics/anonymous-named-closure-rtd-review.json)
also checks anonymous allocation before Closure creation, genuine capture/call frames,
and second-call fatal redeclaration before another publication or allocation.
These earlier context reviews cover plain named bodies and parentless anonymous
forms without interfaces, attributes or constructor arguments; public untyped
property defaults use the literal/constant-concat parser, and public noarg by-value
nonmagic methods use existing body compilation. Later extensions are described
below. Plain global noarg/by-value/untyped named
functions and static no-capture Closures can contain these anonymous classes.
The compiler records only the authentic class checkpoint while inside the factory, then saves
the image after restoring the containing unit scope. This publishes the class
before any call and preserves compilation order independently of call order.
Ordinary function/Closure declarations do not consume the RTD counter. Wider
factory contexts and incomplete containing-scope images remain Unsupported;
wider include/eval contexts, inheritance, attributes, wider members/defaults
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
parameters/types, nonpublic constructors and broader lifecycle interactions remained
required at that cut. The [constructor review](../../coverage/semantics/anonymous-constructors-review.json)
separates original-source agreement, actual call/unwind states and pure receipt queries.

Anonymous classes accept finite sequences of direct positional/named `new`
arguments and unpromoted value or reference parameters, including a final variadic tail.
The ordinary signature compiler validates their types, defaults, requiredness and
final-only variadic placement; the ordinary binder
completes named holes before typed reception. A class without `__construct`
evaluates positional arguments and ignores their values. The compiled identity
precedes execution; a deferred class links and publishes at its first `new`
before argument expressions, then uses the ordinary method or no-constructor
send tasks. Without a variadic tail, an unknown named argument stops before the
next value expression; typed reception errors leave the `new` assignment
destination unchanged. The
[argument review](../../coverage/semantics/anonymous-constructor-arguments-review.json)
retains its seven native-backed sources, independent weak int-coercion source and
107 source-reached premises at the earlier two-parameter/send cut.
The [finite-arity review](../../coverage/semantics/anonymous-constructor-arity-review.json)
records root and successful include/eval sites, inherited constructors, surplus
positional sends, named-default reception retry and pruned versus eager invalid
defaults. Promoted or nonpublic constructors, unpacking and wider object lifetimes
remain partial.
Reference sends use the saved constructor signature and hold their actual cell
before later argument effects. Named sends select the formal index when they run;
rebinding a constructor local does not rebind the caller. Missing variables can
be initialized quietly, and omitted reference defaults get fresh callee locals.
Weak type reception may update a supplied caller cell; later body writes remain
ordinary unless that cell has a persistent property-reference source. VAR values
can warn and receive a temporary reference; an invalid TMP stops later sends and
the body. The [reference-constructor review](../../coverage/semantics/anonymous-constructor-reference-review.json)
records these source, cell, mode and reception checks.
Final variadic formals reuse the ordinary positional and named-tail collectors.
Positional extras keep integer keys; unknown named extras keep source order and
string keys. By-value tails copy received values, while reference tails retain
caller cells and may coerce them at reception. Fixed defaults finish before tail
collection, and an empty tail still receives an array. All sends precede typed
tail errors; invalid reference sends stop later sends. The
[variadic review](../../coverage/semantics/anonymous-constructor-variadic-review.json)
retains six agreements and the original excluded `count()` observer separately;
[CORE](CORE.md#environment-and-ordinary-library-boundary) defines that library boundary.
Argument TypeErrors, missing named fixed arguments and nonreferenceable-send
Errors format the whole callable name as one C string. Ordinary too-few-argument
errors format the lexical declaring class and member separately.
Stored class names and `::class` values keep their complete bytes.

Unit0 anonymous classes may now extend an ordinary named class through the
ordinary class-reference forms. Parent declarations follow the normal compiler/linker,
including its supported ancestor and member forms. The anonymous class keeps the
existing bounded member and argument grammar. Its compiler name starts with the resolved parent
reference spelling followed by `@anonymous`, NUL, file, line and RTD counter;
an early named parent consumes no counter key. The body and defaults compile
eagerly, but the first reached `new` links the parented class before allocation
and argument evaluation. An incompatible inherited property therefore fails at
that site, while an invalid own default fails compilation even in a skipped
branch. A successful link survives a throwing argument and later visits reuse
the compiled identity. An inherited constructor sees the parent's
property defaults; an override may call `parent::__construct`. Inherited methods
keep Base lexical scope and the anonymous called scope, and a private Base slot
remains distinct from a public child slot of the same name. Repeated factory
calls allocate distinct objects of one compiled anonymous class.
The [parent review](../../coverage/semantics/anonymous-parent-review.json)
retains its historical source comparisons, reached states and wrong-prefix
counterexample. The [typed-property review](../../coverage/semantics/anonymous-typed-properties-review.json)
records the corrected first-NEW publication phase and typed extension.
Wider inheritance remains partial or explicit Unsupported; later-unit dependency
sites retain the placement and argument limits described below.

Unit0 anonymous classes may implement a finite list of
interfaces, including inherited interface contracts, with or without the admitted
Base. The generated prefix uses the Base reference when present, otherwise the
first resolved interface reference, preserving its spelling. Ordinary interface
linking checks all direct kinds and duplicates before inheriting each interface's
members and calling its implementation handler. Method visibility, staticness and
signature checks use real source or internal prototype headers; later interfaces
cannot affect earlier failures or tentative-return notices. Both parentless and
Base-backed interface classes link at the first reached `new`, before arguments;
skipped sites leave their interface obligations unchecked. Bodies and defaults
still compile eagerly. A successful link survives an argument throw and later
visits reuse the published identity. Interface identity, type checks, inherited
constructors and typed slots use the shared machinery. Ordinary private helpers
also compose with existing parentless eval assignment sites. The
[interface review](../../coverage/semantics/anonymous-interfaces-review.json)
records these source and publication checks. Traits and wider member forms remain
partial or Unsupported; later-unit interface sites follow the bounded extension below.

Compiled anonymous identity is independent of dependency availability and source
order. Forward declarations can supply the Base and interfaces; a skipped site
may retain unresolved dependencies and a parent-typed uninitialized slot without
publishing or loading the class. Own defaults still validate eagerly. At a reached
`new`, ordinary declaration continuations load the parent then each interface
before kind/duplicate/member validation, allocation or arguments. A throwing loader
retains successful earlier loads; retry selects the same compiled descriptor and
publishes once before evaluating arguments. Ready dependencies keep the existing
direct linking path. Ordinary named declarations use their normal compiler metadata
in the shared counter walk, including implicit Stringable on an unused `__toString`
helper. This permits unrelated magic-method classes without broadening anonymous
bodies. The [dependency review](../../coverage/semantics/anonymous-dependencies-review.json)
records the native-first sources and reached compilation/autoload states.

Namespace and import contexts now use the same dependency route. Ordinary class
resolution handles plain, qualified, namespace-relative and fully qualified names,
including grouped imports and alias prefixes. Class references consult class
imports independently of function/constant imports and have no global fallback.
Each namespace block and factory keeps the imports visible at its source position;
repeated namespace names do not merge their import tables. Generated prefixes,
dependency links and declared property types keep resolved full byte names.
The [namespace dependency review](../../coverage/semantics/anonymous-namespace-dependencies-review.json)
records exact names/counters, ordinary named-header replay and autoload retry/cause
checks.

Successfully compiled include/eval units also admit dependent anonymous classes.
Each unit uses its own
namespace/import environment; eval does not inherit caller imports. Ordinary named
loader callbacks can load dependencies through nested units. First-NEW staging,
retained loads after a throw, same-site retry and publication before construction
use the existing declaration continuations with the actual unit/class-child cause.
The compiler replays the live parent bindings captured at that unit's entry, so a
later named subclass of an already-live Base can bind early without consuming an
RTD key. Later loads cannot change that frozen entry view. Local class cost is
added once to the request seed, independently of runtime visits.
The [dynamic dependency review](../../coverage/semantics/anonymous-dynamic-dependencies-review.json)
records these source, entry-view and history checks. Closed successful compilation
history and absence of pre-name diagnostics remain required.

The placement extension reuses the same compiler route for later-unit expressions,
including returns, nested and call-argument NEW, and the existing ordinary named
and static no-capture Closure factories. Finite direct positional/named
constructor arguments use the ordinary binder; wider bodies, factories, captures
and argument modes retain their documented bounds. Factory compilation records class identities before calls;
first-NEW linking precedes argument effects, and successful publication survives a
throwing send. Later visits allocate fresh objects of that same class. Ordinary
named declarations inside admitted factories consume their deferred keys in actual
compiler order, even when an outside allocation executes first. Site admission is
structural; the compiler image decides whether an AST site consumed a key. Constant
skipped `&&`/`||` RHS classes have no descriptor, while a `??` default and a
variable-guarded unvisited class compile and consume keys. A skipped bad default
therefore differs from an eager bad default in an unused factory body.
Root try continuations in a running dynamic unit restore only its actual entered
caller, with the active eval/include binding, owner depth and end-marker suffix.
Callable-local and same-unit continuation guards remain intact.
The [placement review](../../coverage/semantics/anonymous-dynamic-placements-review.json)
keeps source comparisons and source-reached image/cause checks separate.
Ordinary traits and enums can share the same successful units with anonymous
sites. Named header replay authenticates their actual kind, flags and implicit
interfaces through the existing compilers. The usual source position, trait uses,
prefix declarations and frozen entry bindings determine early eligibility; an
already-live trait spelling cannot acquire a fresh early binding in a later unit.
Class-key costs come from compiler-visited descriptors. Pruned declarations
contribute none, while compiled unvisited declarations retain their normal cost. Include-once hits do not compile again; a fresh include contributes
its own compiled descriptors. Trait imports, enum-case caches, anonymous linking
and argument-throw retry keep their ordinary source and publication authority.
The [mixed-kind review](../../coverage/semantics/anonymous-trait-enum-review.json)
records these shared contexts without widening anonymous bodies or factories.
Rejected parsing reserves a source identity and retains its actual failed-source
record without installing an accepted source, code image or binding. An exact entered
unit followed immediately by its rejected exit contributes zero class keys. This
covers ParseError and parser-stage CompileError; textual class/NEW prefixes in a
rejected source publish nothing. Later accepted units retain their real source
IDs and use the unchanged class-key seed. Opened include-once/require-once files
remain marked after parser rejection, so a later once hit does not parse or
advance the compilation sequence again. Existing parser services, filenames,
source-site validation and constructor/publication rules remain authoritative.
The [rejected-source review](../../coverage/semantics/anonymous-rejected-sources-review.json)
records recovery without treating an unmatched history segment as zero cost.
Body/default compilation fatals remain terminal. Accepted partial, open or
reentered compilers and broader factory/capture/constructor-argument modes remain
Unsupported.

Plain anonymous and Base property types use the ordinary normalizer, invariant
link checks and typed storage. An absent typed default starts uninitialized,
including nullable declarations; nullable reference fetch can initialize null.
A compatible public redeclaration selects the child's physical declaration and
default, while a private Base slot stays separate from a child shadow of another
type. Live property-reference sources constrain the shared cell until their
individual slots are unset. Diagnostic names use the prefix before NUL and
preserve source `self`/`parent` spelling; logical class names, types and source
origins retain their full identities. Shared admission also covers plain typed
parentless eval sites under the existing dynamic-unit guards. Hooks, readonly,
asymmetric/static properties and wider defaults retain their existing boundaries.

Raw `getTrace()['class']` retains the entire generated name. The shared trace
renderer applies `c_string` only to the displayed CLASS bytes, matching Zend's
`TRACE_APPEND_KEY`; `getTraceAsString()` therefore prints the prefix before NUL:
`class@anonymous` without dependencies, or the resolved parent/first-interface
reference followed by `@anonymous` for the admitted dependent classes.
Stored names and trace arrays remain intact. The
[anonymous class review](../../coverage/semantics/anonymous-classes-review.json)
keeps five exact originals and publication/allocation, factory and trace frontiers
at their distinct cuts. Pure formatter/domain/display and compiler-context queries
are separated from reached states; earlier failures retain zero credit.

## Generated enum method strings

For published enums, computed, literal and compiler-folded `Class::method`
strings select generated `cases()`, `from()` and `tryFrom()` before evaluating
arguments. Lookup uses the published class and generated method identity, while
the selected-call record preserves the full original string, method bytes,
source occurrence, line and nonce. Later callee rebinding cannot change this
selected enum. These internal operations reuse ordinary argument sends and enum
reception without constructing a user method body or an owning receiver.

Named Stringable inputs retain their real argument child and call line through
`__toString()` and release a temporary input before backing-table lookup. A
selected call requires the same source child at callback entry; wider packed
origins produce explicit Unsupported before conversion. Caller strictness,
backing checks, singleton caches and ordinary internal argument errors keep
their existing rules.

First-class captures authenticate the actual placeholder, init/conversion line
and full fixed or computed string before creating the existing internal Closure.
The Closure stores the selected generated operation; it owns no receiver, creator
or original callee string. Invocation owns the Closure through reception and
lookup even if an argument or Stringable callback clears its source variable.
The temporary Stringable input still retires before lookup, and the Closure
retires after the call when no outside owner remains.

The engine routes are `zend_init_dynamic_call_string` and `ZEND_INIT_DYNAMIC_CALL`,
the compiler's fixed-call lowering, and the generated handlers registered in
`Zend/zend_enum.c`. For captures, `ZEND_CALLABLE_CONVERT` calls
`zend_closure_from_frame` in `Zend/zend_closures.c`. The [string review](../../coverage/semantics/enum-string-callable-review.json)
keeps original source comparisons, reached guards and the shared identity-receipt
normalization at separate cuts. The
[capture review](../../coverage/semantics/enum-string-capture-review.json) keeps
its new capture sources and owner/ingress checks separate. Callable admission,
first-class array captures, pipe and `Closure::fromCallable` consumers, first-use loading, enum
collectability and wider object lifetimes remain partial.
