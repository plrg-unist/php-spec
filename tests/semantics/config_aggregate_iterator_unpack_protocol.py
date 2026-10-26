#!/usr/bin/env python3
"""Real Aggregate callbacks transfer their owned Iterator return into DATA."""
import argparse
import json
import os
import sys
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import config_aggregate_iterator_unpack_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64
PREFIX = r"""
dec $test_config_aggregate_front(pstate, nat) : bool
def $test_config_aggregate_front(S, 0) = true
  -- if S.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_config_aggregate_front(S, 1) = true
  -- if S.TODO = (CONFIG_AGGREGATE pconfigaggregate) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $test_config_aggregate_front(S, 2) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "ready") :: ptask_tail*
def $test_config_aggregate_front(S, n) = false -- otherwise
dec $test_config_aggregate_seek(pstate, nat, nat) : pstate
def $test_config_aggregate_seek(S, n_stage, 0) = S
def $test_config_aggregate_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_config_aggregate_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ (S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
def $test_config_aggregate_seek(S, n_stage, n) = $test_config_aggregate_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_config_aggregate_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~(S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
dec $test_config_aggregate_step(pstate) : pstate
def $test_config_aggregate_step(S) = S_next
  -- PhpStep: S ~> S_next
"""


def reach(state, start, stage):
    return [state + '_found = $test_config_aggregate_seek(' + start + ',' + str(stage) + ',3000)',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_config_aggregate_front(' + state + ',' + str(stage) + ')']


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)',
        state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)',
        state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def checks(program, path, name):
    owned = name == 'retained-config-aggregate-preserves-selected-setter-through-producer'
    assert owned or name == 'fixed-config-aggregate-produces-retained-user-iterator'
    first, second, value, old = ('3', '3', '11', '7') if owned else ('$(-11)', '7', '8', '14')
    callroots = '[HOBJECT n_owner]' if owned else 'eps'
    roots = '[HOBJECT n_iterator_object,HOBJECT n_owner]' if owned else '[HOBJECT n_iterator_object]'
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *reach('S_pre', 'S_initial', 0),
        'S_pre.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*',
        'pconfigcall.KIND = INTRINSIC_INI_SET', 'pconfigcall.INDEX = 0',
        'pconfigcall.SENT = eps', 'pconfigcall.PACKS = eps', '~pconfigcall.NAMED',
        '$intrinsic_argument(S_pre,pconfigcall.SITE,0) = ((expression,true,eps,porigin_argument,z_argument))',
        'S_pre.RESULT = VARIABLE ' + text('aggregate') + ' z_argument',
        '$lookup(S_pre.ENV,' + text('aggregate') + ') = (n_aggregate_cell)',
        'S_pre.STORE[n_aggregate_cell] = DEFINED (POBJECT n_aggregate_object)',
        '$lookup(S_pre.ENV,' + text('aggregateHold') + ') = (n_aggregate_hold)',
        '$lookup(S_pre.ENV,' + text('it') + ') = (n_iterator_cell)',
        'S_pre.STORE[n_iterator_cell] = DEFINED (POBJECT n_iterator_object)',
        '$lookup(S_pre.ENV,' + text('iteratorHold') + ') = (n_iterator_hold)',
        '$lookup(S_pre.ENV,' + text('result') + ') = (n_result_cell)',
        'S_pre.STORE[n_result_cell] = DEFINED (PINT 99)',
        '$heap_owners($heap_graph(S_pre),HOBJECT n_aggregate_object) = 2',
        '$heap_owners($heap_graph(S_pre),HOBJECT n_iterator_object) = 2',
        '$config_aggregate_start(S_pre,pconfigcall,S_pre.RESULT,n_aggregate_object)',
        '~$config_iterator_start(S_pre,pconfigcall,S_pre.RESULT,n_aggregate_object)',
        '~$config_invoke_valid(S_pre,pconfigcall)', *common.public('S_pre'),
        'S_pending = $test_config_aggregate_step(S_pre)',
        'S_pending.TODO = (CALL_ARGS pcalltarget eps 0 eps (porigin_argument) z_argument) :: (CONFIG_AGGREGATE pconfigaggregate) :: ptask_tail*',
        'pcalltarget = AGGREGATE_METHOD_TARGET n_aggregate_object porigin_method',
        'pconfigaggregate = {CALL pconfigcall,OBJECT n_aggregate_object,INPUT S_pre.RESULT}',
        '$target_nodes(pcalltarget) = eps',
        '$task_nodes(CONFIG_AGGREGATE pconfigaggregate) = ' + callroots,
        '$heap_graph(S_pending) = $heap_graph(S_pre)',
        'S_pending.ITERATORS = S_pre.ITERATORS', 'S_pending.NEXTITER = S_pre.NEXTITER',
        'S_pending.ARRAYS = S_pre.ARRAYS', 'S_pending.EVENTS = S_pre.EVENTS',
        '$config_aggregate_pending_site(S_pending,porigin_argument)',
        '$call_selected_valid(S_pending,pcalltarget,(porigin_argument))',
        *common.public('S_pending'), *reach('S_return', 'S_pending', 1),
        'S_return.TODO = (CONFIG_AGGREGATE pconfigaggregate) :: ptask_tail*',
        'S_return.RESULT = KNOWN (POBJECT n_iterator_object)',
        '$config_aggregate_return_allowed(S_return,pconfigaggregate)',
        '$heap_owners($heap_graph(S_return),HOBJECT n_aggregate_object) = 2',
        '$heap_owners($heap_graph(S_return),HOBJECT n_iterator_object) = 3',
        'S_return.ITERATORS = S_pre.ITERATORS', 'S_return.NEXTITER = S_pre.NEXTITER',
        'S_return.ARRAYS = S_pre.ARRAYS',
        'S_return.PRECISIONINI = ' + text('6' if owned else '14'),
        '$test_outputs(S_return.EVENTS) = ' + text('B|G|'),
        *common.public('S_return'),
        'S_data = $test_config_aggregate_step(S_return)',
        'S_data = $config_aggregate_promote(S_return,pconfigaggregate,ptask_tail*)',
        'S_data.TODO = (CONFIG_ITERATOR pconfigiterator "rewind-start") :: ptask_tail*',
        'pconfigiterator = {CALL pconfigcall,ITERATOR S_pre.NEXTITER,OBJECT n_iterator_object,INPUT S_pre.RESULT,PRODUCER (n_aggregate_object),ITEMS eps,CURRENT (KNOWN PNULL),KEY (KNOWN PNULL)}',
        'S_data.RESULT = KNOWN PNULL', 'S_data.NEXTITER = $(S_pre.NEXTITER + 1)',
        '$iterator_lookup(S_data.ITERATORS,S_pre.NEXTITER) = (OBJECTITER S_pre.NEXTITER n_iterator_object 0 false)',
        '$task_nodes(CONFIG_ITERATOR pconfigiterator "rewind-start") = ' + roots,
        '$heap_graph(S_data) = $heap_graph(S_return)',
        'S_data.STORE = S_return.STORE', 'S_data.EVENTS = S_return.EVENTS',
        'S_data.ARRAYS = S_return.ARRAYS',
        '$config_iterator_valid(S_data,pconfigiterator,"rewind-start")',
        *common.public('S_data'), *reach('S_ready', 'S_data', 2),
        'S_ready.TODO = (CONFIG_ITERATOR pconfigiterator_ready "ready") :: ptask_tail*',
        'pconfigiterator_ready.CALL = pconfigcall',
        'pconfigiterator_ready.INPUT = S_pre.RESULT',
        'pconfigiterator_ready.ITEMS = [ENTRY (KINT ' + first + ') (DIRECT pvalue_option),ENTRY (KINT ' + second + ') (DIRECT pvalue_value)]',
        '$string_bytes(pvalue_option) = (' + text('precision') + ')',
        '$string_bytes(pvalue_value) = (' + text(value) + ')',
        '$heap_owners($heap_graph(S_ready),HOBJECT n_iterator_object) = 2',
        '$heap_owners($heap_graph(S_ready),HOBJECT n_aggregate_object) = 2',
        'S_ready.ITERATORS = S_pre.ITERATORS', 'S_ready.ARRAYS = S_pre.ARRAYS',
        'S_ready.PRECISIONINI = ' + text(old),
        *common.step('S_api', 'S_ready'),
        'S_api.TODO = ptask_tail*', 'S_api.RESULT = KNOWN pvalue_old',
        '$string_bytes(pvalue_old) = (' + text(old) + ')',
        'S_api.PRECISIONINI = ' + text(value),
        'S_api.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_last_iterator = S_return[.STORE[n_iterator_cell] = DEFINED PNULL][.STORE[n_iterator_hold] = DEFINED PNULL]',
        'S_last_iterator.RESULT = S_return.RESULT',
        '$heap_owners($heap_graph(S_last_iterator),HOBJECT n_iterator_object) = 1',
        '$config_aggregate_valid(S_last_iterator,pconfigaggregate)',
        '$config_aggregate_return_allowed(S_last_iterator,pconfigaggregate)',
        'S_last_promoted = $config_aggregate_promote(S_last_iterator,pconfigaggregate,ptask_tail*)',
        'S_last_promoted.TODO = (CONFIG_ITERATOR pconfigiterator_last "rewind-start") :: ptask_tail*',
        'pconfigiterator_last.PRODUCER = (n_aggregate_object)',
        '$config_iterator_producer_valid(S_last_promoted,pconfigiterator_last)',
        '$heap_owners($heap_graph(S_last_promoted),HOBJECT n_iterator_object) = 1',
        'S_lost_aggregate = S_return[.STORE[n_aggregate_cell] = DEFINED PNULL][.STORE[n_aggregate_hold] = DEFINED PNULL]',
        '$heap_owners($heap_graph(S_lost_aggregate),HOBJECT n_aggregate_object) = 0',
        '$config_aggregate_promote(S_lost_aggregate,pconfigaggregate,ptask_tail*) = S_lost_aggregate[.COMPLETION = UNSUPPORTED "CONFIG Aggregate return outside shared initialized Iterator domain"]']
    if owned:
        values += ['pconfigcall.OWNER = (n_owner)',
            'S_pre.OBJECTS[n_owner] = INTRINSICCLOSURE INTRINSIC_INI_SET',
            '$lookup(S_pre.ENV,' + text('call') + ') = (n_call_cell)',
            '$lookup(S_pre.ENV,' + text('keep') + ') = (n_keep_cell)',
            'S_return.STORE[n_call_cell] = DEFINED (POBJECT n_getter)',
            'S_return.OBJECTS[n_getter] = INTRINSICCLOSURE INTRINSIC_INI_GET',
            'n_getter =/= n_owner',
            '$heap_owners($heap_graph(S_return),HOBJECT n_owner) = 2',
            '$heap_owners($heap_graph(S_api),HOBJECT n_owner) = 1',
            'S_last_callee = S_return[.STORE[n_keep_cell] = DEFINED PNULL]',
            '$config_aggregate_promote(S_last_callee,pconfigaggregate,ptask_tail*) = S_last_callee[.COMPLETION = UNSUPPORTED "CONFIG Aggregate return outside shared initialized Iterator domain"]']
    else:
        values += ['pconfigcall.OWNER = eps']
    for index, change in enumerate(('.SITE = PORIGIN 0 eps', '.LINE = $(pconfigcall.LINE + 1)',
            '.SELECTION = (S_pre.SELECTSEQ)', '.KIND = INTRINSIC_INI_GET')):
        call, state = 'pconfigcall_bad' + str(index), 'S_bad' + str(index)
        values += [call + ' = pconfigcall[' + change + ']',
            state + ' = S_pre[.TODO = (CONFIG_UNPACK_PREP ' + call + ') :: ptask_tail*][.ORIGIN = (' + call + '.SITE)]',
            '~$config_aggregate_start(' + state + ',' + call + ',S_pre.RESULT,n_aggregate_object)']
    values += ['~$config_aggregate_scope(S_return,pconfigaggregate[.INPUT = KNOWN (POBJECT n_aggregate_object)])',
        '~$config_aggregate_scope(S_return,pconfigaggregate[.INPUT = VARIABLE ' + text('aggregate') + ' $(z_argument + 1)])',
        *budget('S_pre'), *budget('S_return'),
        'S_final = $drive_steps(S_api,3000)', 'S_final.COMPLETION = NORMAL',
        'S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.ITERATORS = S_pre.ITERATORS', 'S_final.ARRAYS = S_pre.ARRAYS',
        'S_final.PRECISIONINI = ' + text('9' if owned else value),
        '$test_outputs(S_final.EVENTS) = ' + text('B|G|R|V0|C0|K0|N0|V1|C1|K1|N1|V2|A|' +
            ('7|11|11|2|R|11|9' if owned else '14|8|2|E')),
        *common.public('S_final')]
    return values


