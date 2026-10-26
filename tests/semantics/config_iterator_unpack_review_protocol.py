#!/usr/bin/env python3
"""Reached CONFIG streaming cache, supplied key throw and iterator cleanup."""
import argparse
import json
import os
import sys
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import config_iterator_unpack_review_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64
PREFIX = r"""
dec $test_config_iterator_peer_front(pstate, nat) : bool
def $test_config_iterator_peer_front(S, 0) = true
  -- if S.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_config_iterator_peer_front(S, 1) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "key-start") :: ptask_tail*
  -- if |pconfigiterator.ITEMS| = 1
def $test_config_iterator_peer_front(S, 2) = true
  -- if S.TODO = (THROW_VALUE porigin z) :: ptask_body*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = UNPACK_ITERATOR_TARGET n porigin_method
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (CONFIG_ITERATOR pconfigiterator "key") :: ptask_tail*
def $test_config_iterator_peer_front(S, 3) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_ITERATOR pconfigiterator "key") :: ptask_tail*
def $test_config_iterator_peer_front(S, 4) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_option),NAMED_SENT (KNOWN pvalue_value)]
  -- if $string_bytes(pvalue_option) = ($ptascii("precision"))
  -- if $string_bytes(pvalue_value) = ($ptascii("9"))
def $test_config_iterator_peer_front(S, 5) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if S.ITERATORS = eps
  -- if S.DESTRUCTION.OPERATIONS = eps
def $test_config_iterator_peer_front(S, n_stage) = false -- otherwise
dec $test_config_iterator_peer_seek(pstate, nat, nat) : pstate
def $test_config_iterator_peer_seek(S, n_stage, 0) = S
def $test_config_iterator_peer_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_config_iterator_peer_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ (S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
def $test_config_iterator_peer_seek(S, n_stage, n) = $test_config_iterator_peer_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_config_iterator_peer_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps \/ S.CURRENT =/= eps \/ S.FRAMES =/= eps
dec $test_config_iterator_peer_step(pstate) : pstate
def $test_config_iterator_peer_step(S) = S_next
  -- PhpStep: S ~> S_next
"""


