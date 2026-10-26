#!/usr/bin/env python3
"""Reached sole-DATA invalid-key Error and Aggregate receipt cleanup."""
import argparse
import json
import os
from pathlib import Path
import sys

import global_constant_scalar_name_protocol as driver
import config_aggregate_fresh_iterator_protocol as prior
import config_aggregate_fresh_invalid_key_sources as sources


text, b64 = driver.text, driver.b64
PREFIX = prior.PREFIX + r"""
dec $test_fresh_invalid_front(pstate) : bool
def $test_fresh_invalid_front(S) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "key") :: ptask*
  -- if $config_iterator_invalid_primitive_key(S.RESULT)
def $test_fresh_invalid_front(S) = false -- otherwise
dec $test_fresh_invalid_seek(pstate, nat) : pstate
def $test_fresh_invalid_seek(S, 0) = S
def $test_fresh_invalid_seek(S, n) = S
  -- if $(n > 0)
  -- if $test_fresh_invalid_front(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET /\ ~$throwable_pending(S.COMPLETION)) \/ (S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
def $test_fresh_invalid_seek(S, n) = $test_fresh_invalid_seek($drive_steps($test_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_fresh_invalid_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET \/ $throwable_pending(S.COMPLETION)
  -- if ~(S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
"""


def key_reach(start):
    return ['S_key_found = $test_fresh_invalid_seek(' + start + ',3000)',
        r'S_key_found.COMPLETION = NORMAL \/ S_key_found.COMPLETION = BUDGET',
        'S_key = S_key_found[.COMPLETION = NORMAL]',
        '$test_fresh_invalid_front(S_key)']


