#!/usr/bin/env python3
"""Acquired and borrowed LEFT roots through real conversion and destruction."""
import base64
import json

import concat_left_stringable_lifetime_cases as cases
import integer_operator_warning_protocol as shared

CASES = tuple(cases.CASES)
HELPERS = shared.HELPERS + r'''
dec $concat_owned_frontier(pstate, nat) : bool
def $concat_owned_frontier(S, 0) = ($concat_owned_plan(S) =/= eps)
def $concat_owned_frontier(S, 1) = true
  -- if S.TODO = (CALL_ARGS (METHOD_TARGET n_object porigin_method) eps 0 eps (porigin_left) z) :: (STRINGIFY_RESULT n_object porigin_left z) :: (CONCAT_OWNED_LEFT pconcatleft) :: ptask_tail*
  -- if n_object = pconcatleft.OBJECT
def $concat_owned_frontier(S, 2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n_object porigin_method
  -- if pcallcontext.RECEIVER = (n_object)
  -- if pcallcontext.CALLSITE = (porigin_left)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (STRINGIFY_RESULT n_object porigin_left z) :: (CONCAT_OWNED_LEFT pconcatleft) :: ptask_tail*
  -- if n_object = pconcatleft.OBJECT
def $concat_owned_frontier(S, 3) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (STRINGIFY_RESULT n_object porigin_left z) :: ptask_tail*
  -- if S.RESULT = KNOWN pvalue
  -- if $string_bytes(pvalue) = ($ptascii("L"))
def $concat_owned_frontier(S, 4) = true
  -- if S.TODO = (CONCAT_OWNED_LEFT pconcatleft) :: ptask_tail*
  -- if S.RESULT = KNOWN pvalue
  -- if $string_bytes(pvalue) = ($ptascii("L"))
def $concat_owned_frontier(S, 5) = true
  -- if S.TODO = (CONCAT_OWNED_RIGHT pconcatleft pvalue_left eps) :: ptask_tail*
  -- if S.RESULT = KNOWN pvalue
  -- if $string_bytes(pvalue) = ($ptascii("fresh"))
def $concat_owned_frontier(S, 6) = true
  -- if S.TODO = (CONCAT_OWNED_RELEASE pconcatleft) :: ptask_tail*
def $concat_owned_frontier(S, 7) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (CONCAT_OWNED_DONE pconcatleft) :: ptask_tail*
def $concat_owned_frontier(S, 8) = true
  -- if S.TODO = (CALL_ARGS (METHOD_TARGET n_right porigin_method) eps 0 eps (porigin_right) z) :: (STRINGIFY_RESULT n_right porigin_right z) :: (CONCAT_OWNED_RIGHT pconcatleft pvalue_left (n_right)) :: ptask_tail*
def $concat_owned_frontier(S, 9) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n_right porigin_method
  -- if pcallcontext.RECEIVER = (n_right)
  -- if pcallcontext.CALLSITE = (porigin_right)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (STRINGIFY_RESULT n_right porigin_right z) :: (CONCAT_OWNED_RIGHT pconcatleft pvalue_left (n_right)) :: ptask_tail*
def $concat_owned_frontier(S, 10) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
  -- if pdestructionoperation.SOURCE = CONCAT_OWNED_RELEASE pconcatleft
  -- if pdestructionoperation.PENDING = eps
def $concat_owned_frontier(S, 11) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("f")
def $concat_owned_frontier(S, 12) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (CONCAT_LEFT expression_right false false 25) :: ptask_tail*
  -- if S.RESULT = KNOWN (POBJECT n)
def $concat_owned_frontier(S, 13) = true
  -- if S.TODO = (CONCAT_PREP (VARIABLE ptbytes_left z_left) (VARIABLE ptbytes_right z_right) false false 25) :: ptask_tail*
def $concat_owned_frontier(S, 14) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
  -- if pdestructionoperation.SOURCE = STRINGIFY_RESULT n_object porigin_left z
  -- if pdestructionoperation.PENDING = eps
def $concat_owned_frontier(S, 15) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (CONCAT_AFTER_LEFT porigin_parent poperand_right false 25) :: ptask_tail*
  -- if $lookup(S.ENV, $ptascii("drops")) = (n)
  -- if S.STORE[n] = DEFINED (PINT 1)
def $concat_owned_frontier(S, 16) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n_object porigin_method
  -- if pcallcontext.RECEIVER = (n_object)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (STRINGIFY_RESULT n_object porigin_left 25) :: (CONCAT_AFTER_LEFT porigin_parent poperand_right false 25) :: ptask_tail*
def $concat_owned_frontier(S, n) = false -- otherwise
dec $concat_owned_seek(pstate, nat, nat) : pstate
def $concat_owned_seek(S, n_stage, n) = S -- if $concat_owned_frontier(S, n_stage)
def $concat_owned_seek(S, n_stage, n) = S
  -- if ~$concat_owned_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $concat_owned_seek(S, n_stage, n) = S
  -- if ~$concat_owned_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $concat_owned_seek(S, n_stage, n) = $concat_owned_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$concat_owned_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
'''


