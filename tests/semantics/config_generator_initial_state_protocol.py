#!/usr/bin/env python3
"""First-yield reuse and CLOSED rejection retain their distinct DATA roots."""
import argparse
import json
import os
import sys
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import config_generator_initial_state_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64
PREFIX = r"""
dec $test_config_initial_front(pstate, nat) : bool
def $test_config_initial_front(S, 0) = true
  -- if S.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_config_initial_front(S, 1) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "finish") :: ptask*
def $test_config_initial_front(S, 2) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "invoke") :: ptask*
  -- if ~((HOBJECT pconfiggenerator.OBJECT) <- S.ALLOCATIONS)
def $test_config_initial_front(S, 3) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_option),NAMED_SENT (KNOWN pvalue_value)]
  -- if $string_bytes(pvalue_option) = ($ptascii("precision"))
  -- if $string_bytes(pvalue_value) = ($ptascii("9"))
def $test_config_initial_front(S, n) = false -- otherwise
dec $test_config_initial_seek(pstate, nat, nat) : pstate
def $test_config_initial_seek(S, n_stage, 0) = S
def $test_config_initial_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_config_initial_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ (S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
def $test_config_initial_seek(S, n_stage, n) = $test_config_initial_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_config_initial_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~(S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
dec $test_config_initial_step(pstate) : pstate
def $test_config_initial_step(S) = S_next
  -- PhpStep: S ~> S_next
"""


def reach(state, start, stage):
    return [state + '_found = $test_config_initial_seek(' + start + ',' + str(stage) + ',3000)',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_config_initial_front(' + state + ',' + str(stage) + ')']


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)',
        state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)',
        state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def setup(program, path):
    return ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *reach('S_pre', 'S_initial', 0),
        'S_pre.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*',
        '$intrinsic_argument(S_pre,pconfigcall.SITE,0) = ((expression,true,eps,porigin_argument,z_argument))',
        'S_pre.RESULT = VARIABLE ' + text('generator') + ' z_argument',
        '$lookup(S_pre.ENV,' + text('generator') + ') = (n_generator_cell)',
        'S_pre.STORE[n_generator_cell] = DEFINED (POBJECT n_generator)',
        'S_pre.OBJECTS[n_generator] = GENERATOR pgenerator_initial',
        '$lookup(S_pre.ENV,' + text('watch') + ') = (n_watch_cell)',
        'S_pre.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)',
        '$lookup(S_pre.ENV,' + text('result') + ') = (n_result_cell)']


