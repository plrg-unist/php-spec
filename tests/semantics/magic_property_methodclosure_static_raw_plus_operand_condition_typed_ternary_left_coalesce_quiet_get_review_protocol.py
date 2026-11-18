#!/usr/bin/env python3
"""Check quiet integer UnaryPlus tags and constructor-only FULL conditions."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_boolean_operand_condition_typed_ternary_left_coalesce_quiet_get_review_protocol as prior

raw, renderer, payload = prior.raw, prior.renderer, prior.payload
source_tree, bindings, roots = prior.source_tree, prior.bindings, prior.roots
operand, typed, certificate = prior.operand, prior.typed, prior.certificate
old_bytes, condition = prior.old_bytes, prior.condition
NULL, FALSE, TRUE = prior.NULL, prior.FALSE, prior.TRUE
string, pstring = prior.string, prior.pstring
CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_plus_operand_condition_typed_ternary_left_coalesce_quiet_get_review_cases_v2.json')
ROWS = json.loads(CATALOGUE.read_bytes())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

# position, typed child, converted integer, selected value, echo, old byte proof.
SITES = [
    {'class': [('condition', pstring(b'00'), 0, 'PBOOL false', b'', None),
               ('operand', 'PNULL', 0, 'PINT 0', b'0', None),
               ('operand', 'PBOOL false', 0, 'PINT 0', b'0', None),
               ('short', pstring(b'0'), 0, pstring(b'0'), b'0', None)],
     'method': [('operand', 'PINT 0', 0, 'PINT 0', b'0', None),
                ('condition', pstring(b'  -7 '), -7, 'PBOOL false', b'', None),
                ('operand', 'PBOOL true', 1, 'PINT 1', b'1', None),
                ('operand', pstring(b'00'), 0, 'PINT 0', b'0', b'0'),
                ('condition', 'PINT 1', 1, pstring(b''), b'', None)]},
    {'class': [('operand', pstring(b'00'), 0, 'PINT 0', b'0', b'0'),
               ('operand', 'PNULL', 0, 'PINT 0', b'0', None),
               ('operand', 'PBOOL true', 1, 'PINT 1', b'1', None),
               ('operand', pstring(b'  +0 '), 0, 'PINT 0', b'0', None)],
     'method': [('condition', pstring(b'+12'), 12, pstring(b'0'), b'0', None),
                ('condition', pstring(b'-0'), 0, 'PINT 0', b'0', None),
                ('condition', pstring(b'9223372036854775807'), 9223372036854775807, 'PBOOL false', b'', None),
                ('condition', pstring(b' -9223372036854775808'), -9223372036854775808, pstring(b''), b'', None)]},
]


def actual_sites(index):
    result = roots(index)
    for side, items in SITES[index].items():
        for number, (position, child_value, integer, selected, echo, old_echo) in enumerate(items):
            integer_term = f'({integer})' if integer < 0 else str(integer)
            label = f'plus_{side}_{number}'
            path = (0 if side == 'class' else 1,) + (0,) * (len(items) - number - 1) + (1,)
            origin, left, plus, child = ('porigin_' + label + suffix for suffix in ('', '_left', '_plus', '_child'))
            expression, expression_left, expression_plus, expression_child = ('expression_' + label + suffix for suffix in ('', '_left', '_plus', '_child'))
            result += [f'$origin_child((porigin_site),{raw.path(path)}) = ({origin})',
                       f'$origin_node(S.SOURCES,{origin}) = ({expression})',
                       f'{expression} = NExprBinaryOpCoalesce {expression_left} expression_{label}_fallback metadata_{label}_outer',
                       f'$origin_child(({origin}),[PCFIELD 0]) = ({left})',
                       typed('S.SOURCES', left, expression_left) + f' = ({selected})',
                       certificate('S.SOURCES', origin, expression) + ' = (' + payload(echo) + ')',
                       f'$origin_child(({left}),{raw.path((1,) if position == "operand" else (0,))}) = ({plus})',
                       f'$origin_node(S.SOURCES,{plus}) = ({expression_plus})',
                       f'{expression_plus} = NExprUnaryPlus {expression_child} metadata_{label}_plus',
                       f'$origin_child(({plus}),[PCFIELD 0]) = ({child})',
                       operand('S.SOURCES', child, expression_child) + f' = ({child_value})',
                       f'$coerce_number({child_value}) = COERCED (NINT {integer_term}) false',
                       old_bytes('S.SOURCES', plus, expression_plus) + (' = eps' if old_echo is None else ' = (' + payload(old_echo) + ')'),
                       operand('S.SOURCES', plus, expression_plus) + f' = (PINT {integer_term})',
                       condition('S.SOURCES', plus, expression_plus) + ' = (' + payload(str(integer).encode()) + ')']
            if position == 'short':
                result += [f'{expression_left} = NExprTernary {expression_plus} ABSENT expression_{label}_false metadata_{label}_short']
    return result


def co(value):
    return ('??', ('?', TRUE, value, NULL), NULL)


def conversion_checks(rows, prefix):
    result = bindings()
    for number, (shape, child_value, integer, old_echo) in enumerate(rows):
        integer_term = f'({integer})' if integer < 0 else str(integer)
        expression, nodes, occurrences = source_tree(('+', shape), prefix + '_' + str(number))
        child_expression = dict(nodes[0][4])[0]
        state, child = 'S_' + prefix + '_' + str(number), 'porigin_' + prefix + '_' + str(number)
        result += [f'{state} = ' + raw.source_state(occurrences),
                   f'$origin_child((porigin_tree_root_class),[PCFIELD 0]) = ({child})',
                   operand(state + '.SOURCES', child, child_expression) + f' = ({child_value})',
                   f'$coerce_number({child_value}) = COERCED (NINT {integer_term}) false',
                   old_bytes(state + '.SOURCES', 'porigin_tree_root_class', expression) + (' = eps' if old_echo is None else ' = (' + payload(old_echo) + ')'),
                   operand(state + '.SOURCES', 'porigin_tree_root_class', expression) + f' = (PINT {integer_term})',
                   condition(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = (' + payload(str(integer).encode()) + ')']
    return result


def scalar_values():
    primitives = [(NULL, 'PNULL', 0), (FALSE, 'PBOOL false', 0), (TRUE, 'PBOOL true', 1),
                  (('i', 0), 'PINT 0', 0), (('i', 7), 'PINT 7', 7)]
    rows = [(shape, value, integer, str(integer).encode()) for shape, value, integer in primitives]
    rows += [(co(shape), value, integer, None) for shape, value, integer in primitives]
    rows += [(('&&', co(TRUE), co(FALSE)), 'PBOOL false', 0, None),
             (('+', co(string(b'  +1 '))), 'PINT 1', 1, None)]
    return conversion_checks(rows, 'plus_scalar')


def numeric_values():
    values = [(b'0', 0), (b'00', 0), (b'  +0 ', 0), (b'-0', 0), (b'01', 1),
              (b'+12', 12), (b' -7 ', -7), (b'9223372036854775807', 9223372036854775807),
              (b' -9223372036854775808', -9223372036854775808)]
    rows = [(string(value), pstring(value), integer, str(integer).encode()) for value, integer in values]
    rows += [(co(string(value)), pstring(value), integer, None) for value, integer in values[:3]]
    return conversion_checks(rows, 'plus_numeric')


COALESCE_TRUE = ('??', ('?', TRUE, NULL, FALSE), TRUE)
LEGACY = [
    ('one', ('+', ('i', 1)), 'PINT 1', b'1', b'1'),
    ('zero', ('+', ('i', 0)), 'PINT 0', b'0', b'0'),
    ('coalesce-zero', ('??', NULL, ('+', ('i', 0))), 'PINT 0', b'0', b'0'),
    ('and-one', ('&&', ('+', ('i', 1)), COALESCE_TRUE), 'PBOOL true', b'1', None),
    ('or-one', ('or', COALESCE_TRUE, ('+', ('i', 1))), 'PBOOL true', b'1', None),
]


def legacy_values():
    result = bindings()
    for number, (_, shape, value, echo, old_echo) in enumerate(LEGACY):
        expression, _, occurrences = source_tree(shape, 'plus_legacy_' + str(number))
        state = 'S_plus_legacy_' + str(number)
        result += [f'{state} = ' + raw.source_state(occurrences),
                   old_bytes(state + '.SOURCES', 'porigin_tree_root_class', expression) + (' = eps' if old_echo is None else ' = (' + payload(old_echo) + ')'),
                   operand(state + '.SOURCES', 'porigin_tree_root_class', expression) + f' = ({value})',
                   condition(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = (' + payload(echo) + ')']
    # Preserve the six old reached-site argument names with explicit AST/origin bindings.
    for prefix in ('condition', 'ternary_condition', 'not'):
        for side, number, integer in (('method', 4, 1), ('class', 3, 0)):
            label = f'{prefix}_{side}_{number}_cond'
            expression, _, _ = source_tree(('+', ('i', integer)), 'plus_legacy_' + label)
            origin, node = 'porigin_' + label, 'expression_' + label
            state = 'S_plus_legacy_' + ('0' if integer else '1')
            result += [f'{origin} = porigin_tree_root_class', f'{node} = {expression}',
                       operand(state + '.SOURCES', origin, node) + f' = (PINT {integer})']
    return result


def source_authority(skipped):
    shape = ('?', FALSE if skipped else TRUE, ('+', co(NULL)), TRUE)
    expression, nodes, occurrences = source_tree(shape, 'plus_source')
    result = bindings() + ['S_plus_source = ' + raw.source_state(occurrences),
                           operand('S_plus_source.SOURCES', 'porigin_tree_root_class', expression) + (' = (PBOOL true)' if skipped else ' = (PINT 0)')]
    for number, (parts, node, metadata, kind, _) in enumerate(nodes):
        path = 'pcpath_site ++ ' + raw.path((0,) + parts)
        changes = [('missing', f'$rawtree_review_without(S_plus_source.SOURCES[0].OCCURRENCES,{path})')]
        if kind in ('?', '??', '+'):
            changes += [('metadata', f'(PCOCCURRENCE ({path}) ({node.removesuffix(metadata)}eps)) :: S_plus_source.SOURCES[0].OCCURRENCES')]
        for label, source in changes:
            state = f'S_plus_source_{number}_{label}'
            result += [f'{state} = ' + raw.source_state(source),
                       operand(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    return result


def bounds():
    result = bindings()
    bad = [string(b'1.0'), string(b'1e0'), string(b'9223372036854775808'),
           string(b'-9223372036854775809'), string(b' -9223372036854775808 '),
           string(b'1tail'), string(b'garbage'), string(b''), string(b'\0'),
           ('f', '0000000000000000'), ('f', '7ff8000000000000'),
           ('cv', b'missing'), ('-', ('i', 1)), ('i', 9223372036854775808)]
    for number, item in enumerate(bad):
        expression, _, occurrences = source_tree(('+', item), 'plus_bound_' + str(number))
        state = 'S_plus_bound_' + str(number)
        result += [f'{state} = ' + raw.source_state(occurrences),
                   old_bytes(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps',
                   operand(state + '.SOURCES', 'porigin_tree_root_class', expression) + (' = (PINT (-1))' if number == 12 else ' = eps'),
                   condition(state + '.SOURCES', 'porigin_tree_root_class', expression) + (' = (' + payload(b'-1') + ')' if number == 12 else ' = eps')]
    for number, shape in enumerate([('-', ('i', 1)),
                                   ('.', ('+', co(TRUE)), string(b''))]):
        expression, _, occurrences = source_tree(shape, 'plus_parent_' + str(number))
        state = 'S_plus_parent_' + str(number)
        result += [f'{state} = ' + raw.source_state(occurrences),
                   operand(state + '.SOURCES', 'porigin_tree_root_class', expression) + (' = (PINT (-1))' if number == 0 else ' = eps'),
                   condition(state + '.SOURCES', 'porigin_tree_root_class', expression) + (' = (' + payload(b'-1') + ')' if number == 0 else ' = eps')]
    expression, _, occurrences = source_tree(('+', string(b'OWNER')), 'plus_owner')
    placeholder = 'NScalarString (BYTES "T1dORVI=") metadata_class'
    child = 'NExprArray (SEQUENCE eps) metadata_class'
    assert placeholder in expression and placeholder in occurrences
    expression, occurrences = expression.replace(placeholder, child), occurrences.replace(placeholder, child)
    result += ['S_plus_owner = ' + raw.source_state(occurrences),
               operand('S_plus_owner.SOURCES', 'porigin_tree_root_class', expression) + ' = eps',
               condition('S_plus_owner.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    return result


CASES = {}
for index, row in enumerate(ROWS):
    base = dict(prior.CASES[prior.ROWS[index]['id'] + '-actual-sites'], source=row['source'])
    CASES[row['id'] + '-actual-sites'] = dict(base, checks=actual_sites(index))
base = CASES[ROWS[0]['id'] + '-actual-sites']
for suffix, checks in [('scalar-values', scalar_values()), ('numeric-values', numeric_values()),
                       ('legacy-values', legacy_values()),
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
