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
operations when the evaluator integrates them. Remaining arithmetic obligations
include integer bitwise/shift/remainder and conversion rules, numeric-string
classification, context-dependent coercions, decimal parsing/formatting and power.
The passing first milestone does not establish complete arithmetic or core PHP.
