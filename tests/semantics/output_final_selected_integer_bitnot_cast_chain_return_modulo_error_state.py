#!/usr/bin/env python3
"""Integer complements preserve typed returns and real retirement."""
import output_final_selected_nested_scalar_cast_return_modulo_error_state as chains
import output_final_selected_integer_bitnot_cast_chain_return_modulo_error_sources as sources

zero, no, prior, runner = chains.zero, chains.no, chains.prior, chains.runner
PREFIX, CONJ = chains.PREFIX, chains.CONJ
DETAILS = {context + '-' + variant: (context, variant) for context, variant, _, _ in sources.VARIANTS}
CASES = {name: sources.CASES['native-selected-integer-bitnot-cast-chain-return-modulo-error-' + name]
         for name in ['deprecated-both-cv-pair-folded-zero',
                      'warning-deprecated-constant-float-emitted-negative']}
# AST kind, operation/leaf spelling, cast style, exact result, compiler-folded flag.
NODES = {'folded-zero': [('NExprCastBool', 'CASTBOOL', 1, 'PBOOL false', False),
                         ('NExprCastInt', 'CASTINT', 1, 'PINT 0', False),
                         ('NExprBitwiseNot', None, None, 'PINT 0', True),
                         ('NExprUnaryMinus', 'NEGATIVE', None, 'PINT $(-1)', True),
                         ('integer', '1', None, 'PINT 1', True)],
 'folded-negative': [('NExprCastDouble', 'CASTFLOAT', 2, 'PFLOAT 13835058055282163712', False),
                     ('NExprCastInt', 'CASTINT', 1, 'PINT $(-2)', False),
                     ('NExprBitwiseNot', None, None, 'PINT $(-2)', True),
                     ('integer', '1', None, 'PINT 1', True)],
 'emitted-zero': [('NExprCastInt', 'CASTINT', 1, 'PINT 0', False),
                  ('NExprCastBool', 'CASTBOOL', 1, 'PBOOL false', False),
                  ('NExprBitwiseNot', None, None, 'PINT 0', False),
                  ('NExprCastInt', 'CASTINT', 1, 'PINT $(-1)', False),
                  ('string', '-1', None, 'PSTRING_CARRIER INTERNED_STRING ($ptascii("-1"))', True)],
 'emitted-negative': [('NExprCastBool', 'CASTBOOL', 1, 'PBOOL true', False),
                      ('NExprCastDouble', 'CASTFLOAT', 2, 'PFLOAT 13830554455654793216', False),
                      ('NExprBitwiseNot', None, None, 'PINT $(-1)', False),
                      ('NExprCastInt', 'CASTINT', 1, 'PINT 0', False),
                      ('string', '0', None, 'PSTRING_CARRIER INTERNED_STRING ($ptascii("0"))', True)]}


def nodes(name):
    return NODES[DETAILS[name][1]]


def slot(index):
    return ['cast', 'cast_1', 'sign'][index] if index < 3 else 'child_' + str(index)


def expression(name, index=0):
    kind, spelling, _, _, _ = nodes(name)[index]
    metadata = 'metadata_' + slot(index)
    if kind == 'string':
        return 'NScalarString (BYTES text_leaf) ' + metadata
    if kind == 'integer':
        return 'NScalarInt (INTEGER ' + spelling + ') ' + metadata
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
                                  'selected_modulo_integer_bitnot_cast_chain_return')
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
        for state in states:
            parts += ['$compiled_read(' + state + ', porigin_' + current + ') = ' + ('(' + cache + ')' if folded else 'eps')]
        if kind in ('string', 'integer'):
            parts += ['z_' + current + ' = $source_line(metadata_' + current + ')']
            continue
        child = nodes(name)[index + 1][3]
        parts += ['z_' + current + ' = $expression_line(' + expression(name, index + 1) + ')']
        if kind == 'NExprUnaryMinus':
            parts += ['$ob_object_cast_chain_sign_number(' + child + ')',
                      '$ob_object_cast_chain_sign_number(' + result + ')',
                      '$type_bytes(' + result + ') = $type_bytes(' + child + ')',
                      '$unary_apply(S[.RESULT = KNOWN (' + child + ')], ' + operator + ', ' + child + ', z_' + current + ') = S[.RESULT = KNOWN (' + result + ')]',
                      '$value_nodes(' + result + ') = eps']
        elif kind == 'NExprBitwiseNot':
            assert child.startswith('PINT ') and result.startswith('PINT ')
            parts += ['$long_range(' + child[5:] + ')', '$long_range(' + result[5:] + ')',
                      '$bitnot_apply(S[.RESULT = KNOWN (' + child + ')], ' + child + ', z_' + current + ') = S[.RESULT = KNOWN (' + result + ')]',
                      '$value_nodes(' + result + ') = eps']
        else:
            parts += ['$plstyle(metadata_' + current + ') = ' + str(style),
                      '$ob_object_cast_chain_quiet(' + operator + ', ' + child + ')',
                      '$cast_apply(S[.RESULT = KNOWN (' + child + ')], ' + operator + ', ' + child + ', z_' + current + ') = S[.RESULT = KNOWN (' + result + ')]']
    return CONJ.join(parts)


def frontier(name, fixture, path):
    bindings, checks = prior.base_for(DETAILS[name][0]).frontier(DETAILS[name][0], fixture, path)
    checks = [(label.replace('NULL', 'integer complement chain'), converted(name, condition)) for label, condition in checks]
    return bindings + return_bindings(name), checks + [
        ('actual compiler flags, raw facts, typed complement/cast states and strict fallback remain exact', return_proof(name))]


def lifecycle(name, fixture, path):
    bindings, checks = prior.base_for(DETAILS[name][0]).lifecycle(DETAILS[name][0], fixture, path)
    return bindings + return_bindings(name), [
        *[(label, converted(name, condition)) for label, condition in checks],
        ('the certified integer child and exact result survive actual formal/native-cell retirement', return_proof(name))]


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
