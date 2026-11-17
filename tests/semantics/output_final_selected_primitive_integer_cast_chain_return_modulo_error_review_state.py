#!/usr/bin/env python3
"""Independent signed integer results over certified primitive children."""
import base64
import output_final_selected_primitive_predicate_cast_chain_return_modulo_error_review_state as primitive
shared = primitive.current.current
adapter_fields = ('DETAILS', 'TREES', 'modulo_line', 'converted', 'expression')
pristine_adapter = tuple(getattr(shared, field) for field in adapter_fields)
import output_final_selected_integer_arithmetic_cast_chain_return_modulo_error_review_state as arithmetic
import output_final_selected_integer_division_cast_chain_return_modulo_error_review_state as division
import output_final_selected_integer_remainder_cast_chain_return_modulo_error_review_state as remainder
import output_final_selected_integer_shift_cast_chain_return_modulo_error_review_state as shift
import output_final_selected_integer_power_cast_chain_return_modulo_error_review_state as power
import output_final_selected_integer_spaceship_cast_chain_return_modulo_error_review_state as spaceship
for field, original in zip(adapter_fields, pristine_adapter):
    setattr(shared, field, original)
import output_final_selected_primitive_integer_cast_chain_return_modulo_error_state as current
import output_final_selected_primitive_integer_cast_chain_return_modulo_error_sources as sources

base, control, scaffold = primitive.base, primitive.control, primitive.scaffold
runner, PREFIX, CONJ = current.runner, scaffold.PREFIX, current.CONJ
value, integer, constant, string, floating = primitive.value, primitive.integer, primitive.constant, primitive.string, primitive.floating
CASES = {name: sources.CASES['native-selected-primitive-integer-cast-chain-return-modulo-error-' + name]
         for name in ['deprecated-both-cv-pair-folded-bool-null-add-one',
                      'warning-right-cv-pair-emitted-string-bool-divide-six',
                      'deprecated-both-cv-pair-folded-mixed-power-spaceship-zero']}
OPERATORS = {
 'add': ('NExprBinaryOpPlus', 'ADD'), 'sub': ('NExprBinaryOpMinus', 'SUBTRACT'),
 'mul': ('NExprBinaryOpMul', 'MULTIPLY'), 'div': ('NExprBinaryOpDiv', 'DIVIDE'),
 'mod': ('NExprBinaryOpMod', 'MODULO'), 'shl': ('NExprBinaryOpShiftLeft', 'SHIFTLEFT'),
 'shr': ('NExprBinaryOpShiftRight', 'SHIFTRIGHT'), 'and': ('NExprBinaryOpBitwiseAnd', 'BITAND'),
 'or': ('NExprBinaryOpBitwiseOr', 'BITOR'), 'xor': ('NExprBinaryOpBitwiseXor', 'BITXOR'),
 'pow': ('NExprBinaryOpPow', 'POWER'), 'space': ('NExprBinaryOpSpaceship', 'SPACESHIP')}


def binary(kind, left, right, pooled):
    constructor, operator = OPERATORS[kind]
    rows, codes, facts, expressions, values = [], [], [], [], []
    for side, (node, typed, fact) in [('left', left), ('right', right)]:
        path, line = 'pcpath_value_' + side, 'z_value_' + side
        metadata = '([(MstartLine ' + line + ')])'
        child = node.format(metadata=metadata)
        rows += [(path, child)]
        if 'NExprConstFetch' in child:
            rows += [('(' + path + ' ++ [PCFIELD 0])', child[len('NExprConstFetch ('):].removesuffix(') ' + metadata))]
        codes += [(path, line, 'true')]
        facts += [(path, fact)]
        expressions += [child]
        values += [typed]
    expression = constructor + ' (' + expressions[0] + ') (' + expressions[1] + ') ([(MstartLine z_value_left)])'
    state, function = scaffold.changed([('pcpath_value', expression), *rows],
        [('pcpath_value', 'z_value_right', 'true'), *codes], [('pcpath_value', pooled), *facts])
    return state, expression, function, operator, expressions, values


def pint(number):
    return 'PINT $(' + str(number) + ')' if number < 0 else 'PINT ' + str(number)


NULL, FALSE, TRUE = [constant(x) for x in ['null', 'false', 'true']]
FLOAT1, FLOAT5 = floating('3ff0000000000000'), floating('4014000000000000')
QUIET = {
 'add': [(TRUE, NULL, 1), (string('2'), FALSE, 2)],
 'sub': [(string('3'), TRUE, 2), (NULL, string('2'), -2)],
 'mul': [(FALSE, string('2'), 0), (string('-2'), TRUE, -2)],
 'div': [(string('6'), TRUE, 6), (NULL, string('2'), 0)],
 'mod': [(FLOAT5, string('2'), 1), (string('-5'), TRUE, 0)],
 'shl': [(string('3'), TRUE, 6), (NULL, FLOAT1, 0)],
 'shr': [(string('8'), FLOAT1, 4), (string('-4'), TRUE, -2)],
 'and': [(string('7'), TRUE, 1), (FLOAT5, integer(3), 1)],
 'or': [(NULL, integer(2), 2), (string('2'), TRUE, 3)],
 'xor': [(NULL, integer(2), 2), (FLOAT5, TRUE, 4)],
 'pow': [(string('2'), TRUE, 2), (NULL, integer(2), 0)],
 'space': [(string('2'), integer(10), -1), (FLOAT1, TRUE, 0)]}


