#!/usr/bin/env python3
"""Integer arithmetic certificates retain typed results and real retirement."""
import output_final_selected_terminal_line_bitwise_cast_chain_return_modulo_error_state as current
import output_final_selected_integer_arithmetic_cast_chain_return_modulo_error_sources as sources

zero, no, prior, runner = current.zero, current.no, current.prior, current.runner
PREFIX, CONJ = current.PREFIX, current.CONJ
integer, negative, string, cast = current.integer, current.negative, current.string, current.cast
DETAILS = {context + '-' + variant: (context, variant) for context, variant, _, _ in sources.VARIANTS}
CASES = {name: sources.CASES['native-selected-integer-arithmetic-cast-chain-return-modulo-error-' + name]
         for name in ['deprecated-both-cv-pair-folded-add-zero',
                      'warning-deprecated-constant-float-emitted-add-zero',
                      'warning-left-constant-emitted-mul-zero']}


def arithmetic(kind, result, left, right):
    constructor, operator = {'add': ('NExprBinaryOpPlus', 'ADD'),
                             'sub': ('NExprBinaryOpMinus', 'SUBTRACT'),
                             'mul': ('NExprBinaryOpMul', 'MULTIPLY')}[kind]
    return (constructor, operator, None, result, left[4] and right[4], [left, right])


TREES = {
 'folded-add-zero': cast('bool', 'PBOOL false', cast('int', 'PINT 0',
    arithmetic('add', 'PINT 0', negative(1), integer(1)))),
 'folded-sub-negative': cast('float', 'PFLOAT 13830554455654793216', cast('int', 'PINT $(-1)',
    arithmetic('sub', 'PINT $(-1)', integer(1), integer(2)))),
 'folded-mul-one': cast('int', 'PINT 1', cast('bool', 'PBOOL true',
    arithmetic('mul', 'PINT 2', negative(1), negative(2)))),
 'emitted-add-zero': cast('int', 'PINT 0', cast('bool', 'PBOOL false',
    arithmetic('add', 'PINT 0', cast('int', 'PINT 2', string('2')), negative(2)))),
 'emitted-sub-negative': cast('bool', 'PBOOL true', cast('float', 'PFLOAT 13830554455654793216',
    arithmetic('sub', 'PINT $(-1)', integer(0), cast('int', 'PINT 1', string('1'))))),
 'emitted-mul-zero': cast('int', 'PINT 0', cast('bool', 'PBOOL false',
    arithmetic('mul', 'PINT 0', cast('int', 'PINT 0', string('0')),
               cast('int', 'PINT 3', string('3')))))}


def children(key, node):
    if not node[5]:
        return []
    if key == 'cast':
        return [('cast_1', 0)]
    if key == 'cast_1':
        return [('value', 0)]
    return [(key + '_left', 0), (key + '_right', 1)] if len(node[5]) == 2 else [(key + '_child', 0)]


def nodes(name):
    result = {}

    def visit(key, node):
        result[key] = node
        for (child, _), descendant in zip(children(key, node), node[5]):
            visit(child, descendant)
    visit('cast', TREES[DETAILS[name][1]])
    return result


def expression(name, key='cast'):
    kind, spelling, _, _, _, _ = nodes(name)[key]
    metadata = 'metadata_' + key
    if kind == 'integer':
        return 'NScalarInt (INTEGER ' + spelling + ') ' + metadata
    if kind == 'string':
        return 'NScalarString (BYTES text_' + key + ') ' + metadata
    return kind + ' ' + ' '.join('(' + expression(name, child) + ')' for child, _ in children(key, nodes(name)[key])) + ' ' + metadata


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


def modulo_line(name):
    source = sources.CASES['native-selected-integer-arithmetic-cast-chain-return-modulo-error-' + name]
    assert source.count(b'%') == 1
    return source[:source.index(b'%')].count(b'\n') + 1


def source_lines(name, condition):
    line = modulo_line(name)
    old_line = 8 if 'cv-pair' in DETAILS[name][0] else 6
    facts = ['z = {line}', 'z_left = {line}', 'z_right = {line}',
             'S_request.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Modulo by zero")) {line}',
             '$code_expression_at_source(S, porigin_operator, [PCFIELD 0]) = ({line})',
             '$code_expression_at_source(S, porigin_operator, [PCFIELD 1]) = ({line})']
    for fact in facts:
        condition = condition.replace(fact.format(line=old_line), fact.format(line=line))
    if default(name):
        for event in no.diagnostics(DETAILS[name][0]):
            condition = condition.replace(event, event.rsplit(' ', 1)[0] + ' ' + str(line))
    return condition


