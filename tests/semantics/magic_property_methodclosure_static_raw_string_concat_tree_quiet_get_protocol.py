#!/usr/bin/env python3
"""Check complete raw source trees, root pools and quiet method-Closure lifetimes."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_literal_selector_quiet_get_protocol as base

CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_raw_string_concat_tree_quiet_get_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

TREE = r'''
$class_at(S.CLASSES,porigin_requested) = (pclassdesc_requested)
porigin_site = PORIGIN n_site pcpath_site
S.SOURCES = [pcunit]
pcunit.ID = n_site
$origin_node(S.SOURCES,porigin_site) = (NExprStaticCall phpType19_class phpType20_method (SEQUENCE ([NVariadicPlaceholder metadata_placeholder])) metadata_site)
phpType19_class = NExprBinaryOpConcat expression_class_left expression_class_right metadata_class
phpType20_method = NExprBinaryOpConcat expression_method_left expression_method_right metadata_method_name
expression_class = NExprBinaryOpConcat expression_class_left expression_class_right metadata_class
expression_method = NExprBinaryOpConcat expression_method_left expression_method_right metadata_method_name
$origin_child((porigin_site),[PCFIELD 0]) = (porigin_class)
$origin_child((porigin_site),[PCFIELD 1]) = (porigin_name)
$origin_node(S.SOURCES,porigin_class) = (expression_class)
$origin_node(S.SOURCES,porigin_name) = (expression_method)
~($property_magic_cv_raw_string_leaf(expression_class_left) /\ $property_magic_cv_raw_string_leaf(expression_class_right))
~($property_magic_cv_raw_string_leaf(expression_method_left) /\ $property_magic_cv_raw_string_leaf(expression_method_right))
$compiled_read(S,porigin_class) = (PSTRING ptbytes_class)
$compiled_read(S,porigin_name) = (PSTRING ptbytes_method)
$property_magic_cv_raw_string_tree(S.SOURCES,porigin_class,expression_class) = (ptbytes_class)
$property_magic_cv_raw_string_tree(S.SOURCES,porigin_name,expression_method) = (ptbytes_method)
$parser_literal(expression_class) = (PSTRING ptbytes_class)
$parser_literal(expression_method) = (PSTRING ptbytes_method)
$ptlc($ppcall_literal_name(ptbytes_class)) = $ptlc(pclassdesc_requested.NAME)
$class_named(S.CLASSNAMES,$ptlc($ppcall_literal_name(ptbytes_class))) = (porigin_requested)
$ptlc(ptbytes_method) = $ptlc(pmethoddesc_method.NAME)
$property_magic_cv_static_method_site_selector(S,porigin_site,phpType19_class,porigin_requested,pclassdesc_requested.NAME)
$property_magic_cv_static_method_site_name(S,porigin_site,phpType20_method,pmethoddesc_method.NAME)
$scoped_requested_site(S,porigin_site,phpType19_class,porigin_requested,eps)
$scoped_source_method_origin(S,porigin_site,phpType20_method,pmethoddesc_method.NAME)
S_trim = S[.POOLS = [{UNIT n_site,CONSTANTS ([PCONSTANT (pcpath_site ++ [PCFIELD 0]) (PSTRING ptbytes_class),PCONSTANT (pcpath_site ++ [PCFIELD 1]) (PSTRING ptbytes_method)])}]]
$property_magic_cv_static_method_site_selector(S_trim,porigin_site,phpType19_class,porigin_requested,pclassdesc_requested.NAME)
$property_magic_cv_static_method_site_name(S_trim,porigin_site,phpType20_method,pmethoddesc_method.NAME)
$property_magic_cv_static_methodclosure(S_trim,n_closure)
$property_empty_rv_kind(S_trim,S_trim.OBJECTS[n_closure])
$property_magic_cv_raw_string_tree(eps,porigin_class,expression_class) = eps
$property_magic_cv_raw_string_tree(eps,porigin_name,expression_method) = eps
'''.strip().splitlines()


def checks(old, index):
    marker = '$class_at(S.CLASSES,porigin_requested) = (pclassdesc_requested)'
    result = old[:old.index(marker)] + TREE
    for side, path in (('class', '[PCFIELD 0,PCFIELD 0,PCFIELD 0]' if index == 0 else '[PCFIELD 0,PCFIELD 1,PCFIELD 1,PCFIELD 0]'),
                       ('method', '[PCFIELD 1,PCFIELD 1,PCFIELD 1,PCFIELD 0]' if index == 0 else '[PCFIELD 1,PCFIELD 0,PCFIELD 0]')):
        result += [
            f'$origin_child((porigin_site),{path}) = (porigin_deep_{side})',
            f'$origin_node(S.SOURCES,porigin_deep_{side}) = (NScalarString (BYTES text_deep_{side}) metadata_deep_{side})',
            f'$compiled_read(S,porigin_deep_{side}) = eps',
            f'$compiled_read(S_trim,porigin_deep_{side}) = eps',
        ]
        root = 'porigin_class' if side == 'class' else 'porigin_name'
        same = ('$property_magic_cv_static_method_site_selector(STATE,porigin_site,phpType19_class,porigin_requested,pclassdesc_requested.NAME)'
                if side == 'class' else '$property_magic_cv_static_method_site_name(STATE,porigin_site,phpType20_method,pmethoddesc_method.NAME)')
        other = ('$property_magic_cv_static_method_site_name(STATE,porigin_site,phpType20_method,pmethoddesc_method.NAME)'
                 if side == 'class' else '$property_magic_cv_static_method_site_selector(STATE,porigin_site,phpType19_class,porigin_requested,pclassdesc_requested.NAME)')
        for label, node in (
            ('bytes', f'NScalarString (BYTES "V1JPTkc=") metadata_deep_{side}'),
            ('metadata', f'NScalarString (BYTES text_deep_{side}) eps'),
            ('kind', f'NScalarInt (INTEGER 17) metadata_deep_{side}'),
            ('missing', f'NStmtNop metadata_deep_{side}'),
        ):
            state = f'S_tree_{side}_{label}'
            result += [
                f'{state} = S[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE (pcpath_site ++ {path}) ({node})) :: pcunit.OCCURRENCES]]]',
                f'$property_magic_cv_raw_string_tree({state}.SOURCES,{root},expression_{side}) = eps',
                '~' + same.replace('STATE', state), other.replace('STATE', state),
                f'$scoped_requested_site({state},porigin_site,phpType19_class,porigin_requested,eps)',
                f'$scoped_source_method_origin({state},porigin_site,phpType20_method,pmethoddesc_method.NAME)',
                f'~$property_magic_cv_static_methodclosure({state},n_closure)',
            ]
        raw = 'ptbytes_' + side
        result += [f'$ptlc({raw}) =/= {raw}']
        for label, value in (('type', 'PINT 17'), ('case', f'PSTRING $ptlc({raw})')):
            state = f'S_pool_{side}_{label}'
            class_value = value if side == 'class' else 'PSTRING ptbytes_class'
            method_value = value if side == 'method' else 'PSTRING ptbytes_method'
            result += [
                f'{state} = S[.POOLS = [{{UNIT n_site,CONSTANTS ([PCONSTANT (pcpath_site ++ [PCFIELD 0]) ({class_value}),PCONSTANT (pcpath_site ++ [PCFIELD 1]) ({method_value})])}}]]',
                f'$property_magic_cv_raw_string_tree({state}.SOURCES,{root},expression_{side}) = ({raw})',
                '~' + same.replace('STATE', state), other.replace('STATE', state),
                f'~$property_magic_cv_static_methodclosure({state},n_closure)',
            ]
    empty_path = '[PCFIELD 0,PCFIELD 0,PCFIELD 1]' if index == 0 else '[PCFIELD 0,PCFIELD 1,PCFIELD 0]'
    result += [
        f'$origin_child((porigin_site),{empty_path}) = (porigin_empty)',
        '$origin_node(S.SOURCES,porigin_empty) = (NScalarString (BYTES "") metadata_empty)',
        'expression_empty = NScalarString (BYTES "") metadata_empty',
        '$property_magic_cv_raw_string_leaf(expression_empty)',
        '$property_magic_cv_raw_string_tree(S.SOURCES,porigin_empty,expression_empty) = (eps)',
        '$property_magic_cv_raw_string_tree(eps,porigin_empty,expression_empty) = eps',
    ]
    for label, node in (('integer', 'NScalarInt (INTEGER 0) metadata_empty'),
                        ('variable', 'NExprVariable (BYTES "cGFydA==") metadata_empty')):
        result += [
            f'expression_leaf_{label} = {node}',
            f'S_leaf_{label} = S[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE (pcpath_site ++ {empty_path}) ({node})) :: pcunit.OCCURRENCES]]]',
            f'$origin_node(S_leaf_{label}.SOURCES,porigin_empty) = (expression_leaf_{label})',
            f'~$property_magic_cv_raw_string_leaf(expression_leaf_{label})',
            f'$property_magic_cv_raw_string_tree(S_leaf_{label}.SOURCES,porigin_empty,expression_leaf_{label}) = eps',
        ]
    if index == 1:
        result += [
            '$origin_child((porigin_class),[PCFIELD 1]) = (porigin_empty_tree)',
            '$origin_node(S.SOURCES,porigin_empty_tree) = (NExprBinaryOpConcat expression_empty_left expression_empty_right metadata_empty_tree)',
            'expression_empty_tree = NExprBinaryOpConcat expression_empty_left expression_empty_right metadata_empty_tree',
            '$property_magic_cv_raw_string_tree(S.SOURCES,porigin_empty_tree,expression_empty_tree) = (eps)',
            '$compiled_read(S,porigin_empty_tree) = eps',
        ]
    return result


CASES = {row['id']: dict(old, source=row['source'], checks=checks(old['checks'], index))
         for index, (row, old) in enumerate(zip(ROWS, base.CASES.values(), strict=True))}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    parents = (base, base.original, base.inherited, base.inherited.prior,
               base.inherited.prior.prior, base.inherited.prior.prior.prior)
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, *(path for parent in parents
                                               for path in (Path(parent.__file__), parent.CATALOGUE))),
                 runner_flags=('--sl',))
