#!/usr/bin/env python3
"""Reached special-name duplicates preserve case, values and captured inputs."""
import json
import os
from pathlib import Path

import define_startup_duplicate_protocol as startup
import define_special_duplicate_sources as sources

driver, common, text, b64 = startup.driver, startup.common, startup.text, startup.b64
PREFIX = startup.PREFIX


def front(state, start, name, candidate, old):
    call = 'pconfigcall_' + state
    return [*startup.reach(state, start, 0, name),
        state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
        '$dynamic_define_values(' + call + ') = ((' + text(name) + ',' + candidate + '))',
        '$named_slot_at(' + call + '.SENT,0) = NAMED_SENT (KNOWN pvalue_name_' + state + ')',
        '$string_carrier_valid(' + state + ',pvalue_name_' + state + ')',
        '$builtin_value_bytes(' + text(name) + ') = eps', '$special_constant(' + text(name) + ') = (' + old + ')',
        '$dynamic_global_constant_value(' + state + ',' + text(name) + ') = (' + old + ')',
        '$user_constant_at(' + state + '.USERCONSTANTS,' + text(name) + ') = eps',
        '$dynamic_startup_define_duplicate_valid(' + state + ',' + call + ',0)',
        '$dynamic_constant_duplicate_valid(' + state + ',' + call + ',0)',
        '$dynamic_scalar_define_arguments(' + state + ',' + call + ',0)',
        '$config_invoke_valid(' + state + ',' + call + ')', *common.public(state)]


def preserved(state):
    return ['$dynamic_global_constant_value(' + state + ',' + text(name) + ') = (' + value + ')'
        for name, value in [('TrUe', 'PBOOL true'), ('false', 'PBOOL false'), ('NULL', 'PNULL')]]


def default(after, before, name):
    call, warning = 'pconfigcall_' + before, after + '_warning'
    return ['~$error_handler_eligible(' + before + ',2)', *common.step(warning, before),
        warning + '.TODO = (DYNAMIC_CONSTANT_DUPLICATE ' + call + ' 0) :: ptask_' + before + '*',
        '$call_task_valid(' + warning + ',DYNAMIC_CONSTANT_DUPLICATE ' + call + ' 0)',
        warning + '.EVENTS = ' + before + '.EVENTS ++ [DIAGNOSTIC "Warning" $global_constant_duplicate_message(' + text(name) + ') ' + call + '.LINE]',
        *startup.unchanged(warning, before, 'USERCONSTANTS STORE ENV STRINGDATA ARRAYS OBJECTS SELECTEDCALLS SOURCES POOLS FILES'),
        *common.public(warning), *common.step(after, warning, 'PBOOL false'),
        after + '.TODO = ptask_' + before + '*', after + '.USERCONSTANTS = eps', *preserved(after)]


