#!/usr/bin/env python3
"""Quiet nonvariable coalesce preserves nonnull values through return casts."""
from pathlib import Path
import function_scope as scope
import output_final_selected_zero_return_modulo_error_sources as prior
from output_final_selected_integer_remainder_cast_chain_return_modulo_error_sources import modulo_line

VARIANTS = [
    ('warning-left-constant', 'nonnull-int-zero', b"(int)'0' ?? UNDEFINED_COALESCE_RIGHT", b'0', b'0.0'),
    ('deprecated-both-cv-pair', 'nonnull-bool-false', b'(bool)0 ?? UNDEFINED_COALESCE_RIGHT', b'false', b'0.0'),
    ('warning-right-cv-pair', 'nonnull-float-zero', b'(float)0 ?? UNDEFINED_COALESCE_RIGHT', b'0.0', b'0.0'),
    ('warning-deprecated-constant-float', 'nonnull-empty-string', b"'' ?? UNDEFINED_COALESCE_RIGHT", b"''", b'0.0'),
    ('warning-left-constant', 'null-int', b'null ?? 1', b'1', b'1.0'),
    ('deprecated-both-cv-pair', 'null-nested-string', b"(null ?? null) ?? '0'", b"'0'", b'0.0'),
    ('warning-right-cv-pair', 'null-cast', b"null ?? (int)'1'", b'1', b'1.0'),
    ('warning-deprecated-constant-float', 'nonnull-negative-int', b"(int)'-1' ?? UNDEFINED_COALESCE_RIGHT", b'-1', b'-1.0')]
CASES = {}
for context, variant, inner, inner_expected, expected in VARIANTS:
    source = prior.CASES['native-selected-zero-return-modulo-error-' + context]
    expression = b'(float)(int)(' + inner + b')'
    witness = b"if ((" + inner + b") !== " + inner_expected + b") echo 'bad-coalesce'; "
    witness += b"if (" + expression + b" !== " + expected + b") echo 'bad-cast'; "
    name = 'native-selected-quiet-coalesce-cast-chain-return-modulo-error-' + context + '-' + variant
    CASES[name] = source.replace(b'selected_modulo_zero_return', b'selected_modulo_quiet_coalesce_return').replace(
        b'return 0;', b'return ' + expression + b';').replace(b"echo 'P';", witness + b"echo 'P';")


if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-quiet-coalesce-cast-chain-return-modulo-error',
                                    Path(__file__), publish=False, model_seconds=90) else 1)
