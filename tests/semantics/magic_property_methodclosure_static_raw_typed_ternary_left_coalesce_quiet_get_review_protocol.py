#!/usr/bin/env python3
"""Check typed ternary nullness, exact source and emitted coalesce selectors."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_ternary_boolean_not_concat_left_coalesce_tree_quiet_get_review_protocol as prior

raw, renderer, payload = prior.raw, prior.renderer, prior.payload
tree, source_tree, bindings = prior.tree, prior.source_tree, prior.bindings
CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_typed_ternary_left_coalesce_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_bytes())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
NULL, FALSE, TRUE = prior.NULL, prior.FALSE, prior.TRUE


def string(value):
    return ('s', value)


def pstring(value):
    return 'PSTRING ' + payload(value)


def typed(sources, origin, expression):
    return f'$property_magic_cv_raw_typed_ternary_left_value({sources},{origin},{expression})'


def certificate(sources, origin, expression):
    return f'$property_magic_cv_raw_typed_ternary_left_coalesce_tree({sources},{origin},{expression})'


def witness(expression):
    return f'$property_magic_cv_ternary_left_coalesce({expression})'


def emitted(state, side):
    return f'$property_magic_cv_emitted_typed_ternary_left_coalesce_concat_value({state},porigin_tree_root_{side},expression_{side})'


def root(side):
    origin, expression = 'porigin_tree_root_' + side, 'expression_' + side
    return [witness(expression), certificate('S.SOURCES', origin, expression) + f' = (ptbytes_{side})',
            f'$compiled_read(S,{origin}) = eps', f'$pool_value(S.POOLS,{origin}) = eps',
            emitted('S', side) + f' = (PSTRING ptbytes_{side})', raw.selector(side)]


def roots(index):
    return bindings(index) + root('class') + root('method') + [
        '$property_magic_cv_static_methodclosure(S,n_closure)', '$property_empty_rv_kind(S,S.OBJECTS[n_closure])']


SCALARS = [(NULL, 'PNULL', b''), (FALSE, 'PBOOL false', b''), (TRUE, 'PBOOL true', b'1'),
           (('i', 0), 'PINT 0', b'0'), (('i', 10), 'PINT 10', b'10'),
           (string(b''), pstring(b''), b''), (string(b'0'), pstring(b'0'), b'0'),
           (string(b'10'), pstring(b'10'), b'10')]


def typed_values():
    cases = []
    for shape, value, _ in SCALARS:
        cases += [(('?', string(b'00'), shape, TRUE), value),
                  (('?', string(b'0'), TRUE, shape), value)]
    cases += [(('?', shape, None, NULL), value) for shape, value, _ in SCALARS if value in ('PBOOL true', 'PINT 10', pstring(b'10'))]
    cases += [(('?', shape, None, fallback), value) for shape, (fallback, value, _) in
              zip((NULL, FALSE, ('i', 0), string(b''), string(b'0')),
                  [SCALARS[1], SCALARS[3], SCALARS[5], SCALARS[6], SCALARS[0]], strict=True)]
    cases += [(('?', ('!', ('??', ('.', string(b'0'), NULL), string(b'BAD'))), NULL, FALSE), 'PNULL'),
              (('?', string(b'10'), NULL, FALSE), 'PNULL'),
              (('?', string(b'10'), None, FALSE), pstring(b'10'))]
    result = bindings()
    for number, (shape, value) in enumerate(cases):
        expression, _, occurrences = source_tree(shape, 'typed_' + str(number))
        state = 'S_typed_value_' + str(number)
        result += [f'{state} = ' + raw.source_state(occurrences),
                   typed(state + '.SOURCES', 'porigin_tree_root_class', expression) + f' = ({value})']
    return result


def bytes_values():
    cases = []
    for shape, value, echo in SCALARS:
        left = ('?', string(b'00'), shape, TRUE)
        coal = ('??', left, string(b'R'))
        selected = b'R' if value == 'PNULL' else echo
        cases += [(coal, selected), (('!', coal), b'1' if selected in (b'', b'0') else b''),
                  (('.', string(b'P'), coal), b'P' + selected)]
    cases += [(('??', ('?', string(b'0'), None, NULL), string(b'0')), b'0'),
              (('??', ('?', string(b'0'), None, FALSE), string(b'BAD')), b''),
              (('??', ('?', ('i', 10), None, FALSE), string(b'BAD')), b'10'),
              (('??', ('?', TRUE, NULL, FALSE), ('??', NULL, string(b'R'))), b'R')]
    result = bindings()
    for number, (shape, value) in enumerate(cases):
        expression, _, occurrences = source_tree(shape, 'bytes_' + str(number))
        state = 'S_typed_bytes_' + str(number)
        result += [f'{state} = ' + raw.source_state(occurrences),
                   certificate(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = (' + payload(value) + ')']
    return result


SITES = [
    {'class': [
        (('?', string(b'00'), NULL, string(b'BAD_FULL_NULL')), b'0', 'PNULL', b'0'),
        (('?', TRUE, FALSE, string(b'BAD_FULL_FALSE')), b'BAD_FALSE_FALLBACK', 'PBOOL false', b''),
        (('?', TRUE, string(b''), string(b'BAD_FULL_EMPTY')), b'BAD_EMPTY_FALLBACK', pstring(b''), b''),
        (('?', TRUE, string(b'0'), string(b'BAD_FULL_ZERO')), b'BAD_ZERO_FALLBACK', pstring(b'0'), b'0'),
        (('?', string(b'0'), None, NULL), b'0', 'PNULL', b'0')],
     'method': [
        (('?', TRUE, ('i', 0), string(b'BAD_FULL_INT')), b'BAD_INT_FALLBACK', 'PINT 0', b'0'),
        (('?', string(b'10'), None, string(b'BAD_SHORT_TRUE')), b'BAD_SHORT_TRUE_FALLBACK', pstring(b'10'), b'10'),
        (('?', FALSE, None, FALSE), b'BAD_SHORT_FALSE_FALLBACK', 'PBOOL false', b'')]},
    {'class': [
        (('?', string(b'0'), string(b'BAD_FULL_TRUE'), NULL), b'00', 'PNULL', b'00'),
        (('?', ('i', 10), None, string(b'BAD_SHORT_INT')), b'BAD_SHORT_INT_FALLBACK', 'PINT 10', b'10')],
     'method': [
        (('?', string(b'0'), string(b'BAD_FULL_INT_TRUE'), ('i', 0)), b'BAD_INT_FALLBACK', 'PINT 0', b'0'),
        (('?', string(b'0'), None, string(b'0')), b'BAD_STRING_ZERO_FALLBACK', pstring(b'0'), b'0'),
        (('?', string(b'0'), string(b'BAD_FULL_EMPTY_TRUE'), string(b'')), b'BAD_EMPTY_FALLBACK', pstring(b''), b''),
        (('?', string(b'0'), string(b'BAD_FULL_FALSE_TRUE'), FALSE), b'BAD_FALSE_FALLBACK', 'PBOOL false', b'')]},
]


def sites(index, side):
    result = bindings(index)
    items = SITES[index][side]
    for number, (left, right, value, echo) in enumerate(items):
        parts = (0 if side == 'class' else 1,) + (0,) * (len(items) - number - 1) + (1,)
        expression, nodes, extra = tree(('??', left, string(right)), 'site_' + str(number))
        expression_left = dict(nodes[0][4])[0]
        origin, origin_left = 'porigin_typed_site_' + str(number), 'porigin_typed_left_' + str(number)
        result += [f'$origin_child((porigin_site),{raw.path(parts)}) = ({origin})',
                   f'$origin_node(S.SOURCES,{origin}) = ({expression})', *extra,
                   f'$origin_child(({origin}),[PCFIELD 0]) = ({origin_left})',
                   typed('S.SOURCES', origin_left, expression_left) + f' = ({value})',
                   f'$property_magic_cv_raw_primitive_coalesce_left(S.SOURCES,{origin_left},{expression_left}) = eps',
                   certificate('S.SOURCES', origin, expression) + ' = (' + payload(echo) + ')',
                   prior.certificate('S.SOURCES', origin, expression) + ' = eps']
        if left[2] is None:
            absent = 'porigin_typed_absent_' + str(number)
            result += [f'$origin_child(({origin_left}),[PCFIELD 1]) = ({absent})', f'$origin_node(S.SOURCES,{absent}) = eps']
    return result


def domain():
    full = ('?', string(b'00'), NULL, FALSE)
    new = ('??', full, string(b'R'))
    shapes = [
        ('?', TRUE, ('!', FALSE), NULL), ('?', TRUE, ('.', string(b''), FALSE), NULL),
        ('?', TRUE, full, NULL), ('?', TRUE, NULL, ('cv', b'skipped')),
        ('?', FALSE, ('cv', b'skipped'), NULL), ('?', TRUE, NULL, ('f', '0000000000000000')),
        ('?', ('f', '8000000000000000'), NULL, FALSE), ('?', string(b'\0'), NULL, FALSE),
        ('?', TRUE, string(b'\0'), NULL), ('?', FALSE, string(b'\0'), NULL),
        ('?', ('!', FALSE), None, NULL), ('?', string(b'10'), None, full),
        ('?', ('f', '7ff8000000000000'), None, NULL), ('?', string(b'\0'), None, NULL),
        ('?', TRUE, ('i', 9223372036854775808), NULL),
    ]
    result = bindings()
    for number, shape in enumerate(shapes):
        expression, _, occurrences = source_tree(shape, 'domain_' + str(number))
        state = 'S_typed_domain_' + str(number)
        value = {0: 'PBOOL true', 1: pstring(b''), 2: 'PNULL', 10: 'PBOOL true', 11: pstring(b'10')}.get(number)
        result += [f'{state} = ' + raw.source_state(occurrences),
                   typed(state + '.SOURCES', 'porigin_tree_root_class', expression) + (' = eps' if value is None else f' = ({value})')]
    parents = [('&&', new, TRUE), ('or', FALSE, new), ('?', TRUE, new, FALSE),
               ('??', full, new), ('??', ('.', new, string(b'')), string(b'R')),
               ('.', new, string(b'\0')), ('!', ('??', full, string(b'\0')))]
    for number, shape in enumerate(parents):
        expression, _, occurrences = source_tree(shape, 'parent_' + str(number))
        state = 'S_typed_parent_' + str(number)
        result += [f'{state} = ' + raw.source_state(occurrences),
                   certificate(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    expression, _, occurrences = source_tree(('?', TRUE, NULL, string(b'REJECT')), 'owning')
    placeholder = 'NScalarString (BYTES "UkVKRUNU") metadata_class'
    name = 'NNameFullyQualified (BYTES "c3RkQ2xhc3M=") metadata_class'
    for label, child in (('array', 'NExprArray (SEQUENCE eps) metadata_class'),
                         ('object', f'NExprNew ({name}) (SEQUENCE eps) metadata_class')):
        changed, source = expression.replace(placeholder, child), occurrences.replace(placeholder, child)
        if label == 'object':
            source = f'(PCOCCURRENCE (pcpath_site ++ [PCFIELD 0,PCFIELD 2,PCFIELD 0]) ({name})) :: ({source})'
        state = 'S_typed_owner_' + label
        result += [f'{state} = ' + raw.source_state(source),
                   typed(state + '.SOURCES', 'porigin_tree_root_class', changed) + ' = eps']
    return result


def source_guards():
    expression, nodes, occurrences = source_tree(('??', ('?', string(b'00'), ('k', 'NULL', True), FALSE), string(b'R')), 'source')
    left = dict(nodes[0][4])[0]
    result = bindings() + ['S_typed_source = ' + raw.source_state(occurrences),
                          certificate('S_typed_source.SOURCES', 'porigin_tree_root_class', expression) + ' = (' + payload(b'R') + ')']
    for number, (parts, node, metadata, kind, _) in enumerate(nodes):
        path = 'pcpath_site ++ ' + raw.path((0,) + parts)
        changes = [('missing', f'$rawtree_review_without(S_typed_source.SOURCES[0].OCCURRENCES,{path})'),
                   ('metadata', f'(PCOCCURRENCE ({path}) ({node.removesuffix(metadata)}eps)) :: S_typed_source.SOURCES[0].OCCURRENCES')]
        if kind == 'name':
            changed = node.replace('NNameFullyQualified', 'NNameRelative', 1) if 'NNameFullyQualified' in node else node.replace('NName ', 'NNameRelative ', 1)
            changes.append(('name', f'(PCOCCURRENCE ({path}) ({changed})) :: S_typed_source.SOURCES[0].OCCURRENCES'))
        for label, source in changes:
            state = 'S_typed_source_' + str(number) + '_' + label
            result += [f'{state} = ' + raw.source_state(source),
                       certificate(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    result += ['$origin_child((porigin_tree_root_class),[PCFIELD 0]) = (porigin_typed_source_left)',
               typed('S_typed_source.SOURCES', 'porigin_typed_source_left', left) + ' = (PNULL)']
    return result


def authority(side):
    result = bindings() + root(side)
    field = 0 if side == 'class' else 1
    path, other = f'(pcpath_site ++ [PCFIELD {field}])', f'(pcpath_site ++ [PCFIELD {1-field}])'
    result += ['$code_at(S.CODE,n_unit) = (pcode_typed)',
               f'$code_expression(pcode_typed.EXPRESSIONS,{path}) = ((z_typed,false))',
               f'$code_expression(pcode_typed.EXPRESSIONS,{other}) = ((z_typed_other,false))',
               f'S_typed_minimal = S[.CODE = [pcode_typed[.EXPRESSIONS = [CODEEXPR {path} z_typed false,CODEEXPR {other} z_typed_other false]]]][.POOLS = eps]',
               emitted('S_typed_minimal', side) + f' = (PSTRING ptbytes_{side})', raw.selector(side, 'S_typed_minimal')]
    for label, code in (
        ('constant', f'pcode_typed[.EXPRESSIONS = (CODEEXPR {path} z_typed true) :: pcode_typed.EXPRESSIONS]'),
        ('zero', f'pcode_typed[.EXPRESSIONS = (CODEEXPR {path} 0 false) :: pcode_typed.EXPRESSIONS]'),
        ('negative', f'pcode_typed[.EXPRESSIONS = (CODEEXPR {path} $(-1) false) :: pcode_typed.EXPRESSIONS]'),
        ('effect', f'pcode_typed[.EXPRESSIONS = (CODEEFFECT {path}) :: pcode_typed.EXPRESSIONS]'),
        ('redirect', f'pcode_typed[.REDIRECTS = (CODEREDIRECT {path} ({path} ++ [PCFIELD 0]) false) :: pcode_typed.REDIRECTS]'),
    ):
        state = 'S_typed_code_' + side + '_' + label
        result += [f'{state} = S[.CODE = [{code}]]', emitted(state, side) + ' = eps', '~' + raw.selector(side, state)]
    for label, code in (('missing', 'eps'), ('wrong', '[pcode_typed[.UNIT = $(n_unit + 1)]]')):
        state = 'S_typed_code_' + side + '_' + label
        result += [f'{state} = S[.CODE = {code}]', emitted(state, side) + ' = eps']
    for label, value in (('string', f'PSTRING ptbytes_{side}'), ('boolean', 'PBOOL true')):
        state = 'S_typed_pool_' + side + '_' + label
        result += [f'{state} = S[.POOLS = [{{UNIT n_unit,CONSTANTS ([PCONSTANT {path} ({value})])}}]]',
                   emitted(state, side) + ' = eps', '~' + raw.selector(side, state)]
    return result


def frontier():
    new = ('??', ('?', TRUE, NULL, FALSE), string(b'R'))
    cases = [(new, True, None, b'R'), (('!', new), True, None, b''),
             (('.', string(b'P'), new), True, None, b'PR'),
             (('??', NULL, string(b'R')), False, b'R', b'R'),
             (('?', string(b'10'), None, FALSE), False, b'10', b'10'),
             (('&&', new, TRUE), False, None, None)]
    result = bindings()
    for number, (shape, marked, old, value) in enumerate(cases):
        expression, _, occurrences = source_tree(shape, 'frontier_' + str(number))
        state = 'S_typed_frontier_' + str(number)
        result += [f'{state} = ' + raw.source_state(occurrences), ('' if marked else '~') + witness(expression),
                   prior.certificate(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = ' + ('eps' if old is None else '(' + payload(old) + ')'),
                   certificate(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = ' + ('eps' if value is None else '(' + payload(value) + ')')]
    return result


CASES = {}
for index, row in enumerate(ROWS):
    base = dict(prior.CASES[prior.ROWS[index]['id'] + '-roots'], source=row['source'])
    CASES[row['id'] + '-roots'] = dict(base, checks=roots(index))
    for side in ('class', 'method'):
        CASES[row['id'] + '-sites-' + side] = dict(base, checks=sites(index, side))
base = CASES[ROWS[0]['id'] + '-roots']
for suffix, checks in (('typed-values', typed_values()), ('bytes-values', bytes_values()), ('domain', domain()),
                       ('source', source_guards()), ('authority-class', authority('class')),
                       ('authority-method', authority('method')), ('frontier', frontier())):
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
