#!/usr/bin/env python3
"""Check own child captures, complete member authority and separate static roots."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_methodclosure_static_named_selector_quiet_get_review_protocol as prior

CATALOGUE = Path(__file__).with_name('magic_property_methodclosure_static_own_child_members_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def refusal(label, state):
    return [f'S_ownchild_{label} = {state}',
            f'~$property_magic_cv_static_methodclosure(S_ownchild_{label},n_closure)',
            f'~$property_empty_rv_kind(S_ownchild_{label},S.OBJECTS[n_closure])']


def class_state(role, descriptor):
    parent = descriptor if role == 'parent' else 'pclassdesc_parent'
    child = descriptor if role == 'child' else 'pclassdesc_target'
    return f'S[.CLASSES = [{parent},{child},pclassdesc_receiver]]'


def member_checks(role, owner, path, statements, descriptors, raw_class):
    raw, desc = '[' + ','.join(statements) + ']', '[' + ','.join(descriptors) + ']'
    other = 'porigin_owner' if role == 'parent' else 'porigin_parent'
    checks = [f'$property_magic_cv_static_method_members(S,{owner},0,{raw},{desc})',
              f'~$property_magic_cv_static_method_members(S,{other},0,{raw},{desc})',
              f'~$property_magic_cv_static_method_members(S,{owner},1,{raw},{desc})',
              f'~$property_magic_cv_static_method_members(S,{owner},0,{raw},eps)',
              f'~$property_magic_cv_static_method_members(S,{owner},0,eps,{desc})']
    for index, (statement, descriptor) in enumerate(zip(statements, descriptors, strict=True)):
        checks += [f'{descriptor}.OWNER = {owner}',
                   f'{descriptor}.FUNCTION.ORIGIN = PORIGIN n_unit ({path} ++ [PCFIELD 5,PCINDEX {index}])',
                   f'{descriptor}.FUNCTION.BODY = {path} ++ [PCFIELD 5,PCINDEX {index},PCFIELD 6]',
                   f'$origin_node(S.SOURCES,{descriptor}.FUNCTION.ORIGIN) = ({statement})']
    first = descriptors[0]
    for label, field, value in (
        ('owner', 'OWNER', other), ('name', 'NAME', 'pmethoddesc_method.NAME'),
        ('origin', 'FUNCTION', f'{first}.FUNCTION[.ORIGIN = porigin_method]'),
        ('body', 'FUNCTION', f'{first}.FUNCTION[.BODY = pcpath_method]'),
        ('static', 'STATIC', f'~{first}.STATIC'), ('final', 'FINAL', f'~{first}.FINAL'),
        ('abstract', 'ABSTRACT', 'true'),
    ):
        changed = list(descriptors)
        changed[0] = f'{first}[.{field} = {value}]'
        target = 'pclassdesc_parent' if role == 'parent' else 'pclassdesc_target'
        checks += refusal(f'{role}_{label}', class_state(role, target + '[.METHODS = [' + ','.join(changed) + ']]'))
    target = 'pclassdesc_parent' if role == 'parent' else 'pclassdesc_target'
    checks += refusal(f'{role}_descriptor_order', class_state(role, target + '[.METHODS = [' + ','.join(reversed(descriptors)) + ']]'))
    for label, members in (
        ('raw_empty', 'eps'), ('raw_order', '[' + ','.join(reversed(statements)) + ']'),
        ('raw_nonmethod', '[NStmtNop metadata_class]'),
        ('raw_orphan', '[' + ','.join(statements[:-1]) + ']'),
    ):
        node = raw_class.format(members=members)
        checks += refusal(f'{role}_{label}', 'S[.SOURCES = [pcunit[.OCCURRENCES = '
                          f'$rc_review_occurrence(pcunit.OCCURRENCES,{path},{node})]]]')
    return checks


def checks(row, constructor, selected):
    statements = ['statement_child_before', 'statement_method'] if selected == 1 else [
        'statement_child_before', 'statement_child_middle', 'statement_method', 'statement_child_after']
    descriptors = ['pmethoddesc_child_before', 'pmethoddesc_method'] if selected == 1 else [
        'pmethoddesc_child_before', 'pmethoddesc_child_middle', 'pmethoddesc_method', 'pmethoddesc_child_after']
    parent_statements = ['statement_parent_before', 'statement_parent_middle', 'statement_parent_method'] if selected == 1 else [
        'statement_parent_before', 'statement_parent_method', 'statement_parent_after']
    parent_descriptors = ['pmethoddesc_parent_before', 'pmethoddesc_parent_middle', 'pmethoddesc_parent_method'] if selected == 1 else [
        'pmethoddesc_parent_before', 'pmethoddesc_parent_method', 'pmethoddesc_parent_after']
    output = base64.b64decode(row['stdout_template_base64']).decode()
    prefix = output.split('RECEIVER;', 1)[0]
    result = []
    for check in prior.front(constructor):
        if check == 'pclassdesc_target.KIND = "class" /\\ pclassdesc_target.PARENT = eps':
            result += ['pclassdesc_target.KIND = "class"', 'pclassdesc_target.PARENT = (ptbytes_parent)']
            continue
        check = check.replace('pcpath_method = pcpath_class ++ [PCFIELD 5,PCINDEX 0]',
                              f'pcpath_method = pcpath_class ++ [PCFIELD 5,PCINDEX {selected}]')
        if check.startswith('$origin_node(S.SOURCES,porigin_owner) = '):
            check = check.replace('ABSENT phpType42', 'phpType44_parent phpType42')
            check = check.replace('(SEQUENCE ([statement_method]))', '(SEQUENCE ([' + ','.join(statements) + ']))')
        check = check.replace('S.STATICS = [pstaticcell]', 'S.STATICS = [pstaticcell,pstaticcell_parent]')
        check = check.replace('$static_roots(S.STATICS) = [HCELL n_counter]', '$static_roots(S.STATICS) = [HCELL n_counter,HCELL pstaticcell_parent.CELL]')
        check = check.replace('STORE[n_counter] = DEFINED (PINT 1)', 'STORE[n_counter] = DEFINED (PINT 2)')
        check = check.replace('S.CLASSES = [pclassdesc_target,pclassdesc_receiver]', 'S.CLASSES = [pclassdesc_parent,pclassdesc_target,pclassdesc_receiver]')
        check = check.replace('"WARM;SOURCES_GONE;I;G;"', '"' + prefix + '"')
        result.append(check)
    child_raw = ('NStmtClass phpType14_class phpType24_class (NIdentifier (BYTES text_class) metadata_class_name) '
                 'phpType44_parent phpType42 (SEQUENCE ({members})) metadata_class')
    parent_raw = ('NStmtClass (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES text_parent_class) metadata_parent_name) '
                  'ABSENT (SEQUENCE eps) (SEQUENCE ({members})) metadata_parent')
    result += [
        'pclassdesc_parent.ORIGIN = porigin_parent', 'porigin_parent = PORIGIN n_unit pcpath_parent',
        'porigin_parent =/= porigin_owner', 'pclassdesc_parent.KIND = "class" /\\ pclassdesc_parent.PARENT = eps',
        'pclassdesc_parent.INTERFACES = eps /\\ pclassdesc_parent.PROPERTIES = eps /\\ pclassdesc_parent.CONSTANTS = eps',
        '~pclassdesc_parent.ABSTRACT /\\ ~pclassdesc_parent.FINAL /\\ ~pclassdesc_parent.READONLY',
        'pclassdesc_target.INTERFACES = eps /\\ pclassdesc_target.PROPERTIES = eps /\\ pclassdesc_target.CONSTANTS = eps',
        '~pclassdesc_target.ABSTRACT /\\ ~pclassdesc_target.FINAL /\\ ~pclassdesc_target.READONLY',
        'phpType14_class = SEQUENCE eps /\\ phpType24_class = INTEGER 0 /\\ phpType42 = SEQUENCE eps',
        '$origin_node(S.SOURCES,porigin_parent) = (' + parent_raw.format(members='[' + ','.join(parent_statements) + ']') + ')',
        'pclassdesc_parent.NAME = $base64(text_parent_class)',
        'pclassdesc_parent.METHODS = [' + ','.join(parent_descriptors) + ']',
        'pclassdesc_target.METHODS = [' + ','.join(descriptors) + ']',
        'phpType44_parent = ' + ('NName' if selected == 1 else 'NNameFullyQualified') + ' (BYTES text_parent) metadata_parent_selector',
        '$base64(text_parent) = ptbytes_parent /\\ ptbytes_parent =/= pclassdesc_parent.NAME',
        '$ptlc(ptbytes_parent) = $ptlc(pclassdesc_parent.NAME)',
        '$class_named(S.CLASSNAMES,$ptlc(pclassdesc_parent.NAME)) = (porigin_parent)',
        '$class_named(S.CLASSNAMES,$ptlc(pclassdesc_target.NAME)) = (porigin_owner)',
        '$class_link_at(S.LINKEDPARENTS,porigin_owner) = (SOURCE_PARENT porigin_parent)',
        '$class_link_at(S.LINKEDPARENTS,porigin_parent) = eps /\\ $class_links_valid(S)',
        '$property_magic_cv_static_method_parent(S,pclassdesc_target,phpType44_parent)',
        '$effective_method(S,porigin_owner,pmethoddesc_method.NAME,|S.CLASSES|) = (pmethoddesc_method)',
        'pmethoddesc_parent_method.NAME = pmethoddesc_method.NAME /\\ pmethoddesc_parent_method.FUNCTION.ORIGIN =/= porigin_method',
        '$effective_method(S,porigin_parent,pmethoddesc_method.NAME,|S.CLASSES|) = (pmethoddesc_parent_method)',
        '$static_function_at($all_functions(S),pstaticcell.ORIGIN) = (pfunction_method)',
        '$static_function_at($all_functions(S),pstaticcell_parent.ORIGIN) = (pmethoddesc_parent_method.FUNCTION)',
        'n_parent_counter = pstaticcell_parent.CELL', 'n_parent_counter =/= n_counter',
        'pstaticcell_parent.ORIGIN =/= pstaticcell.ORIGIN',
        'S.STORE[n_parent_counter] = DEFINED (PINT 101)',
        '(HCELL n_parent_counter) <- S.ALLOCATIONS /\\ n_parent_counter <- S.REFCELLS',
        '$heap_owners($heap_graph(S),HCELL n_parent_counter) = 1',
        '~$property_magic_cv_inherited_static_methodclosure(S,n_closure)',
    ]
    result += member_checks('parent', 'porigin_parent', 'pcpath_parent', parent_statements, parent_descriptors, parent_raw)
    result += member_checks('child', 'porigin_owner', 'pcpath_class', statements, descriptors, child_raw)
    method_raw = ('NStmtClassMethod phpType14_method (INTEGER {flags}) phpType4_ref '
                  '(NIdentifier (BYTES text_method) metadata_method_name) phpType16 phpType18 '
                  '(SEQUENCE ({body})) metadata_method')
    for label, flags, update in (
        ('selected_nonstatic', 1, '[.STATIC = false]'),
        ('selected_private', 12, '[.VISIBILITY = PROPERTY_PRIVATE]'),
        ('selected_generator', 9, ''),
    ):
        body = '[NStmtExpression (NExprYield ABSENT ABSENT metadata_method) metadata_method]' if label.endswith('generator') else 'statement*'
        changed_method = method_raw.format(flags=flags, body=body)
        changed_raw = list(statements)
        changed_raw[selected] = changed_method
        changed_desc = list(descriptors)
        changed_desc[selected] += update
        node = child_raw.format(members='[' + ','.join(changed_raw) + ']')
        occurrences = f'$rc_review_occurrence(pcunit.OCCURRENCES,pcpath_class,{node})'
        occurrences = f'$rc_review_occurrence({occurrences},pcpath_method,{changed_method})'
        state = class_state('child', 'pclassdesc_target[.METHODS = [' + ','.join(changed_desc) + ']]')
        result += refusal(label, state + '[.SOURCES = [pcunit[.OCCURRENCES = ' + occurrences + ']]]')
        result += [f'$property_magic_cv_static_method_members(S_ownchild_{label},porigin_owner,0,['
                   + ','.join(changed_raw) + '],[' + ','.join(changed_desc) + '])']
        if label.endswith('generator'):
            result += ['$function_generator(S_ownchild_selected_generator,pfunction_method)']
    for role in ('parent', 'child'):
        target = 'pclassdesc_parent' if role == 'parent' else 'pclassdesc_target'
        for label, field, value in (
            ('trait', 'KIND', '"trait"'), ('interfaces', 'INTERFACES', '[pclassdesc_receiver.NAME]'),
            ('properties', 'PROPERTIES', 'pclassdesc_receiver.PROPERTIES'),
            ('abstract', 'ABSTRACT', 'true'), ('final', 'FINAL', 'true'), ('readonly', 'READONLY', 'true'),
        ):
            result += refusal(f'{role}_class_{label}', class_state(role, f'{target}[.{field} = {value}]'))
    for label, links in (
        ('unlinked', 'eps'), ('wrong_link', '[CLASSLINK porigin_owner (SOURCE_PARENT pclassdesc_receiver.ORIGIN)]'),
        ('self_link', '[CLASSLINK porigin_owner (SOURCE_PARENT porigin_owner)]'),
        ('internal_link', '[CLASSLINK porigin_owner STDCLASS_PARENT]'),
    ):
        result += refusal(label, f'S[.LINKEDPARENTS = {links}]')
    for label, scope in (('parent_lexical', 'pclosurescope[.LEXICAL = porigin_parent]'),
                         ('parent_called', 'pclosurescope[.CALLED = porigin_parent]')):
        result += refusal(label, f'S[.CLOSURESCOPES = [{scope}]]')
    result += refusal('parent_cache', 'S[.CLOSURECACHES = [pclosurecache_original,pclosurecache_intermediate,pclosurecache[.SCOPE = (BIND_CLASS porigin_parent)]]]')
    result += refusal('parent_method_capture', 'S[.OBJECTS[n_closure] = METHODCLOSURE pmethoddesc_parent_method.FUNCTION.ORIGIN porigin_site porigin_owner eps]')
    result += refusal('parent_requested', 'S[.OBJECTS[n_closure] = METHODCLOSURE porigin_method porigin_site porigin_parent eps]')
    authority = prior.prior.AUTHORITY
    if selected == 2:
        # Literal Empty uses its RV-kind gate; the CV helper deliberately bypasses it.
        authority = [check for check in authority if not check.startswith('~$property_magic_cv_result_supported(')]
        authority += ['~$property_empty_rv_kind(S_unallocated,S_unallocated.OBJECTS[n_closure])']
    result += authority + prior.SELECTOR
    if selected == 1:
        result += ['$property_magic_cv_empty_source(S,ppropertyempty.SITE,ppropertyempty.LINE)',
                   '$property_magic_cv_result_supported(S,ppropertyempty.SITE,ppropertyempty.LINE,true,S.RESULT)']
    else:
        result += ['~$property_magic_cv_source(S,ppropertyempty.SITE,ppropertyempty.LINE)']
    tail = prior.prior.LIFETIME + ([] if selected == 1 else prior.prior.THROW) + prior.prior.DONE
    for check in tail:
        check = check.replace('S_done.STORE[n_counter] = DEFINED (PINT 2)', 'S_done.STORE[n_counter] = DEFINED (PINT 3)')
        check = check.replace('STORE[n_counter] = DEFINED (PINT 1)', 'STORE[n_counter] = DEFINED (PINT 2)')
        check = check.replace('"WARM;SOURCES_GONE;I;G;', '"' + prefix)
        check = check.replace('$throwable_field(S_catch,n_error,"line") = PINT 7', '$throwable_field(S_catch,n_error,"line") = PINT 8')
        result.append(check)
    result += [f'S_done.STORE[n_destination] = DEFINED (PBOOL false)' if selected == 1 else 'S_done.STORE[n_destination] = DEFINED (PINT 42)',
               'S_done.STORE[n_parent_counter] = DEFINED (PINT 102)',
               'S_retired_raw.STORE[n_parent_counter] = DEFINED (PINT 101)',
               'S_ready.STORE[n_parent_counter] = DEFINED (PINT 101)',
               '$owning_review_output(S_done.EVENTS) = $ptascii("' + output + '")']
    return result


CASES = {row['id']: {'source': row['source'], 'stage': prior.STAGE, 'checks': checks(row, constructor, selected)}
         for row, constructor, selected in zip(ROWS, ('NNameFullyQualified', 'NName'), (1, 2), strict=True)}

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
