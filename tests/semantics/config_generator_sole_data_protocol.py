#!/usr/bin/env python3
"""Sole DATA retires before historical CONFIG success or API arity failure."""
import argparse
import json
import os
import sys
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import config_generator_sole_data_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64
PREFIX = r"""
dec $test_config_sole_front(pstate, nat) : bool
def $test_config_sole_front(S, 0) = true
  -- if S.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_config_sole_front(S, 1) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "finish") :: ptask*
def $test_config_sole_front(S, 2) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "invoke") :: ptask*
  -- if ~((HOBJECT pconfiggenerator.OBJECT) <- S.ALLOCATIONS)
def $test_config_sole_front(S, 3) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_option),NAMED_SENT (KNOWN pvalue_value)]
  -- if $string_bytes(pvalue_option) = ($ptascii("precision"))
  -- if $string_bytes(pvalue_value) = ($ptascii("9"))
def $test_config_sole_front(S, n) = false -- otherwise
dec $test_config_sole_seek(pstate, nat, nat) : pstate
def $test_config_sole_seek(S, n_stage, 0) = S
def $test_config_sole_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_config_sole_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ (S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
def $test_config_sole_seek(S, n_stage, n) = $test_config_sole_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_config_sole_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~(S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
dec $test_config_sole_step(pstate) : pstate
def $test_config_sole_step(S) = S_next
  -- PhpStep: S ~> S_next
"""


