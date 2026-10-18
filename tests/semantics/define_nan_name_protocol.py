#!/usr/bin/env python3
"""Reached NaN name rendering preserves two diagnostic phases and raw authority."""
import json
import os
from pathlib import Path

import define_scalar_false_flag_protocol as scalar
import define_nan_name_sources as sources

driver, common, text, b64 = scalar.driver, scalar.common, scalar.text, scalar.b64
NAN = 'PFLOAT 9221120237041090560'

PREFIX = r"""
dec $test_nan_name_front(pstate, nat) : bool
def $test_nan_name_front(S, 0) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if $dynamic_nan_define_name_call(pconfigcall)
def $test_nan_name_front(S, 1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_call(S,pcallcontext) = (perrorcall)
  -- if perrorcall.RESUME = DYNAMIC_NAN_DEFINE_NAME_RESULT pconfigcall pvalue z
def $test_nan_name_front(S, 2) = true
  -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_NAN_DEFINE_NAME_RESULT pconfigcall pvalue z
def $test_nan_name_front(S, 4) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_call(S,pcallcontext) = (perrorcall)
  -- if perrorcall.RESUME = DYNAMIC_NAN_DEFINE_NAME_DUPLICATE pconfigcall pvalue z n_prefix
def $test_nan_name_front(S, 5) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_NAN_DEFINE_NAME_DUPLICATE pconfigcall pvalue z n_prefix
def $test_nan_name_front(S, n_stage) = false -- otherwise
dec $test_nan_name_seek(pstate, nat, nat) : pstate
def $test_nan_name_seek(S, n_stage, 0) = S
def $test_nan_name_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_nan_name_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_nan_name_seek(S, n_stage, n) = $test_nan_name_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_nan_name_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def reach(state, start, stage):
    return [state + '_found = $test_nan_name_seek(' + start + ',' + str(stage) + ',3000)',
        state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]', '$test_nan_name_front(' + state + ',' + str(stage) + ')']


def front(state, start, candidate, omitted=False):
    call = 'pconfigcall_' + state
    return [*reach(state, start, 0), state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
        call + '.SENT = [NAMED_SENT (KNOWN (' + NAN + ')),NAMED_SENT (KNOWN (' + candidate + '))' + ('' if omitted else ',NAMED_SENT (KNOWN (PBOOL false))') + ']',
        '$config_invoke_valid(' + state + ',' + call + ')', '$dynamic_scalar_define_valid(' + state + ',' + call + ')',
        '$dynamic_nan_define_name_valid(' + state + ',' + call + ')', *common.public(state)]


def builtin(state):
    return ['$source_constant_lookup(' + state + ',' + text('NAN') + ') = (VALUE (' + NAN + '))',
        '$user_constant_at(' + state + '.USERCONSTANTS,' + text('NAN') + ') = eps']


def render(state):
    return ['$dynamic_nan_define_name_entry(' + state + ',pconfigcall_' + state + ')',
        '$precision_value(' + state + ') = 14',
        state + '_rendered = $string_request(' + state + ',' + text('NAN') + ')',
        state + '_rendered.RESULT = KNOWN pvalue_received',
        'pvalue_received = PSTRING_CARRIER (REQUEST_STRING n_string) ' + text('NAN'),
        'n_string = |' + state + '.STRINGDATA|', '$string_carrier_valid(' + state + '_rendered,pvalue_received)']


def refusals(state, call):
    values = ['~$dynamic_scalar_define_received(' + state + ',' + call + ',pvalue_received,14)',
        '~$dynamic_scalar_define_duplicate_valid(' + state + ',' + call + ',pvalue_received,14,0)',
        '~$call_task_valid(' + state + ',DYNAMIC_SCALAR_DEFINE_DUPLICATE ' + call + ' pvalue_received 14 0)',
        '~$dynamic_nan_define_name_received(' + state + ',' + call + ',PSTRING ' + text('NAN') + ',14)',
        'pvalue_bad_received = PSTRING_CARRIER (REQUEST_STRING (|' + state + '.STRINGDATA|)) ' + text('NAN'),
        '~$dynamic_nan_define_name_received(' + state + ',' + call + ',pvalue_bad_received,14)',
        '~$dynamic_nan_define_name_duplicate_valid(' + state + ',' + call + ',pvalue_received,14,$(|' + state + '.USERCONSTANTS| + 1))']
    for precision in ('1', '2', '-2', '9223372036854775808'):
        values += ['~$dynamic_nan_define_name_received(' + state + ',' + call + ',pvalue_received,' + precision + ')']
    for precision in ('3', '-1'):
        values += ['$dynamic_nan_define_name_received(' + state + ',' + call + ',pvalue_received,' + precision + ')']
    for field in ('.SITE = PORIGIN 0 eps', '.LINE = $(' + call + '.LINE + 1)', '.SELECTION = (|' + state + '.SELECTEDCALLS|)', '.OWNER = (0)', '.KIND = INTRINSIC_CONSTANT'):
        values += ['~$dynamic_nan_define_name_valid(' + state + ',' + call + '[' + field + '])']
    return values


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')', 'S_initial.COMPLETION = BUDGET']
    if name == 'literal-nan-name-conversion-warning-then-startup-duplicate':
        values += [*front('S', 'S_initial', 'PINT 953', True), 'S.USERCONSTANTS = eps', '~$error_handler_eligible(S,2)',
            *render('S'), *common.step('S_conversion', 'S'),
            'S_conversion.TODO = (DYNAMIC_NAN_DEFINE_NAME_RESULT pconfigcall_S pvalue_received 14) :: ptask_S*',
            '$call_task_valid(S_conversion,DYNAMIC_NAN_DEFINE_NAME_RESULT pconfigcall_S pvalue_received 14)',
            'S_conversion.EVENTS = S.EVENTS ++ [DIAGNOSTIC "Warning" $dynamic_nan_define_name_message() pconfigcall_S.LINE]',
            'S_conversion.STRINGDATA = S_rendered.STRINGDATA',
            *scalar.unchanged('S_conversion', 'S', 'STORE ENV USERCONSTANTS ARRAYS OBJECTS SELECTEDCALLS SOURCES POOLS FILES'),
            *builtin('S_conversion'), *common.public('S_conversion'), *common.step('S_duplicate', 'S_conversion'),
            'S_duplicate.TODO = (DYNAMIC_NAN_DEFINE_NAME_DUPLICATE pconfigcall_S pvalue_received 14 0) :: ptask_S*',
            '$call_task_valid(S_duplicate,DYNAMIC_NAN_DEFINE_NAME_DUPLICATE pconfigcall_S pvalue_received 14 0)',
            'S_duplicate.EVENTS = S_conversion.EVENTS ++ [DIAGNOSTIC "Warning" $global_constant_duplicate_message(' + text('NAN') + ') pconfigcall_S.LINE]',
            *scalar.unchanged('S_duplicate', 'S_conversion', 'STORE ENV USERCONSTANTS STRINGDATA ARRAYS OBJECTS SELECTEDCALLS'),
            *common.step('S_return', 'S_duplicate', 'PBOOL false'), 'S_return.TODO = ptask_S*', 'S_return.USERCONSTANTS = eps',
            *builtin('S_return'), *refusals('S_conversion', 'pconfigcall_S'),
            '$dynamic_define_known(S,pconfigcall_S.SITE,0) = (' + NAN + ')',
            'pconfigcall_other_nan = pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,0,KNOWN (PFLOAT 18444492273895866368))]',
            '$dynamic_nan_define_name_call(pconfigcall_other_nan)', '~$dynamic_nan_define_name_valid(S,pconfigcall_other_nan)',
            *scalar.budget('S'), *scalar.budget('S_conversion')]
        for flag in ('PBOOL true', 'PNULL', 'PINT 0', 'PSTRING ' + text('0')):
            values += ['~$dynamic_nan_define_name_call(pconfigcall_S[.SENT = pconfigcall_S.SENT ++ [NAMED_SENT (KNOWN (' + flag + '))]])']
    elif name == 'captured-nan-name-precision-change-before-second-warning-throw':
        values += [*front('S', 'S_initial', 'pvalue_candidate'), 'S.USERCONSTANTS = eps',
            'pvalue_candidate = PSTRING_CARRIER (REQUEST_STRING n_candidate_string) preqbytes_candidate',
            'preqbytes_candidate = ' + text('outer-value46'), '$string_carrier_valid(S,pvalue_candidate)',
            '$test_outputs(S.EVENTS) = ' + text('B|V|N|'),
            '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            '$lookup(S.ENV,' + text('count') + ') = (n_count)', 'S.STORE[n_count] = DEFINED (PINT 0)',
            '$lookup(S.ENV,' + text('flag') + ') = (n_flag)', 'S.STORE[n_flag] = DEFINED (PBOOL true)',
            *render('S'), *common.step('S_warning', 'S'),
            'S_warning.TODO = (ERROR_HANDLER_INVOKE perrorcall_first) :: ptask_S*',
            'perrorcall_first.RESUME = DYNAMIC_NAN_DEFINE_NAME_RESULT pconfigcall_S pvalue_received 14',
            '$error_call_valid(S_warning,perrorcall_first)', 'S_warning.EVENTS = S.EVENTS',
            'S_warning.STRINGDATA = S_rendered.STRINGDATA',
            *reach('S_entered', 'S_warning', 1), 'S_entered.CURRENT = (pcallcontext_first)',
            '$error_context_valid(S_entered,pcallcontext_first)', '$error_context_trigger(S_entered,pcallcontext_first) = (pconfigcall_S)',
            '$error_handler_trace_values(S_entered,pcallcontext_first,pconfigcall_S) = [' + NAN + ',pvalue_candidate,PBOOL false]',
            *reach('S_first_return', 'S_entered', 2),
            'S_first_return.TODO = (ERROR_HANDLER_RESULT perrorcall_returned) :: ptask_S*',
            'perrorcall_returned.RESUME = perrorcall_first.RESUME', 'S_first_return.RESULT = KNOWN (PBOOL true)',
            '$precision_value(S_first_return) = 1', '~$dynamic_nan_define_name_entry(S_first_return,pconfigcall_S)',
            '$dynamic_nan_define_name_received(S_first_return,pconfigcall_S,pvalue_received,14)',
            'S_first_return.STORE[n_count] = DEFINED (PINT 1)', 'S_first_return.STORE[n_result] = DEFINED (PINT 99)',
            'S_first_return.USERCONSTANTS = [puserconstant_sibling]', 'puserconstant_sibling.NAME = ' + text('NanNameSibling46'),
            'puserconstant_sibling.VALUE = PINT 971', 'puserconstant_sibling.CLASS = PVSCALAR',
            *common.step('S_received', 'S_first_return'),
            'S_received.TODO = (DYNAMIC_NAN_DEFINE_NAME_RESULT pconfigcall_S pvalue_received 14) :: ptask_S*',
            'S_received.EVENTS = S_first_return.EVENTS',
            *common.step('S_second_warning', 'S_received'),
            'S_second_warning.TODO = (ERROR_HANDLER_INVOKE perrorcall_second) :: ptask_S*',
            'perrorcall_second.RESUME = DYNAMIC_NAN_DEFINE_NAME_DUPLICATE pconfigcall_S pvalue_received 14 1',
            'perrorcall_second.MESSAGE = $global_constant_duplicate_message(' + text('NAN') + ')',
            '$error_call_valid(S_second_warning,perrorcall_second)',
            *reach('S_second_entered', 'S_second_warning', 4), 'S_second_entered.CURRENT = (pcallcontext_second)',
            '$error_context_valid(S_second_entered,pcallcontext_second)',
            'pconfigcall_api = pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,0,KNOWN pvalue_received)]',
            '$error_context_trigger(S_second_entered,pcallcontext_second) = (pconfigcall_api)',
            '$error_handler_trace_values(S_second_entered,pcallcontext_second,pconfigcall_api) = [pvalue_received,pvalue_candidate,PBOOL false]',
            *reach('S_thrown', 'S_second_entered', 5),
            'S_thrown.TODO = (THROW_SEARCH n_throw) :: (ERROR_HANDLER_RESULT perrorcall_thrown) :: ptask_S*',
            'perrorcall_thrown.RESUME = perrorcall_second.RESUME', '$error_call_valid(S_thrown,perrorcall_thrown)',
            'S_thrown.OBJECTS[n_throw] = THROWABLE pthrowable', 'pthrowable.KIND = "Exception"',
            '$throwable_field(S_thrown,n_throw,"previous") = PNULL',
            '$lookup(S_thrown.ENV,' + text('pending') + ') = (n_pending)', 'S_thrown.STORE[n_pending] = DEFINED (POBJECT n_throw)',
            'S_thrown.STORE[n_count] = DEFINED (PINT 2)', 'S_thrown.STORE[n_result] = DEFINED (PINT 99)',
            '$throwable_field(S_thrown,n_throw,"trace") = PARRAY n_trace',
            'S_thrown.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_handler)),ENTRY (KINT 1) (DIRECT (PARRAY n_api)),ENTRY (KINT 2) (DIRECT (PARRAY n_caller))]',
            '$trace_array_field(S_thrown,n_api,' + text('function') + ') = PSTRING ' + text('define'),
            '$trace_array_field(S_thrown,n_api,' + text('args') + ') = PARRAY n_args',
            'S_thrown.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_received),ENTRY (KINT 1) (DIRECT pvalue_candidate),ENTRY (KINT 2) (DIRECT (PBOOL false))]',
            *builtin('S_thrown'), '$precision_value(S_thrown) = 1', *common.public('S_thrown'),
            'S_discard = S_thrown[.TODO = (THROW_SEARCH n_throw) :: ptask_S*]',
            'S_expected = $error_handler_restore($identity_read_discard(S_discard,perrorcall_thrown.RESUME),perrorcall_thrown.CALLBACK)',
            *common.step('S_after', 'S_thrown'), 'S_after = S_expected',
            'S_after.USERCONSTANTS = [puserconstant_sibling]', 'S_after.STORE[n_result] = DEFINED (PINT 99)',
            'S_after.STRINGDATA = S_expected.STRINGDATA', *builtin('S_after'),
            *refusals('S_thrown', 'pconfigcall_S'), *scalar.budget('S_warning'), *scalar.budget('S_thrown')]
        for call, state in [('perrorcall_first', 'S_warning'), ('perrorcall_second', 'S_second_warning')]:
            for field in ('.LEVEL = 8192', '.MESSAGE = ' + text('changed'), '.LINE = $(' + call + '.LINE + 1)', '.EVENT = DIAGNOSTIC "Notice" ' + call + '.MESSAGE ' + call + '.LINE'):
                values += ['~$error_call_valid(' + state + ',' + call + '[' + field + '])']
        values += ['pvalue_bad_candidate = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) preqbytes_candidate',
            '~$dynamic_nan_define_name_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,1,KNOWN pvalue_bad_candidate)])']
    else:
        assert name == 'strict-nan-name-error-before-conversion-warning'
        values += [*front('S', 'S_initial', 'PINT 977'), 'pvalue_flag_S = PBOOL false',
            '$config_strict(S,pconfigcall_S)', '~$dynamic_nan_define_name_entry(S,pconfigcall_S)',
            '$test_outputs(S.EVENTS) = ' + text('B|V|N|'),
            '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            *scalar.strict_error('S_error', 'S', NAN, 'PINT 977', 'float'),
            'S_error.STORE[n_result] = DEFINED (PINT 99)',
            'pvalue_received = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ' + text('NAN'),
            '~$dynamic_nan_define_name_received(S,pconfigcall_S,pvalue_received,14)', *scalar.budget('S')]
    return values


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__),
        str(Path(scalar.__file__).relative_to(driver.ROOT)): sources.family.sha(scalar.__file__)})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
