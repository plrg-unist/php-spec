#!/usr/bin/env python3
"""Reached quiet coalesce capture, composed leaf flow and temporary retirement."""
from pathlib import Path

import global_constant_stdclass_new_protocol as protocol
import global_constant_stdclass_coalesce_review_sources as sources
import global_constant_stdclass_protocol as std

common, text = protocol.common, protocol.text
PREFIX = r'''
dec $test_v62_quiet(pstate) : bool
def $test_v62_quiet(S) = true
  -- if S.TODO = (COALESCE_QUIET expression z_left z_right) :: ptask_tail*
  -- if S.CONSTCONTEXT =/= eps
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES,porigin) = (NExprBinaryOpCoalesce expression_left expression metadata)
def $test_v62_quiet(S) = false -- otherwise
dec $test_v62_seek(pstate, nat) : pstate
def $test_v62_seek(S,0) = S
def $test_v62_seek(S,n) = S
  -- if $(n > 0)
  -- if $test_v62_quiet(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_v62_seek(S,n) = $test_v62_seek($drive_steps($test_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_v62_quiet(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def birth(start, suffix):
    before, born, done = ('S_' + label + '_' + suffix for label in ['before','born','done'])
    obj, site, record = 'n_' + suffix, 'porigin_' + suffix, 'pconstantstdobject_' + suffix
    return [*std.reach(before,start,0), f'{before}.ORIGIN = ({site})',
        f'{before}.CONSTCONTEXT = (pconstantcontext_{suffix})',
        f'pconstantcontext_{suffix}.ORIGIN = porigin_decl',
        f'pconstantcontext_{suffix}.FACTS =/= eps',
        f'$global_std_ready({before},$ptascii("stdClass"))',
        *std.step(born,before), f'{obj} = |{before}.OBJECTS|',
        f'{born}.OBJECTS = {before}.OBJECTS ++ [STDINSTANCE]',
        f'{born}.ALLOCATIONS = {before}.ALLOCATIONS ++ [HOBJECT {obj}]',
        f'$global_std_record({born}.CONSTANTSTDOBJECTS,{obj}) = ({record})',
        f'{born}.CONSTANTSTDOBJECTS = {before}.CONSTANTSTDOBJECTS ++ [{record}]',
        f'{record}.OBJECT = {obj}', f'{record}.SITE = {site}', f'{record}.DECL = porigin_decl',
        f'~{record}.COMPLETE', f'$heap_owners($heap_graph({born}),HOBJECT {obj}) = 1',
        *std.step(done,born), f'{done}.RESULT = KNOWN (POBJECT {obj})',
        f'{done}.CONSTANTSTDOBJECTS = {before}.CONSTANTSTDOBJECTS ++ [{record}[.COMPLETE = true]]',
        f'$global_std_completed({done},{record}[.COMPLETE = true])',
        f'$constant_value_class_valid({done},POBJECT {obj},PVSTDCLASS {obj} {site})']


def flow(state, origin, obj, site):
    return f'$global_constant_flow({state},{origin},porigin_decl,eps,PVSTDCLASS {obj} {site},{state}.USERCONSTANTS,$global_constant_reads({state},porigin_decl),eps)'


def checks(initial, name_unused, stdout, responses_unused, restore_line_unused):
    values = [*initial, *birth('S_initial','left'),
        'S_before_left.CONSTANTSTDOBJECTS = eps',
        'S_quiet_found = $test_v62_seek(S_done_left,3000)',
        r'S_quiet_found.COMPLETION = NORMAL \/ S_quiet_found.COMPLETION = BUDGET',
        'S_quiet = $test_running(S_quiet_found)', '$test_v62_quiet(S_quiet)', *common.public('S_quiet'),
        'S_quiet.ORIGIN = (porigin_coalesce_left)',
        'S_quiet.TODO = (COALESCE_QUIET expression_right z_left z_right) :: ptask_quiet*',
        '$compiled_redirect(S_quiet,porigin_coalesce_left) = eps',
        'porigin_quiet_dim = $constant_child(porigin_coalesce_left,[PCFIELD 0])',
        'porigin_skipped_right = $constant_child(porigin_coalesce_left,[PCFIELD 1])',
        '$constant_callable_path(S_quiet,porigin_left,porigin_quiet_dim)',
        '$reference_origin_parent(porigin_coalesce_left,1) = ((porigin_ternary_left,[PCFIELD 1]))',
        '$compiled_redirect(S_quiet,porigin_ternary_left) = eps',
        '$constant_recorded_truth(S_quiet,$constant_child(porigin_ternary_left,[PCFIELD 0])) = (true)',
        'S_quiet.BASE = BASE_DIM pbase_array poperand_key z_key',
        'S_base = $quiet_base(S_quiet,pbase_array,z_key)',
        'S_base.COMPLETION = NORMAL', 'S_base.RESULT = KNOWN (PARRAY n_temporary)',
        'S_quiet.ARRAYS[n_temporary].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_left))]',
        '(HARRAY n_temporary) <- S_quiet.ALLOCATIONS',
        'H_quiet = $heap_graph(S_quiet)',
        '$heap_edge_owners(HOBJECT n_left,H_quiet.EDGES,[HARRAY n_temporary]) = 1',
        flow('S_quiet','porigin_coalesce_left','n_left','porigin_left'),
        flow('S_quiet','porigin_ternary_left','n_left','porigin_left'),
        'S_incomplete = S_quiet[.CONSTANTSTDOBJECTS[0].COMPLETE = false]',
        '~' + flow('S_incomplete','porigin_coalesce_left','n_left','porigin_left'),
        '~' + flow('S_quiet','porigin_coalesce_left','n_left','porigin_skipped_right'),
        *common.step('S_captured','S_quiet','POBJECT n_left'),
        'S_captured.TODO = ptask_quiet*', 'S_captured.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_captured.CONSTCONTEXT = (pconstantcontext_captured)',
        '$constant_fact_at(pconstantcontext_captured.FACTS,porigin_quiet_dim) = (pconstantfact_quiet)',
        'pconstantfact_quiet.VALUE = eps', 'pconstantfact_quiet.CLASS = PVSTDCLASS n_left porigin_left',
        'pconstantfact_quiet.LOOKUP = eps',
        '$constant_recorded_null(S_captured,porigin_quiet_dim) = (false)',
        '$constant_fact_at(pconstantcontext_captured.FACTS,porigin_skipped_right) = eps',
        'S_captured.ARRAYS = S_quiet.ARRAYS', 'S_captured.OBJECTS = S_quiet.OBJECTS',
        'S_captured.CONSTANTSTDOBJECTS = S_quiet.CONSTANTSTDOBJECTS',
        # Pure malformed observation history; this projection is never driven.
        'pconstantfact_skipped = {ORIGIN porigin_skipped_right, VALUE eps, CLASS PVOBJECT, LOOKUP eps}',
        'pconstantcontext_skipped = pconstantcontext_captured[.FACTS = $constant_fact_put(pconstantcontext_captured.FACTS,pconstantfact_skipped)]',
        'S_skipped = S_captured[.CONSTCONTEXT = (pconstantcontext_skipped)]',
        '$constant_facts_valid(S_skipped,porigin_decl,pconstantcontext_skipped.FACTS)',
        '~$constant_branches_valid(S_skipped)', '~$constant_context_valid(S_skipped)',
        *birth('S_captured','right'),
        'n_right =/= n_left', 'S_before_right.CONSTANTSTDOBJECTS = S_done_left.CONSTANTSTDOBJECTS',
        '$reference_origin_parent(porigin_right,1) = ((porigin_ternary_right,[PCFIELD 2]))',
        '$reference_origin_parent(porigin_ternary_right,1) = ((porigin_coalesce_right,[PCFIELD 1]))',
        '$origin_node(S_before_right.SOURCES,porigin_coalesce_right) = (NExprBinaryOpCoalesce expression_null expression_ternary metadata_coalesce)',
        '$compiled_redirect(S_before_right,porigin_coalesce_right) = eps',
        '$compiled_redirect(S_before_right,porigin_ternary_right) = eps',
        '$constant_recorded_null(S_before_right,$constant_child(porigin_coalesce_right,[PCFIELD 0])) = (true)',
        '$constant_recorded_truth(S_before_right,$constant_child(porigin_ternary_right,[PCFIELD 0])) = (false)',
        '$constant_fact_at(pconstantcontext_right.FACTS,porigin_quiet_dim) = (pconstantfact_quiet)',
        '~' + flow('S_born_right','porigin_coalesce_right','n_right','porigin_right'),
        flow('S_done_right','porigin_coalesce_right','n_right','porigin_right'),
        '~' + flow('S_done_right','porigin_coalesce_right','n_right','porigin_left'),
        *common.reach('S_query','S_done_right',0,'V62_REVIEW_TREE'), *common.public('S_query'),
        'S_query.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_query*',
        '$dynamic_global_constant_valid(S_query,pconfigcall)',
        '$user_constant_at(S_query.USERCONSTANTS,$ptascii("V62_REVIEW_TREE")) = (puserconstant)',
        'puserconstant.VALUE = PARRAY n_root',
        'S_query.ARRAYS[n_root].ITEMS = [ENTRY (KINT 0) (DIRECT (PFLOAT 9221120237041090560)),ENTRY (KINT 1) (DIRECT (PARRAY n_child))]',
        'S_query.ARRAYS[n_child].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_left)),ENTRY (KINT 1) (DIRECT (POBJECT n_right)),ENTRY (KINT 2) (DIRECT (PARRAY n_empty))]',
        '$pvclass_get(puserconstant.CLASS,KINT 1) = (pvalueclass_child)',
        '$pvclass_get(pvalueclass_child,KINT 0) = (PVSTDCLASS n_left porigin_left)',
        '$pvclass_get(pvalueclass_child,KINT 1) = (PVSTDCLASS n_right porigin_right)',
        'S_query.CONSTANTSTDOBJECTS = [pconstantstdobject_left[.COMPLETE = true],pconstantstdobject_right[.COMPLETE = true]]',
        '~((HARRAY n_temporary) <- S_query.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_query),HARRAY n_temporary) = 0',
        '$dynamic_global_constant_value(S_query,$ptascii("V62_REVIEW_TREE")) = (PARRAY n_root)',
        'H_query = $heap_graph(S_query)', '$heap_owners(H_query,HARRAY n_root) = 1',
        '$heap_owners(H_query,HOBJECT n_left) = 1', '$heap_owners(H_query,HOBJECT n_right) = 1',
        *common.step('S_value','S_query','PARRAY n_root'), 'S_value.TODO = ptask_query*',
        'H_value = $heap_graph(S_value)', 'H_value.NODES = H_query.NODES', 'H_value.EDGES = H_query.EDGES',
        '$heap_owners(H_value,HARRAY n_root) = 2', '$heap_owners(H_value,HOBJECT n_left) = 1',
        '$heap_owners(H_value,HOBJECT n_right) = 1']
    values += [f'S_value.{field} = S_query.{field}' for field in
        ['ARRAYS','OBJECTS','OBJECTPROPS','OBJECTTABLES','ALLOCATIONS','STORE','USERCONSTANTS','CONSTANTSTDOBJECTS']]
    values += ['S_final = $drive_steps(S_value,5000)', 'S_final.COMPLETION = NORMAL',
        'S_final.TODO = eps', 'S_final.FRAMES = eps', 'S_final.CURRENT = eps', 'S_final.CONSTCONTEXT = eps',
        '$test_outputs(S_final.EVENTS) = ' + protocol.term(stdout), *common.public('S_final'),
        'S_final.CONSTANTSTDOBJECTS = S_query.CONSTANTSTDOBJECTS',
        '~((HARRAY n_temporary) <- S_final.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_final),HARRAY n_root) = 2']
    for suffix, value in [('left',31),('right',37)]:
        values += [f'$heap_owners($heap_graph(S_final),HOBJECT n_{suffix}) = 1',
            *std.property_value('S_final','n_'+suffix,value,'final_'+suffix)]
    return values


protocol.sources, protocol.checks = sources, checks
protocol.PREFIX += PREFIX
protocol.packet.sources = sources
family_fingerprint = sources.family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(protocol.ROOT)): sources.family.sha(__file__)})


sources.family.fingerprint = fingerprint

if __name__ == '__main__':
    raise SystemExit(0 if protocol.packet.main() else 1)
