#!/usr/bin/env python3
"""Shorthand ternaries retain raw condition tags, fallback copies and retirement."""
import base64
import output_final_selected_zero_return_modulo_error_state as zero
import output_final_selected_emitted_condition_shorthand_ternary_cast_chain_return_modulo_error_sources as sources

prior, runner = zero.prior, zero.runner
PREFIX = zero.PREFIX.replace('(PINT 0)', 'pvalue_return')
CONJ = r' /\ '
DETAILS = {context + '-' + variant: (context, variant, expected)
           for context, variant, _, _, expected in sources.VARIANTS}
CASES = {name: sources.CASES['native-selected-emitted-condition-shorthand-ternary-cast-chain-return-modulo-error-' + name]
         for name in ['warning-left-constant-false-string',
                      'warning-deprecated-constant-float-truthy-negative']}


def nodes(name):
    _, variant, expected = DETAILS[name]
    result_value = {'truthy-int': 'PINT 1', 'truthy-float': 'PFLOAT 4607182418800017408',
                    'truthy-bool': 'PBOOL true', 'false-int': 'PINT 0',
                    'false-string': 'PSTRING_CARRIER INTERNED_STRING ($ptascii("1"))',
                    'false-null': 'PNULL', 'false-cast': 'PINT 1', 'truthy-negative': 'PINT (-1)'}[variant]
    result = {
        'cast': ('NExprCastDouble', 'CASTFLOAT', 2, root_value(name), False, ['cast_1']),
        'cast_1': ('NExprCastInt', 'CASTINT', 1, 'PINT ' + {b'0.0': '0', b'1.0': '1', b'-1.0': '(-1)'}[expected], False, ['value']),
        'value': ('NExprTernary', None, None, result_value, False, ['value_cond', 'value_true', 'value_false']),
        'value_true': ('absent', None, None, None, None, [])}
    if variant in ['truthy-int', 'false-int', 'truthy-negative']:
        text = {'truthy-int': '1', 'false-int': '0', 'truthy-negative': '-1'}[variant]
        result['value_cond'] = ('NExprCastInt', 'CASTINT', 1, 'PINT ' + ('(-1)' if text == '-1' else text), False, ['value_cond_child'])
        result['value_cond_child'] = ('string', text, None,
            'PSTRING_CARRIER INTERNED_STRING ($ptascii("' + text + '"))', True, [])
    else:
        truth = variant.startswith('truthy-')
        boolean = variant in ['truthy-bool', 'false-null']
        typed = 'PBOOL ' + str(truth).lower() if boolean else 'PFLOAT ' + ('4607182418800017408' if truth else '0')
        result['value_cond'] = ('NExprCastBool' if boolean else 'NExprCastDouble',
            'CASTBOOL' if boolean else 'CASTFLOAT', 1 if boolean else 2, typed, False, ['value_cond_child'])
        result['value_cond_child'] = ('integer', str(int(truth)), None, 'PINT ' + str(int(truth)), True, [])
    if variant.startswith('truthy-'):
        result['value_false'] = ('constant', 'UNDEFINED_SHORTHAND_FALSE', None, None, False, [])
    elif variant == 'false-int':
        result['value_false'] = ('integer', '0', None, 'PINT 0', True, [])
    elif variant == 'false-string':
        result['value_false'] = ('string', '1', None, result_value, True, [])
    elif variant == 'false-null':
        result['value_false'] = ('constant', 'null', None, 'PNULL', True, [])
    else:
        result['value_false'] = ('NExprCastInt', 'CASTINT', 1, 'PINT 1', False, ['value_false_child'])
        result['value_false_child'] = ('string', '1', None,
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
    return zero.converted(condition).replace('selected_modulo_zero_return', 'selected_modulo_emitted_condition_shorthand_ternary_return').replace(
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
        if key == 'value':
            truth = variant.startswith('truthy-')
            cond, fallback = nodes(name)['value_cond'][3], expression(name, 'value_false')
            parts += ['$ob_object_cast_chain_quiet(CASTBOOL, ' + cond + ')',
                      '$boolean_result(S[.RESULT = KNOWN (' + cond + ')], false, z_value_cond) = S[.RESULT = KNOWN (PBOOL ' + str(truth).lower() + ')]',
                      '$compiled_effects(S, porigin_value) = eps', '$compiled_redirect(S, porigin_value) = eps']
            plan = '$selected_branch(S[.ORIGIN = (porigin_value)][.RESULT = KNOWN (PBOOL ' + str(truth).lower() + ')], ABSENT, ' + fallback + ', ' + cond + ', 0, z_value_false)'
            if truth:
                parts += [plan + ' = S[.ORIGIN = (porigin_value)][.RESULT = KNOWN (' + result + ')][.BASE = BASE_VALUE (KNOWN PNULL)]',
                          '$ob_object_cast_chain_skipped_line(S, pfunction_handler, porigin_value_false, ' + fallback + ') = (z_value_false)']
            else:
                parts += [plan + ' = S[.ORIGIN = (porigin_value)][.TODO = [AT porigin_value_false (EVAL (' + fallback + ')), VALUE_COPY z_value_false] ++ S.TODO][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
                          '$resolve_at(S[.RESULT = KNOWN (' + result + ')], KNOWN (' + result + '), z_value_false) = S[.RESULT = KNOWN (' + result + ')]']
        else:
            child_value = nodes(name)[selected][3]
            parts += ['$plstyle(metadata_' + key + ') = ' + str(style),
                      '$cast_apply(S[.RESULT = KNOWN (' + child_value + ')], ' + operator + ', ' + child_value + ', z_' + key + ') = S[.RESULT = KNOWN (' + result + ')]']
    return CONJ.join(parts)


def frontier(name, fixture, path):
    context = DETAILS[name][0]
    bindings, checks = prior.base_for(context).frontier(context, fixture, path)
    return bindings + return_bindings(name), [*[(label, converted(name, condition)) for label, condition in checks],
        ('proper emitted condition, absent TRUE source/code, raw retained VALUE or fallback COPY and FALSE line', return_proof(name))]


def lifecycle(name, fixture, path):
    context = DETAILS[name][0]
    bindings, checks = prior.base_for(context).lifecycle(context, fixture, path)
    return bindings + return_bindings(name), [*[(label, converted(name, condition)) for label, condition in checks],
        ('shorthand raw tags and fallback copies survive real formal/native-cell retirement', return_proof(name))]


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
