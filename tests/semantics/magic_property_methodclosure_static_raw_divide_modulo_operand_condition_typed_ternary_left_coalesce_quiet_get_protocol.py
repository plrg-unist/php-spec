#!/usr/bin/env python3
"""Check quiet fitting Divide/Modulo at reached static USER selector sources."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_multiply_operand_condition_typed_ternary_left_coalesce_quiet_get_protocol as prior

source_tree, renderer = prior.source_tree, prior.renderer
CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_divide_modulo_operand_condition_typed_ternary_left_coalesce_quiet_get_cases.json')
ROWS = json.loads(CATALOGUE.read_bytes())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
string, pint = prior.string, prior.pint


def checks(index):
    result = prior.checks(index)[:25]
    sites = ([
        ('class', (1, 0, 0), True, 'PINT 1'),
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
        site, node = f'porigin_quotrem_site_{number}', f'expression_quotrem_site_{number}'
        origin, condition = f'porigin_quotrem_condition_{number}', f'expression_quotrem_condition_{number}'
        left_origin, left = f'porigin_quotrem_left_{number}', f'expression_quotrem_left_{number}'
        right_origin, right = f'porigin_quotrem_right_{number}', f'expression_quotrem_right_{number}'
        integer = -1 if truth else 0
        kind, lv, rv, li, ri = [
            ('Div', pint(integer), 'PBOOL true', integer, 1),
            ('Mod', pint(integer), string('  +2 '), integer, 2),
            ('Div', 'PINT 0', string(' -9223372036854775808'), 0, -9223372036854775808),
            ('Mod', pint(integer), pint(-3), integer, -3),
        ][number]
        helper = (f'$num_div(NINT {pint(li).removeprefix("PINT ")},NINT {pint(ri).removeprefix("PINT ")}) = NUM (NINT {pint(integer).removeprefix("PINT ")})' if kind == 'Div' else f'$long_mod({pint(li).removeprefix("PINT ")},{pint(ri).removeprefix("PINT ")}) = IRESULT {pint(integer).removeprefix("PINT ")}')
        result += [
            f'$origin_child(({root}),{source_tree.path(relative)}) = ({site})',
            f'$origin_node(S.SOURCES,{site}) = ({node})',
            f'{node} = NExprTernary {condition} expression_quotrem_true_{number} expression_quotrem_false_{number} metadata_quotrem_site_{number}',
            f'$origin_child(({site}),[PCFIELD 0]) = ({origin})',
            f'$origin_node(S.SOURCES,{origin}) = ({condition})',
            f'{condition} = NExprBinaryOp{kind} {left} {right} metadata_quotrem_condition_{number}',
            f'$origin_child(({origin}),[PCFIELD 0]) = ({left_origin})',
            f'$origin_child(({origin}),[PCFIELD 1]) = ({right_origin})',
            f'$origin_node(S.SOURCES,{left_origin}) = ({left})',
            f'$origin_node(S.SOURCES,{right_origin}) = ({right})',
            f'$property_magic_cv_raw_ternary_boolean_not_concat_left_coalesce_tree(S.SOURCES,{origin},{condition}) = eps',
            f'$property_magic_cv_raw_typed_ternary_operand_value(S.SOURCES,{left_origin},{left}) = ({lv})',
            f'$property_magic_cv_raw_typed_ternary_operand_value(S.SOURCES,{right_origin},{right}) = ({rv})',
            f'$coerce_number({lv}) = COERCED (NINT {pint(li).removeprefix("PINT ")}) false',
            f'$coerce_number({rv}) = COERCED (NINT {pint(ri).removeprefix("PINT ")}) false',
            helper,
            f'$property_magic_cv_raw_typed_ternary_operand_value(S.SOURCES,{origin},{condition}) = ({pint(integer)})',
            f'$property_magic_cv_raw_typed_ternary_full_condition_bytes(S.SOURCES,{origin},{condition}) = ($ptascii("{integer}"))',
            f'$property_magic_cv_raw_typed_ternary_left_value(S.SOURCES,{site},{node}) = ({selected})',
        ]
        for cut, suffix in enumerate(((), (0,), (1,))):
            path = 'pcpath_site ++ ' + source_tree.path(((0 if side == 'class' else 1),) + relative + (0,) + suffix)
            state = f'S_quotrem_condition_missing_{number}_{cut}'
            result += [f'{state} = S[.SOURCES = [pcunit[.OCCURRENCES = $fqn_keyword_without(pcunit.OCCURRENCES,{path})]]]',
                       f'$property_magic_cv_raw_typed_ternary_full_condition_bytes({state}.SOURCES,{origin},{condition}) = eps',
                       f'$property_magic_cv_raw_typed_ternary_left_value({state}.SOURCES,{site},{node}) = eps']
    if index == 0:
        for number, (side, relative, lv, rv, integer) in enumerate([
            ('class', (1, 0, 0, 1), 'PINT 1', string('2'), 1),
            ('class', (1, 1, 0, 0, 2, 0), pint(-10), string('2'), -5),
            ('method', (1, 1, 1, 1, 0, 0, 0), 'PINT 1', string('2'), 1),
            ('method', (1, 1, 1, 1, 1, 0, 0, 0, 2, 0), pint(-10), string('2'), -5),
        ]):
            root = 'porigin_class' if side == 'class' else 'porigin_name'
            origin, node = f'porigin_quotrem_operand_{number}', f'expression_quotrem_operand_{number}'
            lo, left = f'porigin_quotrem_operand_left_{number}', f'expression_quotrem_operand_left_{number}'
            ro, right = f'porigin_quotrem_operand_right_{number}', f'expression_quotrem_operand_right_{number}'
            li, ri = (1, 2) if integer == 1 else (-10, 2)
            kind = 'Mod' if integer == 1 else 'Div'
            helper = (f'$num_div(NINT {pint(li).removeprefix("PINT ")},NINT {pint(ri).removeprefix("PINT ")}) = NUM (NINT {pint(integer).removeprefix("PINT ")})' if kind == 'Div' else f'$long_mod({pint(li).removeprefix("PINT ")},{pint(ri).removeprefix("PINT ")}) = IRESULT {pint(integer).removeprefix("PINT ")}')
            result += [f'$origin_child(({root}),{source_tree.path(relative)}) = ({origin})',
                       f'$origin_node(S.SOURCES,{origin}) = ({node})',
                       f'{node} = NExprBinaryOp{kind} {left} {right} metadata_quotrem_operand_{number}',
                       f'$origin_child(({origin}),[PCFIELD 0]) = ({lo})',
                       f'$origin_child(({origin}),[PCFIELD 1]) = ({ro})',
                       f'$origin_node(S.SOURCES,{lo}) = ({left})',
                       f'$origin_node(S.SOURCES,{ro}) = ({right})',
                       f'$property_magic_cv_raw_typed_ternary_operand_value(S.SOURCES,{lo},{left}) = ({lv})',
                       f'$property_magic_cv_raw_typed_ternary_operand_value(S.SOURCES,{ro},{right}) = ({rv})',
                       f'$coerce_number({lv}) = COERCED (NINT {pint(li).removeprefix("PINT ")}) false',
                       f'$coerce_number({rv}) = COERCED (NINT {pint(ri).removeprefix("PINT ")}) false',
                       helper,
                       f'$property_magic_cv_raw_typed_ternary_operand_value(S.SOURCES,{origin},{node}) = ({pint(integer)})']
    result += ['S_quotrem_root_pool = S[.POOLS = [{UNIT n_site,CONSTANTS ([PCONSTANT (pcpath_site ++ [PCFIELD 0]) (PSTRING ptbytes_class)])}]]',
               '$property_magic_cv_emitted_typed_ternary_left_coalesce_concat_value(S_quotrem_root_pool,porigin_class,expression_class) = eps',
               '~' + source_tree.selector('class', 'S_quotrem_root_pool')]
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
