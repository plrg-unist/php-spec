#!/usr/bin/env python3
"""Selected MOD handler casts consume quiet integer results over primitives."""
from pathlib import Path
import function_scope as scope
import output_final_selected_zero_return_modulo_error_sources as prior
from output_final_selected_integer_remainder_cast_chain_return_modulo_error_sources import modulo_line

VARIANTS = [
    ('deprecated-both-cv-pair', 'folded-bool-null-add-one', b'(bool)(int)(true +\n null)', b'true', b'1'),
    ('warning-left-constant', 'emitted-string-bool-subtract-two', b"(float)(int)('3' -\n ((bool)1))", b'2.0', b'2'),
    ('deprecated-both-cv-pair', 'folded-bool-string-multiply-zero', b"(bool)(float)(false *\n '2')", b'false', b'0'),
    ('warning-right-cv-pair', 'emitted-string-bool-divide-six', b"(int)(bool)('6' /\n ((bool)1))", b'1', b'6'),
    ('warning-left-constant', 'folded-float-string-modulo-one', b"(float)(int)(5.0 %\n '2')", b'1.0', b'1'),
    ('warning-deprecated-constant-float', 'emitted-string-bool-left-shift-six', b"(int)(bool)('3' <<\n ((bool)1))", b'1', b'6'),
    ('warning-left-constant', 'folded-string-float-right-shift-four', b"(int)(bool)('8' >>\n 1.0)", b'1', b'4'),
    ('warning-deprecated-constant-float', 'emitted-mixed-bitwise-three', b"(bool)(float)(('7' & ((bool)1)) |\n (null ^ 2))", b'true', b'3'),
    ('deprecated-both-cv-pair', 'folded-mixed-power-spaceship-zero', b"(bool)(int)(('2' ** true) <=>\n (false + 2))", b'false', b'0')]
CASES = {}
for context, variant, expression, expected, expected_inner in VARIANTS:
    source = prior.CASES['native-selected-zero-return-modulo-error-' + context]
    assert source.count(b'selected_modulo_zero_return') == 2 and source.count(b'return 0;') == 1
    assert source.count(b"echo 'P';") == 1
    inner = expression.split(b')', 2)[2]
    witness = b"if (" + inner + b" !== " + expected_inner + b") echo 'bad-integer'; "
    witness += b"if (" + expression + b" !== " + expected + b") echo 'bad-cast'; "
    name = 'native-selected-primitive-integer-cast-chain-return-modulo-error-' + context + '-' + variant
    CASES[name] = source.replace(b'selected_modulo_zero_return', b'selected_modulo_primitive_integer_cast_chain_return').replace(
        b'return 0;', b'return ' + expression + b';').replace(b"echo 'P';", witness + b"echo 'P';")


if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-primitive-integer-cast-chain-return-modulo-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
