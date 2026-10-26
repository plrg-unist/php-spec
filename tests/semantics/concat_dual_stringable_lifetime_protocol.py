#!/usr/bin/env python3
"""Two acquired operands, distinct cast roots and ordered normal retirement."""
import base64
import json

import concat_dual_stringable_lifetime_cases as cases
import integer_operator_warning_protocol as shared

CASES = tuple(cases.CASES)
HELPERS = shared.HELPERS + r'''
dec $concat_dual_frontier(pstate, nat) : bool
def $concat_dual_frontier(S, 0) = true
  -- if $concat_owned_plan(S) = (pconcatleft)
  -- if $concat_owned_dual(S, pconcatleft)
'''
HELPERS += r'''
def $concat_dual_frontier(S, 1) = true
  -- if S.TODO = (CALL_ARGS (METHOD_TARGET n_method porigin_method) eps 0 eps (porigin_site) z) :: (STRINGIFY_RESULT n_method porigin_site z) :: (CONCAT_OWNED_LEFT pconcatleft) :: ptask_tail*
  -- if n_method = pconcatleft.OBJECT
def $concat_dual_frontier(S, 2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n_method porigin_method
  -- if pcallcontext.RECEIVER = (n_method)
  -- if pcallcontext.CALLSITE = (porigin_site)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (STRINGIFY_RESULT n_method porigin_site z) :: (CONCAT_OWNED_LEFT pconcatleft) :: ptask_tail*
  -- if n_method = pconcatleft.OBJECT
'''
HELPERS += r'''
def $concat_dual_frontier(S, 5) = true
  -- if S.TODO = (CALL_ARGS (METHOD_TARGET n_method porigin_method) eps 0 eps (porigin_site) z) :: (STRINGIFY_RESULT n_method porigin_site z) :: (CONCAT_OWNED_RIGHT pconcatleft pvalue_left (n_method)) :: ptask_tail*
  -- if pconcatleft.RIGHT = KNOWN (POBJECT n_method)
def $concat_dual_frontier(S, 6) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n_method porigin_method
  -- if pcallcontext.RECEIVER = (n_method)
  -- if pcallcontext.CALLSITE = (porigin_site)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (STRINGIFY_RESULT n_method porigin_site z) :: (CONCAT_OWNED_RIGHT pconcatleft pvalue_left (n_method)) :: ptask_tail*
  -- if pconcatleft.RIGHT = KNOWN (POBJECT n_method)
'''
HELPERS += r'''
def $concat_dual_frontier(S, 3) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (STRINGIFY_RESULT n porigin z) :: (CONCAT_OWNED_LEFT pconcatleft) :: ptask*
  -- if S.RESULT = KNOWN pvalue
  -- if $string_bytes(pvalue) = ($ptascii("L"))
def $concat_dual_frontier(S, 4) = true
  -- if S.TODO = (CONCAT_OWNED_LEFT pconcatleft) :: ptask*
  -- if S.RESULT = KNOWN pvalue
  -- if $string_bytes(pvalue) = ($ptascii("L"))
def $concat_dual_frontier(S, 7) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (STRINGIFY_RESULT n porigin z) :: (CONCAT_OWNED_RIGHT pconcatleft pvalue_left (n)) :: ptask*
  -- if S.RESULT = KNOWN pvalue
  -- if $string_bytes(pvalue) = ($ptascii("R"))
def $concat_dual_frontier(S, 8) = true
  -- if S.TODO = (CONCAT_OWNED_RIGHT pconcatleft pvalue_left n?) :: ptask*
  -- if S.RESULT = KNOWN pvalue
  -- if $string_bytes(pvalue) = ($ptascii("R"))
def $concat_dual_frontier(S, 9) = true
  -- if S.TODO = (CONCAT_OWNED_RELEASE pconcatleft) :: ptask*
def $concat_dual_frontier(S, 10) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (CONCAT_OWNED_RIGHT_RELEASE pconcatleft) :: ptask*
def $concat_dual_frontier(S, 11) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (CONCAT_OWNED_DONE pconcatleft) :: ptask*
def $concat_dual_frontier(S, 12) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
  -- if pdestructionoperation.SOURCE = CONCAT_OWNED_RELEASE pconcatleft
  -- if pdestructionoperation.PENDING = eps
def $concat_dual_frontier(S, 13) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
  -- if pdestructionoperation.SOURCE = CONCAT_OWNED_RIGHT_RELEASE pconcatleft
  -- if pdestructionoperation.PENDING = eps
def $concat_dual_frontier(S, 14) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("f")
def $concat_dual_frontier(S, 15) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (CONCAT_LEFT expression false false 25) :: ptask*
  -- if S.RESULT = KNOWN (POBJECT n)
def $concat_dual_frontier(S, 16) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("g")
def $concat_dual_frontier(S, 17) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (CONCAT_RIGHT (KNOWN (POBJECT n_left)) false false 25) :: ptask*
  -- if S.RESULT = KNOWN (POBJECT n_right)
def $concat_dual_frontier(S, n) = false -- otherwise
dec $concat_dual_seek(pstate, nat, nat) : pstate
def $concat_dual_seek(S, n_stage, n) = S -- if $concat_dual_frontier(S, n_stage)
def $concat_dual_seek(S, n_stage, n) = S
  -- if ~$concat_dual_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $concat_dual_seek(S, n_stage, n) = S
  -- if ~$concat_dual_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $concat_dual_seek(S, n_stage, n) = $concat_dual_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$concat_dual_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
'''


