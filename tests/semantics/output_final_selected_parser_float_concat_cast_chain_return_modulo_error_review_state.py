#!/usr/bin/env python3
"""Independent finite FLOAT parser bytes, precision and retirement controls."""
import output_final_selected_parser_float_concat_cast_chain_return_modulo_error_state as current
import output_final_selected_parser_float_concat_cast_chain_return_modulo_error_sources as sources

CASES = {name: sources.CASES['native-selected-parser-float-concat-cast-chain-return-modulo-error-' + name]
         for name in ['warning-right-cv-pair-both-floats', 'deprecated-both-cv-pair-left-empty-zero',
                      'warning-deprecated-constant-float-scientific']}
shared = current.prior.prior.prior
adapter_fields = ('DETAILS', 'TREES', 'modulo_line', 'converted', 'expression', 'return_proof', 'return_bindings')
pristine = tuple(getattr(shared, field) for field in adapter_fields)
import output_final_selected_parser_integer_concat_cast_chain_return_modulo_error_review_state as previous
for field, original in zip(adapter_fields, pristine):
    setattr(shared, field, original)

runner, PREFIX, CONJ = current.runner, previous.PREFIX, current.CONJ
control, original = previous.control, previous.previous
value, plain, carrier = previous.value, previous.plain, previous.carrier
query, compiled = previous.query, original.compiled


def floating(bits):
    return 'NScalarFloat (FLOAT "' + bits + '") (eps)'


def epoch(path):
    return 'S[.POOLS = ppool_handler[.CONSTANTS = (PCCPRECISION ' + path + ' 1) :: ppool_handler.CONSTANTS] :: S.POOLS]'


POSITIVE = [((floating('0000000000000000'), b''), b'0'),
            ((floating('3ff8000000000000'), b'0'), b'1.50'),
            ((b'A', floating('3fd0000000000000')), b'A0.25'),
            ((floating('3ff8000000000000'), 1), b'1.51'),
            ((1, (floating('4004000000000000'), b'')), b'12.5'),
            ((floating('4415af1d78b58c40'), b''), b'1.0E+20'),
            ((floating('0000000000000001'), b''), b'4.9406564584125E-324'),
            ((floating('7fefffffffffffff'), b''), b'1.7976931348623E+308')]


