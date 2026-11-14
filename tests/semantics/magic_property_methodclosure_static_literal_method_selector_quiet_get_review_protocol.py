#!/usr/bin/env python3
"""Check exact literal method names without changing class or lifetime authority."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_own_child_members_quiet_get_review_protocol as own
import magic_property_methodclosure_static_inherited_child_members_quiet_get_review_protocol as inherited

CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_literal_method_selector_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def refusal(label, state):
    return [f'S_method_name_{label} = {state}',
            f'~$property_magic_cv_static_method_site_name(S_method_name_{label},porigin_site,phpType20_method,pmethoddesc_method.NAME)',
            f'~$property_magic_cv_static_methodclosure(S_method_name_{label},n_closure)',
            f'~$property_empty_rv_kind(S_method_name_{label},S_method_name_{label}.OBJECTS[n_closure])']


NAME = r'''
$class_at(S.CLASSES,porigin_requested) = (pclassdesc_requested)
phpType20_method = NScalarString (BYTES text_selected) metadata_selected
$origin_child((porigin_site),[PCFIELD 1]) = (porigin_name)
porigin_name = PORIGIN n_unit (pcpath_site ++ [PCFIELD 1])
$origin_node(S.SOURCES,porigin_name) = (phpType20_method)
ptbytes_method = $base64(text_selected)
$compiled_read(S,porigin_name) = (PSTRING ptbytes_method)
$ptlc(ptbytes_method) = $ptlc(pmethoddesc_method.NAME)
$ptlc(ptbytes_method) =/= ptbytes_method
$scoped_source_method_origin(S,porigin_site,phpType20_method,pmethoddesc_method.NAME)
$property_magic_cv_static_method_site_selector(S,porigin_site,phpType19_class,porigin_requested,pclassdesc_requested.NAME)
$property_magic_cv_static_method_site_name(S,porigin_site,phpType20_method,pmethoddesc_method.NAME)
$property_magic_cv_static_method_site_name(S,porigin_site,NIdentifier (BYTES text_selected) metadata_selected,pmethoddesc_method.NAME)
$property_magic_cv_static_method_site_name(S[.POOLS = eps],porigin_site,NIdentifier (BYTES text_selected) metadata_selected,pmethoddesc_method.NAME)
~$property_magic_cv_static_method_site_name(S,porigin_name,phpType20_method,pmethoddesc_method.NAME)
~$property_magic_cv_static_method_site_name(S,porigin_site,phpType20_method,pclassdesc_requested.NAME)
~$property_magic_cv_static_method_site_name(S[.SOURCES = eps],porigin_site,phpType20_method,pmethoddesc_method.NAME)
~$property_magic_cv_static_method_site_name(S,porigin_site,NExprVariable (BYTES text_selected) metadata_selected,pmethoddesc_method.NAME)
~$property_magic_cv_static_method_site_name(S,porigin_site,NExprBinaryOpConcat (NScalarString (BYTES text_selected) metadata_selected) (NScalarString (BYTES text_selected) metadata_selected) metadata_selected,pmethoddesc_method.NAME)
'''.strip().splitlines()


def checks(old, index):
    result = []
    for check in old:
        check = check.replace('NIdentifier (BYTES text_selected) metadata_selected',
                              'NScalarString (BYTES text_selected) metadata_selected')
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
    ):
        pools = 'eps' if constants is None else '[{UNIT n_unit,CONSTANTS (' + constants + ')}]'
        state = f'S[.POOLS = {pools}]'
        result += [f'S_method_name_{label} = {state}',
                   f'$compiled_read(S_method_name_{label},porigin_name) = {expected}',
                   f'$property_magic_cv_static_method_site_selector(S_method_name_{label},porigin_site,phpType19_class,porigin_requested,pclassdesc_requested.NAME)',
                   f'$scoped_requested_site(S_method_name_{label},porigin_site,phpType19_class,porigin_requested,eps)',
                   f'$scoped_source_method_origin(S_method_name_{label},porigin_site,phpType20_method,pmethoddesc_method.NAME)',
                   f'~$property_magic_cv_static_method_site_name(S_method_name_{label},porigin_site,phpType20_method,pmethoddesc_method.NAME)',
                   f'~$property_magic_cv_static_methodclosure(S_method_name_{label},n_closure)',
                   f'~$property_empty_rv_kind(S_method_name_{label},S_method_name_{label}.OBJECTS[n_closure])']
    for label, child in (
        ('child_value', 'NScalarString (BYTES "T3RoZXI=") metadata_selected'),
        ('child_metadata', 'NScalarString (BYTES text_selected) metadata_site'),
        ('child_variable', 'NExprVariable (BYTES text_selected) metadata_selected'),
    ):
        result += refusal(label, 'S[.SOURCES = [pcunit[.OCCURRENCES = '
                          f'$rc_review_occurrence(pcunit.OCCURRENCES,pcpath_site ++ [PCFIELD 1],{child})]]]')
    result += refusal('no_code', 'S[.CODE = eps]')
    raw_name = 'CoUnTeR' if index == 0 else 'cOunter'
    encoded = base64.b64encode(('\\' + raw_name).encode()).decode()
    scalar = f'NScalarString (BYTES "{encoded}") metadata_selected'
    site = ('NExprStaticCall phpType19_class (' + scalar + ') '
            '(SEQUENCE ([NVariadicPlaceholder metadata_placeholder])) metadata_site')
    occurrences = f'$rc_review_occurrence(pcunit.OCCURRENCES,pcpath_site,{site})'
    occurrences = f'$rc_review_occurrence({occurrences},pcpath_site ++ [PCFIELD 1],{scalar})'
    result += [
        '$base64(text_selected) = $ptascii("' + raw_name + '")',
        'ptbytes_method_slash = 92 :: ptbytes_method',
        f'phpType20_slash = {scalar}',
        '$base64("' + encoded + '") = ptbytes_method_slash',
        'S_method_name_slash = S[.SOURCES = [pcunit[.OCCURRENCES = ' + occurrences + ']]][.POOLS = [{UNIT n_unit,CONSTANTS ([PCONSTANT (pcpath_site ++ [PCFIELD 1]) (PSTRING ptbytes_method_slash)])}]]',
        '$origin_node(S_method_name_slash.SOURCES,porigin_name) = (phpType20_slash)',
        '$compiled_read(S_method_name_slash,porigin_name) = (PSTRING ptbytes_method_slash)',
        '~$scoped_source_method_origin(S_method_name_slash,porigin_site,phpType20_slash,pmethoddesc_method.NAME)',
        '~$property_magic_cv_static_method_site_name(S_method_name_slash,porigin_site,phpType20_slash,pmethoddesc_method.NAME)',
        '~$property_magic_cv_static_methodclosure(S_method_name_slash,n_closure)',
        '~$property_empty_rv_kind(S_method_name_slash,S_method_name_slash.OBJECTS[n_closure])',
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
