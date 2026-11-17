#!/usr/bin/env python3
"""Independent folded STRING complement, child-line and producer controls."""
import output_final_selected_folded_string_bitnot_cast_chain_return_modulo_error_state as current
import output_final_selected_folded_string_bitnot_cast_chain_return_modulo_error_sources as sources
CASES = {name: sources.CASES['native-selected-folded-string-bitnot-cast-chain-return-modulo-error-' + name]
         for name in ['warning-right-cv-pair-multi-not-twenty', 'deprecated-both-cv-pair-single-not-nul',
                      'warning-deprecated-constant-float-bitand-not-two-nul']}
shared = current.current
adapter_fields = ('DETAILS', 'TREES', 'modulo_line', 'converted', 'expression', 'return_proof')
pristine_adapter = tuple(getattr(shared, field) for field in adapter_fields)
import output_final_selected_folded_string_bitwise_cast_chain_return_modulo_error_review_state as previous
import output_final_selected_integer_bitnot_cast_chain_return_modulo_error_review_state as oldnot
for field, original in zip(adapter_fields, pristine_adapter):
    setattr(shared, field, original)

control, scaffold = previous.control, previous.scaffold
runner, PREFIX, CONJ = current.runner, scaffold.PREFIX, current.CONJ
value, string = previous.value, previous.string
data, plain = previous.data, previous.plain


def unary(leaf, pooled):
    raw, typed, fact = leaf
    child = raw.format(metadata='metadata_value_child')
    expression = 'NExprBitwiseNot (' + child + ') metadata_value'
    state, function = scaffold.changed([('pcpath_value', expression), ('pcpath_value_child', child)],
        [('pcpath_value', 'z_value_child', 'true'), ('pcpath_value_child', 'z_value_child', 'true')],
        [('pcpath_value', pooled), ('pcpath_value_child', fact)])
    return state, expression, function, child, typed


def compiled_proof(query, raw, answer, admitted=True):
    state, expression, function, child, typed = query
    result = plain(answer)
    parts = [value(state, child, 'porigin_value_child', function) + ' = (' + typed + ')',
             '$string_not((' + data(raw) + ')) = (' + data(answer) + ')']
    if admitted:
        parts += ['$compiled_read(' + state + ', porigin_value) = (' + result + ')',
                  '$compiled_effects(' + state + ', porigin_value) = eps',
                  '$compiled_string_value(' + state + ', porigin_value, ' + result + ') = ' + result,
                  '$enter_compiled_task(' + state + ', porigin_value, EVAL (' + expression + '), ' + state + '.TODO) = ' + state + '[.RESULT = KNOWN (' + result + ')]']
    parts += [value(state, expression, function=function) + (' = (' + result + ')' if admitted else ' = eps')]
    return CONJ.join(parts)


def runtime_proof(query, raw, answer):
    state, expression, function, child, typed = query
    call = '$bitnot_apply(' + state + '[.RESULT = KNOWN (' + typed + ')], ' + typed + ', z_value_child)'
    if len(raw) == 1:
        result = 'PSTRING_CARRIER INTERNED_STRING (' + data(answer) + ')'
        expected = state + '[.RESULT = KNOWN (' + result + ')]'
    else:
        result = 'PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) (' + data(answer) + ')'
        expected = state + '[.STRINGDATA = S.STRINGDATA ++ [(' + data(answer) + ')]][.RESULT = KNOWN (' + result + ')]'
    return call + ' = ' + expected


QUERIES = [(b'\xce', b'1'), (b'\xcd\xcf', b'20'), (b'\xff', b'\0'), (b'', b''),
           (b'0', b'\xcf'), (b'\xff\xff', b'\0\0'), (b'1', b'\xce'),
           (b'\x01', b'\xfe'), (b'\x80', b'\x7f'), (b'ab', b'\x9e\x9d'),
           (b' \t', b'\xdf\xf6'), (b'00', b'\xcf\xcf')]


