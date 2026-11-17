#!/usr/bin/env python3
"""Selected MOD handler casts consume quiet floating results over primitives."""
from pathlib import Path
import function_scope as scope
import output_final_selected_zero_return_modulo_error_sources as prior
from output_final_selected_integer_remainder_cast_chain_return_modulo_error_sources import modulo_line

VARIANTS = [
    ('warning-left-constant', 'folded-float-bool-add-two', b'(float)(int)(1.0 +\n true)', b'2.0', b'2.0'),
    ('deprecated-both-cv-pair', 'emitted-float-string-subtract-zero', b"(bool)(float)(1.0 -\n ((float)'1'))", b'false', b'0.0'),
    ('warning-right-cv-pair', 'folded-float-string-multiply-three', b"(int)(bool)(1.5 *\n '2')", b'1', b'3.0'),
    ('deprecated-both-cv-pair', 'folded-bool-integer-divide-half', b'(bool)(float)(true /\n 2)', b'true', b'0.5'),
    ('warning-deprecated-constant-float', 'emitted-float-power-one', b"(bool)(int)(((float)'1') **\n 3)", b'true', b'1.0'),
    ('warning-left-constant', 'emitted-integer-bool-add-overflow', b"(int)(bool)(((int)'9223372036854775807') +\n true)", b'1', b'9223372036854775808.0')]
CASES = {}
for context, variant, expression, expected, expected_inner in VARIANTS:
    source = prior.CASES['native-selected-zero-return-modulo-error-' + context]
    assert source.count(b'selected_modulo_zero_return') == 2 and source.count(b'return 0;') == 1
    assert source.count(b"echo 'P';") == 1
    inner = expression.split(b')', 2)[2]
    witness = b"if (" + inner + b" !== " + expected_inner + b") echo 'bad-float'; "
    witness += b"if (" + expression + b" !== " + expected + b") echo 'bad-cast'; "
    name = 'native-selected-primitive-float-cast-chain-return-modulo-error-' + context + '-' + variant
    CASES[name] = source.replace(b'selected_modulo_zero_return', b'selected_modulo_primitive_float_cast_chain_return').replace(
        b'return 0;', b'return ' + expression + b';').replace(b"echo 'P';", witness + b"echo 'P';")


if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-primitive-float-cast-chain-return-modulo-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
