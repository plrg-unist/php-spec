#!/usr/bin/env python3
"""Terminal native Generator resume keeps both sends pending until throw cleanup."""
import argparse
import json
import os
import sys
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import config_generator_unpack_review_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64
PREFIX = r"""
dec $test_config_generator_peer_front(pstate, nat) : bool
def $test_config_generator_peer_front(S, 0) = true
  -- if S.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_config_generator_peer_front(S, 1) = true
  -- if S.TODO = (THROW_VALUE porigin z) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (GENERATOR_RESUME pgeneratorop) :: (CONFIG_GENERATOR pconfiggenerator "next") :: ptask_caller*
def $test_config_generator_peer_front(S, 2) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_GENERATOR pconfiggenerator "next") :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $test_config_generator_peer_front(S, 3) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_option),NAMED_SENT (KNOWN pvalue_value)]
  -- if $string_bytes(pvalue_option) = ($ptascii("precision"))
  -- if $string_bytes(pvalue_value) = ($ptascii("9"))
def $test_config_generator_peer_front(S, 4) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if S.DESTRUCTION.OPERATIONS = eps
def $test_config_generator_peer_front(S, n) = false -- otherwise
dec $test_config_generator_peer_seek(pstate, nat, nat) : pstate
def $test_config_generator_peer_seek(S, n_stage, 0) = S
def $test_config_generator_peer_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_config_generator_peer_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ (S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
def $test_config_generator_peer_seek(S, n_stage, n) = $test_config_generator_peer_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_config_generator_peer_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~(S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
dec $test_config_generator_peer_step(pstate) : pstate
def $test_config_generator_peer_step(S) = S_next
  -- PhpStep: S ~> S_next
"""