def converted(name, condition):
    condition = no.converted(DETAILS[name][0], condition) if default(name) else zero.converted(condition)
    condition = condition.replace('selected_modulo_' + ('false' if default(name) else 'zero') + '_return',
                                  'selected_modulo_integer_arithmetic_cast_chain_return')
    for state in ['S_handler', 'S_handler_right']:
        condition = condition.replace(state + '.RESULT = KNOWN (PINT 0)',
                                      state + '.RESULT = KNOWN (' + root_value(name) + ')')
    return source_lines(name, condition)


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
    condition = source_lines(name, adapted(name, condition))
    old = r'z_cast = $source_line(metadata_cast) /\ b_cast /\ '
    assert condition.count(old) == 1
    condition = condition.replace(old, r'z_cast = z_cast_1 /\ ~b_cast /\ ')
    old = 'z_cast_return = $source_line(metadata_cast_return)'
    assert condition.count(old) == 1
    condition = condition.replace(old, 'z_cast_return = z_cast')
    states = ['S_return', 'S', *(['S_return_right'] if prior.two_calls(context) else [])]
    for state in states:
        read = '$compiled_read(' + state + ', porigin_cast) = (' + root_value(name) + ')'
        assert condition.count(read) == 1
        condition = condition.replace(read, '$compiled_read(' + state + ', porigin_cast) = eps')
    parts = [condition, 'S.COMPLETION = NORMAL', 'z_cast =/= $expression_line(' + expression(name) + ')']
    for key, node in nodes(name).items():
        kind, operator, style, result, folded, descendants = node
        parts += [('b_' if folded else '~b_') + key,
                  '$ob_object_cast_chain_value(S, pfunction_handler, porigin_' + key + ', ' + expression(name, key) + ') = (' + result + ')',
                  '$value_nodes(' + result + ') = eps']
        cache = result
        if kind == 'string':
            cache = 'PSTRING ($ptascii("' + operator + '"))'
            parts += ['$base64(text_' + key + ') = $ptascii("' + operator + '")']
            parts += ['$compiled_string_value(' + state + ', porigin_' + key + ', ' + cache + ') = ' + result for state in states]
        parts += ['$compiled_read(' + state + ', porigin_' + key + ') = ' + ('(' + cache + ')' if folded else 'eps') for state in states]
        if not descendants:
            parts += ['z_' + key + ' = $source_line(metadata_' + key + ')']
            continue
        child = children(key, node)[-1][0]
        parts += ['z_' + key + ' = z_' + child]
        for descendant, field in children(key, node):
            parts += ['pcpath_' + descendant + ' = pcpath_' + key + ' ++ [PCFIELD ' + str(field) + ']']
        child_value = descendants[-1][3]
        if len(descendants) == 2:
            left, right = descendants[0][3], descendants[1][3]
            parts += ['b_' + key + r' = (b_' + key + r'_left /\ b_' + key + '_right)',
                      '$binary_apply(S[.RESULT = KNOWN (' + right + ')], ' + operator + ', ' + left + ', ' + right + ', z_' + key + ') = S[.RESULT = KNOWN (' + result + ')]']
        elif kind in ('NExprUnaryPlus', 'NExprUnaryMinus'):
            parts += ['$unary_apply(S[.RESULT = KNOWN (' + child_value + ')], ' + operator + ', ' + child_value + ', z_' + key + ') = S[.RESULT = KNOWN (' + result + ')]']
        elif kind == 'NExprBitwiseNot':
            parts += ['$bitnot_apply(S[.RESULT = KNOWN (' + child_value + ')], ' + child_value + ', z_' + key + ') = S[.RESULT = KNOWN (' + result + ')]']
        elif kind == 'NExprBooleanNot':
            parts += ['$boolean_result(S[.RESULT = KNOWN (' + child_value + ')], true, z_' + key + ') = S[.RESULT = KNOWN (' + result + ')]']
        else:
            parts += ['$plstyle(metadata_' + key + ') = ' + str(style),
                      '$ob_object_cast_chain_quiet(' + operator + ', ' + child_value + ')',
                      '$cast_apply(S[.RESULT = KNOWN (' + child_value + ')], ' + operator + ', ' + child_value + ', z_' + key + ') = S[.RESULT = KNOWN (' + result + ')]']
    return CONJ.join(parts)


def frontier(name, fixture, path):
    context = DETAILS[name][0]
    bindings, checks = prior.base_for(context).frontier(context, fixture, path)
    return bindings + return_bindings(name), [
        *[(label.replace('NULL', 'terminal-line tree'), converted(name, condition)) for label, condition in checks],
        ('integer arithmetic retains distinct terminal CODE, exact typed results and quiet state through every link', return_proof(name))]


def lifecycle(name, fixture, path):
    context = DETAILS[name][0]
    bindings, checks = prior.base_for(context).lifecycle(context, fixture, path)
    old_line, line = (8 if 'cv-pair' in context else 6), modulo_line(name)

    def fatal(number):
        return (b'Fatal error: Uncaught DivisionByZeroError: Modulo by zero in ' + bytes(path) + b':' + str(number).encode() +
                b'\nStack trace:\n#0 [internal function]: T->__toString()\n#1 {main}\n  thrown in ' + bytes(path) +
                b' on line ' + str(number).encode() + b'\n')

    label, condition = checks[2]
    rendered = prior.prior.value(fatal(old_line))
    pending = 'pobdeactivate.COMPLETION = REQUESTFATAL ($ptascii("DivisionByZeroError")) ' + prior.prior.value(b'Modulo by zero')
    assert condition.count(rendered) == 1 and condition.count(pending + ' ' + str(old_line)) == 1
    checks[2] = (label, condition.replace(rendered, prior.prior.value(fatal(line))).replace(
        pending + ' ' + str(old_line), pending + ' ' + str(line)))
    return bindings + return_bindings(name), [
        *[(label, converted(name, condition)) for label, condition in checks],
        ('integer arithmetic authority and strict typed results survive real formal/native-cell retirement', return_proof(name))]


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
