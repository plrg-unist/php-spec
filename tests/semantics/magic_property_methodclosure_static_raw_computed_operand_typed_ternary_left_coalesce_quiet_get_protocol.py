#!/usr/bin/env python3
"""Check constructor-known operands at reached quiet Get source states."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_typed_ternary_left_coalesce_quiet_get_protocol as prior

source_tree, renderer = prior.source_tree, prior.renderer
CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_computed_operand_typed_ternary_left_coalesce_quiet_get_cases.json')
ROWS = json.loads(CATALOGUE.read_bytes())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def string(text):
    return f'PSTRING $ptascii("{text}")'


def checks(index):
    result = prior.checks(index)[:18]
    for side, origin in (('class', 'porigin_class'), ('method', 'porigin_name')):
        result += [
            f'$property_magic_cv_raw_typed_ternary_left_coalesce_tree(S.SOURCES,{origin},expression_{side}) = (ptbytes_{side})',
            f'$property_magic_cv_emitted_typed_ternary_left_coalesce_concat_value(S,{origin},expression_{side}) = (PSTRING ptbytes_{side})',
            source_tree.selector(side)]
    result += ['$property_magic_cv_static_methodclosure(S,n_closure)']
    # Each row binds a reached COALESCE_RESULT to its exact typed ternary value.
    sites = ([
        ('class', (1, 0), 'PBOOL true', 'PNULL', string('BAD_CLASS'), 'PNULL', (2,)),
        ('class', (1, 1, 0), 'PBOOL true', 'PBOOL false', string('BAD_CLASS'), 'PBOOL false', (1,)),
        ('class', (1, 1, 1), 'PBOOL true', 'PSTRING eps', string('BAD_CLASS'), 'PSTRING eps', (1,)),
        ('method', (1, 0), 'PBOOL true', 'PINT 0', 'PBOOL false', 'PINT 0', (2,)),
        ('method', (1, 1, 1, 1, 0), string('1'), None, 'PNULL', string('1'), (0,)),
        ('method', (1, 1, 1, 1, 1, 0, 0), 'PBOOL true', string('0'), 'PNULL', string('0'), (1,)),
    ] if index == 0 else [
        ('class', (1, 0), 'PBOOL false', None, 'PNULL', 'PNULL', (0,)),
        ('class', (1, 1, 0), 'PBOOL false', None, 'PBOOL false', 'PBOOL false', (0, 2)),
        ('class', (1, 1, 1, 0), string('01'), None, 'PNULL', string('01'), (0,)),
        ('class', (1, 1, 1, 1, 0), 'PSTRING eps', None, string('1'), string('1'), (0, 2)),
        ('method', (1, 0), 'PBOOL true', None, 'PNULL', 'PBOOL true', (0,)),
        ('method', (1, 1, 0, 0), 'PBOOL false', None, 'PINT 0', 'PINT 0', (0,)),
    ])
    for number, (side, relative, cond, yes, no, selected, computed) in enumerate(sites):
        root = 'porigin_class' if side == 'class' else 'porigin_name'
        coal, left = f'porigin_computed_coalesce_{number}', f'porigin_computed_left_{number}'
        node, term = f'expression_computed_coalesce_{number}', f'expression_computed_left_{number}'
        names = {field: f'expression_operand_{number}_{field}' for field in (0, 1, 2)}
        ternary = f'NExprTernary {names[0]} ' + ('ABSENT' if yes is None else names[1]) + f' {names[2]} metadata_operand_{number}'
        result += [
            f'$origin_child(({root}),{source_tree.path(relative)}) = ({coal})',
            f'$origin_node(S.SOURCES,{coal}) = ({node})',
            f'{node} = NExprBinaryOpCoalesce {term} expression_computed_rhs_{number} metadata_computed_coalesce_{number}',
            f'$origin_child(({coal}),[PCFIELD 0]) = ({left})',
            f'$origin_node(S.SOURCES,{left}) = ({term})', f'{term} = {ternary}',
            f'$property_magic_cv_raw_typed_ternary_left_value(S.SOURCES,{left},{term}) = ({selected})']
        for field, value in ((0, cond), (1, yes), (2, no)):
            operand = f'porigin_operand_{number}_{field}'
            result += [f'$origin_child(({left}),[PCFIELD {field}]) = ({operand})']
            if value is None:
                result += [f'$origin_node(S.SOURCES,{operand}) = eps']
                continue
            result += [f'$origin_node(S.SOURCES,{operand}) = ({names[field]})',
                       f'$property_magic_cv_raw_typed_ternary_operand_value(S.SOURCES,{operand},{names[field]}) = ({value})']
            if field not in computed:
                result += [f'$property_magic_cv_raw_primitive_coalesce_left(S.SOURCES,{operand},{names[field]}) = ({value})']
                continue
            result += [f'$property_magic_cv_raw_primitive_coalesce_left(S.SOURCES,{operand},{names[field]}) = eps']
            # Constructor roots and proper children retain actual SOURCE authority.
            for cut, suffix in enumerate(((), (0,))):
                path = 'pcpath_site ++ ' + source_tree.path(((0 if side == 'class' else 1),) + relative + (0, field) + suffix)
                state = f'S_operand_missing_{number}_{field}_{cut}'
                result += [f'{state} = S[.SOURCES = [pcunit[.OCCURRENCES = $fqn_keyword_without(pcunit.OCCURRENCES,{path})]]]',
                           f'$property_magic_cv_raw_typed_ternary_operand_value({state}.SOURCES,{operand},{names[field]}) = eps']
    # A typed outer constructor is required; arbitrary bare results stay outside.
    for label, node in (
            ('float', 'NScalarFloat (FLOAT "3ff0000000000000") metadata_class'),
            ('variable', 'NExprVariable (BYTES "eA==") metadata_class'),
            ('nul', 'NScalarString (BYTES "AA==") metadata_class'),
            ('bare_ternary', 'NExprTernary expression_class_left ABSENT expression_class_right metadata_class'),
            ('bare_coalesce', 'NExprBinaryOpCoalesce expression_class_left expression_class_right metadata_class')):
        state, expression = f'S_operand_control_{label}', f'expression_operand_control_{label}'
        result += [f'{expression} = {node}',
                   f'{state} = S[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE (pcpath_site ++ [PCFIELD 0]) ({expression})) :: pcunit.OCCURRENCES]]]',
                   f'$property_magic_cv_raw_typed_ternary_operand_value({state}.SOURCES,porigin_class,{expression}) = eps']
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
