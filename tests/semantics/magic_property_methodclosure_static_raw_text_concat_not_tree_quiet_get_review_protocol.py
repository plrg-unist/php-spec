#!/usr/bin/env python3
"""Check certified text CONCAT truth, exact source wrappers and bounded fallback."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_integer_concat_not_tree_quiet_get_review_protocol as prior

raw = prior.raw
CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_text_concat_not_tree_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def certificate(sources, origin, expression):
    return f'$property_magic_cv_raw_text_concat_not_tree({sources},{origin},{expression})'


def tree(shape, suffix, parts=(), concrete=False):
    key = suffix + '_' + ''.join(map(str, parts))
    metadata = 'metadata_class' if concrete else 'metadata_text_' + key
    kind = shape[0]
    nodes, bindings = [], []
    if kind in ('s', 'i', 'f', 'cv'):
        constructor, domain = {'s': ('NScalarString', 'BYTES'), 'i': ('NScalarInt', 'INTEGER'),
                               'f': ('NScalarFloat', 'FLOAT'), 'cv': ('NExprVariable', 'BYTES')}[kind]
        value = str(shape[1]) if kind == 'i' else '"' + (base64.b64encode(shape[1]).decode()
                                                               if kind in ('s', 'cv') else shape[1]) + '"'
        payload = value if concrete else ('i_text_' if kind == 'i' else 'text_text_') + key
        expression = f'{constructor} ({domain} {payload}) {metadata}'
        if not concrete:
            bindings += [f'{payload} = {value}']
    elif kind == 'k':
        constructor = 'NNameFullyQualified' if shape[2] else 'NName'
        payload = '"' + base64.b64encode(shape[1].encode()).decode() + '"'
        name_metadata = 'metadata_class' if concrete else 'metadata_name_' + key
        name = f'{constructor} (BYTES {payload}) {name_metadata}'
        expression = f'NExprConstFetch ({name}) {metadata}'
        nodes.append((parts + (0,), name, name_metadata))
    else:
        left, nodes, bindings = tree(shape[1], suffix, parts + (0,), concrete)
        if kind in ('.', 'add'):
            right, other_nodes, other_bindings = tree(shape[2], suffix, parts + (1,), concrete)
            nodes += other_nodes
            bindings += other_bindings
            constructor = 'NExprBinaryOpConcat' if kind == '.' else 'NExprBinaryOpPlus'
            expression = f'{constructor} ({left}) ({right}) {metadata}'
        else:
            constructor = {'+': 'NExprUnaryPlus', '-': 'NExprUnaryMinus', '!': 'NExprBooleanNot'}[kind]
            expression = f'{constructor} ({left}) {metadata}'
    return expression, [(parts, expression, metadata), *nodes], bindings


def roots(index):
    inherited = prior.prior.prior.checks(index)
    inherited = inherited[:inherited.index('$property_magic_cv_static_methodclosure(S_roots,n_closure)') + 1]
    return [line.replace('$property_magic_cv_raw_double_not_tree(',
                         '$property_magic_cv_raw_text_concat_not_tree(')
            .replace('$property_magic_cv_raw_keyword_string_tree(',
                     '$property_magic_cv_raw_integer_concat_not_tree(') for line in inherited]


def checks(index, section='all'):
    result = roots(index)
    shared, groups = list(result), []
    false, null = ('k', 'false', False), ('k', 'NULL', True)
    samples = ((('class', (0, 1, 1, 1, 0, 0), ('.', null, false), b''),
                ('class', (0, 1, 1, 1, 0, 1), ('.', ('.', false, ('+', ('i', 0))), ('s', b'')), b'0'),
                ('method', (1, 1, 1, 1, 1),
                 ('.', ('.', ('!', ('s', b'0')), ('+', ('s', b'001'))),
                  ('!', ('!', ('k', 'TRUE', True)))), b'111')) if index == 0 else
               (('class', (0, 0, 1, 1), ('.', false, ('s', b'00')), b'00'),
                ('method', (1, 1, 1, 1, 1, 1, 1, 0), ('.', ('+', ('i', 0)), ('s', b'')), b'0'),
                ('method', (1, 1, 1, 1, 1, 1, 1, 1),
                 ('.', ('.', ('!', ('k', 'TRUE', True)), ('+', ('s', b'0'))), ('s', b'')), b'0')))
    for number, (side, parts, shape, joined) in enumerate(samples):
        start = len(result)
        child, nodes, bindings = tree(shape, str(number), (0,))
        metadata = 'metadata_not_' + str(number)
        expression = f'NExprBooleanNot ({child}) {metadata}'
        origin = 'porigin_not_' + str(number)
        child_origin = 'porigin_child_' + str(number)
        truth = 'false' if joined in (b'', b'0') else 'true'
        output = '1' if truth == 'false' else ''
        result += [f'$origin_child((porigin_site),{raw.path(parts)}) = ({origin})',
                   f'$origin_node(S.SOURCES,{origin}) = ({expression})', f'{metadata} =/= eps',
                   f'$origin_child(({origin}),[PCFIELD 0]) = ({child_origin})', *bindings,
                   f'$property_magic_cv_raw_double_not_tree(S.SOURCES,{child_origin},{child}) = ($base64("{base64.b64encode(joined).decode()}"))',
                   f'$truth_value(S,PSTRING $base64("{base64.b64encode(joined).decode()}"),0) = S[.RESULT = KNOWN (PBOOL {truth})]',
                   certificate('S.SOURCES', origin, expression) + f' = ($ptascii("{output}"))',
                   certificate('eps', origin, expression) + ' = eps',
                   f'$property_magic_cv_raw_integer_concat_not_tree(S.SOURCES,{origin},{expression}) = eps',
                   f'$compiled_read(S_roots,{origin}) = eps',
                   '~' + raw.selector('class', expression=expression),
                   '~' + raw.selector('method', expression=expression)]
        for position, (relative, node, node_metadata) in enumerate(nodes):
            node_origin = f'porigin_text_{number}_{position}'
            result += [f'$origin_child(({origin}),{raw.path(relative)}) = ({node_origin})',
                       f'$origin_node(S.SOURCES,{node_origin}) = ({node})',
                       f'{node_metadata} =/= eps', f'$compiled_read(S_roots,{node_origin}) = eps']
        selected = [((), expression, metadata), *nodes[:2]]
        for position, (relative, node, node_metadata) in enumerate(selected):
            for label, replacement in (('missing', None), ('metadata', node[:-len(node_metadata)] + 'eps'),
                                       ('kind', f'NScalarInt (INTEGER 0) {node_metadata}')):
                state = f'S_text_{number}_{position}_{label}'
                path = 'pcpath_site ++ ' + raw.path(parts + relative)
                occurrences = (f'$rawtree_review_without(pcunit.OCCURRENCES,{path})' if replacement is None else
                               f'(PCOCCURRENCE ({path}) ({replacement})) :: pcunit.OCCURRENCES')
                result += [f'{state} = ' + raw.source_state(occurrences),
                           certificate(state + '.SOURCES', origin, expression) + ' = eps',
                           '~' + raw.selector(side, state)]
        groups.append(result[start:])
    guards = len(result)
    for side in ('class', 'method'):
        for label, value in (('missing', None), ('type', 'PBOOL false'),
                             ('case', 'PSTRING $ptlc(ptbytes_' + side + ')')):
            state = 'S_text_root_' + side + '_' + label
            constants = []
            for field, selected in enumerate(('class', 'method')):
                selected_value = value if side == selected else 'PSTRING ptbytes_' + selected
                if selected_value is not None:
                    constants.append(f'PCONSTANT (pcpath_site ++ [PCFIELD {field}]) ({selected_value})')
            result += [f'{state} = S[.POOLS = [{{UNIT n_unit,CONSTANTS ([' + ','.join(constants) + '])}]]',
                       '~' + raw.selector(side, state),
                       raw.selector('method' if side == 'class' else 'class', state)]
    if section != 'all':
        selected = {'class': 0, 'method-1': 1, 'method-2': 2}[section]
        return shared + groups[selected] + (result[guards:] if section == 'class' else [])
    return result


def controls():
    result = roots(0)
    false, empty, zero = ('k', 'false', False), ('s', b''), ('i', 0)
    accepted = [(false, ('k', 'NULL', True), b''), (false, ('s', b'0'), b'0'),
                (('s', b'x'), empty, b'x'),
                (('+', zero), ('s', b'0'), b'00'),
                (('+', ('s', b'  +00012 ')), empty, b'12'),
                (('!', ('!', ('k', 'TRUE', True))), false, b'1')]
    denied = [('f', '0000000000000000'), ('cv', b'part'), ('-', zero), ('add', zero, zero),
              ('+', ('s', b'1foo')), ('+', ('s', b'1.5')),
              ('+', ('s', b'9223372036854775808')), ('+', ('f', '0000000000000000')),
              ('+', ('!', false)), ('!', ('!', ('!', false))),
              ('!', ('.', false, empty)), ('!', ('f', '0000000000000000')),
              ('s', b'\0'), ('k', 'Unknown', False), ('k', 'space\\false', True),
              ('+', ('i', 9223372036854775808))]
    for number, (left, right, joined) in enumerate([*accepted, *((leaf, empty, None) for leaf in denied)]):
        shape = ('!', ('.', left, right))
        expression, nodes, _ = tree(shape, str(number), concrete=True)
        state = 'S_text_control_' + str(number)
        occurrences = 'pcunit.OCCURRENCES'
        for parts, node, _ in nodes:
            path = 'pcpath_site ++ ' + raw.path((0,) + parts)
            occurrences = f'(PCOCCURRENCE ({path}) ({node})) :: ({occurrences})'
        expected = 'eps' if joined is None else '($ptascii("' + ('1' if joined in (b'', b'0') else '') + '"))'
        result += [f'{state} = ' + raw.source_state(occurrences),
                   certificate(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = ' + expected]
    return result


CASES = {}
for index, row in enumerate(ROWS):
    original = row['derived_from']['id']
    old = prior.CASES[original if original in prior.CASES else original + '-class-origins']
    for section, suffix in ((('all', ''),) if index == 0 else
                            (('class', '-class'), ('method-1', '-method-1'), ('method-2', '-method-2'))):
        CASES[row['id'] + suffix] = dict(old, source=row['source'], checks=checks(index, section))
CASES[ROWS[0]['id'] + '-controls'] = dict(CASES[ROWS[0]['id']], checks=controls())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    parents = []
    parent = prior
    while hasattr(parent, 'prior'):
        parents.append(parent)
        parent = parent.prior
    parents.append(parent)
    literal = raw.literal
    parents += [raw, literal, literal.own, literal.own.prior, literal.own.prior.prior,
                literal.inherited, literal.inherited.prior, literal.inherited.prior.prior,
                literal.inherited.prior.prior.prior, literal.own.prior.prior.owning,
                literal.own.prior.prior.literal]
    renderer = prior.prior.prior.prior.prior.prior.prior.prior.prior.prior.prior
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, *(entry for parent in parents
                                               for entry in (Path(parent.__file__), parent.CATALOGUE))),
                 runner_flags=('--sl',), fixture_renderer=renderer.render)
