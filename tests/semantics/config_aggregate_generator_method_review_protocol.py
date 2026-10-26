#!/usr/bin/env python3
"""Real method-Generator capture survives two sends and terminal throw cleanup."""
import argparse
import json
import os
import sys
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import config_aggregate_generator_method_review_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64
PREFIX = r"""
dec $test_config_method_peer_front(pstate, nat) : bool
def $test_config_method_peer_front(S, 0) = true
  -- if S.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_config_method_peer_front(S, 1) = true
  -- if S.TODO = (CONFIG_AGGREGATE pconfigaggregate) :: ptask*
  -- if S.RESULT = KNOWN (POBJECT n)
  -- if S.OBJECTS[n] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_FRESH
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $test_config_method_peer_front(S, 2) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask*
  -- if pconfiggenerator.ITEMS = eps
  -- if S.OBJECTS[pconfiggenerator.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_PAUSED
def $test_config_method_peer_front(S, 3) = true
  -- if S.TODO = (THROW_VALUE porigin z) :: ptask_body*
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (GENERATOR_RESUME pgeneratorop) :: (CONFIG_GENERATOR pconfiggenerator "next") :: ptask_caller*
def $test_config_method_peer_front(S, 4) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_GENERATOR pconfiggenerator "next") :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $test_config_method_peer_front(S, 5) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask*
  -- if ~$test_config_method_peer_front(S,4)
  -- if S.DESTRUCTION.OPERATIONS = eps
def $test_config_method_peer_front(S, 6) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_option),NAMED_SENT (KNOWN pvalue_value)]
  -- if $string_bytes(pvalue_option) = ($ptascii("precision"))
  -- if $string_bytes(pvalue_value) = ($ptascii("9"))
def $test_config_method_peer_front(S, n) = false -- otherwise
dec $test_config_method_peer_seek(pstate, nat, nat) : pstate
def $test_config_method_peer_seek(S, n_stage, 0) = S
def $test_config_method_peer_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_config_method_peer_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ (S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
def $test_config_method_peer_seek(S, n_stage, n) = $test_config_method_peer_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_config_method_peer_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~(S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
dec $test_config_method_peer_step(pstate) : pstate
def $test_config_method_peer_step(S) = S_next
  -- PhpStep: S ~> S_next
"""