def seek(checks, label, start, stage):
    checks += [
        f'{label}_found = $concat_owned_seek({start}, {stage}, 3000)',
        f'{label}_found.COMPLETION = NORMAL \\/ {label}_found.COMPLETION = BUDGET',
        f'{label} = {label}_found[.COMPLETION = NORMAL]',
        f'$concat_owned_frontier({label}, {stage})',
    ]


def prefix(program, path):
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]
    seek(checks, 'S_factory', 'S_initial', 11)
    checks += ['S_factory.CURRENT = (pcallcontext_factory)', 'pcallcontext_factory.CALLSITE = (porigin_left)',
               '$call_descriptors_valid(S_factory)', '$heap_valid($heap_graph(S_factory))']
    seek(checks, 'S_factory_return', 'S_factory', 12)
    checks += ['S_factory_return.RESULT = KNOWN (POBJECT n_object)',
               '$stringable_instance(S_factory_return, n_object)',
               '$heap_owners($heap_prune($heap_graph(S_factory_return)), HOBJECT n_object) = 1',
               '$integer_outputs(S_factory_return.EVENTS) = ($ptascii("P;"))',
               '$call_descriptors_valid(S_factory_return)', '$heap_valid($heap_graph(S_factory_return))']
    seek(checks, 'S_entry', 'S_factory_return', 0)
    checks += [
        '$concat_owned_plan(S_entry) = (pconcatleft)',
        'S_entry.TODO = (CONCAT_PREP (KNOWN (POBJECT n_object)) poperand_right false false 25) :: ptask_tail*',
        'S_entry.ORIGIN = (porigin_parent)', 'pconcatleft.SITE = porigin_parent',
        'pconcatleft.LINE = 25', 'pconcatleft.OBJECT = n_object',
        'pconcatleft.RIGHT = poperand_right', 'pconcatleft.RIGHTCONST = false',
        'poperand_right = VARIABLE ($ptascii("right")) 25',
        '$origin_child((porigin_parent), [PCFIELD 0]) = (porigin_left)',
        '$origin_child((porigin_parent), [PCFIELD 1]) = (porigin_right)',
        '$lookup(S_entry.ENV, $ptascii("right")) = (n_right_cell)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        '$lookup(S_entry.ENV, $ptascii("leftcalls")) = (n_leftcalls)',
        '$lookup(S_entry.ENV, $ptascii("rightcalls")) = (n_rightcalls)',
        '$lookup(S_entry.ENV, $ptascii("drops")) = (n_drops)',
        'S_entry.STORE[n_right_cell] = DEFINED pvalue_initial_right',
        '$string_bytes(pvalue_initial_right) = ($ptascii("old"))',
        'S_entry.STORE[n_v] = DEFINED (PINT 100)',
        'S_entry.STORE[n_leftcalls] = DEFINED (PINT 0)',
        'S_entry.STORE[n_rightcalls] = DEFINED (PINT 0)',
        'S_entry.STORE[n_drops] = DEFINED (PINT 0)',
        '$concat_owned_source(S_entry, pconcatleft)', '$concat_owned_ready(S_entry, poperand_right)',
        '$heap_count(HOBJECT n_object, $tasks_nodes(S_entry.TODO)) = 1',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HOBJECT n_object) = 1',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
    ]
    seek(checks, 'S_pendingS', 'S_entry', 1)
    checks += [
        'S_pendingS.TODO = (CALL_ARGS (METHOD_TARGET n_object porigin_method_left) eps 0 eps (porigin_left) 25) :: (STRINGIFY_RESULT n_object porigin_left 25) :: (CONCAT_OWNED_LEFT pconcatleft) :: ptask_tail*',
        '$task_nodes(CONCAT_OWNED_LEFT pconcatleft) = [HOBJECT n_object]',
        '$heap_count(HOBJECT n_object, $tasks_nodes(S_pendingS.TODO)) = 3',
        '$call_descriptors_valid(S_pendingS)', '$heap_valid($heap_graph(S_pendingS))',
    ]
    seek(checks, 'S_enteredS', 'S_pendingS', 2)
    checks += [
        'S_enteredS.CURRENT = (pcallcontext_s)',
        'pcallcontext_s.TARGET = METHOD_TARGET n_object porigin_method_left',
        'pcallcontext_s.RECEIVER = (n_object)', 'pcallcontext_s.CALLSITE = (porigin_left)',
        'S_enteredS.FRAMES = pframe_s :: pframe_s_tail*',
        'pframe_s.TODO = (STRINGIFY_RESULT n_object porigin_left 25) :: (CONCAT_OWNED_LEFT pconcatleft) :: ptask_tail*',
        'S_enteredS.STORE[n_v] = DEFINED (PINT 100)',
        'S_enteredS.STORE[n_leftcalls] = DEFINED (PINT 0)',
        'S_enteredS.STORE[n_rightcalls] = DEFINED (PINT 0)',
        'S_enteredS.STORE[n_drops] = DEFINED (PINT 0)',
        '$stringify_chain_valid(S_enteredS, S_enteredS.CURRENT, S_enteredS.FRAMES)',
        '$call_descriptors_valid(S_enteredS)', '$heap_valid($heap_graph(S_enteredS))',
    ]
    return checks


