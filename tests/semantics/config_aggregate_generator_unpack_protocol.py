#!/usr/bin/env python3
"""A genuine Aggregate return transfers into native Generator DATA."""
import argparse
import json
import os
import sys
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import config_aggregate_generator_unpack_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64
PREFIX = r"""
dec $test_config_aggregate_generator_front(pstate, nat) : bool
def $test_config_aggregate_generator_front(S, 0) = true
  -- if S.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_config_aggregate_generator_front(S, 1) = true
  -- if S.TODO = (CONFIG_AGGREGATE pconfigaggregate) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $test_config_aggregate_generator_front(S, 2) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "finish") :: ptask_tail*
def $test_config_aggregate_generator_front(S, n) = false -- otherwise
dec $test_config_aggregate_generator_seek(pstate, nat, nat) : pstate
def $test_config_aggregate_generator_seek(S, n_stage, 0) = S
def $test_config_aggregate_generator_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_config_aggregate_generator_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ (S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
def $test_config_aggregate_generator_seek(S, n_stage, n) = $test_config_aggregate_generator_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_config_aggregate_generator_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~(S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
dec $test_config_aggregate_generator_step(pstate) : pstate
def $test_config_aggregate_generator_step(S) = S_next
  -- PhpStep: S ~> S_next
"""


