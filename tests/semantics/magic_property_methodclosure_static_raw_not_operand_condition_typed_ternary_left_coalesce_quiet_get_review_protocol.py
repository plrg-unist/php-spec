#!/usr/bin/env python3
"""Check quiet typed NOT operands and FULL conditions at reached Get sources."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_ternary_condition_typed_ternary_left_coalesce_quiet_get_review_protocol as prior

raw, renderer, payload = prior.raw, prior.renderer, prior.payload
source_tree, bindings, roots = prior.source_tree, prior.bindings, prior.roots
operand, typed, certificate = prior.operand, prior.typed, prior.certificate
old_bytes, condition = prior.old_bytes, prior.condition
NULL, FALSE, TRUE = prior.NULL, prior.FALSE, prior.TRUE
string, pstring = prior.string, prior.pstring
CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_not_operand_condition_typed_ternary_left_coalesce_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_bytes())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


# Outer typed TERNARY selection, then the exact condition of that TERNARY.
SITES = [
    {'class': [(True, 'PBOOL false', b'', 'old', 'PBOOL true', b'1'),
               (True, 'PNULL', b'0', 'old', 'PBOOL false', b''),
               (True, 'PINT 0', b'0', 'not', 'PBOOL false', b''),
               (True, pstring(b'0'), b'0', 'not', 'PBOOL true', b'1')],
     'method': [(False, 'PINT 0', b'0', 'not', 'PBOOL false', b''),
                (True, 'PBOOL false', b'', 'old', 'PBOOL false', b''),
                (False, 'PBOOL true', b'1', 'old', 'PBOOL false', b''),
                (True, pstring(b'0'), b'0', 'not', 'PBOOL true', b'1'),
                (True, pstring(b''), b'', 'old', None, b'1')]},
    {'class': [(True, pstring(b'00'), b'00', 'not', 'PBOOL true', b'1'),
               (True, pstring(b'1'), b'1', 'not', 'PBOOL true', b'1'),
               (True, pstring(b'0'), b'0', 'not', 'PBOOL false', b''),
               (True, pstring(b''), b'', 'old', None, b'0')],
     'method': [(True, pstring(b'0'), b'0', 'not', 'PBOOL true', b'1'),
                (True, pstring(b'0'), b'0', 'not', 'PBOOL false', b'')]},
]

# Paths start at each outer TERNARY. Every entry is a genuine old-None NOT.
NOT_SITES = [
    {'class': {0: [((1,), 'PBOOL false', 'PBOOL true')],
               1: [((1,), 'PBOOL true', 'PBOOL false')],
               2: [((0,), 'PBOOL false', 'PBOOL true')],
               3: [((0,), 'PBOOL true', 'PNULL')]},
     'method': {0: [((0,), 'PBOOL false', 'PBOOL true')],
                1: [((2,), 'PBOOL false', 'PBOOL true')],
                2: [((2,), 'PBOOL true', 'PBOOL false')],
                3: [((0,), 'PBOOL true', pstring(b'0'))]}},
    {'class': {0: [((0,), 'PBOOL true', 'PINT 0')],
               1: [((0,), 'PBOOL true', pstring(b''))],
               2: [((0,), 'PBOOL false', pstring(b'10'))]},
     'method': {0: [((0,), 'PBOOL true', 'PBOOL false'),
                    ((0, 0), 'PBOOL false', 'PBOOL true')],
                1: [((0,), 'PBOOL false', 'PBOOL true')]}},
]


def actual_sites(index):
    result = roots(index)
    for side, items in SITES[index].items():
        for number, (present, value, echo, cond_kind, cond_value, cond_echo) in enumerate(items):
            label = f'not_{side}_{number}'
            path = (0 if side == 'class' else 1,) + (0,) * (len(items) - number - 1) + (1,)
            origin, left = ('porigin_' + label + suffix for suffix in ('', '_left'))
            expression, expression_left, expression_cond = ('expression_' + label + suffix for suffix in ('', '_left', '_cond'))
            arm = f'expression_{label}_true' if present else 'ABSENT'
            result += [f'$origin_child((porigin_site),{raw.path(path)}) = ({origin})',
                       f'$origin_node(S.SOURCES,{origin}) = ({expression})',
                       f'{expression} = NExprBinaryOpCoalesce {expression_left} expression_{label}_rhs metadata_{label}_outer',
                       f'$origin_child(({origin}),[PCFIELD 0]) = ({left})',
                       f'{expression_left} = NExprTernary {expression_cond} {arm} expression_{label}_false metadata_{label}_ternary',
                       typed('S.SOURCES', left, expression_left) + f' = ({value})',
                       certificate('S.SOURCES', origin, expression) + ' = (' + payload(echo) + ')']
            if not present:
                result += [f'$origin_child(({left}),[PCFIELD 1]) = (porigin_{label}_absent)',
                           f'$origin_node(S.SOURCES,porigin_{label}_absent) = eps']
            if cond_kind == 'old':
                cond = f'porigin_{label}_cond'
                result += [f'$origin_child(({left}),[PCFIELD 0]) = ({cond})',
                           old_bytes('S.SOURCES', cond, expression_cond) + ' = (' + payload(cond_echo) + ')',
                           operand('S.SOURCES', cond, expression_cond) + (' = eps' if cond_value is None else f' = ({cond_value})'),
                           condition('S.SOURCES', cond, expression_cond) + ' = (' + payload(cond_echo) + ')']
            for cut, (parts, not_value, child_value) in enumerate(NOT_SITES[index][side].get(number, [])):
                prefix = f'{label}_{cut}'
                not_origin, child_origin = f'porigin_{prefix}_not', f'porigin_{prefix}_child'
                not_expr, child_expr = f'expression_{prefix}_not', f'expression_{prefix}_child'
                echo_not = b'1' if not_value == 'PBOOL true' else b''
                result += [f'$origin_child(({left}),{raw.path(parts)}) = ({not_origin})',
                           f'$origin_node(S.SOURCES,{not_origin}) = ({not_expr})',
                           f'{not_expr} = NExprBooleanNot {child_expr} metadata_{prefix}_not',
                           f'$origin_child(({not_origin}),[PCFIELD 0]) = ({child_origin})',
                           operand('S.SOURCES', child_origin, child_expr) + f' = ({child_value})',
                           old_bytes('S.SOURCES', not_origin, not_expr) + ' = eps',
                           operand('S.SOURCES', not_origin, not_expr) + f' = ({not_value})',
                           condition('S.SOURCES', not_origin, not_expr) + ' = (' + payload(echo_not) + ')']
    return result


def values_and_positions():
    def co(value):
        return ('??', ('?', TRUE, value, NULL), FALSE)
    ternary_true = ('?', TRUE, ('??', ('?', TRUE, NULL, FALSE), TRUE), FALSE)
    rows = [(('??', ('?', TRUE, NULL, FALSE), NULL), 'PNULL', 'PBOOL true'),
            (co(FALSE), 'PBOOL false', 'PBOOL true'),
            (co(('i', 0)), 'PINT 0', 'PBOOL true'),
            (co(string(b'')), pstring(b''), 'PBOOL true'),
            (co(string(b'0')), pstring(b'0'), 'PBOOL true'),
            (co(string(b'10')), pstring(b'10'), 'PBOOL false'),
            (co(TRUE), 'PBOOL true', 'PBOOL false'),
            (co(('i', 7)), 'PINT 7', 'PBOOL false'),
            (('?', FALSE, None, co(FALSE)), 'PBOOL false', 'PBOOL true'),
            (('!', co(TRUE)), 'PBOOL false', 'PBOOL true'),
            # Exact old S_ternary_condition_parent_2 child and condition callee.
            (ternary_true, 'PBOOL true', 'PBOOL false'),
            (co(string(b'00')), pstring(b'00'), 'PBOOL false')]
    result = bindings()
    for number, (child, child_value, value) in enumerate(rows):
        shape = ('!', child)
        expression, nodes, occurrences = source_tree(('?', shape, NULL, FALSE), 'not_condition_value_' + str(number))
        condition_expr = dict(nodes[0][4])[0]
        child_expr = dict(next(fields for parts, _, _, kind, fields in nodes if parts == (0,) and kind == '!'))[0]
        state, origin, child_origin = ('S_not_value_' + str(number), 'porigin_not_value_' + str(number), 'porigin_not_child_' + str(number))
        echo = b'1' if value == 'PBOOL true' else b''
        selected = 'PNULL' if echo else 'PBOOL false'
        result += [f'{state} = ' + raw.source_state(occurrences),
                   f'$origin_child((porigin_tree_root_class),[PCFIELD 0]) = ({origin})',
                   f'$origin_child(({origin}),[PCFIELD 0]) = ({child_origin})',
                   operand(state + '.SOURCES', child_origin, child_expr) + f' = ({child_value})',
                   old_bytes(state + '.SOURCES', origin, condition_expr) + ' = eps',
                   operand(state + '.SOURCES', origin, condition_expr) + f' = ({value})',
                   condition(state + '.SOURCES', origin, condition_expr) + ' = (' + payload(echo) + ')',
                   operand(state + '.SOURCES', 'porigin_tree_root_class', expression) + f' = ({selected})']
    # Existing NOT byte branches and UnaryPlus condition bytes carry zero new credit.
    retained = [(('!', FALSE), 'PBOOL true', b'1'), (('!', string(b'0')), 'PBOOL true', b'1'),
                (('!', string(b'10')), 'PBOOL false', b''), (('+', ('i', 1)), None, b'1'),
                (('+', ('i', 0)), None, b'0')]
    for number, (shape, value, echo) in enumerate(retained):
        expression, _, occurrences = source_tree(shape, 'not_retained_' + str(number))
        state = 'S_not_retained_' + str(number)
        result += [f'{state} = ' + raw.source_state(occurrences),
                   old_bytes(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = (' + payload(echo) + ')',
                   operand(state + '.SOURCES', 'porigin_tree_root_class', expression) + (' = eps' if value is None else f' = ({value})'),
                   condition(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = (' + payload(echo) + ')']
    not_false, not_true = ('!', co(TRUE)), ('!', co(FALSE))
    positions = [(('?', TRUE, not_false, NULL), 'PBOOL false', b''),
                 (('?', FALSE, NULL, not_true), 'PBOOL true', b'1'),
                 (('?', not_true, None, FALSE), 'PBOOL true', b'1'),
                 (('?', FALSE, None, not_false), 'PBOOL false', b'')]
    for number, (shape, value, echo) in enumerate(positions):
        expression, nodes, occurrences = source_tree(('??', shape, string(b'R')), 'not_position_' + str(number))
        expression_left = dict(nodes[0][4])[0]
        state, origin = 'S_not_position_' + str(number), 'porigin_not_position_' + str(number)
        result += [f'{state} = ' + raw.source_state(occurrences),
                   f'$origin_child((porigin_tree_root_class),[PCFIELD 0]) = ({origin})',
                   operand(state + '.SOURCES', origin, expression_left) + f' = ({value})',
                   certificate(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = (' + payload(echo) + ')']
    return result


def source_authority(skipped):
    child = ('??', ('?', TRUE, NULL, FALSE), FALSE)
    selected = 'PBOOL false' if skipped else 'PBOOL true'
    shape = ('?', FALSE if skipped else TRUE, ('!', child), ('?', TRUE, FALSE, NULL))
    expression, nodes, occurrences = source_tree(shape, 'not_source')
    result = bindings() + ['S_not_source = ' + raw.source_state(occurrences),
                           operand('S_not_source.SOURCES', 'porigin_tree_root_class', expression) + f' = ({selected})']
    for number, (parts, node, metadata, kind, _) in enumerate(nodes):
        path = 'pcpath_site ++ ' + raw.path((0,) + parts)
        changes = [('missing', f'$rawtree_review_without(S_not_source.SOURCES[0].OCCURRENCES,{path})')]
        if kind in ('?', '??', '!'):
            changes += [('metadata', f'(PCOCCURRENCE ({path}) ({node.removesuffix(metadata)}eps)) :: S_not_source.SOURCES[0].OCCURRENCES')]
        for label, source in changes:
            state = f'S_not_source_{number}_{label}'
            result += [f'{state} = ' + raw.source_state(source),
                       operand(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    return result


def bounds():
    result = bindings()
    bad = [string(b'\0'), ('f', '0000000000000000'), ('f', '7ff8000000000000'),
           ('cv', b'value'), ('i', 9223372036854775808)]
    for number, item in enumerate(bad):
        shape = ('!', ('??', ('?', TRUE, item, NULL), FALSE))
        expression, _, occurrences = source_tree(shape, 'not_bound_' + str(number))
        state = 'S_not_bound_' + str(number)
        result += [f'{state} = ' + raw.source_state(occurrences),
                   old_bytes(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps',
                   operand(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps',
                   condition(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    expression, _, occurrences = source_tree(('-', ('i', 1)), 'not_minus_boundary')
    result += ['S_not_minus_boundary = ' + raw.source_state(occurrences),
               old_bytes('S_not_minus_boundary.SOURCES', 'porigin_tree_root_class', expression) + ' = eps',
               operand('S_not_minus_boundary.SOURCES', 'porigin_tree_root_class', expression) + ' = eps',
               condition('S_not_minus_boundary.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    new = ('!', ('?', TRUE, ('??', ('?', TRUE, NULL, FALSE), TRUE), FALSE))
    for number, shape in enumerate((('.', new, string(b'')), ('and', TRUE, new),
                                   ('or', FALSE, new), ('xor', TRUE, new))):
        expression, _, occurrences = source_tree(shape, 'not_parent_' + str(number))
        state = 'S_not_parent_' + str(number)
        result += [f'{state} = ' + raw.source_state(occurrences),
                   old_bytes(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps',
                   condition(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    for number, shape in enumerate((('!', string(b'OWNER')),
                                   ('!', ('??', ('?', TRUE, NULL, string(b'OWNER')), FALSE)))):
        expression, _, occurrences = source_tree(shape, 'not_owner_' + str(number))
        placeholder = 'NScalarString (BYTES "T1dORVI=") metadata_class'
        assert placeholder in expression and placeholder in occurrences
        child = 'NExprArray (SEQUENCE eps) metadata_class'
        expression, occurrences = expression.replace(placeholder, child), occurrences.replace(placeholder, child)
        state = 'S_not_owner_' + str(number)
        result += [f'{state} = ' + raw.source_state(occurrences),
                   operand(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps',
                   condition(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    return result


CASES = {}
for index, row in enumerate(ROWS):
    base = dict(prior.CASES[prior.ROWS[index]['id'] + '-actual-sites'], source=row['source'])
    CASES[row['id'] + '-actual-sites'] = dict(base, checks=actual_sites(index))
base = CASES[ROWS[0]['id'] + '-actual-sites']
for suffix, checks in [('values-positions', values_and_positions()),
                       ('selected-source', source_authority(False)), ('skipped-source', source_authority(True)),
                       ('bounds', bounds()),
                       ('root-authority', prior.CASES[prior.ROWS[0]['id'] + '-root-authority']['checks'])]:
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
