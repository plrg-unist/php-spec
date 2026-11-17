#!/usr/bin/env python3
"""Selected MOD handler casts consume quiet signed64 integer remainders."""
from pathlib import Path
import function_scope as scope
import output_final_selected_zero_return_modulo_error_sources as prior

VARIANTS = [
    ('deprecated-both-cv-pair', 'folded-mod-zero', b'(bool)(int)(6 %\n 3)', b'false'),
    ('warning-left-constant', 'folded-mod-negative', b'(float)(int)((-5) %\n 2)', b'-1.0'),
    ('warning-right-cv-pair', 'folded-mod-one', b'(int)(bool)(5 %\n (-2))', b'1'),
    ('warning-deprecated-constant-float', 'emitted-mod-zero', b"(int)(bool)((int)'6' %\n 3)", b'0'),
    ('deprecated-both-cv-pair', 'emitted-mod-negative', b"(bool)(float)((-5) %\n (int)'2')", b'true'),
    ('warning-left-constant', 'emitted-mod-min-minus-one', b"(int)(bool)((int)'-9223372036854775808' %\n (-1))", b'0')]
CASES = {}
for context, variant, expression, expected in VARIANTS:
    source = prior.CASES['native-selected-zero-return-modulo-error-' + context]
    assert source.count(b'selected_modulo_zero_return') == 2 and source.count(b'return 0;') == 1
    assert source.count(b"echo 'P';") == 1
    witness = b"if (" + expression + b" !== " + expected + b") echo 'bad-cast'; "
    name = 'native-selected-integer-remainder-cast-chain-return-modulo-error-' + context + '-' + variant
    CASES[name] = source.replace(b'selected_modulo_zero_return', b'selected_modulo_integer_remainder_cast_chain_return').replace(
        b'return 0;', b'return ' + expression + b';').replace(b"echo 'P';", witness + b"echo 'P';")


def modulo_line(context, source):
    original = prior.CASES['native-selected-zero-return-modulo-error-' + context]
    line, = [line for line in original.splitlines(keepends=True) if b'%' in line]
    assert line.count(b'%') == 1 and source.count(line) == 1
    return source[:source.index(line) + line.index(b'%')].count(b'\n') + 1


if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-integer-remainder-cast-chain-return-modulo-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
