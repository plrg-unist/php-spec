#!/usr/bin/env python3
"""The reached query error preserves a receiver without invoking ordinary toString."""
import json
import os
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import query_nonstringable_name_review_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64

PREFIX = r"""
dec $test_nonstring_query_front(pstate, nat) : bool
def $test_nonstring_query_front(S, 0) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINED
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_object))]
def $test_nonstring_query_front(S, 1) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINED
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue)]
  -- if $string_bytes(pvalue) = ($ptascii("TRUE"))
def $test_nonstring_query_front(S, n_stage) = false -- otherwise
dec $test_nonstring_query_seek(pstate, nat, nat) : pstate
def $test_nonstring_query_seek(S, n_stage, 0) = S
def $test_nonstring_query_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_nonstring_query_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_nonstring_query_seek(S, n_stage, n) = $test_nonstring_query_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_nonstring_query_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def front(state, start, stage):
    return [state + '_found = $test_nonstring_query_seek(' + start + ',' + str(stage) + ',3000)',
        state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_nonstring_query_front(' + state + ',' + str(stage) + ')',
        state + '.TODO = (CONFIG_INVOKE pconfigcall_' + state + ') :: ptask_' + state + '*',
        '$config_invoke_valid(' + state + ',pconfigcall_' + state + ')', *common.public(state)]


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)', state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)', state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def checks(program, path, name):
    assert name == 'selected-nonstringable-defined-does-not-call-ordinary-string-method'
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *front('S', 'S_initial', 0),
        'pconfigcall_S.KIND = INTRINSIC_DEFINED', 'pconfigcall_S.INDEX = 1',
        '$intrinsic_count(S,pconfigcall_S.SITE) = (1)',
        'pconfigcall_S.SENT = [NAMED_SENT (KNOWN (POBJECT n_receiver))]',
        'pconfigcall_S.OWNER = eps', 'pconfigcall_S.PACKS = eps', '~pconfigcall_S.NAMED',
        'pconfigcall_S.SELECTION = (n_selection)', 'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINED',
        '$dynamic_query_string_call(pconfigcall_S)',
        '$dynamic_query_nonstring_object(S,n_receiver)', '$dynamic_query_nonstring_valid(S,pconfigcall_S)',
        '~$dynamic_query_string_valid(S,pconfigcall_S)', '~$stringable_instance(S,n_receiver)',
        '~$config_strict(S,pconfigcall_S)', '~$config_string_launch(S,pconfigcall_S)',
        'S_file = S[.FILEINCLUDEPATH = (' + text('.') + ')]',
        '~$config_string_launch(S_file,pconfigcall_S)',
        '$dynamic_query_nonstring_valid(S_file,pconfigcall_S)',
        'S.OBJECTS[n_receiver] = INSTANCE porigin_class',
        '$effective_method(S,porigin_class,' + text('toString') + ',|S.CLASSES|) = (pmethoddesc_ordinary)',
        '$effective_method(S,porigin_class,' + text('__toString') + ',|S.CLASSES|) = eps',
        '$object_name(S,n_receiver) = ' + text('QueryNonStringReview54'),
        '$intrinsic_argument(S,pconfigcall_S.SITE,0) = ((expression_argument,false,eps,porigin_argument,z_argument))',
        '$compiled_read(S,porigin_argument) = eps',
        '$lookup(S.ENV,' + text('keep') + ') = (n_keep)', 'S.STORE[n_keep] = DEFINED (POBJECT n_receiver)',
        '$lookup(S.ENV,' + text('name') + ') = (n_name)', 'S.STORE[n_name] = DEFINED pvalue_name',
        '$string_bytes(pvalue_name) = (' + text('argument-live54') + ')',
        '$lookup(S.ENV,' + text('call') + ') = (n_call)', 'S.STORE[n_call] = DEFINED pvalue_call',
        '$string_bytes(pvalue_call) = (' + text('constant') + ')',
        '$lookup(S.ENV,' + text('effects') + ') = (n_effects)', 'S.STORE[n_effects] = DEFINED (PINT 1)',
        '$lookup(S.ENV,' + text('methodCalls') + ') = (n_method)', 'S.STORE[n_method] = DEFINED (PINT 0)',
        '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
        'S.USERCONSTANTS = eps', 'S.ERRORHANDLER.CALLBACK = eps',
        '$test_outputs(S.EVENTS) = ' + text('B|A|'), *common.step('S_error', 'S'),
        'S_error.TODO = (THROW_SEARCH n_error) :: ptask_S*',
        'S_error.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "TypeError"',
        'pthrowable.ORIGIN = (pconfigcall_S.SITE)',
        '$string_bytes($throwable_field(S_error,n_error,"message")) = (' + text('defined(): Argument #1 ($constant_name) must be of type string, QueryNonStringReview54 given') + ')',
        '$throwable_field(S_error,n_error,"line") = PINT pconfigcall_S.LINE',
        '$string_bytes($throwable_field(S_error,n_error,"file")) = ($call_sourcefile(S_error.FILES,pconfigcall_S.SITE))',
        '$throwable_field(S_error,n_error,"previous") = PNULL',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
        'S_error.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_api)),ENTRY (KINT 1) (DIRECT (PARRAY n_caller))]',
        '$trace_array_field(S_error,n_api,' + text('function') + ') = PSTRING ' + text('defined'),
        '$trace_array_field(S_error,n_api,' + text('line') + ') = PINT pconfigcall_S.LINE',
        '$trace_array_field(S_error,n_api,' + text('args') + ') = PARRAY n_args',
        'S_error.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_receiver))]',
        '$node_children(S_error,HARRAY n_args) = [HOBJECT n_receiver]',
        '$trace_array_field(S_error,n_caller,' + text('function') + ') = PSTRING ' + text('queryNonStringReviewCaller54'),
        'S_error.OBJECTS[n_receiver] = INSTANCE porigin_class',
        'S_error.STORE[n_result] = DEFINED (PINT 99)', 'S_error.STORE[n_method] = DEFINED (PINT 0)']
    values += ['S_error.' + field + ' = S.' + field for field in (
        'STORE', 'ENV', 'USERCONSTANTS', 'STRINGDATA', 'EVENTS', 'SELECTEDCALLS', 'REFCELLS',
        'ERRORHANDLER', 'AUTOLOAD', 'CLASSNAMES', 'CLASSCONSTANTCACHE', 'SOURCES', 'POOLS', 'FILES', 'STATICS')]
    values += [*common.public('S_error')]
    for field in ('.SITE = PORIGIN 0 eps', '.LINE = $(pconfigcall_S.LINE + 1)', '.INDEX = 0',
            '.SELECTION = eps', '.SELECTION = (|S.SELECTEDCALLS|)', '.KIND = INTRINSIC_CONSTANT'):
        values += ['~$dynamic_query_nonstring_valid(S,pconfigcall_S[' + field + '])']
    for field in ('.OWNER = (0)', '.NAMED = true', '.KIND = INTRINSIC_DEFINE', '.SENT = eps',
            '.SENT = pconfigcall_S.SENT ++ [NAMED_SENT (KNOWN PNULL)]', '.SENT = [NAMED_SENT (KNOWN PNULL)]'):
        bad = 'pconfigcall_S[' + field + ']'
        values += ['~$dynamic_query_string_call(' + bad + ')', '~$dynamic_query_nonstring_valid(S,' + bad + ')']
    values += ['n_dead = |S.OBJECTS|', '~$dynamic_query_nonstring_object(S,n_dead)',
        'pconfigcall_dead = pconfigcall_S[.SENT = [NAMED_SENT (KNOWN (POBJECT n_dead))]]',
        '$dynamic_query_string_call(pconfigcall_dead)', '~$dynamic_query_nonstring_valid(S,pconfigcall_dead)',
        *budget('S'), *front('S_recovery', 'S_error', 1),
        'pconfigcall_S_recovery.SELECTION = (n_recovery_selection)',
        'S_recovery.SELECTEDCALLS[n_recovery_selection].KIND = INTRINSIC_DEFINED',
        'S_recovery.STORE[n_result] = DEFINED (PINT 99)', 'S_recovery.STORE[n_method] = DEFINED (PINT 0)',
        'S_recovery.STORE[n_effects] = DEFINED (PINT 1)', 'S_recovery.STORE[n_keep] = DEFINED (POBJECT n_receiver)',
        'S_recovery.USERCONSTANTS = eps', '~$dynamic_query_string_call(pconfigcall_S_recovery)',
        '~$dynamic_query_nonstring_valid(S_recovery,pconfigcall_S_recovery)',
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
