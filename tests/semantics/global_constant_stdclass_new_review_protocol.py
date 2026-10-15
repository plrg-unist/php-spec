#!/usr/bin/env python3
"""Independent selected births, skipped-arm history guards and shared leaves."""
import argparse
from pathlib import Path
import sys

import global_constant_stdclass_new_protocol as protocol
import global_constant_stdclass_new_review_sources as sources
import global_constant_stdclass_protocol as birth

# Source wrappers share the family module; retain both case sets.
full_cases = dict(sources.family.CASES)
import global_constant_stdclass_new_shorthand_review_sources as shorthand

sources.family.CASES = dict(full_cases, **shorthand.family.CASES)
common, text = protocol.common, protocol.text


def selected_birth(start, suffix, selected, skipped_field, truth):
    before, born, done = ('S_' + label + '_' + suffix for label in ['before', 'born', 'done'])
    obj, site, choice = ('n_object_' + suffix, 'porigin_site_' + suffix, 'porigin_choice_' + suffix)
    context, record = 'pconstantcontext_' + suffix, 'pconstantstdobject_' + suffix
    values = [*birth.reach(before, start, 0),
        f'{before}.CONSTCONTEXT = ({context})', f'{context}.ORIGIN = porigin_decl',
        f'{before}.ORIGIN = ({site})', f'$(0 < |{context}.FACTS|)',
        f'{site} =/= $constant_child(porigin_decl,[PCFIELD 1])',
        f'$reference_origin_parent({site},1) = (({choice},[PCFIELD {selected}]))',
        f'$constant_recorded_truth({before},$constant_child({choice},[PCFIELD 0])) = ' +
            ('eps' if truth is None else '(' + str(truth).lower() + ')'),
        f'$constant_facts_valid({before},porigin_decl,{context}.FACTS)',
        f'$constant_branches_valid({before})', f'$constant_context_valid({before})',
        f'$global_std_ready({before},$ptascii("stdClass"))',
        f'$global_std_source({before},{site},porigin_decl,|{before}.DECLARATIONS|)']
    wrong_site = '$constant_child(' + choice + ',[PCFIELD 0])'
    if skipped_field is not None:
        skipped = 'porigin_skipped_' + suffix
        wrong_site = skipped
        # Pure malformed history: never drive this projected state.
        values += [f'{skipped} = $constant_child({choice},[PCFIELD {skipped_field}])',
            f'$constant_facts_below({context}.FACTS,{skipped}) = false',
            f'pconstantfact_skipped_{suffix} = {{ORIGIN {skipped}, VALUE eps, CLASS PVOBJECT, LOOKUP eps}}',
            f'pconstantcontext_skipped_{suffix} = {context}[.FACTS = $constant_fact_put({context}.FACTS,pconstantfact_skipped_{suffix})]',
            f'S_skipped_{suffix} = {before}[.CONSTCONTEXT = (pconstantcontext_skipped_{suffix})]',
            f'$constant_facts_valid(S_skipped_{suffix},porigin_decl,pconstantcontext_skipped_{suffix}.FACTS)',
            f'~$constant_branches_valid(S_skipped_{suffix})',
            f'~$constant_context_valid(S_skipped_{suffix})',
            f'~$global_std_ready(S_skipped_{suffix},$ptascii("stdClass"))']
    values += [f'porigin_wrong_{suffix} = {wrong_site}', *birth.step(born, before),
        f'{born}.TODO = (DEFAULT_NEW_ARGS pdefaultnew_{suffix}) :: ptask_born_{suffix}*',
        f'{obj} = |{before}.OBJECTS|', f'pdefaultnew_{suffix}.OBJECT = {obj}',
        f'pdefaultnew_{suffix}.SITE = {site}', f'pdefaultnew_{suffix}.ARGUMENTS = eps',
        f'pdefaultnew_{suffix}.VALUES = eps', f'pdefaultnew_{suffix}.INDEX = 0',
        f'{born}.OBJECTS = {before}.OBJECTS ++ [STDINSTANCE]',
        f'{born}.ALLOCATIONS = {before}.ALLOCATIONS ++ [HOBJECT {obj}]',
        f'n_prefix_{suffix} = |{before}.DECLARATIONS|',
        f'{record} = {{OBJECT {obj}, SITE {site}, DECL porigin_decl, PREFIX n_prefix_{suffix}, COMPLETE false}}',
        f'{born}.CONSTANTSTDOBJECTS = {before}.CONSTANTSTDOBJECTS ++ [{record}]',
        f'$global_std_pending({born},pdefaultnew_{suffix})',
        f'$heap_owners($heap_graph({born}),HOBJECT {obj}) = 1',
        f'~$global_std_completed({born},{record})',
        f'~$global_constant_flow({born},{choice},porigin_decl,eps,PVSTDCLASS {obj} {site},{born}.USERCONSTANTS,$global_constant_reads({born},porigin_decl),eps)',
        *birth.step(done, born), f'{done}.RESULT = KNOWN (POBJECT {obj})',
        f'{done}.CONSTANTSTDOBJECTS = {before}.CONSTANTSTDOBJECTS ++ [{record}[.COMPLETE = true]]',
        f'$global_std_completed({done},{record}[.COMPLETE = true])',
        f'$global_new_value_class({done},{site}) = PVSTDCLASS {obj} {site}',
        f'$constant_value_class_valid({done},POBJECT {obj},PVSTDCLASS {obj} {site})',
        f'$global_constant_flow({done},{choice},porigin_decl,eps,PVSTDCLASS {obj} {site},{done}.USERCONSTANTS,$global_constant_reads({done},porigin_decl),eps)',
        f'~$global_constant_flow({done},{choice},porigin_decl,eps,PVSTDCLASS {obj} porigin_wrong_{suffix},{done}.USERCONSTANTS,$global_constant_reads({done},porigin_decl),eps)',
        f'~$default_cacheable(PVSTDCLASS {obj} {site})',
        f'~$constant_callable_foldable(PVSTDCLASS {obj} {site})']
    return values


