#!/usr/bin/env python3
"""Compiler-derived NOT certificates preserve typed returns and real retirement."""
import output_final_selected_nested_scalar_cast_return_modulo_error_state as chains
import output_final_selected_certified_not_cast_chain_return_modulo_error_sources as sources

zero, no, prior, runner = chains.zero, chains.no, chains.prior, chains.runner
PREFIX, CONJ = chains.PREFIX, chains.CONJ
DETAILS = {context + '-' + variant: (context, variant) for context, variant, _, _ in sources.VARIANTS}
CASES = {name: sources.CASES['native-selected-certified-not-cast-chain-return-modulo-error-' + name]
         for name in ['warning-right-cv-pair-string-zero', 'warning-left-constant-emitted-int',
                      'deprecated-both-cv-pair-folded-nested']}
# AST kind, operation/leaf spelling, cast style, exact result, compiler-folded flag.
NODES = {
    'keyword-false': [('NExprCastBool', 'CASTBOOL', 1, 'PBOOL true', False),
                      ('NExprCastInt', 'CASTINT', 1, 'PINT 1', False),
                      ('NExprBooleanNot', None, None, 'PBOOL true', True),
                      ('keyword', 'false', None, 'PBOOL false', True)],
    'keyword-null': [('NExprCastBool', 'CASTBOOL', 1, 'PBOOL true', False),
                     ('NExprCastDouble', 'CASTFLOAT', 2, 'PFLOAT 4607182418800017408', False),
                     ('NExprBooleanNot', None, None, 'PBOOL true', True),
                     ('keyword', 'null', None, 'PNULL', True)],
    'string-zero': [('NExprCastInt', 'CASTINT', 1, 'PINT 1', False),
                    ('NExprCastBool', 'CASTBOOL', 1, 'PBOOL true', False),
                    ('NExprBooleanNot', None, None, 'PBOOL true', True),
                    ('string', '0', None, 'PSTRING_CARRIER INTERNED_STRING ($ptascii("0"))', True)],
    'string-truthy': [('NExprCastDouble', 'CASTFLOAT', 2, 'PFLOAT 0', False),
                      ('NExprCastInt', 'CASTINT', 1, 'PINT 0', False),
                      ('NExprBooleanNot', None, None, 'PBOOL false', True),
                      ('string', 'x', None, 'PSTRING_CARRIER INTERNED_STRING ($ptascii("x"))', True)],
    'emitted-int': [('NExprCastBool', 'CASTBOOL', 1, 'PBOOL true', False),
                    ('NExprCastInt', 'CASTINT', 1, 'PINT 1', False),
                    ('NExprBooleanNot', None, None, 'PBOOL true', False),
                    ('NExprCastInt', 'CASTINT', 1, 'PINT 0', False),
                    ('string', '0', None, 'PSTRING_CARRIER INTERNED_STRING ($ptascii("0"))', True)],
    'folded-nested': [('NExprCastBool', 'CASTBOOL', 1, 'PBOOL false', False),
                      ('NExprCastDouble', 'CASTFLOAT', 2, 'PFLOAT 0', False),
                      ('NExprBooleanNot', None, None, 'PBOOL false', True),
                      ('NExprBooleanNot', None, None, 'PBOOL true', True),
                      ('keyword', 'false', None, 'PBOOL false', True)],
    'emitted-nested': [('NExprCastInt', 'CASTINT', 1, 'PINT 0', False),
                       ('NExprCastBool', 'CASTBOOL', 1, 'PBOOL false', False),
                       ('NExprBooleanNot', None, None, 'PBOOL false', False),
                       ('NExprBooleanNot', None, None, 'PBOOL true', False),
                       ('NExprCastInt', 'CASTINT', 1, 'PINT 0', False),
                       ('string', 'x', None, 'PSTRING_CARRIER INTERNED_STRING ($ptascii("x"))', True)]}


def nodes(name):
    return NODES[DETAILS[name][1]]


def slot(index):
    return ['cast', 'cast_1', 'not'][index] if index < 3 else 'child_' + str(index)


def expression(name, index=0):
    kind, spelling, _, _, _ = nodes(name)[index]
    metadata = 'metadata_' + slot(index)
    if kind == 'keyword':
        return 'NExprConstFetch (NName (BYTES text_leaf) metadata_leaf_name) ' + metadata
    if kind == 'string':
        return 'NScalarString (BYTES text_leaf) ' + metadata
    return kind + ' (' + expression(name, index + 1) + ') ' + metadata


def root_value(name):
    return nodes(name)[0][3]


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
    context = DETAILS[name][0]
    condition = no.converted(context, condition) if default(name) else zero.converted(condition)
    condition = condition.replace('selected_modulo_' + ('false' if default(name) else 'zero') + '_return',
                                  'selected_modulo_certified_not_cast_chain_return')
    for state in ['S_handler', 'S_handler_right']:
        condition = condition.replace(state + '.RESULT = KNOWN (PINT 0)',
                                      state + '.RESULT = KNOWN (' + root_value(name) + ')')
    return condition


