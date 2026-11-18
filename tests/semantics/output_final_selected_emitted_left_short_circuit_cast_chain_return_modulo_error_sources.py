#!/usr/bin/env python3
"""Quiet emitted-left short circuits retain selected nested return casts."""
from pathlib import Path
import function_scope as scope
import output_final_selected_zero_return_modulo_error_sources as prior
from output_final_selected_integer_remainder_cast_chain_return_modulo_error_sources import modulo_line

VARIANTS = [
    ('warning-left-constant', 'and-skip', b'(bool)0.0 && UNDEFINED_EMITTED_SHORT_RHS', b'false', b'0.0'),
    ('deprecated-both-cv-pair', 'or-skip', b'!0.0 || UNDEFINED_EMITTED_SHORT_RHS', b'true', b'1.0'),
    ('warning-right-cv-pair', 'logical-and-skip', b'(bool)0.0 and UNDEFINED_EMITTED_SHORT_RHS', b'false', b'0.0'),
    ('warning-deprecated-constant-float', 'logical-or-skip', b'!0.0 or UNDEFINED_EMITTED_SHORT_RHS', b'true', b'1.0'),
    ('warning-left-constant', 'and-right', b'!0.0 && false', b'false', b'0.0'),
    ('deprecated-both-cv-pair', 'or-right', b'(bool)0.0 || true', b'true', b'1.0'),
    ('warning-right-cv-pair', 'and-emitted-right', b'!0.0 && (bool)0.0', b'false', b'0.0'),
    ('warning-deprecated-constant-float', 'or-emitted-right', b'(bool)0.0 || !0.0', b'true', b'1.0')]
CASES = {}
for context, variant, inner, inner_expected, expected in VARIANTS:
    source = prior.CASES['native-selected-zero-return-modulo-error-' + context]
    expression = b'(float)(int)(' + inner + b')'
    witness = b"if ((" + inner + b") !== " + inner_expected + b") echo 'bad-short'; "
    witness += b"if (" + expression + b" !== " + expected + b") echo 'bad-cast'; "
    name = 'native-selected-emitted-left-short-circuit-cast-chain-return-modulo-error-' + context + '-' + variant
    CASES[name] = source.replace(b'selected_modulo_zero_return', b'selected_modulo_emitted_left_short_circuit_return').replace(
        b'return 0;', b'return ' + expression + b';').replace(b"echo 'P';", witness + b"echo 'P';")


if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-emitted-left-short-circuit-cast-chain-return-modulo-error',
                                    Path(__file__), publish=False, model_seconds=90) else 1)
