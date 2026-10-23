#!/usr/bin/env python3
"""Reached WeakMap key rejection preserves current, call ownership and recovery."""
import json
import os
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import config_weakmap_unpack_review_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64
MESSAGE = 'Keys must be of type int|string during argument unpacking'
PREFIX = r"""
dec $test_config_weakmap_peer_front(pstate, nat) : bool
def $test_config_weakmap_peer_front(S, 0) = true
  -- if S.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_config_weakmap_peer_front(S, 1) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_option),NAMED_SENT (KNOWN pvalue_value)]
  -- if $string_bytes(pvalue_option) = ($ptascii("precision"))
  -- if $string_bytes(pvalue_value) = ($ptascii("9"))
def $test_config_weakmap_peer_front(S, n_stage) = false -- otherwise
dec $test_config_weakmap_peer_seek(pstate, nat, nat) : pstate
def $test_config_weakmap_peer_seek(S, n_stage, 0) = S
def $test_config_weakmap_peer_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_config_weakmap_peer_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ (S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
def $test_config_weakmap_peer_seek(S, n_stage, n) = $test_config_weakmap_peer_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_config_weakmap_peer_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps \/ S.CURRENT =/= eps \/ S.FRAMES =/= eps
dec $test_config_weakmap_peer_step(pstate) : pstate
def $test_config_weakmap_peer_step(S) = S_next
  -- PhpStep: S ~> S_next
"""


def reach(state, start, stage):
    return [state + '_found = $test_config_weakmap_peer_seek(' + start + ',' + str(stage) + ',3000)',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_config_weakmap_peer_front(' + state + ',' + str(stage) + ')']


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)',
        state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)',
        state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def owners(state, callee):
    return ['$heap_owners($heap_graph(' + state + '),HOBJECT ' + node + ') = ' + str(count)
        for node, count in [('n_map', 2), ('n_key', 2), ('n_current', 1), ('n_owner', callee)]]


