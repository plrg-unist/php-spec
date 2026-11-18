#!/usr/bin/env python3
"""Independent folded-condition authority, raw selection and retirement checks."""
import output_final_selected_constant_float_cast_return_modulo_error_review_state as control
import output_final_selected_recursive_numeric_sign_cast_chain_return_modulo_error_review_state as scaffold
import output_final_selected_quiet_short_circuit_cast_chain_return_modulo_error_review_state as samples
import output_final_selected_emitted_condition_full_ternary_cast_chain_return_modulo_error_review_state as full
import output_final_selected_emitted_condition_shorthand_ternary_cast_chain_return_modulo_error_review_state as short
import output_final_selected_folded_condition_ternary_cast_chain_return_modulo_error_state as current

runner, CONJ = current.runner, current.CONJ
PREFIX = current.PREFIX + full.PREFIX[len(full.current.PREFIX):]
CASES = {name: current.sources.CASES['native-selected-folded-condition-ternary-cast-chain-return-modulo-error-' + name]
         for name in ['warning-right-cv-pair-full-false-string',
                      'warning-left-constant-shorthand-true-int']}
value = full.value


def graph(condition, truth, shorthand, selected=None):
    rows, codes, facts = [], [], []

    def child(path, field):
        return '(' + path + ' ++ [PCFIELD ' + str(field) + '])'

    def raw(node, path):
        line = '$(z_value_false + ' + str(len(rows) + 11) + ')'
        metadata = '([(MstartLine ' + line + ')])'
        if isinstance(node, dict):
            children = [raw(item, child(path, field)) for field, item in enumerate(node['children'])]
            expression = node['kind'] + ' ' + ' '.join('(' + item[0] + ')' for item in children) + ' ' + metadata
            typed = pooled = node['result']
            line = children[-1][2]
        else:
            template, typed, pooled = node
            expression = template.replace('{metadata}', metadata)
            if expression.startswith('NExprConstFetch '):
                rows.append((child(path, 0), expression[len('NExprConstFetch ('):].removesuffix(') ' + metadata)))
        rows.append((path, expression))
        codes.append((path, line, str(typed is not None).lower()))
        if pooled is not None:
            facts.append((path, pooled))
        return expression, typed, line

    cond, cond_value, _ = raw(condition, child('pcpath_value', 0))
    selected = selected or (samples.string('0') if truth else samples.keyword('false'))
    yes = ('ABSENT', None, None) if shorthand else raw(selected if truth else full.unknown('SKIPPED_TRUE158'), child('pcpath_value', 1))
    no = raw(full.unknown('SKIPPED_FALSE158') if truth else selected, child('pcpath_value', 2))
    expression = 'NExprTernary (' + cond + ') ' + ('ABSENT' if shorthand else '(' + yes[0] + ')') + ' (' + no[0] + ') metadata_value'
    rows.append(('pcpath_value', expression))
    codes.append(('pcpath_value', no[2], 'false'))
    state, function = scaffold.changed(rows, codes, facts)
    if shorthand:
        original = function
        function = function.replace('pfunction_handler.CODE.EXPRESSIONS',
                                    '$or154_code_drop(pfunction_handler.CODE.EXPRESSIONS, pcpath_value ++ [PCFIELD 1])')
        state = state.replace(original, function).replace('pcunit_handler.OCCURRENCES',
                '$or131_drop(pcunit_handler.OCCURRENCES, pcpath_value ++ [PCFIELD 1])')
    return state, expression, function, cond_value if shorthand and truth else (yes[1] if truth else no[1]), no[2]


