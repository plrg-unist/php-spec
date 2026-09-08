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

Remaining arithmetic obligations include context-dependent coercions,
decimal formatting and power.
The passing first milestone does not establish complete arithmetic or core PHP.
