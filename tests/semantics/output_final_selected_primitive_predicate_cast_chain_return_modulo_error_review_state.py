#!/usr/bin/env python3
"""Independent quiet primitive predicates, exact tags and cleanup boundaries."""
import base64
import output_final_selected_integer_predicate_cast_chain_return_modulo_error_state as inherited
shared = inherited.current
adapter_fields = ('DETAILS', 'TREES', 'modulo_line', 'converted', 'expression')
pristine_adapter = tuple(getattr(shared, field) for field in adapter_fields)
import output_final_selected_integer_predicate_cast_chain_return_modulo_error_review_state as old141
for field, original in zip(adapter_fields, pristine_adapter):
    setattr(shared, field, original)
import output_final_selected_primitive_predicate_cast_chain_return_modulo_error_state as current
import output_final_selected_primitive_predicate_cast_chain_return_modulo_error_sources as sources

base, control, scaffold = old141.affected, old141.control, old141.scaffold
runner, PREFIX, CONJ = current.runner, scaffold.PREFIX, current.CONJ
CASES = {name: sources.CASES['native-selected-primitive-predicate-cast-chain-return-modulo-error-' + name]
         for name in ['deprecated-both-cv-pair-folded-bool-identical-true',
                      'warning-right-cv-pair-folded-null-bool-notequal-false',
                      'deprecated-both-cv-pair-emitted-string-bool-xor-false']}
value = old141.value


def integer(number):
    text = '$(' + str(number) + ')' if number < 0 else str(number)
    return old141.integer(text)


def constant(name):
    payload = base64.b64encode(name.encode()).decode()
    typed = {'true': 'PBOOL true', 'false': 'PBOOL false', 'null': 'PNULL'}[name]
    return ('NExprConstFetch (NName (BYTES "' + payload + '") {metadata}) {metadata}', typed, typed)


def string(text):
    raw = text.encode() if isinstance(text, str) else text
    payload = base64.b64encode(raw).decode()
    data = '[' + ', '.join(map(str, raw)) + ']' if raw else 'eps'
    return ('NScalarString (BYTES "' + payload + '") {metadata}',
            'PSTRING_CARRIER INTERNED_STRING (' + data + ')', 'PSTRING (' + data + ')')


def floating(bits):
    typed = 'PFLOAT ' + str(int(bits, 16))
    return ('NScalarFloat (FLOAT "' + bits + '") {metadata}', typed, typed)


def binary(kind, left, right, pooled):
    constructor, operator = old141.OPERATORS[kind]
    rows, codes, facts, expressions, values = [], [], [], [], []
    for side, (node, typed, fact) in [('left', left), ('right', right)]:
        path, line = 'pcpath_value_' + side, 'z_value_' + side
        metadata = '([(MstartLine ' + line + ')])'
        child = node.format(metadata=metadata)
        rows += [(path, child)]
        if 'NExprConstFetch' in child:
            rows += [('(' + path + ' ++ [PCFIELD 0])',
                      child[len('NExprConstFetch ('):].removesuffix(') ' + metadata))]
        codes += [(path, line, 'true')]
        facts += [(path, fact)]
        expressions += [child]
        values += [typed]
    expression = constructor + ' (' + expressions[0] + ') (' + expressions[1] + ') ([(MstartLine z_value_left)])'
    state, function = scaffold.changed([('pcpath_value', expression), *rows],
        [('pcpath_value', 'z_value_right', 'true'), *codes], [('pcpath_value', pooled), *facts])
    return state, expression, function, operator, expressions, values


