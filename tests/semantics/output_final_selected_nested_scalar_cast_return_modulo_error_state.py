#!/usr/bin/env python3
"""Quiet cast chains retain exact typed returns, default choice and retirement."""
import output_final_selected_zero_return_modulo_error_state as zero
import output_final_selected_false_return_modulo_error_state as no
import output_final_selected_nested_scalar_cast_return_modulo_error_sources as sources

prior, runner = zero.prior, zero.runner
PREFIX = zero.PREFIX.replace('(PINT 0)', 'pvalue_return')
CASES = {name: sources.CASES['native-selected-nested-scalar-cast-return-modulo-error-' + name]
         for name in ['warning-left-constant', 'warning-right-cv-pair']}
CASTS = {
    'warning-left-constant': [('NExprCastBool', 'CASTBOOL', 1, 'PBOOL false'),
                              ('NExprCastDouble', 'CASTFLOAT', 2, 'PFLOAT 0')],
    'deprecated-both-cv-pair': [('NExprCastBool', 'CASTBOOL', 1, 'PBOOL false'),
                               ('NExprCastInt', 'CASTINT', 1, 'PINT 0')],
    'warning-right-cv-pair': [('NExprCastInt', 'CASTINT', 1, 'PINT 0'),
                             ('NExprCastBool', 'CASTBOOL', 1, 'PBOOL false')],
    'warning-deprecated-constant-float': [('NExprCastDouble', 'CASTFLOAT', 2, 'PFLOAT 4607182418800017408'),
                                         ('NExprCastInt', 'CASTINT', 1, 'PINT 1'),
                                         ('NExprCastBool', 'CASTBOOL', 1, 'PBOOL true')]}
STRINGS = {'warning-left-constant': 'x', 'deprecated-both-cv-pair': '0.125tail',
           'warning-right-cv-pair': '0', 'warning-deprecated-constant-float': 'x'}
LEAF = 'NScalarString (BYTES text_string) metadata_string'
CONJ = r' /\ '


def slot(index):
    return 'cast' + ('_' + str(index) if index else '')


def expression(name, index=0):
    if index == len(CASTS[name]):
        return LEAF
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
    if default(name):
        return no.converted(name, condition).replace('selected_modulo_false_return',
            'selected_modulo_nested_scalar_cast_return')
    condition = zero.converted(condition).replace('selected_modulo_zero_return',
        'selected_modulo_nested_scalar_cast_return')
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
        '$origin_child((porigin_' + slot(len(CASTS[name]) - 1) + '), [PCFIELD 0]) = (porigin_string)',
        'porigin_string = PORIGIN n_cast_handler pcpath_string',
        '$origin_node(S.SOURCES, porigin_string) = (' + LEAF + ')',
        '$code_expression(pfunction_handler.CODE.EXPRESSIONS, pcpath_string) = ((z_string, b_string))',
        '$evaluate(' + LEAF + ') = VALUE (PSTRING n_string*)']
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
    condition = condition.replace(line,
        'z_cast = $expression_line(' + expression(name, 1) + r') /\ ~b_cast /\ ')
    states = ['S_return', 'S', *(['S_return_right'] if prior.two_calls(name) else [])]
    for state in states:
        read = '$compiled_read(' + state + ', porigin_cast) = (' + root_value(name) + ')'
        assert condition.count(read) == 1
        condition = condition.replace(read, '$compiled_read(' + state + ', porigin_cast) = eps')
    parts = [condition, 'S.COMPLETION = NORMAL',
             'n_string* = $ptascii("' + STRINGS[name] + '")',
             '$base64(text_string) = n_string*', '~(0 <- n_string*)',
             'z_string = $source_line(metadata_string)', 'b_string',
             '$value_nodes(PSTRING_CARRIER INTERNED_STRING n_string*) = eps',
             '$ob_object_cast_chain_value(S, pfunction_handler, porigin_cast, ' + expression(name) + ') = (' + root_value(name) + ')']
    for index, (_, operator, kind, result) in enumerate(CASTS[name]):
        current = slot(index)
        child = ('PSTRING_CARRIER INTERNED_STRING n_string*' if index + 1 == len(CASTS[name])
                 else CASTS[name][index + 1][3])
        parts += ['$plstyle(metadata_' + current + ') = ' + str(kind),
                  '$ob_object_cast_chain_quiet(' + operator + ', ' + child + ')',
                  '$cast_apply(S[.RESULT = KNOWN (' + child + ')], ' + operator + ', ' + child + ', z_' + current + ') = S[.RESULT = KNOWN (' + result + ')]']
        if index:
            parts += ['pcpath_' + current + ' = pcpath_' + slot(index - 1) + ' ++ [PCFIELD 0]',
                      'z_' + current + ' = $expression_line(' + expression(name, index + 1) + ')',
                      '~b_' + current]
            parts += ['$compiled_read(' + state + ', porigin_' + current + ') = eps' for state in states]
    parts += ['pcpath_string = pcpath_' + slot(len(CASTS[name]) - 1) + ' ++ [PCFIELD 0]']
    for state in states:
        parts += ['$compiled_read(' + state + ', porigin_string) = (PSTRING n_string*)',
                  '$compiled_string_value(' + state + ', porigin_string, PSTRING n_string*) = PSTRING_CARRIER INTERNED_STRING n_string*']
    return CONJ.join(parts)


def frontier(name, fixture, path):
    bindings, checks = prior.base_for(name).frontier(name, fixture, path)
    bindings += return_bindings(name)
    checks = [(label.replace('NULL', 'nested scalar cast'), converted(name, condition))
              for label, condition in checks]
    checks += [('proper emitted cast links preserve intrinsic quietness, exact typed values and strict fallback choice',
                return_proof(name))]
    assert not any('pobobjectreturn_seed' in binding for binding in bindings)
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = prior.base_for(name).lifecycle(name, fixture, path)
    return bindings + return_bindings(name), [
        *[(label, converted(name, condition)) for label, condition in checks],
        ('the quiet chain and typed default choice survive actual formal and native-cell retirement', return_proof(name))]


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
