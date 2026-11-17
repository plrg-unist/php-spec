#!/usr/bin/env python3
"""Parser CONCAT owns one compiled entry; its raw children have no CODE."""
import base64
import output_final_selected_terminal_line_bitwise_cast_chain_return_modulo_error_state as prior
import output_final_selected_parser_string_concat_cast_chain_return_modulo_error_sources as sources

zero, no, scaffold, runner = prior.zero, prior.no, prior.prior, prior.runner
PREFIX, CONJ = prior.PREFIX, prior.CONJ
DETAILS = {context + '-' + variant: (context, variant) for context, variant, _, _, _ in sources.VARIANTS}
CASES = {name: sources.CASES['native-selected-parser-string-concat-cast-chain-return-modulo-error-' + name]
         for name in ['warning-left-constant-right-empty-one', 'warning-left-constant-nested-twelve',
                      'deprecated-both-cv-pair-empty']}
TREES = {'right-empty-one': (b'1', b''), 'multiline-twenty': (b'2', b'0'),
         'left-empty-zero': (b'', b'0'), 'nested-twelve': ((b'1', b'2'), b''),
         'high-byte': (b'\xff', b'x'), 'empty': (b'', b'')}
CASTS = {'right-empty-one': [('NExprCastDouble', 'CASTFLOAT', 2, 'PFLOAT 4607182418800017408'), ('NExprCastInt', 'CASTINT', 1, 'PINT 1')],
         'multiline-twenty': [('NExprCastBool', 'CASTBOOL', 1, 'PBOOL true'), ('NExprCastDouble', 'CASTFLOAT', 2, 'PFLOAT 4626322717216342016')],
         'left-empty-zero': [('NExprCastInt', 'CASTINT', 1, 'PINT 0'), ('NExprCastBool', 'CASTBOOL', 1, 'PBOOL false')],
         'nested-twelve': [('NExprCastDouble', 'CASTFLOAT', 2, 'PFLOAT 4622945017495814144'), ('NExprCastInt', 'CASTINT', 1, 'PINT 12')],
         'high-byte': [('NExprCastInt', 'CASTINT', 1, 'PINT 1'), ('NExprCastBool', 'CASTBOOL', 1, 'PBOOL true')],
         'empty': [('NExprCastBool', 'CASTBOOL', 1, 'PBOOL false'), ('NExprCastInt', 'CASTINT', 1, 'PINT 0')]}


def tree(name):
    return TREES[DETAILS[name][1]]


def nodes(name):
    result = {}
    def visit(key, node):
        result[key] = node
        if isinstance(node, tuple):
            visit(key + '_left', node[0]); visit(key + '_right', node[1])
    visit('value', tree(name))
    return result


def raw(node):
    return raw(node[0]) + raw(node[1]) if isinstance(node, tuple) else node


def data(value):
    return '(' + (('[' + ', '.join(map(str, value)) + ']') if value else 'eps') + ')'


def plain(name):
    return 'PSTRING ' + data(raw(tree(name)))


def carrier(name):
    return 'PSTRING_CARRIER INTERNED_STRING ' + data(raw(tree(name)))


def expression(name, key='cast'):
    if key in ('cast', 'cast_1'):
        index = 0 if key == 'cast' else 1
        return CASTS[DETAILS[name][1]][index][0] + ' (' + expression(name, 'cast_1' if index == 0 else 'value') + ') metadata_' + key
    node = nodes(name)[key]
    if isinstance(node, tuple):
        return 'NExprBinaryOpConcat (' + expression(name, key + '_left') + ') (' + expression(name, key + '_right') + ') metadata_' + key
    return 'NScalarString (BYTES "' + base64.b64encode(node).decode() + '") metadata_' + key


def root_value(name):
    return CASTS[DETAILS[name][1]][0][3]


def default(name):
    return root_value(name) == 'PBOOL false'


