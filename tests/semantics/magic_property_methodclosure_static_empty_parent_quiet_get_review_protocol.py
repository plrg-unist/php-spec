#!/usr/bin/env python3
"""Check empty source-parent authority and unchanged static-method Get lifetimes."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_named_selector_quiet_get_review_protocol as prior

CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_empty_parent_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

PARENT = r'''
phpType44_parent = NName (BYTES text_parent) metadata_extends
pclassdesc_target.PARENT = (ptbytes_parent)
$base64(text_parent) = ptbytes_parent
$class_named(S.CLASSNAMES,$ptlc(ptbytes_parent)) = (porigin_parent)
$class_at(S.CLASSES,porigin_parent) = (pclassdesc_parent)
porigin_parent = PORIGIN n_unit pcpath_parent
$class_link_at(S.LINKEDPARENTS,porigin_owner) = (SOURCE_PARENT porigin_parent)
$class_link_at(S.LINKEDPARENTS,porigin_parent) = eps
$class_links_valid(S)
S_extra_root_link = S[.LINKEDPARENTS = S.LINKEDPARENTS ++ [CLASSLINK porigin_parent STDCLASS_PARENT]]
~$class_links_valid(S_extra_root_link)
$origin_node(S.SOURCES,porigin_parent) = (statement_parent)
statement_parent = NStmtClass (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES text_parent) metadata_parent_name) ABSENT (SEQUENCE eps) (SEQUENCE eps) metadata_parent
pclassdesc_parent.NAME = ptbytes_parent /\ pclassdesc_parent.KIND = "class"
pclassdesc_parent.PARENT = eps /\ pclassdesc_parent.INTERFACES = eps
pclassdesc_parent.PROPERTIES = eps /\ pclassdesc_parent.METHODS = eps /\ pclassdesc_parent.CONSTANTS = eps
~pclassdesc_parent.ABSTRACT /\ ~pclassdesc_parent.FINAL /\ ~pclassdesc_parent.READONLY
$property_magic_cv_static_method_parent(S,pclassdesc_target,phpType44_parent)
$property_magic_cv_static_method_parent(S,pclassdesc_parent,ABSENT)
~$property_magic_cv_static_method_parent(S,pclassdesc_target,ABSENT)
~$property_magic_cv_static_method_parent(S,pclassdesc_parent,phpType44_parent)
$property_magic_cv_static_method_parent(S,pclassdesc_target,NNameFullyQualified (BYTES text_parent) metadata_extends)
~$property_magic_cv_static_method_parent(S,pclassdesc_target,NNameRelative (BYTES text_parent) metadata_extends)
~$property_magic_cv_static_method_parent(S,pclassdesc_target,NName (BYTES "T3RoZXI=") metadata_extends)
~$property_magic_cv_static_method_parent(S[.CLASSES = [pclassdesc_target,pclassdesc_receiver]],pclassdesc_target,phpType44_parent)
~$property_magic_cv_static_method_parent(S[.CLASSNAMES = eps],pclassdesc_target,phpType44_parent)
~$property_magic_cv_static_method_parent(S[.CLASSNAMES = [($ptlc(ptbytes_parent),porigin_owner)]],pclassdesc_target,phpType44_parent)
~$property_magic_cv_static_method_parent(S[.SOURCES = eps],pclassdesc_target,phpType44_parent)
pclassconstantdesc_forged = {ORIGIN porigin_parent,OWNER porigin_parent,OWNERNAME ptbytes_parent,NAME $ptascii("constant"),VISIBILITY PROPERTY_PUBLIC,FINAL false,TYPE eps,INITIALIZER porigin_parent,FOLDED false,LINE 2}
'''.strip().splitlines()


def parent_state(label, state):
    return [
        f'S_parent_{label} = {state}',
        f'~$property_magic_cv_static_method_parent(S_parent_{label},pclassdesc_target,phpType44_parent)',
        f'~$property_magic_cv_static_methodclosure(S_parent_{label},n_closure)',
        f'~$property_empty_rv_kind(S_parent_{label},S.OBJECTS[n_closure])',
    ]


for label, link in (
    ('unlinked', 'eps'),
    ('wrong_link', '[CLASSLINK porigin_owner (SOURCE_PARENT pclassdesc_receiver.ORIGIN)]'),
    ('self_link', '[CLASSLINK porigin_owner (SOURCE_PARENT porigin_owner)]'),
    ('internal_link', '[CLASSLINK porigin_owner STDCLASS_PARENT]'),
):
    PARENT += parent_state(label, f'S[.LINKEDPARENTS = {link}]')

for label, field in (
    ('absent', 'ABSENT'),
    ('wrong', 'NName (BYTES "T3RoZXI=") metadata_extends'),
    ('fully_qualified', 'NNameFullyQualified (BYTES text_parent) metadata_extends'),
    ('relative', 'NNameRelative (BYTES text_parent) metadata_extends'),
):
    child = ('NStmtClass phpType14_class phpType24_class '
             '(NIdentifier (BYTES text_class) metadata_class_name) '
             f'({field}) phpType42 (SEQUENCE ([statement_method])) metadata_class')
    prefix = '' if label == 'fully_qualified' else '~'
    PARENT += [
        f'S_child_{label} = S[.SOURCES = [pcunit[.OCCURRENCES = $rc_review_occurrence(pcunit.OCCURRENCES,pcpath_class,{child})]]]',
        f'{prefix}$property_magic_cv_static_methodclosure(S_child_{label},n_closure)',
        f'{prefix}$property_empty_rv_kind(S_child_{label},S.OBJECTS[n_closure])',
    ]

for label, field, value in (
    ('name', 'NAME', 'pclassdesc_receiver.NAME'),
    ('trait', 'KIND', '"trait"'),
    ('interface', 'KIND', '"interface"'),
    ('ancestry', 'PARENT', '(pclassdesc_receiver.NAME)'),
    ('interfaces', 'INTERFACES', '[pclassdesc_receiver.NAME]'),
    ('properties', 'PROPERTIES', 'pclassdesc_receiver.PROPERTIES'),
    ('methods', 'METHODS', 'pclassdesc_target.METHODS'),
    ('constants', 'CONSTANTS', '[pclassconstantdesc_forged]'),
    ('abstract', 'ABSTRACT', 'true'),
    ('final', 'FINAL', 'true'),
    ('readonly', 'READONLY', 'true'),
):
    PARENT += parent_state(label,
                          f'S[.CLASSES = [pclassdesc_parent[.{field} = {value}],pclassdesc_target,pclassdesc_receiver]]')

for label, attributes, flags, name, extends, interfaces, body in (
    ('attributes', '(SEQUENCE ([NAttributeGroup (SEQUENCE eps) metadata_parent]))', '0', '(BYTES text_parent)', 'ABSENT', '(SEQUENCE eps)', '(SEQUENCE eps)'),
    ('flags', '(SEQUENCE eps)', '32', '(BYTES text_parent)', 'ABSENT', '(SEQUENCE eps)', '(SEQUENCE eps)'),
    ('raw_name', '(SEQUENCE eps)', '0', '(BYTES "T3RoZXI=")', 'ABSENT', '(SEQUENCE eps)', '(SEQUENCE eps)'),
    ('raw_ancestry', '(SEQUENCE eps)', '0', '(BYTES text_parent)', '(NName (BYTES text_class) metadata_extends)', '(SEQUENCE eps)', '(SEQUENCE eps)'),
    ('raw_interfaces', '(SEQUENCE eps)', '0', '(BYTES text_parent)', 'ABSENT', '(SEQUENCE ([NName (BYTES text_class) metadata_extends]))', '(SEQUENCE eps)'),
    ('raw_method', '(SEQUENCE eps)', '0', '(BYTES text_parent)', 'ABSENT', '(SEQUENCE eps)', '(SEQUENCE ([statement_method]))'),
    ('raw_body', '(SEQUENCE eps)', '0', '(BYTES text_parent)', 'ABSENT', '(SEQUENCE eps)', '(SEQUENCE ([NStmtNop metadata_parent]))'),
):
    node = (f'NStmtClass {attributes} (INTEGER {flags}) (NIdentifier {name} metadata_parent_name) '
            f'{extends} {interfaces} {body} metadata_parent')
    PARENT += parent_state(label,
                          'S[.SOURCES = [pcunit[.OCCURRENCES = '
                          f'$rc_review_occurrence(pcunit.OCCURRENCES,pcpath_parent,{node})]]]')


def checks(original):
    result = []
    for check in original:
        check = check.replace('pclassdesc_target.KIND = "class" /\\ pclassdesc_target.PARENT = eps',
                              'pclassdesc_target.KIND = "class"')
        check = check.replace('metadata_class_name) ABSENT phpType42',
                              'metadata_class_name) phpType44_parent phpType42')
        check = check.replace('S.CLASSES = [pclassdesc_target,pclassdesc_receiver]',
                              'S.CLASSES = [pclassdesc_parent,pclassdesc_target,pclassdesc_receiver]')
        check = check.replace('$throwable_field(S_catch,n_error,"line") = PINT 7',
                              '$throwable_field(S_catch,n_error,"line") = PINT 8')
        result.append(check)
        if check == 'S.CLASSES = [pclassdesc_parent,pclassdesc_target,pclassdesc_receiver]':
            result += PARENT
    return result


CASES = {row['id']: dict(old, source=row['source'], checks=checks(old['checks']))
         for row, old in zip(ROWS, prior.CASES.values(), strict=True)}

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
