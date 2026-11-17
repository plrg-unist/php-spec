#!/usr/bin/env python3
"""Check nested typed ternary selection, recursive source and scalar boundaries."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_computed_operand_typed_ternary_left_coalesce_quiet_get_review_protocol as prior

raw, renderer, payload = prior.raw, prior.renderer, prior.payload
tree, source_tree, bindings = prior.tree, prior.source_tree, prior.bindings
operand, typed, certificate = prior.operand, prior.typed, prior.certificate
NULL, FALSE, TRUE = prior.NULL, prior.FALSE, prior.TRUE
string, pstring = prior.string, prior.pstring
CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_nested_operand_typed_ternary_left_coalesce_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_bytes())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

LEFTS = [
    {'class': [
        ('?', string(b'00'), ('?', string(b'0'), FALSE, NULL), ('.', string(b'BAD'), string(b'_FULL_NULL'))),
        ('?', TRUE, ('?', string(b'0'), NULL, ('!', string(b'00'))), string(b'BAD_FULL_FALSE')),
        ('?', TRUE, ('?', string(b'0'), FALSE, ('.', string(b''), FALSE)), string(b'BAD_FULL_EMPTY')),
        ('?', TRUE, ('?', ('.', string(b'0'), FALSE), None, ('.', string(b'0'), NULL)), string(b'BAD_FULL_ZERO')),
        ('?', ('?', string(b'0'), TRUE, ('.', string(b'0'), NULL)), None, ('?', FALSE, FALSE, NULL))],
     'method': [
        ('?', TRUE, ('i', 0), ('?', string(b'00'), ('.', string(b'BAD'), string(b'_FULL_INT')), NULL)),
        ('?', ('?', ('and', TRUE, string(b'00')), None, FALSE), None, string(b'BAD_SHORT_TRUE')),
        ('?', TRUE, ('?', string(b'0'), NULL, ('.', string(b'0'), FALSE)), string(b'BAD_FULL_STRING0')),
        ('?', ('?', FALSE, TRUE, ('!', string(b'00'))), None, ('?', FALSE, None, ('.', string(b''), NULL)))]},
    {'class': [
        ('?', string(b'0'), ('.', string(b'BAD'), string(b'_FULL_TRUE')), ('?', string(b'00'), NULL, FALSE)),
        ('?', ('?', string(b'0'), ('!', TRUE), ('.', string(b'1'), ('i', 0))), None, string(b'BAD_SHORT_INT'))],
     'method': [
        ('?', string(b'0'), string(b'BAD_FULL_INT_TRUE'), ('?', FALSE, None, ('i', 0))),
        ('?', ('?', FALSE, NULL, ('and', FALSE, TRUE)), None, ('?', string(b'0'), NULL, ('.', string(b'0'), NULL))),
        ('?', string(b'0'), string(b'BAD_FULL_EMPTY_TRUE'), ('?', ('.', string(b'0'), NULL), None, ('.', string(b''), FALSE))),
        ('?', string(b'0'), string(b'BAD_FULL_FALSE_TRUE'), ('?', string(b'0'), NULL, ('and', TRUE, FALSE)))]},
]
SITES = [{side: [(left, *old[1:]) for left, old in zip(lefts, prior.SITES[index][side], strict=True)]
          for side, lefts in sides.items()} for index, sides in enumerate(LEFTS)]


def actual_sites(index):
    result = prior.prior.roots(index)
    for side, items in SITES[index].items():
        for number, (left, right, value, echo) in enumerate(items):
            label = f'nested_{side}_{number}'
            parts = (0 if side == 'class' else 1,) + (0,) * (len(items) - number - 1) + (1,)
            expression, nodes, extra = tree(('??', left, string(right)), label)
            expression_left = dict(nodes[0][4])[0]
            origin, origin_left = 'porigin_' + label, 'porigin_' + label + '_left'
            result += [f'$origin_child((porigin_site),{raw.path(parts)}) = ({origin})',
                       f'$origin_node(S.SOURCES,{origin}) = ({expression})', *extra,
                       f'$origin_child(({origin}),[PCFIELD 0]) = ({origin_left})',
                       typed('S.SOURCES', origin_left, expression_left) + f' = ({value})',
                       certificate('S.SOURCES', origin, expression) + ' = (' + payload(echo) + ')']
            for position, (relative, _, _, kind, children) in enumerate(nodes):
                if kind == '?' and 1 not in dict(children):
                    absent = f'porigin_{label}_absent_{position}'
                    result += [f'$origin_child(({origin}),{raw.path(relative + (1,))}) = ({absent})',
                               f'$origin_node(S.SOURCES,{absent}) = eps']
    return result


def depth_four(leaf, fallback):
    first = ('?', string(b'00'), leaf, FALSE)
    second = ('?', first, None, ('.', string(b'0'), NULL))
    third = ('?', TRUE, second, ('?', TRUE, ('i', 0), FALSE))
    return ('?', third, None, ('?', FALSE, NULL, fallback))


def recursion_blocks():
    cases = [
        (('?', string(b'00'), NULL, FALSE), 'PNULL', b'R'),
        (('?', string(b'0'), NULL, FALSE), 'PBOOL false', b''),
        (('?', string(b'0'), FALSE, ('.', string(b''), FALSE)), pstring(b''), b''),
        (('?', TRUE, ('i', 0), string(b'0')), 'PINT 0', b'0'),
        (('?', FALSE, ('i', 0), string(b'0')), pstring(b'0'), b'0'),
        (('?', NULL, None, FALSE), 'PBOOL false', b''),
        (('?', FALSE, None, ('i', 0)), 'PINT 0', b'0'),
        (('?', string(b'0'), None, ('.', string(b''), NULL)), pstring(b''), b''),
        (('?', ('?', string(b'0'), NULL, ('.', string(b'1'), ('i', 0))), None, TRUE), pstring(b'10'), b'10'),
        (('?', ('?', TRUE, None, FALSE), None, string(b'10')), 'PBOOL true', b'1'),
        (('?', ('??', NULL, TRUE), NULL, FALSE), 'PNULL', b'R'),
        (depth_four(NULL, FALSE), 'PBOOL false', b''),
        (depth_four(NULL, NULL), 'PNULL', b'R'),
    ]
    for leaf, value, echo in ((('.', string(b'1'), ('i', 0)), pstring(b'10'), b'10'),
                              (('and', TRUE, string(b'00')), 'PBOOL true', b'1')):
        first = ('?', string(b'0'), NULL, leaf)
        second = ('?', first, None, FALSE)
        third = ('?', TRUE, second, NULL)
        cases += [(('?', third, None, FALSE), value, echo)]
    result = bindings()
    for number, (shape, value, echo) in enumerate(cases):
        expression, nodes, occurrences = source_tree(('??', shape, string(b'R')), 'value_' + str(number))
        left = dict(nodes[0][4])[0]
        state, origin = 'S_nested_value_' + str(number), 'porigin_nested_value_' + str(number)
        result += [f'{state} = ' + raw.source_state(occurrences),
                   f'$origin_child((porigin_tree_root_class),[PCFIELD 0]) = ({origin})',
                   operand(state + '.SOURCES', origin, left) + f' = ({value})',
                   certificate(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = (' + payload(echo) + ')']
    value_checks = result
    result = bindings()
    shape = depth_four(NULL, FALSE)
    expression, nodes, occurrences = source_tree(shape, 'source')
    result += ['S_nested_source = ' + raw.source_state(occurrences),
               operand('S_nested_source.SOURCES', 'porigin_tree_root_class', expression) + ' = (PBOOL false)']
    for number, (parts, node, metadata, kind, _) in enumerate(nodes):
        path = 'pcpath_site ++ ' + raw.path((0,) + parts)
        changes = [('missing', f'$rawtree_review_without(S_nested_source.SOURCES[0].OCCURRENCES,{path})')]
        if kind == '?':
            changes += [('metadata', f'(PCOCCURRENCE ({path}) ({node.removesuffix(metadata)}eps)) :: S_nested_source.SOURCES[0].OCCURRENCES')]
        for label, source in changes:
            state = f'S_nested_source_{number}_{label}'
            result += [f'{state} = ' + raw.source_state(source),
                       operand(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    source_checks = result
    result = bindings()
    rejected = [
        depth_four(string(b'\0'), FALSE), depth_four(('f', '0000000000000000'), FALSE),
        depth_four(('cv', b'value'), FALSE), depth_four(('??', NULL, FALSE), FALSE),
        depth_four(NULL, string(b'\0')), depth_four(NULL, ('f', '7ff8000000000000')),
        depth_four(NULL, ('??', NULL, FALSE)),
        ('?', ('??', NULL, TRUE), None, FALSE),
        ('?', TRUE, NULL, ('?', TRUE, ('cv', b'skipped'), FALSE)),
        ('?', string(b'\0'), NULL, FALSE),
    ]
    for number, shape in enumerate(rejected):
        expression, _, occurrences = source_tree(shape, 'domain_' + str(number))
        state = 'S_nested_domain_' + str(number)
        result += [f'{state} = ' + raw.source_state(occurrences),
                   operand(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    new = ('??', ('?', TRUE, ('?', string(b'00'), NULL, FALSE), FALSE), string(b'R'))
    parents = [('??', NULL, FALSE), ('&&', new, TRUE), ('?', TRUE, new, FALSE),
               ('??', new, string(b'R')), ('??', ('.', new, string(b'')), string(b'R'))]
    for number, shape in enumerate(parents):
        expression, _, occurrences = source_tree(shape, 'parent_' + str(number))
        state = 'S_nested_parent_' + str(number)
        result += [f'{state} = ' + raw.source_state(occurrences)]
        call = operand if number == 0 else certificate
        result += [call(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    expression, _, occurrences = source_tree(depth_four(NULL, string(b'REJECT')), 'owner')
    placeholder = 'NScalarString (BYTES "UkVKRUNU") metadata_class'
    child = 'NExprArray (SEQUENCE eps) metadata_class'
    expression, occurrences = expression.replace(placeholder, child), occurrences.replace(placeholder, child)
    result += ['S_nested_owner = ' + raw.source_state(occurrences),
               operand('S_nested_owner.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    return [('recursive-values', value_checks), ('deep-source', source_checks),
            ('domain-bounds', result)]


CASES = {}
for index, row in enumerate(ROWS):
    base = dict(prior.CASES[prior.ROWS[index]['id'] + '-actual-sites'], source=row['source'])
    CASES[row['id'] + '-actual-sites'] = dict(base, checks=actual_sites(index))
base = CASES[ROWS[0]['id'] + '-actual-sites']
for suffix, checks in [*recursion_blocks(),
                       ('root-authority', prior.prior.authority('class'))]:
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
