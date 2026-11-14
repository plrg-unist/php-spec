#!/usr/bin/env python3
"""Check String/Integer CONCAT authority, root pools and quiet Get ownership."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_string_concat_tree_quiet_get_protocol as prior

CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_integer_concat_tree_quiet_get_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

TREE = [line.replace('$property_magic_cv_raw_string_tree(',
                     '$property_magic_cv_raw_integer_string_tree(') for line in prior.TREE]
TREE += [
    '$property_magic_cv_raw_string_tree(S.SOURCES,porigin_class,expression_class) = eps',
    '$property_magic_cv_raw_string_tree(S.SOURCES,porigin_name,expression_method) = eps',
]


def selector(side, state='S'):
    if side == 'class':
        return f'$property_magic_cv_static_method_site_selector({state},porigin_site,phpType19_class,porigin_requested,pclassdesc_requested.NAME)'
    return f'$property_magic_cv_static_method_site_name({state},porigin_site,phpType20_method,pmethoddesc_method.NAME)'


def checks(old, index):
    marker = '$class_at(S.CLASSES,porigin_requested) = (pclassdesc_requested)'
    result = [line.replace('QuietLiteralSelectorInheritedAssignTarget',
                           'QuietLiteralSelectorInheritedAssignTarget12')
              for line in old[:old.index(marker)]] + TREE
    paths = (('[PCFIELD 0,PCFIELD 1,PCFIELD 1]', '[PCFIELD 1,PCFIELD 1,PCFIELD 1,PCFIELD 1]')
             if index == 0 else ('[PCFIELD 0,PCFIELD 1,PCFIELD 1,PCFIELD 0]', '[PCFIELD 1,PCFIELD 1]'))
    for side, path in zip(('class', 'method'), paths, strict=True):
        root = 'porigin_class' if side == 'class' else 'porigin_name'
        origin = 'porigin_integer_' + side
        metadata = 'metadata_integer_' + side
        integer = 'i_integer_' + side
        node = f'NScalarInt (INTEGER {integer}) {metadata}'
        result += [
            f'$origin_child((porigin_site),{path}) = ({origin})',
            f'$origin_node(S.SOURCES,{origin}) = ({node})',
            f'{metadata} =/= eps',
            f'{integer} = {0 if (index == 0) == (side == "class") else 12}',
            f'$long_range({integer})',
            f'$compiled_read(S_trim,{origin}) = eps',
            f'$property_magic_cv_raw_integer_string_tree(S.SOURCES,{origin},{node}) = ($ntsigned({integer}))',
            f'$property_magic_cv_raw_string_tree(S.SOURCES,{origin},{node}) = eps',
        ]
        for label, forged in (
            ('value', f'NScalarInt (INTEGER $({integer} + 1)) {metadata}'),
            ('metadata', f'NScalarInt (INTEGER {integer}) eps'),
            ('string', f'NScalarString (BYTES "MA==") {metadata}'),
            ('float', f'NScalarFloat (FLOAT "0000000000000000") {metadata}'),
            ('variable', f'NExprVariable (BYTES "cGFydA==") {metadata}'),
        ):
            state = f'S_integer_{side}_{label}'
            result += [
                f'{state} = S[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE (pcpath_site ++ {path}) ({forged})) :: pcunit.OCCURRENCES]]]',
                f'$property_magic_cv_raw_integer_string_tree({state}.SOURCES,{root},expression_{side}) = eps',
                '~' + selector(side, state),
                selector('method' if side == 'class' else 'class', state),
                f'~$property_magic_cv_static_methodclosure({state},n_closure)',
            ]
        for label, value in (('missing', None), ('type', 'PINT 17'),
                             ('case', f'PSTRING $ptlc(ptbytes_{side})')):
            state = f'S_root_{side}_{label}'
            constants = []
            for field, selected in enumerate(('class', 'method')):
                selected_value = value if selected == side else 'PSTRING ptbytes_' + selected
                if selected_value is not None:
                    constants.append(f'PCONSTANT (pcpath_site ++ [PCFIELD {field}]) ({selected_value})')
            result += [
                f'{state} = S[.POOLS = [{{UNIT n_site,CONSTANTS ([' + ','.join(constants) + '])}]]',
                f'$property_magic_cv_raw_integer_string_tree({state}.SOURCES,{root},expression_{side}) = (ptbytes_{side})',
                '~' + selector(side, state),
                selector('method' if side == 'class' else 'class', state),
                f'~$property_magic_cv_static_methodclosure({state},n_closure)',
            ]
    empty_path = '[PCFIELD 0,PCFIELD 0,PCFIELD 1]' if index == 0 else '[PCFIELD 0,PCFIELD 1,PCFIELD 0]'
    result += [
        f'$origin_child((porigin_site),{empty_path}) = (porigin_empty)',
        '$origin_node(S.SOURCES,porigin_empty) = (NScalarString (BYTES "") metadata_empty)',
        'expression_empty = NScalarString (BYTES "") metadata_empty',
        '$property_magic_cv_raw_integer_string_tree(S.SOURCES,porigin_empty,expression_empty) = (eps)',
        '$property_magic_cv_raw_string_tree(S.SOURCES,porigin_empty,expression_empty) = (eps)',
        '$property_magic_cv_raw_integer_string_tree(eps,porigin_empty,expression_empty) = eps',
    ]
    for label, integer in (('zero', 0), ('negative', -1), ('minimum', -(2**63)),
                           ('maximum', 2**63 - 1), ('below', -(2**63) - 1), ('above', 2**63)):
        node = f'NScalarInt (INTEGER $({integer})) metadata_empty'
        state = 'S_bound_' + label
        encoded = base64.b64encode(str(integer).encode()).decode()
        expected = f'($base64("{encoded}"))' if -(2**63) <= integer < 2**63 else 'eps'
        result += [
            f'{state} = S[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE (pcpath_site ++ {empty_path}) ({node})) :: pcunit.OCCURRENCES]]]',
            f'$property_magic_cv_raw_integer_string_tree({state}.SOURCES,porigin_empty,{node}) = {expected}',
            f'$property_magic_cv_raw_string_tree({state}.SOURCES,porigin_empty,{node}) = eps',
        ]
    for label, node in (
        ('float', 'NScalarFloat (FLOAT "0000000000000000") metadata_empty'),
        ('variable', 'NExprVariable (BYTES "cGFydA==") metadata_empty'),
        ('unary', 'NExprUnaryMinus (NScalarInt (INTEGER 1) metadata_empty) metadata_empty'),
    ):
        state = 'S_forbidden_' + label
        result += [
            f'{state} = S[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE (pcpath_site ++ {empty_path}) ({node})) :: pcunit.OCCURRENCES]]]',
            f'$property_magic_cv_raw_integer_string_tree({state}.SOURCES,porigin_empty,{node}) = eps',
        ]
    result += [
        '~$property_magic_cv_static_method_site_selector(S,porigin_site,NScalarInt (INTEGER 0) metadata_empty,porigin_requested,pclassdesc_requested.NAME)',
        '~$property_magic_cv_static_method_site_name(S,porigin_site,NScalarInt (INTEGER 0) metadata_empty,pmethoddesc_method.NAME)',
    ]
    return result


CASES = {row['id']: dict(old, source=row['source'], checks=checks(old['checks'], index))
         for index, (row, old) in enumerate(zip(ROWS, prior.base.CASES.values(), strict=True))}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    base = prior.base
    parents = (prior, base, base.original, base.inherited, base.inherited.prior,
               base.inherited.prior.prior, base.inherited.prior.prior.prior)
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, *(path for parent in parents
                                               for path in (Path(parent.__file__), parent.CATALOGUE))),
                 runner_flags=('--sl',))
