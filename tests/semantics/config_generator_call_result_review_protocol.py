#!/usr/bin/env python3
"""A factory result keeps INPUT distinct from DATA through supplied throw cleanup."""
import argparse
import json
import os
import sys
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import config_generator_call_result_review_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64
PREFIX = r"""
dec $test_config_result_peer_front(pstate, nat) : bool
def $test_config_result_peer_front(S, 0) = true
  -- if S.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_config_result_peer_front(S, 1) = true
  -- if S.TODO = (THROW_VALUE porigin z) :: ptask_body*
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (GENERATOR_RESUME pgeneratorop) :: (CONFIG_GENERATOR pconfiggenerator "next") :: ptask_caller*
def $test_config_result_peer_front(S, 2) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_GENERATOR pconfiggenerator "next") :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $test_config_result_peer_front(S, 3) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_GENERATOR pconfiggenerator "input-release") :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.DESTRUCTION.OPERATIONS = eps
  -- if $heap_owners($heap_graph(S),HOBJECT pconfiggenerator.OBJECT) = 1
def $test_config_result_peer_front(S, 4) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask*
  -- if ~$test_config_result_peer_front(S,2)
  -- if ~$test_config_result_peer_front(S,3)
  -- if S.DESTRUCTION.OPERATIONS = eps
def $test_config_result_peer_front(S, 5) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_option),NAMED_SENT (KNOWN pvalue_value)]
  -- if $string_bytes(pvalue_option) = ($ptascii("precision"))
  -- if $string_bytes(pvalue_value) = ($ptascii("9"))
def $test_config_result_peer_front(S, n) = false -- otherwise
dec $test_config_result_peer_seek(pstate, nat, nat) : pstate
def $test_config_result_peer_seek(S, n_stage, 0) = S
def $test_config_result_peer_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_config_result_peer_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ (S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
def $test_config_result_peer_seek(S, n_stage, n) = $test_config_result_peer_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_config_result_peer_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~(S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
dec $test_config_result_peer_step(pstate) : pstate
def $test_config_result_peer_step(S) = S_next
  -- PhpStep: S ~> S_next
"""


