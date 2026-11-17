#!/usr/bin/env python3
"""Same-line integer bitwise trees retain typed returns and real retirement."""
import output_final_selected_nested_scalar_cast_return_modulo_error_state as chains
import output_final_selected_integer_bitwise_cast_chain_return_modulo_error_sources as sources

zero, no, prior, runner = chains.zero, chains.no, chains.prior, chains.runner
PREFIX, CONJ = chains.PREFIX, chains.CONJ
DETAILS = {context + '-' + variant: (context, variant) for context, variant, _, _ in sources.VARIANTS}
CASES = {name: sources.CASES['native-selected-integer-bitwise-cast-chain-return-modulo-error-' + name]
         for name in ['deprecated-both-cv-pair-folded-and-zero',
                      'deprecated-both-cv-pair-emitted-or-negative',
                      'warning-left-constant-emitted-xor-zero']}


def integer(i):
    return ('integer', str(i), None, 'PINT ' + str(i), True, [])


def negative(i):
    return ('NExprUnaryMinus', 'NEGATIVE', None, 'PINT $(-' + str(i) + ')', True, [integer(i)])


def string(text):
    return ('string', text, None, 'PSTRING_CARRIER INTERNED_STRING ($ptascii("' + text + '"))', True, [])


def cast(kind, result, child):
    constructor, operator, style = {'bool': ('NExprCastBool', 'CASTBOOL', 1),
                                   'int': ('NExprCastInt', 'CASTINT', 1),
                                   'float': ('NExprCastDouble', 'CASTFLOAT', 2)}[kind]
    return (constructor, operator, style, result, False, [child])


def bitwise(kind, result, left, right):
    constructor, operator = {'and': ('NExprBinaryOpBitwiseAnd', 'BITAND'),
                             'or': ('NExprBinaryOpBitwiseOr', 'BITOR'),
                             'xor': ('NExprBinaryOpBitwiseXor', 'BITXOR')}[kind]
    return (constructor, operator, None, result, left[4] and right[4], [left, right])


TREES = {
 'folded-and-zero': cast('bool', 'PBOOL false', cast('int', 'PINT 0',
    bitwise('and', 'PINT 0', integer(6), integer(1)))),
 'folded-or-negative': cast('float', 'PFLOAT 13830554455654793216', cast('int', 'PINT $(-1)',
    bitwise('or', 'PINT $(-1)', negative(2), integer(1)))),
 'folded-xor-one': cast('int', 'PINT 1', cast('bool', 'PBOOL true',
    bitwise('xor', 'PINT 1', negative(1), negative(2)))),
 'emitted-and-zero': cast('int', 'PINT 0', cast('bool', 'PBOOL false',
    bitwise('and', 'PINT 0', cast('int', 'PINT 2', string('2')), integer(1)))),
 'emitted-or-negative': cast('bool', 'PBOOL true', cast('float', 'PFLOAT 13830554455654793216',
    bitwise('or', 'PINT $(-1)', negative(2), cast('int', 'PINT 1', string('1'))))),
 'emitted-xor-zero': cast('int', 'PINT 0', cast('bool', 'PBOOL false',
    bitwise('xor', 'PINT 0', cast('int', 'PINT 3', string('3')), cast('int', 'PINT 3', string('3')))))}


def children(key, node):
    if key == 'cast':
        return [('cast_1', 0)]
    if key == 'cast_1':
        return [('binary', 0)]
    return [('bit_left', 0), ('bit_right', 1)] if key == 'binary' else [(key + '_child', 0)] if node[5] else []


def nodes(name):
    result = {}

    def visit(key, node):
        result[key] = node
        for (child, _), descendant in zip(children(key, node), node[5]):
            visit(child, descendant)
    visit('cast', TREES[DETAILS[name][1]])
    return result


def expression(name, key='cast'):
    node = nodes(name)[key]
    kind, spelling = node[:2]
    metadata = 'metadata_' + key
    if kind == 'integer':
        return 'NScalarInt (INTEGER ' + spelling + ') ' + metadata
    if kind == 'string':
        return 'NScalarString (BYTES text_' + key + ') ' + metadata
    return kind + ' ' + ' '.join('(' + expression(name, child) + ')' for child, _ in children(key, node)) + ' ' + metadata


def root_value(name):
    return nodes(name)['cast'][3]


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
                                  'selected_modulo_integer_bitwise_cast_chain_return')
    for state in ['S_handler', 'S_handler_right']:
        condition = condition.replace(state + '.RESULT = KNOWN (PINT 0)',
                                      state + '.RESULT = KNOWN (' + root_value(name) + ')')
    return condition


