#!/usr/bin/env python3
"""Reached NaN receive, ignored/duplicate phases, raw capture and strict errors."""
import json
import os
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import define_nan_flag_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64
NAN = 'PFLOAT 9221120237041090560'

PREFIX = r"""
dec $test_nan_flag_task(ptask) : (nat, pconfigcall)?
def $test_nan_flag_task(CONFIG_INVOKE pconfigcall) = ((0,pconfigcall))
  -- if $dynamic_nan_define_flag_call(pconfigcall)
def $test_nan_flag_task(DYNAMIC_NAN_DEFINE_FLAG_RESULT pconfigcall) = ((1,pconfigcall))
def $test_nan_flag_task(DYNAMIC_NAN_DEFINE_FLAG_CASE pconfigcall) = ((2,pconfigcall))
def $test_nan_flag_task(DYNAMIC_NAN_DEFINE_FLAG_DUPLICATE pconfigcall n) = ((3,pconfigcall))
def $test_nan_flag_task(ptask) = eps -- otherwise
dec $test_nan_flag_front(pstate, nat, preqbytes) : bool
def $test_nan_flag_front(S, n_stage, preqbytes) = true
  -- if S.TODO = ptask :: ptask_tail*
  -- if $test_nan_flag_task(ptask) = ((n_stage,pconfigcall))
  -- if $named_slot_at(pconfigcall.SENT,0) = NAMED_SENT (KNOWN pvalue_name)
  -- if $string_bytes(pvalue_name) = (preqbytes)
def $test_nan_flag_front(S, n_stage, preqbytes) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_call(S,pcallcontext) = (perrorcall)
  -- if $test_nan_flag_task(perrorcall.RESUME) = ((n_phase,pconfigcall))
  -- if n_stage = $(n_phase + 3)
  -- if $named_slot_at(pconfigcall.SENT,0) = NAMED_SENT (KNOWN pvalue_name)
  -- if $string_bytes(pvalue_name) = (preqbytes)
def $test_nan_flag_front(S, 7, preqbytes) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_NAN_DEFINE_FLAG_CASE pconfigcall
  -- if $named_slot_at(pconfigcall.SENT,0) = NAMED_SENT (KNOWN pvalue_name)
  -- if $string_bytes(pvalue_name) = (preqbytes)
def $test_nan_flag_front(S, n_stage, preqbytes) = false -- otherwise
dec $test_nan_flag_seek(pstate, nat, preqbytes, nat) : pstate
def $test_nan_flag_seek(S, n_stage, preqbytes, 0) = S
def $test_nan_flag_seek(S, n_stage, preqbytes, n) = S
  -- if $(n > 0)
  -- if $test_nan_flag_front(S,n_stage,preqbytes) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_nan_flag_seek(S, n_stage, preqbytes, n) = $test_nan_flag_seek($drive_steps($test_running(S),1),n_stage,preqbytes,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_nan_flag_front(S,n_stage,preqbytes)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def reach(state, start, stage, name):
    return [state + '_found = $test_nan_flag_seek(' + start + ',' + str(stage) + ',' + text(name) + ',3000)',
        state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_nan_flag_front(' + state + ',' + str(stage) + ',' + text(name) + ')', *common.public(state)]


def front(state, start, name, value):
    call = 'pconfigcall_' + state
    return [*reach(state, start, 0, name), state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
        call + '.SENT = [NAMED_SENT (KNOWN pvalue_name_' + state + '),NAMED_SENT (KNOWN (' + value + ')),NAMED_SENT (KNOWN (' + NAN + '))]',
        call + '.KIND = INTRINSIC_DEFINE', call + '.OWNER = eps', call + '.PACKS = eps',
        '$config_invoke_valid(' + state + ',' + call + ')', '$dynamic_nan_define_flag_valid(' + state + ',' + call + ')',
        '~$dynamic_scalar_define_flag_call(' + call + ')', '~$dynamic_constant_case_valid(' + state + ',' + call + ')']


def unchanged(after, before, fields):
    return [after + '.' + field + ' = ' + before + '.' + field for field in fields.split()]


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)', state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)', state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def default_warning(state, source, call, resume, message):
    return [*common.step(state, source), state + '.TODO = (' + resume + ') :: ptask_' + source + '*',
        state + '.EVENTS = ' + source + '.EVENTS ++ [DIAGNOSTIC "Warning" ' + message + ' ' + call + '.LINE]',
        '$call_task_valid(' + state + ',' + resume + ')',
        *unchanged(state, source, 'STORE ENV USERCONSTANTS STRINGDATA ARRAYS OBJECTS ALLOCATIONS SELECTEDCALLS'), *common.public(state)]


def warning(state, source, call, resume, message):
    error = 'perrorcall_' + state
    return [*common.step(state, source), state + '.TODO = (ERROR_HANDLER_INVOKE ' + error + ') :: ptask_' + source + '*',
        error + '.RESUME = ' + resume, error + '.SITE = ' + call + '.SITE', error + '.LINE = ' + call + '.LINE',
        error + '.LEVEL = 2', error + '.MESSAGE = ' + message,
        error + '.EVENT = DIAGNOSTIC "Warning" ' + message + ' ' + call + '.LINE',
        '$error_call_valid(' + state + ',' + error + ')',
        *unchanged(state, source, 'STORE ENV USERCONSTANTS STRINGDATA ARRAYS OBJECTS ALLOCATIONS EVENTS SELECTEDCALLS'), *common.public(state)]


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', '~$dynamic_define_quiet_flag(' + NAN + ')']
    if name == 'literal-nan-flag-publication-and-duplicate':
        values += [*front('S', 'S_initial', 'LiteralNanFlag35', 'PINT 193'), '~$config_strict(S,pconfigcall_S)',
            'pconfigcall_S.SELECTION = eps', 'S.USERCONSTANTS = eps',
            '$intrinsic_argument(S,pconfigcall_S.SITE,2) = ((expression,false,eps,porigin_flag,z_flag))',
            '$compiled_read(S,porigin_flag) = (' + NAN + ')',
            '~$call_task_valid(S,DYNAMIC_SCALAR_DEFINE_FLAG_RESULT pconfigcall_S)',
            *default_warning('S_received', 'S', 'pconfigcall_S', 'DYNAMIC_NAN_DEFINE_FLAG_RESULT pconfigcall_S', '$dynamic_nan_define_flag_message()'),
            *default_warning('S_case', 'S_received', 'pconfigcall_S', 'DYNAMIC_NAN_DEFINE_FLAG_CASE pconfigcall_S', '$dynamic_constant_case_message()'),
            *common.step('S_published', 'S_case', 'PBOOL true'),
            'S_published.USERCONSTANTS = [puserconstant]', 'puserconstant.NAME = ' + text('LiteralNanFlag35'),
            'puserconstant.ORIGIN = pconfigcall_S.SITE', 'puserconstant.VALUE = PINT 193',
            'puserconstant.CLASS = PVSCALAR', 'puserconstant.READS = eps', 'puserconstant.RECEIVES = eps',
            'S_published = S_case[.TODO = ptask_S*][.USERCONSTANTS = [puserconstant]][.RESULT = KNOWN (PBOOL true)][.BASE = BASE_VALUE (KNOWN PNULL)]',
            '$user_constants_valid(S_published,S_published.USERCONSTANTS)',
            '~$user_constants_valid(S_published,[puserconstant[.VALUE = PINT 194]])',
            *front('S_second', 'S_published', 'LiteralNanFlag35', 'PINT 194'),
            *default_warning('S_second_received', 'S_second', 'pconfigcall_S_second', 'DYNAMIC_NAN_DEFINE_FLAG_RESULT pconfigcall_S_second', '$dynamic_nan_define_flag_message()'),
            *default_warning('S_second_case', 'S_second_received', 'pconfigcall_S_second', 'DYNAMIC_NAN_DEFINE_FLAG_CASE pconfigcall_S_second', '$dynamic_constant_case_message()'),
            *default_warning('S_duplicate', 'S_second_case', 'pconfigcall_S_second', 'DYNAMIC_NAN_DEFINE_FLAG_DUPLICATE pconfigcall_S_second 1', '$global_constant_duplicate_message(' + text('LiteralNanFlag35') + ')'),
            '~$dynamic_nan_define_flag_duplicate_valid(S_duplicate,pconfigcall_S_second,0)',
            '~$dynamic_nan_define_flag_duplicate_valid(S_duplicate,pconfigcall_S_second,2)',
            *common.step('S_return', 'S_duplicate', 'PBOOL false'),
            'S_return = S_duplicate[.TODO = ptask_S_second_case*][.RESULT = KNOWN (PBOOL false)][.BASE = BASE_VALUE (KNOWN PNULL)]',
            'pconfigcall_bad = pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,2,KNOWN (PFLOAT 9221120237041090561))]',
            '$dynamic_nan_define_flag_call(pconfigcall_bad)', '$config_invoke_valid(S,pconfigcall_bad)',
            '~$dynamic_nan_define_flag_valid(S,pconfigcall_bad)',
            'S_bad = $drive_steps(S[.TODO = (CONFIG_INVOKE pconfigcall_bad) :: ptask_S*],1)',
            'S_bad.COMPLETION = UNSUPPORTED "NaN define flag reception"', *budget('S'), *budget('S_received'), *budget('S_duplicate')]
    elif name == 'captured-nan-flag-and-later-warning-throw':
        values += [*front('S', 'S_initial', 'CapturedNanFlag35', 'PINT 197'),
            'pconfigcall_S.SELECTION = (n_selection)', 'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
            '$test_outputs(S.EVENTS) = ' + text('B|V|N|'),
            '$lookup(S.ENV,' + text('flag') + ') = (n_flag)', 'S.STORE[n_flag] = DEFINED (PINT 0)',
            *warning('S_warning', 'S', 'pconfigcall_S', 'DYNAMIC_NAN_DEFINE_FLAG_RESULT pconfigcall_S', '$dynamic_nan_define_flag_message()'),
            *reach('S_handler', 'S_warning', 4, 'CapturedNanFlag35'),
            'S_handler.CURRENT = (pcallcontext_handler)', '$error_context_call(S_handler,pcallcontext_handler) = (perrorcall_handler)',
            '$error_context_trigger(S_handler,pcallcontext_handler) = (pconfigcall_S)',
            '$error_handler_trace_values(S_handler,pcallcontext_handler,pconfigcall_S) = [pvalue_name_S,(PINT 197),(' + NAN + ')]',
            *reach('S_received', 'S_handler', 1, 'CapturedNanFlag35'),
            'S_received.TODO = (DYNAMIC_NAN_DEFINE_FLAG_RESULT pconfigcall_S) :: ptask_received*',
            'S_received.USERCONSTANTS = [puserconstant]', 'puserconstant.VALUE = PINT 297',
            'S_received.STORE[n_flag] = DEFINED (PBOOL false)',
            *warning('S_ignored', 'S_received', 'pconfigcall_S', 'DYNAMIC_NAN_DEFINE_FLAG_CASE pconfigcall_S', '$dynamic_constant_case_message()'),
            *reach('S_throw', 'S_ignored', 7, 'CapturedNanFlag35'),
            'S_throw.TODO = (THROW_SEARCH n_throw) :: (ERROR_HANDLER_RESULT perrorcall_throw) :: ptask_tail*',
            'perrorcall_throw.RESUME = DYNAMIC_NAN_DEFINE_FLAG_CASE pconfigcall_S',
            '$throwable_live(S_throw,n_throw)', '$throwable_field(S_throw,n_throw,"previous") = PNULL',
            '$lookup(S_throw.ENV,' + text('result') + ') = (n_result)', 'S_throw.STORE[n_result] = DEFINED (PINT 99)',
            'S_discard = S_throw[.TODO = (THROW_SEARCH n_throw) :: ptask_tail*]',
            'S_before = $error_handler_restore($identity_read_discard(S_discard,perrorcall_throw.RESUME),perrorcall_throw.CALLBACK)',
            '$error_handler_eligible(S_before,2)', 'S_before.USERCONSTANTS = [puserconstant]',
            'S_expected = S_before[.ERRORFATALTRACE = eps]',
            '$dynamic_nan_define_flag_pending(S_before,pconfigcall_S) = S_expected',
            *common.step('S_after', 'S_throw'), 'S_after = S_expected',
            'S_after.STORE[n_result] = DEFINED (PINT 99)', '$throwable_live(S_after,n_throw)',
            *common.public('S_after'), *budget('S_warning'), *budget('S_received'), *budget('S_throw')]
        for field in ('.SITE = PORIGIN 0 eps', '.LINE = $(pconfigcall_S.LINE + 1)', '.SELECTION = eps', '.KIND = INTRINSIC_CONSTANT'):
            values += ['~$dynamic_nan_define_flag_valid(S,pconfigcall_S[' + field + '])']
    else:
        assert name == 'strict-nan-flag-after-all-argument-effects'
        values += [*front('S', 'S_initial', 'StrictNanFlag35', 'PINT 199'), '$config_strict(S,pconfigcall_S)',
            '$test_outputs(S.EVENTS) = ' + text('B|V|N|'), 'S.USERCONSTANTS = eps',
            '~$call_task_valid(S,DYNAMIC_NAN_DEFINE_FLAG_RESULT pconfigcall_S)',
            '~$call_task_valid(S,DYNAMIC_NAN_DEFINE_FLAG_CASE pconfigcall_S)',
            '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            *common.step('S_error', 'S'), 'S_error.TODO = (THROW_SEARCH n_error) :: ptask_error*',
            'S_error.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "TypeError"',
            '$string_bytes($throwable_field(S_error,n_error,"message")) = (' + text('define(): Argument #3 ($case_insensitive) must be of type bool, float given') + ')',
            '$throwable_field(S_error,n_error,"line") = PINT pconfigcall_S.LINE',
            '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
            'S_error.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_frame))]',
            '$trace_array_field(S_error,n_frame,' + text('function') + ') = PSTRING ' + text('define'),
            '$trace_array_field(S_error,n_frame,' + text('args') + ') = PARRAY n_args',
            'S_error.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_name_S),ENTRY (KINT 1) (DIRECT (PINT 199)),ENTRY (KINT 2) (DIRECT (' + NAN + '))]',
            *unchanged('S_error', 'S', 'STORE USERCONSTANTS STRINGDATA EVENTS SELECTEDCALLS'), *common.public('S_error'), *budget('S')]
    return values


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
