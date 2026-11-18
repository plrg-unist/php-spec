#!/usr/bin/env python3
"""Emitted byte complements retain interned values through actual retirement."""
import base64
import output_final_selected_zero_return_modulo_error_state as zero
import output_final_selected_emitted_byte_bitnot_cast_chain_return_modulo_error_sources as sources

prior, runner = zero.prior, zero.runner
PREFIX = zero.PREFIX.replace('(PINT 0)', 'pvalue_return')
CONJ = r' /\ '
DETAILS = {context + '-' + variant: (context, variant, expected)
           for context, variant, _, _, expected in sources.VARIANTS}
CASES = {name: sources.CASES['native-selected-emitted-byte-bitnot-cast-chain-return-modulo-error-' + name]
         for name in ['warning-left-constant-full-true', 'deprecated-both-cv-pair-full-false-digit']}


def string(raw):
    return 'PSTRING_CARRIER INTERNED_STRING ' + ('([' + ', '.join(map(str, raw)) + '])' if raw else 'eps')


def nodes(name):
    variant = DETAILS[name][1]
    leaf = lambda kind, spelling, value: (kind, spelling, None, value, value is not None, [])
    literal = lambda raw: leaf('string', raw, string(raw))
    keyword = lambda spelling: leaf('constant', spelling, {'true': 'PBOOL true', 'false': 'PBOOL false', 'null': 'PNULL'}.get(spelling))
    ternary = lambda cond, yes, no, value: ('NExprTernary', None, None, value, False, [cond, yes, no])
    absent = leaf('absent', None, None)
    child, raw = {
        'full-true': (ternary(keyword('true'), literal(b'0'), keyword('UNDEFINED_CHAR_FALSE'), string(b'0')), b'0'),
        'full-false-digit': (ternary(keyword('false'), keyword('UNDEFINED_CHAR_TRUE'), literal(b'\xce'), string(b'\xce')), b'\xce'),
        'shorthand-true': (ternary(literal(b'\xcf'), absent, keyword('UNDEFINED_CHAR_FALSE'), string(b'\xcf')), b'\xcf'),
        'shorthand-false-digit': (ternary(literal(b''), absent, literal(b'\xce'), string(b'\xce')), b'\xce'),
        'coalesce-nonnull': (('NExprBinaryOpCoalesce', None, None, string(b'1'), False, [literal(b'1'), keyword('UNDEFINED_CHAR_FALSE')]), b'1'),
        'coalesce-null-nul': (('NExprBinaryOpCoalesce', None, None, string(b'\xff'), False, [keyword('null'), literal(b'\xff')]), b'\xff'),
        'full-false-letter': (ternary(keyword('false'), keyword('UNDEFINED_CHAR_TRUE'), literal(b'\xbe'), string(b'\xbe')), b'\xbe'),
        'nested-full': (ternary(keyword('true'), ternary(keyword('false'), keyword('UNDEFINED_CHAR_TRUE'), literal(b'2'), string(b'2')), keyword('UNDEFINED_CHAR_FALSE'), string(b'2')), b'2')}[variant]
    one = DETAILS[name][2] == b'1.0'
    tree = ('NExprCastDouble', 'CASTFLOAT', 2, root_value(name), False, [
        ('NExprCastInt', 'CASTINT', 1, 'PINT ' + str(int(one)), False, [
            ('NExprBitwiseNot', None, None, string(bytes([255 - raw[0]])), False, [child])])])
    result = {}

    def visit(key, node):
        kind, spelling, style, value, folded, descendants = node
        names = (['cast_1'] if key == 'cast' else ['value'] if key == 'cast_1' else
                 [key + '_cond', key + '_true', key + '_false'] if kind == 'NExprTernary' else
                 [key + '_left', key + '_right'] if kind == 'NExprBinaryOpCoalesce' else [key + '_child'])
        names = names[:len(descendants)]
        result[key] = (kind, spelling, style, value, folded, names)
        for child_key, descendant in zip(names, descendants):
            visit(child_key, descendant)
    visit('cast', tree)
    return result


def root_value(name):
    return 'PFLOAT ' + ('4607182418800017408' if DETAILS[name][2] == b'1.0' else '0')


