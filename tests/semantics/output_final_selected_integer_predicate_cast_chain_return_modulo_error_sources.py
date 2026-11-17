#!/usr/bin/env python3
"""Selected MOD handler casts consume quiet Boolean predicates over integers."""
from pathlib import Path
import function_scope as scope
import output_final_selected_zero_return_modulo_error_sources as prior
from output_final_selected_integer_remainder_cast_chain_return_modulo_error_sources import modulo_line

VARIANTS = [
    ('deprecated-both-cv-pair', 'folded-identical-true', b'(bool)(int)(7 ===\n 7)', b'true', b'true'),
    ('warning-left-constant', 'emitted-notidentical-false', b"(float)(int)(((int)'7') !==\n 7)", b'0.0', b'false'),
    ('deprecated-both-cv-pair', 'folded-equal-false', b'(bool)(float)(7 ==\n 8)', b'false', b'false'),
    ('warning-right-cv-pair', 'emitted-notequal-true', b"(int)(bool)((-5) !=\n ((int)'-6'))", b'1', b'true'),
    ('warning-left-constant', 'folded-less-true', b'(float)(int)((-5) <\n 5)', b'1.0', b'true'),
    ('warning-deprecated-constant-float', 'emitted-lessequal-true', b"(int)(bool)(((int)'7') <=\n 7)", b'1', b'true'),
    ('warning-left-constant', 'emitted-greater-false', b"(int)(bool)(((int)'1') >\n 2)", b'0', b'false'),
    ('warning-deprecated-constant-float', 'emitted-greaterequal-true', b"(bool)(float)(((int)'7') >=\n 7)", b'true', b'true'),
    ('deprecated-both-cv-pair', 'emitted-xor-false', b"(bool)(int)((((int)'2') xor\n 4))", b'false', b'false')]
CASES = {}
for context, variant, expression, expected, expected_inner in VARIANTS:
    source = prior.CASES['native-selected-zero-return-modulo-error-' + context]
    assert source.count(b'selected_modulo_zero_return') == 2 and source.count(b'return 0;') == 1
    assert source.count(b"echo 'P';") == 1
    inner = expression.split(b')', 2)[2]
    witness = b"if (" + inner + b" !== " + expected_inner + b") echo 'bad-predicate'; "
    witness += b"if (" + expression + b" !== " + expected + b") echo 'bad-cast'; "
    if variant == 'emitted-xor-false':
        witness += b"if ((0 xor 2) !== true) echo 'bad-zero-truth'; if ((2 xor 4) !== false) echo 'bad-nonzero-truth'; "
    name = 'native-selected-integer-predicate-cast-chain-return-modulo-error-' + context + '-' + variant
    CASES[name] = source.replace(b'selected_modulo_zero_return', b'selected_modulo_integer_predicate_cast_chain_return').replace(
        b'return 0;', b'return ' + expression + b';').replace(b"echo 'P';", witness + b"echo 'P';")


if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-selected-integer-predicate-cast-chain-return-modulo-error', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
