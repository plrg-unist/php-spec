#!/usr/bin/env python3
"""Selected MOD handlers retain quiet raw signed numeric NOT inside cast chains."""
from pathlib import Path
import function_scope as scope
import output_final_selected_zero_return_modulo_error_sources as prior

CASES = {}
for (name, source), expression, expected in zip(prior.CASES.items(),
        [b'(bool)(int)(!(-7))', b'(bool)(float)(!(+0.125))', b'(int)(bool)(!(+0))', b'(float)(int)(!(-0.0))'],
        [b'false', b'false', b'1', b'1.0'], strict=True):
    assert source.count(b'selected_modulo_zero_return') == 2 and source.count(b'return 0;') == 1
    assert source.count(b"echo 'P';") == 1
    witness = b"if (" + expression + b" !== " + expected + b") echo 'bad-cast'; "
    CASES[name.replace('selected-zero-return', 'selected-signed-numeric-not-cast-chain-return')] = source.replace(
        b'selected_modulo_zero_return', b'selected_modulo_signed_numeric_not_cast_chain_return').replace(
        b'return 0;', b'return ' + expression + b';').replace(b"echo 'P';", witness + b"echo 'P';")

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-signed-numeric-not-cast-chain-return-modulo-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
