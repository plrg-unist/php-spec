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
Ordinary function/Closure declarations do not consume the RTD counter. Named-class
method factories are described below. Other factory contexts and incomplete
containing-scope images remain Unsupported;
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
arguments, including array unpack, and ordinary value or reference parameters
with an optional final variadic tail.
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
defaults. Promoted or nonpublic constructors, Traversable unpacking and wider
object lifetimes remain partial.
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
Array unpack uses the ordinary CV/VAR/value source classifier. Reference demand
separates shared writable arrays, keeps embedded aliases and promotes direct
slots only in the live table. Direct elements of value inputs use fresh cells
when passed to by-reference formals; existing embedded aliases remain shared.
Expanded integer positions and string names feed the same binder, including
named holes filled before typing. Static order errors and dynamic name/duplicate
errors keep their argument-effect priority. Constructorless classes retain the
ordinary dummy send frame: positional values are ignored, while a named key stops
later sends. The [array-unpack review](../../coverage/semantics/anonymous-constructor-unpack-review.json)
records these source, table, cell and default checks. Existing array/reference and
source-history limits remain; constructor Traversable producers are still separate.
Argument TypeErrors, missing named fixed arguments and nonreferenceable-send
Errors format the whole callable name as one C string. Ordinary too-few-argument
errors format the lexical declaring class and member separately.
Stored class names and `::class` values keep their complete bytes.
Public zero-argument anonymous `__destruct` methods with no return annotation or
reference return now use the ordinary method compiler and destructor lifecycle.
Last-owner release and reverse global cleanup retain real receivers and callers;
successful eval classes use their installed unit descriptors. Failed constructors
suppress later automatic destruction even when `$this` escapes, while explicit
calls remain ordinary methods. A destructor throwing during unwind chains the
saved exception as Previous. The [destructor review](../../coverage/semantics/anonymous-destructors-review.json)
records five agreements and 240 conditions (228 reached, 12 derived across six controls).
Public zero-argument anonymous `__toString` methods share ordinary signature
checking, implicit `Stringable` and string-conversion callbacks. The implicit
interface defers publication without changing the raw-header name prefix or
one counter step per anonymous site; named Stringable classes keep their own
ordinary counter cost. Selected receivers survive rebinding until cleanup before
emission, and successful eval factories retain the same unit-specific identity.
Ordinary return errors format lexical class and original member separately;
never-return errors format one callable C string and identify ordinary methods.
Invalid return annotations preserve the source method spelling.
The [Stringable review](../../coverage/semantics/anonymous-stringable-review.json)
records nine agreements and 285 conditions (278 reached, seven controls).
Ordinary anonymous instance methods now accept unpromoted value, reference,
default and variadic parameters under the existing visibility and return fences.
The method compiler and call binder retain their ordinary signature, named-hole,
send and typed-reception rules. Missing-arity errors compose the declaring lexical
class and member separately, including inherited named methods. Five fresh
originals agree with the pinned PHP engine; two source-reached state groups pass
247 conditions (243 reached, four guards), including private caller aliases,
literal reference failure, and fresh local defaults for by-reference formals in
an eval unit. The [method-parameter review](../../coverage/semantics/anonymous-method-parameters-review.json)
records the private cuts and retained unchanged refusals.
Public/default-public nongenerator anonymous `__invoke` with unpromoted formals
uses the ordinary method descriptor and existing implicit object-call selection.
Five fresh originals agree, including explicit calls, parent dispatch, eval
factories, named defaults and a selected receiver retained through argument
rebinding and frame-release destruction. Two state groups pass 275 conditions
(272 reached, three controls). The [invoke review](../../coverage/semantics/anonymous-invoke-review.json)
keeps the unchanged admission refusals and two zero-credit fixture corrections.
Public/default-public zero-argument nongenerator anonymous `__clone` now uses
the existing clone copy, callback and cleanup routes. Declared arrays separate
on callback writes while embedded references stay shared; parent callbacks
can release a rebound source before the fresh copy is observed. Failed clone
callbacks may leave an escaped copy eligible for normal automatic destruction.
Keyword clone ignores a callback's value return, while an explicit call observes
it. Six normal originals and one invalid-return rejection agree, including a
`never` fallthrough TypeError at the method end line. Two state groups pass
210 conditions (207 reached, three controls). The [clone review](../../coverage/semantics/anonymous-clone-review.json)
keeps the two unchanged admission refusals and one zero-credit fixture correction.
Ordinary nongenerator anonymous static methods now admit public, protected and
private unpromoted formals through the existing receiverless call path. Six
native-first originals check access before sends, typed reference updates,
shared static locals, inherited lexical scope, captured calls after rebinding,
and segmented missing-arity and ordinary return names, plus the `never` method
kind. Two source-reached state groups pass 220 conditions (215 reached, five
controls). The
[static-method review](../../coverage/semantics/anonymous-static-method-review.json)
records the distinct validation cuts and both zero-credit failures; ordinary
captured `CLOSURE_TARGET` diagnostics follow below.
Ordinary first-class captures of static and instance class methods now format
missing-arity and ordinary return diagnostics with the declaring class and
member, including explicit `->__invoke`. Typed input and `never` retain the
whole-name C-string view; `never` identifies a method. Four native-first
sources, private strict433 and two source-reached state groups pass 295
conditions (291 reached, four controls). Copied trait `self` views are handled
below; other copied views, rebound scopes and real Closure/API/wrapper views
remain separate. The
[captured-method review](../../coverage/semantics/anonymous-captured-method-diagnostics-review.json)
retains two normal pre-fix mismatch observations and the distinct zero-credit
preflight, strict-placement, comparator and fixture corrections.
Trait-constant first-class static captures with a saved `self` parameter view
now report `never` fallthrough as a method when the base and copied function
views differ. The saved type rejects an importing-class instance where a direct
method call accepts it; an old clone and later using-class capture retain
distinct lexical names. Three exact native/source agreements, private strict433
and two source-reached state groups pass 130 conditions (126 reached, four
guards). The [trait-capture review](../../coverage/semantics/trait-captured-method-kind-review.json)
keeps two pre-fix normal mismatches and exact capture-time deprecations.
Alias/failure receipts, anonymous using-class names, rebound scopes and other
Closure/API/wrapper views remain separate.

