#!/usr/bin/env python3
"""Real Generator storage pins preserve RETURN destructor throw and recovery."""
import argparse
import json
import os
import sys
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import config_generator_return_storage_review_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64
PREFIX = r"""
dec $test_config_storage_peer_cfg_task(ptask) : bool
def $test_config_storage_peer_cfg_task(CONFIG_GENERATOR pconfiggenerator text) = true
def $test_config_storage_peer_cfg_task(ptask) = false -- otherwise
dec $test_config_storage_peer_marker(ptask*) : bool
def $test_config_storage_peer_marker(eps) = false
def $test_config_storage_peer_marker((CONFIG_GENERATOR pconfiggenerator text) :: ptask*) = true
def $test_config_storage_peer_marker(ptask :: ptask_tail*) = $test_config_storage_peer_marker(ptask_tail*)
  -- if ~$test_config_storage_peer_cfg_task(ptask)
dec $test_config_storage_peer_front(pstate, nat) : bool
def $test_config_storage_peer_front(S, 0) = true
  -- if S.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_config_storage_peer_front(S, 1) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "finish") :: ptask*
def $test_config_storage_peer_front(S, 2) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "input-release") :: ptask*
  -- if S.DESTRUCTION.OPERATIONS = eps
  -- if $heap_owners($heap_graph(S),HOBJECT pconfiggenerator.OBJECT) = 1
def $test_config_storage_peer_front(S, 3) = true
  -- if S.TODO = (GENERATOR_STORAGE_STEP pgenstorage) :: ptask*
  -- if pgenstorage.NEXT = 0
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $test_config_storage_peer_front(S, 4) = true
  -- if S.TODO = (THROW_VALUE porigin z) :: ptask*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin_method
  -- if $trace_context_function(S,pcallcontext) = $ptascii("__destruct")
def $test_config_storage_peer_front(S, 5) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_GENERATOR pconfiggenerator text) :: ptask*
  -- if ~((HOBJECT pconfiggenerator.OBJECT) <- S.ALLOCATIONS)
  -- if S.CURRENT = eps /\ S.FRAMES = eps /\ S.DESTRUCTION.OPERATIONS = eps
def $test_config_storage_peer_front(S, 6) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask*
  -- if ~$test_config_storage_peer_marker(S.TODO)
  -- if S.CURRENT = eps /\ S.FRAMES = eps /\ S.DESTRUCTION.OPERATIONS = eps
def $test_config_storage_peer_front(S, 7) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_option),NAMED_SENT (KNOWN pvalue_value)]
  -- if $string_bytes(pvalue_option) = ($ptascii("precision"))
  -- if $string_bytes(pvalue_value) = ($ptascii("9"))
def $test_config_storage_peer_front(S, n) = false -- otherwise
dec $test_config_storage_peer_seek(pstate, nat, nat) : pstate
def $test_config_storage_peer_seek(S, n_stage, 0) = S
def $test_config_storage_peer_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_config_storage_peer_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ (S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
def $test_config_storage_peer_seek(S, n_stage, n) = $test_config_storage_peer_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_config_storage_peer_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~(S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
dec $test_config_storage_peer_step(pstate) : pstate
def $test_config_storage_peer_step(S) = S_next
  -- PhpStep: S ~> S_next
dec $test_config_storage_peer_recovery_done(pstate, ptask*, porigin?) : bool
def $test_config_storage_peer_recovery_done(S, ptask*, porigin?) = (S.TODO = ptask* /\ S.ORIGIN = porigin? /\ S.CURRENT = eps /\ S.FRAMES = eps /\ S.DESTRUCTION.OPERATIONS = eps)
dec $test_config_storage_peer_recovery_seek(pstate, ptask*, porigin?, nat) : pstate
def $test_config_storage_peer_recovery_seek(S, ptask*, porigin?, 0) = S
def $test_config_storage_peer_recovery_seek(S, ptask*, porigin?, n) = S
  -- if $(n > 0)
  -- if $test_config_storage_peer_recovery_done(S,ptask*,porigin?) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ (S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
def $test_config_storage_peer_recovery_seek(S, ptask*, porigin?, n) = $test_config_storage_peer_recovery_seek($drive_steps($test_running(S),1),ptask*,porigin?,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_config_storage_peer_recovery_done(S,ptask*,porigin?)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~(S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
"""


