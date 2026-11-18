#!/usr/bin/env python3
"""Independent shorthand raw-tag, absent-TRUE, fallback-copy and retirement checks."""
import output_final_selected_constant_float_cast_return_modulo_error_review_state as control
import output_final_selected_recursive_numeric_sign_cast_chain_return_modulo_error_review_state as scaffold
import output_final_selected_quiet_short_circuit_cast_chain_return_modulo_error_review_state as samples
import output_final_selected_emitted_condition_full_ternary_cast_chain_return_modulo_error_review_state as full
import output_final_selected_emitted_condition_shorthand_ternary_cast_chain_return_modulo_error_state as current

runner, CASES, CONJ = current.runner, current.CASES, current.CONJ
PREFIX = current.PREFIX + full.PREFIX[len(full.current.PREFIX):]


def value(state, expression, origin='porigin_value', function='pfunction_handler'):
    return scaffold.value(state, expression, origin, function)


def integer(number):
    typed = 'PINT ' + str(number)
    return 'NScalarInt (INTEGER ' + str(number) + ') {metadata}', typed, typed


def cast(kind, child, result):
    return {'cast': kind, 'child': child, 'result': result}


def shorthand(truth, condition, fallback):
    return {'truth': truth, 'condition': condition, 'fallback': fallback}


def graph(node):
    rows, codes, facts = [], [], []

    def child(path, field):
        return '(' + path + ' ++ [PCFIELD ' + str(field) + '])'

    def build(node, path):
        line = '$(z_value_false + ' + str(len(rows) + 11) + ')'
        metadata = '([(MstartLine ' + line + ')])'
        if not isinstance(node, dict):
            template, typed, pooled = node
            expression = template.replace('{metadata}', metadata)
            if expression.startswith('NExprConstFetch '):
                rows.append((child(path, 0), expression[len('NExprConstFetch ('):].removesuffix(') ' + metadata)))
            folded = typed is not None
        elif 'cast' in node:
            expression_child, _, line = build(node['child'], child(path, 0))
            kind = node['cast']
            style = '2' if kind == 'NExprCastDouble' else '1'
            metadata = metadata[:-2] + ', (Mkind ' + style + ')])'
            expression = kind + ' (' + expression_child + ') ' + metadata
            typed, pooled, folded = node['result'], None, False
        elif 'selected' in node:
            condition = cast('NExprCastBool', integer(int(node['selected'])),
                             'PBOOL ' + str(node['selected']).lower())
            expr_cond, _, _ = build(condition, child(path, 0))
            expr_true, true_value, _ = build(node['yes'], child(path, 1))
            expr_false, false_value, line = build(node['no'], child(path, 2))
            expression = 'NExprTernary (' + expr_cond + ') (' + expr_true + ') (' + expr_false + ') ' + metadata
            typed, pooled, folded = true_value if node['selected'] else false_value, None, False
        else:
            expr_cond, cond_value, _ = build(node['condition'], child(path, 0))
            expr_false, false_value, line = build(node['fallback'], child(path, 2))
            expression = 'NExprTernary (' + expr_cond + ') ABSENT (' + expr_false + ') ' + metadata
            typed, pooled, folded = cond_value if node['truth'] else false_value, None, False
        rows.append((path, expression))
        codes.append((path, line, str(folded).lower()))
        if pooled is not None:
            facts.append((path, pooled))
        return expression, typed, line

    expression, result, terminal = build(node, 'pcpath_value')
    state, function = scaffold.changed(rows, codes, facts)
    return state, expression, function, result, terminal