For existing copied trait first-class captures, a `parent` parameter is checked
against the saved lexical scope. An old cloned capture can retain a trait scope
without a parent: a reached object argument then fails before the body if its
union reaches `parent`; an earlier matching class branch succeeds. A later
capture can retain the first using class as lexical scope while the called
class differs, so its `parent` type follows the first class's parent. Null
bypasses the unresolved class lookup in `?parent`. Four exact source originals
and three source-reached state groups (79, 86 and 93 conditions) validate these
existing rules without a semantic edit. The
[parent-view review](../../coverage/semantics/trait-captured-parent-view-review.json)
records the native/model cuts and the two corrected fixture failures. Trait
alias/failure receipts, anonymous using-class names, rebound and wider callable
views remain partial. The engine routes are `zend_check_type_slow` and
`zend_fetch_ce_from_type` in `Zend/zend_execute.c`, then `zend_fetch_class`
using `zend_get_executed_scope` in `Zend/zend_execute_API.c`.

A copied alias captured during a failed first class link keeps its selected
method and lexical scope when a later class reads the constant. If property
binding fails before trait method fixup, the retained alias has trait scope:
the reached `parent` parameter fails and its stack frame names `U::q`. If the
link fails after fixup on an abstract requirement, the retained alias has the
failed class scope: `parent` accepts that class's parent, and a later wrong
argument produces `C::q`. The copied method is absent from the published
method table in both cases. Its authenticated receipt supplies the bare `q`
function name, while the saved closure scope supplies `U` or `C`. Four exact
native/model originals and two source-reached trace groups (39 conditions
each) cover this boundary. [Alias trace review](../../coverage/semantics/trait-captured-alias-parent-trace-review.json).
The engine routes are `zend_fixup_trait_method` in `Zend/zend_inheritance.c`
and `zend_fetch_debug_backtrace` in `Zend/zend_builtin_functions.c`.
Anonymous using-class names, rebound scopes, and wider callable views remain
partial. Three native tick-wrapper probes print the retained `U::q` frame,
but the model stops before callback entry at explicit tick placement or eval
class-constant admission; they have zero agreement credit.

Nonpublic/reference-return/attributed magic methods and remaining magic dispatch
stay open, alongside constructor Traversable producers,
promotion/nonpublic forms and wider factories/lifetimes.

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

Unit0 anonymous classes admit finite trait-name lists, multiple use statements
and ordinary alias/precedence adaptations within the existing member grammar,
with or without a parent and explicit interfaces. The source gate validates
names, nonempty uses, qualified precedence targets and exclusions, and the
single allowed alias modifier (public/protected/private/final). The ordinary
trait compiler and linker own name resolution, deduplication, ambiguity,
precedence, excluded-method aliases, visibility, signatures and interface
requirements. `insteadof` does not resolve an unqualified alias ambiguity.

Every trait-using anonymous descriptor remains deferred. The first reached
`new` composes and publishes it before allocation or constructor arguments;
skipped conflicts remain inert, and failed links leave the class unpublished.
Link warnings keep the class-site source until the original `new` resumes;
private-final alias E_COMPILE_WARNING (128) bypasses user handlers and precedes allocation.
The live descriptor must retain the compiler-derived own-member projection and
full declaration replay. Duplicate forged imported methods fail that replay.
Copied trait constants and first-class method captures keep distinct source and
import identities, the full generated NUL class name, saved lexical/called scope
and the using class's parent type at receive. A parentless `parent` parameter
raises Error before the body. Distinct imported method names have independent
static-variable cells; duplicate or case-only aliases share the selected name.

Trait collision, unimported-trait selection and method visibility/static
conflict diagnostics truncate class-name arguments as the engine's `%s` sites
do, retaining suffixes and physical source lines; stored identities stay complete.
[Adaptation review](../../coverage/semantics/anonymous-trait-adaptations-review.json)
records native/model sources, reached-state guards and original failures.
Earlier bounded cuts remain in the [trait-capture](../../coverage/semantics/anonymous-trait-capture-review.json),
[parentless](../../coverage/semantics/anonymous-parentless-trait-capture-review.json)
and [alias-capture](../../coverage/semantics/anonymous-trait-alias-capture-review.json)
reviews.

Imported `__toString` and ordinary methods aliased to it also retain inferred
Stringable interfaces in admitted anonymous classes. Before stripping imported
members, the live interface list must equal the shared trait importer's derived
list. Only the own-member comparison restores the raw interface field; full
declaration replay remains mandatory. Inference does not change the compiler's
generated name prefix or RTD key. Explicit mixed-case Stringable keeps its source
spelling and gains no duplicate; a Base and an explicit interface retain their
normal prefix and link targets.

The ordinary parentless trait capture view permits authenticated nonempty live
interfaces after publication, with matching linked targets and full declaration
history. It retains the no-parent receive fatal before the body. The former
empty-interface path and saved-snapshot branches are unchanged. Return,
visibility and static Stringable contract conflicts retain the physical trait
method line and short class display, without publication or allocation.
[Stringable trait review](../../coverage/semantics/anonymous-trait-stringable-review.json)
records its original main-unit sources and reached guards.

Successfully compiled include/eval units use the same own-member and derived
interface projection. Their completed source-unit receipt, exact NEW occurrence,
frozen compilation-entry view, history seed and compiler-derived counter remain
mandatory. The composed view additionally requires the published name, runtime
publication receipt and full declaration replay; duplicate imported methods or
interfaces cannot gain authority by surviving the own-member projection.
Skipped conflicts keep their compiler key without linking; reached interface
conflicts precede constructor argument effects. Repeated allocation uses one
compiled class, while recompilation creates a fresh name. A copied trait
constant's retained callable target still follows its first selected binding,
even across distinct eval-created class identities.

Ordinary cached-method history and scope checks finish before the extra trait
view requests full replay. This breaks the dynamic compiler/cache validation
cycle without changing source-entry authority or weakening the parameter view's
interface checks. Resolved expected argument types and object trace names use
the engine's C-string display boundary; stored names and type atoms remain full.
[Dynamic trait review](../../coverage/semantics/dynamic-anonymous-traits-review.json)
records native originals, source-entry/counter/capture checks and preserved
failures. Wider dynamic source, explicit-interface/unpublished/collision scope
histories and other member/type/lifetime contexts remain partial.

Engine routes: `Zend/zend_compile.c::zend_compile_use_trait`,
`zend_compile_trait_alias`, `zend_compile_trait_precedence`;
`Zend/zend_inheritance.c::zend_traits_init_trait_structures`,
`zend_traits_copy_functions`, `zend_add_trait_method`,
`do_inherit_method`; and `Zend/zend_execute.c::zend_verify_recv_arg_type`.

