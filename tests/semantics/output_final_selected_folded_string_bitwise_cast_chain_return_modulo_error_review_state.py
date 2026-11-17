#!/usr/bin/env python3
"""Independent folded STRING bytes, producer identities and retirement fences."""
import output_final_selected_folded_string_bitwise_cast_chain_return_modulo_error_state as current
import output_final_selected_folded_string_bitwise_cast_chain_return_modulo_error_sources as sources
CASES = {name: sources.CASES['native-selected-folded-string-bitwise-cast-chain-return-modulo-error-' + name]
         for name in ['warning-right-cv-pair-single-or-three', 'deprecated-both-cv-pair-single-xor-nul',
                      'warning-deprecated-constant-float-nested-or-thirty']}
shared = current.current
adapter_fields = ('DETAILS', 'TREES', 'modulo_line', 'converted', 'expression', 'return_proof')
pristine_adapter = tuple(getattr(shared, field) for field in adapter_fields)
import output_final_selected_terminal_line_bitwise_cast_chain_return_modulo_error_review_state as base
import output_final_selected_primitive_integer_cast_chain_return_modulo_error_review_state as old143
for field, original in zip(adapter_fields, pristine_adapter):
    setattr(shared, field, original)

control, scaffold = base.control, base.scaffold
runner, PREFIX, CONJ = current.runner, scaffold.PREFIX, current.CONJ
value, binary, string = old143.value, old143.binary, old143.string


def data(raw):
    return '[' + ', '.join(map(str, raw)) + ']' if raw else 'eps'


def plain(raw):
    return 'PSTRING (' + data(raw) + ')'


def compiled_proof(query, left, right, result, admitted=True):
    state, expression, function, operator, children, values = query
    typed = plain(result)
    parts = [value(state, child, 'PORIGIN n_cast_handler pcpath_value_' + side, function) + ' = (' + expected + ')'
             for side, child, expected in zip(['left', 'right'], children, values)]
    parts += ['$byte_binary(' + operator + ', (' + data(left) + '), (' + data(right) + ')) = (' + data(result) + ')']
    if admitted:
        parts += ['$compiled_read(' + state + ', porigin_value) = (' + typed + ')',
                  '$compiled_effects(' + state + ', porigin_value) = eps',
                  '$compiled_string_value(' + state + ', porigin_value, ' + typed + ') = ' + typed,
                  '$enter_compiled_task(' + state + ', porigin_value, EVAL (' + expression + '), ' + state + '.TODO) = ' + state + '[.RESULT = KNOWN (' + typed + ')]']
    parts += [value(state, expression, function=function) + (' = (' + typed + ')' if admitted else ' = eps')]
    return CONJ.join(parts)


def runtime_proof(query, left, right, result):
    state, expression, function, operator, children, values = query
    call = '$binary_apply(' + state + '[.RESULT = KNOWN (' + values[1] + ')], ' + operator + ', ' + values[0] + ', ' + values[1] + ', z_value_right)'
    if len(left) == len(right) == 1:
        typed = 'PSTRING_CARRIER INTERNED_STRING (' + data(result) + ')'
        expected = state + '[.RESULT = KNOWN (' + typed + ')]'
    else:
        typed = 'PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) (' + data(result) + ')'
        expected = state + '[.STRINGDATA = S.STRINGDATA ++ [(' + data(result) + ')]][.RESULT = KNOWN (' + typed + ')]'
    return call + ' = ' + expected


QUERIES = [
 ('and', b'3', b'1', b'1'), ('or', b'2', b'1', b'3'), ('xor', b'1', b'1', b'\0'),
 ('and', b'20', b'1', b'0'), ('and', b'1', b'20', b'0'),
 ('or', b'20', b'1', b'30'), ('or', b'1', b'20', b'30'), ('xor', b'11', b'2', b'\x03'),
 ('and', b'\xff', b'\x80', b'\x80'), ('or', b'\x80', b'\x01', b'\x81'), ('xor', b'\xff', b'\x80', b'\x7f'),
 ('and', b'', b'1', b''), ('or', b'', b'a', b'a'), ('xor', b'', b'11', b''),
 ('and', b'ab', b'Z0', b'@ '), ('or', b'ab', b'Z', b'{b'), ('xor', b'ab', b'Z', b';')]


