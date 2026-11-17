#!/usr/bin/env python3
"""Independent parser STRING authority, byte domain and retirement checks."""
import base64
import output_final_selected_parser_string_concat_cast_chain_return_modulo_error_state as current
import output_final_selected_parser_string_concat_cast_chain_return_modulo_error_sources as sources

CASES = {name: sources.CASES['native-selected-parser-string-concat-cast-chain-return-modulo-error-' + name]
         for name in ['warning-right-cv-pair-multiline-twenty', 'deprecated-both-cv-pair-left-empty-zero',
                      'warning-deprecated-constant-float-high-byte']}
shared = current.prior
adapter_fields = ('DETAILS', 'TREES', 'modulo_line', 'converted', 'expression', 'return_proof', 'return_bindings')
pristine = tuple(getattr(shared, field) for field in adapter_fields)
import output_final_selected_folded_string_bitwise_cast_chain_return_modulo_error_review_state as old145
for field, original in zip(adapter_fields, pristine):
    setattr(shared, field, original)

control, scaffold = old145.control, old145.scaffold
runner, PREFIX, CONJ = current.runner, scaffold.PREFIX, current.CONJ


def value(state, expression, origin='porigin_value', function='pfunction_handler'):
    return '$ob_object_cast_chain_value(' + state + ', ' + function + ', ' + origin + ', ' + expression + ')'


def plain(raw):
    return 'PSTRING ' + current.data(raw)


def carrier(raw):
    return 'PSTRING_CARRIER INTERNED_STRING ' + current.data(raw)


def query(tree, answer=None):
    rows, paths = [], []
    def visit(node, path, root=False):
        metadata = 'metadata_value' if root else '([(MstartLine 1), (MconcatExprLine 2)])'
        if isinstance(node, tuple):
            left = visit(node[0], '(' + path + ' ++ [PCFIELD 0])')
            right = visit(node[1], '(' + path + ' ++ [PCFIELD 1])')
            expression = 'NExprBinaryOpConcat (' + left + ') (' + right + ') ' + metadata
        elif isinstance(node, bytes):
            expression = 'NScalarString (BYTES "' + base64.b64encode(node).decode() + '") ' + metadata
        else:
            expression = node
        rows.append((path, expression))
        paths.append(path)
        return expression
    expression = visit(tree, 'pcpath_value', True)
    def raw(node):
        return raw(node[0]) + raw(node[1]) if isinstance(node, tuple) else node
    answer = raw(tree) if answer is None else answer
    state, function = scaffold.changed(rows, [('pcpath_value', '$concat_line(metadata_value)', 'true')],
                                       [('pcpath_value', plain(answer))])
    return state, expression, function, paths, answer


def compiled(query_value):
    state, expression, function, paths, answer = query_value
    result = carrier(answer)
    parts = [value(state, expression, function=function) + ' = (' + result + ')',
             '$parser_literal_origin(' + state + ', (porigin_value), ' + expression + ') = (' + plain(answer) + ')',
             '$compiled_read(' + state + ', porigin_value) = (' + plain(answer) + ')',
             '$compiled_string_value(' + state + ', porigin_value, ' + plain(answer) + ') = ' + result,
             '$compiled_effects(' + state + ', porigin_value) = eps',
             '$enter_compiled_task(' + state + ', porigin_value, EVAL (' + expression + '), ' + state + '.TODO) = ' +
             state + '[.RESULT = KNOWN (' + result + ')]']
    parts += ['$code_expression(' + function + '.CODE.EXPRESSIONS, ' + path + ') = eps' for path in paths[:-1]]
    return CONJ.join(parts)


def runtime(left, right):
    answer = left + right
    call = '$string_concat_unknown(S, ' + carrier(left) + ', ' + carrier(right) + ')'
    if left and right:
        result = 'PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ' + current.data(answer)
        expected = 'S[.STRINGDATA = S.STRINGDATA ++ [' + current.data(answer) + ']][.RESULT = KNOWN (' + result + ')]'
    else:
        expected = 'S[.RESULT = KNOWN (' + plain(answer) + ')]'
    return call + ' = ' + expected


