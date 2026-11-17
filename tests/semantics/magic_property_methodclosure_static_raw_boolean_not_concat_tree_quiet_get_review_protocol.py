#!/usr/bin/env python3
"""Check five quiet Boolean operators, both source operands and recursive truth."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_recursive_not_concat_tree_quiet_get_review_protocol as prior
import magic_property_methodclosure_static_raw_keyword_concat_tree_quiet_get_review_protocol as renderer

raw = prior.raw
CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_boolean_not_concat_tree_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

BINARY = {'.': 'Concat', '&&': 'BooleanAnd', 'and': 'LogicalAnd',
          '||': 'BooleanOr', 'or': 'LogicalOr', 'xor': 'LogicalXor', 'add': 'Plus'}
BOOLEAN = ('&&', 'and', '||', 'or', 'xor')


def certificate(sources, origin, expression):
    return f'$property_magic_cv_raw_boolean_not_concat_tree({sources},{origin},{expression})'


def tree(shape, suffix, parts=(), concrete=False):
    kind = shape[0]
    if kind in ('s', 'i', 'f', 'cv', 'k'):
        expression, nodes, bindings = prior.prior.tree(shape, suffix, parts, concrete)
        return expression, [(p, n, m, kind if p == parts else 'name', None, None)
                            for p, n, m in nodes], bindings
    metadata = 'metadata_class' if concrete else 'metadata_boolean_' + suffix + '_' + ''.join(map(str, parts))
    left, nodes, bindings = tree(shape[1], suffix, parts + (0,), concrete)
    right = None
    if kind in BINARY:
        right, other_nodes, other_bindings = tree(shape[2], suffix, parts + (1,), concrete)
        nodes += other_nodes
        bindings += other_bindings
        expression = f'NExprBinaryOp{BINARY[kind]} ({left}) ({right}) {metadata}'
    else:
        constructor = {'!': 'NExprBooleanNot', '+': 'NExprUnaryPlus', '-': 'NExprUnaryMinus'}[kind]
        expression = f'{constructor} ({left}) {metadata}'
    return expression, [(parts, expression, metadata, kind, left, right), *nodes], bindings


def roots(index):
    return [line.replace('$property_magic_cv_raw_recursive_not_concat_tree(',
                         '$property_magic_cv_raw_boolean_not_concat_tree(')
            .replace('$property_magic_cv_raw_text_concat_not_tree(',
                     '$property_magic_cv_raw_recursive_not_concat_tree(') for line in prior.roots(index)]


def checks(index, section='all'):
    result = roots(index)
    shared, groups = list(result), []
    false, true, fqn_true, null = ('k', 'false', False), ('k', 'true', False), ('k', 'TRUE', True), ('k', 'null', False)
    zero, zeros = ('s', b'0'), ('s', b'00')
    samples = ((('class', (0, 1, 1, 1, 0, 0), ('xor', ('and', zero, ('+', ('i', 0))), fqn_true),
                 {(): True, (0,): False}),
                ('class', (0, 1, 1, 1, 0, 1), ('!', ('||', ('&&', zeros, false), null)),
                 {(): True, (0,): False, (0, 0): False}),
                ('method', (1, 1, 1, 1, 1), ('and', ('or', fqn_true, ('+', ('s', b'000'))), false),
                 {(): False, (0,): True})) if index == 0 else
               (('class', (0, 0, 1, 1), ('||', ('and', false, ('xor', zeros, true)), ('&&', zero, fqn_true)),
                 {(): False, (0,): False, (0, 1): False, (1,): False}),
                ('method', (1, 1, 1, 1, 1, 1, 1, 0), ('xor', ('||', false, zeros), false),
                 {(): True, (0,): True}),
                ('method', (1, 1, 1, 1, 1, 1, 1, 1), ('and', fqn_true, ('xor', zero, true)),
                 {(): True, (1,): True})))
    for number, (side, parts, shape, values) in enumerate(samples):
        start = len(result)
        expression, nodes, bindings = tree(shape, str(number))
        origin = 'porigin_boolean_' + str(number)
        expected = str(values[()]).lower()
        result += [f'$origin_child((porigin_site),{raw.path(parts)}) = ({origin})',
                   f'$origin_node(S.SOURCES,{origin}) = ({expression})', *bindings,
                   certificate('S.SOURCES', origin, expression) + f' = ($echo_value(PBOOL {expected}))',
                   f'$property_magic_cv_raw_recursive_not_concat_tree(S.SOURCES,{origin},{expression}) = eps',
                   f'$compiled_read(S_roots,{origin}) = eps']
        for position, (relative, node, metadata, kind, left, right) in enumerate(nodes):
            if relative not in values:
                continue
            node_origin = f'porigin_boolean_{number}_{position}'
            value = str(values[relative]).lower()
            result += [f'$origin_child(({origin}),{raw.path(relative)}) = ({node_origin})',
                       f'$origin_node(S.SOURCES,{node_origin}) = ({node})',
                       certificate('S.SOURCES', node_origin, node) + f' = ($echo_value(PBOOL {value}))']
            if index == 0 and kind in BOOLEAN:
                shape_check = (f'PFBINARY LOGICALXOR ({left}) ({right})' if kind == 'xor' else
                               f'PFSHORT {"false" if kind in ("&&", "and") else "true"} ({left}) ({right})')
                result += [f'$pfshape({node}) = {shape_check}']
                for field in (0, 1):
                    child_origin = f'porigin_boolean_{number}_{position}_operand_{field}'
                    path = 'pcpath_site ++ ' + raw.path(parts + relative + (field,))
                    state = f'S_boolean_operand_{number}_{position}_{field}'
                    result += [f'$origin_child(({node_origin}),[PCFIELD {field}]) = ({child_origin})',
                               f'$compiled_read(S_roots,{child_origin}) = eps',
                               f'{state} = ' + raw.source_state(f'$rawtree_review_without(pcunit.OCCURRENCES,{path})'),
                               certificate(state + '.SOURCES', node_origin, node) + ' = eps']
        state = f'S_boolean_root_missing_{number}'
        path = 'pcpath_site ++ ' + raw.path(parts)
        result += [f'{state} = ' + raw.source_state(f'$rawtree_review_without(pcunit.OCCURRENCES,{path})'),
                   certificate(state + '.SOURCES', origin, expression) + ' = eps',
                   '~' + raw.selector(side, state)]
        groups.append(result[start:])
    guards = len(result)
    for side in ('class', 'method'):
        state = 'S_boolean_pool_' + side
        other = 'method' if side == 'class' else 'class'
        field = 1 if other == 'method' else 0
        result += [f'{state} = S[.POOLS = [{{UNIT n_unit,CONSTANTS ([PCONSTANT (pcpath_site ++ [PCFIELD {field}]) (PSTRING ptbytes_{other})])}}]]',
                   '~' + raw.selector(side, state), raw.selector(other, state)]
    if section != 'all':
        bindings = [shared[i] for i in (0, 1, 2, 3, 4, 5, 6, 7, 8, 11, 13, 16, 20)]
        if section == 'sites':
            return bindings + [shared[i] for i in (9, 10, 12, 14, 15, 17)]
        if section in ('owner', 'empty-kind', 'root-owner'):
            return bindings + [shared[{'owner': 18, 'empty-kind': 19, 'root-owner': 21}[section]]]
        selected = {'class': 0, 'method-1': 1, 'method-2': 2}[section]
        return bindings + groups[selected] + (result[guards:] if section == 'class' else [])
    return result


def controls():
    result = roots(0)
    false, true = ('k', 'false', False), ('k', 'true', False)
    operands = [(('s', b'0'), false), (('s', b'0'), true),
                (('s', b'00'), ('i', 0)), (('s', b'00'), ('i', 12))]
    truth = {'&&': (False, False, False, True), 'and': (False, False, False, True),
             '||': (False, True, True, True), 'or': (False, True, True, True),
             'xor': (False, True, True, False)}
    cases = [((kind, left, right), value) for kind in BOOLEAN
             for (left, right), value in zip(operands, truth[kind], strict=True)]
    cases += [(shape, None) for shape in (
        ('&&', false, ('cv', b'part')), ('or', true, ('cv', b'part')),
        ('and', false, ('s', b'\0')), ('||', true, ('s', b'\0')),
        ('&&', ('s', b'\0'), false), ('or', ('s', b'\0'), true),
        ('xor', false, ('f', '8000000000000000')),
        ('and', false, ('+', ('s', b'1foo'))),
        ('!', ('&&', false, ('cv', b'part'))))]
    for number, (shape, value) in enumerate(cases):
        expression, nodes, _ = tree(shape, str(number), concrete=True)
        occurrences = 'eps'
        for parts, node, _, _, _, _ in nodes:
            path = 'pcpath_site ++ ' + raw.path((0,) + parts)
            occurrences = f'(PCOCCURRENCE ({path}) ({node})) :: ({occurrences})'
        state = 'S_boolean_control_' + str(number)
        expected = 'eps' if value is None else '($echo_value(PBOOL ' + str(value).lower() + '))'
        result += [f'{state} = ' + raw.source_state(occurrences),
                   certificate(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = ' + expected]
    return result


CASES = {}
for index, row in enumerate(ROWS):
    for section, suffix in ((('all', ''),) if index == 0 else
                            tuple((section, '-' + section) for section in
                                  ('sites', 'owner', 'empty-kind', 'root-owner', 'class', 'method-1', 'method-2'))):
        CASES[row['id'] + suffix] = dict(prior.CASES[row['derived_from']['id']],
                                      source=row['source'], checks=checks(index, section))
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
