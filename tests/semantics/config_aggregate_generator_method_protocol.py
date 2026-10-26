#!/usr/bin/env python3
"""A real Generator-method receiver survives source replacement and retires."""
import argparse
import json
import os
import sys
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import config_aggregate_generator_method_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64
PREFIX = r"""
dec $test_config_method_front(pstate, nat) : bool
def $test_config_method_front(S, 0) = true
  -- if S.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_config_method_front(S, 1) = true
  -- if S.TODO = (CONFIG_AGGREGATE pconfigaggregate) :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $test_config_method_front(S, 2) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "next") :: ptask*
  -- if |pconfiggenerator.ITEMS| = 1
def $test_config_method_front(S, 3) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "finish") :: ptask*
def $test_config_method_front(S, 4) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "invoke") :: ptask*
  -- if ~((HOBJECT pconfiggenerator.OBJECT) <- S.ALLOCATIONS)
def $test_config_method_front(S, n) = false -- otherwise
dec $test_config_method_seek(pstate, nat, nat) : pstate
def $test_config_method_seek(S, n_stage, 0) = S
def $test_config_method_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_config_method_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ (S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
def $test_config_method_seek(S, n_stage, n) = $test_config_method_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_config_method_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~(S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
dec $test_config_method_step(pstate) : pstate
def $test_config_method_step(S) = S_next
  -- PhpStep: S ~> S_next
"""


