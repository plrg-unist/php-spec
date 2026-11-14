#!/usr/bin/env python3
"""Check raw literal class-string capture authority through quiet Get transfer."""
import argparse
import hashlib
import json
import re
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_quiet_get_protocol as original
import magic_property_methodclosure_static_inherited_child_members_quiet_get_protocol as inherited

CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_literal_selector_quiet_get_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

SELECTOR = r'''
$class_at(S.CLASSES,porigin_requested) = (pclassdesc_requested)
porigin_site = PORIGIN n_site pcpath_site
$origin_node(S.SOURCES,porigin_site) = (NExprStaticCall phpType19_selector (NIdentifier (BYTES text_selected) metadata_selected) (SEQUENCE ([NVariadicPlaceholder metadata_placeholder])) metadata_site)
phpType19_selector = NScalarString (BYTES text_selector) metadata_selector
$origin_child((porigin_site),[PCFIELD 0]) = (porigin_selector)
porigin_selector = PORIGIN n_site (pcpath_site ++ [PCFIELD 0])
$origin_node(S.SOURCES,porigin_selector) = (phpType19_selector)
ptbytes_raw = $base64(text_selector)
$compiled_read(S,porigin_selector) = (PSTRING ptbytes_raw)
$ptlc($ppcall_literal_name(ptbytes_raw)) = $ptlc(pclassdesc_requested.NAME)
$class_named(S.CLASSNAMES,$ptlc($ppcall_literal_name(ptbytes_raw))) = (porigin_requested)
$property_magic_cv_static_method_site_selector(S,porigin_site,phpType19_selector,porigin_requested,pclassdesc_requested.NAME)
~$property_magic_cv_static_method_selector(phpType19_selector,pclassdesc_requested.NAME)
$ptlc($base64(text_selected)) = $ptlc(pmethoddesc_method.NAME)
~$ppscoped_keyword(phpType19_selector)
$scoped_requested_site(S,porigin_site,phpType19_selector,porigin_requested,eps)
$goto_source_owner($all_functions(S),n_site,pcpath_site) = eps
$closure_source_class(S,porigin_site) = eps
S.CODE = [pcode_target]
pcode_target.UNIT = n_site
$code_name(pcode_target.NAMES,pcpath_site) = eps
$property_magic_cv_static_methodclosure(S[.CODE = [pcode_target[.NAMES = eps]]],n_closure)
~$property_magic_cv_static_method_site_selector(S,porigin_site,phpType19_selector,porigin_method,pclassdesc_requested.NAME)
~$property_magic_cv_static_method_site_selector(S,porigin_selector,phpType19_selector,porigin_requested,pclassdesc_requested.NAME)
~$property_magic_cv_static_method_site_selector(S,porigin_site,phpType19_selector,porigin_requested,pmethoddesc_method.NAME)
~$property_magic_cv_static_method_site_selector(S[.SOURCES = eps],porigin_site,phpType19_selector,porigin_requested,pclassdesc_requested.NAME)
~$property_magic_cv_static_method_site_selector(S[.CLASSNAMES = eps],porigin_site,phpType19_selector,porigin_requested,pclassdesc_requested.NAME)
~$property_magic_cv_static_methodclosure(S[.CLASSNAMES = eps],n_closure)
~$property_magic_cv_static_method_site_selector(S,porigin_site,NScalarString (BYTES "d3Jvbmc=") metadata_selector,porigin_requested,pclassdesc_requested.NAME)
~$property_magic_cv_static_method_site_selector(S,porigin_site,NExprVariable (BYTES text_selector) metadata_selector,porigin_requested,pclassdesc_requested.NAME)
~$property_magic_cv_static_method_site_selector(S,porigin_site,NExprBinaryOpConcat (NScalarString (BYTES text_selector) metadata_selector) (NScalarString (BYTES text_selector) metadata_selector) metadata_selector,porigin_requested,pclassdesc_requested.NAME)
~$property_magic_cv_static_method_site_selector(S,porigin_site,NNameRelative (BYTES text_selector) metadata_selector,porigin_requested,pclassdesc_requested.NAME)
~$property_magic_cv_static_method_selector(NExprVariable (BYTES text_selector) metadata_selector,pclassdesc_requested.NAME)
~$property_magic_cv_static_method_selector(NScalarString (BYTES text_selector) metadata_selector,pclassdesc_requested.NAME)
S_missing = S[.POOLS = eps]
$compiled_read(S_missing,porigin_selector) = eps
~$scoped_class_literal(S_missing[.ORIGIN = (porigin_site)],phpType19_selector)
$scoped_requested_site(S_missing,porigin_site,phpType19_selector,porigin_requested,eps)
~$property_magic_cv_static_method_site_selector(S_missing,porigin_site,phpType19_selector,porigin_requested,pclassdesc_requested.NAME)
~$property_magic_cv_static_methodclosure(S_missing,n_closure)
~$property_empty_rv_kind(S_missing,S_missing.OBJECTS[n_closure])
S_wrong_type = S[.POOLS = [{UNIT n_site,CONSTANTS ([PCONSTANT (pcpath_site ++ [PCFIELD 0]) (PINT 17)])}]]
$compiled_read(S_wrong_type,porigin_selector) = (PINT 17)
~$scoped_class_literal(S_wrong_type[.ORIGIN = (porigin_site)],phpType19_selector)
$scoped_requested_site(S_wrong_type,porigin_site,phpType19_selector,porigin_requested,eps)
~$property_magic_cv_static_method_site_selector(S_wrong_type,porigin_site,phpType19_selector,porigin_requested,pclassdesc_requested.NAME)
~$property_magic_cv_static_methodclosure(S_wrong_type,n_closure)
~$property_empty_rv_kind(S_wrong_type,S_wrong_type.OBJECTS[n_closure])
$ptlc(ptbytes_raw) =/= ptbytes_raw
S_case_read = S[.POOLS = [{UNIT n_site,CONSTANTS ([PCONSTANT (pcpath_site ++ [PCFIELD 0]) (PSTRING $ptlc(ptbytes_raw))])}]]
$compiled_read(S_case_read,porigin_selector) = (PSTRING $ptlc(ptbytes_raw))
$scoped_class_literal(S_case_read[.ORIGIN = (porigin_site)],phpType19_selector)
$scoped_requested_site(S_case_read,porigin_site,phpType19_selector,porigin_requested,eps)
~$property_magic_cv_static_method_site_selector(S_case_read,porigin_site,phpType19_selector,porigin_requested,pclassdesc_requested.NAME)
~$property_magic_cv_static_methodclosure(S_case_read,n_closure)
~$property_empty_rv_kind(S_case_read,S_case_read.OBJECTS[n_closure])
S_no_code = S[.CODE = eps]
$compiled_read(S_no_code,porigin_selector) = eps
$scoped_requested_site(S_no_code,porigin_site,phpType19_selector,porigin_requested,eps)
~$property_magic_cv_static_method_site_selector(S_no_code,porigin_site,phpType19_selector,porigin_requested,pclassdesc_requested.NAME)
~$property_magic_cv_static_methodclosure(S_no_code,n_closure)
'''.strip().splitlines()


