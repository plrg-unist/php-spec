#!/usr/bin/env python3
"""Reached infinite-name reception, protected duplicates and strict NaN errors."""
import json
import os
from pathlib import Path

import define_scalar_false_flag_protocol as scalar
import define_nonfinite_name_sources as sources

driver, common, text, b64 = scalar.driver, scalar.common, scalar.text, scalar.b64
INF = 'PFLOAT 9218868437227405312'
NEG_INF = 'PFLOAT 18442240474082181120'
NAN = 'PFLOAT 9221120237041090560'

PREFIX = r"""
dec $test_infinite_call(pconfigcall, pvalue) : bool
def $test_infinite_call(pconfigcall, pvalue_raw) = true
  -- if $dynamic_scalar_define_call(pconfigcall)
  -- if $dynamic_scalar_define_values(pconfigcall) = ((pvalue_raw,pvalue))
def $test_infinite_call(pconfigcall, pvalue_raw) = false -- otherwise
dec $test_infinite_front(pstate, nat, pvalue) : bool
def $test_infinite_front(S, 0, pvalue_raw) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if $test_infinite_call(pconfigcall,pvalue_raw)
def $test_infinite_front(S, 1, pvalue_raw) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_call(S,pcallcontext) = (perrorcall)
  -- if perrorcall.RESUME = DYNAMIC_SCALAR_DEFINE_DUPLICATE pconfigcall pvalue_name z n_prefix
  -- if $test_infinite_call(pconfigcall,pvalue_raw)
def $test_infinite_front(S, 2, pvalue_raw) = true
  -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_SCALAR_DEFINE_DUPLICATE pconfigcall pvalue_name z n_prefix
  -- if $test_infinite_call(pconfigcall,pvalue_raw)
def $test_infinite_front(S, n_stage, pvalue_raw) = false -- otherwise
dec $test_infinite_seek(pstate, nat, pvalue, nat) : pstate
def $test_infinite_seek(S, n_stage, pvalue_raw, 0) = S
def $test_infinite_seek(S, n_stage, pvalue_raw, n) = S
  -- if $(n > 0)
  -- if $test_infinite_front(S,n_stage,pvalue_raw) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_infinite_seek(S, n_stage, pvalue_raw, n) = $test_infinite_seek($drive_steps($test_running(S),1),n_stage,pvalue_raw,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_infinite_front(S,n_stage,pvalue_raw)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def reach(state, start, raw, stage=0):
    return [state + '_found = $test_infinite_seek(' + start + ',' + str(stage) + ',' + raw + ',3000)',
        state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_infinite_front(' + state + ',' + str(stage) + ',' + raw + ')']


def front(state, start, raw, candidate, omitted=False):
    call = 'pconfigcall_' + state
    return [*reach(state, start, raw), state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
        call + '.SENT = [NAMED_SENT (KNOWN (' + raw + ')),NAMED_SENT (KNOWN (' + candidate + '))' + ('' if omitted else ',NAMED_SENT (KNOWN (PBOOL false))') + ']',
        '$dynamic_scalar_define_values(' + call + ') = ((' + raw + ',' + candidate + '))',
        '$dynamic_scalar_define_call(' + call + ')', '$dynamic_scalar_define_valid(' + state + ',' + call + ')',
        '$config_invoke_valid(' + state + ',' + call + ')', *common.public(state)]


def known_inf(state):
    return ['$source_constant_lookup(' + state + ',' + text('INF') + ') = (VALUE (' + INF + '))',
        '$user_constant_at(' + state + '.USERCONSTANTS,' + text('INF') + ') = eps']


def default(after, before):
    call, warning, received = 'pconfigcall_' + before, after + '_warning', 'pvalue_received_' + before
    return [*scalar.converted(before, INF, 'INF'), '~$error_handler_eligible(' + before + ',2)',
        *common.step(warning, before),
        warning + '.TODO = (DYNAMIC_SCALAR_DEFINE_DUPLICATE ' + call + ' ' + received + ' 14 0) :: ptask_' + before + '*',
        '$dynamic_scalar_define_received(' + warning + ',' + call + ',' + received + ',14)',
        '~$dynamic_scalar_define_received(' + warning + ',' + call + ',' + received + ',1)',
        '$dynamic_scalar_define_received(' + warning + ',' + call + ',' + received + ',-1)',
        '$dynamic_scalar_define_duplicate_valid(' + warning + ',' + call + ',' + received + ',14,0)',
        warning + '.EVENTS = ' + before + '.EVENTS ++ [DIAGNOSTIC "Warning" $global_constant_duplicate_message(' + text('INF') + ') ' + call + '.LINE]',
        warning + '.STRINGDATA = ' + before + '_converted.STRINGDATA',
        *scalar.unchanged(warning, before, 'STORE ENV USERCONSTANTS ARRAYS OBJECTS SELECTEDCALLS SOURCES POOLS FILES'),
        *known_inf(warning), *common.public(warning), *common.step(after, warning, 'PBOOL false'),
        after + '.TODO = ptask_' + before + '*', after + '.USERCONSTANTS = eps', *known_inf(after)]


def refusals(state, received, call):
    values = ['~$dynamic_scalar_define_duplicate_valid(' + state + ',' + call + ',' + received + ',14,$(|' + state + '.USERCONSTANTS| + 1))',
        '~$dynamic_scalar_define_received(' + state + ',' + call + ',' + received + ',-2)',
        '~$dynamic_scalar_define_received(' + state + ',' + call + ',' + received + ',9223372036854775808)',
        '~$dynamic_scalar_define_received(' + state + ',' + call + ',PSTRING ' + text('NAN') + ',14)',
        '~$dynamic_scalar_define_received(' + state + ',' + call + ',PSTRING ' + text('inf') + ',14)',
        'pvalue_bad_received_' + state + ' = PSTRING_CARRIER (REQUEST_STRING (|' + state + '.STRINGDATA|)) ' + text('INF'),
        '~$dynamic_scalar_define_received(' + state + ',' + call + ',pvalue_bad_received_' + state + ',14)']
    for field in ('.SITE = PORIGIN 0 eps', '.LINE = $(' + call + '.LINE + 1)', '.SELECTION = (|' + state + '.SELECTEDCALLS|)', '.OWNER = (0)', '.KIND = INTRINSIC_CONSTANT'):
        values += ['~$dynamic_scalar_define_valid(' + state + ',' + call + '[' + field + '])']
    return values


def handler(state, candidate):
    call, received = 'pconfigcall_' + state, 'pvalue_received_' + state
    warning, entered, returned, pending, after = [state + suffix for suffix in ('_warning', '_entered', '_returned', '_pending', '_after')]
    values = [*scalar.converted(state, INF, 'INF'), *common.step(warning, state),
        warning + '.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_' + state + '*',
        'perrorcall.RESUME = DYNAMIC_SCALAR_DEFINE_DUPLICATE ' + call + ' ' + received + ' 14 0',
        'perrorcall.LEVEL = 2', 'perrorcall.LINE = ' + call + '.LINE', 'perrorcall.SITE = ' + call + '.SITE',
        'perrorcall.MESSAGE = $global_constant_duplicate_message(' + text('INF') + ')',
        'perrorcall.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE ' + call + '.LINE',
        '$error_call_valid(' + warning + ',perrorcall)', warning + '.EVENTS = ' + state + '.EVENTS',
        warning + '.STRINGDATA = ' + state + '_converted.STRINGDATA', warning + '.USERCONSTANTS = eps',
        *reach(entered, warning, INF, 1), entered + '.CURRENT = (pcallcontext)',
        '$error_context_valid(' + entered + ',pcallcontext)',
        'pconfigcall_api = ' + call + '[.SENT = $named_slot_set(' + call + '.SENT,0,KNOWN ' + received + ')]',
        '$error_context_trigger(' + entered + ',pcallcontext) = (pconfigcall_api)',
        '$error_handler_trace_values(' + entered + ',pcallcontext,pconfigcall_api) = [' + received + ',' + candidate + ',PBOOL false]',
        entered + '.USERCONSTANTS = eps', *common.public(entered),
        *reach(returned, entered, INF, 2),
        returned + '.TODO = (ERROR_HANDLER_RESULT perrorcall_returned) :: ptask_' + state + '*',
        'perrorcall_returned.RESUME = perrorcall.RESUME', returned + '.RESULT = KNOWN (PBOOL false)',
        '$call_task_valid(' + returned + ',ERROR_HANDLER_RESULT perrorcall_returned)',
        returned + '.USERCONSTANTS = [puserconstant_sibling]', 'puserconstant_sibling.NAME = ' + text('InfiniteSibling45'),
        'puserconstant_sibling.VALUE = PINT 929', 'puserconstant_sibling.CLASS = PVSCALAR',
        '$dynamic_scalar_define_duplicate_valid(' + returned + ',' + call + ',' + received + ',14,0)',
        '~$dynamic_scalar_define_duplicate_valid(' + returned + ',' + call + ',' + received + ',1,1)',
        '$dynamic_scalar_define_duplicate_valid(' + returned + ',' + call + ',' + received + ',-1,1)',
        '~$dynamic_scalar_define_duplicate_valid(' + returned + ',' + call + ',' + received + ',14,2)',
        returned + '.STORE[n_result] = DEFINED (PINT 99)', returned + '.STORE[n_count] = DEFINED (PINT 1)',
        returned + '.STORE[n_candidate] = DEFINED (PINT 991)', returned + '.STORE[n_flag] = DEFINED (PBOOL true)',
        *known_inf(returned), *common.step(pending, returned),
        pending + '.TODO = perrorcall.RESUME :: ptask_' + state + '*',
        pending + '.EVENTS = ' + returned + '.EVENTS ++ [DIAGNOSTIC "Warning" perrorcall.MESSAGE ' + call + '.LINE]',
        *common.step(after, pending, 'PBOOL false'), after + '.TODO = ptask_' + state + '*',
        *scalar.unchanged(after, returned, 'STORE ENV USERCONSTANTS SELECTEDCALLS STRINGDATA'), *known_inf(after),
        after + '.STORE[n_result] = DEFINED (PINT 99)', *scalar.budget(returned)]
    for field in ('.LEVEL = 8192', '.MESSAGE = ' + text('changed'), '.LINE = $(perrorcall.LINE + 1)', '.EVENT = DIAGNOSTIC "Notice" perrorcall.MESSAGE perrorcall.LINE'):
        values += ['~$error_call_valid(' + warning + ',perrorcall[' + field + '])']
    return values


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')', 'S_initial.COMPLETION = BUDGET']
    if name == 'infinite-names-startup-duplicates-and-negative-fresh-key':
        values += [*front('S', 'S_initial', INF, 'PINT 901', True), 'S.USERCONSTANTS = eps',
            *default('S_first', 'S'), *front('S_second', 'S_first', INF, 'PINT 907'),
            *default('S_second_return', 'S_second'), *front('S_negative', 'S_second_return', NEG_INF, 'PINT 911'),
            *scalar.publish('S_fresh', 'S_negative', NEG_INF, 'PINT 911', '-INF'),
            'S_fresh.EVENTS = S_negative.EVENTS', *known_inf('S_fresh'),
            *refusals('S_first_warning', 'pvalue_received_S', 'pconfigcall_S'),
            '$dynamic_scalar_name_at(' + INF + ',1) = (' + text('I') + ')',
            '$dynamic_scalar_name_at(' + INF + ',14) = (' + text('INF') + ')',
            '$dynamic_scalar_name_at(' + INF + ',-1) = (' + text('INF') + ')',
            '$dynamic_define_known(S,pconfigcall_S.SITE,0) = (' + INF + ')',
            '$dynamic_define_known(S_negative,pconfigcall_S_negative.SITE,0) = (' + NEG_INF + ')',
            'pconfigcall_nan = pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,0,KNOWN (' + NAN + '))]',
            '$dynamic_scalar_define_call(pconfigcall_nan)', '~$dynamic_scalar_define_valid(S,pconfigcall_nan)',
            '~$dynamic_scalar_define_received(S,pconfigcall_nan,PSTRING ' + text('NAN') + ',14)',
            'pconfigcall_fresh_negative = pconfigcall_S_negative[.SENT = $named_slot_set(pconfigcall_S_negative.SENT,0,KNOWN (' + INF + '))]',
            '$dynamic_scalar_define_call(pconfigcall_fresh_negative)', '~$dynamic_scalar_define_valid(S_negative,pconfigcall_fresh_negative)',
            *scalar.budget('S'), *scalar.budget('S_first_warning')]
        for flag in ('PINT 0', 'PSTRING ' + text('0'), 'PFLOAT 0', 'PNULL', 'PBOOL true'):
            values += ['~$dynamic_scalar_define_call(pconfigcall_S[.SENT = pconfigcall_S.SENT ++ [NAMED_SENT (KNOWN (' + flag + '))]])']
    elif name == 'captured-infinite-name-before-request-value-and-live-effects':
        values += [*front('S', 'S_initial', INF, 'pvalue_candidate'), 'S.USERCONSTANTS = eps',
            'pvalue_candidate = PSTRING_CARRIER (REQUEST_STRING n_string) preqbytes_candidate',
            'preqbytes_candidate = ' + text('outer-candidate45'), '$string_carrier_valid(S,pvalue_candidate)',
            '$test_outputs(S.EVENTS) = ' + text('B|V|N|'), 'pconfigcall_S.SELECTION = (n_selection)',
            'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
            '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            '$lookup(S.ENV,' + text('count') + ') = (n_count)', 'S.STORE[n_count] = DEFINED (PINT 0)',
            '$lookup(S.ENV,' + text('candidate') + ') = (n_candidate)', 'S.STORE[n_candidate] = DEFINED (PINT 997)',
            '$lookup(S.ENV,' + text('flag') + ') = (n_flag)', 'S.STORE[n_flag] = DEFINED (PBOOL true)',
            *handler('S', 'pvalue_candidate'),
            'pvalue_bad_candidate = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) preqbytes_candidate',
            '~$dynamic_scalar_define_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,1,KNOWN pvalue_bad_candidate)])',
            *scalar.budget('S')]
    else:
        assert name == 'strict-nan-name-rejected-before-string-conversion-after-effects'
        values += [*front('S', 'S_initial', NAN, 'PINT 947'), 'pvalue_flag_S = PBOOL false', 'S.USERCONSTANTS = eps',
            '$test_outputs(S.EVENTS) = ' + text('B|V|N|'), '$config_strict(S,pconfigcall_S)',
            '$config_conversion(S,pconfigcall_S,' + NAN + ') = TYPEREJECT',
            '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            '$lookup(S.ENV,' + text('flag') + ') = (n_flag)', 'S.STORE[n_flag] = DEFINED (PBOOL true)',
            *scalar.strict_error('S_error', 'S', NAN, 'PINT 947', 'float'),
            'S_error.STORE[n_result] = DEFINED (PINT 99)',
            '~$dynamic_scalar_define_received(S,pconfigcall_S,PSTRING ' + text('NAN') + ',14)', *scalar.budget('S')]
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
