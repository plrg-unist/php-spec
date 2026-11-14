#!/usr/bin/env python3
"""Check raw method-name authority composed with quiet literal-class captures."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_literal_selector_quiet_get_protocol as prior

CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_literal_method_selector_quiet_get_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

METHOD = r'''
phpType20_method = NScalarString (BYTES text_selected) metadata_selected
$origin_child((porigin_site),[PCFIELD 1]) = (porigin_name)
porigin_name = PORIGIN n_site (pcpath_site ++ [PCFIELD 1])
$origin_node(S.SOURCES,porigin_name) = (phpType20_method)
ptbytes_method = $base64(text_selected)
$compiled_read(S,porigin_name) = (PSTRING ptbytes_method)
$property_magic_cv_static_method_site_name(S,porigin_site,phpType20_method,pmethoddesc_method.NAME)
$property_magic_cv_static_method_site_name(S,porigin_site,NIdentifier (BYTES text_selected) metadata_selected,pmethoddesc_method.NAME)
$scoped_source_method_origin(S,porigin_site,phpType20_method,pmethoddesc_method.NAME)
~$property_magic_cv_static_method_site_name(S,porigin_name,phpType20_method,pmethoddesc_method.NAME)
~$property_magic_cv_static_method_site_name(S,porigin_site,phpType20_method,pclassdesc_requested.NAME)
~$property_magic_cv_static_method_site_name(S[.SOURCES = eps],porigin_site,phpType20_method,pmethoddesc_method.NAME)
~$property_magic_cv_static_method_site_name(S,porigin_site,NScalarString (BYTES "Y291bnRlcg==") metadata_selected,pmethoddesc_method.NAME)
~$property_magic_cv_static_method_site_name(S,porigin_site,NExprVariable (BYTES text_selected) metadata_selected,pmethoddesc_method.NAME)
~$property_magic_cv_static_method_site_name(S,porigin_site,NExprBinaryOpConcat (NScalarString (BYTES text_selected) metadata_selected) (NScalarString (BYTES text_selected) metadata_selected) metadata_selected,pmethoddesc_method.NAME)
S_method_missing = S[.POOLS = [{UNIT n_site,CONSTANTS ([PCONSTANT (pcpath_site ++ [PCFIELD 0]) (PSTRING ptbytes_raw)])}]]
$compiled_read(S_method_missing,porigin_selector) = (PSTRING ptbytes_raw)
$property_magic_cv_static_method_site_selector(S_method_missing,porigin_site,phpType19_selector,porigin_requested,pclassdesc_requested.NAME)
$compiled_read(S_method_missing,porigin_name) = eps
$scoped_source_method_origin(S_method_missing,porigin_site,phpType20_method,pmethoddesc_method.NAME)
~$property_magic_cv_static_method_site_name(S_method_missing,porigin_site,phpType20_method,pmethoddesc_method.NAME)
~$property_magic_cv_static_methodclosure(S_method_missing,n_closure)
~$property_empty_rv_kind(S_method_missing,S_method_missing.OBJECTS[n_closure])
S_method_type = S[.POOLS = [{UNIT n_site,CONSTANTS ([PCONSTANT (pcpath_site ++ [PCFIELD 0]) (PSTRING ptbytes_raw),PCONSTANT (pcpath_site ++ [PCFIELD 1]) (PINT 17)])}]]
$compiled_read(S_method_type,porigin_selector) = (PSTRING ptbytes_raw)
$property_magic_cv_static_method_site_selector(S_method_type,porigin_site,phpType19_selector,porigin_requested,pclassdesc_requested.NAME)
$compiled_read(S_method_type,porigin_name) = (PINT 17)
$scoped_source_method_origin(S_method_type,porigin_site,phpType20_method,pmethoddesc_method.NAME)
~$property_magic_cv_static_method_site_name(S_method_type,porigin_site,phpType20_method,pmethoddesc_method.NAME)
~$property_magic_cv_static_methodclosure(S_method_type,n_closure)
~$property_empty_rv_kind(S_method_type,S_method_type.OBJECTS[n_closure])
$ptlc(ptbytes_method) =/= ptbytes_method
S_method_case = S[.POOLS = [{UNIT n_site,CONSTANTS ([PCONSTANT (pcpath_site ++ [PCFIELD 0]) (PSTRING ptbytes_raw),PCONSTANT (pcpath_site ++ [PCFIELD 1]) (PSTRING $ptlc(ptbytes_method))])}]]
$compiled_read(S_method_case,porigin_selector) = (PSTRING ptbytes_raw)
$property_magic_cv_static_method_site_selector(S_method_case,porigin_site,phpType19_selector,porigin_requested,pclassdesc_requested.NAME)
$compiled_read(S_method_case,porigin_name) = (PSTRING $ptlc(ptbytes_method))
$scoped_source_method_origin(S_method_case,porigin_site,phpType20_method,pmethoddesc_method.NAME)
~$property_magic_cv_static_method_site_name(S_method_case,porigin_site,phpType20_method,pmethoddesc_method.NAME)
~$property_magic_cv_static_methodclosure(S_method_case,n_closure)
~$property_empty_rv_kind(S_method_case,S_method_case.OBJECTS[n_closure])
S_method_slash = S[.POOLS = [{UNIT n_site,CONSTANTS ([PCONSTANT (pcpath_site ++ [PCFIELD 0]) (PSTRING ptbytes_raw),PCONSTANT (pcpath_site ++ [PCFIELD 1]) (PSTRING (92 :: ptbytes_method))])}]]
$compiled_read(S_method_slash,porigin_name) = (PSTRING (92 :: ptbytes_method))
$scoped_source_method_origin(S_method_slash,porigin_site,phpType20_method,pmethoddesc_method.NAME)
~$property_magic_cv_static_method_site_name(S_method_slash,porigin_site,phpType20_method,pmethoddesc_method.NAME)
~$property_magic_cv_static_methodclosure(S_method_slash,n_closure)
~$property_empty_rv_kind(S_method_slash,S_method_slash.OBJECTS[n_closure])
'''.strip().splitlines()


def checks(old):
    result = []
    for check in old:
        if check.startswith('$origin_node(S.SOURCES,porigin_site) = '):
            check = check.replace('(NIdentifier (BYTES text_selected) metadata_selected)',
                                  '(NScalarString (BYTES text_selected) metadata_selected)')
        result.append(check)
    return result + METHOD


CASES = {row['id']: dict(old, source=row['source'], checks=checks(old['checks']))
         for row, old in zip(ROWS, prior.CASES.values(), strict=True)}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    parents = (prior, prior.original, prior.inherited, prior.inherited.prior,
               prior.inherited.prior.prior, prior.inherited.prior.prior.prior)
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, *(path for parent in parents
                                               for path in (Path(parent.__file__), parent.CATALOGUE))),
                 runner_flags=('--sl',))
