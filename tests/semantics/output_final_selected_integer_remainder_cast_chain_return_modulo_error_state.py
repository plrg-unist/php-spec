#!/usr/bin/env python3
"""Integer-remainder trees reuse the standalone arithmetic predicate generator."""
import output_final_selected_integer_arithmetic_cast_chain_return_modulo_error_state as current
import output_final_selected_integer_remainder_cast_chain_return_modulo_error_sources as sources

integer, negative, string, cast = current.integer, current.negative, current.string, current.cast
runner, PREFIX, CONJ = current.runner, current.PREFIX, current.CONJ
DETAILS = {context + '-' + variant: (context, variant) for context, variant, _, _ in sources.VARIANTS}
CASES = {name: sources.CASES['native-selected-integer-remainder-cast-chain-return-modulo-error-' + name]
         for name in ['deprecated-both-cv-pair-folded-mod-zero',
                      'warning-deprecated-constant-float-emitted-mod-zero',
                      'warning-left-constant-emitted-mod-min-minus-one']}


def remainder(result, left, right):
    return ('NExprBinaryOpMod', 'MODULO', None, result, left[4] and right[4], [left, right])


TREES = {
 'folded-mod-zero': cast('bool', 'PBOOL false', cast('int', 'PINT 0',
    remainder('PINT 0', integer(6), integer(3)))),
 'folded-mod-negative': cast('float', 'PFLOAT 13830554455654793216', cast('int', 'PINT $(-1)',
    remainder('PINT $(-1)', negative(5), integer(2)))),
 'folded-mod-one': cast('int', 'PINT 1', cast('bool', 'PBOOL true',
    remainder('PINT 1', integer(5), negative(2)))),
 'emitted-mod-zero': cast('int', 'PINT 0', cast('bool', 'PBOOL false',
    remainder('PINT 0', cast('int', 'PINT 6', string('6')), integer(3)))),
 'emitted-mod-negative': cast('bool', 'PBOOL true', cast('float', 'PFLOAT 13830554455654793216',
    remainder('PINT $(-1)', negative(5), cast('int', 'PINT 2', string('2'))))),
 'emitted-mod-min-minus-one': cast('int', 'PINT 0', cast('bool', 'PBOOL false',
    remainder('PINT 0', cast('int', 'PINT $(-9223372036854775808)', string('-9223372036854775808')), negative(1))))}


def modulo_line(name):
    source = sources.CASES['native-selected-integer-remainder-cast-chain-return-modulo-error-' + name]
    return sources.modulo_line(DETAILS[name][0], source)


arithmetic_converted = current.converted


def converted(name, condition):
    return arithmetic_converted(name, condition).replace('selected_modulo_integer_arithmetic_cast_chain_return',
                                                       'selected_modulo_integer_remainder_cast_chain_return')


# Entry points use fresh processes; accepted predecessor files stay unchanged.
current.DETAILS, current.TREES = DETAILS, TREES
current.modulo_line, current.converted = modulo_line, converted
nodes, expression, root_value = current.nodes, current.expression, current.root_value
frontier, lifecycle = current.frontier, current.lifecycle


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
