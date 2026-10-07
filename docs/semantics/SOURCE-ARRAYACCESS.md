# Source ArrayAccess dimensions

Module284 admits the builtin ArrayAccess contract and ordinary staged dimension
calls. Implementations retain public/nonstatic mixed offset/value compatibility;
static or narrowed offset declarations produce CompileError. Tentative return
notices run through the published declaration queue, including
ReturnTypeWillChange suppression and inherited/indirect interface methods.

Ordinary reads call offsetGet. Coalesce first calls offsetExists and calls Get
only when its result converts to true. Isset uses Exists; empty may continue through Get.
Direct assignment, append and unset call Set/Unset with the original mixed key;
append supplies null, and array/object/float keys receive no array-key coercion.

Reads, coalesce and Set retain the originally selected receiver across a missing
key warning. Terminal isset/empty and unset sample their selected container after
that warning. The slow terminal route does not retry an installed array. Missing
key or RHS warnings resume with captured null; Set copies its key after RHS
demand. Computed RHS evaluation precedes receiver/key selection. After Set, the
assignment result samples its original CV or already dereferenced real CELL
pointer, including callback mutations and CV rebinding.

The std handler retains its receiver and dereferenced key value through the
implicit call. Original CV/temporary operands and entered parameter values keep
their genuine owners; sampled VALUE/SELECTED fields add none. A NaN truth result
stages its bool warning while preserving the inner receiver and copied key.
Source, method, line, constants and operand forms are authenticated; consistent
dynamic selected facts do not claim a callback-history proof.

Module292 adds ordinary by-value compound assignment and writable Get
continuations. Direct compound calls Get in read mode, applies the operator,
then calls Set. Defined key and RHS CV wrappers are read again after Get;
missing-CV demands before Get latch independent null. The compound result is
the computed value. A throwing Get produces the opcode's replacement Error,
with the original exception and its existing previous chain retained.

W/RW/Unset Get fetches keep one owned temporary cell. Nonobject, nonreference
returns emit the indirect modification Notice; returned objects continue without
it. Array copies preserve real reference rows, and nested writes mutate the
owned temporary or extracted real cell. Computed RHS evaluation precedes queued
Get/Notice; delayed RHS CV demand follows Notice, and a thrown Notice suppresses
later demand, write and unset. Pre/post updates use the fetched temporary without
calling Set. Final nested Unset retains its borrowed ROOT/ELEMENT or reference
selection through key warnings and reads the selected object afterwards; malformed
pointer forms are rejected without claiming callback-history authenticity.

An exposed GLOBALS reference finish is repaired in276: the converted variable
name survives the writer, global binding ignores a function-local shadow, and
owning keys/captured real source cells survive callbacks. A missing name CV can
be populated by its warning handler before conversion, unlike an ArrayAccess
key's independent-null latch. The old249 direct unset admission is restricted
to its direct base, avoiding overlap with255's nested continuation.

Module304 reconstructs intermediate append after Get, including repeated `[]`,
and final compound append through returned arrays or child objects. Array append
inserts the next index without a null/missing-key lookup; an ArrayAccess child
receives null in Get and Set. Owned returned ancestors survive until selected
rows are extracted. Copies of real reference cells detach only when their actual
owners permit it, including permanent literal-pool roots. Append and explicit-null
dimension tasks retain distinct source forms at public admission.

False-conversion handler throws still permit the DIM_OP's row insertion, late CV
sample and binary operation. A successful numeric result can be written while the
old error remains pending; divide/modulo by zero or negative shift instead installs
the new primary above its complete old chain. Conversion warnings and integer
double conversion have their own pending-error checkpoints. Eligible installed
handlers are skipped by Zend's pending-exception call API; ineligible or absent
handlers retain default reporting. Object concat skips method execution and keeps
the pending error, so this branch uses no live Stringable return producer.

Final simple append to a returned ArrayAccess child, wider memoized/property/GLOBALS
ArrayAccess producers, by-reference Get results and combined Iterator/ArrayAccess declaration ordering
remain required core work. Newly reachable unsupported paths stop explicitly.
By-reference Get stays separate from the user-paused return verification.

Author13 agreements comprise six normal originals, two declaration errors and
five independent controls at9d. Independent20 retains those same five and adds
15 normal comparisons atbb:28 unique private programs (26 normal, two declaration
errors). Author69/61/75=205 and independent78/61/64/84=287 reached assertions pass
atbb, retaining the original author compiler cut at9d and the corrected fourth
independent compiler separately. One actual465d source at6ccb agrees through
private Owner/Child selection, receiver retirement and post-Set readback from the
old typed reference cell. The [ledger](../../coverage/semantics/arrayaccess-review.json)
keeps these cuts and original parser, recorder, descriptor and fixture failures.

The catalogue and reached fixtures are `tests/semantics/arrayaccess_cases.py`
and `arrayaccess_protocol.py`. `python3 -B tests/semantics/arrayaccess_prepare.py
[fixture-id ...]` compiles selected source-derived fixtures with the existing
project-local tools. The maintained NaN original recovers its reached fixture;
copying helpers and composing the publication parent adds no execution credit.
Earlier284 production comparisons use SL_mode and reached fixtures use AL_mode; no fresh
build or full-family closure is claimed.

The writable milestone retains34 distinct normal source agreements: author8
and independent26, including the affected GLOBALS/Unset controls. Author223 and independent793 premises pass across13 recipes (1016 total):
634 in AL_mode and382 in strict SL_mode.
The [writable ledger](../../coverage/semantics/arrayaccess-write-review.json)
records actual HEAD805 plus each tracked diff, tools, commands, limits and
original failures. The original count-based Unset observer remains Unsupported
with zero agreement; its separate isset/row-value companion agrees under the
core-language observation boundary. Earlier284 gates are retained without renewal. One fresh actual38f+292/274
source combines include conversion287, private Owner/Child selection and live
GLOBALS RHS rebinding; algorithmic compilation, structuring and loader checks
pass. Its original missing finite-provider input failure remains0; only the
affected model rerun adds the explicit cwd/caller/Array certificate.

Writable originals are in `arrayaccess_write_cases.py` and
`arrayaccess_write_review_cases.py`; `arrayaccess_write_protocol.py` retains13
source-reached recipes. `python3 -B tests/semantics/arrayaccess_write_prepare.py
[fixture-id ...]` compiles them using the existing tools and a read-only revision
snapshot. Compilation, source agreement and reached-state execution remain
separate; promotion of identical recipes adds no semantic execution credit.

Append304 retains 49 unique normal comparisons at three source cuts and eight
source-reached strict-SL recipes/723 premises at two state cuts. The
[append ledger](../../coverage/semantics/arrayaccess-append-review.json) records
the existing exact runtime, caps, environment, original failures and narrower
admission repair. One fresh actual38f+accepted292+304/275 source agrees through
include conversion, private Owner/Child scope and a retained old reference cell;
its finite-v2 cwd/caller/Array certificate is supplied from the start. Earlier284
and292 gates are retained without renewal.

Append originals and original native observations are in
`arrayaccess_append_cases.py` and `arrayaccess_append_review_cases.py`.
Two default diagnostics retain their original visible filename in `OBSERVED_FILES`;
a fresh differential comparison must use its new native observation or explicitly
substitute that filename. `arrayaccess_append_protocol.py` and
`arrayaccess_append_review_protocol.py` retain the eight executed recipes.
`python3 -B tests/semantics/arrayaccess_append_prepare.py [fixture-id ...]`
compiles their merged helper prefix; three affected prefix checks are preparation
only and do not renew the 723 executed premises.
