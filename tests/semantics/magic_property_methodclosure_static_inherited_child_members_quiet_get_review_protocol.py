#!/usr/bin/env python3
"""Check complete child methods without admitting child-selected overrides."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_inherited_members_quiet_get_review_protocol as prior

CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_inherited_child_members_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def refusal(label, state):
    return [f'S_childmembers_{label} = {state}',
            f'~$property_magic_cv_inherited_static_methodclosure(S_childmembers_{label},n_closure)',
            f'~$property_magic_cv_static_methodclosure(S_childmembers_{label},n_closure)',
            f'~$property_empty_rv_kind(S_childmembers_{label},S.OBJECTS[n_closure])']


def child_checks(statements, descriptors):
    raw = '[' + ','.join(statements) + ']'
    desc = '[' + ','.join(descriptors) + ']'
    first = descriptors[0]
    checks = [
        f'$property_magic_cv_static_method_members(S,porigin_requested,0,{raw},{desc})',
        f'~$property_magic_cv_static_method_members(S,porigin_owner,0,{raw},{desc})',
        f'~$property_magic_cv_static_method_members(S,porigin_requested,1,{raw},{desc})',
        f'~$property_magic_cv_static_method_members(S,porigin_requested,0,eps,{desc})',
        f'~$property_magic_cv_static_method_members(S,porigin_requested,0,{raw},eps)',
        f'$effective_method(S,porigin_requested,{first}.NAME,|S.CLASSES|) = ({first})',
        f'{first} =/= pmethoddesc_method',
    ]
    for index, (statement, descriptor) in enumerate(zip(statements, descriptors, strict=True)):
        checks += [
            f'{descriptor}.OWNER = porigin_requested',
            f'{descriptor}.FUNCTION.ORIGIN = PORIGIN n_unit (pcpath_child ++ [PCFIELD 5,PCINDEX {index}])',
            f'{descriptor}.FUNCTION.BODY = pcpath_child ++ [PCFIELD 5,PCINDEX {index},PCFIELD 6]',
            f'$origin_node(S.SOURCES,{descriptor}.FUNCTION.ORIGIN) = ({statement})',
        ]
    for label, field, value in (
        ('owner', 'OWNER', 'porigin_owner'),
        ('name', 'NAME', 'pmethoddesc_method.NAME'),
        ('origin', 'FUNCTION', f'{first}.FUNCTION[.ORIGIN = porigin_method]'),
        ('body', 'FUNCTION', f'{first}.FUNCTION[.BODY = pcpath_method]'),
        ('final', 'FINAL', 'true'),
        ('abstract', 'ABSTRACT', 'true'),
    ):
        changed = list(descriptors)
        changed[0] = f'{first}[.{field} = {value}]'
        checks += refusal(label, 'S[.CLASSES = [pclassdesc_target,pclassdesc_child[.METHODS = ['
                          + ','.join(changed) + ']],pclassdesc_receiver]]')
    checks += refusal('descriptor_orphan', 'S[.CLASSES = [pclassdesc_target,pclassdesc_child[.METHODS = eps],pclassdesc_receiver]]')
    root = ('NStmtClass (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES text_child) metadata_child_name) '
            'phpType44_parent (SEQUENCE eps) (SEQUENCE ({members})) metadata_child')
    raw_changes = [('raw_empty', 'eps'), ('raw_nonmethod', '[NStmtNop metadata_child]')]
    if len(statements) > 1:
        raw_changes.append(('raw_order', '[' + ','.join(reversed(statements)) + ']'))
        checks += refusal('descriptor_order', 'S[.CLASSES = [pclassdesc_target,pclassdesc_child[.METHODS = ['
                          + ','.join(reversed(descriptors)) + ']],pclassdesc_receiver]]')
    for label, value in raw_changes:
        node = root.format(members=value)
        checks += refusal(label, 'S[.SOURCES = [pcunit[.OCCURRENCES = '
                          f'$rc_review_occurrence(pcunit.OCCURRENCES,pcpath_child,{node})]]]')
    checks += [
        f'{statements[0]} = NStmtClassMethod phpType14_child0 phpType24_child0 phpType4_child0 (NIdentifier phpType33_child0 metadata_child0_name) phpType16_child0 phpType18_child0 (SEQUENCE statement_child0_body*) metadata_child0',
        'statement_shadow = NStmtClassMethod phpType14_child0 (INTEGER 9) phpType4_child0 (NIdentifier (BYTES "Y291bnRlcg==") metadata_child0_name) phpType16_child0 phpType18_child0 (SEQUENCE statement_child0_body*) metadata_child0',
        f'pmethoddesc_shadow = {first}[.NAME = $ptascii("counter")][.VISIBILITY = PROPERTY_PUBLIC][.STATIC = true][.FINAL = false][.ABSTRACT = false]',
    ]
    shadow_raw = ['statement_shadow', *statements[1:]]
    shadow_desc = ['pmethoddesc_shadow', *descriptors[1:]]
    node = root.format(members='[' + ','.join(shadow_raw) + ']')
    occurrences = f'$rc_review_occurrence(pcunit.OCCURRENCES,pcpath_child,{node})'
    occurrences = f'$rc_review_occurrence({occurrences},pcpath_child ++ [PCFIELD 5,PCINDEX 0],statement_shadow)'
    checks += [
        'S_shadow = S[.CLASSES = [pclassdesc_target,pclassdesc_child[.METHODS = ['
        + ','.join(shadow_desc) + ']],pclassdesc_receiver]][.SOURCES = [pcunit[.OCCURRENCES = ' + occurrences + ']]]',
        f'$property_magic_cv_static_method_members(S_shadow,porigin_requested,0,[{",".join(shadow_raw)}],[{",".join(shadow_desc)}])',
        '$effective_method(S_shadow,porigin_requested,pmethoddesc_method.NAME,|S.CLASSES|) = (pmethoddesc_shadow)',
        r'pmethoddesc_shadow.OWNER = porigin_requested /\ pmethoddesc_shadow.OWNER =/= porigin_owner',
        '~$property_magic_cv_inherited_static_methodclosure(S_shadow,n_closure)',
        '~$property_magic_cv_static_methodclosure(S_shadow,n_closure)',
        '~$property_empty_rv_kind(S_shadow,S.OBJECTS[n_closure])',
    ]
    return checks


def checks(old, count):
    statements = [f'statement_child{i}' for i in range(count)]
    descriptors = [f'pmethoddesc_child{i}' for i in range(count)]
    result = []
    for check in old:
        if check.startswith('pclassdesc_child.METHODS = eps /\\ '):
            result.append('pclassdesc_child.METHODS = [' + ','.join(descriptors) + ']')
            check = check.removeprefix('pclassdesc_child.METHODS = eps /\\ ')
        if check.startswith('$origin_node(S.SOURCES,porigin_requested) = '):
            check = check.replace('(SEQUENCE eps) metadata_child)',
                                  '(SEQUENCE ([' + ','.join(statements) + '])) metadata_child)')
        result.append(check)
        if check.startswith('$origin_node(S.SOURCES,porigin_requested) = '):
            result += child_checks(statements, descriptors)
    return result


CASES = {row['id']: dict(old, source=row['source'], checks=checks(old['checks'], count))
         for row, old, count in zip(ROWS, prior.CASES.values(), (1, 3), strict=True)}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, Path(prior.__file__), prior.CATALOGUE,
                  Path(prior.prior.__file__), prior.prior.CATALOGUE,
                  Path(prior.prior.prior.__file__), prior.prior.prior.CATALOGUE,
                  Path(prior.prior.prior.prior.__file__), prior.prior.prior.prior.CATALOGUE,
                  Path(prior.prior.prior.prior.owning.__file__), prior.prior.prior.prior.owning.CATALOGUE,
                  Path(prior.prior.prior.prior.literal.__file__), prior.prior.prior.prior.literal.CATALOGUE),
                 runner_flags=('--sl',), fixture_renderer=prior.prior.prior.prior.literal.render)
