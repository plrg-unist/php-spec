#!/usr/bin/env python3
"""Selected MOD handler casts consume quiet signed64 integer shifts."""
from pathlib import Path
import function_scope as scope
import output_final_selected_zero_return_modulo_error_sources as prior
from output_final_selected_integer_remainder_cast_chain_return_modulo_error_sources import modulo_line

VARIANTS = [
    ('deprecated-both-cv-pair', 'folded-shl-zero', b'(bool)(int)(1 <<\n 64)', b'false'),
    ('warning-left-constant', 'folded-shr-negative', b'(float)(int)((-5) >>\n 1)', b'-3.0'),
    ('warning-right-cv-pair', 'folded-shl-min', b'(float)(int)(1 <<\n 63)', b'-9223372036854775808.0'),
    ('warning-deprecated-constant-float', 'emitted-shr-zero', b"(int)(bool)((int)'5' >>\n 64)", b'0'),
    ('deprecated-both-cv-pair', 'emitted-shr-negative', b"(bool)(float)((-5) >>\n (int)'64')", b'true'),
    ('warning-left-constant', 'emitted-shl-min', b"(float)(int)((int)'1' <<\n (int)'63')", b'-9223372036854775808.0')]
CASES = {}
for context, variant, expression, expected in VARIANTS:
    source = prior.CASES['native-selected-zero-return-modulo-error-' + context]
    assert source.count(b'selected_modulo_zero_return') == 2 and source.count(b'return 0;') == 1
    assert source.count(b"echo 'P';") == 1
    witness = b"if (" + expression + b" !== " + expected + b") echo 'bad-cast'; "
    name = 'native-selected-integer-shift-cast-chain-return-modulo-error-' + context + '-' + variant
    CASES[name] = source.replace(b'selected_modulo_zero_return', b'selected_modulo_integer_shift_cast_chain_return').replace(
        b'return 0;', b'return ' + expression + b';').replace(b"echo 'P';", witness + b"echo 'P';")


if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-integer-shift-cast-chain-return-modulo-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
