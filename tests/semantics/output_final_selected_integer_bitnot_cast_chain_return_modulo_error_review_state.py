#!/usr/bin/env python3
"""Independent signed-width, type, source and retirement controls for INT NOT."""
import output_final_selected_constant_float_cast_return_modulo_error_review_state as control
import output_final_selected_recursive_numeric_sign_cast_chain_return_modulo_error_review_state as scaffold
import output_final_selected_integer_bitnot_cast_chain_return_modulo_error_state as current
import output_final_selected_integer_bitnot_cast_chain_return_modulo_error_sources as sources

runner, PREFIX, value = current.runner, scaffold.PREFIX, scaffold.value
CASES = {name: sources.CASES['native-selected-integer-bitnot-cast-chain-return-modulo-error-' + name]
         for name in ['warning-left-constant-folded-negative', 'warning-right-cv-pair-emitted-zero']}


def integer(i):
    return str(i) if i >= 0 else '$(' + str(i) + ')'


def raw_not(leaf, raw, result, name=None):
    expression = 'NExprBitwiseNot (' + leaf + ') metadata_sign'
    rows = [('pcpath_sign', expression), ('pcpath_child_3', leaf)]
    if name is not None:
        rows += [('(pcpath_child_3 ++ [PCFIELD 0])', name)]
    state, function = scaffold.changed(rows,
        [('pcpath_sign', '$expression_line(' + leaf + ')', 'true'),
         ('pcpath_child_3', '$source_line(metadata_child_3)', 'true')],
        [('pcpath_child_3', raw), ('pcpath_sign', result)])
    return state, expression, function


