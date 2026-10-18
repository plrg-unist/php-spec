#!/usr/bin/env python3
"""Reached define rejection precedes true-flag reception after both later effects."""
import json
import os
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import define_nonstringable_name_review_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64

PREFIX = r"""
dec $test_nonstring_define_front(pstate, nat) : bool
def $test_nonstring_define_front(S, 0) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if $dynamic_define_nonstring_call(pconfigcall)
def $test_nonstring_define_front(S, 1) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINED
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue)]
  -- if $string_bytes(pvalue) = ($ptascii("TRUE"))
def $test_nonstring_define_front(S, n_stage) = false -- otherwise
dec $test_nonstring_define_seek(pstate, nat, nat) : pstate
def $test_nonstring_define_seek(S, n_stage, 0) = S
def $test_nonstring_define_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_nonstring_define_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_nonstring_define_seek(S, n_stage, n) = $test_nonstring_define_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_nonstring_define_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def front(state, start, stage):
    return [state + '_found = $test_nonstring_define_seek(' + start + ',' + str(stage) + ',3000)',
        state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_nonstring_define_front(' + state + ',' + str(stage) + ')',
        state + '.TODO = (CONFIG_INVOKE pconfigcall_' + state + ') :: ptask_' + state + '*',
        '$config_invoke_valid(' + state + ',pconfigcall_' + state + ')', *common.public(state)]


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)', state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)', state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def checks(program, path, name):
    assert name == 'selected-nonstringable-define-before-captured-true-flag-reception'
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *front('S', 'S_initial', 0),
        'pconfigcall_S.KIND = INTRINSIC_DEFINE', 'pconfigcall_S.INDEX = 3',
        '$intrinsic_count(S,pconfigcall_S.SITE) = (3)',
        'pconfigcall_S.SENT = [NAMED_SENT (KNOWN (POBJECT n_receiver)),NAMED_SENT (KNOWN pvalue_candidate),NAMED_SENT (KNOWN (PBOOL true))]',
        'pvalue_candidate = PSTRING_CARRIER (REQUEST_STRING n_candidate) ' + text('captured-value56'),
        '$string_carrier_valid(S,pvalue_candidate)',
        'pconfigcall_S.OWNER = eps', 'pconfigcall_S.PACKS = eps', '~pconfigcall_S.NAMED',
        'pconfigcall_S.SELECTION = (n_selection)', 'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
        '$dynamic_define_nonstring_call(pconfigcall_S)', '$dynamic_define_nonstring_valid(S,pconfigcall_S)',
        '$dynamic_query_nonstring_object(S,n_receiver)', '~$stringable_instance(S,n_receiver)',
        '~$dynamic_define_string_valid(S,pconfigcall_S)', '~$config_strict(S,pconfigcall_S)',
        '~$config_string_launch(S,pconfigcall_S)',
        'S_file = S[.FILEINCLUDEPATH = (' + text('.') + ')]',
        '~$config_string_launch(S_file,pconfigcall_S)', '$dynamic_define_nonstring_valid(S_file,pconfigcall_S)',
        'S.OBJECTS[n_receiver] = INSTANCE porigin_class',
        '$effective_method(S,porigin_class,' + text('toString') + ',|S.CLASSES|) = (pmethoddesc_ordinary)',
        '$effective_method(S,porigin_class,' + text('__toString') + ',|S.CLASSES|) = eps',
        '$object_name(S,n_receiver) = ' + text('DefineNonStringReview56'),
        '$intrinsic_argument(S,pconfigcall_S.SITE,0) = ((expression_argument,false,eps,porigin_argument,z_argument))',
        '$compiled_read(S,porigin_argument) = eps',
        '$lookup(S.ENV,' + text('keep') + ') = (n_keep)', 'S.STORE[n_keep] = DEFINED (POBJECT n_receiver)',
        '$lookup(S.ENV,' + text('name') + ') = (n_name)', 'S.STORE[n_name] = DEFINED pvalue_name',
        '$string_bytes(pvalue_name) = (' + text('flag-name56') + ')',
        '$lookup(S.ENV,' + text('call') + ') = (n_call)', 'S.STORE[n_call] = DEFINED pvalue_call',
        '$string_bytes(pvalue_call) = (' + text('constant') + ')',
        '$lookup(S.ENV,' + text('value') + ') = (n_value)', 'S.STORE[n_value] = DEFINED pvalue_live_value',
        '$string_bytes(pvalue_live_value) = (' + text('flag-value56') + ')',
        '$lookup(S.ENV,' + text('flag') + ') = (n_flag)', 'S.STORE[n_flag] = DEFINED (PBOOL false)',
        '$lookup(S.ENV,' + text('effects') + ') = (n_effects)', 'S.STORE[n_effects] = DEFINED (PINT 2)',
        '$lookup(S.ENV,' + text('methodCalls') + ') = (n_method)', 'S.STORE[n_method] = DEFINED (PINT 0)',
        '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
        'S.USERCONSTANTS = eps', 'S.ERRORHANDLER.CALLBACK = eps',
        '$test_outputs(S.EVENTS) = ' + text('B|V|F|'), *common.step('S_error', 'S'),
        'S_error.TODO = (THROW_SEARCH n_error) :: ptask_S*',
        'S_error.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "TypeError"',
        'pthrowable.ORIGIN = (pconfigcall_S.SITE)',
        '$string_bytes($throwable_field(S_error,n_error,"message")) = (' + text('define(): Argument #1 ($constant_name) must be of type string, DefineNonStringReview56 given') + ')',
        '$throwable_field(S_error,n_error,"line") = PINT pconfigcall_S.LINE',
        '$string_bytes($throwable_field(S_error,n_error,"file")) = ($call_sourcefile(S_error.FILES,pconfigcall_S.SITE))',
        '$throwable_field(S_error,n_error,"previous") = PNULL',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
        'S_error.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_api)),ENTRY (KINT 1) (DIRECT (PARRAY n_caller))]',
        '$trace_array_field(S_error,n_api,' + text('function') + ') = PSTRING ' + text('define'),
        '$trace_array_field(S_error,n_api,' + text('line') + ') = PINT pconfigcall_S.LINE',
        '$trace_array_field(S_error,n_api,' + text('args') + ') = PARRAY n_args',
        'S_error.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_receiver)),ENTRY (KINT 1) (DIRECT pvalue_candidate),ENTRY (KINT 2) (DIRECT (PBOOL true))]',
        '$trace_array_field(S_error,n_caller,' + text('function') + ') = PSTRING ' + text('defineNonStringReviewCaller56'),
        'S_error.OBJECTS[n_receiver] = INSTANCE porigin_class',
        '$objectprops_at(S_error.OBJECTPROPS,n_receiver) = $objectprops_at(S.OBJECTPROPS,n_receiver)',
        'S_error.STORE[n_result] = DEFINED (PINT 99)', 'S_error.STORE[n_method] = DEFINED (PINT 0)']
    values += ['S_error.' + field + ' = S.' + field for field in (
        'STORE', 'ENV', 'USERCONSTANTS', 'STRINGDATA', 'EVENTS', 'SELECTEDCALLS', 'REFCELLS',
        'ERRORHANDLER', 'AUTOLOAD', 'CLASSNAMES', 'CLASSCONSTANTCACHE', 'SOURCES', 'POOLS', 'FILES', 'STATICS')]
    values += [*common.public('S_error'), '~$dynamic_query_nonstring_object(S_error,n_error)']
    for field in ('.SITE = PORIGIN 0 eps', '.LINE = $(pconfigcall_S.LINE + 1)', '.INDEX = 0',
            '.SELECTION = eps', '.SELECTION = (|S.SELECTEDCALLS|)', '.KIND = INTRINSIC_CONSTANT'):
        values += ['~$dynamic_define_nonstring_valid(S,pconfigcall_S[' + field + '])']
    for field in ('.OWNER = (0)', '.NAMED = true', '.KIND = INTRINSIC_DEFINED', '.SENT = eps',
            '.SENT = pconfigcall_S.SENT ++ [NAMED_SENT (KNOWN PNULL)]',
            '.SENT = $named_slot_set(pconfigcall_S.SENT,0,KNOWN PNULL)'):
        bad = 'pconfigcall_S[' + field + ']'
        values += ['~$dynamic_define_nonstring_call(' + bad + ')', '~$dynamic_define_nonstring_valid(S,' + bad + ')']
    values += ['n_dead = |S.OBJECTS|', '~$dynamic_query_nonstring_object(S,n_dead)',
        'pconfigcall_dead = pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,0,KNOWN (POBJECT n_dead))]',
        '$dynamic_define_nonstring_call(pconfigcall_dead)', '~$dynamic_define_nonstring_valid(S,pconfigcall_dead)',
        'pconfigcall_two = pconfigcall_S[.SENT = pconfigcall_S.SENT[0:2]][.INDEX = 2]',
        '$dynamic_define_nonstring_call(pconfigcall_two)', '~$dynamic_define_nonstring_valid(S,pconfigcall_two)',
        'pvalue_bad_candidate = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ' + text('captured-value56'),
        'pconfigcall_bad_candidate = pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,1,KNOWN pvalue_bad_candidate)]',
        '$dynamic_define_nonstring_call(pconfigcall_bad_candidate)', '~$dynamic_define_nonstring_valid(S,pconfigcall_bad_candidate)',
        'pvalue_bad_flag = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ' + text('0'),
        'pconfigcall_bad_flag = pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,2,KNOWN pvalue_bad_flag)]',
        '$dynamic_define_nonstring_call(pconfigcall_bad_flag)', '~$dynamic_define_nonstring_valid(S,pconfigcall_bad_flag)',
        *budget('S'), *front('S_recovery', 'S_error', 1),
        'pconfigcall_S_recovery.SELECTION = (n_recovery_selection)',
        'S_recovery.SELECTEDCALLS[n_recovery_selection].KIND = INTRINSIC_DEFINED',
        'S_recovery.STORE[n_result] = DEFINED (PINT 99)', 'S_recovery.STORE[n_method] = DEFINED (PINT 0)',
        'S_recovery.STORE[n_effects] = DEFINED (PINT 2)', 'S_recovery.STORE[n_keep] = DEFINED (POBJECT n_receiver)',
        'S_recovery.USERCONSTANTS = eps', '~$dynamic_define_nonstring_call(pconfigcall_S_recovery)',
        '~$dynamic_define_nonstring_valid(S_recovery,pconfigcall_S_recovery)',
        *common.step('S_recovered', 'S_recovery', 'PBOOL true'),
        'S_recovered.TODO = ptask_S_recovery*', 'S_recovered.STORE = S_recovery.STORE',
        'S_recovered.USERCONSTANTS = eps', 'S_recovered.STORE[n_method] = DEFINED (PINT 0)',
        *budget('S_recovery')]
    return values


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
