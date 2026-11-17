#!/usr/bin/env python3
"""Selected MOD handlers retain recursively certified quiet numeric signs."""
from pathlib import Path
import function_scope as scope
import output_final_selected_zero_return_modulo_error_sources as prior

VARIANTS = [
    ('warning-left-constant', 'folded-int-double', b'(bool)(int)(-(-7))', b'true'),
    ('deprecated-both-cv-pair', 'folded-float-double', b'(bool)(float)(-(-0.0))', b'false'),
    ('warning-right-cv-pair', 'emitted-int-cast', b"(int)(bool)(-(int)'7')", b'1'),
    ('warning-deprecated-constant-float', 'emitted-float-cast', b"(float)(int)(+(float)'0.5')", b'0.0'),
    ('warning-left-constant', 'emitted-not-int', b'(bool)(int)(-(int)(!false))', b'true'),
    ('warning-right-cv-pair', 'emitted-float-zero', b"(int)(bool)(+(float)'-0')", b'0')]
CASES = {}
for context, variant, expression, expected in VARIANTS:
    source = prior.CASES['native-selected-zero-return-modulo-error-' + context]
    assert source.count(b'selected_modulo_zero_return') == 2 and source.count(b'return 0;') == 1
    assert source.count(b"echo 'P';") == 1
    witness = b"if (" + expression + b" !== " + expected + b") echo 'bad-cast'; "
    name = 'native-selected-recursive-numeric-sign-cast-chain-return-modulo-error-' + context + '-' + variant
    CASES[name] = source.replace(b'selected_modulo_zero_return', b'selected_modulo_recursive_numeric_sign_cast_chain_return').replace(
        b'return 0;', b'return ' + expression + b';').replace(b"echo 'P';", witness + b"echo 'P';")

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-recursive-numeric-sign-cast-chain-return-modulo-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
