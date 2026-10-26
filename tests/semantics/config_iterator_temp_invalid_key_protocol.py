#!/usr/bin/env python3
"""Reached temporary Iterator invalid-key Error and DATA/INPUT cleanup."""
import argparse
import json
import os
from pathlib import Path
import sys

import global_constant_scalar_name_protocol as driver
import config_iterator_temp_invalid_key_sources as sources


text, b64 = driver.text, driver.b64
PREFIX = r"""
dec $test_temp_bad_key_task(ptask) : bool
def $test_temp_bad_key_task(CONFIG_ITERATOR pconfigiterator text) = true
def $test_temp_bad_key_task(ptask) = false -- otherwise
dec $test_temp_bad_key_tasks(ptask*) : bool
def $test_temp_bad_key_tasks(eps) = true
def $test_temp_bad_key_tasks(ptask :: ptask_tail*) = (~$test_temp_bad_key_task(ptask) /\ $test_temp_bad_key_tasks(ptask_tail*))
dec $test_temp_bad_key_front(pstate, nat) : bool
def $test_temp_bad_key_front(S, 0) = true
  -- if S.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_temp_bad_key_front(S, 1) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "key") :: ptask*
  -- if $config_iterator_invalid_primitive_key(S.RESULT)
def $test_temp_bad_key_front(S, 2) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_ITERATOR pconfigiterator "input-release") :: ptask*
  -- if $useriter_cursor_count(S.ITERATORS,pconfigiterator.ITERATOR) = 0
def $test_temp_bad_key_front(S, 3) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask*
  -- if S.ITERATORS = eps
  -- if $test_temp_bad_key_tasks(S.TODO)
def $test_temp_bad_key_front(S, n_stage) = false -- otherwise
dec $test_temp_bad_key_seek(pstate, nat, nat) : pstate
def $test_temp_bad_key_seek(S, n_stage, 0) = S
def $test_temp_bad_key_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_temp_bad_key_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET /\ ~$throwable_pending(S.COMPLETION)) \/ (S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
def $test_temp_bad_key_seek(S, n_stage, n) = $test_temp_bad_key_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_temp_bad_key_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET \/ $throwable_pending(S.COMPLETION)
  -- if ~(S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
dec $test_temp_bad_key_step(pstate) : pstate
def $test_temp_bad_key_step(S) = S_next
  -- PhpStep: S ~> S_next
"""