def reach(state, start, stage):
    return [state + '_found = $test_config_iterator_peer_seek(' + start + ',' + str(stage) + ',3000)',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_config_iterator_peer_front(' + state + ',' + str(stage) + ')']


def unchanged(after, before, fields):
    return [after + '.' + field + ' = ' + before + '.' + field for field in fields.split()]


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)',
        state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)',
        state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def checks(program, path, name):
    assert name == 'selected-config-iterator-key-throw-preserves-unsent-current-and-setter'
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *reach('S_pre','S_initial',0),
        'S_pre.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*',
        'pconfigcall.KIND = INTRINSIC_INI_SET', 'pconfigcall.INDEX = 0',
        'pconfigcall.OWNER = eps', 'pconfigcall.SELECTION = (n_selection)',
        'pconfigcall.SENT = eps', 'pconfigcall.PACKS = eps', '~pconfigcall.NAMED',
        '$config_pending_valid(S_pre,pconfigcall,true)', '~$config_invoke_valid(S_pre,pconfigcall)',
        '$intrinsic_count(S_pre,pconfigcall.SITE) = (1)',
        '$intrinsic_argument(S_pre,pconfigcall.SITE,0) = ((expression,true,eps,porigin_argument,z_argument))',
        'S_pre.RESULT = VARIABLE ' + text('iterator') + ' z_argument',
        '$lookup(S_pre.ENV,' + text('iterator') + ') = (n_iterator_cell)',
        'S_pre.STORE[n_iterator_cell] = DEFINED (POBJECT n_object)',
        '$lookup(S_pre.ENV,' + text('hold') + ') = (n_hold_cell)',
        'S_pre.STORE[n_hold_cell] = DEFINED (POBJECT n_object)',
        '$useriter_instance(S_pre,n_object)', 'S_pre.OBJECTS[n_object] = INSTANCE porigin_class',
        '$lookup(S_pre.ENV,' + text('call') + ') = (n_call_cell)',
        'S_pre.STORE[n_call_cell] = DEFINED pvalue_original',
        '$string_bytes(pvalue_original) = (' + text('InI_SeT') + ')',
        '$lookup(S_pre.ENV,' + text('keep') + ') = (n_keep_cell)',
        'S_pre.STORE[n_keep_cell] = DEFINED pvalue_original',
        '$lookup(S_pre.ENV,' + text('result') + ') = (n_result_cell)',
        'S_pre.STORE[n_result_cell] = DEFINED (PINT 99)',
        '$lookup(S_pre.ENV,' + text('effects') + ') = (n_effects_cell)',
        'S_pre.STORE[n_effects_cell] = DEFINED (PINT 0)',
        '$lookup(S_pre.ENV,' + text('saved') + ') = (n_saved_cell)',
        'S_pre.STORE[n_saved_cell] = DEFINED PNULL',
        'S_pre.SELECTEDCALLS[n_selection] = pselectedcall',
        'pselectedcall.KIND = INTRINSIC_INI_SET', 'pselectedcall.ORIGINAL = ' + text('InI_SeT'),
        '$selected_entry_valid(S_pre,pselectedcall)',
        '$selected_task_count(S_pre.TODO,n_selection) = 1', '$config_nodes(pconfigcall) = eps',
        'S_pre.PRECISIONINI = ' + text('14'), 'S_pre.CURRENT = eps', 'S_pre.FRAMES = eps',
        '$heap_owners($heap_graph(S_pre),HOBJECT n_object) = 2',
        '$test_outputs(S_pre.EVENTS) = ' + text('B|'), *common.public('S_pre'),
        *common.step('S_start','S_pre'),
        'S_start.TODO = (CONFIG_ITERATOR pconfigiterator_start "rewind-start") :: ptask_tail*',
        'pconfigiterator_start.CALL = pconfigcall', 'pconfigiterator_start.OBJECT = n_object',
        'pconfigiterator_start.INPUT = S_pre.RESULT', 'pconfigiterator_start.ITERATOR = n_iterator',
        'n_iterator = S_pre.NEXTITER', 'S_start.NEXTITER = $(n_iterator + 1)',
        'pconfigiterator_start.ITEMS = eps', 'pconfigiterator_start.CURRENT = KNOWN PNULL',
        'pconfigiterator_start.KEY = KNOWN PNULL', 'S_start.ORIGIN = (porigin_argument)',
        '$iterator_lookup(S_start.ITERATORS,n_iterator) = (OBJECTITER n_iterator n_object 0 false)',
        '$config_iterator_valid(S_start,pconfigiterator_start,"rewind-start")',
        '$config_iterator_nodes(pconfigiterator_start,"rewind-start") = [HOBJECT n_object]',
        '$selected_task_count(S_start.TODO,n_selection) = 1',
        '$heap_owners($heap_graph(S_start),HOBJECT n_object) = 3',
        *unchanged('S_start','S_pre','ARRAYS ALLOCATIONS STORE ENV SOURCES CODE POOLS EVENTS SELECTEDCALLS STRINGDATA'),
        *common.public('S_start'), *reach('S_key','S_start',1),
        'S_key.TODO = (CONFIG_ITERATOR pconfigiterator_key "key-start") :: ptask_tail*',
        'pconfigiterator_key.CALL = pconfigcall', 'pconfigiterator_key.OBJECT = n_object',
        'pconfigiterator_key.INPUT = pconfigiterator_start.INPUT',
        'pconfigiterator_key.ITERATOR = n_iterator',
        'pconfigiterator_key.ITEMS = [ENTRY (KINT 5) (DIRECT pvalue_option)]',
        '$string_bytes(pvalue_option) = (' + text('precision') + ')',
        'pconfigiterator_key.CURRENT = KNOWN pvalue_current',
        '$string_bytes(pvalue_current) = (' + text('8') + ')',
        'pconfigiterator_key.KEY = KNOWN PNULL',
        '$config_iterator_valid(S_key,pconfigiterator_key,"key-start")',
        '$config_iterator_nodes(pconfigiterator_key,"key-start") = [HOBJECT n_object]',
        '$heap_owners($heap_graph(S_key),HOBJECT n_object) = 3',
        'S_key.CURRENT = eps', 'S_key.FRAMES = eps',
        'S_key.SELECTEDCALLS[n_selection] = pselectedcall',
        'S_key.STORE[n_call_cell] = DEFINED pvalue_live_call',
        '$string_bytes(pvalue_live_call) = (' + text('ini_get') + ')',
        'S_key.STORE[n_keep_cell] = DEFINED pvalue_original',
        'S_key.STORE[n_iterator_cell] = DEFINED (POBJECT n_object)',
        'S_key.STORE[n_hold_cell] = DEFINED (POBJECT n_object)',
        'S_key.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_key.STORE[n_effects_cell] = DEFINED (PINT 2)',
        'S_key.ARRAYS = S_pre.ARRAYS',
        'S_key.PRECISIONINI = ' + text('14'),
        '$test_outputs(S_key.EVENTS) = ' + text('B|R|V0|C0|K0|N0|V1|C1|'),
        *common.public('S_key'), *reach('S_throw','S_key',2),
        'S_throw.TODO = (THROW_VALUE porigin_throw z_throw) :: ptask_body*',
        'S_throw.CURRENT = (pcallcontext_key)',
        'pcallcontext_key.TARGET = UNPACK_ITERATOR_TARGET n_object porigin_key',
        'S_throw.FRAMES = [pframe_key]',
        'pframe_key.TODO = (CONFIG_ITERATOR pconfigiterator_key "key") :: ptask_tail*',
        'pcallcontext_key.ARGC = 0', 'pcallcontext_key.EXTRA = eps', 'pcallcontext_key.NAMED = eps',
        '$useriter_frame(S_throw,pcallcontext_key,pframe_key)',
        '$useriter_method_selected(S_throw,n_object,porigin_key,"key")',
        'S_throw.STORE[n_saved_cell] = DEFINED (POBJECT n_exception)',
        'S_throw.OBJECTS[n_exception] = THROWABLE pthrowable', 'pthrowable.KIND = "Exception"',
        '$string_bytes($throwable_field(S_throw,n_exception,"message")) = (' + text('config-iterator-before-api87') + ')',
        '$throwable_field(S_throw,n_exception,"previous") = PNULL',
        '$throwable_field(S_throw,n_exception,"trace") = PARRAY n_trace',
        'S_throw.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_frame))]',
        '$trace_array_field(S_throw,n_frame,' + text('function') + ') = PSTRING ' + text('key'),
        '$trace_array_field(S_throw,n_frame,' + text('class') + ') = PSTRING ' + text('ConfigIteratorReview87'),
        '$trace_array_field(S_throw,n_frame,' + text('type') + ') = PSTRING ' + text('->'),
        '$trace_array_field(S_throw,n_frame,' + text('line') + ') = PINT z_argument',
        '$trace_array_field(S_throw,n_frame,' + text('args') + ') = PARRAY n_args',
        'S_throw.ARRAYS[n_args].ITEMS = eps',
        'S_throw.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_throw.STORE[n_effects_cell] = DEFINED (PINT 3)',
        'S_throw.PRECISIONINI = ' + text('6'),
        '$test_outputs(S_throw.EVENTS) = ' + text('B|R|V0|C0|K0|N0|V1|C1|K1|'),
        *common.public('S_throw'), *common.step('S_throwing','S_throw'),
        'S_throwing.TODO = (THROW_SEARCH n_exception) :: ptask_body*',
        *reach('S_thrown','S_throwing',3),
        'S_thrown.TODO = (THROW_SEARCH n_exception) :: (CONFIG_ITERATOR pconfigiterator_key "key") :: ptask_tail*',
        'S_thrown.CURRENT = eps', 'S_thrown.FRAMES = eps', 'S_thrown.ENV = S_pre.ENV',
        '$iterator_lookup(S_thrown.ITERATORS,n_iterator) = (OBJECTITER n_iterator n_object 0 false)',
        '$heap_owners($heap_graph(S_thrown),HOBJECT n_object) = 3',
        'S_thrown.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_thrown.STORE[n_effects_cell] = DEFINED (PINT 3)',
        'S_thrown.STORE[n_saved_cell] = DEFINED (POBJECT n_exception)',
        'S_thrown.PRECISIONINI = ' + text('6'),
        '$test_outputs(S_thrown.EVENTS) = $test_outputs(S_throw.EVENTS)', *common.public('S_thrown')]
    for field in ('.SITE = PORIGIN 0 eps', '.LINE = $(pconfigcall.LINE + 1)',
            '.INDEX = 1', '.KIND = INTRINSIC_INI_GET', '.NAMED = true',
            '.SELECTION = eps', '.SELECTION = (|S_key.SELECTEDCALLS|)',
            '.OWNER = (|S_key.OBJECTS|)', '.SENT = [NAMED_SENT (KNOWN PNULL)]'):
        values += ['~$config_iterator_valid(S_key,pconfigiterator_key[.CALL = pconfigcall[' + field + ']],"key-start")']
    for field in ('.ITERATOR = S_key.NEXTITER', '.OBJECT = |S_key.OBJECTS|',
            '.INPUT = KNOWN (POBJECT n_object)', '.INPUT = REFERENCE n_iterator_cell',
            '.INPUT = VARIABLE ' + text('hold') + ' z_argument',
            '.INPUT = VARIABLE ' + text('iterator') + ' $(z_argument + 1)',
            '.CURRENT = KNOWN PNULL', '.CURRENT = KNOWN (PINT 8)',
            '.CURRENT = KNOWN (POBJECT n_object)', '.KEY = KNOWN (PINT 5)',
            '.ITEMS = [ENTRY (KINT 5) (ALIAS n_iterator_cell)]',
            '.ITEMS = [ENTRY (KINT 5) (DIRECT PNULL)]',
            '.ITEMS = [ENTRY (KSTRING ' + text('0') + ') (DIRECT pvalue_option)]'):
        values += ['~$config_iterator_valid(S_key,pconfigiterator_key[' + field + '],"key-start")']
    values += ['~$config_iterator_valid(S_key[.CODE = eps],pconfigiterator_key,"key-start")',
        '~$config_iterator_valid(S_key,pconfigiterator_key,"ready")',
        '~$config_iterator_valid(S_key,pconfigiterator_key,"unknown")',
        '$config_traversable_value(S_pre,POBJECT n_object)',
        '~$config_traversable_value(S_pre,PINT 0)',
        'S_last_data = S_thrown[.STORE[n_iterator_cell] = DEFINED PNULL][.STORE[n_hold_cell] = DEFINED PNULL]',
        '$config_iterator_valid(S_last_data,pconfigiterator_key,"key")',
        '$heap_owners($heap_graph(S_last_data),HOBJECT n_object) = 1',
        'S_last_data_scope = S_last_data[.TODO = (THROW_SEARCH n_exception) :: ptask_tail*]',
        '~$config_iterator_discard_allowed(S_last_data_scope,pconfigiterator_key)',
        'S_last_data_stopped = $test_config_iterator_peer_step(S_last_data)',
        'S_last_data_stopped = S_last_data[.COMPLETION = UNSUPPORTED "CONFIG Iterator unpack last cleanup owner"]',
        '$iterator_lookup(S_last_data_stopped.ITERATORS,n_iterator) = (OBJECTITER n_iterator n_object 0 false)',
        '$heap_owners($heap_graph(S_last_data_stopped),HOBJECT n_object) = 1',
        '$selected_task_count(S_last_data_stopped.TODO,n_selection) = 1',
        '$throwable_live(S_last_data_stopped,n_exception)', *common.public('S_last_data_stopped'),
        'S_discard = S_thrown[.TODO = (THROW_SEARCH n_exception) :: ptask_tail*]',
        'S_expected = $config_iterator_discard(S_discard,pconfigiterator_key,"key")',
        *common.step('S_after','S_thrown'), 'S_after = S_expected',
        '$throwable_live(S_after,n_exception)', *common.public('S_after'),
        *reach('S_disposed','S_after',5),
        'S_disposed.TODO = (THROW_SEARCH n_exception) :: ptask_tail*',
        '$iterator_lookup(S_disposed.ITERATORS,n_iterator) = eps',
        '$heap_owners($heap_graph(S_disposed),HOBJECT n_object) = 2',
        '$selected_task_count(S_disposed.TODO,n_selection) = 0',
        'S_disposed.STORE[n_iterator_cell] = DEFINED (POBJECT n_object)',
        'S_disposed.STORE[n_hold_cell] = DEFINED (POBJECT n_object)',
        'S_disposed.STORE[n_saved_cell] = DEFINED (POBJECT n_exception)',
        'S_disposed.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_disposed.STORE[n_effects_cell] = DEFINED (PINT 3)',
        'S_disposed.PRECISIONINI = ' + text('6'),
        '$throwable_field(S_disposed,n_exception,"previous") = PNULL',
        '$test_outputs(S_disposed.EVENTS) = $test_outputs(S_throw.EVENTS)', *common.public('S_disposed')]
    values += [*budget('S_pre'), *budget('S_key'), *budget('S_thrown'),
        *reach('S_recovery','S_disposed',4),
        'S_recovery.TODO = (CONFIG_INVOKE pconfigcall_recovery) :: ptask_recovery*',
        '$config_invoke_valid(S_recovery,pconfigcall_recovery)',
        '$iterator_lookup(S_recovery.ITERATORS,n_iterator) = eps',
        '$heap_owners($heap_graph(S_recovery),HOBJECT n_object) = 2',
        'S_recovery.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_recovery.STORE[n_saved_cell] = DEFINED (POBJECT n_exception)',
        'S_recovery.STORE[n_keep_cell] = DEFINED pvalue_original',
        'S_recovery.PRECISIONINI = ' + text('6'), *common.public('S_recovery'),
        *common.step('S_recovered','S_recovery'),
        'S_recovered.TODO = ptask_recovery*', 'S_recovered.RESULT = KNOWN pvalue_old',
        '$string_bytes(pvalue_old) = (' + text('6') + ')', 'S_recovered.PRECISIONINI = ' + text('9'),
        *unchanged('S_recovered','S_recovery','STORE ENV OBJECTS ARRAYS USERCONSTANTS SELECTEDCALLS EVENTS'),
        *common.public('S_recovered'), 'S_final = $drive_steps(S_recovered,3000)',
        'S_final.COMPLETION = NORMAL', 'S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.ITERATORS = eps', 'S_final.PRECISIONINI = ' + text('9'),
        '$test_outputs(S_final.EVENTS) = ' + text('B|R|V0|C0|K0|N0|V1|C1|K1|I|99|3|ini_get|6|Z|R|6|9|99'),
        *common.public('S_final')]
    return values