def modulo_line(name):
    return sources.modulo_line(DETAILS[name][0], sources.CASES['native-selected-parser-string-concat-cast-chain-return-modulo-error-' + name])


def adapted(name, condition):
    old = ('NExprConstFetch (NName (BYTES text_false) metadata_false_name) metadata_false'
           if default(name) else 'NScalarInt (INTEGER 0) metadata_zero')
    condition = condition.replace(old, expression(name))
    if not default(name):
        condition = condition.replace('(PINT 0)', '(' + root_value(name) + ')')
    return condition.replace('_false' if default(name) else '_zero', '_cast')


def source_lines(name, condition):
    old, line = (8 if 'cv-pair' in DETAILS[name][0] else 6), modulo_line(name)
    for fact in ['z = {line}', 'z_left = {line}', 'z_right = {line}',
                 'S_request.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Modulo by zero")) {line}',
                 '$code_expression_at_source(S, porigin_operator, [PCFIELD 0]) = ({line})',
                 '$code_expression_at_source(S, porigin_operator, [PCFIELD 1]) = ({line})']:
        condition = condition.replace(fact.format(line=old), fact.format(line=line))
    if default(name):
        for event in no.diagnostics(DETAILS[name][0]):
            condition = condition.replace(event, event.rsplit(' ', 1)[0] + ' ' + str(line))
    return condition


def converted(name, condition):
    condition = no.converted(DETAILS[name][0], condition) if default(name) else zero.converted(condition)
    condition = condition.replace('selected_modulo_' + ('false' if default(name) else 'zero') + '_return',
                                  sources.function_name(DETAILS[name][1]))
    for state in ['S_handler', 'S_handler_right']:
        condition = condition.replace(state + '.RESULT = KNOWN (PINT 0)', state + '.RESULT = KNOWN (' + root_value(name) + ')')
    return source_lines(name, condition)


def parser_bindings(name):
    bindings = []
    for key in nodes(name):
        if key == 'value':
            continue
        parent, field = key.rsplit('_', 1)
        bindings += ['$origin_child((porigin_' + parent + '), [PCFIELD ' + ('0' if field == 'left' else '1') + ']) = (porigin_' + key + ')',
                     'porigin_' + key + ' = PORIGIN n_cast_handler pcpath_' + key,
                     '$origin_node(S.SOURCES, porigin_' + key + ') = (' + expression(name, key) + ')']
    return bindings


def return_bindings(name):
    base = no if default(name) else zero
    bindings = [adapted(name, binding) for binding in base.return_bindings(DETAILS[name][0])]
    bindings += ['$origin_node(S.SOURCES, porigin_cast) = (' + expression(name) + ')']
    for parent, key in [('cast', 'cast_1'), ('cast_1', 'value')]:
        bindings += ['$origin_child((porigin_' + parent + '), [PCFIELD 0]) = (porigin_' + key + ')',
                     'porigin_' + key + ' = PORIGIN n_cast_handler pcpath_' + key,
                     '$origin_node(S.SOURCES, porigin_' + key + ') = (' + expression(name, key) + ')',
                     '$code_expression(pfunction_handler.CODE.EXPRESSIONS, pcpath_' + key + ') = ((z_' + key + ', b_' + key + '))']
    return bindings + parser_bindings(name) + ['$source_precision(S, (porigin_value)) = (z_parser)']


def parser_proof(name):
    value, result = plain(name), carrier(name)
    parts = ['S.COMPLETION = NORMAL', 'b_value', 'z_value = $concat_line(metadata_value)', '$(z_value > 0)',
             '$source_precision(S, (porigin_value)) = (z_parser)',
             '$parser_literal_at(' + expression(name, 'value') + ', z_parser) = (' + value + ')',
             '$compiled_read(S, porigin_value) = (' + value + ')', '$compiled_effects(S, porigin_value) = eps',
             '$compiled_string_value(S, porigin_value, ' + value + ') = ' + result,
             '$enter_compiled_task(S, porigin_value, EVAL (' + expression(name, 'value') + '), S.TODO) = S[.RESULT = KNOWN (' + result + ')]',
             '$value_nodes(' + result + ') = eps']
    for key in nodes(name):
        if key != 'value':
            parts += ['$code_expression(pfunction_handler.CODE.EXPRESSIONS, pcpath_' + key + ') = eps',
                      '$compiled_read(S, porigin_' + key + ') = eps']
    return CONJ.join(parts)


