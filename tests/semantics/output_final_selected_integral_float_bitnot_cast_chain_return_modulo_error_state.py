#!/usr/bin/env python3
"""Quiet float complements preserve typed returns and real retirement."""
import base64
import output_final_selected_zero_return_modulo_error_state as zero
import output_final_selected_integral_float_bitnot_cast_chain_return_modulo_error_sources as sources

prior, runner = zero.prior, zero.runner
PREFIX = zero.PREFIX.replace('(PINT 0)', 'pvalue_return')
CONJ = r' /\ '
DETAILS = {context + '-' + variant: (context, variant, int(raw))
           for context, variant, _, raw, _ in sources.VARIANTS}
CASES = {name: sources.CASES['native-selected-integral-float-bitnot-cast-chain-return-modulo-error-' + name]
         for name in ['warning-left-constant-folded-one',
                      'warning-deprecated-constant-float-emitted-negative']}


def integer(value):
    return str(value) if value >= 0 else '$(' + str(value) + ')'


def floating(bits):
    return ('float', bits, None, 'PFLOAT ' + str(int(bits, 16)), True)


def string(value):
    return ('string', value, None, 'PSTRING_CARRIER INTERNED_STRING ($ptascii("' + value + '"))', True)


def float_cast(bits):
    return ('NExprCastDouble', 'CASTFLOAT', 2, 'PFLOAT ' + str(int(bits, 16)), False)


def chain(result, bits, children):
    raw = 'PINT ' + integer(result)
    return [('NExprCastDouble', 'CASTFLOAT', 2, 'PFLOAT ' + str(int(bits, 16)), False),
            ('NExprCastInt', 'CASTINT', 1, raw, False),
            ('NExprBitwiseNot', None, None, raw, children[0][4]), *children]


NODES = {
    'folded-one': chain(-2, 'c000000000000000', [floating('3ff0000000000000')]),
    'folded-negzero': chain(-1, 'bff0000000000000', [
        ('NExprUnaryMinus', 'NEGATIVE', None, 'PFLOAT 9223372036854775808', True), floating('0000000000000000')]),
    'emitted-one': chain(-2, 'c000000000000000', [float_cast('3ff0000000000000'), string('1')]),
    'emitted-negative': chain(0, '0000000000000000', [
        ('NExprUnaryMinus', 'NEGATIVE', None, 'PFLOAT 13830554455654793216', False),
        float_cast('3ff0000000000000'), string('1')]),
    'folded-min': chain(9223372036854775807, '43e0000000000000', [
        ('NExprUnaryMinus', 'NEGATIVE', None, 'PFLOAT 14114281232179134464', True), floating('43e0000000000000')]),
    'folded-near-max': chain(-9223372036854774785, 'c3dfffffffffffff', [floating('43dfffffffffffff')]),
    'emitted-zero': chain(-1, 'bff0000000000000', [float_cast('0000000000000000'), string('0')]),
    'folded-negative': chain(0, '0000000000000000', [
        ('NExprUnaryMinus', 'NEGATIVE', None, 'PFLOAT 13830554455654793216', True), floating('3ff0000000000000')])}


def nodes(name):
    return NODES[DETAILS[name][1]]


def slot(index):
    return ['cast', 'cast_1', 'sign'][index] if index < 3 else 'child_' + str(index)


def expression(name, index=0):
    kind, spelling, _, _, _ = nodes(name)[index]
    metadata = 'metadata_' + slot(index)
    if kind == 'float':
        return 'NScalarFloat (FLOAT "' + spelling + '") ' + metadata
    if kind == 'string':
        return 'NScalarString (BYTES "' + base64.b64encode(spelling.encode()).decode() + '") ' + metadata
    return kind + ' (' + expression(name, index + 1) + ') ' + metadata


def root_value(name):
    return nodes(name)[0][3]


def adapted(name, condition):
    return condition.replace('NScalarInt (INTEGER 0) metadata_zero', expression(name)).replace(
        '(PINT 0)', '(' + root_value(name) + ')').replace('_zero', '_cast')


def converted(name, condition):
    condition = zero.converted(condition).replace('selected_modulo_zero_return', 'selected_modulo_integral_float_bitnot_return')
    for state in ['S_handler', 'S_handler_right']:
        condition = condition.replace(state + '.RESULT = KNOWN (PINT 0)', state + '.RESULT = KNOWN (' + root_value(name) + ')')
    return condition