PAIRS = [(b'', b''), (b'0', b''), (b'', b'0'), (b'2', b'0'), (b'1', b'2'),
         (b'\xff', b'x'), (b'ab', b'CD'), (b' ', b'\t'), (b'00', b''), (b'', b'nope')]


def frontier(name, fixture, path):
    bindings, checks = current.frontier(name, fixture, path)
    bindings += ['$source_unit(S.SOURCES, n_cast_handler) = (pcunit_handler)',
                 '$pool_at(S.POOLS, n_cast_handler) = (ppool_handler)',
                 'z_value_left = $source_line(metadata_value_left)',
                 'z_value_right = $source_line(metadata_value_right)']
    expression, result = current.expression(name, 'value'), current.carrier(name)
    checks += [('the actual parser entry is INTERNED rather than a plain or REQUEST result',
                current.parser_proof(name) + CONJ + value('S', expression) + ' = (' + result + ')'),
               ('an abrupt preset result cannot replace NORMAL parser source authority',
                value('S[.COMPLETION = BUDGET][.RESULT = KNOWN (' + result + ')]', expression) + ' = eps'),
               ('the original handler UNIT and BODY remain required',
                '~' + control.tail(function='pfunction_handler[.CODE.UNIT = $(n_cast_handler + 1)]') + CONJ +
                '~' + control.tail(function='pfunction_handler[.BODY = pfunction_handler.BODY ++ [PCINDEX 0]]'))]
    for key, flag in [('cast', 'false'), ('cast_1', 'false'), ('value', 'true')]:
        for label, line, changed_flag in [('line', '$(z_' + key + ' + 1)', flag),
                                          ('flag', 'z_' + key, 'false' if flag == 'true' else 'true')]:
            checks += [(key + ' retains its own compiler ' + label,
                        '~' + control.tail(function=control.code_function('pcpath_' + key, line, changed_flag)))]
    for key in ['cast', 'cast_1', *current.nodes(name)]:
        state = 'S[.SOURCES = pcunit_handler[.OCCURRENCES = $or131_drop(pcunit_handler.OCCURRENCES, pcpath_' + key + ')] :: S.SOURCES]'
        checks += [(key + ' indexed SOURCE cannot be replaced by intact parent or sibling facts', '~' + control.tail(state))]
    state = 'S[.POOLS = ppool_handler[.CONSTANTS = $or131_fact_drop(ppool_handler.CONSTANTS, pcpath_value)] :: S.POOLS]'
    checks += [('an absent own pool cannot borrow STRING bytes from SOURCE', '~' + control.tail(state))]
    for wrong in ['PINT 0', 'PBOOL false', 'PFLOAT 0', result,
                  'PSTRING_CARRIER (REQUEST_STRING 0) ([49])', plain(b'wrong'), 'POBJECT 0']:
        checks += [('the parser pool retains its exact plain tag and bytes', '~' + control.tail(control.pool_state('pcpath_value', wrong)))]
    unread = 'S[.CODE = pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR pcpath_value z_value false) :: pfunction_handler.CODE.EXPRESSIONS] :: S.CODE]'
    effect = 'S[.CODE = pfunction_handler.CODE[.EXPRESSIONS = (CODEEFFECT pcpath_value_left) :: pfunction_handler.CODE.EXPRESSIONS] :: S.CODE]'
    checks += [('an unread global pool cannot borrow the function-local fold flag',
                '$compiled_read(' + unread + ', porigin_value) = eps' + CONJ + value(unread, expression) + ' = eps'),
               ('a compiler effect cannot be discarded by an exact parser byte fact',
                '$compiled_effects(' + effect + ', porigin_value) =/= eps' + CONJ + value(effect, expression) + ' = eps'),
               ('the left syntax line cannot replace the distinct own CONCAT line',
                'z_value =/= z_value_left' + CONJ +
                '~' + control.tail(function=control.code_function('pcpath_value', 'z_value_left', 'true')))]
    epoch = 'S[.POOLS = ppool_handler[.CONSTANTS = (PCCPRECISION pcpath_value 1) :: ppool_handler.CONSTANTS] :: S.POOLS]'
    checks += [('saved STRING bytes survive a compiler precision epoch and changed live precision',
                '$compiled_precision(' + epoch + ', (porigin_value)) = (1)' + CONJ +
                value(epoch, expression) + ' = (' + result + ')' + CONJ +
                value('$precision_memory(S, 1)', expression) + ' = (' + result + ')')]
    bare = 'NStmtReturn (' + expression + ') metadata_cast_return'
    single = current.expression(name, 'cast_1')
    statement = 'NStmtReturn (' + single + ') metadata_cast_return'
    checks += [('bare and single-cast handlers retain their existing tail fences',
                '~' + control.tail(control.source_state([('pcpath_cast_return', bare)]), statement=bare) + CONJ +
                '~' + control.tail(control.source_state([('pcpath_cast_return', statement), ('pcpath_cast', single)]), statement=statement))]
    if current.DETAILS[name][1] == 'multiline-twenty':
        for left, right in PAIRS:
            checks += [('source0 byte-only parser CONCAT keeps exact bytes and INTERNED constant entry', compiled(query((left, right)))),
                       ('source0 runtime CONCAT retains allocation or unknown empty-side identity', runtime(left, right))]
        nested = query((b'1', (b'2', b'3')))
        checks += [('source0 a nested parser tree authenticates deep SOURCE without child CODE', compiled(nested))]
        state, expr, function, _, _ = nested
        deep = '((pcpath_value ++ [PCFIELD 1]) ++ [PCFIELD 0])'
        missing = state + '[.SOURCES = pcunit_handler[.OCCURRENCES = $or131_drop(' + state + '.SOURCES[0].OCCURRENCES, ' + deep + ')] :: S.SOURCES]'
        checks += [('source0 a missing deep SOURCE cannot be borrowed from the nested parent', value(missing, expr, function=function) + ' = eps')]
        checks += [('source0 the exact fitting INT1 parser CONCAT now retains its constant entry',
                    compiled(query(('NScalarInt (INTEGER 1) (eps)', b''), b'1')))]
        checks += [('source0 the exact finite FLOAT1.5 parser CONCAT now retains its constant entry',
                    compiled(query(('NScalarFloat (FLOAT "3ff8000000000000") (eps)', b''), b'1.5')))]
        for raw, answer in [('NExprConstFetch (NName (BYTES "dHJ1ZQ==") (eps)) (eps)', b'1'),
                            ('NExprConstFetch (NName (BYTES "bnVsbA==") (eps)) (eps)', b''),
                            ('NExprCastInt (NScalarString (BYTES "MQ==") (eps)) (eps)', b'1')]:
            state, expr, function, _, _ = query((raw, b''), answer)
            checks += [('source0 keyword and emitted-cast leaves stay outside the parser domain',
                        value(state, expr, function=function) + ' = eps')]
        state, expr, function, _, _ = query((b'\0', b'x'))
        checks += [('source0 literal NUL remains outside this non-NUL parser source domain', value(state, expr, function=function) + ' = eps')]
        old = old145.binary('and', old145.string('3'), old145.string('1'), old145.plain(b'1'))
        state, expr, function = [part.replace('NExprBinaryOpBitwiseAnd', 'NExprBinaryOpConcat') for part in old[:3]]
        checks += [('source0 the actual old145 CONCAT forgery still cannot borrow BIT3 result bytes',
                    value(state, expr, function=function) + ' = eps')]
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = current.lifecycle(name, fixture, path)
    expression, result = current.expression(name, 'value'), current.carrier(name)
    checks += [('the actual parser STRING and strict outer scalar survive native-formal retirement',
                'S_handler.RESULT = KNOWN (' + current.root_value(name) + ')' + CONJ +
                'S.RESULT = KNOWN PNULL' + CONJ + value('S', expression) + ' = (' + result + ')')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
