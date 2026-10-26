#!/usr/bin/env python3
"""Reached temporary Iterator DATA, INPUT, API, and key-throw cleanup."""
import argparse
import json
import os
from pathlib import Path
import sys

import global_constant_scalar_name_protocol as driver
import config_iterator_temp_call_sources as sources


text, b64 = driver.text, driver.b64
PREFIX = r"""
dec $test_temp_iterator_front(pstate, nat) : bool
def $test_temp_iterator_front(S, 0) = true
  -- if S.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_temp_iterator_front(S, 1) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "finish") :: ptask*
def $test_temp_iterator_front(S, 2) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "input-release") :: ptask*
  -- if $useriter_cursor_count(S.ITERATORS,pconfigiterator.ITERATOR) = 0
def $test_temp_iterator_front(S, 3) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "ready") :: ptask*
def $test_temp_iterator_front(S, 4) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_ITERATOR pconfigiterator "key") :: ptask*
def $test_temp_iterator_front(S, 5) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_ITERATOR pconfigiterator "input-release") :: ptask*
  -- if $useriter_cursor_count(S.ITERATORS,pconfigiterator.ITERATOR) = 0
def $test_temp_iterator_front(S, 6) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask*
  -- if S.ITERATORS = eps
  -- if $useriter_tasks_ids(S.TODO) = eps
def $test_temp_iterator_front(S, n_stage) = false -- otherwise
dec $test_temp_iterator_seek(pstate, nat, nat) : pstate
def $test_temp_iterator_seek(S, n_stage, 0) = S
def $test_temp_iterator_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_temp_iterator_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET /\ ~$throwable_pending(S.COMPLETION)) \/ (S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
def $test_temp_iterator_seek(S, n_stage, n) = $test_temp_iterator_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_temp_iterator_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET \/ $throwable_pending(S.COMPLETION)
  -- if ~(S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
dec $test_temp_iterator_step(pstate) : pstate
def $test_temp_iterator_step(S) = S_next
  -- PhpStep: S ~> S_next
"""


