#!/usr/bin/env python3
"""Independent full-ternary VALUE, copy, compiler-line and retirement controls."""
import base64
import output_final_selected_constant_float_cast_return_modulo_error_review_state as control
import output_final_selected_recursive_numeric_sign_cast_chain_return_modulo_error_review_state as scaffold
import output_final_selected_quiet_short_circuit_cast_chain_return_modulo_error_review_state as samples
import output_final_selected_emitted_left_short_circuit_cast_chain_return_modulo_error_review_state as prior
import output_final_selected_emitted_condition_full_ternary_cast_chain_return_modulo_error_state as current

runner, CASES, CONJ = current.runner, current.CASES, current.CONJ
PREFIX = current.PREFIX + prior.PREFIX[len(prior.current.PREFIX):]


def value(state, expression, origin='porigin_value', function='pfunction_handler'):
    return scaffold.value(state, expression, origin, function)


def unknown(name):
    payload = base64.b64encode(name.encode()).decode()
    return ('NExprConstFetch (NName (BYTES "' + payload + '") {metadata}) {metadata}', None, None)


def ternary(truth, yes, no, cond=None, cond_kind='NExprCastBool', false_line='z_value_false'):
    rows, codes, facts = [], [], []

    def child(path, field):
        return '(' + path + ' ++ [PCFIELD ' + str(field) + '])'

    def raw(node, path, line):
        template, typed, pooled = node
        metadata = '([(MstartLine ' + line + ')])'
        expression = template.replace('{metadata}', metadata)
        rows.append((path, expression))
        if expression.startswith('NExprConstFetch '):
            rows.append((child(path, 0), expression[len('NExprConstFetch ('):].removesuffix(') ' + metadata)))
        codes.append((path, line, 'false' if typed is None else 'true'))
        if pooled is not None:
            facts.append((path, pooled))
        return expression, typed, line

    def arm(node, path, line):
        if isinstance(node, dict):
            base = line[2:-1] if line.startswith('$(') and line.endswith(')') else line
            return build(node['truth'], node['yes'], node['no'], path,
                         '$((' + base + ') + 1)', '$((' + base + ') + 2)', '$((' + base + ') + 3)')
        return raw(node, path, line)

    def build(selected, yes, no, path, cond_line, true_line, false_line, cond=None, kind='NExprCastBool'):
        cond_path = child(path, 0)
        leaf = samples.floating('3ff0000000000000' if selected else '0000000000000000') if cond is None else cond
        if kind is None:
            condition, _, _ = raw(leaf, cond_path, cond_line)
        else:
            expression, _, terminal = raw(leaf, child(cond_path, 0), cond_line)
            metadata = '([(MstartLine ' + cond_line + '), (Mkind ' + ('2' if kind == 'NExprCastDouble' else '1') + ')])'
            condition = kind + ' (' + expression + ') ' + metadata
            rows.append((cond_path, condition))
            codes.append((cond_path, terminal, 'false'))
        expression_true, value_true, _ = arm(yes, child(path, 1), true_line)
        expression_false, value_false, terminal = arm(no, child(path, 2), false_line)
        expression = 'NExprTernary (' + condition + ') (' + expression_true + ') (' + expression_false + ') ([(MstartLine ' + cond_line + ')])'
        rows.append((path, expression))
        codes.append((path, terminal, 'false'))
        return expression, value_true if selected else value_false, terminal

    expression, result, terminal = build(truth, yes, no, 'pcpath_value',
        'z_value_cond_child', 'z_value_true', false_line, cond, cond_kind)
    state, function = scaffold.changed(rows, codes, facts)
    return state, expression, function, result, terminal


