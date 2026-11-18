#!/usr/bin/env python3
"""Coalesce retains nonnull tags or copies the fallback before retirement."""
import base64
import output_final_selected_zero_return_modulo_error_state as zero
import output_final_selected_quiet_coalesce_cast_chain_return_modulo_error_sources as sources

prior, runner = zero.prior, zero.runner
PREFIX = zero.PREFIX.replace('(PINT 0)', 'pvalue_return')
CONJ = r' /\ '
DETAILS = {context + '-' + variant: (context, variant, expected)
           for context, variant, _, _, expected in sources.VARIANTS}
CASES = {name: sources.CASES['native-selected-quiet-coalesce-cast-chain-return-modulo-error-' + name]
         for name in ['warning-left-constant-nonnull-int-zero',
                      'deprecated-both-cv-pair-null-nested-string']}


def nodes(name):
    _, variant, expected = DETAILS[name]
    result_value = {
        'nonnull-int-zero': 'PINT 0', 'nonnull-bool-false': 'PBOOL false',
        'nonnull-float-zero': 'PFLOAT 0',
        'nonnull-empty-string': 'PSTRING_CARRIER INTERNED_STRING eps',
        'null-int': 'PINT 1',
        'null-nested-string': 'PSTRING_CARRIER INTERNED_STRING ($ptascii("0"))',
        'null-cast': 'PINT 1', 'nonnull-negative-int': 'PINT (-1)'}[variant]
    result = {
        'cast': ('NExprCastDouble', 'CASTFLOAT', 2, root_value(name), False, ['cast_1']),
        'cast_1': ('NExprCastInt', 'CASTINT', 1, 'PINT ' + {b'0.0': '0', b'1.0': '1', b'-1.0': '(-1)'}[expected], False, ['value']),
        'value': ('NExprBinaryOpCoalesce', None, None, result_value, False, ['value_left', 'value_right'])}
    if variant in ['nonnull-int-zero', 'nonnull-negative-int']:
        spelling = '-1' if variant == 'nonnull-negative-int' else '0'
        result['value_left'] = ('NExprCastInt', 'CASTINT', 1, result_value, False, ['value_left_child'])
        result['value_left_child'] = ('string', spelling, None,
            'PSTRING_CARRIER INTERNED_STRING ($ptascii("' + spelling + '"))', True, [])
    elif variant in ['nonnull-bool-false', 'nonnull-float-zero']:
        boolean = variant == 'nonnull-bool-false'
        result['value_left'] = ('NExprCastBool' if boolean else 'NExprCastDouble',
            'CASTBOOL' if boolean else 'CASTFLOAT', 1 if boolean else 2, result_value, False, ['value_left_child'])
        result['value_left_child'] = ('integer', '0', None, 'PINT 0', True, [])
    elif variant == 'nonnull-empty-string':
        result['value_left'] = ('string', '', None, result_value, True, [])
    elif variant == 'null-nested-string':
        result['value_left'] = ('NExprBinaryOpCoalesce', None, None, 'PNULL', False, ['value_left_left', 'value_left_right'])
        result['value_left_left'] = ('constant', 'null', None, 'PNULL', True, [])
        result['value_left_right'] = ('constant', 'null', None, 'PNULL', True, [])
    else:
        result['value_left'] = ('constant', 'null', None, 'PNULL', True, [])
    if variant.startswith('nonnull-'):
        result['value_right'] = ('constant', 'UNDEFINED_COALESCE_RIGHT', None, None, False, [])
    elif variant == 'null-int':
        result['value_right'] = ('integer', '1', None, 'PINT 1', True, [])
    elif variant == 'null-nested-string':
        result['value_right'] = ('string', '0', None, result_value, True, [])
    else:
        result['value_right'] = ('NExprCastInt', 'CASTINT', 1, 'PINT 1', False, ['value_right_child'])
        result['value_right_child'] = ('string', '1', None,
            'PSTRING_CARRIER INTERNED_STRING ($ptascii("1"))', True, [])
    return result


