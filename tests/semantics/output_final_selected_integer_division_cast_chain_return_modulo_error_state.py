#!/usr/bin/env python3
"""Exact-division trees reuse the standalone integer-arithmetic predicate generator."""
import output_final_selected_integer_arithmetic_cast_chain_return_modulo_error_state as current
import output_final_selected_integer_division_cast_chain_return_modulo_error_sources as sources

integer, negative, string, cast = current.integer, current.negative, current.string, current.cast
runner, PREFIX, CONJ = current.runner, current.PREFIX, current.CONJ
DETAILS = {context + '-' + variant: (context, variant) for context, variant, _, _ in sources.VARIANTS}
CASES = {name: sources.CASES['native-selected-integer-division-cast-chain-return-modulo-error-' + name]
         for name in ['deprecated-both-cv-pair-folded-div-zero',
                      'warning-deprecated-constant-float-emitted-div-zero',
                      'warning-left-constant-emitted-div-one']}


def division(result, left, right):
    return ('NExprBinaryOpDiv', 'DIVIDE', None, result, left[4] and right[4], [left, right])


TREES = {
 'folded-div-zero': cast('bool', 'PBOOL false', cast('int', 'PINT 0',
    division('PINT 0', integer(0), integer(2)))),
 'folded-div-negative': cast('float', 'PFLOAT 13835058055282163712', cast('int', 'PINT $(-2)',
    division('PINT $(-2)', negative(4), integer(2)))),
 'folded-div-one': cast('int', 'PINT 1', cast('bool', 'PBOOL true',
    division('PINT 2', integer(6), integer(3)))),
 'emitted-div-zero': cast('int', 'PINT 0', cast('bool', 'PBOOL false',
    division('PINT 0', cast('int', 'PINT 0', string('0')), integer(2)))),
 'emitted-div-negative': cast('bool', 'PBOOL true', cast('float', 'PFLOAT 13835058055282163712',
    division('PINT $(-2)', integer(4), cast('int', 'PINT $(-2)', string('-2'))))),
 'emitted-div-one': cast('int', 'PINT 1', cast('bool', 'PBOOL true',
    division('PINT 2', cast('int', 'PINT 6', string('6')), cast('int', 'PINT 3', string('3')))))}


def modulo_line(name):
    source = sources.CASES['native-selected-integer-division-cast-chain-return-modulo-error-' + name]
    assert source.count(b'%') == 1
    return source[:source.index(b'%')].count(b'\n') + 1


arithmetic_converted = current.converted


def converted(name, condition):
    return arithmetic_converted(name, condition).replace('selected_modulo_integer_arithmetic_cast_chain_return',
                                                       'selected_modulo_integer_division_cast_chain_return')


# Each fixture entry point runs in its own Python process. Configure the existing
# pure predicate generator without changing any accepted predecessor file.
current.DETAILS, current.TREES = DETAILS, TREES
current.modulo_line, current.converted = modulo_line, converted
nodes, expression, root_value = current.nodes, current.expression, current.root_value
frontier, lifecycle = current.frontier, current.lifecycle


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
