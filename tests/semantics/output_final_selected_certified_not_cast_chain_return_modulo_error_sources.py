#!/usr/bin/env python3
"""Selected MOD handlers certify quiet NOT children from their own compiler facts."""
from pathlib import Path
import function_scope as scope
import output_final_selected_zero_return_modulo_error_sources as prior

VARIANTS = [
    ('warning-left-constant', 'keyword-false', b'(bool)(int)(!false)', b'true'),
    ('deprecated-both-cv-pair', 'keyword-null', b'(bool)(float)(!null)', b'true'),
    ('warning-right-cv-pair', 'string-zero', b"(int)(bool)(!'0')", b'1'),
    ('warning-deprecated-constant-float', 'string-truthy', b"(float)(int)(!'x')", b'0.0'),
    ('warning-left-constant', 'emitted-int', b"(bool)(int)(!(int)'0')", b'true'),
    ('deprecated-both-cv-pair', 'folded-nested', b'(bool)(float)(!!false)', b'false'),
    ('warning-right-cv-pair', 'emitted-nested', b"(int)(bool)(!!(int)'x')", b'0')]
CASES = {}
for context, variant, expression, expected in VARIANTS:
    source = prior.CASES['native-selected-zero-return-modulo-error-' + context]
    assert source.count(b'selected_modulo_zero_return') == 2 and source.count(b'return 0;') == 1
    assert source.count(b"echo 'P';") == 1
    witness = b"if (" + expression + b" !== " + expected + b") echo 'bad-cast'; "
    name = 'native-selected-certified-not-cast-chain-return-modulo-error-' + context + '-' + variant
    CASES[name] = source.replace(b'selected_modulo_zero_return', b'selected_modulo_certified_not_cast_chain_return').replace(
        b'return 0;', b'return ' + expression + b';').replace(b"echo 'P';", witness + b"echo 'P';")

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-certified-not-cast-chain-return-modulo-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
