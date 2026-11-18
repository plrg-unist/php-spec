#!/usr/bin/env python3
"""Independent quiet float NOT, exact pool, rounding and retirement checks."""
import output_final_selected_constant_float_cast_return_modulo_error_review_state as control
import output_final_selected_recursive_numeric_sign_cast_chain_return_modulo_error_review_state as scaffold
import output_final_selected_integer_bitnot_cast_chain_return_modulo_error_review_state as old
import output_final_selected_integral_float_bitnot_cast_chain_return_modulo_error_state as current

runner, CONJ, value = current.runner, current.CONJ, scaffold.value
PREFIX = current.PREFIX + scaffold.PREFIX[len(scaffold.current.PREFIX):]
CASES = {name: current.sources.CASES['native-selected-integral-float-bitnot-cast-chain-return-modulo-error-' + name]
         for name in ['warning-right-cv-pair-emitted-one', 'warning-left-constant-folded-min']}


def bitnot(bits, result, emitted=False):
    raw = 'PFLOAT ' + str(int(bits, 16))
    slot = 'child_4' if emitted else 'child_3'
    leaf = 'NScalarFloat (FLOAT "' + bits + '") metadata_' + slot
    child = 'NExprCastDouble (' + leaf + ') ((Mkind 2) :: metadata_child_3)' if emitted else leaf
    expression = 'NExprBitwiseNot (' + child + ') metadata_sign'
    line = '$source_line(metadata_' + slot + ')'
    rows = [('pcpath_sign', expression), ('pcpath_child_3', child)]
    codes = [('pcpath_sign', line, str(not emitted).lower()), ('pcpath_child_3', line, str(not emitted).lower())]
    facts = [('pcpath_' + slot, raw)]
    if emitted:
        rows += [('pcpath_child_4', leaf)]
        codes += [('pcpath_child_4', line, 'true')]
    else:
        facts += [('pcpath_sign', result)]
    state, function = scaffold.changed(rows, codes, facts)
    return state, expression, function, child, raw


