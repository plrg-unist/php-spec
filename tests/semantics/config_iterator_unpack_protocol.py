#!/usr/bin/env python3
"""Streaming CONFIG arguments, independent DATA ownership and API entry."""
import argparse
import json
import os
import sys
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import config_iterator_unpack_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64
PREFIX = r"""
dec $test_config_iterator_front(pstate, nat) : bool
def $test_config_iterator_front(S, 0) = true
  -- if S.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_config_iterator_front(S, 1) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "key-start") :: ptask_tail*
  -- if |pconfigiterator.ITEMS| = 1
def $test_config_iterator_front(S, 2) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "send") :: ptask_tail*
  -- if |pconfigiterator.ITEMS| = 1
def $test_config_iterator_front(S, 3) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "finish") :: ptask_tail*
def $test_config_iterator_front(S, 4) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "ready") :: ptask_tail*
def $test_config_iterator_front(S, n_stage) = false -- otherwise
dec $test_config_iterator_seek(pstate, nat, nat) : pstate
def $test_config_iterator_seek(S, n_stage, 0) = S
def $test_config_iterator_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_config_iterator_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ (S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
def $test_config_iterator_seek(S, n_stage, n) = $test_config_iterator_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_config_iterator_front(S,n_stage)
  -- if ~(S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def reach(state, start, stage):
    return [state + '_found = $test_config_iterator_seek(' + start + ',' + str(stage) + ',3000)',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_config_iterator_front(' + state + ',' + str(stage) + ')']


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)',
        state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)',
        state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def unchanged(after, before, fields):
    return [after + '.' + field + ' = ' + before + '.' + field for field in fields.split()]


def checks(program, path, name):
    owned = name == 'retained-config-iterator-preserves-callee-across-callback-writes'
    assert owned or name == 'fixed-config-iterator-runs-all-callbacks-before-api'
    first, second, value = ('3', '3', '11') if owned else ('$(-11)', '7', '8')
    old = '6' if owned else '14'
    callroots = '[HOBJECT n_owner]' if owned else 'eps'
    roots = '[HOBJECT n_object,HOBJECT n_owner]' if owned else '[HOBJECT n_object]'
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *reach('S_pre','S_initial',0),
        'S_pre.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*',
        'pconfigcall.KIND = INTRINSIC_INI_SET', 'pconfigcall.INDEX = 0',
        'pconfigcall.SENT = eps', 'pconfigcall.PACKS = eps', '~pconfigcall.NAMED',
        'pconfigcall.SELECTION = eps', '$config_pending_valid(S_pre,pconfigcall,true)',
        '~$config_invoke_valid(S_pre,pconfigcall)',
        '$intrinsic_count(S_pre,pconfigcall.SITE) = (1)',
        '$intrinsic_argument(S_pre,pconfigcall.SITE,0) = ((expression,true,eps,porigin_argument,z_argument))',
        'S_pre.RESULT = VARIABLE ' + text('it') + ' z_argument',
        '$lookup(S_pre.ENV,' + text('it') + ') = (n_iterator_cell)',
        'S_pre.STORE[n_iterator_cell] = DEFINED (POBJECT n_object)',
        '$useriter_instance(S_pre,n_object)',
        '$config_iterator_start(S_pre,pconfigcall,S_pre.RESULT,n_object)',
        '$config_nodes(pconfigcall) = ' + callroots,
        '$lookup(S_pre.ENV,' + text('result') + ') = (n_result_cell)',
        'S_pre.STORE[n_result_cell] = DEFINED (PINT 99)',
        '$heap_owners($heap_graph(S_pre),HOBJECT n_object) = 1',
        'S_pre.PRECISIONINI = ' + text('14'), 'S_pre.CURRENT = eps', 'S_pre.FRAMES = eps',
        '$test_outputs(S_pre.EVENTS) = ' + text('B|'), *common.public('S_pre')]
    if owned:
        values += ['pconfigcall.OWNER = (n_owner)',
            'S_pre.OBJECTS[n_owner] = INTRINSICCLOSURE INTRINSIC_INI_SET',
            '$lookup(S_pre.ENV,' + text('call') + ') = (n_call_cell)',
            '$lookup(S_pre.ENV,' + text('keep') + ') = (n_keep_cell)',
            'S_pre.STORE[n_call_cell] = DEFINED (POBJECT n_owner)',
            'S_pre.STORE[n_keep_cell] = DEFINED (POBJECT n_owner)',
            '$heap_owners($heap_graph(S_pre),HOBJECT n_owner) = 3']
    else:
        values += ['pconfigcall.OWNER = eps']
    values += [*common.step('S_start','S_pre'),
        'S_start.TODO = (CONFIG_ITERATOR pconfigiterator_start "rewind-start") :: ptask_tail*',
        'pconfigiterator_start.CALL = pconfigcall', 'pconfigiterator_start.OBJECT = n_object',
        'pconfigiterator_start.INPUT = S_pre.RESULT', 'pconfigiterator_start.ITERATOR = n_iterator',
        'n_iterator = S_pre.NEXTITER', 'S_start.NEXTITER = $(n_iterator + 1)',
        'pconfigiterator_start.ITEMS = eps', 'pconfigiterator_start.CURRENT = KNOWN PNULL',
        'pconfigiterator_start.KEY = KNOWN PNULL', 'S_start.ORIGIN = (porigin_argument)',
        '$iterator_lookup(S_start.ITERATORS,n_iterator) = (OBJECTITER n_iterator n_object 0 false)',
        '$config_iterator_valid(S_start,pconfigiterator_start,"rewind-start")',
        '$config_iterator_nodes(pconfigiterator_start,"rewind-start") = ' + roots,
        '$heap_owners($heap_graph(S_start),HOBJECT n_object) = 2',
        *unchanged('S_start','S_pre','ARRAYS ALLOCATIONS STORE ENV SOURCES CODE POOLS EVENTS SELECTEDCALLS STRINGDATA'),
        *common.public('S_start'), *reach('S_key','S_start',1),
        'S_key.TODO = (CONFIG_ITERATOR pconfigiterator_key "key-start") :: ptask_tail*',
        'pconfigiterator_key.CALL = pconfigcall', 'pconfigiterator_key.ITERATOR = n_iterator',
        'pconfigiterator_key.OBJECT = n_object', 'pconfigiterator_key.INPUT = S_pre.RESULT',
        'pconfigiterator_key.ITEMS = [ENTRY (KINT ' + first + ') (DIRECT pvalue_option)]',
        '$string_bytes(pvalue_option) = (' + text('precision') + ')',
        'pconfigiterator_key.CURRENT = KNOWN pvalue_value',
        '$string_bytes(pvalue_value) = (' + text(value) + ')',
        'pconfigiterator_key.KEY = KNOWN PNULL',
        '$config_iterator_valid(S_key,pconfigiterator_key,"key-start")',
        'S_key.CURRENT = eps', 'S_key.FRAMES = eps',
        '$config_iterator_nodes(pconfigiterator_key,"key-start") = ' + roots,
        '$heap_owners($heap_graph(S_key),HOBJECT n_object) = 2',
        'S_key.ARRAYS = S_pre.ARRAYS', 'S_key.STORE[n_result_cell] = DEFINED (PINT 99)',
        '$test_outputs(S_key.EVENTS) = ' + text('B|R|V0|C0|K0|N0|V1|C1|'),
        *common.public('S_key'), *reach('S_send','S_key',2),
        'S_send.TODO = (CONFIG_ITERATOR pconfigiterator_send "send") :: ptask_tail*',
        'pconfigiterator_send.CALL = pconfigcall',
        'pconfigiterator_send.ITEMS = pconfigiterator_key.ITEMS',
        'pconfigiterator_send.CURRENT = KNOWN pvalue_value',
        'pconfigiterator_send.KEY = KNOWN (PINT ' + second + ')',
        '$config_iterator_valid(S_send,pconfigiterator_send,"send")',
        *common.public('S_send'), *reach('S_finish','S_send',3),
        'S_finish.TODO = (CONFIG_ITERATOR pconfigiterator_finish "finish") :: ptask_tail*',
        'pconfigiterator_finish.CALL = pconfigcall',
        'pconfigiterator_finish.ITEMS = [ENTRY (KINT ' + first + ') (DIRECT pvalue_option),ENTRY (KINT ' + second + ') (DIRECT pvalue_value)]',
        'pconfigiterator_finish.CURRENT = KNOWN PNULL', 'pconfigiterator_finish.KEY = KNOWN PNULL',
        '$config_iterator_valid(S_finish,pconfigiterator_finish,"finish")',
        'S_finish.PRECISIONINI = ' + text(old), 'S_finish.ARRAYS = S_pre.ARRAYS',
        '$heap_owners($heap_graph(S_finish),HOBJECT n_object) = 2',
        '$test_outputs(S_finish.EVENTS) = ' + text('B|R|V0|C0|K0|N0|V1|C1|K1|N1|V2|'),
        *common.public('S_finish'), *reach('S_ready','S_finish',4),
        'S_ready.TODO = (CONFIG_ITERATOR pconfigiterator_finish "ready") :: ptask_tail*',
        '$config_iterator_valid(S_ready,pconfigiterator_finish,"ready")',
        '$iterator_lookup(S_ready.ITERATORS,n_iterator) = eps',
        '$useriter_task_ids(CONFIG_ITERATOR pconfigiterator_finish "ready") = eps',
        '$config_iterator_nodes(pconfigiterator_finish,"ready") = ' + callroots,
        '$heap_owners($heap_graph(S_ready),HOBJECT n_object) = 1',
        '$config_pack_prefix(pconfigcall,pconfigiterator_finish.ITEMS,false) = (pconfigcall_normalized)',
        'pconfigcall_normalized.SENT = [NAMED_SENT (KNOWN pvalue_option),NAMED_SENT (KNOWN pvalue_value)]',
        'pconfigcall_normalized.PACKS = eps',
        '~$config_invoke_valid(S_ready,pconfigcall_normalized[.INDEX = 1])',
        *unchanged('S_ready','S_finish','ARRAYS STORE ENV SOURCES CODE POOLS EVENTS SELECTEDCALLS STRINGDATA'),
        *common.public('S_ready'), *common.step('S_after','S_ready'),
        'S_after.TODO = ptask_tail*', 'S_after.RESULT = KNOWN pvalue_result',
        '$string_bytes(pvalue_result) = (' + text(old) + ')',
        'S_after.PRECISIONINI = ' + text(value),
        'S_after.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_after.EVENTS = S_ready.EVENTS', 'S_after.ARRAYS = S_pre.ARRAYS',
        *common.public('S_after'),
        'S_last = S_finish[.STORE[n_iterator_cell] = DEFINED PNULL]',
        '$config_iterator_valid(S_last,pconfigiterator_finish,"finish")',
        '$heap_owners($heap_graph(S_last),HOBJECT n_object) = 1',
        'S_last_stopped = $config_iterator_finish(S_last,pconfigiterator_finish,ptask_tail*)',
        'S_last_stopped = S_last[.COMPLETION = UNSUPPORTED "CONFIG Iterator unpack last DATA owner"]',
        '$task_nodes(CONFIG_ITERATOR pconfigiterator_finish "finish") = ' + roots]
    if owned:
        values += ['S_key.STORE[n_call_cell] = DEFINED (POBJECT n_getter)',
            'n_getter =/= n_owner', 'S_key.OBJECTS[n_getter] = INTRINSICCLOSURE INTRINSIC_INI_GET',
            'S_key.STORE[n_keep_cell] = DEFINED (POBJECT n_owner)',
            '$heap_owners($heap_graph(S_key),HOBJECT n_owner) = 2',
            '$heap_owners($heap_graph(S_after),HOBJECT n_owner) = 1',
            'S_discard_scope = S_key[.TODO = ptask_tail*]',
            '$config_iterator_discard_allowed(S_discard_scope,pconfigiterator_key)',
            'S_last_owner = S_discard_scope[.STORE[n_keep_cell] = DEFINED PNULL]',
            '$heap_owners($heap_graph(S_last_owner),HOBJECT n_object) = 1',
            '$heap_owners($heap_graph(S_last_owner),HOBJECT n_owner) = 0',
            '~$config_iterator_discard_allowed(S_last_owner,pconfigiterator_key)']
    for field in ('.KIND = INTRINSIC_INI_GET', '.INDEX = 1', '.SITE = PORIGIN 0 eps',
            '.LINE = $(pconfigcall.LINE + 1)', '.SENT = [NAMED_SENT (KNOWN PNULL)]', '.NAMED = true'):
        values += ['~$config_iterator_valid(S_key,pconfigiterator_key[.CALL = pconfigcall[' + field + ']],"key-start")']
    for field in ('.INPUT = KNOWN (POBJECT n_object)', '.INPUT = VARIABLE ' + text('missing_iterator') + ' z_argument',
            '.INPUT = VARIABLE ' + text('it') + ' $(z_argument + 1)', '.OBJECT = |S_key.OBJECTS|',
            '.ITERATOR = S_key.NEXTITER', '.ITEMS = [ENTRY (KINT 3) (DIRECT PNULL)]',
            '.ITEMS = [ENTRY (KSTRING ' + text('value') + ') (DIRECT pvalue_value)]',
            '.CURRENT = KNOWN PNULL', '.KEY = KNOWN (PINT 0)'):
        values += ['~$config_iterator_valid(S_key,pconfigiterator_key[' + field + '],"key-start")']
    values += ['~$config_iterator_valid(S_key[.ITERATORS = eps],pconfigiterator_key,"key-start")',
        '~$config_iterator_valid(S_key,pconfigiterator_key,"ready")',
        '~$config_iterator_valid(S_key,pconfigiterator_key,"rewind-start")',
        '~$config_iterator_valid(S_key,pconfigiterator_key,"send")',
        '~$config_iterator_valid(S_ready,pconfigiterator_finish,"finish")',
        *budget('S_pre'), *budget('S_key'), *budget('S_finish'), *budget('S_ready'),
        'S_final = $drive_steps(S_after,3000)', 'S_final.COMPLETION = NORMAL',
        'S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.ITERATORS = eps', 'S_final.STORE[n_result_cell] = DEFINED pvalue_final_result',
        '$string_bytes(pvalue_final_result) = (' + text(old) + ')',
        'S_final.ARRAYS = S_pre.ARRAYS',
        '$test_outputs(S_final.EVENTS) = ' + text('B|R|V0|C0|K0|N0|V1|C1|K1|N1|V2|A|' +
            ('6|11|11|2|E|R|11|12' if owned else '14|8|2|E')),
        *common.public('S_final')]
    return values



def partition(values, name, part):
    cut = values.index('$heap_valid($heap_graph(S_key))') + 1
    if part == 'entry':
        return values[:cut]
    owned = name == 'retained-config-iterator-preserves-callee-across-callback-writes'
    first = '3' if owned else '$(-11)'
    # Recompute reached states; every prefix assertion remains in the entry part.
    setup = [values[0], values[1], *reach('S_pre','S_initial',0),
        'S_pre.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*',
        '$intrinsic_argument(S_pre,pconfigcall.SITE,0) = ((expression,true,eps,porigin_argument,z_argument))',
        '$lookup(S_pre.ENV,' + text('it') + ') = (n_iterator_cell)',
        'S_pre.STORE[n_iterator_cell] = DEFINED (POBJECT n_object)',
        '$lookup(S_pre.ENV,' + text('result') + ') = (n_result_cell)']
    if owned:
        setup += ['pconfigcall.OWNER = (n_owner)',
            '$lookup(S_pre.ENV,' + text('call') + ') = (n_call_cell)',
            '$lookup(S_pre.ENV,' + text('keep') + ') = (n_keep_cell)']
    setup += [*reach('S_key','S_pre',1),
        'S_key.TODO = (CONFIG_ITERATOR pconfigiterator_key "key-start") :: ptask_tail*',
        'pconfigiterator_key.ITERATOR = n_iterator',
        'pconfigiterator_key.ITEMS = [ENTRY (KINT ' + first + ') (DIRECT pvalue_option)]',
        'pconfigiterator_key.CURRENT = KNOWN pvalue_value']
    assert not any('S_start' in value for value in values[cut:])
    return setup + values[cut:]


def main():
    sources.family.CASES = {name: source for name, source in sources.family.CASES.items()
        if name.startswith(('fixed-config-iterator-', 'retained-config-iterator-'))}
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['prepare', 'check'], required=True)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--part', choices=['entry', 'completion', 'all'], default='all')
    args = parser.parse_args()
    driver.sources, driver.PREFIX = sources, PREFIX
    for part in (['entry', 'completion'] if args.part == 'all' else [args.part]):
        driver.checks = lambda program, path, name: partition(checks(program,path,name),name,part)
        sys.argv = [sys.argv[0], '--phase', args.phase, '--sources', str(args.sources),
            '--output', str(args.output / part)]
        driver.main()


if __name__ == '__main__':
    main()
