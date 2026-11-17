#!/usr/bin/env python3
"""Selected MOD handler certificates follow multiline terminal compiler lines."""
from pathlib import Path
import function_scope as scope
import output_final_selected_zero_return_modulo_error_sources as prior

VARIANTS = [
    ('deprecated-both-cv-pair', 'folded-and-zero', b'(bool)(int)(6 &\n 1)', b'false'),
    ('warning-left-constant', 'folded-negative-or', b'(float)(int)(-((-2) |\n 1))', b'1.0'),
    ('warning-right-cv-pair', 'folded-xor-one', b'(int)(bool)((-1) ^\n (-2))', b'1'),
    ('warning-deprecated-constant-float', 'emitted-positive-and', b"(int)(bool)(+((int)'2' &\n 1))", b'0'),
    ('deprecated-both-cv-pair', 'emitted-not-or', b"(bool)(float)(~(0 |\n (int)'1'))", b'true'),
    ('warning-left-constant', 'emitted-not-nested-xor', b"(int)(bool)(!((int)'3' ^\n ((int)'1' |\n (int)'2')))", b'1')]
CASES = {}
for context, variant, expression, expected in VARIANTS:
    source = prior.CASES['native-selected-zero-return-modulo-error-' + context]
    assert source.count(b'selected_modulo_zero_return') == 2 and source.count(b'return 0;') == 1
    assert source.count(b"echo 'P';") == 1
    witness = b"if (" + expression + b" !== " + expected + b") echo 'bad-cast'; "
    name = 'native-selected-terminal-line-bitwise-cast-chain-return-modulo-error-' + context + '-' + variant
    CASES[name] = source.replace(b'selected_modulo_zero_return', b'selected_modulo_terminal_line_bitwise_cast_chain_return').replace(
        b'return 0;', b'return ' + expression + b';').replace(b"echo 'P';", witness + b"echo 'P';")

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-terminal-line-bitwise-cast-chain-return-modulo-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