def return_proof(name):
    condition = (no if default(name) else zero).return_proof(DETAILS[name][0])
    if default(name):
        condition = condition.replace(r'$ptlc($base64(text_false)) = $ptascii("false") /\ ', '')
    condition = source_lines(name, adapted(name, condition))
    condition = condition.replace(r'z_cast = $source_line(metadata_cast) /\ b_cast /\ ', r'z_cast = z_cast_1 /\ ~b_cast /\ ')
    condition = condition.replace('z_cast_return = $source_line(metadata_cast_return)', 'z_cast_return = z_cast')
    for state in ['S_return', 'S', *(['S_return_right'] if scaffold.two_calls(DETAILS[name][0]) else [])]:
        condition = condition.replace('$compiled_read(' + state + ', porigin_cast) = (' + root_value(name) + ')', '$compiled_read(' + state + ', porigin_cast) = eps')
    parts = [condition, parser_proof(name), '~b_cast_1', 'z_cast_1 = z_value']
    casts = CASTS[DETAILS[name][1]]
    for index, key in enumerate(['cast', 'cast_1']):
        _, operator, style, result = casts[index]
        child = casts[1][3] if index == 0 else carrier(name)
        parts += ['$plstyle(metadata_' + key + ') = ' + str(style),
                  '$ob_object_cast_chain_value(S, pfunction_handler, porigin_' + key + ', ' + expression(name, key) + ') = (' + result + ')',
                  '$cast_apply(S[.RESULT = KNOWN (' + child + ')], ' + operator + ', ' + child + ', z_' + key + ') = S[.RESULT = KNOWN (' + result + ')]',
                  '$value_nodes(' + result + ') = eps']
    parts += ['$ob_object_cast_chain_value(S, pfunction_handler, porigin_value, ' + expression(name, 'value') + ') = (' + carrier(name) + ')']
    return CONJ.join(parts)


def frontier(name, fixture, path):
    bindings, checks = scaffold.base_for(DETAILS[name][0]).frontier(DETAILS[name][0], fixture, path)
    return bindings + return_bindings(name), [*[(label, converted(name, condition)) for label, condition in checks],
        ('own parser STRING entry, skipped child CODE and exact scalar casts retain source authority', return_proof(name))]


def lifecycle(name, fixture, path):
    bindings, checks = scaffold.base_for(DETAILS[name][0]).lifecycle(DETAILS[name][0], fixture, path)
    old, line = (8 if 'cv-pair' in DETAILS[name][0] else 6), modulo_line(name)
    def fatal(number):
        return b'Fatal error: Uncaught DivisionByZeroError: Modulo by zero in ' + bytes(path) + b':' + str(number).encode() + b'\nStack trace:\n#0 [internal function]: T->__toString()\n#1 {main}\n  thrown in ' + bytes(path) + b' on line ' + str(number).encode() + b'\n'
    label, condition = checks[2]
    pending = 'pobdeactivate.COMPLETION = REQUESTFATAL ($ptascii("DivisionByZeroError")) ' + scaffold.prior.value(b'Modulo by zero')
    checks[2] = (label, condition.replace(scaffold.prior.value(fatal(old)), scaffold.prior.value(fatal(line))).replace(pending + ' ' + str(old), pending + ' ' + str(line)))
    return bindings + return_bindings(name), [*[(label, converted(name, condition)) for label, condition in checks],
        ('parser STRING identity and both casts survive actual formal/native-cell retirement', return_proof(name))]


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