def checks(old, index):
    result = []
    for check in old:
        if 'S_member_' in check or 'S_child_member_' in check:
            continue
        if index == 1:
            old_names = re.findall(r'\bclass ([A-Za-z_]\w*)', inherited.ROWS[1]['source'])
            new_names = re.findall(r'\bclass ([A-Za-z_]\w*)', ROWS[1]['source'])
            for before, after in zip(old_names, new_names, strict=True):
                check = check.replace(before, after)
            if check == 'pclosurecache = {OBJECT n_closure,FUNCTION porigin_method,SOURCE eps,SCOPE (BIND_CLASS porigin_owner),CACHE (CACHE_SHARED)}':
                result += [
                    'pclosurecache = {OBJECT n_closure,FUNCTION porigin_method,SOURCE (n_source),SCOPE (BIND_CLASS porigin_owner),CACHE (CACHE_SHARED)}',
                    'S.CLOSURECACHES = [pclosurecache_source,pclosurecache]',
                    'pclosurecache_source = {OBJECT n_source,FUNCTION porigin_method,SOURCE eps,SCOPE (BIND_CLASS porigin_owner),CACHE (CACHE_SHARED)}',
                    '$(n_source < n_closure)',
                    'S.OBJECTS[n_source] = S.OBJECTS[n_closure]',
                    '~((HOBJECT n_source) <- S.ALLOCATIONS)',
                    '$closure_scope_at(S.CLOSURESCOPES,n_source) = eps',
                    '$lookup(S.ENV,$ptascii("seed")) = eps',
                    '$property_magic_cv_inherited_static_method_clone_history(S,n_closure,porigin_method,porigin_site,porigin_requested,porigin_owner)',
                ]
                continue
            if check == '~$property_magic_cv_inherited_static_method_clone_history(S,n_closure,porigin_method,porigin_site,porigin_requested,porigin_owner)':
                continue
            check = check.replace('CLOSURECACHES = [pclosurecache[.', 'CLOSURECACHES = [pclosurecache_source,pclosurecache[.')
        result.append(check)
    if index == 0:
        result.append('porigin_requested = porigin_owner')
    result += SELECTOR
    if index == 1:
        result += [
            'ptbytes_raw = 92 :: ptbytes_normalized',
            '$ppcall_literal_name(ptbytes_raw) = ptbytes_normalized',
            'S_slash_read = S[.POOLS = [{UNIT n_site,CONSTANTS ([PCONSTANT (pcpath_site ++ [PCFIELD 0]) (PSTRING ptbytes_normalized)])}]]',
            '$compiled_read(S_slash_read,porigin_selector) = (PSTRING ptbytes_normalized)',
            '$scoped_requested_site(S_slash_read,porigin_site,phpType19_selector,porigin_requested,eps)',
            '~$property_magic_cv_static_method_site_selector(S_slash_read,porigin_site,phpType19_selector,porigin_requested,pclassdesc_requested.NAME)',
            '~$property_magic_cv_static_methodclosure(S_slash_read,n_closure)',
            '~$property_empty_rv_kind(S_slash_read,S_slash_read.OBJECTS[n_closure])',
        ]
    return result


old_cases = (next(iter(original.CASES.values())), list(inherited.CASES.values())[1])
CASES = {row['id']: dict(old, source=row['source'], checks=checks(old['checks'], index))
         for index, (row, old) in enumerate(zip(ROWS, old_cases, strict=True))}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    parents = (original, inherited, inherited.prior, inherited.prior.prior, inherited.prior.prior.prior)
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, *(path for parent in parents
                                               for path in (Path(parent.__file__), parent.CATALOGUE))),
                 runner_flags=('--sl',))
