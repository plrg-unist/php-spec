#!/usr/bin/env python3
"""Check typed TERNARY roots in FULL quiet Get conditions."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_coalesce_condition_typed_ternary_left_coalesce_quiet_get_review_protocol as prior

raw, renderer, payload = prior.raw, prior.renderer, prior.payload
source_tree, bindings, roots = prior.source_tree, prior.bindings, prior.roots
operand, typed, certificate = prior.operand, prior.typed, prior.certificate
old_bytes, condition = prior.old_bytes, prior.condition
NULL, FALSE, TRUE = prior.NULL, prior.FALSE, prior.TRUE
string, pstring = prior.string, prior.pstring
CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_ternary_condition_typed_ternary_left_coalesce_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_bytes())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


SITES = [
    {'class': [(True, 'PBOOL false', b'', 'PBOOL true', b'1', 'full'),
               (True, 'PNULL', b'0', 'PBOOL false', b'', 'full'),
               (True, 'PINT 0', b'0', 'PNULL', b'', 'short'),
               (True, pstring(b'0'), b'0', pstring(b''), b'', 'full')],
     'method': [(True, 'PINT 0', b'0', 'PINT 0', b'0', 'short'),
                (True, pstring(b''), b'', pstring(b'10'), b'10', 'full'),
                (False, 'PBOOL true', b'1', 'PBOOL true', b'1', 'coalesce'),
                (True, pstring(b'0'), b'0', pstring(b'0'), b'0', 'short'),
                (True, pstring(b''), b'', None, b'1', 'plus')]},
    {'class': [(True, pstring(b'00'), b'00', 'PBOOL false', b'', 'short'),
               (True, pstring(b'1'), b'1', pstring(b'0'), b'0', 'full'),
               (True, pstring(b'0'), b'0', 'PBOOL true', b'1', 'full'),
               (True, pstring(b''), b'', None, b'0', 'plus')],
     'method': [(True, 'PNULL', b'0', 'PNULL', b'', 'full'),
                (True, pstring(b'0'), b'0', pstring(b'10'), b'10', 'short')]},
]


def actual_sites(index):
    result = roots(index)
    for side, items in SITES[index].items():
        for number, (present, value, echo, value_cond, bytes_cond, kind) in enumerate(items):
            label = f'ternary_condition_{side}_{number}'
            path = (0 if side == 'class' else 1,) + (0,) * (len(items) - number - 1) + (1,)
            origin, left, cond = ('porigin_' + label + suffix for suffix in ('', '_left', '_cond'))
            expression, expression_left, expression_cond = ('expression_' + label + suffix for suffix in ('', '_left', '_cond'))
            arm = f'expression_{label}_true' if present else 'ABSENT'
            ternary = f'NExprTernary {expression_cond} {arm} expression_{label}_false metadata_{label}_ternary'
            result += [f'$origin_child((porigin_site),{raw.path(path)}) = ({origin})',
                       f'$origin_node(S.SOURCES,{origin}) = ({expression})',
                       f'{expression} = NExprBinaryOpCoalesce {expression_left} expression_{label}_rhs metadata_{label}_outer',
                       f'$origin_child(({origin}),[PCFIELD 0]) = ({left})',
                       f'{expression_left} = {ternary}',
                       typed('S.SOURCES', left, expression_left) + f' = ({value})',
                       certificate('S.SOURCES', origin, expression) + ' = (' + payload(echo) + ')',
                       f'$origin_child(({left}),[PCFIELD 0]) = ({cond})',
                       f'$origin_node(S.SOURCES,{cond}) = ({expression_cond})']
            if kind in ('full', 'short'):
                inner_arm = f'expression_{label}_inner_true' if kind == 'full' else 'ABSENT'
                constructor = f'NExprTernary expression_{label}_inner_cond {inner_arm} expression_{label}_inner_false'
            elif kind == 'coalesce':
                constructor = f'NExprBinaryOpCoalesce expression_{label}_lhs expression_{label}_rhs_cond'
            else:
                constructor = f'NExprUnaryPlus expression_{label}_signed'
            result += [f'{expression_cond} = {constructor} metadata_{label}_cond']
            if value_cond is None:
                result += [old_bytes('S.SOURCES', cond, expression_cond) + ' = (' + payload(bytes_cond) + ')',
                           operand('S.SOURCES', cond, expression_cond) + ' = eps']
            else:
                result += [old_bytes('S.SOURCES', cond, expression_cond) + ' = eps',
                           operand('S.SOURCES', cond, expression_cond) + f' = ({value_cond})']
            if present:
                result += [condition('S.SOURCES', cond, expression_cond) + ' = (' + payload(bytes_cond) + ')']
            else:
                result += [f'$origin_child(({left}),[PCFIELD 1]) = (porigin_{label}_absent)',
                           f'$origin_node(S.SOURCES,porigin_{label}_absent) = eps']
    return result


def values_and_positions():
    full_null = ('?', TRUE, NULL, FALSE)
    coalesce_null = ('??', full_null, NULL)
    coalesce_true = ('??', full_null, TRUE)
    coalesce_false = ('??', ('?', TRUE, FALSE, NULL), TRUE)
    coalesce_zero = ('??', ('?', TRUE, ('i', 0), NULL), TRUE)
    coalesce_empty = ('??', ('?', TRUE, string(b''), NULL), TRUE)
    coalesce_string_zero = ('??', ('?', TRUE, string(b'0'), NULL), TRUE)
    coalesce_ten = ('??', ('?', TRUE, string(b'10'), NULL), FALSE)
    rows = [
        (('?', TRUE, coalesce_null, FALSE), 'PNULL', b''),
        (('?', FALSE, FALSE, coalesce_true), 'PBOOL true', b'1'),
        (('?', TRUE, coalesce_false, NULL), 'PBOOL false', b''),
        (('?', FALSE, None, coalesce_zero), 'PINT 0', b'0'),
        (('?', TRUE, coalesce_empty, NULL), pstring(b''), b''),
        (('?', FALSE, None, coalesce_string_zero), pstring(b'0'), b'0'),
        (('?', coalesce_true, coalesce_ten, FALSE), pstring(b'10'), b'10'),
        (('?', FALSE, None, coalesce_null), 'PNULL', b''),
        (('?', coalesce_false, NULL, ('i', 1)), 'PINT 1', b'1'),
        (('?', TRUE, None, coalesce_false), 'PBOOL true', b'1'),
        # Exact maintained S_condition_parent_0 shape and condition callee.
        (('?', TRUE, coalesce_true, FALSE), 'PBOOL true', b'1'),
    ]
    result = bindings()
    for number, (shape, value, echo) in enumerate(rows):
        expression, nodes, occurrences = source_tree(('?', shape, NULL, FALSE), 'ternary_condition_value_' + str(number))
        expression_cond = dict(nodes[0][4])[0]
        state, origin = 'S_ternary_condition_value_' + str(number), 'porigin_ternary_condition_value_' + str(number)
        selected = 'PBOOL false' if echo in (b'', b'0') else 'PNULL'
        result += [f'{state} = ' + raw.source_state(occurrences),
                   f'$origin_child((porigin_tree_root_class),[PCFIELD 0]) = ({origin})',
                   old_bytes(state + '.SOURCES', origin, expression_cond) + ' = eps',
                   operand(state + '.SOURCES', origin, expression_cond) + f' = ({value})',
                   condition(state + '.SOURCES', origin, expression_cond) + ' = (' + payload(echo) + ')',
                   operand(state + '.SOURCES', 'porigin_tree_root_class', expression) + f' = ({selected})']
    # Existing fast paths and the preceding COALESCE fallback carry zero new credit.
    for number, (shape, echo) in enumerate(((('+', ('i', 1)), b'1'), (('+', ('i', 0)), b'0'),
                                           (('??', NULL, ('+', ('i', 0))), b'0'))):
        expression, _, occurrences = source_tree(shape, 'retained_condition_' + str(number))
        state = 'S_retained_condition_' + str(number)
        result += [f'{state} = ' + raw.source_state(occurrences),
                   old_bytes(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = (' + payload(echo) + ')',
                   operand(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps',
                   condition(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = (' + payload(echo) + ')']
    expression, _, occurrences = source_tree(coalesce_true, 'retained_coalesce_condition')
    result += ['S_retained_coalesce_condition = ' + raw.source_state(occurrences),
               old_bytes('S_retained_coalesce_condition.SOURCES', 'porigin_tree_root_class', expression) + ' = eps',
               operand('S_retained_coalesce_condition.SOURCES', 'porigin_tree_root_class', expression) + ' = (PBOOL true)',
               condition('S_retained_coalesce_condition.SOURCES', 'porigin_tree_root_class', expression) + ' = (' + payload(b'1') + ')']
    inner_true = ('?', rows[10][0], string(b'10'), FALSE)
    inner_false = ('?', rows[2][0], NULL, ('i', 0))
    positions = [(('?', TRUE, inner_true, NULL), pstring(b'10'), b'10'),
                 (('?', FALSE, NULL, inner_false), 'PINT 0', b'0'),
                 (('?', inner_true, None, FALSE), pstring(b'10'), b'10'),
                 (('?', FALSE, None, inner_false), 'PINT 0', b'0')]
    for number, (shape, value, echo) in enumerate(positions):
        expression, nodes, occurrences = source_tree(('??', shape, string(b'R')), 'ternary_condition_position_' + str(number))
        expression_left = dict(nodes[0][4])[0]
        state, origin = 'S_ternary_condition_position_' + str(number), 'porigin_ternary_condition_position_' + str(number)
        result += [f'{state} = ' + raw.source_state(occurrences),
                   f'$origin_child((porigin_tree_root_class),[PCFIELD 0]) = ({origin})',
                   operand(state + '.SOURCES', origin, expression_left) + f' = ({value})',
                   certificate(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = (' + payload(echo) + ')']
    return result


def source_authority(skipped):
    left = FALSE if skipped else NULL
    coalesce = ('??', ('?', TRUE, left, FALSE), ('?', FALSE, TRUE, FALSE))
    cond = ('?', FALSE if skipped else TRUE, coalesce, ('?', TRUE, FALSE, NULL))
    expression, nodes, occurrences = source_tree(('?', cond, NULL, FALSE), 'ternary_condition_source')
    result = bindings() + ['S_ternary_condition_source = ' + raw.source_state(occurrences),
                           operand('S_ternary_condition_source.SOURCES', 'porigin_tree_root_class', expression) + ' = (PBOOL false)']
    for number, (parts, node, metadata, kind, _) in enumerate(nodes):
        path = 'pcpath_site ++ ' + raw.path((0,) + parts)
        changes = [('missing', f'$rawtree_review_without(S_ternary_condition_source.SOURCES[0].OCCURRENCES,{path})')]
        if kind in ('?', '??'):
            changes += [('metadata', f'(PCOCCURRENCE ({path}) ({node.removesuffix(metadata)}eps)) :: S_ternary_condition_source.SOURCES[0].OCCURRENCES')]
        for label, source in changes:
            state = f'S_ternary_condition_source_{number}_{label}'
            result += [f'{state} = ' + raw.source_state(source),
                       operand(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    return result


def bounds():
    bad = [string(b'\0'), ('f', '0000000000000000'), ('f', '7ff8000000000000'),
           ('cv', b'value'), ('i', 9223372036854775808)]
    shapes = [('?', TRUE, ('??', ('?', TRUE, item, NULL), FALSE), FALSE) for item in bad]
    shapes += [('?', FALSE, FALSE, ('??', ('?', TRUE, item, NULL), FALSE)) for item in bad]
    result = bindings()
    for number, shape in enumerate(shapes):
        expression, _, occurrences = source_tree(shape, 'ternary_condition_bound_' + str(number))
        state = 'S_ternary_condition_bound_' + str(number)
        result += [f'{state} = ' + raw.source_state(occurrences),
                   old_bytes(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps',
                   condition(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    expression, _, occurrences = source_tree(('-', ('i', 1)), 'ternary_condition_minus')
    result += ['S_ternary_condition_minus = ' + raw.source_state(occurrences),
               old_bytes('S_ternary_condition_minus.SOURCES', 'porigin_tree_root_class', expression) + ' = eps',
               operand('S_ternary_condition_minus.SOURCES', 'porigin_tree_root_class', expression) + ' = eps',
               condition('S_ternary_condition_minus.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    new = ('?', TRUE, ('??', ('?', TRUE, NULL, FALSE), TRUE), FALSE)
    for number, shape in enumerate((('.', new, string(b'')), ('and', TRUE, new), ('!', new))):
        expression, _, occurrences = source_tree(shape, 'ternary_condition_parent_' + str(number))
        state = 'S_ternary_condition_parent_' + str(number)
        result += [f'{state} = ' + raw.source_state(occurrences),
                   old_bytes(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps',
                   condition(state + '.SOURCES', 'porigin_tree_root_class', expression) + (' = (' + payload(b'') + ')' if number == 2 else ' = eps')]
    for number, shape in enumerate((('?', TRUE, ('??', ('?', TRUE, string(b'OWNER'), NULL), FALSE), FALSE),
                                   ('?', TRUE, FALSE, ('??', ('?', TRUE, string(b'OWNER'), NULL), FALSE)))):
        expression, _, occurrences = source_tree(shape, 'ternary_condition_owner_' + str(number))
        placeholder = 'NScalarString (BYTES "T1dORVI=") metadata_class'
        assert placeholder in expression and placeholder in occurrences
        child = 'NExprArray (SEQUENCE eps) metadata_class'
        expression, occurrences = expression.replace(placeholder, child), occurrences.replace(placeholder, child)
        state = 'S_ternary_condition_owner_' + str(number)
        result += [f'{state} = ' + raw.source_state(occurrences),
                   condition(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    return result


CASES = {}
for index, row in enumerate(ROWS):
    base = dict(prior.CASES[prior.ROWS[index]['id'] + '-actual-sites'], source=row['source'])
    CASES[row['id'] + '-actual-sites'] = dict(base, checks=actual_sites(index))
base = CASES[ROWS[0]['id'] + '-actual-sites']
for suffix, checks in [('values-positions', values_and_positions()),
                       ('selected-source', source_authority(False)), ('skipped-source', source_authority(True)),
                       ('bounds', bounds()), ('root-authority', prior.prior.root_authority())]:
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
