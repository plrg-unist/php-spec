#!/usr/bin/env python3
"""Independent integer arithmetic, promotion and source-authority controls."""
import output_final_selected_constant_float_cast_return_modulo_error_review_state as control
import output_final_selected_recursive_numeric_sign_cast_chain_return_modulo_error_review_state as scaffold
import output_final_selected_integer_arithmetic_cast_chain_return_modulo_error_state as current
import output_final_selected_integer_arithmetic_cast_chain_return_modulo_error_sources as sources

runner, PREFIX = current.runner, scaffold.PREFIX
CASES = {name: sources.CASES['native-selected-integer-arithmetic-cast-chain-return-modulo-error-' + name]
         for name in ['warning-left-constant-folded-sub-negative',
                      'warning-right-cv-pair-folded-mul-one',
                      'deprecated-both-cv-pair-emitted-sub-negative']}


def value(state, expression, origin='porigin_value', function='pfunction_handler'):
    return scaffold.value(state, expression, origin, function)


def binary(kind, left, right, result):
    constructor, operator = {'add': ('NExprBinaryOpPlus', 'ADD'),
                             'sub': ('NExprBinaryOpMinus', 'SUBTRACT'),
                             'mul': ('NExprBinaryOpMul', 'MULTIPLY'),
                             'div': ('NExprBinaryOpDiv', 'DIVIDE')}[kind]
    rows, codes, facts, expressions, values = [], [], [], [], []
    for side, (node, typed, pooled) in [('left', left), ('right', right)]:
        path, line = 'pcpath_value_' + side, 'z_value_' + side
        metadata = '([(MstartLine ' + line + ')])'
        expression = node.format(metadata=metadata)
        rows += [(path, expression)]
        if 'NExprConstFetch' in expression:
            rows += [('(' + path + ' ++ [PCFIELD 0])',
                      expression[len('NExprConstFetch ('):].removesuffix(') ' + metadata))]
        codes += [(path, line, 'true')]
        facts += [(path, pooled)]
        expressions += [expression]
        values += [typed]
    expression = constructor + ' (' + expressions[0] + ') (' + expressions[1] + ') ([(MstartLine z_value_left)])'
    state, function = scaffold.changed([('pcpath_value', expression), *rows],
        [('pcpath_value', 'z_value_right', 'true'), *codes], [('pcpath_value', result), *facts])
    return state, expression, function, operator, expressions, values


def integer(number):
    return ('NScalarInt (INTEGER ' + number + ') {metadata}', 'PINT ' + number, 'PINT ' + number)


