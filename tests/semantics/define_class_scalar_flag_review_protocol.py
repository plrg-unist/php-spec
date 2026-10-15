#!/usr/bin/env python3
"""Reached false scalar flags keep their raw API values at class-name errors."""
import json
import os
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import define_class_scalar_flag_review_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64
NEGATIVE_ZERO = 'PFLOAT 9223372036854775808'

PREFIX = r"""
dec $test_false_class_flag_front(pstate, preqbytes) : bool
def $test_false_class_flag_front(S, preqbytes) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if $dynamic_class_define_scalar_call(pconfigcall)
  -- if $named_slot_at(pconfigcall.SENT,0) = NAMED_SENT (KNOWN pvalue_name)
  -- if $string_bytes(pvalue_name) = (preqbytes)
def $test_false_class_flag_front(S, preqbytes) = false -- otherwise
dec $test_false_class_flag_seek(pstate, preqbytes, nat) : pstate
def $test_false_class_flag_seek(S, preqbytes, 0) = S
def $test_false_class_flag_seek(S, preqbytes, n) = S
  -- if $(n > 0)
  -- if $test_false_class_flag_front(S,preqbytes) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_false_class_flag_seek(S, preqbytes, n) = $test_false_class_flag_seek($drive_steps($test_running(S),1),preqbytes,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_false_class_flag_front(S,preqbytes)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def front(state, start, name, candidate, flag):
    call = 'pconfigcall_' + state
    return [state + '_found = $test_false_class_flag_seek(' + start + ',' + text(name) + ',3000)',
        state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_false_class_flag_front(' + state + ',' + text(name) + ')',
        state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
        call + '.SENT = [NAMED_SENT (KNOWN pvalue_name_' + state + '),NAMED_SENT (KNOWN (' + candidate + ')),NAMED_SENT (KNOWN (' + flag + '))]',
        call + '.KIND = INTRINSIC_DEFINE', call + '.OWNER = eps', call + '.PACKS = eps',
        '$string_bytes(pvalue_name_' + state + ') = (' + text(name) + ')',
        '$string_carrier_valid(' + state + ',pvalue_name_' + state + ')',
        '$config_invoke_valid(' + state + ',' + call + ')',
        '$dynamic_class_define_scalar_valid(' + state + ',' + call + ')',
        '~$config_strict(' + state + ',' + call + ')',
        '$dynamic_scalar_define_flag_call(' + call + ')',
        '~$dynamic_scalar_define_flag_valid(' + state + ',' + call + ')',
        '~$dynamic_class_define_call(' + call + ')',
        '~$truth(' + state + ',' + flag + ')',
        state + '.USERCONSTANTS = eps', *common.public(state)]


def error(state, before, candidate, flag):
    call = 'pconfigcall_' + before
    return [*common.step(state, before),
        state + '.TODO = (THROW_SEARCH n_' + state + ') :: ptask_' + state + '*',
        state + '.OBJECTS[n_' + state + '] = THROWABLE pthrowable_' + state,
        'pthrowable_' + state + '.KIND = "ValueError"',
        'pthrowable_' + state + '.ORIGIN = (' + call + '.SITE)',
        '$throwable_field(' + state + ',n_' + state + ',"previous") = PNULL',
        '$throwable_field(' + state + ',n_' + state + ',"line") = PINT ' + call + '.LINE',
        '$string_bytes($throwable_field(' + state + ',n_' + state + ',"file")) = ($call_sourcefile(' + state + '.FILES,' + call + '.SITE))',
        '$string_bytes($throwable_field(' + state + ',n_' + state + ',"message")) = (' + text('define(): Argument #1 ($constant_name) cannot be a class constant') + ')',
        '$throwable_field(' + state + ',n_' + state + ',"trace") = PARRAY n_trace_' + state,
        state + '.ARRAYS[n_trace_' + state + '].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_frame_' + state + ')),ENTRY (KINT 1) (DIRECT (PARRAY n_caller_' + state + '))]',
        '$trace_array_field(' + state + ',n_frame_' + state + ',' + text('function') + ') = PSTRING ' + text('define'),
        '$trace_array_field(' + state + ',n_frame_' + state + ',' + text('line') + ') = PINT ' + call + '.LINE',
        '$trace_array_field(' + state + ',n_frame_' + state + ',' + text('args') + ') = PARRAY n_args_' + state,
        state + '.ARRAYS[n_args_' + state + '].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_name_' + before + '),ENTRY (KINT 1) (DIRECT (' + candidate + ')),ENTRY (KINT 2) (DIRECT (' + flag + '))]',
        '$trace_array_field(' + state + ',n_caller_' + state + ',' + text('function') + ') = PSTRING ' + text('falseClassFlags37'),
        *[state + '.' + field + ' = ' + before + '.' + field for field in (
            'STORE', 'ENV', 'USERCONSTANTS', 'STRINGDATA', 'EVENTS', 'SELECTEDCALLS', 'ERRORHANDLER')],
        *common.public(state)]


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)', state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)', state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def checks(program, path, name):
    assert name == 'negative-zero-and-request-zero-flags-stay-raw'
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET',
        *front('S', 'S_initial', 'Negative::Flag37', 'PINT 317', NEGATIVE_ZERO),
        '$number_bool(NFLOAT 9223372036854775808) = (false,false)',
        'pconfigcall_S.SELECTION = eps', '~pconfigcall_S.NAMED',
        '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
        '$lookup(S.ENV,' + text('warnings') + ') = (n_warnings)', 'S.STORE[n_warnings] = DEFINED (PINT 0)',
        *error('S_error', 'S', 'PINT 317', NEGATIVE_ZERO),
        'S_error.STORE[n_result] = DEFINED (PINT 99)',
        *front('S_second', 'S_error', 'Zero::Flag37', 'pvalue_candidate', 'pvalue_flag'),
        'pvalue_name_S_second = PSTRING_CARRIER (REQUEST_STRING n_name) preqbytes_name',
        'preqbytes_name = ' + text('Zero::Flag37'),
        'pvalue_candidate = PSTRING_CARRIER (REQUEST_STRING n_candidate) preqbytes_candidate',
        'preqbytes_candidate = ' + text('request-value'), '$string_carrier_valid(S_second,pvalue_candidate)',
        'pvalue_flag = PSTRING_CARRIER (REQUEST_STRING n_flag) preqbytes_flag',
        'preqbytes_flag = ' + text('0'), '$string_carrier_valid(S_second,pvalue_flag)',
        'S_second.STRINGDATA[n_flag] = preqbytes_flag',
        'pconfigcall_S_second.SELECTION = (n_selection)', '$(n_selection < |S_second.SELECTEDCALLS|)',
        'S_second.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE', 'pconfigcall_S_second.NAMED',
        '$lookup(S_second.ENV,' + text('flag') + ') = (n_flag_cell)', 'S_second.STORE[n_flag_cell] = DEFINED pvalue_flag',
        '$lookup(S_second.ENV,' + text('result') + ') = (n_result)', 'S_second.STORE[n_result] = DEFINED (PINT 101)',
        'S_second.STORE[n_warnings] = DEFINED (PINT 0)',
        *error('S_second_error', 'S_second', 'pvalue_candidate', 'pvalue_flag'),
        'S_second_error.STORE[n_result] = DEFINED (PINT 101)',
        '~$dynamic_class_define_scalar_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,1,KNOWN (PINT 318))])',
        'n_bad_string = |S_second.STRINGDATA|',
    ]
    for slot, label, value in ((0, 'name', 'Zero::Flag37'), (1, 'candidate', 'request-value'), (2, 'flag', '0')):
        values += ['pvalue_bad_' + label + ' = PSTRING_CARRIER (REQUEST_STRING n_bad_string) ' + text(value),
            '~$string_carrier_valid(S_second,pvalue_bad_' + label + ')',
            '~$dynamic_class_define_scalar_valid(S_second,pconfigcall_S_second[.SENT = $named_slot_set(pconfigcall_S_second.SENT,' + str(slot) + ',KNOWN pvalue_bad_' + label + ')])']
    for field in ('.SITE = PORIGIN 0 eps', '.LINE = $(pconfigcall_S_second.LINE + 1)', '.SELECTION = eps',
            '.OWNER = (0)', '.KIND = INTRINSIC_CONSTANT'):
        values += ['~$dynamic_class_define_scalar_valid(S_second,pconfigcall_S_second[' + field + '])']
    for value in ('PSTRING ' + text('Ordinary37'), 'PSTRING (' + text('Bad::37') + ' ++ [0])', 'PINT 3', 'PNULL'):
        values += ['~$dynamic_class_define_scalar_call(pconfigcall_S_second[.SENT = $named_slot_set(pconfigcall_S_second.SENT,0,KNOWN (' + value + '))])']
    for value in ('PNULL', 'PBOOL false', 'PBOOL true', 'PFLOAT 9221120237041090560', 'PARRAY 0', 'POBJECT 0'):
        values += ['~$dynamic_class_define_scalar_call(pconfigcall_S_second[.SENT = $named_slot_set(pconfigcall_S_second.SENT,2,KNOWN (' + value + '))])']
    values += [*budget('S'), *budget('S_second')]
    return values


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
