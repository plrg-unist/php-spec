#!/usr/bin/env python3
"""Genuine NaN reception fronts order conversion Warning and raw body errors."""
import json
import os
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import define_class_nan_flag_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64

PREFIX = r"""
dec $test_class_nan_front(pstate, nat, preqbytes) : bool
def $test_class_nan_front(S, 0, preqbytes) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if $dynamic_class_define_nan_call(pconfigcall)
  -- if $named_slot_at(pconfigcall.SENT,0) = NAMED_SENT (KNOWN pvalue_name)
  -- if $string_bytes(pvalue_name) = (preqbytes)
def $test_class_nan_front(S, 1, preqbytes) = true
  -- if S.TODO = (DYNAMIC_CLASS_DEFINE_NAN_RESULT pconfigcall) :: ptask_tail*
  -- if $named_slot_at(pconfigcall.SENT,0) = NAMED_SENT (KNOWN pvalue_name)
  -- if $string_bytes(pvalue_name) = (preqbytes)
def $test_class_nan_front(S, 2, preqbytes) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_call(S,pcallcontext) = (perrorcall)
  -- if perrorcall.RESUME = DYNAMIC_CLASS_DEFINE_NAN_RESULT pconfigcall
  -- if $named_slot_at(pconfigcall.SENT,0) = NAMED_SENT (KNOWN pvalue_name)
  -- if $string_bytes(pvalue_name) = (preqbytes)
def $test_class_nan_front(S, n_stage, preqbytes) = false -- otherwise
dec $test_class_nan_seek(pstate, nat, preqbytes, nat) : pstate
def $test_class_nan_seek(S, n_stage, preqbytes, 0) = S
def $test_class_nan_seek(S, n_stage, preqbytes, n) = S
  -- if $(n > 0)
  -- if $test_class_nan_front(S,n_stage,preqbytes) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_class_nan_seek(S, n_stage, preqbytes, n) = $test_class_nan_seek($drive_steps($test_running(S),1),n_stage,preqbytes,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_class_nan_front(S,n_stage,preqbytes)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def reach(state, start, stage, name):
    return [state + '_found = $test_class_nan_seek(' + start + ',' + str(stage) + ',' + text(name) + ',3000)',
        state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]', '$test_class_nan_front(' + state + ',' + str(stage) + ',' + text(name) + ')', *common.public(state)]


def front(state, start, name, value):
    call = 'pconfigcall_' + state
    return [*reach(state, start, 0, name), state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
        call + '.SENT = [NAMED_SENT (KNOWN pvalue_name_' + state + '),NAMED_SENT (KNOWN (' + value + ')),NAMED_SENT (KNOWN (PFLOAT 9221120237041090560))]',
        call + '.KIND = INTRINSIC_DEFINE', call + '.OWNER = eps', call + '.PACKS = eps',
        '$config_invoke_valid(' + state + ',' + call + ')', '$dynamic_class_define_nan_valid(' + state + ',' + call + ')',
        '$dynamic_nan_define_flag_call(' + call + ')', '~$dynamic_nan_define_flag_valid(' + state + ',' + call + ')',
        '~$call_task_valid(' + state + ',DYNAMIC_NAN_DEFINE_FLAG_RESULT ' + call + ')', state + '.USERCONSTANTS = eps']


def unchanged(after, before, fields):
    return [after + '.' + field + ' = ' + before + '.' + field for field in fields.split()]


def error(after, before, call, raw_name, value, strict=False, caller=None):
    message = 'define(): Argument #3 ($case_insensitive) must be of type bool, float given' if strict else 'define(): Argument #1 ($constant_name) cannot be a class constant'
    frames = ['ENTRY (KINT 0) (DIRECT (PARRAY n_frame_' + after + '))']
    if caller:
        frames += ['ENTRY (KINT 1) (DIRECT (PARRAY n_caller_' + after + '))']
    values = [before + '.TODO = ptask :: ptask_' + before + '*', *common.step(after, before),
        after + '.TODO = (THROW_SEARCH n_error_' + after + ') :: ptask_' + before + '*',
        after + '.OBJECTS[n_error_' + after + '] = THROWABLE pthrowable_' + after,
        'pthrowable_' + after + '.KIND = ' + json.dumps('TypeError' if strict else 'ValueError'),
        'pthrowable_' + after + '.ORIGIN = (' + call + '.SITE)', '$throwable_live(' + after + ',n_error_' + after + ')',
        '$string_bytes($throwable_field(' + after + ',n_error_' + after + ',"message")) = (' + text(message) + ')',
        '$throwable_field(' + after + ',n_error_' + after + ',"line") = PINT ' + call + '.LINE',
        '$string_bytes($throwable_field(' + after + ',n_error_' + after + ',"file")) = ($call_sourcefile(' + before + '.FILES,' + call + '.SITE))',
        '$throwable_field(' + after + ',n_error_' + after + ',"previous") = PNULL',
        '$throwable_field(' + after + ',n_error_' + after + ',"trace") = PARRAY n_trace_' + after,
        after + '.ARRAYS[n_trace_' + after + '].ITEMS = [' + ','.join(frames) + ']',
        '$trace_array_field(' + after + ',n_frame_' + after + ',' + text('function') + ') = PSTRING ' + text('define'),
        '$trace_array_field(' + after + ',n_frame_' + after + ',' + text('line') + ') = PINT ' + call + '.LINE',
        '$trace_array_field(' + after + ',n_frame_' + after + ',' + text('args') + ') = PARRAY n_args_' + after,
        after + '.ARRAYS[n_args_' + after + '].ITEMS = [ENTRY (KINT 0) (DIRECT ' + raw_name + '),ENTRY (KINT 1) (DIRECT (' + value + ')),ENTRY (KINT 2) (DIRECT (PFLOAT 9221120237041090560))]',
        *unchanged(after, before, 'STORE ENV USERCONSTANTS STRINGDATA SELECTEDCALLS EVENTS SOURCES POOLS FILES STATICS ERRORHANDLER ERRORHANDLERS'), *common.public(after)]
    if caller:
        values += ['$trace_array_field(' + after + ',n_caller_' + after + ',' + text('function') + ') = PSTRING ' + text(caller)]
    return values


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)', state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)', state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')', 'S_initial.COMPLETION = BUDGET']
    if name == 'literal-nan-flag-conversion-warning-before-class-name-error':
        values += [*front('S', 'S_initial', 'Literal::Nan39', 'PINT 433'), '~$config_strict(S,pconfigcall_S)',
            '~$error_handler_eligible(S,2)', 'pconfigcall_S.LINE = 4',
            *common.step('S_default', 'S'), 'S_default.TODO = (DYNAMIC_CLASS_DEFINE_NAN_RESULT pconfigcall_S) :: ptask_S*',
            '$call_task_valid(S_default,DYNAMIC_CLASS_DEFINE_NAN_RESULT pconfigcall_S)',
            'S_default.EVENTS = S.EVENTS ++ [DIAGNOSTIC "Warning" $dynamic_nan_define_flag_message() pconfigcall_S.LINE]',
            *unchanged('S_default', 'S', 'STORE ENV USERCONSTANTS STRINGDATA ARRAYS OBJECTS SELECTEDCALLS'), *common.public('S_default'),
            *error('S_error', 'S_default', 'pconfigcall_S', 'pvalue_name_S', 'PINT 433'),
            'pconfigcall_bad_name = pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,0,KNOWN (PSTRING ' + text('Other::Nan39') + '))]',
            '$config_invoke_valid(S,pconfigcall_bad_name)', '$dynamic_class_define_nan_call(pconfigcall_bad_name)',
            '~$dynamic_class_define_nan_valid(S,pconfigcall_bad_name)',
            'S_bad = $drive_steps(S[.TODO = (CONFIG_INVOKE pconfigcall_bad_name) :: ptask_S*],1)',
            'S_bad.COMPLETION = UNSUPPORTED "class-qualified NaN define flag capture"',
            'pconfigcall_bad_nan = pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,2,KNOWN (PFLOAT 18444492273895866368))]',
            '$dynamic_class_define_nan_call(pconfigcall_bad_nan)', '~$dynamic_class_define_nan_valid(S,pconfigcall_bad_nan)',
            *budget('S'), *budget('S_default')]
        for flag in ('PNULL', 'PBOOL false', 'PINT 0', 'PFLOAT 4607182418800017408'):
            values += ['~$dynamic_class_define_nan_call(pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,2,KNOWN (' + flag + '))])']
        for raw in ('PSTRING ' + text('Ordinary39'), 'PSTRING (' + text('::') + ' ++ [0])'):
            values += ['~$dynamic_class_define_nan_call(pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,0,KNOWN (' + raw + '))])']
    else:
        strict = name == 'strict-nan-flag-before-conversion-warning-and-class-name-error'
        assert strict or name == 'captured-nan-flag-handler-return-then-class-name-error'
        actual_name,value = ('Strict::Nan39','PINT 447') if strict else ('Captured::Nan39','pvalue_candidate')
        values += [*front('S', 'S_initial', actual_name, value),
            ('$config_strict' if strict else '~$config_strict') + '(S,pconfigcall_S)', '$test_outputs(S.EVENTS) = ' + text('B|V|N|'),
            'pconfigcall_S.SELECTION = (n_selection)', 'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
            '$lookup(S.ENV,' + text('flag') + ') = (n_flag)', 'S.STORE[n_flag] = DEFINED (PBOOL ' + ('true' if strict else 'false') + ')',
            '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)']
        if strict:
            values += ['~$call_task_valid(S,DYNAMIC_CLASS_DEFINE_NAN_RESULT pconfigcall_S)',
                *error('S_error', 'S', 'pconfigcall_S', 'pvalue_name_S', value, strict=True)]
        else:
            values += ['pvalue_candidate = PSTRING_CARRIER (REQUEST_STRING n_candidate) preqbytes_candidate',
                'preqbytes_candidate = ' + text('captured-value39'), '$string_carrier_valid(S,pvalue_candidate)',
                *common.step('S_warning', 'S'), 'S_warning.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_S*',
                'perrorcall.RESUME = DYNAMIC_CLASS_DEFINE_NAN_RESULT pconfigcall_S',
                'perrorcall.SITE = pconfigcall_S.SITE', 'perrorcall.LEVEL = 2', 'perrorcall.LINE = pconfigcall_S.LINE',
                'perrorcall.MESSAGE = $dynamic_nan_define_flag_message()',
                'perrorcall.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE pconfigcall_S.LINE', '$error_call_valid(S_warning,perrorcall)',
                *unchanged('S_warning', 'S', 'STORE ENV USERCONSTANTS STRINGDATA ARRAYS OBJECTS SELECTEDCALLS EVENTS'), *common.public('S_warning'),
                *reach('S_handler', 'S_warning', 2, actual_name), 'S_handler.CURRENT = (pcallcontext)',
                '$error_context_call(S_handler,pcallcontext) = (perrorcall_handler)',
                '$error_context_valid(S_handler,pcallcontext)', '$error_context_trigger(S_handler,pcallcontext) = (pconfigcall_S)',
                '$error_handler_trace_values(S_handler,pcallcontext,pconfigcall_S) = [pvalue_name_S,pvalue_candidate,(PFLOAT 9221120237041090560)]',
                *reach('S_resume', 'S_handler', 1, actual_name),
                'S_resume.TODO = (DYNAMIC_CLASS_DEFINE_NAN_RESULT pconfigcall_S) :: ptask_resume*',
                '$call_task_valid(S_resume,DYNAMIC_CLASS_DEFINE_NAN_RESULT pconfigcall_S)',
                '$(|S_resume.EVENTS| > 0)',
                'S_resume.EVENTS[$nabs($(|S_resume.EVENTS| - 1))] = DIAGNOSTIC "Warning" $dynamic_nan_define_flag_message() pconfigcall_S.LINE',
                '$(|S_resume.USERCONSTANTS| = 1)', '$user_constant_at(S_resume.USERCONSTANTS,' + text('ClassNanInner39') + ') = (puserconstant_inner)',
                'puserconstant_inner.VALUE = PINT 458', 'S_resume.STORE[n_flag] = DEFINED (PBOOL true)',
                '$lookup(S_resume.ENV,' + text('name') + ') = (n_name)', 'S_resume.STORE[n_name] = DEFINED pvalue_live_name',
                '$string_bytes(pvalue_live_name) = (' + text('LivePlain39') + ')',
                '$lookup(S_resume.ENV,' + text('value') + ') = (n_value)', 'S_resume.STORE[n_value] = DEFINED (PINT 938)',
                '$lookup(S_resume.ENV,' + text('call') + ') = (n_call)', 'S_resume.STORE[n_call] = DEFINED pvalue_live_call',
                '$string_bytes(pvalue_live_call) = (' + text('constant') + ')',
                '$lookup(S_resume.ENV,' + text('warnings') + ') = (n_warnings)', 'S_resume.STORE[n_warnings] = DEFINED (PINT 1)',
                *error('S_error', 'S_resume', 'pconfigcall_S', 'pvalue_name_S', value, caller='classNanCaller39'),
                'S_error.STORE[n_result] = DEFINED (PINT 99)', *budget('S_warning'), *budget('S_resume')]
            for field in ('.LEVEL = 8192', '.LINE = $(perrorcall.LINE + 1)', '.MESSAGE = eps', '.EVENT = DIAGNOSTIC "Deprecated" perrorcall.MESSAGE perrorcall.LINE'):
                values += ['~$error_call_valid(S_warning,perrorcall[' + field + '])']
        values += [*budget('S')]
        for field in ('.SITE = PORIGIN 0 eps', '.LINE = $(pconfigcall_S.LINE + 1)', '.SELECTION = eps', '.KIND = INTRINSIC_CONSTANT', '.OWNER = (0)'):
            values += ['~$dynamic_class_define_nan_valid(S,pconfigcall_S[' + field + '])']
    return values


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
