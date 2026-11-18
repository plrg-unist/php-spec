#!/usr/bin/env python3
"""Independent quiet-coercion, compiler authority and retirement controls."""
import base64
import output_final_selected_primitive_unary_sign_cast_chain_return_modulo_error_state as current
import output_final_selected_primitive_unary_sign_cast_chain_return_modulo_error_sources as sources

legacy = current.legacy_recursive
control, value = legacy.control, legacy.value
runner, PREFIX, CONJ = current.runner, current.PREFIX, current.CONJ
CASES = {name: sources.CASES['native-selected-primitive-unary-sign-cast-chain-return-modulo-error-' + name]
         for name in ['warning-deprecated-constant-float-minus-null',
                      'warning-left-constant-fraction-string', 'deprecated-both-cv-pair-exponent-zero']}


def string_query(data, result):
    payload = base64.b64encode(data).decode()
    leaf = 'NScalarString (BYTES "' + payload + '") metadata_child_3'
    raw = 'PSTRING ([' + ','.join(str(n) for n in data) + '])'
    return (*legacy.raw_sign('NExprUnaryPlus', leaf, raw, result), leaf, raw)


def frontier(name, fixture, path):
    bindings, checks = current.frontier(name, fixture, path)
    bindings += ['$source_unit(S.SOURCES, n_cast_handler) = (pcunit_handler)',
                 '$pool_at(S.POOLS, n_cast_handler) = (ppool_handler)',
                 'pcpath_child_4 = pcpath_child_3 ++ [PCFIELD 0]',
                 'metadata_child_4 = metadata_child_3']
    expression, result = current.expression(name, 2), current.nodes(name)[2][3]
    child = current.nodes(name)[3][3]
    checks += [('the actual quiet coercion retains exact child and numeric result tags',
                value('S', expression) + ' = (' + result + ')' + CONJ +
                '$value_nodes(' + child + ') = eps' + CONJ + '$value_nodes(' + result + ') = eps'),
               ('preset results cannot bypass NORMAL or the selected handler UNIT and BODY',
                value('S[.COMPLETION = BUDGET][.RESULT = KNOWN (' + result + ')]', expression) + ' = eps' + CONJ +
                '~' + control.tail(function='pfunction_handler[.CODE.UNIT = $(n_cast_handler + 1)]') + CONJ +
                '~' + control.tail(function='pfunction_handler[.BODY = pfunction_handler.BODY ++ [PCINDEX 0]]'))]
    for index, (_, _, _, _, folded) in enumerate(current.nodes(name)):
        slot = current.slot(index)
        flag = 'true' if folded else 'false'
        for label, line, changed_flag in [('flag', 'z_' + slot, 'false' if folded else 'true'),
                                          ('line', '$(z_' + slot + ' + 1)', flag)]:
            checks += [(slot + ' retains its exact CODE ' + label,
                        '~' + control.tail(function=control.code_function('pcpath_' + slot, line, changed_flag)))]
        missing = ('S[.SOURCES = pcunit_handler[.OCCURRENCES = '
                   '$or131_drop(pcunit_handler.OCCURRENCES, pcpath_' + slot + ')] :: S.SOURCES]')
        checks += [('every proper source occurrence remains necessary: ' + slot, '~' + control.tail(missing))]
        if folded:
            missing = ('S[.POOLS = ppool_handler[.CONSTANTS = '
                       '$or131_fact_drop(ppool_handler.CONSTANTS, pcpath_' + slot + ')] :: S.POOLS]')
            checks += [(slot + ' needs its own typed folded pool',
                        '~' + control.tail(missing) + CONJ +
                        '~' + control.tail(control.pool_state('pcpath_' + slot, 'POBJECT 0')))]
    wrong = 'PINT 0' if result.startswith('PFLOAT') else 'PFLOAT 0'
    checks += [('a wrong scalar tag cannot replace the typed sign pool',
                value(control.pool_state('pcpath_sign', wrong), expression) + ' = eps')]
    global_code = ('pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR pcpath_sign z_sign false) :: '
                   'pfunction_handler.CODE.EXPRESSIONS]')
    checks += [('folded sign facts cannot replace the authentic global CODE flag',
                value('S[.CODE = ' + global_code + ' :: S.CODE]', expression) + ' = eps')]
    if current.DETAILS[name][1] == 'minus-null':
        for data in [b'12tail', b'12\0', b'', b'twelve']:
            state, expr, function, leaf, raw = string_query(data, 'PINT 12')
            masked = state + '[.REPORTING = 0][.ERRORHANDLER = {CALLBACK eps, LEVELS 0}][.ERRORFATALTRACE = eps]'
            expected = 'COERCED (NINT 12) true' if data.startswith(b'12') else 'BADNUMBER'
            checks += [('intrinsic nonquiet or failed string coercion stays refused under masks: ' + repr(data),
                        '$coerce_number(' + raw + ') = ' + expected + CONJ +
                        value(masked, expr, function=function) + ' = eps')]
            if data == b'12tail':
                checks += [('the leading-number refusal has a genuine independently certified STRING child',
                            value(masked, leaf, 'porigin_child_3', function) +
                            ' = (PSTRING_CARRIER INTERNED_STRING ([49,50,116,97,105,108]))')]
        state, expr, function, _, raw = string_query(b' \t12\n', 'PINT 12')
        checks += [('full numeric whitespace remains quiet without borrowing a Boolean tag',
                    '$coerce_number(' + raw + ') = COERCED (NINT 12) false' + CONJ +
                    value(state, expr, function=function) + ' = (PINT 12)')]
        leaf = 'NScalarInt (INTEGER $(-9223372036854775808)) metadata_child_3'
        state, expr, function = legacy.raw_sign('NExprUnaryMinus', leaf,
            'PINT $(-9223372036854775808)', 'PFLOAT 4890909195324358656')
        checks += [('the primitive extension preserves the old numeric INT_MIN promotion fence',
                    value(state, leaf, 'porigin_child_3', function) + ' = (PINT $(-9223372036854775808))' + CONJ +
                    value(state, expr, function=function) + ' = eps')]
        leaf = 'NScalarFloat (FLOAT "7ff8abcdef012345") metadata_child_3'
        state, expr, function = legacy.raw_sign('NExprUnaryPlus', leaf,
            'PFLOAT 9221309138007565125', 'PFLOAT 9221309138007565125')
        checks += [('a quiet NaN unary result remains outside the old numeric sign policy',
                    value(state, expr, function=function) + ' = eps')]
        raw = 'NScalarFloat (FLOAT "3ff0000000000000") metadata_child_4'
        boolean = 'NExprBooleanNot (' + raw + ') metadata_child_3'
        emitted = 'NExprUnaryMinus (' + boolean + ') metadata_sign'
        state, function = legacy.changed(
            [('pcpath_sign', emitted), ('pcpath_child_3', boolean), ('pcpath_child_4', raw)],
            [('pcpath_sign', '$expression_line(' + boolean + ')', 'false'),
             ('pcpath_child_3', '$expression_line(' + raw + ')', 'false'),
             ('pcpath_child_4', '$source_line(metadata_child_4)', 'true')],
            [('pcpath_child_4', 'PFLOAT 4607182418800017408')])
        bindings += ['S_emitted = ' + state, 'pfunction_emitted = ' + function]
        checks += [('a genuine emitted Boolean child supplies quiet type-changing numeric zero',
                    '$compiled_read(S_emitted, porigin_sign) = eps' + CONJ +
                    value('S_emitted', emitted, function='pfunction_emitted') + ' = (PINT 0)')]
        forged = ('S_emitted[.POOLS = ppool_handler[.CONSTANTS = (PCONSTANT pcpath_sign (PINT 0)) :: '
                  'ppool_handler.CONSTANTS] :: S_emitted.POOLS][.CODE = pfunction_emitted.CODE[.EXPRESSIONS = '
                  '(CODEEXPR pcpath_sign ($expression_line(' + boolean + ')) true) :: '
                  'pfunction_emitted.CODE.EXPRESSIONS] :: S_emitted.CODE]')
        checks += [('a forged global folded read cannot replace emitted sign authority',
                    '$compiled_read(' + forged + ', porigin_sign) = (PINT 0)' + CONJ +
                    value(forged, emitted, function='pfunction_emitted') + ' = eps')]
    bare = 'NStmtReturn (' + expression + ') metadata_cast_return'
    single = current.nodes(name)[1][0] + ' (' + expression + ') metadata_cast_1'
    statement = 'NStmtReturn (' + single + ') metadata_cast_return'
    checks += [('bare and single-cast handlers retain the two-cast admission fence',
                '~' + control.tail(control.source_state([('pcpath_cast_return', bare)]), statement=bare) + CONJ +
                '~' + control.tail(control.source_state([('pcpath_cast_return', statement), ('pcpath_cast', single)]),
                                  statement=statement))]
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = current.lifecycle(name, fixture, path)
    result = current.root_value(name)
    checks += [('the exact scalar return survives real retirement before the MOD Error',
                'S_handler.RESULT = KNOWN (' + result + ')' + CONJ + 'S.RESULT = KNOWN PNULL' + CONJ +
                value('S', current.expression(name, 2)) + ' = (' + current.nodes(name)[2][3] + ')')]
    if current.default(name):
        checks += [('strict FALSE remains distinct from integer and FLOAT zero after retirement',
                    'S_handler.RESULT = KNOWN (PBOOL false)' + CONJ +
                    'S_handler.RESULT =/= KNOWN (PINT 0)' + CONJ + 'S_handler.RESULT =/= KNOWN (PFLOAT 0)')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
