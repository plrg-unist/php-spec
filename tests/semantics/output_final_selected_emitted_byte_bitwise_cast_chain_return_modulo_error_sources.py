#!/usr/bin/env python3
"""Emitted one-byte STRING bitwise results retain permanent character identity."""
from pathlib import Path
import function_scope as scope
import output_final_selected_zero_return_modulo_error_sources as prior

VARIANTS = [
    ('warning-left-constant', 'and-left-full', b"(true ? '3' : UNDEFINED_BYTE_LEFT) &\n '1'", b"'1'", b'1.0'),
    ('warning-right-cv-pair', 'and-right-coalesce', b"'3' & (null ?? '1')", b"'1'", b'1.0'),
    ('deprecated-both-cv-pair', 'and-both-selections', b"('3' ?: UNDEFINED_BYTE_LEFT) & (false ? UNDEFINED_BYTE_RIGHT : '1')", b"'1'", b'1.0'),
    ('warning-deprecated-constant-float', 'or-left-derived-nul', b'(~(null ?? "\\xff")) | \'1\'', b"'1'", b'1.0'),
    ('warning-left-constant', 'or-right-overlap', b"'3' |\n (false ? UNDEFINED_BYTE_RIGHT : '1')", b"'3'", b'3.0'),
    ('deprecated-both-cv-pair', 'or-both-selections', b"('0' ?? UNDEFINED_BYTE_LEFT) | ('1' ?: UNDEFINED_BYTE_RIGHT)", b"'1'", b'1.0'),
    ('warning-right-cv-pair', 'xor-left-full-zero', b"(true ? 'q' : UNDEFINED_BYTE_LEFT) ^ 'A'", b"'0'", b'0.0'),
    ('warning-deprecated-constant-float', 'xor-right-coalesce-nul', b"'1' ^ (null ?? '1')", b'"\\0"', b'0.0'),
    ('deprecated-both-cv-pair', 'xor-both-selections-nul', b"('1' ?? UNDEFINED_BYTE_LEFT) ^\n (false ? UNDEFINED_BYTE_RIGHT : '1')", b'"\\0"', b'0.0')]
CASES = {}
for context, variant, inner, inner_expected, expected in VARIANTS:
    source = prior.CASES['native-selected-zero-return-modulo-error-' + context]
    assert source.count(b'selected_modulo_zero_return') == 2 and source.count(b'return 0;') == 1
    assert source.count(b"echo 'P';") == 1
    expression = b'(float)(int)(' + inner + b')'
    witness = b"if ((" + inner + b") !== " + inner_expected + b") echo 'bad-byte-bitwise'; "
    witness += b"if (" + expression + b" !== " + expected + b") echo 'bad-cast'; "
    name = 'native-selected-emitted-byte-bitwise-cast-chain-return-modulo-error-' + context + '-' + variant
    CASES[name] = source.replace(b'selected_modulo_zero_return', b'selected_modulo_emitted_byte_bitwise_return').replace(
        b'return 0;', b'return ' + expression + b';').replace(b"echo 'P';", witness + b"echo 'P';")


if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-emitted-byte-bitwise-cast-chain-return-modulo-error',
                                    Path(__file__), publish=False, model_seconds=90) else 1)