def handler(name, candidate, returning):
    values = [*common.step('S_warning', 'S'),
        'S_warning.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_S*',
        'perrorcall.RESUME = DYNAMIC_CONSTANT_DUPLICATE pconfigcall_S 0',
        'perrorcall.LEVEL = 2', 'perrorcall.SITE = pconfigcall_S.SITE', 'perrorcall.LINE = pconfigcall_S.LINE',
        'perrorcall.MESSAGE = $global_constant_duplicate_message(' + text(name) + ')',
        'perrorcall.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE pconfigcall_S.LINE',
        '$error_call_valid(S_warning,perrorcall)', 'S_warning.EVENTS = S.EVENTS', 'S_warning.USERCONSTANTS = eps',
        *common.public('S_warning'), *startup.reach('S_entered', 'S_warning', 1, name),
        'S_entered.CURRENT = (pcallcontext)', '$error_context_valid(S_entered,pcallcontext)',
        '$error_context_trigger(S_entered,pcallcontext) = (pconfigcall_S)',
        '$error_handler_trace_values(S_entered,pcallcontext,pconfigcall_S) = [pvalue_name_S,' + candidate + ',PBOOL false]',
        'S_entered.USERCONSTANTS = eps', *common.public('S_entered'),
        *startup.reach('S_returned', 'S_entered', 2, name),
        'S_returned.TODO = (ERROR_HANDLER_RESULT perrorcall_returned) :: ptask_S*',
        'perrorcall_returned.RESUME = DYNAMIC_CONSTANT_DUPLICATE pconfigcall_S 0',
        'S_returned.RESULT = KNOWN (PBOOL ' + ('false' if returning else 'true') + ')',
        '$dynamic_startup_define_duplicate_valid(S_returned,pconfigcall_S,0)',
        '$call_task_valid(S_returned,ERROR_HANDLER_RESULT perrorcall_returned)', *common.public('S_returned')]
    if returning:
        values += ['S_returned.USERCONSTANTS = [puserconstant_sibling]',
            'puserconstant_sibling.NAME = ' + text('SpecialSibling44'), 'puserconstant_sibling.VALUE = PINT 887',
            'puserconstant_sibling.CLASS = PVSCALAR', '$dynamic_startup_define_duplicate_valid(S_returned,pconfigcall_S,1)',
            '~$dynamic_startup_define_duplicate_valid(S_returned,pconfigcall_S,2)',
            'S_returned.STORE[n_name] = DEFINED pvalue_live_name', '$string_bytes(pvalue_live_name) = (' + text('handler-name44') + ')',
            'S_returned.STORE[n_candidate] = DEFINED (PINT 777)', 'S_returned.STORE[n_flag] = DEFINED (PBOOL true)',
            'S_returned.STORE[n_call] = DEFINED pvalue_live_call', '$string_bytes(pvalue_live_call) = (' + text('defined') + ')']
    else:
        values += ['S_returned.USERCONSTANTS = eps']
    values += ['S_returned.STORE[n_count] = DEFINED (PINT 1)', 'S_returned.STORE[n_result] = DEFINED (PINT 99)',
        *preserved('S_returned'), *common.step('S_pending', 'S_returned'),
        'S_pending.TODO = (DYNAMIC_CONSTANT_DUPLICATE pconfigcall_S 0) :: ptask_S*',
        'S_pending.EVENTS = S_returned.EVENTS' + (' ++ [DIAGNOSTIC "Warning" $global_constant_duplicate_message(' + text(name) + ') pconfigcall_S.LINE]' if returning else ''),
        'S_pending.USERCONSTANTS = S_returned.USERCONSTANTS', *common.public('S_pending'),
        *common.step('S_after', 'S_pending', 'PBOOL false'), 'S_after.TODO = ptask_S*',
        'S_after.USERCONSTANTS = S_returned.USERCONSTANTS', 'S_after.STORE[n_result] = DEFINED (PINT 99)', *preserved('S_after'),
        'pconfigcall_case = pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,0,KNOWN (PSTRING ' + text('TRUE' if returning else 'false') + '))]',
        '$dynamic_startup_define_duplicate_valid(S_warning,pconfigcall_case,0)',
        '~$error_call_valid(S_warning,perrorcall[.RESUME = DYNAMIC_CONSTANT_DUPLICATE pconfigcall_case 0])']
    for field in ('.LEVEL = 8192', '.MESSAGE = ' + text('forged'), '.LINE = $(perrorcall.LINE + 1)',
            '.EVENT = DIAGNOSTIC "Notice" perrorcall.MESSAGE pconfigcall_S.LINE'):
        values += ['~$error_call_valid(S_warning,perrorcall[' + field + '])']
    return values


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')', 'S_initial.COMPLETION = BUDGET']
    if name == 'literal-special-duplicates-preserve-true-false-null':
        values += [*front('S', 'S_initial', 'true', 'PINT 853', 'PBOOL true'), 'S.USERCONSTANTS = eps',
            'pconfigcall_S.SELECTION = eps', 'pconfigcall_S.SENT = [NAMED_SENT (KNOWN pvalue_name_S),NAMED_SENT (KNOWN (PINT 853))]',
            *default('S_true_return', 'S', 'true'),
            *front('S_false', 'S_true_return', 'FaLsE', 'PINT 857', 'PBOOL false'),
            'pconfigcall_S_false.SENT = [NAMED_SENT (KNOWN pvalue_name_S_false),NAMED_SENT (KNOWN (PINT 857)),NAMED_SENT (KNOWN (PBOOL false))]',
            *default('S_false_return', 'S_false', 'FaLsE'),
            *front('S_null', 'S_false_return', 'NULL', 'PINT 859', 'PNULL'),
            'pconfigcall_S_null.SENT = [NAMED_SENT (KNOWN pvalue_name_S_null),NAMED_SENT (KNOWN (PINT 859)),NAMED_SENT (KNOWN (PBOOL false))]',
            *default('S_null_return', 'S_null', 'NULL'),
            'pconfigcall_case = pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,0,KNOWN (PSTRING ' + text('TRUE') + '))]',
            '$special_constant(' + text('TRUE') + ') = (PBOOL true)', '~$dynamic_startup_define_duplicate_valid(S,pconfigcall_case,0)',
            '~$dynamic_startup_define_duplicate_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,1,KNOWN (PINT 999))],0)',
            *startup.refusals('S'), *startup.budget('S')]
        for flag in ('PBOOL true', 'PNULL', 'PINT 0', 'PFLOAT 9221120237041090560', 'PSTRING ' + text('0')):
            values += ['~$dynamic_startup_define_duplicate_valid(S_false,pconfigcall_S_false[.SENT = $named_slot_set(pconfigcall_S_false.SENT,2,KNOWN (' + flag + '))],0)']
    else:
        captured = name == 'captured-special-name-and-false-flag-before-live-effects'
        assert captured or name == 'strict-special-duplicate-after-all-argument-effects'
        key, candidate, old = ('tRuE', 'pvalue_candidate', 'PBOOL true') if captured else ('FaLsE', 'PINT 889', 'PBOOL false')
        values += [*front('S', 'S_initial', key, candidate, old), 'S.USERCONSTANTS = eps',
            'pconfigcall_S.SENT = [NAMED_SENT (KNOWN pvalue_name_S),NAMED_SENT (KNOWN (' + candidate + ')),NAMED_SENT (KNOWN (PBOOL false))]',
            'pvalue_name_S = PSTRING_CARRIER (REQUEST_STRING n_name_string) ' + text(key),
            'pconfigcall_S.SELECTION = (n_selection)', 'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
            '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            '$lookup(S.ENV,' + text('count') + ') = (n_count)', 'S.STORE[n_count] = DEFINED (PINT 0)',
            '$lookup(S.ENV,' + text('call') + ') = (n_call)', 'S.STORE[n_call] = DEFINED pvalue_current_call',
            '$string_bytes(pvalue_current_call) = (' + text('constant' if captured else 'defined') + ')',
            ('~$config_strict(S,pconfigcall_S)' if captured else '$config_strict(S,pconfigcall_S)'),
            '$test_outputs(S.EVENTS) = ' + text('B|V|' if captured else 'B|V|N|')]
        if captured:
            values += ['pvalue_candidate = PSTRING_CARRIER (REQUEST_STRING n_candidate_string) preqbytes_candidate',
                'preqbytes_candidate = ' + text('outer-value44'), '$string_carrier_valid(S,pvalue_candidate)',
                '$lookup(S.ENV,' + text('name') + ') = (n_name)', 'S.STORE[n_name] = DEFINED pvalue_before_name',
                '$string_bytes(pvalue_before_name) = (' + text('value-name44') + ')',
                '$lookup(S.ENV,' + text('candidate') + ') = (n_candidate)', 'S.STORE[n_candidate] = DEFINED (PINT 997)',
                '$lookup(S.ENV,' + text('flag') + ') = (n_flag)', 'S.STORE[n_flag] = DEFINED (PBOOL true)',
                'n_bad_string = |S.STRINGDATA|',
                'pvalue_bad_name = PSTRING_CARRIER (REQUEST_STRING n_bad_string) ' + text(key),
                '~$string_carrier_valid(S,pvalue_bad_name)',
                '~$dynamic_startup_define_duplicate_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,0,KNOWN pvalue_bad_name)],0)',
                'pvalue_bad_candidate = PSTRING_CARRIER (REQUEST_STRING n_bad_string) preqbytes_candidate',
                '~$string_carrier_valid(S,pvalue_bad_candidate)',
                '~$dynamic_startup_define_duplicate_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,1,KNOWN pvalue_bad_candidate)],0)']
        values += [*handler(key, candidate, captured), *startup.refusals('S'), *startup.budget('S')]
    return values


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__),
        str(Path(startup.__file__).relative_to(driver.ROOT)): sources.family.sha(startup.__file__)})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
