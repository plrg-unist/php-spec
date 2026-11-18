#!/usr/bin/env python3
"""Independent emitted-char tags, string arena, authority and retirement checks."""
import base64
import output_final_selected_constant_float_cast_return_modulo_error_review_state as control
import output_final_selected_recursive_numeric_sign_cast_chain_return_modulo_error_review_state as scaffold
import output_final_selected_emitted_byte_bitnot_cast_chain_return_modulo_error_state as current

runner, CONJ = current.runner, current.CONJ
PREFIX = current.PREFIX + scaffold.PREFIX[len(scaffold.current.PREFIX):]
CASES = {name: current.sources.CASES['native-selected-emitted-byte-bitnot-cast-chain-return-modulo-error-' + name]
         for name in ['deprecated-both-cv-pair-coalesce-null-nul', 'warning-right-cv-pair-shorthand-true']}


def value(state, expression, origin='porigin_value', function='pfunction_handler'):
    return scaffold.value(state, expression, origin, function)


def data(raw):
    return '$base64("' + base64.b64encode(raw).decode() + '")'


def plain(raw):
    return 'PSTRING (' + data(raw) + ')'


def byte_not(raw, folded=False):
    line = '$(z_value_child + 13)'
    metadata = '([(MstartLine ' + line + ')])'
    leaf = 'NScalarString (BYTES "' + base64.b64encode(raw).decode() + '") ' + metadata
    complement = bytes(255 - byte for byte in raw)
    if folded:
        child = leaf
        rows = [('pcpath_value_child', leaf)]
        codes = [('pcpath_value_child', line, 'true')]
        facts = [('pcpath_value_child', plain(raw)), ('pcpath_value', plain(complement))]
    else:
        name = 'NName (BYTES "bnVsbA==") metadata_value'
        left = 'NExprConstFetch (' + name + ') metadata_value'
        child = 'NExprBinaryOpCoalesce (' + left + ') (' + leaf + ') metadata_value'
        left_path, right_path = '(pcpath_value_child ++ [PCFIELD 0])', '(pcpath_value_child ++ [PCFIELD 1])'
        rows = [('pcpath_value_child', child), (left_path, left), (right_path, leaf),
                ('(' + left_path + ' ++ [PCFIELD 0])', name)]
        codes = [('pcpath_value_child', line, 'false'), (left_path, '$source_line(metadata_value)', 'true'),
                 (right_path, line, 'true')]
        facts = [(left_path, 'PNULL'), (right_path, plain(raw))]
    expression = 'NExprBitwiseNot (' + child + ') metadata_value'
    rows.insert(0, ('pcpath_value', expression))
    codes.insert(0, ('pcpath_value', line, str(folded).lower()))
    state, function = scaffold.changed(rows, codes, facts)
    return state, expression, function, current.string(raw), complement


