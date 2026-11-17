#!/usr/bin/env python3
"""Check typed primitive-left coalesces against actual quiet Get source states."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_ternary_boolean_not_concat_tree_quiet_get_protocol as prior

source_tree = prior.source_tree
renderer = prior.renderer
CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_primitive_coalesce_tree_quiet_get_cases.json')
ROWS = json.loads(CATALOGUE.read_bytes())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def checks(index):
    result = ['S.RESULT = KNOWN (POBJECT n_closure)',
              'S.OBJECTS[n_closure] = METHODCLOSURE porigin_method porigin_site porigin_requested eps',
              '$class_method_origin(S.CLASSES,porigin_method) = (pmethoddesc_method)'] + prior.TREE[:15]
    for side, origin, expression, expected in (
            ('class', 'porigin_class', 'expression_class',
             '$ptlc($ppcall_literal_name(ptbytes_class)) = $ptlc(pclassdesc_requested.NAME)'),
            ('method', 'porigin_name', 'expression_method',
             '$ptlc(ptbytes_method) = $ptlc(pmethoddesc_method.NAME)')):
        result += [
            f'$property_magic_cv_raw_primitive_coalesce_tree(S.SOURCES,{origin},{expression}) = (ptbytes_{side})',
            expected,
            f'$property_magic_cv_raw_ternary_boolean_not_concat_tree(S.SOURCES,{origin},{expression}) = eps',
            f'$compiled_read(S,{origin}) = eps',
            f'$pool_value(S.POOLS,{origin}) = eps',
            f'$property_magic_cv_emitted_primitive_coalesce_concat_value(S,{origin},{expression}) = (PSTRING ptbytes_{side})',
        ]
    result += ['$code_at(S.CODE,n_site) = (pcode_selectors)',
               '$code_expression(pcode_selectors.EXPRESSIONS,pcpath_site ++ [PCFIELD 0]) = ((z_class,false))',
               '$code_expression(pcode_selectors.EXPRESSIONS,pcpath_site ++ [PCFIELD 1]) = ((z_method,false))',
               r'$(z_class > 0) /\ $(z_method > 0)',
               '$property_magic_cv_static_method_site_selector(S,porigin_site,phpType19_class,porigin_requested,pclassdesc_requested.NAME)',
               '$property_magic_cv_static_method_site_name(S,porigin_site,phpType20_method,pmethoddesc_method.NAME)',
               '$property_magic_cv_static_methodclosure(S,n_closure)',
               'S_trim = S[.POOLS = [{UNIT n_site,CONSTANTS eps}]]',
               '$property_magic_cv_static_method_site_selector(S_trim,porigin_site,phpType19_class,porigin_requested,pclassdesc_requested.NAME)',
               '$property_magic_cv_static_method_site_name(S_trim,porigin_site,phpType20_method,pmethoddesc_method.NAME)']
    primitives = ([('class', (1, 1, 0, 0), 'PNULL'),
                   ('class', (1, 1, 1, 0), 'PSTRING $ptascii("1")'),
                   ('method', (1, 0, 0), 'PINT 0')] if index == 0 else
                  [('class', (0, 1, 0, 0), 'PBOOL false'),
                   ('class', (0, 1, 1, 0), 'PINT 0'),
                   ('class', (1, 1, 0, 0), 'PSTRING eps'),
                   ('method', (1, 0, 0), 'PNULL'),
                   ('method', (1, 1, 0), 'PINT 1')])
    for number, (side, relative, value) in enumerate(primitives):
        origin = 'porigin_class' if side == 'class' else 'porigin_name'
        selected = 'expression_class' if side == 'class' else 'expression_method'
        path = source_tree.path(relative)
        site_path = 'pcpath_site ++ ' + source_tree.path(((0 if side == 'class' else 1),) + relative)
        leaf = f'porigin_primitive_{number}'
        node = f'expression_primitive_{number}'
        state = f'S_primitive_missing_{number}'
        result += [f'$origin_child(({origin}),{path}) = ({leaf})',
                   f'$origin_node(S.SOURCES,{leaf}) = ({node})',
                   f'$property_magic_cv_raw_primitive_coalesce_left(S.SOURCES,{leaf},{node}) = ({value})',
                   f'{state} = S[.SOURCES = [pcunit[.OCCURRENCES = $fqn_keyword_without(pcunit.OCCURRENCES,{site_path})]]]',
                   f'$property_magic_cv_raw_primitive_coalesce_left({state}.SOURCES,{leaf},{node}) = eps',
                   f'$property_magic_cv_raw_primitive_coalesce_tree({state}.SOURCES,{origin},{selected}) = eps',
                   '~' + source_tree.selector(side, state)]
    for field, side in enumerate(('class', 'method')):
        origin = 'porigin_class' if side == 'class' else 'porigin_name'
        expression = 'expression_' + side
        path = f'pcpath_site ++ [PCFIELD {field}]'
        for label, value in [('exact', f'PSTRING ptbytes_{side}'), ('type', 'PBOOL false'),
                             ('case', f'PSTRING $ptlc(ptbytes_{side})')]:
            state = f'S_coalesce_pool_{side}_{label}'
            result += [f'{state} = S[.POOLS = [{{UNIT n_site,CONSTANTS ([PCONSTANT ({path}) ({value})])}}]]',
                       f'$property_magic_cv_emitted_primitive_coalesce_concat_value({state},{origin},{expression}) = eps',
                       '~' + source_tree.selector(side, state)]
        for label, code in [
                ('constant', f'pcode_selectors[.EXPRESSIONS = (CODEEXPR ({path}) z_{side} true) :: pcode_selectors.EXPRESSIONS]'),
                ('zero', f'pcode_selectors[.EXPRESSIONS = (CODEEXPR ({path}) 0 false) :: pcode_selectors.EXPRESSIONS]'),
                ('negative', f'pcode_selectors[.EXPRESSIONS = (CODEEXPR ({path}) $(-1) false) :: pcode_selectors.EXPRESSIONS]'),
                ('redirect', f'pcode_selectors[.REDIRECTS = (CODEREDIRECT ({path}) ({path} ++ [PCFIELD 0]) false) :: pcode_selectors.REDIRECTS]'),
                ('effect', f'pcode_selectors[.EXPRESSIONS = (CODEEFFECT ({path})) :: pcode_selectors.EXPRESSIONS]')]:
            state = f'S_coalesce_code_{side}_{label}'
            result += [f'{state} = S[.CODE = [{code}]]',
                       f'$property_magic_cv_emitted_primitive_coalesce_concat_value({state},{origin},{expression}) = eps',
                       '~' + source_tree.selector(side, state)]
    result += ['S_coalesce_no_code = S[.CODE = eps]',
               '$property_magic_cv_emitted_primitive_coalesce_concat_value(S_coalesce_no_code,porigin_class,expression_class) = eps',
               '$property_magic_cv_emitted_primitive_coalesce_concat_value(S_coalesce_no_code,porigin_name,expression_method) = eps']
    return result


CASES = {row['id']: dict(source=row['source'], stage=prior.CASES[row['derived_from']['id']]['stage'],
                        checks=checks(index)) for index, row in enumerate(ROWS)}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    base = source_tree.prior.prior.base
    parents = []
    parent = prior
    while hasattr(parent, 'prior'):
        parents.append(parent)
        parent = parent.prior
    parents.append(parent)
    parents += [renderer, source_tree, source_tree.prior, source_tree.prior.prior,
                base, base.original, base.inherited, base.inherited.prior,
                base.inherited.prior.prior, base.inherited.prior.prior.prior,
                renderer.renderer]
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, *(entry for parent in parents
                                               for entry in (Path(parent.__file__), parent.CATALOGUE))),
                 runner_flags=('--sl',), fixture_renderer=renderer.render)