def reach(state, start, stage):
    return [state + '_found = $test_config_method_peer_seek(' + start + ',' + str(stage) + ',3000)',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_config_method_peer_front(' + state + ',' + str(stage) + ')']


def owners(state, receiver, generator, callee):
    return ['$heap_owners($heap_graph(' + state + '),HOBJECT ' + node + ') = ' + str(count)
        for node, count in [('n_receiver', receiver), ('n_generator', generator), ('n_owner', callee)]]


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)',
        state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)',
        state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def checks(program, path, name):
    assert name == 'aggregate-generator-method-terminal-throw-keeps-real-receiver-and-trace'
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *reach('S_pre', 'S_initial', 0),
        'S_pre.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*',
        'pconfigcall.OWNER = (n_owner)',
        '$intrinsic_argument(S_pre,pconfigcall.SITE,0) = ((expression,true,eps,porigin_argument,z_argument))',
        'pconfigcall.LINE = 18', 'z_argument = 19',
        'S_pre.RESULT = VARIABLE ' + text('aggregate') + ' z_argument']
    for variable, cell in [('aggregate', 'n_receiver_cell'), ('hold', 'n_hold_cell'),
            ('watch', 'n_watch_cell'), ('call', 'n_call_cell'), ('keep', 'n_keep_cell'),
            ('saved', 'n_saved_cell'), ('result', 'n_result_cell'), ('effects', 'n_effects_cell')]:
        values += ['$lookup(S_pre.ENV,' + text(variable) + ') = (' + cell + ')']
    values += ['S_pre.STORE[n_receiver_cell] = DEFINED (POBJECT n_receiver)',
        'S_pre.STORE[n_hold_cell] = DEFINED (POBJECT n_receiver)',
        'S_pre.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)',
        'S_pre.OBJECTS[n_watch] = WEAKREFERENCE (n_receiver)',
        '$node_children(S_pre,HOBJECT n_watch) = eps',
        '$heap_owners($heap_graph(S_pre),HOBJECT n_receiver) = 2',
        '$heap_owners($heap_graph(S_pre),HOBJECT n_owner) = 3', *common.public('S_pre'),
        *reach('S_return', 'S_pre', 1),
        'S_return.TODO = (CONFIG_AGGREGATE pconfigaggregate) :: ptask_tail*',
        'pconfigaggregate = {CALL pconfigcall,OBJECT n_receiver,INPUT S_pre.RESULT}',
        'S_return.RESULT = KNOWN (POBJECT n_generator)',
        'S_return.OBJECTS[n_generator] = GENERATOR pgenerator_fresh',
        'pgenerator_fresh.PHASE = GENERATOR_FRESH',
        'pgenerator_fresh.CLOSURE = eps', 'pgenerator_fresh.ACCESS = eps',
        'pgenerator_fresh.FRAME = (pframe_method)', 'pframe_method.CONTEXT = (pcallcontext_created)',
        'pcallcontext_created.TARGET = CONFIG_AGGREGATE_GENERATOR_TARGET pconfiggeneratorproducer',
        'pconfiggeneratorproducer = {AGGREGATE pconfigaggregate,METHOD pgenerator_fresh.FUNCTION}',
        'pcallcontext_created.FUNCTION = pconfiggeneratorproducer.METHOD',
        'pcallcontext_created.INSTANCE = eps',
        '$target_nodes(CONFIG_AGGREGATE_GENERATOR_TARGET pconfiggeneratorproducer) = [HOBJECT n_receiver]',
        '$config_aggregate_generator_producer_valid(S_return,pconfiggeneratorproducer)',
        '$config_aggregate_generator_capture(S_return,pconfiggeneratorproducer,n_generator)',
        '$config_aggregate_method_generator_return_allowed(S_return,pconfigaggregate)',
        '$test_outputs(S_return.EVENTS) = ' + text('B|'),
        *owners('S_return', 3, 1, 3), *common.public('S_return'),
        'S_data = $test_config_method_peer_step(S_return)',
        'pconfiggenerator_initial = {CALL pconfigcall,OBJECT n_generator,INPUT S_pre.RESULT,ITEMS eps,PRODUCER (pconfiggeneratorproducer)}',
        'S_data = S_return[.TODO = (CONFIG_GENERATOR pconfiggenerator_initial "rewind") :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$heap_graph(S_data) = $heap_graph(S_return)',
        '$task_nodes(CONFIG_GENERATOR pconfiggenerator_initial "rewind") = [HOBJECT n_generator,HOBJECT n_owner]',
        'S_data.ITERATORS = S_pre.ITERATORS', 'S_data.NEXTITER = S_pre.NEXTITER',
        *common.public('S_data'),
        'pconfiggenerator_missing = pconfiggenerator_initial[.PRODUCER = eps]',
        'S_missing = S_data[.TODO = (CONFIG_GENERATOR pconfiggenerator_missing "rewind") :: ptask_tail*]',
        '~$config_generator_valid(S_missing,pconfiggenerator_missing,"rewind")',
        'pconfiggeneratorproducer_bad = pconfiggeneratorproducer[.METHOD = pconfigcall.SITE]',
        '~$config_aggregate_generator_producer_valid(S_return,pconfiggeneratorproducer_bad)',
        *reach('S_ready', 'S_data', 2),
        'S_ready.TODO = (CONFIG_GENERATOR pconfiggenerator_ready "ready") :: ptask_tail*',
        'pconfiggenerator_ready = pconfiggenerator_initial',
        'S_ready.OBJECTS[n_generator] = GENERATOR pgenerator_paused',
        'pgenerator_paused.FRAME = (pframe_paused)',
        'pframe_paused.CONTEXT = (pcallcontext_paused)',
        'pcallcontext_paused.TARGET = CONFIG_AGGREGATE_GENERATOR_TARGET pconfiggeneratorproducer',
        'S_ready.CURRENT = eps', 'S_ready.FRAMES = eps',
        'S_ready.STORE[n_receiver_cell] = DEFINED (PINT 23)',
        'S_ready.STORE[n_hold_cell] = DEFINED (POBJECT n_receiver)',
        'S_ready.STORE[n_saved_cell] = DEFINED (POBJECT n_exception)',
        'S_ready.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_ready.STORE[n_effects_cell] = DEFINED (PINT 1)',
        'S_ready.PRECISIONINI = ' + text('6'),
        '$test_outputs(S_ready.EVENTS) = ' + text('B|Y0|S|'),
        '$throwable_field(S_ready,n_exception,"line") = PINT 7',
        '$throwable_field(S_ready,n_exception,"trace") = PARRAY n_trace',
        'S_ready.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_trace_frame))]',
        '$trace_array_field(S_ready,n_trace_frame,' + text('function') + ') = PSTRING ' + text('getIterator'),
        '$trace_array_field(S_ready,n_trace_frame,' + text('class') + ') = PSTRING ' + text('ConfigAggregateGeneratorMethodReview93'),
        '$trace_array_field(S_ready,n_trace_frame,' + text('type') + ') = PSTRING ' + text('->'),
        '$trace_array_field(S_ready,n_trace_frame,' + text('line') + ') = PINT z_argument',
        '$trace_array_field(S_ready,n_trace_frame,' + text('args') + ') = PARRAY n_trace_args',
        'S_ready.ARRAYS[n_trace_args].ITEMS = eps',
        '$node_children(S_ready,HARRAY n_trace_frame) = [HARRAY n_trace_args]',
        *owners('S_ready', 2, 1, 2), *common.public('S_ready'),
        *reach('S_throw', 'S_ready', 3),
        'S_throw.CURRENT = (pcallcontext_active)',
        'pcallcontext_active.TARGET = CONFIG_AGGREGATE_GENERATOR_TARGET pconfiggeneratorproducer',
        'pcallcontext_active.FUNCTION = pconfiggeneratorproducer.METHOD',
        'pcallcontext_active.INSTANCE = eps',
        'S_throw.FRAMES = pframe_caller :: pframe_tail*',
        'pframe_caller.TODO = (GENERATOR_RESUME pgeneratorop) :: (CONFIG_GENERATOR pconfiggenerator "next") :: ptask_tail*',
        'pgeneratorop = {OBJECT n_generator,NAME "next",SITE porigin_argument,LINE z_argument,LOOP eps,ADVANCE false,ARGUMENTS eps,STARTPACK true,BORROWED true}',
        '$generator_operation_valid(S_throw,pgeneratorop)',
        '$generator_operation_nodes(pgeneratorop) = eps',
        '$generator_operation_trace(S_throw,pgeneratorop) = eps',
        'pconfiggenerator.PRODUCER = (pconfiggeneratorproducer)',
        'pconfiggenerator.ITEMS = [ENTRY (KINT 3) (DIRECT pvalue_option),ENTRY (KINT 3) (DIRECT pvalue_value)]',
        '$string_bytes(pvalue_option) = (' + text('precision') + ')',
        '$string_bytes(pvalue_value) = (' + text('11') + ')',
        'S_throw.STORE[n_call_cell] = DEFINED (POBJECT n_getter)',
        'S_throw.OBJECTS[n_getter] = INTRINSICCLOSURE INTRINSIC_INI_GET',
        'S_throw.STORE[n_saved_cell] = DEFINED (POBJECT n_exception)',
        'S_throw.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_throw.STORE[n_effects_cell] = DEFINED (PINT 3)',
        'S_throw.PRECISIONINI = ' + text('7'),
        '$throwable_field(S_throw,n_exception,"trace") = PARRAY n_trace',
        'S_throw.ARRAYS[n_trace] = S_ready.ARRAYS[n_trace]',
        *owners('S_throw', 2, 1, 2), *common.public('S_throw'),
        *reach('S_thrown', 'S_throw', 4),
        'S_thrown.TODO = (THROW_SEARCH n_exception) :: (CONFIG_GENERATOR pconfiggenerator "next") :: ptask_tail*',
        'S_thrown.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
        'pgenerator_closed.PHASE = GENERATOR_CLOSED', 'pgenerator_closed.FRAME = eps',
        '$node_children(S_thrown,HOBJECT n_generator) = eps',
        '$config_aggregate_generator_capture(S_thrown,pconfiggeneratorproducer,n_generator)',
        *owners('S_thrown', 1, 1, 2), *common.public('S_thrown'),
        'S_last_callee = S_thrown[.STORE[n_keep_cell] = DEFINED PNULL]',
        '$heap_owners($heap_graph(S_last_callee),HOBJECT n_owner) = 1',
        'S_stopped = $test_config_method_peer_step(S_last_callee)',
        'S_stopped = S_last_callee[.COMPLETION = UNSUPPORTED "CONFIG Generator unpack last cleanup owner"]',
        '$drive_steps(S_stopped,4) = S_stopped',
        'S_after = $test_config_method_peer_step(S_thrown)',
        'S_after = $config_generator_discard(S_thrown[.TODO = (THROW_SEARCH n_exception) :: ptask_tail*],pconfiggenerator,"next")',
        *reach('S_disposed', 'S_thrown', 5),
        'S_disposed.TODO = (THROW_SEARCH n_exception) :: ptask_tail*',
        '~((HOBJECT n_generator) <- S_disposed.ALLOCATIONS)',
        '$weakref_get(S_disposed,n_watch) = POBJECT n_receiver',
        '$throwable_field(S_disposed,n_exception,"trace") = PARRAY n_trace',
        '$throwable_field(S_disposed,n_exception,"previous") = PNULL',
        *owners('S_disposed', 1, 0, 1), *common.public('S_disposed'),
        *budget('S_return'), *budget('S_thrown'),
        *reach('S_recovery', 'S_disposed', 6),
        'S_recovery.TODO = (CONFIG_INVOKE pconfigcall_recovery) :: ptask_recovery*',
        'pconfigcall_recovery.OWNER = (n_owner)',
        '$lookup(S_recovery.ENV,' + text('e') + ') = (n_caught_cell)',
        'S_recovery.STORE[n_caught_cell] = DEFINED (POBJECT n_exception)',
        'S_recovery.STORE[n_saved_cell] = DEFINED (POBJECT n_exception)',
        'S_recovery.STORE[n_result_cell] = DEFINED (PINT 99)',
        '~((HOBJECT n_receiver) <- S_recovery.ALLOCATIONS)',
        '$weakref_get(S_recovery,n_watch) = PNULL',
        '$config_generator_retired_scope(S_recovery,pconfiggenerator)',
        'S_recovery.PRECISIONINI = ' + text('7'),
        *owners('S_recovery', 0, 0, 2), *common.public('S_recovery'),
        *common.step('S_recovered', 'S_recovery'),
        'S_recovered.RESULT = KNOWN pvalue_old',
        '$string_bytes(pvalue_old) = (' + text('7') + ')',
        'S_recovered.PRECISIONINI = ' + text('9'),
        *owners('S_recovered', 0, 0, 1), *common.public('S_recovered'),
        'S_final = $drive_steps(S_recovered,3000)', 'S_final.COMPLETION = NORMAL',
        'S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        '$weakref_get(S_final,n_watch) = PNULL',
        '$test_outputs(S_final.EVENTS) = ' + text('B|Y0|S|Y1|T|I|99|3|7|23|getIterator|ConfigAggregateGeneratorMethodReview93|->|19|A|F|H|D|L|7|R|7|9|99'),
        *common.public('S_final')]
    return values


