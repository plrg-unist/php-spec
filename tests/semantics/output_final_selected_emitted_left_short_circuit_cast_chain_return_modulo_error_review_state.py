#!/usr/bin/env python3
"""Independent emitted-left pruning, compiler authority and retirement checks."""
import output_final_selected_constant_float_cast_return_modulo_error_review_state as control
import output_final_selected_recursive_numeric_sign_cast_chain_return_modulo_error_review_state as scaffold
import output_final_selected_quiet_short_circuit_cast_chain_return_modulo_error_review_state as samples
import output_final_selected_emitted_left_short_circuit_cast_chain_return_modulo_error_state as current

runner, CASES, CONJ = current.runner, current.CASES, current.CONJ
PREFIX = current.PREFIX + scaffold.PREFIX[len(scaffold.current.PREFIX):] + r'''
dec $or154_code_at(pcodeexpr, pcpath) : bool
def $or154_code_at(CODEEXPR pcpath z b, pcpath) = true
def $or154_code_at(pcodeexpr, pcpath) = false -- otherwise
dec $or154_code_drop(pcodeexpr*, pcpath) : pcodeexpr*
def $or154_code_drop(eps, pcpath) = eps
def $or154_code_drop(pcodeexpr :: pcodeexpr_tail*, pcpath) = $or154_code_drop(pcodeexpr_tail*, pcpath)
  -- if $or154_code_at(pcodeexpr, pcpath)
def $or154_code_drop(pcodeexpr :: pcodeexpr_tail*, pcpath) = pcodeexpr :: $or154_code_drop(pcodeexpr_tail*, pcpath)
  -- if ~$or154_code_at(pcodeexpr, pcpath)
'''


def value(state, expression, origin='porigin_value', function='pfunction_handler'):
    return scaffold.value(state, expression, origin, function)


def skipped(state, expression, function='pfunction_handler'):
    return '$ob_object_cast_chain_skipped_line(' + state + ', ' + function + ', porigin_value_right, ' + expression + ')'


def short(kind, left, right, left_kind='NExprCastBool'):
    rows, codes, facts, expressions, values = [], [], [], [], []
    for side, (template, typed, pooled) in [('left_child', left), ('right', right)]:
        path, line = 'pcpath_value_' + side, 'z_value_' + side
        expression = template.replace('{metadata}', '([(MstartLine ' + line + ')])')
        rows += [(path, expression)]
        if expression.startswith('NExprConstFetch '):
            rows += [('(' + path + ' ++ [PCFIELD 0])',
                      expression[len('NExprConstFetch ('):].removesuffix(') ([(MstartLine ' + line + ')])'))]
        codes += [(path, line, 'true')]
        facts += [(path, pooled)]
        expressions += [expression]
        values += [typed]
    left = left_kind + ' (' + expressions[0] + ') ([(MstartLine z_value_left), (Mkind 1)])'
    if left_kind == 'NExprCastDouble':
        left = left.replace('(Mkind 1)', '(Mkind 2)')
    expression = kind + ' (' + left + ') (' + expressions[1] + ') metadata_value'
    state, function = scaffold.changed([('pcpath_value', expression), ('pcpath_value_left', left), *rows],
        [('pcpath_value', 'z_value_right', 'false'), ('pcpath_value_left', 'z_value_left_child', 'false'), *codes], facts)
    return state, expression, function, left, expressions[1], values


