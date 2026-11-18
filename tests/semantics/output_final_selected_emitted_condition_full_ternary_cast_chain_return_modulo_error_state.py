#!/usr/bin/env python3
"""Full ternaries retain selected VALUE tags, compiler lines and real retirement."""
import base64
import output_final_selected_zero_return_modulo_error_state as zero
import output_final_selected_emitted_condition_full_ternary_cast_chain_return_modulo_error_sources as sources

prior, runner = zero.prior, zero.runner
PREFIX = zero.PREFIX.replace('(PINT 0)', 'pvalue_return')
CONJ = r' /\ '
DETAILS = {context + '-' + variant: (context, variant, expected)
           for context, variant, _, _, expected in sources.VARIANTS}
CASES = {name: sources.CASES['native-selected-emitted-condition-full-ternary-cast-chain-return-modulo-error-' + name]
         for name in ['warning-left-constant-false-constant',
                      'warning-deprecated-constant-float-true-string']}


def nodes(name):
    _, variant, expected = DETAILS[name]
    one, truth = expected == b'1.0', variant.startswith('true-')
    selected = {'false-constant': 'PINT 0', 'true-constant': 'PINT 1',
                'false-float': 'PFLOAT 0', 'true-bool': 'PBOOL true',
                'false-cast': 'PINT 0', 'true-cast': 'PBOOL true',
                'false-null': 'PNULL', 'true-string': 'PSTRING_CARRIER INTERNED_STRING ([49])'}[variant]
    result = {
        'cast': ('NExprCastDouble', 'CASTFLOAT', 2, root_value(name), False, ['cast_1']),
        'cast_1': ('NExprCastInt', 'CASTINT', 1, 'PINT ' + str(int(one)), False, ['value']),
        'value': ('NExprTernary', None, None, selected, False, ['value_cond', 'value_true', 'value_false']),
        'value_cond': (('NExprBooleanNot', None, None, 'PBOOL true', False, ['value_cond_child'])
                       if truth else ('NExprCastBool', 'CASTBOOL', 1, 'PBOOL false', False, ['value_cond_child'])),
        'value_cond_child': ('float', '0000000000000000', None, 'PFLOAT 0', True, [])}
    if variant in ['false-constant', 'false-float']:
        result['value_true'] = ('constant', 'UNDEFINED_TERNARY_TRUE', None, None, False, [])
    elif variant in ['true-constant', 'false-cast']:
        result['value_true'] = ('integer', '1', None, 'PINT 1', True, [])
    elif variant in ['true-bool', 'false-null']:
        result['value_true'] = ('constant', 'true', None, 'PBOOL true', True, [])
    elif variant == 'true-cast':
        result['value_true'] = ('NExprCastBool', 'CASTBOOL', 1, 'PBOOL true', False, ['value_true_child'])
        result['value_true_child'] = ('float', '3ff0000000000000', None, 'PFLOAT 4607182418800017408', True, [])
    else:
        result['value_true'] = ('string', '1', None, selected, True, [])
    if variant in ['true-constant', 'true-bool']:
        result['value_false'] = ('constant', 'UNDEFINED_TERNARY_FALSE', None, None, False, [])
    elif variant in ['false-constant', 'true-cast']:
        result['value_false'] = ('integer', '0', None, 'PINT 0', True, [])
    elif variant == 'false-float':
        result['value_false'] = ('float', '0000000000000000', None, 'PFLOAT 0', True, [])
    elif variant == 'false-cast':
        result['value_false'] = ('NExprCastInt', 'CASTINT', 1, 'PINT 0', False, ['value_false_child'])
        result['value_false_child'] = ('float', '0000000000000000', None, 'PFLOAT 0', True, [])
    elif variant == 'false-null':
        result['value_false'] = ('constant', 'null', None, 'PNULL', True, [])
    else:
        result['value_false'] = ('constant', 'false', None, 'PBOOL false', True, [])
    return result


def root_value(name):
    return 'PFLOAT ' + ('4607182418800017408' if DETAILS[name][2] == b'1.0' else '0')


def expression(name, key='cast'):
    kind, spelling, _, _, _, children = nodes(name)[key]
    metadata = 'metadata_' + key
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
    return zero.converted(condition).replace('selected_modulo_zero_return', 'selected_modulo_emitted_condition_full_ternary_return').replace(
        'S_handler.RESULT = KNOWN (PINT 0)', 'S_handler.RESULT = KNOWN (' + root_value(name) + ')').replace(
        'S_handler_right.RESULT = KNOWN (PINT 0)', 'S_handler_right.RESULT = KNOWN (' + root_value(name) + ')')


