#!/usr/bin/env python3
"""Emitted one-byte STRING binary results preserve real returns and retirement."""
import output_final_selected_emitted_byte_bitnot_cast_chain_return_modulo_error_state as current
import output_final_selected_emitted_byte_bitwise_cast_chain_return_modulo_error_sources as sources

zero, prior, runner = current.zero, current.prior, current.runner
PREFIX, CONJ = current.PREFIX, current.CONJ
DETAILS = {context + '-' + variant: (context, variant, expected)
           for context, variant, _, _, expected in sources.VARIANTS}
CASES = {name: sources.CASES['native-selected-emitted-byte-bitwise-cast-chain-return-modulo-error-' + name]
         for name in ['warning-left-constant-and-left-full',
                      'warning-deprecated-constant-float-or-left-derived-nul']}
string = current.string


def nodes(name):
    variant = DETAILS[name][1]
    leaf = lambda kind, spelling, value: (kind, spelling, None, value, value is not None, [])
    literal = lambda raw: leaf('string', raw, string(raw))
    keyword = lambda spelling: leaf('constant', spelling, {'true': 'PBOOL true', 'false': 'PBOOL false', 'null': 'PNULL'}.get(spelling))
    full = lambda truth, selected: ('NExprTernary', None, None, selected[3], False,
        [keyword(str(truth).lower()), selected if truth else keyword('UNDEFINED_BYTE_RIGHT'),
         keyword('UNDEFINED_BYTE_LEFT') if truth else selected])
    short = lambda raw, skipped: ('NExprTernary', None, None, string(raw), False,
        [literal(raw), leaf('absent', None, None), keyword(skipped)])
    coalesce = lambda raw, null=False: ('NExprBinaryOpCoalesce', None, None, string(raw), False,
        [keyword('null') if null else literal(raw), literal(raw) if null else keyword('UNDEFINED_BYTE_LEFT')])
    operator, left, right, result = {
        'and-left-full': ('and', full(True, literal(b'3')), literal(b'1'), b'1'),
        'and-right-coalesce': ('and', literal(b'3'), coalesce(b'1', True), b'1'),
        'and-both-selections': ('and', short(b'3', 'UNDEFINED_BYTE_LEFT'), full(False, literal(b'1')), b'1'),
        'or-left-derived-nul': ('or', ('NExprBitwiseNot', None, None, string(b'\0'), False, [coalesce(b'\xff', True)]), literal(b'1'), b'1'),
        'or-right-overlap': ('or', literal(b'3'), full(False, literal(b'1')), b'3'),
        'or-both-selections': ('or', coalesce(b'0'), short(b'1', 'UNDEFINED_BYTE_RIGHT'), b'1'),
        'xor-left-full-zero': ('xor', full(True, literal(b'q')), literal(b'A'), b'0'),
        'xor-right-coalesce-nul': ('xor', literal(b'1'), coalesce(b'1', True), b'\0'),
        'xor-both-selections-nul': ('xor', coalesce(b'1'), full(False, literal(b'1')), b'\0')}[variant]
    kind, spelling = {'and': ('NExprBinaryOpBitwiseAnd', 'BITAND'),
                      'or': ('NExprBinaryOpBitwiseOr', 'BITOR'),
                      'xor': ('NExprBinaryOpBitwiseXor', 'BITXOR')}[operator]
    integer = DETAILS[name][2].decode().split('.')[0]
    tree = ('NExprCastDouble', 'CASTFLOAT', 2, root_value(name), False, [
        ('NExprCastInt', 'CASTINT', 1, 'PINT ' + integer, False, [
            (kind, spelling, None, string(result), False, [left, right])])])
    result = {}

    def visit(key, node):
        kind, spelling, style, value, folded, descendants = node
        names = (['cast_1'] if key == 'cast' else ['value'] if key == 'cast_1' else
                 [key + '_cond', key + '_true', key + '_false'] if kind == 'NExprTernary' else
                 [key + '_left', key + '_right'] if len(descendants) == 2 else [key + '_child'])
        names = names[:len(descendants)]
        result[key] = (kind, spelling, style, value, folded, names)
        for child_key, descendant in zip(names, descendants):
            visit(child_key, descendant)
    visit('cast', tree)
    return result


