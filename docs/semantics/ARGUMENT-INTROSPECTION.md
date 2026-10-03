# Ordinary-frame argument introspection

Target: PHP 8.5.10 CLI NTS 64-bit.

`func_num_args`, `func_get_arg` and `func_get_args` read the active ordinary
function, method or Closure frame. Fixed parameters use current local cells;
retained positional extras use the call context. Unset slots read as null.
Named holes contribute defaults within the supplied fixed extent; trailing
defaults and extra named variadic entries do not contribute. Value variadic
array writes leave retained extras unchanged, while shared reference-cell
writes remain visible.

Results remove outer references. `func_get_args` creates a fresh packed array;
child arrays retain normal copy-on-write behavior, embedded reference cells
remain shared, and objects retain identity. The live view adds no heap roots.

The builtin receives its own arguments before checking the caller. The indexed
API orders arity, int conversion, negative index, code/global context, dynamic
prohibition and range. Zero-argument APIs order arity, context and dynamic
prohibition. Converted indices leave source values and error trace arguments
unchanged. Intrinsic `Closure->__invoke` receives weakly and sees its internal
wrapper; an ordinary intrinsic Closure call still checks global context first.
Direct code in include/eval is a code frame even when it shares lexical locals;
a function called there uses its own frame and restores its caller afterward.

Direct names, imports, namespace fallback and actual compiler CONST callees
use ordinary routes. A constant-valued expression is not necessarily CONST:
a ternary may remain dynamic. Variable strings and intrinsic Closure calls
reach the native dynamic-call error after earlier receive checks. A selected
namespace fallback remains selected during argument effects that publish a
new primary. Source declarations, modes and temporary-write priorities remain
with the existing compiler modules.

Direct PHP-name and parser-created string-literal num/get_args calls, including
literal concatenations, retain their optimized TMP result class with no fallback
and zero source arguments in an ordinary body. Required-reference
consumers preserve this class through suppression and nonreference list
assignment. They evaluate all delayed chain key and dynamic property-selector
expressions, then reject the first temporary dimension or property fetch at
its emitted line; literal CV reads and conversions have not run. Generic VAR
call routes retain their reference behavior. Nullsafe API chains use byvalue
fetches and the native required-reference SEND error. Evaluated temporaries own
their operands once and release them on normal or abrupt unwinding.

Compiled constant array property selectors produce their conversion warning
during compilation. An earlier optimized call or temporary receiver write error
prevents that selector from compiling; erased selectors produce no warning.
Suppression in a known write context rejects before compiling its child.

198/199 are a privately reviewed ordinary-frame increment over accepted
fdef6285d. [The review ledger](../../coverage/semantics/argument-introspection-review.json)
binds author gates, 26 retained compatibility sources, and independent
83 ordinary sources plus 24 unique state cases/445 assertions. State certificates
combine exact retained and focused receipts; original failed aggregates remain
failed. Invalid-fixture diagnostics and future Unsupported controls are separate.
Installation on current master and a fresh offline network-isolated rebuild remain
pending. Generator/Fiber, autoload, unfinished handlers and source `__invoke`
interactions beyond this baseline require later work. The inventory row stays partial.

The projection on tested SET13c9c4dd is accepted privately at 47040e57,
preserving installed capture, named/unpacked calls and CONFIG certificates.
[The current ledger](../../coverage/semantics/argument-introspection-current-review.json)
binds author mixed source157 (retained3 plus fresh154) and mixed finite29/712
(retained71 plus fresh641), with one Unsupported control separately executed
at zero agreement. Independent fresh ordinary source2 and finite2/79 retain
separate profiles and mixed compiler provenance. Earlier failed witnesses and
aggregates remain exact; the engine-defect case and model-only17 were excluded
from renewed execution. Canonical integration and wider interactions remain open.

The [CALLS union ledger](../../coverage/semantics/argument-introspection-calls-current-review.json)
accepts private1d615 on source18a with its five-document child: author mixed
source3 and fresh finite4/241 plus retained15/355, independently source2 and
finite2/147. These reach inherited receiver authority, delayed temporary argument
errors and Stringable SET borrowing. The invalid earlier native witness and all
failed preparations remain preserved. Composition on accepted INI7dd keeps those
source endpoints exact; its new live-NUL callback gates and installation are pending.

The pin has an internal MAKE_REF defect for reference-list assignment directly
from optimized `func_get_args()`. The model keeps general list language behavior;
that original is a deliberate engine disagreement with zero native agreement.
Nonoptimized/CV/COW source controls and reached private/CV-alias list stores
validate the general language behavior. The optimized original has a separate
model-only state receipt, recorded in [the discrepancy ledger](DISCREPANCIES.md).