def frontier(name, fixture, path):
    bindings, checks = current.frontier(name, fixture, path)
    bindings += ['$source_unit(S.SOURCES, n_cast_handler) = (pcunit_handler)',
                 '$pool_at(S.POOLS, n_cast_handler) = (ppool_handler)']
    nodes = current.nodes(name)
    expression, result = current.expression(name, 'value'), nodes['value'][3]
    checks += [('the full ternary retains its selected raw tag and no owner',
                value('S', expression) + ' = (' + result + r') /\ $value_nodes(' + result + ') = eps'),
               ('BUDGET cannot borrow a preset selected result',
                value('S[.COMPLETION = BUDGET][.RESULT = KNOWN (' + result + ')]', expression) + ' = eps'),
               ('the handler keeps its real CODE unit and BODY',
                '~' + control.tail(function='pfunction_handler[.CODE.UNIT = $(n_cast_handler + 1)]') + CONJ +
                '~' + control.tail(function='pfunction_handler[.BODY = pfunction_handler.BODY ++ [PCINDEX 0]]'))]
    for key, node in nodes.items():
        source = ('S[.SOURCES = pcunit_handler[.OCCURRENCES = '
                  '$or131_drop(pcunit_handler.OCCURRENCES, pcpath_' + key + ')] :: S.SOURCES]')
        checks += [(key + ' has its own SOURCE even when unselected', '~' + control.tail(source))]
        flag = 'true' if node[4] else 'false'
        for label, line, forged in [('line', '$(z_' + key + ' + 1)', flag),
                                    ('flag', 'z_' + key, 'false' if node[4] else 'true')]:
            checks += [(key + ' keeps its exact compiler ' + label,
                        '~' + control.tail(function=control.code_function('pcpath_' + key, line, forged)))]
        if node[4]:
            state = ('S[.POOLS = ppool_handler[.CONSTANTS = '
                     '$or131_fact_drop(ppool_handler.CONSTANTS, pcpath_' + key + ')] :: S.POOLS]')
            checks += [(key + ' retains its folded pool fact', '~' + control.tail(state)),
                       (key + ' cannot borrow an owning fact', '~' + control.tail(control.pool_state('pcpath_' + key, 'POBJECT 0')))]
    for key in ['value_true', 'value_false']:
        function = 'pfunction_handler[.CODE.EXPRESSIONS = $or154_code_drop(pfunction_handler.CODE.EXPRESSIONS, pcpath_' + key + ')]'
        checks += [('both arms retain CODE before runtime selection', '~' + control.tail(function=function))]
    for key in ['value', 'value_cond', 'value_true', 'value_false']:
        code = ('pfunction_handler.CODE[.EXPRESSIONS = (CODEEFFECT pcpath_' + key + ') :: pfunction_handler.CODE.EXPRESSIONS]')
        state = 'S[.CODE = ' + code + ' :: S.CODE]'
        checks += [('a compiled effect at ' + key + ' cannot disappear through selection',
                    '$compiled_effects(' + state + ', porigin_value) =/= eps' + CONJ + value(state, expression) + ' = eps')]
    checks += [('an unread parent pool does not replace selected VALUE authority',
                value(control.pool_state('pcpath_value', 'POBJECT 0'), expression) + ' = (' + result + ')')]
    code = ('pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR pcpath_value z_value true) :: pfunction_handler.CODE.EXPRESSIONS]')
    pooled = 'PSTRING ([49])' if name.endswith('true-string') else result
    state = control.pool_state('pcpath_value', pooled) + '[.CODE = ' + code + ' :: S.CODE]'
    checks += [('an exact forged folded read cannot replace the emitted parent',
                '$compiled_read(' + state + ', porigin_value) = (' + pooled + ')' + CONJ + value(state, expression) + ' = eps')]
    for target in ['pcpath_value_cond', 'pcpath_value_true', 'pcpath_value_false']:
        for flag in ['false', 'true']:
            code = ('pfunction_handler.CODE[.REDIRECTS = (CODEREDIRECT pcpath_value ' + target + ' ' + flag + ') :: pfunction_handler.CODE.REDIRECTS]')
            checks += [('a full runtime ternary cannot borrow a parent redirect',
                        value('S[.CODE = ' + code + ' :: S.CODE]', expression) + ' = eps')]
    bare = 'NStmtReturn (' + expression + ') metadata_cast_return'
    single = 'NExprCastInt (' + expression + ') metadata_cast_1'
    statement = 'NStmtReturn (' + single + ') metadata_cast_return'
    checks += [('selected VALUE cannot bypass the existing two-cast handler gate',
                '~' + control.tail(control.source_state([('pcpath_cast_return', bare)]), statement=bare) + CONJ +
                '~' + control.tail(control.source_state([('pcpath_cast_return', statement), ('pcpath_cast', single)]), statement=statement))]
    for other in ['PNULL', 'PBOOL false', 'PBOOL true', 'PINT 0', 'PINT 1', 'PFLOAT 0', 'PSTRING ([49])']:
        if other != result:
            checks += [('selection preserves the actual tag rather than only truth or final cast bits',
                        value('S', expression) + ' =/= (' + other + ')')]
    if name.endswith('false-constant'):
        source = ('S[.SOURCES = pcunit_handler[.OCCURRENCES = '
                  '$or131_drop(pcunit_handler.OCCURRENCES, pcpath_value_true ++ [PCFIELD 0])] :: S.SOURCES]')
        checks += [('the skipped unresolved TRUE name has its own source child', '~' + control.tail(source))]
        choices = [samples.keyword('false'), samples.keyword('true'), samples.keyword('null'),
                   samples.string(''), samples.string('0'), samples.string('00'),
                   samples.floating('8000000000000000'), samples.floating('7ff0000000000000')]
        for truth in [False, True]:
            for selected in choices:
                state, expr, function, typed, _ = ternary(truth,
                    selected if truth else unknown('UNSELECTED_TRUE155'),
                    unknown('UNSELECTED_FALSE155') if truth else selected)
                checks += [('source0 selection copies the exact scalar VALUE without an arm truth conversion',
                            value(state, expr, function=function) + ' = (' + typed + ')' + CONJ +
                            '$resolve_at(' + state + '[.RESULT = KNOWN (' + typed + ')], KNOWN (' + typed + '), z_value_false) = ' + state + '[.RESULT = KNOWN (' + typed + ')]')]
            state, expr, function, _, terminal = ternary(truth, samples.keyword('true'), samples.keyword('false'),
                false_line='$(z_value_false + 7)')
            wrong = function + '[.CODE.EXPRESSIONS = (CODEEXPR pcpath_value z_value_true false) :: ' + function + '.CODE.EXPRESSIONS]'
            checks += [('source0 FALSE supplies the parent line regardless of selected arm',
                        value(state, expr, function=function) + ' = (PBOOL ' + str(truth).lower() + ')' + CONJ +
                        value(state, expr, function=wrong) + ' = eps')]
            state, expr, function, _, _ = ternary(truth, samples.keyword('true'), samples.keyword('false'), cond_kind=None)
            checks += [('source0 a folded condition cannot borrow the emitted-condition contour',
                        value(state, expr, function=function) + ' = eps')]
            nested = {'truth': not truth, 'yes': samples.keyword('true'), 'no': samples.keyword('null')}
            state, expr, function, typed, _ = ternary(truth,
                nested if truth else unknown('SKIPPED_OUTER_TRUE155'),
                unknown('SKIPPED_OUTER_FALSE155') if truth else nested,
                false_line='$(z_value_false + 9)')
            checks += [('source0 a nested selected chain preserves its own VALUE and distinct terminal lines',
                        value(state, expr, function=function) + ' = (' + typed + ')')]
        for bits in ['7ff8000000000001', '7ff0000000000001']:
            nan = samples.floating(bits)
            state, expr, function, _, _ = ternary(True, samples.keyword('true'), samples.keyword('false'), nan, 'NExprCastDouble')
            masked = 'S_masked_' + str(len(bindings))
            bindings += [masked + ' = ' + state + '[.REPORTING = 0][.ERRORHANDLER = {CALLBACK eps, LEVELS 0}][.SOURCEPENDING = eps][.ERRORFATALTRACE = eps]']
            checks += [('source0 NaN condition truth remains intrinsically refused under diagnostic masks',
                        '~$ob_object_cast_chain_quiet(CASTBOOL, ' + nan[1] + ')' + CONJ +
                        '$boolean_result(' + masked + '[.RESULT = KNOWN (' + nan[1] + ')], false, z_value_cond) = ' + masked + '[.RESULT = KNOWN (PBOOL true)]' + CONJ +
                        value(masked, expr, function=function) + ' = eps')]
            for truth in [False, True]:
                state, expr, function, _, _ = ternary(truth, nan if truth else samples.keyword('false'), samples.keyword('true') if truth else nan)
                checks += [('source0 selected NaN is a VALUE and follows outer CASTFLOAT policy without truth demand',
                            value(state, expr, function=function) + ' = (' + nan[1] + ')' + CONJ +
                            '$ob_object_cast_chain_quiet(CASTFLOAT, ' + nan[1] + ')' + CONJ +
                            '$cast_apply(S[.RESULT = KNOWN (' + nan[1] + ')], CASTFLOAT, ' + nan[1] + ', z_value_false) = S[.RESULT = KNOWN (' + nan[1] + ')]')]
                state, expr, function, typed, _ = ternary(truth, samples.keyword('false') if truth else nan, nan if truth else samples.keyword('true'))
                checks += [('source0 a compiled skipped NaN has a line without an arm truth demand',
                            value(state, expr, function=function) + ' = (' + typed + ')')]
        short = 'NExprTernary (' + current.expression(name, 'value_cond') + ') ABSENT (' + current.expression(name, 'value_false') + ') metadata_value'
        checks += [('a shorthand conditional cannot borrow the full-ternary rule',
                    value(control.source_state([('pcpath_value', short)]), short) + ' = eps')]
        for owned in ['POBJECT 0', 'PARRAY 0', 'PSTRING_CARRIER (REQUEST_STRING 0) ([48])']:
            checks += [('owning or request-string conditions cannot borrow quiet primitive truth',
                        '~$ob_object_cast_chain_quiet(CASTBOOL, ' + owned + ')')]
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = current.lifecycle(name, fixture, path)
    checks += [('actual formal/native-cell retirement keeps selected raw VALUE and exact nested return',
                'S_handler.RESULT = KNOWN (' + current.root_value(name) + r') /\ S.RESULT = KNOWN PNULL /\ ' +
                value('S', current.expression(name), 'porigin_cast') + ' = (' + current.root_value(name) + ')')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
