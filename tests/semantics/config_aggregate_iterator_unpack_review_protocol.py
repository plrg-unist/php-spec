#!/usr/bin/env python3
"""Real getIterator failure preserves borrowed receivers and cancels DATA/API."""
import argparse
import json
import os
import sys
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import config_aggregate_iterator_unpack_review_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64
PREFIX = r"""
dec $test_config_aggregate_peer_front(pstate, nat) : bool
def $test_config_aggregate_peer_front(S, 0) = true
  -- if S.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_config_aggregate_peer_front(S, 1) = true
  -- if S.TODO = (THROW_VALUE porigin z) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = AGGREGATE_METHOD_TARGET n porigin_method
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (CONFIG_AGGREGATE pconfigaggregate) :: ptask_caller*
def $test_config_aggregate_peer_front(S, 2) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_AGGREGATE pconfigaggregate) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $test_config_aggregate_peer_front(S, 3) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_option),NAMED_SENT (KNOWN pvalue_value)]
  -- if $string_bytes(pvalue_option) = ($ptascii("precision"))
  -- if $string_bytes(pvalue_value) = ($ptascii("9"))
def $test_config_aggregate_peer_front(S, 4) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if S.DESTRUCTION.OPERATIONS = eps
def $test_config_aggregate_peer_front(S, n) = false -- otherwise
dec $test_config_aggregate_peer_seek(pstate, nat, nat) : pstate
def $test_config_aggregate_peer_seek(S, n_stage, 0) = S
def $test_config_aggregate_peer_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_config_aggregate_peer_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ (S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
def $test_config_aggregate_peer_seek(S, n_stage, n) = $test_config_aggregate_peer_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_config_aggregate_peer_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~(S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
dec $test_config_aggregate_peer_step(pstate) : pstate
def $test_config_aggregate_peer_step(S) = S_next
  -- PhpStep: S ~> S_next
"""


