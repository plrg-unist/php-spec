#!/usr/bin/env python3
"""Independent multiline terminal-line authority and retirement controls."""
import output_final_selected_constant_float_cast_return_modulo_error_review_state as control
import output_final_selected_recursive_numeric_sign_cast_chain_return_modulo_error_review_state as scaffold
import output_final_selected_terminal_line_bitwise_cast_chain_return_modulo_error_state as current
import output_final_selected_terminal_line_bitwise_cast_chain_return_modulo_error_sources as sources

runner, PREFIX = current.runner, scaffold.PREFIX
CASES = {name: sources.CASES['native-selected-terminal-line-bitwise-cast-chain-return-modulo-error-' + name]
         for name in ['warning-left-constant-folded-negative-or',
                      'warning-right-cv-pair-folded-xor-one',
                      'deprecated-both-cv-pair-emitted-not-or']}


def value(state, expression, origin='porigin_cast', function='pfunction_handler'):
    return scaffold.value(state, expression, origin, function)


def nested(key, terminal_offset=0, inner_offset=0, leaf_offset=0):
    path = 'pcpath_' + key
    left, right = '(' + path + ' ++ [PCFIELD 0])', '(' + path + ' ++ [PCFIELD 1])'
    middle, last = '(' + right + ' ++ [PCFIELD 0])', '(' + right + ' ++ [PCFIELD 1])'
    line = 'z_' + key
    meta = lambda offset: '([(MstartLine $(' + line + ' + ' + str(offset) + '))])'
    first = 'NScalarInt (INTEGER 6) ' + meta(0)
    second = 'NScalarInt (INTEGER 1) ' + meta(1)
    third = 'NScalarInt (INTEGER 1) ' + meta(2)
    child = 'NExprBinaryOpBitwiseXor (' + second + ') (' + third + ') ' + meta(1)
    expression = 'NExprBinaryOpBitwiseOr (' + first + ') (' + child + ') ' + meta(0)
    rows = [(path, expression), (left, first), (right, child), (middle, second), (last, third)]
    codes = [(path, '$(' + line + ' + ' + str(2 + terminal_offset) + ')', 'true'),
             (left, line, 'true'),
             (right, '$(' + line + ' + ' + str(2 + inner_offset) + ')', 'true'),
             (middle, '$(' + line + ' + 1)', 'true'),
             (last, '$(' + line + ' + ' + str(2 + leaf_offset) + ')', 'true')]
    facts = [(path, 'PINT 6'), (left, 'PINT 6'), (right, 'PINT 0'), (middle, 'PINT 1'), (last, 'PINT 1')]
    state, function = scaffold.changed(rows, codes, facts)
    return state, expression, child, right, function


