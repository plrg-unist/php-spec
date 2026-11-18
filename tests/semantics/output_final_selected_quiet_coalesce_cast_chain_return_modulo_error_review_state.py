#!/usr/bin/env python3
"""Independent strict-NULL, raw VALUE, compiler authority and retirement checks."""
import output_final_selected_constant_float_cast_return_modulo_error_review_state as control
import output_final_selected_recursive_numeric_sign_cast_chain_return_modulo_error_review_state as scaffold
import output_final_selected_quiet_short_circuit_cast_chain_return_modulo_error_review_state as samples
import output_final_selected_emitted_condition_full_ternary_cast_chain_return_modulo_error_review_state as full
import output_final_selected_quiet_coalesce_cast_chain_return_modulo_error_state as current

runner, CASES, CONJ = current.runner, current.CASES, current.CONJ
PREFIX = current.PREFIX + full.PREFIX[len(full.current.PREFIX):]


def value(state, expression, origin='porigin_value', function='pfunction_handler'):
    return scaffold.value(state, expression, origin, function)


def integer(number):
    spelling = '(' + str(number) + ')' if number < 0 else str(number)
    typed = 'PINT ' + spelling
    return 'NScalarInt (INTEGER ' + spelling + ') {metadata}', typed, typed


def coalesce(left, right):
    return {'left': left, 'right': right}


def cast(kind, child, result):
    return {'cast': kind, 'child': child, 'result': result}


