# Explicit closure templates and lexical captures

This compiler gives each real closure expression an unregistered source
template. The descriptor reuses function signatures, default locations, CVs, body
code and diagnostic names; it is kept in CLOSURETEMPLATES and never installed as a
named callable. The runtime instance is a separate identity. Invocation, capture
ownership and per-instance static storage require the paired runtime116 evidence;
compiler phase agreement alone does not establish them.

Closure parameters retain their original FIELD3 paths and the body retains FIELD6.
CODELEXICAL records each original use path, name, reference mode and variable-token
line. The outer compiler checks forbidden and duplicate lexical names before
parameter compilation. Parameter/use conflicts precede body compilation; lexical
names also occupy the static declaration namespace. Native multiline originals
show that forbidden/duplicate diagnostics retain the prior emitted line until a
capture succeeds, and parameter/use conflicts retain the signature cursor. An
ampersand on a preceding line does not change the captured variable's emitted line.
The same line serves outer BIND_LEXICAL and inner BIND_STATIC operations, whose
runtime ownership and sequencing remain distinct.

Named and closure scopes both participate in parent code filtering. Capture,
parameter and body descriptors of nested templates cannot leak into parent code.
Named declarations reset the active closure context and restore it afterward.
Magic function/method names preserve the source filename or enclosing function
context and closure start line, including nested closure names. Those strings are
diagnostics and language magic values, not runtime identity or lookup registration.

The admitted signature masks add object and callable plus the normalized known
Closure class. Arbitrary classes, intersections and iterable protocols retain their
existing dependencies. Object casts compile their operand; identity-preserving
casts of existing closure values are paired with runtime behavior, while ordinary
object construction remains a required separate dependency. Exactly two existing
object/callable declaration expectations are retired after preserving their actual
stale assertion failure and native source contexts.

Private maintained checks cover26 compiler phases and109 source projections,
including22 own source contexts, two reviewer-owned type/cast contexts and the two
retired declaration cases. Five focused shared gates pass typed59 plus5 pending,
named-static29 plus1 pending, main-static12, dynamic42 plus2 pending and function46.
These preserve their exact1011/63d0 input identity. The initial namespace-fixture
setup failure, DSL binder failure and actual multiline diagnostic mismatch remain
retained before their bounded corrections. The final runtime pair is1017/9325, installed as875c7867. Arrow
implicit captures, fake first-class callables, methods, object services, exceptions
and dynamic-source lifetime remain required later.

The paired runtime type lane changes four files while preserving pure compiler
type conversion. State-aware receives and returns recognize live closure objects
for object/callable/Closure, registered named functions and configured builtins for
callable checks. Potential method callback services remain explicit dependencies.
Caller/callee strictness, deferred default caches and reference-return writeback
retain their existing rules. Class diagnostics say Closure and traces render
Object(Closure), independently of the object type mask. Its13 retained source
replays and35 helper assertions passed on1010/89f; the final pair contains those
exact bytes. The archive retains its first elaboration and fixture syntax failures
separately. The independently audited28 ordinary scalar/array regression replays
pass on1017/9325 using the retained historical CLI profiles, without native repeats.
