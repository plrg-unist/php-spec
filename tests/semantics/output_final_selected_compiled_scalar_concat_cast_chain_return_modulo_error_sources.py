#!/usr/bin/env python3
"""Quiet compiler-folded scalar CONCAT preserves selected handler return casts."""
from pathlib import Path
import function_scope as scope
import output_final_selected_zero_return_modulo_error_sources as prior
from output_final_selected_integer_remainder_cast_chain_return_modulo_error_sources import modulo_line

VARIANTS = [
    ('warning-left-constant', 'negative-fraction', b"(float)(int)(-1.5 . '')", b'-1.0', b"'-1.5'"),
    ('warning-right-cv-pair', 'positive-both', b"(bool)(float)(+1.5 .\n 0.0)", b'true', b"'1.50'"),
    ('deprecated-both-cv-pair', 'negative-zero-right', b"(int)(bool)('' .\n -0.0)", b'1', b"'-0'"),
    ('warning-left-constant', 'negative-integer', b"(float)(int)((-12) .\n '')", b'-12.0', b"'-12'"),
    ('warning-deprecated-constant-float', 'arithmetic', b"(bool)(int)((1.5 +\n 2.5) .\n '')", b'true', b"'4'"),
    ('deprecated-both-cv-pair', 'nested-zero', b"(bool)(int)((-0.0 . '') .\n '0')", b'false', b"'-00'"),
    ('warning-deprecated-constant-float', 'keyword-suffix', b"(bool)(int)((-1.5 . true) .\n null)", b'true', b"'-1.51'"),
    ('deprecated-both-cv-pair', 'negative-infinity', b"(bool)(int)((-1e999) .\n '')", b'false', b"'-INF'")]
CASES = {}


def function_name(variant):
    return ('selected_modulo_signed_float_concat_assessment' if variant == 'negative-fraction'
            else 'selected_modulo_compiled_scalar_concat_cast_chain_return')


for context, variant, expression, expected, inner_expected in VARIANTS:
    source = prior.CASES['native-selected-zero-return-modulo-error-' + context]
    inner = expression.split(b')', 2)[2]
    witness = b"if (" + inner + b" !== " + inner_expected + b") echo 'bad-string'; "
    witness += b"if (" + expression + b" !== " + expected + b") echo 'bad-cast'; "
    CASES['native-selected-compiled-scalar-concat-cast-chain-return-modulo-error-' + context + '-' + variant] = source.replace(
        b'selected_modulo_zero_return', function_name(variant).encode()).replace(
        b'return 0;', b'return ' + expression + b';').replace(b"echo 'P';", witness + b"echo 'P';")

PRECISION_CASE = next(iter(CASES.values())).replace(
    b'selected_modulo_signed_float_concat_assessment', b'selected_modulo_compiled_scalar_concat_precision_return').replace(
    b"!== '-1.5'", b"!== '-2'").replace(b'!== -1.0', b'!== -2.0')


if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-compiled-scalar-concat-cast-chain-return-modulo-error',
                                    Path(__file__), publish=False, model_seconds=90) else 1)