Own anonymous class constants reuse the ordinary class-constant compiler for
types, values, declaration lines and public/protected/private/final modifiers.
Nonempty groups may contain multiple declarators. Types and initializers follow
the ordinary compiler's admission. Private-final and wrong typed values
fail during compilation before body effects. Parent-final and incompatible trait
constants fail at first-new linking before constructor argument effects; matching
trait/own definitions compose normally.

Own callable constants retain their class's method and source identity. Separate
eval compilations therefore accept their respective self types and reject a
cross-class argument. Full class/constant names remain in descriptors and the
successful value path. Initializer, access, final-override and trait-conflict
diagnostics truncate only class-name operands as the engine's C-string calls do.
The [own constant review](../../coverage/semantics/anonymous-own-constants-review.json)
records exact originals, table/source forgery refusals, actual own-FCC receives
and compile-versus-link ordering. Attribute-bearing constants and wider
member/type/initializer contexts remain partial.

Attribute-free, hook-free anonymous property groups now share the ordinary
property compiler, including multiple declarators, types and nonliteral defaults.
Modifier admission shares the ordinary finite predicate for read/set visibility,
static, readonly and final combinations; compiler-invalid forms retain the shared
error order. No-argument constructorless allocation first runs pending instance/static
default work through the existing source-authenticated constructor marker. When
both default task lists are empty, allocation follows the original direct path.

Private parent and child slots retain separate full-name keys. Instance arrays
separate on clone writes; repeated visits to one class share static cells, while
fresh eval compilations receive distinct cells and source identities. Visibility,
static/instance inheritance and readonly checks use the existing runtime rules.
The exercised diagnostic class-name operands truncate at NUL without changing
stored names, keys or successful lookup identities. The
[property review](../../coverage/semantics/anonymous-properties-review.json)
records actual default-work/allocation fronts, private-key reads, static sharing
and compile/link order.

Equivalent read/set visibility normalizes to the ordinary setter, while genuine
private(set) is implicitly final. Parent-final conflicts precede private-slot
independence; setter narrowing is checked before read visibility/type inheritance.
Final properties remain writable. Explicit public(set) readonly permits its first
global initialization, then ordinary readonly checks reject another write.
Setter authorization remains lexical; diagnostic caller display uses called scope.
The [modifier review](../../coverage/semantics/anonymous-property-modifiers-review.json)
checks stored flags/cells, actual permitted and denied stores, scope/descriptor
forgeries and compile/link boundaries. Attributes, hooks and wider
member/type/default/lifetime combinations remain partial.

Anonymous constructors also admit attribute-free, hook-free
promoted formals using the shared nonstatic property modifier predicate. The
ordinary signature compiler retains parameter types/defaults and rejects promotion
outside constructors; the method compiler owns promoted declarations, duplicate,
variadic and property-type checks. Each declaration keeps the actual NParam origin
and full private key. Parameter defaults remain parameter defaults, while the
promoted property starts in its ordinary uninitialized/null state.

Source-authenticated PROMOTE_PARAMETER tasks run after reception and before the
body. Value stores separate later local writes and array COW; reference stores
attach the declared property constraint to the sent cell. Readonly reference
acquisition fails before the body. Separate eval compilations keep distinct
promoted declarations and self scopes. The pinned engine accepts final/private
promotion because that route bypasses ordinary property-group validation; the
ordinary declaration error remains in place. Only the exercised duplicate,
forbidden-property-type and complete optional-warning callable display operands
truncate at NUL. The [promotion review](../../coverage/semantics/anonymous-promotion-review.json)
retains source/prologue/reference and compile/link evidence. Attributes, hooks
and wider signature/default/lifetime contexts remain partial.

Readonly anonymous headers use the same finite ordinary member grammar. The
header's readonly bit reaches declared and promoted properties, parent/trait
checks and both compiler-counter receipt routes. Readonly headers require one
in-range `classKeywordLine` fact from the actual class token; the frontend skips
attribute token ranges before scanning. Missing, duplicate and out-of-range
facts are refused. Ordinary headers retain their prior line behavior. Stored
class names, private keys and source origins remain complete.

Initialization and later writes use the existing readonly runtime. Clone callbacks
may reinitialize each copied field once; a second or manual callback write fails.
Explicit public(set) permits first global initialization, while reference promotion
fails before the body without attaching a property type source or changing the
donor. Compatible readonly parents, imported readonly trait fields/Stringable and
separate eval/self scopes retain their ordinary identities. Incompatible parents
and trait fields fail before constructor arguments/allocation; untyped fields,
declared defaults and static fields fail during compilation. Only the exercised
readonly trait/dynamic-property diagnostic class operands are clipped at NUL.
The [readonly review](../../coverage/semantics/anonymous-readonly-review.json)
records the scoped source, metadata and reached-state checks. Attributes, hooks
and wider member/type/lifetime combinations remain partial.

Concrete ordinary anonymous methods and constructors now share the finite named
method modifier predicate. Final instance/static methods retain their dispatch,
source flags and cloned callable scopes. Private-final ordinary methods emit the
native warnings before main execution, while private-final constructors do not.
Final constructors keep ordinary promotion without making the promoted field final.
Protected/private constructor access precedes argument effects, reception and body
execution; failed automatic construction marks the object ineligible for automatic
destruction. A bound static Closure in related parent lexical scope can construct
the protected child through the existing factory grammar.

Static constructors reach the shared signature, parameter validation and body
compiler before the magic-method rejection, preserving default/body error priority.
Inherited-final conflicts still occur before constructor arguments/allocation.
Duplicate/static diagnostic class operands truncate at NUL; stored names and scope
authority stay complete. The [method modifier review](../../coverage/semantics/anonymous-method-modifiers-review.json)
retains the exact sources and reached fronts. At that historical cut, anonymous
abstract methods, wider method-body factories, attributes and byref/magic/generator
forms retained explicit boundaries. The historical177 boundary originals
retain zero credit there; the named-owner witness has a separate fresh178 agreement.

Ordinary nonmagic methods and nongenerator byvalue constructors in admitted named
source classes compile anonymous child factories. Unit0 anonymous classes and traits
share these contexts, including method-owned Closures and arrows nested through
admitted deferred bodies. Nonmagic methods and deferred Closure/arrow declarations
may return by reference when nongenerator; byvalue generator bodies are also
admitted. Method-owned deferred contexts, anonymous owners and traits retain their
unit0 restriction; the existing direct named-method dynamic-unit policy is unchanged.

