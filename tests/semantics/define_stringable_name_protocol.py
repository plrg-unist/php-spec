#!/usr/bin/env python3
"""Reached define-name casts precede fresh registration and callback-created duplicates."""
import argparse
import json
import os
from pathlib import Path
import sys

import global_constant_scalar_name_protocol as driver
import define_stringable_name_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64

PREFIX = r"""
dec $test_define_string_front(pstate, nat) : bool
def $test_define_string_front(S, 0) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if $dynamic_define_string_call(pconfigcall)
def $test_define_string_front(S, 1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $context_target(pcallcontext) = METHOD_TARGET n_object porigin_method
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (STRINGIFY_RESULT n_object porigin_child z_call) :: (CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) :: ptask_tail*
  -- if $dynamic_define_string_call(pconfigcall)
def $test_define_string_front(S, 2) = true
  -- if S.TODO = (CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) :: ptask_tail*
  -- if $dynamic_define_string_call(pconfigcall)
def $test_define_string_front(S, 3) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_call(S,pcallcontext) = (perrorcall)
  -- if perrorcall.RESUME = DYNAMIC_CONSTANT_DUPLICATE pconfigcall n_prefix
  -- if pconfigcall.KIND = INTRINSIC_DEFINE
def $test_define_string_front(S, 4) = true
  -- if S.TODO = (THROW_SEARCH n_throw) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_CONSTANT_DUPLICATE pconfigcall n_prefix
  -- if pconfigcall.KIND = INTRINSIC_DEFINE
def $test_define_string_front(S, n_stage) = false -- otherwise
dec $test_define_string_seek(pstate, nat, nat) : pstate
def $test_define_string_seek(S, n_stage, 0) = S
def $test_define_string_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_define_string_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_define_string_seek(S, n_stage, n) = $test_define_string_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_define_string_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def reach(state, start, stage):
    return [state + '_found = $test_define_string_seek(' + start + ',' + str(stage) + ',3000)',
        state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_define_string_front(' + state + ',' + str(stage) + ')']


def unchanged(after, before, fields):
    return [after + '.' + field + ' = ' + before + '.' + field for field in fields.split()]


def front(state, start, three):
    call, obj = 'pconfigcall_' + state, 'n_object_' + state
    tail = ',NAMED_SENT (KNOWN (PBOOL false))' if three else ''
    return [*reach(state, start, 0),
        state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
        call + '.SENT = [NAMED_SENT (KNOWN (POBJECT ' + obj + ')),NAMED_SENT (KNOWN pvalue_candidate_' + state + ')' + tail + ']',
        call + '.KIND = INTRINSIC_DEFINE', call + '.OWNER = eps', call + '.PACKS = eps', '~' + call + '.NAMED',
        '$dynamic_define_string_valid(' + state + ',' + call + ')', '$config_invoke_valid(' + state + ',' + call + ')',
        '~$config_string_kind(INTRINSIC_DEFINE)',
        '$config_string_source(' + state + ',' + call + ') = ((porigin_child_' + state + ',z_child_' + state + '))',
        '$config_string_object(' + call + ') = (' + obj + ')', *common.public(state)]


def weak(state, name):
    call, obj = 'pconfigcall_' + state, 'n_object_' + state
    child, line = 'porigin_child_' + state, 'z_child_' + state
    launch, entered, returned, ready = [state + suffix for suffix in ('_launch','_entered','_returned','_ready')]
    values = ['~$config_strict(' + state + ',' + call + ')',
        '$config_string_site_valid(' + state + ',' + call + ',' + obj + ',' + child + ',' + line + ',' + call + '.LINE)',
        '$config_string_launch(' + state + ',' + call + ')',
        '$config_string_launch(' + state + '[.FILEINCLUDEPATH = (eps)],' + call + ')',
        *common.step(launch,state),
        launch + '.TODO = (CALL_ARGS (METHOD_TARGET ' + obj + ' porigin_method_' + state + ') eps 0 eps (' + child + ') ' + call + '.LINE) :: (STRINGIFY_RESULT ' + obj + ' ' + child + ' ' + call + '.LINE) :: (CONFIG_STRING_RESULT ' + call + ' ' + obj + ' ' + child + ' ' + line + ' ' + call + '.LINE) :: ptask_' + state + '*',
        *reach(entered,launch,1), entered + '.CURRENT = (pcallcontext_' + state + ')',
        '$config_string_trace_context(' + entered + ',pcallcontext_' + state + ')',
        '$config_string_site_valid(' + entered + ',' + call + ',' + obj + ',' + child + ',' + line + ',' + call + '.LINE)',
        *common.public(entered), *reach(returned,entered,2),
        returned + '.TODO = (CONFIG_STRING_RESULT ' + call + ' ' + obj + ' ' + child + ' ' + line + ' ' + call + '.LINE) :: ptask_' + state + '*',
        returned + '.RESULT = KNOWN pvalue_string_' + state,
        '$string_bytes(pvalue_string_' + state + ') = (' + text(name) + ')',
        '$string_carrier_valid(' + returned + ',pvalue_string_' + state + ')',
        '$config_string_site_valid(' + returned + ',' + call + ',' + obj + ',' + child + ',' + line + ',' + call + '.LINE)',
        *common.step(ready,returned),
        'pconfigcall_converted_' + state + ' = ' + call + '[.SENT = $named_slot_set(' + call + '.SENT,0,KNOWN pvalue_string_' + state + ')]',
        ready + '.TODO = (CONFIG_INVOKE pconfigcall_converted_' + state + ') :: ptask_' + state + '*',
        ready + '.ORIGIN = (' + call + '.SITE)', ready + '.RESULT = KNOWN PNULL', ready + '.BASE = BASE_VALUE (KNOWN PNULL)',
        '$config_invoke_valid(' + ready + ',pconfigcall_converted_' + state + ')',
        '~$dynamic_define_string_call(pconfigcall_converted_' + state + ')',
        '~$config_string_launch(' + ready + ',pconfigcall_converted_' + state + ')',
        *unchanged(ready,returned,'STORE ENV ARRAYS OBJECTS OBJECTPROPS USERCONSTANTS STRINGDATA EVENTS SELECTEDCALLS AUTOLOAD CLASSNAMES CLASSCONSTANTCACHE'),
        *common.public(ready)]
    return values


def refusals(state):
    call, obj = 'pconfigcall_' + state, 'n_object_' + state
    child, line = 'porigin_child_' + state, 'z_child_' + state
    values = []
    for field in ('.SITE = PORIGIN 0 eps', '.LINE = $(' + call + '.LINE + 1)', '.INDEX = 0', '.SELECTION = (|' + state + '.SELECTEDCALLS|)'):
        values += ['~$dynamic_define_string_valid(' + state + ',' + call + '[' + field + '])']
    for field in ('.OWNER = (0)', '.NAMED = true', '.KIND = INTRINSIC_DEFINED', '.SENT = eps',
            '.SENT = ' + call + '.SENT ++ [NAMED_SENT (KNOWN PNULL)]',
            '.SENT = $named_slot_set(' + call + '.SENT,1,KNOWN (PARRAY 0))'):
        bad = call + '[' + field + ']'
        values += ['~$dynamic_define_string_call(' + bad + ')',
            '~$config_string_site_valid(' + state + ',' + bad + ',' + obj + ',' + child + ',' + line + ',' + call + '.LINE)',
            '~$config_string_launch(' + state + '[.FILEINCLUDEPATH = (eps)],' + bad + ')']
    values += ['~$config_string_site_valid(' + state + ',' + call + ',' + obj + ',' + child + ',$(' + line + ' + 1),' + call + '.LINE)',
        '~$config_string_site_valid(' + state + ',' + call + ',' + obj + ',PORIGIN 0 eps,' + line + ',' + call + '.LINE)',
        'pconfigcall_dead_' + state + ' = ' + call + '[.SENT = $named_slot_set(' + call + '.SENT,0,KNOWN (POBJECT (|' + state + '.OBJECTS|)))]',
        '$dynamic_define_string_call(pconfigcall_dead_' + state + ')',
        '~$dynamic_define_string_valid(' + state + ',pconfigcall_dead_' + state + ')']
    return values


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)', state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)', state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def duplicate(before, name):
    call = 'pconfigcall_converted_' + before
    ready, warning, done = [before + suffix for suffix in ('_ready','_warning','_done')]
    return ['$dynamic_constant_duplicate_valid(' + ready + ',' + call + ',1)',
        '~$error_handler_eligible(' + ready + ',2)', *common.step(warning,ready),
        warning + '.TODO = (DYNAMIC_CONSTANT_DUPLICATE ' + call + ' 1) :: ptask_' + before + '*',
        warning + '.EVENTS = ' + ready + '.EVENTS ++ [DIAGNOSTIC "Warning" $global_constant_duplicate_message(' + text(name) + ') ' + call + '.LINE]',
        *unchanged(warning,ready,'USERCONSTANTS STORE ENV STRINGDATA ARRAYS OBJECTS SELECTEDCALLS'),
        *common.public(warning), *common.step(done,warning,'PBOOL false'),
        done + '.TODO = ptask_' + before + '*', done + '.USERCONSTANTS = ' + ready + '.USERCONSTANTS']


def captured_throw():
    values = [*reach('S_handler','S_warning',3), 'S_handler.CURRENT = (pcallcontext_handler)',
        '$error_context_trigger(S_handler,pcallcontext_handler) = (pconfigcall_converted_S)',
        '$error_handler_trace_values(S_handler,pcallcontext_handler,pconfigcall_converted_S) = [pvalue_api_name,pvalue_candidate_S,PBOOL false]',
        '$string_bytes(pvalue_api_name) = (' + text('CAPTUREDEFINE55') + ')',
        *common.public('S_handler'), *reach('S_thrown','S_handler',4),
        'S_thrown.TODO = (THROW_SEARCH n_throw) :: (ERROR_HANDLER_RESULT perrorcall_thrown) :: ptask_S*',
        'perrorcall_thrown.RESUME = DYNAMIC_CONSTANT_DUPLICATE pconfigcall_converted_S 1',
        '$error_call_valid(S_thrown,perrorcall_thrown)', '$throwable_live(S_thrown,n_throw)',
        '$throwable_field(S_thrown,n_throw,"previous") = PNULL',
        '$string_bytes($throwable_field(S_thrown,n_throw,"message")) = (' + text('duplicate55') + ')',
        '$throwable_field(S_thrown,n_throw,"trace") = PARRAY n_trace',
        'S_thrown.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_handler)),ENTRY (KINT 1) (DIRECT (PARRAY n_api)),ENTRY (KINT 2) (DIRECT (PARRAY n_caller))]',
        '$trace_array_field(S_thrown,n_handler,' + text('function') + ') = PSTRING ' + text('defineStringWarning55'),
        '$trace_array_field(S_thrown,n_api,' + text('function') + ') = PSTRING ' + text('define'),
        '$trace_array_field(S_thrown,n_api,' + text('args') + ') = PARRAY n_args',
        'S_thrown.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_api_name),ENTRY (KINT 1) (DIRECT pvalue_candidate_S),ENTRY (KINT 2) (DIRECT (PBOOL false))]',
        '$trace_array_field(S_thrown,n_caller,' + text('function') + ') = PSTRING ' + text('capturedDefineCaller55'),
        '$lookup(S_thrown.ENV,' + text('saved') + ') = (n_saved)', 'S_thrown.STORE[n_saved] = DEFINED (POBJECT n_throw)',
        '$lookup(S_thrown.ENV,' + text('warnings') + ') = (n_warnings)', 'S_thrown.STORE[n_warnings] = DEFINED (PINT 1)',
        'S_thrown.STORE[n_result] = DEFINED (PINT 99)',
        '$source_constant_lookup(S_thrown,' + text('CAPTUREDEFINE55') + ') = (VALUE (PINT 1493))',
        'S_discard = S_thrown[.TODO = (THROW_SEARCH n_throw) :: ptask_S*]',
        'S_expected = $error_handler_restore($identity_read_discard(S_discard,perrorcall_thrown.RESUME),perrorcall_thrown.CALLBACK)',
        '$error_read_discard(S_expected,perrorcall_thrown.RESUME) = S_expected',
        *common.step('S_after','S_thrown'), 'S_after = S_expected',
        'S_after.STORE[n_result] = DEFINED (PINT 99)', *common.public('S_after')]
    return values


def checks(program,path,name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *front('S','S_initial',name != 'weak-stringable-define-names-fresh-then-duplicate')]
    if name == 'weak-stringable-define-names-fresh-then-duplicate':
        values += ['pvalue_candidate_S = PINT 1481', *weak('S','STRINGDEFINE55'),
            '$source_constant_lookup(S_ready,' + text('STRINGDEFINE55') + ') = eps',
            *common.step('S_published','S_ready','PBOOL true'),
            'S_published.USERCONSTANTS = [{NAME ' + text('STRINGDEFINE55') + ',ORIGIN pconfigcall_S.SITE,VALUE (PINT 1481),CLASS PVSCALAR,READS eps,RECEIVES eps}]',
            *unchanged('S_published','S_ready','STORE ENV ARRAYS OBJECTS OBJECTPROPS STRINGDATA EVENTS'),
            *front('S_duplicate','S_published',True), 'n_object_S_duplicate = n_object_S',
            'pvalue_candidate_S_duplicate = PINT 1487', *weak('S_duplicate','STRINGDEFINE55'),
            *duplicate('S_duplicate','STRINGDEFINE55'),
            '$source_constant_lookup(S_duplicate_done,' + text('STRINGDEFINE55') + ') = (VALUE (PINT 1481))',
            '$test_outputs(S_duplicate_done.EVENTS) = ' + text('B|S|T|1481|S|'),
            '~$dynamic_define_string_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,1,KNOWN (PINT 1482))])',
            *refusals('S'), *budget('S'), *budget('S_returned')]
    elif name == 'selected-stringable-name-callback-installs-duplicate-key':
        values += ['pconfigcall_S.SELECTION = (n_selection)', 'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
            'pvalue_candidate_S = PSTRING_CARRIER (REQUEST_STRING n_candidate) ' + text('captured-candidate55'),
            '$string_carrier_valid(S,pvalue_candidate_S)', '$test_outputs(S.EVENTS) = ' + text('B|V|'),
            '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            *weak('S','CAPTUREDEFINE55'),
            'pvalue_string_S = PSTRING_CARRIER (REQUEST_STRING n_name) ' + text('CAPTUREDEFINE55'),
            '$source_constant_lookup(S,' + text('CAPTUREDEFINE55') + ') = eps',
            '$source_constant_lookup(S_ready,' + text('CAPTUREDEFINE55') + ') = (VALUE (PINT 1493))',
            'S_ready.USERCONSTANTS = [puserconstant_inner]', 'puserconstant_inner.VALUE = PINT 1493',
            '$lookup(S_ready.ENV,' + text('call') + ') = (n_live_call)', 'S_ready.STORE[n_live_call] = DEFINED pvalue_live_call',
            '$string_bytes(pvalue_live_call) = (' + text('constant') + ')',
            '$lookup(S_ready.ENV,' + text('name') + ') = (n_live_name)', 'S_ready.STORE[n_live_name] = DEFINED pvalue_live_name',
            '$string_bytes(pvalue_live_name) = (' + text('cast-live55') + ')',
            '$lookup(S_ready.ENV,' + text('value') + ') = (n_live_value)', 'S_ready.STORE[n_live_value] = DEFINED (PINT 997)',
            '$lookup(S_ready.ENV,' + text('flag') + ') = (n_flag)', 'S_ready.STORE[n_flag] = DEFINED (PBOOL true)',
            '$lookup(S_ready.ENV,' + text('calls') + ') = (n_calls)', 'S_ready.STORE[n_calls] = DEFINED (PINT 1)',
            '$lookup(S_ready.ENV,' + text('effects') + ') = (n_effects)', 'S_ready.STORE[n_effects] = DEFINED (PINT 1)',
            '$dynamic_constant_duplicate_valid(S_ready,pconfigcall_converted_S,1)',
            *common.step('S_warning','S_ready'),
            'S_warning.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_S*',
            'perrorcall.RESUME = DYNAMIC_CONSTANT_DUPLICATE pconfigcall_converted_S 1',
            'perrorcall.LEVEL = 2', 'perrorcall.MESSAGE = $global_constant_duplicate_message(' + text('CAPTUREDEFINE55') + ')',
            'perrorcall.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE pconfigcall_S.LINE',
            '$error_call_valid(S_warning,perrorcall)', 'S_warning.EVENTS = S_ready.EVENTS',
            *captured_throw(), *refusals('S'), *budget('S'), *budget('S_returned'),
            'pvalue_bad_candidate = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ' + text('captured-candidate55'),
            '~$dynamic_define_string_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,1,KNOWN pvalue_bad_candidate)])']
        for value in ('PSTRING ' + text('A::B'), 'PSTRING (' + text('name55') + ' ++ [0])',
                'PSTRING ' + text('__COMPILER_HALT_OFFSET__'),
                'PSTRING_CARRIER (REQUEST_STRING (|S_returned.STRINGDATA|)) ' + text('CAPTUREDEFINE55')):
            values += ['S_refused_' + str(len(values)) + ' = $dynamic_define_string_finish(S_returned,pconfigcall_S,' + value + ')',
                'S_refused_' + str(len(values)) + '.COMPLETION = UNSUPPORTED "Stringable define global name"']
    else:
        assert name == 'strict-stringable-define-rejects-before-name-method'
        values += ['$config_strict(S,pconfigcall_S)', '~$config_string_launch(S,pconfigcall_S)',
            '~$config_string_site_valid(S,pconfigcall_S,n_object_S,porigin_child_S,z_child_S,pconfigcall_S.LINE)',
            'pvalue_candidate_S = PINT 1507', '$test_outputs(S.EVENTS) = ' + text('B|V|'),
            '$lookup(S.ENV,' + text('effects') + ') = (n_effects)', 'S.STORE[n_effects] = DEFINED (PINT 1)',
            '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            *common.step('S_error','S'), 'S_error.TODO = (THROW_SEARCH n_error) :: ptask_S*',
            'S_error.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "TypeError"',
            'pthrowable.ORIGIN = (pconfigcall_S.SITE)',
            '$string_bytes($throwable_field(S_error,n_error,"message")) = (' + text('define(): Argument #1 ($constant_name) must be of type string, StrictStringDefine55 given') + ')',
            '$throwable_field(S_error,n_error,"previous") = PNULL',
            '$throwable_field(S_error,n_error,"line") = PINT pconfigcall_S.LINE',
            '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
            'S_error.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_api)),ENTRY (KINT 1) (DIRECT (PARRAY n_caller))]',
            '$trace_array_field(S_error,n_api,' + text('function') + ') = PSTRING ' + text('define'),
            '$trace_array_field(S_error,n_api,' + text('args') + ') = PARRAY n_args',
            'S_error.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_object_S)),ENTRY (KINT 1) (DIRECT (PINT 1507)),ENTRY (KINT 2) (DIRECT (PBOOL false))]',
            '$trace_array_field(S_error,n_caller,' + text('function') + ') = PSTRING ' + text('strictStringDefineCaller55'),
            *unchanged('S_error','S','STORE ENV USERCONSTANTS STRINGDATA EVENTS SELECTEDCALLS AUTOLOAD CLASSNAMES CLASSCONSTANTCACHE'),
            'S_error.STORE[n_result] = DEFINED (PINT 99)', *common.public('S_error'), *refusals('S'), *budget('S')]
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
