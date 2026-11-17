#!/usr/bin/env python3
"""Check typed primitive nullness and emitted closed coalesce selectors."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_ternary_boolean_not_concat_tree_quiet_get_review_protocol as prior

raw, renderer = prior.raw, prior.renderer
CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_primitive_coalesce_tree_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
BINARY = dict(prior.prior.BINARY, **{'??': 'Coalesce'})


def certificate(sources, origin, expression):
    return f'$property_magic_cv_raw_primitive_coalesce_tree({sources},{origin},{expression})'


def primitive(sources, origin, expression):
    return f'$property_magic_cv_raw_primitive_coalesce_left({sources},{origin},{expression})'


def emitted(state, side):
    return f'$property_magic_cv_emitted_primitive_coalesce_concat_value({state},porigin_tree_root_{side},expression_{side})'


def tree(shape, suffix, parts=(), concrete=False):
    kind = shape[0]
    if kind in ('s', 'i', 'f', 'cv', 'k'):
        return prior.tree(shape, suffix, parts, concrete)
    metadata = 'metadata_class' if concrete else 'metadata_coalesce_' + suffix + '_' + ''.join(map(str, parts))
    fields = ((0, shape[1]), (2, shape[3])) if kind == '?' and shape[2] is None else (
        ((0, shape[1]), (1, shape[2]), (2, shape[3])) if kind == '?' else
        ((0, shape[1]), (1, shape[2])) if kind in BINARY else ((0, shape[1]),))
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
    elif kind in BINARY:
        expression = f'NExprBinaryOp{BINARY[kind]} ({expressions[0]}) ({expressions[1]}) {metadata}'
    else:
        constructor = {'!': 'NExprBooleanNot', '+': 'NExprUnaryPlus', '-': 'NExprUnaryMinus'}[kind]
        expression = f'{constructor} ({expressions[0]}) {metadata}'
    return expression, [(parts, expression, metadata, kind, children), *nodes], bindings


def bindings(index=0):
    return prior.roots(index, whole_owner=False)[:11]


def roots(index, side):
    origin = 'porigin_tree_root_' + side
    expression = 'expression_' + side
    return bindings(index) + [
        certificate('S.SOURCES', origin, expression) + f' = (ptbytes_{side})',
        prior.certificate('S.SOURCES', origin, expression) + ' = eps',
        f'$compiled_read(S,{origin}) = eps',
        f'$pool_value(S.POOLS,{origin}) = eps',
        emitted('S', side) + f' = (PSTRING ptbytes_{side})',
        raw.selector(side),
    ]


def synthetic(typed=False):
    result = bindings()
    null, false, true = ('k', 'null', False), ('k', 'false', False), ('k', 'true', False)
    fqn_null, fqn_false = ('k', 'NULL', True), ('k', 'FALSE', True)
    coalesce = lambda left, right: ('??', left, right)
    if typed:
        cases = [(null, 'PNULL'), (false, 'PBOOL false'), (true, 'PBOOL true'),
                 (fqn_null, 'PNULL'), (fqn_false, 'PBOOL false'),
                 (('i', 0), 'PINT 0'), (('i', 12), 'PINT 12'),
                 (('s', b''), 'PSTRING ' + prior.payload(b'')),
                 (('s', b'0'), 'PSTRING ' + prior.payload(b'0'))]
        cases += [(shape, None) for shape in (('s', b'\0'), ('i', 9223372036854775808),
                  ('f', '0000000000000000'), ('cv', b'nullValue'), ('+', ('i', 0)),
                  coalesce(null, null))]
    else:
        cases = [(coalesce(left, ('s', b'R')), value) for left, value in
                 ((null, b'R'), (false, b''), (true, b'1'), (fqn_null, b'R'),
                  (fqn_false, b''), (('i', 0), b'0'), (('s', b''), b''),
                  (('s', b'0'), b'0'), (('s', b'00'), b'00'), (('s', b'01'), b'01'))]
        cases += [(coalesce(null, null), b''), (coalesce(null, false), b''),
                  (coalesce(null, coalesce(null, ('s', b'00'))), b'00'),
                  (coalesce(false, coalesce(null, ('s', b'BAD'))), b''),
                  (coalesce(null, ('?', ('s', b'00'), null, true)), b''),
                  (('.', ('s', b'P'), coalesce(false, ('s', b'BAD'))), b'P')]
        cases += [(shape, None) for shape in (
            coalesce(('s', b'\0'), ('s', b'R')),
            coalesce(false, ('s', b'\0')), coalesce(false, ('cv', b'skipped')),
            coalesce(null, ('f', '0000000000000000')),
            coalesce(false, ('+', ('s', b'1foo'))),
            coalesce(null, ('-', ('i', 1))), coalesce(null, ('add', ('i', 1), ('i', 1))),
            coalesce(('f', '0000000000000000'), ('s', b'R')),
            coalesce(('cv', b'nullValue'), ('s', b'R')),
            coalesce(('+', ('i', 0)), ('s', b'R')),
            coalesce(coalesce(null, null), ('s', b'R')),
            ('!', coalesce(null, false)), ('or', true, coalesce(null, false)),
            ('?', true, ('s', b'A'), coalesce(null, false)),
            ('.', ('s', b'P'), coalesce(false, ('s', b'\0'))),
        )]
    for number, (shape, value) in enumerate(cases):
        expression, nodes, _ = tree(shape, str(number), concrete=True)
        occurrences = 'eps'
        for parts, node, _, _, _ in nodes:
            occurrences = f'(PCOCCURRENCE (pcpath_site ++ {raw.path((0,) + parts)}) ({node})) :: ({occurrences})'
        state = 'S_coalesce_control_' + str(number)
        expected = 'eps' if value is None else '(' + (value if typed else prior.payload(value)) + ')'
        call = primitive if typed else certificate
        result += [f'{state} = ' + raw.source_state(occurrences),
                   call(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = ' + expected]
    return result


def source_guards():
    result = bindings()
    samples = [((0, 1, 0, 0), ('??', ('k', 'NULL', True),
                ('?', ('s', b'00'), ('s', b'00'), ('k', 'false', False))), 'PNULL', b'00'),
               ((0, 1, 0, 1), ('??', ('k', 'FALSE', True), ('s', b'BAD_FALSE')), 'PBOOL false', b'')]
    for number, (parts, shape, value, joined) in enumerate(samples):
        expression, nodes, data = tree(shape, str(number))
        origin = 'porigin_coalesce_' + str(number)
        result += [f'$origin_child((porigin_site),{raw.path(parts)}) = ({origin})',
                   f'$origin_node(S.SOURCES,{origin}) = ({expression})', *data,
                   certificate('S.SOURCES', origin, expression) + ' = (' + prior.payload(joined) + ')',
                   prior.certificate('S.SOURCES', origin, expression) + ' = eps']
        left = dict(nodes[0][4])[0]
        left_origin = 'porigin_left_' + str(number)
        result += [f'$origin_child(({origin}),[PCFIELD 0]) = ({left_origin})',
                   primitive('S.SOURCES', left_origin, left) + ' = (' + value + ')']
        for field in (0, 1):
            state = f'S_coalesce_missing_{number}_{field}'
            result += [f'{state} = ' + raw.source_state(f'$rawtree_review_without(pcunit.OCCURRENCES,pcpath_site ++ {raw.path(parts + (field,))})'),
                       certificate(state + '.SOURCES', origin, expression) + ' = eps']
        name_origin = 'porigin_left_name_' + str(number)
        text, metadata = 'text_coalesce_name_' + str(number), 'metadata_coalesce_name_' + str(number)
        result += [f'$origin_child(({left_origin}),[PCFIELD 0]) = ({name_origin})',
                   f'$origin_node(S.SOURCES,{name_origin}) = (NNameFullyQualified (BYTES {text}) {metadata})']
        name_path = 'pcpath_site ++ ' + raw.path(parts + (0, 0))
        for label, node in (('missing', None), ('kind', f'NName (BYTES {text}) {metadata}'),
                            ('metadata', f'NNameFullyQualified (BYTES {text}) eps')):
            state = f'S_coalesce_name_{number}_{label}'
            occurrences = (f'$rawtree_review_without(pcunit.OCCURRENCES,{name_path})' if node is None else
                           f'(PCOCCURRENCE ({name_path}) ({node})) :: pcunit.OCCURRENCES')
            result += [f'{state} = ' + raw.source_state(occurrences),
                       primitive(state + '.SOURCES', left_origin, left) + ' = eps',
                       certificate(state + '.SOURCES', origin, expression) + ' = eps']
            if number == 0 and label == 'missing':
                result += ['~' + raw.selector('class', state)]
    return result


def authority(side):
    result = roots(0, side)
    path = '(pcpath_site ++ [PCFIELD ' + ('0' if side == 'class' else '1') + '])'
    result += ['$code_at(S.CODE,n_unit) = (pcode_coalesce)',
               f'$code_expression(pcode_coalesce.EXPRESSIONS,{path}) = ((z_coalesce,false))']
    other_path = '(pcpath_site ++ [PCFIELD ' + ('1' if side == 'class' else '0') + '])'
    result += [f'$code_expression(pcode_coalesce.EXPRESSIONS,{other_path}) = ((z_coalesce_other,false))',
               f'S_coalesce_minimal = S[.CODE = [pcode_coalesce[.EXPRESSIONS = [CODEEXPR {path} z_coalesce false,CODEEXPR {other_path} z_coalesce_other false]]]]',
               emitted('S_coalesce_minimal', side) + f' = (PSTRING ptbytes_{side})',
               raw.selector(side, 'S_coalesce_minimal')]
    codes = [('constant', f'pcode_coalesce[.EXPRESSIONS = (CODEEXPR {path} z_coalesce true) :: pcode_coalesce.EXPRESSIONS]'),
             ('zero_line', f'pcode_coalesce[.EXPRESSIONS = (CODEEXPR {path} 0 false) :: pcode_coalesce.EXPRESSIONS]'),
             ('effect', f'pcode_coalesce[.EXPRESSIONS = (CODEEFFECT {path}) :: pcode_coalesce.EXPRESSIONS]'),
             ('redirect', f'pcode_coalesce[.REDIRECTS = (CODEREDIRECT {path} (pcpath_site ++ [PCFIELD 99]) false) :: pcode_coalesce.REDIRECTS]')]
    for label, code in codes:
        state = 'S_coalesce_code_' + side + '_' + label
        result += [f'{state} = S[.CODE = [{code}]]', emitted(state, side) + ' = eps',
                   '~' + raw.selector(side, state)]
    for label, code in (('missing_unit', 'eps'), ('wrong_unit', '[pcode_coalesce[.UNIT = $(n_unit + 1)]]')):
        state = 'S_coalesce_code_' + side + '_' + label
        result += [f'{state} = S[.CODE = {code}]', emitted(state, side) + ' = eps']
    return result


def pools():
    result = bindings()
    for field, side in enumerate(('class', 'method')):
        result += [certificate('S.SOURCES', 'porigin_tree_root_' + side, 'expression_' + side) + f' = (ptbytes_{side})']
        for kind, value in (('string', f'PSTRING ptbytes_{side}'), ('boolean', 'PBOOL true')):
            state = 'S_coalesce_pool_' + side + '_' + kind
            result += [f'{state} = S[.POOLS = [{{UNIT n_unit,CONSTANTS ([PCONSTANT (pcpath_site ++ [PCFIELD {field}]) ({value})])}}]]',
                       emitted(state, side) + ' = eps', '~' + raw.selector(side, state)]
    return result


CASES = {}
for index, row in enumerate(ROWS):
    original = prior.ROWS[index]['id'] + ('-class-root' if index else '')
    for side in ('class', 'method'):
        CASES[row['id'] + '-root-' + side] = dict(prior.CASES[original], source=row['source'], checks=roots(index, side))
base = dict(CASES[ROWS[0]['id'] + '-root-class'])
for suffix, checks in (('owner', ['$property_magic_cv_static_methodclosure(S,n_closure)']),
                       ('typed-controls', synthetic(True)), ('value-controls', synthetic()),
                       ('source-guards', source_guards()), ('pools', pools()),
                       ('authority-class', authority('class')), ('authority-method', authority('method'))):
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
