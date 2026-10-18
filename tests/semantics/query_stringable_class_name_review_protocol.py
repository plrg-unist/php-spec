#!/usr/bin/env python3
"""A converted class query reaches a real autoload throw and clears its cursor."""
import json
import os
from pathlib import Path

import query_stringable_name_protocol as cast
import query_stringable_class_name_review_sources as sources

driver, common, text, b64 = cast.driver, cast.common, cast.text, cast.b64
PREFIX = cast.PREFIX + r"""
dec $test_string_class_throw_front(pstate, nat) : bool
def $test_string_class_throw_front(S, 0) = true
  -- if S.TODO = (THROW_VALUE porigin z) :: ptask_body*
  -- if S.CURRENT = (pcallcontext)
  -- if $autoload_context_call(pcallcontext,S.CURRENT,S.FRAMES) = ((pautoloadcall,pautoloadentry,poperand))
  -- if pautoloadcall.MODE = AUTO_EXPLICIT pconfigcall
  -- if pconfigcall.KIND = INTRINSIC_CONSTANT
  -- if pautoloadcall.NAME = $ptascii("AutoStringQuery58")
def $test_string_class_throw_front(S, 1) = true
  -- if S.TODO = (THROW_SEARCH n) :: (AUTO_RESULT pautoloadcall pautoloadentry poperand) :: ptask_tail*
  -- if pautoloadcall.MODE = AUTO_EXPLICIT pconfigcall
  -- if pconfigcall.KIND = INTRINSIC_CONSTANT
  -- if pautoloadcall.NAME = $ptascii("AutoStringQuery58")
def $test_string_class_throw_front(S, n_stage) = false -- otherwise
dec $test_string_class_throw_seek(pstate, nat, nat) : pstate
def $test_string_class_throw_seek(S, n_stage, 0) = S
def $test_string_class_throw_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_string_class_throw_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_string_class_throw_seek(S, n_stage, n) = $test_string_class_throw_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_string_class_throw_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def reach(state, start, stage):
    return [state + '_found = $test_string_class_throw_seek(' + start + ',' + str(stage) + ',3000)',
        state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_string_class_throw_front(' + state + ',' + str(stage) + ')']


def checks(program, path, name):
    assert name == 'selected-stringable-class-query-enters-loader-before-supplied-throw'
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *cast.front('S', 'S_initial', 'INTRINSIC_CONSTANT'),
        'pconfigcall_S.INDEX = 1', '$intrinsic_count(S,pconfigcall_S.SITE) = (1)',
        'pconfigcall_S.SELECTION = (n_selection)', 'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_CONSTANT',
        '$lookup(S.ENV,' + text('keep') + ') = (n_keep)', 'S.STORE[n_keep] = DEFINED (POBJECT n_object_S)',
        '$lookup(S.ENV,' + text('name') + ') = (n_name)', 'S.STORE[n_name] = DEFINED (POBJECT n_object_S)',
        '$lookup(S.ENV,' + text('call') + ') = (n_call)', 'S.STORE[n_call] = DEFINED pvalue_before_call',
        '$string_bytes(pvalue_before_call) = (' + text('CoNsTaNt') + ')',
        '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
        '$lookup(S.ENV,' + text('casts') + ') = (n_casts)', 'S.STORE[n_casts] = DEFINED (PINT 0)',
        '$lookup(S.ENV,' + text('loads') + ') = (n_loads)', 'S.STORE[n_loads] = DEFINED (PINT 0)',
        '$lookup(S.ENV,' + text('saved') + ') = (n_saved)', 'S.STORE[n_saved] = DEFINED PNULL',
        'S.USERCONSTANTS = eps', '$test_outputs(S.EVENTS) = ' + text('B|'),
        *cast.weak('S', 'INTRINSIC_CONSTANT', 'AutoStringQuery58::VALUE', None),
        'pvalue_string_S = PSTRING_CARRIER (REQUEST_STRING n_converted) ' + text('AutoStringQuery58::VALUE'),
        '~$dynamic_constant_global_name(' + text('AutoStringQuery58::VALUE') + ')',
        '$dynamic_constant_class_name(' + text('AutoStringQuery58::VALUE') + ')',
        '$dynamic_class_constant_valid(S_ready,pconfigcall_converted_S)',
        '$dynamic_defined_query(pconfigcall_converted_S) = ((' + text('AutoStringQuery58') + ',' + text('VALUE') + '))',
        'S_ready.STORE[n_result] = DEFINED (PINT 99)', 'S_ready.STORE[n_casts] = DEFINED (PINT 1)',
        'S_ready.STORE[n_loads] = DEFINED (PINT 0)', 'S_ready.STORE[n_saved] = DEFINED PNULL',
        'S_ready.STORE[n_keep] = DEFINED (POBJECT n_object_S)',
        'S_ready.STORE[n_call] = DEFINED pvalue_cast_call', '$string_bytes(pvalue_cast_call) = (' + text('defined') + ')',
        'S_ready.STORE[n_name] = DEFINED pvalue_cast_name', '$string_bytes(pvalue_cast_name) = (' + text('cast-name58') + ')',
        '$class_named(S_ready.CLASSNAMES,' + text('autostringquery58') + ') = eps',
        '$autoload_pending(S_ready,' + text('AutoStringQuery58') + ')',
        '$test_outputs(S_ready.EVENTS) = ' + text('B|S|'), *common.step('S_next', 'S_ready'),
        'S_next.TODO = (AUTO_NEXT pautoloadcall) :: ptask_S*',
        'pautoloadcall.MODE = AUTO_EXPLICIT pconfigcall_converted_S',
        'pautoloadcall.RESUME = DYNAMIC_CLASS_CONSTANT_RESUME pconfigcall_converted_S',
        'pautoloadcall.NAME = ' + text('AutoStringQuery58'), 'pautoloadcall.KEY = ' + text('autostringquery58'),
        'pautoloadcall.SITE = pconfigcall_S.SITE', 'pautoloadcall.LINE = pconfigcall_S.LINE',
        'pautoloadcall.INDEX = 0', 'pautoloadcall.BIRTH = eps',
        '$dynamic_class_constant_autoload_valid(S_next,pautoloadcall)',
        '$autoload_trace_arguments(pconfigcall_converted_S,pautoloadcall.NAME) = [pvalue_string_S]',
        '$autoload_active_tasks(S_next.TODO,pautoloadcall.KEY)',
        '~$autoload_pending(S_next,pautoloadcall.NAME)',
        'S_next.STORE = S_ready.STORE', 'S_next.EVENTS = S_ready.EVENTS',
        *common.public('S_next'), *reach('S_throw', 'S_next', 0),
        'S_throw.TODO = (THROW_VALUE porigin_throw z_throw) :: ptask_body*',
        'S_throw.CURRENT = (pcallcontext_loader)',
        '$autoload_context_call(pcallcontext_loader,S_throw.CURRENT,S_throw.FRAMES) = ((pautoloadcall_selected,pautoloadentry,poperand))',
        'pautoloadcall_selected.MODE = AUTO_EXPLICIT pconfigcall_converted_S',
        'pautoloadcall_selected.RESUME = DYNAMIC_CLASS_CONSTANT_RESUME pconfigcall_converted_S',
        'pautoloadcall_selected.NAME = pautoloadcall.NAME', 'pautoloadcall_selected.KEY = pautoloadcall.KEY',
        'pautoloadentry.TARGET = AUTO_TARGET pcallcontext_loader.TARGET',
        'pcallcontext_loader.CALLSITE = eps', 'pcallcontext_loader.LINE = $(-1)',
        'poperand = KNOWN (PSTRING ' + text('AutoStringQuery58') + ')',
        '$autoload_context_valid(S_throw,pcallcontext_loader)',
        'S_throw.FRAMES = pframe_call :: pframe_outer*',
        'pframe_call.CONTEXT = S.CURRENT', 'pframe_call.LOCALS = ($active_table(S))',
        'pframe_call.TODO = (AUTO_RESULT pautoloadcall_selected pautoloadentry poperand) :: ptask_S*',
        '$trace_context(S_throw,S_throw.ENV,S_throw.CURRENT) = [ptraceframe_loader,ptraceframe_api]',
        'ptraceframe_loader.FILE = eps', 'ptraceframe_loader.LINE = $(-1)',
        'ptraceframe_api.FUNCTION = ' + text('constant'),
        'ptraceframe_api.ARGS = $trace_indexed_args([pvalue_string_S],0)',
        'ptraceframe_api.LINE = pconfigcall_S.LINE',
        'ptraceframe_api.FILE = $call_sourcefile(S_throw.FILES,pconfigcall_S.SITE)',
        'S_throw.STORE[n_saved] = DEFINED (POBJECT n_exception)',
        'S_throw.OBJECTS[n_exception] = THROWABLE pthrowable', 'pthrowable.KIND = "Exception"',
        '$string_bytes($throwable_field(S_throw,n_exception,"message")) = (' + text('autoload58-stop') + ')',
        '$throwable_field(S_throw,n_exception,"previous") = PNULL',
        '$throwable_field(S_throw,n_exception,"trace") = PARRAY n_trace',
        'S_throw.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_loader)),ENTRY (KINT 1) (DIRECT (PARRAY n_api)),ENTRY (KINT 2) (DIRECT (PARRAY n_caller))]',
        '$trace_array_field(S_throw,n_loader,' + text('function') + ') = PSTRING ' + text('stringQueryReviewLoader58'),
        '$trace_array_field(S_throw,n_loader,' + text('args') + ') = PARRAY n_loader_args',
        'S_throw.ARRAYS[n_loader_args].ITEMS = [ENTRY (KINT 0) (DIRECT (PSTRING ' + text('AutoStringQuery58') + '))]',
        '$trace_array_field(S_throw,n_api,' + text('function') + ') = PSTRING ' + text('constant'),
        '$trace_array_field(S_throw,n_api,' + text('line') + ') = PINT pconfigcall_S.LINE',
        '$trace_array_field(S_throw,n_api,' + text('args') + ') = PARRAY n_api_args',
        'S_throw.ARRAYS[n_api_args].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_string_S)]',
        '$node_children(S_throw,HARRAY n_api_args) = eps',
        '$trace_array_field(S_throw,n_caller,' + text('function') + ') = PSTRING ' + text('stringQueryReviewCaller58'),
        'S_throw.STORE[n_result] = DEFINED (PINT 99)',
        'S_throw.STORE[n_casts] = DEFINED (PINT 1)', 'S_throw.STORE[n_loads] = DEFINED (PINT 1)',
        'S_throw.STORE[n_keep] = DEFINED (POBJECT n_object_S)',
        'S_throw.STORE[n_call] = DEFINED pvalue_loader_call', '$string_bytes(pvalue_loader_call) = (' + text('constant') + ')',
        'S_throw.STORE[n_name] = DEFINED pvalue_loader_name', '$string_bytes(pvalue_loader_name) = (' + text('loader-name58') + ')',
        'S_throw.USERCONSTANTS = [puserconstant_sibling]',
        'puserconstant_sibling.NAME = ' + text('SOURCE58PEER'), 'puserconstant_sibling.VALUE = PINT 1699',
        'puserconstant_sibling.CLASS = PVSCALAR',
        '$class_named(S_throw.CLASSNAMES,' + text('autostringquery58') + ') = eps',
        'S_throw.AUTOLOAD = S_ready.AUTOLOAD', 'S_throw.CLASSNAMES = S_ready.CLASSNAMES',
        'S_throw.CLASSCONSTANTCACHE = S_ready.CLASSCONSTANTCACHE',
        'S_throw.OBJECTS[n_object_S] = S_ready.OBJECTS[n_object_S]',
        '$objectprops_at(S_throw.OBJECTPROPS,n_object_S) = $objectprops_at(S_ready.OBJECTPROPS,n_object_S)',
        '$test_outputs(S_throw.EVENTS) = ' + text('B|S|L|AutoStringQuery58|'),
        '~$autoload_pending(S_throw,pautoloadcall.NAME)', *common.public('S_throw'),
        *common.step('S_throwing', 'S_throw'),
        'S_throwing.TODO = (THROW_SEARCH n_exception) :: ptask_body*',
        'S_throwing.OBJECTS[n_exception] = THROWABLE pthrowable',
        *reach('S_unwind', 'S_throwing', 1),
        'S_unwind.TODO = (THROW_SEARCH n_exception) :: (AUTO_RESULT pautoloadcall_selected pautoloadentry poperand) :: ptask_S*',
        'S_unwind.CURRENT = S.CURRENT', 'S_unwind.ENV = S.ENV',
        'S_unwind.STORE[n_result] = DEFINED (PINT 99)',
        'S_unwind.STORE[n_keep] = DEFINED (POBJECT n_object_S)',
        'S_unwind.STORE[n_saved] = DEFINED (POBJECT n_exception)',
        'S_unwind.OBJECTS[n_exception] = THROWABLE pthrowable',
        'S_unwind.USERCONSTANTS = [puserconstant_sibling]',
        '$autoload_active_tasks(S_unwind.TODO,pautoloadcall.KEY)',
        '~$autoload_pending(S_unwind,pautoloadcall.NAME)',
        *common.public('S_unwind'), *common.step('S_discard', 'S_unwind'),
        'S_discard = S_unwind[.TODO = (THROW_SEARCH n_exception) :: ptask_S*]',
        '~$autoload_active_tasks(S_discard.TODO,pautoloadcall.KEY)',
        '~$autoload_active_frames(S_discard.FRAMES,pautoloadcall.KEY)',
        '$autoload_pending(S_discard,pautoloadcall.NAME)',
        *common.public('S_discard'), *cast.refusals('S'),
        'pconfigcall_bad_carrier = pconfigcall_converted_S[.SENT = [NAMED_SENT (KNOWN (PSTRING_CARRIER (REQUEST_STRING (|S_ready.STRINGDATA|)) ' + text('AutoStringQuery58::VALUE') + '))]]',
        '~$dynamic_class_constant_valid(S_ready,pconfigcall_bad_carrier)',
        '~$dynamic_class_constant_valid(S_ready,pconfigcall_S)',
        '~$dynamic_class_constant_valid(S_ready,pconfigcall_converted_S[.SELECTION = (|S_ready.SELECTEDCALLS|)])',
        *cast.budget('S'), *cast.budget('S_returned'), *cast.budget('S_next'), *cast.budget('S_unwind')]
    for i, field in enumerate(('.NAME = ' + text('OtherQuery58'), '.KEY = ' + text('OtherQuery58'),
            '.LINE = $(pautoloadcall.LINE + 1)', '.RESUME = DYNAMIC_DEFINED_RESUME pconfigcall_converted_S')):
        values += ['pautoloadcall_bad_' + str(i) + ' = pautoloadcall[' + field + ']',
            '~$dynamic_class_constant_autoload_valid(S_next,pautoloadcall_bad_' + str(i) + ')']
    for i, value in enumerate(('PSTRING (' + text('A::B') + ' ++ [0])',
            'PSTRING ' + text('__COMPILER_HALT_OFFSET__'),
            'PSTRING_CARRIER (REQUEST_STRING (|S_returned.STRINGDATA|)) ' + text('AutoStringQuery58::VALUE'))):
        state = 'S_refused_' + str(i)
        values += [state + ' = $dynamic_query_string_finish(S_returned,pconfigcall_S,' + value + ')',
            state + '.COMPLETION = UNSUPPORTED "Stringable query global name"']
    values += ['S_final = $drive_steps(S_discard,3000)', 'S_final.COMPLETION = NORMAL',
        'S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.USERCONSTANTS = [puserconstant_sibling]', 'S_final.AUTOLOAD = S_ready.AUTOLOAD',
        'S_final.CLASSNAMES = S_ready.CLASSNAMES', 'S_final.CLASSCONSTANTCACHE = S_ready.CLASSCONSTANTCACHE',
        '$test_outputs(S_final.EVENTS) = ' + text('B|S|L|AutoStringQuery58|I|autoload58-stop|99|1|1|constant|loader-name58|1699|Z|99'),
        *common.public('S_final')]
    return values


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__),
        str(Path(cast.__file__).relative_to(driver.ROOT)): sources.family.sha(cast.__file__)})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