def return_bindings(name):
    base = no if default(name) else zero
    bindings = [adapted(name, binding) for binding in base.return_bindings(DETAILS[name][0])]
    bindings += ['$origin_node(S.SOURCES, porigin_cast) = (' + expression(name) + ')']
    for index in range(1, len(nodes(name))):
        current, parent = slot(index), slot(index - 1)
        bindings += [
            '$origin_child((porigin_' + parent + '), [PCFIELD 0]) = (porigin_' + current + ')',
            'porigin_' + current + ' = PORIGIN n_cast_handler pcpath_' + current,
            '$origin_node(S.SOURCES, porigin_' + current + ') = (' + expression(name, index) + ')',
            '$code_expression(pfunction_handler.CODE.EXPRESSIONS, pcpath_' + current + ') = ((z_' + current + ', b_' + current + '))']
    if nodes(name)[-1][0] == 'keyword':
        bindings += ['$origin_child((porigin_' + slot(len(nodes(name)) - 1) + '), [PCFIELD 0]) = (porigin_leaf_name)',
                     '$origin_node(S.SOURCES, porigin_leaf_name) = (NName (BYTES text_leaf) metadata_leaf_name)']
    return bindings


def return_proof(name):
    context = DETAILS[name][0]
    base = no if default(name) else zero
    condition = base.return_proof(context)
    if default(name):
        keyword = r'$ptlc($base64(text_false)) = $ptascii("false") /\ '
        assert condition.count(keyword) == 1
        condition = condition.replace(keyword, '')
    condition = adapted(name, condition)
    line = r'z_cast = $source_line(metadata_cast) /\ b_cast /\ '
    assert condition.count(line) == 1
    condition = condition.replace(line, 'z_cast = $expression_line(' + expression(name, 1) + r') /\ ~b_cast /\ ')
    states = ['S_return', 'S', *(['S_return_right'] if prior.two_calls(context) else [])]
    for state in states:
        read = '$compiled_read(' + state + ', porigin_cast) = (' + root_value(name) + ')'
        assert condition.count(read) == 1
        condition = condition.replace(read, '$compiled_read(' + state + ', porigin_cast) = eps')
    parts = [condition, 'S.COMPLETION = NORMAL']
    for index, (kind, operator, style, result, folded) in enumerate(nodes(name)):
        current = slot(index)
        parts += [('b_' if folded else '~b_') + current,
                  '$ob_object_cast_chain_value(S, pfunction_handler, porigin_' + current + ', ' + expression(name, index) + ') = (' + result + ')']
        if index:
            parts += ['pcpath_' + current + ' = pcpath_' + slot(index - 1) + ' ++ [PCFIELD 0]']
        cache = result
        if kind == 'string':
            cache = 'PSTRING ($ptascii("' + operator + '"))'
            parts += ['$base64(text_leaf) = $ptascii("' + operator + '")',
                      '$value_nodes(' + result + ') = eps']
            for state in states:
                parts += ['$compiled_string_value(' + state + ', porigin_' + current + ', ' + cache + ') = ' + result]
        elif kind == 'keyword':
            parts += ['$ptlc($base64(text_leaf)) = $ptascii("' + operator + '")']
        for state in states:
            parts += ['$compiled_read(' + state + ', porigin_' + current + ') = ' + ('(' + cache + ')' if folded else 'eps')]
        if kind in ('string', 'keyword'):
            parts += ['z_' + current + ' = $source_line(metadata_' + current + ')']
            continue
        child = nodes(name)[index + 1][3]
        parts += ['z_' + current + ' = $expression_line(' + expression(name, index + 1) + ')']
        if kind == 'NExprBooleanNot':
            parts += ['$ob_object_cast_chain_quiet(CASTBOOL, ' + child + ')',
                      '$boolean_result(S[.RESULT = KNOWN (' + child + ')], true, z_' + current + ') = S[.RESULT = KNOWN (' + result + ')]']
        else:
            parts += ['$plstyle(metadata_' + current + ') = ' + str(style),
                      '$ob_object_cast_chain_quiet(' + operator + ', ' + child + ')',
                      '$cast_apply(S[.RESULT = KNOWN (' + child + ')], ' + operator + ', ' + child + ', z_' + current + ') = S[.RESULT = KNOWN (' + result + ')]']
    return CONJ.join(parts)


def frontier(name, fixture, path):
    bindings, checks = prior.base_for(DETAILS[name][0]).frontier(DETAILS[name][0], fixture, path)
    checks = [(label.replace('NULL', 'certified NOT chain'), converted(name, condition)) for label, condition in checks]
    return bindings + return_bindings(name), checks + [
        ('actual compiler flags, raw facts, typed NOT/cast states and strict fallback remain exact', return_proof(name))]


def lifecycle(name, fixture, path):
    bindings, checks = prior.base_for(DETAILS[name][0]).lifecycle(DETAILS[name][0], fixture, path)
    return bindings + return_bindings(name), [
        *[(label, converted(name, condition)) for label, condition in checks],
        ('the certified child and strict result survive actual formal/native-cell retirement', return_proof(name))]


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