def reach(state, start, stage):
    return [state + '_found = $test_config_sole_seek(' + start + ',' + str(stage) + ',3000)',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_config_sole_front(' + state + ',' + str(stage) + ')']


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)',
        state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)',
        state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def checks(program, path, name):
    owned = name == 'sole-data-config-generator-retires-before-owned-arity-error'
    assert owned or name == 'sole-data-config-generator-retires-before-normal-api'
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *reach('S_pre', 'S_initial', 0),
        'S_pre.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*',
        '$intrinsic_argument(S_pre,pconfigcall.SITE,0) = ((expression,true,eps,porigin_argument,z_argument))',
        'S_pre.RESULT = VARIABLE ' + text('generator') + ' z_argument',
        '$lookup(S_pre.ENV,' + text('generator') + ') = (n_generator_cell)',
        'S_pre.STORE[n_generator_cell] = DEFINED (POBJECT n_generator)',
        '$lookup(S_pre.ENV,' + text('watch') + ') = (n_watch_cell)',
        'S_pre.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)',
        'S_pre.OBJECTS[n_watch] = WEAKREFERENCE (n_generator)',
        '$node_children(S_pre,HOBJECT n_watch) = eps',
        '$heap_owners($heap_graph(S_pre),HOBJECT n_generator) = 1',
        '$lookup(S_pre.ENV,' + text('result') + ') = (n_result_cell)',
        'S_pre.STORE[n_result_cell] = DEFINED (PINT 99)',
        '$config_generator_start(S_pre,pconfigcall,S_pre.RESULT,n_generator)',
        *common.public('S_pre'),
        *reach('S_finish', 'S_pre', 1),
        'S_finish.TODO = (CONFIG_GENERATOR pconfiggenerator "finish") :: ptask_tail*',
        'pconfiggenerator.CALL = pconfigcall', 'pconfiggenerator.OBJECT = n_generator',
        'pconfiggenerator.INPUT = S_pre.RESULT',
        'pconfiggenerator.ITEMS = [ENTRY (KINT 3) (DIRECT pvalue_option)]' if owned else
        'pconfiggenerator.ITEMS = [ENTRY (KINT 3) (DIRECT pvalue_option),ENTRY (KINT 3) (DIRECT pvalue_value)]',
        '$string_bytes(pvalue_option) = (' + text('precision') + ')',
        'S_finish.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
        'pgenerator_closed.PHASE = GENERATOR_CLOSED', 'pgenerator_closed.FRAME = eps',
        'S_finish.STORE[n_generator_cell] = DEFINED (PINT 17)',
        'S_finish.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_finish.PRECISIONINI = ' + text('7' if owned else '14'),
        '$test_outputs(S_finish.EVENTS) = ' + text('B|Y0|F|' if owned else 'B|Y0|Y1|F|'),
        '$heap_owners($heap_graph(S_finish),HOBJECT n_generator) = 1',
        '$weakref_get(S_finish,n_watch) = POBJECT n_generator',
        '$node_children(S_finish,HOBJECT n_generator) = eps',
        '$config_generator_scope(S_finish,pconfiggenerator)',
        '$config_generator_quiet_closed(S_finish,pconfiggenerator)',
        '$config_generator_finish_allowed(S_finish,pconfiggenerator)',
        *common.public('S_finish')]
    values += ['S_releasing = $test_config_sole_step(S_finish)',
        'S_releasing = $config_generator_finish(S_finish,pconfiggenerator,ptask_tail*)',
        *reach('S_invoke', 'S_finish', 2),
        'S_invoke.TODO = (CONFIG_GENERATOR pconfiggenerator "invoke") :: ptask_tail*',
        '~((HOBJECT n_generator) <- S_invoke.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_invoke),HOBJECT n_generator) = 0',
        '$weakref_get(S_invoke,n_watch) = PNULL',
        'S_invoke.OBJECTS[n_generator] = GENERATOR pgenerator_retired',
        'pgenerator_retired.FUNCTION = pgenerator_closed.FUNCTION',
        'pgenerator_retired.PHASE = GENERATOR_CLOSED',
        'S_invoke.STORE = S_finish.STORE', 'S_invoke.EVENTS = S_finish.EVENTS',
        'S_invoke.ARRAYS = S_finish.ARRAYS',
        'S_invoke.ITERATORS = S_pre.ITERATORS', 'S_invoke.NEXTITER = S_pre.NEXTITER',
        '$task_nodes(CONFIG_GENERATOR pconfiggenerator "invoke") = ' + ('[HOBJECT n_owner]' if owned else 'eps'),
        '$config_generator_history(S_invoke,pconfiggenerator)',
        '$config_generator_retired_scope(S_invoke,pconfiggenerator)',
        '~$config_generator_scope(S_invoke,pconfiggenerator)',
        '$config_generator_valid(S_invoke,pconfiggenerator,"invoke")',
        '~$config_generator_valid(S_invoke,pconfiggenerator,"ready")',
        '~$config_generator_valid(S_invoke,pconfiggenerator,"next")',
        *common.public('S_invoke'),
        '~$config_generator_retired_scope(S_invoke[.CODE = eps],pconfiggenerator)',
        '~$config_generator_retired_scope(S_invoke,pconfiggenerator[.INPUT = KNOWN (POBJECT n_generator)])',
        '~$config_generator_valid(S_invoke[.ORIGIN = (porigin_argument)],pconfiggenerator,"invoke")',
        'S_dead_paused = S_invoke[.OBJECTS[n_generator] = GENERATOR pgenerator_retired[.PHASE = GENERATOR_PAUSED]]',
        '~$config_generator_retired_scope(S_dead_paused,pconfiggenerator)',
        'S_owning = S_finish[.OBJECTS[n_generator] = GENERATOR pgenerator_closed[.RETURN = (POBJECT n_watch)]]',
        '$heap_valid($heap_graph(S_owning))',
        '$node_children(S_owning,HOBJECT n_generator) = [HOBJECT n_watch]',
        '~$config_generator_quiet_closed(S_owning,pconfiggenerator)',
        'S_owning_stopped = $test_config_sole_step(S_owning)',
        'S_owning_stopped = S_owning[.COMPLETION = UNSUPPORTED "CONFIG Generator unpack last DATA or callee owner"]',
        '$drive_steps(S_owning_stopped,4) = S_owning_stopped',
        '$weakref_get(S_owning_stopped,n_watch) = POBJECT n_generator']
    if owned:
        values += ['pconfigcall.OWNER = (n_owner)',
            '$lookup(S_pre.ENV,' + text('call') + ') = (n_call_cell)',
            '$lookup(S_pre.ENV,' + text('keep') + ') = (n_keep_cell)',
            'S_finish.STORE[n_call_cell] = DEFINED (POBJECT n_getter)',
            'S_finish.OBJECTS[n_getter] = INTRINSICCLOSURE INTRINSIC_INI_GET',
            '$heap_owners($heap_graph(S_finish),HOBJECT n_owner) = 2',
            'S_last_callee = S_finish[.STORE[n_keep_cell] = DEFINED PNULL]',
            '$heap_owners($heap_graph(S_last_callee),HOBJECT n_owner) = 1',
            'S_callee_stopped = $test_config_sole_step(S_last_callee)',
            'S_callee_stopped = S_last_callee[.COMPLETION = UNSUPPORTED "CONFIG Generator unpack last DATA or callee owner"]',
            '$weakref_get(S_callee_stopped,n_watch) = POBJECT n_generator',
            *common.step('S_error', 'S_invoke'),
            'S_error.TODO = (THROW_SEARCH n_error) :: (CONFIG_GENERATOR pconfiggenerator "invoke") :: ptask_tail*',
            'S_error.OBJECTS[n_error] = THROWABLE pthrowable',
            'pthrowable.KIND = "ArgumentCountError"',
            '$string_bytes($throwable_field(S_error,n_error,"message")) = (' + text('ini_set() expects exactly 2 arguments, 1 given') + ')',
            '$throwable_field(S_error,n_error,"line") = PINT 12',
            '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
            'S_error.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_api)),ENTRY (KINT 1) (DIRECT (PARRAY n_wrapper))]',
            '$trace_array_field(S_error,n_api,' + text('function') + ') = PSTRING ' + text('ini_set'),
            '$trace_array_field(S_error,n_api,' + text('args') + ') = PARRAY n_api_args',
            'S_error.ARRAYS[n_api_args].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_option)]',
            '$trace_array_field(S_error,n_wrapper,' + text('function') + ') = PSTRING ' + text('__invoke'),
            '$trace_array_field(S_error,n_wrapper,' + text('args') + ') = PARRAY n_wrapper_args',
            'S_error.ARRAYS[n_wrapper_args].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_option)]',
            '$weakref_get(S_error,n_watch) = PNULL',
            *common.public('S_error'), *reach('S_recovery', 'S_error', 3),
            'S_recovery.TODO = (CONFIG_INVOKE pconfigcall_recovery) :: ptask_recovery*',
            'pconfigcall_recovery.OWNER = (n_owner)',
            '$config_generator_count(S_recovery.TODO,pconfigcall.SITE) = 0',
            '$heap_owners($heap_graph(S_recovery),HOBJECT n_owner) = 2',
            'S_recovery.STORE[n_result_cell] = DEFINED (PINT 99)',
            '$weakref_get(S_recovery,n_watch) = PNULL',
            'S_recovery.PRECISIONINI = ' + text('7'),
            *common.step('S_after', 'S_recovery'),
            'S_after.RESULT = KNOWN pvalue_old',
            '$string_bytes(pvalue_old) = (' + text('7') + ')',
            'S_after.PRECISIONINI = ' + text('9')]
    else:
        values += ['pconfigcall.OWNER = eps',
            '$string_bytes(pvalue_value) = (' + text('8') + ')',
            *common.step('S_after', 'S_invoke'),
            'S_after.TODO = ptask_tail*', 'S_after.RESULT = KNOWN pvalue_old',
            '$string_bytes(pvalue_old) = (' + text('14') + ')',
            'S_after.PRECISIONINI = ' + text('8')]
    values += [*budget('S_finish'), *budget('S_invoke'),
        'S_final = $drive_steps(S_after,3000)', 'S_final.COMPLETION = NORMAL',
        'S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        '~((HOBJECT n_generator) <- S_final.ALLOCATIONS)',
        '$weakref_get(S_final,n_watch) = PNULL',
        '$test_outputs(S_final.EVENTS) = ' + text(
            'B|Y0|F|C|ini_set() expects exactly 2 arguments, 1 given|12|ini_set|precision|W|__invoke|precision|99|7|17|D|L|7|R|7|9|99'
            if owned else 'B|Y0|Y1|F|A|14|8|17|D|E'),
        *common.public('S_final')]
    return values


