#!/usr/bin/env python3
"""Selected MOD handler casts consume quiet exact signed64 integer quotients."""
from pathlib import Path
import function_scope as scope
import output_final_selected_zero_return_modulo_error_sources as prior

VARIANTS = [
    ('deprecated-both-cv-pair', 'folded-div-zero', b'(bool)(int)(0 /\n 2)', b'false'),
    ('warning-left-constant', 'folded-div-negative', b'(float)(int)((-4) /\n 2)', b'-2.0'),
    ('warning-right-cv-pair', 'folded-div-one', b'(int)(bool)(6 /\n 3)', b'1'),
    ('warning-deprecated-constant-float', 'emitted-div-zero', b"(int)(bool)((int)'0' /\n 2)", b'0'),
    ('deprecated-both-cv-pair', 'emitted-div-negative', b"(bool)(float)(4 /\n (int)'-2')", b'true'),
    ('warning-left-constant', 'emitted-div-one', b"(int)(bool)((int)'6' /\n (int)'3')", b'1')]
CASES = {}
for context, variant, expression, expected in VARIANTS:
    source = prior.CASES['native-selected-zero-return-modulo-error-' + context]
    assert source.count(b'selected_modulo_zero_return') == 2 and source.count(b'return 0;') == 1
    assert source.count(b"echo 'P';") == 1
    witness = b"if (" + expression + b" !== " + expected + b") echo 'bad-cast'; "
    name = 'native-selected-integer-division-cast-chain-return-modulo-error-' + context + '-' + variant
    CASES[name] = source.replace(b'selected_modulo_zero_return', b'selected_modulo_integer_division_cast_chain_return').replace(
        b'return 0;', b'return ' + expression + b';').replace(b"echo 'P';", witness + b"echo 'P';")

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-integer-division-cast-chain-return-modulo-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
