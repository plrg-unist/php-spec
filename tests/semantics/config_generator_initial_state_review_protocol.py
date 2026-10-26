#!/usr/bin/env python3
"""Native rewind error precedes invalid current and preserves the paused owner."""
import argparse
import json
import os
import sys
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import config_generator_initial_state_review_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64
PREFIX = r"""
dec $test_config_advanced_front(pstate, nat) : bool
def $test_config_advanced_front(S, 0) = true
  -- if S.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_config_advanced_front(S, 1) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_GENERATOR pconfiggenerator "rewind") :: ptask*
def $test_config_advanced_front(S, 2) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask*
  -- if ~$test_config_advanced_front(S,1)
  -- if S.DESTRUCTION.OPERATIONS = eps
def $test_config_advanced_front(S, 3) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_option),NAMED_SENT (KNOWN pvalue_value)]
  -- if $string_bytes(pvalue_option) = ($ptascii("precision"))
  -- if $string_bytes(pvalue_value) = ($ptascii("9"))
def $test_config_advanced_front(S, n) = false -- otherwise
dec $test_config_advanced_seek(pstate, nat, nat) : pstate
def $test_config_advanced_seek(S, n_stage, 0) = S
def $test_config_advanced_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_config_advanced_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ (S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
def $test_config_advanced_seek(S, n_stage, n) = $test_config_advanced_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_config_advanced_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~(S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
dec $test_config_advanced_step(pstate) : pstate
def $test_config_advanced_step(S) = S_next
  -- PhpStep: S ~> S_next
"""


def reach(state, start, stage):
    return [state + '_found = $test_config_advanced_seek(' + start + ',' + str(stage) + ',3000)',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_config_advanced_front(' + state + ',' + str(stage) + ')']


def owners(state, generator, callee):
    return ['$heap_owners($heap_graph(' + state + '),HOBJECT ' + node + ') = ' + str(count)
        for node, count in [('n_generator', generator), ('n_owner', callee)]]


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)',
        state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)',
        state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def setup(program, path):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *reach('S_pre', 'S_initial', 0),
        'S_pre.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*',
        'pconfigcall.OWNER = (n_owner)',
        '$intrinsic_argument(S_pre,pconfigcall.SITE,0) = ((expression,true,eps,porigin_argument,z_argument))',
        'S_pre.RESULT = VARIABLE ' + text('generator') + ' z_argument']
    for variable, cell in [('generator', 'n_generator_cell'), ('watch', 'n_watch_cell'),
            ('result', 'n_result_cell'), ('effects', 'n_effects_cell')]:
        values += ['$lookup(S_pre.ENV,' + text(variable) + ') = (' + cell + ')']
    return values + ['S_pre.STORE[n_generator_cell] = DEFINED (POBJECT n_generator)',
        'S_pre.OBJECTS[n_generator] = GENERATOR pgenerator_initial',
        'S_pre.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)']


