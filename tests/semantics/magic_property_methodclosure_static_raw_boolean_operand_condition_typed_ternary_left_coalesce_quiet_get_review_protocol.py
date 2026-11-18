#!/usr/bin/env python3
"""Check quiet typed Boolean operands and constructor-only FULL conditions."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_not_operand_condition_typed_ternary_left_coalesce_quiet_get_review_protocol as prior

raw, renderer, payload = prior.raw, prior.renderer, prior.payload
source_tree, bindings, roots = prior.source_tree, prior.bindings, prior.roots
operand, typed, certificate = prior.operand, prior.typed, prior.certificate
old_bytes, condition = prior.old_bytes, prior.condition
NULL, FALSE, TRUE = prior.NULL, prior.FALSE, prior.TRUE
string, pstring = prior.string, prior.pstring
CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_boolean_operand_condition_typed_ternary_left_coalesce_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_bytes())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
KINDS = {'&&': 'BooleanAnd', 'and': 'LogicalAnd', '||': 'BooleanOr', 'or': 'LogicalOr', 'xor': 'LogicalXor'}

# operator, left/right values, Boolean result, position, selected value, echo.
SITES = [
    {'class': [('&&', pstring(b'00'), 'PINT 0', False, 'operand', 'PBOOL false', b''),
               ('and', 'PNULL', 'PBOOL true', False, 'condition', 'PINT 0', b'0'),
               ('||', pstring(b'00'), pstring(b'0'), True, 'condition', pstring(b'0'), b'0'),
               ('or', pstring(b''), pstring(b'0'), False, 'condition', pstring(b'0'), b'0')],
     'method': [('xor', 'PINT 0', 'PINT 7', True, 'condition', pstring(b'0'), b'0'),
                ('&&', 'PBOOL false', pstring(b'00'), False, 'operand', 'PBOOL false', b''),
                ('||', pstring(b''), pstring(b'10'), True, 'operand', 'PBOOL true', b'1'),
                ('xor', 'PBOOL false', 'PNULL', False, 'condition', 'PINT 0', b'0'),
                ('and', 'PINT 7', pstring(b'00'), True, 'not-operand', 'PBOOL false', b'')]},
    {'class': [('&&', pstring(b'00'), 'PINT 7', True, 'condition', pstring(b'00'), b'00'),
               ('or', 'PINT 0', pstring(b'00'), True, 'condition', pstring(b'1'), b'1'),
               ('xor', 'PBOOL true', 'PINT 7', False, 'condition', pstring(b'0'), b'0'),
               ('and', 'PNULL', pstring(b'00'), False, 'condition', pstring(b''), b'')],
     'method': [('||', pstring(b''), pstring(b'0'), False, 'condition', 'PINT 0', b'0'),
                ('xor', pstring(b'00'), 'PBOOL false', True, 'condition', pstring(b'0'), b'0'),
                ('xor', 'PBOOL true', pstring(b'00'), False, 'operand', 'PBOOL false', b''),
                ('or', pstring(b'00'), 'PNULL', True, 'not-operand', 'PBOOL false', b'')]},
]


def actual_sites(index):
    result = roots(index)
    for side, items in SITES[index].items():
        for number, (op, left_value, right_value, truth, position, selected, echo) in enumerate(items):
            label = f'boolean_{side}_{number}'
            path = (0 if side == 'class' else 1,) + (0,) * (len(items) - number - 1) + (1,)
            origin, left, boolean, lhs, rhs = ('porigin_' + label + suffix for suffix in ('', '_left', '_boolean', '_lhs', '_rhs'))
            expression, expression_left, expression_boolean, expression_lhs, expression_rhs = ('expression_' + label + suffix for suffix in ('', '_left', '_boolean', '_lhs', '_rhs'))
            boolean_path = (0,) if position == 'condition' else ((1, 0) if position == 'not-operand' else (1,))
            value = 'PBOOL true' if truth else 'PBOOL false'
            result += [f'$origin_child((porigin_site),{raw.path(path)}) = ({origin})',
                       f'$origin_node(S.SOURCES,{origin}) = ({expression})',
                       f'{expression} = NExprBinaryOpCoalesce {expression_left} expression_{label}_fallback metadata_{label}_outer',
                       f'$origin_child(({origin}),[PCFIELD 0]) = ({left})',
                       typed('S.SOURCES', left, expression_left) + f' = ({selected})',
                       certificate('S.SOURCES', origin, expression) + ' = (' + payload(echo) + ')',
                       f'$origin_child(({left}),{raw.path(boolean_path)}) = ({boolean})',
                       f'$origin_node(S.SOURCES,{boolean}) = ({expression_boolean})',
                       f'{expression_boolean} = NExprBinaryOp{KINDS[op]} {expression_lhs} {expression_rhs} metadata_{label}_boolean',
                       f'$origin_child(({boolean}),[PCFIELD 0]) = ({lhs})',
                       f'$origin_child(({boolean}),[PCFIELD 1]) = ({rhs})',
                       operand('S.SOURCES', lhs, expression_lhs) + f' = ({left_value})',
                       operand('S.SOURCES', rhs, expression_rhs) + f' = ({right_value})',
                       old_bytes('S.SOURCES', boolean, expression_boolean) + ' = eps',
                       operand('S.SOURCES', boolean, expression_boolean) + f' = ({value})',
                       condition('S.SOURCES', boolean, expression_boolean) + ' = (' + payload(b'1' if truth else b'') + ')']
    return result


COALESCE_FALSE = ('??', ('?', TRUE, NULL, FALSE), FALSE)
COALESCE_TRUE = ('??', ('?', TRUE, NULL, FALSE), TRUE)
TERNARY_TRUE = ('?', TRUE, COALESCE_TRUE, FALSE)
NOT_FALSE = ('!', TERNARY_TRUE)
# The six exact old AST/callees whose maintained None tails are promoted.
LEGACY = [
    ('coalesce_bound_12', ('and', TRUE, COALESCE_FALSE), 'operand', 'PBOOL false'),
    ('condition_parent_2', ('and', TRUE, COALESCE_TRUE), 'condition', b'1'),
    ('ternary_condition_parent_1', ('and', TRUE, TERNARY_TRUE), 'condition', b'1'),
    ('not_parent_1', ('and', TRUE, NOT_FALSE), 'condition', b''),
    ('not_parent_2', ('or', FALSE, NOT_FALSE), 'condition', b''),
    ('not_parent_3', ('xor', TRUE, NOT_FALSE), 'condition', b'1'),
]


def values_and_positions():
    result = bindings()
    for op in KINDS:
        for left in (False, True):
            for right in (False, True):
                truth = (left and right) if op in ('&&', 'and') else ((left or right) if op in ('||', 'or') else left != right)
                shape = (op, COALESCE_TRUE if left else COALESCE_FALSE, COALESCE_TRUE if right else COALESCE_FALSE)
                expression, _, occurrences = source_tree(shape, f'boolean_value_{KINDS[op]}_{left}_{right}')
                state = f'S_boolean_value_{KINDS[op]}_{left}_{right}'
                result += [f'{state} = ' + raw.source_state(occurrences),
                           old_bytes(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps',
                           operand(state + '.SOURCES', 'porigin_tree_root_class', expression) + (' = (PBOOL true)' if truth else ' = (PBOOL false)'),
                           condition(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = (' + payload(b'1' if truth else b'') + ')']
    for number, (label, shape, helper, value) in enumerate(LEGACY):
        expression, _, occurrences = source_tree(shape, 'boolean_legacy_' + str(number))
        state = 'S_boolean_legacy_' + str(number)
        call = operand if helper == 'operand' else condition
        expected = value if helper == 'operand' else payload(value)
        result += [f'{state} = ' + raw.source_state(occurrences),
                   old_bytes(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps',
                   call(state + '.SOURCES', 'porigin_tree_root_class', expression) + f' = ({expected})']
    for number, (shape, value) in enumerate([(('?', TRUE, ('&&', COALESCE_TRUE, COALESCE_FALSE), NULL), 'PBOOL false'),
                                           (('?', FALSE, NULL, ('||', COALESCE_FALSE, COALESCE_TRUE)), 'PBOOL true'),
                                           (('?', ('xor', COALESCE_TRUE, COALESCE_FALSE), None, NULL), 'PBOOL true'),
                                           (('?', FALSE, None, ('and', COALESCE_TRUE, COALESCE_FALSE)), 'PBOOL false')]):
        expression, _, occurrences = source_tree(shape, 'boolean_position_' + str(number))
        state = 'S_boolean_position_' + str(number)
        result += [f'{state} = ' + raw.source_state(occurrences),
                   operand(state + '.SOURCES', 'porigin_tree_root_class', expression) + f' = ({value})']
    return result


def source_authority(skipped):
    result = bindings()
    for op in KINDS:
        shape = ('?', FALSE if skipped else TRUE, (op, COALESCE_FALSE, COALESCE_TRUE), TRUE)
        expression, nodes, occurrences = source_tree(shape, 'boolean_source_' + KINDS[op])
        state = 'S_boolean_source_' + KINDS[op]
        truth = skipped or op not in ('&&', 'and')
        result += [f'{state} = ' + raw.source_state(occurrences),
                   operand(state + '.SOURCES', 'porigin_tree_root_class', expression) + (' = (PBOOL true)' if truth else ' = (PBOOL false)')]
        for number, (parts, node, metadata, _, _) in enumerate(nodes):
            if parts not in ((), (1,), (1, 0), (1, 1)):
                continue
            path = 'pcpath_site ++ ' + raw.path((0,) + parts)
            changes = [('missing', f'$rawtree_review_without({state}.SOURCES[0].OCCURRENCES,{path})'),
                       ('metadata', f'(PCOCCURRENCE ({path}) ({node.removesuffix(metadata)}eps)) :: {state}.SOURCES[0].OCCURRENCES')]
            for label, source in changes:
                changed = f'{state}_{number}_{label}'
                result += [f'{changed} = ' + raw.source_state(source),
                           operand(changed + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    return result


def bounds():
    result = bindings()
    bad = [string(b'\0'), ('f', '0000000000000000'), ('f', '7ff8000000000000'),
           ('cv', b'skipped'), ('i', 9223372036854775808), ('-', ('i', 1)), ('+', ('i', 1))]
    shapes = [(op, FALSE if op in ('&&', 'and') else TRUE, ('cv', b'skipped')) for op in KINDS]
    shapes += [('&&', item, COALESCE_TRUE) for item in bad]
    shapes += [('or', COALESCE_TRUE, item) for item in bad]
    for number, shape in enumerate(shapes):
        expression, _, occurrences = source_tree(shape, 'boolean_bound_' + str(number))
        state = 'S_boolean_bound_' + str(number)
        result += [f'{state} = ' + raw.source_state(occurrences),
                   old_bytes(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps',
                   operand(state + '.SOURCES', 'porigin_tree_root_class', expression) + (' = (PBOOL true)' if number in (10, 11, 17, 18) else ' = eps'),
                   condition(state + '.SOURCES', 'porigin_tree_root_class', expression) + (' = (' + payload(b'1') + ')' if number in (10, 11, 17, 18) else ' = eps')]
    expression, _, occurrences = source_tree(('.', ('&&', COALESCE_TRUE, COALESCE_FALSE), string(b'')), 'boolean_concat_parent')
    result += ['S_boolean_concat_parent = ' + raw.source_state(occurrences),
               old_bytes('S_boolean_concat_parent.SOURCES', 'porigin_tree_root_class', expression) + ' = eps',
               condition('S_boolean_concat_parent.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    for number, shape in enumerate([('&&', COALESCE_FALSE, string(b'OWNER')), ('or', COALESCE_TRUE, string(b'OWNER'))]):
        expression, _, occurrences = source_tree(shape, 'boolean_owner_' + str(number))
        placeholder = 'NScalarString (BYTES "T1dORVI=") metadata_class'
        assert placeholder in expression and placeholder in occurrences
        child = 'NExprArray (SEQUENCE eps) metadata_class'
        expression, occurrences = expression.replace(placeholder, child), occurrences.replace(placeholder, child)
        state = 'S_boolean_owner_' + str(number)
        result += [f'{state} = ' + raw.source_state(occurrences),
                   operand(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps',
                   condition(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    return result


CASES = {}
for index, row in enumerate(ROWS):
    base = dict(prior.CASES[prior.ROWS[index]['id'] + '-actual-sites'], source=row['source'])
    CASES[row['id'] + '-actual-sites'] = dict(base, checks=actual_sites(index))
base = CASES[ROWS[0]['id'] + '-actual-sites']
value_checks = values_and_positions()
value_prefix = len(bindings())
value_split = value_prefix + 56
for suffix, checks in [('values-positions-1', value_checks[:value_split]),
                       ('values-positions-2', value_checks[:value_prefix] + value_checks[value_split:]),
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