def checks(program, path, name):
    first = name == 'fresh-null-first-key'
    assert first or name in ('fresh-bool-second-key-rebind', 'fresh-float-second-key-rebind')
    prefix = ('B|G|R|V0|C0|H|K0|H|' if first else
              'B|G|R|V0|C0|H|K0|H|N0|V1|C1|H|K1|H|U|')
    message = 'Keys must be of type int|string during argument unpacking'
    final = prefix + 'E|' + message + '|33|99|14|output_buffering|D|R|14|9'
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *prior.reach('S_pre', 'S_initial', 0),
        'S_pre.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*',
        'pconfigcall.KIND = INTRINSIC_INI_SET', 'pconfigcall.OWNER = eps',
        '$intrinsic_argument(S_pre,pconfigcall.SITE,0) = ((expression,true,eps,porigin_argument,z_argument))',
        'z_argument = 33',
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
        *driver.common.public('S_pre'), *prior.reach('S_return', 'S_pre', 1),
        'S_return.TODO = (CONFIG_AGGREGATE pconfigaggregate) :: ptask_tail*',
        'pconfigaggregate = {CALL pconfigcall,OBJECT n_aggregate,INPUT S_pre.RESULT}',
        'S_return.RESULT = KNOWN (POBJECT n_iterator)',
        '$heap_owners($heap_graph(S_return),HOBJECT n_iterator) = 1',
        '$config_aggregate_return_allowed(S_return,pconfigaggregate)',
        '$lookup(S_return.ENV,' + text('watch') + ') = (n_watch_cell)',
        'S_return.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)',
        'S_return.OBJECTS[n_watch] = WEAKREFERENCE (n_iterator)',
        '$weakref_get(S_return,n_watch) = POBJECT n_iterator',
        '$test_outputs(S_return.EVENTS) = ' + text('B|G|'),
        *driver.common.public('S_return'),
        'S_data = $test_fresh_aggregate_step(S_return)',
        'S_data.TODO = (CONFIG_ITERATOR pconfigiterator_initial "rewind-start") :: ptask_tail*',
        'pconfigiterator_initial = {CALL pconfigcall,ITERATOR S_return.NEXTITER,OBJECT n_iterator,INPUT S_pre.RESULT,PRODUCER (n_aggregate),ITEMS eps,CURRENT (KNOWN PNULL),KEY (KNOWN PNULL)}',
        '$config_iterator_valid(S_data,pconfigiterator_initial,"rewind-start")',
        '$heap_owners($heap_graph(S_data),HOBJECT n_iterator) = 1',
        '~$config_iterator_producer_valid(S_data,pconfigiterator_initial[.PRODUCER = (n_iterator)])',
        *prior.budget('S_return'), *driver.common.public('S_data'),
        *key_reach('S_data'),
        'S_key.TODO = (CONFIG_ITERATOR pconfigiterator "key") :: ptask_key*',
        'pconfigiterator.CALL = pconfigcall',
        'pconfigiterator.OBJECT = n_iterator',
        'pconfigiterator.INPUT = S_pre.RESULT',
        'pconfigiterator.PRODUCER = (n_aggregate)',
        'pconfigiterator.KEY = KNOWN PNULL',
        '$config_iterator_valid(S_key,pconfigiterator,"key")',
        '$config_iterator_producer_valid(S_key,pconfigiterator)',
        '$config_iterator_quiet_aggregate_data(S_key,pconfigiterator)',
        '$heap_owners($heap_graph(S_key),HOBJECT n_iterator) = 1',
        '$weakref_get(S_key,n_watch) = POBJECT n_iterator',
        'S_key.STORE[n_aggregate_hold] = DEFINED (POBJECT n_aggregate)',
        'S_key.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_key.PRECISIONINI = ' + text('14'),
        'pconfigiterator.CURRENT = KNOWN pvalue_current',
        '$string_bytes(pvalue_current) = (' + text('precision' if first else '8') + ')',
        '$config_iterator_fresh_aggregate_primitive_key(S_key,pconfigiterator,S_key.RESULT)',
        '~$config_iterator_live_cv_primitive_key(S_key,pconfigiterator,S_key.RESULT)',
        '~$config_iterator_temp_primitive_key(S_key,pconfigiterator,S_key.RESULT)',
        '~$config_iterator_key_operand(S_key,pconfigiterator,S_key.RESULT)',
        '~$config_iterator_fresh_aggregate_primitive_key(S_key,pconfigiterator[.PRODUCER = eps],S_key.RESULT)',
        '~$config_iterator_fresh_aggregate_primitive_key(S_key,pconfigiterator[.PRODUCER = (n_iterator)],S_key.RESULT)',
        '~$config_iterator_fresh_aggregate_primitive_key(S_key,pconfigiterator,KNOWN (PINT 0))',
        '~$config_iterator_valid(S_key,pconfigiterator[.CALL = pconfigcall[.SITE = PORIGIN 999 eps]],"key")',
        '$test_outputs(S_key.EVENTS) = ' + text(prefix),
        *driver.common.public('S_key')]
    if first:
        values += ['pconfigiterator.ITEMS = eps', 'S_key.RESULT = KNOWN PNULL',
            'S_key.STORE[n_aggregate_cell] = DEFINED (POBJECT n_aggregate)',
            '$heap_owners($heap_graph(S_key),HOBJECT n_aggregate) = 2']
    else:
        values += ['pconfigiterator.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_option)]',
            '$string_bytes(pvalue_option) = (' + text('precision') + ')',
            'S_key.STORE[n_aggregate_cell] = DEFINED PNULL',
            '$heap_owners($heap_graph(S_key),HOBJECT n_aggregate) = 1',
            'S_key.RESULT = KNOWN ' + ('(PBOOL false)' if name.startswith('fresh-bool-') else '(PFLOAT n_float)')]
    values += [
        'S_error = $test_fresh_aggregate_step(S_key)',
        'S_error = $throw_scalar(S_key[.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)],"Error",' + text(message) + ',33)',
        'S_error.COMPLETION = THROWN "Error" ' + text(message) + ' 33',
        'S_error.TODO = S_key.TODO', 'S_error.STORE = S_key.STORE',
        'S_error.EVENTS = S_key.EVENTS', 'S_error.PRECISIONINI = S_key.PRECISIONINI',
        *prior.budget('S_key'), *driver.common.public('S_error'),
        *prior.reach('S_disposed', 'S_error', 5),
        'S_disposed.TODO = (THROW_SEARCH n_error) :: ptask_disposed*',
        '$throwable_live(S_disposed,n_error)',
        '$string_bytes($throwable_field(S_disposed,n_error,"message")) = (' + text(message) + ')',
        '$throwable_field(S_disposed,n_error,"line") = PINT 33',
        'S_disposed.ITERATORS = eps',
        '$test_fresh_aggregate_tasks(S_disposed.TODO)',
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
        '$test_outputs(S_final.EVENTS) = ' + text(final),
        *driver.common.public('S_final')]
    return values


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['prepare', 'check'], required=True)
    parser.add_argument('--case', action='append', default=[])
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    frozen = dict(sources.family.CASES)
    selected = args.case or list(frozen)[:3]
    assert len(selected) == len(set(selected)) and set(selected) <= frozen.keys()
    sources.family.CASES = {name: frozen[name] for name in selected}
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
