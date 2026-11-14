#!/usr/bin/env python3
"""Check exact raw class-string authority and retained quiet Empty ownership."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_own_child_members_quiet_get_review_protocol as own
import magic_property_methodclosure_static_inherited_child_members_quiet_get_review_protocol as inherited

CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_literal_selector_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def refused(label, state):
    return [f'S_literal_{label} = {state}',
            f'~$property_magic_cv_static_method_site_selector(S_literal_{label},porigin_site,phpType19_selector,porigin_requested,pclassdesc_requested.NAME)',
            f'~$property_magic_cv_static_methodclosure(S_literal_{label},n_closure)',
            f'~$property_empty_rv_kind(S_literal_{label},S_literal_{label}.OBJECTS[n_closure])']


SELECTOR = r'''
$class_at(S.CLASSES,porigin_requested) = (pclassdesc_requested)
phpType19_selector = NScalarString (BYTES text_requested) metadata_requested
$origin_child((porigin_site),[PCFIELD 0]) = (porigin_selector)
porigin_selector = PORIGIN n_unit (pcpath_site ++ [PCFIELD 0])
$origin_node(S.SOURCES,porigin_selector) = (phpType19_selector)
ptbytes_raw = $base64(text_requested)
$compiled_read(S,porigin_selector) = (PSTRING ptbytes_raw)
$ptlc($ppcall_literal_name(ptbytes_raw)) = $ptlc(pclassdesc_requested.NAME)
$class_named(S.CLASSNAMES,$ptlc($ppcall_literal_name(ptbytes_raw))) = (porigin_requested)
$property_magic_cv_static_method_site_selector(S,porigin_site,phpType19_selector,porigin_requested,pclassdesc_requested.NAME)
~$property_magic_cv_static_method_selector(phpType19_selector,pclassdesc_requested.NAME)
~$property_magic_cv_static_method_site_selector(S,porigin_selector,phpType19_selector,porigin_requested,pclassdesc_requested.NAME)
~$property_magic_cv_static_method_site_selector(S,porigin_site,phpType19_selector,porigin_method,pclassdesc_requested.NAME)
~$property_magic_cv_static_method_site_selector(S,porigin_site,phpType19_selector,porigin_requested,pclassdesc_receiver.NAME)
~$property_magic_cv_static_method_site_selector(S[.SOURCES = eps],porigin_site,phpType19_selector,porigin_requested,pclassdesc_requested.NAME)
~$property_magic_cv_static_method_site_selector(S[.CLASSNAMES = eps],porigin_site,phpType19_selector,porigin_requested,pclassdesc_requested.NAME)
~$property_magic_cv_static_method_site_selector(S,porigin_site,NExprVariable (BYTES text_requested) metadata_requested,porigin_requested,pclassdesc_requested.NAME)
~$property_magic_cv_static_method_site_selector(S,porigin_site,NExprBinaryOpConcat (NScalarString (BYTES text_requested) metadata_requested) (NScalarString (BYTES text_requested) metadata_requested) metadata_requested,porigin_requested,pclassdesc_requested.NAME)
~$property_magic_cv_static_method_site_selector(S,porigin_site,NNameRelative (BYTES text_requested) metadata_requested,porigin_requested,pclassdesc_requested.NAME)
$ptlc(ptbytes_raw) =/= ptbytes_raw
S_literal_missing = S[.POOLS = eps]
$compiled_read(S_literal_missing,porigin_selector) = eps
~$scoped_class_literal(S_literal_missing[.ORIGIN = (porigin_site)],phpType19_selector)
$scoped_requested_site(S_literal_missing,porigin_site,phpType19_selector,porigin_requested,eps)
~$property_magic_cv_static_method_site_selector(S_literal_missing,porigin_site,phpType19_selector,porigin_requested,pclassdesc_requested.NAME)
~$property_magic_cv_static_methodclosure(S_literal_missing,n_closure)
~$property_empty_rv_kind(S_literal_missing,S_literal_missing.OBJECTS[n_closure])
S_literal_type = S[.POOLS = [{UNIT n_unit,CONSTANTS ([PCONSTANT (pcpath_site ++ [PCFIELD 0]) (PINT 17)])}]]
$compiled_read(S_literal_type,porigin_selector) = (PINT 17)
~$scoped_class_literal(S_literal_type[.ORIGIN = (porigin_site)],phpType19_selector)
$scoped_requested_site(S_literal_type,porigin_site,phpType19_selector,porigin_requested,eps)
~$property_magic_cv_static_method_site_selector(S_literal_type,porigin_site,phpType19_selector,porigin_requested,pclassdesc_requested.NAME)
~$property_magic_cv_static_methodclosure(S_literal_type,n_closure)
~$property_empty_rv_kind(S_literal_type,S_literal_type.OBJECTS[n_closure])
S_literal_case = S[.POOLS = [{UNIT n_unit,CONSTANTS ([PCONSTANT (pcpath_site ++ [PCFIELD 0]) (PSTRING $ptlc(ptbytes_raw))])}]]
$compiled_read(S_literal_case,porigin_selector) = (PSTRING $ptlc(ptbytes_raw))
$scoped_class_literal(S_literal_case[.ORIGIN = (porigin_site)],phpType19_selector)
$scoped_requested_site(S_literal_case,porigin_site,phpType19_selector,porigin_requested,eps)
~$property_magic_cv_static_method_site_selector(S_literal_case,porigin_site,phpType19_selector,porigin_requested,pclassdesc_requested.NAME)
~$property_magic_cv_static_methodclosure(S_literal_case,n_closure)
~$property_empty_rv_kind(S_literal_case,S_literal_case.OBJECTS[n_closure])
S_literal_no_code = S[.CODE = eps]
$compiled_read(S_literal_no_code,porigin_selector) = eps
$scoped_requested_site(S_literal_no_code,porigin_site,phpType19_selector,porigin_requested,eps)
~$property_magic_cv_static_method_site_selector(S_literal_no_code,porigin_site,phpType19_selector,porigin_requested,pclassdesc_requested.NAME)
~$property_magic_cv_static_methodclosure(S_literal_no_code,n_closure)
'''.strip().splitlines()


def checks(old, index):
    result = []
    constructor = 'NNameFullyQualified' if index == 0 else 'NName'
    target = 'pclassdesc_target' if index == 0 else 'pclassdesc_child'
    for check in old:
        if check.startswith('$property_magic_cv_static_method_selector('):
            continue
        if check.startswith('S_string = ') or '(S_string,' in check:
            continue
        if check.startswith('$origin_node(S.SOURCES,porigin_site) = ') or check.startswith('$scoped_requested_site(S,porigin_site,'):
            check = check.replace(constructor + ' (BYTES text_requested) metadata_requested',
                                  'NScalarString (BYTES text_requested) metadata_requested')
        check = check.replace('$ptlc($base64(text_requested))', '$ptlc($ppcall_literal_name($base64(text_requested)))')
        if check == '$code_name(pcode.NAMES,pcpath_site) = (($base64(text_requested),eps))':
            check = '$code_name(pcode.NAMES,pcpath_site) = eps'
        if check.startswith('~$property_magic_cv_static_methodclosure(S[.CODE = [pcode[.NAMES = '):
            check = check.removeprefix('~')
        if index == 1 and check == '~$property_magic_cv_static_method_parent(S,pclassdesc_child,phpType44_parent)':
            # The accepted own-child gate also authenticates this genuine parent.
            check = check.removeprefix('~')
        result.append(check)
    if index == 0:
        result.append('porigin_requested = porigin_owner')
    canonical = 'text_class' if index == 0 else 'text_child'
    result += [f'$property_magic_cv_static_method_selector(NName (BYTES {canonical}) metadata_requested,{target}.NAME)',
               f'$property_magic_cv_static_method_selector(NNameFullyQualified (BYTES {canonical}) metadata_requested,{target}.NAME)']
    result += SELECTOR
    pool_bytes = '92 :: ptbytes_raw' if index == 0 else '$ppcall_literal_name(ptbytes_raw)'
    result += [f'ptbytes_slash = {pool_bytes}', 'ptbytes_slash =/= ptbytes_raw',
               'S_literal_slash = S[.POOLS = [{UNIT n_unit,CONSTANTS ([PCONSTANT (pcpath_site ++ [PCFIELD 0]) (PSTRING ptbytes_slash)])}]]',
               '$compiled_read(S_literal_slash,porigin_selector) = (PSTRING ptbytes_slash)',
               '$scoped_class_literal(S_literal_slash[.ORIGIN = (porigin_site)],phpType19_selector)',
               '$scoped_requested_site(S_literal_slash,porigin_site,phpType19_selector,porigin_requested,eps)',
               '~$property_magic_cv_static_method_site_selector(S_literal_slash,porigin_site,phpType19_selector,porigin_requested,pclassdesc_requested.NAME)',
               '~$property_magic_cv_static_methodclosure(S_literal_slash,n_closure)',
               '~$property_empty_rv_kind(S_literal_slash,S_literal_slash.OBJECTS[n_closure])']
    for label, child in (
        ('child_value', 'NScalarString (BYTES "T3RoZXI=") metadata_requested'),
        ('child_metadata', 'NScalarString (BYTES text_requested) metadata_site'),
        ('child_variable', 'NExprVariable (BYTES text_requested) metadata_requested'),
    ):
        result += refused(label, 'S[.SOURCES = [pcunit[.OCCURRENCES = '
                          f'$rc_review_occurrence(pcunit.OCCURRENCES,pcpath_site ++ [PCFIELD 0],{child})]]]')
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
