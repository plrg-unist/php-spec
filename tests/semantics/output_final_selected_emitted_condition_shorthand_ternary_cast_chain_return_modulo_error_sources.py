#!/usr/bin/env python3
"""Quiet shorthand ternaries retain raw values through nested return casts."""
from pathlib import Path
import function_scope as scope
import output_final_selected_zero_return_modulo_error_sources as prior
from output_final_selected_integer_remainder_cast_chain_return_modulo_error_sources import modulo_line

VARIANTS = [
    ('warning-left-constant', 'truthy-int', b"(int)'1' ?: UNDEFINED_SHORTHAND_FALSE", b'1', b'1.0'),
    ('deprecated-both-cv-pair', 'truthy-float', b'(float)1 ?: UNDEFINED_SHORTHAND_FALSE', b'1.0', b'1.0'),
    ('warning-right-cv-pair', 'truthy-bool', b'(bool)1 ?: UNDEFINED_SHORTHAND_FALSE', b'true', b'1.0'),
    ('warning-deprecated-constant-float', 'false-int', b"(int)'0' ?: 0", b'0', b'0.0'),
    ('warning-left-constant', 'false-string', b"(float)0 ?: '1'", b"'1'", b'1.0'),
    ('deprecated-both-cv-pair', 'false-null', b'(bool)0 ?: null', b'null', b'0.0'),
    ('warning-right-cv-pair', 'false-cast', b"(float)0 ?: (int)'1'", b'1', b'1.0'),
    ('warning-deprecated-constant-float', 'truthy-negative', b"(int)'-1' ?: UNDEFINED_SHORTHAND_FALSE", b'-1', b'-1.0')]
CASES = {}
for context, variant, inner, inner_expected, expected in VARIANTS:
    source = prior.CASES['native-selected-zero-return-modulo-error-' + context]
    expression = b'(float)(int)(' + inner + b')'
    witness = b"if ((" + inner + b") !== " + inner_expected + b") echo 'bad-shorthand'; "
    witness += b"if (" + expression + b" !== " + expected + b") echo 'bad-cast'; "
    name = 'native-selected-emitted-condition-shorthand-ternary-cast-chain-return-modulo-error-' + context + '-' + variant
    CASES[name] = source.replace(b'selected_modulo_zero_return', b'selected_modulo_emitted_condition_shorthand_ternary_return').replace(
        b'return 0;', b'return ' + expression + b';').replace(b"echo 'P';", witness + b"echo 'P';")


if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-emitted-condition-shorthand-ternary-cast-chain-return-modulo-error',
                                    Path(__file__), publish=False, model_seconds=90) else 1)