The concrete method GOTOROOT must belong to its parsed owner. Source-derived
namespace/imports, complete current/folded class contexts, lexical function name
and every body prefix must agree. Folded `__METHOD__` preserves the full nested
Closure name. A Closure/arrow's own compiler `RETURNREF` equals
its checked header flag. Authentication of its containing method restores that
method's independently checked flag only in a temporary compiler-context query.
Thus a reference Closure may occur in a byvalue or reference method without
confusing their return modes. Actual captures, receivers and return cells use the
ordinary runtime protocols.

Byvalue nongenerator `__invoke`, `__get`, `__toString`, `__set`, `__isset`,
`__unset`, `__call` and `__callStatic` factory bodies share this method ancestry,
including admitted nested deferred factories. Getter headers
retain untyped required byvalue nonvariadic parameters without defaults and no
declared return type; successful reception has one parameter. Wider getter
headers remain a source boundary. Existing callable, property-get and Stringable
consumers supply the actual receiver/frame; no conversion or dispatch rule is
widened. A getter frame borrows its receiver from the saved property-result task,
so clearing the caller's receiver variable does not destroy it during child `new`.

Property magic factories retain the existing consumer contracts: public ordinary
methods in parentless nonreadonly declaring classes (including anonymous owners), inherited
receivers, external CV receivers with literal private-property names and supported
plain signatures.
Setter/unsetter names are required `string` parameters with `void` returns; setters
also take an untyped value. Terminal isset retains its existing string-name and
bool/absent-return routes. Setter RHSs remain initially nonreference integer CVs
or integer literals. Its captured argument remains fixed while a nonowning delivery
reads the original RHS cell after receiver destruction. A created child may outlive
that receiver through its ordinary global/caller owner. Trait declarations, wider
receivers/RHSs and signatures remain partial under the existing
[property consumers](SOURCE-PROPERTIES.md).

Argument-magic factory bodies retain plain `__call(string,array)` and static
`__callStatic(string,array)` headers without a return declaration. Direct
positional originals admit zero sends or the existing one/two-send family:
integer literals, an initialized nonreference integer/ordinary-object first CV,
nullary named producers and no-ctor named `new`, with supported int/leaf-instance
values. Objects require actual `node_children(...)=eps`; primitive fields are
admitted. Instance sends admit a positional or explicitly named first object CV,
including a positional object before a named later argument. First array CVs
may contain only direct integers/ordinary leaf objects; generic COW separates
later caller writes while preserving the captured container and shared object
handles. The first original argument may instead be a flat array literal;
items must be nonreference/nonspread, while keys and value expressions retain
existing generic literal evaluation. Actual captured values require direct
integers/ordinary leaf objects. Contextual collection checks the first CV/literal
source role, preserving CV snapshots after caller rebinding/reference promotion
and temporary literal owners through later sends. A later
argument may change the caller's CV and receiver binding while the earlier send
stays fixed. The trampoline then supplies the real name/array pair. With no sends,
Zend supplies `ZVAL_EMPTY_ARRAY`; the model represents that empty value by an
immutable abstract array node, with no first-argument read or payload edge.
The ordinary ownership graph retains that node; the collector excludes it until
a write separates a mutable copy.

The parameter CV owns that array; its historical target metadata adds no payload
owner. Instance magic retains its actual receiver and lexical/called classes;
static magic invents no receiver. A returned child may retain a payload or the
actual array after magic-local/receiver cleanup. These source/ownership extensions
reuse the existing [magic-call consumers](SOURCE-METHODS.md). Named-only calls
share the parameter table with the actual retained named buffer: releasing the
parameter and child copies leaves that buffer as the last table/payload owner
until return cleanup, before receiver release. Array-returning producers, later
array sends, unpacking, nested/reference carriers, string/reference CVs and wider
object/source/header layouts remain visible
unfinished core boundaries rather than new dispatch rules.

Named owners receive deferred keys after their children compile; an anonymous
owner reserves its key before compiling members and replaces that compiler-local
descriptor in place on success. Recursive children therefore retain source order
through reversed or repeated calls, which reuse templates but allocate fresh
instances. The provisional owner retains its raw parent/interface prefix and early
marker. Ordinary interface, trait and constant siblings use existing composition
rules, including implicit Stringable from a public class-free `__toString` sibling.
The linked Stringable view does not overwrite the raw header or generated name.
Trait composition precedes interface validation and constructor arguments;
constant and child compilation retain member order.

A source trait's actual body field and header establish its `PTTRAIT` context.
Consumers, aliases and inherited calls share one child template per source
occurrence. Ordinary trait copying supplies the importing lexical class, while
late-static access follows the actual called class. Inherited calls retain their
declaring importer for private/self/parent access. Compiled `__METHOD__` and
`__FUNCTION__` values and nested Closure names retain definition identity;
invocation aliases still use the ordinary renamed method descriptors.

The Generator owns its suspended frame, and resumption installs that frame's real
source, locals and call context. Child `new` uses the saved method or Closure's
receiver and lexical/called classes after yields, injected throws or creator-CV
cleanup. Method-Generator completion releases its execution receiver. A closed
Closure-Generator instead retains its actual Closure after the frame retires;
that Closure continues to own its receiver/captured cells until release. Static
Closures without captures preserve source identity after their creator retires.
Native API resumptions mark the body trace internal and retain the API call's
source location; user/`foreach` resumptions retain their source location.

Reference returns transfer real cells, preserving caller aliases and copies
independently of the method/Closure receiver. Temporary returns emit the ordinary
notice and remain owned through callbacks. A throwing handler still completes
return-value handling before callable cleanup, preserving distinct used/unused
receiver/child retirement order. An Arrow's implicit expression return is
source-authenticated through its actual current callee, checked Arrow template and
compiled body line. Nongenerator reference Arrows may unwind at that boundary;
finalized statement returns keep their existing body-scope authority. An Arrow
expression return is never classified as ordinary implicit-null fallthrough.

Compilation still rejects errors in uncalled bodies. Child errors precede rejected
static/return-typed constructors, and earlier private-final warnings remain visible.
On abrupt unit compilation, diagnostic replay skips only authenticated child
checkpoints whose owner/child images were never installed, including named/Trait
methods authenticated through their actual owner body field. This preserves child
warnings before a later magic signature fatal. Plain getter wrong-arity errors
are diagnosed after the body; wider getter signatures retain explicit Unsupported.
Valid compilation keeps its EARLY activation checkpoints. Normal and installed histories retain their usual handling. Lazy child-link failures precede
argument effects and preserve the actual call/resumption trace. Protected access,
promotion, failed constructors, imported names and readonly rules remain ordinary.

