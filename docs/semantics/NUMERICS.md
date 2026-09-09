# Numeric reference

`spec/semantics/00-numeric.watsup` is pure executable SpecTec. `pnumber` is
`NINT int | NFLOAT nat`: signed 64-bit integers and unsigned binary64 bits.
Callers must check these ranges. `pnumresult` distinguishes `NUM pnumber` from
`DIVZERO`; an absent derivation is never a PHP exception.

The first numeric milestone supplies `num_add`, `num_sub`, `num_mul`, and
`num_div`, plus `float_of_int`, bit decoding and rational-to-binary64 rounding.
Finite values decode to an exact signed rational; operations round to nearest,
ties to even, with subnormals, overflow, infinities, NaNs and signed zero.
Integer overflow converts each operand to binary64 before floating arithmetic.
Division retains an integer only for exact, representable integer quotients.

The source authority is PHP 8.5.10's `Zend/zend_operators.h`
(`fast_long_add_function`, `fast_long_sub_function`), `Zend/zend_multiply.h`
(`ZEND_SIGNED_MULTIPLY_LONG`) and `Zend/zend_operators.c`
(`mul_function_fast`, `div_function_base`). The target is the pinned Linux
x86_64 build with nearest-even arithmetic. Invalid float operations produce its
negative quiet NaN; arithmetic quiets incoming NaNs and retains the first NaN's
payload. Subtraction preserves an incoming right NaN's sign. These payload details
are tested instrumentation observations, not a claim of portable PHP guarantees.

Run `python3 tests/semantics/numeric.py`. It builds an isolated local test runner,
executes the actual DSL with determinism checking and disabled interpreter caching,
and checks boundary grids, seeded binary64 operands, result types and eight
independent rational-rounding witnesses. The oracle is only `.tools/php/bin/php`.
Test-only `pack('E')`/`unpack('E')` read/write IEEE big-endian bits; their bridge is
checked with raw round trips and known values before testing. `gettype` observes
integer versus float results. None of these observers is a semantic intrinsic.
The report in `coverage/semantics/numeric.json` records the fixed profile, seed,
case-manifest hash and unchanged before/after implementation fingerprints.

This is helper validation; checked PHP source execution must also validate these
operations when the evaluator integrates them. `01-integer.watsup` additionally supplies signed bitwise operations, shifts,
remainder and float-to-integer conversion. `float_long(bits, implicit)` returns
an integer and ordered pending `castnotice` values. The evaluator must run each
notice's handler before committing the result and must propagate abrupt effects.
PHP 8.5 warns even for explicit out-of-range/nonfinite float casts; implicit NaN
casts also deprecate precision loss. Float casts wrap modulo 2^64, whereas numeric
string casts will need their separate saturation rule. Source:
`zend_operators.c` (`shift_left_function`, `shift_right_function`, `mod_function`,
`zend_dval_to_lval_slow`) and `zend_operators.h` (`zend_dval_to_lval`,
`zend_dval_to_lval_safe`). `python3 tests/semantics/integer.py` validates these
helpers, including ordered diagnostic identities with test-only handler
instrumentation; the message renderer and throwing handlers need evaluator tests.

`02-numeric-text.watsup` recognizes numeric byte strings as `NOTNUMERIC`,
`FULLNUM pnumber` or `LEADNUM pnumber`. It preserves integer/float classification,
signed zero, decimal/exponent grammar, whitespace, trailing data and binary64
rounding. Huge exponents use conservative magnitude guards before exact rational
conversion. Source: `zend_operators.c::_is_numeric_string_ex` and
`zend_strtod.c::zend_strtod`. Run `python3 tests/semantics/numeric_text.py` for
boundary strings and seeded decimal cases. The test uses unary plus to obtain the
oracle value and separately checks `is_numeric` and leading-numeric warnings;
these are test instrumentation, not implementations available to the semantics.

At exactly 19 significant integer digits, the pinned classifier compares a
NUL-terminated suffix with `long_min_digits`, including trailing whitespace or
junk. An invalid exponent with a sign advances its pointer once, shifting the
comparison start by one digit. Thus negative minimum followed by a space becomes
a float, negative minimum followed by NUL remains a leading integer, and positive
`9223372036854775808e+` becomes the signed minimum integer. The rules preserve
this source-specific comparison and signed interpretation of the accumulated
unsigned bits. The expanded tests retain both signs, leading zeros, adjacent
bounds, whitespace, NUL and valid/invalid exponents; the original disagreement
observations remain in `coverage/semantics/numeric-boundary-disagreement.json`.