def delivery(state, start, query):
    after = state + '_value'
    values = [*common.reach(state,start,0,query), *common.public(state),
        f'{state}.TODO = (CONFIG_INVOKE pconfigcall_{state}) :: ptask_{state}*',
        f'$dynamic_global_constant_valid({state},pconfigcall_{state})',
        f'$dynamic_global_constant_value({state},{text(query)}) = (PARRAY n_root)',
        f'H_{state} = $heap_graph({state})',
        f'n_rootowners_{state} = $heap_owners(H_{state},HARRAY n_root)',
        *common.step(after,state,'PARRAY n_root'), f'{after}.TODO = ptask_{state}*',
        f'H_{after} = $heap_graph({after})', f'H_{after}.NODES = H_{state}.NODES',
        f'H_{after}.EDGES = H_{state}.EDGES',
        f'$heap_owners(H_{after},HARRAY n_root) = $(n_rootowners_{state} + 1)']
    for suffix in ['first','second']:
        values += [f'$heap_owners(H_{after},HOBJECT n_object_{suffix}) = $heap_owners(H_{state},HOBJECT n_object_{suffix})']
    values += [f'{after}.{field} = {state}.{field}' for field in
        ['ARRAYS','OBJECTS','OBJECTPROPS','OBJECTTABLES','ALLOCATIONS','STORE','USERCONSTANTS','CONSTANTSTDOBJECTS']]
    return values