def reach(state, start, stage):
    return [state + '_found = $test_temp_bad_key_seek(' + start + ',' + str(stage) + ',3000)',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_temp_bad_key_front(' + state + ',' + str(stage) + ')']


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)',
        state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)',
        state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def checks(program, path, name):
    retained = name == 'retained-second-bool-key-keeps-input'
    first_key = name == 'sole-first-null-key-retires-input'
    assert retained or first_key or name == 'sole-second-float-key-retires-input'
    owners_pre = '2' if retained else '1'
    owners_key = '3' if retained else '2'
    owners_input = '2' if retained else '1'
    owners_done = '1' if retained else '0'
    prefix = 'B|P|R|V0|C0|K0|H|' if first_key else 'B|P|R|V0|C0|K0|H|N0|V1|C1|K1|H|'
    v1 = '8' if first_key else 'precision'
    key_index = '0' if first_key else '1'
    death = 'H' if retained else 'D'
    message = 'Keys must be of type int|string during argument unpacking'
    final = prefix + 'E|' + message + '|31|99|14|' + key_index + '|8|' + v1 + '|' + death + '|F'
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *reach('S_pre','S_initial',0),
        'S_pre.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*',
        'pconfigcall.KIND = INTRINSIC_INI_SET', 'pconfigcall.OWNER = eps',
        '$intrinsic_argument(S_pre,pconfigcall.SITE,0) = ((expression,true,eps,PORIGIN n_source pcpath_argument,z_argument))',
        'z_argument = 31',
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
        '$lookup(S_pre.ENV,' + text('hold') + ') = (n_hold_cell)',
        'S_pre.STORE[n_hold_cell] = DEFINED ' + ('(POBJECT n_object)' if retained else 'PNULL'),
        '$lookup(S_pre.ENV,' + text('result') + ') = (n_result_cell)',
        'S_pre.STORE[n_result_cell] = DEFINED (PINT 99)',
        '$heap_owners($heap_graph(S_pre),HOBJECT n_object) = ' + owners_pre,
        'pconfigiterator_initial = {CALL pconfigcall,ITERATOR S_pre.NEXTITER,OBJECT n_object,INPUT S_pre.RESULT,PRODUCER eps,ITEMS eps,CURRENT (KNOWN PNULL),KEY (KNOWN PNULL)}',
        '$config_iterator_input(S_pre,pconfigiterator_initial)',
        '$config_iterator_start(S_pre,pconfigcall,S_pre.RESULT,n_object)',
        '$config_iterator_owning_input(pconfigiterator_initial)',
        '$test_outputs(S_pre.EVENTS) = ' + text('B|P|'),
        *driver.common.public('S_pre'),
        'S_start = $test_temp_bad_key_step(S_pre)',
        'S_start.TODO = (CONFIG_ITERATOR pconfigiterator_initial "rewind-start") :: ptask_tail*',
        '$task_nodes(CONFIG_ITERATOR pconfigiterator_initial "rewind-start") = [HOBJECT n_object,HOBJECT n_object]',
        '$heap_owners($heap_graph(S_start),HOBJECT n_object) = ' + owners_key,
        *reach('S_key','S_start',1),
        'S_key.TODO = (CONFIG_ITERATOR pconfigiterator "key") :: ptask_key*',
        'pconfigiterator.CALL = pconfigcall',
        'pconfigiterator.OBJECT = n_object',
        'pconfigiterator.INPUT = S_pre.RESULT',
        'pconfigiterator.KEY = KNOWN PNULL',
        '$config_iterator_valid(S_key,pconfigiterator,"key")',
        '$config_iterator_temp_primitive_key(S_key,pconfigiterator,S_key.RESULT)',
        '~$config_iterator_live_cv_primitive_key(S_key,pconfigiterator,S_key.RESULT)',
        '~$config_iterator_key_operand(S_key,pconfigiterator,S_key.RESULT)',
        '~$config_iterator_temp_primitive_key(S_key,pconfigiterator,KNOWN (PINT 0))',
        '~$config_iterator_temp_primitive_key(S_key,pconfigiterator[.INPUT = KNOWN PNULL],S_key.RESULT)',
        '~$config_iterator_input(S_key[.CODE = eps],pconfigiterator)',
        '~$config_iterator_valid(S_key,pconfigiterator[.CALL = pconfigcall[.SITE = PORIGIN 999 eps]],"key")',
        '$intrinsic_argument(S_key,pconfigcall.SITE,0) = ((expression,true,eps,PORIGIN n_source pcpath_argument,31))',
        '$heap_owners($heap_graph(S_key),HOBJECT n_object) = ' + owners_key,
        '$weakref_get(S_key,n_watch) = POBJECT n_object',
        '$lookup(S_key.ENV,' + text('v0') + ') = (n_v0_cell)',
        'S_key.STORE[n_v0_cell] = DEFINED pvalue_v0',
        '$string_bytes(pvalue_v0) = (' + text('8') + ')',
        '$lookup(S_key.ENV,' + text('v1') + ') = (n_v1_cell)',
        'S_key.STORE[n_v1_cell] = DEFINED pvalue_v1',
        '$string_bytes(pvalue_v1) = (' + text(v1) + ')',
        'pconfigiterator.CURRENT = KNOWN pvalue_current',
        '$string_bytes(pvalue_current) = (' + text('precision' if first_key else '8') + ')',
        'S_key.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_key.PRECISIONINI = ' + text('14'),
        '$test_outputs(S_key.EVENTS) = ' + text(prefix),
        *driver.common.public('S_key')]
    if first_key:
        values += ['pconfigiterator.ITEMS = eps', 'S_key.RESULT = KNOWN PNULL']
    else:
        values += ['pconfigiterator.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_option)]',
            '$string_bytes(pvalue_option) = (' + text('precision') + ')',
            'S_key.RESULT = KNOWN ' + ('(PBOOL true)' if retained else '(PFLOAT n_float)')]
    values += [
        'S_error = $test_temp_bad_key_step(S_key)',
        'S_error = $throw_scalar(S_key[.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)],"Error",' + text(message) + ',31)',
        'S_error.COMPLETION = THROWN "Error" ' + text(message) + ' 31',
        'S_error.RESULT = KNOWN PNULL',
        'S_error.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_error.TODO = S_key.TODO',
        'S_error.ITERATORS = S_key.ITERATORS',
        'S_error.STORE = S_key.STORE',
        'S_error.EVENTS = S_key.EVENTS',
        'S_error.PRECISIONINI = S_key.PRECISIONINI',
        *budget('S_key'), *driver.common.public('S_error'),
        *reach('S_input','S_error',2),
        'S_input.TODO = (THROW_SEARCH n_error) :: (CONFIG_ITERATOR pconfigiterator_cleared "input-release") :: ptask_input*',
        'pconfigiterator_cleared = pconfigiterator[.CURRENT = KNOWN PNULL][.KEY = KNOWN PNULL]',
        '$config_iterator_valid(S_input[.TODO = (CONFIG_ITERATOR pconfigiterator_cleared "input-release") :: ptask_input*],pconfigiterator_cleared,"input-release")',
        '$task_nodes(CONFIG_ITERATOR pconfigiterator_cleared "input-release") = [HOBJECT n_object]',
        '$heap_owners($heap_graph(S_input),HOBJECT n_object) = ' + owners_input,
        '$weakref_get(S_input,n_watch) = POBJECT n_object',
        'S_input.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_input.PRECISIONINI = ' + text('14'),
        '$test_outputs(S_input.EVENTS) = ' + text(prefix),
        *budget('S_input'), *driver.common.public('S_input'),
        *reach('S_disposed','S_input',3),
        'S_disposed.TODO = (THROW_SEARCH n_error) :: ptask_disposed*',
        '$throwable_live(S_disposed,n_error)',
        'S_disposed.OBJECTS[n_error] = THROWABLE pthrowable_error',
        'pthrowable_error.KIND = "Error"',
        '$string_bytes($throwable_field(S_disposed,n_error,"message")) = (' + text(message) + ')',
        '$throwable_field(S_disposed,n_error,"line") = PINT 31',
        'S_disposed.ITERATORS = eps',
        '$test_temp_bad_key_tasks(S_disposed.TODO)',
        '$heap_owners($heap_graph(S_disposed),HOBJECT n_object) = ' + owners_done,
        '$weakref_get(S_disposed,n_watch) = ' + ('POBJECT n_object' if retained else 'PNULL'),
        'S_disposed.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_disposed.PRECISIONINI = ' + text('14'),
        '$test_outputs(S_disposed.EVENTS) = ' + text(prefix),
        *driver.common.public('S_disposed'),
        'S_final = $drive_steps(S_disposed,3000)',
        'S_final.COMPLETION = NORMAL', 'S_final.TODO = eps',
        'S_final.ITERATORS = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_final.PRECISIONINI = ' + text('14'),
        '$test_outputs(S_final.EVENTS) = ' + text(final),
        *driver.common.public('S_final')]
    if retained:
        values += ['(HOBJECT n_object) <- S_disposed.ALLOCATIONS']
    else:
        values += ['~((HOBJECT n_object) <- S_disposed.ALLOCATIONS)']
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
