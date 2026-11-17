#!/usr/bin/env python3
"""Proper primitive floating results retain exact bits and real retirement."""
import output_final_selected_primitive_integer_cast_chain_return_modulo_error_state as prior
import output_final_selected_primitive_float_cast_chain_return_modulo_error_sources as sources

current = prior.current
integer, string, cast, constant = prior.integer, prior.string, prior.cast, prior.constant
floating, binary = prior.floating, prior.binary
runner, PREFIX, CONJ = prior.runner, prior.PREFIX, prior.CONJ
DETAILS = {context + '-' + variant: (context, variant) for context, variant, _, _, _ in sources.VARIANTS}
CASES = {name: sources.CASES['native-selected-primitive-float-cast-chain-return-modulo-error-' + name]
         for name in ['warning-left-constant-folded-float-bool-add-two',
                      'deprecated-both-cv-pair-emitted-float-string-subtract-zero',
                      'warning-left-constant-emitted-integer-bool-add-overflow']}

TREES = {
 'folded-float-bool-add-two': cast('float', 'PFLOAT 4611686018427387904', cast('int', 'PINT 2',
    binary('add', 'PFLOAT 4611686018427387904', floating('3ff0000000000000'), constant('true')))),
 'emitted-float-string-subtract-zero': cast('bool', 'PBOOL false', cast('float', 'PFLOAT 0',
    binary('sub', 'PFLOAT 0', floating('3ff0000000000000'), cast('float', 'PFLOAT 4607182418800017408', string('1'))))),
 'folded-float-string-multiply-three': cast('int', 'PINT 1', cast('bool', 'PBOOL true',
    binary('mul', 'PFLOAT 4613937818241073152', floating('3ff8000000000000'), string('2')))),
 'folded-bool-integer-divide-half': cast('bool', 'PBOOL true', cast('float', 'PFLOAT 4602678819172646912',
    binary('div', 'PFLOAT 4602678819172646912', constant('true'), integer(2)))),
 'emitted-float-power-one': cast('bool', 'PBOOL true', cast('int', 'PINT 1',
    binary('pow', 'PFLOAT 4607182418800017408', cast('float', 'PFLOAT 4607182418800017408', string('1')), integer(3)))),
 'emitted-integer-bool-add-overflow': cast('int', 'PINT 1', cast('bool', 'PBOOL true',
    binary('add', 'PFLOAT 4890909195324358656', cast('int', 'PINT 9223372036854775807', string('9223372036854775807')),
           constant('true'))))}


def modulo_line(name):
    source = sources.CASES['native-selected-primitive-float-cast-chain-return-modulo-error-' + name]
    return sources.modulo_line(DETAILS[name][0], source)


integer_converted = current.converted


def converted(name, condition):
    return integer_converted(name, condition).replace('selected_modulo_primitive_integer_cast_chain_return',
                                                    'selected_modulo_primitive_float_cast_chain_return')


current.DETAILS, current.TREES = DETAILS, TREES
current.modulo_line, current.converted, current.expression = modulo_line, converted, prior.expression
nodes, root_value, expression = current.nodes, current.root_value, current.expression
frontier, lifecycle = current.frontier, current.lifecycle


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
