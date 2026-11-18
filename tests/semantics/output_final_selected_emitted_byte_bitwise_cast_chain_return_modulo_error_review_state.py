#!/usr/bin/env python3
"""Independent byte binary tags, input lengths, compiler authority and retirement."""
import base64
import output_final_selected_constant_float_cast_return_modulo_error_review_state as control
import output_final_selected_recursive_numeric_sign_cast_chain_return_modulo_error_review_state as scaffold
import output_final_selected_emitted_byte_bitwise_cast_chain_return_modulo_error_state as current

runner, CONJ = current.runner, current.CONJ
PREFIX = current.PREFIX + scaffold.PREFIX[len(scaffold.current.PREFIX):]
CASES = {name: current.sources.CASES['native-selected-emitted-byte-bitwise-cast-chain-return-modulo-error-' + name]
         for name in ['warning-left-constant-or-right-overlap', 'deprecated-both-cv-pair-xor-both-selections-nul']}


def value(state, expression, origin='porigin_value', function='pfunction_handler'):
    return scaffold.value(state, expression, origin, function)


def data(raw):
    return '$base64("' + base64.b64encode(raw).decode() + '")'


def plain(raw):
    return 'PSTRING (' + data(raw) + ')'


def byte_result(kind, left, right):
    operation = {'BITAND': lambda a, b: a & b, 'BITOR': lambda a, b: a | b, 'BITXOR': lambda a, b: a ^ b}[kind]
    result = bytes(operation(a, b) for a, b in zip(left, right))
    return result + (left if len(left) >= len(right) else right)[len(result):] if kind == 'BITOR' else result


def synthetic(tree, force_emitted=False):
    rows, codes, facts = [], [], []

    def visit(path, node, line, root=False):
        if isinstance(node, bytes):
            expression = 'NScalarString (BYTES "' + base64.b64encode(node).decode() + '") ([(MstartLine ' + line + ')])'
            typed, raw, folded = current.string(node), node, True
            facts.append((path, plain(raw)))
        elif node[0] == 'select':
            raw = node[1]
            left_path, right_path = '(' + path + ' ++ [PCFIELD 0])', '(' + path + ' ++ [PCFIELD 1])'
            name = 'NName (BYTES "bnVsbA==") metadata_value'
            left = 'NExprConstFetch (' + name + ') metadata_value'
            rows.extend([(left_path, left), ('(' + left_path + ' ++ [PCFIELD 0])', name)])
            codes.append((left_path, '$source_line(metadata_value)', 'true'))
            facts.append((left_path, 'PNULL'))
            right, typed, _, _, _ = visit(right_path, raw, line)
            expression = 'NExprBinaryOpCoalesce (' + left + ') (' + right + ') metadata_value'
            folded = False
        else:
            kind, left, right = node
            left_expr, left_value, left_raw, left_folded, _ = visit('(' + path + ' ++ [PCFIELD 0])', left, '$(z_value_left + 17)')
            right_expr, right_value, right_raw, right_folded, line = visit('(' + path + ' ++ [PCFIELD 1])', right, '$(z_value_right + 23)')
            raw = byte_result(kind, left_raw, right_raw)
            folded = left_folded and right_folded and not (root and force_emitted)
            typed = plain(raw) if folded else current.string(raw)
            constructor = {'BITAND': 'NExprBinaryOpBitwiseAnd', 'BITOR': 'NExprBinaryOpBitwiseOr', 'BITXOR': 'NExprBinaryOpBitwiseXor'}[kind]
            expression = constructor + ' (' + left_expr + ') (' + right_expr + ') metadata_value'
            if folded:
                facts.append((path, plain(raw)))
            if root:
                operands.extend([kind, left_value, right_value, line])
        rows.append((path, expression))
        codes.append((path, line, str(folded).lower()))
        return expression, typed, raw, folded, line

    operands = []
    expression, typed, raw, _, _ = visit('pcpath_value', tree, 'z_value', True)
    state, function = scaffold.changed(rows, codes, facts)
    return state, expression, function, operands, raw, typed


