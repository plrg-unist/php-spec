#!/usr/bin/env python3
"""Check inherited static Get captures with distinct declaring and called scopes."""
import argparse
import hashlib
import json
import re
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_quiet_get_protocol as prior

CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_inherited_quiet_get_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

DECLARATION = r'''
porigin_owner =/= porigin_requested
$class_at(S.CLASSES,porigin_owner) = (pclassdesc_parent)
$class_at(S.CLASSES,porigin_requested) = (pclassdesc_child)
S.CLASSES = [pclassdesc_parent,pclassdesc_child,pclassdesc_receiver]
$class_named(S.CLASSNAMES,$ptlc(pclassdesc_parent.NAME)) = (porigin_owner)
$class_named(S.CLASSNAMES,$ptlc(pclassdesc_child.NAME)) = (porigin_requested)
$class_link_at(S.LINKEDPARENTS,porigin_requested) = (SOURCE_PARENT porigin_owner)
$effective_method(S,porigin_requested,pmethoddesc_method.NAME,|S.CLASSES|) = (pmethoddesc_method)
pclassdesc_parent.KIND = "class" /\ pclassdesc_parent.PARENT = eps /\ pclassdesc_parent.INTERFACES = eps
pclassdesc_parent.PROPERTIES = eps /\ pclassdesc_parent.METHODS = [pmethoddesc_method] /\ pclassdesc_parent.CONSTANTS = eps
~pclassdesc_parent.ABSTRACT /\ ~pclassdesc_parent.FINAL /\ ~pclassdesc_parent.READONLY
pclassdesc_child.KIND = "class" /\ pclassdesc_child.INTERFACES = eps
pclassdesc_child.PROPERTIES = eps /\ pclassdesc_child.METHODS = eps /\ pclassdesc_child.CONSTANTS = eps
~pclassdesc_child.ABSTRACT /\ ~pclassdesc_child.FINAL /\ ~pclassdesc_child.READONLY
pclassdesc_child.PARENT = (ptbytes_parent)
$ptlc(ptbytes_parent) = $ptlc(pclassdesc_parent.NAME)
porigin_owner = PORIGIN n_unit pcpath_owner
porigin_requested = PORIGIN n_unit pcpath_child
porigin_method = PORIGIN n_unit pcpath_method
pcpath_method = pcpath_owner ++ [PCFIELD 5,PCINDEX 0]
pmethoddesc_method.FUNCTION.BODY = pcpath_method ++ [PCFIELD 6]
$origin_node(S.SOURCES,porigin_owner) = (NStmtClass (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES text_owner) metadata_owner_name) ABSENT (SEQUENCE eps) (SEQUENCE ([statement_method])) metadata_owner)
pclassdesc_parent.NAME = $base64(text_owner)
$origin_node(S.SOURCES,porigin_method) = (statement_method)
$origin_node(S.SOURCES,porigin_requested) = (NStmtClass (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES text_child) metadata_child_name) phpType44_parent (SEQUENCE eps) (SEQUENCE eps) metadata_child)
pclassdesc_child.NAME = $base64(text_child)
$property_magic_cv_static_method_parent_selector(phpType44_parent,ptbytes_parent)
'''.strip().splitlines()