def frontier(name, fixture, path):
    bindings, checks = current.frontier(name, fixture, path)
    bindings += ['$source_unit(S.SOURCES, n_cast_handler) = (pcunit_handler)',
                 '$pool_at(S.POOLS, n_cast_handler) = (ppool_handler)']
    nodes = current.nodes(name)
    expression, result = current.expression(name, 'value'), nodes['value'][3]
    checks += [('the shorthand retains its raw selected tag and no owner',
                value('S', expression) + ' = (' + result + r') /\ $value_nodes(' + result + ') = eps'),
               ('a preset result cannot replace NORMAL source authority',
                value('S[.COMPLETION = BUDGET][.RESULT = KNOWN (' + result + ')]', expression) + ' = eps'),
               ('the handler retains its exact CODE unit and BODY',
                '~' + control.tail(function='pfunction_handler[.CODE.UNIT = $(n_cast_handler + 1)]') + CONJ +
                '~' + control.tail(function='pfunction_handler[.BODY = pfunction_handler.BODY ++ [PCINDEX 0]]'))]
    for key, node in nodes.items():
        if node[0] == 'absent':
            for forged in [current.expression(name, 'value_cond_child'), 'NScalarInt (INTEGER 1) metadata_value']:
                checks += [('the ABSENT TRUE field cannot borrow any SOURCE occurrence',
                            value(control.source_state([('pcpath_' + key, forged)]), expression) + ' = eps')]
            for flag in ['true', 'false']:
                checks += [('the ABSENT TRUE field cannot borrow a CODE row',
                            value('S', expression, function=control.code_function('pcpath_' + key, 'z_value_false', flag)) + ' = eps')]
            continue
        state = ('S[.SOURCES = pcunit_handler[.OCCURRENCES = '
                 '$or131_drop(pcunit_handler.OCCURRENCES, pcpath_' + key + ')] :: S.SOURCES]')
        checks += [(key + ' retains its own SOURCE even when skipped', '~' + control.tail(state))]
        flag = str(node[4]).lower()
        for label, line, changed_flag in [('line', '$(z_' + key + ' + 1)', flag),
                                          ('flag', 'z_' + key, 'false' if node[4] else 'true')]:
            checks += [(key + ' retains its exact CODE ' + label,
                        '~' + control.tail(function=control.code_function('pcpath_' + key, line, changed_flag)))]
        if node[4]:
            state = ('S[.POOLS = ppool_handler[.CONSTANTS = '
                     '$or131_fact_drop(ppool_handler.CONSTANTS, pcpath_' + key + ')] :: S.POOLS]')
            checks += [(key + ' retains its folded pool fact', '~' + control.tail(state)),
                       (key + ' cannot borrow an owning pool fact', '~' + control.tail(control.pool_state('pcpath_' + key, 'POBJECT 0')))]
    function = 'pfunction_handler[.CODE.EXPRESSIONS = $or154_code_drop(pfunction_handler.CODE.EXPRESSIONS, pcpath_value_false)]'
    checks += [('FALSE retains CODE even on the retained-condition route', '~' + control.tail(function=function))]
    for key in ['value', 'value_cond', 'value_false']:
        code = ('pfunction_handler.CODE[.EXPRESSIONS = (CODEEFFECT pcpath_' + key + ') :: pfunction_handler.CODE.EXPRESSIONS]')
        state = 'S[.CODE = ' + code + ' :: S.CODE]'
        checks += [('a compiled effect at ' + key + ' cannot disappear through selection',
                    '$compiled_effects(' + state + ', porigin_value) =/= eps' + CONJ +
                    value(state, expression) + ' = eps' + CONJ + value(state + '[.REPORTING = 0]', expression) + ' = eps')]
    checks += [('an unread parent pool cannot replace raw selected VALUE authority',
                value(control.pool_state('pcpath_value', 'POBJECT 0'), expression) + ' = (' + result + ')')]
    code = ('pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR pcpath_value z_value true) :: pfunction_handler.CODE.EXPRESSIONS]')
    pooled = 'PSTRING ([49])' if name.endswith('false-string') else result
    state = control.pool_state('pcpath_value', pooled) + '[.CODE = ' + code + ' :: S.CODE]'
    checks += [('a forged folded parent read cannot replace emitted authority',
                '$compiled_read(' + state + ', porigin_value) = (' + pooled + ')' + CONJ + value(state, expression) + ' = eps')]
    for target in ['pcpath_value_cond', 'pcpath_value_false']:
        for flag in ['true', 'false']:
            code = ('pfunction_handler.CODE[.REDIRECTS = (CODEREDIRECT pcpath_value ' + target + ' ' + flag + ') :: pfunction_handler.CODE.REDIRECTS]')
            checks += [('an emitted shorthand cannot borrow a parent redirect',
                        value('S[.CODE = ' + code + ' :: S.CODE]', expression) + ' = eps')]
    for other in ['PNULL', 'PBOOL false', 'PBOOL true', 'PINT 0', 'PINT (-1)', 'PFLOAT 0', 'PSTRING ([49])']:
        if other != result:
            checks += [('selection preserves its raw tag rather than truth or outer cast bits',
                        value('S', expression) + ' =/= (' + other + ')')]
    bare = 'NStmtReturn (' + expression + ') metadata_cast_return'
    single = 'NExprCastInt (' + expression + ') metadata_cast_1'
    statement = 'NStmtReturn (' + single + ') metadata_cast_return'
    checks += [('raw selected values retain the existing two-cast handler gate',
                '~' + control.tail(control.source_state([('pcpath_cast_return', bare)]), statement=bare) + CONJ +
                '~' + control.tail(control.source_state([('pcpath_cast_return', statement), ('pcpath_cast', single)]), statement=statement))]
    if name.endswith('truthy-negative'):
        state = ('S[.SOURCES = pcunit_handler[.OCCURRENCES = '
                 '$or131_drop(pcunit_handler.OCCURRENCES, pcpath_value_false ++ [PCFIELD 0])] :: S.SOURCES]')
        checks += [('the skipped unresolved FALSE name retains its own source child', '~' + control.tail(state))]
    else:
        choices = [samples.keyword('false'), samples.keyword('true'), samples.keyword('null'),
                   samples.string(''), samples.string('0'), samples.string('00'),
                   samples.floating('8000000000000000'), samples.floating('7ff0000000000000')]
        true_cond = cast('NExprCastInt', integer(7), 'PINT 7')
        false_cond = cast('NExprCastDouble', integer(0), 'PFLOAT 0')
        for selected in choices:
            state, expr, function, typed, terminal = graph(shorthand(False, false_cond, selected))
            checks += [('source0 a selected scalar fallback keeps its raw tag and exact full-state COPY',
                        value(state, expr, function=function) + ' = (' + typed + ')' + CONJ +
                        '$resolve_at(' + state + '[.RESULT = KNOWN (' + typed + ')], KNOWN (' + typed + '), ' + terminal + ') = ' + state + '[.RESULT = KNOWN (' + typed + ')]')]
        for truth, raw in [(True, integer(7)), (True, samples.keyword('true')),
                           (True, samples.floating('7ff0000000000000')), (True, samples.string('00')),
                           (False, samples.keyword('false')), (False, samples.keyword('null')),
                           (False, samples.string('')), (False, samples.string('0')),
                           (False, samples.floating('8000000000000000'))]:
            condition = {'selected': True, 'yes': raw, 'no': full.unknown('SKIPPED_CONDITION156')}
            state, expr, function, typed, terminal = graph(shorthand(truth, condition,
                full.unknown('SKIPPED_RAW_FALSE156') if truth else integer(4)))
            wrong = function + '[.CODE.EXPRESSIONS = (CODEEXPR pcpath_value z_value_cond false) :: ' + function + '.CODE.EXPRESSIONS]'
            checks += [('source0 emitted full conditions retain STRING/zero tags and the FALSE terminal line',
                        value(state, expr, function=function) + ' = (' + typed + ')' + CONJ + value(state, expr, function=wrong) + ' = eps')]
        for truth in [False, True]:
            inner = shorthand(truth, true_cond if truth else false_cond, integer(3))
            outer = shorthand(True, inner, full.unknown('SKIPPED_NESTED_FALSE156'))
            state, expr, function, typed, _ = graph(outer)
            checks += [('source0 nested emitted shorthand conditions retain their raw result',
                        value(state, expr, function=function) + ' = (' + typed + ')')]
            state, expr, function, typed, _ = graph(shorthand(truth, integer(int(truth)), integer(2)))
            wrong = function + '[.CODE.EXPRESSIONS = (CODEEXPR pcpath_value_cond z_value_cond false) :: ' + function + '.CODE.EXPRESSIONS]'
            checks += [('source0 a folded condition needs its authentic compiler flag',
                        value(state, expr, function=function) + ' = (' + typed + ')' + CONJ +
                        value(state, expr, function=wrong) + ' = eps')]
        for bits in ['7ff8000000000001', '7ff0000000000001']:
            nan = samples.floating(bits)
            condition = cast('NExprCastDouble', nan, nan[1])
            state, expr, function, _, _ = graph(shorthand(True, condition, integer(1)))
            masked = state + '[.REPORTING = 0][.ERRORHANDLER = {CALLBACK eps, LEVELS 0}][.SOURCEPENDING = eps][.ERRORFATALTRACE = eps]'
            checks += [('source0 either NaN condition remains intrinsically refused under diagnostic masks',
                        '~$ob_object_cast_chain_quiet(CASTBOOL, ' + nan[1] + ')' + CONJ + value(masked, expr, function=function) + ' = eps')]
            for truth in [False, True]:
                state, expr, function, typed, _ = graph(shorthand(truth, true_cond if truth else false_cond, nan))
                checks += [('source0 selected or skipped NaN fallback has no independent truth demand',
                            value(state, expr, function=function) + ' = (' + typed + ')')]
        for owned in ['POBJECT 0', 'PARRAY 0', 'PSTRING_CARRIER (REQUEST_STRING 0) ([48])']:
            checks += [('owning or request-string conditions cannot borrow quiet primitive truth',
                        '~$ob_object_cast_chain_quiet(CASTBOOL, ' + owned + ')')]
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = current.lifecycle(name, fixture, path)
    checks += [('actual formal/native-cell retirement preserves raw selection and the strict cast return',
                'S_handler.RESULT = KNOWN (' + current.root_value(name) + r') /\ S.RESULT = KNOWN PNULL /\ ' +
                value('S', current.expression(name), 'porigin_cast') + ' = (' + current.root_value(name) + ')')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
