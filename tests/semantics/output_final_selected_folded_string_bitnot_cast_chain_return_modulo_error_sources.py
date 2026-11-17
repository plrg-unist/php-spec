#!/usr/bin/env python3
"""Selected MOD handler casts consume authenticated folded STRING bitwise NOT."""
from pathlib import Path
import function_scope as scope
import output_final_selected_zero_return_modulo_error_sources as prior
from output_final_selected_integer_remainder_cast_chain_return_modulo_error_sources import modulo_line

VARIANTS = [
    ('warning-left-constant', 'single-not-one', b'(float)(int)(~\n "\\xce")', b'1.0', b"'1'"),
    ('warning-right-cv-pair', 'multi-not-twenty', b'(bool)(float)(~\n "\\xcd\\xcf")', b'true', b"'20'"),
    ('deprecated-both-cv-pair', 'single-not-nul', b'(int)(bool)(~\n "\\xff")', b'1', b'"\\x00"'),
    ('warning-left-constant', 'double-not-zero', b"(int)(bool)(~\n (~'0'))", b'0', b"'0'"),
    ('warning-deprecated-constant-float', 'bitand-not-two-nul', b'(float)(int)(~\n ("\\xff\\xff" &\n "\\xff\\xff"))', b'0.0', b'"\\x00\\x00"'),
    ('deprecated-both-cv-pair', 'empty-not-empty', b"(bool)(int)(~\n '')", b'false', b"''")]
CASES = {}
for context, variant, expression, expected, expected_inner in VARIANTS:
    source = prior.CASES['native-selected-zero-return-modulo-error-' + context]
    assert source.count(b'selected_modulo_zero_return') == 2 and source.count(b'return 0;') == 1
    assert source.count(b"echo 'P';") == 1
    inner = expression.split(b')', 2)[2]
    witness = b"if (" + inner + b" !== " + expected_inner + b") echo 'bad-string'; "
    witness += b"if (" + expression + b" !== " + expected + b") echo 'bad-cast'; "
    name = 'native-selected-folded-string-bitnot-cast-chain-return-modulo-error-' + context + '-' + variant
    CASES[name] = source.replace(b'selected_modulo_zero_return', b'selected_modulo_folded_string_bitnot_cast_chain_return').replace(
        b'return 0;', b'return ' + expression + b';').replace(b"echo 'P';", witness + b"echo 'P';")


if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-folded-string-bitnot-cast-chain-return-modulo-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
