#!/usr/bin/env python3
"""Pre-conversion undefined fetch retains A and restores a fixed fallback."""
import base64
import json

import concat_undefined_right_cases as cases
import integer_operator_warning_protocol as shared

CASES = tuple(cases.CASES)
HELPERS = shared.HELPERS + r'''
dec $concat_missing_frontier(pstate, nat) : bool
def $concat_missing_frontier(S, 0) = true
  -- if S.TODO = (CONCAT_PREP (KNOWN (POBJECT n)) (VARIABLE ptbytes z_input) false false z) :: ptask*
  -- if $error_read_plan(S) =/= eps
def $concat_missing_frontier(S, 1) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask*
  -- if perrorcall.RESUME = ERROR_READ_RESULT perrorread
  -- if perrorread.ORIGINAL = CONCAT_PREP (KNOWN (POBJECT n)) (VARIABLE ptbytes z_input) false false z
def $concat_missing_frontier(S, 2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("h")
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask*
  -- if perrorcall.RESUME = ERROR_READ_RESULT perrorread
  -- if perrorread.ORIGINAL = CONCAT_PREP (KNOWN (POBJECT n)) (VARIABLE ptbytes z_input) false false z
def $concat_missing_frontier(S, 3) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask*
  -- if perrorcall.RESUME = ERROR_READ_RESULT perrorread
  -- if S.RESULT = KNOWN (PBOOL false)
def $concat_missing_frontier(S, 4) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (ERROR_READ_RESULT perrorread) :: ptask*
  -- if perrorread.ORIGINAL = CONCAT_PREP (KNOWN (POBJECT n)) (VARIABLE ptbytes z_input) false false z
def $concat_missing_frontier(S, 5) = true
  -- if S.TODO = (CONCAT_PREP (KNOWN (POBJECT n)) (KNOWN PNULL) false false z) :: ptask*
def $concat_missing_frontier(S, 6) = true
  -- if S.TODO = (CALL_ARGS (METHOD_TARGET n porigin_method) eps 0 eps (porigin_left) z) :: (STRINGIFY_RESULT n porigin_left z) :: (CONCAT_OWNED_LEFT pconcatleft) :: ptask*
  -- if n = pconcatleft.OBJECT /\ pconcatleft.RIGHT = KNOWN PNULL
def $concat_missing_frontier(S, 7) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin_method
  -- if pcallcontext.RECEIVER = (n)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (STRINGIFY_RESULT n porigin_left z) :: (CONCAT_OWNED_LEFT pconcatleft) :: ptask*
  -- if n = pconcatleft.OBJECT /\ pconcatleft.RIGHT = KNOWN PNULL
def $concat_missing_frontier(S, 8) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (STRINGIFY_RESULT n porigin_left z) :: (CONCAT_OWNED_LEFT pconcatleft) :: ptask*
  -- if S.RESULT = KNOWN pvalue
  -- if $string_bytes(pvalue) = ($ptascii("L"))
def $concat_missing_frontier(S, 9) = true
  -- if S.TODO = (CONCAT_OWNED_LEFT pconcatleft) :: ptask*
  -- if S.RESULT = KNOWN pvalue
  -- if $string_bytes(pvalue) = ($ptascii("L"))
def $concat_missing_frontier(S, 10) = true
  -- if S.TODO = (CONCAT_OWNED_RIGHT pconcatleft pvalue_left eps) :: ptask*
  -- if S.RESULT = KNOWN pvalue
  -- if $string_bytes(pvalue) = (ptbytes)
  -- if ptbytes = eps
def $concat_missing_frontier(S, 11) = true
  -- if S.TODO = (CONCAT_OWNED_RELEASE pconcatleft) :: ptask*
def $concat_missing_frontier(S, 12) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
  -- if pdestructionoperation.SOURCE = CONCAT_OWNED_RELEASE pconcatleft
  -- if pdestructionoperation.PENDING = eps
def $concat_missing_frontier(S, 13) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (CONCAT_OWNED_DONE pconcatleft) :: ptask*
def $concat_missing_frontier(S, 14) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("f")
def $concat_missing_frontier(S, 15) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (CONCAT_LEFT expression false false 25) :: ptask*
  -- if S.RESULT = KNOWN (POBJECT n)
def $concat_missing_frontier(S, n) = false -- otherwise
dec $concat_missing_seek(pstate, nat, nat) : pstate
def $concat_missing_seek(S, n_stage, n) = S -- if $concat_missing_frontier(S, n_stage)
def $concat_missing_seek(S, n_stage, n) = S
  -- if ~$concat_missing_frontier(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $concat_missing_seek(S, n_stage, n) = S
  -- if ~$concat_missing_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO = eps \/ n = 0
def $concat_missing_seek(S, n_stage, n) = $concat_missing_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$concat_missing_frontier(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
  -- if $(n > 0)
dec $concat_missing_warnings(pevent*) : nat
dec $concat_missing_is_warning(pevent) : bool
def $concat_missing_is_warning(WARNING ptbytes z) = true
def $concat_missing_is_warning(WARNING_SOURCE n_unit ptbytes z) = true
def $concat_missing_is_warning(pevent) = false -- otherwise
def $concat_missing_warnings(eps) = 0
def $concat_missing_warnings((WARNING ptbytes z) :: pevent_tail*) = $(1 + $concat_missing_warnings(pevent_tail*))
def $concat_missing_warnings((WARNING_SOURCE n_unit ptbytes z) :: pevent_tail*) = $(1 + $concat_missing_warnings(pevent_tail*))
def $concat_missing_warnings(pevent :: pevent_tail*) = $concat_missing_warnings(pevent_tail*) -- if ~$concat_missing_is_warning(pevent)
'''


