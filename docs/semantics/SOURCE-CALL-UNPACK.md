# Array call argument unpacking

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

Traversable expansion requires object semantics. Builtin bodies, builtin default
receives and callbacks remain required integration work; their source name/mode
catalogue does not constitute body execution. Reporting configuration, other
callables, static locals, closures, objects, exceptions, dynamic source, lifetime
and the final complete-core gates remain pending. This checkpoint closes no
entire semantic family.

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
