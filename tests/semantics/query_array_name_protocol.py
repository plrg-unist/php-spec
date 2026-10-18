#!/usr/bin/env python3
"""Reached query array-name errors preserve the captured array graph and COW."""
import json
import os
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import query_array_name_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64

PREFIX = r"""
dec $test_query_array_front(pstate, pintrinsic) : bool
def $test_query_array_front(S, pintrinsic) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = pintrinsic
  -- if $dynamic_query_array_call(pconfigcall)
def $test_query_array_front(S, pintrinsic) = false -- otherwise
dec $test_query_array_seek(pstate, pintrinsic, nat) : pstate
def $test_query_array_seek(S, pintrinsic, 0) = S
def $test_query_array_seek(S, pintrinsic, n) = S
  -- if $(n > 0)
  -- if $test_query_array_front(S,pintrinsic) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_query_array_seek(S, pintrinsic, n) = $test_query_array_seek($drive_steps($test_running(S),1),pintrinsic,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_query_array_front(S,pintrinsic)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def front(state, start, kind):
    call, array = 'pconfigcall_' + state, 'n_array_' + state
    return [state + '_found = $test_query_array_seek(' + start + ',' + kind + ',3000)',
        state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_query_array_front(' + state + ',' + kind + ')',
        state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
        call + '.KIND = ' + kind, call + '.SENT = [NAMED_SENT (KNOWN (PARRAY ' + array + '))]',
        call + '.INDEX = 1', '$intrinsic_count(' + state + ',' + call + '.SITE) = (1)',
        call + '.OWNER = eps', call + '.PACKS = eps', '~' + call + '.NAMED',
        '$config_invoke_valid(' + state + ',' + call + ')',
        '$dynamic_query_array_valid(' + state + ',' + call + ')',
        '~$dynamic_query_arity_call(' + call + ')',
        '~$dynamic_scalar_constant_call(' + call + ')',
        '~$dynamic_null_constant_call(' + call + ')',
        '$dynamic_query_array_entries(' + state + ',' + state + '.ARRAYS[' + array + '].ITEMS)',
        *common.public(state)]


def error(after, before, api):
    call, array = 'pconfigcall_' + before, 'n_array_' + before
    return [*common.step(after, before),
        after + '.TODO = (THROW_SEARCH n_throw_' + after + ') :: ptask_' + before + '*',
        after + '.OBJECTS[n_throw_' + after + '] = THROWABLE pthrowable_' + after,
        'pthrowable_' + after + '.KIND = "TypeError"', 'pthrowable_' + after + '.ORIGIN = (' + call + '.SITE)',
        '$string_bytes($throwable_field(' + after + ',n_throw_' + after + ',"message")) = (' + text(api+'(): Argument #1 ($'+('name' if api == 'constant' else 'constant_name')+') must be of type string, array given') + ')',
        '$throwable_field(' + after + ',n_throw_' + after + ',"previous") = PNULL',
        '$throwable_field(' + after + ',n_throw_' + after + ',"line") = PINT ' + call + '.LINE',
        '$string_bytes($throwable_field(' + after + ',n_throw_' + after + ',"file")) = ($call_sourcefile(' + before + '.FILES,' + call + '.SITE))',
        '$throwable_field(' + after + ',n_throw_' + after + ',"trace") = PARRAY n_trace_' + after,
        after + '.ARRAYS[n_trace_' + after + '].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_api_' + after + '))]',
        '$trace_array_field(' + after + ',n_api_' + after + ',' + text('function') + ') = PSTRING ' + text(api),
        '$trace_array_field(' + after + ',n_api_' + after + ',' + text('line') + ') = PINT ' + call + '.LINE',
        '$trace_array_field(' + after + ',n_api_' + after + ',' + text('args') + ') = PARRAY n_args_' + after,
        after + '.ARRAYS[n_args_' + after + '].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY ' + array + '))]',
        '$node_children(' + after + ',HARRAY n_args_' + after + ') = [HARRAY ' + array + ']',
        after + '.ARRAYS[' + array + '] = ' + before + '.ARRAYS[' + array + ']',
        *[after + '.' + field + ' = ' + before + '.' + field for field in ('STORE','ENV','USERCONSTANTS','STRINGDATA','SELECTEDCALLS','EVENTS','SOURCES','POOLS','FILES','STATICS','ERRORHANDLER','PRECISIONINI','AUTOLOAD','AUTOSEQ','CLASSNAMES','CLASSCONSTANTCACHE','REFCELLS')],
        *common.public(after)]


def refusals(state):
    call = 'pconfigcall_' + state
    values = []
    for field in ('.SITE = PORIGIN 0 eps', '.LINE = $(' + call + '.LINE + 1)', '.SELECTION = (|' + state + '.SELECTEDCALLS|)', '.KIND = INTRINSIC_DEFINE'):
        values += ['~$dynamic_query_array_valid(' + state + ',' + call + '[' + field + '])']
    for field in ('.OWNER = (0)', '.NAMED = true', '.SENT = eps', '.SENT = ' + call + '.SENT ++ [NAMED_SENT (KNOWN PNULL)]', '.SENT = [NAMED_SENT (KNOWN PNULL)]'):
        values += ['~$dynamic_query_array_call(' + call + '[' + field + '])']
    values += ['pconfigcall_' + state + '_dead = ' + call + '[.SENT = [NAMED_SENT (KNOWN (PARRAY (|' + state + '.ARRAYS|)))]]',
        '$dynamic_query_array_call(pconfigcall_' + state + '_dead)',
        '~$dynamic_query_array_valid(' + state + ',pconfigcall_' + state + '_dead)']
    for item in ('DIRECT (PARRAY 0)', 'DIRECT (POBJECT 0)', 'UNINITIALIZED', 'ALIAS (|' + state + '.STORE|)'):
        values += ['~$dynamic_query_array_entries(' + state + ',[ENTRY (KINT 0) (' + item + ')])']
    values += ['$dynamic_query_array_entries(' + state + ',[ENTRY (KINT 0) (DIRECT PNULL),ENTRY (KINT 1) (DIRECT (PBOOL false)),ENTRY (KINT 2) (DIRECT (PINT 51)),ENTRY (KINT 3) (DIRECT (PFLOAT 4609434218613702656))])',
        '~$dynamic_query_array_entries(' + state + ',[ENTRY (KINT 0) (DIRECT (PSTRING_CARRIER (REQUEST_STRING (|' + state + '.STRINGDATA|)) ' + text('invalid51') + '))])']
    return values


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)', state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)', state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def literal_authority(state):
    call, array = 'pconfigcall_' + state, 'n_array_' + state
    return ['$intrinsic_argument(' + state + ',' + call + '.SITE,0) = ((expression,false,eps,porigin_literal_' + state + ',z_literal_' + state + '))',
        '$compiled_read(' + state + ',porigin_literal_' + state + ') = (PARRAY n_literal_' + state + ')',
        '$dynamic_array_known_matches(' + state + ',PARRAY ' + array + ',(PARRAY n_literal_' + state + '))',
        'n_changed_' + state + ' = |' + state + '.ARRAYS|',
        state + '_changed = ' + state + '[.ARRAYS = ' + state + '.ARRAYS ++ [$array_insert($array_empty(),KINT 0,DIRECT (PINT 999))]][.ALLOCATIONS = ' + state + '.ALLOCATIONS ++ [HARRAY n_changed_' + state + ']]',
        'pconfigcall_' + state + '_changed = ' + call + '[.SENT = [NAMED_SENT (KNOWN (PARRAY n_changed_' + state + '))]]',
        '$dynamic_query_array_call(pconfigcall_' + state + '_changed)',
        '$config_invoke_valid(' + state + '_changed,pconfigcall_' + state + '_changed)',
        '~$dynamic_query_array_valid(' + state + '_changed,pconfigcall_' + state + '_changed)']


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')', 'S_initial.COMPLETION = BUDGET']
    if name == 'literal-empty-array-query-names':
        values += [*front('S', 'S_initial', 'INTRINSIC_DEFINED'),
            'S.ARRAYS[n_array_S].ITEMS = eps', '~$config_strict(S,pconfigcall_S)',
            '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            *error('S_error', 'S', 'defined'), *literal_authority('S'),
            *front('S_constant', 'S_error', 'INTRINSIC_CONSTANT'),
            'S_constant.ARRAYS[n_array_S_constant].ITEMS = eps',
            *error('S_constant_error', 'S_constant', 'constant'),
            'S_constant_error.STORE[n_result] = DEFINED (PINT 99)', *refusals('S_constant'), *budget('S'), *budget('S_constant')]
    elif name == 'selected-constant-array-name-keeps-captured-cow-value':
        values += [*front('S', 'S_initial', 'INTRINSIC_CONSTANT'), '~$config_strict(S,pconfigcall_S)',
            'pconfigcall_S.SELECTION = (n_selection)', 'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_CONSTANT',
            'S.ARRAYS[n_array_S].ITEMS = [ENTRY (KSTRING ' + text('first') + ') (DIRECT pvalue_leaf),ENTRY (KINT 3) (DIRECT PNULL)]',
            'pvalue_leaf = PSTRING_CARRIER (REQUEST_STRING n_leaf) preqbytes_leaf',
            'preqbytes_leaf = ' + text('captured-array51'), '$string_carrier_valid(S,pvalue_leaf)',
            '$lookup(S.ENV,' + text('call') + ') = (n_call)', 'S.STORE[n_call] = DEFINED pvalue_live_call',
            '$string_bytes(pvalue_live_call) = (' + text('defined') + ')',
            '$lookup(S.ENV,' + text('effects') + ') = (n_effects)', 'S.STORE[n_effects] = DEFINED (PINT 1)',
            '$test_outputs(S.EVENTS) = ' + text('B|N|'), *error('S_error', 'S', 'constant'),
            'S_bad_leaf = S[.ARRAYS = $array_replace(S.ARRAYS,n_array_S,$array_insert(S.ARRAYS[n_array_S],KSTRING ' + text('first') + ',DIRECT (PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) preqbytes_leaf)))]',
            '~$dynamic_query_array_valid(S_bad_leaf,pconfigcall_S)',
            *refusals('S'), *budget('S'),
            'S_end = $drive_steps(S_error,3000)', 'S_end.COMPLETION = NORMAL', 'S_end.TODO = eps',
            '$lookup(S_end.ENV,' + text('name') + ') = (n_name)', 'S_end.STORE[n_name] = DEFINED (PARRAY n_name_array)',
            '$lookup(S_end.ENV,' + text('snapshot') + ') = (n_snapshot)', 'S_end.STORE[n_snapshot] = DEFINED (PARRAY n_array_S)',
            'n_name_array =/= n_array_S',
            '$entry_lookup(S_end.ARRAYS[n_name_array].ITEMS,KSTRING ' + text('first') + ') = (DIRECT pvalue_caller)',
            '$string_bytes(pvalue_caller) = (' + text('caller-array51') + ')',
            '$entry_lookup(S_end.ARRAYS[n_array_S].ITEMS,KSTRING ' + text('first') + ') = (DIRECT pvalue_leaf)',
            '$lookup(S_end.ENV,' + text('trace') + ') = (n_trace_cell)', 'S_end.STORE[n_trace_cell] = DEFINED (PARRAY n_trace_copy)',
            '$entry_lookup(S_end.ARRAYS[n_trace_copy].ITEMS,KINT 0) = (DIRECT (PARRAY n_trace_frame_copy))',
            '$trace_array_field(S_end,n_trace_frame_copy,' + text('args') + ') = PARRAY n_trace_args_copy',
            '$entry_lookup(S_end.ARRAYS[n_trace_args_copy].ITEMS,KINT 0) = (DIRECT (PARRAY n_trace_name_copy))',
            'n_trace_name_copy =/= n_array_S', 'n_trace_name_copy =/= n_name_array',
            '$entry_lookup(S_end.ARRAYS[n_trace_name_copy].ITEMS,KSTRING ' + text('first') + ') = (DIRECT pvalue_trace_leaf)',
            '$string_bytes(pvalue_trace_leaf) = (' + text('trace-array51') + ')', *common.public('S_end')]
    else:
        assert name == 'strict-defined-flat-array-name-type-error'
        values += [*front('S', 'S_initial', 'INTRINSIC_DEFINED'), '$config_strict(S,pconfigcall_S)',
            'S.ARRAYS[n_array_S].ITEMS = [ENTRY (KINT 0) (DIRECT (PBOOL true)),ENTRY (KINT 1) (DIRECT (PINT 1277)),ENTRY (KINT 2) (DIRECT (PFLOAT 4609434218613702656))]',
            *error('S_error', 'S', 'defined'), *literal_authority('S'), *refusals('S'), *budget('S')]
    return values


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
