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

Full nested/read-write/reference and memoized ArrayAccess consumers remain
required core work. Their newly reachable unsupported paths stop explicitly
instead of producing an ordinary-object error. By-reference Get results stay
separate from the user-paused return verification. Combined Iterator/ArrayAccess
source-interface notice ordering remains required.

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
Production comparisons use SL_mode, reached fixtures use AL_mode, and no fresh
build or full-family closure is claimed.
