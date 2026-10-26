#!/usr/bin/env python3
"""Reached invalid Iterator-key Error, cached current, and throw cleanup."""
import argparse
import json
import os
from pathlib import Path
import sys

import global_constant_scalar_name_protocol as driver
import config_iterator_invalid_key_sources as sources


text, b64 = driver.text, driver.b64
PREFIX = r"""
dec $test_invalid_iterator_task(ptask) : bool
def $test_invalid_iterator_task(CONFIG_ITERATOR pconfigiterator text) = true
def $test_invalid_iterator_task(ptask) = false -- otherwise
dec $test_invalid_iterator_tasks(ptask*) : bool
def $test_invalid_iterator_tasks(eps) = true
def $test_invalid_iterator_tasks(ptask :: ptask_tail*) = (~$test_invalid_iterator_task(ptask) /\ $test_invalid_iterator_tasks(ptask_tail*))
dec $test_invalid_iterator_front(pstate, nat) : bool
def $test_invalid_iterator_front(S, 0) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "key") :: ptask*
  -- if $config_iterator_invalid_primitive_key(S.RESULT)
def $test_invalid_iterator_front(S, 1) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_ITERATOR pconfigiterator "key") :: ptask*
def $test_invalid_iterator_front(S, 2) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask*
  -- if S.ITERATORS = eps
  -- if S.DESTRUCTION.OPERATIONS = eps
  -- if $test_invalid_iterator_tasks(S.TODO)
def $test_invalid_iterator_front(S, n_stage) = false -- otherwise
dec $test_invalid_iterator_seek(pstate, nat, nat) : pstate
def $test_invalid_iterator_seek(S, n_stage, 0) = S
def $test_invalid_iterator_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_invalid_iterator_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET /\ ~$throwable_pending(S.COMPLETION)) \/ (S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
def $test_invalid_iterator_seek(S, n_stage, n) = $test_invalid_iterator_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_invalid_iterator_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET \/ $throwable_pending(S.COMPLETION)
  -- if ~(S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
dec $test_invalid_iterator_step(pstate) : pstate
def $test_invalid_iterator_step(S) = S_next
  -- PhpStep: S ~> S_next
"""


def reach(name, start, stage):
    return [name + '_found = $test_invalid_iterator_seek(' + start + ',' + str(stage) + ',3000)',
        name + r'_found.COMPLETION = NORMAL \/ ' + name + '_found.COMPLETION = BUDGET',
        name + ' = ' + name + '_found[.COMPLETION = NORMAL]',
        '$test_invalid_iterator_front(' + name + ',' + str(stage) + ')']


def budget(name):
    return [name + '_pause = $drive_steps(' + name + ',0)',
        name + '_pause = ' + name + '[.COMPLETION = BUDGET]',
        name + '_one = $drive_steps(' + name + ',1)',
        name + '_one = $drive_steps(' + name + '_pause[.COMPLETION = NORMAL],1)']


