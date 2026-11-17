#!/usr/bin/env python3
"""Folded raw signs retain exact values and ownership through nested casts."""
import output_final_selected_nested_scalar_cast_return_modulo_error_state as chains
import output_final_selected_signed_numeric_cast_chain_return_modulo_error_sources as sources

zero, no, prior, runner = chains.zero, chains.no, chains.prior, chains.runner
PREFIX = chains.PREFIX
CASES = {name: sources.CASES['native-selected-signed-numeric-cast-chain-return-modulo-error-' + name]
         for name in ['warning-left-constant', 'warning-right-cv-pair']}
CASTS = {
    'warning-left-constant': [('NExprCastBool', 'CASTBOOL', 1, 'PBOOL false'),
                              ('NExprCastDouble', 'CASTFLOAT', 2, 'PFLOAT 9223372036854775808')],
    'deprecated-both-cv-pair': [('NExprCastBool', 'CASTBOOL', 1, 'PBOOL false'),
                               ('NExprCastInt', 'CASTINT', 1, 'PINT 0')],
    'warning-right-cv-pair': [('NExprCastInt', 'CASTINT', 1, 'PINT 1'),
                             ('NExprCastBool', 'CASTBOOL', 1, 'PBOOL true')],
    'warning-deprecated-constant-float': [('NExprCastDouble', 'CASTFLOAT', 2, 'PFLOAT 4619567317775286272'),
                                         ('NExprCastInt', 'CASTINT', 1, 'PINT 7')]}
SIGNS = {
    'warning-left-constant': ('NExprUnaryMinus', 'NEGATIVE', 'PFLOAT 9223372036854775808'),
    'deprecated-both-cv-pair': ('NExprUnaryPlus', 'POSITIVE', 'PFLOAT 4593671619917905920'),
    'warning-right-cv-pair': ('NExprUnaryMinus', 'NEGATIVE', 'PINT $(-7)'),
    'warning-deprecated-constant-float': ('NExprUnaryPlus', 'POSITIVE', 'PINT 7')}
RAW = {
    'warning-left-constant': ('NScalarFloat (FLOAT text_raw) metadata_raw', 'PFLOAT 0', '0000000000000000'),
    'deprecated-both-cv-pair': ('NScalarFloat (FLOAT text_raw) metadata_raw', 'PFLOAT 4593671619917905920', '3fc0000000000000'),
    'warning-right-cv-pair': ('NScalarInt (INTEGER 7) metadata_raw', 'PINT 7', None),
    'warning-deprecated-constant-float': ('NScalarInt (INTEGER 7) metadata_raw', 'PINT 7', None)}
CONJ = chains.CONJ
slot = chains.slot


def expression(name, index=0):
    if index == len(CASTS[name]):
        return SIGNS[name][0] + ' (' + RAW[name][0] + ') metadata_sign'
    return CASTS[name][index][0] + ' (' + expression(name, index + 1) + ') metadata_' + slot(index)


def root_value(name):
    return CASTS[name][0][3]


def default(name):
    return root_value(name) == 'PBOOL false'


def adapted(name, condition):
    raw = ('NExprConstFetch (NName (BYTES text_false) metadata_false_name) metadata_false'
           if default(name) else 'NScalarInt (INTEGER 0) metadata_zero')
    condition = condition.replace(raw, expression(name))
    if not default(name):
        condition = condition.replace('(PINT 0)', '(' + root_value(name) + ')')
    return condition.replace('_false' if default(name) else '_zero', '_cast')


def converted(name, condition):
    condition = no.converted(name, condition) if default(name) else zero.converted(condition)
    condition = condition.replace('selected_modulo_' + ('false' if default(name) else 'zero') + '_return',
                                  'selected_modulo_signed_numeric_cast_chain_return')
    for state in ['S_handler', 'S_handler_right']:
        condition = condition.replace(state + '.RESULT = KNOWN (PINT 0)',
                                      state + '.RESULT = KNOWN (' + root_value(name) + ')')
    return condition


