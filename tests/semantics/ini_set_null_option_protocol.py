#!/usr/bin/env python3
"""Reached two-slot NULL INI options resume captured values after handlers."""
import json
import os
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import ini_set_null_option_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64
MESSAGE = 'ini_set(): Passing null to parameter #1 ($option) of type string is deprecated'
PREFIX = r"""
dec $test_ini_null_front(pstate, nat) : bool
def $test_ini_null_front(S, 0) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN PNULL), NAMED_SENT (KNOWN pvalue)]
def $test_ini_null_front(S, 1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_call(S,pcallcontext) = (perrorcall)
  -- if perrorcall.RESUME = CONFIG_INI_NULL_RESULT pconfigcall
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_ini_null_front(S, 2) = true
  -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = CONFIG_INI_NULL_RESULT pconfigcall
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_ini_null_front(S, 3) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_option), NAMED_SENT (KNOWN pvalue)]
  -- if $string_bytes(pvalue_option) = ($ptascii("precision"))
def $test_ini_null_front(S, n_stage) = false -- otherwise
dec $test_ini_null_seek(pstate, nat, nat) : pstate
def $test_ini_null_seek(S, n_stage, 0) = S
def $test_ini_null_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_ini_null_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_ini_null_seek(S, n_stage, n) = $test_ini_null_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_ini_null_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def reach(state, start, stage):
    return [state + '_found = $test_ini_null_seek(' + start + ',' + str(stage) + ',3000)',
        state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_ini_null_front(' + state + ',' + str(stage) + ')']


def unchanged(after, before, fields):
    return [after + '.' + field + ' = ' + before + '.' + field for field in fields.split()]


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)',
        state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)',
        state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def front(candidate):
    return [*reach('S', 'S_initial', 0),
        'S.TODO = (CONFIG_INVOKE pconfigcall_S) :: ptask_S*',
        'pconfigcall_S.KIND = INTRINSIC_INI_SET', 'pconfigcall_S.INDEX = 2',
        'pconfigcall_S.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (' + candidate + '))]',
        'pconfigcall_S.OWNER = eps', 'pconfigcall_S.PACKS = eps', '~pconfigcall_S.NAMED',
        '~$pipe_site(S,pconfigcall_S.SITE)', '$config_invoke_valid(S,pconfigcall_S)',
        '$dynamic_scalar_define_arguments(S,pconfigcall_S,0)',
        '$config_ini_quiet_value(S,' + candidate + ')', 'S.USERCONSTANTS = eps', *common.public('S')]


def refusals():
    values = []
    for field in ('.SITE = PORIGIN 0 eps', '.LINE = $(pconfigcall_S.LINE + 1)',
            '.INDEX = 1', '.OWNER = (0)', '.NAMED = true', '.KIND = INTRINSIC_INI_GET',
            '.SELECTION = (|S.SELECTEDCALLS|)', '.SENT = pconfigcall_S.SENT[0:1]',
            '.SENT = pconfigcall_S.SENT ++ [NAMED_SENT (KNOWN PNULL)]'):
        values += ['~$config_ini_null_valid(S,pconfigcall_S[' + field + '])']
    values += ['~$config_ini_null_valid(S[.CODE = eps],pconfigcall_S)',
        '~$config_ini_null_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,0,KNOWN (PBOOL false))])',
        'pvalue_bad = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ' + text('forged-value62'),
        '~$string_carrier_valid(S,pvalue_bad)', '~$config_ini_quiet_value(S,pvalue_bad)',
        '~$config_ini_null_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,1,KNOWN pvalue_bad)])']
    for value in ('PNULL', 'PBOOL false', 'PINT 0', 'PFLOAT 4612811918334230528',
            'PFLOAT 9218868437227405312', 'PSTRING_CARRIER INTERNED_STRING ' + text('12')):
        values += ['$config_ini_quiet_value(S,' + value + ')']
    for value in ('PFLOAT 9221120237041090560', 'PSTRING ' + text('12'), 'PARRAY 0', 'POBJECT 0'):
        values += ['~$config_ini_quiet_value(S,' + value + ')']
    return values


def strict_error():
    return [*common.step('S_error', 'S'),
        'S_error.TODO = (THROW_SEARCH n_error) :: ptask_S*',
        'S_error.OBJECTS[n_error] = THROWABLE pthrowable_error', 'pthrowable_error.KIND = "TypeError"',
        'pthrowable_error.ORIGIN = (pconfigcall_S.SITE)',
        '$string_bytes($throwable_field(S_error,n_error,"message")) = (' + text('ini_set(): Argument #1 ($option) must be of type string, null given') + ')',
        '$throwable_field(S_error,n_error,"previous") = PNULL',
        '$throwable_field(S_error,n_error,"line") = PINT pconfigcall_S.LINE',
        '$string_bytes($throwable_field(S_error,n_error,"file")) = ($call_sourcefile(S.FILES,pconfigcall_S.SITE))',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
        'S_error.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_api)),ENTRY (KINT 1) (DIRECT (PARRAY n_caller))]',
        '$trace_array_field(S_error,n_api,' + text('function') + ') = PSTRING ' + text('ini_set'),
        '$trace_array_field(S_error,n_api,' + text('line') + ') = PINT pconfigcall_S.LINE',
        '$trace_array_field(S_error,n_api,' + text('args') + ') = PARRAY n_args',
        'S_error.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT PNULL),ENTRY (KINT 1) (DIRECT (PINT 1987))]',
        '$node_children(S_error,HARRAY n_args) = eps',
        '$trace_array_field(S_error,n_caller,' + text('function') + ') = PSTRING ' + text('strictNullSetCaller62'),
        'S_error.STORE[n_result] = DEFINED (PINT 99)',
        *unchanged('S_error', 'S', 'STORE ENV EVENTS USERCONSTANTS STRINGDATA SELECTEDCALLS ERRORHANDLER PRECISIONINI PRECISIONMODIFIED FILEINCLUDEPATH'),
        *common.public('S_error')]


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET']
    if name == 'ordinary-null-ini-set-default-and-precision-recovery':
        values += [*front('PINT 1973'), '~$config_strict(S,pconfigcall_S)',
            '$config_ini_null_valid(S,pconfigcall_S)', '~$error_handler_eligible(S,8192)',
            'pconfigcall_S.SELECTION = eps', '$test_outputs(S.EVENTS) = ' + text('B|'),
            'S.PRECISIONINI = ' + text('14'), *common.step('S_after', 'S'),
            'S_after.RESULT = KNOWN (PBOOL false)', 'S_after.TODO = ptask_S*',
            'S_after.BASE = BASE_VALUE (KNOWN PNULL)',
            'S_after.EVENTS = S.EVENTS ++ [DIAGNOSTIC "Deprecated" $config_ini_null_message(pconfigcall_S) pconfigcall_S.LINE]',
            *unchanged('S_after', 'S', 'STORE ENV ARRAYS OBJECTS OBJECTPROPS USERCONSTANTS STRINGDATA PRECISIONINI PRECISIONMODIFIED FILEINCLUDEPATH'),
            *common.public('S_after'),
            '~$dynamic_scalar_define_arguments(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,1,KNOWN (PINT 1974))],0)',
            '~$config_ini_null_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,1,KNOWN (PINT 1974))])',
            *reach('S_recovery', 'S_after', 3),
            'S_recovery.TODO = (CONFIG_INVOKE pconfigcall_recovery) :: ptask_recovery*',
            '$config_invoke_valid(S_recovery,pconfigcall_recovery)',
            '$dynamic_scalar_define_arguments(S_recovery,pconfigcall_recovery,0)',
            'pconfigcall_forged_null = pconfigcall_recovery[.SENT = $named_slot_set(pconfigcall_recovery.SENT,0,KNOWN PNULL)]',
            '$config_invoke_valid(S_recovery,pconfigcall_forged_null)',
            '~$dynamic_scalar_define_arguments(S_recovery,pconfigcall_forged_null,0)',
            '~$config_ini_null_valid(S_recovery,pconfigcall_forged_null)',
            *common.step('S_recovered', 'S_recovery'),
            'S_recovered.RESULT = KNOWN pvalue_old_precision',
            '$string_bytes(pvalue_old_precision) = (' + text('14') + ')',
            'S_recovered.PRECISIONINI = ' + text('12'), 'S_recovered.PRECISIONMODIFIED',
            'S_recovered.TODO = ptask_recovery*', *common.public('S_recovered'),
            *refusals(), *budget('S'),
            'S_final = $drive_steps(S_recovered,3000)', 'S_final.COMPLETION = NORMAL',
            '$test_outputs(S_final.EVENTS) = ' + text('B|F|14|R|14|12'),
            'S_final.PRECISIONINI = ' + text('12'), *common.public('S_final')]
    else:
        strict = name == 'strict-null-ini-set-option-before-value-after-effects'
        assert strict or name == 'selected-null-option-handler-preserves-captures-and-precision'
        values += [*front('PINT 1987' if strict else 'pvalue_captured'),
            'pconfigcall_S.SELECTION = (n_selection)',
            'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_INI_SET',
            '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            '$lookup(S.ENV,' + text('effects') + ') = (n_effects)', 'S.STORE[n_effects] = DEFINED (PINT 1)',
            '$test_outputs(S.EVENTS) = ' + text('B|V|'),
            '$lookup(S.ENV,' + text('call') + ') = (n_call)',
            'S.STORE[n_call] = DEFINED pvalue_call', '$string_bytes(pvalue_call) = (' + text('ini_get') + ')',
            '$lookup(S.ENV,' + text('option') + ') = (n_option)',
            'S.STORE[n_option] = DEFINED pvalue_option', '$string_bytes(pvalue_option) = (' + text('precision') + ')',
            '$lookup(S.ENV,' + text('value') + ') = (n_value)']
        if strict:
            values += ['$config_strict(S,pconfigcall_S)', '~$config_ini_null_valid(S,pconfigcall_S)',
                'S.STORE[n_value] = DEFINED (PINT 0)', 'S.PRECISIONINI = ' + text('9'),
                'S.ERRORHANDLER.CALLBACK = eps', *strict_error(), *refusals(), *budget('S'),
                'S_final = $drive_steps(S_error,3000)', 'S_final.COMPLETION = NORMAL',
                '$test_outputs(S_final.EVENTS) = ' + text('B|V|ini_set(): Argument #1 ($option) must be of type string, null given|ini_set|N|1987|strictNullSetCaller62|99|1|9|ini_get|precision|0'),
                'S_final.PRECISIONINI = ' + text('9'), *common.public('S_final')]
        else:
            values += ['pvalue_captured = PSTRING_CARRIER (REQUEST_STRING n_candidate) ' + text('captured-value62'),
                '$string_carrier_valid(S,pvalue_captured)', '~$config_strict(S,pconfigcall_S)',
                '$config_ini_null_valid(S,pconfigcall_S)', '$error_handler_eligible(S,8192)',
                'S.PRECISIONINI = ' + text('6'), 'S.STORE[n_value] = DEFINED pvalue_live',
                '$string_bytes(pvalue_live) = (' + text('value-live62') + ')',
                '$lookup(S.ENV,' + text('warnings') + ') = (n_warnings)', 'S.STORE[n_warnings] = DEFINED (PINT 0)',
                *common.step('S_dispatch', 'S'),
                'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_deprecated) :: ptask_S*',
                'perrorcall_deprecated.RESUME = CONFIG_INI_NULL_RESULT pconfigcall_S',
                'perrorcall_deprecated.LEVEL = 8192', 'perrorcall_deprecated.MESSAGE = ' + text(MESSAGE),
                'perrorcall_deprecated.MESSAGE = $config_ini_null_message(pconfigcall_S)',
                'perrorcall_deprecated.SITE = pconfigcall_S.SITE', 'perrorcall_deprecated.LINE = pconfigcall_S.LINE',
                'perrorcall_deprecated.EVENT = DIAGNOSTIC "Deprecated" perrorcall_deprecated.MESSAGE pconfigcall_S.LINE',
                '$error_call_valid(S_dispatch,perrorcall_deprecated)',
                '$call_task_valid(S_dispatch,ERROR_HANDLER_INVOKE perrorcall_deprecated)',
                *unchanged('S_dispatch', 'S', 'STORE ENV EVENTS USERCONSTANTS STRINGDATA PRECISIONINI PRECISIONMODIFIED FILEINCLUDEPATH'),
                *common.public('S_dispatch'), *reach('S_handler', 'S_dispatch', 1),
                'S_handler.CURRENT = (pcallcontext_handler)', '$error_context_valid(S_handler,pcallcontext_handler)',
                '$error_context_trigger(S_handler,pcallcontext_handler) = (pconfigcall_S)',
                '$error_handler_trace_values(S_handler,pcallcontext_handler,pconfigcall_S) = [PNULL,pvalue_captured]',
                'S_handler.ERRORHANDLER.CALLBACK = eps', *common.public('S_handler'),
                *reach('S_return', 'S_handler', 2),
                'S_return.TODO = (ERROR_HANDLER_RESULT perrorcall_return) :: ptask_S*',
                'perrorcall_return.RESUME = CONFIG_INI_NULL_RESULT pconfigcall_S',
                'perrorcall_return.CALLBACK = perrorcall_deprecated.CALLBACK',
                '$call_task_valid(S_return,ERROR_HANDLER_RESULT perrorcall_return)',
                'S_return.RESULT = KNOWN (PBOOL true)', 'S_return.CURRENT = S.CURRENT',
                'S_return.ENV = S.ENV', 'S_return.FRAMES = S.FRAMES',
                'S_return.STORE[n_result] = DEFINED (PINT 99)', 'S_return.STORE[n_effects] = DEFINED (PINT 1)',
                'S_return.STORE[n_warnings] = DEFINED (PINT 1)', 'S_return.PRECISIONINI = ' + text('8'),
                'S_return.PRECISIONMODIFIED', '$config_ini_null_valid(S_return,pconfigcall_S)',
                '$test_outputs(S_return.EVENTS) = ' + text('B|V|W|8192|' + MESSAGE + '|'),
                *common.public('S_return')]
            for variable, spelling in [('call', 'ini_restore'), ('option', 'precision'), ('value', 'handler-value62')]:
                values += ['S_return.STORE[n_' + variable + '] = DEFINED pvalue_handler_' + variable,
                    '$string_bytes(pvalue_handler_' + variable + ') = (' + text(spelling) + ')']
            values += ['S_marker = $error_handler_restore(S_return[.TODO = (CONFIG_INI_NULL_RESULT pconfigcall_S) :: ptask_S*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)],perrorcall_return.CALLBACK)',
                *common.step('S_resume', 'S_return'), 'S_resume = S_marker',
                '$call_task_valid(S_resume,CONFIG_INI_NULL_RESULT pconfigcall_S)',
                '$task_nodes(CONFIG_INI_NULL_RESULT pconfigcall_S) = eps',
                *common.public('S_resume'), *common.step('S_after', 'S_resume'),
                'S_after = S_resume[.TODO = ptask_S*][.RESULT = KNOWN (PBOOL false)][.BASE = BASE_VALUE (KNOWN PNULL)]',
                'S_after.PRECISIONINI = ' + text('8'), 'S_after.STORE[n_result] = DEFINED (PINT 99)',
                '$string_carrier_valid(S_after,pvalue_captured)', *common.public('S_after'), *refusals(),
                *budget('S'), *budget('S_resume'),
                'S_final = $drive_steps(S_after,3000)', 'S_final.COMPLETION = NORMAL',
                '$test_outputs(S_final.EVENTS) = ' + text('B|V|W|8192|' + MESSAGE + '|F|8|1|1|ini_restore|precision|handler-value62|Z'),
                'S_final.PRECISIONINI = ' + text('8'), 'S_final.ERRORHANDLER.CALLBACK = eps',
                *common.public('S_final')]
            for field in ('.LEVEL = 2', '.LINE = $(perrorcall_deprecated.LINE + 1)', '.MESSAGE = ' + text('changed'),
                    '.EVENT = DIAGNOSTIC "Warning" perrorcall_deprecated.MESSAGE perrorcall_deprecated.LINE'):
                values += ['~$error_call_valid(S_resume,perrorcall_deprecated[' + field + '])']
    values += ['S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.USERCONSTANTS = eps']
    return values


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