def reach(state, start, stage):
    return [state + '_found = $test_config_aggregate_generator_seek(' + start + ',' + str(stage) + ',3000)',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_config_aggregate_generator_front(' + state + ',' + str(stage) + ')']


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)',
        state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)',
        state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def checks(program, path, name):
    owned = name == 'retained-config-aggregate-generator-preserves-two-histories'
    assert owned or name == 'fixed-config-aggregate-produces-retained-generator'
    first, second, value, old = ('3', '3', '11', '8') if owned else ('$(-11)', '7', '8', '14')
    roots = '[HOBJECT n_generator,HOBJECT n_owner]' if owned else '[HOBJECT n_generator]'
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *reach('S_pre', 'S_initial', 0),
        'S_pre.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*',
        '$intrinsic_argument(S_pre,pconfigcall.SITE,0) = ((expression,true,eps,porigin_argument,z_argument))',
        'S_pre.RESULT = VARIABLE ' + text('aggregate') + ' z_argument',
        '$lookup(S_pre.ENV,' + text('aggregate') + ') = (n_aggregate_cell)',
        'S_pre.STORE[n_aggregate_cell] = DEFINED (POBJECT n_aggregate)',
        '$lookup(S_pre.ENV,' + text('aggregateHold') + ') = (n_aggregate_hold)',
        '$lookup(S_pre.ENV,' + text('it') + ') = (n_generator_cell)',
        'S_pre.STORE[n_generator_cell] = DEFINED (POBJECT n_generator)',
        '$lookup(S_pre.ENV,' + text('iteratorHold') + ') = (n_generator_hold)',
        '$lookup(S_pre.ENV,' + text('result') + ') = (n_result_cell)',
        'S_pre.STORE[n_result_cell] = DEFINED (PINT 99)',
        '$heap_owners($heap_graph(S_pre),HOBJECT n_aggregate) = 2',
        '$heap_owners($heap_graph(S_pre),HOBJECT n_generator) = 2',
        '$config_aggregate_start(S_pre,pconfigcall,S_pre.RESULT,n_aggregate)',
        '~$config_generator_start(S_pre,pconfigcall,S_pre.RESULT,n_generator)',
        *common.public('S_pre'), *reach('S_return', 'S_pre', 1),
        'S_return.TODO = (CONFIG_AGGREGATE pconfigaggregate) :: ptask_tail*',
        'pconfigaggregate = {CALL pconfigcall,OBJECT n_aggregate,INPUT S_pre.RESULT}',
        'S_return.RESULT = KNOWN (POBJECT n_generator)',
        'S_return.OBJECTS[n_generator] = GENERATOR pgenerator_initial',
        'pgenerator_initial.PHASE = GENERATOR_FRESH',
        '$heap_owners($heap_graph(S_return),HOBJECT n_generator) = 3',
        '$heap_owners($heap_graph(S_return),HOBJECT n_aggregate) = ' + ('1' if owned else '2'),
        '$config_aggregate_generator_return_allowed(S_return,pconfigaggregate)',
        '~$config_aggregate_return_allowed(S_return,pconfigaggregate)',
        'S_return.ITERATORS = S_pre.ITERATORS', 'S_return.NEXTITER = S_pre.NEXTITER',
        'S_return.ARRAYS = S_pre.ARRAYS',
        'S_return.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_return.PRECISIONINI = ' + text('6' if owned else '14'),
        '$test_outputs(S_return.EVENTS) = ' + text('B|G|'),
        *common.public('S_return'),
        'S_data = $test_config_aggregate_generator_step(S_return)',
        'S_data.TODO = (CONFIG_GENERATOR pconfiggenerator "rewind") :: ptask_tail*',
        'pconfiggenerator = {CALL pconfigcall,OBJECT n_generator,INPUT S_pre.RESULT,ITEMS eps}',
        'S_data = S_return[.TODO = (CONFIG_GENERATOR pconfiggenerator "rewind") :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$heap_graph(S_data) = $heap_graph(S_return)',
        '$task_nodes(CONFIG_GENERATOR pconfiggenerator "rewind") = ' + roots,
        '$config_generator_valid(S_data,pconfiggenerator,"rewind")',
        *common.public('S_data')]
    values += [*reach('S_finish', 'S_data', 2),
        'S_finish.TODO = (CONFIG_GENERATOR pconfiggenerator_finish "finish") :: ptask_tail*',
        'pconfiggenerator_finish.CALL = pconfigcall',
        'pconfiggenerator_finish.INPUT = S_pre.RESULT',
        'pconfiggenerator_finish.ITEMS = [ENTRY (KINT ' + first + ') (DIRECT pvalue_option),ENTRY (KINT ' + second + ') (DIRECT pvalue_value)]',
        '$string_bytes(pvalue_option) = (' + text('precision') + ')',
        '$string_bytes(pvalue_value) = (' + text(value) + ')',
        'S_finish.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
        'pgenerator_closed.PHASE = GENERATOR_CLOSED',
        '$heap_owners($heap_graph(S_finish),HOBJECT n_generator) = ' + ('2' if owned else '3'),
        'S_finish.PRECISIONINI = ' + text(old),
        'S_finish.STORE[n_result_cell] = DEFINED (PINT 99)',
        '$test_outputs(S_finish.EVENTS) = ' + text('B|G|Y0|Y1|F|'),
        *common.public('S_finish'),
        'S_invoke = $test_config_aggregate_generator_step(S_finish)',
        'S_invoke.TODO = (CONFIG_GENERATOR pconfiggenerator_finish "invoke") :: ptask_tail*',
        '$heap_owners($heap_graph(S_invoke),HOBJECT n_generator) = ' + ('1' if owned else '2'),
        'S_invoke.ITERATORS = S_pre.ITERATORS', 'S_invoke.NEXTITER = S_pre.NEXTITER',
        'S_invoke.ARRAYS = S_pre.ARRAYS', *common.public('S_invoke'),
        *common.step('S_api', 'S_invoke'),
        'S_api.TODO = ptask_tail*', 'S_api.RESULT = KNOWN pvalue_old',
        '$string_bytes(pvalue_old) = (' + text(old) + ')',
        'S_api.PRECISIONINI = ' + text(value),
        'S_api.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_last_generator = S_return[.STORE[n_generator_cell] = DEFINED PNULL][.STORE[n_generator_hold] = DEFINED PNULL]',
        '$heap_owners($heap_graph(S_last_generator),HOBJECT n_generator) = 1',
        '~$config_aggregate_generator_return_allowed(S_last_generator,pconfigaggregate)',
        '$test_config_aggregate_generator_step(S_last_generator) = S_last_generator[.COMPLETION = UNSUPPORTED "CONFIG Aggregate return outside shared initialized Iterator domain"]',
        'S_lost_aggregate = S_return[.STORE[n_aggregate_cell] = DEFINED PNULL][.STORE[n_aggregate_hold] = DEFINED PNULL]',
        '$heap_owners($heap_graph(S_lost_aggregate),HOBJECT n_aggregate) = 0',
        '$test_config_aggregate_generator_step(S_lost_aggregate) = S_lost_aggregate[.COMPLETION = UNSUPPORTED "CONFIG Aggregate return outside shared initialized Iterator domain"]',
        'S_started_generator = S_return[.OBJECTS[n_generator] = GENERATOR pgenerator_initial[.PHASE = GENERATOR_PAUSED]]',
        '~$config_aggregate_generator_return_allowed(S_started_generator,pconfigaggregate)',
        '~$config_aggregate_generator_return_allowed(S_return[.RESULT = KNOWN PNULL],pconfigaggregate)',
        '~$config_aggregate_generator_return_allowed(S_return[.CODE = eps],pconfigaggregate)',
        '~$config_aggregate_generator_return_allowed(S_return,pconfigaggregate[.INPUT = KNOWN (POBJECT n_generator)])']
    if owned:
        values += ['pconfigcall.OWNER = (n_owner)',
            '$lookup(S_pre.ENV,' + text('call') + ') = (n_call_cell)',
            '$lookup(S_pre.ENV,' + text('keep') + ') = (n_keep_cell)',
            'S_return.STORE[n_aggregate_cell] = DEFINED (PINT 23)',
            'S_return.STORE[n_call_cell] = DEFINED (POBJECT n_getter)',
            'S_return.OBJECTS[n_getter] = INTRINSICCLOSURE INTRINSIC_INI_GET',
            '$heap_owners($heap_graph(S_return),HOBJECT n_owner) = 2',
            'S_finish.STORE[n_generator_cell] = DEFINED (PINT 17)',
            'S_finish.STORE[n_aggregate_cell] = DEFINED (PINT 23)',
            '$heap_owners($heap_graph(S_api),HOBJECT n_owner) = 1',
            'S_last_callee = S_return[.STORE[n_keep_cell] = DEFINED PNULL]',
            '$heap_owners($heap_graph(S_last_callee),HOBJECT n_owner) = 1',
            '$test_config_aggregate_generator_step(S_last_callee) = S_last_callee[.COMPLETION = UNSUPPORTED "CONFIG Aggregate return outside shared initialized Iterator domain"]']
    else:
        values += ['pconfigcall.OWNER = eps']
    values += [*budget('S_return'), *budget('S_data'),
        'S_final = $drive_steps(S_api,3000)', 'S_final.COMPLETION = NORMAL',
        'S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.ITERATORS = S_pre.ITERATORS', 'S_final.NEXTITER = S_pre.NEXTITER',
        'S_final.ARRAYS = S_pre.ARRAYS',
        '$test_outputs(S_final.EVENTS) = ' + text('B|G|Y0|Y1|F|A|' +
            ('8|11|11|17|23|R|11|9' if owned else '14|8|E')),
        *common.public('S_final')]
    return values