def checks(initial, name, stdout, responses_unused, restore_line_unused):
    short = name.startswith('shorthand-')
    query = 'V61_SHORT_TREE' if short else 'V61_REVIEW_TREE'
    values = [*initial, *selected_birth('S_initial','first',0 if short else 1,2,None if short else True),
        'S_before_first.CONSTANTSTDOBJECTS = eps',
        *selected_birth('S_done_first','second',2,None if short else 1,False),
        'S_before_second.CONSTANTSTDOBJECTS = S_done_first.CONSTANTSTDOBJECTS',
        'n_object_first =/= n_object_second', 'porigin_site_first =/= porigin_site_second',
        'porigin_choice_first =/= porigin_choice_second',
        '$constant_fact_at(pconstantcontext_second.FACTS,porigin_site_first) = (pconstantfact_first)',
        'pconstantfact_first.VALUE = eps',
        'pconstantfact_first.CLASS = PVSTDCLASS n_object_first porigin_site_first',
        f'S_first_header_found = $test_constant_seek(S_done_second,0,{text(query)},3000)',
        'S_first_header = $test_running(S_first_header_found)',
        f'$user_constant_at(S_first_header.USERCONSTANTS,{text(query)}) = (puserconstant)',
        'puserconstant.VALUE = PARRAY n_root',
        'S_first_header.ARRAYS[n_root].ITEMS = [ENTRY (KINT 0) (DIRECT (PFLOAT 9221120237041090560)),ENTRY (KINT 1) (DIRECT (PARRAY n_child))]',
        'S_first_header.ARRAYS[n_child].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_object_first)),ENTRY (KINT 1) (DIRECT (POBJECT n_object_second)),ENTRY (KINT 2) (DIRECT (PARRAY n_empty))]',
        '$pvclass_get(puserconstant.CLASS,KINT 1) = (pvalueclass_child)',
        '$pvclass_get(pvalueclass_child,KINT 0) = (PVSTDCLASS n_object_first porigin_site_first)',
        '$pvclass_get(pvalueclass_child,KINT 1) = (PVSTDCLASS n_object_second porigin_site_second)',
        *delivery('S_first','S_first_header',query), 'S_first = S_first_header',
        'S_first.CONSTANTSTDOBJECTS = [pconstantstdobject_first[.COMPLETE = true],pconstantstdobject_second[.COMPLETE = true]]',
        'n_rootowners_S_first = 1']
    finish = 'S_first_value'
    if not short:
        values += [*delivery('S_again','S_first_value',query), 'n_rootowners_S_again = 1',
            '$lookup(S_again.ENV,$ptascii("copy")) = (n_copy)',
            'S_again.STORE[n_copy] = DEFINED (PARRAY n_copy_root)', 'n_copy_root =/= n_root',
            'S_again.ARRAYS[n_copy_root].ITEMS = [ENTRY (KINT 0) (DIRECT (PFLOAT 9221120237041090560)),ENTRY (KINT 1) (DIRECT (PARRAY n_copy_child))]',
            'n_copy_child =/= n_child',
            'S_again.ARRAYS[n_copy_child].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_object_first)),ENTRY (KINT 1) (DIRECT (POBJECT n_object_second)),ENTRY (KINT 2) (DIRECT (PARRAY n_empty)),ENTRY (KINT 3) (DIRECT pvalue_tail)]',
            '$string_bytes(pvalue_tail) = ($ptascii("tail"))',
            'S_again.ARRAYS[n_child].ITEMS = S_first.ARRAYS[n_child].ITEMS']
        for suffix, value in [('first',31),('second',37)]:
            values += [*birth.property_value('S_again','n_object_'+suffix,value,suffix),
                f'$heap_owners(H_S_again,HOBJECT n_object_{suffix}) = 3']
        values += [*delivery('S_last','S_again_value',query), 'n_rootowners_S_last = 1',
            '~((HARRAY n_copy_root) <- S_last.ALLOCATIONS)', '~((HARRAY n_copy_child) <- S_last.ALLOCATIONS)']
        finish = 'S_last_value'
    values += [f'S_final = $drive_steps({finish},5000)', 'S_final.COMPLETION = NORMAL',
        'S_final.TODO = eps', 'S_final.FRAMES = eps', 'S_final.CURRENT = eps', 'S_final.CONSTCONTEXT = eps',
        '$test_outputs(S_final.EVENTS) = ' + protocol.term(stdout), *common.public('S_final'),
        'S_final.CONSTANTSTDOBJECTS = S_first.CONSTANTSTDOBJECTS',
        '$heap_owners($heap_graph(S_final),HARRAY n_root) = 2']
    for suffix, value in [('first',31),('second',37)]:
        values += [f'$heap_owners(H_S_first,HOBJECT n_object_{suffix}) = 1',
            f'$heap_owners($heap_graph(S_final),HOBJECT n_object_{suffix}) = 1',
            *birth.property_value('S_final','n_object_'+suffix,value,suffix+'_final')]
    return values


protocol.sources, protocol.checks = sources, checks
protocol.packet.sources = sources
family_fingerprint = sources.family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(protocol.ROOT)): sources.family.sha(__file__)})


sources.family.fingerprint = fingerprint

if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--case', choices=sources.family.CASES, required=True)
    args, remaining = parser.parse_known_args()
    sources.family.CASES = {args.case:sources.family.CASES[args.case]}
    sys.argv = [sys.argv[0], *remaining]
    raise SystemExit(0 if protocol.packet.main() else 1)