def seek(checks, label, start, stage):
    checks += [f'{label}_found = $concat_dual_seek({start}, {stage}, 3000)',
               f'{label}_found.COMPLETION = NORMAL \\/ {label}_found.COMPLETION = BUDGET',
               f'{label} = {label}_found[.COMPLETION = NORMAL]',
               f'$concat_dual_frontier({label}, {stage})']


def prefix(program, path):
    checks = ['S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
              'S_initial.COMPLETION = BUDGET']
    seek(checks, 'S_factory', 'S_initial', 14)
    checks += ['S_factory.CURRENT = (pcallcontext_f)',
               'pcallcontext_f.CALLSITE = (porigin_left)',
               '$call_descriptors_valid(S_factory)', '$heap_valid($heap_graph(S_factory))']
    seek(checks, 'S_factory_return', 'S_factory', 15)
    checks += ['S_factory_return.RESULT = KNOWN (POBJECT n_object)',
               '$stringable_instance(S_factory_return, n_object)',
               '$heap_owners($heap_prune($heap_graph(S_factory_return)), HOBJECT n_object) = 1',
               '$integer_outputs(S_factory_return.EVENTS) = ($ptascii("P;"))',
               '$call_descriptors_valid(S_factory_return)', '$heap_valid($heap_graph(S_factory_return))']
    seek(checks, 'S_factory_g', 'S_factory_return', 16)
    checks += ['S_factory_g.CURRENT = (pcallcontext_g)',
               'pcallcontext_g.CALLSITE = (porigin_right)',
               'S_factory_g.FRAMES = pframe_g :: pframe_g_tail*',
               '$heap_count(HOBJECT n_object, $tasks_nodes(pframe_g.TODO)) = 1',
               '$call_descriptors_valid(S_factory_g)', '$heap_valid($heap_graph(S_factory_g))']
    seek(checks, 'S_factory_g_return', 'S_factory_g', 17)
    checks += ['S_factory_g_return.TODO = (CONCAT_RIGHT (KNOWN (POBJECT n_object)) false false 25) :: ptask_tail*',
               'S_factory_g_return.RESULT = KNOWN (POBJECT n_right_object)',
               'n_right_object =/= n_object', '$stringable_instance(S_factory_g_return, n_right_object)',
               '$heap_count(HOBJECT n_object, $tasks_nodes(S_factory_g_return.TODO)) = 1',
               '$heap_owners($heap_prune($heap_graph(S_factory_g_return)), HOBJECT n_right_object) = 1',
               '$integer_outputs(S_factory_g_return.EVENTS) = ($ptascii("P;Q;"))',
               '$call_descriptors_valid(S_factory_g_return)', '$heap_valid($heap_graph(S_factory_g_return))']
    seek(checks, 'S_entry', 'S_factory_g_return', 0)
    checks += ['$concat_owned_plan(S_entry) = (pconcatleft)',
               'S_entry.TODO = (CONCAT_PREP (KNOWN (POBJECT n_object)) (KNOWN (POBJECT n_right_object)) false false 25) :: ptask_tail*',
               'S_entry.ORIGIN = (porigin_parent)', 'pconcatleft.SITE = porigin_parent',
               'pconcatleft.LINE = 25', 'pconcatleft.OBJECT = n_object',
               'pconcatleft.RIGHT = KNOWN (POBJECT n_right_object)', 'pconcatleft.RIGHTCONST = false',
               '$origin_child((porigin_parent), [PCFIELD 0]) = (porigin_left)',
               '$origin_child((porigin_parent), [PCFIELD 1]) = (porigin_right)',
               '$lookup(S_entry.ENV, $ptascii("seed")) = eps',
               '$concat_owned_dual(S_entry, pconcatleft)', '$concat_owned_live(S_entry, pconcatleft)',
               '$concat_owned_ready(S_entry, pconcatleft.RIGHT)',
               '$heap_owners($heap_prune($heap_graph(S_entry)), HOBJECT n_object) = 1',
               '$heap_owners($heap_prune($heap_graph(S_entry)), HOBJECT n_right_object) = 1',
               '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))']
    for name in ('v', 'leftcalls', 'rightcalls', 'adrops', 'bdrops'):
        checks += [f'$lookup(S_entry.ENV, $ptascii("{name}")) = (n_{name})',
                   f'S_entry.STORE[n_{name}] = DEFINED (PINT {100 if name == "v" else 0})']
    seek(checks, 'S_pendingS', 'S_entry', 1)
    checks += ['S_pendingS.TODO = (CALL_ARGS (METHOD_TARGET n_object porigin_method_left) eps 0 eps (porigin_left) 25) :: (STRINGIFY_RESULT n_object porigin_left 25) :: (CONCAT_OWNED_LEFT pconcatleft) :: ptask_tail*',
               '$task_nodes(CONCAT_OWNED_LEFT pconcatleft) = [HOBJECT n_object, HOBJECT n_right_object]',
               '$heap_count(HOBJECT n_object, $tasks_nodes(S_pendingS.TODO)) = 3',
               '$heap_count(HOBJECT n_right_object, $tasks_nodes(S_pendingS.TODO)) = 1',
               '$call_descriptors_valid(S_pendingS)', '$heap_valid($heap_graph(S_pendingS))']
    seek(checks, 'S_enteredS', 'S_pendingS', 2)
    checks += ['S_enteredS.CURRENT = (pcallcontext_s)',
               'pcallcontext_s.TARGET = METHOD_TARGET n_object porigin_method_left',
               'pcallcontext_s.RECEIVER = (n_object)', 'pcallcontext_s.CALLSITE = (porigin_left)',
               'S_enteredS.FRAMES = pframe_s :: pframe_s_tail*',
               'pframe_s.TODO = (STRINGIFY_RESULT n_object porigin_left 25) :: (CONCAT_OWNED_LEFT pconcatleft) :: ptask_tail*',
               '$heap_count(HOBJECT n_object, $tasks_nodes(pframe_s.TODO)) = 2',
               '$heap_count(HOBJECT n_right_object, $tasks_nodes(pframe_s.TODO)) = 1',
               'S_enteredS.STORE[n_v] = DEFINED (PINT 100)',
               '$stringify_chain_valid(S_enteredS, S_enteredS.CURRENT, S_enteredS.FRAMES)',
               '$call_descriptors_valid(S_enteredS)', '$heap_valid($heap_graph(S_enteredS))']
    return checks