def frontier(name, fixture, path):
    bindings, checks = current.frontier(name, fixture, path)
    bindings += ['$source_unit(S.SOURCES, n_cast_handler) = (pcunit_handler)',
                 '$pool_at(S.POOLS, n_cast_handler) = (ppool_handler)']
    nodes = current.nodes(name)
    expression, result = current.expression(name, 'value'), nodes['value'][3]
    checks += [('a folded condition selects the raw tag before either return cast',
                value('S', expression) + ' = (' + result + ')' + CONJ + '$value_nodes(' + result + ') = eps'),
               ('NORMAL and the real handler unit/body remain required',
                value('S[.COMPLETION = BUDGET][.RESULT = KNOWN (' + result + ')]', expression) + ' = eps' + CONJ +
                '~' + control.tail(function='pfunction_handler[.CODE.UNIT = $(n_cast_handler + 1)]') + CONJ +
                '~' + control.tail(function='pfunction_handler[.BODY = pfunction_handler.BODY ++ [PCINDEX 0]]'))]
    for key, node in nodes.items():
        if node[0] == 'absent':
            checks += [('ABSENT TRUE admits neither SOURCE nor CODE authority',
                        value(control.source_state([('pcpath_' + key, 'NScalarInt (INTEGER 1) metadata_value')]), expression) + ' = eps' + CONJ +
                        value('S', expression, function=control.code_function('pcpath_' + key, 'z_value_false', 'true')) + ' = eps' + CONJ +
                        value('S', expression, function=control.code_function('pcpath_' + key, 'z_value_false', 'false')) + ' = eps')]
            continue
        state = ('S[.SOURCES = pcunit_handler[.OCCURRENCES = '
                 '$or131_drop(pcunit_handler.OCCURRENCES, pcpath_' + key + ')] :: S.SOURCES]')
        checks += [(key + ' keeps its own SOURCE even on the skipped route', '~' + control.tail(state))]
        for label, line, flag in [('line', '$(z_' + key + ' + 1)', str(node[4]).lower()),
                                  ('flag', 'z_' + key, str(not node[4]).lower())]:
            checks += [(key + ' keeps its own compiler ' + label,
                        '~' + control.tail(function=control.code_function('pcpath_' + key, line, flag)))]
        if node[4]:
            state = ('S[.POOLS = ppool_handler[.CONSTANTS = '
                     '$or131_fact_drop(ppool_handler.CONSTANTS, pcpath_' + key + ')] :: S.POOLS]')
            checks += [(key + ' cannot borrow a missing or owning folded fact',
                        '~' + control.tail(state) + CONJ + '~' + control.tail(control.pool_state('pcpath_' + key, 'POBJECT 0')))]
    for key in ['value', 'value_cond', 'value_false'] + ([] if 'shorthand' in name else ['value_true']):
        code = 'pfunction_handler.CODE[.EXPRESSIONS = (CODEEFFECT pcpath_' + key + ') :: pfunction_handler.CODE.EXPRESSIONS]'
        state = 'S[.CODE = ' + code + ' :: S.CODE]'
        checks += [('compiled effects at ' + key + ' cannot disappear behind a diagnostic mask',
                    '$compiled_effects(' + state + ', porigin_value) =/= eps' + CONJ +
                    value(state + '[.REPORTING = 0]', expression) + ' = eps')]
    code = 'pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR pcpath_value z_value true) :: pfunction_handler.CODE.EXPRESSIONS]'
    pooled = result.replace('PSTRING_CARRIER INTERNED_STRING', 'PSTRING')
    state = control.pool_state('pcpath_value', pooled) + '[.CODE = ' + code + ' :: S.CODE]'
    checks += [('a folded condition cannot certify a forged folded ternary root',
                '$compiled_read(' + state + ', porigin_value) = (' + pooled + ')' + CONJ + value(state, expression) + ' = eps')]
    for target in ['pcpath_value_cond', 'pcpath_value_false']:
        code = 'pfunction_handler.CODE[.REDIRECTS = (CODEREDIRECT pcpath_value ' + target + ' false) :: pfunction_handler.CODE.REDIRECTS]'
        checks += [('the emitted ternary cannot borrow a constexpr parent redirect',
                    value('S[.CODE = ' + code + ' :: S.CODE]', expression) + ' = eps')]
    for other in ['PNULL', 'PBOOL false', 'PBOOL true', 'PINT 0', 'PFLOAT 0', 'PSTRING ([49])']:
        if other != result:
            checks += [('equal outer-cast bits do not erase the selected raw tag', value('S', expression) + ' =/= (' + other + ')')]
    bare = 'NStmtReturn (' + expression + ') metadata_cast_return'
    single = 'NExprCastInt (' + expression + ') metadata_cast_1'
    statement = 'NStmtReturn (' + single + ') metadata_cast_return'
    checks += [('folded condition selection retains the existing two-cast return gate',
                '~' + control.tail(control.source_state([('pcpath_cast_return', bare)]), statement=bare) + CONJ +
                '~' + control.tail(control.source_state([('pcpath_cast_return', statement), ('pcpath_cast', single)]), statement=statement))]
    if name.endswith('full-false-string'):
        choices = [(samples.keyword('false'), False), (samples.keyword('true'), True),
                   (samples.keyword('null'), False), (short.integer(0), False), (short.integer(1), True),
                   (samples.string(''), False), (samples.string('0'), False), (samples.string('00'), True),
                   (samples.floating('0000000000000000'), False),
                   (samples.floating('8000000000000000'), False), (samples.floating('7ff0000000000000'), True),
                   ({'kind': 'NExprBooleanNot', 'children': [short.integer(0)], 'result': 'PBOOL true'}, True),
                   ({'kind': 'NExprUnaryMinus', 'children': [short.integer(1)], 'result': 'PINT (-1)'}, True),
                   ({'kind': 'NExprBinaryOpSmaller', 'children': [short.integer(0), short.integer(1)], 'result': 'PBOOL true'}, True)]
        for condition, truth in choices:
            for shorthand in [False, True]:
                state, expr, function, typed, terminal = graph(condition, truth, shorthand)
                wrong = function + '[.CODE.EXPRESSIONS = (CODEEXPR pcpath_value $(' + terminal[2:-1] + ' + 1) false) :: ' + function + '.CODE.EXPRESSIONS]'
                checks += [('source0 folded primitive and compound conditions preserve full/shorthand raw VALUE and FALSE terminal line',
                            value(state, expr, function=function) + ' = (' + typed + ')' + CONJ +
                            value(state, expr, function=wrong) + ' = eps' + CONJ +
                            '$resolve_at(' + state + '[.RESULT = KNOWN (' + typed + ')], KNOWN (' + typed + '), ' + terminal + ') = ' + state + '[.RESULT = KNOWN (' + typed + ')]')]
        for bits in ['7ff8000000000001', '7ff0000000000001']:
            nan = samples.floating(bits)
            for shorthand in [False, True]:
                state, expr, function, _, _ = graph(nan, True, shorthand)
                masked = state + '[.REPORTING = 0][.ERRORHANDLER = {CALLBACK eps, LEVELS 0}][.SOURCEPENDING = eps][.ERRORFATALTRACE = eps]'
                checks += [('source0 either NaN class remains an intrinsically refused condition under masks',
                            '~$ob_object_cast_chain_quiet(CASTBOOL, ' + nan[1] + ')' + CONJ + value(masked, expr, function=function) + ' = eps')]
            state, expr, function, typed, _ = graph(short.integer(1), True, False, nan)
            checks += [('source0 a selected NaN VALUE does not bypass the separate outer INT cast guard',
                        value(state, expr, function=function) + ' = (' + typed + ')' + CONJ + '~$ob_object_cast_chain_quiet(CASTINT, ' + typed + ')')]
        for template in ['NExprVariable (BYTES "eA==") {metadata}',
                         'NExprFuncCall (NName (BYTES "cGVlcjE1OA==") (eps)) (SEQUENCE eps) {metadata}']:
            for shorthand in [False, True]:
                state, expr, function, _, _ = graph((template, 'PINT 0', 'PINT 0'), False, shorthand)
                checks += [('source0 a location or call cannot borrow fabricated folded scalar authority', value(state, expr, function=function) + ' = eps')]
        for owned in ['POBJECT 0', 'PARRAY 0', 'PSTRING_CARRIER (REQUEST_STRING 0) ([48])']:
            checks += [('owning and request-string conditions retain the intrinsic quiet primitive fence',
                        '~$ob_object_cast_chain_quiet(CASTBOOL, ' + owned + ')' + CONJ +
                        value(control.pool_state('pcpath_value_cond', owned), expression) + ' = eps')]
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = current.lifecycle(name, fixture, path)
    checks += [('real formal/native-cell retirement preserves the selected raw tag and exact nested return',
                'S_handler.RESULT = KNOWN (' + current.root_value(name) + ')' + CONJ + 'S.RESULT = KNOWN PNULL' + CONJ +
                value('S', current.expression(name), 'porigin_cast') + ' = (' + current.root_value(name) + ')')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
