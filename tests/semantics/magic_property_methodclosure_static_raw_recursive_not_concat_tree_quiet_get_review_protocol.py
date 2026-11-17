#!/usr/bin/env python3
"""Check recursive NOT/CONCAT source links and the quiet scalar echo/truth invariant."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_text_concat_not_tree_quiet_get_review_protocol as prior
import magic_property_methodclosure_static_raw_keyword_concat_tree_quiet_get_review_protocol as renderer

raw = prior.raw
CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_recursive_not_concat_tree_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def certificate(sources, origin, expression):
    return f'$property_magic_cv_raw_recursive_not_concat_tree({sources},{origin},{expression})'


def roots(index):
    return [line.replace('$property_magic_cv_raw_text_concat_not_tree(',
                         '$property_magic_cv_raw_recursive_not_concat_tree(')
            .replace('$property_magic_cv_raw_integer_concat_not_tree(',
                     '$property_magic_cv_raw_text_concat_not_tree(') for line in prior.roots(index)]


def checks(index):
    result = roots(index)
    false, null, empty = ('k', 'false', False), ('k', 'NULL', True), ('s', b'')
    triple = ('!', ('!', ('!', false)))
    samples = ((('class', (0, 1, 1, 1, 0, 0), triple, 'PBOOL false', b'', b'1'),
                ('class', (0, 1, 1, 1, 0, 1), ('!', ('+', false)), 'PINT 0', b'0', b'1'),
                ('method', (1, 1, 1, 1, 1),
                 ('!', ('.', ('!', ('.', null, false)), ('.', ('+', ('i', 12)), empty))),
                 'PSTRING $ptascii("112")', b'112', b'')) if index == 0 else
               (('class', (0, 0, 1, 1), ('!', ('.', ('!', ('.', false, ('k', 'null', False))), ('s', b'0'))),
                 'PSTRING $ptascii("10")', b'10', b''),
                ('method', (1, 1, 1, 1, 1, 1, 1, 0), ('!', ('+', ('s', b'  -000 '))),
                 'PINT 0', b'0', b'1'),
                ('method', (1, 1, 1, 1, 1, 1, 1, 1), triple, 'PBOOL false', b'', b'1')))
    for number, (side, parts, shape, child_value, child_bytes, output) in enumerate(samples):
        expression, nodes, bindings = prior.tree(shape, str(number))
        child, _, _ = prior.tree(shape[1], str(number), (0,))
        origin, child_origin = f'porigin_recursive_{number}', f'porigin_recursive_child_{number}'
        truth = 'false' if child_bytes in (b'', b'0') else 'true'
        result += [f'$origin_child((porigin_site),{raw.path(parts)}) = ({origin})',
                   f'$origin_node(S.SOURCES,{origin}) = ({expression})', *bindings,
                   f'$origin_child(({origin}),[PCFIELD 0]) = ({child_origin})',
                   f'$origin_node(S.SOURCES,{child_origin}) = ({child})',
                   f'$echo_value({child_value}) = $base64("{base64.b64encode(child_bytes).decode()}")',
                   f'$truth_value(S,{child_value},0) = S[.RESULT = KNOWN (PBOOL {truth})]',
                   f'$truth_value(S,PSTRING $echo_value({child_value}),0) = S[.RESULT = KNOWN (PBOOL {truth})]',
                   certificate('S.SOURCES', child_origin, child) + f' = ($echo_value({child_value}))',
                   certificate('S.SOURCES', origin, expression) + f' = ($base64("{base64.b64encode(output).decode()}"))',
                   f'$property_magic_cv_raw_text_concat_not_tree(S.SOURCES,{origin},{expression}) = eps',
                   f'$compiled_read(S_roots,{origin}) = eps']
        for position, (relative, node, metadata) in enumerate(nodes):
            if not node.startswith(('NExprBooleanNot', 'NExprBinaryOpConcat')):
                continue
            path = 'pcpath_site ++ ' + raw.path(parts + relative)
            state = f'S_recursive_source_{number}_{position}'
            forged = node[:-len(metadata)] + 'eps'
            occurrences = f'(PCOCCURRENCE ({path}) ({forged})) :: pcunit.OCCURRENCES'
            result += [f'{metadata} =/= eps', f'{state} = ' + raw.source_state(occurrences),
                       certificate(state + '.SOURCES', origin, expression) + ' = eps']
        state = f'S_recursive_missing_{number}'
        path = 'pcpath_site ++ ' + raw.path(parts)
        result += [f'{state} = ' + raw.source_state(f'$rawtree_review_without(pcunit.OCCURRENCES,{path})'),
                   certificate(state + '.SOURCES', origin, expression) + ' = eps',
                   '~' + raw.selector(side, state)]
    for side in ('class', 'method'):
        state = 'S_recursive_pool_' + side
        other = 'method' if side == 'class' else 'class'
        field = 1 if other == 'method' else 0
        result += [f'{state} = S[.POOLS = [{{UNIT n_unit,CONSTANTS ([PCONSTANT (pcpath_site ++ [PCFIELD {field}]) (PSTRING ptbytes_{other})])}}]]',
                   '~' + raw.selector(side, state), raw.selector(other, state)]
    return result


def controls():
    result = roots(0)
    empty, false = ('s', b''), ('k', 'false', False)
    accepted = [(('!', ('!', ('!', false))), b'1'),
                (('!', ('+', ('s', b' -000 '))), b'1'),
                (('!', ('.', ('!', ('.', false, empty)), ('s', b'0'))), b''),
                (('!', ('!', ('!', ('!', false)))), b'')]
    denied = [('!', ('s', b'\0')), ('!', ('!', ('s', b'\0'))),
              ('!', ('.', ('s', b'x\0'), empty)),
              ('!', ('f', '8000000000000000')), ('!', ('cv', b'part')),
              ('!', ('add', ('i', 0), ('i', 0))), ('!', ('-', ('i', 0))),
              ('!', ('+', ('!', false))), ('!', ('+', ('s', b'1foo')))]
    for number, (shape, output) in enumerate([*accepted, *((shape, None) for shape in denied)]):
        expression, nodes, _ = prior.tree(shape, str(number), concrete=True)
        occurrences = 'eps'
        for parts, node, _ in nodes:
            path = 'pcpath_site ++ ' + raw.path((0,) + parts)
            occurrences = f'(PCOCCURRENCE ({path}) ({node})) :: ({occurrences})'
        state = 'S_recursive_control_' + str(number)
        expected = 'eps' if output is None else '($base64("' + base64.b64encode(output).decode() + '"))'
        result += [f'{state} = ' + raw.source_state(occurrences),
                   certificate(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = ' + expected]
    return result


CASES = {}
for index, row in enumerate(ROWS):
    original = row['derived_from']['id']
    old = prior.CASES[original if original in prior.CASES else original + '-class']
    CASES[row['id']] = dict(old, source=row['source'], checks=checks(index))
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
    parents += [raw, renderer, literal, literal.own, literal.own.prior, literal.own.prior.prior,
                literal.inherited, literal.inherited.prior, literal.inherited.prior.prior,
                literal.inherited.prior.prior.prior, literal.own.prior.prior.owning,
                literal.own.prior.prior.literal]
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, *(entry for parent in parents
                                               for entry in (Path(parent.__file__), parent.CATALOGUE))),
                 runner_flags=('--sl',), fixture_renderer=renderer.render)