Reference/generator constructors, reference generators, attributed factories,
reference/generator forms of the admitted magic methods, other magic bodies,
named nested functions and wider binding/dynamic deferred contexts remain partial. Constant
and default positions retain their separate source fences.

The [method](../../coverage/semantics/anonymous-method-factories-review.json),
[constructor](../../coverage/semantics/anonymous-constructor-factories-review.json),
[anonymous owner](../../coverage/semantics/anonymous-owner-factories-review.json),
[Stringable sibling](../../coverage/semantics/anonymous-owner-stringable-review.json),
[method Closure](../../coverage/semantics/anonymous-method-closure-factories-review.json)
and [mixed-owner](../../coverage/semantics/anonymous-owner-declarations-review.json)
ledgers preserve their historical scopes and source/state evidence. The
[Trait](../../coverage/semantics/trait-source-factories-review.json),
[generator method](../../coverage/semantics/generator-method-factories-review.json),
[generator Closure](../../coverage/semantics/anonymous-generator-closure-factories-review.json),
[reference method](../../coverage/semantics/anonymous-reference-method-factories-review.json)
[reference Closure](../../coverage/semantics/anonymous-reference-closure-factories-review.json)
[magic method](../../coverage/semantics/anonymous-magic-factories-review.json)
[property magic](../../coverage/semantics/anonymous-property-magic-factories-review.json)
[argument magic](../../coverage/semantics/anonymous-magic-argument-factories-review.json)
[zero-send magic](../../coverage/semantics/anonymous-zero-argument-magic-review.json)
[object-CV magic](../../coverage/semantics/anonymous-object-cv-magic-review.json)
[named object-CV magic](../../coverage/semantics/anonymous-named-object-cv-magic-review.json)
[array-CV magic](../../coverage/semantics/anonymous-array-cv-magic-review.json)
and [array-literal magic](../../coverage/semantics/anonymous-array-literal-magic-review.json)
reviews distinguish exact originals, genuine reached ownership/resumption,
explicitly derived context refusals and native-only preparations.

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
pipe and `Closure::fromCallable` have separate reviewed cuts below; first-use
loading and wider object lifetimes remain partial.

## Generated enum array captures

Published enum class names and enum-case receivers in callable arrays can create
first-class internal Closures for generated `cases()`, `from()` and `tryFrom()`.
The engine selects them through `zend_init_dynamic_call_array`, followed by
`ZEND_CALLABLE_CONVERT` and `zend_closure_from_frame`.
Creation authenticates the actual live array, its selected class/method pair and
the first-class source/init/conversion line before allocation. The internal
Closure retains no array, receiver or creator. Existing call owners preserve it
through argument-side clearing, Stringable conversion and lazy lookup.

A runtime source array can retire when its last real owner disappears; literal
arrays may remain rooted by compiled constants. Fetching an enum-case receiver
warms its backed table before capture, while a class-name receiver can keep that
table cold until invocation. The
[array-capture review](../../coverage/semantics/enum-array-capture-review.json)
keeps these cases and source/owner checks separate. Other callable consumers,
loading and wider backing contexts remain partial. GC08 covers cached enum-case
GC candidate exclusion; original receiverless Closures use the shared GC09 birth
policy. Wider GC interactions remain partial.

## Callable-typed generated enum strings

Ordinary callable-typed parameters admit published generated enum method strings
as their original values. Reception creates no Closure or selected-call record;
arguments finish before the receiving frame checks callable validity. That
frame's scope controls ordinary private method strings and arrays, while a
Closure captured inside the class retains its selected private target. Existing
array and Closure identities are unchanged. The [admission review](../../coverage/semantics/enum-string-admission-review.json)
records source, state and receiving-scope checks at its private cut.

## Generated enum conversion with Closure::fromCallable

`Closure::fromCallable` converts published generated enum strings and arrays,
including through a captured factory. The actual API call and received value
authenticate conversion; the existing internal Closure allocator stores the
selected operation without a source array, case receiver or factory owner.
Existing Closure and `__invoke` array identity forms allocate nothing. Calls
retain the new Closure through argument clearing and Stringable conversion,
then can retire it after invocation. The pinned engine routes are
`zend_create_closure_from_callable`, `zend_is_callable_ex` and
`zend_create_fake_closure`. The [conversion review](../../coverage/semantics/enum-from-callable-review.json)
records distinct source and state checks at its private cut. `is_callable`,
wider reception, loading and backing contexts remain partial. The
[current-tail gate](../../coverage/semantics/enum-callable-current-tail-review.json)
joins reception and conversion in one original program.

## Generated enum pipe calls

An evaluated method string, class-name array or enum-case array can select a
published generated `cases()`, `from()` or `tryFrom()` target for `|>`. The pipe
fixes that target before sending its forced left value. The saved invoke has
one positional value and a source-bound selected nonce; the right callable
retires without becoming an owner of the selected enum. A Stringable left
argument uses the pipe's left source child, so its callback can rebind the
original callable while lookup still uses the selected enum and cold backing
table. Strict scalar errors, case-object selection and `cases()` arity follow
the same reception rules as direct generated calls. The
[pipe review](../../coverage/semantics/enum-pipe-review.json) records four exact
native-first originals and two source-reached strict SL guard groups. Wider
callable APIs and default loading remain partial.

## Published enum is_callable queries