def expression(name, key='cast'):
    kind, spelling, _, _, _, children = nodes(name)[key]
    metadata = 'metadata_' + key
    if kind == 'absent':
        return 'ABSENT'
    if kind in ('constant', 'string'):
        payload = base64.b64encode(spelling.encode() if kind == 'constant' else spelling).decode()
        if kind == 'constant':
            return 'NExprConstFetch (NName (BYTES "' + payload + '") ' + metadata + '_name) ' + metadata
        return 'NScalarString (BYTES "' + payload + '") ' + metadata
    return kind + ' ' + ' '.join('(' + expression(name, child) + ')' for child in children) + ' ' + metadata


def adapted(name, condition):
    return condition.replace('NScalarInt (INTEGER 0) metadata_zero', expression(name)).replace(
        '(PINT 0)', '(' + root_value(name) + ')').replace('_zero', '_cast')


def converted(name, condition):
    condition = zero.converted(condition).replace('selected_modulo_zero_return', 'selected_modulo_emitted_byte_bitnot_return')
    for state in ['S_handler', 'S_handler_right']:
        condition = condition.replace(state + '.RESULT = KNOWN (PINT 0)', state + '.RESULT = KNOWN (' + root_value(name) + ')')
    return condition


def return_bindings(name):
    bindings = [adapted(name, binding) for binding in zero.return_bindings(DETAILS[name][0])]
    bindings += ['$origin_node(S.SOURCES, porigin_cast) = (' + expression(name) + ')']
    for key, node in nodes(name).items():
        for field, child in enumerate(node[5]):
            bindings += ['$origin_child((porigin_' + key + '), [PCFIELD ' + str(field) + ']) = (porigin_' + child + ')',
                         'porigin_' + child + ' = PORIGIN n_cast_handler pcpath_' + child]
            bindings += (['$origin_node(S.SOURCES, porigin_' + child + ') = eps'] if nodes(name)[child][0] == 'absent' else [
                '$origin_node(S.SOURCES, porigin_' + child + ') = (' + expression(name, child) + ')',
                '$code_expression(pfunction_handler.CODE.EXPRESSIONS, pcpath_' + child + ') = ((z_' + child + ', b_' + child + '))'])
    return bindings


