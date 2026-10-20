#!/usr/bin/env python3
"""Numeric unpack snapshots survive live-pack mutation and owned NULL cancellation."""
import json
import os
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import ini_set_owned_unpack_null_option_review_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64
MESSAGE = 'ini_set(): Passing null to parameter #1 ($option) of type string is deprecated'
PREFIX = r"""
dec $test_ini_owned_unpack_review_front(pstate, nat) : bool
def $test_ini_owned_unpack_review_front(S, 0) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN pvalue)]
def $test_ini_owned_unpack_review_front(S, 1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_call(S,pcallcontext) = (perrorcall)
  -- if perrorcall.RESUME = CONFIG_INI_NULL_RESULT pconfigcall
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_ini_owned_unpack_review_front(S, 2) = true
  -- if S.TODO = (THROW_VALUE porigin z) :: ptask_body*
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_call(S,pcallcontext) = (perrorcall)
  -- if perrorcall.RESUME = CONFIG_INI_NULL_RESULT pconfigcall
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_ini_owned_unpack_review_front(S, 3) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = CONFIG_INI_NULL_RESULT pconfigcall
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_ini_owned_unpack_review_front(S, 4) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET /\ pconfigcall.OWNER =/= eps
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_option),NAMED_SENT (KNOWN pvalue)]
  -- if $string_bytes(pvalue_option) = ($ptascii("precision"))
  -- if $string_bytes(pvalue) = ($ptascii("12"))
def $test_ini_owned_unpack_review_front(S, 5) = true
  -- if S.TODO = (CONFIG_UNPACK_NEXT pconfigcall (KNOWN (PARRAY n_pack)) 0) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET /\ pconfigcall.OWNER =/= eps
  -- if pconfigcall.INDEX = 0 /\ pconfigcall.SENT = eps
  -- if pconfigcall.PACKS = [pconfigpack]
def $test_ini_owned_unpack_review_front(S, n_stage) = false -- otherwise
dec $test_ini_owned_unpack_review_seek(pstate, nat, nat) : pstate
def $test_ini_owned_unpack_review_seek(S, n_stage, 0) = S
def $test_ini_owned_unpack_review_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_ini_owned_unpack_review_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_ini_owned_unpack_review_seek(S, n_stage, n) = $test_ini_owned_unpack_review_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_ini_owned_unpack_review_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def reach(state, start, stage):
    return [state + '_found = $test_ini_owned_unpack_review_seek(' + start + ',' + str(stage) + ',3000)',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_ini_owned_unpack_review_front(' + state + ',' + str(stage) + ')']


def unchanged(after, before, fields):
    return [after + '.' + field + ' = ' + before + '.' + field for field in fields.split()]


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)',
        state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)',
        state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def checks(program, path, name):
    assert name == 'strict-explicit-owned-unpack-null-keeps-captured-numeric-args'
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *reach('S_capture', 'S_initial', 5),
        'S_capture.TODO = (CONFIG_UNPACK_NEXT pconfigcall_capture (KNOWN (PARRAY n_pack)) 0) :: ptask_S*',
        'pconfigcall_capture.KIND = INTRINSIC_INI_SET', 'pconfigcall_capture.OWNER = (n_owner)',
        'pconfigcall_capture.INDEX = 0', 'pconfigcall_capture.SENT = eps', '~pconfigcall_capture.NAMED',
        'pconfigcall_capture.SELECTION = eps', 'pconfigcall_capture.PACKS = [pconfigpack]',
        'pconfigpack.INDEX = 0', 'pconfigpack.ARRAY = n_pack',
        'pconfigpack.ITEMS = [ENTRY (KINT 3) (DIRECT PNULL),ENTRY (KINT 7) (DIRECT pvalue_captured)]',
        'pvalue_captured = PSTRING_CARRIER (REQUEST_STRING n_candidate) ' + text('unpack-owned-value66'),
        '$string_carrier_valid(S_capture,pvalue_captured)',
        '$config_pack_source_valid(S_capture,pconfigcall_capture,pconfigpack)',
        '$config_unpack_valid(S_capture,pconfigcall_capture,KNOWN (PARRAY n_pack),0)',
        '$call_task_valid(S_capture,CONFIG_UNPACK_NEXT pconfigcall_capture (KNOWN (PARRAY n_pack)) 0)',
        'pconfigpack.ITEMS = $config_pack_capture(S_capture,S_capture.ARRAYS[n_pack].ITEMS)',
        '(HARRAY n_pack) <- S_capture.ALLOCATIONS',
        '$task_nodes(CONFIG_UNPACK_NEXT pconfigcall_capture (KNOWN (PARRAY n_pack)) 0) = [HOBJECT n_owner,HARRAY n_pack]',
        '$lookup(S_capture.ENV,' + text('pack') + ') = (n_pack_cell)',
        'S_capture.STORE[n_pack_cell] = DEFINED (PARRAY n_pack)',
        '$lookup(S_capture.ENV,' + text('call') + ') = (n_call)',
        'S_capture.STORE[n_call] = DEFINED (POBJECT n_live)',
        'S_capture.OBJECTS[n_live] = INTRINSICCLOSURE INTRINSIC_INI_GET', 'n_live =/= n_owner',
        '$lookup(S_capture.ENV,' + text('keep') + ') = (n_keep)',
        'S_capture.STORE[n_keep] = DEFINED (POBJECT n_owner)',
        '$lookup(S_capture.ENV,' + text('effects') + ') = (n_effects)',
        'S_capture.STORE[n_effects] = DEFINED (PINT 1)',
        '$lookup(S_capture.ENV,' + text('value') + ') = (n_value)',
        'S_capture.STORE[n_value] = DEFINED pvalue_live_before',
        '$string_bytes(pvalue_live_before) = (' + text('after-value66') + ')',
        'S_capture.PRECISIONINI = ' + text('7'), '$test_outputs(S_capture.EVENTS) = ' + text('B|V|'),
        *common.public('S_capture'), *common.step('S_first', 'S_capture'),
        'pconfigcall_first = pconfigcall_capture[.SENT = [NAMED_SENT (KNOWN PNULL)]]',
        'S_first.TODO = (CONFIG_UNPACK_NEXT pconfigcall_first (KNOWN (PARRAY n_pack)) 1) :: ptask_S*',
        '$config_unpack_valid(S_first,pconfigcall_first,KNOWN (PARRAY n_pack),1)',
        *common.step('S_second', 'S_first'),
        'pconfigcall_second = pconfigcall_capture[.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN pvalue_captured)]]',
        'S_second.TODO = (CONFIG_UNPACK_NEXT pconfigcall_second (KNOWN (PARRAY n_pack)) 2) :: ptask_S*',
        '$config_unpack_valid(S_second,pconfigcall_second,KNOWN (PARRAY n_pack),2)',
        *common.step('S_args', 'S_second'),
        'pconfigcall_S = pconfigcall_second[.INDEX = 1]',
        'S_args.TODO = (CONFIG_ARGS pconfigcall_S) :: ptask_S*',
        '$call_task_valid(S_args,CONFIG_ARGS pconfigcall_S)', *common.step('S', 'S_args'),
        'S.TODO = (CONFIG_INVOKE pconfigcall_S) :: ptask_S*',
        'pconfigcall_S.PACKS = [pconfigpack]', 'pconfigcall_S.INDEX = 1', '~pconfigcall_S.NAMED',
        '$intrinsic_count(S,pconfigcall_S.SITE) = (1)',
        '$intrinsic_argument(S,pconfigcall_S.SITE,0) = ((expression_pack,true,eps,pconfigpack.SITE,pconfigpack.LINE))',
        '$compiled_read(S,pconfigpack.SITE) = eps',
        '$config_source_replay(S,pconfigcall_S,pconfigcall_S[.INDEX = 0][.SENT = eps][.NAMED = false][.PACKS = eps],pconfigcall_S.PACKS) = ((pconfigcall_replayed,eps))',
        'pconfigcall_replayed = pconfigcall_S[.PACKS = eps]',
        '$config_ini_pack_known(S,pconfigpack.ITEMS,eps)',
        '~$config_ini_pack_known(S,pconfigpack.ITEMS,(PINT 1))',
        '$config_invoke_valid(S,pconfigcall_S)', '$config_ini_null_valid(S,pconfigcall_S)',
        '~$config_strict(S,pconfigcall_S)', '$exit_strict(S,pconfigcall_S.SITE)',
        '$config_method_receiver(S,pconfigcall_S)', '$exit_method_site(S,pconfigcall_S.SITE)',
        '$config_nodes(pconfigcall_S) = [HOBJECT n_owner]',
        '$task_nodes(CONFIG_INI_NULL_RESULT pconfigcall_S) = [HOBJECT n_owner]',
        '~((HARRAY n_pack) <- $config_nodes(pconfigcall_S))',
        'S.STORE[n_keep] = DEFINED (POBJECT n_owner)',
        'S.OBJECTS[n_owner] = INTRINSICCLOSURE INTRINSIC_INI_SET',
        '(HOBJECT n_owner) <- $gc_physical_nodes(S.GC.BUFFER)',
        '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
        '$lookup(S.ENV,' + text('warnings') + ') = (n_warnings)', 'S.STORE[n_warnings] = DEFINED (PINT 0)',
        '$lookup(S.ENV,' + text('saved') + ') = (n_saved)', 'S.STORE[n_saved] = DEFINED PNULL',
        *unchanged('S', 'S_capture', 'STORE ENV EVENTS PRECISIONINI USERCONSTANTS'), *common.public('S'),
        *common.step('S_dispatch', 'S'),
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_deprecated) :: ptask_S*',
        'perrorcall_deprecated.RESUME = CONFIG_INI_NULL_RESULT pconfigcall_S',
        'perrorcall_deprecated.LEVEL = 8192', 'perrorcall_deprecated.MESSAGE = ' + text(MESSAGE),
        'perrorcall_deprecated.MESSAGE = $config_ini_null_message(pconfigcall_S)',
        'perrorcall_deprecated.EVENT = DIAGNOSTIC "Deprecated" perrorcall_deprecated.MESSAGE pconfigcall_S.LINE',
        'perrorcall_deprecated.SITE = pconfigcall_S.SITE', 'perrorcall_deprecated.LINE = pconfigcall_S.LINE',
        '$error_call_valid(S_dispatch,perrorcall_deprecated)',
        *unchanged('S_dispatch', 'S', 'STORE ENV ARRAYS OBJECTS OBJECTPROPS USERCONSTANTS STRINGDATA EVENTS SELECTEDCALLS PRECISIONINI'),
        *common.public('S_dispatch'), *reach('S_handler', 'S_dispatch', 1),
        'S_handler.CURRENT = (pcallcontext_handler)', '$error_context_valid(S_handler,pcallcontext_handler)',
        '$error_context_trigger(S_handler,pcallcontext_handler) = (pconfigcall_S)',
        '$error_handler_trace_values(S_handler,pcallcontext_handler,pconfigcall_S) = [PNULL,pvalue_captured]',
        *common.public('S_handler'), *reach('S_throw', 'S_handler', 2),
        'S_throw.TODO = (THROW_VALUE porigin_throw z_throw) :: ptask_body*',
        'S_throw.CURRENT = (pcallcontext_handler)', 'S_throw.FRAMES = pframe_call :: pframe_outer*',
        'pframe_call.CONTEXT = S.CURRENT', 'pframe_call.LOCALS = ($active_table(S))',
        'pframe_call.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_S*',
        'perrorcall_entered.RESUME = CONFIG_INI_NULL_RESULT pconfigcall_S',
        'S_throw.STORE[n_saved] = DEFINED (POBJECT n_exception)',
        'S_throw.OBJECTS[n_exception] = THROWABLE pthrowable', 'pthrowable.KIND = "Exception"',
        '$string_bytes($throwable_field(S_throw,n_exception,"message")) = (' + text('unpack-owned66-stop') + ')',
        '$throwable_field(S_throw,n_exception,"previous") = PNULL',
        '$throwable_field(S_throw,n_exception,"trace") = PARRAY n_trace',
        'S_throw.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_handler)),ENTRY (KINT 1) (DIRECT (PARRAY n_api)),ENTRY (KINT 2) (DIRECT (PARRAY n_invoke)),ENTRY (KINT 3) (DIRECT (PARRAY n_caller))]',
        '$trace_array_field(S_throw,n_handler,' + text('function') + ') = PSTRING ' + text('iniOwnedUnpackReviewDeprecated66'),
        '$trace_array_field(S_throw,n_api,' + text('function') + ') = PSTRING ' + text('ini_set'),
        '$trace_array_field(S_throw,n_api,' + text('line') + ') = PINT pconfigcall_S.LINE',
        '$trace_array_field(S_throw,n_api,' + text('args') + ') = PARRAY n_args',
        'S_throw.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT PNULL),ENTRY (KINT 1) (DIRECT pvalue_captured)]',
        '$node_children(S_throw,HARRAY n_args) = eps',
        '$trace_array_field(S_throw,n_invoke,' + text('function') + ') = PSTRING ' + text('__invoke'),
        '$trace_array_field(S_throw,n_invoke,' + text('class') + ') = PSTRING ' + text('Closure'),
        '$trace_array_field(S_throw,n_invoke,' + text('type') + ') = PSTRING ' + text('->'),
        '$trace_array_field(S_throw,n_invoke,' + text('line') + ') = PINT pconfigcall_S.LINE',
        '$trace_array_field(S_throw,n_invoke,' + text('args') + ') = PARRAY n_invoke_args',
        'S_throw.ARRAYS[n_invoke_args].ITEMS = [ENTRY (KINT 0) (DIRECT PNULL),ENTRY (KINT 1) (DIRECT pvalue_captured)]',
        '$node_children(S_throw,HARRAY n_invoke_args) = eps',
        '$trace_array_field(S_throw,n_caller,' + text('function') + ') = PSTRING ' + text('iniOwnedUnpackReviewCaller66'),
        'S_throw.STORE[n_keep] = DEFINED (POBJECT n_owner)',
        'S_throw.OBJECTS[n_owner] = INTRINSICCLOSURE INTRINSIC_INI_SET',
        'S_throw.STORE[n_result] = DEFINED (PINT 99)', 'S_throw.STORE[n_effects] = DEFINED (PINT 1)',
        'S_throw.STORE[n_warnings] = DEFINED (PINT 1)', 'S_throw.PRECISIONINI = ' + text('10'),
        'S_throw.USERCONSTANTS = [puserconstant_sibling]', 'puserconstant_sibling.NAME = ' + text('SOURCE66PEER'),
        'puserconstant_sibling.VALUE = PINT 2197', 'puserconstant_sibling.CLASS = PVSCALAR',
        'S_throw.STORE[n_pack_cell] = DEFINED (PARRAY n_pack_live)',
        '$entry_lookup(S_throw.ARRAYS[n_pack_live].ITEMS,KINT 3) = (DIRECT pvalue_pack_option)',
        '$entry_lookup(S_throw.ARRAYS[n_pack_live].ITEMS,KINT 7) = (DIRECT pvalue_pack_value)',
        '$string_bytes(pvalue_pack_option) = (' + text('precision') + ')',
        '$string_bytes(pvalue_pack_value) = (' + text('handler-pack66') + ')',
        '$config_pack_capture(S_throw,S_throw.ARRAYS[n_pack_live].ITEMS) =/= pconfigpack.ITEMS',
        '$test_outputs(S_throw.EVENTS) = ' + text('B|V|D|8192|' + MESSAGE + '|'),
        *unchanged('S_throw', 'S', 'AUTOLOAD CLASSNAMES CLASSCONSTANTCACHE FILEINCLUDEPATH'),
        *common.public('S_throw'), *common.step('S_throwing', 'S_throw'),
        'S_throwing.TODO = (THROW_SEARCH n_exception) :: ptask_body*', *reach('S_thrown', 'S_throwing', 3),
        'S_thrown.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_S*',
        'S_thrown.CURRENT = S.CURRENT', 'S_thrown.ENV = S.ENV',
        'S_thrown.STORE[n_saved] = DEFINED (POBJECT n_exception)',
        'S_thrown.STORE[n_result] = DEFINED (PINT 99)', 'S_thrown.USERCONSTANTS = [puserconstant_sibling]',
        'S_thrown.PRECISIONINI = ' + text('10'), '$config_ini_null_valid(S_thrown,pconfigcall_S)',
        *common.public('S_thrown'),
        'S_discard = S_thrown[.TODO = (THROW_SEARCH n_exception) :: ptask_S*]',
        'S_expected = $error_handler_restore($identity_read_discard(S_discard,perrorcall_entered.RESUME),perrorcall_entered.CALLBACK)',
        '$error_read_discard(S_expected,perrorcall_entered.RESUME) = S_expected',
        *common.step('S_after', 'S_thrown'), 'S_after = S_expected',
        '$throwable_live(S_after,n_exception)', 'S_after.STORE[n_result] = DEFINED (PINT 99)',
        'S_after.STORE[n_keep] = DEFINED (POBJECT n_owner)', *common.public('S_after')]
    for variable, spelling in [('call', 'constant'), ('value', 'handler-value66')]:
        values += ['S_thrown.STORE[n_' + variable + '] = DEFINED pvalue_handler_' + variable,
            '$string_bytes(pvalue_handler_' + variable + ') = (' + text(spelling) + ')']
    for field in ('.SITE = PORIGIN 0 eps', '.LINE = $(pconfigcall_S.LINE + 1)',
            '.SELECTION = (|S.SELECTEDCALLS|)', '.INDEX = 2', '.OWNER = (n_live)', '.NAMED = true',
            '.KIND = INTRINSIC_INI_GET', '.PACKS = eps', '.PACKS = [pconfigpack,pconfigpack]'):
        values += ['~$config_ini_null_valid(S,pconfigcall_S[' + field + '])']
    for field in ('.INDEX = 1', '.SITE = PORIGIN 0 eps', '.LINE = $(pconfigpack.LINE + 1)', '.ARRAY = |S.ARRAYS|'):
        values += ['~$config_ini_null_valid(S,pconfigcall_S[.PACKS = [pconfigpack[' + field + ']]])']
    values += ['~$config_ini_null_valid(S,pconfigcall_S[.OWNER = eps])',
        '~$config_ini_null_valid(S,pconfigcall_S[.OWNER = (|S.OBJECTS|)])',
        '~$config_ini_null_valid(S[.ALLOCATIONS = eps],pconfigcall_S)',
        '~$config_ini_null_valid(S,pconfigcall_S[.SENT = pconfigcall_S.SENT[0:1]])',
        '~$config_ini_null_valid(S,pconfigcall_S[.SENT = pconfigcall_S.SENT ++ [NAMED_SENT (KNOWN PNULL)]])',
        'pconfigpack_named = pconfigpack[.ITEMS = [ENTRY (KSTRING ' + text('option') + ') (DIRECT PNULL),ENTRY (KSTRING ' + text('value') + ') (DIRECT pvalue_captured)]]',
        'pconfigcall_named = pconfigcall_S[.NAMED = true][.PACKS = [pconfigpack_named]]',
        '$config_invoke_valid(S,pconfigcall_named)', '$config_ini_null_valid(S,pconfigcall_named)',
        'pvalue_bad = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ' + text('unpack-owned-value66'),
        '~$string_carrier_valid(S,pvalue_bad)', '~$config_ini_quiet_value(S,pvalue_bad)',
        'pconfigpack_bad = pconfigpack[.ITEMS = [ENTRY (KINT 3) (DIRECT PNULL),ENTRY (KINT 7) (DIRECT pvalue_bad)]]',
        'pconfigcall_bad = pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,1,KNOWN pvalue_bad)][.PACKS = [pconfigpack_bad]]',
        '$config_invoke_valid(S,pconfigcall_bad)', '~$config_ini_null_valid(S,pconfigcall_bad)',
        '~$config_ini_null_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,1,KNOWN pvalue_bad)])']
    for value in ['PSTRING ' + text('unpack-owned-value66'), 'PFLOAT 9221120237041090560', 'PARRAY 0', 'POBJECT 0']:
        values += ['~$config_ini_quiet_value(S,' + value + ')']
    for field in ('.LEVEL = 2', '.MESSAGE = ' + text('changed'), '.LINE = $(perrorcall_deprecated.LINE + 1)',
            '.EVENT = DIAGNOSTIC "Deprecated" perrorcall_deprecated.MESSAGE $(perrorcall_deprecated.LINE + 1)'):
        values += ['~$error_call_valid(S_expected,perrorcall_deprecated[' + field + '])']
    values += [*budget('S_capture'), *budget('S_thrown'), *reach('S_recovery', 'S_after', 4),
        'S_recovery.TODO = (CONFIG_INVOKE pconfigcall_recovery) :: ptask_recovery*',
        'pconfigcall_recovery.OWNER = (n_owner)', 'pconfigcall_recovery.SELECTION = eps',
        'pconfigcall_recovery.PACKS = eps', '~pconfigcall_recovery.NAMED',
        'pconfigcall_recovery.SENT = [NAMED_SENT (KNOWN pvalue_option),NAMED_SENT (KNOWN pvalue_precision)]',
        '$string_bytes(pvalue_option) = (' + text('precision') + ')',
        '$string_bytes(pvalue_precision) = (' + text('12') + ')',
        '$config_invoke_valid(S_recovery,pconfigcall_recovery)',
        '~$config_method_receiver(S_recovery,pconfigcall_recovery)', '$config_strict(S_recovery,pconfigcall_recovery)',
        '~$config_ini_null_valid(S_recovery,pconfigcall_recovery)',
        'S_recovery.STORE[n_keep] = DEFINED (POBJECT n_owner)',
        'S_recovery.OBJECTS[n_owner] = INTRINSICCLOSURE INTRINSIC_INI_SET',
        'S_recovery.PRECISIONINI = ' + text('10'), 'S_recovery.ERRORHANDLER.CALLBACK = eps',
        *common.public('S_recovery'), *common.step('S_recovered', 'S_recovery'),
        'S_recovered.TODO = ptask_recovery*', 'S_recovered.RESULT = KNOWN pvalue_old_precision',
        '$string_bytes(pvalue_old_precision) = (' + text('10') + ')',
        'S_recovered.PRECISIONINI = ' + text('12'),
        *unchanged('S_recovered', 'S_recovery', 'STORE ENV OBJECTS USERCONSTANTS SELECTEDCALLS EVENTS'),
        *common.public('S_recovered'), 'S_final = $drive_steps(S_recovered,3000)',
        'S_final.COMPLETION = NORMAL', 'S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.USERCONSTANTS = [puserconstant_sibling]', 'S_final.PRECISIONINI = ' + text('12'),
        'S_final.ERRORHANDLER.CALLBACK = eps',
        *unchanged('S_final', 'S', 'AUTOLOAD CLASSNAMES CLASSCONSTANTCACHE FILEINCLUDEPATH'),
        '$test_outputs(S_final.EVENTS) = ' + text('B|V|D|8192|' + MESSAGE + '|I|N|unpack-owned-value66|99|1|1|constant|handler-value66|precision|handler-pack66|10|2197|Z|R|10|12|99'),
        *common.public('S_final')]
    return values


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
