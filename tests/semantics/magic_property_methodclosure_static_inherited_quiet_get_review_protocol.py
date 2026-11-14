#!/usr/bin/env python3
"""Check inherited static-method scope, Shared ancestry and Empty cleanup."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_named_selector_quiet_get_review_protocol as prior

CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_inherited_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

PARENT = r'''
porigin_owner =/= porigin_requested
$class_at(S.CLASSES,porigin_requested) = (pclassdesc_child)
porigin_requested = PORIGIN n_unit pcpath_child
pclassdesc_target.METHODS = [pmethoddesc_method]
pclassdesc_target.PROPERTIES = eps /\ pclassdesc_target.CONSTANTS = eps /\ pclassdesc_target.INTERFACES = eps
~pclassdesc_target.ABSTRACT /\ ~pclassdesc_target.FINAL /\ ~pclassdesc_target.READONLY
phpType14_class = SEQUENCE eps /\ phpType24_class = INTEGER 0 /\ phpType42 = SEQUENCE eps
pclassdesc_child.KIND = "class"
pclassdesc_child.METHODS = eps /\ pclassdesc_child.PROPERTIES = eps /\ pclassdesc_child.CONSTANTS = eps /\ pclassdesc_child.INTERFACES = eps
~pclassdesc_child.ABSTRACT /\ ~pclassdesc_child.FINAL /\ ~pclassdesc_child.READONLY
pclassdesc_child.PARENT = (ptbytes_parent)
$class_named(S.CLASSNAMES,$ptlc(pclassdesc_target.NAME)) = (porigin_owner)
$class_named(S.CLASSNAMES,$ptlc(pclassdesc_child.NAME)) = (porigin_requested)
$class_link_at(S.LINKEDPARENTS,porigin_requested) = (SOURCE_PARENT porigin_owner)
$class_link_at(S.LINKEDPARENTS,porigin_owner) = eps
$class_links_valid(S)
$effective_method(S,porigin_requested,pmethoddesc_method.NAME,|S.CLASSES|) = (pmethoddesc_method)
$origin_node(S.SOURCES,porigin_requested) = (NStmtClass (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES text_child) metadata_child_name) phpType44_parent (SEQUENCE eps) (SEQUENCE eps) metadata_child)
pclassdesc_child.NAME = $base64(text_child)
$base64(text_parent) = ptbytes_parent
$base64(text_parent) =/= pclassdesc_target.NAME
$ptlc(ptbytes_parent) = $ptlc(pclassdesc_target.NAME)
$property_magic_cv_static_method_parent_selector(phpType44_parent,ptbytes_parent)
$property_magic_cv_inherited_static_methodclosure(S,n_closure)
~$property_magic_cv_static_method_clone_history(S,n_closure,porigin_method,porigin_site,porigin_owner)
~$property_magic_cv_static_method_parent(S,pclassdesc_child,phpType44_parent)
S_child_lexical = S[.CLOSURESCOPES = [pclosurescope[.LEXICAL = porigin_requested]]]
~$property_magic_cv_inherited_static_methodclosure(S_child_lexical,n_closure)
S_parent_called = S[.CLOSURESCOPES = [pclosurescope[.CALLED = porigin_owner]]]
~$property_magic_cv_inherited_static_methodclosure(S_parent_called,n_closure)
S_child_cache = S[.CLOSURECACHES = [pclosurecache_original,pclosurecache_intermediate,pclosurecache[.SCOPE = (BIND_CLASS porigin_requested)]]]
~$property_magic_cv_inherited_static_methodclosure(S_child_cache,n_closure)
~$property_empty_rv_kind(S_child_cache,S.OBJECTS[n_closure])
S_resolved_parent = S[.CLASSES = [pclassdesc_target,pclassdesc_child[.PARENT = (pclassdesc_target.NAME)],pclassdesc_receiver]]
~$property_magic_cv_inherited_static_methodclosure(S_resolved_parent,n_closure)
~$property_empty_rv_kind(S_resolved_parent,S.OBJECTS[n_closure])
'''.strip().splitlines()


def refusal(label, state):
    return [f'S_inherited_{label} = {state}',
            f'~$property_magic_cv_inherited_static_methodclosure(S_inherited_{label},n_closure)',
            f'~$property_magic_cv_static_methodclosure(S_inherited_{label},n_closure)',
            f'~$property_empty_rv_kind(S_inherited_{label},S.OBJECTS[n_closure])']


for label, links in (
    ('unlinked', 'eps'),
    ('wrong_link', '[CLASSLINK porigin_requested (SOURCE_PARENT pclassdesc_receiver.ORIGIN)]'),
    ('self_link', '[CLASSLINK porigin_requested (SOURCE_PARENT porigin_requested)]'),
    ('internal_link', '[CLASSLINK porigin_requested STDCLASS_PARENT]'),
):
    PARENT += refusal(label, f'S[.LINKEDPARENTS = {links}]')

for label, field, value in (
    ('child_name', 'NAME', 'pclassdesc_target.NAME'),
    ('child_case', 'NAME', '$base64(text_requested)'),
    ('child_trait', 'KIND', '"trait"'),
    ('child_interfaces', 'INTERFACES', '[pclassdesc_target.NAME]'),
    ('child_methods', 'METHODS', '[pmethoddesc_method]'),
    ('child_properties', 'PROPERTIES', 'pclassdesc_receiver.PROPERTIES'),
    ('child_abstract', 'ABSTRACT', 'true'),
    ('child_readonly', 'READONLY', 'true'),
):
    PARENT += refusal(label, f'S[.CLASSES = [pclassdesc_target,pclassdesc_child[.{field} = {value}],pclassdesc_receiver]]')

PARENT += refusal('parent_case',
                  'S[.CLASSES = [pclassdesc_target[.NAME = ptbytes_parent],pclassdesc_child,pclassdesc_receiver]]')

for label, parent, body in (
    ('child_absent_parent', 'ABSENT', 'eps'),
    ('child_relative_parent', 'NNameRelative (BYTES text_parent) metadata_extends', 'eps'),
    ('child_alias_parent', 'NName (BYTES "QWxpYXM=") metadata_extends', 'eps'),
    ('child_body', 'phpType44_parent', '[NStmtNop metadata_child]'),
    ('child_method', 'phpType44_parent', '[statement_method]'),
    ('child_trait_use', 'phpType44_parent', '[NStmtTraitUse (SEQUENCE ([NName (BYTES text_class) metadata_class_name])) (SEQUENCE eps) metadata_child]'),
):
    node = ('NStmtClass (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES text_child) metadata_child_name) '
            f'({parent}) (SEQUENCE eps) (SEQUENCE ({body})) metadata_child')
    PARENT += refusal(label, 'S[.SOURCES = [pcunit[.OCCURRENCES = '
                      f'$rc_review_occurrence(pcunit.OCCURRENCES,pcpath_child,{node})]]]')


def checks(old, row, parent_constructor):
    output = base64.b64decode(row['stdout_template_base64']).decode()
    prefix = output.split('RECEIVER;', 1)[0]
    parent, child = output.split(';', 1)[0].split('>')
    result = []
    for check in old:
        check = check.replace('METHODCLOSURE porigin_method porigin_site porigin_owner',
                              'METHODCLOSURE porigin_method porigin_site porigin_requested')
        check = check.replace('CALLED porigin_owner', 'CALLED porigin_requested')
        check = check.replace(',porigin_owner,eps)', ',porigin_requested,eps)')
        check = check.replace(',pclassdesc_receiver]', ',pclassdesc_child,pclassdesc_receiver]')
        if not check.startswith('pclassdesc_target.NAME = '):
            check = check.replace('pclassdesc_target.NAME', 'pclassdesc_child.NAME')
        if '$property_magic_cv_static_method_clone_history(' in check:
            check = check.replace('$property_magic_cv_static_method_clone_history(',
                                  '$property_magic_cv_inherited_static_method_clone_history(')
            check = check.replace(',porigin_site,porigin_owner)',
                                  ',porigin_site,porigin_requested,porigin_owner)')
        check = check.replace('STORE[n_counter] = DEFINED (PINT 1)', 'STORE[n_counter] = DEFINED (PINT 3)')
        check = check.replace('S_done.STORE[n_counter] = DEFINED (PINT 2)',
                              'S_done.STORE[n_counter] = DEFINED (PINT 4)')
        check = check.replace('"WARM;SOURCES_GONE;I;G;', '"' + prefix)
        check = check.replace('RECEIVER_GONE;STATIC;DONE;',
                              f'RECEIVER_GONE;{parent}>{child};STATIC;DONE;')
        check = check.replace('$throwable_field(S_catch,n_error,"line") = PINT 7',
                              '$throwable_field(S_catch,n_error,"line") = PINT 8')
        result.append(check)
        if check == '$class_at(S.CLASSES,porigin_owner) = (pclassdesc_target)':
            result.append('$class_at(S.CLASSES,porigin_requested) = (pclassdesc_child)')
        if check == 'S.CLASSES = [pclassdesc_target,pclassdesc_child,pclassdesc_receiver]':
            for parent_check in PARENT:
                result.append(parent_check)
                if parent_check.startswith('$origin_node(S.SOURCES,porigin_requested) = '):
                    result.append(f'phpType44_parent = {parent_constructor} (BYTES text_parent) metadata_extends')
    return result


CASES = {row['id']: dict(old, source=row['source'], checks=checks(old['checks'], row, constructor))
         for row, old, constructor in zip(ROWS, prior.CASES.values(),
                                           ('NName', 'NNameFullyQualified'), strict=True)}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, Path(prior.__file__), prior.CATALOGUE,
                  Path(prior.prior.__file__), prior.prior.CATALOGUE,
                  Path(prior.prior.owning.__file__), prior.prior.owning.CATALOGUE,
                  Path(prior.prior.literal.__file__), prior.prior.literal.CATALOGUE),
                 runner_flags=('--sl',), fixture_renderer=prior.prior.literal.render)