def checks(program, path, name):
    closed = name == 'closed-generator-config-rejects-before-iterator-data'
    assert closed or name == 'cached-first-generator-config-reuses-value-and-retires-data'
    values = [*setup(program, path), 'S_pre.OBJECTS[n_watch] = WEAKREFERENCE (n_generator)',
        '$node_children(S_pre,HOBJECT n_watch) = eps',
        '$heap_owners($heap_graph(S_pre),HOBJECT n_generator) = 1',
        'S_pre.STORE[n_result_cell] = DEFINED (PINT 99)',
        'pgenerator_initial.PHASE = ' + ('GENERATOR_CLOSED' if closed else 'GENERATOR_PAUSED'),
        'pgenerator_initial.DELEGATE = eps', 'pconfigcall.OWNER = eps',
        '$config_generator_initial(S_pre.RESULT,pgenerator_initial)',
        '~$config_generator_initial(KNOWN (POBJECT n_generator),pgenerator_initial)',
        '~$config_generator_initial(S_pre.RESULT,pgenerator_initial[.PHASE = GENERATOR_RUNNING])',
        '$config_generator_start(S_pre,pconfigcall,S_pre.RESULT,n_generator)',
        '~$config_generator_start(S_pre[.ORIGIN = (porigin_argument)],pconfigcall,S_pre.RESULT,n_generator)',
        '$config_nodes(pconfigcall) = eps', *common.public('S_pre')]
    if closed:
        values += ['pgenerator_initial.FRAME = eps', 'z_argument = 11',
            'S_pre.PRECISIONINI = ' + text('6'),
            '$test_outputs(S_pre.EVENTS) = ' + text('B|Y0|F|C|'),
            'S_raw = $test_config_initial_step(S_pre)',
            'S_raw = S_pre[.COMPLETION = THROWN "Exception" ' + text('Cannot traverse an already closed generator') + ' z_argument]',
            '$heap_owners($heap_graph(S_raw),HOBJECT n_generator) = 1',
            '$task_nodes(CONFIG_UNPACK_PREP pconfigcall) = eps',
            '$config_generator_count(S_raw.TODO,pconfigcall.SITE) = 0',
            '$heap_valid($heap_graph(S_raw))',
            *common.step('S_error', 'S_pre'),
            'S_error.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
            'S_error.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "Exception"',
            'pthrowable.ORIGIN = (pconfigcall.SITE)',
            '$string_bytes($throwable_field(S_error,n_error,"message")) = (' + text('Cannot traverse an already closed generator') + ')',
            '$throwable_field(S_error,n_error,"line") = PINT z_argument',
            '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
            'S_error.ARRAYS[n_trace].ITEMS = eps',
            'S_error.OBJECTS[n_generator] = GENERATOR pgenerator_initial',
            '$heap_owners($heap_graph(S_error),HOBJECT n_generator) = 1',
            '$weakref_get(S_error,n_watch) = POBJECT n_generator',
            'S_error.STORE = S_pre.STORE', 'S_error.EVENTS = S_pre.EVENTS',
            'S_error.PRECISIONINI = S_pre.PRECISIONINI',
            'S_error.ITERATORS = S_pre.ITERATORS', 'S_error.NEXTITER = S_pre.NEXTITER',
            '$config_generator_count(S_error.TODO,pconfigcall.SITE) = 0', *common.public('S_error'),
            *budget('S_pre'), *budget('S_error'), *reach('S_recovery', 'S_error', 3),
            'S_recovery.TODO = (CONFIG_INVOKE pconfigcall_recovery) :: ptask_recovery*',
            'pconfigcall_recovery.OWNER = eps',
            '~((HOBJECT n_generator) <- S_recovery.ALLOCATIONS)',
            '$weakref_get(S_recovery,n_watch) = PNULL',
            'S_recovery.STORE[n_result_cell] = DEFINED (PINT 99)',
            'S_recovery.PRECISIONINI = ' + text('6'), *common.step('S_after', 'S_recovery'),
            'S_after.RESULT = KNOWN pvalue_old', '$string_bytes(pvalue_old) = (' + text('6') + ')',
            'S_after.PRECISIONINI = ' + text('9')]
    else:
        values += ['pgenerator_initial.FIRST', 'pgenerator_initial.FRAME = (pframe_generator)',
            'pgenerator_initial.VALUE = (pvalue_option)',
            '$string_bytes(pvalue_option) = (' + text('precision') + ')',
            'pgenerator_initial.KEY = (PINT 3)',
            '$test_outputs(S_pre.EVENTS) = ' + text('B|C|Y0|precision|U|'),
            'pconfiggenerator = {CALL pconfigcall,OBJECT n_generator,INPUT S_pre.RESULT,ITEMS eps,PRODUCER eps}',
            'S_data = $test_config_initial_step(S_pre)',
            'S_data = S_pre[.ORIGIN = (porigin_argument)][.TODO = (CONFIG_GENERATOR pconfiggenerator "rewind") :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
            '$task_nodes(CONFIG_GENERATOR pconfiggenerator "rewind") = [HOBJECT n_generator]',
            '$heap_owners($heap_graph(S_data),HOBJECT n_generator) = 2',
            'S_ready = $test_config_initial_step(S_data)',
            'S_ready = S_data[.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask_tail*]',
            '$config_generator_valid(S_ready,pconfiggenerator,"ready")',
            'S_item = $test_config_initial_step(S_ready)',
            'pconfiggenerator_first = pconfiggenerator[.ITEMS = [ENTRY (KINT 3) (DIRECT pvalue_option)]]',
            'S_item = S_ready[.TODO = (CONFIG_GENERATOR pconfiggenerator_first "next") :: ptask_tail*]',
            '$heap_owners($heap_graph(S_item),HOBJECT n_generator) = 2', *common.public('S_item'),
            *reach('S_finish', 'S_item', 1),
            'S_finish.TODO = (CONFIG_GENERATOR pconfiggenerator_done "finish") :: ptask_tail*',
            'pconfiggenerator_done = pconfiggenerator[.ITEMS = pconfiggenerator_done.ITEMS]',
            'pconfiggenerator_done.ITEMS = [ENTRY (KINT 3) (DIRECT pvalue_option),ENTRY (KINT 3) (DIRECT pvalue_value)]',
            '$string_bytes(pvalue_value) = (' + text('8') + ')',
            'S_finish.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
            'pgenerator_closed.PHASE = GENERATOR_CLOSED', 'pgenerator_closed.FRAME = eps',
            'S_finish.STORE[n_generator_cell] = DEFINED (PINT 17)',
            'S_finish.STORE[n_result_cell] = DEFINED (PINT 99)',
            'S_finish.PRECISIONINI = ' + text('6'),
            '$test_outputs(S_finish.EVENTS) = ' + text('B|C|Y0|precision|U|Y1|F|'),
            '$heap_owners($heap_graph(S_finish),HOBJECT n_generator) = 1',
            '$weakref_get(S_finish,n_watch) = POBJECT n_generator',
            '$config_generator_quiet_closed(S_finish,pconfiggenerator_done)',
            'S_releasing = $test_config_initial_step(S_finish)',
            'S_releasing = $config_generator_finish(S_finish,pconfiggenerator_done,ptask_tail*)',
            *reach('S_invoke', 'S_finish', 2),
            'S_invoke.TODO = (CONFIG_GENERATOR pconfiggenerator_done "invoke") :: ptask_tail*',
            '$heap_owners($heap_graph(S_invoke),HOBJECT n_generator) = 0',
            '$weakref_get(S_invoke,n_watch) = PNULL',
            '$config_generator_retired_scope(S_invoke,pconfiggenerator_done)',
            '~$config_generator_scope(S_invoke,pconfiggenerator_done)',
            'S_invoke.STORE = S_finish.STORE', 'S_invoke.EVENTS = S_finish.EVENTS',
            *common.public('S_invoke'), *budget('S_data'), *budget('S_invoke'),
            *common.step('S_after', 'S_invoke'), 'S_after.TODO = ptask_tail*',
            'S_after.RESULT = KNOWN pvalue_old', '$string_bytes(pvalue_old) = (' + text('6') + ')',
            'S_after.PRECISIONINI = ' + text('8')]
    values += ['S_final = $drive_steps(S_after,3000)', 'S_final.COMPLETION = NORMAL',
        'S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        '~((HOBJECT n_generator) <- S_final.ALLOCATIONS)', '$weakref_get(S_final,n_watch) = PNULL',
        '$test_outputs(S_final.EVENTS) = ' + text(
            'B|Y0|F|C|E|Exception|Cannot traverse an already closed generator|11|T|99|6|H|D|R|6|9'
            if closed else 'B|C|Y0|precision|U|Y1|F|A|6|8|17|D'), *common.public('S_final')]
    return values