def seek(checks, label, start, stage):
    checks += [f'{label}_found = $concat_missing_seek({start}, {stage}, 3000)',
               f'{label}_found.COMPLETION = NORMAL \\/ {label}_found.COMPLETION = BUDGET',
               f'{label} = {label}_found[.COMPLETION = NORMAL]',
               f'$concat_missing_frontier({label}, {stage})']


def prefix(program, path):
    checks = ['S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
              'S_initial.COMPLETION = BUDGET']
    seek(checks, 'S_factory', 'S_initial', 14)
    checks += ['S_factory.CURRENT = (pcallcontext_f)', 'pcallcontext_f.CALLSITE = (porigin_left)',
               '$call_descriptors_valid(S_factory)', '$heap_valid($heap_graph(S_factory))']
    seek(checks, 'S_factory_return', 'S_factory', 15)
    checks += ['S_factory_return.RESULT = KNOWN (POBJECT n_object)',
               '$stringable_instance(S_factory_return, n_object)',
               '$heap_owners($heap_prune($heap_graph(S_factory_return)), HOBJECT n_object) = 1',
               '$integer_outputs(S_factory_return.EVENTS) = ($ptascii("P;"))',
               '$call_descriptors_valid(S_factory_return)', '$heap_valid($heap_graph(S_factory_return))']
    seek(checks, 'S_entry', 'S_factory_return', 0)
    checks += ['S_entry.TODO = (CONCAT_PREP (KNOWN (POBJECT n_object)) poperand_right false false 25) :: ptask_tail*',
               'poperand_right = VARIABLE ($ptascii("right")) 25',
               'S_entry.ORIGIN = (porigin_parent)',
               '$origin_child((porigin_parent), [PCFIELD 0]) = (porigin_left)',
               '$origin_child((porigin_parent), [PCFIELD 1]) = (porigin_right)',
               '$lookup(S_entry.ENV, $ptascii("right")) = eps',
               'S_entry.RESULT = KNOWN PNULL', 'S_entry.BASE = BASE_VALUE (KNOWN PNULL)',
               '$concat_undefined_missing(S_entry, poperand_right)',
               '$error_read_pending(S_entry)', '$error_read_plan(S_entry) = (perrorread)',
               'perrorread.ORIGINAL = CONCAT_PREP (KNOWN (POBJECT n_object)) poperand_right false false 25',
               'perrorread.INPUT = poperand_right', 'perrorread.NAME = $ptascii("right")', 'perrorread.LINE = 25',
               'perrorread.TASK = CONCAT_PREP (KNOWN (POBJECT n_object)) (KNOWN PNULL) false false 25',
               'perrorread.RESULT = KNOWN PNULL', 'perrorread.BASE = BASE_VALUE (KNOWN PNULL)',
               '$error_read_valid(S_entry, perrorread)',
               '$concat_owned_plan(S_entry) = (pconcatleft_original)',
               'pconcatleft_original = {SITE porigin_parent, LINE 25, OBJECT n_object, RIGHT poperand_right, RIGHTCONST false}',
               'pconcatleft_fixed = pconcatleft_original[.RIGHT = KNOWN PNULL]',
               '$task_nodes(ERROR_READ_RESULT perrorread) = [HOBJECT n_object]',
               '$heap_owners($heap_prune($heap_graph(S_entry)), HOBJECT n_object) = 1',
               '$call_descriptors_valid(S_entry)', '$heap_valid($heap_graph(S_entry))']
    for name in ('v', 'calls', 'casts', 'drops'):
        checks += [f'$lookup(S_entry.ENV, $ptascii("{name}")) = (n_{name})',
                   f'S_entry.STORE[n_{name}] = DEFINED (PINT {100 if name == "v" else 0})']
    seek(checks, 'S_dispatch', 'S_entry', 1)
    checks += ['S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_initial) :: ptask_tail*',
               'perrorcall_initial.SITE = porigin_parent', 'perrorcall_initial.LINE = 25',
               'perrorcall_initial.LEVEL = 2', 'perrorcall_initial.TARGET = eps',
               'perrorcall_initial.MESSAGE = $ptascii("Undefined variable $right")',
               'perrorcall_initial.EVENT = WARNING ($ptascii("right")) 25',
               'perrorcall_initial.RESUME = ERROR_READ_RESULT perrorread',
               '$heap_count(HOBJECT n_object, $tasks_nodes(S_dispatch.TODO)) = 1',
               '$concat_missing_warnings(S_dispatch.EVENTS) = 0',
               '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))']
    seek(checks, 'S_enteredH', 'S_dispatch', 2)
    checks += ['S_enteredH.CURRENT = (pcallcontext_h)',
               'pcallcontext_h.TARGET = porigin_h',
               'pcallcontext_h.RECEIVER = eps', 'pcallcontext_h.CALLSITE = (porigin_parent)',
               'S_enteredH.FRAMES = pframe_h :: pframe_h_tail*',
               'pframe_h.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*',
               'perrorcall = perrorcall_initial[.TARGET = (porigin_h)]',
               '$heap_count(HOBJECT n_object, $tasks_nodes(pframe_h.TODO)) = 1',
               '$heap_owners($heap_prune($heap_graph(S_enteredH)), HOBJECT n_object) = 1',
               'S_enteredH.STORE[n_calls] = DEFINED (PINT 0)',
               'S_enteredH.STORE[n_casts] = DEFINED (PINT 0)',
               'S_enteredH.STORE[n_drops] = DEFINED (PINT 0)', 'S_enteredH.STORE[n_v] = DEFINED (PINT 100)',
               '$concat_missing_warnings(S_enteredH.EVENTS) = 0',
               '$call_descriptors_valid(S_enteredH)', '$heap_valid($heap_graph(S_enteredH))']
    return checks


