#!/usr/bin/env python3
"""Independent exact FLOAT results, affected builders and quiet-state fences."""
import output_final_selected_primitive_integer_cast_chain_return_modulo_error_review_state as integers
shared = integers.current.current
adapter_fields = ('DETAILS', 'TREES', 'modulo_line', 'converted', 'expression')
pristine_adapter = tuple(getattr(shared, field) for field in adapter_fields)
import output_final_selected_integer_arithmetic_cast_chain_return_modulo_error_review_state as arithmetic
import output_final_selected_integer_division_cast_chain_return_modulo_error_review_state as division
import output_final_selected_integer_power_cast_chain_return_modulo_error_review_state as power
for field, original in zip(adapter_fields, pristine_adapter):
    setattr(shared, field, original)
import output_final_selected_primitive_float_cast_chain_return_modulo_error_state as current
import output_final_selected_primitive_float_cast_chain_return_modulo_error_sources as sources

base, control, scaffold = integers.base, integers.control, integers.scaffold
runner, PREFIX, CONJ = current.runner, scaffold.PREFIX, current.CONJ
value, integer, constant, string, floating = integers.value, integers.integer, integers.constant, integers.string, integers.floating
binary, proof = integers.binary, integers.primitive.old141.proof
CASES = {name: sources.CASES['native-selected-primitive-float-cast-chain-return-modulo-error-' + name]
         for name in ['warning-right-cv-pair-folded-float-string-multiply-three',
                      'deprecated-both-cv-pair-folded-bool-integer-divide-half',
                      'warning-deprecated-constant-float-emitted-float-power-one']}
NULL, FALSE, TRUE = [constant(name) for name in ['null', 'false', 'true']]
F0, F1, F2, FHALF, NEGZERO = [floating(bits) for bits in
    ['0000000000000000', '3ff0000000000000', '4000000000000000', '3fe0000000000000', '8000000000000000']]
INF, NAN = floating('7ff0000000000000'), floating('7ff800000000002a')
FINITE = {
 'add': (F1, TRUE, F2[1]), 'sub': (integer(1), F1, F0[1]),
 'mul': (floating('3ff8000000000000'), string('2'), 'PFLOAT 4613937818241073152'),
 'div': (TRUE, integer(2), FHALF[1]), 'pow': (F1, integer(3), F1[1])}


def predecessor_queries():
    i = arithmetic.integer
    for kind, left, right, result in [
            ('add', i('9223372036854775807'), i('1'), 'PFLOAT 4890909195324358656'),
            ('sub', i('$(-9223372036854775808)'), i('1'), 'PFLOAT 14114281232179134464'),
            ('mul', i('$(-9223372036854775808)'), i('$(-1)'), 'PFLOAT 4890909195324358656'),
            ('mul', F1, i('2'), F2[1])]:
        yield 'arithmetic', arithmetic.binary(kind, left, right, result), result
    for left, right, result in [(i('2'), i('4'), FHALF[1]),
                               (i('$(-9223372036854775808)'), i('$(-1)'), 'PFLOAT 4890909195324358656'),
                               (F1, i('1'), F1[1])]:
        yield 'division', division.affected.binary('div', left, right, result), result
    for left, right, result in [('2', '63', 'PFLOAT 4890909195324358656'),
                                ('$(-9223372036854775808)', '2', 'PFLOAT 5174635971848699904'),
                                ('2', '$(-1)', FHALF[1]), ('$(-1)', '$(-1)', 'PFLOAT 13830554455654793216'),
                                ('1', '$(-9223372036854775808)', F1[1])]:
        state, expression, function, children, values = power.binary(i(left), i(right), result)
        yield 'power', (state, expression, function, 'POWER', children, values), result
    state, expression, function, children, values = power.binary(F1, i('3'), F1[1])
    yield 'power', (state, expression, function, 'POWER', children, values), F1[1]
    for family, query, result in integers.predecessor_queries():
        if result.startswith('PFLOAT '):
            yield 'primitive-integer-' + family, query, result
    for kind, left, right, result in [
            ('add', F1, TRUE, F2[1]), ('sub', integer(1), F1, F0[1]),
            ('div', TRUE, integer(2), FHALF[1]), ('pow', F1, integer(3), F1[1]),
            ('add', string('9223372036854775807'), TRUE, 'PFLOAT 4890909195324358656')]:
        yield 'primitive-integer', integers.binary(kind, left, right, result), result


