#!/usr/bin/env python3
"""Source-reached Aggregate receipt and quiet sole Iterator DATA retirement."""
import argparse
import json
import os
from pathlib import Path
import sys

import global_constant_scalar_name_protocol as driver
import config_aggregate_fresh_iterator_sources as sources


text, b64 = driver.text, driver.b64
PREFIX = r"""
dec $test_fresh_aggregate_task(ptask) : bool
def $test_fresh_aggregate_task(CONFIG_ITERATOR pconfigiterator text) = true
def $test_fresh_aggregate_task(ptask) = false -- otherwise
dec $test_fresh_aggregate_tasks(ptask*) : bool
def $test_fresh_aggregate_tasks(eps) = true
def $test_fresh_aggregate_tasks(ptask :: ptask_tail*) = (~$test_fresh_aggregate_task(ptask) /\ $test_fresh_aggregate_tasks(ptask_tail*))
dec $test_fresh_aggregate_front(pstate, nat) : bool
def $test_fresh_aggregate_front(S, 0) = true
  -- if S.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_fresh_aggregate_front(S, 1) = true
  -- if S.TODO = (CONFIG_AGGREGATE pconfigaggregate) :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $test_fresh_aggregate_front(S, 2) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "finish") :: ptask*
def $test_fresh_aggregate_front(S, 3) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "ready") :: ptask*
  -- if ~((HOBJECT pconfigiterator.OBJECT) <- S.ALLOCATIONS)
def $test_fresh_aggregate_front(S, 4) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_ITERATOR pconfigiterator "key") :: ptask*
def $test_fresh_aggregate_front(S, 5) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask*
  -- if S.ITERATORS = eps
  -- if $test_fresh_aggregate_tasks(S.TODO)
def $test_fresh_aggregate_front(S, n_stage) = false -- otherwise
dec $test_fresh_aggregate_seek(pstate, nat, nat) : pstate
def $test_fresh_aggregate_seek(S, n_stage, 0) = S
def $test_fresh_aggregate_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_fresh_aggregate_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET /\ ~$throwable_pending(S.COMPLETION)) \/ (S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
def $test_fresh_aggregate_seek(S, n_stage, n) = $test_fresh_aggregate_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_fresh_aggregate_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET \/ $throwable_pending(S.COMPLETION)
  -- if ~(S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
dec $test_fresh_aggregate_step(pstate) : pstate
def $test_fresh_aggregate_step(S) = S_next
  -- PhpStep: S ~> S_next
"""