def checks(program, path, name):
    first = name == 'null-first-key-stops-before-send'
    assert first or name in {'null-second-key-abandons-first-send',
        'bool-second-key-abandons-first-send', 'float-second-key-abandons-first-send'}
    prefix = 'B|R|V0|C0|K0|' if first else 'B|R|V0|C0|K0|N0|V1|C1|K1|'
    option = '8' if first else 'output_buffering'
    index = '0' if first else '1'
    message = 'Keys must be of type int|string during argument unpacking'
    final = prefix + 'E|' + message + '|23|99|14|' + index + '|output_buffering|' + option + '|F'
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *reach('S_key','S_initial',0),
        'S_key.TODO = (CONFIG_ITERATOR pconfigiterator "key") :: ptask_tail*',
        'pconfigiterator.CALL.KIND = INTRINSIC_INI_SET',
        'pconfigiterator.INPUT = VARIABLE ' + text('it') + ' z_argument',
        '$intrinsic_argument(S_key,pconfigiterator.CALL.SITE,0) = ((expression,true,eps,porigin_argument,z_argument))',
        'z_argument = 23', 'S_key.ORIGIN = (porigin_argument)',
        '$config_iterator_input(S_key,pconfigiterator)',
        '$config_iterator_valid(S_key,pconfigiterator,"key")',
        '$heap_owners($heap_graph(S_key),HOBJECT pconfigiterator.OBJECT) = 2',
        '$lookup(S_key.ENV,' + text('it') + ') = (n_iterator_cell)',
        'S_key.STORE[n_iterator_cell] = DEFINED (POBJECT pconfigiterator.OBJECT)',
        '$lookup(S_key.ENV,' + text('result') + ') = (n_result_cell)',
        'S_key.STORE[n_result_cell] = DEFINED (PINT 99)',
        '$lookup(S_key.ENV,' + text('v0') + ') = (n_v0_cell)',
        'S_key.STORE[n_v0_cell] = DEFINED pvalue_v0',
        '$string_bytes(pvalue_v0) = (' + text('output_buffering') + ')',
        '$lookup(S_key.ENV,' + text('v1') + ') = (n_v1_cell)',
        'S_key.STORE[n_v1_cell] = DEFINED pvalue_v1',
        '$string_bytes(pvalue_v1) = (' + text(option) + ')',
        'pconfigiterator.CURRENT = KNOWN pvalue_current',
        '$string_bytes(pvalue_current) = (' + text('precision' if first else '8') + ')',
        'pconfigiterator.KEY = KNOWN PNULL',
        '$config_iterator_live_cv_primitive_key(S_key,pconfigiterator,S_key.RESULT)',
        '~$config_iterator_key_operand(S_key,pconfigiterator,S_key.RESULT)',
        'S_key.PRECISIONINI = ' + text('14'),
        '$test_outputs(S_key.EVENTS) = ' + text(prefix),
        *driver.common.public('S_key')]
    if first:
        values += ['pconfigiterator.ITEMS = eps', 'S_key.RESULT = KNOWN PNULL']
    else:
        values += ['pconfigiterator.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_option)]',
            '$string_bytes(pvalue_option) = (' + text('precision') + ')']
        if name.startswith('null-'):
            values += ['S_key.RESULT = KNOWN PNULL']
        elif name.startswith('bool-'):
            values += ['S_key.RESULT = KNOWN (PBOOL true)']
        else:
            values += ['S_key.RESULT = KNOWN (PFLOAT n_float)']
    values += [
        '~$config_iterator_invalid_primitive_key(KNOWN (PINT 0))',
        '~$config_iterator_live_cv_primitive_key(S_key,pconfigiterator[.INPUT = KNOWN (POBJECT pconfigiterator.OBJECT)],S_key.RESULT)',
        '~$config_iterator_live_cv_primitive_key(S_key[.STORE[n_iterator_cell] = DEFINED PNULL],pconfigiterator,S_key.RESULT)',
        '~$config_iterator_valid(S_key,pconfigiterator[.CALL = pconfigiterator.CALL[.SITE = PORIGIN 999 eps]],"key")',
        'S_error = $test_invalid_iterator_step(S_key)',
        'S_error = $throw_scalar(S_key[.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)],"Error",' + text(message) + ',23)',
        'S_error.COMPLETION = THROWN "Error" ' + text(message) + ' 23',
        'S_error.RESULT = KNOWN PNULL',
        'S_error.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_error.TODO = S_key.TODO',
        'S_error.STORE = S_key.STORE',
        'S_error.EVENTS = S_key.EVENTS',
        'S_error.PRECISIONINI = S_key.PRECISIONINI',
        *budget('S_key'), *driver.common.public('S_error'),
        *reach('S_throw','S_error',1),
        'S_throw.TODO = (THROW_SEARCH n_error) :: (CONFIG_ITERATOR pconfigiterator "key") :: ptask_tail*',
        '$throwable_live(S_throw,n_error)',
        'S_throw.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_throw.PRECISIONINI = ' + text('14'),
        '$test_outputs(S_throw.EVENTS) = ' + text(prefix),
        *driver.common.public('S_throw'),
        *reach('S_disposed','S_throw',2),
        'S_disposed.TODO = (THROW_SEARCH n_error) :: ptask_disposed*',
        'S_disposed.ITERATORS = eps',
        '$test_invalid_iterator_tasks(S_disposed.TODO)',
        '$heap_owners($heap_graph(S_disposed),HOBJECT pconfigiterator.OBJECT) = 1',
        '(HOBJECT pconfigiterator.OBJECT) <- S_disposed.ALLOCATIONS',
        'S_disposed.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_disposed.PRECISIONINI = ' + text('14'),
        '$test_outputs(S_disposed.EVENTS) = ' + text(prefix),
        *driver.common.public('S_disposed'),
        'S_final = $drive_steps(S_disposed,3000)',
        'S_final.COMPLETION = NORMAL', 'S_final.TODO = eps',
        'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.ITERATORS = eps',
        'S_final.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_final.PRECISIONINI = ' + text('14'),
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
    cases = dict(sources.family.CASES)
    selected = args.case or ['null-first-key-stops-before-send',
        'bool-second-key-abandons-first-send', 'float-second-key-abandons-first-send']
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
