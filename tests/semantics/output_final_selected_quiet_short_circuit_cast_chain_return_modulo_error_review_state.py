#!/usr/bin/env python3
"""Independent selected/skipped truth, compiler authority and retirement checks."""
import base64
import output_final_selected_constant_float_cast_return_modulo_error_review_state as control
import output_final_selected_recursive_numeric_sign_cast_chain_return_modulo_error_review_state as scaffold
import output_final_selected_quiet_short_circuit_cast_chain_return_modulo_error_state as current

runner, CASES = current.runner, current.CASES
PREFIX = current.PREFIX + scaffold.PREFIX[len(scaffold.current.PREFIX):]
CONJ = current.CONJ


def value(state, expression, origin='porigin_value', function='pfunction_handler'):
    return scaffold.value(state, expression, origin, function)


def keyword(text):
    payload = base64.b64encode(text.encode()).decode()
    node = 'NExprConstFetch (NName (BYTES "' + payload + '") {metadata}) {metadata}'
    typed = 'PNULL' if text == 'null' else 'PBOOL ' + text
    return node, typed, typed


def floating(bits):
    typed = 'PFLOAT ' + str(int(bits, 16))
    return 'NScalarFloat (FLOAT "' + bits + '") {metadata}', typed, typed


def string(text):
    payload = base64.b64encode(text.encode()).decode()
    raw = 'PSTRING ($ptascii("' + text + '"))'
    return ('NScalarString (BYTES "' + payload + '") {metadata}',
            'PSTRING_CARRIER INTERNED_STRING ($ptascii("' + text + '"))', raw)


def short(kind, left, right, skip, result):
    rows, codes, facts, expressions, values = [], [], [], [], []
    for side, (template, typed, pooled) in [('left', left), ('right', right)]:
        path, line = 'pcpath_value_' + side, 'z_value_' + side
        metadata = '([(MstartLine ' + line + ')])'
        expression = template.replace('{metadata}', metadata)
        rows += [(path, expression)]
        if expression.startswith('NExprConstFetch '):
            rows += [('(' + path + ' ++ [PCFIELD 0])',
                      expression[len('NExprConstFetch ('):].removesuffix(') ' + metadata))]
        if side == 'left' or not skip:
            codes += [(path, line, 'true')]
            facts += [(path, pooled)]
        expressions += [expression]
        values += [typed]
    expression = kind + ' (' + expressions[0] + ') (' + expressions[1] + ') metadata_value'
    line = 'z_value_left' if skip else 'z_value_right'
    state, function = scaffold.changed([('pcpath_value', expression), *rows],
        [('pcpath_value', line, 'true'), *codes], [('pcpath_value', result), *facts])
    return state, expression, function, expressions, values