GUARDS = r'''
$property_magic_cv_inherited_static_methodclosure(S,n_closure)
~$property_magic_cv_inherited_static_method_clone_history(S,n_closure,porigin_method,porigin_site,porigin_requested,porigin_owner)
S_requested_owner = S[.OBJECTS[n_closure] = METHODCLOSURE porigin_method porigin_site porigin_owner pmethodcapture?]
~$property_magic_cv_inherited_static_methodclosure(S_requested_owner,n_closure)
~$property_magic_cv_static_methodclosure(S_requested_owner,n_closure)
S_lexical_child = S[.CLOSURESCOPES = [pclosurescope[.LEXICAL = porigin_requested]]]
~$property_magic_cv_inherited_static_methodclosure(S_lexical_child,n_closure)
S_called_parent = S[.CLOSURESCOPES = [pclosurescope[.CALLED = porigin_owner]]]
~$property_magic_cv_inherited_static_methodclosure(S_called_parent,n_closure)
S_cache_child = S[.CLOSURECACHES = [pclosurecache[.SCOPE = (BIND_CLASS porigin_requested)]]]
~$property_magic_cv_inherited_static_methodclosure(S_cache_child,n_closure)
S_no_parent_link = S[.LINKEDPARENTS = eps]
~$property_magic_cv_inherited_static_methodclosure(S_no_parent_link,n_closure)
S_child_method = S[.CLASSES = [pclassdesc_parent,pclassdesc_child[.METHODS = [pmethoddesc_method]],pclassdesc_receiver]]
~$property_magic_cv_inherited_static_methodclosure(S_child_method,n_closure)
S_parent_ancestry = S[.CLASSES = [pclassdesc_parent[.PARENT = (pclassdesc_child.NAME)],pclassdesc_child,pclassdesc_receiver]]
~$property_magic_cv_inherited_static_methodclosure(S_parent_ancestry,n_closure)
S_parent_final = S[.CLASSES = [pclassdesc_parent[.FINAL = true],pclassdesc_child,pclassdesc_receiver]]
~$property_magic_cv_inherited_static_methodclosure(S_parent_final,n_closure)
S_parent_name = S[.CLASSES = [pclassdesc_parent[.NAME = pclassdesc_child.NAME],pclassdesc_child,pclassdesc_receiver]]
~$property_magic_cv_inherited_static_methodclosure(S_parent_name,n_closure)
'''.strip().splitlines()


def events(parts):
    return '[' + ','.join('OUTPUT $ptascii(' + json.dumps(part) + ')' for part in parts) + ']'


def checks(old, base, child):
    result = []
    for check in old:
        if check == 'S.OBJECTS[n_closure] = METHODCLOSURE porigin_method porigin_site porigin_owner pmethodcapture?':
            check = check.replace('porigin_owner', 'porigin_requested')
        if check.startswith('pclosurescope = '):
            check = check.replace('CALLED porigin_owner', 'CALLED porigin_requested')
        if check.startswith('S.EVENTS = '):
            check = 'S.EVENTS = ' + events((base, '>', base, ';', 'WARM;', 'I;', 'G;'))
        if check.startswith('S_done.EVENTS = '):
            check = 'S_done.EVENTS = S.EVENTS ++ ' + events((
                'RECEIVER;', 'SAME;', base, '>', child, ';', 'RESULT;',
                base, '>', child, ';', 'STATIC;', 'CAPTURE;', 'RETIRED;', 'DONE;'))
        result.append(check)
        if check == 'pmethoddesc_method.OWNER = porigin_owner':
            result += DECLARATION
        if check == '$property_magic_cv_static_methodclosure(S,n_closure)':
            result += GUARDS
        if check == '$property_magic_cv_static_methodclosure(S_clone,n_clone)':
            result += [
                '$property_magic_cv_inherited_static_methodclosure(S_clone,n_clone)',
                '$property_magic_cv_inherited_static_method_clone_history(S_clone,n_clone,porigin_method,porigin_site,porigin_requested,porigin_owner)',
                '~$property_magic_cv_static_method_clone_history(S_clone,n_clone,porigin_method,porigin_site,porigin_requested)',
            ]
    return result


CASES = {}
for row, old in zip(ROWS, prior.CASES.values(), strict=True):
    base, child, _ = re.findall(r'\bclass ([A-Za-z_]\w*)', row['source'])
    CASES[row['id']] = dict(old, source=row['source'], checks=checks(old['checks'], base, child))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, Path(prior.__file__), prior.CATALOGUE),
                 runner_flags=('--sl',))