def reach(state, start, stage):
    return [state + '_found = $test_config_result_peer_seek(' + start + ',' + str(stage) + ',3000)',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_config_result_peer_front(' + state + ',' + str(stage) + ')']


def owners(state, generator, callee):
    return ['$heap_owners($heap_graph(' + state + '),HOBJECT ' + node + ') = ' + str(count)
        for node, count in [('n_generator', generator), ('n_owner', callee)]]


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)',
        state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)',
        state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def checks(program, path, name):
    assert name == 'factory-generator-call-result-terminal-throw-releases-input'
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *reach('S_pre', 'S_initial', 0),
        'S_pre.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*',
        'pconfigcall.OWNER = (n_owner)',
        '$intrinsic_argument(S_pre,pconfigcall.SITE,0) = ((expression,true,eps,porigin_argument,z_argument))',
        'pconfigcall.LINE = 22', 'z_argument = 23',
        'porigin_argument = PORIGIN n_source pcpath',
        'expression = NExprFuncCall name (SEQUENCE eps) metadata_call',
        '$code_at(S_pre.CODE,n_source) = (pcode)',
        '$source_unit(S_pre.SOURCES,n_source) = (pcunit)',
        '$ppunpack_class(pcode,pcunit,pcpath) = (UNPACK_VAR)',
        '$code_name(pcode.NAMES,pcpath) = ((ptbytes_factory,eps))',
        '$call_target(S_pre,ptbytes_factory,eps) = (pfunction_factory)',
        'pfunction_factory.NAME = ' + text('configGeneratorFactoryReview94'),
        'S_pre.RESULT = KNOWN (POBJECT n_generator)',
        'S_pre.OBJECTS[n_generator] = GENERATOR pgenerator_initial',
        'pgenerator_initial.PHASE = GENERATOR_FRESH',
        'pgenerator_initial.FRAME = (pframe_created)',
        'pframe_created.CONTEXT = (pcallcontext_created)',
        'pcallcontext_created.TARGET = pgenerator_initial.FUNCTION',
        '$function_at($all_functions(S_pre),pgenerator_initial.FUNCTION) = (pfunction_body)',
        'pfunction_body.NAME = ' + text('configGeneratorBodyReview94'),
        'pfunction_body.ORIGIN =/= pfunction_factory.ORIGIN',
        'S_pre.CURRENT = eps', 'S_pre.FRAMES = eps']
    for variable, cell in [('watch', 'n_watch_cell'), ('call', 'n_call_cell'),
            ('keep', 'n_keep_cell'), ('saved', 'n_saved_cell'),
            ('result', 'n_result_cell'), ('effects', 'n_effects_cell')]:
        values += ['$lookup(S_pre.ENV,' + text(variable) + ') = (' + cell + ')']
    values += ['S_pre.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)',
        'S_pre.OBJECTS[n_watch] = WEAKREFERENCE (n_generator)',
        '$node_children(S_pre,HOBJECT n_watch) = eps',
        '$weakref_get(S_pre,n_watch) = POBJECT n_generator',
        'S_pre.STORE[n_call_cell] = DEFINED (POBJECT n_getter)',
        'S_pre.OBJECTS[n_getter] = INTRINSICCLOSURE INTRINSIC_INI_GET',
        'n_getter =/= n_owner',
        'S_pre.STORE[n_saved_cell] = DEFINED (POBJECT n_exception)',
        '$throwable_field(S_pre,n_exception,"line") = PINT 7',
        '$throwable_field(S_pre,n_exception,"trace") = PARRAY n_trace',
        'S_pre.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_trace_frame))]',
        '$trace_array_field(S_pre,n_trace_frame,' + text('function') + ') = PSTRING ' + text('configGeneratorFactoryReview94'),
        '$trace_array_field(S_pre,n_trace_frame,' + text('line') + ') = PINT z_argument',
        '$trace_array_field(S_pre,n_trace_frame,' + text('args') + ') = PARRAY n_trace_args',
        'S_pre.ARRAYS[n_trace_args].ITEMS = eps',
        '$node_children(S_pre,HARRAY n_trace_frame) = [HARRAY n_trace_args]',
        'S_pre.PRECISIONINI = ' + text('6'),
        '$test_outputs(S_pre.EVENTS) = ' + text('B|P|'),
        '$config_generator_start(S_pre,pconfigcall,S_pre.RESULT,n_generator)',
        *owners('S_pre', 1, 2), *common.public('S_pre'),
        'S_data = $test_config_result_peer_step(S_pre)',
        'pconfiggenerator_initial = {CALL pconfigcall,OBJECT n_generator,INPUT S_pre.RESULT,ITEMS eps,PRODUCER eps}',
        'S_data = S_pre[.ORIGIN = (porigin_argument)][.TODO = (CONFIG_GENERATOR pconfiggenerator_initial "rewind") :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$config_generator_input(S_data,pconfiggenerator_initial)',
        '$config_generator_owning_input(pconfiggenerator_initial)',
        '$config_generator_input_nodes(pconfiggenerator_initial) = [HOBJECT n_generator]',
        '$task_nodes(CONFIG_GENERATOR pconfiggenerator_initial "rewind") = [HOBJECT n_generator,HOBJECT n_generator,HOBJECT n_owner]',
        *owners('S_data', 2, 2), *common.public('S_data'),
        *reach('S_throw', 'S_data', 1),
        'S_throw.CURRENT = (pcallcontext_active)',
        'pcallcontext_active.FUNCTION = pgenerator_initial.FUNCTION',
        'pcallcontext_active.TARGET = pgenerator_initial.FUNCTION',
        'S_throw.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (GENERATOR_RESUME pgeneratorop) :: (CONFIG_GENERATOR pconfiggenerator "next") :: ptask_tail*',
        'pgeneratorop = {OBJECT n_generator,NAME "next",SITE porigin_argument,LINE z_argument,LOOP eps,ADVANCE false,ARGUMENTS eps,STARTPACK true,BORROWED true}',
        '$generator_operation_valid(S_throw,pgeneratorop)',
        '$generator_operation_nodes(pgeneratorop) = eps',
        '$generator_operation_trace(S_throw,pgeneratorop) = eps',
        'pconfiggenerator.CALL = pconfigcall', 'pconfiggenerator.OBJECT = n_generator',
        'pconfiggenerator.INPUT = S_pre.RESULT', 'pconfiggenerator.PRODUCER = eps',
        'pconfiggenerator.ITEMS = [ENTRY (KINT 3) (DIRECT pvalue_option),ENTRY (KINT 3) (DIRECT pvalue_value)]',
        '$string_bytes(pvalue_option) = (' + text('precision') + ')',
        '$string_bytes(pvalue_value) = (' + text('11') + ')',
        'S_throw.STORE[n_saved_cell] = DEFINED (POBJECT n_exception)',
        '$throwable_field(S_throw,n_exception,"trace") = PARRAY n_trace',
        'S_throw.ARRAYS[n_trace] = S_pre.ARRAYS[n_trace]',
        'S_throw.ARRAYS[n_trace_frame] = S_pre.ARRAYS[n_trace_frame]',
        'S_throw.ARRAYS[n_trace_args] = S_pre.ARRAYS[n_trace_args]',
        'S_throw.STORE[n_effects_cell] = DEFINED (PINT 4)',
        'S_throw.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_throw.PRECISIONINI = ' + text('7'),
        '$test_outputs(S_throw.EVENTS) = ' + text('B|P|Y0|H|Y1|T|'),
        'S_throw.ITERATORS = S_pre.ITERATORS', 'S_throw.NEXTITER = S_pre.NEXTITER',
        *owners('S_throw', 2, 2), *common.public('S_throw'),
        *reach('S_thrown', 'S_throw', 2),
        'S_thrown.TODO = (THROW_SEARCH n_exception) :: (CONFIG_GENERATOR pconfiggenerator "next") :: ptask_tail*',
        '$config_generator_valid(S_thrown,pconfiggenerator,"next")',
        'S_thrown.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
        'pgenerator_closed.PHASE = GENERATOR_CLOSED', 'pgenerator_closed.FRAME = eps',
        '$node_children(S_thrown,HOBJECT n_generator) = eps',
        '$weakref_get(S_thrown,n_watch) = POBJECT n_generator',
        '$throwable_field(S_thrown,n_exception,"trace") = PARRAY n_trace',
        'S_thrown.ARRAYS[n_trace] = S_pre.ARRAYS[n_trace]',
        *owners('S_thrown', 2, 2), *common.public('S_thrown'),
        'S_last_callee = S_thrown[.STORE[n_keep_cell] = DEFINED PNULL]',
        '$heap_owners($heap_graph(S_last_callee),HOBJECT n_owner) = 1',
        'S_callee_stopped = $test_config_result_peer_step(S_last_callee)',
        'S_callee_stopped = S_last_callee[.COMPLETION = UNSUPPORTED "CONFIG Generator unpack last cleanup owner"]',
        '$drive_steps(S_callee_stopped,4) = S_callee_stopped',
        'S_after_data = $test_config_result_peer_step(S_thrown)',
        'S_after_data = $config_generator_discard(S_thrown[.TODO = (THROW_SEARCH n_exception) :: ptask_tail*],pconfiggenerator,"next")',
        *reach('S_input', 'S_thrown', 3),
        'S_input.TODO = (THROW_SEARCH n_exception) :: (CONFIG_GENERATOR pconfiggenerator "input-release") :: ptask_tail*',
        'S_input.ORIGIN = (pconfigcall.SITE)',
        '$config_generator_valid(S_input,pconfiggenerator,"input-release")',
        '$task_nodes(CONFIG_GENERATOR pconfiggenerator "input-release") = [HOBJECT n_generator,HOBJECT n_owner]',
        'S_input.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
        '$weakref_get(S_input,n_watch) = POBJECT n_generator',
        '$throwable_live(S_input,n_exception)',
        '$throwable_field(S_input,n_exception,"trace") = PARRAY n_trace',
        'S_input.ARRAYS = S_thrown.ARRAYS', 'S_input.STORE = S_thrown.STORE',
        'S_input.PRECISIONINI = ' + text('7'),
        '$test_outputs(S_input.EVENTS) = ' + text('B|P|Y0|H|Y1|T|'),
        *owners('S_input', 1, 2), *common.public('S_input'),
        'S_input_last_callee = S_input[.STORE[n_keep_cell] = DEFINED PNULL]',
        '$heap_owners($heap_graph(S_input_last_callee),HOBJECT n_owner) = 1',
        'S_input_callee_stopped = $test_config_result_peer_step(S_input_last_callee)',
        'S_input_callee_stopped = S_input_last_callee[.COMPLETION = UNSUPPORTED "CONFIG Generator unpack last cleanup owner"]',
        '$drive_steps(S_input_callee_stopped,4) = S_input_callee_stopped',
        'S_after_input = $test_config_result_peer_step(S_input)',
        'S_after_input = $config_generator_discard(S_input[.TODO = (THROW_SEARCH n_exception) :: ptask_tail*],pconfiggenerator,"input-release")',
        *reach('S_disposed', 'S_input', 4),
        'S_disposed.TODO = (THROW_SEARCH n_exception) :: ptask_tail*',
        '~((HOBJECT n_generator) <- S_disposed.ALLOCATIONS)',
        '$weakref_get(S_disposed,n_watch) = PNULL',
        '$config_generator_history(S_disposed,pconfiggenerator)',
        '$config_generator_retired_scope(S_disposed,pconfiggenerator)',
        '~$config_generator_scope(S_disposed,pconfiggenerator)',
        '$task_nodes(CONFIG_GENERATOR pconfiggenerator "invoke") = [HOBJECT n_owner]',
        '$throwable_live(S_disposed,n_exception)',
        '$throwable_field(S_disposed,n_exception,"trace") = PARRAY n_trace',
        '$throwable_field(S_disposed,n_exception,"previous") = PNULL',
        'S_disposed.STORE = S_thrown.STORE', 'S_disposed.ARRAYS = S_thrown.ARRAYS',
        'S_disposed.ITERATORS = S_pre.ITERATORS', 'S_disposed.NEXTITER = S_pre.NEXTITER',
        *owners('S_disposed', 0, 1), *common.public('S_disposed'),
        *budget('S_input'),
        *reach('S_recovery', 'S_disposed', 5),
        'S_recovery.TODO = (CONFIG_INVOKE pconfigcall_recovery) :: ptask_recovery*',
        'pconfigcall_recovery.OWNER = (n_owner)',
        '$lookup(S_recovery.ENV,' + text('e') + ') = (n_caught_cell)',
        'S_recovery.STORE[n_caught_cell] = DEFINED (POBJECT n_exception)',
        'S_recovery.STORE[n_saved_cell] = DEFINED (POBJECT n_exception)',
        'S_recovery.STORE[n_result_cell] = DEFINED (PINT 99)',
        '$weakref_get(S_recovery,n_watch) = PNULL',
        'S_recovery.PRECISIONINI = ' + text('7'),
        *owners('S_recovery', 0, 2), *common.public('S_recovery'),
        *common.step('S_recovered', 'S_recovery'),
        'S_recovered.RESULT = KNOWN pvalue_old',
        '$string_bytes(pvalue_old) = (' + text('7') + ')',
        'S_recovered.PRECISIONINI = ' + text('9'),
        *owners('S_recovered', 0, 1), *common.public('S_recovered'),
        'S_final = $drive_steps(S_recovered,3000)', 'S_final.COMPLETION = NORMAL',
        'S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        '~((HOBJECT n_generator) <- S_final.ALLOCATIONS)',
        '$weakref_get(S_final,n_watch) = PNULL',
        '$test_outputs(S_final.EVENTS) = ' + text('B|P|Y0|H|Y1|T|I|99|4|7|configGeneratorFactoryReview94|23|A|F|D|L|7|R|7|9|99'),
        *common.public('S_final')]
    return values


def partition(values, part):
    cut = values.index('$heap_valid($heap_graph(S_thrown))') + 1
    if part == 'entry':
        return values[:cut]
    # Recompute the same real source state; repeated bindings add no coverage.
    setup = [values[0], values[1], *reach('S_pre', 'S_initial', 0),
        'S_pre.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*',
        'pconfigcall.OWNER = (n_owner)']
    for variable, cell in [('watch', 'n_watch_cell'), ('keep', 'n_keep_cell'),
            ('saved', 'n_saved_cell'), ('result', 'n_result_cell')]:
        setup += ['$lookup(S_pre.ENV,' + text(variable) + ') = (' + cell + ')']
    setup += ['S_pre.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)',
        'S_pre.OBJECTS[n_watch] = WEAKREFERENCE (n_generator)',
        *reach('S_thrown', 'S_pre', 2),
        'S_thrown.TODO = (THROW_SEARCH n_exception) :: (CONFIG_GENERATOR pconfiggenerator "next") :: ptask_tail*',
        'pconfiggenerator.CALL = pconfigcall',
        'S_thrown.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
        '$throwable_field(S_thrown,n_exception,"trace") = PARRAY n_trace']
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