def frontier(name, fixture, path):
    bindings, checks = current.frontier(name, fixture, path)
    bindings += ['$source_unit(S.SOURCES, n_cast_handler) = (pcunit_handler)',
                 '$pool_at(S.POOLS, n_cast_handler) = (ppool_handler)',
                 '$source_precision(S, (porigin_value)) = (14)']
    expression, result, raw_result = current.expression(name, 'value'), current.carrier(name), current.plain(name)
    checks += [('the actual finite FLOAT parser tree retains its exact INTERNED entry',
                current.parser_proof(name) + CONJ + value('S', expression) + ' = (' + result + ')'),
               ('an abrupt preset result cannot supply FLOAT parser authority',
                value('S[.COMPLETION = BUDGET][.RESULT = KNOWN (' + result + ')]', expression) + ' = eps'),
               ('the selected handler retains its own UNIT and source BODY',
                '~' + control.tail(function='pfunction_handler[.CODE.UNIT = $(n_cast_handler + 1)]') + CONJ +
                '~' + control.tail(function='pfunction_handler[.BODY = pfunction_handler.BODY ++ [PCINDEX 0]]')),
               ('FLOAT bytes require authenticated declaration precision',
                '$source_precision(S[.DECLARATIONS = eps], (porigin_value)) = eps' + CONJ +
                value('S[.DECLARATIONS = eps]', expression) + ' = eps'),
               ('changed live precision cannot reformat an existing parser STRING',
                value('$precision_memory(S, 1)', expression) + ' = (' + result + ')')]
    for key, node in current.nodes(name).items():
        if isinstance(node, float):
            leaf = current.expression(name, key)
            checks += [('each raw finite FLOAT keeps its own indexed source and parser bytes',
                        '$ob_object_parser_string(S, porigin_' + key + ', ' + leaf + ') = ' + current.data(current.TEXT[node]))]
            missing = 'S[.SOURCES = pcunit_handler[.OCCURRENCES = $or131_drop(pcunit_handler.OCCURRENCES, pcpath_' + key + ')] :: S.SOURCES]'
            checks += [('a FLOAT leaf cannot borrow SOURCE from an intact parent or sibling',
                        value(missing, expression) + ' = eps')]
    for wrong in ['PINT 0', result, 'POBJECT 0']:
        checks += [('numeric, INTERNED and owning pool tags cannot replace exact plain parser bytes',
                    value(control.pool_state('pcpath_value', wrong), expression) + ' = eps')]
    unread = 'S[.CODE = pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR pcpath_value z_value false) :: pfunction_handler.CODE.EXPRESSIONS] :: S.CODE]'
    checks += [('emitted CONCAT cannot borrow the raw FLOAT parser certificate',
                '$compiled_read(' + unread + ', porigin_value) = eps' + CONJ + value(unread, expression) + ' = eps')]
    root_epoch = epoch('pcpath_value')
    if current.DETAILS[name][1] == 'both-floats':
        leaf_epoch = epoch('pcpath_value_left')
        checks += [('a child-only PCC1 marker cannot replace source14 while root PCC14 stays valid',
                    CONJ.join(['$compiled_precision(' + leaf_epoch + ', (porigin_value_left)) = (1)',
                               '$source_precision(' + leaf_epoch + ', (porigin_value_left)) = (14)',
                               '$ob_object_parser_string(' + leaf_epoch + ', porigin_value_left, ' + current.expression(name, 'value_left') + ') = ([49, 46, 53])',
                               value(leaf_epoch, expression) + ' = (' + result + ')'])),
                   ('a changed-byte root PCC1 producer stays plain and cannot supply INTERNED authority',
                    CONJ.join(['$parser_literal_origin(' + root_epoch + ', (porigin_value), ' + expression + ') = (' + raw_result + ')',
                               '$parser_literal_at(' + expression + ', 1) = (' + plain(b'20') + ')',
                               '$compiled_string_value(' + root_epoch + ', porigin_value, ' + raw_result + ') = ' + raw_result,
                               '$enter_compiled_task(' + root_epoch + ', porigin_value, EVAL (' + expression + '), ' + root_epoch + '.TODO) = ' + root_epoch + '[.RESULT = KNOWN (' + raw_result + ')]',
                               value(root_epoch, expression) + ' = eps']))]
        for tree, answer in POSITIVE:
            checks += [('source0 canonical finite FLOAT trees retain exact bytes and actual constant entry',
                        compiled(query(tree, answer)))]
        for bits, answer in [('8000000000000000', b'-0'), ('bff8000000000000', b'-1.5'),
                             ('fff0000000000000', b'-INF')]:
            checks += [('source0 signed or nonfinite raw FLOAT refuses even a matching byte pool',
                        previous.matched_refusal(query((floating(bits), b''), answer)))]
        checks += [('source0 the affected raw positive-INF query is promoted through its original builder',
                    compiled(query((floating('7ff0000000000000'), b''), b'INF')))]
        for bits in ['7ff8000000000000', '7ff0000000000001', 'fff8000000000000']:
            state, expr, function, _, _ = query((floating(bits), b''), b'1.5')
            checks += [('source0 NaN payload stays on the guarded value refusal route',
                        value(state, expr, function=function) + ' = eps')]
        for bits in ['3FF8000000000000', '3ff800000000000', '03ff8000000000000', '3fg8000000000000']:
            state, expr, _, _, _ = query((floating(bits), b''), b'1.5')
            checks += [('source0 malformed payload stays on the guarded parser-string refusal route',
                        '$ob_object_parser_string(' + state + ', porigin_value, ' + expr + ') = eps')]
        for raw in ['NExprUnaryMinus (' + floating('3ff8000000000000') + ') (eps)',
                    'NExprUnaryPlus (' + floating('3ff8000000000000') + ') (eps)',
                    'NExprCastDouble (NScalarInt (INTEGER 1) (eps)) (eps)']:
            state, expr, function, _, _ = query((raw, b''), b'1.5')
            checks += [('source0 unary or emitted producers cannot borrow a raw FLOAT leaf',
                        value(state, expr, function=function) + ' = eps')]
        state, expr, function, _, _ = query((b'\0', floating('3ff8000000000000')), b'\x001.5')
        checks += [('source0 an admitted FLOAT sibling cannot admit a NUL STRING leaf',
                    value(state, expr, function=function) + ' = eps')]
        old = original.query((floating('3ff8000000000000'), b''), b'1.5')
        checks += [('source0 the affected old FLOAT1.5 query is promoted through its original builder',
                    compiled(old))]
    if current.DETAILS[name][1] == 'scientific':
        checks += [('a byte-identical root PCC1 producer retains INTERNED authority without precision equality',
                    '$parser_literal_at(' + expression + ', 1) = (' + raw_result + ')' + CONJ +
                    value(root_epoch, expression) + ' = (' + result + ')')]
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = current.lifecycle(name, fixture, path)
    checks += [('parser FLOAT bytes and strict scalar results survive real formal/native-cell retirement',
                'S_handler.RESULT = KNOWN (' + current.root_value(name) + ')' + CONJ + 'S.RESULT = KNOWN PNULL' + CONJ +
                value('S', current.expression(name, 'value')) + ' = (' + current.carrier(name) + ')')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
