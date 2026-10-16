#!/usr/bin/env python3
"""Reached int/bool names retain false raw flags through publication and errors."""
import json
import os
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import define_scalar_false_flag_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64

PREFIX = r"""
dec $test_false_scalar_front(pstate, pvalue) : bool
def $test_false_scalar_front(S, pvalue_name) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if $dynamic_scalar_define_call(pconfigcall)
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_name),NAMED_SENT (KNOWN pvalue),NAMED_SENT (KNOWN pvalue_flag)]
  -- if $dynamic_define_false_scalar_flag(pvalue_flag)
def $test_false_scalar_front(S, pvalue_name) = false -- otherwise
dec $test_false_scalar_seek(pstate, pvalue, nat) : pstate
def $test_false_scalar_seek(S, pvalue_name, 0) = S
def $test_false_scalar_seek(S, pvalue_name, n) = S
  -- if $(n > 0)
  -- if $test_false_scalar_front(S,pvalue_name) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_false_scalar_seek(S, pvalue_name, n) = $test_false_scalar_seek($drive_steps($test_running(S),1),pvalue_name,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_false_scalar_front(S,pvalue_name)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def front(state, start, name, value):
    call = 'pconfigcall_' + state
    return [state + '_found = $test_false_scalar_seek(' + start + ',' + name + ',3000)',
        state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]', '$test_false_scalar_front(' + state + ',' + name + ')',
        state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
        call + '.SENT = [NAMED_SENT (KNOWN (' + name + ')),NAMED_SENT (KNOWN (' + value + ')),NAMED_SENT (KNOWN pvalue_flag_' + state + ')]',
        call + '.KIND = INTRINSIC_DEFINE', call + '.OWNER = eps', call + '.PACKS = eps',
        '$config_invoke_valid(' + state + ',' + call + ')', '$dynamic_scalar_define_valid(' + state + ',' + call + ')',
        '$dynamic_scalar_define_flag_carrier_valid(' + state + ',' + call + ')', *common.public(state)]


def unchanged(after, before, fields):
    return [after + '.' + field + ' = ' + before + '.' + field for field in fields.split()]


def converted(before, name, key):
    call = 'pconfigcall_' + before
    return ['~$config_strict(' + before + ',' + call + ')',
        '$config_conversion(' + before + ',' + call + ',' + name + ') = TYPESTRING (' + name + ')',
        before + '_converted = $typed_apply(' + before + ',TYPESTRING (' + name + '),' + call + '.LINE)',
        before + '_converted.COMPLETION = NORMAL', before + '_converted.RESULT = KNOWN pvalue_received_' + before,
        '$string_bytes(pvalue_received_' + before + ') = (' + text(key) + ')',
        '$string_carrier_valid(' + before + '_converted,pvalue_received_' + before + ')']


def publish(after, before, name, value, key):
    call = 'pconfigcall_' + before
    return [*converted(before, name, key), *common.step(after, before, 'PBOOL true'),
        after + '.TODO = ptask_' + before + '*', after + '.BASE = BASE_VALUE (KNOWN PNULL)',
        '$dynamic_constant_class(' + value + ') = (pvalueclass_' + before + ')',
        after + '.USERCONSTANTS = ' + before + '.USERCONSTANTS ++ [{NAME ' + text(key) + ',ORIGIN ' + call + '.SITE,VALUE ' + value + ',CLASS pvalueclass_' + before + ',READS eps,RECEIVES eps}]',
        after + '.STRINGDATA = ' + before + '_converted.STRINGDATA',
        *unchanged(after, before, 'STORE ENV ARRAYS OBJECTS SELECTEDCALLS SOURCES POOLS FILES STATICS')]


def strict_error(after, before, name, value, given):
    call = 'pconfigcall_' + before
    return ['$config_strict(' + before + ',' + call + ')', *common.step(after, before),
        after + '.TODO = (THROW_SEARCH n_error_' + after + ') :: ptask_' + before + '*',
        after + '.OBJECTS[n_error_' + after + '] = THROWABLE pthrowable_' + after,
        'pthrowable_' + after + '.KIND = "TypeError"', 'pthrowable_' + after + '.ORIGIN = (' + call + '.SITE)',
        '$string_bytes($throwable_field(' + after + ',n_error_' + after + ',"message")) = (' + text('define(): Argument #1 ($constant_name) must be of type string, ' + given + ' given') + ')',
        '$throwable_field(' + after + ',n_error_' + after + ',"previous") = PNULL',
        '$throwable_field(' + after + ',n_error_' + after + ',"line") = PINT ' + call + '.LINE',
        '$string_bytes($throwable_field(' + after + ',n_error_' + after + ',"file")) = ($call_sourcefile(' + before + '.FILES,' + call + '.SITE))',
        '$throwable_field(' + after + ',n_error_' + after + ',"trace") = PARRAY n_trace_' + after,
        after + '.ARRAYS[n_trace_' + after + '].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_frame_' + after + '))]',
        '$trace_array_field(' + after + ',n_frame_' + after + ',' + text('function') + ') = PSTRING ' + text('define'),
        '$trace_array_field(' + after + ',n_frame_' + after + ',' + text('args') + ') = PARRAY n_args_' + after,
        after + '.ARRAYS[n_args_' + after + '].ITEMS = [ENTRY (KINT 0) (DIRECT (' + name + ')),ENTRY (KINT 1) (DIRECT (' + value + ')),ENTRY (KINT 2) (DIRECT pvalue_flag_' + before + ')]',
        *unchanged(after, before, 'STORE ENV USERCONSTANTS STRINGDATA SELECTEDCALLS EVENTS SOURCES POOLS FILES STATICS ERRORHANDLER'), *common.public(after)]


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)', state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)', state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')', 'S_initial.COMPLETION = BUDGET']
    if name == 'fresh-scalar-names-false-flags-and-default-duplicate':
        values += [*front('S', 'S_initial', 'PINT 37', 'PINT 401'), 'pvalue_flag_S = PINT 0', 'S.USERCONSTANTS = eps',
            *publish('S_first', 'S', 'PINT 37', 'PINT 401', '37'),
            *front('S_false', 'S_first', 'PBOOL false', 'PINT 402'), '$string_bytes(pvalue_flag_S_false) = (' + text('0') + ')',
            *publish('S_empty', 'S_false', 'PBOOL false', 'PINT 402', ''),
            *front('S_true', 'S_empty', 'PBOOL true', 'PINT 403'), 'pvalue_flag_S_true = PFLOAT 9223372036854775808',
            *publish('S_true_published', 'S_true', 'PBOOL true', 'PINT 403', '1'),
            *front('S_two', 'S_true_published', 'PINT 2', 'PINT 404'), '$string_bytes(pvalue_flag_S_two) = (eps)',
            *publish('S_four', 'S_two', 'PINT 2', 'PINT 404', '2'),
            *front('S_duplicate', 'S_four', 'PINT 37', 'PINT 405'), 'pvalue_flag_S_duplicate = PINT 0',
            '$(|S_duplicate.USERCONSTANTS| = 4)', '~$error_handler_eligible(S_duplicate,2)',
            *converted('S_duplicate', 'PINT 37', '37'),
            'z_precision = $precision_value(S_duplicate)', *common.step('S_warning', 'S_duplicate'),
            'S_warning.TODO = (DYNAMIC_SCALAR_DEFINE_DUPLICATE pconfigcall_S_duplicate pvalue_received_S_duplicate z_precision 4) :: ptask_S_duplicate*',
            '$call_task_valid(S_warning,DYNAMIC_SCALAR_DEFINE_DUPLICATE pconfigcall_S_duplicate pvalue_received_S_duplicate z_precision 4)',
            'S_warning.EVENTS = S_duplicate.EVENTS ++ [DIAGNOSTIC "Warning" $global_constant_duplicate_message(' + text('37') + ') pconfigcall_S_duplicate.LINE]',
            'S_warning.STRINGDATA = S_duplicate_converted.STRINGDATA',
            *unchanged('S_warning', 'S_duplicate', 'STORE ENV USERCONSTANTS ARRAYS OBJECTS SELECTEDCALLS'), *common.public('S_warning'),
            *common.step('S_return', 'S_warning', 'PBOOL false'), 'S_return.TODO = ptask_S_duplicate*',
            'S_return.USERCONSTANTS = S_warning.USERCONSTANTS',
            '~$dynamic_scalar_define_duplicate_valid(S_warning,pconfigcall_S_duplicate,pvalue_received_S_duplicate,z_precision,0)',
            '~$dynamic_scalar_define_duplicate_valid(S_warning,pconfigcall_S_duplicate,pvalue_received_S_duplicate,z_precision,5)',
            'pconfigcall_bad_flag = pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,2,KNOWN (PSTRING ' + text('0') + '))]',
            '$dynamic_scalar_define_call(pconfigcall_bad_flag)', '~$dynamic_scalar_define_valid(S,pconfigcall_bad_flag)',
            *budget('S'), *budget('S_warning')]
        for flag in ('PBOOL true', 'PNULL', 'PINT 1', 'PFLOAT 9221120237041090560', 'PSTRING ' + text('false'), 'PARRAY 0', 'POBJECT 0'):
            values += ['~$dynamic_define_false_scalar_flag(' + flag + ')', '~$dynamic_scalar_define_call(pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,2,KNOWN (' + flag + '))])']
        values += ['$dynamic_scalar_define_call(pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,2,KNOWN (PBOOL false))])',
            '$dynamic_scalar_define_call(pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,0,KNOWN (PFLOAT 4612811918334230528))])',
            '~$dynamic_scalar_define_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,0,KNOWN (PFLOAT 4612811918334230528))])']
    elif name == 'captured-request-zero-before-live-truthy-flag-effects':
        values += [*front('S', 'S_initial', 'PINT 42', 'pvalue_candidate'), 'S.USERCONSTANTS = eps',
            'pvalue_flag_S = PSTRING_CARRIER (REQUEST_STRING n_flag_string) preqbytes_flag', 'preqbytes_flag = ' + text('0'),
            '$string_carrier_valid(S,pvalue_flag_S)', '~$truth(S,pvalue_flag_S)',
            'pvalue_candidate = PSTRING_CARRIER (REQUEST_STRING n_candidate) preqbytes_candidate', 'preqbytes_candidate = ' + text('captured-value40'),
            '$string_carrier_valid(S,pvalue_candidate)', '$test_outputs(S.EVENTS) = ' + text('B|V|N|'),
            'pconfigcall_S.SELECTION = (n_selection)', 'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
            '$lookup(S.ENV,' + text('flag') + ') = (n_flag)', 'S.STORE[n_flag] = DEFINED pvalue_live_flag', '$string_bytes(pvalue_live_flag) = (' + text('false') + ')',
            '$truth(S,pvalue_live_flag)', '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            *publish('S_published', 'S', 'PINT 42', 'pvalue_candidate', '42'), 'S_published.STORE[n_result] = DEFINED (PINT 99)',
            'n_bad_string = |S.STRINGDATA|', 'pvalue_bad_flag = PSTRING_CARRIER (REQUEST_STRING n_bad_string) preqbytes_flag',
            '$dynamic_define_false_scalar_flag(pvalue_bad_flag)', '~$string_carrier_valid(S,pvalue_bad_flag)',
            '~$dynamic_scalar_define_flag_carrier_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,2,KNOWN pvalue_bad_flag)])',
            '~$dynamic_scalar_define_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,2,KNOWN pvalue_bad_flag)])', *budget('S')]
        for field in ('.SITE = PORIGIN 0 eps', '.LINE = $(pconfigcall_S.LINE + 1)', '.SELECTION = eps', '.KIND = INTRINSIC_CONSTANT'):
            values += ['~$dynamic_scalar_define_valid(S,pconfigcall_S[' + field + '])']
    else:
        assert name == 'strict-name-error-precedes-nonbool-flag-after-effects'
        values += [*front('S', 'S_initial', 'PINT 47', 'PINT 447'), 'pvalue_flag_S = PINT 0', 'S.USERCONSTANTS = eps',
            '$test_outputs(S.EVENTS) = ' + text('B|V|N|'), 'pconfigcall_S.SELECTION = (n_selection)',
            '$lookup(S.ENV,' + text('flag') + ') = (n_flag)', 'S.STORE[n_flag] = DEFINED (PBOOL true)',
            '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            *strict_error('S_error', 'S', 'PINT 47', 'PINT 447', 'int'),
            *front('S_false', 'S_error', 'PBOOL false', 'PINT 449'), '$string_bytes(pvalue_flag_S_false) = (' + text('0') + ')',
            *strict_error('S_false_error', 'S_false', 'PBOOL false', 'PINT 449', 'false'),
            'S_false_error.STORE[n_result] = DEFINED (PINT 99)', *budget('S')]
    return values


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