def frontier(name, fixture, path):
    bindings, checks = current.frontier(name, fixture, path)
    bindings += ['$source_unit(S.SOURCES, n_cast_handler) = (pcunit_handler)',
                 '$pool_at(S.POOLS, n_cast_handler) = (ppool_handler)']
    tree = current.nodes(name)
    expression, result = current.expression(name, 'value'), tree['value'][3]
    input_value = tree['value_child'][3]
    checks += [('the real emitted result is an interned char with the entire string arena unchanged',
                value('S', expression) + ' = (' + result + ')' + CONJ + '$string_carrier_valid(S, ' + result + ')' + CONJ +
                '$bitnot_apply(S[.RESULT = KNOWN (' + input_value + ')], ' + input_value + ', z_value) = S[.RESULT = KNOWN (' + result + ')]'),
               ('NORMAL and exact handler CODE unit/body remain required',
                value('S[.COMPLETION = BUDGET][.RESULT = KNOWN (' + result + ')]', expression) + ' = eps' + CONJ +
                '~' + control.tail(function='pfunction_handler[.CODE.UNIT = $(n_cast_handler + 1)]') + CONJ +
                '~' + control.tail(function='pfunction_handler[.BODY = pfunction_handler.BODY ++ [PCINDEX 0]]'))]
    for key, node in tree.items():
        if node[0] == 'absent':
            checks += [('ABSENT TRUE retains empty SOURCE and both CODE alternatives are refused',
                        value(control.source_state([('pcpath_' + key, 'NScalarString (BYTES "QQ==") metadata_value')]), expression) + ' = eps' + CONJ +
                        value('S', expression, function=control.code_function('pcpath_' + key, 'z_value_child', 'true')) + ' = eps' + CONJ +
                        value('S', expression, function=control.code_function('pcpath_' + key, 'z_value_child', 'false')) + ' = eps')]
            continue
        state = ('S[.SOURCES = pcunit_handler[.OCCURRENCES = '
                 '$or131_drop(pcunit_handler.OCCURRENCES, pcpath_' + key + ')] :: S.SOURCES]')
        checks += [(key + ' retains its own SOURCE even when skipped', '~' + control.tail(state))]
        for label, line, flag in [('line', '$(z_' + key + ' + 1)', str(node[4]).lower()),
                                  ('flag', 'z_' + key, str(not node[4]).lower())]:
            checks += [(key + ' retains its compiler ' + label,
                        '~' + control.tail(function=control.code_function('pcpath_' + key, line, flag)))]
        if node[4]:
            state = ('S[.POOLS = ppool_handler[.CONSTANTS = '
                     '$or131_fact_drop(ppool_handler.CONSTANTS, pcpath_' + key + ')] :: S.POOLS]')
            checks += [(key + ' cannot borrow a missing or owning folded fact',
                        '~' + control.tail(state) + CONJ + '~' + control.tail(control.pool_state('pcpath_' + key, 'POBJECT 0')))]
        if node[0] == 'string':
            request = 'PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) (' + data(node[1]) + ')'
            state = control.pool_state('pcpath_' + key, request) + '[.STRINGDATA = S.STRINGDATA ++ [' + data(node[1]) + ']]'
            checks += [('a valid nonowning REQUEST identity cannot replace exact literal-pool authority',
                        '$value_nodes(' + request + ') = eps' + CONJ + '$string_carrier_valid(' + state + ', ' + request + ')' + CONJ + '~' + control.tail(state))]
    for key in ['value', 'value_child']:
        code = 'pfunction_handler.CODE[.EXPRESSIONS = (CODEEFFECT pcpath_' + key + ') :: pfunction_handler.CODE.EXPRESSIONS]'
        state = 'S[.CODE = ' + code + ' :: S.CODE]'
        checks += [('compiler effects at ' + key + ' remain refused even under diagnostic masks',
                    '$compiled_effects(' + state + ', porigin_value) =/= eps' + CONJ +
                    value(state, expression) + ' = eps' + CONJ + value(state + '[.REPORTING = 0]', expression) + ' = eps')]
    checks += [('an unread own pool cannot change the emitted char result',
                value(control.pool_state('pcpath_value', 'POBJECT 0'), expression) + ' = (' + result + ')')]
    code = 'pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR pcpath_value z_value true) :: pfunction_handler.CODE.EXPRESSIONS]'
    pooled = result.replace('PSTRING_CARRIER INTERNED_STRING', 'PSTRING')
    state = control.pool_state('pcpath_value', pooled) + '[.CODE = ' + code + ' :: S.CODE]'
    checks += [('even exact folded bytes cannot replace the emitted read-eps certificate',
                '$compiled_read(' + state + ', porigin_value) = (' + pooled + ')' + CONJ + value(state, expression) + ' = eps')]
    for flag in ['false', 'true']:
        code = 'pfunction_handler.CODE[.REDIRECTS = (CODEREDIRECT pcpath_value pcpath_value_child ' + flag + ') :: pfunction_handler.CODE.REDIRECTS]'
        checks += [('an emitted NOT cannot borrow a child redirect', value('S[.CODE = ' + code + ' :: S.CODE]', expression) + ' = eps')]
    for other in [pooled, 'PBOOL false', 'PNULL', 'PINT 0']:
        checks += [('equal outer-cast bits retain the actual interned STRING tag', value('S', expression) + ' =/= (' + other + ')')]
    bare = 'NStmtReturn (' + expression + ') metadata_cast_return'
    single = 'NExprCastInt (' + expression + ') metadata_cast_1'
    statement = 'NStmtReturn (' + single + ') metadata_cast_return'
    checks += [('emitted chars do not bypass the existing two-cast handler gate',
                '~' + control.tail(control.source_state([('pcpath_cast_return', bare)]), statement=bare) + CONJ +
                '~' + control.tail(control.source_state([('pcpath_cast_return', statement), ('pcpath_cast', single)]), statement=statement))]
    if name.endswith('coalesce-null-nul'):
        for byte in [1, 48, 49, 65, 127, 128, 198, 206, 207, 254, 255]:
            state, expr, function, operand, output = byte_not(bytes([byte]))
            char = current.string(output)
            integer = output[0] - 48 if 48 <= output[0] <= 57 else 0
            checks += [('source0 emitted single-byte complements preserve char identity and quiet integer conversion',
                        value(state, expr, function=function) + ' = (' + char + ')' + CONJ +
                        '$bitnot_apply(S[.RESULT = KNOWN (' + operand + ')], ' + operand + ', z_value_child) = S[.RESULT = KNOWN (' + char + ')]' + CONJ +
                        '$cast_apply(S[.RESULT = KNOWN (' + char + ')], CASTINT, ' + char + ', z_value_child) = S[.RESULT = KNOWN (PINT ' + str(integer) + ')]')]
        for raw in [b'', b'00', b'abc']:
            state, expr, function, operand, output = byte_not(raw)
            request = 'PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) (' + data(output) + ')'
            call = '$bitnot_apply(S[.RESULT = KNOWN (' + operand + ')], ' + operand + ', z_value_child)'
            checks += [('source0 zero/multiple-byte results allocate string metadata despite having no heap owner',
                        call + ' = S[.STRINGDATA = S.STRINGDATA ++ [' + data(output) + ']][.RESULT = KNOWN (' + request + ')]' + CONJ +
                        '$value_nodes(' + request + ') = eps' + CONJ + call + ' =/= S[.RESULT = KNOWN (' + request + ')]' + CONJ +
                        value(state, expr, function=function) + ' = eps')]
        for raw in [b'0', b'\xff']:
            state, expr, function, _, output = byte_not(raw, True)
            checks += [('source0 folded STRING NOT keeps its old raw pooled result disjoint from emitted chars',
                        value(state, expr, function=function) + ' = (' + plain(output) + ')' + CONJ +
                        value(state, expr, function=function) + ' =/= (' + current.string(output) + ')')]
        for folded in [False, True]:
            state, expr, function, _, _ = byte_not(b'\0', folded)
            checks += [('source0 the original literal-NUL source fence is unchanged', value(state, expr, function=function) + ' = eps')]
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = current.lifecycle(name, fixture, path)
    checks += [('real formal/native-cell retirement preserves the exact char subtree and rounded handler result',
                'S_handler.RESULT = KNOWN (' + current.root_value(name) + ')' + CONJ + 'S.RESULT = KNOWN PNULL' + CONJ +
                value('S', current.expression(name, 'value')) + ' = (' + current.nodes(name)['value'][3] + ')')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