def graph(node):
    rows, codes, facts = [], [], []

    def child(path, field):
        return '(' + path + ' ++ [PCFIELD ' + str(field) + '])'

    def build(node, path):
        line = '$(z_value_right + ' + str(len(rows) + 11) + ')'
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
        else:
            expression_left, value_left, _ = build(node['left'], child(path, 0))
            expression_right, value_right, line = build(node['right'], child(path, 1))
            expression = 'NExprBinaryOpCoalesce (' + expression_left + ') (' + expression_right + ') ' + metadata
            typed, pooled, folded = value_right if value_left == 'PNULL' else value_left, None, False
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
    checks += [('strict NULL selection retains the exact raw nonowning tag',
                value('S', expression) + ' = (' + result + r') /\ $value_nodes(' + result + ') = eps'),
               ('preset raw VALUE cannot replace NORMAL source authority',
                value('S[.COMPLETION = BUDGET][.RESULT = KNOWN (' + result + ')]', expression) + ' = eps'),
               ('the selected handler retains its exact CODE unit and BODY',
                '~' + control.tail(function='pfunction_handler[.CODE.UNIT = $(n_cast_handler + 1)]') + CONJ +
                '~' + control.tail(function='pfunction_handler[.BODY = pfunction_handler.BODY ++ [PCINDEX 0]]'))]
    for key, node in nodes.items():
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
                       (key + ' cannot borrow an owning pool value',
                        '~' + control.tail(control.pool_state('pcpath_' + key, 'POBJECT 0')))]
    for key in ['cast_return', 'value_right ++ [PCFIELD 0]'] if name.endswith('nonnull-int-zero') else ['cast_return']:
        state = ('S[.SOURCES = pcunit_handler[.OCCURRENCES = '
                 '$or131_drop(pcunit_handler.OCCURRENCES, pcpath_' + key + ')] :: S.SOURCES]')
        checks += [('Return and skipped indexed name retain separate SOURCE authority', '~' + control.tail(state))]
    function = 'pfunction_handler[.CODE.EXPRESSIONS = $or154_code_drop(pfunction_handler.CODE.EXPRESSIONS, pcpath_value_right)]'
    checks += [('both arms retain CODE even on the nonnull retained-value route', '~' + control.tail(function=function))]
    for key in ['value', 'value_left', 'value_right']:
        code = ('pfunction_handler.CODE[.EXPRESSIONS = (CODEEFFECT pcpath_' + key + ') :: pfunction_handler.CODE.EXPRESSIONS]')
        state = 'S[.CODE = ' + code + ' :: S.CODE]'
        checks += [('compiled effects at ' + key + ' cannot be erased by NULL selection or masks',
                    '$compiled_effects(' + state + ', porigin_value) =/= eps' + CONJ +
                    value(state, expression) + ' = eps' + CONJ + value(state + '[.REPORTING = 0]', expression) + ' = eps')]
    checks += [('an unread parent pool cannot replace emitted raw VALUE authority',
                value(control.pool_state('pcpath_value', 'POBJECT 0'), expression) + ' = (' + result + ')'),
               ('live display precision does not change strict NULL selection',
                value('$precision_memory(S, 1)', expression) + ' = (' + result + ')')]
    code = ('pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR pcpath_value z_value true) :: pfunction_handler.CODE.EXPRESSIONS]')
    pooled = 'PSTRING ([48])' if name.endswith('null-nested-string') else result
    state = control.pool_state('pcpath_value', pooled) + '[.CODE = ' + code + ' :: S.CODE]'
    checks += [('even an exact forged folded root cannot replace emitted read-eps authority',
                '$compiled_read(' + state + ', porigin_value) = (' + pooled + ')' + CONJ + value(state, expression) + ' = eps')]
    for target in ['pcpath_value_left', 'pcpath_value_right']:
        for flag in ['true', 'false']:
            code = ('pfunction_handler.CODE[.REDIRECTS = (CODEREDIRECT pcpath_value ' + target + ' ' + flag + ') :: pfunction_handler.CODE.REDIRECTS]')
            checks += [('emitted coalesce cannot borrow a parent redirect',
                        value('S[.CODE = ' + code + ' :: S.CODE]', expression) + ' = eps')]
    for other in ['PNULL', 'PBOOL false', 'PBOOL true', 'PINT 0', 'PINT (-1)', 'PFLOAT 0', 'PSTRING ([48])']:
        if other != result:
            checks += [('strict NULL selection preserves raw type before the outer casts',
                        value('S', expression) + ' =/= (' + other + ')')]
    bare = 'NStmtReturn (' + expression + ') metadata_cast_return'
    single = 'NExprCastInt (' + expression + ') metadata_cast_1'
    statement = 'NStmtReturn (' + single + ') metadata_cast_return'
    checks += [('selected raw tags retain the existing two-cast return gate',
                '~' + control.tail(control.source_state([('pcpath_cast_return', bare)]), statement=bare) + CONJ +
                '~' + control.tail(control.source_state([('pcpath_cast_return', statement), ('pcpath_cast', single)]), statement=statement))]
    if name.endswith('nonnull-int-zero'):
        choices = [samples.keyword('false'), samples.keyword('true'), integer(0), integer(-1),
                   samples.floating('0000000000000000'), samples.floating('8000000000000000'),
                   samples.floating('7ff0000000000000'), samples.string(''), samples.string('0'), samples.string('00')]
        for raw in choices:
            for left, right in [(raw, full.unknown('SKIPPED_NULL_RHS157')), (samples.keyword('null'), raw)]:
                state, expr, function, typed, terminal = graph(coalesce(left, right))
                wrong = function + '[.CODE.EXPRESSIONS = (CODEEXPR pcpath_value 0 false) :: ' + function + '.CODE.EXPRESSIONS]'
                checks += [('source0 false-like nonnull VALUE is retained and only NULL selects the exact fallback COPY',
                            value(state, expr, function=function) + ' = (' + typed + ')' + CONJ +
                            value(state, expr, function=wrong) + ' = eps' + CONJ +
                            '$resolve_at(' + state + '[.RESULT = KNOWN (' + typed + ')], KNOWN (' + typed + '), ' + terminal + ') = ' + state + '[.RESULT = KNOWN (' + typed + ')]')]
        for kind, raw, typed in [('NExprCastInt', samples.string('0'), 'PINT 0'),
                                  ('NExprCastBool', integer(0), 'PBOOL false'),
                                  ('NExprCastDouble', integer(0), 'PFLOAT 0')]:
            state, expr, function, _, _ = graph(coalesce(cast(kind, raw, typed), full.unknown('SKIPPED_EMITTED_LEFT157')))
            checks += [('source0 emitted false-like LEFT retains its tag without a Boolean demand',
                        value(state, expr, function=function) + ' = (' + typed + ')')]
        for node in [coalesce(coalesce(samples.keyword('null'), samples.keyword('false')), full.unknown('SKIPPED_NESTED157')),
                     coalesce(samples.keyword('null'), coalesce(samples.keyword('false'), full.unknown('SKIPPED_NESTED157'))),
                     coalesce(coalesce(samples.keyword('null'), samples.keyword('null')), samples.string('0'))]:
            state, expr, function, typed, _ = graph(node)
            checks += [('source0 recursive LEFT and RIGHT coalesce preserve strict NULL and raw tags',
                        value(state, expr, function=function) + ' = (' + typed + ')')]
        for bits in ['7ff8000000000001', '7ff0000000000001']:
            nan = samples.floating(bits)
            for node in [coalesce(nan, full.unknown('SKIPPED_NAN157')),
                         coalesce(samples.keyword('null'), nan), coalesce(integer(0), nan)]:
                state, expr, function, typed, _ = graph(node)
                masked = state + '[.REPORTING = 0][.ERRORHANDLER = {CALLBACK eps, LEVELS 0}][.SOURCEPENDING = eps][.ERRORFATALTRACE = eps]'
                checks += [('source0 retained, selected and skipped NaN VALUE has no independent truth demand',
                            '~$ob_object_cast_chain_quiet(CASTBOOL, ' + nan[1] + ')' + CONJ +
                            value(masked, expr, function=function) + ' = (' + typed + ')')]
            state, expr, function, _, _ = graph(cast('NExprCastInt', coalesce(nan, integer(1)), 'PINT 0'))
            checks += [('source0 accepting NaN VALUE does not bypass the separate outer INT cast guard',
                        '~$ob_object_cast_chain_quiet(CASTINT, ' + nan[1] + ')' + CONJ + value(state, expr, function=function) + ' = eps')]
        for template in ['NExprVariable (BYTES "eA==") {metadata}',
                         'NExprFuncCall (NName (BYTES "cGVlcjE1Nw==") (eps)) (SEQUENCE eps) {metadata}']:
            forged = (template, 'PINT 0', 'PINT 0')
            for node in [coalesce(forged, integer(1)), coalesce(samples.keyword('null'), forged), coalesce(integer(0), forged)]:
                state, expr, function, _, _ = graph(node)
                checks += [('location or call shapes cannot borrow fabricated scalar CODE and pool authority',
                            value(state, expr, function=function) + ' = eps')]
        for owned in ['POBJECT 0', 'PARRAY 0', 'PSTRING_CARRIER (REQUEST_STRING 0) ([48])']:
            checks += [('selected primitive source cannot borrow an owning or request-string pool fact',
                        value(control.pool_state('pcpath_value_left_child', owned), expression) + ' = eps')]
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = current.lifecycle(name, fixture, path)
    checks += [('actual formal/native-cell retirement preserves coalesce VALUE and the strict return cast',
                'S_handler.RESULT = KNOWN (' + current.root_value(name) + r') /\ S.RESULT = KNOWN PNULL /\ ' +
                value('S', current.expression(name), 'porigin_cast') + ' = (' + current.root_value(name) + ')')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