def frontier(name, fixture, path):
    bindings, checks = base.frontier(name, fixture, path)
    checks = [(label.replace('multiline', 'folded STRING'), condition) for label, condition in checks]
    nodes = current.nodes(name)
    expression, result = current.expression(name, 'value'), nodes['value'][3]
    checks += [('the actual folded subtree loads plain PSTRING without allocating request data',
                CONJ.join([value('S', expression) + ' = (' + result + ')',
                           '$compiled_string_value(S, porigin_value, ' + result + ') = ' + result,
                           '$enter_compiled_task(S, porigin_value, EVAL (' + expression + '), S.TODO) = S[.RESULT = KNOWN (' + result + ')]']))]
    for key, node in nodes.items():
        if node[3].startswith('PSTRING ') and len(node[5]) == 2:
            for wrong in ['PINT 0', 'PBOOL true', 'PSTRING_CARRIER INTERNED_STRING ' + node[3].removeprefix('PSTRING '),
                          'PSTRING ([255, 255, 255])']:
                checks += [('the folded STRING at ' + key + ' retains its own plain tag and exact byte fact',
                            '~' + control.tail(control.pool_state('pcpath_' + key, wrong)))]
    effect_code = 'pfunction_handler.CODE[.EXPRESSIONS = (CODEEFFECT pcpath_value_left) :: pfunction_handler.CODE.EXPRESSIONS]'
    effect_state = 'S[.CODE = ' + effect_code + ' :: S.CODE]'
    checks += [('an attached compiler effect cannot be discarded by an otherwise exact folded STRING fact',
                '$compiled_effects(' + effect_state + ', porigin_value) =/= eps /\\ ' + value(effect_state, expression) + ' = eps')]
    unread = 'S[.CODE = pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR pcpath_value z_value false) :: pfunction_handler.CODE.EXPRESSIONS] :: S.CODE]'
    checks += [('an unread own pool cannot replace the global folded CODE certificate',
                '$compiled_read(' + unread + ', porigin_value) = eps /\\ ' + value(unread, expression) + ' = eps')]
    if current.DETAILS[name][1] == 'single-or-three':
        for kind, left, right, answer in QUERIES:
            query = binary(kind, string(left), string(right), plain(answer))
            checks += [('source0 ' + kind + ' preserves exact folded bytes, length and source-owned plain pool identity',
                        compiled_proof(query, left, right, answer)),
                       ('source0 runtime ' + kind + ' retains its distinct BOTH-length1 or REQUEST/STRINGDATA producer',
                        runtime_proof(query, left, right, answer))]
        for kind, left, right, answer in QUERIES[:3]:
            for wrong in ['PINT 1', 'PBOOL true', 'PSTRING_CARRIER INTERNED_STRING (' + data(answer) + ')', plain(b'wrong')]:
                checks += [('source0 exact bytes cannot authenticate another tag, identity or wrong folded STRING',
                            compiled_proof(binary(kind, string(left), string(right), wrong), left, right, answer, False))]
        # Precisely the three affected old143 factories; keep runtime and compiled results distinct.
        for kind, left, right, answer in [('and', b'3', b'1', b'1'), ('or', b'2', b'1', b'3'), ('xor', b'3', b'1', b'\x02')]:
            query = old143.binary(kind, old143.string(left), old143.string(right), plain(answer))
            checks += [('source0 actual old143 ' + kind + ' builder now admits plain compiled STRING while preserving runtime carrier',
                        compiled_proof(query, left, right, answer) + CONJ + runtime_proof(query, left, right, answer))]
        for raw, truth, number in [(b'\0', True, 0), (b'', False, 0), (b'0', False, 0), (b'30', True, 30)]:
            typed = plain(raw)
            checks += [('source0 NUL, empty, zero-text and numeric STRING keep distinct truth and quiet explicit INT casts',
                        CONJ.join(['$ob_object_cast_chain_quiet(CASTBOOL, ' + typed + ')',
                                   '$ob_object_cast_chain_quiet(CASTINT, ' + typed + ')',
                                   '$ob_object_cast_chain_quiet(CASTFLOAT, ' + typed + ')',
                                   '$cast_apply(S, CASTBOOL, ' + typed + ', z_value) = S[.RESULT = KNOWN (PBOOL ' + str(truth).lower() + ')]',
                                   '$cast_apply(S, CASTINT, ' + typed + ', z_value) = S[.RESULT = KNOWN (PINT ' + str(number) + ')]']))]
        query = binary('and', string('3'), string('1'), plain(b'1'))
        state, expr, function, operator, children, values = query
        emitted = function + '[.CODE.EXPRESSIONS = (CODEEXPR pcpath_value z_value_right false) :: ' + function + '.CODE.EXPRESSIONS]'
        emitted_state = state + '[.CODE = ' + emitted + '.CODE :: ' + state + '.CODE]'
        checks += [('source0 an emitted read-eps node cannot borrow the folded-only STRING rule',
                    '$compiled_read(' + emitted_state + ', porigin_value) = eps /\\ ' + value(emitted_state, expr, function=emitted) + ' = eps')]
        concat_state, concat_expr, concat_function = [part.replace('NExprBinaryOpBitwiseAnd', 'NExprBinaryOpConcat') for part in [state, expr, function]]
        checks += [('source0 CONCAT remains outside this folded BIT3 producer rule',
                    value(concat_state, concat_expr, function=concat_function) + ' = eps')]
        for leaf in [string(b'\0'), (*string('1')[:2], 'PSTRING_CARRIER (REQUEST_STRING 0) ([49])')]:
            state, expr, function, operator, children, values = binary('xor', leaf, string('1'), plain(b'\0'))
            checks += [('source0 literal NUL and REQUEST-tagged forged leaves retain their prior source/identity fences',
                        value(state, children[0], 'PORIGIN n_cast_handler pcpath_value_left', function) + ' = eps /\\ ' + value(state, expr, function=function) + ' = eps')]
        for wrong in ['PARRAY 0', 'POBJECT 0']:
            leaf = (string('1')[0], wrong, wrong)
            state, expr, function, operator, children, values = binary('and', leaf, string('1'), plain(b'1'))
            checks += [('source0 an owning child cannot borrow folded STRING authority',
                        '$value_nodes(' + wrong + ') =/= eps /\\ ' + value(state, children[0], 'PORIGIN n_cast_handler pcpath_value_left', function) + ' = eps /\\ ' + value(state, expr, function=function) + ' = eps')]
        checks += [('source0 REQUEST identity is not admitted by the new plain-STRING quiet-cast gate',
                    CONJ.join('~$ob_object_cast_chain_quiet(' + cast + ', PSTRING_CARRIER (REQUEST_STRING 0) ([49]))'
                              for cast in ['CASTINT', 'CASTBOOL', 'CASTFLOAT']))]
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = base.lifecycle(name, fixture, path)
    checks += [('plain folded STRING and both scalar casts survive actual formal/native-cell retirement',
                CONJ.join(['S_handler.RESULT = KNOWN (' + current.root_value(name) + ')', 'S.RESULT = KNOWN PNULL',
                           value('S', current.expression(name, 'value')) + ' = (' + current.nodes(name)['value'][3] + ')']))]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