def returned_left(checks):
    seek(checks, 'S_returnS', 'S_enteredS', 3)
    checks += [
        'S_returnS.TODO = (STRINGIFY_RESULT n_object porigin_left 25) :: (CONCAT_OWNED_LEFT pconcatleft) :: ptask_tail*',
        'S_returnS.RESULT = KNOWN pvalue_left', '$string_bytes(pvalue_left) = ($ptascii("L"))',
        'S_returnS.STORE[n_leftcalls] = DEFINED (PINT 1)',
        'S_returnS.STORE[n_rightcalls] = DEFINED (PINT 0)',
        'S_returnS.STORE[n_drops] = DEFINED (PINT 0)',
        '$heap_count(HOBJECT n_object, $tasks_nodes(S_returnS.TODO)) = 2',
        '$heap_owners($heap_prune($heap_graph(S_returnS)), HOBJECT n_object) = 2',
        '$call_descriptors_valid(S_returnS)', '$heap_valid($heap_graph(S_returnS))',
    ]
    seek(checks, 'S_left', 'S_returnS', 4)
    checks += [
        'S_left.TODO = (CONCAT_OWNED_LEFT pconcatleft) :: ptask_tail*',
        'S_left.RESULT = KNOWN pvalue_left',
        'S_left.STORE[n_v] = DEFINED (PINT 100)', 'S_left.STORE[n_drops] = DEFINED (PINT 0)',
        '$heap_owners($heap_prune($heap_graph(S_left)), HOBJECT n_object) = 1',
        '$heap_count(HOBJECT n_object, $tasks_nodes(S_left.TODO)) = 1',
        '$concat_owned_source(S_left, pconcatleft)',
        '$call_descriptors_valid(S_left)', '$heap_valid($heap_graph(S_left))',
    ]