def frontier(name, fixture, path):
    bindings, checks = current.frontier(name, fixture, path)
    bindings += ['$source_unit(S.SOURCES, n_cast_handler) = (pcunit_handler)',
                 '$pool_at(S.POOLS, n_cast_handler) = (ppool_handler)']
    expression, result = current.expression(name, 2), current.nodes(name)[2][3]
    checks += [
        ('the actual complement retains an exact signed64 PINT with no owner',
         value('S', expression) + ' = (' + result + r') /\ $value_nodes(' + result + ') = eps'),
        ('an abrupt preset result cannot borrow the no-op bitnot helper',
         value('S[.COMPLETION = BUDGET][.RESULT = KNOWN (' + result + ')]', expression) + ' = eps'),
        ('own handler CODE unit and BODY remain required',
         '~' + control.tail(function='pfunction_handler[.CODE.UNIT = $(n_cast_handler + 1)]') + r' /\ ~' +
         control.tail(function='pfunction_handler[.BODY = pfunction_handler.BODY ++ [PCINDEX 0]]'))]
    for index, (_, _, _, _, folded) in enumerate(current.nodes(name)):
        slot = current.slot(index)
        flag = 'true' if folded else 'false'
        for label, line, changed_flag in [('flag', 'z_' + slot, 'false' if folded else 'true'),
                                          ('line', '$(z_' + slot + ' + 1)', flag)]:
            checks += [(slot + ' exact CODE ' + label + ' is required through the whole tail',
                        '~' + control.tail(function=control.code_function('pcpath_' + slot, line, changed_flag)))]
        state = ('S[.SOURCES = pcunit_handler[.OCCURRENCES = '
                 '$or131_drop(pcunit_handler.OCCURRENCES, pcpath_' + slot + ')] :: S.SOURCES]')
        checks += [('removing only ' + slot + ' source refuses the entire tail', '~' + control.tail(state))]
        if folded:
            state = ('S[.POOLS = ppool_handler[.CONSTANTS = '
                     '$or131_fact_drop(ppool_handler.CONSTANTS, pcpath_' + slot + ')] :: S.POOLS]')
            checks += [(slot + ' folded fact is independently required', '~' + control.tail(state)),
                       (slot + ' wrong-tag owner fact cannot replace an INT certificate',
                        '~' + control.tail(control.pool_state('pcpath_' + slot, 'POBJECT 0')))]
    if current.nodes(name)[2][4]:
        checks += [('a folded complement needs its exact own value',
                    value(control.pool_state('pcpath_sign', 'PINT 0'), expression) + ' = eps')]
        code = ('pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR pcpath_sign z_sign false) :: '
                'pfunction_handler.CODE.EXPRESSIONS]')
        checks += [('an unread folded pool cannot replace genuine global CODE',
                    value('S[.CODE = ' + code + ' :: S.CODE]', expression) + ' = eps')]
    else:
        checks += [('an unread forged pool cannot change an emitted complement',
                    value(control.pool_state('pcpath_sign', 'POBJECT 0'), expression) + ' = (' + result + ')')]
        code = ('pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR pcpath_sign z_sign true) :: '
                'pfunction_handler.CODE.EXPRESSIONS]')
        state = control.pool_state('pcpath_sign', result) + '[.CODE = ' + code + ' :: S.CODE]'
        checks += [('an exact forged global read cannot replace emitted read-eps',
                    '$compiled_read(' + state + ', porigin_sign) = (' + result + r') /\ ' +
                    value(state, expression) + ' = eps')]
    if current.DETAILS[name][1] == 'folded-negative':
        for i, j in [(0, -1), (-1, 0), (-9223372036854775808, 9223372036854775807),
                     (9223372036854775807, -9223372036854775808)]:
            leaf = 'NScalarInt (INTEGER ' + integer(i) + ') metadata_child_3'
            raw, complement = 'PINT ' + integer(i), 'PINT ' + integer(j)
            state, expr, function = raw_not(leaf, raw, complement)
            checks += [('source0 exact INT complement preserves zero and both signed64 endpoints',
                        value(state, leaf, 'porigin_child_3', function) + ' = (' + raw + r') /\ ' +
                        value(state, expr, function=function) + ' = (' + complement + ')')]
        for i in [-9223372036854775809, 9223372036854775808]:
            leaf = 'NScalarInt (INTEGER ' + integer(i) + ') metadata_child_3'
            state, expr, function = raw_not(leaf, 'PINT ' + integer(i), 'PINT ' + integer(-i-1))
            checks += [('out-of-range mathematical integers cannot masquerade as signed64 children',
                        value(state, expr, function=function) + ' = eps')]
        for payload, raw in [('ZmFsc2U=', 'PBOOL false'), ('bnVsbA==', 'PNULL')]:
            node = 'NName (BYTES "' + payload + '") metadata_child_3'
            leaf = 'NExprConstFetch (' + node + ') metadata_child_3'
            state, expr, function = raw_not(leaf, raw, 'PINT $(-1)', name=node)
            checks += [('a properly certified Boolean or NULL child remains outside integer bitnot',
                        value(state, leaf, 'porigin_child_3', function) + ' = (' + raw + r') /\ ' +
                        value(state, expr, function=function) + ' = eps')]
        for leaf, raw, typed, complement in [
                ('NScalarFloat (FLOAT "3ff0000000000000") metadata_child_3', 'PFLOAT 4607182418800017408', 'PFLOAT 4607182418800017408', 'PINT $(-2)'),
                ('NScalarString (BYTES "MA==") metadata_child_3', 'PSTRING ($ptascii("0"))', 'PSTRING_CARRIER INTERNED_STRING ($ptascii("0"))', 'PINT $(-1)')]:
            state, expr, function = raw_not(leaf, raw, complement)
            checks += [('an exact integral FLOAT complements while a numeric STRING retains bytewise semantics',
                        value(state, leaf, 'porigin_child_3', function) + ' = (' + typed + r') /\ ' +
                        value(state, expr, function=function) + (' = (' + complement + ')' if raw.startswith('PFLOAT ') else ' = eps'))]
        leaf = 'NScalarInt (INTEGER 1) metadata_child_3'
        child = 'NExprBitwiseNot (' + leaf + ') metadata_child_3'
        expr = 'NExprBitwiseNot (' + child + ') metadata_sign'
        rows = [('pcpath_sign', expr), ('pcpath_child_3', child), ('(pcpath_child_3 ++ [PCFIELD 0])', leaf)]
        codes = [('pcpath_sign', '$expression_line(' + child + ')', 'true'),
                 ('pcpath_child_3', '$expression_line(' + leaf + ')', 'true'),
                 ('(pcpath_child_3 ++ [PCFIELD 0])', '$source_line(metadata_child_3)', 'true')]
        facts = [('pcpath_sign', 'PINT 1'), ('pcpath_child_3', 'PINT $(-2)'),
                 ('(pcpath_child_3 ++ [PCFIELD 0])', 'PINT 1')]
        state, function = scaffold.changed(rows, codes, facts)
        incomplete, incomplete_function = scaffold.changed(rows[:2], codes, facts)
        checks += [('two genuine proper INT bitnot nodes compose without changing the original integer',
                    value(state, child, 'porigin_child_3', function) + r' = (PINT $(-2)) /\ ' +
                    value(state, expr, function=function) + ' = (PINT 1)'),
                   ('the same double complement cannot skip its proper grandchild source',
                    value(incomplete, expr, function=incomplete_function) + ' = eps')]
    bare = 'NStmtReturn (' + expression + ') metadata_cast_return'
    single = current.nodes(name)[1][0] + ' (' + expression + ') metadata_cast_1'
    statement = 'NStmtReturn (' + single + ') metadata_cast_return'
    checks += [('the helper leaves bare and single-cast bitnot handler routes refused',
                '~' + control.tail(control.source_state([('pcpath_cast_return', bare)]), statement=bare) + r' /\ ~' +
                control.tail(control.source_state([('pcpath_cast_return', statement), ('pcpath_cast', single)]), statement=statement))]
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = current.lifecycle(name, fixture, path)
    checks += [('the exact INT subtree and typed handler return survive actual formal/native-cell retirement',
                'S_handler.RESULT = KNOWN (' + current.root_value(name) + r') /\ S.RESULT = KNOWN PNULL /\ ' +
                value('S', current.expression(name, 2)) + ' = (' + current.nodes(name)[2][3] + ')')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
