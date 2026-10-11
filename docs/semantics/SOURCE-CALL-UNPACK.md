# Call argument unpacking

The paired107/108 slice expands arrays into direct user-function calls. Integer
keys send positional arguments in insertion order; their numeric values do not
select parameter positions. String keys bind fixed parameters or ordered named
variadic entries through the existing named binder. The string-key phase belongs
to each unpacked container: an integer following a string in that container
errors, while a later unpack container begins its own phase. Explicit positional
arguments after unpack remain a static error. Later explicit named arguments
retain their original source index while using accumulated destination slots.

Each UNPACK_NEXT task owns its operand independently of the arguments already
sent. It stores the current entry cursor and container string-key phase, without
a historical starting argument count or prior operand snapshots. Source argument
index, effective positional extent, fixed holes, and ordered extra names remain
separate. HOLE has no operand and differs from PHP NULL, even when a diagnostic
renders a missing trace slot as NULL.

The emitted operand class determines whether reference sends may update entries
of the unpacked array. Ordinary literal and folded variable names are CVs, excluding auto-globals and
whole GLOBALS; user-call and
reference-assignment results are VARs. Ordinary assignments, conditional and
coalesce results, computed variable reads, and dimension reads have value
semantics for this operation. List assignment and suppression follow their
source-derived emitted result class. Return-reference designation alone does not
determine the class. Existing source constant, redirect and name descriptors
supply compiler facts; dependent builtin result lowering remains explicit.

Eligible CV/VAR arrays undergo the source-pinned reference-demand prescan and
copy-on-write separation before entry errors. Entries are promoted and bound as
the loop reaches them. A captured reference operand preserves its cell identity;
borrowed reads do not add an owner that spuriously forces another separation.
Temporary value arrays give new references to non-reference entries while
preserving existing reference cells. Earlier sent arguments remain rooted if a
later entry errors, another argument calls a function, or the source variable is
unset. Normal and abrupt cleanup release the container and sent owners through
the ordinary heap and call machinery.

Expanded fixed holes use named default preflight before ordinary typed receive.
Successful deferred scalar defaults are cached before receive coercion; omitted
reference parameters receive independent cells. Preflight and binding inspect
live formal definedness and the effective positional extent. Trailing formals
remain absent until ordinary receive. Typed named tails retain the diagnostic
index max(fixed parameter count, effective positional ARGC)+1; extra named reference
SEND errors use fixed parameter count+1, while explicit fixed named destinations
use their mapped fixed index+1. Suppression and saved caller ownership
follow the accepted101 protocol.

SEND_UNPACK uses the final operand emission line. An original NArg-root CODEEXPR
marker records that line separately from the child call's own emitted line and
the outer call line. The marker has a false constant flag and adds no operand
mode descriptor. Validation projects only actual unpack marker and classifier
consumers from checked source, with literal/folded CV names source-bound at the
active PREP stage. Pending stages bind source lane, callee, source index,
remaining arguments and mode-valid owners. Entry stages check cursor range,
key phase and collected destination presence. At entry zero before any earlier
unpack, the explicit source prefix determines the initial slot shape; later
containers keep their accumulated dynamic slots. Prior values are not replayed.
Arbitrary consistent sent values, container entries and reference-cell values
remain legitimate paused states.

At the array checkpoint, Traversable expansion required object semantics. The
direct Iterator extension below adds that consumer. Builtin bodies, builtin
default receives and wider callbacks remain required integration work; their
source name/mode catalogue does not constitute body execution. Reporting
configuration, other callables, static locals, closures, objects, exceptions,
dynamic source, lifetime and the final complete-core gates remain pending. This
checkpoint closes no entire semantic family.

Validation covers55 exact source outcomes (31 normal,18 PHP errors,6 static
rejections),29 compiler phase comparisons and56 source projections,34 public
state controls with824 assertions,12 adjacent runtime profiles, and two author
ownership cases with435 assertions. Three builtin result contexts remain
explicit dependencies. Independent review adds seven source profiles, four
state cases with1063 assertions, and14 exact compatibility cuts against the
accepted972 baseline. These sets overlap. The cursor guard repair retains the
earlier gate identities; the final two-line unused-helper removal has an exact
zero-reference and byte/mode bridge.

The [runtime record](../../coverage/semantics/call-unpack-runtime.json),
[compiler record](../../coverage/semantics/call-unpack-compiler-pairing.json), and
[independent review](../../coverage/semantics/call-unpack-review.json) bind the
source profiles, failed originals, immutable inputs, and raw process closures.

## Direct user Iterators

