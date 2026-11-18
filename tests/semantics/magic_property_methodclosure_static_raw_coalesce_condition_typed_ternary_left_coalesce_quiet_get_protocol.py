#!/usr/bin/env python3
"""Check typed COALESCE FULL conditions at reached quiet Get source states."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_coalesce_operand_typed_ternary_left_coalesce_quiet_get_protocol as prior

source_tree, renderer = prior.source_tree, prior.renderer
CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_coalesce_condition_typed_ternary_left_coalesce_quiet_get_cases.json')
ROWS = json.loads(CATALOGUE.read_bytes())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
string = prior.string


def checks(index):
    result = prior.checks(index)[:25]
    sites = ([
        ('class', (1, 0, 0), 'PBOOL true', '1', 'PNULL'),
        ('class', (1, 1, 0, 0), 'PBOOL false', '', 'PBOOL false'),
        ('class', (1, 1, 1, 0), 'PSTRING eps', '', 'PSTRING eps'),
        ('method', (1, 0, 0), string('10'), '10', 'PINT 0'),
    ] if index == 0 else [
        ('class', (1, 1, 0, 0, 2), string('0'), '0', 'PBOOL false'),
        ('class', (1, 1, 1, 0, 0, 2, 1), 'PINT 0', '0', string('01')),
        ('method', (1, 0, 0, 0, 0, 0, 0), 'PBOOL false', '', string('10')),
        ('method', (1, 1, 0, 0, 0, 2, 1), 'PNULL', '', 'PINT 0'),
    ])
    for number, (side, relative, condition, echo, selected) in enumerate(sites):
        root = 'porigin_class' if side == 'class' else 'porigin_name'
        origin, node = f'porigin_full_condition_site_{number}', f'expression_full_condition_site_{number}'
        cond_origin, cond = f'porigin_full_condition_{number}', f'expression_full_condition_{number}'
        result += [
            f'$origin_child(({root}),{source_tree.path(relative)}) = ({origin})',
            f'$origin_node(S.SOURCES,{origin}) = ({node})',
            f'{node} = NExprTernary {cond} expression_full_true_{number} expression_full_false_{number} metadata_full_site_{number}',
            f'$origin_child(({origin}),[PCFIELD 0]) = ({cond_origin})',
            f'$origin_node(S.SOURCES,{cond_origin}) = ({cond})',
            f'{cond} = NExprBinaryOpCoalesce expression_condition_left_{number} expression_condition_right_{number} metadata_condition_{number}',
            f'$property_magic_cv_raw_ternary_boolean_not_concat_left_coalesce_tree(S.SOURCES,{cond_origin},{cond}) = eps',
            f'$property_magic_cv_raw_typed_ternary_operand_value(S.SOURCES,{cond_origin},{cond}) = ({condition})',
            f'$property_magic_cv_raw_typed_ternary_full_condition_bytes(S.SOURCES,{cond_origin},{cond}) = ($ptascii("{echo}"))',
            f'$property_magic_cv_raw_typed_ternary_left_value(S.SOURCES,{origin},{node}) = ({selected})',
            f'$property_magic_cv_raw_typed_ternary_operand_value(S.SOURCES,{origin},{node}) = ({selected})']
        for cut, suffix in enumerate(((), (0,), (1,))):
            path = 'pcpath_site ++ ' + source_tree.path(((0 if side == 'class' else 1),) + relative + (0,) + suffix)
            state = f'S_full_condition_missing_{number}_{cut}'
            result += [f'{state} = S[.SOURCES = [pcunit[.OCCURRENCES = $fqn_keyword_without(pcunit.OCCURRENCES,{path})]]]',
                       f'$property_magic_cv_raw_typed_ternary_full_condition_bytes({state}.SOURCES,{cond_origin},{cond}) = eps',
                       f'$property_magic_cv_raw_typed_ternary_left_value({state}.SOURCES,{origin},{node}) = eps']
    result += ['S_full_condition_root_pool = S[.POOLS = [{UNIT n_site,CONSTANTS ([PCONSTANT (pcpath_site ++ [PCFIELD 0]) (PSTRING ptbytes_class)])}]]',
               '$property_magic_cv_emitted_typed_ternary_left_coalesce_concat_value(S_full_condition_root_pool,porigin_class,expression_class) = eps',
               '~' + source_tree.selector('class', 'S_full_condition_root_pool')]
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
