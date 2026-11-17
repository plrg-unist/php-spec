#!/usr/bin/env python3
"""Independent raw INT parser range, source, precision and retirement checks."""
import output_final_selected_parser_integer_concat_cast_chain_return_modulo_error_state as current
import output_final_selected_parser_integer_concat_cast_chain_return_modulo_error_sources as sources

CASES = {name: sources.CASES['native-selected-parser-integer-concat-cast-chain-return-modulo-error-' + name]
         for name in ['warning-right-cv-pair-both-integers', 'deprecated-both-cv-pair-left-empty-zero',
                      'warning-deprecated-constant-float-maximum']}
shared = current.prior.prior
adapter_fields = ('DETAILS', 'TREES', 'modulo_line', 'converted', 'expression', 'return_proof', 'return_bindings')
pristine = tuple(getattr(shared, field) for field in adapter_fields)
import output_final_selected_parser_string_concat_cast_chain_return_modulo_error_review_state as previous
for field, original in zip(adapter_fields, pristine):
    setattr(shared, field, original)

runner, PREFIX, CONJ = current.runner, previous.PREFIX, current.CONJ
control, scaffold = previous.control, previous.scaffold
value, plain, carrier = previous.value, previous.plain, previous.carrier
MAXIMUM = 9223372036854775807


def integer(number):
    text = str(number) if number >= 0 else '$(' + str(number) + ')'
    return 'NScalarInt (INTEGER ' + text + ') (eps)'


def query(tree, answer):
    def syntax(node):
        if isinstance(node, tuple):
            return tuple(syntax(child) for child in node)
        return integer(node) if isinstance(node, int) else node
    return previous.query(syntax(tree), answer)


def matched_refusal(query_value):
    state, expression, function, _, answer = query_value
    return CONJ.join(['$parser_literal_origin(' + state + ', (porigin_value), ' + expression + ') = (' + plain(answer) + ')',
                     '$compiled_read(' + state + ', porigin_value) = (' + plain(answer) + ')',
                     '$compiled_string_value(' + state + ', porigin_value, ' + plain(answer) + ') = ' + carrier(answer),
                     value(state, expression, function=function) + ' = eps'])


POSITIVE = [((0, b''), b'0'), ((1, b''), b'1'), ((10, b''), b'10'),
            ((MAXIMUM, b''), b'9223372036854775807'), ((b'', 0), b'0'),
            ((b'\xff', 1), b'\xff1'), ((2, 0), b'20'), ((1, (2, b'')), b'12'),
            ((b'0', 1), b'01'), (((MAXIMUM, b''), 0), b'92233720368547758070')]


