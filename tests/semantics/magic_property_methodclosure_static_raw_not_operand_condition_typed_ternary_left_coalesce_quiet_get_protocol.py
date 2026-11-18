#!/usr/bin/env python3
"""Check exact quiet NOT tags in reached typed selector source positions."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_ternary_condition_typed_ternary_left_coalesce_quiet_get_protocol as prior

source_tree, renderer = prior.source_tree, prior.renderer
CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_not_operand_condition_typed_ternary_left_coalesce_quiet_get_cases.json')
ROWS = json.loads(CATALOGUE.read_bytes())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
string = prior.string


def checks(index):
    result = prior.checks(index)[:25]
    sites = ([
        ('class', (1, 0, 0), True, 'PBOOL true'),
        ('class', (1, 1, 0, 0), False, 'PBOOL false'),
        ('class', (1, 1, 1, 0), False, 'PSTRING eps'),
        ('method', (1, 0, 0), True, 'PINT 0'),
    ] if index == 0 else [
        ('class', (1, 1, 0, 0, 2), False, 'PBOOL false'),
        ('class', (1, 1, 1, 0, 0, 2, 1), False, string('01')),
        ('method', (1, 0, 0, 0, 0, 0, 0), False, string('10')),
        ('method', (1, 1, 0, 0, 0, 2, 1), False, 'PINT 0'),
    ])
    for number, (side, relative, truth, selected) in enumerate(sites):
        root = 'porigin_class' if side == 'class' else 'porigin_name'
        site, node = f'porigin_not_site_{number}', f'expression_not_site_{number}'
        origin, condition = f'porigin_not_condition_{number}', f'expression_not_condition_{number}'
        child_origin, child = f'porigin_not_condition_child_{number}', f'expression_not_condition_child_{number}'
        value, inner, echo = ('PBOOL true', 'PBOOL false', '1') if truth else ('PBOOL false', 'PBOOL true', '')
        result += [
            f'$origin_child(({root}),{source_tree.path(relative)}) = ({site})',
            f'$origin_node(S.SOURCES,{site}) = ({node})',
            f'{node} = NExprTernary {condition} expression_not_true_{number} expression_not_false_{number} metadata_not_site_{number}',
            f'$origin_child(({site}),[PCFIELD 0]) = ({origin})',
            f'$origin_node(S.SOURCES,{origin}) = ({condition})',
            f'{condition} = NExprBooleanNot {child} metadata_not_condition_{number}',
            f'$origin_child(({origin}),[PCFIELD 0]) = ({child_origin})',
            f'$origin_node(S.SOURCES,{child_origin}) = ({child})',
            f'{child} = NExprBooleanNot expression_not_grandchild_{number} metadata_not_child_{number}',
            f'$property_magic_cv_raw_ternary_boolean_not_concat_left_coalesce_tree(S.SOURCES,{origin},{condition}) = eps',
            f'$property_magic_cv_raw_typed_ternary_operand_value(S.SOURCES,{child_origin},{child}) = ({inner})',
            f'$property_magic_cv_raw_typed_ternary_operand_value(S.SOURCES,{origin},{condition}) = ({value})',
            f'$property_magic_cv_raw_typed_ternary_full_condition_bytes(S.SOURCES,{origin},{condition}) = ($ptascii("{echo}"))',
            f'$property_magic_cv_raw_typed_ternary_left_value(S.SOURCES,{site},{node}) = ({selected})']
        for cut, suffix in enumerate(((), (0,))):
            path = 'pcpath_site ++ ' + source_tree.path(((0 if side == 'class' else 1),) + relative + (0,) + suffix)
            state = f'S_not_condition_missing_{number}_{cut}'
            result += [f'{state} = S[.SOURCES = [pcunit[.OCCURRENCES = $fqn_keyword_without(pcunit.OCCURRENCES,{path})]]]',
                       f'$property_magic_cv_raw_typed_ternary_full_condition_bytes({state}.SOURCES,{origin},{condition}) = eps',
                       f'$property_magic_cv_raw_typed_ternary_left_value({state}.SOURCES,{site},{node}) = eps']
    if index == 0:
        for number, (side, relative, child_value, value) in enumerate([
            ('class', (1, 0, 0, 1), 'PBOOL false', 'PBOOL true'),
            ('class', (1, 1, 0, 0, 2), string('10'), 'PBOOL false'),
            ('method', (1, 1, 1, 1, 0, 0, 0), 'PBOOL false', 'PBOOL true'),
            ('method', (1, 1, 1, 1, 1, 0, 0, 0, 2), string('10'), 'PBOOL false'),
        ]):
            root = 'porigin_class' if side == 'class' else 'porigin_name'
            origin, node = f'porigin_not_operand_{number}', f'expression_not_operand_{number}'
            child_origin, child = f'porigin_not_operand_child_{number}', f'expression_not_operand_child_{number}'
            result += [f'$origin_child(({root}),{source_tree.path(relative)}) = ({origin})',
                       f'$origin_node(S.SOURCES,{origin}) = ({node})',
                       f'{node} = NExprBooleanNot {child} metadata_not_operand_{number}',
                       f'$property_magic_cv_raw_ternary_boolean_not_concat_left_coalesce_tree(S.SOURCES,{origin},{node}) = eps',
                       f'$origin_child(({origin}),[PCFIELD 0]) = ({child_origin})',
                       f'$property_magic_cv_raw_typed_ternary_operand_value(S.SOURCES,{child_origin},{child}) = ({child_value})',
                       f'$property_magic_cv_raw_typed_ternary_operand_value(S.SOURCES,{origin},{node}) = ({value})']
    result += ['S_not_root_pool = S[.POOLS = [{UNIT n_site,CONSTANTS ([PCONSTANT (pcpath_site ++ [PCFIELD 0]) (PSTRING ptbytes_class)])}]]',
               '$property_magic_cv_emitted_typed_ternary_left_coalesce_concat_value(S_not_root_pool,porigin_class,expression_class) = eps',
               '~' + source_tree.selector('class', 'S_not_root_pool')]
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
