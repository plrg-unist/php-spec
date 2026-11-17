#!/usr/bin/env python3
"""Proper primitive predicates retain exact typed results and real retirement."""
import base64
import output_final_selected_integer_predicate_cast_chain_return_modulo_error_state as prior
import output_final_selected_primitive_predicate_cast_chain_return_modulo_error_sources as sources

current = prior.current
integer, string, cast, predicate = current.integer, current.string, current.cast, prior.predicate
runner, PREFIX, CONJ = current.runner, current.PREFIX, current.CONJ
DETAILS = {context + '-' + variant: (context, variant) for context, variant, _, _, _ in sources.VARIANTS}
CASES = {name: sources.CASES['native-selected-primitive-predicate-cast-chain-return-modulo-error-' + name]
         for name in ['deprecated-both-cv-pair-folded-string-int-equal-false',
                      'warning-deprecated-constant-float-emitted-float-int-lessequal-false',
                      'warning-deprecated-constant-float-emitted-string-int-greaterequal-true']}


def constant(name):
    return ('constant', name, None, {'null': 'PNULL', 'false': 'PBOOL false', 'true': 'PBOOL true'}[name], True, [])


TREES = {
 'folded-bool-identical-true': cast('bool', 'PBOOL true', cast('int', 'PINT 1',
    predicate('identical', 'PBOOL true',
              predicate('identical', 'PBOOL true', integer(7), integer(7)),
              predicate('identical', 'PBOOL true', integer(8), integer(8))))),
 'emitted-bool-int-notidentical-true': cast('float', 'PFLOAT 4607182418800017408', cast('int', 'PINT 1',
    predicate('notidentical', 'PBOOL true', cast('bool', 'PBOOL true', cast('int', 'PINT 1', integer(1))), integer(1)))),
 'folded-string-int-equal-false': cast('bool', 'PBOOL false', cast('float', 'PFLOAT 0',
    predicate('equal', 'PBOOL false', string('seven'), integer(0)))),
 'folded-null-bool-notequal-false': cast('int', 'PINT 0', cast('bool', 'PBOOL false',
    predicate('notequal', 'PBOOL false', constant('null'), constant('false')))),
 'folded-null-string-less-true': cast('float', 'PFLOAT 4607182418800017408', cast('int', 'PINT 1',
    predicate('less', 'PBOOL true', constant('null'), string('0')))),
 'emitted-float-int-lessequal-false': cast('int', 'PINT 0', cast('bool', 'PBOOL false',
    predicate('lessequal', 'PBOOL false', cast('float', 'PFLOAT 4607182418800017408', integer(1)), integer(0)))),
 'folded-numeric-strings-greater-true': cast('int', 'PINT 1', cast('bool', 'PBOOL true',
    predicate('greater', 'PBOOL true', string('10'), string('2')))),
 'emitted-string-int-greaterequal-true': cast('bool', 'PBOOL true', cast('float', 'PFLOAT 4607182418800017408',
    predicate('greaterequal', 'PBOOL true', string('a'), cast('int', 'PINT 99', string('99'))))),
 'emitted-string-bool-xor-false': cast('bool', 'PBOOL false', cast('int', 'PINT 0',
    predicate('xor', 'PBOOL false', string('0'), cast('bool', 'PBOOL false', integer(0)))))}


def expression(name, key='cast'):
    kind, spelling, _, _, _, _ = current.nodes(name)[key]
    metadata = 'metadata_' + key
    if kind == 'integer':
        return 'NScalarInt (INTEGER ' + spelling + ') ' + metadata
    if kind == 'string':
        return 'NScalarString (BYTES text_' + key + ') ' + metadata
    if kind == 'constant':
        payload = base64.b64encode(spelling.encode()).decode()
        return 'NExprConstFetch (NName (BYTES "' + payload + '") ' + metadata + '_name) ' + metadata
    return kind + ' ' + ' '.join('(' + expression(name, child) + ')' for child, _ in current.children(key, current.nodes(name)[key])) + ' ' + metadata


def modulo_line(name):
    source = sources.CASES['native-selected-primitive-predicate-cast-chain-return-modulo-error-' + name]
    return sources.modulo_line(DETAILS[name][0], source)


predicate_converted = current.converted


def converted(name, condition):
    return predicate_converted(name, condition).replace('selected_modulo_integer_predicate_cast_chain_return',
                                                      'selected_modulo_primitive_predicate_cast_chain_return')


current.DETAILS, current.TREES = DETAILS, TREES
current.modulo_line, current.converted, current.expression = modulo_line, converted, expression
nodes, root_value = current.nodes, current.root_value
frontier, lifecycle = current.frontier, current.lifecycle


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