def finish(checks, start, wanted, stdout):
    checks += [
        f'S_done = $drive_steps({start}, 3000)', 'S_done.COMPLETION = NORMAL',
        'S_done.EXITSTATUS = 0', 'S_done.TODO = eps', 'S_done.CURRENT = eps',
        'S_done.FRAMES = eps', 'S_done.HELD = eps', 'S_done.DESTRUCTION.OPERATIONS = eps',
        'S_done.STORE[n_v] = DEFINED pvalue_final',
        '$string_bytes(pvalue_final) = ($ptascii("' + wanted + '"))',
        '$lookup(S_done.ENV, $ptascii("left")) = (n_left_end)',
        'S_done.STORE[n_left_end] = DEFINED (PINT 8)',
        'S_done.STORE[n_right_cell] = DEFINED (PINT 9)',
        'S_done.STORE[n_leftcalls] = DEFINED (PINT 1)',
        'S_done.STORE[n_rightcalls] = DEFINED (PINT 0)',
        'S_done.STORE[n_drops] = DEFINED (PINT 1)',
        '$heap_owners($heap_prune($heap_graph(S_done)), HOBJECT n_object) = 0',
        '~((HOBJECT n_object) <- S_done.ALLOCATIONS)',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_entry, 0) = S_entry[.COMPLETION = BUDGET]',
    ]


