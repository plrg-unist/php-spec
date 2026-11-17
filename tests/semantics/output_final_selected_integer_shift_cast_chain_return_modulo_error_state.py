#!/usr/bin/env python3
"""Quiet integer shifts retain exact typed returns and real retirement."""
import output_final_selected_integer_arithmetic_cast_chain_return_modulo_error_state as current
import output_final_selected_integer_shift_cast_chain_return_modulo_error_sources as sources

integer, negative, string, cast = current.integer, current.negative, current.string, current.cast
runner, PREFIX, CONJ = current.runner, current.PREFIX, current.CONJ
DETAILS = {context + '-' + variant: (context, variant) for context, variant, _, _ in sources.VARIANTS}
CASES = {name: sources.CASES['native-selected-integer-shift-cast-chain-return-modulo-error-' + name]
         for name in ['deprecated-both-cv-pair-folded-shl-zero',
                      'warning-deprecated-constant-float-emitted-shr-zero',
                      'warning-left-constant-emitted-shl-min']}


def shift(kind, result, left, right):
    constructor, operator = {'left': ('NExprBinaryOpShiftLeft', 'SHIFTLEFT'),
                             'right': ('NExprBinaryOpShiftRight', 'SHIFTRIGHT')}[kind]
    return (constructor, operator, None, result, left[4] and right[4], [left, right])


TREES = {
 'folded-shl-zero': cast('bool', 'PBOOL false', cast('int', 'PINT 0',
    shift('left', 'PINT 0', integer(1), integer(64)))),
 'folded-shr-negative': cast('float', 'PFLOAT 13837309855095848960', cast('int', 'PINT $(-3)',
    shift('right', 'PINT $(-3)', negative(5), integer(1)))),
 'folded-shl-min': cast('float', 'PFLOAT 14114281232179134464', cast('int', 'PINT $(-9223372036854775808)',
    shift('left', 'PINT $(-9223372036854775808)', integer(1), integer(63)))),
 'emitted-shr-zero': cast('int', 'PINT 0', cast('bool', 'PBOOL false',
    shift('right', 'PINT 0', cast('int', 'PINT 5', string('5')), integer(64)))),
 'emitted-shr-negative': cast('bool', 'PBOOL true', cast('float', 'PFLOAT 13830554455654793216',
    shift('right', 'PINT $(-1)', negative(5), cast('int', 'PINT 64', string('64'))))),
 'emitted-shl-min': cast('float', 'PFLOAT 14114281232179134464', cast('int', 'PINT $(-9223372036854775808)',
    shift('left', 'PINT $(-9223372036854775808)', cast('int', 'PINT 1', string('1')),
          cast('int', 'PINT 63', string('63')))))}


def modulo_line(name):
    source = sources.CASES['native-selected-integer-shift-cast-chain-return-modulo-error-' + name]
    return sources.modulo_line(DETAILS[name][0], source)


arithmetic_converted = current.converted


def converted(name, condition):
    return arithmetic_converted(name, condition).replace('selected_modulo_integer_arithmetic_cast_chain_return',
                                                       'selected_modulo_integer_shift_cast_chain_return')


# Entry points use fresh processes; accepted predecessor files stay unchanged.
current.DETAILS, current.TREES = DETAILS, TREES
current.modulo_line, current.converted = modulo_line, converted
nodes, expression, root_value = current.nodes, current.expression, current.root_value
frontier, lifecycle = current.frontier, current.lifecycle


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