def frontier(name, fixture, path):
    bindings, checks = current.frontier(name, fixture, path)
    bindings += ['$source_unit(S.SOURCES, n_cast_handler) = (pcunit_handler)',
                 '$pool_at(S.POOLS, n_cast_handler) = (ppool_handler)']
    nodes = current.nodes(name)
    checks += [
        ('the actual binary subtree keeps its signed64 integer tag through both outer casts',
         value('S', current.expression(name, 'value')) + ' = (' + nodes['value'][3] + ')'),
        ('a preset result cannot replace NORMAL source authority',
         value('S[.COMPLETION = BUDGET][.RESULT = KNOWN (' + nodes['value'][3] + ')]', current.expression(name, 'value')) + ' = eps'),
        ('the arithmetic handler keeps its exact source UNIT and BODY',
         '~' + control.tail(function='pfunction_handler[.CODE.UNIT = $(n_cast_handler + 1)]') + r' /\ ~' +
         control.tail(function='pfunction_handler[.BODY = pfunction_handler.BODY ++ [PCINDEX 0]]'))]
    for key, node in nodes.items():
        flag = 'true' if node[4] else 'false'
        for label, line, changed_flag in [('line', '$(z_' + key + ' + 1)', flag),
                                          ('flag', 'z_' + key, 'false' if node[4] else 'true')]:
            checks += [(key + ' keeps its exact compiler ' + label,
                        '~' + control.tail(function=control.code_function('pcpath_' + key, line, changed_flag)))]
        state = ('S[.SOURCES = pcunit_handler[.OCCURRENCES = '
                 '$or131_drop(pcunit_handler.OCCURRENCES, pcpath_' + key + ')] :: S.SOURCES]')
        checks += [(key + ' cannot borrow another proper source occurrence', '~' + control.tail(state))]
        if node[4]:
            state = ('S[.POOLS = ppool_handler[.CONSTANTS = '
                     '$or131_fact_drop(ppool_handler.CONSTANTS, pcpath_' + key + ')] :: S.POOLS]')
            checks += [(key + ' retains its own folded fact', '~' + control.tail(state)),
                       (key + ' cannot borrow an object-tagged folded fact',
                        '~' + control.tail(control.pool_state('pcpath_' + key, 'POBJECT 0')))]
    expression, result = current.expression(name, 'value'), nodes['value'][3]
    global_code = ('pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR pcpath_value z_value ' +
                   ('false' if nodes['value'][4] else 'true') + ') :: pfunction_handler.CODE.EXPRESSIONS]')
    if nodes['value'][4]:
        checks += [('folded arithmetic cannot borrow a missing global compiled read',
                    value('S[.CODE = ' + global_code + ' :: S.CODE]', expression) + ' = eps')]
    else:
        checks += [('an unread forged pool does not fold actual emitted arithmetic',
                    value(control.pool_state('pcpath_value', 'POBJECT 0'), expression) + ' = (' + result + ')')]
        state = control.pool_state('pcpath_value', result) + '[.CODE = ' + global_code + ' :: S.CODE]'
        checks += [('a forged exact global read cannot replace emitted read-eps authority',
                    '$compiled_read(' + state + ', porigin_value) = (' + result + r') /\ ' +
                    value(state, expression) + ' = eps')]
    if current.DETAILS[name][1] == 'folded-sub-negative':
        for kind, left, right, result, admitted in [
                ('add', '9223372036854775807', '0', 'PINT 9223372036854775807', True),
                ('sub', '$(-9223372036854775808)', '0', 'PINT $(-9223372036854775808)', True),
                ('mul', '$(-9223372036854775808)', '1', 'PINT $(-9223372036854775808)', True),
                ('sub', '4', '9', 'PINT $(-5)', True),
                ('sub', '9', '4', 'PINT 5', True),
                ('add', '9223372036854775807', '1', 'PFLOAT 4890909195324358656', False),
                ('sub', '$(-9223372036854775808)', '1', 'PFLOAT 14114281232179134464', False),
                ('mul', '$(-9223372036854775808)', '$(-1)', 'PFLOAT 4890909195324358656', False),
                ('div', '4', '2', 'PINT 2', True)]:
            state, expression, function, operator, children, values = binary(kind, integer(left), integer(right), result)
            proof = [value(state, child, 'PORIGIN n_cast_handler pcpath_value_' + side, function) + ' = (' + typed + ')'
                     for side, child, typed in zip(['left', 'right'], children, values)]
            proof += ['$binary_apply(' + state + '[.RESULT = KNOWN (' + values[1] + ')], ' + operator + ', ' +
                      values[0] + ', ' + values[1] + ', z_value_right) = ' + state + '[.RESULT = KNOWN (' + result + ')]',
                      value(state, expression, function=function) + (' = (' + result + ')' if admitted else ' = eps')]
            checks += [('source0 ' + kind + ' keeps endpoint/order results and refuses promotion or other operators', current.CONJ.join(proof))]
        false = ('NExprConstFetch (NName (BYTES "ZmFsc2U=") {metadata}) {metadata}', 'PBOOL false', 'PBOOL false')
        null = ('NExprConstFetch (NName (BYTES "bnVsbA==") {metadata}) {metadata}', 'PNULL', 'PNULL')
        floating = ('NScalarFloat (FLOAT "3ff0000000000000") {metadata}',
                    'PFLOAT 4607182418800017408', 'PFLOAT 4607182418800017408')
        string = ('NScalarString (BYTES "Mg==") {metadata}',
                  'PSTRING_CARRIER INTERNED_STRING ($ptascii("2"))', 'PSTRING ($ptascii("2"))')
        for kind, left, right, result in [
                ('add', false, integer('1'), 'PINT 1'),
                ('sub', integer('1'), null, 'PINT 1'),
                ('mul', floating, integer('2'), 'PFLOAT 4611686018427387904'),
                ('add', integer('1'), string, 'PINT 3')]:
            state, expression, function, operator, children, values = binary(kind, left, right, result)
            proof = [value(state, child, 'PORIGIN n_cast_handler pcpath_value_' + side, function) + ' = (' + typed + ')'
                     for side, child, typed in zip(['left', 'right'], children, values)]
            proof += ['$binary_apply(' + state + '[.RESULT = KNOWN (' + values[1] + ')], ' + operator + ', ' +
                      values[0] + ', ' + values[1] + ', z_value_right) = ' + state + '[.RESULT = KNOWN (' + result + ')]',
                      value(state, expression, function=function) + ' = eps']
            checks += [('source0 certified BOOL/NULL/FLOAT/STRING children retain their quiet coercion boundary', current.CONJ.join(proof))]
    bare = 'NStmtReturn (' + current.expression(name, 'value') + ') metadata_cast_return'
    single = nodes['cast_1'][0] + ' (' + current.expression(name, 'value') + ') metadata_cast_1'
    statement = 'NStmtReturn (' + single + ') metadata_cast_return'
    checks += [('arithmetic helper authority preserves bare and single-cast handler fences',
                '~' + control.tail(control.source_state([('pcpath_cast_return', bare)]), statement=bare) + r' /\ ~' +
                control.tail(control.source_state([('pcpath_cast_return', statement), ('pcpath_cast', single)]), statement=statement))]
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = current.lifecycle(name, fixture, path)
    checks += [('the exact arithmetic return survives real formal/native-cell retirement',
                'S_handler.RESULT = KNOWN (' + current.root_value(name) + r') /\ S.RESULT = KNOWN PNULL /\ ' +
                value('S', current.expression(name), 'porigin_cast') + ' = (' + current.root_value(name) + ')')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
