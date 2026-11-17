#!/usr/bin/env python3
"""Independent two-child, signed-width, line and retirement controls."""
import output_final_selected_constant_float_cast_return_modulo_error_review_state as control
import output_final_selected_recursive_numeric_sign_cast_chain_return_modulo_error_review_state as scaffold
import output_final_selected_integer_bitwise_cast_chain_return_modulo_error_state as current
import output_final_selected_integer_bitwise_cast_chain_return_modulo_error_sources as sources

runner, PREFIX = current.runner, scaffold.PREFIX
CASES = {name: sources.CASES['native-selected-integer-bitwise-cast-chain-return-modulo-error-' + name]
         for name in ['warning-left-constant-folded-or-negative',
                      'warning-right-cv-pair-folded-xor-one',
                      'warning-deprecated-constant-float-emitted-and-zero']}


def value(state, expression, origin='porigin_binary', function='pfunction_handler'):
    return scaffold.value(state, expression, origin, function)


def integer(i):
    return str(i) if i >= 0 else '$(' + str(i) + ')'


def leaf(i, side):
    return 'NScalarInt (INTEGER ' + integer(i) + ') metadata_bit_' + side


def pair(kind, left, right, result, extras=(), codes=()):
    expression = kind + ' (' + left[0] + ') (' + right[0] + ') metadata_binary'
    rows = [('pcpath_binary', expression), ('pcpath_bit_left', left[0]),
            ('pcpath_bit_right', right[0]), *extras]
    entries = [('pcpath_binary', '$expression_line(' + right[0] + ')', 'true'),
               ('pcpath_bit_left', '$expression_line(' + left[0] + ')', 'true'),
               ('pcpath_bit_right', '$expression_line(' + right[0] + ')', 'true'), *codes]
    state, function = scaffold.changed(rows, entries,
        [('pcpath_bit_left', left[1]), ('pcpath_bit_right', right[1]), ('pcpath_binary', result)])
    return state, expression, function


