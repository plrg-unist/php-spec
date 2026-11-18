#!/usr/bin/env python3
"""Check exact COALESCE operand tags in reached quiet Get source states."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_nested_operand_typed_ternary_left_coalesce_quiet_get_protocol as prior

source_tree, renderer = prior.source_tree, prior.renderer
CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_coalesce_operand_typed_ternary_left_coalesce_quiet_get_cases.json')
ROWS = json.loads(CATALOGUE.read_bytes())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
string = prior.string


def checks(index):
    result = prior.checks(index)[:25]
    sites = ([
        ('class', (1, 0), True, 'PNULL', '1', {1: 'PNULL', 2: 'PBOOL false'}),
        ('class', (1, 1, 0), True, 'PBOOL false', '', {1: 'PBOOL false'}),
        ('class', (1, 1, 1), True, 'PSTRING eps', '', {1: 'PSTRING eps'}),
        ('method', (1, 0), True, 'PINT 0', '0', {2: 'PINT 0'}),
        ('method', (1, 1, 1, 1, 0), False, string('1'), '1', {0: string('1'), 2: string('BAD_SHORT')}),
        ('method', (1, 1, 1, 1, 1, 0, 0), False, string('0'), '0', {0: 'PBOOL false', 2: string('0')}),
    ] if index == 0 else [
        ('class', (1, 0), False, 'PNULL', '', {2: 'PNULL'}),
        ('class', (1, 1, 0), False, 'PBOOL false', '', {0: 'PBOOL false'}),
        ('class', (1, 1, 1, 0), False, string('01'), '01', {0: string('0'), 2: string('01')}),
        ('class', (1, 1, 1, 1, 0), False, string('1'), '1', {0: string('1'), 2: string('BAD_SHORT')}),
        ('method', (1, 0, 0, 0), False, string('10'), '10', {0: string('10'), 2: string('BAD_SHORT')}),
        ('method', (1, 1, 0, 0), False, 'PINT 0', '0', {2: 'PINT 0'}),
    ])
    for number, (side, relative, present, value, echo, fields) in enumerate(sites):
        root = 'porigin_class' if side == 'class' else 'porigin_name'
        coal, left = f'porigin_coal_outer_{number}', f'porigin_coal_ternary_{number}'
        node, expression = f'expression_coal_outer_{number}', f'expression_coal_ternary_{number}'
        operands = {field: f'expression_coal_operand_{number}_{field}' for field in (0, 1, 2)}
        outer = f'NExprTernary {operands[0]} ' + (operands[1] if present else 'ABSENT') + f' {operands[2]} metadata_coal_ternary_{number}'
        result += [
            f'$origin_child(({root}),{source_tree.path(relative)}) = ({coal})',
            f'$origin_node(S.SOURCES,{coal}) = ({node})',
            f'{node} = NExprBinaryOpCoalesce {expression} expression_coal_rhs_{number} metadata_coal_outer_{number}',
            f'$origin_child(({coal}),[PCFIELD 0]) = ({left})',
            f'$origin_node(S.SOURCES,{left}) = ({expression})', f'{expression} = {outer}',
            f'$property_magic_cv_raw_typed_ternary_left_value(S.SOURCES,{left},{expression}) = ({value})',
            f'$property_magic_cv_raw_typed_ternary_operand_value(S.SOURCES,{left},{expression}) = ({value})',
            f'$property_magic_cv_raw_typed_ternary_left_coalesce_tree(S.SOURCES,{coal},{node}) = ($ptascii("{echo}"))']
        if not present:
            result += [f'$origin_child(({left}),[PCFIELD 1]) = (porigin_coal_absent_{number})',
                       f'$origin_node(S.SOURCES,porigin_coal_absent_{number}) = eps']
        for field, selected in fields.items():
            origin = f'porigin_coal_operand_{number}_{field}'
            result += [
                f'$origin_child(({left}),[PCFIELD {field}]) = ({origin})',
                f'$origin_node(S.SOURCES,{origin}) = ({operands[field]})',
                f'{operands[field]} = NExprBinaryOpCoalesce expression_coal_left_{number}_{field} expression_coal_right_{number}_{field} metadata_coal_{number}_{field}',
                f'$property_magic_cv_raw_typed_ternary_operand_value(S.SOURCES,{origin},{operands[field]}) = ({selected})',
                f'$property_magic_cv_raw_primitive_coalesce_left(S.SOURCES,{origin},{operands[field]}) = eps']
            for cut, suffix in enumerate(((), (0,), (1,))):
                path = 'pcpath_site ++ ' + source_tree.path(((0 if side == 'class' else 1),) + relative + (0, field) + suffix)
                state = f'S_coal_missing_{number}_{field}_{cut}'
                result += [f'{state} = S[.SOURCES = [pcunit[.OCCURRENCES = $fqn_keyword_without(pcunit.OCCURRENCES,{path})]]]',
                           f'$property_magic_cv_raw_typed_ternary_left_value({state}.SOURCES,{left},{expression}) = eps']
    result += ['S_coal_root_pool = S[.POOLS = [{UNIT n_site,CONSTANTS ([PCONSTANT (pcpath_site ++ [PCFIELD 0]) (PSTRING ptbytes_class)])}]]',
               '$property_magic_cv_emitted_typed_ternary_left_coalesce_concat_value(S_coal_root_pool,porigin_class,expression_class) = eps',
               '~' + source_tree.selector('class', 'S_coal_root_pool')]
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
