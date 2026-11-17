#!/usr/bin/env python3
"""Check exact ternary selection, optional arms and pure skipped-source receipts."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_boolean_not_concat_tree_quiet_get_review_protocol as prior

raw, renderer = prior.raw, prior.renderer
CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_ternary_boolean_not_concat_tree_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def certificate(sources, origin, expression):
    return f'$property_magic_cv_raw_ternary_boolean_not_concat_tree({sources},{origin},{expression})'


def payload(value):
    return '$base64("' + base64.b64encode(value).decode() + '")'


def tree(shape, suffix, parts=(), concrete=False):
    kind = shape[0]
    if kind in ('s', 'i', 'f', 'cv', 'k'):
        expression, nodes, bindings = prior.tree(shape, suffix, parts, concrete)
        return expression, [(p, n, m, k, []) for p, n, m, k, _, _ in nodes], bindings
    metadata = 'metadata_class' if concrete else 'metadata_ternary_' + suffix + '_' + ''.join(map(str, parts))
    fields = ((0, shape[1]), (2, shape[3])) if kind == '?' and shape[2] is None else (
        ((0, shape[1]), (1, shape[2]), (2, shape[3])) if kind == '?' else
        ((0, shape[1]), (1, shape[2])) if kind in prior.BINARY else ((0, shape[1]),))
    nodes, bindings, children = [], [], []
    for field, child in fields:
        expression, child_nodes, child_bindings = tree(child, suffix, parts + (field,), concrete)
        children.append((field, expression))
        nodes += child_nodes
        bindings += child_bindings
    expressions = dict(children)
    if kind == '?':
        arm = 'ABSENT' if shape[2] is None else '(' + expressions[1] + ')'
        expression = f'NExprTernary ({expressions[0]}) {arm} ({expressions[2]}) {metadata}'
    elif kind in prior.BINARY:
        expression = f'NExprBinaryOp{prior.BINARY[kind]} ({expressions[0]}) ({expressions[1]}) {metadata}'
    else:
        constructor = {'!': 'NExprBooleanNot', '+': 'NExprUnaryPlus', '-': 'NExprUnaryMinus'}[kind]
        expression = f'{constructor} ({expressions[0]}) {metadata}'
    return expression, [(parts, expression, metadata, kind, children), *nodes], bindings


def emitted(state, side):
    return f'$property_magic_cv_emitted_ternary_concat_value({state},porigin_tree_root_{side},expression_{side})'


def roots(index, whole_owner=True):
    shared = [line.replace('$property_magic_cv_raw_boolean_not_concat_tree(',
                           '$property_magic_cv_raw_ternary_boolean_not_concat_tree(')
                  .replace('$property_magic_cv_raw_recursive_not_concat_tree(',
                           '$property_magic_cv_raw_boolean_not_concat_tree(') for line in prior.roots(index)]
    result = [shared[i] for i in (0, 1, 2, 3, 4, 5, 6, 7, 8, 13)]
    result += ['S_roots = S[.POOLS = eps]']
    for side, receipt, old, selector in (('class', 9, 10, 12), ('method', 14, 15, 17)):
        result += [shared[receipt], shared[old],
                   f'$compiled_read(S,porigin_tree_root_{side}) = eps',
                   emitted('S', side) + f' = (PSTRING ptbytes_{side})', shared[selector]]
    if index == 0 and whole_owner:
        result += [shared[21]]
    return result


def checks(index, section='all'):
    result = roots(index)
    shared, groups = list(result), []
    false, true, null = ('k', 'false', False), ('k', 'true', False), ('k', 'null', False)
    samples = ((('class', (0, 1, 1, 1, 0, 0), ('?', ('s', b'00'), ('+', ('s', b'001')), null), {(): b'1'}),
                ('class', (0, 1, 1, 1, 0, 1), ('?', ('s', b'00'), None, false), {(): b'00'}),
                ('method', (1, 1, 1, 1, 1), ('?', ('s', b'0'), ('s', b'1'), null), {(): b''})) if index == 0 else
               (('class', (0, 0, 1, 1), ('?', ('s', b'00'), null, true), {(): b''}),
                ('method', (1, 1, 1, 1, 1, 1, 1, 0), ('?', ('s', b'01'), None, false), {(): b'01'}),
                ('method', (1, 1, 1, 1, 1, 1, 1, 1), ('?', ('s', b'0'), None, ('?', ('s', b'00'), ('k', 'TRUE', True), false)),
                 {(): b'1', (2,): b'1'})))
    for number, (side, parts, shape, values) in enumerate(samples):
        start = len(result)
        expression, nodes, bindings = tree(shape, str(number))
        origin = 'porigin_ternary_' + str(number)
        result += [f'$origin_child((porigin_site),{raw.path(parts)}) = ({origin})',
                   f'$origin_node(S.SOURCES,{origin}) = ({expression})', *bindings]
        for position, (relative, node, metadata, kind, children) in enumerate(nodes):
            if kind != '?':
                continue
            node_origin = f'porigin_ternary_{number}_{position}'
            result += [f'$origin_child(({origin}),{raw.path(relative)}) = ({node_origin})',
                       f'$origin_node(S.SOURCES,{node_origin}) = ({node})',
                       certificate('S.SOURCES', node_origin, node) + ' = (' + payload(values[relative]) + ')',
                       prior.certificate('S.SOURCES', node_origin, node) + ' = eps']
            for field, child in children:
                child_origin = f'{node_origin}_arm_{field}'
                state = f'S_ternary_missing_{number}_{position}_{field}'
                path = 'pcpath_site ++ ' + raw.path(parts + relative + (field,))
                result += [f'$origin_child(({node_origin}),[PCFIELD {field}]) = ({child_origin})',
                           f'$compiled_read(S_roots,{child_origin}) = eps',
                           f'{state} = ' + raw.source_state(f'$rawtree_review_without(pcunit.OCCURRENCES,{path})'),
                           certificate(state + '.SOURCES', node_origin, node) + ' = eps',
                           '~' + raw.selector(side, state)]
            if 1 not in dict(children):
                absent_origin = node_origin + '_absent_if'
                result += [f'$origin_child(({node_origin}),[PCFIELD 1]) = ({absent_origin})',
                           f'$origin_node(S.SOURCES,{absent_origin}) = eps']
        groups.append(result[start:])
    guards = len(result)
    for field, side in enumerate(('class', 'method')):
        for kind, value in (('string', f'PSTRING ptbytes_{side}'), ('boolean', 'PBOOL true')):
            state = f'S_ternary_pool_{side}_{kind}'
            result += [f'{state} = S[.POOLS = [{{UNIT n_unit,CONSTANTS ([PCONSTANT (pcpath_site ++ [PCFIELD {field}]) ({value})])}}]]',
                       emitted(state, side) + ' = eps', '~' + raw.selector(side, state)]
    if section != 'all':
        bindings = shared[:11]
        if section == 'class-root':
            return bindings + shared[11:16]
        if section == 'method-root':
            return bindings + shared[16:21]
        if section == 'pools':
            return bindings + [shared[11], shared[16]] + result[guards:]
        if section == 'method-2-outer':
            return bindings + groups[2][:20]
        if section.startswith('method-2-inner-'):
            arm = int(section.rsplit('-', 1)[1])
            # Four sample bindings precede sixteen outer and nineteen inner facts.
            inner = groups[2][20:]
            return bindings + groups[2][:4] + inner[:4] + inner[4 + 5 * arm:9 + 5 * arm]
        selected = {'class': 0, 'method-1': 1}[section]
        return bindings + groups[selected]
    return result


def controls():
    result = roots(0)
    false, true, null = ('k', 'false', False), ('k', 'true', False), ('k', 'null', False)
    zero, zeros, one = ('s', b'0'), ('s', b'00'), ('s', b'01')
    full = ('?', zero, null, zeros)
    short = ('?', one, None, false)
    cases = [
        (full, b'00'), (('?', zeros, null, true), b''),
        (('?', zeros, None, false), b'00'), (('?', zero, None, ('i', 12)), b'12'),
        (('?', false, None, ('+', ('s', b'001'))), b'1'),
        (('!', ('?', zeros, null, true)), b'1'),
        (('xor', ('?', zeros, null, true), ('?', zero, None, ('i', 12))), b'1'),
        (('.', full, short), b'0001'), (('?', full, ('s', b'A'), ('s', b'B')), b'A'),
        (('&&', full, short), b'1'),
        (('and', full, ('?', zeros, null, true)), b''),
        (('||', ('?', zeros, null, true), short), b'1'),
        (('or', full, ('?', zero, None, ('i', 0))), b'1'),
    ]
    cases += [(shape, None) for shape in (
        ('?', true, ('s', b'good'), ('cv', b'skipped')),
        ('?', false, ('cv', b'skipped'), ('s', b'good')),
        ('?', zeros, None, ('cv', b'skipped')),
        ('?', ('s', b'\0'), false, true),
        ('?', false, ('s', b'\0'), true), ('?', true, false, ('s', b'\0')),
        ('?', true, false, ('f', '8000000000000000')),
        ('?', true, false, ('+', ('s', b'1foo'))),
        ('?', true, false, ('-', ('i', 1))),
        ('?', true, false, ('add', ('i', 1), ('i', 1))),
        ('!', ('?', true, false, ('cv', b'skipped'))),
        ('or', true, ('?', true, false, ('cv', b'skipped'))),
    )]
    for number, (shape, value) in enumerate(cases):
        expression, nodes, _ = tree(shape, str(number), concrete=True)
        occurrences = 'eps'
        for parts, node, _, _, _ in nodes:
            occurrences = f'(PCOCCURRENCE (pcpath_site ++ {raw.path((0,) + parts)}) ({node})) :: ({occurrences})'
        state = 'S_ternary_control_' + str(number)
        expected = 'eps' if value is None else '(' + payload(value) + ')'
        result += [f'{state} = ' + raw.source_state(occurrences),
                   certificate(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = ' + expected]
    return result


def authority(side):
    result = roots(0, whole_owner=False)
    paths = {name: f'(pcpath_site ++ [PCFIELD {field}])'
             for field, name in enumerate(('class', 'method'))}
    record = lambda name, line=None, flag='false': f'CODEEXPR {paths[name]} {line or "z_ternary_" + name} {flag}'
    records = {name: record(name) for name in paths}
    result += ['$code_at(S.CODE,n_unit) = (pcode_ternary)',
               f'$code_expression(pcode_ternary.EXPRESSIONS,{paths["class"]}) = ((z_ternary_class,false))',
               f'$code_expression(pcode_ternary.EXPRESSIONS,{paths["method"]}) = ((z_ternary_method,false))']
    both = '[' + ','.join(records.values()) + ']'
    state = 'S_ternary_root_code'
    result += [f'{state} = S[.CODE = [pcode_ternary[.EXPRESSIONS = {both}]]]']
    for name in paths:
        result += [emitted(state, name) + f' = (PSTRING ptbytes_{name})', raw.selector(name, state)]
    other = 'method' if side == 'class' else 'class'
    expression_sets = {
        'missing': '[' + records[other] + ']',
        'constant-flag': '[' + record(side, flag='true') + ',' + records[other] + ']',
        'zero-line': '[' + record(side, line='0') + ',' + records[other] + ']',
        'effect': both[:-1] + f',CODEEFFECT {paths[side]}]',
    }
    for label, expressions in expression_sets.items():
        bad = 'S_ternary_authority_' + side + '_' + label.replace('-', '_')
        result += [f'{bad} = S[.CODE = [pcode_ternary[.EXPRESSIONS = {expressions}]]]',
                   emitted(bad, side) + ' = eps']
        if label == 'constant-flag':
            result += ['~' + raw.selector(side, bad)]
    bad = 'S_ternary_authority_' + side + '_dangling_redirect'
    redirect = f'CODEREDIRECT {paths[side]} ({paths[side]} ++ [PCFIELD 99]) false'
    result += [f'{bad} = S[.CODE = [pcode_ternary[.EXPRESSIONS = {both}][.REDIRECTS = [{redirect}]]]]',
               emitted(bad, side) + ' = eps']
    for label, code in (('missing_unit', 'eps'),
                        ('wrong_unit', f'[pcode_ternary[.UNIT = $(n_unit + 1)][.EXPRESSIONS = {both}]]')):
        bad = 'S_ternary_authority_' + side + '_' + label
        result += [f'{bad} = S[.CODE = {code}]', emitted(bad, side) + ' = eps']
    return result


CASES = {}
for index, row in enumerate(ROWS):
    original = row['derived_from']['id'] + ('-sites' if index else '')
    for section, suffix in ((('all', ''),) if index == 0 else
                            tuple((section, '-' + section) for section in
                                  ('class-root', 'method-root', 'class', 'method-1', 'method-2-outer',
                                   'method-2-inner-0', 'method-2-inner-1', 'method-2-inner-2', 'pools'))):
        CASES[row['id'] + suffix] = dict(prior.CASES[original], source=row['source'], checks=checks(index, section))
CASES[ROWS[0]['id'] + '-controls'] = dict(CASES[ROWS[0]['id']], checks=controls())
for side in ('class', 'method'):
    CASES[ROWS[0]['id'] + '-authority-' + side] = dict(CASES[ROWS[0]['id']], checks=authority(side))


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