def checks(program, path, name):
    assert name == 'advanced-config-generator-rewind-error-precedes-current-send'
    values = [*setup(program, path), 'pconfigcall.LINE = 13', 'z_argument = 14',
        'pgenerator_initial.PHASE = GENERATOR_PAUSED', '~pgenerator_initial.FIRST',
        'pgenerator_initial.DELEGATE = eps', 'pgenerator_initial.FRAME = (pframe_paused)',
        'pgenerator_initial.VALUE = (PINT 17)', 'pgenerator_initial.KEY = (PINT 3)',
        'S_pre.OBJECTS[n_watch] = WEAKREFERENCE (n_generator)',
        '$node_children(S_pre,HOBJECT n_watch) = eps',
        'S_pre.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_pre.STORE[n_effects_cell] = DEFINED (PINT 2)',
        'S_pre.PRECISIONINI = ' + text('6'),
        '$test_outputs(S_pre.EVENTS) = ' + text('Y0|Y1|B|'),
        '$config_generator_start(S_pre,pconfigcall,S_pre.RESULT,n_generator)',
        *owners('S_pre', 1, 3), *common.public('S_pre'),
        'pconfiggenerator = {CALL pconfigcall,OBJECT n_generator,INPUT S_pre.RESULT,ITEMS eps,PRODUCER eps}',
        'S_data = $test_config_advanced_step(S_pre)',
        'S_data = S_pre[.ORIGIN = (porigin_argument)][.TODO = (CONFIG_GENERATOR pconfiggenerator "rewind") :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$task_nodes(CONFIG_GENERATOR pconfiggenerator "rewind") = [HOBJECT n_generator,HOBJECT n_owner]',
        '~$config_generator_send_allowed(S_data,pconfiggenerator)',
        'pgeneratorop = {OBJECT n_generator,NAME "rewind",SITE porigin_argument,LINE z_argument,LOOP eps,ADVANCE false,ARGUMENTS eps,STARTPACK true,BORROWED true}',
        '$config_generator_header(S_data,pgeneratorop,pconfiggenerator,"rewind")',
        '$generator_operation_trace(S_data,pgeneratorop) = eps',
        *owners('S_data', 2, 3), *common.public('S_data'),
        'S_raw = $test_config_advanced_step(S_data)',
        'S_raw = $config_generator_run(S_data,pconfiggenerator,"rewind",ptask_tail*)',
        'S_raw.COMPLETION = THROWING n_error',
        'S_raw.OBJECTS[n_generator] = GENERATOR pgenerator_initial',
        'S_raw.TODO = S_data.TODO',
        '$throwable_field(S_raw,n_error,"trace") = PARRAY n_trace',
        'S_raw.ARRAYS[n_trace].ITEMS = eps',
        '$heap_valid($heap_graph(S_raw))',
        *common.step('S_error', 'S_data'),
        'S_error.TODO = (THROW_SEARCH n_error) :: (CONFIG_GENERATOR pconfiggenerator "rewind") :: ptask_tail*',
        'S_error.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "Exception"',
        'pthrowable.ORIGIN = (porigin_argument)',
        '$string_bytes($throwable_field(S_error,n_error,"message")) = (' + text('Cannot rewind a generator that was already run') + ')',
        '$throwable_field(S_error,n_error,"line") = PINT z_argument',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
        'S_error.ARRAYS[n_trace].ITEMS = eps',
        'S_error.OBJECTS[n_generator] = GENERATOR pgenerator_initial',
        'S_error.STORE = S_pre.STORE', 'S_error.EVENTS = S_pre.EVENTS',
        'S_error.PRECISIONINI = S_pre.PRECISIONINI',
        'S_error.CURRENT = eps', 'S_error.FRAMES = eps',
        '$weakref_get(S_error,n_watch) = POBJECT n_generator',
        *owners('S_error', 2, 3), *common.public('S_error'),
        'S_no_cv = S_error[.STORE[n_generator_cell] = DEFINED PNULL]',
        '$heap_owners($heap_graph(S_no_cv),HOBJECT n_generator) = 1',
        'S_stopped = $test_config_advanced_step(S_no_cv)',
        'S_stopped = S_no_cv[.COMPLETION = UNSUPPORTED "CONFIG Generator unpack last cleanup owner"]',
        '$drive_steps(S_stopped,4) = S_stopped',
        '$weakref_get(S_stopped,n_watch) = POBJECT n_generator',
        'S_after_data = $test_config_advanced_step(S_error)',
        'S_after_data = $config_generator_discard(S_error[.TODO = (THROW_SEARCH n_error) :: ptask_tail*],pconfiggenerator,"rewind")',
        *reach('S_disposed', 'S_error', 2),
        'S_disposed.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
        'S_disposed.OBJECTS[n_generator] = GENERATOR pgenerator_initial',
        '$weakref_get(S_disposed,n_watch) = POBJECT n_generator',
        '$throwable_live(S_disposed,n_error)',
        '$throwable_field(S_disposed,n_error,"trace") = PARRAY n_trace',
        'S_disposed.ARRAYS = S_error.ARRAYS', 'S_disposed.STORE = S_pre.STORE',
        'S_disposed.EVENTS = S_pre.EVENTS', 'S_disposed.PRECISIONINI = ' + text('6'),
        '$config_generator_count(S_disposed.TODO,pconfigcall.SITE) = 0',
        *owners('S_disposed', 1, 2), *common.public('S_disposed'),
        *budget('S_error'), *reach('S_recovery', 'S_disposed', 3),
        'S_recovery.TODO = (CONFIG_INVOKE pconfigcall_recovery) :: ptask_recovery*',
        'pconfigcall_recovery.OWNER = (n_owner)',
        '$lookup(S_recovery.ENV,' + text('e') + ') = (n_caught_cell)',
        'S_recovery.STORE[n_caught_cell] = DEFINED (POBJECT n_error)',
        'S_recovery.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_recovery.STORE[n_effects_cell] = DEFINED (PINT 3)',
        '~((HOBJECT n_generator) <- S_recovery.ALLOCATIONS)',
        '$weakref_get(S_recovery,n_watch) = PNULL',
        'S_recovery.PRECISIONINI = ' + text('6'),
        *owners('S_recovery', 0, 3), *common.public('S_recovery'),
        *common.step('S_after', 'S_recovery'),
        'S_after.RESULT = KNOWN pvalue_old', '$string_bytes(pvalue_old) = (' + text('6') + ')',
        'S_after.PRECISIONINI = ' + text('9'), *owners('S_after', 0, 2), *common.public('S_after'),
        'S_final = $drive_steps(S_after,3000)', 'S_final.COMPLETION = NORMAL',
        'S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        '$test_outputs(S_final.EVENTS) = ' + text('Y0|Y1|B|X|Cannot rewind a generator that was already run|14|99|2|6|17|N|H|F|D|R|6|9|99|3'),
        *common.public('S_final')]
    return values


def partition(values, part):
    cut = values.index('$heap_valid($heap_graph(S_error))') + 1
    if part == 'entry':
        return values[:cut]
    prefix = values[:values.index('pconfigcall.LINE = 13')]
    prefix += ['pconfiggenerator = {CALL pconfigcall,OBJECT n_generator,INPUT S_pre.RESULT,ITEMS eps,PRODUCER eps}',
        'S_data = $test_config_advanced_step(S_pre)', *common.step('S_error', 'S_data'),
        'S_error.TODO = (THROW_SEARCH n_error) :: (CONFIG_GENERATOR pconfiggenerator "rewind") :: ptask_tail*',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace']
    return prefix + values[cut:]


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