def return_bindings(name):
    base = no if default(name) else zero
    bindings = [adapted(name, binding) for binding in base.return_bindings(name)]
    bindings += ['$origin_node(S.SOURCES, porigin_cast) = (' + expression(name) + ')']
    for index in range(1, len(CASTS[name])):
        current, parent = slot(index), slot(index - 1)
        bindings += [
            '$origin_child((porigin_' + parent + '), [PCFIELD 0]) = (porigin_' + current + ')',
            'porigin_' + current + ' = PORIGIN n_cast_handler pcpath_' + current,
            '$origin_node(S.SOURCES, porigin_' + current + ') = (' + expression(name, index) + ')',
            '$code_expression(pfunction_handler.CODE.EXPRESSIONS, pcpath_' + current + ') = ((z_' + current + ', b_' + current + '))']
    bindings += [
        '$origin_child((porigin_' + slot(len(CASTS[name]) - 1) + '), [PCFIELD 0]) = (porigin_sign)',
        'porigin_sign = PORIGIN n_cast_handler pcpath_sign',
        '$origin_node(S.SOURCES, porigin_sign) = (' + expression(name, len(CASTS[name])) + ')',
        '$code_expression(pfunction_handler.CODE.EXPRESSIONS, pcpath_sign) = ((z_sign, b_sign))',
        '$origin_child((porigin_sign), [PCFIELD 0]) = (porigin_raw)',
        'porigin_raw = PORIGIN n_cast_handler pcpath_raw',
        '$origin_node(S.SOURCES, porigin_raw) = (' + RAW[name][0] + ')',
        '$code_expression(pfunction_handler.CODE.EXPRESSIONS, pcpath_raw) = ((z_raw, b_raw))']
    return bindings


def return_proof(name):
    base = no if default(name) else zero
    condition = base.return_proof(name)
    if default(name):
        keyword = r'$ptlc($base64(text_false)) = $ptascii("false") /\ '
        assert condition.count(keyword) == 1
        condition = condition.replace(keyword, '')
    condition = adapted(name, condition)
    line = r'z_cast = $source_line(metadata_cast) /\ b_cast /\ '
    assert condition.count(line) == 1
    condition = condition.replace(line, 'z_cast = $expression_line(' + expression(name, 1) + r') /\ ~b_cast /\ ')
    states = ['S_return', 'S', *(['S_return_right'] if prior.two_calls(name) else [])]
    for state in states:
        read = '$compiled_read(' + state + ', porigin_cast) = (' + root_value(name) + ')'
        assert condition.count(read) == 1
        condition = condition.replace(read, '$compiled_read(' + state + ', porigin_cast) = eps')
    parts = [condition, 'S.COMPLETION = NORMAL',
             'pcpath_sign = pcpath_' + slot(len(CASTS[name]) - 1) + ' ++ [PCFIELD 0]',
             'pcpath_raw = pcpath_sign ++ [PCFIELD 0]',
             'z_sign = $expression_line(' + RAW[name][0] + ')', 'b_sign',
             'z_raw = $source_line(metadata_raw)', 'b_raw',
             '$unary_apply(S[.RESULT = KNOWN (' + RAW[name][1] + ')], ' + SIGNS[name][1] + ', ' + RAW[name][1] + ', z_sign) = S[.RESULT = KNOWN (' + SIGNS[name][2] + ')]',
             '$ob_object_cast_chain_value(S, pfunction_handler, porigin_sign, ' + expression(name, len(CASTS[name])) + ') = (' + SIGNS[name][2] + ')',
             '$ob_object_cast_chain_value(S, pfunction_handler, porigin_cast, ' + expression(name) + ') = (' + root_value(name) + ')']
    if RAW[name][2] is not None:
        parts += ['text_raw = "' + RAW[name][2] + '"']
    for index, (_, operator, kind, result) in enumerate(CASTS[name]):
        current = slot(index)
        child = SIGNS[name][2] if index + 1 == len(CASTS[name]) else CASTS[name][index + 1][3]
        parts += ['$plstyle(metadata_' + current + ') = ' + str(kind),
                  '$ob_object_cast_chain_quiet(' + operator + ', ' + child + ')',
                  '$cast_apply(S[.RESULT = KNOWN (' + child + ')], ' + operator + ', ' + child + ', z_' + current + ') = S[.RESULT = KNOWN (' + result + ')]']
        if index:
            parts += ['pcpath_' + current + ' = pcpath_' + slot(index - 1) + ' ++ [PCFIELD 0]',
                      'z_' + current + ' = $expression_line(' + expression(name, index + 1) + ')', '~b_' + current]
            parts += ['$compiled_read(' + state + ', porigin_' + current + ') = eps' for state in states]
    for state in states:
        parts += ['$compiled_read(' + state + ', porigin_sign) = (' + SIGNS[name][2] + ')',
                  '$compiled_read(' + state + ', porigin_raw) = (' + RAW[name][1] + ')']
    return CONJ.join(parts)


def frontier(name, fixture, path):
    bindings, checks = prior.base_for(name).frontier(name, fixture, path)
    bindings += return_bindings(name)
    checks = [(label.replace('NULL', 'signed numeric cast chain'), converted(name, condition)) for label, condition in checks]
    checks += [('actual folded numeric sign and each emitted cast preserve exact typed results and default choice', return_proof(name))]
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = prior.base_for(name).lifecycle(name, fixture, path)
    return bindings + return_bindings(name), [
        *[(label, converted(name, condition)) for label, condition in checks],
        ('exact signed numeric and cast results survive real formal/native-cell retirement', return_proof(name))]


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
