#!/usr/bin/env python3
"""Reached define() count errors preserve raw arguments before reception."""
import json
import os
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import define_arity_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64

PREFIX = r"""
dec $test_define_arity_front(pstate, nat) : bool
def $test_define_arity_front(S, n_count) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if |pconfigcall.SENT| = n_count
  -- if $dynamic_define_arity_call(pconfigcall)
def $test_define_arity_front(S, n_count) = false -- otherwise
dec $test_define_arity_seek(pstate, nat, nat) : pstate
def $test_define_arity_seek(S, n_count, 0) = S
def $test_define_arity_seek(S, n_count, n) = S
  -- if $(n > 0)
  -- if $test_define_arity_front(S,n_count) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_define_arity_seek(S, n_count, n) = $test_define_arity_seek($drive_steps($test_running(S),1),n_count,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_define_arity_front(S,n_count)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def front(state, start, count):
    call = 'pconfigcall_' + state
    return [state + '_found = $test_define_arity_seek(' + start + ',' + str(count) + ',3000)',
        state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_define_arity_front(' + state + ',' + str(count) + ')',
        state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
        call + '.KIND = INTRINSIC_DEFINE', call + '.OWNER = eps', call + '.PACKS = eps', '~' + call + '.NAMED',
        '$config_invoke_valid(' + state + ',' + call + ')',
        '$dynamic_define_arity_valid(' + state + ',' + call + ')',
        '$dynamic_scalar_define_arguments(' + state + ',' + call + ',0)', *common.public(state)]


def error(after, before, arguments):
    call = 'pconfigcall_' + before
    items = ('[' + ','.join('ENTRY (KINT ' + str(i) + ') (DIRECT (' + value + '))' for i,value in enumerate(arguments)) + ']') if arguments else 'eps'
    message = 'define() expects ' + ('at least 2' if len(arguments) < 2 else 'at most 3') + ' arguments, ' + str(len(arguments)) + ' given'
    return ['$dynamic_define_arity_message(' + call + ') = ' + text(message), *common.step(after, before),
        after + '.TODO = (THROW_SEARCH n_throw_' + after + ') :: ptask_' + before + '*',
        after + '.OBJECTS[n_throw_' + after + '] = THROWABLE pthrowable_' + after,
        'pthrowable_' + after + '.KIND = "ArgumentCountError"', 'pthrowable_' + after + '.ORIGIN = (' + call + '.SITE)',
        '$string_bytes($throwable_field(' + after + ',n_throw_' + after + ',"message")) = (' + text(message) + ')',
        '$throwable_field(' + after + ',n_throw_' + after + ',"previous") = PNULL',
        '$throwable_field(' + after + ',n_throw_' + after + ',"line") = PINT ' + call + '.LINE',
        '$string_bytes($throwable_field(' + after + ',n_throw_' + after + ',"file")) = ($call_sourcefile(' + before + '.FILES,' + call + '.SITE))',
        '$throwable_field(' + after + ',n_throw_' + after + ',"trace") = PARRAY n_trace_' + after,
        after + '.ARRAYS[n_trace_' + after + '].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_api_' + after + '))]',
        '$trace_array_field(' + after + ',n_api_' + after + ',' + text('function') + ') = PSTRING ' + text('define'),
        '$trace_array_field(' + after + ',n_api_' + after + ',' + text('line') + ') = PINT ' + call + '.LINE',
        '$trace_array_field(' + after + ',n_api_' + after + ',' + text('args') + ') = PARRAY n_args_' + after,
        after + '.ARRAYS[n_args_' + after + '].ITEMS = ' + items,
        *[after + '.' + field + ' = ' + before + '.' + field for field in ('STORE','ENV','USERCONSTANTS','STRINGDATA','SELECTEDCALLS','EVENTS','SOURCES','POOLS','FILES','STATICS','ERRORHANDLER','PRECISIONINI')],
        *common.public(after)]


def refusals(state):
    call = 'pconfigcall_' + state
    values = []
    for field in ('.SITE = PORIGIN 0 eps', '.LINE = $(' + call + '.LINE + 1)', '.SELECTION = (|' + state + '.SELECTEDCALLS|)', '.KIND = INTRINSIC_DEFINED'):
        values += ['~$dynamic_define_arity_valid(' + state + ',' + call + '[' + field + '])']
    for field in ('.OWNER = (0)', '.NAMED = true', '.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN PNULL)]', '.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN PNULL)]'):
        values += ['~$dynamic_define_arity_call(' + call + '[' + field + '])']
    values += ['~$dynamic_query_arity_arguments(' + state + ',[NAMED_HOLE])',
        '~$dynamic_query_arity_arguments(' + state + ',[NAMED_SENT (KNOWN (PARRAY 0))])',
        '~$dynamic_query_arity_arguments(' + state + ',[NAMED_SENT (KNOWN (POBJECT 0))])',
        '$dynamic_query_arity_arguments(' + state + ',[NAMED_SENT (KNOWN (PINT 49)),NAMED_SENT (KNOWN (PBOOL false))])',
        '$dynamic_query_arity_arguments(' + state + ',[NAMED_SENT (KNOWN (PFLOAT 4612811918334230528))])']
    return values


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)', state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)', state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')', 'S_initial.COMPLETION = BUDGET']
    if name == 'too-few-define-arguments-preserve-null-and-caller-result':
        values += [*front('S', 'S_initial', 0), 'pconfigcall_S.SENT = eps',
            '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            'S.USERCONSTANTS = eps', '$test_outputs(S.EVENTS) = ' + text('B|'),
            *error('S_error', 'S', []), 'S_error.STORE[n_result] = DEFINED (PINT 99)',
            *front('S_null', 'S_error', 1), 'pconfigcall_S_null.SENT = [NAMED_SENT (KNOWN PNULL)]',
            *error('S_null_error', 'S_null', ['PNULL']), 'S_null_error.STORE[n_result] = DEFINED (PINT 99)',
            'pconfigcall_changed_null = pconfigcall_S_null[.SENT = [NAMED_SENT (KNOWN (PBOOL false))]]',
            '$dynamic_define_arity_call(pconfigcall_changed_null)', '~$dynamic_define_arity_valid(S_null,pconfigcall_changed_null)',
            *refusals('S'), *budget('S'), *budget('S_null')]
    else:
        strict = name == 'strict-four-argument-define-count-before-null-type-rejection'
        assert strict or name == 'selected-four-argument-define-keeps-raw-captures-after-effects'
        arguments = ['PNULL','PINT 1091' if strict else 'pvalue_candidate','PNULL','PINT 1103' if strict else 'pvalue_extra']
        sent = '[' + ','.join('NAMED_SENT (KNOWN (' + value + '))' for value in arguments) + ']'
        values += [*front('S', 'S_initial', 4), 'pconfigcall_S.SENT = ' + sent,
            ('$config_strict(S,pconfigcall_S)' if strict else '~$config_strict(S,pconfigcall_S)'),
            'pconfigcall_S.SELECTION = (n_selection)', 'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
            '$test_outputs(S.EVENTS) = ' + text('B|E|' if strict else 'B|N|E|'),
            '$lookup(S.ENV,' + text('effects') + ') = (n_effects)', 'S.STORE[n_effects] = DEFINED (PINT ' + ('1' if strict else '2') + ')',
            '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            '$lookup(S.ENV,' + text('call') + ') = (n_call)', 'S.STORE[n_call] = DEFINED pvalue_live_call',
            '$string_bytes(pvalue_live_call) = (' + text('constant') + ')',
            '$lookup(S.ENV,' + text('flag') + ') = (n_flag)', 'S.STORE[n_flag] = DEFINED (PBOOL true)',
            'S.USERCONSTANTS = eps', 'S.ERRORHANDLER.CALLBACK = eps']
        if not strict:
            for variable, spelling, slot in (('candidate','captured-value49',1),('extra','captured-extra49',3)):
                values += ['pvalue_' + variable + ' = PSTRING_CARRIER (REQUEST_STRING n_' + variable + ') preqbytes_' + variable,
                    'preqbytes_' + variable + ' = ' + text(spelling), '$string_carrier_valid(S,pvalue_' + variable + ')',
                    'pvalue_bad_' + variable + ' = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) preqbytes_' + variable,
                    'pconfigcall_bad_' + variable + ' = pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,' + str(slot) + ',KNOWN pvalue_bad_' + variable + ')]',
                    '$dynamic_define_arity_call(pconfigcall_bad_' + variable + ')',
                    '~$dynamic_define_arity_valid(S,pconfigcall_bad_' + variable + ')']
        values += [*error('S_error', 'S', arguments), 'S_error.STORE[n_result] = DEFINED (PINT 99)',
            'S_error.STORE[n_effects] = S.STORE[n_effects]', *refusals('S'), *budget('S')]
    return values


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
