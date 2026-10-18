#!/usr/bin/env python3
"""Reached startup duplicates keep fixed values and original call captures."""
import argparse
import json
import os
from pathlib import Path
import sys

import global_constant_scalar_name_protocol as driver
import define_startup_duplicate_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64

PREFIX = r"""
dec $test_startup_call(pconfigcall, preqbytes) : bool
def $test_startup_call(pconfigcall, preqbytes) = true
  -- if pconfigcall.KIND = INTRINSIC_DEFINE
  -- if $dynamic_define_values(pconfigcall) = ((preqbytes,pvalue))
def $test_startup_call(pconfigcall, preqbytes) = false -- otherwise
dec $test_startup_front(pstate, nat, preqbytes) : bool
def $test_startup_front(S, 0, preqbytes) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if $test_startup_call(pconfigcall,preqbytes)
def $test_startup_front(S, 1, preqbytes) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_call(S,pcallcontext) = (perrorcall)
  -- if perrorcall.RESUME = DYNAMIC_CONSTANT_DUPLICATE pconfigcall n_constants
  -- if $test_startup_call(pconfigcall,preqbytes)
def $test_startup_front(S, 2, preqbytes) = true
  -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_CONSTANT_DUPLICATE pconfigcall n_constants
  -- if $test_startup_call(pconfigcall,preqbytes)
def $test_startup_front(S, n_stage, preqbytes) = false -- otherwise
dec $test_startup_seek(pstate, nat, preqbytes, nat) : pstate
def $test_startup_seek(S, n_stage, preqbytes, 0) = S
def $test_startup_seek(S, n_stage, preqbytes, n) = S
  -- if $(n > 0)
  -- if $test_startup_front(S,n_stage,preqbytes) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_startup_seek(S, n_stage, preqbytes, n) = $test_startup_seek($drive_steps($test_running(S),1),n_stage,preqbytes,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_startup_front(S,n_stage,preqbytes)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def reach(state, start, stage, name):
    return [state + '_found = $test_startup_seek(' + start + ',' + str(stage) + ',' + text(name) + ',3000)',
        state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_startup_front(' + state + ',' + str(stage) + ',' + text(name) + ')']


def front(state, start, name, candidate, old):
    call = 'pconfigcall_' + state
    return [*reach(state, start, 0, name),
        state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
        '$dynamic_define_values(' + call + ') = ((' + text(name) + ',' + candidate + '))',
        '$named_slot_at(' + call + '.SENT,0) = NAMED_SENT (KNOWN pvalue_name_' + state + ')',
        '$string_carrier_valid(' + state + ',pvalue_name_' + state + ')',
        '$dynamic_constant_initial(' + text(name) + ')', '$builtin_value_bytes(' + text(name) + ') = (' + old + ')',
        '$source_constant_lookup(' + state + ',' + text(name) + ') = (VALUE (' + old + '))',
        '$user_constant_at(' + state + '.USERCONSTANTS,' + text(name) + ') = eps',
        '$dynamic_startup_define_duplicate_valid(' + state + ',' + call + ',0)',
        '$dynamic_constant_duplicate_valid(' + state + ',' + call + ',0)',
        '$dynamic_scalar_define_arguments(' + state + ',' + call + ',0)',
        '$config_invoke_valid(' + state + ',' + call + ')', *common.public(state)]


def unchanged(after, before, fields):
    return [after + '.' + field + ' = ' + before + '.' + field for field in fields.split()]


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)', state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)', state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def default(after, before, name, old):
    call, warning = 'pconfigcall_' + before, after + '_warning'
    return ['~$error_handler_eligible(' + before + ',2)', *common.step(warning, before),
        warning + '.TODO = (DYNAMIC_CONSTANT_DUPLICATE ' + call + ' 0) :: ptask_' + before + '*',
        '$call_task_valid(' + warning + ',DYNAMIC_CONSTANT_DUPLICATE ' + call + ' 0)',
        warning + '.EVENTS = ' + before + '.EVENTS ++ [DIAGNOSTIC "Warning" $global_constant_duplicate_message(' + text(name) + ') ' + call + '.LINE]',
        *unchanged(warning, before, 'USERCONSTANTS STORE ENV STRINGDATA ARRAYS OBJECTS SELECTEDCALLS SOURCES POOLS FILES'),
        *common.public(warning), *common.step(after, warning, 'PBOOL false'),
        after + '.TODO = ptask_' + before + '*', after + '.BASE = BASE_VALUE (KNOWN PNULL)',
        after + '.USERCONSTANTS = eps', '$source_constant_lookup(' + after + ',' + text(name) + ') = (VALUE (' + old + '))']


def refusals(state):
    call = 'pconfigcall_' + state
    values = ['~$dynamic_startup_define_duplicate_valid(' + state + ',' + call + ',$(|' + state + '.USERCONSTANTS| + 1))']
    for field in ('.SITE = PORIGIN 0 eps', '.LINE = $(' + call + '.LINE + 1)',
            '.OWNER = (0)', '.KIND = INTRINSIC_CONSTANT', '.SELECTION = (|' + state + '.SELECTEDCALLS|)'):
        values += ['~$dynamic_startup_define_duplicate_valid(' + state + ',' + call + '[' + field + '],0)']
    for name in ('PHP_VERSION_ID', 'php_int_size', '\\PHP_INT_SIZE', 'A::B'):
        values += ['$builtin_value_bytes(' + text(name) + ') = eps',
            '~$dynamic_startup_define_duplicate_valid(' + state + ',' + call + '[.SENT = $named_slot_set(' + call + '.SENT,0,KNOWN (PSTRING ' + text(name) + '))],0)']
    for candidate in ('PARRAY 0', 'POBJECT 0'):
        values += ['~$dynamic_startup_define_duplicate_valid(' + state + ',' + call + '[.SENT = $named_slot_set(' + call + '.SENT,1,KNOWN (' + candidate + '))],0)']
    values += ['~$dynamic_startup_define_duplicate_valid(' + state + ',' + call + '[.SENT = $named_slot_set(' + call + '.SENT,0,KNOWN (PSTRING (' + text('PHP_INT_SIZE') + ' ++ [0])))],0)']
    return values


def handler(state, name, candidate, returning):
    call = 'pconfigcall_' + state
    warning, entered, returned, pending, after = [state + suffix for suffix in ('_warning', '_entered', '_returned', '_pending', '_after')]
    values = [*common.step(warning, state),
        warning + '.TODO = (ERROR_HANDLER_INVOKE perrorcall_' + state + ') :: ptask_' + state + '*',
        'perrorcall_' + state + '.RESUME = DYNAMIC_CONSTANT_DUPLICATE ' + call + ' 0',
        'perrorcall_' + state + '.LEVEL = 2', 'perrorcall_' + state + '.SITE = ' + call + '.SITE',
        'perrorcall_' + state + '.LINE = ' + call + '.LINE',
        'perrorcall_' + state + '.MESSAGE = $global_constant_duplicate_message(' + text(name) + ')',
        'perrorcall_' + state + '.EVENT = DIAGNOSTIC "Warning" perrorcall_' + state + '.MESSAGE ' + call + '.LINE',
        '$error_call_valid(' + warning + ',perrorcall_' + state + ')',
        warning + '.EVENTS = ' + state + '.EVENTS', warning + '.USERCONSTANTS = eps', *common.public(warning),
        *reach(entered, warning, 1, name), entered + '.CURRENT = (pcallcontext_' + state + ')',
        '$error_context_valid(' + entered + ',pcallcontext_' + state + ')',
        '$error_context_trigger(' + entered + ',pcallcontext_' + state + ') = (' + call + ')',
        '$error_handler_trace_values(' + entered + ',pcallcontext_' + state + ',' + call + ') = [pvalue_name_' + state + ',' + candidate + ',PBOOL false]',
        entered + '.USERCONSTANTS = eps', *common.public(entered),
        *reach(returned, entered, 2, name),
        returned + '.TODO = (ERROR_HANDLER_RESULT perrorcall_returned_' + state + ') :: ptask_' + state + '*',
        'perrorcall_returned_' + state + '.RESUME = DYNAMIC_CONSTANT_DUPLICATE ' + call + ' 0',
        returned + '.RESULT = KNOWN (PBOOL ' + ('false' if returning else 'true') + ')',
        '$dynamic_startup_define_duplicate_valid(' + returned + ',' + call + ',0)',
        '$call_task_valid(' + returned + ',ERROR_HANDLER_RESULT perrorcall_returned_' + state + ')', *common.public(returned)]
    if returning:
        values += [returned + '.USERCONSTANTS = [puserconstant_sibling]',
            'puserconstant_sibling.NAME = ' + text('StartupSibling43'), 'puserconstant_sibling.VALUE = PINT 819',
            'puserconstant_sibling.CLASS = PVSCALAR',
            '$dynamic_startup_define_duplicate_valid(' + returned + ',' + call + ',1)',
            '~$dynamic_startup_define_duplicate_valid(' + returned + ',' + call + ',2)',
            returned + '.STORE[n_name] = DEFINED pvalue_live_name', '$string_bytes(pvalue_live_name) = (' + text('handler-name') + ')',
            returned + '.STORE[n_candidate] = DEFINED (PINT 777)', returned + '.STORE[n_call] = DEFINED pvalue_live_call',
            '$string_bytes(pvalue_live_call) = (' + text('defined') + ')']
    else:
        values += [returned + '.USERCONSTANTS = eps']
    values += [returned + '.STORE[n_count] = DEFINED (PINT 1)', returned + '.STORE[n_result] = DEFINED (PINT 99)',
        '$source_constant_lookup(' + returned + ',' + text(name) + ') = (VALUE (PINT 8))',
        *common.step(pending, returned), pending + '.TODO = (DYNAMIC_CONSTANT_DUPLICATE ' + call + ' 0) :: ptask_' + state + '*',
        pending + '.EVENTS = ' + returned + '.EVENTS' + (' ++ [DIAGNOSTIC "Warning" $global_constant_duplicate_message(' + text(name) + ') ' + call + '.LINE]' if returning else ''),
        pending + '.USERCONSTANTS = ' + returned + '.USERCONSTANTS', *common.public(pending),
        *common.step(after, pending, 'PBOOL false'), after + '.TODO = ptask_' + state + '*',
        after + '.USERCONSTANTS = ' + returned + '.USERCONSTANTS', after + '.STORE[n_result] = DEFINED (PINT 99)',
        '$source_constant_lookup(' + after + ',' + text(name) + ') = (VALUE (PINT 8))']
    values += ['pconfigcall_special_' + state + ' = ' + call + '[.SENT = $named_slot_set(' + call + '.SENT,0,KNOWN (PSTRING ' + text('true') + '))]',
        '$dynamic_startup_define_duplicate_valid(' + warning + ',pconfigcall_special_' + state + ',0)',
        '~$error_call_valid(' + warning + ',perrorcall_' + state + '[.RESUME = DYNAMIC_CONSTANT_DUPLICATE pconfigcall_special_' + state + ' 0])']
    for field in ('.LEVEL = 8192', '.MESSAGE = ' + text('forged'), '.LINE = $(perrorcall_' + state + '.LINE + 1)',
            '.EVENT = DIAGNOSTIC "Notice" perrorcall_' + state + '.MESSAGE ' + call + '.LINE'):
        values += ['~$error_call_valid(' + warning + ',perrorcall_' + state + '[' + field + '])']
    return values


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')', 'S_initial.COMPLETION = BUDGET']
    if name == 'literal-startup-duplicates-keep-original-values':
        values += [*front('S', 'S_initial', 'PHP_INT_SIZE', 'PINT 801', 'PINT 8'),
            'S.USERCONSTANTS = eps', 'pconfigcall_S.SELECTION = eps',
            'pconfigcall_S.SENT = [NAMED_SENT (KNOWN pvalue_name_S),NAMED_SENT (KNOWN (PINT 801))]',
            *default('S_size_return', 'S', 'PHP_INT_SIZE', 'PINT 8'),
            *front('S_warning', 'S_size_return', 'E_WARNING', 'PINT 802', 'PINT 2'),
            'pconfigcall_S_warning.SENT = [NAMED_SENT (KNOWN pvalue_name_S_warning),NAMED_SENT (KNOWN (PINT 802)),NAMED_SENT (KNOWN (PBOOL false))]',
            *default('S_warning_return', 'S_warning', 'E_WARNING', 'PINT 2'),
            *front('S_infinity', 'S_warning_return', 'INF', 'PINT 803', 'PFLOAT 9218868437227405312'),
            'pconfigcall_S_infinity.SENT = [NAMED_SENT (KNOWN pvalue_name_S_infinity),NAMED_SENT (KNOWN (PINT 803)),NAMED_SENT (KNOWN (PBOOL false))]',
            *default('S_infinity_return', 'S_infinity', 'INF', 'PFLOAT 9218868437227405312'),
            'pconfigcall_other_builtin = pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,0,KNOWN (PSTRING ' + text('E_WARNING') + '))]',
            '$builtin_value_bytes(' + text('E_WARNING') + ') = (PINT 2)',
            '~$dynamic_startup_define_duplicate_valid(S,pconfigcall_other_builtin,0)',
            '~$dynamic_constant_duplicate_valid(S,pconfigcall_other_builtin,0)',
            '~$dynamic_startup_define_duplicate_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,0,KNOWN (PSTRING ' + text('true') + '))],0)',
            '~$dynamic_startup_define_duplicate_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,1,KNOWN (PINT 999))],0)',
            *refusals('S'), *budget('S')]
        call = 'pconfigcall_S_warning'
        for flag in ('PBOOL true', 'PNULL', 'PINT 0', 'PFLOAT 9221120237041090560', 'PSTRING ' + text('0')):
            values += ['~$dynamic_startup_define_duplicate_valid(S_warning,' + call + '[.SENT = $named_slot_set(' + call + '.SENT,2,KNOWN (' + flag + '))],0)']
    else:
        captured = name == 'captured-startup-name-before-returning-duplicate-effects'
        assert captured or name == 'strict-startup-duplicate-after-all-argument-effects'
        candidate = 'pvalue_candidate' if captured else 'PINT 831'
        values += [*front('S', 'S_initial', 'PHP_INT_SIZE', candidate, 'PINT 8'), 'S.USERCONSTANTS = eps',
            'pconfigcall_S.SENT = [NAMED_SENT (KNOWN pvalue_name_S),NAMED_SENT (KNOWN (' + candidate + ')),NAMED_SENT (KNOWN (PBOOL false))]',
            'pvalue_name_S = PSTRING_CARRIER (REQUEST_STRING n_name_string) ' + text('PHP_INT_SIZE'),
            'pconfigcall_S.SELECTION = (n_selection)', 'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
            '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            '$lookup(S.ENV,' + text('count') + ') = (n_count)', 'S.STORE[n_count] = DEFINED (PINT 0)',
            '$lookup(S.ENV,' + text('call') + ') = (n_call)', 'S.STORE[n_call] = DEFINED pvalue_current_call',
            '$string_bytes(pvalue_current_call) = (' + text('constant' if captured else 'defined') + ')',
            ('$config_strict(S,pconfigcall_S)' if not captured else '~$config_strict(S,pconfigcall_S)'),
            '$test_outputs(S.EVENTS) = ' + text('B|V|' if captured else 'B|V|N|')]
        if captured:
            values += ['pvalue_candidate = PSTRING_CARRIER (REQUEST_STRING n_candidate_string) preqbytes_candidate',
                'preqbytes_candidate = ' + text('outer-value43'), '$string_carrier_valid(S,pvalue_candidate)',
                '$lookup(S.ENV,' + text('name') + ') = (n_name)', 'S.STORE[n_name] = DEFINED pvalue_before_name',
                '$string_bytes(pvalue_before_name) = (' + text('value-name') + ')',
                '$lookup(S.ENV,' + text('candidate') + ') = (n_candidate)', 'S.STORE[n_candidate] = DEFINED (PINT 997)',
                'n_bad_string = |S.STRINGDATA|',
                'pvalue_bad_name = PSTRING_CARRIER (REQUEST_STRING n_bad_string) ' + text('PHP_INT_SIZE'),
                '~$string_carrier_valid(S,pvalue_bad_name)',
                '~$dynamic_startup_define_duplicate_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,0,KNOWN pvalue_bad_name)],0)',
                'pvalue_bad_candidate = PSTRING_CARRIER (REQUEST_STRING n_bad_string) preqbytes_candidate',
                '~$string_carrier_valid(S,pvalue_bad_candidate)',
                '~$dynamic_startup_define_duplicate_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,1,KNOWN pvalue_bad_candidate)],0)']
        values += [*handler('S', 'PHP_INT_SIZE', candidate, captured), *refusals('S'), *budget('S')]
    return values


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--case', action='append', default=[])
    args, remaining = parser.parse_known_args()
    if args.case:
        assert len(set(args.case)) == len(args.case) and set(args.case) <= sources.family.CASES.keys()
        sources.family.CASES = {name: sources.family.CASES[name] for name in args.case}
    sys.argv = [sys.argv[0], *remaining]
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