def partition(values, part, owned):
    cut = values.index('$heap_valid($heap_graph(S_finish))') + 1
    if part == 'entry':
        return values[:cut]
    setup = [values[0], values[1], *reach('S_pre', 'S_initial', 0),
        'S_pre.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*',
        '$intrinsic_argument(S_pre,pconfigcall.SITE,0) = ((expression,true,eps,porigin_argument,z_argument))',
        '$lookup(S_pre.ENV,' + text('watch') + ') = (n_watch_cell)',
        'S_pre.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)',
        'S_pre.OBJECTS[n_watch] = WEAKREFERENCE (n_generator)',
        '$lookup(S_pre.ENV,' + text('result') + ') = (n_result_cell)',
        *reach('S_finish', 'S_pre', 1),
        'S_finish.TODO = (CONFIG_GENERATOR pconfiggenerator "finish") :: ptask_tail*',
        'S_finish.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
        'pconfiggenerator.ITEMS = (ENTRY (KINT 3) (DIRECT pvalue_option)) :: pentry_tail*']
    if not owned:
        setup += ['pentry_tail* = [ENTRY (KINT 3) (DIRECT pvalue_value)]']
    return setup + values[cut:]


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
                name == 'sole-data-config-generator-retires-before-owned-arity-error')
            sys.argv = [sys.argv[0], '--phase', args.phase, '--sources', str(args.sources),
                '--output', str(args.output / name / part)]
            driver.main()


if __name__ == '__main__':
    main()
