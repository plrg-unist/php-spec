#!/usr/bin/env python3
"""Selected MOD handler casts consume quiet predicates over proper primitives."""
from pathlib import Path
import function_scope as scope
import output_final_selected_zero_return_modulo_error_sources as prior
from output_final_selected_integer_remainder_cast_chain_return_modulo_error_sources import modulo_line

VARIANTS = [
    ('deprecated-both-cv-pair', 'folded-bool-identical-true', b'(bool)(int)((7 === 7) ===\n (8 === 8))', b'true', b'true'),
    ('warning-left-constant', 'emitted-bool-int-notidentical-true', b'(float)(int)(((bool)(int)1) !==\n 1)', b'1.0', b'true'),
    ('deprecated-both-cv-pair', 'folded-string-int-equal-false', b"(bool)(float)('seven' ==\n 0)", b'false', b'false'),
    ('warning-right-cv-pair', 'folded-null-bool-notequal-false', b'(int)(bool)(null !=\n false)', b'0', b'false'),
    ('warning-left-constant', 'folded-null-string-less-true', b"(float)(int)(null <\n '0')", b'1.0', b'true'),
    ('warning-deprecated-constant-float', 'emitted-float-int-lessequal-false', b'(int)(bool)(((float)1) <=\n 0)', b'0', b'false'),
    ('warning-left-constant', 'folded-numeric-strings-greater-true', b"(int)(bool)('10' >\n '2')", b'1', b'true'),
    ('warning-deprecated-constant-float', 'emitted-string-int-greaterequal-true', b"(bool)(float)('a' >=\n ((int)'99'))", b'true', b'true'),
    ('deprecated-both-cv-pair', 'emitted-string-bool-xor-false', b"(bool)(int)(('0' xor\n ((bool)0)))", b'false', b'false')]
CASES = {}
for context, variant, expression, expected, expected_inner in VARIANTS:
    source = prior.CASES['native-selected-zero-return-modulo-error-' + context]
    assert source.count(b'selected_modulo_zero_return') == 2 and source.count(b'return 0;') == 1
    assert source.count(b"echo 'P';") == 1
    inner = expression.split(b')', 2)[2]
    witness = b"if (" + inner + b" !== " + expected_inner + b") echo 'bad-predicate'; "
    witness += b"if (" + expression + b" !== " + expected + b") echo 'bad-cast'; "
    if variant == 'emitted-string-bool-xor-false':
        witness += b"if (('0' xor '00') !== true) echo 'bad-string-truth'; "
    name = 'native-selected-primitive-predicate-cast-chain-return-modulo-error-' + context + '-' + variant
    CASES[name] = source.replace(b'selected_modulo_zero_return', b'selected_modulo_primitive_predicate_cast_chain_return').replace(
        b'return 0;', b'return ' + expression + b';').replace(b"echo 'P';", witness + b"echo 'P';")


if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-primitive-predicate-cast-chain-return-modulo-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