def reach(state, start, stage):
    return [state + '_found = $test_config_storage_peer_seek(' + start + ',' + str(stage) + ',4000)',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_config_storage_peer_front(' + state + ',' + str(stage) + ')']


def owners(state, generator, callee):
    return ['$heap_owners($heap_graph(' + state + '),HOBJECT ' + node + ') = ' + str(count)
        for node, count in [('n_generator', generator), ('n_owner', callee)]]


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)',
        state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)',
        state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def checks(program, path, name):
    assert name == 'temporary-generator-return-dtor-throw-precedes-config-api'
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *reach('S_pre', 'S_initial', 0),
        'S_pre.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*',
        'pconfigcall.OWNER = (n_owner)',
        '$intrinsic_argument(S_pre,pconfigcall.SITE,0) = ((expression,true,eps,porigin_argument,z_argument))',
        'pconfigcall.LINE = 31', 'z_argument = 32',
        'S_pre.RESULT = KNOWN (POBJECT n_generator)',
        'S_pre.OBJECTS[n_generator] = GENERATOR pgenerator_initial',
        'pgenerator_initial.PHASE = GENERATOR_FRESH',
        '$function_at($all_functions(S_pre),pgenerator_initial.FUNCTION) = (pfunction_body)',
        'pfunction_body.NAME = ' + text('configGeneratorStorageBodyReview96')]
    for variable, cell in [('watchGenerator', 'n_watch_generator_cell'),
            ('watchReturn', 'n_watch_return_cell'), ('keep', 'n_keep_cell'),
            ('saved', 'n_saved_cell'), ('result', 'n_result_cell'),
            ('effects', 'n_effects_cell')]:
        values += ['$lookup(S_pre.ENV,' + text(variable) + ') = (' + cell + ')']
    values += ['S_pre.STORE[n_watch_generator_cell] = DEFINED (POBJECT n_watch_generator)',
        'S_pre.OBJECTS[n_watch_generator] = WEAKREFERENCE (n_generator)',
        '$node_children(S_pre,HOBJECT n_watch_generator) = eps',
        'S_pre.STORE[n_watch_return_cell] = DEFINED PNULL',
        'S_pre.STORE[n_saved_cell] = DEFINED PNULL',
        '$test_outputs(S_pre.EVENTS) = ' + text('B|P|'),
        '$config_generator_start(S_pre,pconfigcall,S_pre.RESULT,n_generator)',
        *owners('S_pre', 1, 3), *common.public('S_pre'),
        'pconfiggenerator_initial = {CALL pconfigcall,OBJECT n_generator,INPUT S_pre.RESULT,ITEMS eps,PRODUCER eps}',
        'S_data = $test_config_storage_peer_step(S_pre)',
        'S_data = S_pre[.ORIGIN = (porigin_argument)][.TODO = (CONFIG_GENERATOR pconfiggenerator_initial "rewind") :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$task_nodes(CONFIG_GENERATOR pconfiggenerator_initial "rewind") = [HOBJECT n_generator,HOBJECT n_generator,HOBJECT n_owner]',
        *owners('S_data', 2, 3), *common.public('S_data'),
        *reach('S_finish', 'S_data', 1),
        'S_finish.TODO = (CONFIG_GENERATOR pconfiggenerator "finish") :: ptask_tail*',
        'pconfiggenerator.ITEMS = [ENTRY (KINT 3) (DIRECT pvalue_option),ENTRY (KINT 3) (DIRECT pvalue_value)]',
        'pconfiggenerator = pconfiggenerator_initial[.ITEMS = pconfiggenerator.ITEMS]',
        '$string_bytes(pvalue_option) = (' + text('precision') + ')',
        '$string_bytes(pvalue_value) = (' + text('8') + ')',
        'S_finish.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
        'pgenerator_closed.PHASE = GENERATOR_CLOSED', 'pgenerator_closed.FRAME = eps',
        'pgenerator_closed.RETURN = (POBJECT n_payload)',
        '$node_children(S_finish,HOBJECT n_generator) = [HOBJECT n_payload]',
        '$ref_return_retire_method(S_finish,n_payload) = (pmethoddesc)',
        '$objectprops_at(S_finish.OBJECTPROPS,n_payload) = (eps)',
        '$node_children(S_finish,HOBJECT n_payload) = eps',
        'S_finish.STORE[n_watch_return_cell] = DEFINED (POBJECT n_watch_return)',
        'S_finish.OBJECTS[n_watch_return] = WEAKREFERENCE (n_payload)',
        '$node_children(S_finish,HOBJECT n_watch_return) = eps',
        'S_finish.STORE[n_effects_cell] = DEFINED (PINT 3)',
        'S_finish.STORE[n_result_cell] = DEFINED (PINT 99)',
        '$test_outputs(S_finish.EVENTS) = ' + text('B|P|Y0|Y1|F|'),
        *owners('S_finish', 2, 3), *common.public('S_finish'),
        'S_raw_data_release = $test_config_storage_peer_step(S_finish)',
        'S_raw_data_release = $config_generator_finish(S_finish,pconfiggenerator,ptask_tail*)',
        *reach('S_input', 'S_finish', 2),
        'S_input.TODO = (CONFIG_GENERATOR pconfiggenerator "input-release") :: ptask_tail*',
        '$config_generator_valid(S_input,pconfiggenerator,"input-release")',
        '$task_nodes(CONFIG_GENERATOR pconfiggenerator "input-release") = [HOBJECT n_generator,HOBJECT n_owner]',
        'S_input.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
        '$weakref_get(S_input,n_watch_generator) = POBJECT n_generator',
        '$weakref_get(S_input,n_watch_return) = POBJECT n_payload',
        '~$config_generator_quiet_closed(S_input,pconfiggenerator)',
        '$config_generator_return_storage(S_input,pconfiggenerator)',
        '$config_generator_finish_allowed(S_input,pconfiggenerator)',
        'S_input.STORE[n_saved_cell] = DEFINED PNULL',
        *owners('S_input', 1, 3), *common.public('S_input'),
        'S_raw_input_release = $test_config_storage_peer_step(S_input)',
        'S_raw_input_release = $config_generator_release_input(S_input,pconfiggenerator,ptask_tail*)',
        *reach('S_pinned', 'S_input', 3),
        'S_pinned.TODO = (GENERATOR_STORAGE_STEP pgenstorage) :: ptask_storage_tail*',
        'pgenstorage.OBJECT = n_generator', 'pgenstorage.NEXT = 0', 'pgenstorage.USER',
        'pgenstorage.ORIGIN = (porigin_argument)',
        'S_pinned.DESTRUCTION.OPERATIONS = [pdestructionoperation]',
        'pdestructionoperation.SOURCE = CONFIG_GENERATOR pconfiggenerator "storage-released"',
        'pdestructionoperation.PENDING = eps',
        'pdestructionoperation.ORIGIN = (porigin_argument)',
        '$eager_operation_source_valid(S_pinned,pdestructionoperation)',
        '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = eps',
        '$generator_storage_valid(S_pinned,pgenstorage)',
        '$generator_storage_state_valid(S_pinned)',
        '$task_nodes(GENERATOR_STORAGE_STEP pgenstorage) = [HOBJECT n_generator]',
        '$node_children(S_pinned,HOBJECT n_generator) = [HOBJECT n_payload]',
        '$weakref_get(S_pinned,n_watch_generator) = POBJECT n_generator',
        '$weakref_get(S_pinned,n_watch_return) = POBJECT n_payload',
        *owners('S_pinned', 1, 3), *common.public('S_pinned'),
        *reach('S_throw', 'S_pinned', 4),
        'S_throw.CURRENT = (pcallcontext_dtor)',
        'pcallcontext_dtor.TARGET = METHOD_TARGET n_payload pmethoddesc.FUNCTION.ORIGIN',
        '$destructor_context_valid(S_throw,pcallcontext_dtor)',
        'S_throw.DESTRUCTION.CALLS = pdestructorcall :: pdestructorcall_tail*',
        'pdestructorcall.OPERATION = (pdestructionoperation)',
        'pdestructorcall.PENDING = eps',
        '$generator_storage_for(S_throw,n_generator) = (pgenstorage[.NEXT = 4])',
        '$task_nodes(GENERATOR_STORAGE_STEP pgenstorage[.NEXT = 4]) = [HOBJECT n_generator]',
        'S_throw.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
        '$node_children(S_throw,HOBJECT n_generator) = eps',
        '$weakref_get(S_throw,n_watch_generator) = POBJECT n_generator',
        '$weakref_get(S_throw,n_watch_return) = POBJECT n_payload',
        'S_throw.STORE[n_saved_cell] = DEFINED (POBJECT n_exception)',
        '$throwable_field(S_throw,n_exception,"line") = PINT 9',
        '$throwable_field(S_throw,n_exception,"trace") = PARRAY n_trace',
        'S_throw.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_trace_frame))]',
        '$trace_array_field(S_throw,n_trace_frame,' + text('function') + ') = PSTRING ' + text('__destruct'),
        '$trace_array_field(S_throw,n_trace_frame,' + text('class') + ') = PSTRING ' + text('ConfigGeneratorStorageThrowReview96'),
        '$trace_array_field(S_throw,n_trace_frame,' + text('type') + ') = PSTRING ' + text('->'),
        '$trace_array_field(S_throw,n_trace_frame,' + text('line') + ') = PINT z_argument',
        '$trace_array_field(S_throw,n_trace_frame,' + text('args') + ') = PARRAY n_trace_args',
        'S_throw.ARRAYS[n_trace_args].ITEMS = eps',
        '$node_children(S_throw,HARRAY n_trace_frame) = [HARRAY n_trace_args]',
        'S_throw.STORE[n_effects_cell] = DEFINED (PINT 4)',
        'S_throw.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_throw.PRECISIONINI = ' + text('6'),
        '$test_outputs(S_throw.EVENTS) = ' + text('B|P|Y0|Y1|F|D|G|V|'),
        *owners('S_throw', 1, 2), *common.public('S_throw'),
        *reach('S_retired', 'S_throw', 5),
        'S_retired.TODO = (THROW_SEARCH n_exception) :: (CONFIG_GENERATOR pconfiggenerator text_retired) :: ptask_tail*',
        'text_retired = "storage-released"',
        'S_retired.ORIGIN = (porigin_argument)',
        '$config_generator_valid(S_retired,pconfiggenerator,text_retired)',
        '~((HOBJECT n_payload) <- S_retired.ALLOCATIONS)',
        '$weakref_get(S_retired,n_watch_generator) = PNULL',
        '$weakref_get(S_retired,n_watch_return) = PNULL',
        '$config_generator_history(S_retired,pconfiggenerator)',
        '$config_generator_return_history(S_retired,pconfiggenerator)',
        '$config_generator_retired_scope(S_retired,pconfiggenerator)',
        '~$config_generator_scope(S_retired,pconfiggenerator)',
        '~$config_generator_valid(S_retired[.ORIGIN = (pconfigcall.SITE)],pconfiggenerator,text_retired)',
        'S_retired.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
        '$task_nodes(CONFIG_GENERATOR pconfiggenerator text_retired) = [HOBJECT n_owner]',
        '$throwable_field(S_retired,n_exception,"trace") = PARRAY n_trace',
        '$throwable_field(S_retired,n_exception,"previous") = PNULL',
        'S_retired.ARRAYS[n_trace] = S_throw.ARRAYS[n_trace]',
        'S_retired.ARRAYS[n_trace_frame] = S_throw.ARRAYS[n_trace_frame]',
        'S_retired.ARRAYS[n_trace_args] = S_throw.ARRAYS[n_trace_args]',
        'S_retired.STORE[n_saved_cell] = DEFINED (POBJECT n_exception)',
        'S_retired.STORE[n_result_cell] = DEFINED (PINT 99)',
        *owners('S_retired', 0, 2), *common.public('S_retired'),
        'S_last_callee = S_retired[.STORE[n_keep_cell] = DEFINED PNULL]',
        '$heap_owners($heap_graph(S_last_callee),HOBJECT n_owner) = 1',
        'S_callee_stopped = $test_config_storage_peer_step(S_last_callee)',
        'S_callee_stopped = S_last_callee[.COMPLETION = UNSUPPORTED "CONFIG Generator unpack last cleanup owner"]',
        '$drive_steps(S_callee_stopped,3) = S_callee_stopped',
        'S_raw_discard = $test_config_storage_peer_step(S_retired)',
        'S_raw_discard = $config_generator_discard(S_retired[.TODO = (THROW_SEARCH n_exception) :: ptask_tail*],pconfiggenerator,text_retired)',
        *reach('S_disposed', 'S_retired', 6),
        'S_disposed.TODO = (THROW_SEARCH n_exception) :: ptask_tail*',
        '$throwable_live(S_disposed,n_exception)',
        '$weakref_get(S_disposed,n_watch_generator) = PNULL',
        '$weakref_get(S_disposed,n_watch_return) = PNULL',
        'S_disposed.STORE[n_result_cell] = DEFINED (PINT 99)',
        '$test_outputs(S_disposed.EVENTS) = ' + text('B|P|Y0|Y1|F|D|G|V|'),
        *owners('S_disposed', 0, 1), *common.public('S_disposed'),
        *budget('S_pinned'),
        *reach('S_recovery', 'S_disposed', 7),
        'S_recovery.TODO = (CONFIG_INVOKE pconfigcall_recovery) :: ptask_recovery*',
        'pconfigcall_recovery.OWNER = (n_owner)',
        '$lookup(S_recovery.ENV,' + text('e') + ') = (n_caught_cell)',
        'S_recovery.STORE[n_caught_cell] = DEFINED (POBJECT n_exception)',
        'S_recovery.STORE[n_saved_cell] = DEFINED (POBJECT n_exception)',
        'S_recovery.STORE[n_result_cell] = DEFINED (PINT 99)',
        '$weakref_get(S_recovery,n_watch_generator) = PNULL',
        '$weakref_get(S_recovery,n_watch_return) = PNULL',
        'S_recovery.PRECISIONINI = ' + text('6'),
        *owners('S_recovery', 0, 2), *common.public('S_recovery'),
        'S_raw_recovery = $test_config_storage_peer_step(S_recovery)',
        'S_raw_recovery.TODO = ptask_recovery*',
        'S_raw_recovery.ORIGIN = S_recovery.ORIGIN',
        'S_raw_recovery.RESULT = KNOWN pvalue_old',
        *common.step('S_after_api', 'S_recovery'),
        'S_after_api.DESTRUCTION.OPERATIONS = [pdestructionoperation_recovery]',
        'pdestructionoperation_recovery.SOURCE = CONFIG_INVOKE pconfigcall_recovery',
        'pdestructionoperation_recovery.VALUE = KNOWN pvalue_old',
        'S_recovered_found = $test_config_storage_peer_recovery_seek(S_after_api,ptask_recovery*,S_recovery.ORIGIN,80)',
        r'S_recovered_found.COMPLETION = NORMAL \/ S_recovered_found.COMPLETION = BUDGET',
        'S_recovered = S_recovered_found[.COMPLETION = NORMAL]',
        '$test_config_storage_peer_recovery_done(S_recovered,ptask_recovery*,S_recovery.ORIGIN)',
        'S_recovered.TODO = ptask_recovery*',
        'S_recovered.ORIGIN = S_recovery.ORIGIN',
        'S_recovered.RESULT = KNOWN pvalue_old',
        '$string_bytes(pvalue_old) = (' + text('6') + ')',
        'S_recovered.PRECISIONINI = ' + text('9'),
        *owners('S_recovered', 0, 1), *common.public('S_recovered'),
        'S_final = $drive_steps(S_recovered,4000)', 'S_final.COMPLETION = NORMAL',
        'S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        '$weakref_get(S_final,n_watch_generator) = PNULL',
        '$weakref_get(S_final,n_watch_return) = PNULL',
        '$test_outputs(S_final.EVENTS) = ' + text('B|P|Y0|Y1|F|D|G|V|I|99|4|6|__destruct|ConfigGeneratorStorageThrowReview96|->|32|A|N|gD|vD|L|6|R|6|9|99'),
        *common.public('S_final')]
    return values