def return_bindings(name):
    bindings = [adapted(name, binding) for binding in zero.return_bindings(DETAILS[name][0])]
    bindings += ['$origin_node(S.SOURCES, porigin_cast) = (' + expression(name) + ')']
    for index in range(1, len(nodes(name))):
        current, parent = slot(index), slot(index - 1)
        bindings += ['$origin_child((porigin_' + parent + '), [PCFIELD 0]) = (porigin_' + current + ')',
                     'porigin_' + current + ' = PORIGIN n_cast_handler pcpath_' + current,
                     '$origin_node(S.SOURCES, porigin_' + current + ') = (' + expression(name, index) + ')',
                     '$code_expression(pfunction_handler.CODE.EXPRESSIONS, pcpath_' + current + ') = ((z_' + current + ', b_' + current + '))']
    return bindings


def return_proof(name):
    context, _, raw = DETAILS[name]
    condition = adapted(name, zero.return_proof(context))
    condition = condition.replace(r'z_cast = $source_line(metadata_cast) /\ b_cast /\ ',
                                  'z_cast = $expression_line(' + expression(name, 1) + r') /\ ~b_cast /\ ')
    states = ['S_return', 'S', *(['S_return_right'] if prior.two_calls(context) else [])]
    for state in states:
        condition = condition.replace('$compiled_read(' + state + ', porigin_cast) = (' + root_value(name) + ')',
                                      '$compiled_read(' + state + ', porigin_cast) = eps')
    parts = [condition, 'S.COMPLETION = NORMAL']
    for index, (kind, operator, style, result, folded) in enumerate(nodes(name)):
        current = slot(index)
        parts += [('b_' if folded else '~b_') + current,
                  '$ob_object_cast_chain_value(S, pfunction_handler, porigin_' + current + ', ' + expression(name, index) + ') = (' + result + ')']
        if index:
            parts += ['pcpath_' + current + ' = pcpath_' + slot(index - 1) + ' ++ [PCFIELD 0]']
        pooled = 'PSTRING ($ptascii("' + operator + '"))' if kind == 'string' else result
        for state in states:
            parts += ['$compiled_read(' + state + ', porigin_' + current + ') = ' + ('(' + pooled + ')' if folded else 'eps')]
        if kind in ('float', 'string'):
            parts += ['z_' + current + ' = $source_line(metadata_' + current + ')', '$value_nodes(' + result + ') = eps']
            continue
        child = nodes(name)[index + 1][3]
        parts += ['z_' + current + ' = $expression_line(' + expression(name, index + 1) + ')']
        if kind == 'NExprUnaryMinus':
            parts += ['$ob_object_cast_chain_sign_number(' + child + ')', '$ob_object_cast_chain_sign_number(' + result + ')',
                      '$type_bytes(' + result + ') = $type_bytes(' + child + ')',
                      '$unary_apply(S[.RESULT = KNOWN (' + child + ')], NEGATIVE, ' + child + ', z_' + current + ') = S[.RESULT = KNOWN (' + result + ')]']
        elif kind == 'NExprBitwiseNot':
            parts += ['$float_long(' + child[7:] + ', true) = (' + integer(-raw - 1) + ', eps)',
                      '$long_range(' + result[5:] + ')', '$value_nodes(' + result + ') = eps',
                      '$bitnot_apply(S[.RESULT = KNOWN (' + child + ')], ' + child + ', z_' + current + ') = S[.RESULT = KNOWN (' + result + ')]']
        else:
            parts += ['$plstyle(metadata_' + current + ') = ' + str(style),
                      '$ob_object_cast_chain_quiet(' + operator + ', ' + child + ')',
                      '$cast_apply(S[.RESULT = KNOWN (' + child + ')], ' + operator + ', ' + child + ', z_' + current + ') = S[.RESULT = KNOWN (' + result + ')]']
    return CONJ.join(parts)


def frontier(name, fixture, path):
    context = DETAILS[name][0]
    bindings, checks = prior.base_for(context).frontier(context, fixture, path)
    return bindings + return_bindings(name), [*[(label, converted(name, condition)) for label, condition in checks],
        ('exact integral float conversion, compiler flags, raw complement and nested casts remain quiet', return_proof(name))]


def lifecycle(name, fixture, path):
    context = DETAILS[name][0]
    bindings, checks = prior.base_for(context).lifecycle(context, fixture, path)
    return bindings + return_bindings(name), [*[(label, converted(name, condition)) for label, condition in checks],
        ('the exact float child and raw complement survive real formal/native-cell retirement', return_proof(name))]


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
