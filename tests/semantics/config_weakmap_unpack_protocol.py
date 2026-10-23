#!/usr/bin/env python3
"""Empty WeakMap traversal reaches zero-argument API reception without owners."""
import json
import os
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import config_weakmap_unpack_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64
MESSAGE = 'ini_set() expects exactly 2 arguments, 0 given'
CASES = ('empty-weakmap-reaches-config-arity-after-traversal',
    'retained-empty-weakmap-arity-preserves-wrapper-and-setter')
PREFIX = r"""
dec $test_config_weakmap_front(pstate, nat) : bool
def $test_config_weakmap_front(S, 0) = true
  -- if S.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_config_weakmap_front(S, 1) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_option),NAMED_SENT (KNOWN pvalue_value)]
  -- if $string_bytes(pvalue_option) = ($ptascii("precision"))
  -- if $string_bytes(pvalue_value) = ($ptascii("9"))
def $test_config_weakmap_front(S, n) = false -- otherwise
dec $test_config_weakmap_seek(pstate, nat, nat) : pstate
def $test_config_weakmap_seek(S, n_stage, 0) = S
def $test_config_weakmap_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_config_weakmap_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ (S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
def $test_config_weakmap_seek(S, n_stage, n) = $test_config_weakmap_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_config_weakmap_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~(S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
dec $test_config_weakmap_step(pstate) : pstate
def $test_config_weakmap_step(S) = S_next
  -- PhpStep: S ~> S_next
"""