def reach(state, start, stage):
    return [state + '_found = $test_config_method_seek(' + start + ',' + str(stage) + ',3000)',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_config_method_front(' + state + ',' + str(stage) + ')']


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)',
        state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)',
        state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def checks(program, path, name):
    owned = name == 'retained-config-inherited-generator-method-preserves-callee'
    assert owned or name == 'fixed-config-generator-method-retains-and-retires-receiver'
    roots = '[HOBJECT n_generator,HOBJECT n_owner]' if owned else '[HOBJECT n_generator]'
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *reach('S_pre', 'S_initial', 0),
        'S_pre.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*',
        '$intrinsic_argument(S_pre,pconfigcall.SITE,0) = ((expression,true,eps,porigin_argument,z_argument))',
        'S_pre.RESULT = VARIABLE ' + text('aggregate') + ' z_argument',
        '$lookup(S_pre.ENV,' + text('aggregate') + ') = (n_aggregate_cell)',
        'S_pre.STORE[n_aggregate_cell] = DEFINED (POBJECT n_aggregate)',
        '$lookup(S_pre.ENV,' + text('watch') + ') = (n_watch_cell)',
        'S_pre.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)',
        'S_pre.OBJECTS[n_watch] = WEAKREFERENCE (n_aggregate)',
        '$node_children(S_pre,HOBJECT n_watch) = eps',
        '$lookup(S_pre.ENV,' + text('result') + ') = (n_result_cell)',
        'S_pre.STORE[n_result_cell] = DEFINED (PINT 99)',
        '$heap_owners($heap_graph(S_pre),HOBJECT n_aggregate) = 1',
        '$config_aggregate_start(S_pre,pconfigcall,S_pre.RESULT,n_aggregate)',
        '~$config_aggregate_start(S_pre[.ORIGIN = (porigin_argument)],pconfigcall,S_pre.RESULT,n_aggregate)',
        *common.public('S_pre'), *reach('S_return', 'S_pre', 1),
        'S_return.TODO = (CONFIG_AGGREGATE pconfigaggregate) :: ptask_tail*',
        'pconfigaggregate = {CALL pconfigcall,OBJECT n_aggregate,INPUT S_pre.RESULT}',
        'S_return.RESULT = KNOWN (POBJECT n_generator)',
        'n_generator = |S_pre.OBJECTS|',
        'S_return.OBJECTS[n_generator] = GENERATOR pgenerator_initial',
        'pgenerator_initial.PHASE = GENERATOR_FRESH',
        'pgenerator_initial.CLOSURE = eps', 'pgenerator_initial.ACCESS = eps',
        'pgenerator_initial.FRAME = (pframe_generator)',
        'pframe_generator.CONTEXT = (pcallcontext_generator)',
        'pcallcontext_generator.TARGET = CONFIG_AGGREGATE_GENERATOR_TARGET pconfiggeneratorproducer',
        'pconfiggeneratorproducer = {AGGREGATE pconfigaggregate,METHOD pgenerator_initial.FUNCTION}',
        'pcallcontext_generator.FUNCTION = pgenerator_initial.FUNCTION',
        'pcallcontext_generator.CALLSITE = (porigin_argument)',
        'pcallcontext_generator.INSTANCE = eps',
        'pcallcontext_generator.RECEIVER = (n_aggregate)',
        '$target_nodes(pcallcontext_generator.TARGET) = [HOBJECT n_aggregate]',
        '$task_nodes(CONFIG_AGGREGATE pconfigaggregate) = ' + ('[HOBJECT n_owner]' if owned else 'eps'),
        'pconfigcall.OWNER = (n_owner)' if owned else 'pconfigcall.OWNER = eps',
        '$heap_owners($heap_graph(S_return),HOBJECT n_generator) = 1',
        '$heap_owners($heap_graph(S_return),HOBJECT n_aggregate) = 2',
        '$config_aggregate_generator_context(S_return,pcallcontext_generator)',
        '$config_aggregate_generator_producer_valid(S_return,pconfiggeneratorproducer)',
        '$config_aggregate_method_generator_return_allowed(S_return,pconfigaggregate)',
        '~$config_aggregate_generator_return_allowed(S_return,pconfigaggregate)',
        '~$config_aggregate_return_allowed(S_return,pconfigaggregate)',
        'S_return.ARRAYS = S_pre.ARRAYS',
        'S_return.PRECISIONINI = ' + text('14'),
        '$test_outputs(S_return.EVENTS) = ' + text('B|'),
        *common.public('S_return'),
        'S_data = $test_config_method_step(S_return)',
        'S_data.TODO = (CONFIG_GENERATOR pconfiggenerator "rewind") :: ptask_tail*',
        'pconfiggenerator = {CALL pconfigcall,OBJECT n_generator,INPUT S_pre.RESULT,ITEMS eps,PRODUCER (pconfiggeneratorproducer)}',
        'S_data = S_return[.TODO = (CONFIG_GENERATOR pconfiggenerator "rewind") :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$heap_graph(S_data) = $heap_graph(S_return)',
        '$task_nodes(CONFIG_GENERATOR pconfiggenerator "rewind") = ' + roots,
        '$config_generator_valid(S_data,pconfiggenerator,"rewind")',
        *common.public('S_data')]
    values += ['pconfiggenerator_missing = pconfiggenerator[.PRODUCER = eps]',
        'S_missing = S_data[.TODO = (CONFIG_GENERATOR pconfiggenerator_missing "rewind") :: ptask_tail*]',
        '~$config_generator_history(S_missing,pconfiggenerator_missing)',
        'pconfiggeneratorproducer_wrong = pconfiggeneratorproducer[.METHOD = pconfigcall.SITE]',
        'pconfiggenerator_wrong = pconfiggenerator[.PRODUCER = (pconfiggeneratorproducer_wrong)]',
        'S_wrong = S_data[.TODO = (CONFIG_GENERATOR pconfiggenerator_wrong "rewind") :: ptask_tail*]',
        '~$config_generator_history(S_wrong,pconfiggenerator_wrong)',
        'pconfiggeneratorproducer_other = pconfiggeneratorproducer[.AGGREGATE = pconfigaggregate[.OBJECT = n_watch]]',
        '~$config_aggregate_generator_producer_valid(S_data,pconfiggeneratorproducer_other)',
        '~$config_aggregate_method_generator_return_allowed(S_return[.CODE = eps],pconfigaggregate)',
        *reach('S_first', 'S_data', 2),
        'S_first.TODO = (CONFIG_GENERATOR pconfiggenerator_first "next") :: ptask_tail*',
        'pconfiggenerator_first.ITEMS = [ENTRY (KINT 3) (DIRECT pvalue_option)]',
        '$string_bytes(pvalue_option) = (' + text('precision') + ')',
        'pconfiggenerator_first.PRODUCER = (pconfiggeneratorproducer)',
        'S_first.STORE[n_aggregate_cell] = DEFINED (PINT ' + ('23' if owned else '17') + ')',
        '$heap_owners($heap_graph(S_first),HOBJECT n_generator) = 1',
        '$heap_owners($heap_graph(S_first),HOBJECT n_aggregate) = 1',
        '$weakref_get(S_first,n_watch) = POBJECT n_aggregate',
        '$config_aggregate_generator_capture(S_first,pconfiggeneratorproducer,n_generator)',
        *common.public('S_first'), *reach('S_finish', 'S_first', 3),
        'S_finish.TODO = (CONFIG_GENERATOR pconfiggenerator_finish "finish") :: ptask_tail*',
        'pconfiggenerator_finish.ITEMS = [ENTRY (KINT 3) (DIRECT pvalue_option),ENTRY (KINT 3) (DIRECT pvalue_value)]',
        '$string_bytes(pvalue_value) = (' + text('11' if owned else '8') + ')',
        'pconfiggenerator_finish.PRODUCER = (pconfiggeneratorproducer)',
        'S_finish.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
        'pgenerator_closed.PHASE = GENERATOR_CLOSED', 'pgenerator_closed.FRAME = eps',
        '$heap_owners($heap_graph(S_finish),HOBJECT n_generator) = 1',
        '~((HOBJECT n_aggregate) <- S_finish.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_finish),HOBJECT n_aggregate) = 0',
        '$weakref_get(S_finish,n_watch) = PNULL',
        '$target_function(S_finish,pcallcontext_generator.TARGET) = eps',
        '$config_aggregate_generator_producer_valid(S_finish,pconfiggeneratorproducer)',
        '~$config_aggregate_scope(S_finish,pconfigaggregate)',
        '$config_generator_quiet_closed(S_finish,pconfiggenerator_finish)',
        '$config_generator_finish_allowed(S_finish,pconfiggenerator_finish)',
        'S_finish.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_finish.PRECISIONINI = ' + text('7' if owned else '14'),
        '$test_outputs(S_finish.EVENTS) = ' + text('B|G|R|Y1|F|'),
        *common.public('S_finish'),
        'S_raw = $test_config_method_step(S_finish)',
        'S_raw = $config_generator_finish(S_finish,pconfiggenerator_finish,ptask_tail*)',
        *reach('S_invoke', 'S_finish', 4),
        'S_invoke.TODO = (CONFIG_GENERATOR pconfiggenerator_finish "invoke") :: ptask_tail*',
        '~((HOBJECT n_generator) <- S_invoke.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_invoke),HOBJECT n_generator) = 0',
        '$weakref_get(S_invoke,n_watch) = PNULL',
        '$config_generator_history(S_invoke,pconfiggenerator_finish)',
        '$config_generator_retired_scope(S_invoke,pconfiggenerator_finish)',
        '~$config_generator_scope(S_invoke,pconfiggenerator_finish)',
        '$config_generator_valid(S_invoke,pconfiggenerator_finish,"invoke")',
        '$task_nodes(CONFIG_GENERATOR pconfiggenerator_finish "invoke") = ' + ('[HOBJECT n_owner]' if owned else 'eps'),
        'S_invoke.ARRAYS = S_pre.ARRAYS',
        'S_invoke.ITERATORS = S_pre.ITERATORS', 'S_invoke.NEXTITER = S_pre.NEXTITER',
        *common.public('S_invoke')]
    if owned:
        values += ['$lookup(S_pre.ENV,' + text('call') + ') = (n_call_cell)',
            '$lookup(S_pre.ENV,' + text('keep') + ') = (n_keep_cell)',
            'S_finish.STORE[n_call_cell] = DEFINED (POBJECT n_getter)',
            'S_finish.OBJECTS[n_getter] = INTRINSICCLOSURE INTRINSIC_INI_GET',
            '$heap_owners($heap_graph(S_finish),HOBJECT n_owner) = 2',
            'S_last_callee = S_finish[.STORE[n_keep_cell] = DEFINED PNULL]',
            '$heap_owners($heap_graph(S_last_callee),HOBJECT n_owner) = 1',
            '$test_config_method_step(S_last_callee) = S_last_callee[.COMPLETION = UNSUPPORTED "CONFIG Generator unpack last DATA or callee owner"]']
    values += [*common.step('S_after', 'S_invoke'),
        'S_after.TODO = ptask_tail*', 'S_after.RESULT = KNOWN pvalue_old',
        '$string_bytes(pvalue_old) = (' + text('7' if owned else '14') + ')',
        'S_after.PRECISIONINI = ' + text('11' if owned else '8'),
        'S_after.STORE[n_result_cell] = DEFINED (PINT 99)',
        *budget('S_return'), *budget('S_invoke'),
        'S_final = $drive_steps(S_after,3000)', 'S_final.COMPLETION = NORMAL',
        'S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        '~((HOBJECT n_generator) <- S_final.ALLOCATIONS)',
        '$weakref_get(S_final,n_watch) = PNULL',
        '$test_outputs(S_final.EVENTS) = ' + text('B|G|R|Y1|F|A|' +
            ('7|11|23|D|L|11|R|11|9' if owned else '14|8|17|D|E')),
        *common.public('S_final')]
    return values


