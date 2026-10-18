#!/usr/bin/env python3
"""Reached array-name errors precede define flag reception after all effects."""
import json
import os
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import define_array_name_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64

PREFIX = r"""
dec $test_define_array_name_front(pstate, nat) : bool
def $test_define_array_name_front(S, n_count) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if $dynamic_define_array_name_call(pconfigcall)
  -- if |pconfigcall.SENT| = n_count
def $test_define_array_name_front(S, n_count) = false -- otherwise
dec $test_define_array_name_seek(pstate, nat, nat) : pstate
def $test_define_array_name_seek(S, n_count, 0) = S
def $test_define_array_name_seek(S, n_count, n) = S
  -- if $(n > 0)
  -- if $test_define_array_name_front(S,n_count) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_define_array_name_seek(S, n_count, n) = $test_define_array_name_seek($drive_steps($test_running(S),1),n_count,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_define_array_name_front(S,n_count)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def front(state, start, count, arguments):
    call, array = 'pconfigcall_' + state, 'n_array_' + state
    sent = '[' + ','.join('NAMED_SENT (KNOWN (' + x + '))' for x in ['PARRAY '+array, *arguments]) + ']'
    return [state + '_found = $test_define_array_name_seek(' + start + ',' + str(count) + ',3000)',
        state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_define_array_name_front(' + state + ',' + str(count) + ')',
        state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
        call + '.KIND = INTRINSIC_DEFINE', call + '.SENT = ' + sent,
        call + '.INDEX = ' + str(count), '$intrinsic_count(' + state + ',' + call + '.SITE) = (' + str(count) + ')',
        call + '.OWNER = eps', call + '.PACKS = eps', '~' + call + '.NAMED',
        '$config_invoke_valid(' + state + ',' + call + ')',
        '$dynamic_define_array_name_valid(' + state + ',' + call + ')',
        '$dynamic_scalar_define_arguments(' + state + ',' + call + ',1)',
        '~$dynamic_define_arity_call(' + call + ')', '~$dynamic_query_array_call(' + call + ')',
        '~$dynamic_scalar_define_call(' + call + ')', '~$dynamic_null_define_call(' + call + ')',
        '~$dynamic_scalar_define_flag_call(' + call + ')', '~$dynamic_null_define_flag_call(' + call + ')',
        '~$dynamic_nan_define_flag_call(' + call + ')', *common.public(state)]


def error(after, before, arguments):
    call, array = 'pconfigcall_' + before, 'n_array_' + before
    items = '[' + ','.join('ENTRY (KINT ' + str(i) + ') (DIRECT (' + x + '))' for i,x in enumerate(['PARRAY '+array, *arguments])) + ']'
    return [*common.step(after, before),
        after + '.TODO = (THROW_SEARCH n_throw_' + after + ') :: ptask_' + before + '*',
        after + '.OBJECTS[n_throw_' + after + '] = THROWABLE pthrowable_' + after,
        'pthrowable_' + after + '.KIND = "TypeError"', 'pthrowable_' + after + '.ORIGIN = (' + call + '.SITE)',
        '$string_bytes($throwable_field(' + after + ',n_throw_' + after + ',"message")) = (' + text('define(): Argument #1 ($constant_name) must be of type string, array given') + ')',
        '$throwable_field(' + after + ',n_throw_' + after + ',"previous") = PNULL',
        '$throwable_field(' + after + ',n_throw_' + after + ',"line") = PINT ' + call + '.LINE',
        '$string_bytes($throwable_field(' + after + ',n_throw_' + after + ',"file")) = ($call_sourcefile(' + before + '.FILES,' + call + '.SITE))',
        '$throwable_field(' + after + ',n_throw_' + after + ',"trace") = PARRAY n_trace_' + after,
        after + '.ARRAYS[n_trace_' + after + '].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_api_' + after + '))]',
        '$trace_array_field(' + after + ',n_api_' + after + ',' + text('function') + ') = PSTRING ' + text('define'),
        '$trace_array_field(' + after + ',n_api_' + after + ',' + text('line') + ') = PINT ' + call + '.LINE',
        '$trace_array_field(' + after + ',n_api_' + after + ',' + text('args') + ') = PARRAY n_args_' + after,
        after + '.ARRAYS[n_args_' + after + '].ITEMS = ' + items,
        '$node_children(' + after + ',HARRAY n_args_' + after + ') = [HARRAY ' + array + ']',
        after + '.ARRAYS[' + array + '] = ' + before + '.ARRAYS[' + array + ']',
        *[after + '.' + field + ' = ' + before + '.' + field for field in ('STORE','ENV','USERCONSTANTS','STRINGDATA','SELECTEDCALLS','EVENTS','SOURCES','POOLS','FILES','STATICS','ERRORHANDLER','PRECISIONINI','AUTOLOAD','AUTOSEQ','CLASSNAMES','CLASSCONSTANTCACHE','REFCELLS')],
        *common.public(after)]


def refusals(state):
    call, array = 'pconfigcall_' + state, 'n_array_' + state
    values = []
    for field in ('.SITE = PORIGIN 0 eps', '.LINE = $(' + call + '.LINE + 1)', '.SELECTION = (|' + state + '.SELECTEDCALLS|)', '.INDEX = 0'):
        values += ['~$dynamic_define_array_name_valid(' + state + ',' + call + '[' + field + '])']
    for field in ('.OWNER = (0)', '.NAMED = true', '.KIND = INTRINSIC_CONSTANT', '.KIND = INTRINSIC_DEFINED',
            '.SENT = [NAMED_SENT (KNOWN (PARRAY ' + array + '))]',
            '.SENT = [NAMED_SENT (KNOWN (PARRAY ' + array + ')),NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN PNULL)]',
            '.SENT = $named_slot_set(' + call + '.SENT,0,KNOWN PNULL)'):
        values += ['~$dynamic_define_array_name_call(' + call + '[' + field + '])']
    values += ['~$dynamic_define_array_name_valid(' + state + ',' + call + '[.SENT = $named_slot_set(' + call + '.SENT,0,KNOWN (PARRAY (|' + state + '.ARRAYS|)))])']
    for label, item in (('array', 'PARRAY '+array), ('object', 'POBJECT 0')):
        changed = 'pconfigcall_' + state + '_owning_' + label
        values += [changed + ' = ' + call + '[.SENT = $named_slot_set(' + call + '.SENT,1,KNOWN (' + item + '))]',
            '$dynamic_define_array_name_call(' + changed + ')',
            '~$dynamic_define_array_name_valid(' + state + ',' + changed + ')']
    values += ['~$dynamic_query_array_entries(' + state + ',[ENTRY (KINT 0) (DIRECT (PARRAY ' + array + '))])',
        '~$dynamic_query_array_entries(' + state + ',[ENTRY (KINT 0) (DIRECT (POBJECT 0))])']
    return values


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)', state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)', state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def literal_authority(state):
    call, array = 'pconfigcall_' + state, 'n_array_' + state
    return ['$intrinsic_argument(' + state + ',' + call + '.SITE,0) = ((expression_literal_' + state + ',false,eps,porigin_literal_' + state + ',z_literal_' + state + '))',
        '$compiled_read(' + state + ',porigin_literal_' + state + ') = (PARRAY n_literal_' + state + ')',
        '$dynamic_array_known_matches(' + state + ',PARRAY ' + array + ',(PARRAY n_literal_' + state + '))',
        'n_changed_' + state + ' = |' + state + '.ARRAYS|',
        state + '_changed = ' + state + '[.ARRAYS = ' + state + '.ARRAYS ++ [$array_insert($array_empty(),KINT 0,DIRECT (PINT 999))]][.ALLOCATIONS = ' + state + '.ALLOCATIONS ++ [HARRAY n_changed_' + state + ']]',
        'pconfigcall_' + state + '_changed = ' + call + '[.SENT = $named_slot_set(' + call + '.SENT,0,KNOWN (PARRAY n_changed_' + state + '))]',
        '$dynamic_define_array_name_call(pconfigcall_' + state + '_changed)',
        '$config_invoke_valid(' + state + '_changed,pconfigcall_' + state + '_changed)',
        '~$dynamic_define_array_name_valid(' + state + '_changed,pconfigcall_' + state + '_changed)']


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')', 'S_initial.COMPLETION = BUDGET']
    if name == 'literal-array-define-names-before-ignored-true-warning':
        values += [*front('S', 'S_initial', 2, ['PINT 1301']), 'S.ARRAYS[n_array_S].ITEMS = eps',
            '~$config_strict(S,pconfigcall_S)', 'S.USERCONSTANTS = eps', '$test_outputs(S.EVENTS) = ' + text('B|'),
            *error('S_error', 'S', ['PINT 1301']), *literal_authority('S'),
            *front('S_true', 'S_error', 3, ['PINT 1327','PBOOL true']),
            'S_true.ARRAYS[n_array_S_true].ITEMS = [ENTRY (KINT 0) (DIRECT (PBOOL false)),ENTRY (KINT 1) (DIRECT (PINT 1319))]',
            '$dynamic_constant_case_flag(pconfigcall_S_true)', '~$dynamic_constant_case_valid(S_true,pconfigcall_S_true)',
            *error('S_true_error', 'S_true', ['PINT 1327','PBOOL true']),
            'S_true_error.USERCONSTANTS = eps', *literal_authority('S_true'), *refusals('S_true'), *budget('S'), *budget('S_true'),
            'pconfigcall_changed_candidate = pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,1,KNOWN (PINT 1303))]',
            '$dynamic_define_array_name_call(pconfigcall_changed_candidate)', '~$dynamic_define_array_name_valid(S,pconfigcall_changed_candidate)',
            'pconfigcall_changed_flag = pconfigcall_S_true[.SENT = $named_slot_set(pconfigcall_S_true.SENT,2,KNOWN (PBOOL false))]',
            '$dynamic_define_array_name_call(pconfigcall_changed_flag)', '~$dynamic_define_array_name_valid(S_true,pconfigcall_changed_flag)']
    else:
        strict = name == 'strict-array-define-name-before-third-integer-type-error'
        assert strict or name == 'captured-array-name-before-null-flag-reception'
        arguments = ['PINT 1381','PINT 17'] if strict else ['pvalue_candidate','PNULL']
        values += [*front('S', 'S_initial', 3, arguments), ('$config_strict(S,pconfigcall_S)' if strict else '~$config_strict(S,pconfigcall_S)'),
            'pconfigcall_S.SELECTION = (n_selection)', 'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
            '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            '$lookup(S.ENV,' + text('effects') + ') = (n_effects)', 'S.STORE[n_effects] = DEFINED (PINT ' + ('1' if strict else '2') + ')',
            '$lookup(S.ENV,' + text('call') + ') = (n_call)', 'S.STORE[n_call] = DEFINED pvalue_call',
            '$string_bytes(pvalue_call) = (' + text('constant' if strict else 'defined') + ')',
            '$test_outputs(S.EVENTS) = ' + text('B|F|' if strict else 'B|V|F|'),
            'S.USERCONSTANTS = eps', 'S.ERRORHANDLER.CALLBACK = eps']
        if strict:
            values += ['S.ARRAYS[n_array_S].ITEMS = [ENTRY (KINT 0) (DIRECT (PBOOL true)),ENTRY (KINT 1) (DIRECT (PINT 1373))]', *literal_authority('S')]
        else:
            values += ['S.ARRAYS[n_array_S].ITEMS = [ENTRY (KSTRING ' + text('plain') + ') (DIRECT pvalue_leaf),ENTRY (KINT 4) (DIRECT (PBOOL false))]',
                'pvalue_leaf = PSTRING_CARRIER (REQUEST_STRING n_leaf) preqbytes_leaf', 'preqbytes_leaf = ' + text('captured-name52'),
                'pvalue_candidate = PSTRING_CARRIER (REQUEST_STRING n_candidate) preqbytes_candidate', 'preqbytes_candidate = ' + text('captured-candidate52'),
                '$string_carrier_valid(S,pvalue_leaf)', '$string_carrier_valid(S,pvalue_candidate)',
                '$lookup(S.ENV,' + text('name') + ') = (n_name)', 'S.STORE[n_name] = DEFINED (PARRAY n_live_name)', 'n_live_name =/= n_array_S',
                'S.ARRAYS[n_live_name].ITEMS = [ENTRY (KSTRING ' + text('plain') + ') (DIRECT pvalue_live_name),ENTRY (KINT 4) (DIRECT (PBOOL true))]',
                '$string_bytes(pvalue_live_name) = (' + text('live-name52') + ')',
                '$lookup(S.ENV,' + text('value') + ') = (n_value)', 'S.STORE[n_value] = DEFINED (PINT 997)',
                '$lookup(S.ENV,' + text('flag') + ') = (n_flag)', 'S.STORE[n_flag] = DEFINED (PBOOL true)',
                'pconfigcall_bad_candidate = pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,1,KNOWN (PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) preqbytes_candidate))]',
                '~$dynamic_define_array_name_valid(S,pconfigcall_bad_candidate)',
                'S_bad_leaf = S[.ARRAYS = $array_replace(S.ARRAYS,n_array_S,$array_insert(S.ARRAYS[n_array_S],KSTRING ' + text('plain') + ',DIRECT (PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) preqbytes_leaf)))]',
                '~$dynamic_define_array_name_valid(S_bad_leaf,pconfigcall_S)']
        values += [*error('S_error', 'S', arguments), 'S_error.STORE[n_result] = DEFINED (PINT 99)', *refusals('S'), *budget('S')]
    return values


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
