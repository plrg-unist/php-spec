#!/usr/bin/env python3
"""Check ternary selection, optional arms and closed coalesce selector authority."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_boolean_not_concat_left_coalesce_tree_quiet_get_review_protocol as prior

raw, renderer, payload = prior.raw, prior.renderer, prior.payload
source_tree, tree = prior.source_tree, prior.prior.prior.tree
bindings = prior.prior.bindings
CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_ternary_boolean_not_concat_left_coalesce_tree_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_bytes())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
NULL, FALSE, TRUE = ('k', 'null', False), ('k', 'false', False), ('k', 'true', False)
ZERO = ('??', ('.', ('s', b'0'), NULL), ('s', b'BAD_COND'))
ZEROS = ('??', ('.', ('s', b'00'), NULL), ('s', b'BAD_COND'))
TEN = ('??', ('.', ('s', b'10'), NULL), ('s', b'BAD_COND'))


def certificate(sources, origin, expression):
    return f'$property_magic_cv_raw_ternary_boolean_not_concat_left_coalesce_tree({sources},{origin},{expression})'


def witness(expression):
    return f'$property_magic_cv_coalesce_under_ternary({expression},false)'


def emitted(state, side):
    return f'$property_magic_cv_emitted_ternary_boolean_not_concat_left_coalesce_concat_value({state},porigin_tree_root_{side},expression_{side})'


def root(side):
    origin, expression = 'porigin_tree_root_' + side, 'expression_' + side
    return [witness(expression),
            certificate('S.SOURCES', origin, expression) + f' = (ptbytes_{side})',
            prior.certificate('S.SOURCES', origin, expression) + ' = eps',
            f'$compiled_read(S,{origin}) = eps', f'$pool_value(S.POOLS,{origin}) = eps',
            emitted('S', side) + f' = (PSTRING ptbytes_{side})', raw.selector(side)]


def roots(index):
    return bindings(index) + root('class') + root('method') + [
        '$property_magic_cv_static_methodclosure(S,n_closure)',
        '$property_empty_rv_kind(S,S.OBJECTS[n_closure])']


def values():
    full = ('?', ZEROS, NULL, ('s', b'R'))
    short = ('?', TEN, None, ('s', b'R'))
    cases = [
        (('?', ZEROS, ('s', b'0'), ('s', b'R')), b'0'),
        (('?', ZERO, NULL, ('s', b'R')), b'R'),
        (('?', ZEROS, None, ('s', b'R')), b'00'),
        (('?', ZERO, None, ('s', b'1')), b'1'), (short, b'10'), (full, b''),
        (('?', ('!', ZERO), FALSE, ('s', b'R')), b''),
        (('?', ('!', ZEROS), NULL, ('s', b'00')), b'00'),
        (('?', ('??', NULL, FALSE), ('s', b'L'), ('s', b'R')), b'R'),
        (('?', ('??', FALSE, TRUE), ('s', b'L'), ('s', b'R')), b'R'),
        (('?', TEN, ('i', 0), ('s', b'R')), b'0'),
        (('?', ZERO, ('s', b'L'), ('i', 12)), b'12'),
        (('?', ('?', ZEROS, ('s', b'0'), ('s', b'R')), ('s', b'A'), ('s', b'B')), b'B'),
        (('?', ZERO, None, ('?', TEN, None, ('s', b'R'))), b'10'),
        (('!', ('?', ZEROS, ('s', b'0'), ('s', b'R'))), b'1'),
        (('!', full), b'1'), (('.', ('s', b'P'), short), b'P10'),
        (('?', ('||', ('!', ZEROS), ('s', b'00')), ('s', b'00'), ('s', b'R')), b'00'),
    ]
    for op in prior.BOOLEAN:
        cases += [((op, full, short), b'1' if op in ('||', 'or', 'xor') else b''),
                  ((op, short, ('?', ZEROS, ('s', b'00'), NULL)), b'' if op == 'xor' else b'1')]
    result = bindings()
    for number, (shape, value) in enumerate(cases):
        expression, _, occurrences = source_tree(shape, 'value_' + str(number))
        state = 'S_ternary_coalesce_value_' + str(number)
        result += [f'{state} = ' + raw.source_state(occurrences),
                   certificate(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = (' + payload(value) + ')']
    return result


def domain():
    new = ('?', ZEROS, NULL, ('s', b'R'))
    shapes = [
        ('?', ZEROS, ('s', b'good'), ('cv', b'skipped')),
        ('?', ZERO, ('cv', b'skipped'), ('s', b'good')),
        ('?', TEN, None, ('cv', b'skipped')),
        ('?', ('f', '8000000000000000'), new, NULL),
        ('?', ZEROS, ('f', '7ff8000000000000'), NULL),
        ('?', ZERO, NULL, ('f', '0000000000000000')),
        ('?', ('s', b'\0'), new, NULL), ('?', ZEROS, ('s', b'\0'), NULL),
        ('?', ZERO, ('s', b'\0'), new), ('?', ZEROS, None, ('s', b'\0')),
        ('?', ZEROS, NULL, ('+', ('s', b'1foo'))),
        ('?', ZERO, ('-', ('i', 1)), new),
        ('??', NULL, new), ('??', ('.', new, ('s', b'')), ('s', b'R')),
        ('||', TRUE, ('?', ZEROS, ('s', b'good'), ('cv', b'skipped'))),
        ('.', new, ('s', b'\0')), ('.', ('s', b'\0'), new),
    ]
    result = bindings()
    for number, shape in enumerate(shapes):
        expression, _, occurrences = source_tree(shape, 'domain_' + str(number))
        state = 'S_ternary_coalesce_domain_' + str(number)
        result += [f'{state} = ' + raw.source_state(occurrences),
                   certificate(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    expression, _, occurrences = source_tree(('?', ZEROS, NULL, ('s', b'R')), 'owning')
    placeholder = 'NScalarString (BYTES "Ug==") metadata_class'
    name = 'NNameFullyQualified (BYTES "c3RkQ2xhc3M=") metadata_class'
    for label, child in (('array', 'NExprArray (SEQUENCE eps) metadata_class'),
                         ('object', f'NExprNew ({name}) (SEQUENCE eps) metadata_class')):
        changed, source = expression.replace(placeholder, child), occurrences.replace(placeholder, child)
        if label == 'object':
            source = f'(PCOCCURRENCE (pcpath_site ++ [PCFIELD 0,PCFIELD 2,PCFIELD 0]) ({name})) :: ({source})'
        state = 'S_ternary_coalesce_' + label
        result += [f'{state} = ' + raw.source_state(source),
                   certificate(state + '.SOURCES', 'porigin_tree_root_class', changed) + ' = eps']
    return result


def sites(index):
    samples = ((('class', (0, 1), ('?', ('||', ('!', ZEROS), ('s', b'00')), ('s', b'00'), ('s', b'BAD_CLASS')), b'00'),
                ('method', (1, 1, 0), ('?', ZERO, None, ('s', b'1')), b'1')) if index == 0 else
               (('class', (0, 1), ('?', TEN, None, ('s', b'BAD_CLASS')), b'10'),
                ('method', (1, 1, 0), ('?', ('!', ('??', ('.', ('s', b'0'), FALSE), ('s', b'BAD_COND'))), NULL, ('s', b'BAD_METHOD')), b'')))
    result = bindings(index) + ['$code_at(S.CODE,n_unit) = (pcode_ternary_sites)']
    for number, (side, parts, shape, value) in enumerate(samples):
        expression, nodes, extra = tree(shape, 'site_' + str(number))
        origin = 'porigin_ternary_coalesce_site_' + str(number)
        result += [f'$origin_child((porigin_site),{raw.path(parts)}) = ({origin})',
                   f'$origin_node(S.SOURCES,{origin}) = ({expression})', *extra,
                   certificate('S.SOURCES', origin, expression) + ' = (' + payload(value) + ')',
                   prior.certificate('S.SOURCES', origin, expression) + ' = eps']
        for field in (0, 1, 2):
            child_origin = f'{origin}_child_{field}'
            result += [f'$origin_child(({origin}),[PCFIELD {field}]) = ({child_origin})']
            if field == 1 and shape[2] is None:
                result += [f'$origin_node(S.SOURCES,{child_origin}) = eps',
                           f'$compiled_read(S,{child_origin}) = eps', f'$pool_value(S.POOLS,{child_origin}) = eps',
                           f'{child_origin} = PORIGIN n_unit pcpath_ternary_absent_{number}',
                           f'$code_expression(pcode_ternary_sites.EXPRESSIONS,pcpath_ternary_absent_{number}) = eps']
            else:
                child = dict(nodes[0][4])[field]
                result += [f'$origin_node(S.SOURCES,{child_origin}) = ({child})']
                if field == 1 and shape[2] == NULL:
                    result += [f'$compiled_read(S,{child_origin}) = (PNULL)', f'$pool_value(S.POOLS,{child_origin}) = (PNULL)']
    return result


def source_guards():
    shape = ('?', ('||', ('!', ZEROS), ('s', b'00')), ('k', 'NULL', True), ('?', ZERO, None, FALSE))
    expression, nodes, occurrences = source_tree(shape, 'source')
    result = bindings() + ['S_ternary_coalesce_source = ' + raw.source_state(occurrences),
                          certificate('S_ternary_coalesce_source.SOURCES', 'porigin_tree_root_class', expression) + ' = (' + payload(b'') + ')']
    for number, (parts, node, _, kind, _) in enumerate(nodes):
        path = 'pcpath_site ++ ' + raw.path((0,) + parts)
        state = 'S_ternary_coalesce_missing_' + str(number)
        remaining = f'$rawtree_review_without(S_ternary_coalesce_source.SOURCES[0].OCCURRENCES,{path})'
        result += [f'{state} = ' + raw.source_state(remaining),
                   certificate(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
        if kind == 'name':
            state = 'S_ternary_coalesce_name_' + str(number)
            changed = node.replace('NNameFullyQualified', 'NName', 1) if 'NNameFullyQualified' in node else node.replace('NName ', 'NNameRelative ', 1)
            result += [f'{state} = ' + raw.source_state(f'(PCOCCURRENCE ({path}) ({changed})) :: S_ternary_coalesce_source.SOURCES[0].OCCURRENCES'),
                       certificate(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    return result


def authority(side):
    result = bindings() + root(side)
    field = 0 if side == 'class' else 1
    path, other = f'(pcpath_site ++ [PCFIELD {field}])', f'(pcpath_site ++ [PCFIELD {1-field}])'
    result += ['$code_at(S.CODE,n_unit) = (pcode_ternary_coalesce)',
               f'$code_expression(pcode_ternary_coalesce.EXPRESSIONS,{path}) = ((z_ternary_coalesce,false))',
               f'$code_expression(pcode_ternary_coalesce.EXPRESSIONS,{other}) = ((z_ternary_coalesce_other,false))',
               f'S_ternary_coalesce_minimal = S[.CODE = [pcode_ternary_coalesce[.EXPRESSIONS = [CODEEXPR {path} z_ternary_coalesce false,CODEEXPR {other} z_ternary_coalesce_other false]]]]',
               emitted('S_ternary_coalesce_minimal', side) + f' = (PSTRING ptbytes_{side})',
               raw.selector(side, 'S_ternary_coalesce_minimal')]
    for label, code in (
        ('constant', f'pcode_ternary_coalesce[.EXPRESSIONS = (CODEEXPR {path} z_ternary_coalesce true) :: pcode_ternary_coalesce.EXPRESSIONS]'),
        ('zero', f'pcode_ternary_coalesce[.EXPRESSIONS = (CODEEXPR {path} 0 false) :: pcode_ternary_coalesce.EXPRESSIONS]'),
        ('negative', f'pcode_ternary_coalesce[.EXPRESSIONS = (CODEEXPR {path} $(-1) false) :: pcode_ternary_coalesce.EXPRESSIONS]'),
        ('effect', f'pcode_ternary_coalesce[.EXPRESSIONS = (CODEEFFECT {path}) :: pcode_ternary_coalesce.EXPRESSIONS]'),
        ('redirect', f'pcode_ternary_coalesce[.REDIRECTS = (CODEREDIRECT {path} (pcpath_site ++ [PCFIELD 99]) false) :: pcode_ternary_coalesce.REDIRECTS]'),
    ):
        state = 'S_ternary_coalesce_code_' + side + '_' + label
        result += [f'{state} = S[.CODE = [{code}]]', emitted(state, side) + ' = eps', '~' + raw.selector(side, state)]
    for label, code in (('missing', 'eps'), ('wrong', '[pcode_ternary_coalesce[.UNIT = $(n_unit + 1)]]')):
        state = 'S_ternary_coalesce_code_' + side + '_' + label
        result += [f'{state} = S[.CODE = {code}]', emitted(state, side) + ' = eps']
    for label, value in (('string', f'PSTRING ptbytes_{side}'), ('boolean', 'PBOOL true')):
        state = 'S_ternary_coalesce_pool_' + side + '_' + label
        result += [f'{state} = S[.POOLS = [{{UNIT n_unit,CONSTANTS ([PCONSTANT {path} ({value})])}}]]',
                   emitted(state, side) + ' = eps', '~' + raw.selector(side, state)]
    return result


def frontier():
    new = ('?', ZEROS, NULL, ('s', b'R'))
    shapes = [(new, True, None, b''), (('!', new), True, None, b'1'),
              (('.', ('s', b'P'), new), True, None, b'P'),
              (('or', FALSE, new), True, None, b''),
              (('?', TRUE, ('s', b'L'), ZERO), True, None, b'L'),
              (('?', ZEROS, None, FALSE), True, None, b'00'),
              (('||', ('!', ZERO), ('s', b'00')), False, b'1', b'1'),
              (('?', ('s', b'00'), NULL, FALSE), False, b'', b''),
              (('??', NULL, new), False, None, None)]
    result = bindings()
    for number, (shape, marked, old, value) in enumerate(shapes):
        expression, _, occurrences = source_tree(shape, 'frontier_' + str(number))
        state = 'S_ternary_coalesce_frontier_' + str(number)
        result += [f'{state} = ' + raw.source_state(occurrences), ('' if marked else '~') + witness(expression),
                   prior.certificate(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = ' + ('eps' if old is None else '(' + payload(old) + ')'),
                   certificate(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = ' + ('eps' if value is None else '(' + payload(value) + ')')]
    return result


CASES = {}
for index, row in enumerate(ROWS):
    base = dict(prior.CASES[prior.ROWS[index]['id'] + '-roots'], source=row['source'])
    CASES[row['id'] + '-roots'] = dict(base, checks=roots(index))
    CASES[row['id'] + '-sites'] = dict(base, checks=sites(index))
base = CASES[ROWS[0]['id'] + '-roots']
for suffix, checks in (('values', values()), ('domain', domain()), ('source', source_guards()),
                       ('authority-class', authority('class')), ('authority-method', authority('method')),
                       ('frontier', frontier())):
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