def reach(state, start, stage):
    return [state + '_found = $test_config_generator_peer_seek(' + start + ',' + str(stage) + ',3000)',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_config_generator_peer_front(' + state + ',' + str(stage) + ')']


def owners(state, generator, callee):
    return ['$heap_owners($heap_graph(' + state + '),HOBJECT ' + node + ') = ' + str(count)
        for node, count in [('n_generator', generator), ('n_owner', callee)]]


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)',
        state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)',
        state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def checks(program, path, name):
    assert name == 'retained-config-generator-terminal-throw-cancels-api'
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *reach('S_pre', 'S_initial', 0),
        'S_pre.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*',
        'pconfigcall.OWNER = (n_owner)',
        '$intrinsic_argument(S_pre,pconfigcall.SITE,0) = ((expression,true,eps,porigin_argument,z_argument))',
        'pconfigcall.LINE = 14', 'z_argument = 15',
        'S_pre.RESULT = VARIABLE ' + text('generator') + ' z_argument']
    for name, cell in [('generator', 'n_generator_cell'), ('generatorHold', 'n_generator_hold'),
            ('call', 'n_call_cell'), ('keep', 'n_keep_cell'), ('saved', 'n_saved_cell'),
            ('result', 'n_result_cell'), ('effects', 'n_effects_cell')]:
        values += ['$lookup(S_pre.ENV,' + text(name) + ') = (' + cell + ')']
    values += ['S_pre.STORE[n_generator_cell] = DEFINED (POBJECT n_generator)',
        'S_pre.OBJECTS[n_generator] = GENERATOR pgenerator_initial',
        'pgenerator_initial.PHASE = GENERATOR_FRESH',
        '$config_generator_start(S_pre,pconfigcall,S_pre.RESULT,n_generator)',
        *owners('S_pre', 2, 3), *common.public('S_pre'),
        'S_data = $test_config_generator_peer_step(S_pre)',
        'S_data.TODO = (CONFIG_GENERATOR pconfiggenerator_initial text_initial) :: ptask_tail*',
        'text_initial = "rewind"',
        'pconfiggenerator_initial = {CALL pconfigcall,OBJECT n_generator,INPUT S_pre.RESULT,ITEMS eps}',
        '$task_nodes(CONFIG_GENERATOR pconfiggenerator_initial text_initial) = [HOBJECT n_generator,HOBJECT n_owner]',
        'S_data.RESULT = KNOWN PNULL', 'S_data.STORE = S_pre.STORE',
        'S_data.OBJECTS = S_pre.OBJECTS', 'S_data.ARRAYS = S_pre.ARRAYS',
        'S_data.ITERATORS = S_pre.ITERATORS', 'S_data.NEXTITER = S_pre.NEXTITER',
        *owners('S_data', 3, 3), *common.public('S_data'),
        *reach('S_throw', 'S_data', 1),
        'S_throw.CURRENT = (pcallcontext)',
        'pcallcontext.FUNCTION = pgenerator_initial.FUNCTION',
        'pcallcontext.TARGET = pgenerator_initial.FUNCTION',
        'S_throw.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (GENERATOR_RESUME pgeneratorop) :: (CONFIG_GENERATOR pconfiggenerator "next") :: ptask_tail*',
        'pgeneratorop = {OBJECT n_generator,NAME "next",SITE porigin_argument,LINE z_argument,LOOP eps,ADVANCE false,ARGUMENTS eps,STARTPACK true,BORROWED true}',
        '$generator_operation_valid(S_throw,pgeneratorop)',
        '$generator_operation_nodes(pgeneratorop) = eps',
        '$generator_operation_trace(S_throw,pgeneratorop) = eps',
        'pgeneratorop_bad = pgeneratorop[.SITE = pconfigcall.SITE]',
        'pframe_bad = pframe[.TODO = (GENERATOR_RESUME pgeneratorop_bad) :: (CONFIG_GENERATOR pconfiggenerator "next") :: ptask_tail*]',
        '~$generator_operation_valid(S_throw[.FRAMES = pframe_bad :: pframe_tail*],pgeneratorop_bad)',
        'pconfiggenerator.CALL = pconfigcall', 'pconfiggenerator.OBJECT = n_generator',
        'pconfiggenerator.INPUT = S_pre.RESULT',
        'pconfiggenerator.ITEMS = [ENTRY (KINT 3) (DIRECT pvalue_option),ENTRY (KINT 3) (DIRECT pvalue_value)]',
        '$string_bytes(pvalue_option) = (' + text('precision') + ')',
        '$string_bytes(pvalue_value) = (' + text('11') + ')',
        'S_throw.STORE[n_saved_cell] = DEFINED (POBJECT n_exception)',
        '$throwable_live(S_throw,n_exception)',
        '$string_bytes($throwable_field(S_throw,n_exception,"message")) = (' + text('config-generator-after-sends90') + ')',
        '$throwable_field(S_throw,n_exception,"trace") = PARRAY n_trace',
        'S_throw.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_frame))]',
        '$trace_array_field(S_throw,n_frame,' + text('function') + ') = PSTRING ' + text('configGeneratorThrowReview90'),
        '$trace_array_field(S_throw,n_frame,' + text('line') + ') = PINT z_argument',
        '$trace_array_field(S_throw,n_frame,' + text('args') + ') = PARRAY n_args',
        'S_throw.ARRAYS[n_args].ITEMS = eps',
        'S_throw.STORE[n_call_cell] = DEFINED (POBJECT n_getter)',
        'S_throw.OBJECTS[n_getter] = INTRINSICCLOSURE INTRINSIC_INI_GET',
        'n_getter =/= n_owner', 'S_throw.PRECISIONINI = ' + text('6'),
        'S_throw.STORE[n_effects_cell] = DEFINED (PINT 3)',
        'S_throw.STORE[n_result_cell] = DEFINED (PINT 99)',
        '$test_outputs(S_throw.EVENTS) = ' + text('B|Y0|Y1|T|'),
        'S_throw.ITERATORS = S_pre.ITERATORS', 'S_throw.NEXTITER = S_pre.NEXTITER',
        *owners('S_throw', 3, 2), *common.public('S_throw'),
        *reach('S_thrown', 'S_throw', 2),
        'S_thrown.TODO = (THROW_SEARCH n_exception) :: (CONFIG_GENERATOR pconfiggenerator "next") :: ptask_tail*',
        '$config_generator_valid(S_thrown,pconfiggenerator,"next")',
        'S_thrown.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
        'pgenerator_closed.PHASE = GENERATOR_CLOSED', 'pgenerator_closed.FRAME = eps',
        'S_thrown.STORE[n_saved_cell] = DEFINED (POBJECT n_exception)',
        'S_thrown.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_thrown.PRECISIONINI = ' + text('6'),
        'S_thrown.ITERATORS = S_pre.ITERATORS', 'S_thrown.NEXTITER = S_pre.NEXTITER',
        *owners('S_thrown', 3, 2), *common.public('S_thrown')]
    for label, update in [('line', '.LINE = $(pconfigcall.LINE + 1)'),
            ('owner', '.OWNER = (n_generator)')]:
        call, state = 'pconfigcall_bad_' + label, 'S_bad_' + label
        values += [call + ' = pconfigcall[' + update + ']',
            state + ' = S_pre[.TODO = (CONFIG_UNPACK_PREP ' + call + ') :: ptask_tail*][.ORIGIN = (' + call + '.SITE)]',
            '~$config_generator_start(' + state + ',' + call + ',' + state + '.RESULT,n_generator)']
    values += ['S_bad_origin = S_pre[.ORIGIN = (porigin_argument)]',
        '~$config_generator_start(S_bad_origin,pconfigcall,S_bad_origin.RESULT,n_generator)',
        'S_last_data = S_thrown[.STORE[n_generator_cell] = DEFINED PNULL][.STORE[n_generator_hold] = DEFINED PNULL]',
        '$heap_owners($heap_graph(S_last_data),HOBJECT n_generator) = 1',
        'S_data_stopped = $test_config_generator_peer_step(S_last_data)',
        'S_data_stopped = S_last_data[.COMPLETION = UNSUPPORTED "CONFIG Generator unpack last cleanup owner"]',
        'S_last_callee = S_thrown[.STORE[n_keep_cell] = DEFINED PNULL]',
        '$heap_owners($heap_graph(S_last_callee),HOBJECT n_owner) = 1',
        'S_callee_stopped = $test_config_generator_peer_step(S_last_callee)',
        'S_callee_stopped = S_last_callee[.COMPLETION = UNSUPPORTED "CONFIG Generator unpack last cleanup owner"]',
        '$drive_steps(S_callee_stopped,4) = S_callee_stopped',
        '$throwable_live(S_callee_stopped,n_exception)',
        'S_after = $test_config_generator_peer_step(S_thrown)',
        'S_after = $config_generator_discard(S_thrown[.TODO = (THROW_SEARCH n_exception) :: ptask_tail*],pconfiggenerator,"next")',
        *reach('S_disposed', 'S_after', 4),
        'S_disposed.TODO = (THROW_SEARCH n_exception) :: ptask_tail*',
        '$throwable_live(S_disposed,n_exception)',
        '$throwable_field(S_disposed,n_exception,"previous") = PNULL',
        'S_disposed.STORE = S_thrown.STORE', 'S_disposed.OBJECTS = S_thrown.OBJECTS',
        'S_disposed.ARRAYS = S_thrown.ARRAYS',
        'S_disposed.ITERATORS = S_pre.ITERATORS', 'S_disposed.NEXTITER = S_pre.NEXTITER',
        *owners('S_disposed', 2, 1), *common.public('S_disposed'),
        *budget('S_pre'), *budget('S_thrown'),
        *reach('S_recovery', 'S_disposed', 3),
        'S_recovery.TODO = (CONFIG_INVOKE pconfigcall_recovery) :: ptask_recovery*',
        'pconfigcall_recovery.OWNER = (n_owner)',
        '$lookup(S_recovery.ENV,' + text('e') + ') = (n_caught_cell)',
        'S_recovery.STORE[n_caught_cell] = DEFINED (POBJECT n_exception)',
        'S_recovery.STORE[n_saved_cell] = DEFINED (POBJECT n_exception)',
        'S_recovery.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_recovery.PRECISIONINI = ' + text('6'),
        *owners('S_recovery', 2, 2), *common.public('S_recovery'),
        *common.step('S_recovered', 'S_recovery'),
        'S_recovered.RESULT = KNOWN pvalue_old',
        '$string_bytes(pvalue_old) = (' + text('6') + ')',
        'S_recovered.PRECISIONINI = ' + text('9'),
        *owners('S_recovered', 2, 1), *common.public('S_recovered'),
        'S_final = $drive_steps(S_recovered,3000)', 'S_final.COMPLETION = NORMAL',
        'S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.ITERATORS = S_pre.ITERATORS', 'S_final.NEXTITER = S_pre.NEXTITER',
        '$test_outputs(S_final.EVENTS) = ' + text('B|Y0|Y1|T|I|99|3|6|configGeneratorThrowReview90|15|A|F|Z|L|6|R|6|9|99'),
        *common.public('S_final')]
    return values


def partition(values, part):
    cut = values.index('$heap_valid($heap_graph(S_thrown))') + 1
    if part == 'entry':
        return values[:cut]
    # Recompute the real terminal throw; these bindings add no coverage credit.
    setup = [values[0], values[1], *reach('S_pre', 'S_initial', 0),
        'S_pre.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*',
        'pconfigcall.OWNER = (n_owner)',
        '$intrinsic_argument(S_pre,pconfigcall.SITE,0) = ((expression,true,eps,porigin_argument,z_argument))']
    for name, cell in [('generator', 'n_generator_cell'), ('generatorHold', 'n_generator_hold'),
            ('keep', 'n_keep_cell'), ('saved', 'n_saved_cell'), ('result', 'n_result_cell')]:
        setup += ['$lookup(S_pre.ENV,' + text(name) + ') = (' + cell + ')']
    setup += ['S_pre.STORE[n_generator_cell] = DEFINED (POBJECT n_generator)',
        *reach('S_thrown', 'S_pre', 2),
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
