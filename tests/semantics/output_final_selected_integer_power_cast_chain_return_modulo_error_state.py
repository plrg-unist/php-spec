#!/usr/bin/env python3
"""Quiet fitting integer powers retain typed returns and real retirement."""
import output_final_selected_integer_arithmetic_cast_chain_return_modulo_error_state as current
import output_final_selected_integer_power_cast_chain_return_modulo_error_sources as sources

integer, negative, string, cast = current.integer, current.negative, current.string, current.cast
runner, PREFIX, CONJ = current.runner, current.PREFIX, current.CONJ
DETAILS = {context + '-' + variant: (context, variant) for context, variant, _, _, _ in sources.VARIANTS}
CASES = {name: sources.CASES['native-selected-integer-power-cast-chain-return-modulo-error-' + name]
         for name in ['deprecated-both-cv-pair-folded-pow-zero',
                      'warning-deprecated-constant-float-emitted-pow-zero',
                      'warning-left-constant-emitted-pow-min']}


def power(result, left, right):
    return ('NExprBinaryOpPow', 'POWER', None, result, left[4] and right[4], [left, right])


TREES = {
 'folded-pow-zero': cast('bool', 'PBOOL false', cast('int', 'PINT 0',
    power('PINT 0', integer(0), integer(3)))),
 'folded-pow-negative': cast('float', 'PFLOAT 13844065254536904704', cast('int', 'PINT $(-8)',
    power('PINT $(-8)', negative(2), integer(3)))),
 'folded-pow-one': cast('int', 'PINT 1', cast('bool', 'PBOOL true',
    power('PINT 1', integer(2), integer(0)))),
 'emitted-pow-zero': cast('int', 'PINT 0', cast('bool', 'PBOOL false',
    power('PINT 0', cast('int', 'PINT 0', string('0')), integer(3)))),
 'emitted-pow-negative': cast('bool', 'PBOOL true', cast('float', 'PFLOAT 13844065254536904704',
    power('PINT $(-8)', negative(2), cast('int', 'PINT 3', string('3'))))),
 'emitted-pow-min': cast('float', 'PFLOAT 14114281232179134464', cast('int', 'PINT $(-9223372036854775808)',
    power('PINT $(-9223372036854775808)', cast('int', 'PINT $(-2)', string('-2')),
          cast('int', 'PINT 63', string('63')))))}


def modulo_line(name):
    source = sources.CASES['native-selected-integer-power-cast-chain-return-modulo-error-' + name]
    return sources.modulo_line(DETAILS[name][0], source)


arithmetic_converted = current.converted


def converted(name, condition):
    return arithmetic_converted(name, condition).replace('selected_modulo_integer_arithmetic_cast_chain_return',
                                                       'selected_modulo_integer_power_cast_chain_return')


# Entry points use fresh processes; accepted predecessor evidence stays unchanged.
current.DETAILS, current.TREES = DETAILS, TREES
current.modulo_line, current.converted = modulo_line, converted
nodes, expression, root_value = current.nodes, current.expression, current.root_value
frontier, lifecycle = current.frontier, current.lifecycle


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