For already published enums, `is_callable` checks generated method strings,
class-name arrays and live enum-case arrays without invoking the target.
One- and two-argument direct, selected dynamic-name and pipe calls use the
ordinary CONFIG argument path. Runtime queries consult the existing callable
admission rules; syntax-only queries accept valid string/array shapes even when
the enum has no such method. A query does not initialize the backing cache.
The [query review](../../coverage/semantics/enum-is-callable-review.json)
records two exact originals and 43 source-reached strict guards. The third
by-reference output for literal generated method strings is described below;
autoload and wider magic/user-method cases remain partial.
Engine routes: `ext/standard/type.c:PHP_FUNCTION(is_callable)` and
`Zend/zend_API.c:zend_is_callable_at_frame`.
Malformed live arrays return false for wrong length, missing keys, a nonclass
receiver or nonstring method before the syntax-only early return. The
[shape review](../../coverage/semantics/enum-is-callable-shape-review.json)
records the published enum key-0 cut; the
[wide-shape review](../../coverage/semantics/enum-is-callable-wide-shape-review.json)
adds seven exact outcomes, 46 reached guards and an affected prior-state check.
For absent concrete/generated methods, the query uses a source-certified
public `__callStatic` for class strings and class-name arrays, or `__call` for
case arrays. An opposite-kind handler cannot rescue the missing method. The
[magic review](../../coverage/semantics/enum-is-callable-magic-review.json)
records eight exact native/model outcomes and 56 reached guards; neither
magic body runs during the query. Other magic sources and inaccessible-method
fallback remain partial.
An array with a live enum case receiver can also name a direct public user
instance or static method. The [case-method review](../../coverage/semantics/enum-is-callable-case-method-review.json)
records seven exact outcomes and 49 reached guards that tie the method
descriptor to its enum source member without entering the body. Imported,
inaccessible and attributed methods remain partial.
For a literal generated enum method string and initialized string-valued
caller CV, the third positional argument retains a reference to that cell
through CONFIG, then receives the canonical name before the boolean result. The
[output-CV review](../../coverage/semantics/enum-is-callable-output-review.json)
records one exact source and 45 reached guards. Array inputs and old-object
destructor/input-output alias effects remained explicit Unsupported at that cut.
The same literal route writes the name for an absent method on both runtime
false and syntax-only true; the
[false-output review](../../coverage/semantics/enum-is-callable-output-false-review.json)
records a second exact source and 42 reached guards.
For two-item literal arrays with canonical enum class spelling, direct class
strings and live enum cases derive the callable name from their actual
receiver and literal method values. The
[array-output review](../../coverage/semantics/enum-is-callable-output-array-review.json)
records two exact outcomes and 68 reached guards. Literal class-string arrays
also retain lowercase and leading backslash source spelling, whereas case
arrays use the canonical enum name. The
[spelling review](../../coverage/semantics/enum-is-callable-output-spelling-review.json)
records three exact outcomes and 64 reached guards. Wider array sources remain
partial beyond the live two-entry route below. Initialized int, bool and null
output CVs also receive the name before the boolean through the same
source-certified path. The
[scalar-output review](../../coverage/semantics/enum-is-callable-output-scalar-review.json)
records three exact outcomes and 79 reached guards; old-object replacement uses
the lifetime rules below.
Literal enum method strings also retain raw class and method spelling in the
third output. The [string-spelling review](../../coverage/semantics/enum-is-callable-output-string-spelling-review.json)
records canonical, lowercase and leading-backslash outcomes with 88 reached
guards.
A direct variable input now captures its string at the first SEND. A nonowning
receipt binds that copy to its call site, argument origin/line and caller depth;
SENT owns the actual argument. The adjacent receipt authenticates the saved
bytes after later arguments rebind the source CV. Normal invocation
consumes it atomically, nested calls keep separate receipts and exception
unwinding discards it before output capture. The
[saved-input review](../../coverage/semantics/enum-is-callable-saved-input-review.json)
records seven exact sources, 200 independent guards and affected variable46/
alias43 checks. Named/unpacked forms remain partial. Engine routes are
`zend_compile_args`, VM `ZEND_SEND_VAR`/`ZEND_SEND_VAR_EX` and
`ext/standard/type.c:PHP_FUNCTION(is_callable)`.
For a live two-entry variable array, the first SEND records its actual array ID
and borrowed member history without owning a second copy. Direct class-string members
retain raw spelling; a case receiver uses its enum's canonical class name.
The sent array stays owned while later arguments or the old output destructor
rebind the source CV. A shared input/output cell receives the name after its
reference is captured, and a throwing destructor commits that name before
exception transfer while leaving the boolean assignment untouched. The
[variable-array review](../../coverage/semantics/enum-is-callable-variable-array-review.json)
records seven exact agreements, two explicit Unsupported controls, strict435
and separate reached groups of 60, 53, 33 and 70 checks. Key-2 input arrays and
wider owning rebound arrays remain outside this receipt route. Engine routes are
`ext/standard/type.c:PHP_FUNCTION(is_callable)` and
`Zend/zend_API.c:zend_is_callable_ex`.
For a shared input/output CV rebound to a new two-entry DIRECT string array,
the original first-SEND array and name remain authenticated through the later
third-argument reference. Writing the selected name releases only the shared
cell's new-array owner; a separate holder retains that array. A throw in the
second argument never reaches the output write. The
[array-alias rebound review](../../coverage/semantics/enum-is-callable-array-alias-rebound-review.json)
records four exact agreements, one explicit Unsupported owning-object control,
strict435 and five separate reached groups (229 checks) at that historical cut.
An exact rebound array with one ordinary childless object now authenticates
its historical array and child through a clear-to-null destructor continuation.
The last owner sees null before destruction; a separate array holder delays
the destructor until after the selected name commits. A throwing child commits
the name before exception transfer, leaving the interrupted result target
unchanged. The [owning-array review](../../coverage/semantics/enum-is-callable-array-alias-owning-review.json)
records three exact agreements, one excluded-builtin control, strict435 and
three separate reached groups (200 checks). ALIAS/reference entries, extra
object children and wider owning shapes remain partial.
When a separate variable owns the one ordinary child object but not its
rebound array, overwriting the shared cell starts an authenticated eager array
release. The child remains live until the separate holder is cleared; releasing
that holder before output instead uses the existing last-owner continuation.
The [retained-child review](../../coverage/semantics/enum-is-callable-array-alias-retained-child-review.json)
records three exact agreements, strict435 and separate held75/released55 checks.
Additional children or ALIAS entries in the rebound array, and wider ownership
graphs, remain partial.
The sent callable array itself now admits DIRECT or genuine untyped ALIAS
members at keys 0 and 1. The first-SEND receipt saves its table identity,
physical slots and borrowed initial member values. Later arguments may rebind
the source or mutate its referenced receiver/method; invocation reads the cells
in the sent table. Ordinary COW retains shared references and unwraps singleton
references under the existing array rules. The output may alias a member cell
or the whole source cell. Before destroying an old output object, invocation
saves a second borrowed member snapshot, the name and the boolean. Output
cleanup validates that selection without rereading changed reference payloads,
including when the destructor changes the method type or throws. Both snapshots
add no heap owners: SENT and ordinary trace arrays retain the real table/cell
edges. Typed, coerced, backed, indebted and retired member cells remain explicit
Unsupported in this receipt route. The
[reference-member review](../../coverage/semantics/enum-is-callable-reference-array-review.json)
records the source and reached cuts. Engine routes are
`Zend/zend_vm_def.h:ZEND_SEND_VAR`, `Zend/zend_hash.c:zend_array_dup_value`,
`Zend/zend_API.c:zend_is_callable_at_frame` and `zend_get_callable_name_ex`, and
`ext/standard/type.c:PHP_FUNCTION(is_callable)`.
Literal arrays, assignment results and function-produced arrays now use the
same first-SEND receipt. The compiled argument origin and send line identify
the expression; the actual KNOWN, VARIABLE or REFERENCE operand determines
the transferred table. A temporary keeps its one table owner, while a
reference-return operand gives up its wrapper owner and retains the table in
SENT. Shared and singleton reference COW, member output aliases, saved output
selection and throwing argument cleanup use the existing owners. In particular,
a last temporary array releases an ordinary child held in its reference cell
before catch, without writing the skipped name/result. The
[temporary-array review](../../coverage/semantics/enum-is-callable-temporary-array-review.json)
records the separate source and reached cuts. Source routes
include `Zend/zend_vm_def.h:ZEND_SEND_VAL` and `ZEND_SEND_VAR` for returned VAR
and ordinary CV operands.
Capture now records genuine slots independently of whether their initial values
form a callable. Its label uses saved bytes or cached case metadata and never
resolves a class name; invocation alone admits the current receiver and method.
Old objects or array children in referenced members can be destroyed during
argument evaluation while their borrowed history remains valid. Type-invalid
current pairs return false and the name `Array` before syntax-only lookup;
output destruction may repair those cells without changing that saved result.
After the C handler returns, argument-child destruction sees the committed name
and an unassigned result, with no `is_callable` trace frame. The
[initial-member review](../../coverage/semantics/enum-is-callable-initial-members-review.json)
records these source and ownership cuts. Typed member cells in otherwise valid
pairs and wider non-enum lookup/lifetime contexts remain partial.
Wrong length or missing key 0/1 now uses one structural check and an empty
member snapshot, distinguished from a string receipt by the saved array ID.
Only shallow entry/cell validity is required; typed reference payloads need no
read or coercion to answer false/`Array`. The actual SENT owner fixes the old
shape through source COW and same-CV output replacement. Output destruction
can repair the source while the saved result and API trace retain the original
shape. A separate array holder delays child destruction; otherwise argument
cleanup runs after the handler and before boolean assignment, without an API
frame. The [structural-array review](../../coverage/semantics/enum-is-callable-structural-array-review.json)
records the bounded source and reached checks.
Third positional simple output CVs now follow the selected builtin's reference
signature at SEND3, independently of query/name admission. Generic writable-name
acquisition initializes an absent CV to null and promotes its real CELL without
an undefined-variable read. The reference slot is validated separately from the
handler's existing value/lifetime fences. A callback may unset the output name
while a retained alias keeps its old cell, or create an output object before
SEND3. Dynamic `SELECTEDCALLS` keeps the chosen builtin when its source callee
variable is rebound; an earlier argument throw never acquires the output.
The [output-acquisition review](../../coverage/semantics/enum-is-callable-output-acquisition-review.json)
records these source and ownership cuts. Fixed namespaced
`is_callable(..., publish(), $name)` now records the actual fallback builtin
before arguments, so `publish()` can declare a local function without changing
the chosen target or reference signature. Root and ordinary named-function
sites reuse this cache authority on later calls, even if the first call threw
during argument evaluation. A distinct cold site selects the local function.
Selection history borrows source/line/function identity and adds no roots;
capture requires a cold builtin lookup or genuine prior authority. The
[fixed-fallback review](../../coverage/semantics/enum-is-callable-fixed-fallback-review.json)
records these source, owner and pending-throw checks. Closure scope changes can
create a private Zend runtime cache, so unproved closure/method/fake/bound and other
unproved owners refuse explicitly. Named/unpacked and wider output places
retain their existing bounds.
Known unscoped real-Closure births at root or in ordinary named functions now
carry a nonowning cache stamp. The first literal birth fixes the template's
scope policy; an unknown birth prevents a later unscoped shape from claiming a
shared cache. Ordinary clones copy a known shared policy, so new factory results
and clones retain the warmed builtin after their creator retires. Selected-call
records distinguish cache identity from the call's real heap owners. Stamps
check immutable function identity and known scope while the object is live;
retired parent IDs remain borrowed history. The
[Closure cache review](../../coverage/semantics/enum-is-callable-closure-cache-review.json)
records this first shared slice. Real bind copies now stamp their completed
scope metadata. Same-scope copies share a known template cache; a scope change
or a private source gives the new object its own fresh cache. Clones retain this
policy even after old binding records retire. Generator `Closure::call` stamps
its actual allocated Closure copy after binding/captures/statics; its Generator
keeps that object through ordinary ownership. The
[private-cache review](../../coverage/semantics/enum-is-callable-private-cache-review.json)
records these copies. Ordinary user `Closure::call` now gives its temporary
function an append-index cache identity, separate from Closure object IDs. Known
scope changes or private sources get fresh invocation keys; only proven same-scope
nonprivate copies can share. Current contexts bind keys to actual function, live source/receiver
and API site; saved frames retain them, and ordinary/named function entry
clears inherited keys. Birth rows own nothing and remain valid after retirement.
The [invocation-cache review](../../coverage/semantics/enum-is-callable-ordinary-call-cache-review.json)
records repeated-site, throw and nested-function checks. Static receiver binding
is rejected before cache birth. Ordinary named/inherited method factories now
prove literal scope using raw named-Class/method source, exact creator target,
function and lexical owner, and the validated post-created scope. Trait/imported
origins and anonymous classes cannot enter through descriptor membership alone.
First known template scope determines sharing; receiver/CALLED class does not.
Inherited Child makers retain Base cache policy through clone, same-Base bind/call
and original retirement, while Child scope changes get fresh caches. Canonical
literal scope also rejects wrong-class history after retirement. An earlier
unknown Fiber birth still blocks a later root birth from claiming sharing. The
[scoped-birth review](../../coverage/semantics/enum-is-callable-scoped-cache-review.json)
records these cuts. Raw ordinary named/inherited nongenerator methods now use
their actual shared op_array cache. Pure history binds the query opcode to its
exact owning descriptor; current authority additionally matches ordinary target,
full function, lexical owner and empty temporary cache key in a valid context.
Receiver/CALLED identity never chooses this cache. Before-argument selection
survives publication, argument throw, output destruction and receiver retirement;
a fresh second method can select USER. The
[method-cache review](../../coverage/semantics/enum-is-callable-method-cache-review.json)
records this cut. Genuine runtime named-function and direct method FCC and plain-function
`Closure::fromCallable` lookup now stamp Shared on the created capture. Those
routes initialize the source runtime cache; method table API lookup and constant
method FCC do not imply that event. Captured functions/scopes remain immutable
history after retirement; parent-stamped clone copies preserve policy, while
unstamped constant/API parents stay unstamped. Converting an existing Closure
through FCC or fromCallable preserves identity and creates no stamp. The
[shared-capture review](../../coverage/semantics/enum-is-callable-shared-capture-cache-review.json)
records this bounded slice. Method `fromCallable` now uses explicit source-cache
registration and actual INIT facts, including attempts that throw before body
entry. Runtime invokable/array/string FCC also records allocation independently
of capture-query admission; raw CAPI method entry supplies its actual later event.
Known cold births and private clones have fresh private keys; initialized sources
share. Initialization/uncertainty boundaries preserve each old capture policy after
later events, and missing history remains unknown. Existing Closure copies never
initialize the original raw source cache. See the
[method-API cache review](../../coverage/semantics/enum-is-callable-method-api-cache-review.json).
Runtime array/string method captures now require recorded INIT at their actual
birth, immutable raw function identity and canonical declared scope. Saved
selection names/classes must still resolve to that function through pure class
metadata; history never dereferences retired receivers or callable arrays. Clone
lineage, argument-throw warmth and output-throw continuation preserve the shared
cache after old captures retire. Missing INIT refuses cache stamps, history and live
ownership. See the [runtime-capture review](../../coverage/semantics/enum-is-callable-runtime-capture-cache-review.json).
Known user fake `bind`/`bindTo` copies now stamp the completed lexical scope and
actual source cache. Same-scope Shared parents share; Private parents and a
named function's dummy `Closure` scope receive fresh private keys. Bound clones
stamp their immediate parent even when their immutable body points further back.
Source, old receiver and selected-array retirement retain pure function/cache
history without adding owners. Binding-site, descending source, completed-scope
and copy-parent coherence checks exclude unrelated same-function stamps; copied
calls do not initialize or taint the original method cache. See the
[fake-bind cache review](../../coverage/semantics/enum-is-callable-fake-bind-cache-review.json).
Known unbound nongenerator user-method `Closure::call` copies now authenticate
temporary cache history through the named method, immutable source and completed
exact declaring-class scope. Private sources receive a fresh invocation key;
Shared sources retain their same-scope cache. Argument-time source removal keeps
the selected source alive through the real API owners, then retires its old
receiver independently of the replacement. History adds no pins and leaves raw
method initialization facts unchanged. See the
[fake-call cache review](../../coverage/semantics/enum-is-callable-fake-call-cache-review.json).
Bound nongenerator user-method temporary calls now follow immutable SOURCE
descent after ancestor capture/receiver retirement. Their completed Base SCOPE
authenticates cache policy independently of a Child CALLED class; replacement
receivers still require exact Base scope. Private calls get fresh invocation
keys and Shared calls keep their cache, with ordinary API ownership and no
history pins. The [bound-call cache review](../../coverage/semantics/enum-is-callable-bound-method-call-cache-review.json)
records one public-method original and its reached scope/owner/history checks.
Constant/default/static/property captures, resumed Generator,
internal/Trait/anonymous/Fiber query owners, bound free-function/dummy-scope
temporary calls and wider transformed contexts remain partial.
An initialized childless ordinary old output object can also be replaced when
the actual postwrite ownership graph still owns it. The captured CV is written
before returning the boolean, and another owner delays destruction. The
[retained-output review](../../coverage/semantics/enum-is-callable-output-retained-review.json)
records its original source/reached cut and owner guards.
For last-owner childless ordinary objects, `ZEND_TRY_ASSIGN_REF_STR` calls
`zval_ptr_safe_dtor`, which sets the captured cell to null before user code.
The output continuation owns that cell and the real call arguments; its old
object metadata owns nothing. Generic eager cleanup runs the destructor before
a raw commit writes the chosen name, including before a pending throw resumes.
The current output variable may have been unset or rebound; the captured cell
still receives the name. Resurrection uses the ordinary once-only destructor
mark. The destructor has an internal call site followed by the `is_callable`
API frame, whose arguments snapshot the captured cell at trace creation. The
[unique-output review](../../coverage/semantics/enum-is-callable-output-unique-review.json)
records twelve normal originals, five explicit controls, strict433,
345 independent guards and affected retained77 checks at separate cuts.
Root VM exit now leaves PHP frames and drains their locals while the real C
destructor pin and output arguments stay owned. A nonowning continuation then
finishes the original destructor and commits the name before exit propagates.
Nested live queries commit in order; neither boolean reaches its abandoned
assignment. Cleanup destructors have an internal site followed by the actual
`is_callable` API snapshot. The
[exit review](../../coverage/semantics/enum-is-callable-output-exit-review.json)
records seven exact exits, seven explicit controls, strict433 and 247 independent
guards. Pending output in an active Fiber caller chain refuses explicitly;
unrelated dormant Fibers do not trigger an early commit. Their force-close
protocol remains partial.
Local cleanup throws replace pending exit; the name commits before a caller
receives the exception.
Compiled CV order preserves each shared-wrapper decrement; the remaining
receiver release and real C pin stay distinct owners until their respective
stages finish. Further local throws retain the ordinary previous-exception
chain. Integer exit status survives a catch and later string exit; another
integer exit replaces it. The
[cleanup review](../../coverage/semantics/enum-is-callable-output-cleanup-review.json)
records eight new/promoted agreements, one affected enum exit-status source,
three explicit controls, strict433 and independent 256+47 guards at separate cuts.
This model slice refuses an exit attempted while an ordinary cleanup Throwable
is pending before generic unwinding can discard the C return.
Nested local cleanup exits now return through each genuine destructor C pin,
preserving the parent query's borrowed receipt and output cell. The latest
integer exit supplies status; a string exit preserves it. An ordinary Child
throw cancels exit while the name still commits, and nested queries keep their
own names and untouched result assignments. The
[reexit review](../../coverage/semantics/enum-is-callable-output-reexit-review.json)
records nine agreements, three explicit Unsupported controls and five separate
reached groups at their actual cuts. `debug_backtrace()` remains outside the
core observer boundary and is a control rather than an agreement.
Owning rebound values and newly attached type sources remain partial.
Native raw overwrite can retain an abandoned count for a destructor-created
object until the store sweep; it cannot be modeled as a second checked write.
Wider variable arrays remain outside third-output name authentication.
