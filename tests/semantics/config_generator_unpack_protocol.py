#!/usr/bin/env python3
"""Source Generator DATA survives live CV/callee writes and drains before API."""
import argparse
import json
import os
import sys
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import config_generator_unpack_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64
PREFIX = r"""
dec $test_config_generator_front(pstate, nat) : bool
def $test_config_generator_front(S, 0) = true
  -- if S.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_config_generator_front(S, 1) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask_tail*
  -- if pconfiggenerator.ITEMS = eps
  -- if S.OBJECTS[pconfiggenerator.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_PAUSED
def $test_config_generator_front(S, 2) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "finish") :: ptask_tail*
def $test_config_generator_front(S, n) = false -- otherwise
dec $test_config_generator_seek(pstate, nat, nat) : pstate
def $test_config_generator_seek(S, n_stage, 0) = S
def $test_config_generator_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_config_generator_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ (S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
def $test_config_generator_seek(S, n_stage, n) = $test_config_generator_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_config_generator_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~(S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
dec $test_config_generator_step(pstate) : pstate
def $test_config_generator_step(S) = S_next
  -- PhpStep: S ~> S_next
"""


def reach(state, start, stage):
    return [state + '_found = $test_config_generator_seek(' + start + ',' + str(stage) + ',3000)',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_config_generator_front(' + state + ',' + str(stage) + ')']


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)',
        state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)',
        state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def checks(program, path, name):
    owned = name == 'retained-config-generator-preserves-selection-and-historical-input'
    assert owned or name == 'fixed-config-generator-drains-before-api'
    first, second, value, old = ('3', '3', '11', '7') if owned else ('$(-11)', '7', '8', '14')
    roots = '[HOBJECT n_generator,HOBJECT n_owner]' if owned else '[HOBJECT n_generator]'
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *reach('S_pre', 'S_initial', 0),
        'S_pre.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*',
        'pconfigcall.KIND = INTRINSIC_INI_SET', 'pconfigcall.INDEX = 0',
        'pconfigcall.SENT = eps', 'pconfigcall.PACKS = eps', '~pconfigcall.NAMED',
        '$intrinsic_argument(S_pre,pconfigcall.SITE,0) = ((expression,true,eps,porigin_argument,z_argument))',
        'S_pre.RESULT = VARIABLE ' + text('it') + ' z_argument',
        '$lookup(S_pre.ENV,' + text('it') + ') = (n_generator_cell)',
        'S_pre.STORE[n_generator_cell] = DEFINED (POBJECT n_generator)',
        'S_pre.OBJECTS[n_generator] = GENERATOR pgenerator_initial',
        'pgenerator_initial.PHASE = GENERATOR_FRESH',
        '$heap_owners($heap_graph(S_pre),HOBJECT n_generator) = ' + ('2' if owned else '1'),
        '$lookup(S_pre.ENV,' + text('result') + ') = (n_result_cell)',
        'S_pre.STORE[n_result_cell] = DEFINED (PINT 99)',
        '$config_generator_start(S_pre,pconfigcall,S_pre.RESULT,n_generator)',
        '~$config_invoke_valid(S_pre,pconfigcall)', *common.public('S_pre'),
        'S_data = $test_config_generator_step(S_pre)',
        'S_data.TODO = (CONFIG_GENERATOR pconfiggenerator_initial "rewind") :: ptask_tail*',
        'pconfiggenerator_initial = {CALL pconfigcall,OBJECT n_generator,INPUT S_pre.RESULT,ITEMS eps,PRODUCER eps}',
        '$task_nodes(CONFIG_GENERATOR pconfiggenerator_initial "rewind") = ' + roots,
        '$heap_owners($heap_graph(S_data),HOBJECT n_generator) = ' + ('3' if owned else '2'),
        'S_data.RESULT = KNOWN PNULL', 'S_data.STORE = S_pre.STORE',
        'S_data.OBJECTS = S_pre.OBJECTS', 'S_data.ARRAYS = S_pre.ARRAYS',
        'S_data.ITERATORS = S_pre.ITERATORS', 'S_data.NEXTITER = S_pre.NEXTITER',
        '$config_generator_valid(S_data,pconfiggenerator_initial,"rewind")',
        *common.public('S_data'), *reach('S_first', 'S_data', 1),
        'S_first.TODO = (CONFIG_GENERATOR pconfiggenerator_first "ready") :: ptask_tail*',
        'pconfiggenerator_first = pconfiggenerator_initial',
        'S_first.OBJECTS[n_generator] = GENERATOR pgenerator_first',
        'pgenerator_first.VALUE = (pvalue_option)',
        '$string_bytes(pvalue_option) = (' + text('precision') + ')',
        'pgenerator_first.KEY = (PINT ' + first + ')',
        'S_first.CURRENT = eps', 'S_first.FRAMES = eps',
        '$heap_owners($heap_graph(S_first),HOBJECT n_generator) = 2',
        'S_first.ARRAYS = S_pre.ARRAYS',
        '$config_generator_send_allowed(S_first,pconfiggenerator_first)',
        '$test_outputs(S_first.EVENTS) = ' + text('B|Y0|'),
        *common.public('S_first')]
    values += ['S_sent = $test_config_generator_step(S_first)',
        'S_sent.TODO = (CONFIG_GENERATOR pconfiggenerator_sent "next") :: ptask_tail*',
        'pconfiggenerator_sent = pconfiggenerator_first[.ITEMS = [ENTRY (KINT ' + first + ') (DIRECT pvalue_option)]]',
        '$heap_graph(S_sent) = $heap_graph(S_first)',
        'S_sent.OBJECTS = S_first.OBJECTS', 'S_sent.ARRAYS = S_first.ARRAYS',
        *reach('S_finish', 'S_sent', 2),
        'S_finish.TODO = (CONFIG_GENERATOR pconfiggenerator_finish "finish") :: ptask_tail*',
        'pconfiggenerator_finish.CALL = pconfigcall',
        'pconfiggenerator_finish.INPUT = S_pre.RESULT',
        'pconfiggenerator_finish.ITEMS = [ENTRY (KINT ' + first + ') (DIRECT pvalue_option),ENTRY (KINT ' + second + ') (DIRECT pvalue_value)]',
        '$string_bytes(pvalue_value) = (' + text(value) + ')',
        'S_finish.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
        'pgenerator_closed.PHASE = GENERATOR_CLOSED',
        '$heap_owners($heap_graph(S_finish),HOBJECT n_generator) = 2',
        'S_finish.PRECISIONINI = ' + text(old),
        '$test_outputs(S_finish.EVENTS) = ' + text('B|Y0|Y1|F|'),
        *common.public('S_finish'),
        'S_invoke = $test_config_generator_step(S_finish)',
        'S_invoke.TODO = (CONFIG_GENERATOR pconfiggenerator_finish "invoke") :: ptask_tail*',
        '$task_nodes(CONFIG_GENERATOR pconfiggenerator_finish "invoke") = ' + ('[HOBJECT n_owner]' if owned else 'eps'),
        '$heap_owners($heap_graph(S_invoke),HOBJECT n_generator) = 1',
        'S_invoke.OBJECTS = S_finish.OBJECTS', 'S_invoke.ARRAYS = S_pre.ARRAYS',
        'S_invoke.ITERATORS = S_pre.ITERATORS', 'S_invoke.NEXTITER = S_pre.NEXTITER',
        *common.public('S_invoke'), *common.step('S_api', 'S_invoke'),
        'S_api.TODO = ptask_tail*', 'S_api.RESULT = KNOWN pvalue_old',
        '$string_bytes(pvalue_old) = (' + text(old) + ')',
        'S_api.PRECISIONINI = ' + text(value),
        'S_api.STORE[n_result_cell] = DEFINED (PINT 99)']
    if owned:
        values += ['pconfigcall.OWNER = (n_owner)',
            '$lookup(S_pre.ENV,' + text('hold') + ') = (n_hold_cell)',
            '$lookup(S_pre.ENV,' + text('call') + ') = (n_call_cell)',
            '$lookup(S_pre.ENV,' + text('keep') + ') = (n_keep_cell)',
            'S_first.STORE[n_generator_cell] = DEFINED (PINT 17)',
            'S_first.STORE[n_hold_cell] = DEFINED (POBJECT n_generator)',
            'S_first.STORE[n_call_cell] = DEFINED (POBJECT n_getter)',
            'S_first.OBJECTS[n_getter] = INTRINSICCLOSURE INTRINSIC_INI_GET',
            '$heap_owners($heap_graph(S_first),HOBJECT n_owner) = 2',
            '$heap_owners($heap_graph(S_api),HOBJECT n_owner) = 1',
            'S_last_callee = S_finish[.STORE[n_keep_cell] = DEFINED PNULL]',
            '$heap_owners($heap_graph(S_last_callee),HOBJECT n_owner) = 1',
            '$config_generator_valid(S_last_callee,pconfiggenerator_finish,"finish")',
            'S_callee_stopped = $test_config_generator_step(S_last_callee)',
            'S_callee_stopped = S_last_callee[.COMPLETION = UNSUPPORTED "CONFIG Generator unpack last DATA or callee owner"]']
    else:
        values += ['pconfigcall.OWNER = eps']
    # Source92 replaces the old last-DATA refusal projections with real retirement.
    values += ['~$config_generator_start(S_pre[.ORIGIN = (porigin_argument)],pconfigcall,S_pre.RESULT,n_generator)',
        '~$config_generator_scope(S_first,pconfiggenerator_first[.INPUT = KNOWN (POBJECT n_generator)])',
        '~$config_generator_scope(S_first[.CODE = eps],pconfiggenerator_first)',
        *budget('S_pre'), *budget('S_finish'),
        'S_final = $drive_steps(S_api,3000)', 'S_final.COMPLETION = NORMAL',
        'S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.ITERATORS = S_pre.ITERATORS', 'S_final.NEXTITER = S_pre.NEXTITER',
        'S_final.ARRAYS = S_pre.ARRAYS',
        '$test_outputs(S_final.EVENTS) = ' + text('B|Y0|Y1|F|A|' +
            ('7|11|11|17|R|11|9' if owned else '14|8|E')),
        *common.public('S_final')]
    return values


