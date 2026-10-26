#!/usr/bin/env python3
"""Returned Generator DATA preserves an Exception captured by getIterator."""
import argparse
import json
import os
import sys
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import config_aggregate_generator_unpack_review_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64
PREFIX = r"""
dec $test_config_aggen_peer_front(pstate, nat) : bool
def $test_config_aggen_peer_front(S, 0) = true
  -- if S.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_config_aggen_peer_front(S, 1) = true
  -- if S.TODO = (CONFIG_AGGREGATE pconfigaggregate) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $test_config_aggen_peer_front(S, 2) = true
  -- if S.TODO = (THROW_VALUE porigin z) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (GENERATOR_RESUME pgeneratorop) :: (CONFIG_GENERATOR pconfiggenerator "next") :: ptask_caller*
def $test_config_aggen_peer_front(S, 3) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_GENERATOR pconfiggenerator "next") :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $test_config_aggen_peer_front(S, 4) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if S.DESTRUCTION.OPERATIONS = eps
def $test_config_aggen_peer_front(S, 5) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_option),NAMED_SENT (KNOWN pvalue_value)]
  -- if $string_bytes(pvalue_option) = ($ptascii("precision"))
  -- if $string_bytes(pvalue_value) = ($ptascii("9"))
def $test_config_aggen_peer_front(S, n) = false -- otherwise
dec $test_config_aggen_peer_seek(pstate, nat, nat) : pstate
def $test_config_aggen_peer_seek(S, n_stage, 0) = S
def $test_config_aggen_peer_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_config_aggen_peer_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ (S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
def $test_config_aggen_peer_seek(S, n_stage, n) = $test_config_aggen_peer_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_config_aggen_peer_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~(S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
dec $test_config_aggen_peer_step(pstate) : pstate
def $test_config_aggen_peer_step(S) = S_next
  -- PhpStep: S ~> S_next
"""