def partition(values, part):
    cut = values.index('$heap_valid($heap_graph(S_data))') + 1
    if part == 'entry':
        return values[:cut]
    setup = [values[0], values[1], *reach('S_pre', 'S_initial', 0),
        'S_pre.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*',
        '$intrinsic_argument(S_pre,pconfigcall.SITE,0) = ((expression,true,eps,porigin_argument,z_argument))']
    for name, cell in [('aggregate', 'n_aggregate_cell'), ('aggregateHold', 'n_aggregate_hold'),
            ('it', 'n_generator_cell'), ('iteratorHold', 'n_generator_hold'), ('result', 'n_result_cell')]:
        setup += ['$lookup(S_pre.ENV,' + text(name) + ') = (' + cell + ')']
    setup += ['S_pre.STORE[n_generator_cell] = DEFINED (POBJECT n_generator)',
        *reach('S_return', 'S_pre', 1),
        'S_return.TODO = (CONFIG_AGGREGATE pconfigaggregate) :: ptask_tail*',
        'pconfigaggregate.OBJECT = n_aggregate',
        'S_return.OBJECTS[n_generator] = GENERATOR pgenerator_initial',
        'S_data = $test_config_aggregate_generator_step(S_return)']
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
            driver.checks = lambda program, path, name: partition(checks(program, path, name), part)
            sys.argv = [sys.argv[0], '--phase', args.phase, '--sources', str(args.sources),
                '--output', str(args.output / name / part)]
            driver.main()


if __name__ == '__main__':
    main()