def returned_h(checks):
    seek(checks, 'S_returnH', 'S_enteredH', 3)
    checks += ['S_returnH.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*',
               'S_returnH.RESULT = KNOWN (PBOOL false)',
               'S_returnH.STORE[n_calls] = DEFINED (PINT 1)',
               'S_returnH.STORE[n_casts] = DEFINED (PINT 0)', 'S_returnH.STORE[n_drops] = DEFINED (PINT 0)',
               '$concat_missing_warnings(S_returnH.EVENTS) = 0',
               '$heap_owners($heap_prune($heap_graph(S_returnH)), HOBJECT n_object) = 1',
               '$call_descriptors_valid(S_returnH)', '$heap_valid($heap_graph(S_returnH))']
    seek(checks, 'S_ready', 'S_returnH', 4)
    checks += ['S_ready.TODO = (ERROR_READ_RESULT perrorread) :: ptask_tail*',
               '$lookup(S_ready.ENV, $ptascii("right")) = (n_right_cell)',
               'S_ready.STORE[n_right_cell] = DEFINED pvalue_handler',
               '$string_bytes(pvalue_handler) = ($ptascii("handler"))',
               'S_ready.STORE[n_calls] = DEFINED (PINT 1)',
               'S_ready.STORE[n_casts] = DEFINED (PINT 0)', 'S_ready.STORE[n_drops] = DEFINED (PINT 0)',
               '$concat_missing_warnings(S_ready.EVENTS) = 1',
               '$error_read_valid(S_ready, perrorread)',
               '~$concat_undefined_missing(S_ready, perrorread.INPUT)',
               '$heap_count(HOBJECT n_object, $tasks_nodes(S_ready.TODO)) = 1',
               '$call_descriptors_valid(S_ready)', '$heap_valid($heap_graph(S_ready))']
    seek(checks, 'S_fixed', 'S_ready', 5)
    checks += ['S_fixed.TODO = perrorread.TASK :: ptask_tail*',
               'S_fixed.TODO = (CONCAT_PREP (KNOWN (POBJECT n_object)) (KNOWN PNULL) false false 25) :: ptask_tail*',
               'S_fixed.RESULT = KNOWN PNULL', 'S_fixed.BASE = BASE_VALUE (KNOWN PNULL)',
               '$concat_owned_plan(S_fixed) = (pconcatleft_fixed)',
               '~$error_read_pending(S_fixed)', '$error_read_plan(S_fixed) = eps',
               '$heap_count(HOBJECT n_object, $tasks_nodes(S_fixed.TODO)) = 1',
               '$concat_missing_warnings(S_fixed.EVENTS) = 1',
               '$call_descriptors_valid(S_fixed)', '$heap_valid($heap_graph(S_fixed))']