def reach(state, start, stage):
    return [state + '_found = $test_config_aggregate_peer_seek(' + start + ',' + str(stage) + ',3000)',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_config_aggregate_peer_front(' + state + ',' + str(stage) + ')']


def owners(state, callee):
    return ['$heap_owners($heap_graph(' + state + '),HOBJECT ' + node + ') = ' + str(count)
        for node, count in [('n_aggregate', 2), ('n_iterator', 2), ('n_owner', callee)]]


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)',
        state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)',
        state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def checks(program, path, name):
    assert name == 'retained-config-aggregate-getiterator-throw-cancels-data-and-api'
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *reach('S_pre', 'S_initial', 0),
        'S_pre.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*',
        'pconfigcall.KIND = INTRINSIC_INI_SET', 'pconfigcall.INDEX = 0',
        'pconfigcall.SENT = eps', 'pconfigcall.PACKS = eps', '~pconfigcall.NAMED',
        'pconfigcall.OWNER = (n_owner)', 'pconfigcall.SELECTION = eps',
        '$intrinsic_argument(S_pre,pconfigcall.SITE,0) = ((expression,true,eps,porigin_argument,z_argument))',
        'pconfigcall.LINE = 23', 'z_argument = 24',
        'S_pre.RESULT = VARIABLE ' + text('aggregate') + ' z_argument',
        '$lookup(S_pre.ENV,' + text('aggregate') + ') = (n_aggregate_cell)',
        'S_pre.STORE[n_aggregate_cell] = DEFINED (POBJECT n_aggregate)',
        '$lookup(S_pre.ENV,' + text('aggregateHold') + ') = (n_aggregate_hold)',
        '$lookup(S_pre.ENV,' + text('iterator') + ') = (n_iterator_cell)',
        'S_pre.STORE[n_iterator_cell] = DEFINED (POBJECT n_iterator)',
        '$objectprops_at(S_pre.OBJECTPROPS,n_iterator) = (ppropertyslot_iterator*)',
        '$lookup(S_pre.ENV,' + text('call') + ') = (n_call_cell)',
        '$lookup(S_pre.ENV,' + text('keep') + ') = (n_keep_cell)',
        'S_pre.STORE[n_keep_cell] = DEFINED (POBJECT n_owner)',
        'S_pre.OBJECTS[n_owner] = INTRINSICCLOSURE INTRINSIC_INI_SET',
        '$lookup(S_pre.ENV,' + text('saved') + ') = (n_saved_cell)',
        'S_pre.STORE[n_saved_cell] = DEFINED PNULL',
        '$lookup(S_pre.ENV,' + text('result') + ') = (n_result_cell)',
        'S_pre.STORE[n_result_cell] = DEFINED (PINT 99)',
        '$lookup(S_pre.ENV,' + text('effects') + ') = (n_effects_cell)',
        'S_pre.STORE[n_effects_cell] = DEFINED (PINT 0)',
        'S_pre.CURRENT = eps', 'S_pre.FRAMES = eps', 'S_pre.ITERATORS = eps',
        '$config_aggregate_start(S_pre,pconfigcall,S_pre.RESULT,n_aggregate)',
        *owners('S_pre', 3), *common.public('S_pre'),
        'S_pending = $test_config_aggregate_peer_step(S_pre)',
        'S_pending.TODO = (CALL_ARGS pcalltarget eps 0 eps (porigin_argument) z_argument) :: (CONFIG_AGGREGATE pconfigaggregate) :: ptask_tail*',
        'pcalltarget = AGGREGATE_METHOD_TARGET n_aggregate porigin_method',
        'pconfigaggregate = {CALL pconfigcall,OBJECT n_aggregate,INPUT S_pre.RESULT}',
        '$target_nodes(pcalltarget) = eps', '$target_instance(pcalltarget) = eps',
        '$task_nodes(CONFIG_AGGREGATE pconfigaggregate) = [HOBJECT n_owner]',
        '$heap_graph(S_pending) = $heap_graph(S_pre)',
        'S_pending.ITERATORS = S_pre.ITERATORS', 'S_pending.NEXTITER = S_pre.NEXTITER',
        '$config_aggregate_pending_site(S_pending,porigin_argument)',
        '$call_selected_valid(S_pending,pcalltarget,(porigin_argument))',
        *common.public('S_pending'), *reach('S_throw', 'S_pending', 1),
        'S_throw.CURRENT = (pcallcontext)',
        'pcallcontext.TARGET = pcalltarget', 'pcallcontext.CALLSITE = (porigin_argument)',
        'pcallcontext.LINE = z_argument', 'pcallcontext.ARGC = 0',
        'S_throw.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (CONFIG_AGGREGATE pconfigaggregate) :: ptask_tail*',
        '$config_aggregate_frame(S_throw,pcallcontext,pframe)',
        'S_throw.STORE[n_saved_cell] = DEFINED (POBJECT n_exception)',
        '$throwable_live(S_throw,n_exception)',
        '$string_bytes($throwable_field(S_throw,n_exception,"message")) = (' + text('config-aggregate-before-iterator89') + ')',
        '$throwable_field(S_throw,n_exception,"trace") = PARRAY n_trace',
        'S_throw.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_frame))]',
        '$trace_array_field(S_throw,n_frame,' + text('function') + ') = PSTRING ' + text('getIterator'),
        '$trace_array_field(S_throw,n_frame,' + text('class') + ') = PSTRING ' + text('ConfigAggregateThrowReview89'),
        '$trace_array_field(S_throw,n_frame,' + text('type') + ') = PSTRING ' + text('->'),
        '$trace_array_field(S_throw,n_frame,' + text('line') + ') = PINT z_argument',
        '$trace_array_field(S_throw,n_frame,' + text('args') + ') = PARRAY n_args',
        'S_throw.ARRAYS[n_args].ITEMS = eps',
        'S_throw.STORE[n_call_cell] = DEFINED (POBJECT n_getter)',
        'S_throw.OBJECTS[n_getter] = INTRINSICCLOSURE INTRINSIC_INI_GET',
        'n_getter =/= n_owner', 'S_throw.PRECISIONINI = ' + text('6'),
        'S_throw.STORE[n_effects_cell] = DEFINED (PINT 1)',
        'S_throw.STORE[n_result_cell] = DEFINED (PINT 99)',
        '$test_outputs(S_throw.EVENTS) = ' + text('B|G|'),
        'S_throw.ITERATORS = S_pre.ITERATORS', 'S_throw.NEXTITER = S_pre.NEXTITER',
        *owners('S_throw', 2), *common.public('S_throw'),
        *reach('S_thrown', 'S_throw', 2),
        'S_thrown.TODO = (THROW_SEARCH n_exception) :: (CONFIG_AGGREGATE pconfigaggregate) :: ptask_tail*',
        '$config_aggregate_valid(S_thrown,pconfigaggregate)',
        'S_thrown.STORE[n_saved_cell] = DEFINED (POBJECT n_exception)',
        'S_thrown.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_thrown.STORE[n_effects_cell] = DEFINED (PINT 1)',
        'S_thrown.PRECISIONINI = ' + text('6'),
        'S_thrown.ITERATORS = S_pre.ITERATORS', 'S_thrown.NEXTITER = S_pre.NEXTITER',
        '$objectprops_at(S_thrown.OBJECTPROPS,n_iterator) = (ppropertyslot_iterator*)',
        'S_thrown.ARRAYS = S_throw.ARRAYS', 'S_thrown.EVENTS = S_throw.EVENTS',
        *owners('S_thrown', 2), *common.public('S_thrown')]
    for label, update in [('line', '.LINE = $(pconfigcall.LINE + 1)'),
            ('owner', '.OWNER = (n_aggregate)')]:
        call, state = 'pconfigcall_bad_' + label, 'S_bad_' + label
        values += [call + ' = pconfigcall[' + update + ']',
            state + ' = S_pre[.TODO = (CONFIG_UNPACK_PREP ' + call + ') :: ptask_tail*][.ORIGIN = (' + call + '.SITE)]',
            '~$config_aggregate_start(' + state + ',' + call + ',' + state + '.RESULT,n_aggregate)']
    values += ['~$config_aggregate_scope(S_thrown,pconfigaggregate[.INPUT = KNOWN (POBJECT n_aggregate)])',
        '~$config_aggregate_scope(S_thrown[.CODE = eps],pconfigaggregate)',
        'S_fake_method = S_pending[.TODO = (CALL_ARGS (METHOD_TARGET n_aggregate porigin_method) eps 0 eps (porigin_argument) z_argument) :: (CONFIG_AGGREGATE pconfigaggregate) :: ptask_tail*]',
        '~$config_aggregate_pending_site(S_fake_method,porigin_argument)',
        'S_last_callee = S_thrown[.STORE[n_keep_cell] = DEFINED PNULL]',
        '$heap_owners($heap_graph(S_last_callee),HOBJECT n_owner) = 1',
        '$config_aggregate_valid(S_last_callee,pconfigaggregate)',
        'S_stopped = $test_config_aggregate_peer_step(S_last_callee)',
        'S_stopped = S_last_callee[.COMPLETION = UNSUPPORTED "CONFIG Aggregate unpack last cleanup owner"]',
        '$throwable_live(S_stopped,n_exception)',
        'S_lost_aggregate = S_thrown[.STORE[n_aggregate_cell] = DEFINED PNULL][.STORE[n_aggregate_hold] = DEFINED PNULL]',
        '$heap_owners($heap_graph(S_lost_aggregate),HOBJECT n_aggregate) = 0',
        'S_aggregate_stopped = $test_config_aggregate_peer_step(S_lost_aggregate)',
        'S_aggregate_stopped = S_lost_aggregate[.COMPLETION = UNSUPPORTED "CONFIG Aggregate unpack last cleanup owner"]',
        'S_after = $test_config_aggregate_peer_step(S_thrown)',
        'S_after = $config_aggregate_discard(S_thrown[.TODO = (THROW_SEARCH n_exception) :: ptask_tail*],pconfigaggregate)',
        *reach('S_disposed', 'S_after', 4),
        'S_disposed.TODO = (THROW_SEARCH n_exception) :: ptask_tail*',
        '$throwable_live(S_disposed,n_exception)',
        '$throwable_field(S_disposed,n_exception,"previous") = PNULL',
        'S_disposed.STORE = S_thrown.STORE', 'S_disposed.ENV = S_thrown.ENV',
        'S_disposed.OBJECTS = S_thrown.OBJECTS', 'S_disposed.ARRAYS = S_thrown.ARRAYS',
        'S_disposed.ITERATORS = S_pre.ITERATORS', 'S_disposed.NEXTITER = S_pre.NEXTITER',
        'S_disposed.EVENTS = S_thrown.EVENTS', *owners('S_disposed', 1),
        *common.public('S_disposed'), *budget('S_pre'), *budget('S_thrown'),
        *reach('S_recovery', 'S_disposed', 3),
        'S_recovery.TODO = (CONFIG_INVOKE pconfigcall_recovery) :: ptask_recovery*',
        '$config_invoke_valid(S_recovery,pconfigcall_recovery)',
        'pconfigcall_recovery.OWNER = (n_owner)',
        '$lookup(S_recovery.ENV,' + text('e') + ') = (n_caught_cell)',
        'S_recovery.STORE[n_caught_cell] = DEFINED (POBJECT n_exception)',
        'S_recovery.STORE[n_saved_cell] = DEFINED (POBJECT n_exception)',
        'S_recovery.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_recovery.PRECISIONINI = ' + text('6'),
        'S_recovery.ITERATORS = S_pre.ITERATORS', 'S_recovery.NEXTITER = S_pre.NEXTITER',
        *owners('S_recovery', 2), *common.public('S_recovery'),
        *common.step('S_recovered', 'S_recovery'),
        'S_recovered.RESULT = KNOWN pvalue_old',
        '$string_bytes(pvalue_old) = (' + text('6') + ')',
        'S_recovered.PRECISIONINI = ' + text('9'),
        'S_recovered.STORE = S_recovery.STORE',
        'S_recovered.OBJECTS = S_recovery.OBJECTS',
        *owners('S_recovered', 1), *common.public('S_recovered'),
        'S_final = $drive_steps(S_recovered,3000)',
        'S_final.COMPLETION = NORMAL', 'S_final.TODO = eps',
        'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.ITERATORS = S_pre.ITERATORS', 'S_final.NEXTITER = S_pre.NEXTITER',
        '$objectprops_at(S_final.OBJECTPROPS,n_iterator) = (ppropertyslot_iterator*)',
        'S_final.PRECISIONINI = ' + text('9'),
        '$test_outputs(S_final.EVENTS) = ' + text('B|G|I|99|1|6|getIterator|ConfigAggregateThrowReview89|->|24|A|T|Z|L|6|R|6|9|99'),
        *common.public('S_final')]
    return values


