#!/usr/bin/env python3
"""Positive infinity is a quiet raw FLOAT parser-CONCAT boundary."""
from pathlib import Path
import function_scope as scope
import output_final_selected_zero_return_modulo_error_sources as prior
from output_final_selected_integer_remainder_cast_chain_return_modulo_error_sources import modulo_line

VARIANTS = [
    ('warning-left-constant', 'right-empty-infinity', b"(float)(int)(1e999 . '')", b'0.0', b"'INF'"),
    ('warning-right-cv-pair', 'left-empty-infinity', b"(int)(bool)('' .\n 1e999)", b'1', b"'INF'"),
    ('deprecated-both-cv-pair', 'infinity-false', b"(bool)(float)(1e999 .\n '')", b'false', b"'INF'"),
    ('warning-deprecated-constant-float', 'infinity-finite', b"(int)(bool)(1e999 .\n 1.5)", b'1', b"'INF1.5'")]
CASES = {}


def function_name(variant):
    return ('selected_modulo_parser_infinite_float_concat_assessment' if variant == 'right-empty-infinity'
            else 'selected_modulo_parser_infinite_float_concat_cast_chain_return')


for context, variant, expression, expected, inner_expected in VARIANTS:
    source = prior.CASES['native-selected-zero-return-modulo-error-' + context]
    inner = expression.split(b')', 2)[2]
    witness = b"if (" + inner + b" !== " + inner_expected + b") echo 'bad-string'; "
    witness += b"if (" + expression + b" !== " + expected + b") echo 'bad-cast'; "
    CASES['native-selected-parser-infinite-float-concat-cast-chain-return-modulo-error-' + context + '-' + variant] = source.replace(
        b'selected_modulo_zero_return', function_name(variant).encode()).replace(
        b'return 0;', b'return ' + expression + b';').replace(b"echo 'P';", witness + b"echo 'P';")

PRECISION_CASE = next(iter(CASES.values())).replace(
    b'selected_modulo_parser_infinite_float_concat_assessment', b'selected_modulo_parser_infinite_float_concat_precision_return').replace(
    b"!== 'INF'", b"!== 'I'")


if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-parser-infinite-float-concat-cast-chain-return-modulo-error',
                                    Path(__file__), publish=False, model_seconds=90) else 1)
