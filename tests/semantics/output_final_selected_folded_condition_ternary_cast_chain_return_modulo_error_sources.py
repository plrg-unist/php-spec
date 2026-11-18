#!/usr/bin/env python3
"""Folded ternary conditions preserve selected values through return casts."""
from pathlib import Path
import function_scope as scope
import output_final_selected_zero_return_modulo_error_sources as prior
from output_final_selected_integer_remainder_cast_chain_return_modulo_error_sources import modulo_line

VARIANTS = [
    ('warning-left-constant', 'full-true-bool', b"true ? (int)'1' : UNDEFINED_TERNARY_FALSE", b'1', b'1.0'),
    ('deprecated-both-cv-pair', 'full-false-bool', b'false ? UNDEFINED_TERNARY_TRUE : 0', b'0', b'0.0'),
    ('warning-right-cv-pair', 'full-false-string', b"'0' ? UNDEFINED_TERNARY_TRUE : '1'", b"'1'", b'1.0'),
    ('warning-deprecated-constant-float', 'full-true-float', b'1.0 ? false : UNDEFINED_TERNARY_FALSE', b'false', b'0.0'),
    ('warning-left-constant', 'shorthand-true-int', b'1 ?: UNDEFINED_SHORTHAND_FALSE', b'1', b'1.0'),
    ('deprecated-both-cv-pair', 'shorthand-false-int', b"0 ?: (int)'1'", b'1', b'1.0'),
    ('warning-right-cv-pair', 'shorthand-true-string', b"'1' ?: UNDEFINED_SHORTHAND_FALSE", b"'1'", b'1.0'),
    ('warning-deprecated-constant-float', 'shorthand-false-null', b'null ?: false', b'false', b'0.0')]
CASES = {}
for context, variant, inner, inner_expected, expected in VARIANTS:
    source = prior.CASES['native-selected-zero-return-modulo-error-' + context]
    expression = b'(float)(int)(' + inner + b')'
    witness = b"if ((" + inner + b") !== " + inner_expected + b") echo 'bad-ternary'; "
    witness += b"if (" + expression + b" !== " + expected + b") echo 'bad-cast'; "
    name = 'native-selected-folded-condition-ternary-cast-chain-return-modulo-error-' + context + '-' + variant
    CASES[name] = source.replace(b'selected_modulo_zero_return', b'selected_modulo_folded_condition_ternary_return').replace(
        b'return 0;', b'return ' + expression + b';').replace(b"echo 'P';", witness + b"echo 'P';")


if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-folded-condition-ternary-cast-chain-return-modulo-error',
                                    Path(__file__), publish=False, model_seconds=90) else 1)
