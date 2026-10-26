#!/usr/bin/env python3
"""Reached named Iterator send, cached current, and early throw cleanup."""
import argparse
import json
import os
from pathlib import Path
import sys

import global_constant_scalar_name_protocol as driver
import config_iterator_named_unpack_sources as sources


text, b64 = driver.text, driver.b64
PREFIX = r"""
dec $test_named_iterator_front(pstate, nat) : bool
def $test_named_iterator_front(S, 0) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "send") :: ptask_tail*
  -- if pconfigiterator.ITEMS = eps
  -- if pconfigiterator.KEY = KNOWN pvalue_key
  -- if $string_bytes(pvalue_key) = ($ptascii("option"))
def $test_named_iterator_front(S, 1) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "send") :: ptask_tail*
  -- if pconfigiterator.ITEMS = [ENTRY (KSTRING preqbytes) (DIRECT pvalue)]
  -- if preqbytes = $ptascii("option")
  -- if pconfigiterator.KEY = KNOWN pvalue_key
  -- if $string_bytes(pvalue_key) = ($ptascii("option"))
def $test_named_iterator_front(S, 2) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if S.ITERATORS = eps
def $test_named_iterator_front(S, n_stage) = false -- otherwise
dec $test_named_iterator_seek(pstate, nat, nat) : pstate
def $test_named_iterator_seek(S, n_stage, 0) = S
def $test_named_iterator_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_named_iterator_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET /\ ~$throwable_pending(S.COMPLETION))
def $test_named_iterator_seek(S, n_stage, n) = $test_named_iterator_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_named_iterator_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET \/ $throwable_pending(S.COMPLETION)
dec $test_named_iterator_step(pstate) : pstate
def $test_named_iterator_step(S) = S_next
  -- PhpStep: S ~> S_next
"""