NULL, FALSE, TRUE = [constant(name) for name in ['null', 'false', 'true']]
ZERO, ONE = integer(0), integer(1)
FLOAT0, FLOAT1, NZERO = [floating(bits) for bits in ['0000000000000000', '3ff0000000000000', '8000000000000000']]
NAN, INF = floating('7ff8000000000000'), floating('7ff0000000000000')
QUERIES = {
 'identical': [(TRUE, TRUE, True), (NULL, NULL, True), (TRUE, ONE, False),
               (FLOAT1, ONE, False), (string('1'), ONE, False), (NZERO, FLOAT0, True), (NAN, NAN, False)],
 'notidentical': [(FALSE, ZERO, True), (NULL, FALSE, True), (string('0'), string('0'), False), (NAN, NAN, True)],
 'equal': [(string('seven'), ZERO, False), (string('0'), ZERO, True), (string(''), ZERO, False),
           (string('01'), ONE, True), (NULL, string(''), True), (NULL, string('0'), False),
           (NULL, FALSE, True), (TRUE, integer(2), True), (NAN, TRUE, True), (INF, string('INF'), True)],
 'notequal': [(NULL, FALSE, False), (FALSE, string('0'), False), (TRUE, string('00'), False), (NAN, FALSE, True)],
 'less': [(NULL, string('0'), True), (string('2'), string('10'), True), (string('a'), integer(99), False),
          (string(''), ZERO, True), (NULL, NAN, True), (FLOAT0, NZERO, False)],
 'lessequal': [(FLOAT1, ZERO, False), (FLOAT1, ONE, True), (NAN, TRUE, True),
               (string('10'), string('2'), False), (NZERO, FALSE, True)],
 'greater': [(string('10'), string('2'), True), (string('2'), string('10'), False),
             (string('a'), integer(99), True), (NAN, NULL, True), (FLOAT1, ONE, False),
             (floating('4340000000000000'), integer(9007199254740993), False)],
 'greaterequal': [(string('a'), integer(99), True), (string(''), NULL, True),
                  (TRUE, NAN, True), (FLOAT0, NZERO, True), (ONE, FLOAT1, True)],
 'xor': [(NULL, TRUE, True), (FALSE, string('0'), False), (TRUE, string('00'), False),
         (NZERO, FALSE, False), (string('0'), string('00'), True), (string('0e0'), string('0'), True),
         (string(''), ZERO, False), (FLOAT1, NULL, True)]}