def checks(program, path, name):
    assert name == 'retained-config-weakmap-key-error-precedes-owning-current-and-api'
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *reach('S', 'S_initial', 0),
        'S.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*',
        'S.ORIGIN = (pconfigcall.SITE)', 'pconfigcall.KIND = INTRINSIC_INI_SET',
        'pconfigcall.INDEX = 0', 'pconfigcall.SENT = eps', 'pconfigcall.PACKS = eps',
        '~pconfigcall.NAMED', 'pconfigcall.OWNER = (n_owner)', 'pconfigcall.SELECTION = eps',
        '$config_pending_valid(S,pconfigcall,true)', '~$config_invoke_valid(S,pconfigcall)',
        '$intrinsic_argument(S,pconfigcall.SITE,0) = ((expression,true,eps,porigin_argument,z_argument))',
        'pconfigcall.LINE = 10', 'z_argument = 11',
        'S.RESULT = VARIABLE ' + text('map') + ' z_argument',
        '$lookup(S.ENV,' + text('map') + ') = (n_map_cell)',
        'S.STORE[n_map_cell] = DEFINED (POBJECT n_map)',
        '$lookup(S.ENV,' + text('mapHold') + ') = (n_map_hold)',
        'S.STORE[n_map_hold] = DEFINED (POBJECT n_map)',
        '$lookup(S.ENV,' + text('key') + ') = (n_key_cell)',
        'S.STORE[n_key_cell] = DEFINED (POBJECT n_key)',
        '$lookup(S.ENV,' + text('keyHold') + ') = (n_key_hold)',
        'S.STORE[n_key_hold] = DEFINED (POBJECT n_key)',
        'S.OBJECTS[n_map] = WEAKMAP (pweakmapentry)',
        'pweakmapentry.KEY = n_key', 'pweakmapentry.VALUE = POBJECT n_current',
        'S.OBJECTS[n_current] = INSTANCE porigin_current',
        '$node_children(S,HOBJECT n_map) = [HOBJECT n_current]',
        '$node_children(S,HOBJECT n_current) = eps',
        '$lookup(S.ENV,' + text('call') + ') = (n_call_cell)',
        '$lookup(S.ENV,' + text('keep') + ') = (n_keep_cell)',
        'S.STORE[n_call_cell] = DEFINED (POBJECT n_owner)',
        'S.STORE[n_keep_cell] = DEFINED (POBJECT n_owner)',
        'S.OBJECTS[n_owner] = INTRINSICCLOSURE INTRINSIC_INI_SET',
        '$lookup(S.ENV,' + text('result') + ') = (n_result_cell)',
        'S.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S.PRECISIONINI = ' + text('14'), 'S.CURRENT = eps', 'S.FRAMES = eps',
        'S.ITERATORS = eps', '$test_outputs(S.EVENTS) = ' + text('B|'),
        '$config_weakmap_scope(S,pconfigcall,S.RESULT,n_map)',
        '$config_traversable_value(S,POBJECT n_map)',
        '~$config_traversable_value(S,POBJECT n_key)', *owners('S', 3), *common.public('S')]
    for label, update in [('site', '.SITE = PORIGIN 0 eps'),
            ('line', '.LINE = $(pconfigcall.LINE + 1)'),
            ('index', '.INDEX = 1'), ('kind', '.KIND = INTRINSIC_INI_GET'),
            ('named', '.NAMED = true'), ('owner', '.OWNER = eps'),
            ('other_owner', '.OWNER = (n_map)'),
            ('sent', '.SENT = [NAMED_SENT (KNOWN PNULL)]')]:
        call, state = 'pconfigcall_bad_' + label, 'S_bad_' + label
        values += [call + ' = pconfigcall[' + update + ']',
            state + ' = S[.TODO = (CONFIG_UNPACK_PREP ' + call + ') :: ptask_tail*][.ORIGIN = (' + call + '.SITE)]',
            '~$config_weakmap_scope(' + state + ',' + call + ',' + state + '.RESULT,n_map)']
    values += ['~$config_weakmap_scope(S[.CODE = eps],pconfigcall,S.RESULT,n_map)',
        '~$config_weakmap_scope(S,pconfigcall,KNOWN (POBJECT n_map),n_map)',
        '~$config_weakmap_scope(S,pconfigcall,VARIABLE ' + text('mapHold') + ' z_argument,n_map)',
        'S_no_map = S[.STORE[n_map_cell] = DEFINED PNULL][.STORE[n_map_hold] = DEFINED PNULL]',
        '~$config_weakmap_scope(S_no_map,pconfigcall,S.RESULT,n_map)',
        'S_no_key = S[.STORE[n_key_cell] = DEFINED PNULL][.STORE[n_key_hold] = DEFINED PNULL]',
        '~$config_weakmap_scope(S_no_key,pconfigcall,S.RESULT,n_map)',
        'S_no_callee = S[.STORE[n_call_cell] = DEFINED PNULL][.STORE[n_keep_cell] = DEFINED PNULL]',
        '$config_pending_valid(S_no_callee,pconfigcall,true)',
        '$heap_owners($heap_graph(S_no_callee),HOBJECT n_owner) = 1',
        '~$config_weakmap_scope(S_no_callee,pconfigcall,S.RESULT,n_map)',
        'S_refused = $test_config_weakmap_peer_step(S_no_callee)',
        'S_refused = S_no_callee[.COMPLETION = UNSUPPORTED "CONFIG WeakMap unpack outside borrowed quiet domain"]',
        'S_raw = $test_config_weakmap_peer_step(S)',
        'S_raw = S[.COMPLETION = THROWN "Error" (' + text(MESSAGE) + ') z_argument]',
        '$heap_graph(S_raw) = $heap_graph(S)',
        *common.step('S_error', 'S'),
        'S_error.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
        'S_error.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "Error"',
        'pthrowable.ORIGIN = (pconfigcall.SITE)',
        '$string_bytes($throwable_field(S_error,n_error,"message")) = (' + text(MESSAGE) + ')',
        '$throwable_field(S_error,n_error,"line") = PINT z_argument',
        '$string_bytes($throwable_field(S_error,n_error,"file")) = ($call_sourcefile(S.FILES,pconfigcall.SITE))',
        '$throwable_field(S_error,n_error,"previous") = PNULL',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
        'n_trace = |S.ARRAYS|', 'S_error.ARRAYS[n_trace].ITEMS = eps',
        '|S_error.ARRAYS| = $(|S.ARRAYS| + 1)',
        'S_error.OBJECTS[0:|S.OBJECTS|] = S.OBJECTS',
        'S_error.STORE = S.STORE', 'S_error.ENV = S.ENV',
        'S_error.ITERATORS = S.ITERATORS', 'S_error.NEXTITER = S.NEXTITER',
        'S_error.PRECISIONINI = S.PRECISIONINI', 'S_error.EVENTS = S.EVENTS',
        *owners('S_error', 2), *common.public('S_error'),
        *budget('S'), *budget('S_error'), *reach('S_recovery', 'S_error', 1),
        'S_recovery.TODO = (CONFIG_INVOKE pconfigcall_recovery) :: ptask_recovery*',
        '$config_invoke_valid(S_recovery,pconfigcall_recovery)',
        'pconfigcall_recovery.OWNER = (n_owner)',
        '$lookup(S_recovery.ENV,' + text('e') + ') = (n_error_cell)',
        'S_recovery.STORE[n_error_cell] = DEFINED (POBJECT n_error)',
        'S_recovery.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_recovery.OBJECTS[n_map] = S.OBJECTS[n_map]',
        'S_recovery.PRECISIONINI = ' + text('14'),
        *owners('S_recovery', 3), *common.public('S_recovery'),
        *common.step('S_recovered', 'S_recovery'),
        'S_recovered.TODO = ptask_recovery*', 'S_recovered.RESULT = KNOWN pvalue_old',
        '$string_bytes(pvalue_old) = (' + text('14') + ')',
        'S_recovered.PRECISIONINI = ' + text('9'),
        'S_recovered.STORE = S_recovery.STORE',
        'S_recovered.OBJECTS = S_recovery.OBJECTS',
        'S_recovered.ARRAYS = S_recovery.ARRAYS',
        *owners('S_recovered', 2), *common.public('S_recovered'),
        'S_final = $drive_steps(S_recovered,3000)',
        'S_final.COMPLETION = NORMAL', 'S_final.TODO = eps',
        'S_final.CURRENT = eps', 'S_final.FRAMES = eps', 'S_final.ITERATORS = eps',
        'S_final.PRECISIONINI = ' + text('9'),
        '$test_outputs(S_final.EVENTS) = ' + text('B|E|' + MESSAGE + '|11|T|99|14|V|Z|R|14|9|99'),
        *common.public('S_final')]
    return values


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
