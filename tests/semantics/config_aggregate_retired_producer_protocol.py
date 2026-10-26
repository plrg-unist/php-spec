#!/usr/bin/env python3
"""Reach a retired Aggregate receipt through its real returned Iterator."""
import argparse
import json
import os
from pathlib import Path
import sys

import global_constant_scalar_name_protocol as driver
import config_aggregate_fresh_iterator_protocol as prior
import config_aggregate_retired_producer_sources as sources


text, b64 = driver.text, driver.b64
PREFIX = prior.PREFIX + r"""
dec $test_retired_front(pstate, nat) : bool
def $test_retired_front(S, 0) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "key") :: ptask*
  -- if pconfigiterator.PRODUCER = (n_aggregate)
  -- if pconfigiterator.ITEMS = eps
  -- if ~((HOBJECT n_aggregate) <- S.ALLOCATIONS)
  -- if S.RESULT = KNOWN (PINT 0)
def $test_retired_front(S, 1) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "key") :: ptask*
  -- if pconfigiterator.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue)]
def $test_retired_front(S, 2) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_ITERATOR pconfigiterator "key") :: ptask*
def $test_retired_front(S, 3) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "finish") :: ptask*
def $test_retired_front(S, 4) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "ready") :: ptask*
  -- if ~((HOBJECT pconfigiterator.OBJECT) <- S.ALLOCATIONS)
def $test_retired_front(S, 5) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask*
  -- if S.ITERATORS = eps
  -- if $test_fresh_aggregate_tasks(S.TODO)
def $test_retired_front(S, n_stage) = false -- otherwise
dec $test_retired_seek(pstate, nat, nat) : pstate
def $test_retired_seek(S, n_stage, 0) = S
def $test_retired_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_retired_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET /\ ~$throwable_pending(S.COMPLETION)) \/ (S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
def $test_retired_seek(S, n_stage, n) = $test_retired_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_retired_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET \/ $throwable_pending(S.COMPLETION)
  -- if ~(S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
"""


