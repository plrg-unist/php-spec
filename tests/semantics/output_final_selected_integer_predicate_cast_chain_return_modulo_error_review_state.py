#!/usr/bin/env python3
"""Independent Boolean integer predicates, typed facts and retirement controls."""
import output_final_selected_integer_arithmetic_cast_chain_return_modulo_error_review_state as affected
# The old query builder imports a state adapter that changes shared arithmetic data.
shared = affected.current
adapter_fields = ('DETAILS', 'TREES', 'modulo_line', 'converted')
pristine_adapter = tuple(getattr(shared, field) for field in adapter_fields)
import output_final_selected_integer_spaceship_cast_chain_return_modulo_error_review_state as old140
for field, original in zip(adapter_fields, pristine_adapter):
    setattr(shared, field, original)
import output_final_selected_integer_predicate_cast_chain_return_modulo_error_state as current
import output_final_selected_integer_predicate_cast_chain_return_modulo_error_sources as sources

control, scaffold = affected.control, affected.scaffold
runner, PREFIX, CONJ = current.runner, scaffold.PREFIX, current.CONJ
CASES = {name: sources.CASES['native-selected-integer-predicate-cast-chain-return-modulo-error-' + name]
         for name in ['warning-left-constant-folded-less-true',
                      'warning-left-constant-emitted-greater-false',
                      'warning-deprecated-constant-float-emitted-greaterequal-true',
                      'deprecated-both-cv-pair-emitted-xor-false']}
OPERATORS = {
    'identical': ('NExprBinaryOpIdentical', 'IDENTICAL'),
    'notidentical': ('NExprBinaryOpNotIdentical', 'NOTIDENTICAL'),
    'equal': ('NExprBinaryOpEqual', 'EQUAL'),
    'notequal': ('NExprBinaryOpNotEqual', 'NOTEQUAL'),
    'less': ('NExprBinaryOpSmaller', 'LESS'),
    'lessequal': ('NExprBinaryOpSmallerOrEqual', 'LESSEQUAL'),
    'greater': ('NExprBinaryOpGreater', 'GREATER'),
    'greaterequal': ('NExprBinaryOpGreaterOrEqual', 'GREATEREQUAL'),
    'xor': ('NExprBinaryOpLogicalXor', 'LOGICALXOR')}


def value(state, expression, origin='porigin_value', function='pfunction_handler'):
    return scaffold.value(state, expression, origin, function)


def integer(number):
    number = '$(' + str(number) + ')' if isinstance(number, int) and number < 0 else str(number)
    return affected.integer(number)


def binary(kind, left, right, pooled):
    constructor, operator = OPERATORS[kind]
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


def proof(query, result, admitted=True):
    state, expression, function, operator, children, values = query
    parts = [value(state, child, 'PORIGIN n_cast_handler pcpath_value_' + side, function) + ' = (' + typed + ')'
             for side, child, typed in zip(['left', 'right'], children, values)]
    parts += ['$binary_apply(' + state + '[.RESULT = KNOWN (' + values[1] + ')], ' + operator + ', ' +
              values[0] + ', ' + values[1] + ', z_value_right) = ' + state + '[.RESULT = KNOWN (' + result + ')]',
              value(state, expression, function=function) + (' = (' + result + ')' if admitted else ' = eps')]
    return CONJ.join(parts)


def expected(kind, left, right):
    if kind in ('identical', 'equal'):
        answer = left == right
    elif kind in ('notidentical', 'notequal'):
        answer = left != right
    elif kind == 'less':
        answer = left < right
    elif kind == 'lessequal':
        answer = left <= right
    elif kind == 'greater':
        answer = left > right
    elif kind == 'greaterequal':
        answer = left >= right
    else:
        answer = bool(left) != bool(right)
    return 'PBOOL ' + str(answer).lower()


