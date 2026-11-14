#!/usr/bin/env python3
"""Check direct mixed-case and fully qualified empty-parent Get selectors."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_empty_parent_quiet_get_protocol as prior

CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_empty_parent_selector_quiet_get_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

PARENT = r'''
$origin_node(S.SOURCES,porigin_owner) = (NStmtClass phpType14_class phpType24_class phpType3_class phpType44_parent phpType42_class phpType23_class metadata_class)
pclassdesc_target.PARENT = (ptbytes_parent)
$base64(text_parent) = ptbytes_parent
$class_named(S.CLASSNAMES,$ptlc(ptbytes_parent)) = (porigin_empty_parent)
$class_link_at(S.LINKEDPARENTS,porigin_owner) = (SOURCE_PARENT porigin_empty_parent)
$class_at(S.CLASSES,porigin_empty_parent) = (pclassdesc_parent)
pclassdesc_parent.KIND = "class"
pclassdesc_parent.NAME =/= ptbytes_parent
$ptlc(pclassdesc_parent.NAME) = $ptlc(ptbytes_parent)
pclassdesc_parent.PARENT = eps /\ pclassdesc_parent.INTERFACES = eps
pclassdesc_parent.PROPERTIES = eps /\ pclassdesc_parent.METHODS = eps /\ pclassdesc_parent.CONSTANTS = eps
~pclassdesc_parent.ABSTRACT /\ ~pclassdesc_parent.FINAL /\ ~pclassdesc_parent.READONLY
$origin_node(S.SOURCES,porigin_empty_parent) = (NStmtClass (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES text_parent_name) metadata_parent_name) ABSENT (SEQUENCE eps) (SEQUENCE eps) metadata_parent)
pclassdesc_parent.NAME = $base64(text_parent_name)
$property_magic_cv_static_method_parent_selector(phpType44_parent,ptbytes_parent)
~$property_magic_cv_static_method_parent_selector(phpType44_parent,pclassdesc_parent.NAME)
~$property_magic_cv_static_method_parent_selector(NNameRelative (BYTES text_parent) metadata_extends,ptbytes_parent)
~$property_magic_cv_static_method_parent_selector(ABSENT,ptbytes_parent)
$property_magic_cv_static_method_parent(S,pclassdesc_target,phpType44_parent)
~$property_magic_cv_static_method_parent(S,pclassdesc_target,ABSENT)
~$property_magic_cv_static_method_parent(S,pclassdesc_parent,phpType44_parent)
~$property_magic_cv_static_method_parent(S,pclassdesc_target,NNameRelative (BYTES text_parent) metadata_extends)
~$property_magic_cv_static_method_parent(S,pclassdesc_target,NName (BYTES "T3RoZXI=") metadata_extends)
'''.strip().splitlines()

CASES = {}
for row, old, kind in zip(ROWS, prior.CASES.values(), ('NNameFullyQualified', 'NName'), strict=True):
    assert old['checks'][-len(prior.PARENT):] == prior.PARENT
    parent = [PARENT[0], f'phpType44_parent = {kind} (BYTES text_parent) metadata_extends', *PARENT[1:]]
    CASES[row['id']] = dict(old, source=row['source'], checks=old['checks'][:-len(prior.PARENT)] + parent)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, Path(prior.__file__), prior.CATALOGUE,
                  Path(prior.original.__file__), prior.original.CATALOGUE,
                  Path(prior.original.original.__file__), prior.original.original.CATALOGUE),
                 runner_flags=('--sl',))
