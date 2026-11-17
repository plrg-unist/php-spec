#!/usr/bin/env python3
"""Proper primitive integer results retain exact tags and real retirement."""
import base64
import output_final_selected_primitive_predicate_cast_chain_return_modulo_error_state as prior
import output_final_selected_primitive_integer_cast_chain_return_modulo_error_sources as sources

current = prior.current
integer, string, cast, constant = current.integer, current.string, current.cast, prior.constant
runner, PREFIX, CONJ = current.runner, current.PREFIX, current.CONJ
DETAILS = {context + '-' + variant: (context, variant) for context, variant, _, _, _ in sources.VARIANTS}
CASES = {name: sources.CASES['native-selected-primitive-integer-cast-chain-return-modulo-error-' + name]
         for name in ['deprecated-both-cv-pair-folded-bool-string-multiply-zero',
                      'warning-left-constant-folded-float-string-modulo-one',
                      'warning-deprecated-constant-float-emitted-mixed-bitwise-three']}


def floating(bits):
    return ('floating', bits, None, 'PFLOAT ' + str(int(bits, 16)), True, [])


def binary(kind, result, left, right):
    constructor, operator = {
        'and': ('NExprBinaryOpBitwiseAnd', 'BITAND'), 'or': ('NExprBinaryOpBitwiseOr', 'BITOR'),
        'xor': ('NExprBinaryOpBitwiseXor', 'BITXOR'), 'add': ('NExprBinaryOpPlus', 'ADD'),
        'sub': ('NExprBinaryOpMinus', 'SUBTRACT'), 'mul': ('NExprBinaryOpMul', 'MULTIPLY'),
        'div': ('NExprBinaryOpDiv', 'DIVIDE'), 'mod': ('NExprBinaryOpMod', 'MODULO'),
        'shl': ('NExprBinaryOpShiftLeft', 'SHIFTLEFT'), 'shr': ('NExprBinaryOpShiftRight', 'SHIFTRIGHT'),
        'pow': ('NExprBinaryOpPow', 'POWER'), 'space': ('NExprBinaryOpSpaceship', 'SPACESHIP')}[kind]
    return (constructor, operator, None, result, left[4] and right[4], [left, right])


TREES = {
 'folded-bool-null-add-one': cast('bool', 'PBOOL true', cast('int', 'PINT 1',
    binary('add', 'PINT 1', constant('true'), constant('null')))),
 'emitted-string-bool-subtract-two': cast('float', 'PFLOAT 4611686018427387904', cast('int', 'PINT 2',
    binary('sub', 'PINT 2', string('3'), cast('bool', 'PBOOL true', integer(1))))),
 'folded-bool-string-multiply-zero': cast('bool', 'PBOOL false', cast('float', 'PFLOAT 0',
    binary('mul', 'PINT 0', constant('false'), string('2')))),
 'emitted-string-bool-divide-six': cast('int', 'PINT 1', cast('bool', 'PBOOL true',
    binary('div', 'PINT 6', string('6'), cast('bool', 'PBOOL true', integer(1))))),
 'folded-float-string-modulo-one': cast('float', 'PFLOAT 4607182418800017408', cast('int', 'PINT 1',
    binary('mod', 'PINT 1', floating('4014000000000000'), string('2')))),
 'emitted-string-bool-left-shift-six': cast('int', 'PINT 1', cast('bool', 'PBOOL true',
    binary('shl', 'PINT 6', string('3'), cast('bool', 'PBOOL true', integer(1))))),
 'folded-string-float-right-shift-four': cast('int', 'PINT 1', cast('bool', 'PBOOL true',
    binary('shr', 'PINT 4', string('8'), floating('3ff0000000000000')))),
 'emitted-mixed-bitwise-three': cast('bool', 'PBOOL true', cast('float', 'PFLOAT 4613937818241073152',
    binary('or', 'PINT 3', binary('and', 'PINT 1', string('7'), cast('bool', 'PBOOL true', integer(1))),
           binary('xor', 'PINT 2', constant('null'), integer(2))))),
 'folded-mixed-power-spaceship-zero': cast('bool', 'PBOOL false', cast('int', 'PINT 0',
    binary('space', 'PINT 0', binary('pow', 'PINT 2', string('2'), constant('true')),
           binary('add', 'PINT 2', constant('false'), integer(2)))))}


def expression(name, key='cast'):
    kind, spelling, _, _, _, _ = current.nodes(name)[key]
    metadata = 'metadata_' + key
    if kind == 'integer':
        return 'NScalarInt (INTEGER ' + spelling + ') ' + metadata
    if kind == 'floating':
        return 'NScalarFloat (FLOAT "' + spelling + '") ' + metadata
    if kind == 'string':
        return 'NScalarString (BYTES text_' + key + ') ' + metadata
    if kind == 'constant':
        payload = base64.b64encode(spelling.encode()).decode()
        return 'NExprConstFetch (NName (BYTES "' + payload + '") ' + metadata + '_name) ' + metadata
    return kind + ' ' + ' '.join('(' + expression(name, child) + ')' for child, _ in current.children(key, current.nodes(name)[key])) + ' ' + metadata


def modulo_line(name):
    source = sources.CASES['native-selected-primitive-integer-cast-chain-return-modulo-error-' + name]
    return sources.modulo_line(DETAILS[name][0], source)


primitive_converted = current.converted


def converted(name, condition):
    return primitive_converted(name, condition).replace('selected_modulo_primitive_predicate_cast_chain_return',
                                                      'selected_modulo_primitive_integer_cast_chain_return')


current.DETAILS, current.TREES = DETAILS, TREES
current.modulo_line, current.converted, current.expression = modulo_line, converted, expression
nodes, root_value = current.nodes, current.root_value
frontier, lifecycle = current.frontier, current.lifecycle


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
