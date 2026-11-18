#!/usr/bin/env python3
"""Quiet primitive unary signs retain selected nested scalar return casts."""
from pathlib import Path
import function_scope as scope
import output_final_selected_zero_return_modulo_error_sources as prior
from output_final_selected_integer_remainder_cast_chain_return_modulo_error_sources import modulo_line

VARIANTS = [
    ('warning-left-constant', 'numeric-string', b"(float)(int)(+'12')", b'12.0', b"(+'12')", b'12'),
    ('deprecated-both-cv-pair', 'minus-true', b'(bool)(float)(-true)', b'true', b'(-true)', b'-1'),
    ('warning-right-cv-pair', 'plus-false', b'(int)(bool)(+false)', b'0', b'(+false)', b'0'),
    ('warning-deprecated-constant-float', 'minus-null', b'(float)(int)(-null)', b'0.0', b'(-null)', b'0'),
    ('warning-left-constant', 'fraction-string', b"(float)(int)(-'1.5')", b'-1.0', b"(-'1.5')", b'-1.5'),
    ('deprecated-both-cv-pair', 'exponent-zero', b"(bool)(float)(+'0e0')", b'false', b"(+'0e0')", b'0.0'),
    ('warning-right-cv-pair', 'emitted-not-float', b'(float)(int)(+(!0.0))', b'1.0', b'(+(!0.0))', b'1'),
    ('warning-deprecated-constant-float', 'parser-concat', b"(int)(bool)(-('0' . '0'))", b'0', b"(-('0' . '0'))", b'0')]
CASES = {}


def function_name(variant):
    return ('selected_modulo_primitive_unary_sign_assessment' if variant == 'numeric-string'
            else 'selected_modulo_primitive_unary_sign_cast_chain_return')


for context, variant, expression, expected, inner, inner_expected in VARIANTS:
    source = prior.CASES['native-selected-zero-return-modulo-error-' + context]
    witness = b"if (" + inner + b" !== " + inner_expected + b") echo 'bad-unary'; "
    witness += b"if (" + expression + b" !== " + expected + b") echo 'bad-cast'; "
    name = 'native-selected-primitive-unary-sign-cast-chain-return-modulo-error-' + context + '-' + variant
    CASES[name] = source.replace(b'selected_modulo_zero_return', function_name(variant).encode()).replace(
        b'return 0;', b'return ' + expression + b';').replace(b"echo 'P';", witness + b"echo 'P';")


if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-primitive-unary-sign-cast-chain-return-modulo-error',
                                    Path(__file__), publish=False, model_seconds=90) else 1)