def frontier(name, fixture, path):
    bindings, checks = affected.frontier(name, fixture, path)
    checks = [(label.replace('signed64 integer tag', 'Boolean tag').replace('arithmetic', 'predicate'), condition)
              for label, condition in checks]
    nodes = current.nodes(name)
    expression, result = current.expression(name, 'value'), nodes['value'][3]
    checks += [('the actual predicate remains BOOL before either outer cast, with no value owner',
                value('S', expression) + ' = (' + result + ') /\\ $value_nodes(' + result + ') = eps'),
               ('a same-truth INT cannot replace the actual BOOL predicate result',
                value('S', expression) + ' =/= (' + ('PINT 1' if result == 'PBOOL true' else 'PINT 0') + ')')]
    if not nodes['value'][4]:
        checks += [('emitted GT, GE and XOR retain left-to-right source children and the RHS terminal compiler line',
                    'z_value = z_value_right /\\ z_value_left =/= z_value_right /\\ '
                    'pcpath_value_left = pcpath_value ++ [PCFIELD 0] /\\ '
                    'pcpath_value_right = pcpath_value ++ [PCFIELD 1]')]
    if current.DETAILS[name][1] == 'folded-less-true':
        minimum, maximum = -(2 ** 63), 2 ** 63 - 1
        pairs = [(0, 0), (1, 2), (2, 1), (minimum, maximum), (maximum, minimum),
                 (minimum, minimum), (maximum, maximum)]
        for kind in OPERATORS:
            selected = [(0, 0), (0, 2), (2, 0), (2, 4), (minimum, maximum), (minimum, 0)] if kind == 'xor' else pairs
            for left, right in selected:
                result = expected(kind, left, right)
                query = binary(kind, integer(left), integer(right), result)
                checks += [('source0 ' + kind + ' keeps strict BOOL equal/reversed/MIN/MAX or zero/nonzero truth', proof(query, result))]
            result = expected(kind, 1, 2)
            for wrong in ['PINT 1' if result == 'PBOOL true' else 'PINT 0',
                          'PBOOL false' if result == 'PBOOL true' else 'PBOOL true']:
                query = binary(kind, integer(1), integer(2), wrong)
                checks += [('source0 ' + kind + ' refuses a same-truth INT or wrong Boolean folded fact', proof(query, result, False))]
        # Exercise precisely the three original old140 promotion builders, once each.
        for constructor, operator, left, right, result in [
                ('NExprBinaryOpEqual', 'EQUAL', '2', '2', 'PBOOL true'),
                ('NExprBinaryOpSmaller', 'LESS', '1', '2', 'PBOOL true'),
                ('NExprBinaryOpGreater', 'GREATER', '1', '2', 'PBOOL false')]:
            state, expression, function, children, values = old140.binary(old140.integer(left), old140.integer(right), result)
            state, expression, function = [part.replace('NExprBinaryOpSpaceship', constructor)
                                           for part in [state, expression, function]]
            query = state, expression, function, operator, children, values
            checks += [('source0 actual old140 ' + operator + ' Boolean query builder is now admitted', proof(query, result))]
        true = ('NExprConstFetch (NName (BYTES "dHJ1ZQ==") {metadata}) {metadata}', 'PBOOL true', 'PBOOL true')
        null = ('NExprConstFetch (NName (BYTES "bnVsbA==") {metadata}) {metadata}', 'PNULL', 'PNULL')
        floating = ('NScalarFloat (FLOAT "3ff0000000000000") {metadata}',
                    'PFLOAT 4607182418800017408', 'PFLOAT 4607182418800017408')
        string = ('NScalarString (BYTES "Mg==") {metadata}',
                  'PSTRING_CARRIER INTERNED_STRING ($ptascii("2"))', 'PSTRING ($ptascii("2"))')
        for kind, left, right, result in [
                ('identical', true, integer(1), 'PBOOL false'),
                ('equal', true, integer(1), 'PBOOL true'),
                ('less', null, integer(1), 'PBOOL true'),
                ('greaterequal', floating, integer(1), 'PBOOL true'),
                ('xor', integer(0), string, 'PBOOL true')]:
            query = binary(kind, left, right, result)
            checks += [('source0 genuine quiet mixed primitive children retain exact Boolean predicate authority', proof(query, result))]
        query = binary('equal', integer(1), integer(1), 'PFLOAT 4607182418800017408')
        checks += [('source0 FLOAT one cannot replace a strict Boolean folded equality fact', proof(query, 'PBOOL true', False))]
        state, expression, function, _, children, _ = binary('equal', integer(2 ** 63), integer(0), 'PBOOL false')
        checks += [('source0 an out-of-range raw integer cannot borrow signed64 proper-child authority',
                    value(state, children[0], 'PORIGIN n_cast_handler pcpath_value_left', function) + ' = eps /\\ ' +
                    value(state, expression, function=function) + ' = eps')]
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = affected.lifecycle(name, fixture, path)
    checks = [(label.replace('arithmetic', 'predicate'), condition) for label, condition in checks]
    checks += [('the strict BOOL predicate and exact outer result survive actual formal/native-cell retirement',
                'S_handler.RESULT = KNOWN (' + current.root_value(name) + ') /\\ S.RESULT = KNOWN PNULL /\\ ' +
                value('S', current.expression(name, 'value')) + ' = (' + current.nodes(name)['value'][3] + ')')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