def partition(values, part, closed):
    cut = values.index('$heap_valid($heap_graph(' + ('S_raw' if closed else 'S_item') + '))') + 1
    if part == 'entry':
        return values[:cut]
    pre_end = values.index('$lookup(S_pre.ENV,' + text('result') + ') = (n_result_cell)') + 1
    prefix = values[:pre_end]
    if not closed:
        prefix += ['pconfiggenerator = {CALL pconfigcall,OBJECT n_generator,INPUT S_pre.RESULT,ITEMS eps,PRODUCER eps}',
            'S_data = $test_config_initial_step(S_pre)', 'S_ready = $test_config_initial_step(S_data)',
            'S_item = $test_config_initial_step(S_ready)']
    return prefix + values[cut:]


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    cases = dict(sources.family.CASES)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['prepare', 'check'], required=True)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--part', choices=['entry', 'completion', 'all'], default='all')
    parser.add_argument('--case', action='append', default=[])
    args = parser.parse_args()
    selected = args.case or list(cases)
    assert len(selected) == len(set(selected)) and set(selected) <= cases.keys()
    driver.sources, driver.PREFIX = sources, PREFIX
    for name in selected:
        case = cases[name]
        sources.family.CASES = {name: case}
        for part in (['entry', 'completion'] if args.part == 'all' else [args.part]):
            driver.checks = lambda program, path, name: partition(checks(program, path, name), part,
                name == 'closed-generator-config-rejects-before-iterator-data')
            sys.argv = [sys.argv[0], '--phase', args.phase, '--sources', str(args.sources),
                '--output', str(args.output / name / part)]
            driver.main()


if __name__ == '__main__':
    main()