def old_string(text):
    payload = base64.b64encode(text.encode()).decode()
    return ('NScalarString (BYTES "' + payload + '") {metadata}',
            'PSTRING_CARRIER INTERNED_STRING ($ptascii("' + text + '"))', 'PSTRING ($ptascii("' + text + '"))')


def predecessor_queries():
    i, two, three = arithmetic.integer, old_string('2'), old_string('3')
    for kind, left, right, result in [('add', FALSE, i('1'), 'PINT 1'), ('sub', i('1'), NULL, 'PINT 1'),
                                     ('mul', FLOAT1, i('2'), 'PFLOAT 4611686018427387904'), ('add', i('1'), two, 'PINT 3')]:
        yield 'arithmetic', arithmetic.binary(kind, left, right, result), result
    for left, right, result in [(i('1'), TRUE, 'PINT 1'), (NULL, i('1'), 'PINT 0'),
                               (FLOAT1, i('1'), 'PFLOAT 4607182418800017408'), (i('2'), two, 'PINT 1')]:
        yield 'division', division.affected.binary('div', left, right, result), result
    for left, right, result in [(TRUE, i('2'), 'PINT 1'), (NULL, i('1'), 'PINT 0'),
                               (FLOAT1, i('2'), 'PINT 1'), (i('5'), two, 'PINT 1')]:
        state, expression, function, children, values = remainder.binary(left, right, result)
        yield 'remainder', (state, expression, function, 'MODULO', children, values), result
    for kind in ['left', 'right']:
        for left, right, result in [(TRUE, i('1'), 'PINT 2' if kind == 'left' else 'PINT 0'),
                                   (NULL, i('0'), 'PINT 0'), (FLOAT1, i('0'), 'PINT 1'),
                                   (i('4'), two, 'PINT 16' if kind == 'left' else 'PINT 1')]:
            yield 'shift-' + kind, shift.binary(kind, left, right, result), result
    for left, right, result in [(TRUE, i('3'), 'PINT 1'), (NULL, i('2'), 'PINT 0'),
                               (FLOAT1, i('3'), 'PFLOAT 4607182418800017408'), (i('2'), three, 'PINT 8')]:
        state, expression, function, children, values = power.binary(left, right, result)
        yield 'power', (state, expression, function, 'POWER', children, values), result
    for left, right, result in [(TRUE, i('0'), 'PINT 1'), (NULL, i('0'), 'PINT 0'),
                               (FLOAT1, i('1'), 'PINT 0'), (two, i('10'), 'PINT $(-1)')]:
        state, expression, function, children, values = spaceship.binary(left, right, result)
        yield 'spaceship', (state, expression, function, 'SPACESHIP', children, values), result


