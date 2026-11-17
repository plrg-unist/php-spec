#!/usr/bin/env python3
"""Selected handler casts consume byte-only parser-created STRING CONCAT."""
from pathlib import Path
import function_scope as scope
import output_final_selected_zero_return_modulo_error_sources as prior
from output_final_selected_integer_remainder_cast_chain_return_modulo_error_sources import modulo_line

VARIANTS = [
    ('warning-left-constant', 'right-empty-one', b"(float)(int)('1' . '')", b'1.0', b"'1'"),
    ('warning-right-cv-pair', 'multiline-twenty', b"(bool)(float)('2' .\n '0')", b'true', b"'20'"),
    ('deprecated-both-cv-pair', 'left-empty-zero', b"(int)(bool)('' .\n '0')", b'0', b"'0'"),
    ('warning-left-constant', 'nested-twelve', b"(float)(int)(('1' .\n '2') . '')", b'12.0', b"'12'"),
    ('warning-deprecated-constant-float', 'high-byte', b'(int)(bool)("\\xff" .\n \'x\')', b'1', b'"\\xffx"'),
    ('deprecated-both-cv-pair', 'empty', b"(bool)(int)('' .\n '')", b'false', b"''")]
CASES = {}


def function_name(variant):
    return ('selected_modulo_parser_concat_assessment' if variant == 'right-empty-one'
            else 'selected_modulo_parser_string_concat_cast_chain_return')


for context, variant, expression, expected, inner_expected in VARIANTS:
    source = prior.CASES['native-selected-zero-return-modulo-error-' + context]
    inner = expression.split(b')', 2)[2]
    witness = b"if (" + inner + b" !== " + inner_expected + b") echo 'bad-string'; "
    witness += b"if (" + expression + b" !== " + expected + b") echo 'bad-cast'; "
    CASES['native-selected-parser-string-concat-cast-chain-return-modulo-error-' + context + '-' + variant] = source.replace(
        b'selected_modulo_zero_return', function_name(variant).encode()).replace(
        b'return 0;', b'return ' + expression + b';').replace(b"echo 'P';", witness + b"echo 'P';")


if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-parser-string-concat-cast-chain-return-modulo-error',
                                    Path(__file__), publish=False, model_seconds=90) else 1)
