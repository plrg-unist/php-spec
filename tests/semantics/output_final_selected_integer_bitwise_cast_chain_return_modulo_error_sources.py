#!/usr/bin/env python3
"""Selected MOD handlers retain certified signed64 integer bitwise results."""
from pathlib import Path
import function_scope as scope
import output_final_selected_zero_return_modulo_error_sources as prior

VARIANTS = [
    ('deprecated-both-cv-pair', 'folded-and-zero', b'(bool)(int)(6 & 1)', b'false'),
    ('warning-left-constant', 'folded-or-negative', b'(float)(int)((-2) | 1)', b'-1.0'),
    ('warning-right-cv-pair', 'folded-xor-one', b'(int)(bool)((-1) ^ (-2))', b'1'),
    ('warning-deprecated-constant-float', 'emitted-and-zero', b"(int)(bool)((int)'2' & 1)", b'0'),
    ('deprecated-both-cv-pair', 'emitted-or-negative', b"(bool)(float)((-2) | (int)'1')", b'true'),
    ('warning-left-constant', 'emitted-xor-zero', b"(int)(bool)((int)'3' ^ (int)'3')", b'0')]
CASES = {}
for context, variant, expression, expected in VARIANTS:
    source = prior.CASES['native-selected-zero-return-modulo-error-' + context]
    assert source.count(b'selected_modulo_zero_return') == 2 and source.count(b'return 0;') == 1
    assert source.count(b"echo 'P';") == 1
    witness = b"if (" + expression + b" !== " + expected + b") echo 'bad-cast'; "
    name = 'native-selected-integer-bitwise-cast-chain-return-modulo-error-' + context + '-' + variant
    CASES[name] = source.replace(b'selected_modulo_zero_return', b'selected_modulo_integer_bitwise_cast_chain_return').replace(
        b'return 0;', b'return ' + expression + b';').replace(b"echo 'P';", witness + b"echo 'P';")

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-integer-bitwise-cast-chain-return-modulo-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
