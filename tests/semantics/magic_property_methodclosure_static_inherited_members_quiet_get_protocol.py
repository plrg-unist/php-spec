#!/usr/bin/env python3
"""Check inherited static Get captures against complete ordered method roots."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_inherited_quiet_get_protocol as prior

CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_inherited_members_quiet_get_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def checks(old, selected):
    methods = ('[pmethoddesc_before,pmethoddesc_method,pmethoddesc_after]' if selected == 1 else
               '[pmethoddesc_before,pmethoddesc_after,pmethoddesc_method]')
    statements = ('[statement_before,statement_method,statement_after]' if selected == 1 else
                  '[statement_before,statement_after,statement_method]')
    result = []
    for check in old:
        if 'pclassdesc_parent.METHODS = [pmethoddesc_method]' in check:
            check = check.replace('[pmethoddesc_method]', methods)
            result.append(f'pclassdesc_parent.METHODS = {methods}')
        if check == 'pcpath_method = pcpath_owner ++ [PCFIELD 5,PCINDEX 0]':
            check = f'pcpath_method = pcpath_owner ++ [PCFIELD 5,PCINDEX {selected}]'
        check = check.replace('(SEQUENCE ([statement_method])) metadata_owner)',
                              f'(SEQUENCE ({statements})) metadata_owner)')
        result.append(check)
        if check == 'pclassdesc_parent.NAME = $base64(text_owner)':
            result += [
                f'statement_members* = {statements}',
                '$property_magic_cv_static_method_members(S,porigin_owner,0,statement_members*,pclassdesc_parent.METHODS)',
                '~$property_magic_cv_static_method_members(S,porigin_owner,1,statement_members*,pclassdesc_parent.METHODS)',
                '~$property_magic_cv_static_method_members(S,porigin_requested,0,statement_members*,pclassdesc_parent.METHODS)',
                '~$property_magic_cv_static_method_members(S,porigin_owner,0,eps,pclassdesc_parent.METHODS)',
                '~$property_magic_cv_static_method_members(S,porigin_owner,0,statement_members*,eps)',
                '~$property_magic_cv_static_method_members(S,porigin_owner,0,statement_members*,[pmethoddesc_method])',
                '~$property_magic_cv_static_method_members(S,porigin_owner,0,[statement_method],pclassdesc_parent.METHODS)',
            ]
            for label, field, value in (
                ('owner', 'OWNER', 'porigin_requested'),
                ('name', 'NAME', '$ptascii("COUNTER")'),
                ('origin', 'FUNCTION', 'pmethoddesc_before.FUNCTION[.ORIGIN = porigin_method]'),
                ('body', 'FUNCTION', 'pmethoddesc_before.FUNCTION[.BODY = pcpath_method ++ [PCFIELD 6]]'),
                ('visibility', 'VISIBILITY', 'PROPERTY_PRIVATE' if selected == 1 else 'PROPERTY_PROTECTED'),
                ('static', 'STATIC', 'true' if selected == 1 else 'false'),
                ('final', 'FINAL', 'true'),
                ('abstract', 'ABSTRACT', 'true'),
            ):
                modified = methods.replace('pmethoddesc_before',f'pmethoddesc_before[.{field} = {value}]',1)
                result += [f'S_member_{label} = S[.CLASSES = [pclassdesc_parent[.METHODS = {modified}],pclassdesc_child,pclassdesc_receiver]]',
                           f'~$property_magic_cv_inherited_static_methodclosure(S_member_{label},n_closure)',
                           f'~$property_empty_rv_kind(S_member_{label},S_member_{label}.OBJECTS[n_closure])']
            swapped = methods.replace('pmethoddesc_before','pmethoddesc_swap').replace('pmethoddesc_after','pmethoddesc_before').replace('pmethoddesc_swap','pmethoddesc_after')
            result += [f'S_member_order = S[.CLASSES = [pclassdesc_parent[.METHODS = {swapped}],pclassdesc_child,pclassdesc_receiver]]',
                       '~$property_magic_cv_inherited_static_methodclosure(S_member_order,n_closure)',
                       '~$property_empty_rv_kind(S_member_order,S_member_order.OBJECTS[n_closure])']
    return result


CASES = {row['id']: dict(old, source=row['source'], checks=checks(old['checks'], index + 1))
         for index, (row, old) in enumerate(zip(ROWS, prior.CASES.values(), strict=True))}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, Path(prior.__file__), prior.CATALOGUE,
                  Path(prior.prior.__file__), prior.prior.CATALOGUE), runner_flags=('--sl',))