def frontier(name, fixture, path):
    bindings, checks = current.frontier(name, fixture, path)
    bindings += ['$source_unit(S.SOURCES, n_cast_handler) = (pcunit_handler)',
                 '$pool_at(S.POOLS, n_cast_handler) = (ppool_handler)']
    expression, result = current.expression(name, 2), current.nodes(name)[2][3]
    checks += [('the actual float complement retains a nonowning signed64 INT tag',
                value('S', expression) + ' = (' + result + ')' + CONJ + '$value_nodes(' + result + ') = eps'),
               ('NORMAL and the real handler CODE unit/body remain required',
                value('S[.COMPLETION = BUDGET][.RESULT = KNOWN (' + result + ')]', expression) + ' = eps' + CONJ +
                '~' + control.tail(function='pfunction_handler[.CODE.UNIT = $(n_cast_handler + 1)]') + CONJ +
                '~' + control.tail(function='pfunction_handler[.BODY = pfunction_handler.BODY ++ [PCINDEX 0]]'))]
    for index, (_, _, _, _, folded) in enumerate(current.nodes(name)):
        slot = current.slot(index)
        state = ('S[.SOURCES = pcunit_handler[.OCCURRENCES = '
                 '$or131_drop(pcunit_handler.OCCURRENCES, pcpath_' + slot + ')] :: S.SOURCES]')
        checks += [(slot + ' retains its own SOURCE through the whole tail', '~' + control.tail(state))]
        for label, line, flag in [('line', '$(z_' + slot + ' + 1)', str(folded).lower()),
                                  ('flag', 'z_' + slot, str(not folded).lower())]:
            checks += [(slot + ' retains the compiler ' + label,
                        '~' + control.tail(function=control.code_function('pcpath_' + slot, line, flag)))]
        if folded:
            state = ('S[.POOLS = ppool_handler[.CONSTANTS = '
                     '$or131_fact_drop(ppool_handler.CONSTANTS, pcpath_' + slot + ')] :: S.POOLS]')
            checks += [(slot + ' requires its own exact nonowning pool fact',
                        '~' + control.tail(state) + CONJ + '~' + control.tail(control.pool_state('pcpath_' + slot, 'POBJECT 0')))]
    if current.nodes(name)[2][4]:
        code = 'pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR pcpath_sign z_sign false) :: pfunction_handler.CODE.EXPRESSIONS]'
        checks += [('folded complement authority needs both its own value and global CODEtrue',
                    value(control.pool_state('pcpath_sign', 'PINT 0'), expression) + ' = eps' + CONJ +
                    value('S[.CODE = ' + code + ' :: S.CODE]', expression) + ' = eps')]
    else:
        code = 'pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR pcpath_sign z_sign true) :: pfunction_handler.CODE.EXPRESSIONS]'
        state = control.pool_state('pcpath_sign', result) + '[.CODE = ' + code + ' :: S.CODE]'
        checks += [('emitted complements ignore unread pools and reject exact forged global reads',
                    value(control.pool_state('pcpath_sign', 'POBJECT 0'), expression) + ' = (' + result + ')' + CONJ +
                    '$compiled_read(' + state + ', porigin_sign) = (' + result + ')' + CONJ + value(state, expression) + ' = eps')]
    for slot in ['sign', 'child_3']:
        code = 'pfunction_handler.CODE[.EXPRESSIONS = (CODEEFFECT pcpath_' + slot + ') :: pfunction_handler.CODE.EXPRESSIONS]'
        checks += [('compiled effects at ' + slot + ' cannot disappear through the two return casts',
                    '~' + control.tail('S[.CODE = ' + code + ' :: S.CODE][.REPORTING = 0]'))]
    bare = 'NStmtReturn (' + expression + ') metadata_cast_return'
    single = 'NExprCastInt (' + expression + ') metadata_cast_1'
    statement = 'NStmtReturn (' + single + ') metadata_cast_return'
    checks += [('quiet FLOAT NOT retains the existing two-cast handler boundary',
                '~' + control.tail(control.source_state([('pcpath_cast_return', bare)]), statement=bare) + CONJ +
                '~' + control.tail(control.source_state([('pcpath_cast_return', statement), ('pcpath_cast', single)]), statement=statement))]
    if name.endswith('folded-min'):
        wrong = 'PINT 9223372036854775806'
        checks += [('identical final FLOAT bits cannot replace the exact raw INT_MAX complement',
                    '$cast_apply(S[.RESULT = KNOWN (' + wrong + ')], CASTFLOAT, ' + wrong + ', z_sign) = S[.RESULT = KNOWN (' + current.root_value(name) + ')]' + CONJ +
                    value(control.pool_state('pcpath_sign', wrong), expression) + ' = eps')]
    if name.endswith('emitted-one'):
        exact = [('0000000000000000', 0), ('8000000000000000', 0),
                 ('3ff0000000000000', 1), ('bff0000000000000', -1),
                 ('4340000000000000', 9007199254740992),
                 ('c3e0000000000000', -9223372036854775808),
                 ('43dfffffffffffff', 9223372036854774784)]
        for bits, integer in exact:
            complement = 'PINT ' + current.integer(-integer - 1)
            for emitted in [False, True]:
                state, expr, function, child, raw = bitnot(bits, complement, emitted)
                checks += [('source0 exact integral FLOATs preserve raw signed complement across folded and emitted children',
                            '$float_long(' + raw[7:] + ', true) = (' + current.integer(integer) + ', eps)' + CONJ +
                            value(state, child, 'porigin_child_3', function) + ' = (' + raw + ')' + CONJ +
                            value(state, expr, function=function) + ' = (' + complement + ')')]
        for bits in ['3ff8000000000000', 'bff8000000000000', '0000000000000001',
                     '7ff0000000000000', 'fff0000000000000',
                     '7ff8000000000001', '7ff0000000000001',
                     '43e0000000000000', 'c3e0000000000001']:
            for emitted in [False, True]:
                state, expr, function, child, raw = bitnot(bits, 'PINT 0', emitted)
                masked = state + '[.REPORTING = 0][.ERRORHANDLER = {CALLBACK eps, LEVELS 0}][.SOURCEPENDING = eps][.ERRORFATALTRACE = eps]'
                checks += [('source0 fractional, subnormal, nonfinite and out-of-range FLOATs remain refused under masks',
                            value(masked, child, 'porigin_child_3', function) + ' = (' + raw + ')' + CONJ +
                            value(masked, expr, function=function) + ' = eps')]
        state, expr, function, _, raw = bitnot('8000000000000000', 'PINT $(-1)')
        changed = state.replace('[.CONSTANTS = [', '[.CONSTANTS = [PCONSTANT pcpath_child_3 (PFLOAT 0), ', 1)
        checks += [('source0 signed-zero input authority survives equal complement results',
                    '$bitnot_apply(S[.RESULT = KNOWN (' + raw + ')], ' + raw + ', z_sign) = S[.RESULT = KNOWN (PINT $(-1))]' + CONJ +
                    '$bitnot_apply(S[.RESULT = KNOWN (PFLOAT 0)], PFLOAT 0, z_sign) = S[.RESULT = KNOWN (PINT $(-1))]' + CONJ +
                    value(changed, expr, function=function) + ' = eps')]
        leaf = 'NScalarInt (INTEGER 1) metadata_child_3'
        state, expr, function = old.raw_not(leaf, 'PINT 1', 'PINT $(-2)')
        checks += [('source0 the original integer complement rule remains exact', value(state, expr, function=function) + ' = (PINT $(-2))')]
        leaf = 'NScalarString (BYTES "MA==") metadata_child_3'
        state, expr, function = old.raw_not(leaf, 'PSTRING ([48])', 'PINT $(-1)')
        checks += [('source0 a numeric STRING cannot borrow the new FLOAT-to-INT result', value(state, expr, function=function) + ' = eps')]
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = current.lifecycle(name, fixture, path)
    checks += [('real formal/native-cell retirement preserves the raw INT and separately rounded return FLOAT',
                'S_handler.RESULT = KNOWN (' + current.root_value(name) + ')' + CONJ + 'S.RESULT = KNOWN PNULL' + CONJ +
                value('S', current.expression(name, 2)) + ' = (' + current.nodes(name)[2][3] + ')')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
