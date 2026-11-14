#!/usr/bin/env python3
"""Check own child-method Get captures and separate overriding method statics."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_quiet_get_protocol as original
import magic_property_methodclosure_static_named_selector_quiet_get_protocol as selector

CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_own_child_members_quiet_get_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

PARENT = r'''
S.CLASSES = [pclassdesc_parent,pclassdesc_target,pclassdesc_receiver]
$class_at(S.CLASSES,porigin_owner) = (pclassdesc_target)
pclassdesc_target.PARENT = (ptbytes_parent)
$class_named(S.CLASSNAMES,$ptlc(ptbytes_parent)) = (porigin_root)
$class_link_at(S.LINKEDPARENTS,porigin_owner) = (SOURCE_PARENT porigin_root)
pclassdesc_parent.ORIGIN = porigin_root
porigin_root = PORIGIN n_unit pcpath_root
porigin_owner = PORIGIN n_unit pcpath_child
pclassdesc_parent.KIND = "class" /\ pclassdesc_target.KIND = "class"
pclassdesc_parent.PARENT = eps /\ pclassdesc_parent.INTERFACES = eps /\ pclassdesc_target.INTERFACES = eps
pclassdesc_parent.PROPERTIES = eps /\ pclassdesc_parent.CONSTANTS = eps
pclassdesc_target.PROPERTIES = eps /\ pclassdesc_target.CONSTANTS = eps
~pclassdesc_parent.ABSTRACT /\ ~pclassdesc_parent.FINAL /\ ~pclassdesc_parent.READONLY
~pclassdesc_target.ABSTRACT /\ ~pclassdesc_target.FINAL /\ ~pclassdesc_target.READONLY
$origin_node(S.SOURCES,porigin_root) = (NStmtClass (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES text_root) metadata_root_name) ABSENT (SEQUENCE eps) (SEQUENCE statement_root*) metadata_root)
pclassdesc_parent.NAME = $base64(text_root)
$origin_node(S.SOURCES,porigin_owner) = (NStmtClass (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES text_child) metadata_child_name) phpType44_parent (SEQUENCE eps) (SEQUENCE statement_child*) metadata_child)
pclassdesc_target.NAME = $base64(text_child)
$property_magic_cv_static_method_parent_selector(phpType44_parent,ptbytes_parent)
$property_magic_cv_static_method_parent(S,pclassdesc_target,phpType44_parent)
~$property_magic_cv_static_method_parent(S,pclassdesc_target,ABSENT)
~$property_magic_cv_static_method_parent(S,pclassdesc_parent,phpType44_parent)
$property_magic_cv_static_method_members(S,porigin_root,0,statement_root*,pclassdesc_parent.METHODS)
$property_magic_cv_static_method_members(S,porigin_owner,0,statement_child*,pclassdesc_target.METHODS)
~$property_magic_cv_static_method_members(S,porigin_owner,0,statement_root*,pclassdesc_parent.METHODS)
~$property_magic_cv_static_method_members(S,porigin_root,0,statement_child*,pclassdesc_target.METHODS)
$effective_method(S,porigin_root,pmethoddesc_method.NAME,|S.CLASSES|) = (pmethoddesc_parentcounter)
pmethoddesc_parentcounter.OWNER = porigin_root
pmethoddesc_parentcounter.FUNCTION.ORIGIN =/= porigin_method
$effective_method(S,porigin_owner,pmethoddesc_method.NAME,|S.CLASSES|) = (pmethoddesc_method)
pmethoddesc_method.OWNER = porigin_owner
$static_function_at($all_functions(S),pstaticcell_parent.ORIGIN) = (pmethoddesc_parentcounter.FUNCTION)
$static_function_at($all_functions(S),pstaticcell.ORIGIN) = (pfunction_method)
$property_get_method(S,n_receiver) = (pmethoddesc)
$class_at(S.CLASSES,pmethoddesc.OWNER) = (pclassdesc_receiver)
'''.strip().splitlines()


def checks(old, index):
    result = []
    for check in old:
        if check == 'S.STATICS = [pstaticcell]':
            result += ['S.STATICS = [pstaticcell_parent,pstaticcell]',
                       'n_parent_counter = pstaticcell_parent.CELL',
                       'S.STORE[n_parent_counter] = DEFINED (PINT 101)',
                       'pstaticcell_parent.ORIGIN =/= pstaticcell.ORIGIN',
                       '$heap_unique([HCELL n_parent_counter,HCELL pstaticcell.CELL])',
                       '$heap_owners($heap_graph(S),HCELL n_parent_counter) = 1']
            continue
        if check == '(HCELL n_counter) <- S.ALLOCATIONS /\\ $static_roots(S.STATICS) = [HCELL n_counter]':
            check = '(HCELL n_counter) <- S.ALLOCATIONS /\\ (HCELL n_parent_counter) <- S.ALLOCATIONS /\\ $static_roots(S.STATICS) = [HCELL n_parent_counter,HCELL n_counter]'
        check = check.replace('S.EVENTS = [OUTPUT $ptascii("WARM;")',
                              'S.EVENTS = [OUTPUT $ptascii("PARENT_WARM;"),OUTPUT $ptascii("WARM;")')
        check = check.replace('OUTPUT $ptascii("STATIC;"),OUTPUT $ptascii("CAPTURE;")',
                              'OUTPUT $ptascii("STATIC;"),OUTPUT $ptascii("PARENT_STATIC;"),OUTPUT $ptascii("CAPTURE;")')
        check = check.replace('FUNCTIONCACHES = [pfunctioncache[.INITIALIZED = ($(n_closure + 1))]]',
                              'FUNCTIONCACHES = $function_cache_set(S.FUNCTIONCACHES,pfunctioncache[.INITIALIZED = ($(n_closure + 1))])')
        if index == 1:
            if check == 'pclosurecache = {OBJECT n_closure,FUNCTION porigin_method,SOURCE eps,SCOPE (BIND_CLASS porigin_owner),CACHE (CACHE_SHARED)}':
                result += ['pclosurecache = {OBJECT n_closure,FUNCTION porigin_method,SOURCE (n_source),SCOPE (BIND_CLASS porigin_owner),CACHE (CACHE_SHARED)}',
                           'S.CLOSURECACHES = [pclosurecache_source,pclosurecache]',
                           'pclosurecache_source = {OBJECT n_source,FUNCTION porigin_method,SOURCE eps,SCOPE (BIND_CLASS porigin_owner),CACHE (CACHE_SHARED)}',
                           '$(n_source < n_closure)',
                           'S.OBJECTS[n_source] = S.OBJECTS[n_closure]',
                           '~((HOBJECT n_source) <- S.ALLOCATIONS)',
                           '$closure_scope_at(S.CLOSURESCOPES,n_source) = eps',
                           '$lookup(S.ENV,$ptascii("original")) = eps',
                           '$property_magic_cv_static_method_clone_history(S,n_closure,porigin_method,porigin_site,porigin_owner)']
                continue
            check = check.replace('CLOSURECACHES = [pclosurecache[.', 'CLOSURECACHES = [pclosurecache_source,pclosurecache[.')
        result.append(check)
        if check == 'S_done.STORE[n_counter] = DEFINED (PINT 3)':
            result += ['S_done.STORE[n_parent_counter] = DEFINED (PINT 102)',
                       'S_done.STATICS = S.STATICS',
                       '$heap_owners($heap_graph(S_done),HCELL n_parent_counter) = 1',
                       '$heap_owners($heap_graph(S_done),HCELL n_counter) = 1']
    result += selector.SELECTOR + PARENT
    child_methods = ('[pmethoddesc_first,pmethoddesc_method,pmethoddesc_last]' if index == 0 else
                     '[pmethoddesc_first,pmethoddesc_last,pmethoddesc_method]')
    root_methods = ('[pmethoddesc_before,pmethoddesc_parentcounter,pmethoddesc_after]' if index == 0 else
                    '[pmethoddesc_parentcounter,pmethoddesc_after,pmethoddesc_before]')
    result += [f'pclassdesc_parent.METHODS = {root_methods}',
               f'pclassdesc_target.METHODS = {child_methods}']
    for family, methods in (('root', root_methods), ('child', child_methods)):
        reversed_methods = '[' + ','.join(reversed(methods[1:-1].split(','))) + ']'
        parent = f'pclassdesc_parent[.METHODS = {reversed_methods}]' if family == 'root' else 'pclassdesc_parent'
        child = f'pclassdesc_target[.METHODS = {reversed_methods}]' if family == 'child' else 'pclassdesc_target'
        result += [f'S_{family}_order = S[.CLASSES = [{parent},{child},pclassdesc_receiver]]',
                   f'~$property_magic_cv_static_methodclosure(S_{family}_order,n_closure)',
                   f'~$property_empty_rv_kind(S_{family}_order,S_{family}_order.OBJECTS[n_closure])']
    for family, methods, descriptor, other in (
        ('root', root_methods, 'pmethoddesc_before', 'porigin_owner'),
        ('child', child_methods, 'pmethoddesc_first', 'porigin_root'),
    ):
        for label, field, value in (
            ('owner', 'OWNER', other), ('name', 'NAME', 'pmethoddesc_method.NAME'),
            ('origin', 'FUNCTION', descriptor + '.FUNCTION[.ORIGIN = porigin_method]'),
            ('body', 'FUNCTION', descriptor + '.FUNCTION[.BODY = pmethoddesc_method.FUNCTION.BODY]'),
            ('visibility', 'VISIBILITY', 'PROPERTY_PRIVATE' if family == 'root' else 'PROPERTY_PROTECTED'),
            ('static', 'STATIC', 'true' if family == 'root' else 'false'),
            ('final', 'FINAL', 'true'), ('abstract', 'ABSTRACT', 'true'),
        ):
            changed = methods.replace(descriptor, f'{descriptor}[.{field} = {value}]', 1)
            parent = f'pclassdesc_parent[.METHODS = {changed}]' if family == 'root' else 'pclassdesc_parent'
            child = f'pclassdesc_target[.METHODS = {changed}]' if family == 'child' else 'pclassdesc_target'
            state = f'S_{family}_{label}'
            result += [f'{state} = S[.CLASSES = [{parent},{child},pclassdesc_receiver]]',
                       f'~$property_magic_cv_static_methodclosure({state},n_closure)',
                       f'~$property_empty_rv_kind({state},{state}.OBJECTS[n_closure])']
    return result


CASES = {row['id']: dict(old, source=row['source'], checks=checks(old['checks'], index))
         for index, (row, old) in enumerate(zip(ROWS, original.CASES.values(), strict=True))}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, Path(original.__file__), original.CATALOGUE,
                  Path(selector.__file__), selector.CATALOGUE), runner_flags=('--sl',))