def frontier(name, fixture, path):
    bindings, checks = current.frontier(name, fixture, path)
    bindings += ['$source_unit(S.SOURCES, n_cast_handler) = (pcunit_handler)',
                 '$pool_at(S.POOLS, n_cast_handler) = (ppool_handler)']
    expression, result = current.expression(name, 'value'), current.carrier(name)
    checks += [('the exact INT parser tree keeps plain pool bytes and an INTERNED NORMAL entry',
                current.parser_proof(name) + CONJ + value('S', expression) + ' = (' + result + ')'),
               ('an abrupt preset result cannot authenticate the new INT parser leaf',
                value('S[.COMPLETION = BUDGET][.RESULT = KNOWN (' + result + ')]', expression) + ' = eps'),
               ('handler UNIT and actual BODY remain required for INT parser returns',
                '~' + control.tail(function='pfunction_handler[.CODE.UNIT = $(n_cast_handler + 1)]') + CONJ +
                '~' + control.tail(function='pfunction_handler[.BODY = pfunction_handler.BODY ++ [PCINDEX 0]]')),
               ('precision-independent INT bytes still require authenticated source precision',
                '$source_precision(S[.DECLARATIONS = eps], (porigin_value)) = eps' + CONJ +
                value('S[.DECLARATIONS = eps]', expression) + ' = eps')]
    for key, node in current.nodes(name).items():
        if isinstance(node, int):
            leaf = current.expression(name, key)
            checks += [('each actual raw INT retains its own fitting range and decimal source bytes',
                        '$long_range(' + str(node) + ')' + CONJ +
                        '$ob_object_parser_string(S, porigin_' + key + ', ' + leaf + ') = ' + current.data(str(node).encode()))]
            missing = 'S[.SOURCES = pcunit_handler[.OCCURRENCES = $or131_drop(pcunit_handler.OCCURRENCES, pcpath_' + key + ')] :: S.SOURCES]'
            checks += [('an INT child cannot borrow its indexed SOURCE from a parent or sibling pool',
                        value(missing, expression) + ' = eps')]
    for wrong in ['PINT 0', 'POBJECT 0', result]:
        checks += [('a numeric, owning or INTERNED pool tag cannot replace exact plain parser bytes',
                    value(control.pool_state('pcpath_value', wrong), expression) + ' = eps')]
    unread = 'S[.CODE = pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR pcpath_value z_value false) :: pfunction_handler.CODE.EXPRESSIONS] :: S.CODE]'
    checks += [('an emitted own CONCAT cannot borrow parser-folded INT authority',
                '$compiled_read(' + unread + ', porigin_value) = eps' + CONJ + value(unread, expression) + ' = eps')]
    if current.DETAILS[name][1] == 'both-integers':
        for tree, answer in POSITIVE:
            checks += [('source0 fitting INT/STRING trees retain exact decimal bytes and constant-entry identity',
                        previous.compiled(query(tree, answer)))]
        for number in [-1, -9223372036854775808, MAXIMUM + 1]:
            checks += [('source0 forged negative or overflowing raw INT refuses even matching own pool bytes',
                        matched_refusal(query((number, b''), str(number).encode())))]
        excluded = [('NScalarFloat (FLOAT "3ff8000000000000") (eps)', b'1.5'),
                    ('NExprUnaryMinus (NScalarInt (INTEGER 1) (eps)) (eps)', b'-1'),
                    ('NExprUnaryPlus (NScalarInt (INTEGER 1) (eps)) (eps)', b'1'),
                    ('NExprConstFetch (NName (BYTES "dHJ1ZQ==") (eps)) (eps)', b'1'),
                    ('NExprConstFetch (NName (BYTES "bnVsbA==") (eps)) (eps)', b''),
                    ('NExprCastInt (NScalarString (BYTES "MQ==") (eps)) (eps)', b'1')]
        for raw, answer in excluded:
            state, expr, function, _, _ = previous.query((raw, b''), answer)
            checks += [('source0 FLOAT, unary, keyword and emitted-cast leaf fences remain',
                        value(state, expr, function=function) + ' = eps')]
        state, expr, function, _, _ = query((b'\0', 1), b'\x001')
        checks += [('source0 a NUL STRING leaf cannot enter through an admitted INT sibling',
                    value(state, expr, function=function) + ' = eps')]
        _, expr, _, _, answer = query((MAXIMUM, b''), b'9223372036854775807')
        checks += [('source0 exact integer decimal text is independent of parser precision',
                    CONJ.join('$parser_literal_at(' + expr + ', ' + precision + ') = (' + plain(answer) + ')'
                              for precision in ['$(-1)', '0', '1', '14', '30']))]
        old = previous.query(('NScalarInt (INTEGER 1) (eps)', b''), b'1')
        checks += [('source0 the exact affected old147 INT1 query is promoted once through its original builder',
                    previous.compiled(old))]
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = current.lifecycle(name, fixture, path)
    checks += [('the INT-derived STRING and strict scalar result survive real formal/native-cell retirement',
                'S_handler.RESULT = KNOWN (' + current.root_value(name) + ')' + CONJ + 'S.RESULT = KNOWN PNULL' + CONJ +
                value('S', current.expression(name, 'value')) + ' = (' + current.carrier(name) + ')')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