def partition(values, part):
    cut = values.index('$heap_valid($heap_graph(S_key))') + 1
    thrown_cut = values.index('$heap_valid($heap_graph(S_thrown))') + 1
    guards_cut = values.index('$heap_valid($heap_graph(S_last_data_stopped))') + 1
    disposed_cut = values.index('$heap_valid($heap_graph(S_disposed))') + 1
    if part == 'entry':
        return values[:cut]
    # No assumed state: replay the source up to the same cached second current.
    setup = [values[0], values[1], *reach('S_pre','S_initial',0),
        'S_pre.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*',
        'pconfigcall.SELECTION = (n_selection)',
        '$intrinsic_argument(S_pre,pconfigcall.SITE,0) = ((expression,true,eps,porigin_argument,z_argument))']
    for name, cell in [('iterator','n_iterator_cell'), ('hold','n_hold_cell'),
            ('keep','n_keep_cell'), ('result','n_result_cell'),
            ('effects','n_effects_cell'), ('saved','n_saved_cell')]:
        setup += ['$lookup(S_pre.ENV,' + text(name) + ') = (' + cell + ')']
    setup += ['S_pre.STORE[n_iterator_cell] = DEFINED (POBJECT n_object)',
        'S_pre.STORE[n_keep_cell] = DEFINED pvalue_original',
        *reach('S_key','S_pre',1),
        'S_key.TODO = (CONFIG_ITERATOR pconfigiterator_key "key-start") :: ptask_tail*',
        'pconfigiterator_key.ITERATOR = n_iterator',
        'pconfigiterator_key.ITEMS = [ENTRY (KINT 5) (DIRECT pvalue_option)]']
    assert not any('S_start' in value for value in values[cut:])
    if part == 'throw':
        return setup + values[cut:thrown_cut]
    setup += [*reach('S_throw','S_key',2),
        'S_throw.TODO = (THROW_VALUE porigin_throw z_throw) :: ptask_body*',
        'S_throw.STORE[n_saved_cell] = DEFINED (POBJECT n_exception)',
        *reach('S_thrown','S_throw',3),
        'S_thrown.TODO = (THROW_SEARCH n_exception) :: (CONFIG_ITERATOR pconfigiterator_key "key") :: ptask_tail*']
    if part == 'guards':
        return setup + values[thrown_cut:guards_cut]
    if part == 'discard':
        return setup + values[guards_cut:disposed_cut]
    setup += [*reach('S_disposed','S_thrown',5),
        'S_disposed.TODO = (THROW_SEARCH n_exception) :: ptask_tail*']
    return setup + values[disposed_cut:]


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['prepare', 'check'], required=True)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--part', choices=['entry', 'throw', 'guards', 'discard', 'recovery', 'all'], default='all')
    args = parser.parse_args()
    driver.sources, driver.PREFIX = sources, PREFIX
    for part in (['entry', 'throw', 'guards', 'discard', 'recovery'] if args.part == 'all' else [args.part]):
        driver.checks = lambda program, path, name: partition(checks(program,path,name),part)
        sys.argv = [sys.argv[0], '--phase', args.phase, '--sources', str(args.sources),
            '--output', str(args.output / part)]
        driver.main()


if __name__ == '__main__':
    main()