def reach(state, start, stage):
    return [state + '_found = $test_temp_iterator_seek(' + start + ',' + str(stage) + ',3000)',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_temp_iterator_front(' + state + ',' + str(stage) + ')']


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)',
        state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)',
        state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def checks(program, path, name):
    retained = name == 'retained-factory-iterator-drains-before-api'
    throwing = name == 'factory-iterator-key-throw-cancels-api'
    assert retained or throwing or name == 'sole-factory-iterator-input-retires-before-api'
    first = '2' if retained else '1'
    second = '3' if retained else '2'
    last = '1' if retained else '0'
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *reach('S_pre','S_initial',0),
        'S_pre.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*',
        'pconfigcall.KIND = INTRINSIC_INI_SET', 'pconfigcall.OWNER = eps',
        '$intrinsic_argument(S_pre,pconfigcall.SITE,0) = ((expression,true,eps,PORIGIN n_source pcpath_argument,z_argument))',
        'expression = NExprFuncCall name (SEQUENCE eps) metadata',
        '$source_emission_noarg_call(S_pre,n_source,pcpath_argument,expression) = (z_call)',
        '$code_at(S_pre.CODE,n_source) = (pcode)',
        '$source_unit(S_pre.SOURCES,n_source) = (pcunit)',
        '$ppunpack_class(pcode,pcunit,pcpath_argument) = (UNPACK_VAR)',
        '$code_name(pcode.NAMES,pcpath_argument) = ((preqbytes_factory,eps))',
        '$call_target(S_pre,preqbytes_factory,eps) = (pfunction_factory)',
        'pfunction_factory.SIGNATURE.PARAMETERS = eps',
        '~pfunction_factory.SIGNATURE.BYREF',
        'S_pre.RESULT = KNOWN (POBJECT n_object)',
        '$useriter_instance(S_pre,n_object)',
        '$lookup(S_pre.ENV,' + text('watch') + ') = (n_watch_cell)',
        'S_pre.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)',
        'S_pre.OBJECTS[n_watch] = WEAKREFERENCE (n_object)',
        '$weakref_get(S_pre,n_watch) = POBJECT n_object',
        '$lookup(S_pre.ENV,' + text('result') + ') = (n_result_cell)',
        'S_pre.STORE[n_result_cell] = DEFINED (PINT 99)',
        '$lookup(S_pre.ENV,' + text('hold') + ') = (n_hold_cell)',
        'S_pre.STORE[n_hold_cell] = DEFINED ' + ('(POBJECT n_object)' if retained else 'PNULL'),
        '$heap_owners($heap_graph(S_pre),HOBJECT n_object) = ' + first,
        'n_iterator = S_pre.NEXTITER',
        'pconfigiterator_initial = {CALL pconfigcall,ITERATOR n_iterator,OBJECT n_object,INPUT S_pre.RESULT,ITEMS eps,CURRENT (KNOWN PNULL),KEY (KNOWN PNULL)}',
        '$config_iterator_input(S_pre,pconfigiterator_initial)',
        '$config_iterator_start(S_pre,pconfigcall,S_pre.RESULT,n_object)',
        '$config_iterator_owning_input(pconfigiterator_initial)',
        '$config_iterator_input_nodes(pconfigiterator_initial) = [HOBJECT n_object]',
        '$test_outputs(S_pre.EVENTS) = ' + text('B|P|'),
        *driver.common.public('S_pre'),
        'S_start = $test_temp_iterator_step(S_pre)',
        'S_start.TODO = (CONFIG_ITERATOR pconfigiterator_initial "rewind-start") :: ptask_tail*',
        '$config_iterator_valid(S_start,pconfigiterator_initial,"rewind-start")',
        '$task_nodes(CONFIG_ITERATOR pconfigiterator_initial "rewind-start") = [HOBJECT n_object,HOBJECT n_object]',
        '$heap_owners($heap_graph(S_start),HOBJECT n_object) = ' + second,
        '$iterator_lookup(S_start.ITERATORS,n_iterator) = (OBJECTITER n_iterator n_object 0 false)',
        '~$config_iterator_input(S_start,pconfigiterator_initial[.INPUT = KNOWN PNULL])',
        '~$config_iterator_input(S_start[.CODE = eps],pconfigiterator_initial)',
        '~$config_iterator_key_input(pconfigiterator_initial,PSTRING ' + text('option') + ')',
        '$config_iterator_send_key(S_start,pconfigiterator_initial,PSTRING ' + text('0') + ') = eps',
        '~$config_iterator_items(S_start,pconfigiterator_initial,[ENTRY (KSTRING ' + text('option') + ') (DIRECT (PSTRING ' + text('precision') + '))])',
        '~$config_iterator_scope(S_start,pconfigiterator_initial[.CALL = pconfigcall[.SITE = PORIGIN 999 eps]])',
        *budget('S_pre'), *driver.common.public('S_start')]
    if throwing:
        values += [*reach('S_throw','S_start',4),
            'S_throw.TODO = (THROW_SEARCH n_exception) :: (CONFIG_ITERATOR pconfigiterator_throw "key") :: ptask_tail*',
            'pconfigiterator_throw.CALL = pconfigcall',
            'pconfigiterator_throw.INPUT = S_pre.RESULT',
            'pconfigiterator_throw.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_option)]',
            '$string_bytes(pvalue_option) = (' + text('precision') + ')',
            'pconfigiterator_throw.CURRENT = KNOWN pvalue_current',
            '$string_bytes(pvalue_current) = (' + text('8') + ')',
            'pconfigiterator_throw.KEY = KNOWN PNULL',
            '$config_iterator_valid(S_throw,pconfigiterator_throw,"key")',
            '$heap_owners($heap_graph(S_throw),HOBJECT n_object) = 2',
            '$weakref_get(S_throw,n_watch) = POBJECT n_object',
            '$test_outputs(S_throw.EVENTS) = ' + text('B|P|R|V0|C0|H|K0|N0|V1|C1|H|K1|T|'),
            'S_throw.STORE[n_result_cell] = DEFINED (PINT 99)',
            *driver.common.public('S_throw'),
            'S_scope = S_throw[.TODO = (THROW_SEARCH n_exception) :: ptask_tail*]',
            'S_staged = $config_iterator_discard_state(S_scope,pconfigiterator_throw,"key")',
            'S_staged.TODO = (THROW_SEARCH n_exception) :: (CONFIG_ITERATOR pconfigiterator_cleared "input-release") :: ptask_tail*',
            'pconfigiterator_cleared = pconfigiterator_throw[.CURRENT = KNOWN PNULL][.KEY = KNOWN PNULL]',
            '$config_iterator_discard_nodes(pconfigiterator_throw,"key") = [HOBJECT n_object]',
            *reach('S_input','S_throw',5),
            'S_input.TODO = (THROW_SEARCH n_exception) :: (CONFIG_ITERATOR pconfigiterator_cleared "input-release") :: ptask_input*',
            '$config_iterator_valid(S_input[.TODO = (CONFIG_ITERATOR pconfigiterator_cleared "input-release") :: ptask_input*],pconfigiterator_cleared,"input-release")',
            '$task_nodes(CONFIG_ITERATOR pconfigiterator_cleared "input-release") = [HOBJECT n_object]',
            '$heap_owners($heap_graph(S_input),HOBJECT n_object) = 1',
            '$weakref_get(S_input,n_watch) = POBJECT n_object',
            '$config_iterator_quiet_input(S_input,pconfigiterator_cleared)',
            'S_input.STORE[n_result_cell] = DEFINED (PINT 99)',
            '$test_outputs(S_input.EVENTS) = $test_outputs(S_throw.EVENTS)',
            *budget('S_input'), *driver.common.public('S_input'),
            *reach('S_disposed','S_input',6),
            'S_disposed.TODO = (THROW_SEARCH n_exception) :: ptask_disposed*',
            '$heap_owners($heap_graph(S_disposed),HOBJECT n_object) = 0',
            '~((HOBJECT n_object) <- S_disposed.ALLOCATIONS)',
            '$weakref_get(S_disposed,n_watch) = PNULL',
            'S_disposed.STORE[n_result_cell] = DEFINED (PINT 99)',
            '$test_outputs(S_disposed.EVENTS) = $test_outputs(S_throw.EVENTS)',
            *driver.common.public('S_disposed'),
            'S_final = $drive_steps(S_disposed,3000)',
            'S_final.COMPLETION = NORMAL', 'S_final.TODO = eps',
            'S_final.ITERATORS = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
            'S_final.STORE[n_result_cell] = DEFINED (PINT 99)',
            'S_final.PRECISIONINI = ' + text('14'),
            '$test_outputs(S_final.EVENTS) = ' + text('B|P|R|V0|C0|H|K0|N0|V1|C1|H|K1|T|I|99|14|D'),
            *driver.common.public('S_final')]
        return values
    values += [*reach('S_finish','S_start',1),
        'S_finish.TODO = (CONFIG_ITERATOR pconfigiterator "finish") :: ptask_tail*',
        'pconfigiterator.CALL = pconfigcall',
        'pconfigiterator.INPUT = S_pre.RESULT',
        'pconfigiterator.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_option),ENTRY (KINT 1) (DIRECT pvalue_value)]',
        '$string_bytes(pvalue_option) = (' + text('precision') + ')',
        '$string_bytes(pvalue_value) = (' + text('8') + ')',
        '$config_iterator_valid(S_finish,pconfigiterator,"finish")',
        '$heap_owners($heap_graph(S_finish),HOBJECT n_object) = ' + second,
        '$weakref_get(S_finish,n_watch) = POBJECT n_object',
        'S_finish.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_finish.PRECISIONINI = ' + text('14'),
        '$test_outputs(S_finish.EVENTS) = ' + text('B|P|R|V0|C0|H|K0|N0|V1|C1|H|K1|N1|V2|'),
        *driver.common.public('S_finish'),
        'S_raw_data = $test_temp_iterator_step(S_finish)',
        'S_raw_data = $config_iterator_finish(S_finish,pconfigiterator,ptask_tail*)',
        *reach('S_input','S_finish',2),
        'S_input.TODO = (CONFIG_ITERATOR pconfigiterator "input-release") :: ptask_tail*',
        '$config_iterator_valid(S_input,pconfigiterator,"input-release")',
        '$task_nodes(CONFIG_ITERATOR pconfigiterator "input-release") = [HOBJECT n_object]',
        '$heap_owners($heap_graph(S_input),HOBJECT n_object) = ' + first,
        '$weakref_get(S_input,n_watch) = POBJECT n_object',
        '$config_iterator_quiet_input(S_input,pconfigiterator)',
        'S_input.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_input.EVENTS = S_finish.EVENTS',
        *budget('S_input'), *driver.common.public('S_input'),
        'S_raw_input = $test_temp_iterator_step(S_input)',
        'S_raw_input = $config_iterator_release_input(S_input,pconfigiterator,ptask_tail*)',
        *reach('S_ready','S_input',3),
        'S_ready.TODO = (CONFIG_ITERATOR pconfigiterator "ready") :: ptask_tail*',
        '$config_iterator_valid(S_ready,pconfigiterator,"ready")',
        '$task_nodes(CONFIG_ITERATOR pconfigiterator "ready") = eps',
        '$heap_owners($heap_graph(S_ready),HOBJECT n_object) = ' + last,
        'S_ready.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_ready.PRECISIONINI = ' + text('14'),
        'S_ready.EVENTS = S_finish.EVENTS',
        *driver.common.public('S_ready')]
    if retained:
        values += ['$config_iterator_scope(S_ready,pconfigiterator)',
            '$weakref_get(S_ready,n_watch) = POBJECT n_object']
    else:
        values += ['$config_iterator_retired_scope(S_ready,pconfigiterator)',
            '~$config_iterator_scope(S_ready,pconfigiterator)',
            '~((HOBJECT n_object) <- S_ready.ALLOCATIONS)',
            '$weakref_get(S_ready,n_watch) = PNULL',
            '~$config_iterator_retired_scope(S_ready[.OBJECTS[n_object] = STDINSTANCE],pconfigiterator)']
    values += [*driver.common.step('S_after','S_ready'),
        'S_after.TODO = ptask_tail*',
        'S_after.RESULT = KNOWN pvalue_old',
        '$string_bytes(pvalue_old) = (' + text('14') + ')',
        'S_after.PRECISIONINI = ' + text('8'),
        'S_after.STORE[n_result_cell] = DEFINED (PINT 99)',
        *budget('S_finish'), *driver.common.public('S_after'),
        'S_final = $drive_steps(S_after,3000)',
        'S_final.COMPLETION = NORMAL', 'S_final.TODO = eps',
        'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.ITERATORS = eps',
        '$test_outputs(S_final.EVENTS) = ' + text('B|P|R|V0|C0|H|K0|N0|V1|C1|H|K1|N1|V2|A|14|8|' + ('2|H' if retained else 'D')),
        *driver.common.public('S_final')]
    return values


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['prepare', 'check'], required=True)
    parser.add_argument('--case', action='append', default=[])
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    cases = dict(sources.family.CASES)
    selected = args.case or list(cases)
    assert len(selected) == len(set(selected)) and set(selected) <= cases.keys()
    sources.family.CASES = {name: cases[name] for name in selected}
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    sys.argv = [sys.argv[0], '--phase', args.phase, '--sources', str(args.sources),
                '--output', str(args.output)]
    driver.main()


if __name__ == '__main__':
    main()