def returned_left(checks):
    seek(checks, 'S_returnS', 'S_enteredS', 3)
    checks += ['S_returnS.TODO = (STRINGIFY_RESULT n_object porigin_left 25) :: (CONCAT_OWNED_LEFT pconcatleft) :: ptask_tail*',
               'S_returnS.RESULT = KNOWN pvalue_left', '$string_bytes(pvalue_left) = ($ptascii("L"))',
               'S_returnS.STORE[n_leftcalls] = DEFINED (PINT 1)',
               'S_returnS.STORE[n_rightcalls] = DEFINED (PINT 0)',
               'S_returnS.STORE[n_adrops] = DEFINED (PINT 0)', 'S_returnS.STORE[n_bdrops] = DEFINED (PINT 0)',
               '$heap_owners($heap_prune($heap_graph(S_returnS)), HOBJECT n_object) = 2',
               '$heap_owners($heap_prune($heap_graph(S_returnS)), HOBJECT n_right_object) = 1',
               '$call_descriptors_valid(S_returnS)', '$heap_valid($heap_graph(S_returnS))']
    seek(checks, 'S_left', 'S_returnS', 4)
    checks += ['S_left.TODO = (CONCAT_OWNED_LEFT pconcatleft) :: ptask_tail*',
               'S_left.RESULT = KNOWN pvalue_left',
               '$heap_owners($heap_prune($heap_graph(S_left)), HOBJECT n_object) = 1',
               '$heap_owners($heap_prune($heap_graph(S_left)), HOBJECT n_right_object) = 1',
               '$integer_outputs(S_left.EVENTS) = ($ptascii("P;Q;S;"))',
               '$call_descriptors_valid(S_left)', '$heap_valid($heap_graph(S_left))']


