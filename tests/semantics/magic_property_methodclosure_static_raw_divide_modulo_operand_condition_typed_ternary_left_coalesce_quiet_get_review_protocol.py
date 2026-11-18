#!/usr/bin/env python3
"""Check quiet exact integer Divide and signed Modulo certificates."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_multiply_operand_condition_typed_ternary_left_coalesce_quiet_get_review_protocol as prior

raw, renderer, payload = prior.raw, prior.renderer, prior.payload
bindings, roots = prior.bindings, prior.roots
operand, typed, certificate = prior.operand, prior.typed, prior.certificate
old_bytes, condition = prior.old_bytes, prior.condition
NULL, FALSE, TRUE = prior.NULL, prior.FALSE, prior.TRUE
string, pstring = prior.string, prior.pstring
MINIMUM, MAXIMUM = -9223372036854775808, 9223372036854775807
MIN_TEXT, MAX_TEXT = b' -9223372036854775808', b'9223372036854775807'
KINDS = {'div': 'Div', 'mod': 'Mod'}
BINARY = {'&&': 'BooleanAnd', 'and': 'LogicalAnd', '||': 'BooleanOr',
          'or': 'LogicalOr', 'xor': 'LogicalXor', '??': 'Coalesce',
          '.': 'Concat', **KINDS}
LEAF_TREE = prior.LEAF_TREE
CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_divide_modulo_operand_condition_typed_ternary_left_coalesce_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_bytes())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def term(integer):
    return f'({integer})' if integer < 0 else str(integer)


def pint(integer):
    return 'PINT ' + term(integer)


def helper(kind, left, right):
    if kind == 'div':
        return f'$num_div(NINT {term(left)},NINT {term(right)})'
    return f'$long_mod({term(left)},{term(right)})'


def helper_integer(kind, integer):
    return f'NUM (NINT {term(integer)})' if kind == 'div' else 'IRESULT ' + term(integer)


def tree(shape, suffix, parts=()):
    kind = shape[0]
    if kind in ('s', 'i', 'f', 'cv', 'k'):
        return LEAF_TREE(shape, suffix, parts, True)
    metadata = 'metadata_class'
    fields = ((0, shape[1]), (2, shape[3])) if kind == '?' and shape[2] is None else (
        ((0, shape[1]), (1, shape[2]), (2, shape[3])) if kind == '?' else
        ((0, shape[1]), (1, shape[2])) if kind in BINARY else ((0, shape[1]),))
    nodes, children = [], []
    for field, child in fields:
        expression, descendants, _ = tree(child, suffix, parts + (field,))
        children.append((field, expression))
        nodes += descendants
    expressions = dict(children)
    if kind == '?':
        arm = 'ABSENT' if shape[2] is None else '(' + expressions[1] + ')'
        expression = f'NExprTernary ({expressions[0]}) {arm} ({expressions[2]}) {metadata}'
    elif kind in BINARY:
        expression = f'NExprBinaryOp{BINARY[kind]} ({expressions[0]}) ({expressions[1]}) {metadata}'
    else:
        constructor = {'!': 'NExprBooleanNot', '+': 'NExprUnaryPlus', '-': 'NExprUnaryMinus'}[kind]
        expression = f'{constructor} ({expressions[0]}) {metadata}'
    return expression, [(parts, expression, metadata, kind, children), *nodes], []


def source_tree(shape, suffix):
    expression, nodes, _ = tree(shape, suffix)
    occurrences = 'eps'
    for parts, node, _, _, _ in nodes:
        occurrences = f'(PCOCCURRENCE (pcpath_site ++ {raw.path((0,) + parts)}) ({node})) :: ({occurrences})'
    return expression, nodes, occurrences


# position, operator, left/right values and converted ints, result, selected, echo.
SITES = [
    {'class': [('condition', 'div', 'PINT 0', 0, pstring(MIN_TEXT), MINIMUM, 0, 'PBOOL false', b''),
               ('operand', 'div', 'PNULL', 0, 'PBOOL true', 1, 0, 'PINT 0', b'0'),
               ('operand', 'mod', 'PBOOL false', 0, pstring(MIN_TEXT), MINIMUM, 0, 'PINT 0', b'0'),
               ('short', 'mod', pstring(b'0'), 0, 'PBOOL true', 1, 0, pstring(b'0'), b'0')],
     'method': [('operand', 'div', 'PINT 0', 0, pstring(b' -2 '), -2, 0, 'PINT 0', b'0'),
                ('condition', 'mod', pstring(b' -7 '), -7, pstring(b' +3 '), 3, -1, 'PBOOL false', b''),
                ('operand', 'div', 'PBOOL true', 1, 'PBOOL true', 1, 1, 'PINT 1', b'1'),
                ('operand', 'mod', pstring(b'00'), 0, pstring(b'3'), 3, 0, 'PINT 0', b'0'),
                ('condition', 'div', pstring(MIN_TEXT), MINIMUM, 'PBOOL true', 1, MINIMUM, pstring(b''), b'')]},
    {'class': [('operand', 'div', pstring(b'00'), 0, pstring(b'1'), 1, 0, 'PINT 0', b'0'),
               ('operand', 'mod', 'PNULL', 0, 'PBOOL true', 1, 0, 'PINT 0', b'0'),
               ('operand', 'div', pstring(b' -1 '), -1, pstring(b'-1'), -1, 1, 'PINT 1', b'1'),
               ('operand', 'mod', pstring(b'  +0 '), 0, pstring(b'-3'), -3, 0, 'PINT 0', b'0')],
     'method': [('condition', 'mod', pstring(b' -7 '), -7, pstring(b' +3 '), 3, -1, pstring(b'0'), b'0'),
                ('condition', 'mod', pstring(MIN_TEXT), MINIMUM, pstring(b'-1'), -1, 0, 'PINT 0', b'0'),
                ('condition', 'mod', pstring(MIN_TEXT), MINIMUM, pstring(MAX_TEXT), MAXIMUM, -1, 'PBOOL false', b''),
                ('condition', 'mod', pstring(MAX_TEXT), MAXIMUM, pstring(MIN_TEXT), MINIMUM, MAXIMUM, pstring(b''), b'')]},
]


def actual_sites(index):
    result = roots(index)
    for side, items in SITES[index].items():
        for number, (position, kind, lv, li, rv, ri, integer, selected, echo) in enumerate(items):
            label = f'integer_{side}_{number}'
            path = (0 if side == 'class' else 1,) + (0,) * (len(items) - number - 1) + (1,)
            origin, left, op, lc, rc = ('porigin_' + label + s for s in ('', '_left', '_op', '_lc', '_rc'))
            expression, left_expression, arithmetic, le, re = ('expression_' + label + s for s in ('', '_left', '_op', '_lc', '_rc'))
            result += [f'$origin_child((porigin_site),{raw.path(path)}) = ({origin})',
                       f'$origin_node(S.SOURCES,{origin}) = ({expression})',
                       f'{expression} = NExprBinaryOpCoalesce {left_expression} expression_{label}_fallback metadata_{label}_outer',
                       f'$origin_child(({origin}),[PCFIELD 0]) = ({left})',
                       typed('S.SOURCES', left, left_expression) + f' = ({selected})',
                       certificate('S.SOURCES', origin, expression) + ' = (' + payload(echo) + ')',
                       f'$origin_child(({left}),{raw.path((1,) if position == "operand" else (0,))}) = ({op})',
                       f'$origin_node(S.SOURCES,{op}) = ({arithmetic})',
                       f'{arithmetic} = NExprBinaryOp{KINDS[kind]} {le} {re} metadata_{label}_op',
                       f'$origin_child(({op}),[PCFIELD 0]) = ({lc})',
                       f'$origin_child(({op}),[PCFIELD 1]) = ({rc})',
                       operand('S.SOURCES', lc, le) + f' = ({lv})',
                       operand('S.SOURCES', rc, re) + f' = ({rv})',
                       f'$coerce_number({lv}) = COERCED (NINT {term(li)}) false',
                       f'$coerce_number({rv}) = COERCED (NINT {term(ri)}) false',
                       helper(kind, li, ri) + ' = ' + helper_integer(kind, integer),
                       old_bytes('S.SOURCES', op, arithmetic) + ' = eps',
                       operand('S.SOURCES', op, arithmetic) + f' = ({pint(integer)})',
                       condition('S.SOURCES', op, arithmetic) + ' = (' + payload(str(integer).encode()) + ')']
            if position == 'short':
                result += [f'{left_expression} = NExprTernary {arithmetic} ABSENT expression_{label}_false metadata_{label}_short']
    return result


def co(shape):
    return ('??', ('?', TRUE, shape, NULL), NULL)


def value_checks(kind, rows, prefix):
    result = bindings()
    for number, (ls, lv, li, rs, rv, ri, integer) in enumerate(rows):
        expression, nodes, occurrences = source_tree((kind, ls, rs), prefix + '_' + str(number))
        le, re = (dict(nodes[0][4])[field] for field in (0, 1))
        state, lc, rc = ('S_' + prefix + '_' + str(number), 'porigin_' + prefix + '_' + str(number) + '_left',
                         'porigin_' + prefix + '_' + str(number) + '_right')
        result += [f'{state} = ' + raw.source_state(occurrences),
                   f'$origin_child((porigin_tree_root_class),[PCFIELD 0]) = ({lc})',
                   f'$origin_child((porigin_tree_root_class),[PCFIELD 1]) = ({rc})',
                   operand(state + '.SOURCES', lc, le) + f' = ({lv})',
                   operand(state + '.SOURCES', rc, re) + f' = ({rv})',
                   f'$coerce_number({lv}) = COERCED (NINT {term(li)}) false',
                   f'$coerce_number({rv}) = COERCED (NINT {term(ri)}) false',
                   helper(kind, li, ri) + ' = ' + helper_integer(kind, integer),
                   old_bytes(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps',
                   operand(state + '.SOURCES', 'porigin_tree_root_class', expression) + f' = ({pint(integer)})',
                   condition(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = (' + payload(str(integer).encode()) + ')']
    return result


def scalar_values(kind):
    minimum, maximum, negative = ('+', string(MIN_TEXT)), ('+', string(MAX_TEXT)), ('-', ('i', 1))
    divide = [(NULL, 'PNULL', 0, TRUE, 'PBOOL true', 1, 0),
              (TRUE, 'PBOOL true', 1, TRUE, 'PBOOL true', 1, 1),
              (co(FALSE), 'PBOOL false', 0, co(TRUE), 'PBOOL true', 1, 0),
              (co(('i', 6)), 'PINT 6', 6, co(('-', ('i', 2))), 'PINT (-2)', -2, -3),
              (minimum, pint(MINIMUM), MINIMUM, ('i', 1), 'PINT 1', 1, MINIMUM),
              (('i', 0), 'PINT 0', 0, minimum, pint(MINIMUM), MINIMUM, 0)]
    modulo = [(NULL, 'PNULL', 0, TRUE, 'PBOOL true', 1, 0),
              (TRUE, 'PBOOL true', 1, TRUE, 'PBOOL true', 1, 0),
              (co(FALSE), 'PBOOL false', 0, co(TRUE), 'PBOOL true', 1, 0),
              (co(('i', 7)), 'PINT 7', 7, co(('-', ('i', 3))), 'PINT (-3)', -3, 1),
              (minimum, pint(MINIMUM), MINIMUM, negative, 'PINT (-1)', -1, 0),
              (maximum, pint(MAXIMUM), MAXIMUM, minimum, pint(MINIMUM), MINIMUM, MAXIMUM)]
    return value_checks(kind, {'div': divide, 'mod': modulo}[kind], kind + '_scalar')


def numeric_values(kind):
    divide = [(b'00', 0, b'-1', -1, 0), (b' -6 ', -6, b'+2', 2, -3),
              (b'+6', 6, b'-2', -2, -3), (b'-6', -6, b'-2', -2, 3),
              (MIN_TEXT, MINIMUM, b'1', 1, MINIMUM), (b'1', 1, b'-1', -1, -1),
              (MAX_TEXT, MAXIMUM, MAX_TEXT, MAXIMUM, 1)]
    modulo = [(b'00', 0, b'-3', -3, 0), (b' -7 ', -7, b'+3', 3, -1),
              (b'+7', 7, b'-3', -3, 1), (b'-7', -7, b'-3', -3, -1),
              (MIN_TEXT, MINIMUM, b'-1', -1, 0), (MIN_TEXT, MINIMUM, MIN_TEXT, MINIMUM, 0),
              (MIN_TEXT, MINIMUM, MAX_TEXT, MAXIMUM, -1),
              (MAX_TEXT, MAXIMUM, MIN_TEXT, MINIMUM, MAXIMUM)]
    values = lambda rows: [(string(a), pstring(a), ai, string(b), pstring(b), bi, output)
                           for a, ai, b, bi, output in rows]
    return value_checks(kind, values({'div': divide, 'mod': modulo}[kind]), kind + '_numeric')


def source_authority(skipped):
    result = bindings()
    for kind in KINDS:
        expression, nodes, occurrences = source_tree(('?', FALSE if skipped else TRUE,
                                                     (kind, NULL, TRUE), TRUE), 'integer_source_' + kind)
        state = 'S_integer_source_' + kind
        value = 'PBOOL true' if skipped else 'PINT 0'
        result += [f'{state} = ' + raw.source_state(occurrences),
                   operand(state + '.SOURCES', 'porigin_tree_root_class', expression) + f' = ({value})']
        for number, (parts, node, metadata, node_kind, _) in enumerate(nodes):
            path = 'pcpath_site ++ ' + raw.path((0,) + parts)
            changes = [('missing', f'$rawtree_review_without({state}.SOURCES[0].OCCURRENCES,{path})')]
            if node_kind in ('?', 'div', 'mod'):
                changes += [('metadata', f'(PCOCCURRENCE ({path}) ({node.removesuffix(metadata)}eps)) :: {state}.SOURCES[0].OCCURRENCES')]
            for label, source in changes:
                changed = f'{state}_{number}_{label}'
                result += [f'{changed} = ' + raw.source_state(source),
                           operand(changed + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    return result


def fences(kind):
    result = bindings()
    zero = ('i', 0)
    bad = [string(b'1tail'), string(b'garbage'), string(b'\0'), string(b'1.5'),
           ('f', '0000000000000000'), ('cv', b'missing'), ('i', 9223372036854775808)]
    divisor = ('i', 1) if kind == 'div' else ('-', ('i', 1))
    pairs = [(zero, value) for value in bad] + [(value, divisor) for value in bad]
    for number, (left, right) in enumerate(pairs):
        expression, _, occurrences = source_tree((kind, left, right), 'integer_fence_' + kind + str(number))
        state = 'S_integer_fence_' + kind + str(number)
        result += [f'{state} = ' + raw.source_state(occurrences),
                   old_bytes(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps',
                   operand(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps',
                   condition(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    for side in (0, 1):
        shape = (kind, string(b'OWNER'), divisor) if side == 0 else (kind, zero, string(b'OWNER'))
        expression, _, occurrences = source_tree(shape, 'integer_owner_' + kind + str(side))
        placeholder = 'NScalarString (BYTES "T1dORVI=") metadata_class'
        child = 'NExprArray (SEQUENCE eps) metadata_class'
        assert placeholder in expression and placeholder in occurrences
        expression, occurrences = expression.replace(placeholder, child), occurrences.replace(placeholder, child)
        state = 'S_integer_owner_' + kind + str(side)
        result += [f'{state} = ' + raw.source_state(occurrences),
                   operand(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps',
                   condition(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    return result


def unsupported_results():
    result = bindings()
    minimum, negative = ('+', string(MIN_TEXT)), ('-', ('i', 1))
    rows = []
    for kind, rejected in [('div', 'DIVZERO'), ('mod', 'INTZERO')]:
        rows += [(kind, NULL, 'PNULL', 0, FALSE, 'PBOOL false', 0, rejected),
                 (kind, TRUE, 'PBOOL true', 1, string(b'00'), pstring(b'00'), 0, rejected),
                 (kind, ('i', 0), 'PINT 0', 0, NULL, 'PNULL', 0, rejected)]
    rows += [('div', ('i', 5), 'PINT 5', 5, ('i', 2), 'PINT 2', 2, 'NUM (NFLOAT 4612811918334230528)'),
             ('div', ('-', ('i', 5)), 'PINT (-5)', -5, ('i', 2), 'PINT 2', 2, 'NUM (NFLOAT 13836183955189006336)'),
             ('div', minimum, pint(MINIMUM), MINIMUM, negative, 'PINT (-1)', -1, 'NUM (NFLOAT 4890909195324358656)')]
    for number, (kind, ls, lv, li, rs, rv, ri, rejected) in enumerate(rows):
        expression, nodes, occurrences = source_tree((kind, ls, rs), 'integer_rejected_' + str(number))
        le, re = (dict(nodes[0][4])[field] for field in (0, 1))
        state, lc, rc = ('S_integer_rejected_' + str(number), 'porigin_integer_rejected_left_' + str(number),
                         'porigin_integer_rejected_right_' + str(number))
        result += [f'{state} = ' + raw.source_state(occurrences),
                   f'$origin_child((porigin_tree_root_class),[PCFIELD 0]) = ({lc})',
                   f'$origin_child((porigin_tree_root_class),[PCFIELD 1]) = ({rc})',
                   operand(state + '.SOURCES', lc, le) + f' = ({lv})',
                   operand(state + '.SOURCES', rc, re) + f' = ({rv})',
                   f'$coerce_number({lv}) = COERCED (NINT {term(li)}) false',
                   f'$coerce_number({rv}) = COERCED (NINT {term(ri)}) false',
                   helper(kind, li, ri) + ' = ' + rejected,
                   old_bytes(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps',
                   operand(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps',
                   condition(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    return result


def compatibility():
    result = bindings()
    for kind in KINDS:
        expression, nodes, occurrences = source_tree(('!', ('.', (kind, ('i', 0), ('i', 1)), string(b''))), 'integer_old_raw_' + kind)
        arithmetic = next(node for _, node, _, node_kind, _ in nodes if node_kind == kind)
        state, origin = 'S_integer_old_raw_' + kind, 'porigin_integer_old_raw_' + kind
        result += [f'{state} = ' + raw.source_state(occurrences),
                   f'$origin_child((porigin_tree_root_class),[PCFIELD 0,PCFIELD 0]) = ({origin})',
                   operand(state + '.SOURCES', origin, arithmetic) + ' = (PINT 0)',
                   condition(state + '.SOURCES', origin, arithmetic) + ' = (' + payload(b'0') + ')',
                   f'$property_magic_cv_raw_text_concat_not_tree({state}.SOURCES,porigin_tree_root_class,{expression}) = eps',
                   old_bytes(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps',
                   operand(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps',
                   condition(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    return result


CASES = {}
for index, row in enumerate(ROWS):
    base = dict(prior.CASES[prior.ROWS[index]['id'] + '-actual-sites'], source=row['source'])
    CASES[row['id'] + '-actual-sites'] = dict(base, checks=actual_sites(index))
base = CASES[ROWS[0]['id'] + '-actual-sites']
groups = [('divide-scalar-values', scalar_values('div')), ('modulo-scalar-values', scalar_values('mod')),
          ('divide-numeric-values', numeric_values('div')), ('modulo-numeric-values', numeric_values('mod')),
          ('selected-source', source_authority(False)), ('skipped-source', source_authority(True)),
          ('divide-fences', fences('div')), ('modulo-fences', fences('mod')),
          ('unsupported-results', unsupported_results()), ('compatibility', compatibility()),
          ('root-authority', prior.CASES[prior.ROWS[0]['id'] + '-root-authority']['checks'])]
for suffix, checks in groups:
    CASES[ROWS[0]['id'] + '-' + suffix] = dict(base, checks=checks)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    parents, parent = [], prior
    while hasattr(parent, 'prior'):
        parents.append(parent)
        parent = parent.prior
    parents.append(parent)
    literal = raw.literal
    parents += [raw, renderer, literal, literal.own, literal.own.prior, literal.own.prior.prior,
                literal.inherited, literal.inherited.prior, literal.inherited.prior.prior,
                literal.inherited.prior.prior.prior, literal.own.prior.prior.owning,
                literal.own.prior.prior.literal]
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, *(entry for parent in parents
                                               for entry in (Path(parent.__file__), parent.CATALOGUE))),
                 runner_flags=('--sl',), fixture_renderer=renderer.render)
