#!/usr/bin/env python3
"""Exact integral float complements preserve selected nested return casts."""
from pathlib import Path
import function_scope as scope
import output_final_selected_zero_return_modulo_error_sources as prior

VARIANTS = [
    ('warning-left-constant', 'folded-one', b'~1.0', b'-2', b'-2.0'),
    ('deprecated-both-cv-pair', 'folded-negzero', b'~-0.0', b'-1', b'-1.0'),
    ('warning-right-cv-pair', 'emitted-one', b"~(float)'1'", b'-2', b'-2.0'),
    ('warning-deprecated-constant-float', 'emitted-negative', b"~(-(float)'1')", b'0', b'0.0'),
    ('warning-left-constant', 'folded-min', b'~(-9223372036854775808.0)', b'9223372036854775807', b'9223372036854775808.0'),
    ('deprecated-both-cv-pair', 'folded-near-max', b'~9223372036854774784.0', b'-9223372036854774785', b'-9223372036854774784.0'),
    ('warning-right-cv-pair', 'emitted-zero', b"~(float)'0'", b'-1', b'-1.0'),
    ('warning-deprecated-constant-float', 'folded-negative', b'~-1.0', b'0', b'0.0')]
CASES = {}
for context, variant, inner, inner_expected, expected in VARIANTS:
    source = prior.CASES['native-selected-zero-return-modulo-error-' + context]
    expression = b'(float)(int)(' + inner + b')'
    witness = b"if ((" + inner + b") !== " + inner_expected + b") echo 'bad-bitnot'; "
    witness += b"if (" + expression + b" !== " + expected + b") echo 'bad-cast'; "
    name = 'native-selected-integral-float-bitnot-cast-chain-return-modulo-error-' + context + '-' + variant
    CASES[name] = source.replace(b'selected_modulo_zero_return', b'selected_modulo_integral_float_bitnot_return').replace(
        b'return 0;', b'return ' + expression + b';').replace(b"echo 'P';", witness + b"echo 'P';")


if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-integral-float-bitnot-cast-chain-return-modulo-error',
                                    Path(__file__), publish=False, model_seconds=90) else 1)
