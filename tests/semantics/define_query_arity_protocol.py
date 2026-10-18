#!/usr/bin/env python3
"""Reached query count errors preserve arguments before all parameter reception."""
import json
import os
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import define_query_arity_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64

PREFIX = r"""
dec $test_query_arity_front(pstate, pintrinsic, nat) : bool
def $test_query_arity_front(S, pintrinsic, n_count) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = pintrinsic
  -- if |pconfigcall.SENT| = n_count
  -- if $dynamic_query_arity_call(pconfigcall)
def $test_query_arity_front(S, pintrinsic, n_count) = false -- otherwise
dec $test_query_arity_seek(pstate, pintrinsic, nat, nat) : pstate
def $test_query_arity_seek(S, pintrinsic, n_count, 0) = S
def $test_query_arity_seek(S, pintrinsic, n_count, n) = S
  -- if $(n > 0)
  -- if $test_query_arity_front(S,pintrinsic,n_count) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_query_arity_seek(S, pintrinsic, n_count, n) = $test_query_arity_seek($drive_steps($test_running(S),1),pintrinsic,n_count,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_query_arity_front(S,pintrinsic,n_count)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def front(state, start, kind, count):
    call = 'pconfigcall_' + state
    return [state + '_found = $test_query_arity_seek(' + start + ',' + kind + ',' + str(count) + ',3000)',
        state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_query_arity_front(' + state + ',' + kind + ',' + str(count) + ')',
        state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
        call + '.KIND = ' + kind, call + '.OWNER = eps', call + '.PACKS = eps', '~' + call + '.NAMED',
        '$config_invoke_valid(' + state + ',' + call + ')',
        '$dynamic_query_arity_valid(' + state + ',' + call + ')',
        '$dynamic_scalar_define_arguments(' + state + ',' + call + ',0)', *common.public(state)]


def error(after, before, api, arguments):
    call = 'pconfigcall_' + before
    items = ('[' + ','.join('ENTRY (KINT ' + str(i) + ') (DIRECT (' + value + '))' for i,value in enumerate(arguments)) + ']') if arguments else 'eps'
    return [*common.step(after, before),
        after + '.TODO = (THROW_SEARCH n_throw_' + after + ') :: ptask_' + before + '*',
        after + '.OBJECTS[n_throw_' + after + '] = THROWABLE pthrowable_' + after,
        'pthrowable_' + after + '.KIND = "ArgumentCountError"', 'pthrowable_' + after + '.ORIGIN = (' + call + '.SITE)',
        '$string_bytes($throwable_field(' + after + ',n_throw_' + after + ',"message")) = (' + text(api+'() expects exactly 1 argument, '+str(len(arguments))+' given') + ')',
        '$throwable_field(' + after + ',n_throw_' + after + ',"previous") = PNULL',
        '$throwable_field(' + after + ',n_throw_' + after + ',"line") = PINT ' + call + '.LINE',
        '$string_bytes($throwable_field(' + after + ',n_throw_' + after + ',"file")) = ($call_sourcefile(' + before + '.FILES,' + call + '.SITE))',
        '$throwable_field(' + after + ',n_throw_' + after + ',"trace") = PARRAY n_trace_' + after,
        after + '.ARRAYS[n_trace_' + after + '].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_api_' + after + '))]',
        '$trace_array_field(' + after + ',n_api_' + after + ',' + text('function') + ') = PSTRING ' + text(api),
        '$trace_array_field(' + after + ',n_api_' + after + ',' + text('line') + ') = PINT ' + call + '.LINE',
        '$trace_array_field(' + after + ',n_api_' + after + ',' + text('args') + ') = PARRAY n_args_' + after,
        after + '.ARRAYS[n_args_' + after + '].ITEMS = ' + items,
        *[after + '.' + field + ' = ' + before + '.' + field for field in ('STORE','ENV','USERCONSTANTS','STRINGDATA','SELECTEDCALLS','EVENTS','SOURCES','POOLS','FILES','STATICS','ERRORHANDLER','PRECISIONINI')],
        *common.public(after)]


def refusals(state):
    call = 'pconfigcall_' + state
    values = []
    for field in ('.SITE = PORIGIN 0 eps', '.LINE = $(' + call + '.LINE + 1)', '.SELECTION = (|' + state + '.SELECTEDCALLS|)', '.KIND = INTRINSIC_DEFINE'):
        values += ['~$dynamic_query_arity_valid(' + state + ',' + call + '[' + field + '])']
    for field in ('.OWNER = (0)', '.NAMED = true', '.SENT = [NAMED_SENT (KNOWN PNULL)]', '.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN PNULL)]'):
        values += ['~$dynamic_query_arity_call(' + call + '[' + field + '])']
    values += ['~$dynamic_query_arity_arguments(' + state + ',[NAMED_SENT (KNOWN (PARRAY 0))])',
        '~$dynamic_query_arity_arguments(' + state + ',[NAMED_SENT (KNOWN (POBJECT 0))])',
        '$dynamic_query_arity_arguments(' + state + ',[NAMED_SENT (KNOWN (PINT 48)),NAMED_SENT (KNOWN (PBOOL false))])',
        '$dynamic_query_arity_arguments(' + state + ',[NAMED_SENT (KNOWN (PFLOAT 4612811918334230528))])']
    return values


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)', state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)', state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')', 'S_initial.COMPLETION = BUDGET']
    if name == 'zero-argument-query-errors-retain-caller-result':
        values += [*front('S', 'S_initial', 'INTRINSIC_DEFINED', 0), 'pconfigcall_S.SENT = eps',
            '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            *error('S_error', 'S', 'defined', []), 'S_error.STORE[n_result] = DEFINED (PINT 99)',
            *front('S_constant', 'S_error', 'INTRINSIC_CONSTANT', 0), 'pconfigcall_S_constant.SENT = eps',
            *error('S_constant_error', 'S_constant', 'constant', []), 'S_constant_error.STORE[n_result] = DEFINED (PINT 99)',
            *refusals('S'), *budget('S'), *budget('S_constant')]
    else:
        strict = name == 'strict-defined-count-before-null-type-error-after-extra-effect'
        assert strict or name == 'selected-constant-extra-arguments-run-before-null-reception'
        kind,api = ('INTRINSIC_DEFINED','defined') if strict else ('INTRINSIC_CONSTANT','constant')
        extra = 'PINT 1073' if strict else 'pvalue_extra'
        values += [*front('S', 'S_initial', kind, 2),
            'pconfigcall_S.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (' + extra + '))]',
            ('$config_strict(S,pconfigcall_S)' if strict else '~$config_strict(S,pconfigcall_S)'),
            'pconfigcall_S.SELECTION = (n_selection)', 'S.SELECTEDCALLS[n_selection].KIND = ' + kind,
            '$test_outputs(S.EVENTS) = ' + text('B|E|' if strict else 'B|A|E|'),
            '$lookup(S.ENV,' + text('effects') + ') = (n_effects)', 'S.STORE[n_effects] = DEFINED (PINT 1)',
            '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            '$lookup(S.ENV,' + text('call') + ') = (n_call)', 'S.STORE[n_call] = DEFINED pvalue_live_call',
            '$string_bytes(pvalue_live_call) = (' + text('constant' if strict else 'define') + ')']
        if not strict:
            values += ['pvalue_extra = PSTRING_CARRIER (REQUEST_STRING n_extra) preqbytes_extra',
                'preqbytes_extra = ' + text('captured-extra48'), '$string_carrier_valid(S,pvalue_extra)',
                'pvalue_bad_extra = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) preqbytes_extra',
                '~$dynamic_query_arity_arguments(S,[NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN pvalue_bad_extra)])',
                '~$dynamic_query_arity_valid(S,pconfigcall_S[.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN pvalue_bad_extra)]])']
        values += [*error('S_error', 'S', api, ['PNULL',extra]), 'S_error.STORE[n_result] = DEFINED (PINT 99)',
            'S_error.STORE[n_effects] = DEFINED (PINT 1)', *refusals('S'), *budget('S')]
        if strict:
            values += ['pconfigcall_changed_null = pconfigcall_S[.SENT = [NAMED_SENT (KNOWN (PBOOL false)),NAMED_SENT (KNOWN (PINT 1073))]]',
                '$dynamic_query_arity_call(pconfigcall_changed_null)', '~$dynamic_query_arity_valid(S,pconfigcall_changed_null)']
    return values


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
