#!/usr/bin/env python3
"""Boolean integer predicates retain exact tags, source and real retirement."""
import output_final_selected_integer_arithmetic_cast_chain_return_modulo_error_state as current
import output_final_selected_integer_predicate_cast_chain_return_modulo_error_sources as sources

integer, negative, string, cast = current.integer, current.negative, current.string, current.cast
runner, PREFIX, CONJ = current.runner, current.PREFIX, current.CONJ
DETAILS = {context + '-' + variant: (context, variant) for context, variant, _, _, _ in sources.VARIANTS}
CASES = {name: sources.CASES['native-selected-integer-predicate-cast-chain-return-modulo-error-' + name]
         for name in ['deprecated-both-cv-pair-folded-equal-false',
                      'warning-deprecated-constant-float-emitted-lessequal-true',
                      'warning-left-constant-emitted-greater-false']}


def predicate(kind, result, left, right):
    constructor, operator = {
        'identical': ('NExprBinaryOpIdentical', 'IDENTICAL'),
        'notidentical': ('NExprBinaryOpNotIdentical', 'NOTIDENTICAL'),
        'equal': ('NExprBinaryOpEqual', 'EQUAL'),
        'notequal': ('NExprBinaryOpNotEqual', 'NOTEQUAL'),
        'less': ('NExprBinaryOpSmaller', 'LESS'),
        'lessequal': ('NExprBinaryOpSmallerOrEqual', 'LESSEQUAL'),
        'greater': ('NExprBinaryOpGreater', 'GREATER'),
        'greaterequal': ('NExprBinaryOpGreaterOrEqual', 'GREATEREQUAL'),
        'xor': ('NExprBinaryOpLogicalXor', 'LOGICALXOR')}[kind]
    return (constructor, operator, None, result, left[4] and right[4], [left, right])


TREES = {
 'folded-identical-true': cast('bool', 'PBOOL true', cast('int', 'PINT 1',
    predicate('identical', 'PBOOL true', integer(7), integer(7)))),
 'emitted-notidentical-false': cast('float', 'PFLOAT 0', cast('int', 'PINT 0',
    predicate('notidentical', 'PBOOL false', cast('int', 'PINT 7', string('7')), integer(7)))),
 'folded-equal-false': cast('bool', 'PBOOL false', cast('float', 'PFLOAT 0',
    predicate('equal', 'PBOOL false', integer(7), integer(8)))),
 'emitted-notequal-true': cast('int', 'PINT 1', cast('bool', 'PBOOL true',
    predicate('notequal', 'PBOOL true', negative(5), cast('int', 'PINT $(-6)', string('-6'))))),
 'folded-less-true': cast('float', 'PFLOAT 4607182418800017408', cast('int', 'PINT 1',
    predicate('less', 'PBOOL true', negative(5), integer(5)))),
 'emitted-lessequal-true': cast('int', 'PINT 1', cast('bool', 'PBOOL true',
    predicate('lessequal', 'PBOOL true', cast('int', 'PINT 7', string('7')), integer(7)))),
 'emitted-greater-false': cast('int', 'PINT 0', cast('bool', 'PBOOL false',
    predicate('greater', 'PBOOL false', cast('int', 'PINT 1', string('1')), integer(2)))),
 'emitted-greaterequal-true': cast('bool', 'PBOOL true', cast('float', 'PFLOAT 4607182418800017408',
    predicate('greaterequal', 'PBOOL true', cast('int', 'PINT 7', string('7')), integer(7)))),
 'emitted-xor-false': cast('bool', 'PBOOL false', cast('int', 'PINT 0',
    predicate('xor', 'PBOOL false', cast('int', 'PINT 2', string('2')), integer(4))))}


def modulo_line(name):
    source = sources.CASES['native-selected-integer-predicate-cast-chain-return-modulo-error-' + name]
    return sources.modulo_line(DETAILS[name][0], source)


arithmetic_converted = current.converted


def converted(name, condition):
    return arithmetic_converted(name, condition).replace('selected_modulo_integer_arithmetic_cast_chain_return',
                                                       'selected_modulo_integer_predicate_cast_chain_return')


current.DETAILS, current.TREES = DETAILS, TREES
current.modulo_line, current.converted = modulo_line, converted
nodes, expression, root_value = current.nodes, current.expression, current.root_value
frontier, lifecycle = current.frontier, current.lifecycle


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