def root_value(name):
    return 'PFLOAT ' + {b'0.0': '0', b'1.0': '4607182418800017408',
                       b'-1.0': '13830554455654793216'}[DETAILS[name][2]]


def expression(name, key='cast'):
    kind, spelling, _, _, _, children = nodes(name)[key]
    metadata = 'metadata_' + key
    if kind == 'absent':
        return 'ABSENT'
    if kind == 'constant':
        payload = base64.b64encode(spelling.encode()).decode()
        return 'NExprConstFetch (NName (BYTES "' + payload + '") ' + metadata + '_name) ' + metadata
    if kind == 'string':
        payload = base64.b64encode(spelling.encode()).decode()
        return 'NScalarString (BYTES \"' + payload + '\") ' + metadata
    if kind == 'integer':
        return 'NScalarInt (INTEGER ' + spelling + ') ' + metadata
    if kind == 'float':
        return 'NScalarFloat (FLOAT "' + spelling + '") ' + metadata
    return kind + ' ' + ' '.join('(' + expression(name, child) + ')' for child in children) + ' ' + metadata


def adapted(name, condition):
    return condition.replace('NScalarInt (INTEGER 0) metadata_zero', expression(name)).replace(
        '(PINT 0)', '(' + root_value(name) + ')').replace('_zero', '_cast')


def converted(name, condition):
    return zero.converted(condition).replace('selected_modulo_zero_return', 'selected_modulo_quiet_coalesce_return').replace(
        'S_handler.RESULT = KNOWN (PINT 0)', 'S_handler.RESULT = KNOWN (' + root_value(name) + ')').replace(
        'S_handler_right.RESULT = KNOWN (PINT 0)', 'S_handler_right.RESULT = KNOWN (' + root_value(name) + ')')


def return_bindings(name):
    bindings = [adapted(name, binding) for binding in zero.return_bindings(DETAILS[name][0])]
    bindings += ['$origin_node(S.SOURCES, porigin_cast) = (' + expression(name) + ')']
    for key, node in nodes(name).items():
        for field, child in enumerate(node[5]):
            bindings += ['$origin_child((porigin_' + key + '), [PCFIELD ' + str(field) + ']) = (porigin_' + child + ')',
                         'porigin_' + child + ' = PORIGIN n_cast_handler pcpath_' + child]
            if nodes(name)[child][0] == 'absent':
                bindings += ['$origin_node(S.SOURCES, porigin_' + child + ') = eps']
            else:
                bindings += ['$origin_node(S.SOURCES, porigin_' + child + ') = (' + expression(name, child) + ')',
                             '$code_expression(pfunction_handler.CODE.EXPRESSIONS, pcpath_' + child + ') = ((z_' + child + ', b_' + child + '))']
    return bindings