Module385 admits direct user Iterators in ordinary source-function call unpack.
The unpack marker owns selected Iterator DATA independently of raw
temporary/reference INPUT; its cursor tracks traversal. A source CV stays borrowed.
The actual argument origin, emitted line, callee, source remainder and destination
modes authenticate pending and saved callbacks. Callback receivers are borrowed;
same-source reentry uses distinct frame-local cursors rather than a global
source-site singleton.

The current cache remains raw through key(). The user Iterator wrapper unwraps
reference-valued keys, normalizes numeric strings, and rejects non-int/string
keys. Values are dereferenced after key effects. Sent arguments own their copies;
next() retires the cached current value first. On error, key, unsent cache, DATA
and raw INPUT retire before pending arguments. Thus an invalid object key dies
before an unsent current object, while a sent object survives DATA cleanup.
An abort operation owns the pending exception while the remaining jobs finish,
including when a destructor replaces the exception. Its source receipt adds no
owners and remains valid after DATA retirement.
Raw valid() results retire before current() or empty completion. Temporary DATA
and INPUT retire before target entry, including empty traversal and defaults.

A by-reference target emits the native argument-number/function/line Warning.
For null/bool/int/float payloads, handlers may mutate a live reference, park or
throw. Resume reads the raw payload once and creates a fresh callee reference
cell; a copied current value is unaffected by handler writes to its source.
Warnings retain actual cursor/cache ownership through invoke/result/cleanup and
saved Fiber views. Copied KNOWN strings also keep their bytes and authenticated
carrier through key/handler writes, named variadic binding and Fiber park/throw.
Zend SEND_UNPACK dereferences and adds a payload reference before the warning,
then wraps the value in a fresh callee cell. Copied strings remain stable across
the callback; immutable string metadata has no modeled heap owners. A live
REFERENCE payload may change during the handler. Authenticated INTERNED_STRING
references now reread that live payload into the fresh callee cell, including
scalar-to-interned handler changes and named variadic or parked Fiber sends.
Zend's interned string flag makes Z_TRY_ADDREF_P inert; no detached payload owner
is needed. The raw source cell retires before next(), independently of the new
callee cell. Handler throw retires raw cell, DATA and temporary INPUT in order.
REQUEST_STRING and plain reference strings, including handler replacements,
remain Unsupported pending their separate pre-warning payload-hold contract.
Direct Generator/Aggregate unpack, other call targets and Generator callbacks
remain explicit follow-ons. The
[string review](../../coverage/semantics/iterator-call-unpack-string-review.json)
records the bounded source and independent state cuts.
The [interned reference review](../../coverage/semantics/iterator-call-unpack-interned-reference-review.json)
retains the two affected originals' earlier native bytes without replaying the
four copied-string agreements or six unaffected state groups.

Copied KNOWN objects now acquire an explicit HOLD before the warning when SENT
is empty. This matches SEND_UNPACK's Z_TRY_ADDREF_P before zend_error, followed
by ZVAL_NEW_REF even when the handler throws. Normal resume transfers HOLD to
the fresh private reference cell and retires the raw current cache before next().
Throw retires cache, DATA and raw INPUT before the failed argument's hold, so
the retained originals destroy the distinct Iterator before the payload after a
handler drops the last independent source owner. Actual Fiber park/resume and
injected throw keep that payload separate from a rewritten global source. HOLD
matches the exact copied object only at byref; earlier, NaN and completed stages
require no hold.
The abort SOURCE receipt validates this shape after payload retirement without
adding an owner. Arrays, REFERENCE objects and copied-object warnings after
earlier sent arguments remain Unsupported. The
[object hold review](../../coverage/semantics/iterator-call-unpack-object-review.json)
records the native-first slice separately from earlier evidence.

Iterator valid NaN warnings keep the raw retval in CURRENT through handler invoke,
result, cleanup and saved Fiber frames. The native `zend_user_it_valid` wrapper
calls `i_zend_is_true`, retires that retval, then permits SEND_UNPACK to check the
exception or fetch current. Its DOUBLE arm rereads the payload after the warning
without redispatching its tag. Numeric references therefore use their live double
bits; an integer minimum reads signed-zero bits and is false. Copied NaN stays true.
The pure existing numeric decision helper performs one reread without another
warning, and raw retval cleanup precedes current or DATA/INPUT teardown. Later
warnings keep earlier sent owners and named phase; handler throw preserves ordered
abort cleanup. Nonnumeric raw-tag changes stay explicit Unsupported.
The [NaN review](../../coverage/semantics/iterator-call-unpack-nan-review.json)
keeps this increment separate from the original unpack source/state cuts.
