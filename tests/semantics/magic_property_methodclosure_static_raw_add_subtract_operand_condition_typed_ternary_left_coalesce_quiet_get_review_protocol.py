#!/usr/bin/env python3
"""Check quiet signed integer Add/Subtract operands and FULL conditions."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_minus_operand_condition_typed_ternary_left_coalesce_quiet_get_review_protocol as prior

raw, renderer, payload = prior.raw, prior.renderer, prior.payload
bindings, roots = prior.bindings, prior.roots
operand, typed, certificate = prior.operand, prior.typed, prior.certificate
old_bytes, condition = prior.old_bytes, prior.condition
NULL, FALSE, TRUE = prior.NULL, prior.FALSE, prior.TRUE
string, pstring = prior.string, prior.pstring
MINIMUM, MAXIMUM = -9223372036854775808, 9223372036854775807
MIN_TEXT, MAX_TEXT = b' -9223372036854775808', b'9223372036854775807'
KINDS = {'add': 'Plus', 'sub': 'Minus'}
BINARY = {'&&': 'BooleanAnd', 'and': 'LogicalAnd', '||': 'BooleanOr',
          'or': 'LogicalOr', 'xor': 'LogicalXor', '??': 'Coalesce',
          '.': 'Concat', **KINDS}
LEAF_TREE = prior.source_tree.__globals__['tree']
CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_add_subtract_operand_condition_typed_ternary_left_coalesce_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_bytes())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def term(integer):
    return f'({integer})' if integer < 0 else str(integer)


def pint(integer):
    return 'PINT ' + term(integer)


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
    {'class': [('condition', 'add', pstring(b'00'), 0, 'PINT 0', 0, 0, 'PBOOL false', b''),
               ('operand', 'sub', 'PNULL', 0, 'PBOOL false', 0, 0, 'PINT 0', b'0'),
               ('operand', 'add', 'PBOOL false', 0, 'PBOOL false', 0, 0, 'PINT 0', b'0'),
               ('short', 'sub', pstring(b'0'), 0, 'PNULL', 0, 0, pstring(b'0'), b'0')],
     'method': [('operand', 'add', 'PINT 0', 0, pstring(b'00'), 0, 0, 'PINT 0', b'0'),
                ('condition', 'sub', 'PBOOL false', 0, 'PBOOL true', 1, -1, 'PBOOL false', b''),
                ('operand', 'sub', 'PBOOL true', 1, 'PNULL', 0, 1, 'PINT 1', b'1'),
                ('operand', 'sub', pstring(b'00'), 0, pstring(b'0'), 0, 0, 'PINT 0', b'0'),
                ('condition', 'add', 'PINT 0', 0, 'PBOOL true', 1, 1, pstring(b''), b'')]},
    {'class': [('operand', 'add', pstring(b'00'), 0, pstring(b'0'), 0, 0, 'PINT 0', b'0'),
               ('operand', 'sub', 'PNULL', 0, 'PINT 0', 0, 0, 'PINT 0', b'0'),
               ('operand', 'add', pstring(b' -1 '), -1, pstring(b' +2 '), 2, 1, 'PINT 1', b'1'),
               ('operand', 'sub', pstring(b'  +0 '), 0, pstring(b'-0'), 0, 0, 'PINT 0', b'0')],
     'method': [('condition', 'add', pstring(b'-7'), -7, pstring(b' -5 '), -5, -12, pstring(b'0'), b'0'),
                ('condition', 'sub', pstring(b'-0'), 0, 'PBOOL false', 0, 0, 'PINT 0', b'0'),
                ('condition', 'add', pstring(MIN_TEXT), MINIMUM, pstring(MAX_TEXT), MAXIMUM, -1, 'PBOOL false', b''),
                ('condition', 'sub', pstring(MAX_TEXT), MAXIMUM, 'PNULL', 0, MAXIMUM, pstring(b''), b'')]},
]


def actual_sites(index):
    result = roots(index)
    for side, items in SITES[index].items():
        for number, (position, kind, lv, li, rv, ri, integer, selected, echo) in enumerate(items):
            label = f'sum_{side}_{number}'
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
                       old_bytes('S.SOURCES', op, arithmetic) + ' = eps',
                       operand('S.SOURCES', op, arithmetic) + f' = ({pint(integer)})',
                       condition('S.SOURCES', op, arithmetic) + ' = (' + payload(str(integer).encode()) + ')']
            if position == 'short':
                result += [f'{left_expression} = NExprTernary {arithmetic} ABSENT expression_{label}_false metadata_{label}_short']
            if index == 0 and side == 'method' and number == 4:
                result += [f'{le} = NExprBinaryOpMinus expression_cancel_left expression_cancel_right metadata_cancel']
                for field, child, value in ((0, 'expression_cancel_left', pstring(MIN_TEXT)),
                                             (1, 'expression_cancel_right', pstring(MIN_TEXT))):
                    child_origin = 'porigin_cancel_' + str(field)
                    result += [f'$origin_child(({lc}),[PCFIELD {field}]) = ({child_origin})',
                               operand('S.SOURCES', child_origin, child) + f' = ({value})',
                               f'$coerce_number({value}) = COERCED (NINT {term(MINIMUM)}) false']
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
                   old_bytes(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps',
                   operand(state + '.SOURCES', 'porigin_tree_root_class', expression) + f' = ({pint(integer)})',
                   condition(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = (' + payload(str(integer).encode()) + ')']
    return result


def scalar_values(kind):
    both_min = (('+', string(MIN_TEXT)), pint(MINIMUM), MINIMUM)
    common = [(NULL, 'PNULL', 0, FALSE, 'PBOOL false', 0, 0),
              (TRUE, 'PBOOL true', 1, ('i', 7), 'PINT 7', 7, 8 if kind == 'add' else -6),
              (('i', 0), 'PINT 0', 0, TRUE, 'PBOOL true', 1, 1 if kind == 'add' else -1),
              (co(FALSE), 'PBOOL false', 0, co(NULL), 'PNULL', 0, 0),
              (co(('i', 7)), 'PINT 7', 7, co(TRUE), 'PBOOL true', 1, 8 if kind == 'add' else 6)]
    if kind == 'add':
        cancel = ('sub', both_min[0], both_min[0])
        common.append((cancel, 'PINT 0', 0, TRUE, 'PBOOL true', 1, 1))
    else:
        common.append((*both_min, *both_min, 0))
    return value_checks(kind, common, 'sum_scalar_' + kind)


def numeric_values(kind):
    rows = [(b'00', 0, b'0', 0, 0), (b'  +0 ', 0, b'-0', 0, 0),
            (b' -7 ', -7, b'+12', 12, 5 if kind == 'add' else -19),
            (b'+1', 1, b'0', 0, 1),
            (MIN_TEXT, MINIMUM, MAX_TEXT if kind == 'add' else MIN_TEXT,
             MAXIMUM if kind == 'add' else MINIMUM, -1 if kind == 'add' else 0),
            (MAX_TEXT, MAXIMUM, b'0', 0, MAXIMUM),
            (MIN_TEXT, MINIMUM, b'0', 0, MINIMUM)]
    values = [(string(a), pstring(a), ai, string(b), pstring(b), bi, output)
              for a, ai, b, bi, output in rows]
    values.append((co(string(b'1')), pstring(b'1'), 1, co(string(b'-1')), pstring(b'-1'), -1,
                   0 if kind == 'add' else 2))
    return value_checks(kind, values, 'sum_numeric_' + kind)


def source_authority(skipped):
    result = bindings()
    for kind in KINDS:
        expression, nodes, occurrences = source_tree(('?', FALSE if skipped else TRUE,
                                                     (kind, NULL, TRUE), TRUE), 'sum_source_' + kind)
        state = 'S_sum_source_' + kind
        value = 'PBOOL true' if skipped else ('PINT 1' if kind == 'add' else 'PINT (-1)')
        result += [f'{state} = ' + raw.source_state(occurrences),
                   operand(state + '.SOURCES', 'porigin_tree_root_class', expression) + f' = ({value})']
        for number, (parts, node, metadata, node_kind, _) in enumerate(nodes):
            path = 'pcpath_site ++ ' + raw.path((0,) + parts)
            changes = [('missing', f'$rawtree_review_without({state}.SOURCES[0].OCCURRENCES,{path})')]
            if node_kind in ('?', 'add', 'sub'):
                changes += [('metadata', f'(PCOCCURRENCE ({path}) ({node.removesuffix(metadata)}eps)) :: {state}.SOURCES[0].OCCURRENCES')]
            for label, source in changes:
                changed = f'{state}_{number}_{label}'
                result += [f'{changed} = ' + raw.source_state(source),
                           operand(changed + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    return result


def fences():
    result = bindings()
    pairs = [(string(b'1tail'), ('i', 0)), (('i', 0), string(b'1tail')),
             (string(b'1.5'), ('i', 0)), (('i', 0), ('f', '0000000000000000')),
             (('cv', b'missing'), ('i', 0)), (('i', 0), string(b'\0')),
             (('i', 0), string(b'')), (('i', 9223372036854775808), ('i', 0))]
    for kind in KINDS:
        for number, (left, right) in enumerate(pairs):
            expression, _, occurrences = source_tree((kind, left, right), 'sum_fence_' + kind + str(number))
            state = 'S_sum_fence_' + kind + str(number)
            result += [f'{state} = ' + raw.source_state(occurrences),
                       old_bytes(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps',
                       operand(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps',
                       condition(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
        expression, _, occurrences = source_tree((kind, string(b'OWNER'), string(b'OWNER')), 'sum_owner_' + kind)
        placeholder = 'NScalarString (BYTES "T1dORVI=") metadata_class'
        assert placeholder in expression and placeholder in occurrences
        child = 'NExprArray (SEQUENCE eps) metadata_class'
        expression, occurrences = expression.replace(placeholder, child), occurrences.replace(placeholder, child)
        state = 'S_sum_owner_' + kind
        result += [f'{state} = ' + raw.source_state(occurrences),
                   operand(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps',
                   condition(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    return result


def overflow():
    result = bindings()
    rows = [('add', MAX_TEXT, MAXIMUM, ('i', 1), 'PINT 1', 1),
            ('add', MIN_TEXT, MINIMUM, ('-', ('i', 1)), 'PINT (-1)', -1),
            ('sub', MAX_TEXT, MAXIMUM, ('-', ('i', 1)), 'PINT (-1)', -1),
            ('sub', MIN_TEXT, MINIMUM, ('i', 1), 'PINT 1', 1)]
    for number, (kind, text, integer, right, rv, ri) in enumerate(rows):
        expression, nodes, occurrences = source_tree((kind, ('+', string(text)), right), 'sum_overflow_' + str(number))
        le, re = (dict(nodes[0][4])[field] for field in (0, 1))
        state, lc, rc = ('S_sum_overflow_' + str(number), 'porigin_sum_overflow_left_' + str(number),
                         'porigin_sum_overflow_right_' + str(number))
        result += [f'{state} = ' + raw.source_state(occurrences),
                   f'$origin_child((porigin_tree_root_class),[PCFIELD 0]) = ({lc})',
                   f'$origin_child((porigin_tree_root_class),[PCFIELD 1]) = ({rc})',
                   operand(state + '.SOURCES', lc, le) + f' = ({pint(integer)})',
                   operand(state + '.SOURCES', rc, re) + f' = ({rv})',
                   f'$coerce_number({pint(integer)}) = COERCED (NINT {term(integer)}) false',
                   f'$coerce_number({rv}) = COERCED (NINT {term(ri)}) false',
                   old_bytes(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps',
                   operand(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps',
                   condition(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    return result


def compatibility():
    expression, nodes, occurrences = source_tree(('!', ('.', ('add', ('i', 0), ('i', 0)), string(b''))), 'sum_old_raw')
    add_expression = next(node for _, node, _, kind, _ in nodes if kind == 'add')
    result = bindings() + ['S_sum_old_raw = ' + raw.source_state(occurrences),
                           '$origin_child((porigin_tree_root_class),[PCFIELD 0,PCFIELD 0]) = (porigin_sum_add_zero)',
                           operand('S_sum_old_raw.SOURCES', 'porigin_sum_add_zero', add_expression) + ' = (PINT 0)',
                           condition('S_sum_old_raw.SOURCES', 'porigin_sum_add_zero', add_expression) + ' = (' + payload(b'0') + ')',
                           f'$property_magic_cv_raw_text_concat_not_tree(S_sum_old_raw.SOURCES,porigin_tree_root_class,{expression}) = eps',
                           old_bytes('S_sum_old_raw.SOURCES', 'porigin_tree_root_class', expression) + ' = eps',
                           operand('S_sum_old_raw.SOURCES', 'porigin_tree_root_class', expression) + ' = eps',
                           condition('S_sum_old_raw.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    return result


CASES = {}
for index, row in enumerate(ROWS):
    base = dict(prior.CASES[prior.ROWS[index]['id'] + '-actual-sites'], source=row['source'])
    CASES[row['id'] + '-actual-sites'] = dict(base, checks=actual_sites(index))
base = CASES[ROWS[0]['id'] + '-actual-sites']
groups = [('scalar-add', scalar_values('add')), ('scalar-subtract', scalar_values('sub')),
          ('numeric-add', numeric_values('add')), ('numeric-subtract', numeric_values('sub')),
          ('selected-source', source_authority(False)), ('skipped-source', source_authority(True)),
          ('fences', fences()), ('overflow', overflow()), ('compatibility', compatibility()),
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
