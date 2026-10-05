# Reads from scalar containers and offset warnings

Module282 stages ordinary R reads from missing CV or null/bool/int/float
containers through genuine base-CV, key-CV and offset warnings. A missing-base
warning resumes with independent null; defining that CV does not supply a later
array lookup. A defined scalar follows its selected CV
or already dereferenced real reference cell for the later diagnostic type. The
scalar path stays selected even if a key-warning callback installs an array.
An object installed at that boundary supplies its immutable class name to the
warning, including after its last owner retires.

Computed or nested row values are copied before the outer key demand. Their
real operands keep genuine temporary arrays and embedded reference cells alive;
borrowed selected pointers and sampled values add no owner. Scalar reads ignore
null/float/array key conversion, so those keys produce no array-key diagnostics.
Source, line, mode, constant operands and owning forms remain checked. Consistent
dynamic cells and sampled values are runtime facts, not callback-history proofs.

Quiet missing bases stay uninitialized and emit no base or offset warning.
A missing key CV still warns. Scalar FETCH_DIM_IS returns null independently of
callback mutation; terminal isset/empty instead samples the selected pointer
and can use the existing string predicate after a scalar-to-string callback.
A newly installed array does not create a late quiet array lookup. Throwing
base/key callbacks suppress the remaining callbacks and later consumers,
preserving the typed destination and the original error's previous chain.

A separate terminal stdClass transition agrees with native PHP. An ArrayAccess
transition is native-grounded, but its model at the282 cut stops earlier at the
existing `internal interface method contract` Unsupported, before the key callback. The
attempt to reach the new guard therefore fails its control assertion and earns
no agreement or guard-execution credit. The complementary, source-reviewed guard
keeps ArrayAccess separate from the ordinary-object Error. Module284 now admits
the [direct ArrayAccess contract and calls](SOURCE-ARRAYACCESS.md) with distinct
evidence; the earlier failed control keeps its original zero credit.

The pinned contracts are `FETCH_DIM_R/IS`, `zend_fetch_dimension_address_read`
and `zend_isset_dim_slow` in `vendor/php-src/Zend`. Author8 agreements include
one independent object-name original; independent13 retains that same original
and adds12 fresh comparisons:20 unique private programs. Author69/72/71=212 and
independent77/67/65/63=272 reached assertions pass atc9a, with earlier source cuts
retained. One actualb025 source at5eefe retains private Owner/Child selection,
genuine key-temporary ownership and live caller/static17. The
[ledger](../../coverage/semantics/container-read-review.json) keeps those cuts and
the original formatter-overlap failure distinct.

The catalogue and reached fixtures are `tests/semantics/container_read_cases.py`
and `container_read_protocol.py`. `python3 -B tests/semantics/container_read_prepare.py
[fixture-id ...]` compiles selected source-derived fixtures with existing local
tools. Production comparisons use SL_mode and reached fixtures use AL_mode,
without a fresh-build or full-family claim.

Initial string/ordinary-object reads, full nested/RW/reference ArrayAccess,
wider variable/property base producers,
GLOBALS quiet/memoized/unset consumers and initial writable memoized/unset/append
containers remain required core work. Paused return verification stays separate.