def acquired(program, path, stdout):
    checks = prefix(program, path)
    returned_left(checks)
    checks += [
        'S_left.STORE[n_right_cell] = DEFINED pvalue_fresh',
        '$string_bytes(pvalue_fresh) = ($ptascii("fresh"))',
        '$integer_outputs(S_left.EVENTS) = ($ptascii("P;S;"))',
        '~$concat_owned_source(S_entry, pconcatleft[.SITE = porigin_left])',
        '~$concat_owned_source(S_entry, pconcatleft[.LINE = 24])',
        '$concat_owned_ready(S_entry, KNOWN PNULL)',
        '~$concat_owned_ready(S_entry, KNOWN PUNDEFINED)',
        'S_missing_entry = $prune_allocations($global_unset(S_entry, $ptascii("right")))',
        '$concat_owned_plan(S_missing_entry) = (pconcatleft)',
        '~$concat_owned_ready(S_missing_entry, pconcatleft.RIGHT)',
        '$heap_valid($heap_graph(S_missing_entry))',
        'S_missing_boundary = S_missing_entry[.COMPLETION = UNSUPPORTED "concatenation acquired left unavailable right operand"]',
        'PhpStep: S_missing_entry ~> S_missing_boundary',
        'S_ref_entry = $global_acquire_name(S_entry, $ptascii("right"))',
        '$concat_owned_plan(S_ref_entry) = (pconcatleft)',
        '~$concat_owned_ready(S_ref_entry, pconcatleft.RIGHT)',
        '$heap_valid($heap_graph(S_ref_entry))',
        'S_ref_boundary = S_ref_entry[.COMPLETION = UNSUPPORTED "concatenation acquired left unavailable right operand"]',
        'PhpStep: S_ref_entry ~> S_ref_boundary',
        'S_pair = S_entry[.TODO = (CONCAT_PREP (KNOWN (POBJECT n_object)) (KNOWN (POBJECT n_object)) false false 25) :: ptask_tail*]',
        '$concat_owned_plan(S_pair) = eps',
        '$heap_owners($heap_prune($heap_graph(S_pair)), HOBJECT n_object) = 2',
        '$heap_valid($heap_graph(S_pair))',
        'S_pair_left = $resolve_at(S_pair, KNOWN (POBJECT n_object), 25)',
        'S_pair_legacy = $user_string_begin(S_pair_left[.ORIGIN = (porigin_left)], n_object, porigin_left, 25, CONCAT_AFTER_LEFT porigin_parent (KNOWN (POBJECT n_object)) false 25, ptask_tail*)',
        'PhpStep: S_pair ~> S_pair_legacy',
        'S_pair_legacy.TODO = (CALL_ARGS (METHOD_TARGET n_object porigin_method_left) eps 0 eps (porigin_left) 25) :: (STRINGIFY_RESULT n_object porigin_left 25) :: (CONCAT_AFTER_LEFT porigin_parent (KNOWN (POBJECT n_object)) false 25) :: ptask_tail*',
        'S_missing_live = $prune_allocations($global_unset(S_left, $ptascii("right")))',
        '$concat_owned_live(S_missing_live, pconcatleft)',
        '$call_descriptors_valid(S_missing_live)',
        '$heap_valid($heap_graph(S_missing_live))',
        '~$concat_owned_ready(S_missing_live, pconcatleft.RIGHT)',
        'S_live_boundary = S_missing_live[.COMPLETION = UNSUPPORTED "concatenation acquired left unavailable right operand"]',
        'PhpStep: S_missing_live ~> S_live_boundary',
        'S_ref_live = $global_acquire_name(S_left, $ptascii("right"))',
        '$concat_owned_live(S_ref_live, pconcatleft)',
        '$call_descriptors_valid(S_ref_live)', '$heap_valid($heap_graph(S_ref_live))',
        '~$concat_owned_ready(S_ref_live, pconcatleft.RIGHT)',
        'S_ref_live_boundary = S_ref_live[.COMPLETION = UNSUPPORTED "concatenation acquired left unavailable right operand"]',
        'PhpStep: S_ref_live ~> S_ref_live_boundary',
        'S_no_tmp = S_returnS[.TODO = (STRINGIFY_RESULT n_object porigin_left 25) :: ptask_tail*]',
        '$heap_owners($heap_prune($heap_graph(S_no_tmp)), HOBJECT n_object) = 1',
        '$heap_valid($heap_graph(S_no_tmp))', '~$call_descriptors_valid(S_no_tmp)',
    ]
    seek(checks, 'S_right', 'S_left', 5)
    checks += [
        'S_right.TODO = (CONCAT_OWNED_RIGHT pconcatleft pvalue_left eps) :: ptask_tail*',
        'S_right.RESULT = KNOWN pvalue_fresh',
        'S_right.STORE[n_v] = DEFINED (PINT 100)', 'S_right.STORE[n_drops] = DEFINED (PINT 0)',
        '$heap_owners($heap_prune($heap_graph(S_right)), HOBJECT n_object) = 1',
        '$call_descriptors_valid(S_right)', '$heap_valid($heap_graph(S_right))',
    ]
    seek(checks, 'S_release', 'S_right', 6)
    checks += [
        'S_release.ORIGIN = (porigin_parent)',
        'S_release.TODO = (CONCAT_OWNED_RELEASE pconcatleft) :: ptask_tail*',
        'S_release.RESULT = KNOWN pvalue_concat',
        '$string_bytes(pvalue_concat) = ($ptascii("Lfresh"))',
        'S_release.BASE = BASE_VALUE (KNOWN pvalue_concat)',
        'S_release.STORE[n_v] = DEFINED (PINT 100)',
        'S_release.STORE[n_drops] = DEFINED (PINT 0)',
        '$heap_owners($heap_prune($heap_graph(S_release)), HOBJECT n_object) = 1',
        '$call_descriptors_valid(S_release)', '$heap_valid($heap_graph(S_release))',
    ]
    seek(checks, 'S_dtor', 'S_release', 10)
    checks += [
        'S_dtor.CURRENT = (pcallcontext_d)',
        '$destructor_context_call(pcallcontext_d, S_dtor.CURRENT, S_dtor.FRAMES) = (pdestructorcall)',
        'pdestructorcall.OBJECT = n_object', 'pdestructorcall.OPERATION = (pdestructionoperation)',
        'pdestructionoperation.SOURCE = CONCAT_OWNED_RELEASE pconcatleft',
        'pdestructionoperation.PENDING = eps', 'pdestructionoperation.VALUE = KNOWN pvalue_concat',
        'S_dtor.STORE[n_v] = DEFINED (PINT 100)',
        'S_dtor.STORE[n_leftcalls] = DEFINED (PINT 1)',
        'S_dtor.STORE[n_rightcalls] = DEFINED (PINT 0)',
        'S_dtor.STORE[n_drops] = DEFINED (PINT 0)',
        'S_dtor.STORE[n_right_cell] = DEFINED pvalue_fresh',
        '$integer_outputs(S_dtor.EVENTS) = ($ptascii("P;S;"))',
        '$destructor_call_live(S_dtor, pdestructorcall)',
        '$call_descriptors_valid(S_dtor)', '$heap_valid($heap_graph(S_dtor))',
    ]
    seek(checks, 'S_released', 'S_dtor', 7)
    checks += [
        'S_released.RESULT = KNOWN pvalue_concat',
        'S_released.STORE[n_v] = DEFINED (PINT 100)',
        'S_released.STORE[n_drops] = DEFINED (PINT 1)',
        'S_released.STORE[n_right_cell] = DEFINED pvalue_retired',
        '$string_bytes(pvalue_retired) = ($ptascii("retired"))',
        '$task_nodes(CONCAT_OWNED_DONE pconcatleft) = eps',
        '~((HOBJECT n_object) <- S_released.ALLOCATIONS)',
        '$heap_owners($heap_prune($heap_graph(S_released)), HOBJECT n_object) = 0',
        '$concat_owned_source(S_released, pconcatleft)',
        '~$concat_owned_live(S_released, pconcatleft)',
        '$call_descriptors_valid(S_released)', '$heap_valid($heap_graph(S_released))',
    ]
    finish(checks, 'S_released', 'Lfresh', stdout)
    checks += ['$drive_steps(S_left, 3000) = S_done']
    return checks