def frontier(name, fixture, path):
    bindings, checks = base.frontier(name, fixture, path)
    checks = [(label.replace('signed64 integer tag', 'exact FLOAT tag').replace('arithmetic', 'primitive FLOAT'), condition)
              for label, condition in checks]
    nodes = current.nodes(name)
    result = nodes['value'][3]
    checks += [('the actual inner result is exact PFLOAT before either outer cast and has no owner',
                CONJ.join([value('S', current.expression(name, 'value')) + ' = (' + result + ')',
                           '$value_nodes(' + result + ') = eps',
                           value('S', current.expression(name, 'value')) + ' =/= (PBOOL true)']))]
    for key, node in nodes.items():
        if node[4] and node[3].startswith('PFLOAT '):
            for wrong in ['PINT 0', 'PBOOL true', 'PFLOAT ' + str(int(node[3].split()[1]) + 1)]:
                checks += [('a wrong tag or adjacent FLOAT bit fact cannot certify ' + key,
                            '~' + control.tail(control.pool_state('pcpath_' + key, wrong)))]
        if node[0] == 'constant':
            name_path = '(pcpath_' + key + ' ++ [PCFIELD 0])'
            state = 'S[.SOURCES = pcunit_handler[.OCCURRENCES = $or131_drop(pcunit_handler.OCCURRENCES, ' + name_path + ')] :: S.SOURCES]'
            checks += [('a primitive keyword retains its own indexed Name source', '~' + control.tail(state))]
    if current.DETAILS[name][1] == 'folded-float-string-multiply-three':
        for kind, (left, right, result) in FINITE.items():
            checks += [('source0 ' + kind + ' retains quiet primitive coercion and an exact FLOAT result',
                        proof(binary(kind, left, right, result), result))]
            for wrong in ['PINT 0', 'PBOOL true', 'PFLOAT ' + str(int(result.split()[1]) + 1)]:
                checks += [('source0 ' + kind + ' refuses wrong INT/BOOL tags and incorrect FLOAT bits',
                            proof(binary(kind, left, right, wrong), result, False))]
        old = list(predecessor_queries())
        assert len(old) == 21
        for family, query, result in old:
            checks += [('source0 actual old ' + family + ' FLOAT expectation instance is admitted with exact bits', proof(query, result))]
        # Canonical raw literals below are constructed-state observations, not extra source/native agreements.
        for kind, left, right, bits in [
                ('sub', F1, F2, 'bff0000000000000'), ('div', integer(-1), F2, 'bfe0000000000000'),
                ('add', NEGZERO, NEGZERO, '8000000000000000'), ('add', NEGZERO, F0, '0000000000000000'),
                ('sub', NEGZERO, F0, '8000000000000000'), ('mul', NEGZERO, floating('bff0000000000000'), '0000000000000000'),
                ('div', NEGZERO, F1, '8000000000000000'), ('pow', NEGZERO, integer(3), '8000000000000000'),
                ('add', floating('7fefffffffffffff'), floating('7fefffffffffffff'), '7ff0000000000000'),
                ('div', floating('0010000000000000'), F2, '0008000000000000'),
                ('add', NAN, F1, '7ff800000000002a'), ('sub', F1, NAN, '7ff800000000002a'),
                ('add', floating('7ff000000000002a'), F1, '7ff800000000002a'),
                ('mul', INF, F0, 'fff8000000000000'), ('pow', F1, NAN, '3ff0000000000000')]:
            result = floating(bits)[1]
            checks += [('source0 ' + kind + ' preserves order, signed zero, subnormal, nonfinite or NaN payload bits',
                        proof(binary(kind, left, right, result), result))]
        for left, right, exact, wrong in [(NEGZERO, NEGZERO, NEGZERO[1], F0[1]),
                                          (NAN, F1, NAN[1], floating('7ff800000000002b')[1])]:
            checks += [('source0 PHP-equal zero or NaN categories cannot replace the exact cached FLOAT bits',
                        proof(binary('add', left, right, wrong), exact, False))]
        for leaf in [NAN, INF]:
            typed = leaf[1]
            checks += [('source0 FLOAT casts retain exact nonfinite bits while existing quiet INT gates refuse them',
                        CONJ.join(['$ob_object_cast_chain_quiet(CASTFLOAT, ' + typed + ')',
                                   '$cast_apply(S[.RESULT = KNOWN (' + typed + ')], CASTFLOAT, ' + typed + ', z_value) = S[.RESULT = KNOWN (' + typed + ')]',
                                   '~$ob_object_cast_chain_quiet(CASTINT, ' + typed + ')']))]
        checks += [('source0 quiet arithmetic NaN does not authorize a warningful Boolean cast',
                    '~$ob_object_cast_chain_quiet(CASTBOOL, ' + NAN[1] + ')')]
        state, expression, function, operator, children, values = binary('pow', integer(0), integer(-1), INF[1])
        quiet = state + '[.ERRORHANDLER = {CALLBACK eps, LEVELS 0}][.REPORTING = 0][.ERRORFATALTRACE = eps][.SOURCEPENDING = eps]'
        visible = quiet + '[.REPORTING = 8192]'
        eligible = state + '[.ERRORHANDLER.LEVELS = 8192][.REPORTING = 0][.ERRORFATALTRACE = eps][.SOURCEPENDING = eps]'
        call = lambda context: '$binary_apply(' + context + '[.RESULT = KNOWN (PINT $(-1))], POWER, PINT 0, PINT $(-1), z_value_right)'
        checks += [('source0 visible zero-negative power changes the full state despite an exact INF fact',
                    CONJ.join([call(visible) + ' =/= ' + visible + '[.RESULT = KNOWN (' + INF[1] + ')]', value(visible, expression, function=function) + ' = eps'])),
                   ('source0 a masked eligible zero-negative power handler still requires its producer continuation',
                    CONJ.join(['$error_handler_eligible(' + eligible + ', 8192)', call(eligible) + '.COMPLETION = UNSUPPORTED "error-handler ingress requires a producer continuation"',
                               value(eligible, expression, function=function) + ' = eps'])),
                   ('source0 masked unhandled power admits only exact quiet full-state INF authority',
                    CONJ.join([call(quiet) + ' = ' + quiet + '[.RESULT = KNOWN (' + INF[1] + ')]', value(quiet, expression, function=function) + ' = (' + INF[1] + ')']))]
        for kind, left, right, error, message in [
                ('div', F1, FALSE, 'DivisionByZeroError', 'Division by zero'),
                ('add', string('seven'), F1, 'TypeError', 'Unsupported operand types: string + float')]:
            state, expression, function, operator, children, values = binary(kind, left, right, F0[1])
            call = '$binary_apply(' + state + '[.RESULT = KNOWN (' + values[1] + ')], ' + operator + ', ' + values[0] + ', ' + values[1] + ', z_value_right)'
            checks += [('source0 an exact-looking FLOAT fact cannot erase genuine arithmetic/type failure',
                        CONJ.join([call + '.COMPLETION = THROWN "' + error + '" ($ptascii("' + message + '")) z_value_right', value(state, expression, function=function) + ' = eps']))]
        wrong_float = (*F1[:2], F0[1])
        for leaf in [string(b'a\0'), wrong_float]:
            state, expression, function, operator, children, values = binary('add', leaf, F1, F2[1])
            checks += [('source0 NUL strings and mismatched canonical FLOAT leaf facts cannot enter the proper primitive rule',
                        CONJ.join([value(state, children[0], 'PORIGIN n_cast_handler pcpath_value_left', function) + ' = eps', value(state, expression, function=function) + ' = eps']))]
        for owning in ['PARRAY 0', 'POBJECT 0']:
            query = binary('add', ('NScalarInt (INTEGER 0) {metadata}', owning, owning), F1, F1[1])
            state, expression, function, operator, children, values = query
            checks += [('source0 an owning child cannot borrow primitive or nonowner authority',
                        CONJ.join(['$value_nodes(' + owning + ') =/= eps', value(state, children[0], 'PORIGIN n_cast_handler pcpath_value_left', function) + ' = eps', value(state, expression, function=function) + ' = eps']))]
        checks += [('source0 a forged out-of-range FLOAT result fact cannot replace actual canonical bits',
                    proof(binary('add', F1, TRUE, 'PFLOAT 18446744073709551616'), F2[1], False))]
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = base.lifecycle(name, fixture, path)
    checks = [(label.replace('arithmetic', 'primitive FLOAT'), condition) for label, condition in checks]
    checks += [('proper primitive FLOAT and both outer tags survive actual formal/native-cell retirement',
                CONJ.join(['S_handler.RESULT = KNOWN (' + current.root_value(name) + ')', 'S.RESULT = KNOWN PNULL',
                           value('S', current.expression(name, 'value')) + ' = (' + current.nodes(name)['value'][3] + ')']))]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