def frontier(name, fixture, path):
    bindings, checks = base.frontier(name, fixture, path)
    checks = [(label.replace('arithmetic', 'proper primitive integer'), condition) for label, condition in checks]
    nodes = current.nodes(name)
    checks += [('the actual result is signed PINT before outer casts, not a same-truth BOOL',
                CONJ.join([value('S', current.expression(name, 'value')) + ' = (' + nodes['value'][3] + ')',
                           value('S', current.expression(name, 'value')) + ' =/= (PBOOL ' + str(nodes['value'][3] != 'PINT 0').lower() + ')']))]
    for key, node in nodes.items():
        if node[4] and node[3].startswith('PINT '):
            wrong = 'PBOOL false' if node[3] == 'PINT 0' else 'PBOOL true'
            checks += [('a same-truth BOOL folded fact cannot replace signed PINT at ' + key,
                        '~' + control.tail(control.pool_state('pcpath_' + key, wrong)))]
        if node[0] == 'constant':
            name_path = '(pcpath_' + key + ' ++ [PCFIELD 0])'
            state = 'S[.SOURCES = pcunit_handler[.OCCURRENCES = $or131_drop(pcunit_handler.OCCURRENCES, ' + name_path + ')] :: S.SOURCES]'
            checks += [('a primitive keyword keeps its own indexed Name SOURCE', '~' + control.tail(state))]
    if current.DETAILS[name][1] == 'folded-bool-null-add-one':
        for kind, pairs in QUIET.items():
            for left, right, number in pairs:
                result = pint(number)
                checks += [('source0 ' + kind + ' keeps quiet proper primitive coercions and exact signed results',
                            primitive.old141.proof(binary(kind, left, right, result), result))]
            left, right, number = pairs[0]
            for wrong in ['PBOOL false' if number == 0 else 'PBOOL true', pint(number + 1)]:
                checks += [('source0 ' + kind + ' refuses same-truth BOOL and incorrect integer folded facts',
                            primitive.old141.proof(binary(kind, left, right, wrong), pint(number), False))]
        for family, query, result in predecessor_queries():
            checks += [('source0 actual old ' + family + ' builder preserves PINT promotion or its FLOAT refusal',
                        primitive.old141.proof(query, result, result.startswith('PINT ')))]
        for kind, left, right, result in [
                ('add', FLOAT1, TRUE, 'PFLOAT 4611686018427387904'),
                ('sub', integer(1), FLOAT1, 'PFLOAT 0'),
                ('div', TRUE, integer(2), 'PFLOAT 4602678819172646912'),
                ('pow', FLOAT1, integer(3), 'PFLOAT 4607182418800017408'),
                ('add', string('9223372036854775807'), TRUE, 'PFLOAT 4890909195324358656')]:
            checks += [('source0 FLOAT typing or overflow cannot borrow signed PINT authority',
                        primitive.old141.proof(binary(kind, left, right, result), result, False))]
        for kind, left, right, data in [('and', '3', '1', '[49]'), ('or', '2', '1', '[51]'), ('xor', '3', '1', '[2]')]:
            query = binary(kind, string(left), string(right), 'PSTRING (' + data + ')')
            checks += [('source0 both-STRING bytewise results remain STRING even when their bytes resemble integers',
                        primitive.old141.proof(query, 'PSTRING_CARRIER INTERNED_STRING (' + data + ')', False))]
        for kind, left, right, error, message in [
                ('div', TRUE, FALSE, 'DivisionByZeroError', 'Division by zero'),
                ('mod', FLOAT5, NULL, 'DivisionByZeroError', 'Modulo by zero'),
                ('shl', string('1'), integer(-1), 'ArithmeticError', 'Bit shift by negative number'),
                ('add', string('seven'), TRUE, 'TypeError', 'Unsupported operand types: string + bool')]:
            state, expression, function, operator, children, values = binary(kind, left, right, 'PINT 0')
            call = '$binary_apply(' + state + '[.RESULT = KNOWN (' + values[1] + ')], ' + operator + ', ' + values[0] + ', ' + values[1] + ', z_value_right)'
            checks += [('source0 genuine arithmetic/type failure cannot be erased by an integer result fact',
                        CONJ.join([call + '.COMPLETION = THROWN "' + error + '" ($ptascii("' + message + '")) z_value_right',
                                   value(state, expression, function=function) + ' = eps']))]
        for leaf, level, number in [(floating('3ff8000000000000'), 8192, 1), (floating('7ff8000000000000'), 2, 0)]:
            state, expression, function, operator, children, values = binary('mod', leaf, integer(2), pint(number))
            quiet = state + '[.ERRORHANDLER = {CALLBACK eps, LEVELS 0}][.REPORTING = 0][.ERRORFATALTRACE = eps][.SOURCEPENDING = eps]'
            visible = quiet + '[.REPORTING = ' + str(level) + ']'
            eligible = state + '[.ERRORHANDLER.LEVELS = ' + str(level) + '][.REPORTING = 0][.ERRORFATALTRACE = eps][.SOURCEPENDING = eps]'
            call = lambda context: '$binary_apply(' + context + '[.RESULT = KNOWN (PINT 2)], MODULO, ' + values[0] + ', PINT 2, z_value_right)'
            checks += [('source0 visible integer-coercion diagnostics retain their full-state change',
                        CONJ.join([call(visible) + ' =/= ' + visible + '[.RESULT = KNOWN (' + pint(number) + ')]', value(visible, expression, function=function) + ' = eps'])),
                       ('source0 a masked eligible integer-coercion handler still needs its producer continuation',
                        CONJ.join(['$error_handler_eligible(' + eligible + ', ' + str(level) + ')', value(eligible, expression, function=function) + ' = eps'])),
                       ('source0 masked unhandled integer coercion admits only an exact quiet full-state result',
                        CONJ.join([call(quiet) + ' = ' + quiet + '[.RESULT = KNOWN (' + pint(number) + ')]', value(quiet, expression, function=function) + ' = (' + pint(number) + ')']))]
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = base.lifecycle(name, fixture, path)
    checks = [(label.replace('arithmetic', 'proper primitive integer'), condition) for label, condition in checks]
    checks += [('proper primitive signed result and outer tags survive actual formal/native-cell retirement',
                CONJ.join(['S_handler.RESULT = KNOWN (' + current.root_value(name) + ')', 'S.RESULT = KNOWN PNULL',
                           value('S', current.expression(name, 'value')) + ' = (' + current.nodes(name)['value'][3] + ')']))]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
