#!/usr/bin/env python3
"""Emitted single-byte complements keep interned return values owner-free."""
from pathlib import Path
import function_scope as scope
import output_final_selected_zero_return_modulo_error_sources as prior

VARIANTS = [
    ('warning-left-constant', 'full-true', b"~(true ? '0' : UNDEFINED_CHAR_FALSE)", b'"\\xcf"', b'0.0'),
    ('deprecated-both-cv-pair', 'full-false-digit', b'~(false ? UNDEFINED_CHAR_TRUE : "\\xce")', b"'1'", b'1.0'),
    ('warning-right-cv-pair', 'shorthand-true', b'~("\\xcf" ?: UNDEFINED_CHAR_FALSE)', b"'0'", b'0.0'),
    ('warning-deprecated-constant-float', 'shorthand-false-digit', b'~(\'\' ?: "\\xce")', b"'1'", b'1.0'),
    ('warning-left-constant', 'coalesce-nonnull', b"~('1' ?? UNDEFINED_CHAR_FALSE)", b'"\\xce"', b'0.0'),
    ('deprecated-both-cv-pair', 'coalesce-null-nul', b'~(null ?? "\\xff")', b'"\\0"', b'0.0'),
    ('warning-right-cv-pair', 'full-false-letter', b'~(false ? UNDEFINED_CHAR_TRUE : "\\xbe")', b"'A'", b'0.0'),
    ('warning-deprecated-constant-float', 'nested-full', b"~(true ? (false ? UNDEFINED_CHAR_TRUE : '2') : UNDEFINED_CHAR_FALSE)", b'"\\xcd"', b'0.0')]
CASES = {}
for context, variant, inner, inner_expected, expected in VARIANTS:
    source = prior.CASES['native-selected-zero-return-modulo-error-' + context]
    expression = b'(float)(int)(' + inner + b')'
    witness = b"if ((" + inner + b") !== " + inner_expected + b") echo 'bad-byte-not'; "
    witness += b"if (" + expression + b" !== " + expected + b") echo 'bad-cast'; "
    name = 'native-selected-emitted-byte-bitnot-cast-chain-return-modulo-error-' + context + '-' + variant
    CASES[name] = source.replace(b'selected_modulo_zero_return', b'selected_modulo_emitted_byte_bitnot_return').replace(
        b'return 0;', b'return ' + expression + b';').replace(b"echo 'P';", witness + b"echo 'P';")


if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-emitted-byte-bitnot-cast-chain-return-modulo-error',
                                    Path(__file__), publish=False, model_seconds=90) else 1)