def borrowed(program, path, stdout):
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]
    seek(checks, 'S_entry', 'S_initial', 13)
    checks += [
        'S_entry.TODO = (CONCAT_PREP (VARIABLE ($ptascii("left")) 24) poperand_right false false 25) :: ptask_tail*',
        'poperand_right = VARIABLE ($ptascii("right")) 25',
        'S_entry.ORIGIN = (porigin_parent)',
        '$origin_child((porigin_parent), [PCFIELD 0]) = (porigin_left)',
        '$lookup(S_entry.ENV, $ptascii("left")) = (n_left_cell)',
        'S_entry.STORE[n_left_cell] = DEFINED (POBJECT n_object)',
        '$lookup(S_entry.ENV, $ptascii("right")) = (n_right_cell)',
        '$lookup(S_entry.ENV, $ptascii("v")) = (n_v)',
        '$lookup(S_entry.ENV, $ptascii("leftcalls")) = (n_leftcalls)',
        '$lookup(S_entry.ENV, $ptascii("rightcalls")) = (n_rightcalls)',
        '$lookup(S_entry.ENV, $ptascii("drops")) = (n_drops)',
        '$concat_owned_plan(S_entry) = eps',
        '$heap_count(HOBJECT n_object, $tasks_nodes(S_entry.TODO)) = 0',
        '$heap_owners($heap_prune($heap_graph(S_entry)), HOBJECT n_object) = 1',
        '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))',
    ]
    seek(checks, 'S_enteredS', 'S_entry', 16)
    checks += [
        'S_enteredS.CURRENT = (pcallcontext_s)',
        'pcallcontext_s.TARGET = METHOD_TARGET n_object porigin_method_left',
        'pcallcontext_s.RECEIVER = (n_object)',
        'S_enteredS.FRAMES = pframe_s :: pframe_s_tail*',
        'pframe_s.TODO = (STRINGIFY_RESULT n_object porigin_left 25) :: (CONCAT_AFTER_LEFT porigin_parent poperand_right false 25) :: ptask_tail*',
        '$heap_count(HOBJECT n_object, $tasks_nodes(pframe_s.TODO)) = 1',
        '$stringify_chain_valid(S_enteredS, S_enteredS.CURRENT, S_enteredS.FRAMES)',
        '$call_descriptors_valid(S_enteredS)', '$heap_valid($heap_graph(S_enteredS))',
    ]
    seek(checks, 'S_returnS', 'S_enteredS', 3)
    checks += [
        'S_returnS.TODO = (STRINGIFY_RESULT n_object porigin_left 25) :: (CONCAT_AFTER_LEFT porigin_parent poperand_right false 25) :: ptask_tail*',
        'S_returnS.RESULT = KNOWN pvalue_left', '$string_bytes(pvalue_left) = ($ptascii("L"))',
        'S_returnS.STORE[n_leftcalls] = DEFINED (PINT 1)',
        'S_returnS.STORE[n_drops] = DEFINED (PINT 0)',
        '$lookup(S_returnS.ENV, $ptascii("left")) = eps',
        '$heap_count(HOBJECT n_object, $tasks_nodes(S_returnS.TODO)) = 1',
        '$heap_owners($heap_prune($heap_graph(S_returnS)), HOBJECT n_object) = 1',
        '$call_descriptors_valid(S_returnS)', '$heap_valid($heap_graph(S_returnS))',
    ]
    seek(checks, 'S_dtor', 'S_returnS', 14)
    checks += [
        'S_dtor.CURRENT = (pcallcontext_d)',
        '$destructor_context_call(pcallcontext_d, S_dtor.CURRENT, S_dtor.FRAMES) = (pdestructorcall)',
        'pdestructorcall.OBJECT = n_object', 'pdestructorcall.OPERATION = (pdestructionoperation)',
        'pdestructionoperation.SOURCE = STRINGIFY_RESULT n_object porigin_left 25',
        'pdestructionoperation.PENDING = eps', 'pdestructionoperation.VALUE = KNOWN pvalue_left',
        'S_dtor.STORE[n_v] = DEFINED (PINT 100)',
        'S_dtor.STORE[n_rightcalls] = DEFINED (PINT 0)',
        'S_dtor.STORE[n_drops] = DEFINED (PINT 0)',
        'S_dtor.STORE[n_right_cell] = DEFINED pvalue_fresh',
        '$string_bytes(pvalue_fresh) = ($ptascii("fresh"))',
        '$integer_outputs(S_dtor.EVENTS) = ($ptascii("S;"))',
        '$destructor_call_live(S_dtor, pdestructorcall)',
        '$call_descriptors_valid(S_dtor)', '$heap_valid($heap_graph(S_dtor))',
    ]
    seek(checks, 'S_after', 'S_dtor', 15)
    checks += [
        'S_after.TODO = (CONCAT_AFTER_LEFT porigin_parent poperand_right false 25) :: ptask_tail*',
        'S_after.RESULT = KNOWN pvalue_left',
        'S_after.STORE[n_v] = DEFINED (PINT 100)',
        'S_after.STORE[n_right_cell] = DEFINED pvalue_retired',
        '$string_bytes(pvalue_retired) = ($ptascii("retired"))',
        'S_after.STORE[n_drops] = DEFINED (PINT 1)',
        '~((HOBJECT n_object) <- S_after.ALLOCATIONS)',
        '$heap_owners($heap_prune($heap_graph(S_after)), HOBJECT n_object) = 0',
        '$integer_outputs(S_after.EVENTS) = ($ptascii("S;D:1:0;"))',
        '$call_descriptors_valid(S_after)', '$heap_valid($heap_graph(S_after))',
    ]
    finish(checks, 'S_after', 'Lretired', stdout)
    checks += ['$drive_steps(S_returnS, 3000) = S_done']
    return checks


def conditions(name, program, path, stdout):
    assert name in CASES
    checks = (acquired if name == 'concat-acquired-left-live-right' else borrowed)(program, path, stdout)
    assert len(checks) == len(set(checks))
    return checks
