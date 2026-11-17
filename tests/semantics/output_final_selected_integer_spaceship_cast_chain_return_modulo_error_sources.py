#!/usr/bin/env python3
"""Selected MOD handler casts consume normalized signed64 integer comparisons."""
from pathlib import Path
import function_scope as scope
import output_final_selected_zero_return_modulo_error_sources as prior
from output_final_selected_integer_remainder_cast_chain_return_modulo_error_sources import modulo_line

VARIANTS = [
    ('deprecated-both-cv-pair', 'folded-cmp-zero', b'(bool)(int)(7 <=>\n 7)', b'false', b'0'),
    ('warning-left-constant', 'folded-cmp-negative', b'(float)(int)((-5) <=>\n 5)', b'-1.0', b'-1'),
    ('warning-right-cv-pair', 'folded-cmp-one', b'(int)(bool)(5 <=>\n (-5))', b'1', b'1'),
    ('warning-deprecated-constant-float', 'emitted-cmp-zero', b"(int)(bool)(((int)'7') <=>\n 7)", b'0', b'0'),
    ('deprecated-both-cv-pair', 'emitted-cmp-one', b"(bool)(float)((-5) <=>\n ((int)'-6'))", b'true', b'1'),
    ('warning-left-constant', 'emitted-cmp-min-max', b"(float)(int)(((int)'-9223372036854775808') <=>\n ((int)'9223372036854775807'))", b'-1.0', b'-1')]
CASES = {}
for context, variant, expression, expected, expected_inner in VARIANTS:
    source = prior.CASES['native-selected-zero-return-modulo-error-' + context]
    assert source.count(b'selected_modulo_zero_return') == 2 and source.count(b'return 0;') == 1
    assert source.count(b"echo 'P';") == 1 and expression.count(b'<=>') == 1
    inner = expression.split(b')', 2)[2]
    witness = b"if (" + inner + b" !== " + expected_inner + b") echo 'bad-order'; "
    witness += b"if (" + expression + b" !== " + expected + b") echo 'bad-cast'; "
    name = 'native-selected-integer-spaceship-cast-chain-return-modulo-error-' + context + '-' + variant
    CASES[name] = source.replace(b'selected_modulo_zero_return', b'selected_modulo_integer_spaceship_cast_chain_return').replace(
        b'return 0;', b'return ' + expression + b';').replace(b"echo 'P';", witness + b"echo 'P';")


if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-integer-spaceship-cast-chain-return-modulo-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