def partition(values, owned, part):
    cut = values.index('$heap_valid($heap_graph(S_first))') + 1
    if part == 'entry':
        return values[:cut]
    setup = [values[0], values[1], *reach('S_pre', 'S_initial', 0),
        'S_pre.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*',
        '$intrinsic_argument(S_pre,pconfigcall.SITE,0) = ((expression,true,eps,porigin_argument,z_argument))',
        '$lookup(S_pre.ENV,' + text('it') + ') = (n_generator_cell)',
        'S_pre.STORE[n_generator_cell] = DEFINED (POBJECT n_generator)',
        '$lookup(S_pre.ENV,' + text('result') + ') = (n_result_cell)',
        *reach('S_first', 'S_pre', 1),
        'S_first.TODO = (CONFIG_GENERATOR pconfiggenerator_first "ready") :: ptask_tail*',
        'S_first.OBJECTS[n_generator] = GENERATOR pgenerator_first',
        'pgenerator_first.VALUE = (pvalue_option)']
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
    args = parser.parse_args()
    driver.sources, driver.PREFIX = sources, PREFIX
    for name, case in cases.items():
        sources.family.CASES = {name: case}
        for part in (['entry', 'completion'] if args.part == 'all' else [args.part]):
            driver.checks = lambda program, path, name: partition(checks(program, path, name), name.startswith('retained-'), part)
            sys.argv = [sys.argv[0], '--phase', args.phase, '--sources', str(args.sources),
                '--output', str(args.output / name / part)]
            driver.main()


if __name__ == '__main__':
    main()
