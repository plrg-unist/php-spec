#!/usr/bin/env python3
"""Check closed NOT truth, source provenance and emitted selector authority."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_concat_left_coalesce_tree_quiet_get_review_protocol as prior

raw, renderer, payload = prior.raw, prior.renderer, prior.payload
source_tree = prior.source_tree
CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_not_concat_left_coalesce_tree_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_bytes())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def certificate(sources, origin, expression):
    return f'$property_magic_cv_raw_not_concat_left_coalesce_tree({sources},{origin},{expression})'


def emitted(state, side):
    return f'$property_magic_cv_emitted_not_concat_left_coalesce_concat_value({state},porigin_tree_root_{side},expression_{side})'


def bindings(index=0):
    return prior.bindings(index)


def roots(index, side):
    origin, expression = 'porigin_tree_root_' + side, 'expression_' + side
    return bindings(index) + [
        f'$property_magic_cv_coalesce_under_not({expression},false)',
        certificate('S.SOURCES', origin, expression) + f' = (ptbytes_{side})',
        prior.certificate('S.SOURCES', origin, expression) + ' = eps',
        f'$compiled_read(S,{origin}) = eps',
        f'$pool_value(S.POOLS,{origin}) = eps',
        emitted('S', side) + f' = (PSTRING ptbytes_{side})',
        raw.selector(side),
    ]


def synthetic(negative=False):
    result = bindings()
    null, false, true = ('k', 'null', False), ('k', 'false', False), ('k', 'true', False)
    cat = lambda left, right: ('.', left, right)
    coal = lambda left, right: ('??', left, right)
    inv = lambda child: ('!', child)
    empty, zero = cat(('s', b''), false), cat(('s', b'0'), null)
    c0, c00 = coal(zero, ('s', b'BAD')), coal(cat(zero, ('s', b'0')), ('s', b'BAD'))
    new = inv(c0)
    if not negative:
        cases = [
            (inv(coal(empty, ('s', b'BAD'))), b'1'), (new, b'1'),
            (inv(c00), b''), (inv(coal(cat(('s', b'0'), true), ('s', b'BAD'))), b''),
            (inv(coal(cat(('s', b'-'), ('i', 0)), ('s', b'BAD'))), b''),
            (inv(inv(c0)), b''), (inv(inv(inv(c0))), b'1'),
            (inv(inv(inv(c00))), b''), (inv(inv(inv(inv(c00)))), b'1'),
            (inv(coal(null, false)), b'1'), (inv(coal(false, true)), b'1'),
            (inv(coal(true, false)), b''), (inv(coal(('i', 0), ('i', 1))), b'1'),
            (inv(coal(('i', '$(-1)'), ('i', 0))), b''),
            (inv(coal(('s', b''), ('s', b'R'))), b'1'),
            (inv(coal(('s', b'0'), ('s', b'R'))), b'1'),
            (inv(coal(('s', b'00'), ('s', b'R'))), b''),
            (inv(coal(('s', b'01'), ('s', b'R'))), b''),
            (inv(coal(('s', b'\xff'), ('s', b'R'))), b''),
            (cat(('s', b'P'), new), b'P1'),
            (inv(cat(c0, inv(c00))), b'1'),
            (cat(inv(coal(empty, false)), cat(new, inv(c00))), b'11'),
        ]
    else:
        cases = [(shape, None) for shape in (
            inv(('f', '8000000000000000')), inv(('f', '0000000000000000')),
            inv(('f', '7ff8000000000000')), inv(('cv', b'current')),
            inv(coal(('f', '8000000000000000'), ('s', b'R'))),
            inv(coal(null, ('f', '7ff8000000000000'))),
            inv(coal(cat(('s', b'\0'), ('s', b'')), ('s', b'R'))),
            inv(coal(empty, ('s', b'\0'))), inv(cat(c0, ('s', b'\0'))),
            ('and', true, new), ('or', false, new), ('xor', true, new),
            ('?', true, new, ('s', b'R')), ('?', true, ('s', b'L'), new),
            ('?', false, None, new), coal(null, new), coal(false, new),
            coal(('s', b'0'), new), coal(cat(new, ('s', b'')), ('s', b'R')),
        )]
    for number, (shape, value) in enumerate(cases):
        expression, _, occurrences = source_tree(shape, str(number))
        state = 'S_not_coalesce_control_' + str(number)
        expected = 'eps' if value is None else '(' + payload(value) + ')'
        result += [f'{state} = ' + raw.source_state(occurrences),
                   certificate(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = ' + expected]
    if negative:
        name = 'NNameFullyQualified (BYTES "c3RkQ2xhc3M=") metadata_class'
        for label, child, children in (
            ('array', 'NExprArray (SEQUENCE eps) metadata_class', []),
            ('object', f'NExprNew ({name}) (SEQUENCE eps) metadata_class', [((0, 0), name)]),
        ):
            expression = f'NExprBooleanNot ({child}) metadata_class'
            nodes = [((), expression), ((0,), child), *children]
            occurrences = 'eps'
            for parts, node in nodes:
                occurrences = f'(PCOCCURRENCE (pcpath_site ++ {raw.path((0,) + parts)}) ({node})) :: ({occurrences})'
            state = 'S_not_coalesce_' + label
            result += [f'{state} = ' + raw.source_state(occurrences),
                       certificate(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    return result


def source_guards():
    result = bindings()
    shape = ('!', ('??', ('.', ('k', 'NULL', True), ('s', b'0')), ('k', 'TRUE', True)))
    expression, nodes, occurrences = source_tree(shape, 'source')
    result += ['S_not_source = ' + raw.source_state(occurrences),
               certificate('S_not_source.SOURCES', 'porigin_tree_root_class', expression) + ' = (' + payload(b'1') + ')',
               prior.certificate('S_not_source.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    for number, (parts, node, _, kind, _) in enumerate(nodes):
        path = 'pcpath_site ++ ' + raw.path((0,) + parts)
        state = 'S_not_source_missing_' + str(number)
        remaining = f'$rawtree_review_without(S_not_source.SOURCES[0].OCCURRENCES,{path})'
        result += [f'{state} = ' + raw.source_state(remaining),
                   certificate(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
        if kind == 'name':
            changed = node.replace('NNameFullyQualified', 'NName', 1)
            state = 'S_not_source_name_' + str(number)
            replacement = f'(PCOCCURRENCE ({path}) ({changed})) :: S_not_source.SOURCES[0].OCCURRENCES'
            result += [f'{state} = ' + raw.source_state(replacement),
                       certificate(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    return result


def dispatch_frontier():
    result = bindings()
    null, false = ('k', 'null', False), ('k', 'false', False)
    empty = ('.', ('s', b''), false)
    new = ('!', ('??', empty, ('s', b'BAD')))
    cases = (
        (new, True, None, b'1'),
        (('.', ('s', b'P'), new), True, None, b'P1'),
        (('!', ('.', ('s', b'P'), ('??', null, ('s', b'R')))), True, None, b''),
        (('??', empty, ('s', b'BAD')), False, b'', b''),
        (('!', ('.', ('s', b'0'), ('s', b'1'))), False, b'', b''),
        (('??', null, ('!', false)), False, b'1', b'1'),
        (('??', null, new), False, None, None),
        (('and', false, new), False, None, None),
    )
    for number, (shape, witness, old_value, value) in enumerate(cases):
        expression, _, occurrences = source_tree(shape, 'dispatch_' + str(number))
        state = 'S_not_dispatch_' + str(number)
        result += [f'{state} = ' + raw.source_state(occurrences),
                   ('' if witness else '~') + f'$property_magic_cv_coalesce_under_not({expression},false)',
                   prior.certificate(state + '.SOURCES', 'porigin_tree_root_class', expression) +
                   ' = ' + ('eps' if old_value is None else '(' + payload(old_value) + ')'),
                   certificate(state + '.SOURCES', 'porigin_tree_root_class', expression) +
                   ' = ' + ('eps' if value is None else '(' + payload(value) + ')')]
    return result


def folded_legacy(side):
    result = bindings()
    field = 0 if side == 'class' else 1
    value = b'\\QuietMethodStaticInheritedCVTarget000' if side == 'class' else b'counter12010'
    shape = ('.', ('s', b''), ('.', ('s', value), ('s', b'')))
    expression, nodes, _ = prior.tree(shape, 'folded_' + side, concrete=True)
    occurrences = 'pcunit.OCCURRENCES'
    for parts, node, _, _, _ in nodes:
        occurrences = f'(PCOCCURRENCE (pcpath_site ++ {raw.path((field,) + parts)}) ({node})) :: ({occurrences})'
    site_class = expression if side == 'class' else 'expression_class'
    site_method = expression if side == 'method' else 'expression_method'
    site = f'NExprStaticCall ({site_class}) ({site_method}) (SEQUENCE ([NVariadicPlaceholder metadata_placeholder])) metadata_site'
    occurrences = f'(PCOCCURRENCE pcpath_site ({site})) :: ({occurrences})'
    path = f'(pcpath_site ++ [PCFIELD {field}])'
    origin = 'porigin_tree_root_' + side
    state = 'S_not_folded_' + side
    code = 'pcode_not_folded_' + side
    raw_value = payload(value)
    result += [f'$code_at(S.CODE,n_unit) = ({code})',
               f'{state} = ' + raw.source_state(occurrences) +
               f'[.CODE = [{code}[.EXPRESSIONS = (CODEEXPR {path} 1 true) :: {code}.EXPRESSIONS]]]' +
               f'[.POOLS = [{{UNIT n_unit,CONSTANTS ([PCONSTANT {path} (PSTRING ({raw_value}))])}}]]',
               f'~$property_magic_cv_coalesce_under_not({expression},false)',
               f'$property_magic_cv_raw_string_tree({state}.SOURCES,{origin},{expression}) = ({raw_value})',
               prior.certificate(state + '.SOURCES', origin, expression) + f' = ({raw_value})',
               certificate(state + '.SOURCES', origin, expression) + f' = ({raw_value})',
               f'$compiled_read({state},{origin}) = (PSTRING ({raw_value}))',
               raw.selector(side, state, expression)]
    return result


def pools():
    result = bindings()
    for field, side in enumerate(('class', 'method')):
        result += [certificate('S.SOURCES', 'porigin_tree_root_' + side, 'expression_' + side) + f' = (ptbytes_{side})']
        for kind, value in (('string', f'PSTRING ptbytes_{side}'), ('boolean', 'PBOOL true')):
            state = 'S_not_coalesce_pool_' + side + '_' + kind
            result += [f'{state} = S[.POOLS = [{{UNIT n_unit,CONSTANTS ([PCONSTANT (pcpath_site ++ [PCFIELD {field}]) ({value})])}}]]',
                       emitted(state, side) + ' = eps', '~' + raw.selector(side, state)]
    expression, _, occurrences = source_tree(('.', ('s', b'Never'), ('s', b'Class')), 'overlap')
    result += ['S_not_overlap = ' + raw.source_state(occurrences),
               certificate('S_not_overlap.SOURCES', 'porigin_tree_root_class', expression) + ' = (' + payload(b'NeverClass') + ')',
               prior.certificate('S_not_overlap.SOURCES', 'porigin_tree_root_class', expression) + ' = (' + payload(b'NeverClass') + ')',
               '$compiled_read(S_not_overlap,porigin_tree_root_class) = eps',
               '$pool_value(S_not_overlap.POOLS,porigin_tree_root_class) = eps',
               '$code_at(S_not_overlap.CODE,n_unit) = (pcode_not_overlap)',
               '$code_expression(pcode_not_overlap.EXPRESSIONS,pcpath_site ++ [PCFIELD 0]) = ((z_not_overlap,false))',
               '$(z_not_overlap > 0)',
               '$code_redirect(pcode_not_overlap.REDIRECTS,pcpath_site ++ [PCFIELD 0]) = eps',
               '$compiled_effects(S_not_overlap,porigin_tree_root_class) = eps',
               f'$property_magic_cv_emitted_not_concat_left_coalesce_concat_value(S_not_overlap,porigin_tree_root_class,{expression}) = eps']
    return result


def authority(side):
    result = roots(0, side)
    field = 0 if side == 'class' else 1
    path, other = f'(pcpath_site ++ [PCFIELD {field}])', f'(pcpath_site ++ [PCFIELD {1-field}])'
    result += ['$code_at(S.CODE,n_unit) = (pcode_not_coalesce)',
               f'$code_expression(pcode_not_coalesce.EXPRESSIONS,{path}) = ((z_not_coalesce,false))',
               f'$code_expression(pcode_not_coalesce.EXPRESSIONS,{other}) = ((z_not_coalesce_other,false))',
               f'S_not_coalesce_minimal = S[.CODE = [pcode_not_coalesce[.EXPRESSIONS = [CODEEXPR {path} z_not_coalesce false,CODEEXPR {other} z_not_coalesce_other false]]]]',
               emitted('S_not_coalesce_minimal', side) + f' = (PSTRING ptbytes_{side})',
               raw.selector(side, 'S_not_coalesce_minimal')]
    for label, code in (
        ('constant', f'pcode_not_coalesce[.EXPRESSIONS = (CODEEXPR {path} z_not_coalesce true) :: pcode_not_coalesce.EXPRESSIONS]'),
        ('zero_line', f'pcode_not_coalesce[.EXPRESSIONS = (CODEEXPR {path} 0 false) :: pcode_not_coalesce.EXPRESSIONS]'),
        ('effect', f'pcode_not_coalesce[.EXPRESSIONS = (CODEEFFECT {path}) :: pcode_not_coalesce.EXPRESSIONS]'),
        ('redirect', f'pcode_not_coalesce[.REDIRECTS = (CODEREDIRECT {path} (pcpath_site ++ [PCFIELD 99]) false) :: pcode_not_coalesce.REDIRECTS]'),
    ):
        state = 'S_not_coalesce_code_' + side + '_' + label
        result += [f'{state} = S[.CODE = [{code}]]', emitted(state, side) + ' = eps',
                   '~' + raw.selector(side, state)]
    for label, code in (('missing_unit', 'eps'), ('wrong_unit', '[pcode_not_coalesce[.UNIT = $(n_unit + 1)]]')):
        state = 'S_not_coalesce_code_' + side + '_' + label
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
    ('value-controls', synthetic()), ('domain-controls', synthetic(True)),
    ('source-guards', source_guards()), ('pools-overlap', pools()),
    ('authority-class', authority('class')), ('authority-method', authority('method')),
    ('dispatch-frontier', dispatch_frontier()),
    ('folded-legacy-class', folded_legacy('class')), ('folded-legacy-method', folded_legacy('method')),
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
