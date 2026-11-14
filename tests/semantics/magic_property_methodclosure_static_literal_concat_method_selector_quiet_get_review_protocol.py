#!/usr/bin/env python3
"""Check exact flat string concatenation independently of generic method matching."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_own_child_members_quiet_get_review_protocol as own
import magic_property_methodclosure_static_inherited_child_members_quiet_get_review_protocol as inherited

CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_literal_concat_method_selector_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

LEFT = 'NScalarString (BYTES text_left) metadata_left'
RIGHT = 'NScalarString (BYTES text_right) metadata_right'
METHOD = f'NExprBinaryOpConcat ({LEFT}) ({RIGHT}) metadata_selected'


def refusal(label, state):
    return [f'S_concat_{label} = {state}',
            f'~$property_magic_cv_static_method_site_name(S_concat_{label},porigin_site,phpType20_method,pmethoddesc_method.NAME)',
            f'~$property_magic_cv_static_methodclosure(S_concat_{label},n_closure)',
            f'~$property_empty_rv_kind(S_concat_{label},S_concat_{label}.OBJECTS[n_closure])']


def occurrences(changes):
    value = 'pcunit.OCCURRENCES'
    for path, node in changes:
        value = f'$rc_review_occurrence({value},pcpath_site ++ {path},{node})'
    return value


def source_state(changes):
    return 'S[.SOURCES = [pcunit[.OCCURRENCES = ' + occurrences(changes) + ']]]'


def coherent_method(method, left, right, value):
    site = ('NExprStaticCall phpType19_class (' + method + ') '
            '(SEQUENCE ([NVariadicPlaceholder metadata_placeholder])) metadata_site')
    state = source_state((('eps', site), ('[PCFIELD 1]', method),
                          ('[PCFIELD 1,PCFIELD 0]', left),
                          ('[PCFIELD 1,PCFIELD 1]', right)))
    return state + '[.POOLS = [{UNIT n_unit,CONSTANTS ([PCONSTANT (pcpath_site ++ [PCFIELD 1]) (PSTRING ' + value + ')])}]]'


NAME = r'''
$class_at(S.CLASSES,porigin_requested) = (pclassdesc_requested)
phpType20_method = METHOD
$origin_child((porigin_site),[PCFIELD 1]) = (porigin_name)
porigin_name = PORIGIN n_unit (pcpath_site ++ [PCFIELD 1])
$origin_child((porigin_name),[PCFIELD 0]) = (porigin_left)
$origin_child((porigin_name),[PCFIELD 1]) = (porigin_right)
$origin_node(S.SOURCES,porigin_name) = (phpType20_method)
$origin_node(S.SOURCES,porigin_left) = (LEFT)
$origin_node(S.SOURCES,porigin_right) = (RIGHT)
ptbytes_method = $base64(text_left) ++ $base64(text_right)
$compiled_read(S,porigin_name) = (PSTRING ptbytes_method)
$compiled_read(S,porigin_left) = eps
$compiled_read(S,porigin_right) = eps
$ptlc(ptbytes_method) = $ptlc(pmethoddesc_method.NAME)
$ptlc(ptbytes_method) =/= ptbytes_method
$scoped_source_method_origin(S,porigin_site,phpType20_method,pmethoddesc_method.NAME)
$property_magic_cv_static_method_site_selector(S,porigin_site,phpType19_class,porigin_requested,pclassdesc_requested.NAME)
$property_magic_cv_static_method_site_name(S,porigin_site,phpType20_method,pmethoddesc_method.NAME)
~$property_magic_cv_static_method_site_name(S,porigin_name,phpType20_method,pmethoddesc_method.NAME)
~$property_magic_cv_static_method_site_name(S,porigin_site,phpType20_method,pclassdesc_requested.NAME)
~$property_magic_cv_static_method_site_name(S[.SOURCES = eps],porigin_site,phpType20_method,pmethoddesc_method.NAME)
S_concat_root_only = S[.POOLS = [{UNIT n_unit,CONSTANTS ([PCONSTANT (pcpath_site ++ [PCFIELD 1]) (PSTRING ptbytes_method)])}]]
$compiled_read(S_concat_root_only,porigin_left) = eps
$compiled_read(S_concat_root_only,porigin_right) = eps
$property_magic_cv_static_method_site_name(S_concat_root_only,porigin_site,phpType20_method,pmethoddesc_method.NAME)
$property_magic_cv_static_methodclosure(S_concat_root_only,n_closure)
$property_empty_rv_kind(S_concat_root_only,S_concat_root_only.OBJECTS[n_closure])
'''.replace('METHOD', METHOD).replace('LEFT', LEFT).replace('RIGHT', RIGHT).strip().splitlines()


def checks(old, index):
    result = []
    for check in old:
        check = check.replace('NIdentifier (BYTES text_selected) metadata_selected', METHOD)
        check = check.replace('$base64(text_selected)', '($base64(text_left) ++ $base64(text_right))')
        if index == 1 and check == '~$property_magic_cv_static_method_parent(S,pclassdesc_child,phpType44_parent)':
            check = check.removeprefix('~')
        result.append(check)
    if index == 0:
        result.append('porigin_requested = porigin_owner')
    constructor = 'NNameFullyQualified' if index == 0 else 'NName'
    result.append(f'phpType19_class = {constructor} (BYTES text_requested) metadata_requested')
    result += NAME
    for label, constants, expected in (
        ('missing', None, 'eps'),
        ('type', '[PCONSTANT (pcpath_site ++ [PCFIELD 1]) (PINT 17)]', '(PINT 17)'),
        ('case', '[PCONSTANT (pcpath_site ++ [PCFIELD 1]) (PSTRING $ptlc(ptbytes_method))]', '(PSTRING $ptlc(ptbytes_method))'),
        ('wrong_slot', '[PCONSTANT (pcpath_site ++ [PCFIELD 0]) (PSTRING ptbytes_method)]', 'eps'),
        ('children_only', '[PCONSTANT (pcpath_site ++ [PCFIELD 1,PCFIELD 0]) (PSTRING $base64(text_left)),PCONSTANT (pcpath_site ++ [PCFIELD 1,PCFIELD 1]) (PSTRING $base64(text_right))]', 'eps'),
    ):
        pools = 'eps' if constants is None else '[{UNIT n_unit,CONSTANTS (' + constants + ')}]'
        result += [f'S_concat_{label} = S[.POOLS = {pools}]',
                   f'$compiled_read(S_concat_{label},porigin_name) = {expected}',
                   f'$property_magic_cv_static_method_site_selector(S_concat_{label},porigin_site,phpType19_class,porigin_requested,pclassdesc_requested.NAME)',
                   f'$scoped_requested_site(S_concat_{label},porigin_site,phpType19_class,porigin_requested,eps)',
                   f'$scoped_source_method_origin(S_concat_{label},porigin_site,phpType20_method,pmethoddesc_method.NAME)',
                   f'~$property_magic_cv_static_method_site_name(S_concat_{label},porigin_site,phpType20_method,pmethoddesc_method.NAME)',
                   f'~$property_magic_cv_static_methodclosure(S_concat_{label},n_closure)',
                   f'~$property_empty_rv_kind(S_concat_{label},S_concat_{label}.OBJECTS[n_closure])']
    for label, path, node in (
        ('root_kind', '[PCFIELD 1]', 'NStmtNop metadata_selected'),
        ('root_order', '[PCFIELD 1]', f'NExprBinaryOpConcat ({RIGHT}) ({LEFT}) metadata_selected'),
        ('root_metadata', '[PCFIELD 1]', f'NExprBinaryOpConcat ({LEFT}) ({RIGHT}) eps'),
        ('left_value', '[PCFIELD 1,PCFIELD 0]', 'NScalarString (BYTES "T3RoZXI=") metadata_left'),
        ('right_value', '[PCFIELD 1,PCFIELD 1]', 'NScalarString (BYTES "T3RoZXI=") metadata_right'),
        ('left_metadata', '[PCFIELD 1,PCFIELD 0]', 'NScalarString (BYTES text_left) eps'),
        ('right_metadata', '[PCFIELD 1,PCFIELD 1]', 'NScalarString (BYTES text_right) eps'),
        ('left_kind', '[PCFIELD 1,PCFIELD 0]', 'NExprVariable (BYTES text_left) metadata_left'),
        ('right_kind', '[PCFIELD 1,PCFIELD 1]', 'NExprVariable (BYTES text_right) metadata_right'),
    ):
        result += refusal(label, source_state(((path, node),)))
        result += [f'$origin_node(S_concat_{label}.SOURCES,PORIGIN n_unit (pcpath_site ++ {path})) = ({node})',
                   f'$compiled_read(S_concat_{label},porigin_name) = (PSTRING ptbytes_method)',
                   f'$scoped_source_method_origin(S_concat_{label},porigin_site,phpType20_method,pmethoddesc_method.NAME)']
    result += refusal('no_code', 'S[.CODE = eps]')

    nested_right = f'NExprBinaryOpConcat ({RIGHT}) (NScalarString (BYTES "") metadata_right) metadata_right'
    nested = f'NExprBinaryOpConcat ({LEFT}) ({nested_right}) metadata_selected'
    result += [
        f'phpType20_nested = {nested}',
        'S_concat_nested = ' + coherent_method(nested, LEFT, nested_right, 'ptbytes_method'),
        '$origin_node(S_concat_nested.SOURCES,porigin_name) = (phpType20_nested)',
        '$compiled_read(S_concat_nested,porigin_name) = (PSTRING ptbytes_method)',
        '$scoped_source_method_origin(S_concat_nested,porigin_site,phpType20_nested,pmethoddesc_method.NAME)',
        '~$property_magic_cv_static_method_site_name(S_concat_nested,porigin_site,phpType20_nested,pmethoddesc_method.NAME)',
        '~$property_magic_cv_static_methodclosure(S_concat_nested,n_closure)',
        '~$property_empty_rv_kind(S_concat_nested,S_concat_nested.OBJECTS[n_closure])',
    ]
    for label, left, right, value in (
        ('numeric', 'NScalarInt (INTEGER 0) metadata_left', RIGHT, '(48 :: $base64(text_right))'),
        ('variable', 'NExprVariable (BYTES text_left) metadata_left', RIGHT, 'ptbytes_method'),
    ):
        method = f'NExprBinaryOpConcat ({left}) ({right}) metadata_selected'
        result += [f'phpType20_{label} = {method}',
                   f'S_concat_{label} = ' + coherent_method(method, left, right, value),
                   f'$origin_node(S_concat_{label}.SOURCES,porigin_name) = (phpType20_{label})',
                   f'$compiled_read(S_concat_{label},porigin_name) = (PSTRING {value})',
                   f'$scoped_source_method_origin(S_concat_{label},porigin_site,phpType20_{label},{value})',
                   ('' if label == 'numeric' else '~') + f'$property_magic_cv_static_method_site_name(S_concat_{label},porigin_site,phpType20_{label},{value})',
                   f'~$property_magic_cv_static_methodclosure(S_concat_{label},n_closure)']

    raw_left = 'Co' if index == 0 else 'cOunt'
    encoded = base64.b64encode(('\\' + raw_left).encode()).decode()
    slash_left = f'NScalarString (BYTES "{encoded}") metadata_left'
    slash = f'NExprBinaryOpConcat ({slash_left}) ({RIGHT}) metadata_selected'
    result += [
        f'$base64(text_left) = $ptascii("{raw_left}")',
        'ptbytes_method_slash = 92 :: ptbytes_method',
        f'phpType20_slash = {slash}',
        'S_concat_slash = ' + coherent_method(slash, slash_left, RIGHT, 'ptbytes_method_slash'),
        '$origin_node(S_concat_slash.SOURCES,porigin_name) = (phpType20_slash)',
        '$compiled_read(S_concat_slash,porigin_name) = (PSTRING ptbytes_method_slash)',
        '$ppcall_literal_name(ptbytes_method_slash) = ptbytes_method',
        '$property_magic_cv_static_method_site_selector(S_concat_slash,porigin_site,phpType19_class,porigin_requested,pclassdesc_requested.NAME)',
        '~$scoped_source_method_origin(S_concat_slash,porigin_site,phpType20_slash,pmethoddesc_method.NAME)',
        '~$property_magic_cv_static_method_site_name(S_concat_slash,porigin_site,phpType20_slash,pmethoddesc_method.NAME)',
        '~$property_magic_cv_static_methodclosure(S_concat_slash,n_closure)',
        '~$property_empty_rv_kind(S_concat_slash,S_concat_slash.OBJECTS[n_closure])',
    ]
    return result


OLD = (next(iter(own.CASES.values())), list(inherited.CASES.values())[1])
CASES = {row['id']: dict(old, source=row['source'], checks=checks(old['checks'], index))
         for index, (row, old) in enumerate(zip(ROWS, OLD, strict=True))}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    parents = (own, own.prior, own.prior.prior, inherited, inherited.prior,
               inherited.prior.prior, inherited.prior.prior.prior,
               own.prior.prior.owning, own.prior.prior.literal)
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, *(path for parent in parents
                                               for path in (Path(parent.__file__), parent.CATALOGUE))),
                 runner_flags=('--sl',), fixture_renderer=own.prior.prior.literal.render)