def partition(values, part, owned):
    cut = values.index('$heap_valid($heap_graph(S_data))') + 1
    if part == 'entry':
        return values[:cut]
    setup = [values[0], values[1], *reach('S_pre', 'S_initial', 0),
        'S_pre.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*',
        '$intrinsic_argument(S_pre,pconfigcall.SITE,0) = ((expression,true,eps,porigin_argument,z_argument))']
    for name, cell in [('aggregate', 'n_aggregate_cell'), ('watch', 'n_watch_cell'), ('result', 'n_result_cell')]:
        setup += ['$lookup(S_pre.ENV,' + text(name) + ') = (' + cell + ')']
    setup += ['S_pre.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)',
        *reach('S_return', 'S_pre', 1),
        'S_return.TODO = (CONFIG_AGGREGATE pconfigaggregate) :: ptask_tail*',
        'pconfigaggregate.OBJECT = n_aggregate', 'S_return.RESULT = KNOWN (POBJECT n_generator)',
        'S_return.OBJECTS[n_generator] = GENERATOR pgenerator_initial',
        'pgenerator_initial.FRAME = (pframe_generator)',
        'pframe_generator.CONTEXT = (pcallcontext_generator)',
        'pcallcontext_generator.TARGET = CONFIG_AGGREGATE_GENERATOR_TARGET pconfiggeneratorproducer',
        'S_data = $test_config_method_step(S_return)',
        'S_data.TODO = (CONFIG_GENERATOR pconfiggenerator "rewind") :: ptask_tail*']
    if owned:
        setup += ['pconfigcall.OWNER = (n_owner)']
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
            driver.checks = lambda program, path, name: partition(checks(program, path, name), part,
                name == 'retained-config-inherited-generator-method-preserves-callee')
            sys.argv = [sys.argv[0], '--phase', args.phase, '--sources', str(args.sources),
                '--output', str(args.output / name / part)]
            driver.main()


if __name__ == '__main__':
    main()
