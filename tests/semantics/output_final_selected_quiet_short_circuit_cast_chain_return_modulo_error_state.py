#!/usr/bin/env python3
"""Selected short circuits retain compiler authority and real retirement."""
import base64
import output_final_selected_zero_return_modulo_error_state as zero
import output_final_selected_quiet_short_circuit_cast_chain_return_modulo_error_sources as sources

prior, runner = zero.prior, zero.runner
PREFIX = zero.PREFIX.replace('(PINT 0)', 'pvalue_return')
CONJ = r' /\ '
DETAILS = {context + '-' + variant: (context, variant, expected)
           for context, variant, _, _, expected in sources.VARIANTS}
CASES = {name: sources.CASES['native-selected-quiet-short-circuit-cast-chain-return-modulo-error-' + name]
         for name in ['warning-left-constant-and-skip',
                      'warning-deprecated-constant-float-or-emitted-right']}


def nodes(name):
    _, variant, expected = DETAILS[name]
    one = expected == b'1.0'
    skip = variant.endswith('-skip')
    is_or = variant.startswith('or-') or variant.startswith('logical-or-')
    constructor = ('NExprBinaryOpLogical' if variant.startswith('logical-') else 'NExprBinaryOpBoolean')
    constructor += 'Or' if is_or else 'And'
    truth = 'true' if one else 'false'
    result = {
        'cast': ('NExprCastDouble', 'CASTFLOAT', 2, root_value(name), False, ['cast_1']),
        'cast_1': ('NExprCastInt', 'CASTINT', 1, 'PINT ' + str(int(one)), False, ['value']),
        'value': (constructor, 'true' if is_or else 'false', None, 'PBOOL ' + truth,
                  skip or not variant.endswith('emitted-right'), ['value_left', 'value_right'])}
    left = is_or if skip else not is_or
    result['value_left'] = (('integer', str(int(left)), None, 'PINT ' + str(int(left)), True, [])
                            if variant.startswith('logical-') else
                            ('constant', str(left).lower(), None, 'PBOOL ' + str(left).lower(), True, []))
    if skip:
        result['value_right'] = ('constant', 'UNDEFINED_SHORT_RHS' if variant.startswith('logical-') else str(not left).lower(),
                                 None, None, None, [])
    elif variant.endswith('emitted-right'):
        result['value_right'] = (('NExprCastBool', 'CASTBOOL', 1, 'PBOOL false', False, ['value_right_child'])
                                 if is_or else
                                 ('NExprBooleanNot', None, None, 'PBOOL true', False, ['value_right_child']))
        result['value_right_child'] = ('float', '0000000000000000', None, 'PFLOAT 0', True, [])
    else:
        result['value_right'] = ('constant', truth, None, 'PBOOL ' + truth, True, [])
    return result


def root_value(name):
    return 'PFLOAT ' + ('4607182418800017408' if DETAILS[name][2] == b'1.0' else '0')


def expression(name, key='cast'):
    kind, spelling, _, _, _, children = nodes(name)[key]
    metadata = 'metadata_' + key
    if kind == 'constant':
        payload = base64.b64encode(spelling.encode()).decode()
        return 'NExprConstFetch (NName (BYTES "' + payload + '") ' + metadata + '_name) ' + metadata
    if kind == 'integer':
        return 'NScalarInt (INTEGER ' + spelling + ') ' + metadata
    if kind == 'float':
        return 'NScalarFloat (FLOAT "' + spelling + '") ' + metadata
    return kind + ' ' + ' '.join('(' + expression(name, child) + ')' for child in children) + ' ' + metadata


def adapted(name, condition):
    return condition.replace('NScalarInt (INTEGER 0) metadata_zero', expression(name)).replace(
        '(PINT 0)', '(' + root_value(name) + ')').replace('_zero', '_cast')


def converted(name, condition):
    return zero.converted(condition).replace('selected_modulo_zero_return', 'selected_modulo_quiet_short_circuit_return').replace(
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
        if folded is None:
            parts += ['$code_expression(pfunction_handler.CODE.EXPRESSIONS, pcpath_' + key + ') = eps',
                      '$ob_object_cast_chain_value(S, pfunction_handler, porigin_' + key + ', ' + expression(name, key) + ') = eps']
            continue
        parts += [('b_' if folded else '~b_') + key,
                  '$ob_object_cast_chain_value(S, pfunction_handler, porigin_' + key + ', ' + expression(name, key) + ') = (' + result + ')',
                  '$value_nodes(' + result + ') = eps']
        parts += ['$compiled_read(' + state + ', porigin_' + key + ') = ' + ('(' + result + ')' if folded else 'eps') for state in states]
        if not children:
            parts += ['z_' + key + ' = $source_line(metadata_' + key + ')']
            continue
        selected = children[0] if key == 'value' and variant.endswith('-skip') else children[-1]
        parts += ['z_' + key + ' = z_' + selected]
        if key == 'value':
            left = nodes(name)['value_left'][3]
            left_truth = operator if variant.endswith('-skip') else ('false' if operator == 'true' else 'true')
            parts += ['$ob_object_cast_chain_quiet(CASTBOOL, ' + left + ')',
                      '$boolean_result(S[.RESULT = KNOWN (' + left + ')], false, z_value_left) = S[.RESULT = KNOWN (PBOOL ' + left_truth + ')]']
            if not variant.endswith('-skip'):
                right = nodes(name)['value_right'][3]
                parts += ['$ob_object_cast_chain_quiet(CASTBOOL, ' + right + ')',
                          '$boolean_result(S[.RESULT = KNOWN (' + right + ')], false, z_value_right) = S[.RESULT = KNOWN (' + result + ')]']
            parts += ['$compiled_effects(S, porigin_value) = eps']
            if not folded:
                parts += ['$compiled_redirect(S, porigin_value) = ((porigin_value_right, ' + expression(name, 'value_right') + ', true, z_value))']
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
        ('proper selected operands, pruned RHS, typed flags and exact quiet Boolean states', return_proof(name))]


def lifecycle(name, fixture, path):
    context = DETAILS[name][0]
    bindings, checks = prior.base_for(context).lifecycle(context, fixture, path)
    return bindings + return_bindings(name), [*[(label, converted(name, condition)) for label, condition in checks],
        ('short-circuit source and typed results survive real formal/native-cell retirement', return_proof(name))]


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