def root_value(name):
    return 'PFLOAT ' + {b'0.0': '0', b'1.0': '4607182418800017408', b'3.0': '4613937818241073152'}[DETAILS[name][2]]


def modulo_line(name):
    source = sources.CASES['native-selected-emitted-byte-bitwise-cast-chain-return-modulo-error-' + name]
    assert source.count(b'%') == 1
    return source[:source.index(b'%')].count(b'\n') + 1


def source_lines(name, condition):
    old_line = 8 if 'cv-pair' in DETAILS[name][0] else 6
    facts = ['z = {line}', 'z_left = {line}', 'z_right = {line}',
             'S_request.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Modulo by zero")) {line}',
             '$code_expression_at_source(S, porigin_operator, [PCFIELD 0]) = ({line})',
             '$code_expression_at_source(S, porigin_operator, [PCFIELD 1]) = ({line})']
    for fact in facts:
        condition = condition.replace(fact.format(line=old_line), fact.format(line=modulo_line(name)))
    return condition


old_converted, old_return_proof = current.converted, current.return_proof


def converted(name, condition):
    return source_lines(name, old_converted(name, condition).replace(
        'selected_modulo_emitted_byte_bitnot_return', 'selected_modulo_emitted_byte_bitwise_return'))


def return_proof(name):
    condition = old_return_proof(name)
    tree = nodes(name)
    operator, result = tree['value'][1], tree['value'][3]
    left, right = tree['value_left'][3], tree['value_right'][3]
    inherited_cast = CONJ.join(['$plstyle(metadata_value) = None', '$ob_object_cast_chain_quiet(' + operator + ', ' + left + ')',
        '$cast_apply(S[.RESULT = KNOWN (' + left + ')], ' + operator + ', ' + left + ', z_value) = S[.RESULT = KNOWN (' + result + ')]'])
    assert condition.count(inherited_cast) == 1
    raw_left, raw_right = [value.removeprefix('PSTRING_CARRIER INTERNED_STRING ') for value in [left, right]]
    proof = CONJ.join([r'~(b_value_left /\ b_value_right)',
        '$string_bytes(' + left + ') = (' + raw_left + ')', '$string_bytes(' + right + ') = (' + raw_right + ')',
        '|' + raw_left + '| = 1', '|' + raw_right + '| = 1',
        '$binary_apply(S[.RESULT = KNOWN (' + right + ')], ' + operator + ', ' + left + ', ' + right + ', z_value) = S[.RESULT = KNOWN (' + result + ')]'])
    return source_lines(name, condition.replace(inherited_cast, proof))


current.DETAILS, current.nodes, current.root_value = DETAILS, nodes, root_value
current.converted, current.return_proof = converted, return_proof
expression, return_bindings = current.expression, current.return_bindings


def frontier(name, fixture, path):
    bindings, checks = current.frontier(name, fixture, path)
    return bindings, [(label.replace('emitted byte NOT', 'emitted byte bitwise'), condition) for label, condition in checks]


def lifecycle(name, fixture, path):
    context = DETAILS[name][0]
    bindings, checks = prior.base_for(context).lifecycle(context, fixture, path)
    old_line, line = (8 if 'cv-pair' in context else 6), modulo_line(name)

    def fatal(number):
        return (b'Fatal error: Uncaught DivisionByZeroError: Modulo by zero in ' + bytes(path) + b':' + str(number).encode() +
                b'\nStack trace:\n#0 [internal function]: T->__toString()\n#1 {main}\n  thrown in ' + bytes(path) +
                b' on line ' + str(number).encode() + b'\n')

    label, condition = checks[2]
    rendered = prior.prior.value(fatal(old_line))
    pending = 'pobdeactivate.COMPLETION = REQUESTFATAL ($ptascii("DivisionByZeroError")) ' + prior.prior.value(b'Modulo by zero')
    assert condition.count(rendered) == 1 and condition.count(pending + ' ' + str(old_line)) == 1
    checks[2] = (label, condition.replace(rendered, prior.prior.value(fatal(line))).replace(
        pending + ' ' + str(old_line), pending + ' ' + str(line)))
    return bindings + return_bindings(name), [*[(label, converted(name, condition)) for label, condition in checks],
        ('exact emitted byte binary result survives real formal/native-cell retirement and original Error', return_proof(name))]


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
