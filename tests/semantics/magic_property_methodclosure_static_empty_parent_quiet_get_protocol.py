#!/usr/bin/env python3
"""Check own static-method Get transfer with a genuine empty source parent."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_named_selector_quiet_get_protocol as original

CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_empty_parent_quiet_get_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

PARENT = r'''
$origin_node(S.SOURCES,porigin_owner) = (NStmtClass phpType14_class phpType24_class phpType3_class phpType44_parent phpType42_class phpType23_class metadata_class)
phpType44_parent = NName (BYTES text_parent) metadata_parent
pclassdesc_target.PARENT = (ptbytes_parent)
$base64(text_parent) = ptbytes_parent
$class_named(S.CLASSNAMES,$ptlc(ptbytes_parent)) = (porigin_empty_parent)
$class_link_at(S.LINKEDPARENTS,porigin_owner) = (SOURCE_PARENT porigin_empty_parent)
$class_at(S.CLASSES,porigin_empty_parent) = (pclassdesc_parent)
pclassdesc_parent.NAME = ptbytes_parent /\ pclassdesc_parent.KIND = "class"
pclassdesc_parent.PARENT = eps /\ pclassdesc_parent.INTERFACES = eps
pclassdesc_parent.PROPERTIES = eps /\ pclassdesc_parent.METHODS = eps /\ pclassdesc_parent.CONSTANTS = eps
~pclassdesc_parent.ABSTRACT /\ ~pclassdesc_parent.FINAL /\ ~pclassdesc_parent.READONLY
$property_magic_cv_static_method_parent(S,pclassdesc_target,phpType44_parent)
~$property_magic_cv_static_method_parent(S,pclassdesc_target,ABSENT)
~$property_magic_cv_static_method_parent(S,pclassdesc_parent,phpType44_parent)
~$property_magic_cv_static_method_parent(S,pclassdesc_target,NNameFullyQualified (BYTES text_parent) metadata_parent)
~$property_magic_cv_static_method_parent(S,pclassdesc_target,NNameRelative (BYTES text_parent) metadata_parent)
'''.strip().splitlines()

CASES = {}
for row, old in zip(ROWS, original.CASES.values(), strict=True):
    CASES[row['id']] = dict(old, source=row['source'], checks=old['checks'] + PARENT)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, Path(original.__file__), original.CATALOGUE,
                  Path(original.original.__file__), original.original.CATALOGUE),
                 runner_flags=('--sl',))
