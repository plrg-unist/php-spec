#!/usr/bin/env python3
"""Check typed ternary-left coalesce using reached quiet Get source states."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_ternary_boolean_not_concat_left_coalesce_tree_quiet_get_protocol as prior

source_tree, renderer = prior.source_tree, prior.renderer
CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_typed_ternary_left_coalesce_quiet_get_cases.json')
ROWS = json.loads(CATALOGUE.read_bytes())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def checks(index):
    result = prior.checks(index)[:18]
    for side, origin, expression, expected in (
            ('class', 'porigin_class', 'expression_class',
             '$ptlc($ppcall_literal_name(ptbytes_class)) = $ptlc(pclassdesc_requested.NAME)'),
            ('method', 'porigin_name', 'expression_method',
             '$ptlc(ptbytes_method) = $ptlc(pmethoddesc_method.NAME)')):
        result += [
            f'$property_magic_cv_ternary_left_coalesce({expression})',
            f'$property_magic_cv_raw_typed_ternary_left_coalesce_tree(S.SOURCES,{origin},{expression}) = (ptbytes_{side})',
            expected,
            f'$property_magic_cv_raw_ternary_boolean_not_concat_left_coalesce_tree(S.SOURCES,{origin},{expression}) = eps',
            f'$compiled_read(S,{origin}) = eps', f'$pool_value(S.POOLS,{origin}) = eps',
            f'$property_magic_cv_emitted_typed_ternary_left_coalesce_concat_value(S,{origin},{expression}) = (PSTRING ptbytes_{side})',
            source_tree.selector(side)]
    result += ['$code_at(S.CODE,n_site) = (pcode_selectors)',
               '$code_expression(pcode_selectors.EXPRESSIONS,pcpath_site ++ [PCFIELD 0]) = ((z_class,false))',
               '$code_expression(pcode_selectors.EXPRESSIONS,pcpath_site ++ [PCFIELD 1]) = ((z_method,false))',
               r'$(z_class > 0) /\ $(z_method > 0)',
               '$property_magic_cv_static_methodclosure(S,n_closure)',
               'S_trim = S[.POOLS = [{UNIT n_site,CONSTANTS eps}]]',
               source_tree.selector('class', 'S_trim'), source_tree.selector('method', 'S_trim')]
    # Paths and tags bind the original-source COALESCE_RESULT observations.
    sites = ([
        ('class', (1, 0), 'PNULL', '1', True, (0, 1)),
        ('class', (1, 1, 0), 'PBOOL false', '', True, (0, 1)),
        ('class', (1, 1, 1), 'PSTRING eps', '', True, (0,)),
        ('method', (1, 0), 'PINT 0', '0', True, (0,)),
        ('method', (1, 1, 1, 1, 0), 'PSTRING $ptascii("1")', '1', False, (2,)),
        ('method', (1, 1, 1, 1, 1, 0, 0), 'PSTRING $ptascii("0")', '0', True, (0, 2)),
    ] if index == 0 else [
        ('class', (1, 0), 'PNULL', '', False, (0, 2)),
        ('class', (1, 1, 0), 'PBOOL false', '', False, (0, 2)),
        ('class', (1, 1, 1, 0), 'PSTRING $ptascii("01")', '01', False, (2,)),
        ('class', (1, 1, 1, 1, 0), 'PSTRING $ptascii("1")', '1', False, (0,)),
        ('method', (1, 0), 'PBOOL true', '1', False, (0, 2)),
        ('method', (1, 1, 0, 0), 'PINT 0', '0', False, (0,)),
    ])
    for number, (side, relative, value, text, present, names) in enumerate(sites):
        root = 'porigin_class' if side == 'class' else 'porigin_name'
        origin, left = f'porigin_typed_coalesce_{number}', f'porigin_typed_left_{number}'
        node, expression = f'expression_typed_coalesce_{number}', f'expression_typed_left_{number}'
        result += [
            f'$origin_child(({root}),{source_tree.path(relative)}) = ({origin})',
            f'$origin_node(S.SOURCES,{origin}) = ({node})',
            f'{node} = NExprBinaryOpCoalesce {expression} expression_rhs_{number} metadata_coalesce_{number}',
            f'$origin_child(({origin}),[PCFIELD 0]) = ({left})',
            f'$origin_node(S.SOURCES,{left}) = ({expression})',
            f'$property_magic_cv_raw_typed_ternary_left_value(S.SOURCES,{left},{expression}) = ({value})',
            f'$property_magic_cv_raw_typed_ternary_left_coalesce_tree(S.SOURCES,{origin},{node}) = ($ptascii("{text}"))',
            f'$property_magic_cv_raw_ternary_boolean_not_concat_left_coalesce_tree(S.SOURCES,{origin},{node}) = eps']
        suffixes = [(), (0,), (1,), (0, 0), (0, 2)]
        if present:
            suffixes.append((0, 1))
        suffixes += [(0, field, 0) for field in names]
        for cut, suffix in enumerate(suffixes):
            path = 'pcpath_site ++ ' + source_tree.path(((0 if side == 'class' else 1),) + relative + suffix)
            state = f'S_typed_source_{number}_{cut}'
            result += [f'{state} = S[.SOURCES = [pcunit[.OCCURRENCES = $fqn_keyword_without(pcunit.OCCURRENCES,{path})]]]',
                       f'$property_magic_cv_raw_typed_ternary_left_coalesce_tree({state}.SOURCES,{root},expression_{side}) = eps']
    for field, side in enumerate(('class', 'method')):
        origin = 'porigin_class' if side == 'class' else 'porigin_name'
        path = f'pcpath_site ++ [PCFIELD {field}]'
        for label, value in [('exact', f'PSTRING ptbytes_{side}'), ('type', 'PBOOL false'),
                             ('case', f'PSTRING $ptlc(ptbytes_{side})')]:
            state = f'S_typed_pool_{side}_{label}'
            result += [f'{state} = S[.POOLS = [{{UNIT n_site,CONSTANTS ([PCONSTANT ({path}) ({value})])}}]]',
                       f'$property_magic_cv_emitted_typed_ternary_left_coalesce_concat_value({state},{origin},expression_{side}) = eps',
                       '~' + source_tree.selector(side, state)]
        for label, code in [
                ('constant', f'pcode_selectors[.EXPRESSIONS = (CODEEXPR ({path}) z_{side} true) :: pcode_selectors.EXPRESSIONS]'),
                ('zero', f'pcode_selectors[.EXPRESSIONS = (CODEEXPR ({path}) 0 false) :: pcode_selectors.EXPRESSIONS]'),
                ('redirect', f'pcode_selectors[.REDIRECTS = (CODEREDIRECT ({path}) ({path} ++ [PCFIELD 0]) false) :: pcode_selectors.REDIRECTS]'),
                ('effect', f'pcode_selectors[.EXPRESSIONS = (CODEEFFECT ({path})) :: pcode_selectors.EXPRESSIONS]')]:
            state = f'S_typed_code_{side}_{label}'
            result += [f'{state} = S[.CODE = [{code}]]',
                       f'$property_magic_cv_emitted_typed_ternary_left_coalesce_concat_value({state},{origin},expression_{side}) = eps',
                       '~' + source_tree.selector(side, state)]
    return result


CASES = {row['id']: dict(source=row['source'], stage=prior.CASES[row['derived_from']['id']]['stage'],
                        checks=checks(index)) for index, row in enumerate(ROWS)}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    base = source_tree.prior.prior.base
    parents, parent = [], prior
    while hasattr(parent, 'prior'):
        parents.append(parent)
        parent = parent.prior
    parents += [parent, renderer, source_tree, source_tree.prior, source_tree.prior.prior,
                base, base.original, base.inherited, base.inherited.prior,
                base.inherited.prior.prior, base.inherited.prior.prior.prior,
                renderer.renderer]
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, *(entry for parent in parents
                                               for entry in (Path(parent.__file__), parent.CATALOGUE))),
                 runner_flags=('--sl',), fixture_renderer=renderer.render)
