#!/usr/bin/env python3
"""Check inherited static Get captures with genuine unselected child methods."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_inherited_members_quiet_get_protocol as prior

CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_inherited_child_members_quiet_get_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def checks(old, index):
    methods = '[pmethoddesc_childfirst,pmethoddesc_childlast]'
    statements = '[statement_childfirst,statement_childlast]'
    result = []
    for check in old:
        if check == 'pclassdesc_child.PROPERTIES = eps /\\ pclassdesc_child.METHODS = eps /\\ pclassdesc_child.CONSTANTS = eps':
            result.append(f'pclassdesc_child.METHODS = {methods}')
            check = 'pclassdesc_child.PROPERTIES = eps /\\ pclassdesc_child.CONSTANTS = eps'
        check = check.replace('phpType44_parent (SEQUENCE eps) (SEQUENCE eps) metadata_child)',
                              f'phpType44_parent (SEQUENCE eps) (SEQUENCE ({statements})) metadata_child)')
        result.append(check)
        if check == 'pclassdesc_child.NAME = $base64(text_child)':
            result += [
                f'statement_child_members* = {statements}',
                '$property_magic_cv_static_method_members(S,porigin_requested,0,statement_child_members*,pclassdesc_child.METHODS)',
                '~$property_magic_cv_static_method_members(S,porigin_owner,0,statement_child_members*,pclassdesc_child.METHODS)',
                '~$property_magic_cv_static_method_members(S,porigin_requested,1,statement_child_members*,pclassdesc_child.METHODS)',
                '~$property_magic_cv_static_method_members(S,porigin_requested,0,eps,pclassdesc_child.METHODS)',
                '~$property_magic_cv_static_method_members(S,porigin_requested,0,statement_child_members*,eps)',
                'pmethoddesc_childfirst.OWNER = porigin_requested /\\ pmethoddesc_childlast.OWNER = porigin_requested',
                'pmethoddesc_childlast.FINAL = ' + ('false' if index == 0 else 'true'),
                '$effective_method(S,porigin_requested,pmethoddesc_method.NAME,|S.CLASSES|) = (pmethoddesc_method)',
            ]
            for label, field, value in (
                ('owner', 'OWNER', 'porigin_owner'),
                ('name', 'NAME', 'pmethoddesc_method.NAME'),
                ('origin', 'FUNCTION', 'pmethoddesc_childfirst.FUNCTION[.ORIGIN = porigin_method]'),
                ('body', 'FUNCTION', 'pmethoddesc_childfirst.FUNCTION[.BODY = pcpath_method ++ [PCFIELD 6]]'),
                ('visibility', 'VISIBILITY', 'PROPERTY_PROTECTED'),
                ('static', 'STATIC', 'false' if index == 0 else 'true'),
                ('final', 'FINAL', 'true'),
                ('abstract', 'ABSTRACT', 'true'),
            ):
                changed = methods.replace('pmethoddesc_childfirst',f'pmethoddesc_childfirst[.{field} = {value}]',1)
                result += [f'S_child_member_{label} = S[.CLASSES = [pclassdesc_parent,pclassdesc_child[.METHODS = {changed}],pclassdesc_receiver]]',
                           f'~$property_magic_cv_inherited_static_methodclosure(S_child_member_{label},n_closure)',
                           f'~$property_empty_rv_kind(S_child_member_{label},S_child_member_{label}.OBJECTS[n_closure])']
            result += [
                'S_child_member_order = S[.CLASSES = [pclassdesc_parent,pclassdesc_child[.METHODS = [pmethoddesc_childlast,pmethoddesc_childfirst]],pclassdesc_receiver]]',
                '~$property_magic_cv_inherited_static_methodclosure(S_child_member_order,n_closure)',
                '~$property_empty_rv_kind(S_child_member_order,S_child_member_order.OBJECTS[n_closure])',
            ]
    return result


CASES = {row['id']: dict(old, source=row['source'], checks=checks(old['checks'], index))
         for index, (row, old) in enumerate(zip(ROWS, prior.CASES.values(), strict=True))}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, Path(prior.__file__), prior.CATALOGUE,
                  Path(prior.prior.__file__), prior.prior.CATALOGUE,
                  Path(prior.prior.prior.__file__), prior.prior.prior.CATALOGUE), runner_flags=('--sl',))
