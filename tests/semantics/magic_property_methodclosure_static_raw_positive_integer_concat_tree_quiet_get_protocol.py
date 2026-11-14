#!/usr/bin/env python3
"""Check raw Integer UnaryPlus identity and selector source authority."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_fqn_keyword_concat_tree_quiet_get_protocol as prior

CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_positive_integer_concat_tree_quiet_get_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

TREE = [line.replace('$property_magic_cv_raw_fqn_keyword_string_tree(',
                     '$property_magic_cv_raw_positive_integer_string_tree(') for line in prior.TREE]
TREE += ['$property_magic_cv_raw_fqn_keyword_string_tree(S.SOURCES,porigin_class,expression_class) = eps',
         '$property_magic_cv_raw_fqn_keyword_string_tree(S.SOURCES,porigin_name,expression_method) = eps']


def checks(index):
    result = ['S.RESULT = KNOWN (POBJECT n_closure)',
              'S.OBJECTS[n_closure] = METHODCLOSURE porigin_method porigin_site porigin_requested eps',
              '$class_method_origin(S.CLASSES,porigin_method) = (pmethoddesc_method)',
              '$property_magic_cv_static_methodclosure(S,n_closure)',
              '$property_coalesce_valid(S,ppropertycoalesce)'] + TREE
    operators = (('class', (0, 1, 1, 0), 0 if index == 0 else 12),
                 ('method', (1, 1, 1, 1, 0) if index == 0 else (1, 0, 1), 12 if index == 0 else 0))
    for number, (side, parts, expected) in enumerate(operators):
        root = 'porigin_class' if side == 'class' else 'porigin_name'
        origin = 'porigin_positive_' + str(number)
        child_origin = 'porigin_positive_child_' + str(number)
        metadata = 'metadata_positive_' + str(number)
        child_metadata = 'metadata_positive_child_' + str(number)
        integer = 'i_positive_' + str(number)
        child = f'NScalarInt (INTEGER {integer}) {child_metadata}'
        node = f'NExprUnaryPlus ({child}) {metadata}'
        expression = 'expression_positive_' + str(number)
        result += [
            f'$origin_child((porigin_site),{prior.prior.path(parts)}) = ({origin})',
            f'$origin_node(S.SOURCES,{origin}) = ({node})',
            f'{expression} = {node}',
            rf'{metadata} =/= eps /\ {child_metadata} =/= eps',
            f'$origin_child(({origin}),[PCFIELD 0]) = ({child_origin})',
            f'$origin_node(S.SOURCES,{child_origin}) = ({child})',
            f'{integer} = {expected}',
            f'$long_range({integer})',
            f'$coerce_number(PINT {integer}) = COERCED (NINT {integer}) false',
            f'$unary_apply(S,POSITIVE,PINT {integer},0) = S[.RESULT = KNOWN (PINT {integer})]',
            f'$property_magic_cv_raw_positive_integer_string_tree(S.SOURCES,{origin},{expression}) = ($ntsigned({integer}))',
            f'$property_magic_cv_raw_fqn_keyword_string_tree(S.SOURCES,{origin},{expression}) = eps',
            f'$property_magic_cv_raw_integer_string_tree(S.SOURCES,{child_origin},{child}) = ($ntsigned({integer}))',
            rf'$compiled_read(S_trim,{origin}) = eps /\ $compiled_read(S_trim,{child_origin}) = eps',
        ]
        for label, changed_parts, forged in (
            ('parent_metadata', parts, f'NExprUnaryPlus ({child}) eps'),
            ('parent_kind', parts, f'NExprUnaryMinus ({child}) {metadata}'),
            ('child_metadata', parts + (0,), f'NScalarInt (INTEGER {integer}) eps'),
            ('child_value', parts + (0,), f'NScalarInt (INTEGER $({integer} + 1)) {child_metadata}'),
            ('child_kind', parts + (0,), f'NScalarString (BYTES "MTI=") {child_metadata}'),
            ('parent_missing', parts, None),
            ('child_missing', parts + (0,), None),
        ):
            state = f'S_positive_{number}_{label}'
            node_path = 'pcpath_site ++ ' + prior.prior.path(changed_parts)
            occurrences = (f'$fqn_keyword_without(pcunit.OCCURRENCES,{node_path})' if forged is None else
                           f'(PCOCCURRENCE ({node_path}) ({forged})) :: pcunit.OCCURRENCES')
            result += [
                f'{state} = S[.SOURCES = [pcunit[.OCCURRENCES = {occurrences}]]]',
                f'$property_magic_cv_raw_positive_integer_string_tree({state}.SOURCES,{root},expression_{side}) = eps',
                '~' + prior.prior.selector(side, state),
            ]
    for side in ('class', 'method'):
        for label, value in (('missing', None), ('type', 'PBOOL true'),
                             ('case', f'PSTRING $ptlc(ptbytes_{side})')):
            state = f'S_positive_root_{side}_{label}'
            constants = []
            for field, selected in enumerate(('class', 'method')):
                selected_value = value if selected == side else 'PSTRING ptbytes_' + selected
                if selected_value is not None:
                    constants.append(f'PCONSTANT (pcpath_site ++ [PCFIELD {field}]) ({selected_value})')
            result += [f'{state} = S[.POOLS = [{{UNIT n_site,CONSTANTS ([' + ','.join(constants) + '])}]]',
                       '~' + prior.prior.selector(side, state),
                       prior.prior.selector('method' if side == 'class' else 'class', state)]
    for number, value in enumerate((-9223372036854775809, -9223372036854775808, -1,
                                    0, 1, 9223372036854775807, 9223372036854775808)):
        integer = f'$({value})'
        child = f'NScalarInt (INTEGER {integer}) metadata_class'
        node = f'NExprUnaryPlus ({child}) metadata_class'
        expression = 'expression_bound_' + str(number)
        state = 'S_bound_' + str(number)
        result += [f'{expression} = {node}',
                   f'{state} = S[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE (pcpath_site ++ [PCFIELD 0]) ({node})) :: (PCOCCURRENCE (pcpath_site ++ [PCFIELD 0,PCFIELD 0]) ({child})) :: pcunit.OCCURRENCES]]]']
        rendered = f'($ntsigned({integer}))' if -9223372036854775808 <= value <= 9223372036854775807 else 'eps'
        result += [f'$property_magic_cv_raw_positive_integer_string_tree({state}.SOURCES,porigin_class,{expression}) = {rendered}']
    for label, child, extra in (
        ('string', 'NScalarString (BYTES "MTI=") metadata_class', ()),
        ('nested', 'NExprUnaryPlus (NScalarInt (INTEGER 12) metadata_class) metadata_class',
         (((0, 0), 'NScalarInt (INTEGER 12) metadata_class'),)),
    ):
        node = f'NExprUnaryPlus ({child}) metadata_class'
        occurrences = 'pcunit.OCCURRENCES'
        for parts, selected in (((), node), ((0,), child), *extra):
            occurrences = f'(PCOCCURRENCE (pcpath_site ++ {prior.prior.path((0,) + parts)}) ({selected})) :: ({occurrences})'
        result += [f'expression_control_{label} = {node}',
                   f'S_control_{label} = S[.SOURCES = [pcunit[.OCCURRENCES = {occurrences}]]]',
                   f'$property_magic_cv_raw_positive_integer_string_tree(S_control_{label}.SOURCES,porigin_class,expression_control_{label}) = eps']
    result += ['~$property_magic_cv_static_method_site_selector(S,porigin_site,expression_positive_0,porigin_requested,pclassdesc_requested.NAME)',
               '~$property_magic_cv_static_method_site_name(S,porigin_site,expression_positive_1,pmethoddesc_method.NAME)']
    return result


CASES = {row['id']: dict(source=row['source'], stage=old['stage'], checks=checks(index))
         for index, (row, old) in enumerate(zip(ROWS, prior.CASES.values(), strict=True))}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    base = prior.prior.prior.prior.base
    parents = (prior, prior.prior, prior.prior.prior, prior.prior.prior.prior, base,
               base.original, base.inherited, base.inherited.prior,
               base.inherited.prior.prior, base.inherited.prior.prior.prior, prior.renderer)
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, *(entry for parent in parents
                                               for entry in (Path(parent.__file__), parent.CATALOGUE))),
                 runner_flags=('--sl',), fixture_renderer=prior.render)