def frontier(name, fixture, path):
    bindings, checks = current.frontier(name, fixture, path)
    bindings += ['$source_unit(S.SOURCES, n_cast_handler) = (pcunit_handler)',
                 '$pool_at(S.POOLS, n_cast_handler) = (ppool_handler)']
    nodes = current.nodes(name)
    expression, result = current.expression(name, 'value'), nodes['value'][3]
    checks += [('the emitted parent has its exact nonowning Boolean result',
                value('S', expression) + ' = (' + result + r') /\ $value_nodes(' + result + ') = eps'),
               ('a preset Boolean cannot replace NORMAL source authority',
                value('S[.COMPLETION = BUDGET][.RESULT = KNOWN (' + result + ')]', expression) + ' = eps'),
               ('the selected handler retains its own CODE unit and BODY',
                '~' + control.tail(function='pfunction_handler[.CODE.UNIT = $(n_cast_handler + 1)]') + CONJ +
                '~' + control.tail(function='pfunction_handler[.BODY = pfunction_handler.BODY ++ [PCINDEX 0]]'))]
    for key, node in nodes.items():
        source = ('S[.SOURCES = pcunit_handler[.OCCURRENCES = '
                  '$or131_drop(pcunit_handler.OCCURRENCES, pcpath_' + key + ')] :: S.SOURCES]')
        checks += [(key + ' retains its proper SOURCE even if skipped', '~' + control.tail(source))]
        flag = 'true' if node[4] else 'false'
        for label, line, forged in [('line', '$(z_' + key + ' + 1)', flag),
                                    ('flag', 'z_' + key, 'false' if node[4] else 'true')]:
            checks += [(key + ' retains its exact compiler ' + label,
                        '~' + control.tail(function=control.code_function('pcpath_' + key, line, forged)))]
        if node[4]:
            state = ('S[.POOLS = ppool_handler[.CONSTANTS = '
                     '$or131_fact_drop(ppool_handler.CONSTANTS, pcpath_' + key + ')] :: S.POOLS]')
            checks += [(key + ' retains its own folded fact', '~' + control.tail(state)),
                       (key + ' cannot borrow an owning fact',
                        '~' + control.tail(control.pool_state('pcpath_' + key, 'POBJECT 0')))]
    for key in ['value', 'value_left', 'value_right']:
        code = ('pfunction_handler.CODE[.EXPRESSIONS = (CODEEFFECT pcpath_' + key +
                ') :: pfunction_handler.CODE.EXPRESSIONS]')
        state = 'S[.CODE = ' + code + ' :: S.CODE]'
        checks += [('a compiled effect at ' + key + ' cannot enter the quiet parent',
                    '$compiled_effects(' + state + ', porigin_value) =/= eps' + CONJ + value(state, expression) + ' = eps')]
    checks += [('an unread parent pool cannot replace emitted authority',
                value(control.pool_state('pcpath_value', 'POBJECT 0'), expression) + ' = (' + result + ')')]
    code = ('pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR pcpath_value z_value true) :: '
            'pfunction_handler.CODE.EXPRESSIONS]')
    state = control.pool_state('pcpath_value', result) + '[.CODE = ' + code + ' :: S.CODE]'
    checks += [('an exact forged global read cannot replace read-eps',
                '$compiled_read(' + state + ', porigin_value) = (' + result + ')' + CONJ + value(state, expression) + ' = eps')]
    for target in ['pcpath_value_left', 'pcpath_value_right']:
        for flag in ['false', 'true']:
            code = ('pfunction_handler.CODE[.REDIRECTS = (CODEREDIRECT pcpath_value ' + target + ' ' + flag +
                    ') :: pfunction_handler.CODE.REDIRECTS]')
            checks += [('an emitted LEFT cannot borrow any parent redirect',
                        value('S[.CODE = ' + code + ' :: S.CODE]', expression) + ' = eps')]
    bare = 'NStmtReturn (' + expression + ') metadata_cast_return'
    single = 'NExprCastInt (' + expression + ') metadata_cast_1'
    statement = 'NStmtReturn (' + single + ') metadata_cast_return'
    checks += [('a helper Boolean cannot bypass the existing two-cast handler gate',
                '~' + control.tail(control.source_state([('pcpath_cast_return', bare)]), statement=bare) + CONJ +
                '~' + control.tail(control.source_state([('pcpath_cast_return', statement), ('pcpath_cast', single)]), statement=statement))]
    if current.DETAILS[name][1] == 'and-skip':
        right = current.expression(name, 'value_right')
        source = ('S[.SOURCES = pcunit_handler[.OCCURRENCES = '
                  '$or131_drop(pcunit_handler.OCCURRENCES, pcpath_value_right ++ [PCFIELD 0])] :: S.SOURCES]')
        checks += [('the skipped unresolved name has its own indexed source',
                    skipped(source, right) + ' = eps' + CONJ + '~' + control.tail(source)),
                   ('a compiled undefined RHS has a line without a demanded value',
                    skipped('S', right) + ' = (z_value_right)' + CONJ + value('S', right, 'porigin_value_right') + ' = eps')]
        function = 'pfunction_handler[.CODE.EXPRESSIONS = $or154_code_drop(pfunction_handler.CODE.EXPRESSIONS, pcpath_value_right)]'
        checks += [('a runtime-skipped RHS must still retain its compiled descriptor',
                    '~' + control.tail(function=function))]
        for kind in ['NNameFullyQualified', 'NNameRelative']:
            changed = right.replace('NName ', kind + ' ', 1)
            state = control.source_state([('pcpath_value_right', changed)])
            checks += [('a skipped raw ' + kind + ' cannot borrow plain-name line authority',
                        skipped(state, changed) + ' = eps')]
        poisoned = control.pool_state('pcpath_value_right', 'POBJECT 0')
        checks += [('an unread skipped pool remains undemanded',
                    '$compiled_read(' + poisoned + ', porigin_value_right) = eps' + CONJ + value(poisoned, expression) + ' = (' + result + ')')]
        for kind, b_or in [('NExprBinaryOpBooleanAnd', False), ('NExprBinaryOpLogicalAnd', False),
                           ('NExprBinaryOpBooleanOr', True), ('NExprBinaryOpLogicalOr', True)]:
            for skip in [True, False]:
                left_truth = b_or if skip else not b_or
                for right_value in [samples.keyword('false'), samples.keyword('true'), samples.keyword('null'),
                                    samples.string(''), samples.string('0'), samples.string('00'),
                                    samples.floating('8000000000000000'), samples.floating('7ff0000000000000')]:
                    truth = right_value[1] not in ['PBOOL false', 'PNULL',
                        'PSTRING_CARRIER INTERNED_STRING ($ptascii(""))',
                        'PSTRING_CARRIER INTERNED_STRING ($ptascii("0"))', 'PFLOAT 9223372036854775808']
                    result_value = 'PBOOL ' + str(b_or if skip else truth).lower()
                    state, expr, function, left, right, _ = short(kind,
                        samples.keyword(str(left_truth).lower()), right_value)
                    checks += [('source0 all four emitted-left shapes retain skipped/selected scalar truth',
                                value(state, left, 'porigin_value_left', function) + ' = (PBOOL ' +
                                str(left_truth).lower() + ')' + CONJ + value(state, expr, function=function) + ' = (' + result_value + ')')]
        for left_truth in ['false', 'true']:
            state, expr, function, _, _, _ = short('NExprBinaryOpBooleanAnd',
                samples.keyword(left_truth), samples.keyword('false'))
            state, expr, function = [part.replace('z_value_right', '$(z_value_right + 3)')
                                     for part in [state, expr, function]]
            wrong = function + '[.CODE.EXPRESSIONS = (CODEEXPR pcpath_value z_value_left_child false) :: ' + function + '.CODE.EXPRESSIONS]'
            checks += [('source0 skipped and selected multiline RHS retain the terminal compiler line',
                        value(state, expr, function=function) + ' = (PBOOL false)' + CONJ +
                        value(state, expr, function=wrong) + ' = eps')]
        for bits in ['7ff8000000000001', '7ff0000000000001']:
            nan = samples.floating(bits)
            for left_nan in [False, True]:
                state, expr, function, left, right, _ = short('NExprBinaryOpBooleanAnd',
                    nan if left_nan else samples.keyword('true'), samples.keyword('true') if left_nan else nan,
                    'NExprCastDouble' if left_nan else 'NExprCastBool')
                masked = 'S_masked_' + str(len(bindings))
                bindings += [masked + ' = ' + state + '[.REPORTING = 0][.ERRORHANDLER = {CALLBACK eps, LEVELS 0}]'
                             '[.SOURCEPENDING = eps][.ERRORFATALTRACE = eps]']
                demanded, origin = (left, 'porigin_value_left') if left_nan else (right, 'porigin_value_right')
                checks += [('source0 demanded NaN truth is intrinsically refused despite hidden diagnostics',
                    value(masked, demanded, origin, function) + ' = (' + nan[1] + ')' + CONJ +
                    '~$ob_object_cast_chain_quiet(CASTBOOL, ' + nan[1] + ')' + CONJ +
                    '$boolean_result(' + masked + '[.RESULT = KNOWN (' + nan[1] + ')], false, z_value_right) = ' +
                    masked + '[.RESULT = KNOWN (PBOOL true)]' + CONJ + value(masked, expr, function=function) + ' = eps')]
            state, expr, function, _, right, _ = short('NExprBinaryOpBooleanAnd', samples.keyword('false'), nan)
            checks += [('source0 a compiled skipped NaN authenticates its line without demanding truth',
                        skipped(state, right, function) + ' = (z_value_right)' + CONJ +
                        value(state, expr, function=function) + ' = (PBOOL false)')]
        for owned in ['POBJECT 0', 'PARRAY 0', 'PSTRING_CARRIER (REQUEST_STRING 0) ([48])']:
            checks += [('owning and request-string truth cannot borrow primitive certification',
                        '~$ob_object_cast_chain_quiet(CASTBOOL, ' + owned + ')')]
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = current.lifecycle(name, fixture, path)
    checks += [('the exact nested return survives actual formal and native-cell retirement',
                'S_handler.RESULT = KNOWN (' + current.root_value(name) + r') /\ S.RESULT = KNOWN PNULL /\ ' +
                value('S', current.expression(name), 'porigin_cast') + ' = (' + current.root_value(name) + ')')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