def frontier(name, fixture, path):
    bindings, checks = current.frontier(name, fixture, path)
    bindings += ['$source_unit(S.SOURCES, n_cast_handler) = (pcunit_handler)',
                 '$pool_at(S.POOLS, n_cast_handler) = (ppool_handler)']
    nodes = current.nodes(name)
    root = current.expression(name)
    checks += [
        ('an actual multiline root uses terminal CODE rather than its syntax start',
         '$expression_line(' + root + r') =/= z_cast /\ ' + value('S', root) + ' = (' + current.root_value(name) + ')'),
        ('an abrupt preset result cannot supply terminal-line authority',
         value('S[.COMPLETION = BUDGET][.RESULT = KNOWN (' + current.root_value(name) + ')]', root) + ' = eps'),
        ('the multiline tail retains its original handler UNIT and BODY',
         '~' + control.tail(function='pfunction_handler[.CODE.UNIT = $(n_cast_handler + 1)]') + r' /\ ~' +
         control.tail(function='pfunction_handler[.BODY = pfunction_handler.BODY ++ [PCINDEX 0]]'))]
    for key, node in nodes.items():
        expression = current.expression(name, key)
        flag = 'true' if node[4] else 'false'
        for label, line, changed_flag in [('line', '$(z_' + key + ' + 1)', flag),
                                          ('flag', 'z_' + key, 'false' if node[4] else 'true')]:
            checks += [(key + ' exact compiler ' + label + ' remains required',
                        '~' + control.tail(function=control.code_function('pcpath_' + key, line, changed_flag)))]
        state = ('S[.SOURCES = pcunit_handler[.OCCURRENCES = '
                 '$or131_drop(pcunit_handler.OCCURRENCES, pcpath_' + key + ')] :: S.SOURCES]')
        checks += [(key + ' missing proper source cannot borrow terminal CODE', '~' + control.tail(state))]
        if node[4]:
            state = ('S[.POOLS = ppool_handler[.CONSTANTS = '
                     '$or131_fact_drop(ppool_handler.CONSTANTS, pcpath_' + key + ')] :: S.POOLS]')
            checks += [(key + ' keeps its own folded fact', '~' + control.tail(state))]
        if key in ['cast', 'cast_1', 'value'] and node[5]:
            function = control.code_function('pcpath_' + key, '$expression_line(' + expression + ')', flag)
            checks += [(key + ' authentic syntax start cannot replace its different terminal CODE line',
                        '$expression_line(' + expression + ') =/= z_' + key + r' /\ ~' + control.tail(function=function))]
    binary = next(key for key, node in nodes.items() if len(node[5]) == 2)
    if current.DETAILS[name][1] == 'folded-negative-or':
        state, expression, child, child_path, function = nested(binary)
        origin = 'porigin_' + binary
        checks += [('source0 recursive RHS authenticates three distinct leaf lines and propagates the final one',
                    value(state, child, 'PORIGIN n_cast_handler ' + child_path, function) + r' = (PINT 0) /\ ' +
                    value(state, expression, origin, function) + ' = (PINT 6)')]
        for label, parent_offset, child_offset, leaf_offset in [
                ('parent syntax', -2, 0, 0), ('RHS syntax', 0, -1, 0),
                ('coherent parent and RHS syntax', -1, -1, 0),
                ('coherent parent, RHS and terminal leaf CODE forgery', 1, 1, 1)]:
            state, expression, _, _, function = nested(binary, parent_offset, child_offset, leaf_offset)
            checks += [('source0 ' + label + ' cannot replace exact recursive terminal lines',
                        value(state, expression, origin, function) + ' = eps')]
        child_key = current.children(binary, nodes[binary])[1][0]
        expression = current.expression(name, binary)
        function = control.code_function('pcpath_' + binary, 'z_' + current.children(binary, nodes[binary])[0][0], 'true')
        checks += [('a genuine left terminal line cannot replace the distinct RHS terminal line',
                    'z_' + child_key + ' =/= z_' + current.children(binary, nodes[binary])[0][0] + r' /\ ~' + control.tail(function=function))]
    expression = current.expression(name, 'value')
    bare = 'NStmtReturn (' + expression + ') metadata_cast_return'
    single = nodes['cast_1'][0] + ' (' + expression + ') metadata_cast_1'
    statement = 'NStmtReturn (' + single + ') metadata_cast_return'
    checks += [('multiline helper authority does not bypass bare and single-cast handler fences',
                '~' + control.tail(control.source_state([('pcpath_cast_return', bare)]), statement=bare) + r' /\ ~' +
                control.tail(control.source_state([('pcpath_cast_return', statement), ('pcpath_cast', single)]), statement=statement))]
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = current.lifecycle(name, fixture, path)
    root = current.expression(name)
    checks += [('the exact multiline return and terminal line survive real formal/native-cell retirement',
                'S_handler.RESULT = KNOWN (' + current.root_value(name) + r') /\ S.RESULT = KNOWN PNULL /\ ' +
                '$expression_line(' + root + r') =/= z_cast /\ ' + value('S', root) + ' = (' + current.root_value(name) + ')')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