def reach(state, start, stage):
    return [state + '_found = $test_fresh_aggregate_seek(' + start + ',' + str(stage) + ',3000)',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_fresh_aggregate_front(' + state + ',' + str(stage) + ')']


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)',
        state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)',
        state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def checks(program, path, name):
    throwing = name == 'fresh-return-key-exception-sole-data'
    assert throwing or name == 'fresh-return-normal-sole-data'
    prefix = ('B|G|R|V0|C0|H|K0|H|N0|V1|C1|H|K1|H|T|' if throwing else
              'B|G|R|V0|C0|H|K0|H|N0|V1|C1|H|K1|H|N1|V2|')
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *reach('S_pre', 'S_initial', 0),
        'S_pre.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*',
        'pconfigcall.KIND = INTRINSIC_INI_SET', 'pconfigcall.OWNER = eps',
        '$intrinsic_argument(S_pre,pconfigcall.SITE,0) = ((expression,true,eps,porigin_argument,z_argument))',
        'S_pre.RESULT = VARIABLE ' + text('aggregate') + ' z_argument',
        '$lookup(S_pre.ENV,' + text('aggregate') + ') = (n_aggregate_cell)',
        '$lookup(S_pre.ENV,' + text('aggregateHold') + ') = (n_aggregate_hold)',
        'S_pre.STORE[n_aggregate_cell] = DEFINED (POBJECT n_aggregate)',
        'S_pre.STORE[n_aggregate_hold] = DEFINED (POBJECT n_aggregate)',
        '$heap_owners($heap_graph(S_pre),HOBJECT n_aggregate) = 2',
        '$lookup(S_pre.ENV,' + text('result') + ') = (n_result_cell)',
        'S_pre.STORE[n_result_cell] = DEFINED (PINT 99)',
        '$config_aggregate_start(S_pre,pconfigcall,S_pre.RESULT,n_aggregate)',
        '$test_outputs(S_pre.EVENTS) = ' + text('B|'),
        *driver.common.public('S_pre'), *reach('S_return', 'S_pre', 1),
        'S_return.TODO = (CONFIG_AGGREGATE pconfigaggregate) :: ptask_tail*',
        'pconfigaggregate = {CALL pconfigcall,OBJECT n_aggregate,INPUT S_pre.RESULT}',
        'S_return.RESULT = KNOWN (POBJECT n_iterator)',
        '$heap_owners($heap_graph(S_return),HOBJECT n_iterator) = 1',
        '$heap_owners($heap_graph(S_return),HOBJECT n_aggregate) = 2',
        '$config_aggregate_return_allowed(S_return,pconfigaggregate)',
        '$destructor_method(S_return,n_iterator) = eps',
        '$node_children(S_return,HOBJECT n_iterator) = eps',
        '$lookup(S_return.ENV,' + text('watch') + ') = (n_watch_cell)',
        'S_return.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)',
        'S_return.OBJECTS[n_watch] = WEAKREFERENCE (n_iterator)',
        '$weakref_get(S_return,n_watch) = POBJECT n_iterator',
        'S_return.PRECISIONINI = ' + text('14'),
        '$test_outputs(S_return.EVENTS) = ' + text('B|G|'),
        *driver.common.public('S_return'),
        'S_data = $test_fresh_aggregate_step(S_return)',
        'S_data.TODO = (CONFIG_ITERATOR pconfigiterator_initial "rewind-start") :: ptask_tail*',
        'pconfigiterator_initial = {CALL pconfigcall,ITERATOR S_return.NEXTITER,OBJECT n_iterator,INPUT S_pre.RESULT,PRODUCER (n_aggregate),ITEMS eps,CURRENT (KNOWN PNULL),KEY (KNOWN PNULL)}',
        '$config_iterator_valid(S_data,pconfigiterator_initial,"rewind-start")',
        '$config_iterator_producer_valid(S_data,pconfigiterator_initial)',
        '$task_nodes(CONFIG_ITERATOR pconfigiterator_initial "rewind-start") = [HOBJECT n_iterator]',
        '$heap_owners($heap_graph(S_data),HOBJECT n_iterator) = 1',
        '$heap_owners($heap_graph(S_data),HOBJECT n_aggregate) = 2',
        '$weakref_get(S_data,n_watch) = POBJECT n_iterator',
        'S_data.STORE = S_return.STORE', 'S_data.EVENTS = S_return.EVENTS',
        '~$config_iterator_producer_valid(S_data,pconfigiterator_initial[.PRODUCER = (n_iterator)])',
        *budget('S_return'), *driver.common.public('S_data')]
    if throwing:
        values += [*reach('S_throw', 'S_data', 4),
            'S_throw.TODO = (THROW_SEARCH n_exception) :: (CONFIG_ITERATOR pconfigiterator "key") :: ptask_tail*',
            'pconfigiterator.PRODUCER = (n_aggregate)',
            'pconfigiterator.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_option)]',
            '$string_bytes(pvalue_option) = (' + text('precision') + ')',
            'pconfigiterator.CURRENT = KNOWN pvalue_current',
            '$string_bytes(pvalue_current) = (' + text('8') + ')',
            '$config_iterator_valid(S_throw,pconfigiterator,"key")',
            '$heap_owners($heap_graph(S_throw),HOBJECT n_iterator) = 1',
            '$weakref_get(S_throw,n_watch) = POBJECT n_iterator',
            'S_throw.STORE[n_result_cell] = DEFINED (PINT 99)',
            'S_throw.PRECISIONINI = ' + text('14'),
            '$test_outputs(S_throw.EVENTS) = ' + text(prefix),
            *driver.common.public('S_throw'),
            'S_scope = S_throw[.TODO = (THROW_SEARCH n_exception) :: ptask_tail*]',
            '$heap_owners($heap_graph(S_scope),HOBJECT n_iterator) = 0',
            '$config_iterator_discard_allowed(S_scope,pconfigiterator)',
            '~$config_iterator_discard_allowed(S_scope,pconfigiterator[.PRODUCER = eps])',
            '~$config_iterator_discard_allowed(S_scope,pconfigiterator[.PRODUCER = (n_iterator)])',
            '$config_iterator_discard_nodes(pconfigiterator,"key") = [HOBJECT n_iterator]',
            *budget('S_throw'), *reach('S_disposed', 'S_throw', 5),
            'S_disposed.TODO = (THROW_SEARCH n_exception) :: ptask_disposed*',
            '~((HOBJECT n_iterator) <- S_disposed.ALLOCATIONS)',
            '$heap_owners($heap_graph(S_disposed),HOBJECT n_iterator) = 0',
            '$weakref_get(S_disposed,n_watch) = PNULL',
            'S_disposed.STORE[n_result_cell] = DEFINED (PINT 99)',
            'S_disposed.PRECISIONINI = ' + text('14'),
            '$test_outputs(S_disposed.EVENTS) = ' + text(prefix),
            *driver.common.public('S_disposed'),
            'S_final = $drive_steps(S_disposed,3000)',
            'S_final.COMPLETION = NORMAL', 'S_final.TODO = eps',
            'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
            'S_final.STORE[n_result_cell] = DEFINED (PINT 99)',
            'S_final.PRECISIONINI = ' + text('9'),
            '$test_outputs(S_final.EVENTS) = ' + text(prefix + 'I|99|14|output_buffering|D|R|14|9'),
            *driver.common.public('S_final')]
        return values
    values += [*reach('S_finish', 'S_data', 2),
        'S_finish.TODO = (CONFIG_ITERATOR pconfigiterator "finish") :: ptask_tail*',
        'pconfigiterator.PRODUCER = (n_aggregate)',
        'pconfigiterator.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_option),ENTRY (KINT 1) (DIRECT pvalue_value)]',
        '$string_bytes(pvalue_option) = (' + text('precision') + ')',
        '$string_bytes(pvalue_value) = (' + text('8') + ')',
        '$config_iterator_valid(S_finish,pconfigiterator,"finish")',
        '$config_iterator_quiet_aggregate_data(S_finish,pconfigiterator)',
        '$heap_owners($heap_graph(S_finish),HOBJECT n_iterator) = 1',
        '$weakref_get(S_finish,n_watch) = POBJECT n_iterator',
        'S_finish.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_finish.PRECISIONINI = ' + text('14'),
        '$test_outputs(S_finish.EVENTS) = ' + text(prefix),
        'S_missing = $config_iterator_finish(S_finish,pconfigiterator[.PRODUCER = eps],ptask_tail*)',
        'S_missing.COMPLETION = UNSUPPORTED "CONFIG Iterator unpack last DATA owner"',
        'S_wrong = $config_iterator_finish(S_finish,pconfigiterator[.PRODUCER = (n_iterator)],ptask_tail*)',
        'S_wrong.COMPLETION = UNSUPPORTED "CONFIG Iterator unpack last DATA owner"',
        *budget('S_finish'), *driver.common.public('S_finish'),
        'S_release = $test_fresh_aggregate_step(S_finish)',
        *reach('S_ready', 'S_finish', 3),
        'S_ready.TODO = (CONFIG_ITERATOR pconfigiterator "ready") :: ptask_tail*',
        'S_ready.ITERATORS = eps',
        '~((HOBJECT n_iterator) <- S_ready.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_ready),HOBJECT n_iterator) = 0',
        '$weakref_get(S_ready,n_watch) = PNULL',
        '$config_iterator_retired_scope(S_ready,pconfigiterator)',
        '~$config_iterator_retired_scope(S_ready,pconfigiterator[.PRODUCER = eps])',
        '~$config_iterator_retired_scope(S_ready,pconfigiterator[.PRODUCER = (n_iterator)])',
        '$config_iterator_valid(S_ready,pconfigiterator,"ready")',
        'S_ready.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_ready.PRECISIONINI = ' + text('14'),
        'S_ready.EVENTS = S_finish.EVENTS',
        *driver.common.public('S_ready'),
        *driver.common.step('S_api', 'S_ready'),
        'S_api.RESULT = KNOWN pvalue_old',
        '$string_bytes(pvalue_old) = (' + text('14') + ')',
        'S_api.PRECISIONINI = ' + text('8'),
        'S_api.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_final = $drive_steps(S_api,3000)',
        'S_final.COMPLETION = NORMAL', 'S_final.TODO = eps',
        'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        '$test_outputs(S_final.EVENTS) = ' + text(prefix + 'A|14|8|output_buffering|D'),
        *driver.common.public('S_final')]
    return values


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['prepare', 'check'], required=True)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    selected = ('fresh-return-normal-sole-data', 'fresh-return-key-exception-sole-data')
    sources.family.CASES = {name: sources.family.CASES[name] for name in selected}
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    if args.phase == 'check':
        recorded = driver.recorder.recorded
        driver.recorder.recorded = lambda command, stem, cap: recorded(command, stem, 240)
    sys.argv = [sys.argv[0], '--phase', args.phase, '--sources', str(args.sources),
                '--output', str(args.output)]
    driver.main()


if __name__ == '__main__':
    main()