def return_proof(name):
    context, variant, _ = DETAILS[name]
    condition = adapted(name, zero.return_proof(context))
    condition = condition.replace(r'z_cast = $source_line(metadata_cast) /\ b_cast /\ ', r'z_cast = z_cast_1 /\ ~b_cast /\ ')
    condition = condition.replace('z_cast_return = $source_line(metadata_cast_return)', 'z_cast_return = z_cast')
    states = ['S_return', 'S', *(['S_return_right'] if prior.two_calls(context) else [])]
    for state in states:
        condition = condition.replace('$compiled_read(' + state + ', porigin_cast) = (' + root_value(name) + ')',
                                      '$compiled_read(' + state + ', porigin_cast) = eps')
    parts = [condition, 'S.COMPLETION = NORMAL']
    for key, (kind, operator, style, result, folded, children) in nodes(name).items():
        if kind == 'absent':
            parts += ['$origin_node(S.SOURCES, porigin_' + key + ') = eps',
                      '$code_expression(pfunction_handler.CODE.EXPRESSIONS, pcpath_' + key + ') = eps']
            parts += ['$compiled_read(' + state + ', porigin_' + key + ') = eps' for state in states]
            continue
        if result is None:
            parts += ['~b_' + key, 'z_' + key + ' = $source_line(metadata_' + key + ')',
                      '$ob_object_cast_chain_value(S, pfunction_handler, porigin_' + key + ', ' + expression(name, key) + ') = eps',
                      '$ob_object_cast_chain_skipped_line(S, pfunction_handler, porigin_' + key + ', ' + expression(name, key) + ') = (z_' + key + ')']
            parts += ['$compiled_read(' + state + ', porigin_' + key + ') = eps' for state in states]
            continue
        parts += [('b_' if folded else '~b_') + key,
                  '$ob_object_cast_chain_value(S, pfunction_handler, porigin_' + key + ', ' + expression(name, key) + ') = (' + result + ')',
                  '$value_nodes(' + result + ') = eps']
        pooled = result.replace('PSTRING_CARRIER INTERNED_STRING', 'PSTRING') if kind == 'string' else result
        parts += ['$compiled_read(' + state + ', porigin_' + key + ') = ' + ('(' + pooled + ')' if folded else 'eps') for state in states]
        if not children:
            parts += ['z_' + key + ' = $source_line(metadata_' + key + ')']
            continue
        selected = children[-1]
        parts += ['z_' + key + ' = z_' + selected]
        if kind == 'NExprBinaryOpCoalesce':
            left, right = children
            left_value, right_value = nodes(name)[left][3], nodes(name)[right][3]
            fallback = expression(name, right)
            parts += ['~$coalesce_quiet_operand(' + expression(name, left) + ')',
                      '$compiled_effects(S, porigin_' + key + ') = eps',
                      '$compiled_redirect(S, porigin_' + key + ') = eps']
            plan = '$coalesce_result(S[.ORIGIN = (porigin_' + key + ')][.RESULT = KNOWN (' + left_value + ')], ' + fallback + ', z_' + left + ', z_' + right + ')'
            if left_value != 'PNULL':
                parts += [plan + ' = S[.ORIGIN = (porigin_' + key + ')][.RESULT = KNOWN (' + result + ')][.BASE = BASE_VALUE (KNOWN PNULL)]',
                          '$ob_object_cast_chain_skipped_line(S, pfunction_handler, porigin_' + right + ', ' + fallback + ') = (z_' + right + ')']
            else:
                parts += [plan + ' = S[.ORIGIN = (porigin_' + key + ')][.TODO = [AT porigin_' + right + ' (EVAL (' + fallback + ')), VALUE_COPY z_' + right + '] ++ S.TODO][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
                          '$resolve_at(S[.RESULT = KNOWN (' + right_value + ')], KNOWN (' + right_value + '), z_' + right + ') = S[.RESULT = KNOWN (' + right_value + ')]']
        else:
            child_value = nodes(name)[selected][3]
            parts += ['$plstyle(metadata_' + key + ') = ' + str(style),
                      '$cast_apply(S[.RESULT = KNOWN (' + child_value + ')], ' + operator + ', ' + child_value + ', z_' + key + ') = S[.RESULT = KNOWN (' + result + ')]']
    return CONJ.join(parts)


def frontier(name, fixture, path):
    context = DETAILS[name][0]
    bindings, checks = prior.base_for(context).frontier(context, fixture, path)
    return bindings + return_bindings(name), [*[(label, converted(name, condition)) for label, condition in checks],
        ('strict NULL selection, retained nonnull VALUE or fallback COPY and compiled RIGHT line', return_proof(name))]


def lifecycle(name, fixture, path):
    context = DETAILS[name][0]
    bindings, checks = prior.base_for(context).lifecycle(context, fixture, path)
    return bindings + return_bindings(name), [*[(label, converted(name, condition)) for label, condition in checks],
        ('coalesce raw tags and fallback copies survive real formal/native-cell retirement', return_proof(name))]


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