def reach(state, start, stage):
    return [state + '_found = $test_config_aggen_peer_seek(' + start + ',' + str(stage) + ',3000)',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_config_aggen_peer_front(' + state + ',' + str(stage) + ')']


def owners(state, aggregate, generator, callee):
    return ['$heap_owners($heap_graph(' + state + '),HOBJECT ' + node + ') = ' + str(count)
        for node, count in [('n_aggregate', aggregate), ('n_generator', generator), ('n_owner', callee)]]


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)',
        state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)',
        state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def checks(program, path, name):
    assert name == 'retained-config-aggregate-generator-rethrows-producer-exception'
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *reach('S_pre', 'S_initial', 0),
        'S_pre.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*',
        'pconfigcall.OWNER = (n_owner)',
        '$intrinsic_argument(S_pre,pconfigcall.SITE,0) = ((expression,true,eps,porigin_argument,z_argument))',
        'pconfigcall.LINE = 23', 'z_argument = 24',
        'S_pre.RESULT = VARIABLE ' + text('aggregate') + ' z_argument']
    for name, cell in [('aggregate', 'n_aggregate_cell'), ('aggregateHold', 'n_aggregate_hold'),
            ('it', 'n_generator_cell'), ('call', 'n_call_cell'),
            ('keep', 'n_keep_cell'), ('saved', 'n_saved_cell'), ('result', 'n_result_cell'),
            ('effects', 'n_effects_cell')]:
        values += ['$lookup(S_pre.ENV,' + text(name) + ') = (' + cell + ')']
    values += ['S_pre.STORE[n_aggregate_cell] = DEFINED (POBJECT n_aggregate)',
        'S_pre.STORE[n_generator_cell] = DEFINED (POBJECT n_generator)',
        'S_pre.STORE[n_saved_cell] = DEFINED PNULL',
        '$config_aggregate_start(S_pre,pconfigcall,S_pre.RESULT,n_aggregate)',
        *owners('S_pre', 2, 2, 3), *common.public('S_pre'),
        *reach('S_return', 'S_pre', 1),
        'S_return.TODO = (CONFIG_AGGREGATE pconfigaggregate) :: ptask_tail*',
        'pconfigaggregate = {CALL pconfigcall,OBJECT n_aggregate,INPUT S_pre.RESULT}',
        'S_return.RESULT = KNOWN (POBJECT n_generator)',
        'S_return.OBJECTS[n_generator] = GENERATOR pgenerator_initial',
        'pgenerator_initial.PHASE = GENERATOR_FRESH',
        '$config_aggregate_generator_return_allowed(S_return,pconfigaggregate)',
        '~$config_aggregate_return_allowed(S_return,pconfigaggregate)',
        '$task_nodes(CONFIG_AGGREGATE pconfigaggregate) = [HOBJECT n_owner]',
        'S_return.STORE[n_aggregate_cell] = DEFINED (PINT 23)',
        'S_return.STORE[n_call_cell] = DEFINED (POBJECT n_getter)',
        'S_return.OBJECTS[n_getter] = INTRINSICCLOSURE INTRINSIC_INI_GET',
        'n_getter =/= n_owner', 'S_return.PRECISIONINI = ' + text('6'),
        'S_return.STORE[n_saved_cell] = DEFINED (POBJECT n_exception)',
        '$throwable_live(S_return,n_exception)',
        '$string_bytes($throwable_field(S_return,n_exception,"message")) = (' + text('config-aggregate-generator-saved-before-resume91') + ')',
        '$throwable_field(S_return,n_exception,"line") = PINT 14',
        '$throwable_field(S_return,n_exception,"trace") = PARRAY n_trace',
        'S_return.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_frame))]',
        '$trace_array_field(S_return,n_frame,' + text('function') + ') = PSTRING ' + text('getIterator'),
        '$trace_array_field(S_return,n_frame,' + text('class') + ') = PSTRING ' + text('ConfigGeneratorExceptionAggregateReview91'),
        '$trace_array_field(S_return,n_frame,' + text('type') + ') = PSTRING ' + text('->'),
        '$trace_array_field(S_return,n_frame,' + text('line') + ') = PINT z_argument',
        '$trace_array_field(S_return,n_frame,' + text('args') + ') = PARRAY n_args',
        'S_return.ARRAYS[n_args].ITEMS = eps',
        '$node_children(S_return,HARRAY n_frame) = [HARRAY n_args]',
        '$test_outputs(S_return.EVENTS) = ' + text('B|G|'),
        *owners('S_return', 1, 3, 2), *common.public('S_return'),
        'S_data = $test_config_aggen_peer_step(S_return)',
        'S_data.TODO = (CONFIG_GENERATOR pconfiggenerator_initial "rewind") :: ptask_tail*',
        'pconfiggenerator_initial = {CALL pconfigcall,OBJECT n_generator,INPUT pconfigaggregate.INPUT,ITEMS eps}',
        'S_data.RESULT = KNOWN PNULL', 'S_data.STORE = S_return.STORE',
        'S_data.OBJECTS = S_return.OBJECTS', 'S_data.ARRAYS = S_return.ARRAYS',
        '$heap_graph(S_data) = $heap_graph(S_return)',
        '$task_nodes(CONFIG_GENERATOR pconfiggenerator_initial "rewind") = [HOBJECT n_generator,HOBJECT n_owner]',
        'S_data.ITERATORS = S_pre.ITERATORS', 'S_data.NEXTITER = S_pre.NEXTITER',
        '$config_generator_valid(S_data,pconfiggenerator_initial,"rewind")',
        *common.public('S_data'),
        'S_fake_pre = S_return[.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*][.ORIGIN = (pconfigcall.SITE)][.RESULT = pconfigaggregate.INPUT]',
        '~$config_generator_start(S_fake_pre,pconfigcall,pconfigaggregate.INPUT,n_generator)',
        *reach('S_throw', 'S_data', 2),
        'S_throw.CURRENT = (pcallcontext)',
        'pcallcontext.FUNCTION = pgenerator_initial.FUNCTION',
        'pcallcontext.TARGET = pgenerator_initial.FUNCTION',
        'S_throw.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (GENERATOR_RESUME pgeneratorop) :: (CONFIG_GENERATOR pconfiggenerator "next") :: ptask_tail*',
        'pgeneratorop = {OBJECT n_generator,NAME "next",SITE porigin_argument,LINE z_argument,LOOP eps,ADVANCE false,ARGUMENTS eps,STARTPACK true,BORROWED true}',
        '$generator_operation_valid(S_throw,pgeneratorop)',
        '$generator_operation_nodes(pgeneratorop) = eps',
        '$generator_operation_trace(S_throw,pgeneratorop) = eps',
        'pconfiggenerator.CALL = pconfigcall', 'pconfiggenerator.OBJECT = n_generator',
        'pconfiggenerator.INPUT = pconfigaggregate.INPUT',
        'pconfiggenerator.ITEMS = [ENTRY (KINT 3) (DIRECT pvalue_option),ENTRY (KINT 3) (DIRECT pvalue_value)]',
        '$string_bytes(pvalue_option) = (' + text('precision') + ')',
        '$string_bytes(pvalue_value) = (' + text('11') + ')',
        'S_throw.STORE[n_saved_cell] = DEFINED (POBJECT n_exception)',
        '$throwable_field(S_throw,n_exception,"trace") = PARRAY n_trace',
        'S_throw.ARRAYS = S_return.ARRAYS',
        'S_throw.STORE[n_generator_cell] = DEFINED (PINT 17)',
        'S_throw.STORE[n_aggregate_cell] = DEFINED (PINT 23)',
        'S_throw.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_throw.STORE[n_effects_cell] = DEFINED (PINT 4)',
        'S_throw.PRECISIONINI = ' + text('7'),
        '$test_outputs(S_throw.EVENTS) = ' + text('B|G|Y0|Y1|T|'),
        *owners('S_throw', 1, 2, 2), *common.public('S_throw'),
        *reach('S_thrown', 'S_throw', 3),
        'S_thrown.TODO = (THROW_SEARCH n_exception) :: (CONFIG_GENERATOR pconfiggenerator "next") :: ptask_tail*',
        '$config_generator_valid(S_thrown,pconfiggenerator,"next")',
        'S_thrown.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
        'pgenerator_closed.PHASE = GENERATOR_CLOSED',
        'S_thrown.STORE[n_saved_cell] = DEFINED (POBJECT n_exception)',
        '$throwable_field(S_thrown,n_exception,"trace") = PARRAY n_trace',
        'S_thrown.ARRAYS = S_return.ARRAYS',
        *owners('S_thrown', 1, 2, 2), *common.public('S_thrown')]
    # Source92 covers actual sole-DATA retirement instead of this old refusal.
    values += ['S_last_callee = S_thrown[.STORE[n_keep_cell] = DEFINED PNULL]',
        '$heap_owners($heap_graph(S_last_callee),HOBJECT n_owner) = 1',
        'S_callee_stopped = $test_config_aggen_peer_step(S_last_callee)',
        'S_callee_stopped = S_last_callee[.COMPLETION = UNSUPPORTED "CONFIG Generator unpack last cleanup owner"]',
        '$drive_steps(S_callee_stopped,4) = S_callee_stopped',
        'S_after = $test_config_aggen_peer_step(S_thrown)',
        'S_after = $config_generator_discard(S_thrown[.TODO = (THROW_SEARCH n_exception) :: ptask_tail*],pconfiggenerator,"next")',
        *reach('S_disposed', 'S_after', 4),
        'S_disposed.TODO = (THROW_SEARCH n_exception) :: ptask_tail*',
        '$throwable_live(S_disposed,n_exception)',
        '$throwable_field(S_disposed,n_exception,"previous") = PNULL',
        'S_disposed.STORE = S_thrown.STORE', 'S_disposed.OBJECTS = S_thrown.OBJECTS',
        'S_disposed.ARRAYS = S_thrown.ARRAYS',
        'S_disposed.ITERATORS = S_pre.ITERATORS', 'S_disposed.NEXTITER = S_pre.NEXTITER',
        *owners('S_disposed', 1, 1, 1), *common.public('S_disposed'),
        *budget('S_return'), *budget('S_thrown'),
        *reach('S_recovery', 'S_disposed', 5),
        'S_recovery.TODO = (CONFIG_INVOKE pconfigcall_recovery) :: ptask_recovery*',
        'pconfigcall_recovery.OWNER = (n_owner)',
        '$lookup(S_recovery.ENV,' + text('e') + ') = (n_caught_cell)',
        'S_recovery.STORE[n_caught_cell] = DEFINED (POBJECT n_exception)',
        'S_recovery.STORE[n_saved_cell] = DEFINED (POBJECT n_exception)',
        'S_recovery.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_recovery.PRECISIONINI = ' + text('7'),
        *owners('S_recovery', 1, 1, 2), *common.public('S_recovery'),
        *common.step('S_recovered', 'S_recovery'),
        'S_recovered.RESULT = KNOWN pvalue_old',
        '$string_bytes(pvalue_old) = (' + text('7') + ')',
        'S_recovered.PRECISIONINI = ' + text('9'),
        *owners('S_recovered', 1, 1, 1), *common.public('S_recovered'),
        'S_final = $drive_steps(S_recovered,3000)', 'S_final.COMPLETION = NORMAL',
        'S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.ITERATORS = S_pre.ITERATORS', 'S_final.NEXTITER = S_pre.NEXTITER',
        '$test_outputs(S_final.EVENTS) = ' + text('B|G|Y0|Y1|T|I|99|4|7|17|23|getIterator|ConfigGeneratorExceptionAggregateReview91|->|24|A|F|Z|L|7|R|7|9|99'),
        *common.public('S_final')]
    return values


def partition(values, part):
    cut = values.index('$heap_valid($heap_graph(S_thrown))') + 1
    if part == 'entry':
        return values[:cut]
    # Every cleanup input is recomputed from the same original PHP source.
    setup = [values[0], values[1], *reach('S_pre', 'S_initial', 0),
        'S_pre.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*',
        'pconfigcall.OWNER = (n_owner)']
    for name, cell in [('keep', 'n_keep_cell'),
            ('saved', 'n_saved_cell'), ('result', 'n_result_cell')]:
        setup += ['$lookup(S_pre.ENV,' + text(name) + ') = (' + cell + ')']
    setup += [*reach('S_return', 'S_pre', 1),
        'S_return.TODO = (CONFIG_AGGREGATE pconfigaggregate) :: ptask_tail*',
        'pconfigaggregate.OBJECT = n_aggregate',
        'S_return.RESULT = KNOWN (POBJECT n_generator)',
        'S_data = $test_config_aggen_peer_step(S_return)',
        *reach('S_thrown', 'S_data', 3),
        'S_thrown.TODO = (THROW_SEARCH n_exception) :: (CONFIG_GENERATOR pconfiggenerator "next") :: ptask_tail*']
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