def conditions(name, program, path, stdout):
    assert name in CASES
    checks = prefix(program, path)
    checks += [
        # These transformed records check authority without claiming native cases.
        '~$error_read_valid(S_entry, perrorread[.LINE = 24])',
        '~$error_read_valid(S_entry, perrorread[.INPUT = VARIABLE ($ptascii("right")) 24])',
        '~$error_read_valid(S_entry, perrorread[.TASK = perrorread.ORIGINAL])',
        '~$error_read_valid(S_entry, perrorread[.RESULT = KNOWN (PBOOL false)])',
        '~$error_read_valid(S_entry[.ORIGIN = (porigin_left)], perrorread)',
        '$task_nodes(ERROR_READ_RESULT perrorread[.TASK = perrorread.ORIGINAL]) = [HOBJECT n_object]',
        '$integer_outputs(S_dispatch.EVENTS) = ($ptascii("P;"))',
    ]
    returned_h(checks)
    checks += [
        '$integer_outputs(S_ready.EVENTS) = ($ptascii("P;H:2:25:Undefined variable $right;"))',
        '$error_read_plan(S_ready) = eps',
        'S_resume = $error_read_resume(S_ready, perrorread, ptask_tail*)',
        'S_resume = S_fixed',
        'PhpStep: S_ready ~> S_fixed',
        'S_defined_entry = S_ready[.TODO = perrorread.ORIGINAL :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$concat_owned_plan(S_defined_entry) = (pconcatleft_original)',
        '$concat_owned_ready(S_defined_entry, perrorread.INPUT)',
        '$concat_owned_source(S_defined_entry, pconcatleft_original)',
        '$error_read_valid(S_defined_entry, perrorread)',
        '$error_read_plan(S_defined_entry) = eps',
        '$heap_valid($heap_graph(S_defined_entry))',
        # Defining/wrapping the original CV cannot change the saved fallback.
        'S_ref_ready = $global_acquire_name(S_ready, $ptascii("right"))',
        'n_right_cell <- S_ref_ready.REFCELLS',
        '$error_read_valid(S_ref_ready, perrorread)',
        '~$concat_undefined_missing(S_ref_ready, perrorread.INPUT)',
        '$heap_owners($heap_prune($heap_graph(S_ref_ready)), HOBJECT n_object) = 1',
        '$call_descriptors_valid(S_ref_ready)', '$heap_valid($heap_graph(S_ref_ready))',
        'S_ref_fixed = $error_read_resume(S_ref_ready, perrorread, ptask_tail*)',
        'S_ref_fixed.TODO = perrorread.TASK :: ptask_tail*',
        'S_ref_fixed.RESULT = KNOWN PNULL',
        'S_ref_fixed.STORE[n_right_cell] = DEFINED pvalue_handler',
        'PhpStep: S_ref_ready ~> S_ref_fixed',
    ]
    seek(checks, 'S_pendingS', 'S_fixed', 6)
    checks += [
        'S_pendingS.TODO = (CALL_ARGS (METHOD_TARGET n_object porigin_method) eps 0 eps (porigin_left) 25) :: (STRINGIFY_RESULT n_object porigin_left 25) :: (CONCAT_OWNED_LEFT pconcatleft_fixed) :: ptask_tail*',
        '$task_nodes(CONCAT_OWNED_LEFT pconcatleft_fixed) = [HOBJECT n_object]',
        '$task_nodes(STRINGIFY_RESULT n_object porigin_left 25) = [HOBJECT n_object]',
        '$heap_count(HOBJECT n_object, $tasks_nodes(S_pendingS.TODO)) = 3',
        '$stringify_consumer_receiver_valid(S_pendingS, n_object, CONCAT_OWNED_LEFT pconcatleft_fixed)',
        '$stringify_source(S_pendingS, porigin_left, 25, CONCAT_OWNED_LEFT pconcatleft_fixed)',
        '$concat_missing_warnings(S_pendingS.EVENTS) = 1',
        'S_pendingS.STORE[n_v] = DEFINED (PINT 100)',
        'S_pendingS.STORE[n_casts] = DEFINED (PINT 0)',
        'S_pendingS.STORE[n_drops] = DEFINED (PINT 0)',
        '$call_descriptors_valid(S_pendingS)', '$heap_valid($heap_graph(S_pendingS))',
    ]
    seek(checks, 'S_enteredS', 'S_pendingS', 7)
    checks += [
        'S_enteredS.CURRENT = (pcallcontext_s)',
        'pcallcontext_s.TARGET = METHOD_TARGET n_object porigin_method',
        'pcallcontext_s.RECEIVER = (n_object)', 'pcallcontext_s.CALLSITE = (porigin_left)',
        'S_enteredS.FRAMES = pframe_s :: pframe_s_tail*',
        'pframe_s.TODO = (STRINGIFY_RESULT n_object porigin_left 25) :: (CONCAT_OWNED_LEFT pconcatleft_fixed) :: ptask_tail*',
        '$heap_count(HOBJECT n_object, $tasks_nodes(pframe_s.TODO)) = 2',
        '$stringify_chain_valid(S_enteredS, S_enteredS.CURRENT, S_enteredS.FRAMES)',
        'S_enteredS.STORE[n_calls] = DEFINED (PINT 1)',
        'S_enteredS.STORE[n_casts] = DEFINED (PINT 0)',
        'S_enteredS.STORE[n_drops] = DEFINED (PINT 0)',
        'S_enteredS.STORE[n_v] = DEFINED (PINT 100)',
        'S_enteredS.STORE[n_right_cell] = DEFINED pvalue_handler',
        '$concat_missing_warnings(S_enteredS.EVENTS) = 1',
        '$call_descriptors_valid(S_enteredS)', '$heap_valid($heap_graph(S_enteredS))',
    ]
    seek(checks, 'S_returnS', 'S_enteredS', 8)
    checks += [
        'S_returnS.TODO = (STRINGIFY_RESULT n_object porigin_left 25) :: (CONCAT_OWNED_LEFT pconcatleft_fixed) :: ptask_tail*',
        'S_returnS.RESULT = KNOWN pvalue_left',
        '$string_bytes(pvalue_left) = ($ptascii("L"))',
        'S_returnS.STORE[n_right_cell] = DEFINED pvalue_method',
        '$string_bytes(pvalue_method) = ($ptascii("method"))',
        'S_returnS.STORE[n_casts] = DEFINED (PINT 1)',
        'S_returnS.STORE[n_drops] = DEFINED (PINT 0)',
        '$heap_count(HOBJECT n_object, $tasks_nodes(S_returnS.TODO)) = 2',
        '$heap_owners($heap_prune($heap_graph(S_returnS)), HOBJECT n_object) = 2',
        '$concat_missing_warnings(S_returnS.EVENTS) = 1',
        '$call_descriptors_valid(S_returnS)', '$heap_valid($heap_graph(S_returnS))',
    ]
    seek(checks, 'S_left', 'S_returnS', 9)
    checks += [
        'S_left.TODO = (CONCAT_OWNED_LEFT pconcatleft_fixed) :: ptask_tail*',
        'S_left.RESULT = KNOWN pvalue_left',
        'S_left.STORE[n_v] = DEFINED (PINT 100)', 'S_left.STORE[n_drops] = DEFINED (PINT 0)',
        '$heap_owners($heap_prune($heap_graph(S_left)), HOBJECT n_object) = 1',
        '$concat_owned_live(S_left, pconcatleft_fixed)',
        '$concat_owned_read_ready(S_left, pconcatleft_fixed.RIGHT)',
        '$call_descriptors_valid(S_left)', '$heap_valid($heap_graph(S_left))',
    ]
    seek(checks, 'S_right', 'S_left', 10)
    checks += [
        'S_right.TODO = (CONCAT_OWNED_RIGHT pconcatleft_fixed pvalue_left eps) :: ptask_tail*',
        'S_right.RESULT = KNOWN pvalue_empty', '$string_bytes(pvalue_empty) = (eps)',
        'S_right.STORE[n_right_cell] = DEFINED pvalue_method',
        'S_right.STORE[n_v] = DEFINED (PINT 100)', 'S_right.STORE[n_drops] = DEFINED (PINT 0)',
        '$heap_owners($heap_prune($heap_graph(S_right)), HOBJECT n_object) = 1',
        '$concat_missing_warnings(S_right.EVENTS) = 1',
        '$call_descriptors_valid(S_right)', '$heap_valid($heap_graph(S_right))',
    ]
    seek(checks, 'S_release', 'S_right', 11)
    checks += [
        'S_release.TODO = (CONCAT_OWNED_RELEASE pconcatleft_fixed) :: ptask_tail*',
        'S_release.RESULT = KNOWN pvalue_concat', '$string_bytes(pvalue_concat) = ($ptascii("L"))',
        'S_release.BASE = BASE_VALUE (KNOWN pvalue_concat)',
        'S_release.ORIGIN = (porigin_parent)',
        'S_release.STORE[n_v] = DEFINED (PINT 100)', 'S_release.STORE[n_drops] = DEFINED (PINT 0)',
        '$heap_owners($heap_prune($heap_graph(S_release)), HOBJECT n_object) = 1',
        '$call_descriptors_valid(S_release)', '$heap_valid($heap_graph(S_release))',
        # Raw root loss is inspected; only the real eager path is then driven.
        'S_raw = S_release[.TODO = (CONCAT_OWNED_DONE pconcatleft_fixed) :: ptask_tail*]',
        'PhpStep: S_release ~> S_raw',
        '$task_nodes(CONCAT_OWNED_DONE pconcatleft_fixed) = eps',
        '$heap_owners($heap_prune($heap_graph(S_raw)), HOBJECT n_object) = 0',
        'S_raw.RESULT = KNOWN pvalue_concat', 'S_raw.EVENTS = S_release.EVENTS',
    ]
    seek(checks, 'S_dtor', 'S_release', 12)
    checks += [
        'S_dtor.CURRENT = (pcallcontext_d)',
        '$destructor_context_call(pcallcontext_d, S_dtor.CURRENT, S_dtor.FRAMES) = (pdestructorcall)',
        'pdestructorcall.OBJECT = n_object', 'pdestructorcall.OPERATION = (pdestructionoperation)',
        'pdestructionoperation.SOURCE = CONCAT_OWNED_RELEASE pconcatleft_fixed',
        'pdestructionoperation.PENDING = eps', 'pdestructionoperation.VALUE = KNOWN pvalue_concat',
        'S_dtor.STORE[n_v] = DEFINED (PINT 100)', 'S_dtor.STORE[n_calls] = DEFINED (PINT 1)',
        'S_dtor.STORE[n_casts] = DEFINED (PINT 1)', 'S_dtor.STORE[n_drops] = DEFINED (PINT 0)',
        'S_dtor.STORE[n_right_cell] = DEFINED pvalue_method',
        '$integer_outputs(S_dtor.EVENTS) = ($ptascii("P;H:2:25:Undefined variable $right;S;"))',
        '$concat_missing_warnings(S_dtor.EVENTS) = 1',
        '$destructor_call_live(S_dtor, pdestructorcall)',
        '$call_descriptors_valid(S_dtor)', '$heap_valid($heap_graph(S_dtor))',
    ]
    seek(checks, 'S_released', 'S_dtor', 13)
    checks += [
        'S_released.TODO = (CONCAT_OWNED_DONE pconcatleft_fixed) :: ptask_tail*',
        'S_released.RESULT = KNOWN pvalue_concat', 'S_released.STORE[n_v] = DEFINED (PINT 100)',
        'S_released.STORE[n_drops] = DEFINED (PINT 1)',
        'S_released.STORE[n_right_cell] = DEFINED pvalue_method',
        '~((HOBJECT n_object) <- S_released.ALLOCATIONS)',
        '$heap_owners($heap_prune($heap_graph(S_released)), HOBJECT n_object) = 0',
        '$error_read_valid(S_released, perrorread)',
        '$call_descriptors_valid(S_released)', '$heap_valid($heap_graph(S_released))',
        'S_done = $drive_steps(S_released, 3000)', 'S_done.COMPLETION = NORMAL',
        'S_done.EXITSTATUS = 0', 'S_done.TODO = eps', 'S_done.FRAMES = eps',
        'S_done.CURRENT = eps', 'S_done.HELD = eps', 'S_done.DESTRUCTION.OPERATIONS = eps',
        'S_done.STORE[n_v] = DEFINED pvalue_final', '$string_bytes(pvalue_final) = ($ptascii("L"))',
        'S_done.STORE[n_right_cell] = DEFINED (PINT 8)',
        'S_done.STORE[n_calls] = DEFINED (PINT 1)',
        'S_done.STORE[n_casts] = DEFINED (PINT 1)', 'S_done.STORE[n_drops] = DEFINED (PINT 1)',
        '~((HOBJECT n_object) <- S_done.ALLOCATIONS)',
        '$heap_owners($heap_prune($heap_graph(S_done)), HOBJECT n_object) = 0',
        '$concat_missing_warnings(S_done.EVENTS) = 1',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_release, 3000) = S_done',
        '$drive_steps(S_entry, 0) = S_entry[.COMPLETION = BUDGET]',
        '$drive_steps(S_fixed, 0) = S_fixed[.COMPLETION = BUDGET]',
        '$drive_steps(S_dtor, 0) = S_dtor[.COMPLETION = BUDGET]',
    ]
    assert len(checks) == len(set(checks))
    return checks