def frontier(name, fixture, path):
    bindings, checks = current.frontier(name, fixture, path)
    bindings += ['$source_unit(S.SOURCES, n_cast_handler) = (pcunit_handler)',
                 '$pool_at(S.POOLS, n_cast_handler) = (ppool_handler)']
    nodes = current.nodes(name)
    expression, result = current.expression(name, 'value'), nodes['value'][3]
    if nodes['value_right'][4] is None:
        bindings += ['z_value_right = $source_line(metadata_value_right)']
    checks += [
        ('the exact selected short-circuit result is Boolean and nonowning',
         value('S', expression) + ' = (' + result + r') /\ $value_nodes(' + result + ') = eps'),
        ('a preset result cannot replace NORMAL source authority',
         value('S[.COMPLETION = BUDGET][.RESULT = KNOWN (' + result + ')]', expression) + ' = eps'),
        ('the selected handler retains its exact CODE unit and BODY',
         '~' + control.tail(function='pfunction_handler[.CODE.UNIT = $(n_cast_handler + 1)]') + CONJ +
         '~' + control.tail(function='pfunction_handler[.BODY = pfunction_handler.BODY ++ [PCINDEX 0]]'))]
    for key, node in nodes.items():
        source = ('S[.SOURCES = pcunit_handler[.OCCURRENCES = '
                  '$or131_drop(pcunit_handler.OCCURRENCES, pcpath_' + key + ')] :: S.SOURCES]')
        checks += [(key + ' retains its proper SOURCE even if skipped', '~' + control.tail(source))]
        if node[4] is None:
            for flag in ['true', 'false']:
                checks += [('a skipped operand cannot acquire CODE ' + flag,
                            '~' + control.tail(function=control.code_function('pcpath_' + key, 'z_value_left', flag)))]
            continue
        flag = 'true' if node[4] else 'false'
        for label, line, forged in [('line', '$(z_' + key + ' + 1)', flag),
                                    ('flag', 'z_' + key, 'false' if node[4] else 'true')]:
            checks += [(key + ' retains its exact CODE ' + label,
                        '~' + control.tail(function=control.code_function('pcpath_' + key, line, forged)))]
        if node[4]:
            state = ('S[.POOLS = ppool_handler[.CONSTANTS = '
                     '$or131_fact_drop(ppool_handler.CONSTANTS, pcpath_' + key + ')] :: S.POOLS]')
            checks += [(key + ' retains its own folded pool fact', '~' + control.tail(state)),
                       (key + ' cannot borrow an owning object fact',
                        '~' + control.tail(control.pool_state('pcpath_' + key, 'POBJECT 0')))]
    source = ('S[.SOURCES = pcunit_handler[.OCCURRENCES = '
              '$or131_drop(pcunit_handler.OCCURRENCES, pcpath_value_left ++ [PCFIELD 0])] :: S.SOURCES]')
    checks += [('the literal left name retains its own source child', '~' + control.tail(source))]
    for key in ['value', 'value_left', 'value_right']:
        code = ('pfunction_handler.CODE[.EXPRESSIONS = (CODEEFFECT pcpath_' + key +
                ') :: pfunction_handler.CODE.EXPRESSIONS]')
        state = 'S[.CODE = ' + code + ' :: S.CODE]'
        checks += [('a poisoned CODEEFFECT at ' + key + ' cannot enter a quiet short circuit',
                    '$compiled_effects(' + state + ', porigin_value) =/= eps' + CONJ +
                    value(state, expression) + ' = eps')]
    if nodes['value'][4]:
        checks += [('FALSE cannot be replaced by same-zero NULL or integer pool tags',
                    CONJ.join(value(control.pool_state('pcpath_value', forged), expression) + ' = eps'
                              for forged in ['PNULL', 'PINT 0', 'PBOOL true']))]
        code = ('pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR pcpath_value z_value false) :: '
                'pfunction_handler.CODE.EXPRESSIONS]')
        checks += [('an unread global pool cannot replace actual folded-root authority',
                    value('S[.CODE = ' + code + ' :: S.CODE]', expression) + ' = eps')]
        poisoned = control.pool_state('pcpath_value_right', 'POBJECT 0')
        checks += [('an uncompiled RHS ignores an unread forged owning pool instead of evaluating it',
                    '$compiled_read(' + poisoned + ', porigin_value_right) = eps' + CONJ +
                    value(poisoned, expression) + ' = (' + result + ')')]
    else:
        checks += [('an emitted root ignores an unread pool without borrowing a folded result',
                    value(control.pool_state('pcpath_value', 'POBJECT 0'), expression) + ' = (' + result + ')')]
        code = ('pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR pcpath_value z_value true) :: '
                'pfunction_handler.CODE.EXPRESSIONS]')
        state = control.pool_state('pcpath_value', result) + '[.CODE = ' + code + ' :: S.CODE]'
        checks += [('an exact forged global read cannot replace emitted read-eps authority',
                    '$compiled_read(' + state + ', porigin_value) = (' + result + ')' + CONJ +
                    value(state, expression) + ' = eps')]
        for target, flag in [('pcpath_value_left', 'true'), ('pcpath_value_right', 'false')]:
            code = ('pfunction_handler.CODE[.REDIRECTS = (CODEREDIRECT pcpath_value ' + target + ' ' + flag +
                    ') :: pfunction_handler.CODE.REDIRECTS]')
            checks += [('an emitted root retains its exact selected RHS and Boolean redirect',
                        value('S[.CODE = ' + code + ' :: S.CODE]', expression) + ' = eps')]
    bare = 'NStmtReturn (' + expression + ') metadata_cast_return'
    single = nodes['cast_1'][0] + ' (' + expression + ') metadata_cast_1'
    statement = 'NStmtReturn (' + single + ') metadata_cast_return'
    checks += [('a helper Boolean cannot bypass the existing two-cast handler gate',
                '~' + control.tail(control.source_state([('pcpath_cast_return', bare)]), statement=bare) + CONJ +
                '~' + control.tail(control.source_state([('pcpath_cast_return', statement), ('pcpath_cast', single)]), statement=statement))]
    if current.DETAILS[name][1] == 'and-skip':
        for kind, b_or in [('NExprBinaryOpBooleanAnd', False), ('NExprBinaryOpLogicalAnd', False),
                           ('NExprBinaryOpBooleanOr', True), ('NExprBinaryOpLogicalOr', True)]:
            for skip in [True, False]:
                left = keyword(str(b_or if skip else not b_or).lower())
                for right in [keyword('false'), keyword('true'), keyword('null'),
                              string(''), string('0'), string('00'), floating('8000000000000000'),
                              floating('7ff0000000000000')]:
                    truth = right[1] not in ['PBOOL false', 'PNULL',
                        'PSTRING_CARRIER INTERNED_STRING ($ptascii(""))',
                        'PSTRING_CARRIER INTERNED_STRING ($ptascii("0"))', 'PFLOAT 9223372036854775808']
                    result = 'PBOOL ' + str(b_or if skip else truth).lower()
                    state, expr, function, children, values = short(kind, left, right, skip, result)
                    proof = [value(state, children[0], 'porigin_value_left', function) + ' = (' + values[0] + ')',
                             value(state, expr, function=function) + ' = (' + result + ')']
                    if not skip:
                        proof.insert(1, value(state, children[1], 'porigin_value_right', function) + ' = (' + values[1] + ')')
                    checks += [('source0 four short-circuit shapes distinguish skipped and selected scalar truth', CONJ.join(proof))]
        state, expr, function, _, _ = short('NExprBinaryOpBooleanAnd', keyword('true'), keyword('false'), False, 'PBOOL false')
        state, expr, function = [part.replace('z_value_right', '$(z_value_right + 3)') for part in [state, expr, function]]
        wrong = function + '[.CODE.EXPRESSIONS = (CODEEXPR pcpath_value z_value_left true) :: ' + function + '.CODE.EXPRESSIONS]'
        checks += [('source0 a multiline selected RHS supplies the parent line independently of the LEFT',
                    value(state, expr, function=function) + ' = (PBOOL false)' + CONJ +
                    value(state, expr, function=wrong) + ' = eps')]
        for bits in ['7ff8000000000001', '7ff0000000000001']:
            nan = floating(bits)
            for left_nan in [False, True]:
                state, expr, function, children, values = short('NExprBinaryOpBooleanAnd',
                    nan if left_nan else keyword('true'), keyword('true') if left_nan else nan, False, 'PBOOL true')
                origin = 'porigin_value_left' if left_nan else 'porigin_value_right'
                child = children[0] if left_nan else children[1]
                index = len(bindings)
                masked = 'S_masked_' + str(index)
                bindings += [masked + ' = ' + state + '[.REPORTING = 0][.ERRORHANDLER = {CALLBACK eps, LEVELS 0}]'
                             '[.SOURCEPENDING = eps][.ERRORFATALTRACE = eps]']
                checks += [('source0 quiet and signaling NaN truth stay intrinsically refused under hidden diagnostics',
                    value(masked, child, origin, function) + ' = (' + nan[1] + ')' + CONJ +
                    '~$ob_object_cast_chain_quiet(CASTBOOL, ' + nan[1] + ')' + CONJ +
                    '$boolean_result(' + masked + '[.RESULT = KNOWN (' + nan[1] + ')], false, z_value_left) = ' +
                    masked + '[.RESULT = KNOWN (PBOOL true)]' + CONJ +
                    value(masked, expr, function=function) + ' = eps')]
            state, expr, function, _, _ = short('NExprBinaryOpBooleanAnd', keyword('false'), nan, True, 'PBOOL false')
            checks += [('source0 a genuinely pruned NaN RHS is not a demanded NaN coercion',
                        value(state, expr, function=function) + ' = (PBOOL false)')]
        for owned in ['POBJECT 0', 'PARRAY 0', 'PSTRING_CARRIER (REQUEST_STRING 0) ([48])']:
            checks += [('owning and request string operands cannot borrow scalar truth certification',
                        '~$ob_object_cast_chain_quiet(CASTBOOL, ' + owned + ')')]
        left = 'NExprCastBool (NScalarFloat (FLOAT "0000000000000000") metadata_value_right) metadata_cast_1'
        right = current.expression(name, 'value_right')
        expr = 'NExprBinaryOpBooleanAnd (' + left + ') (' + right + ') metadata_value'
        state, function = scaffold.changed([('pcpath_value', expr), ('pcpath_value_left', left),
            ('(pcpath_value_left ++ [PCFIELD 0])', 'NScalarFloat (FLOAT "0000000000000000") metadata_value_right')],
            [('pcpath_value', 'z_value_left', 'false'), ('pcpath_value_left', 'z_value_right', 'false'),
             ('(pcpath_value_left ++ [PCFIELD 0])', '$source_line(metadata_value_right)', 'true')],
            [('(pcpath_value_left ++ [PCFIELD 0])', 'PFLOAT 0')])
        checks += [('source0 an authenticated emitted LEFT remains outside the constant-left contour',
                    value(state, left, 'porigin_value_left', function) + ' = (PBOOL false)' + CONJ +
                    value(state, expr, function=function) + ' = eps')]
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = current.lifecycle(name, fixture, path)
    checks += [('the exact Boolean and nested scalar casts survive actual formal/native-cell retirement',
                'S_handler.RESULT = KNOWN (' + current.root_value(name) + r') /\ S.RESULT = KNOWN PNULL /\ ' +
                value('S', current.expression(name), 'porigin_cast') + ' = (' + current.root_value(name) + ')')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
