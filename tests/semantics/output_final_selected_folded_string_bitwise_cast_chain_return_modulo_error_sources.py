#!/usr/bin/env python3
"""Selected MOD handler casts consume authenticated folded STRING bitwise trees."""
from pathlib import Path
import function_scope as scope
import output_final_selected_zero_return_modulo_error_sources as prior
from output_final_selected_integer_remainder_cast_chain_return_modulo_error_sources import modulo_line

VARIANTS = [
    ('warning-left-constant', 'single-and-one', b"(float)(int)('3' &\n '1')", b'1.0', b"'1'"),
    ('warning-right-cv-pair', 'single-or-three', b"(bool)(float)('2' |\n '1')", b'true', b"'3'"),
    ('deprecated-both-cv-pair', 'single-xor-nul', b"(int)(bool)('1' ^\n '1')", b'1', b'"\\x00"'),
    ('warning-left-constant', 'unequal-and-zero', b"(int)(bool)('20' &\n '1')", b'0', b"'0'"),
    ('warning-deprecated-constant-float', 'nested-or-thirty', b"(float)(int)('20' |\n ('1' & '3'))", b'30.0', b"'30'"),
    ('deprecated-both-cv-pair', 'empty-xor-empty', b"(bool)(int)('' ^\n '11')", b'false', b"''")]
CASES = {}
for context, variant, expression, expected, expected_inner in VARIANTS:
    source = prior.CASES['native-selected-zero-return-modulo-error-' + context]
    assert source.count(b'selected_modulo_zero_return') == 2 and source.count(b'return 0;') == 1
    assert source.count(b"echo 'P';") == 1
    inner = expression.split(b')', 2)[2]
    witness = b"if (" + inner + b" !== " + expected_inner + b") echo 'bad-string'; "
    witness += b"if (" + expression + b" !== " + expected + b") echo 'bad-cast'; "
    name = 'native-selected-folded-string-bitwise-cast-chain-return-modulo-error-' + context + '-' + variant
    CASES[name] = source.replace(b'selected_modulo_zero_return', b'selected_modulo_folded_string_bitwise_cast_chain_return').replace(
        b'return 0;', b'return ' + expression + b';').replace(b"echo 'P';", witness + b"echo 'P';")


if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-folded-string-bitwise-cast-chain-return-modulo-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