def return_bindings(name):
    bindings = [adapted(name, binding) for binding in zero.return_bindings(DETAILS[name][0])]
    bindings += ['$origin_node(S.SOURCES, porigin_cast) = (' + expression(name) + ')']
    for key, node in nodes(name).items():
        for field, child in enumerate(node[5]):
            bindings += ['$origin_child((porigin_' + key + '), [PCFIELD ' + str(field) + ']) = (porigin_' + child + ')',
                         'porigin_' + child + ' = PORIGIN n_cast_handler pcpath_' + child,
                         '$origin_node(S.SOURCES, porigin_' + child + ') = (' + expression(name, child) + ')']
            if nodes(name)[child][4] is not None:
                bindings += ['$code_expression(pfunction_handler.CODE.EXPRESSIONS, pcpath_' + child + ') = ((z_' + child + ', b_' + child + '))']
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
        if result is None:
            parts += ['~b_' + key, 'z_' + key + ' = $source_line(metadata_' + key + ')',
                      '$ob_object_cast_chain_value(S, pfunction_handler, porigin_' + key + ', ' + expression(name, key) + ') = eps',
                      '$ob_object_cast_chain_skipped_line(S, pfunction_handler, porigin_' + key + ', ' + expression(name, key) + ') = (z_' + key + ')']
            parts += ['$compiled_read(' + state + ', porigin_' + key + ') = eps' for state in states]
            continue
        parts += [('b_' if folded else '~b_') + key,
                  '$ob_object_cast_chain_value(S, pfunction_handler, porigin_' + key + ', ' + expression(name, key) + ') = (' + result + ')',
                  '$value_nodes(' + result + ') = eps']
        pooled = 'PSTRING ([49])' if kind == 'string' else result
        parts += ['$compiled_read(' + state + ', porigin_' + key + ') = ' + ('(' + pooled + ')' if folded else 'eps') for state in states]
        if not children:
            parts += ['z_' + key + ' = $source_line(metadata_' + key + ')']
            continue
        selected = children[-1]
        parts += ['z_' + key + ' = z_' + selected]
        if key == 'value':
            truth = variant.startswith('true-')
            branch = 'value_true' if truth else 'value_false'
            skipped = 'value_false' if truth else 'value_true'
            cond = nodes(name)['value_cond'][3]
            parts += ['$ob_object_cast_chain_quiet(CASTBOOL, ' + cond + ')',
                      '$boolean_result(S[.RESULT = KNOWN (' + cond + ')], false, z_value_cond) = S[.RESULT = KNOWN (PBOOL ' + str(truth).lower() + ')]',
                      '$compiled_effects(S, porigin_value) = eps', '$compiled_redirect(S, porigin_value) = eps',
                      '$ob_object_cast_chain_skipped_line(S, pfunction_handler, porigin_' + skipped + ', ' + expression(name, skipped) + ') = (z_' + skipped + ')',
                      '$selected_branch(S[.ORIGIN = (porigin_value)][.RESULT = KNOWN (PBOOL ' + str(truth).lower() + ')], ' + expression(name, 'value_true') + ', ' + expression(name, 'value_false') + ', ' + cond + ', z_value_true, z_value_false) = S[.ORIGIN = (porigin_value)][.TODO = [AT porigin_' + branch + ' (EVAL (' + expression(name, branch) + ')), VALUE_COPY z_' + branch + '] ++ S.TODO][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
                      '$resolve_at(S[.RESULT = KNOWN (' + result + ')], KNOWN (' + result + '), z_' + branch + ') = S[.RESULT = KNOWN (' + result + ')]']
        elif kind == 'NExprBooleanNot':
            child_value = nodes(name)[selected][3]
            parts += ['$boolean_result(S[.RESULT = KNOWN (' + child_value + ')], true, z_' + key + ') = S[.RESULT = KNOWN (' + result + ')]']
        else:
            child_value = nodes(name)[selected][3]
            parts += ['$plstyle(metadata_' + key + ') = ' + str(style),
                      '$cast_apply(S[.RESULT = KNOWN (' + child_value + ')], ' + operator + ', ' + child_value + ', z_' + key + ') = S[.RESULT = KNOWN (' + result + ')]']
    return CONJ.join(parts)


def frontier(name, fixture, path):
    context = DETAILS[name][0]
    bindings, checks = prior.base_for(context).frontier(context, fixture, path)
    return bindings + return_bindings(name), [*[(label, converted(name, condition)) for label, condition in checks],
        ('proper emitted condition, both compiled arms, selected VALUE/copy and FALSE terminal line', return_proof(name))]


def lifecycle(name, fixture, path):
    context = DETAILS[name][0]
    bindings, checks = prior.base_for(context).lifecycle(context, fixture, path)
    return bindings + return_bindings(name), [*[(label, converted(name, condition)) for label, condition in checks],
        ('full ternary source and selected VALUE tags survive real formal/native-cell retirement', return_proof(name))]


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
