#!/usr/bin/env python3
"""Check keyword expression/name authority and quiet method-Closure ownership."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_raw_integer_concat_tree_quiet_get_protocol as prior

CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_keyword_concat_tree_quiet_get_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

TREE = [line.replace('$property_magic_cv_raw_integer_string_tree(',
                     '$property_magic_cv_raw_keyword_string_tree(') for line in prior.TREE]
TREE = [line.split(' = ')[0] + ' = eps' if line.startswith('$parser_literal(') else line for line in TREE]
TREE += [
    '$property_magic_cv_raw_integer_string_tree(S.SOURCES,porigin_class,expression_class) = eps',
    '$property_magic_cv_raw_integer_string_tree(S.SOURCES,porigin_name,expression_method) = eps',
    '~$scoped_method_literal(expression_method)',
    '$property_computed_name(expression_method)',
]


def path(parts):
    return '[' + ','.join('PCFIELD ' + str(part) for part in parts) + ']'


def selector(side, state='S'):
    if side == 'class':
        return f'$property_magic_cv_static_method_site_selector({state},porigin_site,phpType19_class,porigin_requested,pclassdesc_requested.NAME)'
    return f'$property_magic_cv_static_method_site_name({state},porigin_site,phpType20_method,pmethoddesc_method.NAME)'


def checks(old, index):
    marker = '$class_at(S.CLASSES,porigin_requested) = (pclassdesc_requested)'
    result = old[:old.index(marker)] + TREE
    keywords = ((('class', (0, 1, 1, 1), 'true'),
                 ('method', (1, 1, 0), 'false'),
                 ('method', (1, 1, 1, 1, 1), 'null')) if index == 0 else
                (('class', (0, 1, 0, 0), 'null'),
                 ('class', (0, 1, 0, 1), 'false'),
                 ('method', (1, 1), 'true')))
    for number, (side, parts, word) in enumerate(keywords):
        root = 'porigin_class' if side == 'class' else 'porigin_name'
        origin = 'porigin_keyword_' + str(number)
        name_origin = 'porigin_keyword_name_' + str(number)
        metadata = 'metadata_keyword_' + str(number)
        name_metadata = 'metadata_keyword_name_' + str(number)
        text = 'text_keyword_' + str(number)
        node = f'NExprConstFetch (NName (BYTES {text}) {name_metadata}) {metadata}'
        expression = 'expression_keyword_' + str(number)
        value = {'true': 'PBOOL true', 'false': 'PBOOL false', 'null': 'PNULL'}[word]
        rendered = '$ptascii("1")' if word == 'true' else 'eps'
        result += [
            f'$origin_child((porigin_site),{path(parts)}) = ({origin})',
            f'$origin_node(S.SOURCES,{origin}) = ({node})',
            f'{expression} = {node}',
            f'{metadata} =/= eps',
            f'{name_metadata} =/= eps',
            f'$origin_child(({origin}),[PCFIELD 0]) = ({name_origin})',
            f'$origin_node(S.SOURCES,{name_origin}) = (NName (BYTES {text}) {name_metadata})',
            f'$special_constant($base64({text})) = ({value})',
            f'$property_magic_cv_raw_keyword_string_tree(S.SOURCES,{origin},{expression}) = ({rendered})',
            f'$property_magic_cv_raw_integer_string_tree(S.SOURCES,{origin},{expression}) = eps',
            f'$parser_literal({expression}) = eps',
            f'$compiled_read(S_trim,{origin}) = eps',
            f'$compiled_read(S_trim,{name_origin}) = eps',
        ]
        for label, changed_parts, forged in (
            ('expression_metadata', parts, f'NExprConstFetch (NName (BYTES {text}) {name_metadata}) eps'),
            ('expression_kind', parts, f'NExprVariable (BYTES {text}) {metadata}'),
            ('name_metadata', parts + (0,), f'NName (BYTES {text}) eps'),
            ('name_value', parts + (0,), f'NName (BYTES "d3Jvbmc=") {name_metadata}'),
            ('name_kind', parts + (0,), f'NNameFullyQualified (BYTES {text}) {name_metadata}'),
        ):
            state = f'S_keyword_{number}_{label}'
            result += [
                f'{state} = S[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE (pcpath_site ++ {path(changed_parts)}) ({forged})) :: pcunit.OCCURRENCES]]]',
                f'$property_magic_cv_raw_keyword_string_tree({state}.SOURCES,{root},expression_{side}) = eps',
                '~' + selector(side, state),
                selector('method' if side == 'class' else 'class', state),
                f'~$property_magic_cv_static_methodclosure({state},n_closure)',
            ]
    for side in ('class', 'method'):
        root = 'porigin_class' if side == 'class' else 'porigin_name'
        for label, value in (('missing', None), ('type', 'PBOOL true'),
                             ('case', f'PSTRING $ptlc(ptbytes_{side})')):
            state = f'S_keyword_root_{side}_{label}'
            constants = []
            for field, selected in enumerate(('class', 'method')):
                selected_value = value if selected == side else 'PSTRING ptbytes_' + selected
                if selected_value is not None:
                    constants.append(f'PCONSTANT (pcpath_site ++ [PCFIELD {field}]) ({selected_value})')
            result += [
                f'{state} = S[.POOLS = [{{UNIT n_site,CONSTANTS ([' + ','.join(constants) + '])}]]',
                f'$property_magic_cv_raw_keyword_string_tree({state}.SOURCES,{root},expression_{side}) = (ptbytes_{side})',
                '~' + selector(side, state),
                selector('method' if side == 'class' else 'class', state),
                f'~$property_magic_cv_static_methodclosure({state},n_closure)',
            ]
    empty_parts = (0, 0, 1) if index == 0 else (0, 1, 1, 1)
    result += [
        f'$origin_child((porigin_site),{path(empty_parts)}) = (porigin_empty)',
        '$origin_node(S.SOURCES,porigin_empty) = (NScalarString (BYTES "") metadata_empty)',
        'expression_empty = NScalarString (BYTES "") metadata_empty',
        '$property_magic_cv_raw_keyword_string_tree(S.SOURCES,porigin_empty,expression_empty) = (eps)',
        '$property_magic_cv_raw_integer_string_tree(S.SOURCES,porigin_empty,expression_empty) = (eps)',
        '$property_magic_cv_raw_keyword_string_tree(eps,porigin_empty,expression_empty) = eps',
        '~$property_magic_cv_static_method_site_selector(S,porigin_site,expression_keyword_0,porigin_requested,pclassdesc_requested.NAME)',
        '~$property_magic_cv_static_method_site_name(S,porigin_site,expression_keyword_2,pmethoddesc_method.NAME)',
    ]
    return result


CASES = {row['id']: dict(old, source=row['source'], checks=checks(old['checks'], index))
         for index, (row, old) in enumerate(zip(ROWS, prior.CASES.values(), strict=True))}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    base = prior.prior.base
    parents = (prior, prior.prior, base, base.original, base.inherited, base.inherited.prior,
               base.inherited.prior.prior, base.inherited.prior.prior.prior)
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, *(entry for parent in parents
                                               for entry in (Path(parent.__file__), parent.CATALOGUE))),
                 runner_flags=('--sl',))