def frontier(name, fixture, path):
    bindings, checks = base.frontier(name, fixture, path)
    checks = [(label.replace('signed64 integer tag', 'primitive predicate Boolean tag').replace('arithmetic', 'primitive predicate'), condition)
              for label, condition in checks]
    nodes = current.nodes(name)
    checks += [('the actual proper primitive predicate retains its exact BOOL result before outer casts',
                value('S', current.expression(name, 'value')) + ' = (' + nodes['value'][3] + ')')]
    for key, node in nodes.items():
        if node[4] and node[3].startswith('PBOOL '):
            wrong = 'PINT 1' if node[3] == 'PBOOL true' else 'PINT 0'
            checks += [('a same-truth integer fact cannot replace the proper Boolean at ' + key,
                        '~' + control.tail(control.pool_state('pcpath_' + key, wrong)))]
        if node[0] == 'constant':
            name_path = '(pcpath_' + key + ' ++ [PCFIELD 0])'
            state = ('S[.SOURCES = pcunit_handler[.OCCURRENCES = '
                     '$or131_drop(pcunit_handler.OCCURRENCES, ' + name_path + ')] :: S.SOURCES]')
            checks += [('the indexed primitive keyword name remains genuine SOURCE without a CODE/pool shortcut',
                        '$code_expression(pfunction_handler.CODE.EXPRESSIONS, ' + name_path + ') = eps /\\ ~' + control.tail(state))]
    if current.DETAILS[name][1] == 'folded-bool-identical-true':
        for kind, pairs in QUERIES.items():
            for left, right, answer in pairs:
                result = 'PBOOL ' + str(answer).lower()
                checks += [('source0 ' + kind + ' keeps genuine primitive tags, ordering and truth',
                            old141.proof(binary(kind, left, right, result), result))]
            left, right, answer = pairs[0]
            result = 'PBOOL ' + str(answer).lower()
            for wrong in ['PINT 1' if answer else 'PINT 0', 'PBOOL ' + str(not answer).lower()]:
                checks += [('source0 ' + kind + ' refuses a same-truth INT or incorrect BOOL folded result',
                            old141.proof(binary(kind, left, right, wrong), result, False))]
        # The five existing old141 mixed queries are exercised through their actual builder.
        old_string = ('NScalarString (BYTES "Mg==") {metadata}',
                      'PSTRING_CARRIER INTERNED_STRING ($ptascii("2"))', 'PSTRING ($ptascii("2"))')
        for kind, left, right, result in [
                ('identical', TRUE, old141.integer('1'), 'PBOOL false'),
                ('equal', TRUE, old141.integer('1'), 'PBOOL true'),
                ('less', NULL, old141.integer('1'), 'PBOOL true'),
                ('greaterequal', FLOAT1, old141.integer('1'), 'PBOOL true'),
                ('xor', old141.integer('0'), old_string, 'PBOOL true')]:
            checks += [('source0 actual old141 ' + kind + ' mixed primitive query is now admitted',
                        old141.proof(old141.binary(kind, left, right, result), result))]
        for left, right in [(NAN, FALSE), (FALSE, NAN)]:
            state, expression, function, operator, children, values = binary('xor', left, right, 'PBOOL true')
            quiet = state + '[.ERRORHANDLER = {CALLBACK eps, LEVELS 0}][.REPORTING = 0][.ERRORFATALTRACE = eps][.SOURCEPENDING = eps]'
            visible = quiet + '[.REPORTING = 2]'
            eligible = state + '[.ERRORHANDLER.LEVELS = 2][.REPORTING = 0][.ERRORFATALTRACE = eps][.SOURCEPENDING = eps]'
            call = lambda context: '$binary_apply(' + context + '[.RESULT = KNOWN (' + values[1] + ')], LOGICALXOR, ' + values[0] + ', ' + values[1] + ', z_value_right)'
            checks += [('source0 visible NaN XOR changes the full state and cannot borrow a Boolean result cache',
                        call(visible) + ' =/= ' + visible + '[.RESULT = KNOWN (PBOOL true)] /\\ ' +
                        value(visible, expression, function=function) + ' = eps'),
                       ('source0 a masked eligible NaN XOR handler still requires its producer continuation',
                        '$error_handler_eligible(' + eligible + ', 2) /\\ ' + call(eligible) + '.COMPLETION = UNSUPPORTED "error-handler ingress requires a producer continuation" /\\ ' +
                        value(eligible, expression, function=function) + ' = eps'),
                       ('source0 a masked unhandled NaN XOR is admitted only as an exact quiet full-state operation',
                        call(quiet) + ' = ' + quiet + '[.RESULT = KNOWN (PBOOL true)] /\\ ' +
                        value(quiet, expression, function=function) + ' = (PBOOL true)')]
        wrong_float = (*floating('3ff0000000000000')[:2], 'PFLOAT 0')
        for leaf in [string(b'a\0'), wrong_float]:
            state, expression, function, operator, children, values = binary('equal', leaf, ZERO, 'PBOOL false')
            checks += [('source0 selected NUL bytes and mismatched canonical FLOAT facts cannot enter through generic primitive admission',
                        value(state, children[0], 'PORIGIN n_cast_handler pcpath_value_left', function) + ' = eps /\\ ' +
                        value(state, expression, function=function) + ' = eps')]
        for owning in ['PARRAY 0', 'POBJECT 0']:
            leaf = ('NScalarInt (INTEGER 0) {metadata}', owning, owning)
            state, expression, function, operator, children, values = binary('equal', leaf, ZERO, 'PBOOL true')
            checks += [('source0 an owning forged child fact cannot borrow proper primitive/nonowner authority',
                        '$value_nodes(' + owning + ') =/= eps /\\ ' +
                        value(state, children[0], 'PORIGIN n_cast_handler pcpath_value_left', function) + ' = eps /\\ ' +
                        value(state, expression, function=function) + ' = eps')]
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = base.lifecycle(name, fixture, path)
    checks = [(label.replace('arithmetic', 'primitive predicate'), condition) for label, condition in checks]
    checks += [('proper primitive predicate and outer tags survive real callback formal/native-cell retirement',
                'S_handler.RESULT = KNOWN (' + current.root_value(name) + ') /\\ S.RESULT = KNOWN PNULL /\\ ' +
                value('S', current.expression(name, 'value')) + ' = (' + current.nodes(name)['value'][3] + ')')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