def partition(values, part):
    cut = values.index('$heap_valid($heap_graph(S_thrown))') + 1
    if part == 'entry':
        return values[:cut]
    # Recompute the real callback throw; duplicated setup adds no coverage.
    setup = [values[0], values[1], *reach('S_pre', 'S_initial', 0),
        'S_pre.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*',
        'pconfigcall.OWNER = (n_owner)',
        '$intrinsic_argument(S_pre,pconfigcall.SITE,0) = ((expression,true,eps,porigin_argument,z_argument))']
    for name, cell in [('aggregate', 'n_aggregate_cell'), ('aggregateHold', 'n_aggregate_hold'),
            ('iterator', 'n_iterator_cell'), ('keep', 'n_keep_cell'),
            ('saved', 'n_saved_cell'), ('result', 'n_result_cell')]:
        setup += ['$lookup(S_pre.ENV,' + text(name) + ') = (' + cell + ')']
    setup += ['S_pre.STORE[n_aggregate_cell] = DEFINED (POBJECT n_aggregate)',
        'S_pre.STORE[n_iterator_cell] = DEFINED (POBJECT n_iterator)',
        '$objectprops_at(S_pre.OBJECTPROPS,n_iterator) = (ppropertyslot_iterator*)',
        'S_pending = $test_config_aggregate_peer_step(S_pre)',
        'S_pending.TODO = (CALL_ARGS (AGGREGATE_METHOD_TARGET n_aggregate porigin_method) eps 0 eps (porigin_argument) z_argument) :: (CONFIG_AGGREGATE pconfigaggregate) :: ptask_tail*',
        *reach('S_thrown', 'S_pending', 2),
        'S_thrown.TODO = (THROW_SEARCH n_exception) :: (CONFIG_AGGREGATE pconfigaggregate) :: ptask_tail*']
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
    driver.sources, driver.PREFIX = sources, PREFIX
    for part in (['entry', 'completion'] if args.part == 'all' else [args.part]):
        driver.checks = checks if part is None else lambda program, path, name: partition(checks(program, path, name), part)
        output = args.output if part is None else args.output / part
        sys.argv = [sys.argv[0], '--phase', args.phase, '--sources', str(args.sources),
            '--output', str(output)]
        driver.main()


if __name__ == '__main__':
    main()
