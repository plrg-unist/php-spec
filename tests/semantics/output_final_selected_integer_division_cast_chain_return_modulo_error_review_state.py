#!/usr/bin/env python3
"""Independent exact-quotient, refusal and real-retirement controls."""
import output_final_selected_constant_float_cast_return_modulo_error_review_state as control
import output_final_selected_recursive_numeric_sign_cast_chain_return_modulo_error_review_state as scaffold
import output_final_selected_integer_arithmetic_cast_chain_return_modulo_error_review_state as affected
import output_final_selected_integer_division_cast_chain_return_modulo_error_state as current
import output_final_selected_integer_division_cast_chain_return_modulo_error_sources as sources

runner, PREFIX = current.runner, scaffold.PREFIX
CASES = {name: sources.CASES['native-selected-integer-division-cast-chain-return-modulo-error-' + name]
         for name in ['warning-left-constant-folded-div-negative',
                      'warning-right-cv-pair-folded-div-one',
                      'deprecated-both-cv-pair-emitted-div-negative']}


def value(state, expression, origin='porigin_value', function='pfunction_handler'):
    return scaffold.value(state, expression, origin, function)


def integer(number):
    return affected.integer(number)


def frontier(name, fixture, path):
    bindings, checks = current.frontier(name, fixture, path)
    bindings += ['$source_unit(S.SOURCES, n_cast_handler) = (pcunit_handler)',
                 '$pool_at(S.POOLS, n_cast_handler) = (ppool_handler)']
    nodes = current.nodes(name)
    checks += [
        ('the actual exact quotient keeps its PINT tag through both outer casts',
         value('S', current.expression(name, 'value')) + ' = (' + nodes['value'][3] + ')'),
        ('a preset quotient cannot replace NORMAL source authority',
         value('S[.COMPLETION = BUDGET][.RESULT = KNOWN (' + nodes['value'][3] + ')]', current.expression(name, 'value')) + ' = eps'),
        ('the quotient handler retains its exact source UNIT and BODY',
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
                       (key + ' cannot borrow an object-tagged fact',
                        '~' + control.tail(control.pool_state('pcpath_' + key, 'POBJECT 0')))]
    expression, result = current.expression(name, 'value'), nodes['value'][3]
    global_code = ('pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR pcpath_value z_value ' +
                   ('false' if nodes['value'][4] else 'true') + ') :: pfunction_handler.CODE.EXPRESSIONS]')
    if nodes['value'][4]:
        checks += [('a folded quotient cannot borrow a missing global compiled read',
                    value('S[.CODE = ' + global_code + ' :: S.CODE]', expression) + ' = eps')]
    else:
        checks += [('an unread forged pool does not fold an actual emitted quotient',
                    value(control.pool_state('pcpath_value', 'POBJECT 0'), expression) + ' = (' + result + ')')]
        state = control.pool_state('pcpath_value', result) + '[.CODE = ' + global_code + ' :: S.CODE]'
        checks += [('a forged exact global read cannot replace emitted read-eps authority',
                    '$compiled_read(' + state + ', porigin_value) = (' + result + r') /\ ' +
                    value(state, expression) + ' = eps')]
    if current.DETAILS[name][1] == 'folded-div-negative':
        # This uses the actual predecessor query builder, not its whole campaign.
        for left, right, result, admitted in [
                ('4', '2', 'PINT 2', True),
                ('2', '4', 'PFLOAT 4602678819172646912', False),
                ('9223372036854775807', '1', 'PINT 9223372036854775807', True),
                ('$(-9223372036854775808)', '1', 'PINT $(-9223372036854775808)', True),
                ('$(-9223372036854775808)', '$(-9223372036854775808)', 'PINT 1', True),
                ('0', '$(-2)', 'PINT 0', True),
                ('$(-6)', '3', 'PINT $(-2)', True),
                ('6', '$(-3)', 'PINT $(-2)', True),
                ('$(-6)', '$(-3)', 'PINT 2', True),
                ('$(-9223372036854775808)', '$(-1)', 'PFLOAT 4890909195324358656', False)]:
            state, expression, function, operator, children, values = affected.binary('div', integer(left), integer(right), result)
            proof = [value(state, child, 'PORIGIN n_cast_handler pcpath_value_' + side, function) + ' = (' + typed + ')'
                     for side, child, typed in zip(['left', 'right'], children, values)]
            proof += ['$binary_apply(' + state + '[.RESULT = KNOWN (' + values[1] + ')], ' + operator + ', ' +
                      values[0] + ', ' + values[1] + ', z_value_right) = ' + state + '[.RESULT = KNOWN (' + result + ')]',
                      value(state, expression, function=function) + (' = (' + result + ')' if admitted else ' = eps')]
            label = ('source0 affected old135 DIV4/2 query is now admitted' if left == '4' and right == '2' else
                     'source0 quotient keeps exact order/sign/width and refuses FLOAT results')
            checks += [(label, current.CONJ.join(proof))]
        state, expression, function, operator, children, values = affected.binary('div', integer('1'), integer('0'), 'PINT 0')
        checks += [('source0 a forged folded zero quotient cannot erase genuine division-by-zero failure',
                    value(state, children[0], 'PORIGIN n_cast_handler pcpath_value_left', function) + r' = (PINT 1) /\ ' +
                    value(state, children[1], 'PORIGIN n_cast_handler pcpath_value_right', function) + r' = (PINT 0) /\ ' +
                    '$binary_apply(' + state + '[.RESULT = KNOWN (PINT 0)], DIVIDE, PINT 1, PINT 0, z_value_right).COMPLETION = '
                    r'THROWN "DivisionByZeroError" ($ptascii("Division by zero")) z_value_right /\ ' +
                    value(state, expression, function=function) + ' = eps')]
        true = ('NExprConstFetch (NName (BYTES "dHJ1ZQ==") {metadata}) {metadata}', 'PBOOL true', 'PBOOL true')
        null = ('NExprConstFetch (NName (BYTES "bnVsbA==") {metadata}) {metadata}', 'PNULL', 'PNULL')
        floating = ('NScalarFloat (FLOAT "3ff0000000000000") {metadata}',
                    'PFLOAT 4607182418800017408', 'PFLOAT 4607182418800017408')
        string = ('NScalarString (BYTES "Mg==") {metadata}',
                  'PSTRING_CARRIER INTERNED_STRING ($ptascii("2"))', 'PSTRING ($ptascii("2"))')
        for left, right, result in [(integer('1'), true, 'PINT 1'), (null, integer('1'), 'PINT 0'),
                                    (floating, integer('1'), 'PFLOAT 4607182418800017408'),
                                    (integer('2'), string, 'PINT 1')]:
            state, expression, function, operator, children, values = affected.binary('div', left, right, result)
            proof = [value(state, child, 'PORIGIN n_cast_handler pcpath_value_' + side, function) + ' = (' + typed + ')'
                     for side, child, typed in zip(['left', 'right'], children, values)]
            proof += ['$binary_apply(' + state + '[.RESULT = KNOWN (' + values[1] + ')], ' + operator + ', ' +
                      values[0] + ', ' + values[1] + ', z_value_right) = ' + state + '[.RESULT = KNOWN (' + result + ')]',
                      value(state, expression, function=function) + (' = (' + result + ')' if result.startswith('PINT ') else ' = eps')]
            checks += [('source0 proper primitive children keep exact quiet signed PINT results and refuse FLOAT results', current.CONJ.join(proof))]
    bare = 'NStmtReturn (' + current.expression(name, 'value') + ') metadata_cast_return'
    single = nodes['cast_1'][0] + ' (' + current.expression(name, 'value') + ') metadata_cast_1'
    statement = 'NStmtReturn (' + single + ') metadata_cast_return'
    checks += [('exact quotient helper authority preserves bare and single-cast handler fences',
                '~' + control.tail(control.source_state([('pcpath_cast_return', bare)]), statement=bare) + r' /\ ~' +
                control.tail(control.source_state([('pcpath_cast_return', statement), ('pcpath_cast', single)]), statement=statement))]
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = current.lifecycle(name, fixture, path)
    checks += [('the exact quotient return survives real formal/native-cell retirement',
                'S_handler.RESULT = KNOWN (' + current.root_value(name) + r') /\ S.RESULT = KNOWN PNULL /\ ' +
                value('S', current.expression(name), 'porigin_cast') + ' = (' + current.root_value(name) + ')')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