def return_bindings(name):
    base = no if default(name) else zero
    bindings = [adapted(name, binding) for binding in base.return_bindings(DETAILS[name][0])]
    bindings += ['$origin_node(S.SOURCES, porigin_cast) = (' + expression(name) + ')']
    for key, node in nodes(name).items():
        for child, field in children(key, node):
            bindings += [
                '$origin_child((porigin_' + key + '), [PCFIELD ' + str(field) + ']) = (porigin_' + child + ')',
                'porigin_' + child + ' = PORIGIN n_cast_handler pcpath_' + child,
                '$origin_node(S.SOURCES, porigin_' + child + ') = (' + expression(name, child) + ')',
                '$code_expression(pfunction_handler.CODE.EXPRESSIONS, pcpath_' + child + ') = ((z_' + child + ', b_' + child + '))']
    return bindings


def return_proof(name):
    context = DETAILS[name][0]
    condition = (no if default(name) else zero).return_proof(context)
    if default(name):
        keyword = r'$ptlc($base64(text_false)) = $ptascii("false") /\ '
        assert condition.count(keyword) == 1
        condition = condition.replace(keyword, '')
    condition = adapted(name, condition)
    line = r'z_cast = $source_line(metadata_cast) /\ b_cast /\ '
    assert condition.count(line) == 1
    condition = condition.replace(line, 'z_cast = $expression_line(' + expression(name, 'cast_1') + r') /\ ~b_cast /\ ')
    states = ['S_return', 'S', *(['S_return_right'] if prior.two_calls(context) else [])]
    for state in states:
        read = '$compiled_read(' + state + ', porigin_cast) = (' + root_value(name) + ')'
        assert condition.count(read) == 1
        condition = condition.replace(read, '$compiled_read(' + state + ', porigin_cast) = eps')
    parts = [condition, 'S.COMPLETION = NORMAL']
    for key, node in nodes(name).items():
        kind, operator, style, result, folded, descendants = node
        parts += [('b_' if folded else '~b_') + key,
                  '$ob_object_cast_chain_value(S, pfunction_handler, porigin_' + key + ', ' + expression(name, key) + ') = (' + result + ')']
        cache = result
        if kind == 'string':
            cache = 'PSTRING ($ptascii("' + operator + '"))'
            parts += ['$base64(text_' + key + ') = $ptascii("' + operator + '")',
                      '$value_nodes(' + result + ') = eps']
            parts += ['$compiled_string_value(' + state + ', porigin_' + key + ', ' + cache + ') = ' + result for state in states]
        parts += ['$compiled_read(' + state + ', porigin_' + key + ') = ' + ('(' + cache + ')' if folded else 'eps') for state in states]
        if not descendants:
            parts += ['z_' + key + ' = $source_line(metadata_' + key + ')']
            continue
        child = children(key, node)[-1][0]
        parts += ['z_' + key + ' = $expression_line(' + expression(name, child) + ')']
        for descendant, field in children(key, node):
            parts += ['pcpath_' + descendant + ' = pcpath_' + key + ' ++ [PCFIELD ' + str(field) + ']']
        if len(descendants) == 2:
            left, right = descendants[0][3], descendants[1][3]
            parts += ['$expression_line(' + expression(name, 'bit_left') + ') = z_binary',
                      'z_bit_left = z_binary', 'z_bit_right = z_binary', r'b_binary = (b_bit_left /\ b_bit_right)',
                      '$long_range(' + left[5:] + ')', '$long_range(' + right[5:] + ')', '$long_range(' + result[5:] + ')',
                      '$binary_apply(S[.RESULT = KNOWN (' + right + ')], ' + operator + ', ' + left + ', ' + right + ', z_binary) = S[.RESULT = KNOWN (' + result + ')]',
                      '$value_nodes(' + result + ') = eps']
        elif kind == 'NExprUnaryMinus':
            child_value = descendants[0][3]
            parts += ['$unary_apply(S[.RESULT = KNOWN (' + child_value + ')], NEGATIVE, ' + child_value + ', z_' + key + ') = S[.RESULT = KNOWN (' + result + ')]']
        else:
            child_value = descendants[0][3]
            parts += ['$plstyle(metadata_' + key + ') = ' + str(style),
                      '$ob_object_cast_chain_quiet(' + operator + ', ' + child_value + ')',
                      '$cast_apply(S[.RESULT = KNOWN (' + child_value + ')], ' + operator + ', ' + child_value + ', z_' + key + ') = S[.RESULT = KNOWN (' + result + ')]']
    return CONJ.join(parts)


def frontier(name, fixture, path):
    context = DETAILS[name][0]
    bindings, checks = prior.base_for(context).frontier(context, fixture, path)
    return bindings + return_bindings(name), [
        *[(label.replace('NULL', 'integer bitwise tree'), converted(name, condition)) for label, condition in checks],
        ('both real child flags, same-line source/CODE, exact integer state and strict fallback remain required', return_proof(name))]


def lifecycle(name, fixture, path):
    context = DETAILS[name][0]
    bindings, checks = prior.base_for(context).lifecycle(context, fixture, path)
    return bindings + return_bindings(name), [
        *[(label, converted(name, condition)) for label, condition in checks],
        ('the exact integer bitwise tree and handler result survive actual formal/native-cell retirement', return_proof(name))]


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
