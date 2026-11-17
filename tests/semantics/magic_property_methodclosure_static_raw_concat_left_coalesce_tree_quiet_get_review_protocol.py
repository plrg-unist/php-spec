#!/usr/bin/env python3
"""Check nonnull CONCAT provenance, closed coalesce trees and emitted roots."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_primitive_coalesce_tree_quiet_get_review_protocol as prior

raw, renderer = prior.raw, prior.renderer
tree, payload = prior.tree, prior.prior.payload
CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_concat_left_coalesce_tree_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def certificate(sources, origin, expression):
    return f'$property_magic_cv_raw_concat_left_coalesce_tree({sources},{origin},{expression})'


def left_value(sources, origin, expression):
    return f'$property_magic_cv_raw_concat_left_coalesce_left({sources},{origin},{expression})'


def emitted(state, side):
    return f'$property_magic_cv_emitted_concat_left_coalesce_concat_value({state},porigin_tree_root_{side},expression_{side})'


def bindings(index=0):
    return prior.bindings(index)


def roots(index, side):
    origin, expression = 'porigin_tree_root_' + side, 'expression_' + side
    return bindings(index) + [
        certificate('S.SOURCES', origin, expression) + f' = (ptbytes_{side})',
        prior.certificate('S.SOURCES', origin, expression) + ' = eps',
        f'$compiled_read(S,{origin}) = eps',
        f'$pool_value(S.POOLS,{origin}) = eps',
        emitted('S', side) + f' = (PSTRING ptbytes_{side})',
        raw.selector(side),
    ]


def source_tree(shape, suffix):
    expression, nodes, _ = tree(shape, suffix, concrete=True)
    occurrences = 'eps'
    for parts, node, _, _, _ in nodes:
        occurrences = f'(PCOCCURRENCE (pcpath_site ++ {raw.path((0,) + parts)}) ({node})) :: ({occurrences})'
    return expression, nodes, occurrences


def synthetic(typed=False):
    result = bindings()
    null, false, true = ('k', 'null', False), ('k', 'false', False), ('k', 'true', False)
    fqn_null = ('k', 'NULL', True)
    cat = lambda left, right: ('.', left, right)
    coal = lambda left, right: ('??', left, right)
    empty = cat(('s', b''), false)
    zero = cat(('s', b'0'), null)
    primitive_inner = cat(('s', b'1'), coal(('i', 0), ('i', 9)))
    computed = [
        (empty, b''), (zero, b'0'), (cat(false, ('i', 0)), b'0'),
        (cat(('i', 0), false), b'0'), (cat(zero, ('s', b'0')), b'00'),
        (cat(cat(('s', b'0'), false), ('s', b'1')), b'01'),
        (cat(true, fqn_null), b'1'), (primitive_inner, b'10'),
        (cat(('k', 'FALSE', True), ('s', b'0')), b'0'),
    ]
    if typed:
        cases = [(shape, 'PSTRING ' + payload(value)) for shape, value in computed]
        cases += [(null, 'PNULL'), (false, 'PBOOL false'), (('i', 0), 'PINT 0')]
        cases += [(shape, None) for shape in (
            cat(('s', b'\0'), ('s', b'')),
            cat(('s', b''), ('s', b'\0')),
            cat(('f', '0000000000000000'), ('s', b'')),
            cat(('cv', b'current'), ('s', b'')),
            cat(coal(empty, ('s', b'R')), ('s', b'')),
            coal(null, ('s', b'0')),
        )]
    else:
        cases = [(coal(shape, ('s', b'BAD')), value) for shape, value in computed]
        cases += [
            (coal(null, coal(zero, ('s', b'BAD'))), b'0'),
            (coal(false, coal(zero, ('s', b'BAD'))), b''),
            (coal(('i', 0), coal(empty, ('s', b'BAD'))), b'0'),
            (coal(empty, coal(zero, ('s', b'BAD'))), b''),
            (cat(('s', b'P'), cat(coal(empty, ('s', b'BAD')), coal(zero, false))), b'P0'),
        ]
        new = coal(zero, ('s', b'BAD'))
        cases += [(shape, None) for shape in (
            coal(cat(('s', b'\0'), ('s', b'')), ('s', b'R')),
            coal(empty, ('s', b'\0')), coal(zero, ('cv', b'skipped')),
            coal(empty, ('f', '0000000000000000')),
            coal(cat(new, ('s', b'')), ('s', b'R')),
            coal(('f', '0000000000000000'), new),
            coal(('cv', b'current'), new),
            coal(('+', ('i', 0)), new),
            ('!', new), ('and', true, new), ('or', false, new),
            ('xor', true, new), ('?', true, new, ('s', b'R')),
            ('?', true, ('s', b'L'), new), ('?', false, None, new),
        )]
    for number, (shape, value) in enumerate(cases):
        expression, _, occurrences = source_tree(shape, str(number))
        state = 'S_concat_coalesce_control_' + str(number)
        expected = 'eps' if value is None else '(' + (value if typed else payload(value)) + ')'
        call = left_value if typed else certificate
        result += [f'{state} = ' + raw.source_state(occurrences),
                   call(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = ' + expected]
    return result


def source_guards():
    result = bindings()
    shape = ('??', ('.', ('k', 'NULL', True), ('s', b'0')), ('k', 'TRUE', True))
    expression, nodes, occurrences = source_tree(shape, 'source')
    result += ['S_concat_source = ' + raw.source_state(occurrences),
               certificate('S_concat_source.SOURCES', 'porigin_tree_root_class', expression) + ' = (' + payload(b'0') + ')',
               prior.certificate('S_concat_source.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    for number, (parts, node, _, kind, _) in enumerate(nodes):
        path = 'pcpath_site ++ ' + raw.path((0,) + parts)
        state = 'S_concat_source_missing_' + str(number)
        remaining = f'$rawtree_review_without(S_concat_source.SOURCES[0].OCCURRENCES,{path})'
        result += [f'{state} = ' + raw.source_state(remaining),
                   certificate(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
        if kind == 'name':
            changed = node.replace('NNameFullyQualified', 'NName', 1)
            state = 'S_concat_source_name_' + str(number)
            replacement = f'(PCOCCURRENCE ({path}) ({changed})) :: S_concat_source.SOURCES[0].OCCURRENCES'
            result += [f'{state} = ' + raw.source_state(replacement),
                       certificate(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    return result


def pools():
    result = bindings()
    for field, side in enumerate(('class', 'method')):
        result += [certificate('S.SOURCES', 'porigin_tree_root_' + side, 'expression_' + side) + f' = (ptbytes_{side})']
        for kind, value in (('string', f'PSTRING ptbytes_{side}'), ('boolean', 'PBOOL true')):
            state = 'S_concat_coalesce_pool_' + side + '_' + kind
            result += [f'{state} = S[.POOLS = [{{UNIT n_unit,CONSTANTS ([PCONSTANT (pcpath_site ++ [PCFIELD {field}]) ({value})])}}]]',
                       emitted(state, side) + ' = eps', '~' + raw.selector(side, state)]
    return result


def authority(side):
    result = roots(0, side)
    field = 0 if side == 'class' else 1
    path, other = f'(pcpath_site ++ [PCFIELD {field}])', f'(pcpath_site ++ [PCFIELD {1-field}])'
    result += ['$code_at(S.CODE,n_unit) = (pcode_concat_coalesce)',
               f'$code_expression(pcode_concat_coalesce.EXPRESSIONS,{path}) = ((z_concat_coalesce,false))',
               f'$code_expression(pcode_concat_coalesce.EXPRESSIONS,{other}) = ((z_concat_coalesce_other,false))',
               f'S_concat_coalesce_minimal = S[.CODE = [pcode_concat_coalesce[.EXPRESSIONS = [CODEEXPR {path} z_concat_coalesce false,CODEEXPR {other} z_concat_coalesce_other false]]]]',
               emitted('S_concat_coalesce_minimal', side) + f' = (PSTRING ptbytes_{side})',
               raw.selector(side, 'S_concat_coalesce_minimal')]
    for label, code in (
        ('constant', f'pcode_concat_coalesce[.EXPRESSIONS = (CODEEXPR {path} z_concat_coalesce true) :: pcode_concat_coalesce.EXPRESSIONS]'),
        ('zero_line', f'pcode_concat_coalesce[.EXPRESSIONS = (CODEEXPR {path} 0 false) :: pcode_concat_coalesce.EXPRESSIONS]'),
        ('effect', f'pcode_concat_coalesce[.EXPRESSIONS = (CODEEFFECT {path}) :: pcode_concat_coalesce.EXPRESSIONS]'),
        ('redirect', f'pcode_concat_coalesce[.REDIRECTS = (CODEREDIRECT {path} (pcpath_site ++ [PCFIELD 99]) false) :: pcode_concat_coalesce.REDIRECTS]'),
    ):
        state = 'S_concat_coalesce_code_' + side + '_' + label
        result += [f'{state} = S[.CODE = [{code}]]', emitted(state, side) + ' = eps',
                   '~' + raw.selector(side, state)]
    for label, code in (('missing_unit', 'eps'), ('wrong_unit', '[pcode_concat_coalesce[.UNIT = $(n_unit + 1)]]')):
        state = 'S_concat_coalesce_code_' + side + '_' + label
        result += [f'{state} = S[.CODE = {code}]', emitted(state, side) + ' = eps']
    return result


CASES = {}
for index, row in enumerate(ROWS):
    for side in ('class', 'method'):
        original = prior.ROWS[index]['id'] + '-root-' + side
        CASES[row['id'] + '-root-' + side] = dict(prior.CASES[original], source=row['source'], checks=roots(index, side))
base = dict(CASES[ROWS[0]['id'] + '-root-class'])
for suffix, checks in (
    ('owner', ['$property_magic_cv_static_methodclosure(S,n_closure)']),
    ('typed-controls', synthetic(True)), ('value-controls', synthetic()),
    ('source-guards', source_guards()), ('pools', pools()),
    ('authority-class', authority('class')), ('authority-method', authority('method')),
):
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