def frontier(name, fixture, path):
    bindings, checks = current.frontier(name, fixture, path)
    bindings += ['$source_unit(S.SOURCES, n_cast_handler) = (pcunit_handler)',
                 '$pool_at(S.POOLS, n_cast_handler) = (ppool_handler)']
    tree = current.nodes(name)
    expression, result = current.expression(name, 'value'), tree['value'][3]
    kind, left, right = tree['value'][1], tree['value_left'][3], tree['value_right'][3]
    checks += [('the actual binary result is an interned char and leaves all string storage unchanged',
                value('S', expression) + ' = (' + result + ')' + CONJ + '$string_carrier_valid(S, ' + result + ')' + CONJ +
                '$binary_apply(S[.RESULT = KNOWN (' + right + ')], ' + kind + ', ' + left + ', ' + right + ', z_value) = S[.RESULT = KNOWN (' + result + ')]'),
               ('NORMAL and exact handler CODE unit/body remain required',
                value('S[.COMPLETION = BUDGET]', expression) + ' = eps' + CONJ +
                '~' + control.tail(function='pfunction_handler[.CODE.UNIT = $(n_cast_handler + 1)]') + CONJ +
                '~' + control.tail(function='pfunction_handler[.BODY = pfunction_handler.BODY ++ [PCINDEX 0]]'))]
    for key, node in tree.items():
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
            checks += [('a valid nonowning REQUEST cannot replace a literal-pool identity',
                        '$value_nodes(' + request + ') = eps' + CONJ + '$string_carrier_valid(' + state + ', ' + request + ')' + CONJ + '~' + control.tail(state))]
    for key in ['value', 'value_left', 'value_right']:
        code = 'pfunction_handler.CODE[.EXPRESSIONS = (CODEEFFECT pcpath_' + key + ') :: pfunction_handler.CODE.EXPRESSIONS]'
        state = 'S[.CODE = ' + code + ' :: S.CODE]'
        checks += [('complete subtree effects at ' + key + ' cannot disappear under reporting masks',
                    '$compiled_effects(' + state + ', porigin_value) =/= eps' + CONJ +
                    value(state, expression) + ' = eps' + CONJ + value(state + '[.REPORTING = 0]', expression) + ' = eps')]
    checks += [('an unread own pool cannot change the emitted result',
                value(control.pool_state('pcpath_value', 'POBJECT 0'), expression) + ' = (' + result + ')')]
    pooled = result.replace('PSTRING_CARRIER INTERNED_STRING', 'PSTRING')
    code = 'pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR pcpath_value z_value true) :: pfunction_handler.CODE.EXPRESSIONS]'
    state = control.pool_state('pcpath_value', pooled) + '[.CODE = ' + code + ' :: S.CODE]'
    checks += [('an exact folded root fact cannot replace emitted child authority',
                '$compiled_read(' + state + ', porigin_value) = (' + pooled + ')' + CONJ + value(state, expression) + ' = eps')]
    for side in ['left', 'right']:
        for flag in ['false', 'true']:
            code = 'pfunction_handler.CODE[.REDIRECTS = (CODEREDIRECT pcpath_value pcpath_value_' + side + ' ' + flag + ') :: pfunction_handler.CODE.REDIRECTS]'
            checks += [('neither operand redirect can replace the binary operation', value('S[.CODE = ' + code + ' :: S.CODE]', expression) + ' = eps')]
    for other in [pooled, 'PBOOL false', 'PNULL', 'PINT 0', current.string(b'0' if name.endswith('-nul') else b'2')]:
        checks += [('equal outer numbers retain exact raw bytes and the INTERNED STRING tag', value('S', expression) + ' =/= (' + other + ')')]
    bare = 'NStmtReturn (' + expression + ') metadata_cast_return'
    single = 'NExprCastInt (' + expression + ') metadata_cast_1'
    statement = 'NStmtReturn (' + single + ') metadata_cast_return'
    checks += [('emitted byte binaries retain the existing two-cast handler gate',
                '~' + control.tail(control.source_state([('pcpath_cast_return', bare)]), statement=bare) + CONJ +
                '~' + control.tail(control.source_state([('pcpath_cast_return', statement), ('pcpath_cast', single)]), statement=statement))]
    if name.endswith('-nul'):
        pairs = [(b'3', b'1'), (b'q', b'A'), (b'q', b'H'), (b'0', b'0'), (b'\xff', b'\x80'), (b'\x7f', b'\xfe'), (b'\x80', b'\xff')]
        for kind in ['BITAND', 'BITOR', 'BITXOR']:
            for index, (left, right) in enumerate(pairs):
                operands = [('select', left) if index % 3 != 1 else left, ('select', right) if index % 3 != 0 else right]
                state, expr, function, (_, a, b, line), output, typed = synthetic((kind, *operands))
                integer = output[0] - 48 if 48 <= output[0] <= 57 else 0
                checks += [('source0 single-byte operands preserve exact ' + kind + ' bits, char identity and quiet INT conversion',
                            value(state, expr, function=function) + ' = (' + typed + ')' + CONJ +
                            '$binary_apply(S[.RESULT = KNOWN (' + b + ')], ' + kind + ', ' + a + ', ' + b + ', ' + line + ') = S[.RESULT = KNOWN (' + typed + ')]' + CONJ +
                            '$cast_apply(S[.RESULT = KNOWN (' + typed + ')], CASTINT, ' + typed + ', ' + line + ') = S[.RESULT = KNOWN (PINT ' + str(integer) + ')]')]
            for left, right in [(b'0', b'00'), (b'00', b'0'), (b'', b'1'), (b'1', b''), (b'12', b'34')]:
                state, expr, function, (_, a, b, line), output, _ = synthetic((kind, ('select', left), right))
                request = 'PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) (' + data(output) + ')'
                call = '$binary_apply(S[.RESULT = KNOWN (' + b + ')], ' + kind + ', ' + a + ', ' + b + ', ' + line + ')'
                checks += [('source0 unequal or empty inputs allocate even when the result has one byte and no heap owner',
                            call + ' = S[.STRINGDATA = S.STRINGDATA ++ [' + data(output) + ']][.RESULT = KNOWN (' + request + ')]' + CONJ +
                            '$value_nodes(' + request + ') = eps' + CONJ + call + ' =/= S[.RESULT = KNOWN (' + request + ')]' + CONJ +
                            value(state, expr, function=function) + ' = eps')]
            state, expr, function, _, output, _ = synthetic((kind, b'3', b'1'))
            checks += [('source0 old folded STRING bytes retain the plain pooled result',
                        value(state, expr, function=function) + ' = (' + plain(output) + ')' + CONJ +
                        value(state, expr, function=function) + ' =/= (' + current.string(output) + ')')]
            state, expr, function, _, _, _ = synthetic((kind, b'3', b'1'), force_emitted=True)
            checks += [('source0 both folded children cannot authenticate a forged emitted root', value(state, expr, function=function) + ' = eps')]
            state, expr, function, _, _, _ = synthetic((kind, ('select', b'\0'), b'1'))
            checks += [('source0 literal-source NUL retains its existing refusal', value(state, expr, function=function) + ' = eps')]
        state, expr, function, _, _, typed = synthetic(('BITOR', ('BITXOR', ('select', b'q'), b'A'), b'1'))
        checks += [('source0 a recursively certified emitted binary child feeds another emitted char binary', value(state, expr, function=function) + ' = (' + typed + ')')]
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = current.lifecycle(name, fixture, path)
    checks += [('real formal/native-cell retirement preserves both exact raw STRING and separate rounded return',
                'S_handler.RESULT = KNOWN (' + current.root_value(name) + ')' + CONJ + 'S.RESULT = KNOWN PNULL' + CONJ +
                value('S', current.expression(name, 'value')) + ' = (' + current.nodes(name)['value'][3] + ')')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