HELPERS += r'''
dec $concat_dual_output_only(pevent*) : bool
def $concat_dual_output_only(eps) = true
def $concat_dual_output_only(pevent :: pevent_tail*) = ($integer_is_output(pevent) /\ $concat_dual_output_only(pevent_tail*))
'''


def conditions(name, program, path, stdout):
    assert name in CASES
    checks = prefix(program, path)
    returned_left(checks)
    checks += [
        '~$concat_owned_source(S_entry, pconcatleft[.SITE = porigin_left])',
        '~$concat_owned_source(S_entry, pconcatleft[.LINE = 24])',
        '~$concat_owned_dual(S_entry, pconcatleft[.RIGHT = KNOWN (POBJECT n_object)])',
        '$concat_owned_plan(S_entry[.TODO = (CONCAT_PREP (KNOWN (POBJECT n_object)) (KNOWN (POBJECT n_object)) false false 25) :: ptask_tail*]) = eps',
        '$return_discard(S_left, CONCAT_OWNED_LEFT pconcatleft) = S_left',
    ]
    seek(checks, 'S_pendingT', 'S_left', 5)
    checks += [
        'S_pendingT.TODO = (CALL_ARGS (METHOD_TARGET n_right_object porigin_method_right) eps 0 eps (porigin_right) 25) :: (STRINGIFY_RESULT n_right_object porigin_right 25) :: (CONCAT_OWNED_RIGHT pconcatleft pvalue_left (n_right_object)) :: ptask_tail*',
        '$task_nodes(CONCAT_OWNED_RIGHT pconcatleft pvalue_left (n_right_object)) = [HOBJECT n_object, HOBJECT n_right_object]',
        '$heap_count(HOBJECT n_object, $tasks_nodes(S_pendingT.TODO)) = 1',
        '$heap_count(HOBJECT n_right_object, $tasks_nodes(S_pendingT.TODO)) = 3',
        '~$stringify_consumer_receiver_valid(S_pendingT, n_object, CONCAT_OWNED_RIGHT pconcatleft pvalue_left (n_right_object))',
        '~$stringify_source(S_pendingT, porigin_left, 25, CONCAT_OWNED_RIGHT pconcatleft pvalue_left (n_right_object))',
        '$call_descriptors_valid(S_pendingT)', '$heap_valid($heap_graph(S_pendingT))',
    ]
    seek(checks, 'S_enteredT', 'S_pendingT', 6)
    checks += [
        'S_enteredT.CURRENT = (pcallcontext_t)',
        'pcallcontext_t.TARGET = METHOD_TARGET n_right_object porigin_method_right',
        'pcallcontext_t.RECEIVER = (n_right_object)', 'pcallcontext_t.CALLSITE = (porigin_right)',
        'S_enteredT.FRAMES = pframe_t :: pframe_t_tail*',
        'pframe_t.TODO = (STRINGIFY_RESULT n_right_object porigin_right 25) :: (CONCAT_OWNED_RIGHT pconcatleft pvalue_left (n_right_object)) :: ptask_tail*',
        '$heap_count(HOBJECT n_object, $tasks_nodes(pframe_t.TODO)) = 1',
        '$heap_count(HOBJECT n_right_object, $tasks_nodes(pframe_t.TODO)) = 2',
        'S_enteredT.STORE[n_adrops] = DEFINED (PINT 0)',
        'S_enteredT.STORE[n_bdrops] = DEFINED (PINT 0)',
        'S_enteredT.STORE[n_rightcalls] = DEFINED (PINT 0)',
        '$stringify_chain_valid(S_enteredT, S_enteredT.CURRENT, S_enteredT.FRAMES)',
        '$call_descriptors_valid(S_enteredT)', '$heap_valid($heap_graph(S_enteredT))',
    ]
    seek(checks, 'S_returnT', 'S_enteredT', 7)
    checks += [
        'S_returnT.TODO = (STRINGIFY_RESULT n_right_object porigin_right 25) :: (CONCAT_OWNED_RIGHT pconcatleft pvalue_left (n_right_object)) :: ptask_tail*',
        'S_returnT.RESULT = KNOWN pvalue_right', '$string_bytes(pvalue_right) = ($ptascii("R"))',
        'S_returnT.STORE[n_leftcalls] = DEFINED (PINT 1)',
        'S_returnT.STORE[n_rightcalls] = DEFINED (PINT 1)',
        'S_returnT.STORE[n_adrops] = DEFINED (PINT 0)', 'S_returnT.STORE[n_bdrops] = DEFINED (PINT 0)',
        '$heap_owners($heap_prune($heap_graph(S_returnT)), HOBJECT n_object) = 1',
        '$heap_owners($heap_prune($heap_graph(S_returnT)), HOBJECT n_right_object) = 2',
        '$integer_outputs(S_returnT.EVENTS) = ($ptascii("P;Q;S;T;"))',
        '$call_descriptors_valid(S_returnT)', '$heap_valid($heap_graph(S_returnT))',
    ]
    seek(checks, 'S_right', 'S_returnT', 8)
    checks += [
        'S_right.TODO = (CONCAT_OWNED_RIGHT pconcatleft pvalue_left (n_right_object)) :: ptask_tail*',
        'S_right.RESULT = KNOWN pvalue_right',
        '$heap_owners($heap_prune($heap_graph(S_right)), HOBJECT n_object) = 1',
        '$heap_owners($heap_prune($heap_graph(S_right)), HOBJECT n_right_object) = 1',
        '$call_descriptors_valid(S_right)', '$heap_valid($heap_graph(S_right))',
    ]
    seek(checks, 'S_release', 'S_right', 9)
    checks += [
        'S_release.ORIGIN = (porigin_parent)',
        'S_release.TODO = (CONCAT_OWNED_RELEASE pconcatleft) :: ptask_tail*',
        'S_release.RESULT = KNOWN pvalue_concat', '$string_bytes(pvalue_concat) = ($ptascii("LR"))',
        'S_release.BASE = BASE_VALUE (KNOWN pvalue_concat)',
        'S_release.STORE[n_v] = DEFINED (PINT 100)',
        'S_release.STORE[n_adrops] = DEFINED (PINT 0)', 'S_release.STORE[n_bdrops] = DEFINED (PINT 0)',
        '$heap_owners($heap_prune($heap_graph(S_release)), HOBJECT n_object) = 1',
        '$heap_owners($heap_prune($heap_graph(S_release)), HOBJECT n_right_object) = 1',
        'PhpStep: S_release ~> S_raw_dropA',
        'S_raw_dropA = S_release[.TODO = (CONCAT_OWNED_RIGHT_RELEASE pconcatleft) :: ptask_tail*]',
        '$task_nodes(CONCAT_OWNED_RIGHT_RELEASE pconcatleft) = [HOBJECT n_right_object]',
        '$heap_count(HOBJECT n_object, $tasks_nodes(S_raw_dropA.TODO)) = 0',
        '$heap_count(HOBJECT n_right_object, $tasks_nodes(S_raw_dropA.TODO)) = 1',
        '$call_descriptors_valid(S_release)', '$heap_valid($heap_graph(S_release))',
    ]
    seek(checks, 'S_dtorA', 'S_release', 12)
    checks += [
        'S_dtorA.CURRENT = (pcallcontext_da)',
        '$destructor_context_call(pcallcontext_da, S_dtorA.CURRENT, S_dtorA.FRAMES) = (pdestructorcall_a)',
        'pdestructorcall_a.OBJECT = n_object', 'pdestructorcall_a.OPERATION = (pdestructionoperation_a)',
        'pdestructionoperation_a.SOURCE = CONCAT_OWNED_RELEASE pconcatleft',
        'pdestructionoperation_a.PENDING = eps', 'pdestructionoperation_a.VALUE = KNOWN pvalue_concat',
        'S_dtorA.FRAMES = pframe_da :: pframe_da_tail*',
        '$heap_count(HOBJECT n_right_object, $tasks_nodes(pframe_da.TODO)) = 1',
        'S_dtorA.STORE[n_v] = DEFINED (PINT 100)',
        'S_dtorA.STORE[n_rightcalls] = DEFINED (PINT 1)',
        'S_dtorA.STORE[n_adrops] = DEFINED (PINT 0)', 'S_dtorA.STORE[n_bdrops] = DEFINED (PINT 0)',
        '$integer_outputs(S_dtorA.EVENTS) = ($ptascii("P;Q;S;T;"))',
        '$destructor_call_live(S_dtorA, pdestructorcall_a)',
        '$call_descriptors_valid(S_dtorA)', '$heap_valid($heap_graph(S_dtorA))',
    ]
    seek(checks, 'S_hold', 'S_dtorA', 10)
    checks += [
        'S_hold.TODO = (CONCAT_OWNED_RIGHT_RELEASE pconcatleft) :: ptask_tail*',
        'S_hold.RESULT = KNOWN pvalue_concat', 'S_hold.STORE[n_v] = DEFINED (PINT 100)',
        'S_hold.STORE[n_adrops] = DEFINED (PINT 1)', 'S_hold.STORE[n_bdrops] = DEFINED (PINT 0)',
        '~((HOBJECT n_object) <- S_hold.ALLOCATIONS)', '(HOBJECT n_right_object) <- S_hold.ALLOCATIONS',
        '$heap_owners($heap_prune($heap_graph(S_hold)), HOBJECT n_object) = 0',
        '$heap_owners($heap_prune($heap_graph(S_hold)), HOBJECT n_right_object) = 1',
        '$concat_owned_source(S_hold, pconcatleft)', '~$concat_owned_live(S_hold, pconcatleft)',
        '$concat_owned_right_release_valid(S_hold, pconcatleft)',
        '~$concat_owned_right_release_valid(S_hold, pconcatleft[.RIGHT = KNOWN (POBJECT n_object)])',
        '~$concat_owned_right_release_valid(S_hold[.ORIGIN = (porigin_method_left)], pconcatleft)',
        '~$concat_owned_right_release_valid(S_hold, pconcatleft[.LINE = 24])',
        '$integer_outputs(S_hold.EVENTS) = ($ptascii("P;Q;S;T;A:1:1:1:1;"))',
        'PhpStep: S_hold ~> S_raw_dropB',
        'S_raw_dropB = S_hold[.TODO = (CONCAT_OWNED_DONE pconcatleft) :: ptask_tail*]',
        '$task_nodes(CONCAT_OWNED_DONE pconcatleft) = eps',
        '$heap_count(HOBJECT n_right_object, $tasks_nodes(S_raw_dropB.TODO)) = 0',
        '$call_descriptors_valid(S_hold)', '$heap_valid($heap_graph(S_hold))',
    ]
    seek(checks, 'S_dtorB', 'S_hold', 13)
    checks += [
        'S_dtorB.CURRENT = (pcallcontext_db)',
        '$destructor_context_call(pcallcontext_db, S_dtorB.CURRENT, S_dtorB.FRAMES) = (pdestructorcall_b)',
        'pdestructorcall_b.OBJECT = n_right_object', 'pdestructorcall_b.OPERATION = (pdestructionoperation_b)',
        'pdestructionoperation_b.SOURCE = CONCAT_OWNED_RIGHT_RELEASE pconcatleft',
        'pdestructionoperation_b.PENDING = eps', 'pdestructionoperation_b.VALUE = KNOWN pvalue_concat',
        'S_dtorB.STORE[n_v] = DEFINED (PINT 100)',
        'S_dtorB.STORE[n_adrops] = DEFINED (PINT 1)', 'S_dtorB.STORE[n_bdrops] = DEFINED (PINT 0)',
        '$destructor_call_live(S_dtorB, pdestructorcall_b)',
        '$call_descriptors_valid(S_dtorB)', '$heap_valid($heap_graph(S_dtorB))',
    ]
    seek(checks, 'S_released', 'S_dtorB', 11)
    checks += [
        'S_released.RESULT = KNOWN pvalue_concat', 'S_released.STORE[n_v] = DEFINED (PINT 100)',
        'S_released.STORE[n_adrops] = DEFINED (PINT 1)', 'S_released.STORE[n_bdrops] = DEFINED (PINT 1)',
        '~((HOBJECT n_object) <- S_released.ALLOCATIONS)', '~((HOBJECT n_right_object) <- S_released.ALLOCATIONS)',
        '$heap_owners($heap_prune($heap_graph(S_released)), HOBJECT n_object) = 0',
        '$heap_owners($heap_prune($heap_graph(S_released)), HOBJECT n_right_object) = 0',
        '$concat_owned_source(S_released, pconcatleft)',
        '~$concat_owned_right_release_valid(S_released, pconcatleft)',
        '$call_descriptors_valid(S_released)', '$heap_valid($heap_graph(S_released))',
        'S_done = $drive_steps(S_released, 3000)', 'S_done.COMPLETION = NORMAL',
        'S_done.TODO = eps', 'S_done.EXITSTATUS = 0', 'S_done.CURRENT = eps', 'S_done.FRAMES = eps',
        'S_done.HELD = eps', 'S_done.DESTRUCTION.OPERATIONS = eps',
        'S_done.STORE[n_v] = DEFINED pvalue_final', '$string_bytes(pvalue_final) = ($ptascii("LR"))',
        'S_done.STORE[n_leftcalls] = DEFINED (PINT 8)', 'S_done.STORE[n_rightcalls] = DEFINED (PINT 9)',
        'S_done.STORE[n_adrops] = DEFINED (PINT 1)', 'S_done.STORE[n_bdrops] = DEFINED (PINT 1)',
        '$heap_owners($heap_prune($heap_graph(S_done)), HOBJECT n_object) = 0',
        '$heap_owners($heap_prune($heap_graph(S_done)), HOBJECT n_right_object) = 0',
        '~((HOBJECT n_object) <- S_done.ALLOCATIONS)', '~((HOBJECT n_right_object) <- S_done.ALLOCATIONS)',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$concat_dual_output_only(S_done.EVENTS)',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_release, 3000) = S_done',
        '$drive_steps(S_entry, 0) = S_entry[.COMPLETION = BUDGET]',
    ]
    return checks