def frontier(name, fixture, path):
    bindings, checks = current.frontier(name, fixture, path)
    bindings += ['$source_unit(S.SOURCES, n_cast_handler) = (pcunit_handler)',
                 '$pool_at(S.POOLS, n_cast_handler) = (ppool_handler)']
    nodes = current.nodes(name)
    expression, result = current.expression(name, 'binary'), nodes['binary'][3]
    checks += [
        ('the actual binary result is an exact nonowning signed64 integer',
         value('S', expression) + ' = (' + result + r') /\ $value_nodes(' + result + ') = eps'),
        ('a preset result under abrupt completion cannot replace NORMAL authority',
         value('S[.COMPLETION = BUDGET][.RESULT = KNOWN (' + result + ')]', expression) + ' = eps'),
        ('the handler retains its exact source CODE unit and BODY',
         '~' + control.tail(function='pfunction_handler[.CODE.UNIT = $(n_cast_handler + 1)]') + r' /\ ~' +
         control.tail(function='pfunction_handler[.BODY = pfunction_handler.BODY ++ [PCINDEX 0]]'))]
    for key, node in nodes.items():
        flag = 'true' if node[4] else 'false'
        for label, line, changed_flag in [('flag', 'z_' + key, 'false' if node[4] else 'true'),
                                          ('line', '$(z_' + key + ' + 1)', flag)]:
            checks += [(key + ' exact CODE ' + label + ' is required through the whole tail',
                        '~' + control.tail(function=control.code_function('pcpath_' + key, line, changed_flag)))]
        state = ('S[.SOURCES = pcunit_handler[.OCCURRENCES = '
                 '$or131_drop(pcunit_handler.OCCURRENCES, pcpath_' + key + ')] :: S.SOURCES]')
        checks += [('removing only ' + key + ' source refuses the whole tail', '~' + control.tail(state))]
        if node[4]:
            state = ('S[.POOLS = ppool_handler[.CONSTANTS = '
                     '$or131_fact_drop(ppool_handler.CONSTANTS, pcpath_' + key + ')] :: S.POOLS]')
            checks += [(key + ' needs its own folded fact', '~' + control.tail(state)),
                       (key + ' cannot borrow an owning fact with another tag',
                        '~' + control.tail(control.pool_state('pcpath_' + key, 'POBJECT 0')))]
    if nodes['binary'][4]:
        checks += [('a folded binary requires its exact own integer independently of child facts',
                    value(control.pool_state('pcpath_binary', 'PINT 8'), expression) + ' = eps')]
        code = ('pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR pcpath_binary z_binary false) :: '
                'pfunction_handler.CODE.EXPRESSIONS]')
        checks += [('an unread folded pool cannot replace genuine global CODE',
                    value('S[.CODE = ' + code + ' :: S.CODE]', expression) + ' = eps')]
    else:
        checks += [('an unread owning pool cannot change an emitted integer result',
                    value(control.pool_state('pcpath_binary', 'POBJECT 0'), expression) + ' = (' + result + ')')]
        code = ('pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR pcpath_binary z_binary true) :: '
                'pfunction_handler.CODE.EXPRESSIONS]')
        state = control.pool_state('pcpath_binary', result) + '[.CODE = ' + code + ' :: S.CODE]'
        checks += [('an exact forged global read cannot replace emitted read-eps',
                    '$compiled_read(' + state + ', porigin_binary) = (' + result + r') /\ ' +
                    value(state, expression) + ' = eps')]
    if current.DETAILS[name][1] == 'folded-or-negative':
        for kind, i, j, expected in [('And', -9223372036854775808, 9223372036854775807, 0),
                                     ('Or', -9223372036854775808, 9223372036854775807, -1),
                                     ('Xor', -9223372036854775808, -1, 9223372036854775807),
                                     ('Xor', 9223372036854775807, -1, -9223372036854775808)]:
            typed = 'PINT ' + integer(expected)
            state, expr, function = pair('NExprBinaryOpBitwise' + kind,
                (leaf(i, 'left'), 'PINT ' + integer(i)), (leaf(j, 'right'), 'PINT ' + integer(j)), typed)
            checks += [('source0 exact signed64 endpoints retain the expected ' + kind + ' result',
                        value(state, expr, function=function) + ' = (' + typed + ')')]
        for side in ['left', 'right']:
            for i in [-9223372036854775809, 9223372036854775808]:
                children = [(leaf(1, 'left'), 'PINT 1'), (leaf(1, 'right'), 'PINT 1')]
                children[side == 'right'] = (leaf(i, side), 'PINT ' + integer(i))
                state, expr, function = pair('NExprBinaryOpBitwiseAnd', *children, 'PINT 0')
                checks += [('out-of-range ' + side + ' integers refuse before binary application',
                            value(state, expr, function=function) + ' = eps')]
            for constructor, raw, typed, expected in [
                    ('NExprConstFetch (NName (BYTES "ZmFsc2U=") METADATA) METADATA', 'PBOOL false', 'PBOOL false', 'PINT 0'),
                    ('NExprConstFetch (NName (BYTES "bnVsbA==") METADATA) METADATA', 'PNULL', 'PNULL', 'PINT 0'),
                    ('NScalarFloat (FLOAT "3ff0000000000000") METADATA', 'PFLOAT 4607182418800017408', 'PFLOAT 4607182418800017408', 'PINT 1'),
                    ('NScalarString (BYTES "MQ==") ((Mkind 1) :: METADATA)', 'PSTRING ($ptascii("1"))', 'PSTRING_CARRIER INTERNED_STRING ($ptascii("1"))', 'PINT 1')]:
                metadata = 'metadata_bit_' + side
                child = constructor.replace('METADATA', metadata)
                children = [(leaf(3, 'left'), 'PINT 3'), (leaf(3, 'right'), 'PINT 3')]
                children[side == 'right'] = (child, raw)
                extras = []
                if constructor.startswith('NExprConstFetch'):
                    name_node = child[len('NExprConstFetch ('):-len(') ' + metadata)]
                    extras = [('(pcpath_bit_' + side + ' ++ [PCFIELD 0])', name_node)]
                state, expr, function = pair('NExprBinaryOpBitwiseAnd', *children, expected, extras=extras)
                checks += [('a genuinely certified non-INT ' + side + ' child refuses despite a coercively correct own INT fact',
                            value(state, child, 'porigin_bit_' + side, function) + ' = (' + typed + r') /\ ' +
                            value(state, expr, function=function) + ' = eps')]
        for left_folded, right_folded in [(True, True), (False, True), (True, False), (False, False)]:
            rows, codes, facts, operands = [], [], [], []
            for side, i, folded in [('left', 6, left_folded), ('right', 1, right_folded)]:
                child = leaf(i, side)
                child_path = 'pcpath_bit_' + side
                if not folded:
                    rows += [('(' + child_path + ' ++ [PCFIELD 0])', child)]
                    codes += [('(' + child_path + ' ++ [PCFIELD 0])', 'z_binary', 'true')]
                    facts += [('(' + child_path + ' ++ [PCFIELD 0])', 'PINT ' + str(i))]
                    child = 'NExprCastInt (' + child + ') ((Mkind 1) :: metadata_bit_' + side + ')'
                rows += [(child_path, child)]
                codes += [(child_path, 'z_binary', 'true' if folded else 'false')]
                facts += [(child_path, 'PINT ' + str(i))]
                operands += [child]
            expr = 'NExprBinaryOpBitwiseAnd (' + operands[0] + ') (' + operands[1] + ') metadata_binary'
            folded = left_folded and right_folded
            rows += [('pcpath_binary', expr)]
            codes += [('pcpath_binary', 'z_binary', 'true' if folded else 'false')]
            state, function = scaffold.changed(rows, codes, facts + [('pcpath_binary', 'PINT 0')])
            checks += [('source0 parent folding is the conjunction of two independently genuine child flags',
                        value(state, expr, function=function) + r' = (PINT 0) /\ $compiled_read(' + state +
                        ', porigin_binary) = ' + ('(PINT 0)' if folded else 'eps'))]
            wrong = function + '[.CODE.EXPRESSIONS = (CODEEXPR pcpath_binary z_binary ' + ('false' if folded else 'true') + ') :: ' + function + '.CODE.EXPRESSIONS]'
            checks += [('changing only the parent flag refuses each genuine child-flag combination',
                        value(state, expr, function=wrong) + ' = eps')]
        left, right = leaf(6, 'left'), 'NScalarInt (INTEGER 1) ([(MstartLine $(z_binary + 1))])'
        state, expr, function = pair('NExprBinaryOpBitwiseAnd', (left, 'PINT 6'), (right, 'PINT 1'), 'PINT 0')
        checks += [('genuine child CODE and own RHS-line facts do not erase the explicit differing-line bound',
                    value(state, left, 'porigin_bit_left', function) + r' = (PINT 6) /\ ' +
                    value(state, right, 'porigin_bit_right', function) + r' = (PINT 1) /\ ' +
                    '$expression_line(' + expr + r') = z_binary /\ ' + value(state, expr, function=function) + ' = eps')]
        left, middle, right = leaf(6, 'left'), leaf(1, 'right'), leaf(1, 'right')
        child = 'NExprBinaryOpBitwiseXor (' + middle + ') (' + right + ') metadata_bit_right'
        expr = 'NExprBinaryOpBitwiseOr (' + left + ') (' + child + ') metadata_binary'
        rows = [('pcpath_binary', expr), ('pcpath_bit_left', left), ('pcpath_bit_right', child),
                ('(pcpath_bit_right ++ [PCFIELD 0])', middle), ('(pcpath_bit_right ++ [PCFIELD 1])', right)]
        codes = [(row[0], 'z_binary', 'true') for row in rows]
        facts = [(rows[index][0], typed) for index, typed in enumerate(['PINT 6', 'PINT 6', 'PINT 0', 'PINT 1', 'PINT 1'])]
        state, function = scaffold.changed(rows, codes, facts)
        incomplete, incomplete_function = scaffold.changed(rows[:-1], codes, facts)
        checks += [('same-line recursive RHS bitwise certificates retain both proper grandchildren',
                    value(state, child, 'porigin_bit_right', function) + r' = (PINT 0) /\ ' +
                    value(state, expr, function=function) + ' = (PINT 6)'),
                   ('complete own folded facts cannot replace a missing proper RHS grandchild',
                    '$origin_node(' + incomplete + r'.SOURCES, PORIGIN n_cast_handler (pcpath_bit_right ++ [PCFIELD 1])) = eps /\ ' +
                    '$origin_node(' + incomplete + '.SOURCES, porigin_binary) = (' + expr + r') /\ ' +
                    value(incomplete, expr, function=incomplete_function) + ' = eps')]
        for kind, typed in [('Mod', 'PINT 0'), ('ShiftLeft', 'PINT 2'), ('Pow', 'PINT 1')]:
            state, expr, function = pair('NExprBinaryOp' + kind, (leaf(1, 'left'), 'PINT 1'),
                                         (leaf(1, 'right'), 'PINT 1'), typed)
            checks += [('the integer ' + kind + ' operation cannot enter the three-operation certificate',
                        value(state, expr, function=function) + ' = eps')]
    bare = 'NStmtReturn (' + expression + ') metadata_cast_return'
    single = nodes['cast_1'][0] + ' (' + expression + ') metadata_cast_1'
    statement = 'NStmtReturn (' + single + ') metadata_cast_return'
    checks += [('the helper preserves bare and single-cast binary handler fences',
                '~' + control.tail(control.source_state([('pcpath_cast_return', bare)]), statement=bare) + r' /\ ~' +
                control.tail(control.source_state([('pcpath_cast_return', statement), ('pcpath_cast', single)]), statement=statement))]
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = current.lifecycle(name, fixture, path)
    checks += [('the exact binary subtree and handler result survive real formal/native-cell retirement',
                'S_handler.RESULT = KNOWN (' + current.root_value(name) + r') /\ S.RESULT = KNOWN PNULL /\ ' +
                value('S', current.expression(name, 'binary')) + ' = (' + current.nodes(name)['binary'][3] + ')')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
