#!/usr/bin/env python3
"""Quiet full ternaries retain selected values through nested return casts."""
from pathlib import Path
import function_scope as scope
import output_final_selected_zero_return_modulo_error_sources as prior
from output_final_selected_integer_remainder_cast_chain_return_modulo_error_sources import modulo_line

VARIANTS = [
    ('warning-left-constant', 'false-constant', b'(bool)0.0 ? UNDEFINED_TERNARY_TRUE : 0', b'0', b'0.0'),
    ('deprecated-both-cv-pair', 'true-constant', b'!0.0 ? 1 : UNDEFINED_TERNARY_FALSE', b'1', b'1.0'),
    ('warning-right-cv-pair', 'false-float', b'(bool)0.0 ? UNDEFINED_TERNARY_TRUE : 0.0', b'0.0', b'0.0'),
    ('warning-deprecated-constant-float', 'true-bool', b'!0.0 ? true : UNDEFINED_TERNARY_FALSE', b'true', b'1.0'),
    ('warning-left-constant', 'false-cast', b'(bool)0.0 ? 1 : (int)0.0', b'0', b'0.0'),
    ('deprecated-both-cv-pair', 'true-cast', b'!0.0 ? (bool)1.0 : 0', b'true', b'1.0'),
    ('warning-right-cv-pair', 'false-null', b'(bool)0.0 ? true : null', b'null', b'0.0'),
    ('warning-deprecated-constant-float', 'true-string', b"!0.0 ? '1' : false", b"'1'", b'1.0')]
CASES = {}
for context, variant, inner, inner_expected, expected in VARIANTS:
    source = prior.CASES['native-selected-zero-return-modulo-error-' + context]
    expression = b'(float)(int)(' + inner + b')'
    witness = b"if ((" + inner + b") !== " + inner_expected + b") echo 'bad-ternary'; "
    witness += b"if (" + expression + b" !== " + expected + b") echo 'bad-cast'; "
    name = 'native-selected-emitted-condition-full-ternary-cast-chain-return-modulo-error-' + context + '-' + variant
    CASES[name] = source.replace(b'selected_modulo_zero_return', b'selected_modulo_emitted_condition_full_ternary_return').replace(
        b'return 0;', b'return ' + expression + b';').replace(b"echo 'P';", witness + b"echo 'P';")


if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-emitted-condition-full-ternary-cast-chain-return-modulo-error',
                                    Path(__file__), publish=False, model_seconds=90) else 1)