def partition(values, part):
    cut = values.index('$heap_valid($heap_graph(S_throw))') + 1
    if part == 'entry':
        return values[:cut]
    # Recompute real creation/throw cuts; no method frame or snapshot is invented.
    setup = [values[0], values[1], *reach('S_pre', 'S_initial', 0),
        'S_pre.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*',
        'pconfigcall.OWNER = (n_owner)']
    for variable, cell in [('watch', 'n_watch_cell'), ('keep', 'n_keep_cell'),
            ('saved', 'n_saved_cell'), ('result', 'n_result_cell')]:
        setup += ['$lookup(S_pre.ENV,' + text(variable) + ') = (' + cell + ')']
    setup += ['S_pre.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)',
        'S_pre.OBJECTS[n_watch] = WEAKREFERENCE (n_receiver)',
        *reach('S_return', 'S_pre', 1), *reach('S_throw', 'S_pre', 3),
        'S_throw.FRAMES = pframe_caller :: pframe_tail*',
        'pframe_caller.TODO = (GENERATOR_RESUME pgeneratorop) :: (CONFIG_GENERATOR pconfiggenerator "next") :: ptask_tail*',
        'pconfiggenerator.OBJECT = n_generator',
        'pconfiggenerator.PRODUCER = (pconfiggeneratorproducer)',
        'S_throw.STORE[n_saved_cell] = DEFINED (POBJECT n_exception)',
        '$throwable_field(S_throw,n_exception,"trace") = PARRAY n_trace']
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
