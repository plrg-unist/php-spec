#!/usr/bin/env python3
"""Check typed COALESCE operands, mutual nesting and complete quiet SOURCE."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_nested_operand_typed_ternary_left_coalesce_quiet_get_review_protocol as prior

raw, renderer, payload = prior.raw, prior.renderer, prior.payload
tree, source_tree, bindings = prior.tree, prior.source_tree, prior.bindings
operand, typed, certificate = prior.operand, prior.typed, prior.certificate
NULL, FALSE, TRUE = prior.NULL, prior.FALSE, prior.TRUE
string, pstring = prior.string, prior.pstring
CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_coalesce_operand_typed_ternary_left_coalesce_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_bytes())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

SITES = [
    {'class': [
        (('?', TRUE, ('??', NULL, ('?', FALSE, NULL, FALSE)), NULL), b'BAD_NULL_FALSE', 'PBOOL false', b''),
        (('?', string(b'0'), TRUE, ('??', FALSE, NULL)), b'BAD_FALSE_NULL', 'PBOOL false', b''),
        (('?', TRUE, ('??', string(b''), string(b'BAD_EMPTY')), FALSE), b'BAD_EMPTY_FALLBACK', pstring(b''), b''),
        (('?', TRUE, ('??', NULL, NULL), FALSE), b'0', 'PNULL', b'0'),
        (('?', TRUE, ('??', ('?', FALSE, NULL, string(b'0')), ('?', TRUE, TRUE, FALSE)), FALSE), b'BAD_ZERO_FALLBACK', pstring(b'0'), b'0'),
        (('?', ('??', string(b'0'), string(b'BAD_COND')), None, ('??', ('i', 0), FALSE)), b'BAD_SHORT_ZERO', 'PINT 0', b'0')],
     'method': [
        (('?', TRUE, ('??', ('i', 0), string(b'BAD_INT')), NULL), b'BAD_INT_FALLBACK', 'PINT 0', b'0'),
        (('?', ('??', string(b'1'), FALSE), None, NULL), b'BAD_SHORT_STRING', pstring(b'1'), b'1'),
        (('?', ('??', string(b''), FALSE), None, ('??', NULL, string(b'0'))), b'BAD_SHORT_FALLBACK', pstring(b'0'), b'0')]},
    {'class': [
        (('?', TRUE, ('??', ('??', NULL, NULL), NULL), FALSE), b'00', 'PNULL', b'00'),
        (('?', ('??', ('.', string(b'1'), ('i', 0)), FALSE), None, ('??', NULL, TRUE)), b'BAD_SHORT_TRUE', pstring(b'10'), b'10'),
        (('?', FALSE, NULL, ('??', string(b''), FALSE)), b'BAD_EMPTY', pstring(b''), b'')],
     'method': [
        (('?', TRUE, ('??', ('??', NULL, ('i', 0)), TRUE), FALSE), b'BAD_INT', 'PINT 0', b'0'),
        (('?', ('??', FALSE, ('.', string(b'BAD'), string(b'LEFT'))), None, ('??', ('??', string(b'0'), NULL), FALSE)), b'BAD_SHORT_ZERO', pstring(b'0'), b'0')]},
]


def actual_sites(index, side):
    result = prior.prior.prior.roots(index)
    items = SITES[index][side]
    for number, (left, right, value, echo) in enumerate(items):
        label = f'coalescing_{side}_{number}'
        parts = (0 if side == 'class' else 1,) + (0,) * (len(items) - number - 1) + (1,)
        expression, nodes, extra = tree(('??', left, string(right)), label)
        expression_left = dict(nodes[0][4])[0]
        origin, origin_left = 'porigin_' + label, 'porigin_' + label + '_left'
        result += [f'$origin_child((porigin_site),{raw.path(parts)}) = ({origin})',
                   f'$origin_node(S.SOURCES,{origin}) = ({expression})', *extra,
                   f'$origin_child(({origin}),[PCFIELD 0]) = ({origin_left})',
                   typed('S.SOURCES', origin_left, expression_left) + f' = ({value})',
                   operand('S.SOURCES', origin_left, expression_left) + f' = ({value})',
                   certificate('S.SOURCES', origin, expression) + ' = (' + payload(echo) + ')']
        if left[2] is None:
            absent = 'porigin_' + label + '_absent'
            result += [f'$origin_child(({origin_left}),[PCFIELD 1]) = ({absent})',
                       f'$origin_node(S.SOURCES,{absent}) = eps']
    return result


def values():
    cases = [
        (('??', NULL, NULL), 'PNULL'), (('??', FALSE, NULL), 'PBOOL false'),
        (('??', NULL, FALSE), 'PBOOL false'), (('??', TRUE, NULL), 'PBOOL true'),
        (('??', ('i', 0), TRUE), 'PINT 0'), (('??', NULL, ('i', 0)), 'PINT 0'),
        (('??', string(b''), TRUE), pstring(b'')), (('??', string(b'0'), NULL), pstring(b'0')),
        (('??', NULL, ('.', string(b'1'), ('i', 0))), pstring(b'10')),
        (('??', ('and', TRUE, FALSE), NULL), 'PBOOL false'),
        (('??', ('?', TRUE, NULL, FALSE), ('?', FALSE, TRUE, ('??', NULL, FALSE))), 'PBOOL false'),
        (('??', ('?', FALSE, NULL, string(b'0')), ('?', TRUE, TRUE, FALSE)), pstring(b'0')),
        (('??', ('??', NULL, NULL), NULL), 'PNULL'),
        (('??', NULL, ('??', NULL, ('i', 0))), 'PINT 0'),
        (('??', ('i', 9223372036854775807), NULL), 'PINT 9223372036854775807'),
    ]
    result = bindings()
    for number, (shape, value) in enumerate(cases):
        expression, _, occurrences = source_tree(shape, 'coalesce_value_' + str(number))
        state = 'S_coalesce_value_' + str(number)
        result += [f'{state} = ' + raw.source_state(occurrences),
                   operand(state + '.SOURCES', 'porigin_tree_root_class', expression) + f' = ({value})']
    return result


def source_authority(skipped):
    left = FALSE if skipped else NULL
    shape = ('??', ('?', TRUE, left, FALSE), ('?', FALSE, TRUE, ('??', NULL, FALSE)))
    expression, nodes, occurrences = source_tree(shape, 'coalesce_source')
    result = bindings()
    result += ['S_coalesce_source = ' + raw.source_state(occurrences),
               operand('S_coalesce_source.SOURCES', 'porigin_tree_root_class', expression) + ' = (PBOOL false)']
    for number, (parts, node, metadata, kind, _) in enumerate(nodes):
        path = 'pcpath_site ++ ' + raw.path((0,) + parts)
        changes = [('missing', f'$rawtree_review_without(S_coalesce_source.SOURCES[0].OCCURRENCES,{path})')]
        if kind == 'k':
            changes += [('missing_name', f'$rawtree_review_without(S_coalesce_source.SOURCES[0].OCCURRENCES,{path} ++ [PCFIELD 0])')]
        if kind in ('??', '?'):
            changes += [('metadata', f'(PCOCCURRENCE ({path}) ({node.removesuffix(metadata)}eps)) :: S_coalesce_source.SOURCES[0].OCCURRENCES')]
        for label, source in changes:
            state = f'S_coalesce_source_{number}_{label}'
            result += [f'{state} = ' + raw.source_state(source),
                       operand(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    return result


def bounds():
    bad = [string(b'\0'), ('f', '0000000000000000'), ('f', '7ff8000000000000'),
           ('cv', b'value'), ('i', 9223372036854775808)]
    shapes = [('??', item, FALSE) for item in bad] + [('??', TRUE, item) for item in bad]
    shapes += [
        ('?', ('??', ('?', TRUE, NULL, FALSE), FALSE), NULL, FALSE),
        ('.', ('??', ('?', TRUE, NULL, FALSE), FALSE), string(b'')),
        ('and', TRUE, ('??', ('?', TRUE, NULL, FALSE), FALSE)),
    ]
    result = bindings()
    for number, shape in enumerate(shapes):
        expression, _, occurrences = source_tree(shape, 'coalesce_bound_' + str(number))
        state = 'S_coalesce_bound_' + str(number)
        value = '(PBOOL false)' if number in (10, 12) else 'eps'
        result += [f'{state} = ' + raw.source_state(occurrences),
                   operand(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = ' + value]
    shape = ('??', ('??', ('?', TRUE, NULL, FALSE), FALSE), string(b'R'))
    expression, _, occurrences = source_tree(shape, 'coalesce_parent')
    result += ['S_coalesce_parent = ' + raw.source_state(occurrences),
               certificate('S_coalesce_parent.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    for number, shape in enumerate((('??', TRUE, string(b'OWNER')),
                                   ('??', NULL, string(b'OWNER')),
                                   ('??', string(b'OWNER'), FALSE))):
        expression, _, occurrences = source_tree(shape, 'coalesce_owner_' + str(number))
        placeholder = 'NScalarString (BYTES "T1dORVI=") metadata_class'
        assert placeholder in expression and placeholder in occurrences
        child = 'NExprArray (SEQUENCE eps) metadata_class'
        expression, occurrences = expression.replace(placeholder, child), occurrences.replace(placeholder, child)
        state = 'S_coalesce_owner_' + str(number)
        result += [f'{state} = ' + raw.source_state(occurrences),
                   operand(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    return result


def root_authority():
    return prior.prior.prior.roots(0) + [
        'S_coalesce_without_code = S[.CODE = eps]',
        '$property_magic_cv_emitted_typed_ternary_left_coalesce_concat_value(S_coalesce_without_code,porigin_tree_root_class,expression_class) = eps',
        '~' + raw.selector('class', 'S_coalesce_without_code'),
        'S_coalesce_with_pool = S[.POOLS = [{UNIT n_unit,CONSTANTS ([PCONSTANT (pcpath_site ++ [PCFIELD 0]) (PSTRING ptbytes_class)])}]]',
        '$property_magic_cv_emitted_typed_ternary_left_coalesce_concat_value(S_coalesce_with_pool,porigin_tree_root_class,expression_class) = eps',
        '~' + raw.selector('class', 'S_coalesce_with_pool')]


def legacy_promotions():
    full = ('?', string(b'00'), NULL, FALSE)
    computed = ('??', ('?', TRUE, ('!', string(b'00')), NULL), string(b'R'))
    cases = [
        ('existing', 'typed_domain_0', typed, ('?', TRUE, ('!', FALSE), NULL), 'PBOOL true'),
        ('existing', 'typed_domain_1', typed, ('?', TRUE, ('.', string(b''), FALSE), NULL), pstring(b'')),
        ('existing', 'typed_domain_2', typed, ('?', TRUE, full, NULL), 'PNULL'),
        ('existing', 'typed_domain_10', typed, ('?', ('!', FALSE), None, NULL), 'PBOOL true'),
        ('existing', 'typed_domain_11', typed, ('?', string(b'10'), None, full), pstring(b'10')),
        ('existing', 'computed_domain_0', operand, ('?', TRUE, NULL, FALSE), 'PNULL'),
        ('new', 'computed_domain_1', operand, ('??', NULL, FALSE), 'PBOOL false'),
        ('new', 'computed_domain_2', operand, ('??', FALSE, NULL), 'PBOOL false'),
        ('existing', 'computed_bad_operand_4', typed, ('?', TRUE, ('?', TRUE, NULL, FALSE), FALSE), 'PNULL'),
        ('new', 'computed_bad_operand_5', typed, ('?', FALSE, NULL, ('??', NULL, string(b'R'))), pstring(b'R')),
        ('new', 'computed_bad_operand_6', typed, ('?', ('??', NULL, TRUE), None, FALSE), 'PBOOL true'),
        ('new', 'computed_bad_operand_7', typed, ('?', TRUE, computed, NULL), 'PBOOL false'),
        ('new', 'computed_bad_operand_8', typed, ('?', FALSE, NULL, computed), 'PBOOL false'),
        ('new', 'nested_domain_3', operand, prior.depth_four(('??', NULL, FALSE), FALSE), 'PBOOL false'),
        ('new', 'nested_domain_6', operand, prior.depth_four(NULL, ('??', NULL, FALSE)), 'PBOOL false'),
        ('new', 'nested_domain_7', operand, ('?', ('??', NULL, TRUE), None, FALSE), 'PBOOL true'),
        ('new', 'nested_parent_0', operand, ('??', NULL, FALSE), 'PBOOL false'),
    ]
    result = bindings()
    for category, label, call, shape, value in cases:
        expression, _, occurrences = source_tree(shape, 'legacy_' + label)
        state = 'S_legacy_' + category + '_' + label
        result += [f'{state} = ' + raw.source_state(occurrences),
                   call(state + '.SOURCES', 'porigin_tree_root_class', expression) + f' = ({value})']
    return result


CASES = {}
for index, row in enumerate(ROWS):
    base = dict(prior.CASES[prior.ROWS[index]['id'] + '-actual-sites'], source=row['source'])
    roots = prior.prior.prior.roots(index)
    class_checks, method_checks = actual_sites(index, 'class'), actual_sites(index, 'method')
    assert class_checks[:len(roots)] == method_checks[:len(roots)] == roots
    checks = class_checks + method_checks[len(roots):]
    CASES[row['id'] + '-actual-sites'] = dict(base, checks=checks)
base = CASES[ROWS[0]['id'] + '-actual-sites']
for suffix, checks in [('values', values()), ('selected-source', source_authority(False)),
                       ('skipped-source', source_authority(True)), ('bounds', bounds()),
                       ('root-authority', root_authority()), ('legacy-promotions', legacy_promotions())]:
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