def reach(state, start, stage):
    return [state + '_found = $test_config_weakmap_seek(' + start + ',' + str(stage) + ',3000)',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_config_weakmap_front(' + state + ',' + str(stage) + ')']


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)',
        state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)',
        state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def checks(program, path, name):
    assert name in CASES
    owned = name == CASES[1]
    line = 5 if owned else 4
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *reach('S', 'S_initial', 0),
        'S.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*',
        'S.ORIGIN = (pconfigcall.SITE)', 'pconfigcall.KIND = INTRINSIC_INI_SET',
        'pconfigcall.INDEX = 0', 'pconfigcall.SENT = eps', 'pconfigcall.PACKS = eps',
        '~pconfigcall.NAMED', '$config_pending_valid(S,pconfigcall,true)',
        '~$config_invoke_valid(S,pconfigcall)',
        '$intrinsic_argument(S,pconfigcall.SITE,0) = ((expression,true,eps,porigin_argument,z_argument))',
        'pconfigcall.LINE = ' + str(line), 'z_argument = ' + str(line + 1),
        'S.RESULT = VARIABLE ' + text('map') + ' z_argument',
        '$lookup(S.ENV,' + text('map') + ') = (n_map_cell)',
        'S.STORE[n_map_cell] = DEFINED (POBJECT n_map)',
        'S.OBJECTS[n_map] = WEAKMAP eps',
        '$heap_owners($heap_graph(S),HOBJECT n_map) = 2',
        '$lookup(S.ENV,' + text('result') + ') = (n_result_cell)',
        'S.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S.PRECISIONINI = ' + text('14'),
        '$config_traversable_value(S,POBJECT n_map)',
        '$config_weakmap_scope(S,pconfigcall,S.RESULT,n_map)',
        *common.public('S')]
    if owned:
        values += ['pconfigcall.OWNER = (n_owner)',
            'S.OBJECTS[n_owner] = INTRINSICCLOSURE INTRINSIC_INI_SET',
            '$heap_owners($heap_graph(S),HOBJECT n_owner) = 3']
    else:
        values += ['pconfigcall.OWNER = eps']
    values += ['S_raw = $test_config_weakmap_step(S)',
        'S_raw = $config_weakmap_finish(S,pconfigcall,n_map,z_argument)',
        'S_raw.COMPLETION = THROWING n_error',
        'S_raw.TODO = S.TODO', 'S_raw.OBJECTS[n_map] = WEAKMAP eps',
        'S_raw.STORE = S.STORE', 'S_raw.ENV = S.ENV',
        'S_raw.RESULT = KNOWN (PARRAY n_trace)', 'S_raw.BASE = S.BASE',
        'S_raw.ITERATORS = S.ITERATORS', 'S_raw.NEXTITER = S.NEXTITER',
        'S_raw.PRECISIONINI = S.PRECISIONINI', 'S_raw.EVENTS = S.EVENTS',
        'S_raw.OBJECTS[n_error] = THROWABLE pthrowable',
        'pthrowable.KIND = "ArgumentCountError"', 'pthrowable.ORIGIN = (pconfigcall.SITE)',
        '$string_bytes($throwable_field(S_raw,n_error,"message")) = (' + text(MESSAGE) + ')',
        '$throwable_field(S_raw,n_error,"line") = PINT pconfigcall.LINE',
        '$string_bytes($throwable_field(S_raw,n_error,"file")) = ($call_sourcefile(S.FILES,pconfigcall.SITE))',
        '$throwable_field(S_raw,n_error,"previous") = PNULL',
        '$throwable_field(S_raw,n_error,"trace") = PARRAY n_trace']
    if owned:
        values += ['S_raw.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_api)),ENTRY (KINT 1) (DIRECT (PARRAY n_wrapper))]',
            '$trace_array_field(S_raw,n_wrapper,' + text('function') + ') = PSTRING ' + text('__invoke'),
            '$trace_array_field(S_raw,n_wrapper,' + text('class') + ') = PSTRING ' + text('Closure'),
            '$trace_array_field(S_raw,n_wrapper,' + text('args') + ') = PARRAY n_wrapper_args',
            'S_raw.ARRAYS[n_wrapper_args].ITEMS = eps',
            '$heap_owners($heap_graph(S_raw),HOBJECT n_owner) = 3']
    else:
        values += ['S_raw.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_api))]']
    values += ['$trace_array_field(S_raw,n_api,' + text('function') + ') = PSTRING ' + text('ini_set'),
        '$trace_array_field(S_raw,n_api,' + text('line') + ') = PINT pconfigcall.LINE',
        '$trace_array_field(S_raw,n_api,' + text('args') + ') = PARRAY n_api_args',
        'S_raw.ARRAYS[n_api_args].ITEMS = eps',
        '$heap_owners($heap_graph(S_raw),HOBJECT n_map) = 2',
        '$heap_valid($heap_graph(S_raw))',
        *common.step('S_error', 'S'),
        'S_error.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
        'S_error.OBJECTS[n_error] = S_raw.OBJECTS[n_error]',
        *common.public('S_error'),
        *budget('S'), *budget('S_error'), *reach('S_recovery', 'S_error', 1),
        'S_recovery.TODO = (CONFIG_INVOKE pconfigcall_recovery) :: ptask_recovery*',
        '$config_invoke_valid(S_recovery,pconfigcall_recovery)',
        'S_recovery.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_recovery.OBJECTS[n_map] = WEAKMAP eps',
        '$heap_owners($heap_graph(S_recovery),HOBJECT n_map) = 2',
        'S_recovery.PRECISIONINI = ' + text('14')]
    if owned:
        values += ['pconfigcall_recovery.OWNER = (n_owner)',
            '$heap_owners($heap_graph(S_recovery),HOBJECT n_owner) = 3']
    else:
        values += ['pconfigcall_recovery.OWNER = eps']
    values += [*common.step('S_recovered', 'S_recovery'),
        'S_recovered.RESULT = KNOWN pvalue_old',
        '$string_bytes(pvalue_old) = (' + text('14') + ')',
        'S_recovered.PRECISIONINI = ' + text('9'),
        'S_recovered.STORE = S_recovery.STORE',
        'S_recovered.OBJECTS = S_recovery.OBJECTS',
        'S_recovered.ARRAYS = S_recovery.ARRAYS',
        'S_final = $drive_steps(S_recovered,3000)',
        'S_final.COMPLETION = NORMAL', 'S_final.TODO = eps',
        'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.ITERATORS = S.ITERATORS', 'S_final.NEXTITER = S.NEXTITER',
        'S_final.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_final.PRECISIONINI = ' + text('9'),
        '$test_outputs(S_final.EVENTS) = ' + text('B|A|' + MESSAGE + '|' + str(line) +
            '|ini_set|Z' + ('|W|__invoke|Z' if owned else '') + '|99|14|R|14|9'),
        *common.public('S_final')]
    return values


def main():
    sources.family.CASES = {name: sources.family.CASES[name] for name in CASES}
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
