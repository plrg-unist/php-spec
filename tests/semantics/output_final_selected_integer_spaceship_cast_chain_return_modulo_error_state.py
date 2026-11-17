#!/usr/bin/env python3
"""Normalized integer comparisons retain typed returns and real retirement."""
import output_final_selected_integer_arithmetic_cast_chain_return_modulo_error_state as current
import output_final_selected_integer_spaceship_cast_chain_return_modulo_error_sources as sources

integer, negative, string, cast = current.integer, current.negative, current.string, current.cast
runner, PREFIX, CONJ = current.runner, current.PREFIX, current.CONJ
DETAILS = {context + '-' + variant: (context, variant) for context, variant, _, _, _ in sources.VARIANTS}
CASES = {name: sources.CASES['native-selected-integer-spaceship-cast-chain-return-modulo-error-' + name]
         for name in ['deprecated-both-cv-pair-folded-cmp-zero',
                      'warning-deprecated-constant-float-emitted-cmp-zero',
                      'warning-left-constant-emitted-cmp-min-max']}


def compare(result, left, right):
    return ('NExprBinaryOpSpaceship', 'SPACESHIP', None, result, left[4] and right[4], [left, right])


TREES = {
 'folded-cmp-zero': cast('bool', 'PBOOL false', cast('int', 'PINT 0',
    compare('PINT 0', integer(7), integer(7)))),
 'folded-cmp-negative': cast('float', 'PFLOAT 13830554455654793216', cast('int', 'PINT $(-1)',
    compare('PINT $(-1)', negative(5), integer(5)))),
 'folded-cmp-one': cast('int', 'PINT 1', cast('bool', 'PBOOL true',
    compare('PINT 1', integer(5), negative(5)))),
 'emitted-cmp-zero': cast('int', 'PINT 0', cast('bool', 'PBOOL false',
    compare('PINT 0', cast('int', 'PINT 7', string('7')), integer(7)))),
 'emitted-cmp-one': cast('bool', 'PBOOL true', cast('float', 'PFLOAT 4607182418800017408',
    compare('PINT 1', negative(5), cast('int', 'PINT $(-6)', string('-6'))))),
 'emitted-cmp-min-max': cast('float', 'PFLOAT 13830554455654793216', cast('int', 'PINT $(-1)',
    compare('PINT $(-1)', cast('int', 'PINT $(-9223372036854775808)', string('-9223372036854775808')),
            cast('int', 'PINT 9223372036854775807', string('9223372036854775807')))))}


def modulo_line(name):
    source = sources.CASES['native-selected-integer-spaceship-cast-chain-return-modulo-error-' + name]
    return sources.modulo_line(DETAILS[name][0], source)


arithmetic_converted = current.converted


def converted(name, condition):
    return arithmetic_converted(name, condition).replace('selected_modulo_integer_arithmetic_cast_chain_return',
                                                       'selected_modulo_integer_spaceship_cast_chain_return')


# Entry points use fresh processes; accepted predecessor evidence stays unchanged.
current.DETAILS, current.TREES = DETAILS, TREES
current.modulo_line, current.converted = modulo_line, converted
nodes, expression, root_value = current.nodes, current.expression, current.root_value
frontier, lifecycle = current.frontier, current.lifecycle


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