def return_proof(name):
    context = DETAILS[name][0]
    condition = adapted(name, zero.return_proof(context)).replace(
        r'z_cast = $source_line(metadata_cast) /\ b_cast /\ ', r'z_cast = z_cast_1 /\ ~b_cast /\ ').replace(
        'z_cast_return = $source_line(metadata_cast_return)', 'z_cast_return = z_cast')
    states = ['S_return', 'S', *(['S_return_right'] if prior.two_calls(context) else [])]
    for state in states:
        condition = condition.replace('$compiled_read(' + state + ', porigin_cast) = (' + root_value(name) + ')',
                                      '$compiled_read(' + state + ', porigin_cast) = eps')
    parts, tree = [condition, 'S.COMPLETION = NORMAL'], nodes(name)
    for key, (kind, operator, style, result, folded, children) in tree.items():
        origin = 'porigin_' + key
        if kind == 'absent':
            parts += ['$origin_node(S.SOURCES, ' + origin + ') = eps', '$code_expression(pfunction_handler.CODE.EXPRESSIONS, pcpath_' + key + ') = eps']
            continue
        parts += [('b_' if folded else '~b_') + key,
                  '$ob_object_cast_chain_value(S, pfunction_handler, ' + origin + ', ' + expression(name, key) + ') = ' + ('eps' if result is None else '(' + result + ')')]
        pooled = result.replace('PSTRING_CARRIER INTERNED_STRING', 'PSTRING') if kind == 'string' else result
        parts += ['$compiled_read(' + state + ', ' + origin + ') = ' + ('(' + pooled + ')' if folded else 'eps') for state in states]
        if result is None:
            parts += ['$ob_object_cast_chain_skipped_line(S, pfunction_handler, ' + origin + ', ' + expression(name, key) + ') = (z_' + key + ')']
            continue
        parts += ['$value_nodes(' + result + ') = eps']
        if not children:
            parts += ['z_' + key + ' = $source_line(metadata_' + key + ')']
            continue
        parts += ['z_' + key + ' = z_' + children[-1]]
        parts += ['pcpath_' + child + ' = pcpath_' + key + ' ++ [PCFIELD ' + str(field) + ']' for field, child in enumerate(children)]
        parts += ['$compiled_effects(S, ' + origin + ') = eps', '$compiled_redirect(S, ' + origin + ') = eps']
        child = tree[children[0]][3]
        if kind == 'NExprBitwiseNot':
            raw = child.removeprefix('PSTRING_CARRIER INTERNED_STRING ')
            parts += ['$string_bytes(' + child + ') = (' + raw + ')', '|' + raw + '| = 1',
                      '$bitnot_apply(S[.RESULT = KNOWN (' + child + ')], ' + child + ', z_' + key + ') = S[.RESULT = KNOWN (' + result + ')]']
        elif kind == 'NExprTernary':
            cond, yes, no = children
            truth = child not in ('PBOOL false', 'PNULL', string(b''), string(b'0'))
            branch = cond if truth and tree[yes][0] == 'absent' else yes if truth else no
            parts += ['$ob_object_cast_chain_quiet(CASTBOOL, ' + child + ')',
                      '$boolean_result(S[.RESULT = KNOWN (' + child + ')], false, z_' + cond + ') = S[.RESULT = KNOWN (PBOOL ' + str(truth).lower() + ')]']
            plan = '$selected_branch(S[.ORIGIN = (' + origin + ')][.RESULT = KNOWN (PBOOL ' + str(truth).lower() + ')], ' + expression(name, yes) + ', ' + expression(name, no) + ', ' + child + ', ' + ('0' if tree[yes][0] == 'absent' else 'z_' + yes) + ', z_' + no + ')'
            if branch == cond:
                parts += [plan + ' = S[.ORIGIN = (' + origin + ')][.RESULT = KNOWN (' + result + ')][.BASE = BASE_VALUE (KNOWN PNULL)]']
            else:
                parts += [plan + ' = S[.ORIGIN = (' + origin + ')][.TODO = [AT porigin_' + branch + ' (EVAL (' + expression(name, branch) + ')), VALUE_COPY z_' + branch + '] ++ S.TODO][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
                          '$resolve_at(S[.RESULT = KNOWN (' + result + ')], KNOWN (' + result + '), z_' + branch + ') = S[.RESULT = KNOWN (' + result + ')]']
        elif kind == 'NExprBinaryOpCoalesce':
            left, right = children
            fallback = expression(name, right)
            parts += ['~$coalesce_quiet_operand(' + expression(name, left) + ')']
            plan = '$coalesce_result(S[.ORIGIN = (' + origin + ')][.RESULT = KNOWN (' + child + ')], ' + fallback + ', z_' + left + ', z_' + right + ')'
            parts += ([plan + ' = S[.ORIGIN = (' + origin + ')][.RESULT = KNOWN (' + result + ')][.BASE = BASE_VALUE (KNOWN PNULL)]'] if child != 'PNULL' else [
                plan + ' = S[.ORIGIN = (' + origin + ')][.TODO = [AT porigin_' + right + ' (EVAL (' + fallback + ')), VALUE_COPY z_' + right + '] ++ S.TODO][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
                '$resolve_at(S[.RESULT = KNOWN (' + result + ')], KNOWN (' + result + '), z_' + right + ') = S[.RESULT = KNOWN (' + result + ')]'])
        else:
            parts += ['$plstyle(metadata_' + key + ') = ' + str(style), '$ob_object_cast_chain_quiet(' + operator + ', ' + child + ')',
                      '$cast_apply(S[.RESULT = KNOWN (' + child + ')], ' + operator + ', ' + child + ', z_' + key + ') = S[.RESULT = KNOWN (' + result + ')]']
    return CONJ.join(parts)


def frontier(name, fixture, path):
    bindings, checks = prior.base_for(DETAILS[name][0]).frontier(DETAILS[name][0], fixture, path)
    return bindings + return_bindings(name), [*[(label.replace('returns NULL', 'returns the nested scalar value').replace(
        'handled NULL result', 'handled scalar result').replace('borrowed NULL return', 'borrowed scalar return'),
        converted(name, condition)) for label, condition in checks],
        ('emitted byte NOT retains exact INTERNED result, terminal flags and unchanged STRINGDATA', return_proof(name))]


def lifecycle(name, fixture, path):
    bindings, checks = prior.base_for(DETAILS[name][0]).lifecycle(DETAILS[name][0], fixture, path)
    return bindings + return_bindings(name), [*[(label, converted(name, condition)) for label, condition in checks],
        ('exact emitted byte result survives real formal/native-cell retirement and original Error', return_proof(name))]


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