def reach(state, start, stage):
    return [state + '_found = $test_named_iterator_seek(' + start + ',' + str(stage) + ',3000)',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_named_iterator_front(' + state + ',' + str(stage) + ')']


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)',
        state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)',
        state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *reach('S_front','S_initial',0),
        'S_front.TODO = (CONFIG_ITERATOR pconfigiterator "send") :: ptask_tail*',
        'pconfigiterator.CALL.KIND = INTRINSIC_INI_SET',
        'pconfigiterator.ITEMS = eps',
        '$intrinsic_argument(S_front,pconfigiterator.CALL.SITE,0) = ((expression,true,eps,porigin_argument,z_argument))',
        'S_front.ORIGIN = (porigin_argument)',
        'pconfigiterator.INPUT = VARIABLE ' + text('it') + ' z_argument',
        '$config_iterator_valid(S_front,pconfigiterator,"send")',
        'pconfigiterator.CURRENT = KNOWN pvalue_current',
        '$string_bytes(pvalue_current) = (' + text('precision') + ')',
        'pconfigiterator.KEY = KNOWN pvalue_key',
        '$string_bytes(pvalue_key) = (' + text('option') + ')',
        '$config_iterator_key(S_front,pvalue_key) = (KSTRING ' + text('option') + ')',
        '$lookup(S_front.ENV,' + text('v0') + ') = (n_v0_cell)',
        'S_front.STORE[n_v0_cell] = DEFINED pvalue_mutated',
        '$string_bytes(pvalue_mutated) = (' + text('output_buffering') + ')',
        '$lookup(S_front.ENV,' + text('result') + ') = (n_result_cell)',
        'S_front.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_front.PRECISIONINI = ' + text('14'),
        '$test_outputs(S_front.EVENTS) = ' + text('B|R|V0|C0|K0|'),
        *driver.common.public('S_front'),
        'S_sent = $test_named_iterator_step(S_front)',
        'S_sent.TODO = (CONFIG_ITERATOR pconfigiterator_sent "next-start") :: ptask_tail*',
        'pconfigiterator_sent = pconfigiterator[.ITEMS = [ENTRY (KSTRING ' + text('option') + ') (DIRECT pvalue_current)]][.CURRENT = KNOWN PNULL][.KEY = KNOWN PNULL]',
        '$config_iterator_valid(S_sent,pconfigiterator_sent,"next-start")',
        'S_sent.EVENTS = S_front.EVENTS',
        'S_sent.STORE = S_front.STORE',
        'S_sent.PRECISIONINI = S_front.PRECISIONINI',
        *driver.common.public('S_sent'),
        '$config_iterator_key(S_front,PSTRING ' + text('0') + ') = (KINT 0)',
        '$config_iterator_key(S_front,PBOOL true) = eps',
        '~$config_iterator_valid(S_front,pconfigiterator[.ITEMS = [ENTRY (KSTRING ' + text('0') + ') (DIRECT pvalue_current)]],"send")',
        '~$config_iterator_valid(S_front,pconfigiterator[.ITEMS = [ENTRY (KSTRING ' + text('option') + ') (DIRECT pvalue_current),ENTRY (KSTRING ' + text('option') + ') (DIRECT pvalue_current)]],"send")',
        '~$config_iterator_valid(S_front,pconfigiterator[.ITEMS = [ENTRY (KSTRING ' + text('option') + ') (DIRECT PNULL)]],"send")',
        '~$config_iterator_valid(S_front,pconfigiterator[.KEY = KNOWN (PBOOL true)],"send")',
        '~$config_iterator_valid(S_front,pconfigiterator[.CALL = pconfigiterator.CALL[.KIND = INTRINSIC_INI_GET]],"send")',
        '~$config_iterator_valid(S_front,pconfigiterator[.CALL = pconfigiterator.CALL[.SITE = PORIGIN 999 eps]],"send")',
        *budget('S_front')]
    if name == 'named-option-then-value-caches-current':
        return values
    assert name == 'duplicate-named-stops-before-next'
    values += [*reach('S_dup','S_sent',1),
        'S_dup.TODO = (CONFIG_ITERATOR pconfigiterator_dup "send") :: ptask_dup*',
        'pconfigiterator_dup.CALL = pconfigiterator.CALL',
        'pconfigiterator_dup.ITEMS = pconfigiterator_sent.ITEMS',
        'pconfigiterator_dup.CURRENT = KNOWN pvalue_second',
        '$string_bytes(pvalue_second) = (' + text('output_buffering') + ')',
        'pconfigiterator_dup.KEY = KNOWN pvalue_duplicate',
        '$string_bytes(pvalue_duplicate) = (' + text('option') + ')',
        '$config_iterator_valid(S_dup,pconfigiterator_dup,"send")',
        '$config_pack_prefix(pconfigiterator_dup.CALL,pconfigiterator_dup.ITEMS,false) = (pconfigcall_prefix)',
        'pconfigcall_prefix.SENT = [NAMED_SENT (KNOWN pvalue_current)]',
        'pconfigcall_prefix.NAMED',
        '$test_outputs(S_dup.EVENTS) = ' + text('B|R|V0|C0|K0|N0|V1|C1|K1|'),
        'S_dup.PRECISIONINI = ' + text('14'),
        'S_dup.STORE[n_result_cell] = DEFINED (PINT 99)',
        *driver.common.public('S_dup'),
        'S_thrown = $test_named_iterator_step(S_dup)',
        'S_thrown = S_dup[.COMPLETION = THROWN "Error" ' + text('Named parameter $option overwrites previous argument') + ' z_argument]',
        'S_thrown.TODO = S_dup.TODO',
        'S_thrown.EVENTS = S_dup.EVENTS',
        'S_thrown.STORE = S_dup.STORE',
        'S_thrown.PRECISIONINI = S_dup.PRECISIONINI',
        *driver.common.public('S_thrown'),
        *budget('S_dup'),
        *reach('S_disposed','S_thrown',2),
        'S_disposed.TODO = (THROW_SEARCH n_exception) :: ptask_disposed*',
        'S_disposed.ITERATORS = eps',
        '$useriter_tasks_ids(S_disposed.TODO) = eps',
        'S_disposed.PRECISIONINI = ' + text('14'),
        'S_disposed.STORE[n_result_cell] = DEFINED (PINT 99)',
        '$test_outputs(S_disposed.EVENTS) = $test_outputs(S_dup.EVENTS)',
        *driver.common.public('S_disposed'),
        'S_final = $drive_steps(S_disposed,3000)',
        'S_final.COMPLETION = NORMAL', 'S_final.TODO = eps',
        'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.ITERATORS = eps',
        'S_final.PRECISIONINI = ' + text('14'),
        'S_final.STORE[n_result_cell] = DEFINED (PINT 99)',
        '$test_outputs(S_final.EVENTS) = ' + text('B|R|V0|C0|K0|N0|V1|C1|K1|E|Named parameter $option overwrites previous argument|99|14|1|output_buffering'),
        *driver.common.public('S_final')]
    return values


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['prepare', 'check'], required=True)
    parser.add_argument('--case', choices=('named-option-then-value-caches-current',
        'duplicate-named-stops-before-next'))
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    selected = (args.case,) if args.case else (
        'named-option-then-value-caches-current', 'duplicate-named-stops-before-next')
    sources.family.CASES = {name: sources.family.CASES[name] for name in selected}
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    sys.argv = [sys.argv[0], '--phase', args.phase, '--sources', str(args.sources),
                '--output', str(args.output)]
    driver.main()


if __name__ == '__main__':
    main()
