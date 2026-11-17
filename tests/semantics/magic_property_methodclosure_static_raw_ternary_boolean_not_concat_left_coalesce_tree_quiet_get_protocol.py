#!/usr/bin/env python3
"""Check full/shorthand ternary selection over actual quiet selector source states."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests/semantics"))
import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_boolean_not_concat_left_coalesce_tree_quiet_get_protocol as prior

source_tree = prior.source_tree
renderer = prior.renderer
CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_ternary_boolean_not_concat_left_coalesce_tree_quiet_get_cases.json')
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
            f'$property_magic_cv_raw_ternary_boolean_not_concat_left_coalesce_tree(S.SOURCES,{origin},{expression}) = (ptbytes_{side})',
            expected,
            f'$property_magic_cv_coalesce_under_ternary({expression},false)',
            f'$property_magic_cv_raw_boolean_not_concat_left_coalesce_tree(S.SOURCES,{origin},{expression}) = eps',
            f'$compiled_read(S,{origin}) = eps',
            f'$pool_value(S.POOLS,{origin}) = eps',
            f'$property_magic_cv_emitted_ternary_boolean_not_concat_left_coalesce_concat_value(S,{origin},{expression}) = (PSTRING ptbytes_{side})',
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
    ternaries = ([
        ('class', (1, 1, 0), '0', 'BAD_CLASS', '1', '1', None),
        ('class', (1, 1, 1, 0, 0), '', None, '', '', None),
        ('method', (1, 0, 1, 0), '1', '', 'BAD_METHOD', '', 'PNULL'),
        ('method', (1, 1, 1, 1), '', None, '1', '1', None),
    ] if index == 0 else [
        ('class', (1, 0), '01', None, 'BAD_CLASS', '01', None),
        ('class', (1, 1, 0), '00', '1', 'BAD_CLASS', '1', None),
        ('method', (1, 0), '1', None, 'BAD_METHOD', '1', None),
        ('method', (1, 1, 0), '1', '', 'BAD_METHOD', '', 'PBOOL false'),
    ])
    for number, (side, relative, cond_value, true_value, false_value, value, true_tag) in enumerate(ternaries):
        origin = 'porigin_class' if side == 'class' else 'porigin_name'
        expression = 'expression_' + side
        selected = f'porigin_ternary_{number}'
        cond, yes, no = (f'expression_cond_{number}', f'expression_true_{number}', f'expression_false_{number}')
        metadata = f'metadata_ternary_{number}'
        node = f'NExprTernary {cond} ' + ('ABSENT' if true_value is None else yes) + f' {no} {metadata}'
        child_cond, child_true, child_false = (f'porigin_cond_{number}', f'porigin_true_{number}', f'porigin_false_{number}')
        result += [
            f'$origin_child(({origin}),{source_tree.path(relative)}) = ({selected})',
            f'$origin_node(S.SOURCES,{selected}) = ({node})',
            f'$origin_child(({selected}),[PCFIELD 0]) = ({child_cond})',
            f'$origin_child(({selected}),[PCFIELD 2]) = ({child_false})',
            f'$property_magic_cv_raw_ternary_boolean_not_concat_left_coalesce_tree(S.SOURCES,{child_cond},{cond}) = ($ptascii("{cond_value}"))',
            f'$property_magic_cv_raw_ternary_boolean_not_concat_left_coalesce_tree(S.SOURCES,{child_false},{no}) = ($ptascii("{false_value}"))',
            f'$property_magic_cv_raw_ternary_boolean_not_concat_left_coalesce_tree(S.SOURCES,{selected},{node}) = ($ptascii("{value}"))',
            f'$property_magic_cv_raw_boolean_not_concat_left_coalesce_tree(S.SOURCES,{selected},{node}) = eps',
        ]
        result += [f'$origin_child(({selected}),[PCFIELD 1]) = ({child_true})']
        if true_value is None:
            path = 'pcpath_site ++ ' + source_tree.path(((0 if side == 'class' else 1),) + relative + (1,))
            result += [f'$origin_node(S.SOURCES,{child_true}) = eps',
                       f'$compiled_read(S,{child_true}) = eps',
                       f'$pool_value(S.POOLS,{child_true}) = eps',
                       f'$code_expression(pcode_selectors.EXPRESSIONS,{path}) = eps']
        else:
            result += [f'$origin_node(S.SOURCES,{child_true}) = ({yes})',
                       f'$property_magic_cv_raw_ternary_boolean_not_concat_left_coalesce_tree(S.SOURCES,{child_true},{yes}) = ($ptascii("{true_value}"))']
            if true_tag:
                result += [f'$compiled_read(S,{child_true}) = ({true_tag})',
                           f'$pool_value(S.POOLS,{child_true}) = ({true_tag})']
        suffixes = [(), (0,), (2,)] + ([(1,)] if true_value is not None else [])
        if true_tag:
            suffixes.append((1, 0))
        for cut, suffix in enumerate(suffixes):
            path = 'pcpath_site ++ ' + source_tree.path(((0 if side == 'class' else 1),) + relative + suffix)
            state = f'S_ternary_source_{number}_{cut}'
            result += [f'{state} = S[.SOURCES = [pcunit[.OCCURRENCES = $fqn_keyword_without(pcunit.OCCURRENCES,{path})]]]',
                       f'$property_magic_cv_raw_ternary_boolean_not_concat_left_coalesce_tree({state}.SOURCES,{origin},{expression}) = eps']
    for field, side in enumerate(('class', 'method')):
        origin = 'porigin_class' if side == 'class' else 'porigin_name'
        expression = 'expression_' + side
        path = f'pcpath_site ++ [PCFIELD {field}]'
        for label, value in [('exact', f'PSTRING ptbytes_{side}'), ('type', 'PBOOL false'),
                             ('case', f'PSTRING $ptlc(ptbytes_{side})')]:
            state = f'S_concat_pool_{side}_{label}'
            result += [f'{state} = S[.POOLS = [{{UNIT n_site,CONSTANTS ([PCONSTANT ({path}) ({value})])}}]]',
                       f'$property_magic_cv_emitted_ternary_boolean_not_concat_left_coalesce_concat_value({state},{origin},{expression}) = eps',
                       '~' + source_tree.selector(side, state)]
        for label, code in [
                ('constant', f'pcode_selectors[.EXPRESSIONS = (CODEEXPR ({path}) z_{side} true) :: pcode_selectors.EXPRESSIONS]'),
                ('zero', f'pcode_selectors[.EXPRESSIONS = (CODEEXPR ({path}) 0 false) :: pcode_selectors.EXPRESSIONS]'),
                ('negative', f'pcode_selectors[.EXPRESSIONS = (CODEEXPR ({path}) $(-1) false) :: pcode_selectors.EXPRESSIONS]'),
                ('redirect', f'pcode_selectors[.REDIRECTS = (CODEREDIRECT ({path}) ({path} ++ [PCFIELD 0]) false) :: pcode_selectors.REDIRECTS]'),
                ('effect', f'pcode_selectors[.EXPRESSIONS = (CODEEFFECT ({path})) :: pcode_selectors.EXPRESSIONS]')]:
            state = f'S_concat_code_{side}_{label}'
            result += [f'{state} = S[.CODE = [{code}]]',
                       f'$property_magic_cv_emitted_ternary_boolean_not_concat_left_coalesce_concat_value({state},{origin},{expression}) = eps',
                       '~' + source_tree.selector(side, state)]
    result += ['S_concat_no_code = S[.CODE = eps]',
               '$property_magic_cv_emitted_ternary_boolean_not_concat_left_coalesce_concat_value(S_concat_no_code,porigin_class,expression_class) = eps',
               '$property_magic_cv_emitted_ternary_boolean_not_concat_left_coalesce_concat_value(S_concat_no_code,porigin_name,expression_method) = eps']
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