def frontier(name, fixture, path):
    bindings, checks = current.frontier(name, fixture, path)
    bindings += ['$source_unit(S.SOURCES, n_cast_handler) = (pcunit_handler)',
                 '$pool_at(S.POOLS, n_cast_handler) = (ppool_handler)']
    nodes = current.nodes(name)
    expression, result = current.expression(name, 'value'), nodes['value'][3]
    checks += [('the actual folded complement keeps plain bytes and the child terminal compiler line',
                CONJ.join([value('S', expression) + ' = (' + result + ')',
                           'z_value = z_value_child', '$source_line(metadata_value) =/= z_value',
                           '$enter_compiled_task(S, porigin_value, EVAL (' + expression + '), S.TODO) = S[.RESULT = KNOWN (' + result + ')]'])),
               ('an abrupt preset result cannot supply a folded STRING certificate',
                value('S[.COMPLETION = BUDGET][.RESULT = KNOWN (' + result + ')]', expression) + ' = eps'),
               ('the handler keeps its actual CODE unit and source BODY',
                '~' + control.tail(function='pfunction_handler[.CODE.UNIT = $(n_cast_handler + 1)]') + CONJ +
                '~' + control.tail(function='pfunction_handler[.BODY = pfunction_handler.BODY ++ [PCINDEX 0]]'))]
    for key, node in nodes.items():
        flag = str(node[4]).lower()
        for label, line, changed_flag in [('line', '$(z_' + key + ' + 1)', flag),
                                          ('fold flag', 'z_' + key, str(not node[4]).lower())]:
            checks += [(key + ' retains its independent compiler ' + label,
                        '~' + control.tail(function=control.code_function('pcpath_' + key, line, changed_flag)))]
        state = 'S[.SOURCES = pcunit_handler[.OCCURRENCES = $or131_drop(pcunit_handler.OCCURRENCES, pcpath_' + key + ')] :: S.SOURCES]'
        checks += [(key + ' retains its own indexed source node', '~' + control.tail(state))]
        if node[4]:
            state = 'S[.POOLS = ppool_handler[.CONSTANTS = $or131_fact_drop(ppool_handler.CONSTANTS, pcpath_' + key + ')] :: S.POOLS]'
            checks += [(key + ' cannot borrow another folded fact', '~' + control.tail(state)),
                       (key + ' cannot borrow an owning fact', '~' + control.tail(control.pool_state('pcpath_' + key, 'POBJECT 0')))]
        if node[0] == 'NExprBitwiseNot' and node[3].startswith('PSTRING '):
            for wrong in ['PINT 0', 'PBOOL true', 'PSTRING_CARRIER INTERNED_STRING ' + node[3].removeprefix('PSTRING '), plain(b'wrong')]:
                checks += [('a complement fact retains its exact plain tag and byte result',
                            '~' + control.tail(control.pool_state('pcpath_' + key, wrong)))]
            if key == 'value':
                checks += [('a unary syntax line cannot replace its distinct child terminal line',
                            '$source_line(metadata_value) =/= z_' + key + CONJ +
                            '~' + control.tail(function=control.code_function('pcpath_' + key, '$source_line(metadata_value)', 'true')))]
    if current.DETAILS[name][1] == 'bitand-not-two-nul':
        child_line = '$expression_line(' + current.expression(name, 'value_child') + ')'
        checks += [('a folded child AND keeps its own distinct terminal RHS line',
                    child_line + ' =/= z_value_child' + CONJ + '~' + control.tail(function=control.code_function('pcpath_value_child', child_line, 'true')))]
        coherent = 'pfunction_handler[.CODE.EXPRESSIONS = [CODEEXPR pcpath_value (' + child_line + ') true, CODEEXPR pcpath_value_child (' + child_line + ') true] ++ pfunction_handler.CODE.EXPRESSIONS]'
        checks += [('coherent parent NOT and child AND syntax lines cannot replace the genuine terminal leaf',
                    '~' + control.tail(function=coherent))]
    code = 'pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR pcpath_value z_value false) :: pfunction_handler.CODE.EXPRESSIONS]'
    unread = 'S[.CODE = ' + code + ' :: S.CODE]'
    effect = 'S[.CODE = pfunction_handler.CODE[.EXPRESSIONS = (CODEEFFECT pcpath_value_child) :: pfunction_handler.CODE.EXPRESSIONS] :: S.CODE]'
    checks += [('an unread own pool cannot replace global folded CODE',
                '$compiled_read(' + unread + ', porigin_value) = eps' + CONJ + value(unread, expression) + ' = eps'),
               ('attached compiler effects cannot be discarded by a plain STRING result',
                '$compiled_effects(' + effect + ', porigin_value) =/= eps' + CONJ + value(effect, expression) + ' = eps')]
    bare = 'NStmtReturn (' + expression + ') metadata_cast_return'
    single = nodes['cast_1'][0] + ' (' + expression + ') metadata_cast_1'
    statement = 'NStmtReturn (' + single + ') metadata_cast_return'
    checks += [('bare and single-cast handler fences remain required',
                '~' + control.tail(control.source_state([('pcpath_cast_return', bare)]), statement=bare) + CONJ +
                '~' + control.tail(control.source_state([('pcpath_cast_return', statement), ('pcpath_cast', single)]), statement=statement))]
    if current.DETAILS[name][1] == 'multi-not-twenty':
        for raw, answer in QUERIES:
            query = unary(string(raw), plain(answer))
            checks += [('source0 exact decoded STRING complement bytes retain the compiled plain producer', compiled_proof(query, raw, answer)),
                       ('source0 runtime NOT retains one-byte INTERNED versus REQUEST/STRINGDATA identity including empty input', runtime_proof(query, raw, answer))]
        for raw, answer in QUERIES[:3]:
            for wrong in ['PINT 0', 'PBOOL true', 'PSTRING_CARRIER INTERNED_STRING (' + data(answer) + ')', plain(b'wrong')]:
                checks += [('source0 a wrong tag, identity or byte fact cannot replace the own compiled complement',
                            compiled_proof(unary(string(raw), wrong), raw, answer, False))]
        query = unary(string(b'\xce'), plain(b'1'))
        state, expr, function, child, typed = query
        emitted = function + '[.CODE.EXPRESSIONS = (CODEEXPR pcpath_value z_value_child false) :: ' + function + '.CODE.EXPRESSIONS]'
        emitted_state = state + '[.CODE = ' + emitted + '.CODE :: ' + state + '.CODE]'
        checks += [('source0 an emitted read-eps NOT cannot borrow folded constant authority',
                    '$compiled_read(' + emitted_state + ', porigin_value) = eps' + CONJ + value(emitted_state, expr, function=emitted) + ' = eps')]
        for leaf in [string(b'\0'), (*string(b'\xce')[:2], 'PSTRING_CARRIER (REQUEST_STRING 0) ([206])')]:
            state, expr, function, child, typed = unary(leaf, plain(b'1'))
            checks += [('source0 literal NUL and forged REQUEST leaf facts retain their prior fences',
                        value(state, child, 'porigin_value_child', function) + ' = eps' + CONJ + value(state, expr, function=function) + ' = eps')]
        for owning in ['PARRAY 0', 'POBJECT 0']:
            state, expr, function, child, typed = unary((string(b'\xce')[0], owning, owning), plain(b'1'))
            checks += [('source0 an owning child cannot borrow proper STRING authority',
                        '$value_nodes(' + owning + ') =/= eps' + CONJ + value(state, child, 'porigin_value_child', function) + ' = eps' + CONJ + value(state, expr, function=function) + ' = eps')]
        bindings += ['pcpath_sign = pcpath_value', 'porigin_sign = porigin_value',
                     'pcpath_child_3 = pcpath_value_child', 'porigin_child_3 = porigin_value_child',
                     'metadata_sign = metadata_value', 'metadata_child_3 = metadata_value_child']
        leaf = 'NScalarString (BYTES "MA==") metadata_child_3'
        state, expr, function = oldnot.raw_not(leaf, 'PSTRING ($ptascii("0"))', 'PINT $(-1)')
        checks += [('source0 the actual old numeric-STRING NOT builder still refuses its forged own PINT fact',
                    value(state, leaf, 'porigin_child_3', function) + ' = (PSTRING_CARRIER INTERNED_STRING ($ptascii("0")))' + CONJ + value(state, expr, 'porigin_sign', function) + ' = eps')]
        leaf = 'NScalarInt (INTEGER 1) metadata_child_3'
        state, expr, function = oldnot.raw_not(leaf, 'PINT 1', 'PINT $(-2)')
        checks += [('source0 the existing exact integer NOT builder remains an integer complement',
                    value(state, expr, 'porigin_sign', function) + ' = (PINT $(-2))')]
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = current.lifecycle(name, fixture, path)
    checks += [('the exact folded STRING and both scalar casts survive formal/native-cell retirement',
                CONJ.join(['S_handler.RESULT = KNOWN (' + current.root_value(name) + ')', 'S.RESULT = KNOWN PNULL',
                           value('S', current.expression(name, 'value')) + ' = (' + current.nodes(name)['value'][3] + ')']))]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