def reach(state, start, stage):
    return [state + '_found = $test_retired_seek(' + start + ',' + str(stage) + ',3000)',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_retired_front(' + state + ',' + str(stage) + ')']


def checks(program, path, name):
    assert name in sources.family.CASES
    normal, invalid = name == 'retired-normal', name == 'retired-invalid'
    first = 'B|G|R|V0|C0|L|K0|PD|IL|'
    second = first + 'N0|V1|C1|L|K1|'
    normal_end = second + 'N1|V2|A|14|8|W|D|D|'
    error = 'Keys must be of type int|string during argument unpacking'
    invalid_end = second + 'E|' + error + '|40|99|14|W|D|D|'
    throw_end = second + 'E|S|saved|99|14|W|D|D|'
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *prior.reach('S_pre', 'S_initial', 0),
        'S_pre.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_pre*',
        'pconfigcall.KIND = INTRINSIC_INI_SET', 'pconfigcall.OWNER = eps',
        '$intrinsic_argument(S_pre,pconfigcall.SITE,0) = ((expression,true,eps,porigin_argument,z_argument))',
        'z_argument = 40',
        'S_pre.RESULT = VARIABLE ' + text('producer') + ' z_argument',
        '$lookup(S_pre.ENV,' + text('producer') + ') = (n_aggregate_cell)',
        'S_pre.STORE[n_aggregate_cell] = DEFINED (POBJECT n_aggregate)',
        '$heap_owners($heap_graph(S_pre),HOBJECT n_aggregate) = 1',
        '$lookup(S_pre.ENV,' + text('producerWatch') + ') = (n_aggregate_watch_cell)',
        'S_pre.STORE[n_aggregate_watch_cell] = DEFINED (POBJECT n_aggregate_watch)',
        'S_pre.OBJECTS[n_aggregate_watch] = WEAKREFERENCE (n_aggregate)',
        '$weakref_get(S_pre,n_aggregate_watch) = POBJECT n_aggregate',
        '$lookup(S_pre.ENV,' + text('result') + ') = (n_result_cell)',
        'S_pre.STORE[n_result_cell] = DEFINED (PINT 99)',
        '$lookup(S_pre.ENV,' + text('saved') + ') = (n_saved_cell)',
        'S_pre.STORE[n_saved_cell] = DEFINED (POBJECT n_saved)',
        '$config_aggregate_start(S_pre,pconfigcall,S_pre.RESULT,n_aggregate)',
        '$test_outputs(S_pre.EVENTS) = ' + text('B|'),
        *driver.common.public('S_pre'), *prior.reach('S_return', 'S_pre', 1),
        'S_return.TODO = (CONFIG_AGGREGATE pconfigaggregate) :: ptask_return*',
        'pconfigaggregate = {CALL pconfigcall,OBJECT n_aggregate,INPUT S_pre.RESULT}',
        'S_return.RESULT = KNOWN (POBJECT n_iterator)',
        '$config_aggregate_return_allowed(S_return,pconfigaggregate)',
        '$heap_owners($heap_graph(S_return),HOBJECT n_aggregate) = 1',
        '$heap_owners($heap_graph(S_return),HOBJECT n_iterator) = 1',
        '$lookup(S_return.ENV,' + text('iterWatch') + ') = (n_iterator_watch_cell)',
        'S_return.STORE[n_iterator_watch_cell] = DEFINED (POBJECT n_iterator_watch)',
        'S_return.OBJECTS[n_iterator_watch] = WEAKREFERENCE (n_iterator)',
        '$weakref_get(S_return,n_iterator_watch) = POBJECT n_iterator',
        '$test_outputs(S_return.EVENTS) = ' + text('B|G|'),
        *driver.common.public('S_return'),
        'S_data = $test_fresh_aggregate_step(S_return)',
        'S_data.TODO = (CONFIG_ITERATOR pconfigiterator_initial "rewind-start") :: ptask_data*',
        'pconfigiterator_initial = {CALL pconfigcall,ITERATOR S_return.NEXTITER,OBJECT n_iterator,INPUT S_pre.RESULT,PRODUCER (n_aggregate),ITEMS eps,CURRENT (KNOWN PNULL),KEY (KNOWN PNULL)}',
        '$config_iterator_valid(S_data,pconfigiterator_initial,"rewind-start")',
        '$heap_owners($heap_graph(S_data),HOBJECT n_iterator) = 1',
        *prior.budget('S_return'), *driver.common.public('S_data'),
        *reach('S_first', 'S_data', 0),
        'S_first.TODO = (CONFIG_ITERATOR pconfigiterator_first "key") :: ptask_first*',
        'pconfigiterator_first.CALL = pconfigcall',
        'pconfigiterator_first.OBJECT = n_iterator',
        'pconfigiterator_first.INPUT = S_pre.RESULT',
        'pconfigiterator_first.PRODUCER = (n_aggregate)',
        'pconfigiterator_first.ITEMS = eps',
        'S_first.RESULT = KNOWN (PINT 0)',
        'S_first.STORE[n_aggregate_cell] = DEFINED PNULL',
        '~((HOBJECT n_aggregate) <- S_first.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_first),HOBJECT n_aggregate) = 0',
        '$weakref_get(S_first,n_aggregate_watch) = PNULL',
        '(HOBJECT n_iterator) <- S_first.ALLOCATIONS',
        '$heap_owners($heap_graph(S_first),HOBJECT n_iterator) = 1',
        '$weakref_get(S_first,n_iterator_watch) = POBJECT n_iterator',
        'S_first.OBJECTS[n_aggregate] = INSTANCE porigin_aggregate',
        'S_first.OBJECTS[n_iterator] = INSTANCE porigin_iterator',
        '$config_aggregate_source(S_first,pconfigaggregate)',
        '~$config_aggregate_scope(S_first,pconfigaggregate)',
        '$config_iterator_producer_valid(S_first,pconfigiterator_first)',
        '$config_iterator_valid(S_first,pconfigiterator_first,"key")',
        '$config_iterator_quiet_aggregate_data(S_first,pconfigiterator_first)',
        '~$config_iterator_quiet_aggregate_data(S_first,pconfigiterator_first[.PRODUCER = eps])',
        '~$config_iterator_producer_valid(S_first,pconfigiterator_first[.PRODUCER = (n_iterator)])',
        '~$config_iterator_producer_valid(S_first,pconfigiterator_first[.PRODUCER = (n_saved)])',
        '~$config_iterator_producer_valid(S_first,pconfigiterator_first[.CALL = pconfigcall[.SITE = PORIGIN 999 eps]])',
        'pconfigiterator_first.CURRENT = KNOWN pvalue_current',
        '$string_bytes(pvalue_current) = (' + text('precision') + ')',
        'S_first.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_first.PRECISIONINI = ' + text('14'),
        '$test_outputs(S_first.EVENTS) = ' + text(first),
        *prior.budget('S_first'), *driver.common.public('S_first'),
        'S_send = $test_fresh_aggregate_step(S_first)',
        'S_send.TODO = (CONFIG_ITERATOR pconfigiterator_send "send") :: ptask_send*',
        'pconfigiterator_send.PRODUCER = (n_aggregate)',
        'pconfigiterator_send.KEY = KNOWN (PINT 0)',
        'S_send.EVENTS = S_first.EVENTS']
    if name != 'retired-throw':
        values += [
        *reach('S_second', 'S_send', 1),
        'S_second.TODO = (CONFIG_ITERATOR pconfigiterator_second "key") :: ptask_second*',
        'pconfigiterator_second.PRODUCER = (n_aggregate)',
        'pconfigiterator_second.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_option)]',
        '$string_bytes(pvalue_option) = (' + text('precision') + ')',
        '$config_iterator_valid(S_second,pconfigiterator_second,"key")',
        '$heap_owners($heap_graph(S_second),HOBJECT n_aggregate) = 0',
        '$heap_owners($heap_graph(S_second),HOBJECT n_iterator) = 1',
        '$weakref_get(S_second,n_aggregate_watch) = PNULL',
        '$weakref_get(S_second,n_iterator_watch) = POBJECT n_iterator',
        'S_second.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_second.PRECISIONINI = ' + text('14'),
        '$test_outputs(S_second.EVENTS) = ' + text(second),
        *prior.budget('S_second'), *driver.common.public('S_second')]
    if normal:
        values += ['S_second.RESULT = KNOWN (PINT 1)',
            *reach('S_finish', 'S_second', 3),
            'S_finish.TODO = (CONFIG_ITERATOR pconfigiterator_finish "finish") :: ptask_finish*',
            'pconfigiterator_finish.PRODUCER = (n_aggregate)',
            'pconfigiterator_finish.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_option),ENTRY (KINT 1) (DIRECT pvalue_value)]',
            '$string_bytes(pvalue_value) = (' + text('8') + ')',
            '$config_iterator_quiet_aggregate_data(S_finish,pconfigiterator_finish)',
            '$heap_owners($heap_graph(S_finish),HOBJECT n_iterator) = 1',
            '$weakref_get(S_finish,n_iterator_watch) = POBJECT n_iterator',
            *prior.budget('S_finish'), *driver.common.public('S_finish'),
            'S_release = $test_fresh_aggregate_step(S_finish)',
            *reach('S_ready', 'S_finish', 4),
            'S_ready.TODO = (CONFIG_ITERATOR pconfigiterator_ready "ready") :: ptask_ready*',
            'pconfigiterator_ready.PRODUCER = (n_aggregate)',
            'S_ready.ITERATORS = eps',
            '$config_iterator_retired_scope(S_ready,pconfigiterator_ready)',
            '$config_iterator_valid(S_ready,pconfigiterator_ready,"ready")',
            '~((HOBJECT n_iterator) <- S_ready.ALLOCATIONS)',
            '$heap_owners($heap_graph(S_ready),HOBJECT n_iterator) = 0',
            '$weakref_get(S_ready,n_aggregate_watch) = PNULL',
            '$weakref_get(S_ready,n_iterator_watch) = PNULL',
            'S_ready.STORE[n_result_cell] = DEFINED (PINT 99)',
            'S_ready.PRECISIONINI = ' + text('14'),
            *driver.common.public('S_ready'),
            'S_api = $test_fresh_aggregate_step(S_ready)',
            'S_api.RESULT = KNOWN pvalue_old',
            '$string_bytes(pvalue_old) = (' + text('14') + ')',
            'S_api.PRECISIONINI = ' + text('8'),
            'S_api.STORE[n_result_cell] = DEFINED (PINT 99)',
            'S_final = $drive_steps(S_api,3000)',
            'S_final.COMPLETION = NORMAL', 'S_final.TODO = eps',
            '$test_outputs(S_final.EVENTS) = ' + text(normal_end),
            *driver.common.public('S_final')]
        return values
    if invalid:
        values += ['S_second.RESULT = KNOWN (PBOOL false)',
            '$config_iterator_fresh_aggregate_primitive_key(S_second,pconfigiterator_second,S_second.RESULT)',
            'S_error = $test_fresh_aggregate_step(S_second)',
            'S_error = $throw_scalar(S_second[.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)],"Error",' + text(error) + ',40)',
            'S_error.COMPLETION = THROWN "Error" ' + text(error) + ' 40',
            'S_error.TODO = S_second.TODO', 'S_error.STORE = S_second.STORE',
            'S_error.EVENTS = S_second.EVENTS',
            *driver.common.public('S_error')]
        source = 'S_error'
    else:
        values += [*reach('S_throw', 'S_send', 2),
            'S_throw.TODO = (THROW_SEARCH n_saved) :: (CONFIG_ITERATOR pconfigiterator_throw "key") :: ptask_throw*',
            'pconfigiterator_throw.PRODUCER = (n_aggregate)',
            'pconfigiterator_throw.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_option)]',
            '$string_bytes(pvalue_option) = (' + text('precision') + ')',
            '$weakref_get(S_throw,n_aggregate_watch) = PNULL',
            '$weakref_get(S_throw,n_iterator_watch) = POBJECT n_iterator',
            'S_throw.STORE[n_result_cell] = DEFINED (PINT 99)',
            'S_throw.PRECISIONINI = ' + text('14'),
            '$test_outputs(S_throw.EVENTS) = ' + text(second),
            *driver.common.public('S_throw')]
        source = 'S_throw'
    values += [*reach('S_disposed', source, 5),
        'S_disposed.TODO = (THROW_SEARCH n_pending) :: ptask_disposed*',
        'S_disposed.ITERATORS = eps',
        '~((HOBJECT n_iterator) <- S_disposed.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_disposed),HOBJECT n_iterator) = 0',
        '$weakref_get(S_disposed,n_aggregate_watch) = PNULL',
        '$weakref_get(S_disposed,n_iterator_watch) = PNULL',
        'S_disposed.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_disposed.PRECISIONINI = ' + text('14'),
        '$test_outputs(S_disposed.EVENTS) = ' + text(second),
        *driver.common.public('S_disposed'),
        'S_final = $drive_steps(S_disposed,3000)',
        'S_final.COMPLETION = NORMAL', 'S_final.TODO = eps',
        'S_final.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_final.PRECISIONINI = ' + text('14'),
        '$test_outputs(S_final.EVENTS) = ' + text(invalid_end if invalid else throw_end),
        *driver.common.public('S_final')]
    if not invalid:
        values += ['n_pending = n_saved']
    return values


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['prepare', 'check'], required=True)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
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
