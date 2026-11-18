#!/usr/bin/env python3
"""Check known scalar tags in typed ternary operands and source authority."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_typed_ternary_left_coalesce_quiet_get_review_protocol as prior

raw, renderer, payload = prior.raw, prior.renderer, prior.payload
tree, source_tree, bindings = prior.tree, prior.source_tree, prior.bindings
typed, certificate = prior.typed, prior.certificate
NULL, FALSE, TRUE = prior.NULL, prior.FALSE, prior.TRUE
string, pstring = prior.string, prior.pstring
CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_computed_operand_typed_ternary_left_coalesce_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_bytes())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def operand(sources, origin, expression):
    return f'$property_magic_cv_raw_typed_ternary_operand_value({sources},{origin},{expression})'


SITES = [
    {'class': [
        (('?', string(b'00'), NULL, ('.', string(b'BAD'), string(b'_FULL_NULL'))), b'0', 'PNULL', b'0'),
        (('?', TRUE, ('!', string(b'00')), string(b'BAD_FULL_FALSE')), b'BAD_FALSE_FALLBACK', 'PBOOL false', b''),
        (('?', TRUE, ('.', string(b''), FALSE), string(b'BAD_FULL_EMPTY')), b'BAD_EMPTY_FALLBACK', pstring(b''), b''),
        (('?', TRUE, ('.', string(b'0'), NULL), string(b'BAD_FULL_ZERO')), b'BAD_ZERO_FALLBACK', pstring(b'0'), b'0'),
        (('?', ('.', string(b'0'), NULL), None, NULL), b'0', 'PNULL', b'0')],
     'method': [
        (('?', TRUE, ('i', 0), string(b'BAD_FULL_INT')), b'BAD_INT_FALLBACK', 'PINT 0', b'0'),
        (('?', ('and', TRUE, string(b'00')), None, string(b'BAD_SHORT_TRUE')), b'BAD_SHORT_TRUE_FALLBACK', 'PBOOL true', b'1'),
        (('?', TRUE, ('.', string(b'0'), FALSE), string(b'BAD_FULL_STRING0')), b'BAD_STRING0_FALLBACK', pstring(b'0'), b'0'),
        (('?', ('!', string(b'00')), None, ('.', string(b''), NULL)), b'BAD_SHORT_FALSE_FALLBACK', pstring(b''), b'')]},
    {'class': [
        (('?', string(b'0'), ('.', string(b'BAD'), string(b'_FULL_TRUE')), NULL), b'00', 'PNULL', b'00'),
        (('?', ('.', string(b'1'), ('i', 0)), None, string(b'BAD_SHORT_INT')), b'BAD_SHORT_INT_FALLBACK', pstring(b'10'), b'10')],
     'method': [
        (('?', string(b'0'), string(b'BAD_FULL_INT_TRUE'), ('i', 0)), b'BAD_INT_FALLBACK', 'PINT 0', b'0'),
        (('?', ('and', FALSE, TRUE), None, ('.', string(b'0'), NULL)), b'BAD_STRING_ZERO_FALLBACK', pstring(b'0'), b'0'),
        (('?', string(b'0'), string(b'BAD_FULL_EMPTY_TRUE'), ('.', string(b''), FALSE)), b'BAD_EMPTY_FALLBACK', pstring(b''), b''),
        (('?', string(b'0'), string(b'BAD_FULL_FALSE_TRUE'), ('and', TRUE, FALSE)), b'BAD_FALSE_FALLBACK', 'PBOOL false', b'')]},
]


def actual_sites(index):
    result = prior.roots(index)
    for side, items in SITES[index].items():
        for number, (left, right, value, echo) in enumerate(items):
            label = f'computed_{side}_{number}'
            parts = (0 if side == 'class' else 1,) + (0,) * (len(items) - number - 1) + (1,)
            expression, nodes, extra = tree(('??', left, string(right)), label)
            expression_left = dict(nodes[0][4])[0]
            origin, origin_left = 'porigin_' + label, 'porigin_' + label + '_left'
            result += [f'$origin_child((porigin_site),{raw.path(parts)}) = ({origin})',
                       f'$origin_node(S.SOURCES,{origin}) = ({expression})', *extra,
                       f'$origin_child(({origin}),[PCFIELD 0]) = ({origin_left})',
                       typed('S.SOURCES', origin_left, expression_left) + f' = ({value})',
                       certificate('S.SOURCES', origin, expression) + ' = (' + payload(echo) + ')']
            if left[2] is None:
                absent = 'porigin_' + label + '_absent'
                result += [f'$origin_child(({origin_left}),[PCFIELD 1]) = ({absent})',
                           f'$origin_node(S.SOURCES,{absent}) = eps']
    return result


def values_and_positions():
    cases = [(NULL, 'PNULL'), (FALSE, 'PBOOL false'), (TRUE, 'PBOOL true'),
             (('i', 0), 'PINT 0'), (string(b''), pstring(b'')), (string(b'0'), pstring(b'0')),
             (('.', string(b''), FALSE), pstring(b'')),
             (('.', string(b'0'), NULL), pstring(b'0')),
             (('.', TRUE, NULL), pstring(b'1')),
             (('.', string(b'0'), TRUE), pstring(b'01')),
             (('.', string(b'1'), ('i', 0)), pstring(b'10')),
             (('!', string(b'00')), 'PBOOL false'), (('!', string(b'0')), 'PBOOL true')]
    for op in ('&&', 'and', '||', 'or', 'xor'):
        left = FALSE if op in ('||', 'or') else TRUE
        cases += [((op, left, FALSE), 'PBOOL false' if op != 'xor' else 'PBOOL true'),
                  ((op, left, TRUE), 'PBOOL true' if op != 'xor' else 'PBOOL false')]
    cases += [(('.', ('??', NULL, string(b'01')), FALSE), pstring(b'01')),
              (('!', ('?', string(b'00'), NULL, FALSE)), 'PBOOL true')]
    result = bindings()
    for number, (shape, value) in enumerate(cases):
        expression, _, occurrences = source_tree(shape, 'operand_' + str(number))
        state = 'S_computed_operand_' + str(number)
        result += [f'{state} = ' + raw.source_state(occurrences),
                   operand(state + '.SOURCES', 'porigin_tree_root_class', expression) + f' = ({value})']
        if shape[0] not in ('k', 'i', 's'):
            result += [f'$property_magic_cv_raw_primitive_coalesce_left({state}.SOURCES,porigin_tree_root_class,{expression}) = eps']
    positions = [
        (('?', TRUE, ('!', string(b'00')), ('.', string(b'0'), NULL)), 'PBOOL false', b''),
        (('?', FALSE, ('.', string(b'BAD'), FALSE), ('and', TRUE, FALSE)), 'PBOOL false', b''),
        (('?', ('.', string(b'0'), TRUE), None, ('!', TRUE)), pstring(b'01'), b'01'),
        (('?', ('!', TRUE), None, ('.', string(b'0'), NULL)), pstring(b'0'), b'0'),
        (('?', ('and', TRUE, string(b'00')), None, ('.', string(b'BAD'), FALSE)), 'PBOOL true', b'1'),
        (('?', ('.', string(b''), FALSE), None, ('and', TRUE, FALSE)), 'PBOOL false', b''),
        (('?', ('.', string(b'0'), NULL), None, NULL), 'PNULL', b'R'),
        (('?', ('!', FALSE), NULL, FALSE), 'PNULL', b'R'),
    ]
    for number, (shape, value, echo) in enumerate(positions):
        expression, nodes, occurrences = source_tree(('??', shape, string(b'R')), 'position_' + str(number))
        left = dict(nodes[0][4])[0]
        state, origin = 'S_computed_position_' + str(number), 'porigin_computed_position_' + str(number)
        result += [f'{state} = ' + raw.source_state(occurrences),
                   f'$origin_child((porigin_tree_root_class),[PCFIELD 0]) = ({origin})',
                   typed(state + '.SOURCES', origin, left) + f' = ({value})',
                   certificate(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = (' + payload(echo) + ')']
    return result


def source_and_bounds():
    result = bindings()
    shapes = [('?', TRUE, ('.', string(b'0'), NULL), ('and', TRUE, FALSE)),
              ('?', ('and', TRUE, string(b'00')), None, ('.', string(b''), FALSE))]
    for number, shape in enumerate(shapes):
        expression, nodes, occurrences = source_tree(shape, 'source_' + str(number))
        state = 'S_computed_source_' + str(number)
        value = pstring(b'0') if number == 0 else 'PBOOL true'
        result += [f'{state} = ' + raw.source_state(occurrences),
                   typed(state + '.SOURCES', 'porigin_tree_root_class', expression) + f' = ({value})']
        for position, (parts, node, metadata, kind, _) in enumerate(nodes):
            path = 'pcpath_site ++ ' + raw.path((0,) + parts)
            changes = [('missing', f'$rawtree_review_without({state}.SOURCES[0].OCCURRENCES,{path})')]
            if number == 0:
                changes += [('metadata', f'(PCOCCURRENCE ({path}) ({node.removesuffix(metadata)}eps)) :: {state}.SOURCES[0].OCCURRENCES')]
            for label, source in changes:
                changed = f'S_computed_source_{number}_{position}_{label}'
                result += [f'{changed} = ' + raw.source_state(source),
                           typed(changed + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    rejected = [
        ('?', TRUE, NULL, FALSE), ('??', NULL, FALSE), ('??', FALSE, NULL),
        ('i', 9223372036854775808), ('f', '0000000000000000'), ('cv', b'value'),
        ('.', string(b'\0'), FALSE), ('.', NULL, string(b'\0')),
        ('!', string(b'\0')), ('and', FALSE, ('cv', b'skipped')),
        ('or', TRUE, ('f', '7ff8000000000000')),
        ('xor', TRUE, string(b'\0')),
    ]
    for number, shape in enumerate(rejected):
        expression, _, occurrences = source_tree(shape, 'domain_' + str(number))
        state = 'S_computed_domain_' + str(number)
        value = {0: 'PNULL', 1: 'PBOOL false', 2: 'PBOOL false'}.get(number)
        result += [f'{state} = ' + raw.source_state(occurrences),
                   operand(state + '.SOURCES', 'porigin_tree_root_class', expression) + (' = eps' if value is None else f' = ({value})')]
    bad_operands = [
        ('?', TRUE, ('.', string(b'\0'), NULL), FALSE),
        ('?', TRUE, NULL, ('!', string(b'\0'))),
        ('?', ('and', TRUE, string(b'\0')), None, NULL),
        ('?', ('.', string(b'0'), NULL), None, ('.', string(b'\0'), FALSE)),
        ('?', TRUE, ('?', TRUE, NULL, FALSE), FALSE),
        ('?', FALSE, NULL, ('??', NULL, string(b'R'))),
        ('?', ('??', NULL, TRUE), None, FALSE),
    ]
    new = ('??', ('?', TRUE, ('!', string(b'00')), NULL), string(b'R'))
    bad_operands += [('?', TRUE, new, NULL), ('?', FALSE, NULL, new)]
    for number, shape in enumerate(bad_operands):
        expression, _, occurrences = source_tree(shape, 'bad_operand_' + str(number))
        state = 'S_computed_bad_operand_' + str(number)
        value = {4: 'PNULL', 5: pstring(b'R'), 6: 'PBOOL true', 7: 'PBOOL false', 8: 'PBOOL false'}.get(number)
        result += [f'{state} = ' + raw.source_state(occurrences),
                   typed(state + '.SOURCES', 'porigin_tree_root_class', expression) + (' = eps' if value is None else f' = ({value})')]
    parents = [('&&', new, TRUE), ('?', TRUE, new, FALSE), ('??', new, string(b'R')),
               ('??', ('.', new, string(b'')), string(b'R'))]
    for number, shape in enumerate(parents):
        expression, _, occurrences = source_tree(shape, 'parent_' + str(number))
        state = 'S_computed_parent_' + str(number)
        result += [f'{state} = ' + raw.source_state(occurrences),
                   certificate(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    expression, _, occurrences = source_tree(('.', string(b''), string(b'REJECT')), 'owner')
    placeholder = 'NScalarString (BYTES "UkVKRUNU") metadata_class'
    child = 'NExprArray (SEQUENCE eps) metadata_class'
    expression, occurrences = expression.replace(placeholder, child), occurrences.replace(placeholder, child)
    result += ['S_computed_owner = ' + raw.source_state(occurrences),
               operand('S_computed_owner.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    return result


CASES = {}
for index, row in enumerate(ROWS):
    base = dict(prior.CASES[prior.ROWS[index]['id'] + '-roots'], source=row['source'])
    CASES[row['id'] + '-actual-sites'] = dict(base, checks=actual_sites(index))
base = CASES[ROWS[0]['id'] + '-actual-sites']
for suffix, checks in (('values-positions', values_and_positions()),
                       ('source-bounds', source_and_bounds()),
                       ('root-authority', prior.authority('class'))):
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
