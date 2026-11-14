#!/usr/bin/env python3
"""Check direct static-method selector spelling through quiet Get transfer."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_quiet_get_protocol as original

CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_named_selector_quiet_get_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

SELECTOR = r'''
$class_at(S.CLASSES,porigin_owner) = (pclassdesc_target)
porigin_site = PORIGIN n_site pcpath_site
$origin_node(S.SOURCES,porigin_site) = (NExprStaticCall phpType19_selector (NIdentifier (BYTES text_selected) metadata_selected) (SEQUENCE ([NVariadicPlaceholder metadata_placeholder])) metadata_site)
$property_magic_cv_static_method_selector(phpType19_selector,pclassdesc_target.NAME)
$ptlc($base64(text_selected)) = $ptlc(pmethoddesc_method.NAME)
~$ppscoped_keyword(phpType19_selector)
$scoped_requested_site(S,porigin_site,phpType19_selector,porigin_owner,eps)
$goto_source_owner($all_functions(S),n_site,pcpath_site) = eps
$closure_source_class(S,porigin_site) = eps
S.CODE = [pcode_target]
pcode_target.UNIT = n_site
$code_name(pcode_target.NAMES,pcpath_site) = ((ptbytes_requested,eps))
$ptlc(ptbytes_requested) = $ptlc(pclassdesc_target.NAME)
~$property_magic_cv_static_methodclosure(S[.CODE = [pcode_target[.NAMES = eps]]],n_closure)
~$property_magic_cv_static_methodclosure(S[.CLASSNAMES = eps],n_closure)
~$property_magic_cv_static_method_selector(NNameRelative (BYTES text_selected) metadata_selected,pmethoddesc_method.NAME)
~$property_magic_cv_static_method_selector(NScalarString (BYTES text_selected) metadata_selected,pmethoddesc_method.NAME)
~$property_magic_cv_static_method_selector(NExprVariable (BYTES text_selected) metadata_selected,pmethoddesc_method.NAME)
~$property_magic_cv_static_method_selector(NName (BYTES text_selected) metadata_selected,pclassdesc_target.NAME)
'''.strip().splitlines()

CASES = {}
for row, old in zip(ROWS, original.CASES.values(), strict=True):
    CASES[row['id']] = dict(old, source=row['source'], checks=old['checks'] + SELECTOR)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, Path(original.__file__), original.CATALOGUE),
                 runner_flags=('--sl',))