`03-numeric-format.watsup` supplies `number_text(pnumber, precision)`, returning
decoded output bytes and a pending NaN-to-string warning flag. Positive precision
uses exact significant-digit rounding; shortest mode tests increasing decimal
precision and neighboring candidates against the binary64 rounding interval.
Neighbor candidates matter at powers of two, where that interval is asymmetric.
It follows `zend_gcvt` fixed/exponential layout, signed zero, configured precision
and the target's conversion of precision to C `int`. Precision zero acts as one;
negative converted precision selects shortest mode. The formatter bounds only
digit generation after an exact binary64 decimal expansion is already possible.

The pinned `zend_gcvt` truncates special-value spellings through
`snprintf(buf, ndigit + 1, ...)`: precision 0/1 gives `I`, `-`, `N` for infinity,
negative infinity and NaN; precision 2 gives `IN`, `-I`, `NA`; precision 3 gives
`INF`, `-IN`, `NAN`. The specification follows this observed engine quirk, with
no intentional disagreement. Default precision 14 prints the full spellings.
`python3 tests/semantics/numeric_format.py` compares exact bytes and NaN-warning
identity across boundary/generated values and the listed precision profiles,
including every normal power-of-two boundary, decimal-decade neighbors and
both adjacent bit patterns in shortest mode. The retained 8,826-case run took
about 55 seconds on the development host. It does not establish every possible precision/value combination.

`04-numeric-context.watsup` supplies numeric three-way/strict comparisons,
numeric boolean conversion with pending NaN warning, canonical integer string
keys, and distinct explicit/implicit string casts. String float casts preserve
negative zero even when numeric-string classification is integer zero. They use
a separate decimal-prefix scan because `zend_strtod` must not inherit the
classifier's shifted-boundary integer wrapping. Explicit
string-to-int casts saturate finite overflow and return zero for infinity without
float-cast warnings; implicit integer operands additionally report leading-data
and precision-loss notices in source order. `num_compare` follows Zend's unordered
result of +1; greater-than must reverse operands, not test for a positive result.
Source: `zend_compare`, `zendi_try_get_long`, `zval_get_long_func`,
`zend_dval_to_lval_cap`, and `i_zend_is_true`. Run
`python3 tests/semantics/numeric_context.py` for keys, casts, numeric comparisons
and warning identities. Handler execution and general mixed-type comparison still
belong to later machine integration.

`05-string-operators.watsup` defines byte-wise `&`, `|`, `^`, `~` and string
increment/decrement. Numeric strings become numbers; other string increments use
right-to-left ASCII carry, with one linear traversal. PHP 8.5 deprecates every
nonnumeric string increment, and nonnumeric/empty-string decrements have distinct
notices. The returned original-value-based update is pending until its notice
handlers finish; machine integration must preserve the engine's callback mutation
and abrupt-completion behavior. Source: `increment_string`, `increment_function`,
`decrement_function` and `bitwise_*_function`. Run
`python3 tests/semantics/string_operators.py` for byte grids, mixed lengths,
carry boundaries and diagnostic identities.

`06-power-prepare.watsup` models PHP's integer exponentiation loop and libm's
zero/infinity/NaN/domain and extreme-exponent branches. It returns `POWERDONE`
for a computed answer or `POWERGENERAL` for a pending pure log/exp task, retaining
any multiplication required after integer overflow and the pending zero-base
negative-exponent deprecation. A pending task is not a successful PHP result.
`python3 tests/semantics/power_prepare.py` checks the bounded preparation milestone.
Power validation pins both PHP and its actual loaded libm/selected CPU variant;
see [power provenance](POWER-PROVENANCE.md). Preload/audit interposition is rejected
by these tests, and no platform routine computes semantic answers.

`07-fma.watsup` supplies exact single-rounding finite fused multiply-add, with
seven independent rounding/cancellation identities in
`tests/semantics/fixtures/fma.watsup`.
`08-libm-data.watsup` encodes the pinned GNU constants/tables; regenerate it with
`scripts/generate-libm-data.py`, which uses only integer operations for encoding.
`09-libm-power.watsup` resolves every `POWERGENERAL` task through the selected
contracted log/exp graph. `num_pow(pnumber, pnumber)` returns a number and pending
zero-base-negative-exponent notice. It performs no native floating arithmetic.
The graph preserves intermediate FMA versus non-FMA rounding, including separate
underflow correction; it intentionally models the selected libm approximation,
which is not necessarily correctly rounded mathematical exponentiation.
`python3 tests/semantics/power.py` checks whole-power result types/bits, special
cases, integer overflow sequencing, all log-table boundaries, subnormal/overflow
and exponent-parity thresholds, plus deterministic finite/raw-bit samples.
The LGPL-derived modules retain source attribution and local license references.

Remaining integration obligations include type coercions and string/mixed
comparisons. Passing helper tests do not establish complete PHP core coverage.
