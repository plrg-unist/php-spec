#!/usr/bin/env python3
"""Check complete inherited method lists, selected indices and Shared cleanup."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_inherited_quiet_get_review_protocol as prior

CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_inherited_members_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def refusal(label, state):
    return [f'S_members_{label} = {state}',
            f'~$property_magic_cv_inherited_static_methodclosure(S_members_{label},n_closure)',
            f'~$property_magic_cv_static_methodclosure(S_members_{label},n_closure)',
            f'~$property_empty_rv_kind(S_members_{label},S.OBJECTS[n_closure])']


def method_list(check, descriptors, selected):
    prefix = 'pclassdesc_target[.METHODS = ['
    if prefix not in check:
        return check
    start = check.index(prefix) + len(prefix)
    depth = 1
    end = start
    while depth:
        depth += (check[end] == '[') - (check[end] == ']')
        end += 1
    entry = check[start:end - 1]
    if not entry.startswith('pmethoddesc_method['):
        return check
    entries = list(descriptors)
    entries[selected] = entry
    return check[:start] + ','.join(entries) + check[end - 1:]


def members(statements, descriptors, selected, first_flags):
    raw = '[' + ','.join(statements) + ']'
    desc = '[' + ','.join(descriptors) + ']'
    checks = [
        f'$property_magic_cv_static_method_members(S,porigin_owner,0,{raw},{desc})',
        f'~$property_magic_cv_static_method_members(S,porigin_owner,1,{raw},{desc})',
        f'~$property_magic_cv_static_method_members(S,porigin_requested,0,{raw},{desc})',
        f'~$property_magic_cv_static_method_members(S,porigin_owner,0,{raw},eps)',
        f'~$property_magic_cv_static_method_members(S,porigin_owner,0,eps,{desc})',
        f'~$property_magic_cv_static_method_members(S,porigin_owner,0,{raw},[{",".join(reversed(descriptors))}])',
        f'~$property_magic_cv_static_method_members(S,porigin_owner,0,[{",".join(statements[:-1])}],{desc})',
        f'~$property_magic_cv_static_method_members(S,porigin_owner,0,{raw},[{",".join(descriptors[:-1])}])',
    ]
    for index, (statement, descriptor) in enumerate(zip(statements, descriptors, strict=True)):
        checks += [
            f'{descriptor}.OWNER = porigin_owner',
            f'{descriptor}.FUNCTION.ORIGIN = PORIGIN n_unit (pcpath_class ++ [PCFIELD 5,PCINDEX {index}])',
            f'{descriptor}.FUNCTION.BODY = pcpath_class ++ [PCFIELD 5,PCINDEX {index},PCFIELD 6]',
            f'$origin_node(S.SOURCES,{descriptor}.FUNCTION.ORIGIN) = ({statement})',
        ]
    first = descriptors[0]
    for label, field, value in (
        ('owner', 'OWNER', 'porigin_requested'),
        ('name', 'NAME', 'pmethoddesc_method.NAME'),
        ('origin', 'FUNCTION', f'{first}.FUNCTION[.ORIGIN = porigin_method]'),
        ('body', 'FUNCTION', f'{first}.FUNCTION[.BODY = pcpath_method]'),
        ('visibility', 'VISIBILITY', 'PROPERTY_PRIVATE' if selected == 2 else 'PROPERTY_PUBLIC'),
        ('static', 'STATIC', 'false' if selected == 2 else 'true'),
        ('final', 'FINAL', 'false' if selected == 2 else 'true'),
        ('abstract', 'ABSTRACT', 'true'),
    ):
        changed = list(descriptors)
        changed[0] = f'{first}[.{field} = {value}]'
        checks += refusal(label, 'S[.CLASSES = [pclassdesc_target[.METHODS = ['
                          + ','.join(changed) + ']],pclassdesc_child,pclassdesc_receiver]]')
    checks += refusal('descriptor_order', 'S[.CLASSES = [pclassdesc_target[.METHODS = ['
                      + ','.join(reversed(descriptors)) + ']],pclassdesc_child,pclassdesc_receiver]]')
    root = ('NStmtClass phpType14_class phpType24_class (NIdentifier (BYTES text_class) metadata_class_name) '
            'ABSENT phpType42 (SEQUENCE ({members})) metadata_class')
    for label, raw_members in (
        ('raw_order', '[' + ','.join(reversed(statements)) + ']'),
        ('raw_orphan', '[' + ','.join(statements[:-1]) + ']'),
        ('raw_nonmethod', '[NStmtNop metadata_class,' + ','.join(statements[1:]) + ']'),
    ):
        node = root.format(members=raw_members)
        checks += refusal(label, 'S[.SOURCES = [pcunit[.OCCURRENCES = '
                          f'$rc_review_occurrence(pcunit.OCCURRENCES,pcpath_class,{node})]]]')
    checks += [
        f'{statements[0]} = NStmtClassMethod phpType14_before (INTEGER flags_before) phpType4_before (NIdentifier (BYTES text_before) metadata_before_name) phpType16_before phpType18_before (SEQUENCE statement_before_body*) metadata_before',
        f'flags_before = {first_flags}',
        f'{first}.FINAL = ' + ('true' if selected == 2 else 'false'),
        f'{first}.STATIC = ' + ('true' if selected == 2 else 'false'),
        'statement_duplicate = NStmtClassMethod phpType14_before (INTEGER flags_before) phpType4_before (NIdentifier (BYTES "Q09VTlRFUg==") metadata_before_name) phpType16_before phpType18_before (SEQUENCE statement_before_body*) metadata_before',
    ]
    duplicate_raw = ['statement_duplicate', *statements[1:]]
    duplicate_desc = [first + '[.NAME = $ptascii("COUNTER")]', *descriptors[1:]]
    node = root.format(members='[' + ','.join(duplicate_raw) + ']')
    occurrences = f'$rc_review_occurrence(pcunit.OCCURRENCES,pcpath_class,{node})'
    occurrences = f'$rc_review_occurrence({occurrences},pcpath_class ++ [PCFIELD 5,PCINDEX 0],statement_duplicate)'
    checks += [
        f'S_duplicate = S[.SOURCES = [pcunit[.OCCURRENCES = {occurrences}]]]',
        f'~$property_magic_cv_static_method_members(S_duplicate,porigin_owner,0,[{",".join(duplicate_raw)}],[{",".join(duplicate_desc)}])',
    ]
    return checks


def checks(old, selected, first_flags):
    statements = ['statement_before', 'statement_middle', 'statement_method'] if selected == 2 else ['statement_before', 'statement_method', 'statement_after']
    descriptors = ['pmethoddesc_before', 'pmethoddesc_middle', 'pmethoddesc_method'] if selected == 2 else ['pmethoddesc_before', 'pmethoddesc_method', 'pmethoddesc_after']
    result = []
    for check in old:
        check = check.replace('pcpath_method = pcpath_class ++ [PCFIELD 5,PCINDEX 0]',
                              f'pcpath_method = pcpath_class ++ [PCFIELD 5,PCINDEX {selected}]')
        if check.startswith('$origin_node(S.SOURCES,porigin_owner) = '):
            check = check.replace('(SEQUENCE ([statement_method]))', '(SEQUENCE ([' + ','.join(statements) + ']))')
        check = method_list(check, descriptors, selected)
        if check == 'pclassdesc_target.METHODS = [pmethoddesc_method]':
            check = 'pclassdesc_target.METHODS = [' + ','.join(descriptors) + ']'
        result.append(check)
        if check == 'pclassdesc_target.METHODS = [' + ','.join(descriptors) + ']':
            result += members(statements, descriptors, selected, first_flags)
    return result


CASES = {row['id']: dict(old, source=row['source'], checks=checks(old['checks'], selected, first_flags))
         for row, old, selected, first_flags in zip(ROWS, prior.CASES.values(), (2, 1), (42, 4), strict=True)}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, Path(prior.__file__), prior.CATALOGUE,
                  Path(prior.prior.__file__), prior.prior.CATALOGUE,
                  Path(prior.prior.prior.__file__), prior.prior.prior.CATALOGUE,
                  Path(prior.prior.prior.owning.__file__), prior.prior.prior.owning.CATALOGUE,
                  Path(prior.prior.prior.literal.__file__), prior.prior.prior.literal.CATALOGUE),
                 runner_flags=('--sl',), fixture_renderer=prior.prior.prior.literal.render)