def partition(values, part):
    cut = values.index('$heap_valid($heap_graph(S_pinned))') + 1
    if part == 'entry':
        return values[:cut]
    # Recompute the physical pin from the same source, without serialized state.
    setup = [values[0], values[1], *reach('S_pre', 'S_initial', 0),
        'S_pre.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*',
        'pconfigcall.OWNER = (n_owner)',
        '$intrinsic_argument(S_pre,pconfigcall.SITE,0) = ((expression,true,eps,porigin_argument,z_argument))',
        'S_pre.RESULT = KNOWN (POBJECT n_generator)']
    for variable, cell in [('watchGenerator', 'n_watch_generator_cell'),
            ('watchReturn', 'n_watch_return_cell'), ('keep', 'n_keep_cell'),
            ('saved', 'n_saved_cell'), ('result', 'n_result_cell'),
            ('effects', 'n_effects_cell')]:
        setup += ['$lookup(S_pre.ENV,' + text(variable) + ') = (' + cell + ')']
    setup += ['S_pre.STORE[n_watch_generator_cell] = DEFINED (POBJECT n_watch_generator)',
        *reach('S_input', 'S_pre', 2),
        'S_input.TODO = (CONFIG_GENERATOR pconfiggenerator "input-release") :: ptask_tail*',
        'S_input.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
        'pgenerator_closed.RETURN = (POBJECT n_payload)',
        '$ref_return_retire_method(S_input,n_payload) = (pmethoddesc)',
        'S_input.STORE[n_watch_return_cell] = DEFINED (POBJECT n_watch_return)',
        *reach('S_pinned', 'S_input', 3),
        'S_pinned.TODO = (GENERATOR_STORAGE_STEP pgenstorage) :: ptask_storage_tail*',
        'S_pinned.DESTRUCTION.OPERATIONS = [pdestructionoperation]']
    return setup + values[cut:]


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['prepare', 'check'], required=True)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--part', choices=['entry', 'completion', 'all'], default='all')
    args = parser.parse_args()
    driver.sources, driver.PREFIX = sources, PREFIX
    for part in (['entry', 'completion'] if args.part == 'all' else [args.part]):
        driver.checks = lambda program, path, name: partition(checks(program, path, name), part)
        sys.argv = [sys.argv[0], '--phase', args.phase, '--sources', str(args.sources),
            '--output', str(args.output / part)]
        driver.main()


if __name__ == '__main__':
    main()
