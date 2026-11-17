#!/usr/bin/env python3
"""Check quiet Boolean truth, complete source and closed coalesce selector authority."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_not_concat_left_coalesce_tree_quiet_get_review_protocol as prior

raw, renderer, payload = prior.raw, prior.renderer, prior.payload
source_tree = prior.source_tree
CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_boolean_not_concat_left_coalesce_tree_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_bytes())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
BOOLEAN = ('&&', 'and', '||', 'or', 'xor')
NULL, FALSE = ('k', 'null', False), ('k', 'false', False)
QUIET_FALSE = ('!', ('??', ('.', ('s', b'00'), FALSE), ('s', b'BAD')))
QUIET_TRUE = ('!', ('??', ('.', ('s', b'0'), NULL), ('s', b'BAD')))


def certificate(sources, origin, expression):
    return f'$property_magic_cv_raw_boolean_not_concat_left_coalesce_tree({sources},{origin},{expression})'


def witness(expression):
    return f'$property_magic_cv_coalesce_under_boolean({expression},false)'


def emitted(state, side):
    return f'$property_magic_cv_emitted_boolean_not_concat_left_coalesce_concat_value({state},porigin_tree_root_{side},expression_{side})'


def root(side):
    origin, expression = 'porigin_tree_root_' + side, 'expression_' + side
    return [witness(expression),
            certificate('S.SOURCES', origin, expression) + f' = (ptbytes_{side})',
            prior.certificate('S.SOURCES', origin, expression) + ' = eps',
            f'$compiled_read(S,{origin}) = eps', f'$pool_value(S.POOLS,{origin}) = eps',
            emitted('S', side) + f' = (PSTRING ptbytes_{side})', raw.selector(side)]


def roots(index):
    return prior.bindings(index) + root('class') + root('method') + [
        '$property_magic_cv_static_methodclosure(S,n_closure)']


def values():
    result = prior.bindings()
    cases = []
    for op in BOOLEAN:
        for left, truth_left in ((QUIET_FALSE, False), (QUIET_TRUE, True)):
            for right, truth_right in ((b'0', False), (b'00', True)):
                truth = (truth_left and truth_right if op in ('&&', 'and') else
                         truth_left or truth_right if op in ('||', 'or') else truth_left != truth_right)
                cases.append(((op, left, ('s', right)), b'1' if truth else b''))
    selected = ('xor', QUIET_FALSE, ('s', b'\xff'))
    cases += [(('!', selected), b''), (('.', ('s', b'P'), selected), b'P1'),
              (('&&', ('||', QUIET_FALSE, ('s', b'00')), QUIET_TRUE), b'1')]
    zero = ('??', ('.', ('s', b'0'), FALSE), ('s', b'BAD'))
    zeros = ('??', ('.', ('s', b'00'), NULL), ('s', b'BAD'))
    cases += [(('xor', zero, ('s', b'0')), b''), (('||', zeros, ('s', b'0')), b'1'),
              (('and', ('??', NULL, FALSE), ('s', b'00')), b''),
              (('&&', ('??', FALSE, ('s', b'BAD')), ('s', b'00')), b''),
              (('or', ('??', ('i', 0), ('s', b'BAD')), ('s', b'00')), b'1')]
    for number, (shape, value) in enumerate(cases):
        expression, _, occurrences = source_tree(shape, 'value_' + str(number))
        state = 'S_boolean_coalesce_value_' + str(number)
        result += [f'{state} = ' + raw.source_state(occurrences),
                   certificate(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = (' + payload(value) + ')']
    return result


def domain():
    result = prior.bindings()
    shapes = []
    for op in BOOLEAN:
        shapes += [(op, QUIET_FALSE, ('cv', b'skipped')), (op, QUIET_TRUE, ('s', b'\0')),
                   (op, ('f', '8000000000000000'), QUIET_TRUE),
                   (op, ('f', '7ff8000000000000'), QUIET_FALSE)]
    new = ('||', QUIET_FALSE, ('s', b'00'))
    shapes += [('??', NULL, new), ('??', ('.', new, ('s', b'')), ('s', b'R')),
               ('?', ('k', 'true', False), new, ('s', b'R')), ('?', FALSE, None, new),
               ('.', new, ('s', b'\0')), ('.', ('s', b'\0'), new)]
    for number, shape in enumerate(shapes):
        expression, _, occurrences = source_tree(shape, 'domain_' + str(number))
        state = 'S_boolean_coalesce_domain_' + str(number)
        result += [f'{state} = ' + raw.source_state(occurrences),
                   certificate(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    expression, _, occurrences = source_tree(('&&', QUIET_FALSE, ('s', b'R')), 'owning')
    placeholder = 'NScalarString (BYTES "Ug==") metadata_class'
    name = 'NNameFullyQualified (BYTES "c3RkQ2xhc3M=") metadata_class'
    for label, child in (('array', 'NExprArray (SEQUENCE eps) metadata_class'),
                         ('object', f'NExprNew ({name}) (SEQUENCE eps) metadata_class')):
        changed = expression.replace(placeholder, child)
        source = occurrences.replace(placeholder, child)
        if label == 'object':
            source = f'(PCOCCURRENCE (pcpath_site ++ [PCFIELD 0,PCFIELD 1,PCFIELD 0]) ({name})) :: ({source})'
        state = 'S_boolean_coalesce_' + label
        result += [f'{state} = ' + raw.source_state(source),
                   certificate(state + '.SOURCES', 'porigin_tree_root_class', changed) + ' = eps']
    return result


def source_guards():
    result = prior.bindings()
    shape = ('||', ('!', ('??', ('.', ('k', 'NULL', True), ('s', b'0')), ('k', 'TRUE', True))), ('s', b'00'))
    expression, nodes, occurrences = source_tree(shape, 'source')
    result += ['S_boolean_coalesce_source = ' + raw.source_state(occurrences),
               certificate('S_boolean_coalesce_source.SOURCES', 'porigin_tree_root_class', expression) + ' = (' + payload(b'1') + ')',
               prior.certificate('S_boolean_coalesce_source.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    for number, (parts, node, _, kind, _) in enumerate(nodes):
        path = 'pcpath_site ++ ' + raw.path((0,) + parts)
        state = 'S_boolean_coalesce_missing_' + str(number)
        missing = f'$rawtree_review_without(S_boolean_coalesce_source.SOURCES[0].OCCURRENCES,{path})'
        result += [f'{state} = ' + raw.source_state(missing),
                   certificate(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
        if kind == 'name':
            changed = node.replace('NNameFullyQualified', 'NName', 1)
            state = 'S_boolean_coalesce_name_' + str(number)
            result += [f'{state} = ' + raw.source_state(f'(PCOCCURRENCE ({path}) ({changed})) :: S_boolean_coalesce_source.SOURCES[0].OCCURRENCES'),
                       certificate(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = eps']
    return result


def pools():
    result = prior.bindings()
    for field, side in enumerate(('class', 'method')):
        result += [certificate('S.SOURCES', 'porigin_tree_root_' + side, 'expression_' + side) + f' = (ptbytes_{side})']
        for label, value in (('string', f'PSTRING ptbytes_{side}'), ('boolean', 'PBOOL true')):
            state = 'S_boolean_coalesce_pool_' + side + '_' + label
            result += [f'{state} = S[.POOLS = [{{UNIT n_unit,CONSTANTS ([PCONSTANT (pcpath_site ++ [PCFIELD {field}]) ({value})])}}]]',
                       emitted(state, side) + ' = eps', '~' + raw.selector(side, state)]
    expression, _, occurrences = source_tree(('.', ('s', b'Never'), ('s', b'Class')), 'overlap')
    result += ['S_boolean_coalesce_overlap = ' + raw.source_state(occurrences),
               certificate('S_boolean_coalesce_overlap.SOURCES', 'porigin_tree_root_class', expression) + ' = (' + payload(b'NeverClass') + ')',
               prior.certificate('S_boolean_coalesce_overlap.SOURCES', 'porigin_tree_root_class', expression) + ' = (' + payload(b'NeverClass') + ')',
               f'$property_magic_cv_emitted_boolean_not_concat_left_coalesce_concat_value(S_boolean_coalesce_overlap,porigin_tree_root_class,{expression}) = eps']
    return result


def authority(side):
    result = prior.bindings() + root(side)
    field = 0 if side == 'class' else 1
    path, other = f'(pcpath_site ++ [PCFIELD {field}])', f'(pcpath_site ++ [PCFIELD {1-field}])'
    result += ['$code_at(S.CODE,n_unit) = (pcode_boolean_coalesce)',
               f'$code_expression(pcode_boolean_coalesce.EXPRESSIONS,{path}) = ((z_boolean_coalesce,false))',
               f'$code_expression(pcode_boolean_coalesce.EXPRESSIONS,{other}) = ((z_boolean_coalesce_other,false))',
               f'S_boolean_coalesce_minimal = S[.CODE = [pcode_boolean_coalesce[.EXPRESSIONS = [CODEEXPR {path} z_boolean_coalesce false,CODEEXPR {other} z_boolean_coalesce_other false]]]]',
               emitted('S_boolean_coalesce_minimal', side) + f' = (PSTRING ptbytes_{side})',
               raw.selector(side, 'S_boolean_coalesce_minimal')]
    for label, code in (
        ('constant', f'pcode_boolean_coalesce[.EXPRESSIONS = (CODEEXPR {path} z_boolean_coalesce true) :: pcode_boolean_coalesce.EXPRESSIONS]'),
        ('zero', f'pcode_boolean_coalesce[.EXPRESSIONS = (CODEEXPR {path} 0 false) :: pcode_boolean_coalesce.EXPRESSIONS]'),
        ('negative', f'pcode_boolean_coalesce[.EXPRESSIONS = (CODEEXPR {path} $(-1) false) :: pcode_boolean_coalesce.EXPRESSIONS]'),
        ('effect', f'pcode_boolean_coalesce[.EXPRESSIONS = (CODEEFFECT {path}) :: pcode_boolean_coalesce.EXPRESSIONS]'),
        ('redirect', f'pcode_boolean_coalesce[.REDIRECTS = (CODEREDIRECT {path} (pcpath_site ++ [PCFIELD 99]) false) :: pcode_boolean_coalesce.REDIRECTS]'),
    ):
        state = 'S_boolean_coalesce_code_' + side + '_' + label
        result += [f'{state} = S[.CODE = [{code}]]', emitted(state, side) + ' = eps', '~' + raw.selector(side, state)]
    for label, code in (('missing', 'eps'), ('wrong', '[pcode_boolean_coalesce[.UNIT = $(n_unit + 1)]]')):
        state = 'S_boolean_coalesce_code_' + side + '_' + label
        result += [f'{state} = S[.CODE = {code}]', emitted(state, side) + ' = eps']
    return result


def frontier_and_folded():
    result = prior.bindings()
    new = ('||', QUIET_FALSE, ('s', b'00'))
    cases = ((QUIET_TRUE, False, b'1', b'1'),
             (('!', QUIET_TRUE), False, b'', b''),
             (('??', NULL, QUIET_FALSE), False, None, None),
             (new, True, None, b'1'), (('!', new), True, None, b''),
             (('.', ('s', b'P'), new), True, None, b'P1'),
             (('&&', ('??', ('.', ('s', b'00'), FALSE), ('s', b'BAD')), ('s', b'00')), True, None, b'1'),
             (('??', NULL, new), False, None, None))
    for number, (shape, marked, old, value) in enumerate(cases):
        expression, _, occurrences = source_tree(shape, 'frontier_' + str(number))
        state = 'S_boolean_coalesce_frontier_' + str(number)
        result += [f'{state} = ' + raw.source_state(occurrences),
                   ('' if marked else '~') + witness(expression),
                   prior.certificate(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = ' + ('eps' if old is None else '(' + payload(old) + ')'),
                   certificate(state + '.SOURCES', 'porigin_tree_root_class', expression) + ' = ' + ('eps' if value is None else '(' + payload(value) + ')')]
    for field, side in enumerate(('class', 'method')):
        value = b'\\QuietMethodStaticInheritedCVTarget000' if side == 'class' else b'counter12010'
        expression, nodes, _ = prior.prior.tree(('.', ('s', b''), ('.', ('s', value), ('s', b''))), 'folded_' + side, concrete=True)
        occurrences = 'pcunit.OCCURRENCES'
        for parts, node, _, _, _ in nodes:
            occurrences = f'(PCOCCURRENCE (pcpath_site ++ {raw.path((field,) + parts)}) ({node})) :: ({occurrences})'
        site_class = expression if side == 'class' else 'expression_class'
        site_method = expression if side == 'method' else 'expression_method'
        site = f'NExprStaticCall ({site_class}) ({site_method}) (SEQUENCE ([NVariadicPlaceholder metadata_placeholder])) metadata_site'
        occurrences = f'(PCOCCURRENCE pcpath_site ({site})) :: ({occurrences})'
        path, origin = f'(pcpath_site ++ [PCFIELD {field}])', 'porigin_tree_root_' + side
        state, code, value = 'S_boolean_folded_' + side, 'pcode_boolean_folded_' + side, payload(value)
        result += [f'$code_at(S.CODE,n_unit) = ({code})',
                   f'{state} = ' + raw.source_state(occurrences) + f'[.CODE = [{code}[.EXPRESSIONS = (CODEEXPR {path} 1 true) :: {code}.EXPRESSIONS]]]' +
                   f'[.POOLS = [{{UNIT n_unit,CONSTANTS ([PCONSTANT {path} (PSTRING ({value}))])}}]]',
                   '~' + witness(expression),
                   f'$property_magic_cv_raw_string_tree({state}.SOURCES,{origin},{expression}) = ({value})',
                   prior.certificate(state + '.SOURCES', origin, expression) + f' = ({value})',
                   certificate(state + '.SOURCES', origin, expression) + f' = ({value})',
                   f'$compiled_read({state},{origin}) = (PSTRING ({value}))', raw.selector(side, state, expression)]
    return result


CASES = {}
for index, row in enumerate(ROWS):
    CASES[row['id'] + '-roots'] = dict(prior.CASES[prior.ROWS[index]['id'] + '-root-class'], source=row['source'], checks=roots(index))
base = dict(CASES[ROWS[0]['id'] + '-roots'])
for suffix, checks in (('values', values()), ('domain', domain()), ('source', source_guards()),
                       ('pools', pools()), ('authority-class', authority('class')),
                       ('authority-method', authority('method')), ('frontier-folded', frontier_and_folded())):
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
