#!/usr/bin/env python3
"""Check raw numeric-String UnaryPlus values and selector source authority."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_positive_keyword_concat_tree_quiet_get_protocol as prior
import magic_property_methodclosure_static_raw_keyword_concat_tree_quiet_get_protocol as source_tree
import magic_property_methodclosure_static_raw_fqn_keyword_concat_tree_quiet_get_protocol as renderer

CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_positive_string_concat_tree_quiet_get_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

TREE = [line.replace('$property_magic_cv_raw_positive_keyword_string_tree(',
                     '$property_magic_cv_raw_positive_string_tree(') for line in prior.TREE]
TREE += ['$property_magic_cv_raw_positive_keyword_string_tree(S.SOURCES,porigin_class,expression_class) = eps',
         '$property_magic_cv_raw_positive_keyword_string_tree(S.SOURCES,porigin_name,expression_method) = eps']


def checks(index):
    result = ['S.RESULT = KNOWN (POBJECT n_closure)',
              'S.OBJECTS[n_closure] = METHODCLOSURE porigin_method porigin_site porigin_requested eps',
              '$class_method_origin(S.CLASSES,porigin_method) = (pmethoddesc_method)',
              '$property_magic_cv_static_methodclosure(S,n_closure)',
              '$property_coalesce_valid(S,ppropertycoalesce)'] + TREE
    strings = ((('class', (0, 1, 1, 1), ' 0001 ', 1),
                ('method', (1, 1, 0), ' -000 ', 0)) if index == 0 else
               (('class', (0, 1, 0, 0), '+000', 0),
                ('method', (1, 1), '001', 1)))
    for number, (side, parts, raw, expected) in enumerate(strings):
        root = 'porigin_class' if side == 'class' else 'porigin_name'
        origin = 'porigin_string_' + str(number)
        child_origin = 'porigin_string_child_' + str(number)
        metadata = 'metadata_string_' + str(number)
        child_metadata = 'metadata_string_child_' + str(number)
        text = 'text_string_' + str(number)
        integer = 'i_string_' + str(number)
        child = f'NScalarString (BYTES {text}) {child_metadata}'
        node = f'NExprUnaryPlus ({child}) {metadata}'
        expression = 'expression_string_' + str(number)
        result += [
            f'$origin_child((porigin_site),{source_tree.path(parts)}) = ({origin})',
            f'$origin_node(S.SOURCES,{origin}) = ({node})',
            f'{expression} = {node}',
            rf'{metadata} =/= eps /\ {child_metadata} =/= eps',
            f'$origin_child(({origin}),[PCFIELD 0]) = ({child_origin})',
            f'$origin_node(S.SOURCES,{child_origin}) = ({child})',
            f'$base64({text}) = $ptascii("{raw}")',
            f'$coerce_number(PSTRING $base64({text})) = COERCED (NINT {integer}) false',
            f'{integer} = {expected}',
            f'$long_range({integer})',
            f'$unary_apply(S,POSITIVE,PSTRING $base64({text}),0) = S[.RESULT = KNOWN (PINT {integer})]',
            f'$property_magic_cv_raw_positive_string_tree(S.SOURCES,{origin},{expression}) = ($ntsigned({integer}))',
            f'$property_magic_cv_raw_positive_keyword_string_tree(S.SOURCES,{origin},{expression}) = eps',
            f'$property_magic_cv_raw_string_tree(S.SOURCES,{child_origin},{child}) = ($base64({text}))',
            rf'$compiled_read(S_trim,{origin}) = eps /\ $compiled_read(S_trim,{child_origin}) = eps',
        ]
        for label, changed_parts, forged in (
            ('parent_metadata', parts, f'NExprUnaryPlus ({child}) eps'),
            ('parent_kind', parts, f'NExprUnaryMinus ({child}) {metadata}'),
            ('child_metadata', parts + (0,), f'NScalarString (BYTES {text}) eps'),
            ('child_value', parts + (0,), f'NScalarString (BYTES "{"MA==" if expected == 0 else "MQ=="}") {child_metadata}'),
            ('child_kind', parts + (0,), f'NScalarInt (INTEGER {integer}) {child_metadata}'),
            ('parent_missing', parts, None),
            ('child_missing', parts + (0,), None),
        ):
            state = f'S_string_{number}_{label}'
            node_path = 'pcpath_site ++ ' + source_tree.path(changed_parts)
            occurrences = (f'$fqn_keyword_without(pcunit.OCCURRENCES,{node_path})' if forged is None else
                           f'(PCOCCURRENCE ({node_path}) ({forged})) :: pcunit.OCCURRENCES')
            result += [f'{state} = S[.SOURCES = [pcunit[.OCCURRENCES = {occurrences}]]]',
                       f'$property_magic_cv_raw_positive_string_tree({state}.SOURCES,{root},expression_{side}) = eps',
                       '~' + source_tree.selector(side, state)]
    for side in ('class', 'method'):
        for label, value in (('missing', None), ('type', 'PBOOL true'),
                             ('case', f'PSTRING $ptlc(ptbytes_{side})')):
            state = f'S_string_root_{side}_{label}'
            constants = []
            for field, selected in enumerate(('class', 'method')):
                selected_value = value if selected == side else 'PSTRING ptbytes_' + selected
                if selected_value is not None:
                    constants.append(f'PCONSTANT (pcpath_site ++ [PCFIELD {field}]) ({selected_value})')
            result += [f'{state} = S[.POOLS = [{{UNIT n_site,CONSTANTS ([' + ','.join(constants) + '])}]]',
                       '~' + source_tree.selector(side, state),
                       source_tree.selector('method' if side == 'class' else 'class', state)]
    for label, text in (('leading', 'MXRhaWw='), ('float', 'MS4w'),
                        ('overflow', 'OTIyMzM3MjAzNjg1NDc3NTgwOA=='), ('nonnumeric', 'bm8=')):
        child = f'NScalarString (BYTES "{text}") metadata_class'
        node = f'NExprUnaryPlus ({child}) metadata_class'
        occurrences = 'pcunit.OCCURRENCES'
        for parts, selected in (((), node), ((0,), child)):
            occurrences = f'(PCOCCURRENCE (pcpath_site ++ {source_tree.path((0,) + parts)}) ({selected})) :: ({occurrences})'
        result += [f'expression_control_{label} = {node}',
                   f'S_control_{label} = S[.SOURCES = [pcunit[.OCCURRENCES = {occurrences}]]]',
                   f'$property_magic_cv_raw_positive_string_tree(S_control_{label}.SOURCES,porigin_class,expression_control_{label}) = eps']
    result += ['~$property_magic_cv_static_method_site_selector(S,porigin_site,expression_string_0,porigin_requested,pclassdesc_requested.NAME)',
               '~$property_magic_cv_static_method_site_name(S,porigin_site,expression_string_1,pmethoddesc_method.NAME)']
    return result


CASES = {row['id']: dict(source=row['source'], stage=old['stage'], checks=checks(index))
         for index, (row, old) in enumerate(zip(ROWS, prior.CASES.values(), strict=True))}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    base = source_tree.prior.prior.base
    parents = (prior, prior.prior, renderer, source_tree, source_tree.prior,
               source_tree.prior.prior, base, base.original, base.inherited,
               base.inherited.prior, base.inherited.prior.prior,
               base.inherited.prior.prior.prior, renderer.renderer)
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, *(entry for parent in parents
                                               for entry in (Path(parent.__file__), parent.CATALOGUE))),
                 runner_flags=('--sl',), fixture_renderer=renderer.render)