def partition(values, part):
    cut = values.index('$heap_valid($heap_graph(S_return))') + 1
    if part == 'entry':
        return values[:cut]
    # Reach the same returned-Iterator frontier; setup adds no coverage credit.
    setup = [values[0], values[1], *reach('S_pre', 'S_initial', 0),
        'S_pre.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*',
        '$intrinsic_argument(S_pre,pconfigcall.SITE,0) = ((expression,true,eps,porigin_argument,z_argument))']
    for name, cell in [('aggregate', 'n_aggregate_cell'), ('aggregateHold', 'n_aggregate_hold'),
            ('it', 'n_iterator_cell'), ('iteratorHold', 'n_iterator_hold'),
            ('result', 'n_result_cell')]:
        setup += ['$lookup(S_pre.ENV,' + text(name) + ') = (' + cell + ')']
    setup += ['S_pre.STORE[n_aggregate_cell] = DEFINED (POBJECT n_aggregate_object)',
        'S_pre.STORE[n_iterator_cell] = DEFINED (POBJECT n_iterator_object)',
        *reach('S_return', 'S_pre', 1),
        'S_return.TODO = (CONFIG_AGGREGATE pconfigaggregate) :: ptask_tail*']
    assert not any('S_pending' in value for value in values[cut:])
    return setup + values[cut:]


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['prepare', 'check'], required=True)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--part', choices=['entry', 'completion', 'all'])
    args = parser.parse_args()
    if args.part is not None:
        name = 'retained-config-aggregate-preserves-selected-setter-through-producer'
        sources.family.CASES = {name: sources.family.CASES[name]}
    driver.sources, driver.PREFIX = sources, PREFIX
    for part in (['entry', 'completion'] if args.part == 'all' else [args.part]):
        driver.checks = checks if part is None else lambda program, path, name: partition(checks(program, path, name), part)
        output = args.output if part is None else args.output / part
        sys.argv = [sys.argv[0], '--phase', args.phase, '--sources', str(args.sources),
            '--output', str(output)]
        driver.main()


if __name__ == '__main__':
    main()
