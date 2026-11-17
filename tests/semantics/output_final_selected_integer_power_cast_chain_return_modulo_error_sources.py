#!/usr/bin/env python3
"""Selected MOD handler casts consume quiet signed64 integer powers."""
from pathlib import Path
import function_scope as scope
import output_final_selected_zero_return_modulo_error_sources as prior
from output_final_selected_integer_remainder_cast_chain_return_modulo_error_sources import modulo_line

VARIANTS = [
    ('deprecated-both-cv-pair', 'folded-pow-zero', b'(bool)(int)(0 **\n 3)', b'false', b'0'),
    ('warning-left-constant', 'folded-pow-negative', b'(float)(int)((-2) **\n 3)', b'-8.0', b'-8'),
    ('warning-right-cv-pair', 'folded-pow-one', b'(int)(bool)(2 **\n 0)', b'1', b'1'),
    ('warning-deprecated-constant-float', 'emitted-pow-zero', b"(int)(bool)(((int)'0') **\n 3)", b'0', b'0'),
    ('deprecated-both-cv-pair', 'emitted-pow-negative', b"(bool)(float)((-2) **\n ((int)'3'))", b'true', b'-8'),
    ('warning-left-constant', 'emitted-pow-min', b"(float)(int)(((int)'-2') **\n ((int)'63'))", b'-9223372036854775808.0', b"((int)'-9223372036854775808')")]
CASES = {}
for context, variant, expression, expected, expected_inner in VARIANTS:
    source = prior.CASES['native-selected-zero-return-modulo-error-' + context]
    assert source.count(b'selected_modulo_zero_return') == 2 and source.count(b'return 0;') == 1
    assert source.count(b"echo 'P';") == 1 and expression.count(b'**') == 1
    inner = expression.split(b')', 2)[2]
    witness = b"if (" + inner + b" !== " + expected_inner + b") echo 'bad-power'; "
    witness += b"if (" + expression + b" !== " + expected + b") echo 'bad-cast'; "
    name = 'native-selected-integer-power-cast-chain-return-modulo-error-' + context + '-' + variant
    CASES[name] = source.replace(b'selected_modulo_zero_return', b'selected_modulo_integer_power_cast_chain_return').replace(
        b'return 0;', b'return ' + expression + b';').replace(b"echo 'P';", witness + b"echo 'P';")


if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-integer-power-cast-chain-return-modulo-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
