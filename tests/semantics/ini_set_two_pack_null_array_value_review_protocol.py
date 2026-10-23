#!/usr/bin/env python3
"""Separate unpack snapshots retain the early array through COW and throw."""
import json
import os
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import ini_set_two_pack_null_array_value_review_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64
MESSAGE = 'ini_set(): Passing null to parameter #1 ($option) of type string is deprecated'
PREFIX = r"""
dec $test_ini_two_pack_review_front(pstate, nat) : bool
def $test_ini_two_pack_review_front(S, 0) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (PARRAY n_array))]
def $test_ini_two_pack_review_front(S, 1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_call(S,pcallcontext) = (perrorcall)
  -- if perrorcall.RESUME = CONFIG_INI_NULL_RESULT pconfigcall
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_ini_two_pack_review_front(S, 2) = true
  -- if S.TODO = (THROW_VALUE porigin z) :: ptask_body*
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_call(S,pcallcontext) = (perrorcall)
  -- if perrorcall.RESUME = CONFIG_INI_NULL_RESULT pconfigcall
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_ini_two_pack_review_front(S, 3) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = CONFIG_INI_NULL_RESULT pconfigcall
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_ini_two_pack_review_front(S, 4) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_option),NAMED_SENT (KNOWN pvalue)]
  -- if $string_bytes(pvalue_option) = ($ptascii("precision"))
  -- if $string_bytes(pvalue) = ($ptascii("12"))
def $test_ini_two_pack_review_front(S, 5) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.INDEX = 0
  -- if pconfigcall.SENT = eps
def $test_ini_two_pack_review_front(S, 6) = true
  -- if S.TODO = (CONFIG_UNPACK_NEXT pconfigcall (KNOWN (PARRAY n_pack)) 0) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.INDEX = 0
def $test_ini_two_pack_review_front(S, 7) = true
  -- if S.TODO = (CONFIG_UNPACK_NEXT pconfigcall (KNOWN (PARRAY n_pack)) 0) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.INDEX = 1
def $test_ini_two_pack_review_front(S, n_stage) = false -- otherwise
dec $test_ini_two_pack_review_seek(pstate, nat, nat) : pstate
def $test_ini_two_pack_review_seek(S, n_stage, 0) = S
def $test_ini_two_pack_review_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_ini_two_pack_review_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_ini_two_pack_review_seek(S, n_stage, n) = $test_ini_two_pack_review_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_ini_two_pack_review_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def reach(state, start, stage):
    return [state + '_found = $test_ini_two_pack_review_seek(' + start + ',' + str(stage) + ',3000)',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_ini_two_pack_review_front(' + state + ',' + str(stage) + ')']


def unchanged(after, before, fields):
    return [after + '.' + field + ' = ' + before + '.' + field for field in fields.split()]


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)',
        state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)',
        state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def checks(program, path, name):
    assert name == 'selected-two-pack-array-captured-before-option-pack-and-cow'
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *reach('S_pre', 'S_initial', 5),
        'S_pre.TODO = (CONFIG_ARGS pconfigcall_pre) :: ptask_S*',
        'pconfigcall_pre.KIND = INTRINSIC_INI_SET', 'pconfigcall_pre.OWNER = eps',
        'pconfigcall_pre.SELECTION = (n_selection)', 'pconfigcall_pre.INDEX = 0',
        'pconfigcall_pre.PACKS = eps', '~pconfigcall_pre.NAMED', 'pconfigcall_pre.SENT = eps',
        '$call_task_valid(S_pre,CONFIG_ARGS pconfigcall_pre)', '$config_pending_valid(S_pre,pconfigcall_pre,true)',
        '$lookup(S_pre.ENV,' + text('value') + ') = (n_value)', 'S_pre.STORE[n_value] = DEFINED (PARRAY n_array)',
        'S_pre.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_leaf)]',
        'pvalue_leaf = PSTRING_CARRIER (REQUEST_STRING n_candidate) ' + text('two-pack-peer86'),
        '$string_carrier_valid(S_pre,pvalue_leaf)', '(HARRAY n_array) <- S_pre.ALLOCATIONS',
        '$lookup(S_pre.ENV,' + text('arrayKeep') + ') = (n_array_keep)', 'S_pre.STORE[n_array_keep] = DEFINED (PARRAY n_array)',
        '$lookup(S_pre.ENV,' + text('valuePack') + ') = (n_pack_cell)', 'S_pre.STORE[n_pack_cell] = DEFINED (PARRAY n_outer)',
        '$lookup(S_pre.ENV,' + text('packOld') + ') = (n_pack_old)', 'S_pre.STORE[n_pack_old] = DEFINED (PARRAY n_outer)',
        'n_outer =/= n_array', '(HARRAY n_outer) <- S_pre.ALLOCATIONS',
        'pentry_value* = [ENTRY (KSTRING ' + text('value') + ') (DIRECT (PARRAY n_array))]',
        'S_pre.ARRAYS[n_outer].ITEMS = pentry_value*', '$node_children(S_pre,HARRAY n_outer) = [HARRAY n_array]',
        '$lookup(S_pre.ENV,' + text('call') + ') = (n_call)', 'S_pre.STORE[n_call] = DEFINED pvalue_keep',
        '$lookup(S_pre.ENV,' + text('keep') + ') = (n_keep)', 'S_pre.STORE[n_keep] = DEFINED pvalue_keep',
        '$string_bytes(pvalue_keep) = (' + text('InI_SeT') + ')',
        '$(n_selection < |S_pre.SELECTEDCALLS|)', 'S_pre.SELECTEDCALLS[n_selection] = pselectedcall',
        'pselectedcall.NONCE = n_selection', 'pselectedcall.KIND = INTRINSIC_INI_SET',
        'pselectedcall.SITE = pconfigcall_pre.SITE', 'pselectedcall.LINE = pconfigcall_pre.LINE',
        'pselectedcall.DEPTH = |S_pre.FRAMES|',
        'pselectedcall.ORIGINAL = ' + text('InI_SeT'), 'pselectedcall.LOOKUP = ' + text('InI_SeT'),
        '$selected_entry_valid(S_pre,pselectedcall)', '$selected_task_count(S_pre.TODO,n_selection) = 1',
        '$lookup(S_pre.ENV,' + text('effects') + ') = (n_effects)', 'S_pre.STORE[n_effects] = DEFINED (PINT 0)',
        '$lookup(S_pre.ENV,' + text('warnings') + ') = (n_warnings)', 'S_pre.STORE[n_warnings] = DEFINED (PINT 0)',
        '$lookup(S_pre.ENV,' + text('saved') + ') = (n_saved)', 'S_pre.STORE[n_saved] = DEFINED PNULL',
        '$lookup(S_pre.ENV,' + text('result') + ') = (n_result)', 'S_pre.STORE[n_result] = DEFINED (PINT 99)',
        '$config_nodes(pconfigcall_pre) = eps', '$test_outputs(S_pre.EVENTS) = ' + text('B|'),
        *common.public('S_pre'), *reach('S_capture', 'S_pre', 6),
        'S_capture.TODO = (CONFIG_UNPACK_NEXT pconfigcall_capture (KNOWN (PARRAY n_outer)) 0) :: ptask_S*',
        'pconfigcall_capture.PACKS = [pconfigpack_value]',
        'pconfigcall_capture = pconfigcall_pre[.PACKS = [pconfigpack_value]]',
        'pconfigpack_value.INDEX = 0', 'pconfigpack_value.ARRAY = n_outer', 'pconfigpack_value.ITEMS = pentry_value*',
        '$config_pack_source_valid(S_capture,pconfigcall_capture,pconfigpack_value)',
        '$config_unpack_valid(S_capture,pconfigcall_capture,KNOWN (PARRAY n_outer),0)',
        '$call_task_valid(S_capture,CONFIG_UNPACK_NEXT pconfigcall_capture (KNOWN (PARRAY n_outer)) 0)',
        'pentry_value* = $config_pack_capture(S_capture,S_capture.ARRAYS[n_outer].ITEMS)',
        '$config_nodes(pconfigcall_capture) = eps',
        '$task_nodes(CONFIG_UNPACK_NEXT pconfigcall_capture (KNOWN (PARRAY n_outer)) 0) = [HARRAY n_outer]',
        *unchanged('S_capture','S_pre','STORE ENV EVENTS'), *common.public('S_capture'),
        *common.step('S_first', 'S_capture'),
        'pconfigcall_first = pconfigcall_capture[.NAMED = true][.SENT = [NAMED_HOLE,NAMED_SENT (KNOWN (PARRAY n_array))]]',
        'S_first.TODO = (CONFIG_UNPACK_NEXT pconfigcall_first (KNOWN (PARRAY n_outer)) 1) :: ptask_S*',
        '$config_unpack_valid(S_first,pconfigcall_first,KNOWN (PARRAY n_outer),1)',
        '$config_nodes(pconfigcall_first) = [HARRAY n_array]',
        '$task_nodes(CONFIG_UNPACK_NEXT pconfigcall_first (KNOWN (PARRAY n_outer)) 1) = [HARRAY n_array,HARRAY n_outer]',
        *common.public('S_first'), *common.step('S_between','S_first'),
        'pconfigcall_between = pconfigcall_first[.INDEX = 1]',
        'S_between.TODO = (CONFIG_ARGS pconfigcall_between) :: ptask_S*',
        '$config_pending_valid(S_between,pconfigcall_between,true)',
        '$task_nodes(CONFIG_ARGS pconfigcall_between) = [HARRAY n_array]',
        'S_between.STORE[n_value] = DEFINED (PARRAY n_array)',
        'S_between.STORE[n_array_keep] = DEFINED (PARRAY n_array)',
        'S_between.STORE[n_pack_cell] = DEFINED (PARRAY n_outer)',
        '$test_outputs(S_between.EVENTS) = ' + text('B|'), *common.public('S_between'),
        *reach('S_option_capture','S_between',7),
        'S_option_capture.TODO = (CONFIG_UNPACK_NEXT pconfigcall_option (KNOWN (PARRAY n_option_outer)) 0) :: ptask_S*',
        'pconfigcall_option.PACKS = [pconfigpack_value,pconfigpack_option]',
        'pconfigcall_option = pconfigcall_between[.PACKS = [pconfigpack_value,pconfigpack_option]]',
        'pconfigpack_option.INDEX = 1', 'pconfigpack_option.ARRAY = n_option_outer',
        'pentry_option* = [ENTRY (KSTRING ' + text('option') + ') (DIRECT PNULL)]',
        'pconfigpack_option.ITEMS = pentry_option*', 'S_option_capture.ARRAYS[n_option_outer].ITEMS = pentry_option*',
        'n_option_outer =/= n_outer', 'n_option_outer =/= n_array',
        '(HARRAY n_option_outer) <- S_option_capture.ALLOCATIONS',
        '$config_pack_source_valid(S_option_capture,pconfigcall_option,pconfigpack_option)',
        '$config_unpack_valid(S_option_capture,pconfigcall_option,KNOWN (PARRAY n_option_outer),0)',
        '$task_nodes(CONFIG_UNPACK_NEXT pconfigcall_option (KNOWN (PARRAY n_option_outer)) 0) = [HARRAY n_array,HARRAY n_option_outer]',
        'S_option_capture.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_leaf)]',
        'S_option_capture.ARRAYS[n_outer].ITEMS = pentry_value*',
        'S_option_capture.STORE[n_pack_old] = DEFINED (PARRAY n_outer)',
        'S_option_capture.STORE[n_pack_cell] = DEFINED (PARRAY n_pack_live)', 'n_pack_live =/= n_outer',
        'S_option_capture.ARRAYS[n_pack_live].ITEMS = [ENTRY (KSTRING ' + text('value') + ') (DIRECT (PINT 0))]',
        'S_option_capture.STORE[n_array_keep] = DEFINED (PARRAY n_option_array)', 'n_option_array =/= n_array',
        'S_option_capture.ARRAYS[n_option_array].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_option_leaf)]',
        '$string_bytes(pvalue_option_leaf) = (' + text('option-array86') + ')',
        'S_option_capture.STORE[n_value] = DEFINED (PINT 997)', 'S_option_capture.STORE[n_effects] = DEFINED (PINT 1)',
        'S_option_capture.STORE[n_call] = DEFINED pvalue_live_call',
        '$string_bytes(pvalue_live_call) = (' + text('ini_get') + ')',
        'S_option_capture.STORE[n_keep] = DEFINED pvalue_keep',
        'S_option_capture.SELECTEDCALLS[n_selection] = pselectedcall', 'S_option_capture.PRECISIONINI = ' + text('14'),
        '$test_outputs(S_option_capture.EVENTS) = ' + text('B|O|'), *common.public('S_option_capture'),
        *common.step('S_second','S_option_capture'),
        'pconfigcall_second = pconfigcall_option[.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (PARRAY n_array))]]',
        'S_second.TODO = (CONFIG_UNPACK_NEXT pconfigcall_second (KNOWN (PARRAY n_option_outer)) 1) :: ptask_S*',
        '$config_unpack_valid(S_second,pconfigcall_second,KNOWN (PARRAY n_option_outer),1)',
        '$task_nodes(CONFIG_UNPACK_NEXT pconfigcall_second (KNOWN (PARRAY n_option_outer)) 1) = [HARRAY n_array,HARRAY n_option_outer]',
        *common.public('S_second'), *common.step('S_args','S_second'),
        'pconfigcall_S = pconfigcall_second[.INDEX = 2]', 'S_args.TODO = (CONFIG_ARGS pconfigcall_S) :: ptask_S*',
        '$call_task_valid(S_args,CONFIG_ARGS pconfigcall_S)', *common.step('S','S_args'),
        'S.TODO = (CONFIG_INVOKE pconfigcall_S) :: ptask_S*',
        '$config_invoke_valid(S,pconfigcall_S)', '$config_selected_valid(S,pconfigcall_S)',
        'pconfigcall_S.PACKS = [pconfigpack_value,pconfigpack_option]', 'pconfigcall_S.INDEX = 2', 'pconfigcall_S.NAMED',
        '$intrinsic_count(S,pconfigcall_S.SITE) = (2)',
        '$intrinsic_argument(S,pconfigcall_S.SITE,0) = ((expression_value_pack,true,eps,pconfigpack_value.SITE,pconfigpack_value.LINE))',
        '$intrinsic_argument(S,pconfigcall_S.SITE,1) = ((expression_option_pack,true,eps,pconfigpack_option.SITE,pconfigpack_option.LINE))',
        '$compiled_read(S,pconfigpack_value.SITE) = eps', '$compiled_read(S,pconfigpack_option.SITE) = eps',
        '$config_source_replay(S,pconfigcall_S,pconfigcall_S[.INDEX = 0][.SENT = eps][.NAMED = false][.PACKS = eps],pconfigcall_S.PACKS) = ((pconfigcall_replayed,eps))',
        'pconfigcall_replayed = pconfigcall_S[.PACKS = eps]',
        '$config_ini_pack_known(S,pentry_value*,eps)', '$config_ini_pack_known(S,pentry_option*,eps)',
        '~$config_ini_pack_known(S,pentry_value*,(PINT 1))',
        '$config_ini_rejected_array(S,n_array)', '$config_ini_null_valid(S,pconfigcall_S)',
        '~$config_ini_quiet_value(S,PARRAY n_array)', '~$config_strict(S,pconfigcall_S)',
        '~$config_method_receiver(S,pconfigcall_S)', '~$exit_method_site(S,pconfigcall_S.SITE)', '~$exit_strict(S,pconfigcall_S.SITE)',
        'pconfigcall_S.SELECTION = (n_selection)', 'S.SELECTEDCALLS[n_selection] = pselectedcall',
        '$config_nodes(pconfigcall_S) = [HARRAY n_array]',
        '$task_nodes(CONFIG_INI_NULL_RESULT pconfigcall_S) = [HARRAY n_array]',
        '~((HARRAY n_outer) <- $config_nodes(pconfigcall_S))',
        '~((HARRAY n_option_outer) <- $config_nodes(pconfigcall_S))', '$node_children(S,HARRAY n_array) = eps',
        'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_leaf)]',
        'S.ARRAYS[n_outer].ITEMS = pentry_value*', 'S.STORE[n_pack_old] = DEFINED (PARRAY n_outer)',
        'S.STORE[n_pack_cell] = DEFINED (PARRAY n_pack_live)', '$node_children(S,HARRAY n_pack_live) = eps',
        'S.STORE[n_keep] = DEFINED pvalue_keep', 'S.PRECISIONINI = ' + text('14'),
        'S.USERCONSTANTS = eps', 'S.CURRENT = eps', 'S.FRAMES = eps',
        *unchanged('S','S_option_capture','STORE ENV EVENTS PRECISIONINI USERCONSTANTS'),
        '$test_outputs(S.EVENTS) = ' + text('B|O|'), *common.public('S'),
        *common.step('S_dispatch','S'),
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_deprecated) :: ptask_S*',
        'perrorcall_deprecated.RESUME = CONFIG_INI_NULL_RESULT pconfigcall_S',
        'perrorcall_deprecated.LEVEL = 8192', 'perrorcall_deprecated.MESSAGE = ' + text(MESSAGE),
        'perrorcall_deprecated.MESSAGE = $config_ini_null_message(pconfigcall_S)',
        'perrorcall_deprecated.EVENT = DIAGNOSTIC "Deprecated" perrorcall_deprecated.MESSAGE pconfigcall_S.LINE',
        'perrorcall_deprecated.SITE = pconfigcall_S.SITE', 'perrorcall_deprecated.LINE = pconfigcall_S.LINE',
        '$error_call_valid(S_dispatch,perrorcall_deprecated)',
        *unchanged('S_dispatch','S','STORE ENV ARRAYS OBJECTS OBJECTPROPS USERCONSTANTS STRINGDATA EVENTS SELECTEDCALLS PRECISIONINI'),
        *common.public('S_dispatch'), *reach('S_handler','S_dispatch',1),
        'S_handler.CURRENT = (pcallcontext_handler)', '$error_context_valid(S_handler,pcallcontext_handler)',
        '$error_context_trigger(S_handler,pcallcontext_handler) = (pconfigcall_S)',
        '$error_handler_trace_values(S_handler,pcallcontext_handler,pconfigcall_S) = [PNULL,PARRAY n_array]',
        *common.public('S_handler'), *reach('S_throw','S_handler',2),
        'S_throw.TODO = (THROW_VALUE porigin_throw z_throw) :: ptask_body*',
        'S_throw.CURRENT = (pcallcontext_handler)', 'S_throw.FRAMES = [pframe_call]',
        'pframe_call.CONTEXT = eps', 'pframe_call.LOCALS = eps',
        'pframe_call.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_S*',
        'perrorcall_entered.RESUME = CONFIG_INI_NULL_RESULT pconfigcall_S',
        'S_throw.STORE[n_saved] = DEFINED (POBJECT n_exception)',
        'S_throw.OBJECTS[n_exception] = THROWABLE pthrowable', 'pthrowable.KIND = "Exception"',
        '$string_bytes($throwable_field(S_throw,n_exception,"message")) = (' + text('two-pack-null-array86-stop') + ')',
        '$throwable_field(S_throw,n_exception,"previous") = PNULL',
        '$throwable_field(S_throw,n_exception,"trace") = PARRAY n_trace',
        'S_throw.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_handler)),ENTRY (KINT 1) (DIRECT (PARRAY n_api))]',
        '$trace_array_field(S_throw,n_handler,' + text('function') + ') = PSTRING ' + text('iniTwoPackNullArrayReviewDeprecated86'),
        '$trace_array_field(S_throw,n_api,' + text('function') + ') = PSTRING ' + text('ini_set'),
        '$trace_array_field(S_throw,n_api,' + text('line') + ') = PINT pconfigcall_S.LINE',
        '$trace_array_field(S_throw,n_api,' + text('args') + ') = PARRAY n_args',
        'S_throw.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT PNULL),ENTRY (KINT 1) (DIRECT (PARRAY n_array))]',
        '$node_children(S_throw,HARRAY n_args) = [HARRAY n_array]',
        'S_throw.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_leaf)]',
        '$string_carrier_valid(S_throw,pvalue_leaf)', '(HARRAY n_array) <- S_throw.ALLOCATIONS',
        'S_throw.STORE[n_pack_old] = DEFINED (PARRAY n_outer)', 'S_throw.STORE[n_keep] = DEFINED pvalue_keep',
        'S_throw.STORE[n_result] = DEFINED (PINT 99)', 'S_throw.STORE[n_effects] = DEFINED (PINT 1)',
        'S_throw.STORE[n_warnings] = DEFINED (PINT 1)', 'S_throw.STORE[n_value] = DEFINED (PINT 123)',
        'S_throw.PRECISIONINI = ' + text('10'),
        'S_throw.USERCONSTANTS = [puserconstant_sibling]', 'puserconstant_sibling.NAME = ' + text('SOURCE86PEER'),
        'puserconstant_sibling.VALUE = PINT 3479', 'puserconstant_sibling.CLASS = PVSCALAR',
        'S_throw.STORE[n_array_keep] = DEFINED (PARRAY n_mutated)', 'n_mutated =/= n_array',
        'S_throw.ARRAYS[n_mutated].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_mutated)]',
        '$string_bytes(pvalue_mutated) = (' + text('handler-array86') + ')',
        'S_throw.ARRAYS[n_outer].ITEMS = pentry_value*',
        '$node_children(S_throw,HARRAY n_outer) = [HARRAY n_array]',
        'S_throw.STORE[n_pack_cell] = DEFINED (PARRAY n_pack_live)',
        'S_throw.ARRAYS[n_pack_live].ITEMS = [ENTRY (KSTRING ' + text('value') + ') (DIRECT (PINT 0))]',
        '$config_pack_capture(S_throw,S_throw.ARRAYS[n_pack_live].ITEMS) =/= pconfigpack_value.ITEMS',
        '(HARRAY n_array) <- $gc_physical_nodes(S_throw.GC.BUFFER)',
        '$test_outputs(S_throw.EVENTS) = ' + text('B|O|D|8192|' + MESSAGE + '|'),
        *unchanged('S_throw','S','AUTOLOAD CLASSNAMES CLASSCONSTANTCACHE FILEINCLUDEPATH'),
        *common.public('S_throw'), *common.step('S_throwing','S_throw'),
        'S_throwing.TODO = (THROW_SEARCH n_exception) :: ptask_body*', *reach('S_thrown','S_throwing',3),
        'S_thrown.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_S*',
        'S_thrown.CURRENT = S.CURRENT', 'S_thrown.ENV = S.ENV',
        'S_thrown.STORE[n_saved] = DEFINED (POBJECT n_exception)',
        'S_thrown.STORE[n_result] = DEFINED (PINT 99)', 'S_thrown.USERCONSTANTS = [puserconstant_sibling]',
        'S_thrown.PRECISIONINI = ' + text('10'), '$config_ini_null_valid(S_thrown,pconfigcall_S)',
        '(HARRAY n_array) <- $gc_physical_nodes(S_thrown.GC.BUFFER)',
        'S_thrown.STORE[n_keep] = DEFINED pvalue_keep', *common.public('S_thrown'),
        'S_discard = S_thrown[.TODO = (THROW_SEARCH n_exception) :: ptask_S*]',
        'S_expected = $error_handler_restore($identity_read_discard(S_discard,perrorcall_entered.RESUME),perrorcall_entered.CALLBACK)',
        '$gc_buffer_add(S_expected.GC,HARRAY n_array) = S_expected.GC',
        '$error_read_discard(S_expected,perrorcall_entered.RESUME) = S_expected',
        *common.step('S_after','S_thrown'), 'S_after = S_expected',
        '$throwable_live(S_after,n_exception)', 'S_after.STORE[n_result] = DEFINED (PINT 99)',
        'S_after.STORE[n_pack_old] = DEFINED (PARRAY n_outer)',
        'S_after.STORE[n_keep] = DEFINED pvalue_keep', *common.public('S_after')]
    for field in ('.SITE = PORIGIN 0 eps', '.LINE = $(pconfigcall_S.LINE + 1)',
            '.SELECTION = (|S.SELECTEDCALLS|)', '.SELECTION = eps', '.INDEX = 1',
            '.NAMED = false', '.KIND = INTRINSIC_INI_GET',
            '.SENT = pconfigcall_S.SENT[0:1]', '.SENT = pconfigcall_S.SENT ++ [NAMED_SENT (KNOWN PNULL)]'):
        values += ['~$config_ini_null_valid(S,pconfigcall_S[' + field + '])']
    values += ['~$config_ini_null_valid(S[.CODE = eps],pconfigcall_S)',
        '~$config_ini_null_valid(S,pconfigcall_S[.OWNER = (|S.OBJECTS|)])',
        '~$config_ini_null_valid(S[.ALLOCATIONS = eps],pconfigcall_S)',
        '~$config_ini_rejected_array(S,|S.ARRAYS|)', '~$config_ini_rejected_array(S[.ARRAYS = eps],n_array)',
        'pvalue_bad = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ' + text('two-pack-peer86'),
        '~$string_carrier_valid(S,pvalue_bad)']
    for packs in ('eps', '[pconfigpack_value]', '[pconfigpack_value,pconfigpack_value]',
            '[pconfigpack_option,pconfigpack_value]'):
        values += ['~$config_ini_null_valid(S,pconfigcall_S[.PACKS = ' + packs + '])']
    for index, pack in enumerate(('pconfigpack_value','pconfigpack_option')):
        other = 'pconfigpack_option' if index == 0 else 'pconfigpack_value'
        for field in ('.INDEX = ' + str(1-index), '.SITE = PORIGIN 0 eps',
                '.LINE = $(' + pack + '.LINE + 1)', '.ARRAY = |S.ARRAYS|'):
            packs = '[' + pack + '[' + field + '],' + other + ']' if index == 0 else '[' + other + ',' + pack + '[' + field + ']]'
            values += ['~$config_ini_null_valid(S,pconfigcall_S[.PACKS = ' + packs + '])']
    for suffix, first, second, named in [
            ('numeric', 'KINT 3', 'KINT 7', False),
            ('forward', 'KSTRING ' + text('option'), 'KSTRING ' + text('value'), True),
            ('mixed', 'KINT 3', 'KSTRING ' + text('value'), True),
            ('named_then_numeric', 'KSTRING ' + text('option'), 'KINT 7', True)]:
        values += ['pconfigpack_' + suffix + '_first = pconfigpack_value[.ITEMS = [ENTRY (' + first + ') (DIRECT PNULL)]]',
            'pconfigpack_' + suffix + '_second = pconfigpack_option[.ITEMS = [ENTRY (' + second + ') (DIRECT (PARRAY n_array))]]',
            'pconfigcall_' + suffix + ' = pconfigcall_S[.NAMED = ' + str(named).lower() + '][.PACKS = [pconfigpack_' + suffix + '_first,pconfigpack_' + suffix + '_second]]',
            '$config_invoke_valid(S,pconfigcall_' + suffix + ')', '$config_ini_null_valid(S,pconfigcall_' + suffix + ')']
    for suffix, first, second in [
            ('unknown', '[ENTRY (KSTRING ' + text('other') + ') (DIRECT (PARRAY n_array))]', 'pentry_option*'),
            ('duplicate', 'pentry_value*', '[ENTRY (KSTRING ' + text('value') + ') (DIRECT PNULL)]'),
            ('numeric_reversed', '[ENTRY (KINT 3) (DIRECT (PARRAY n_array))]', '[ENTRY (KINT 7) (DIRECT PNULL)]'),
            ('within_pack_late_numeric', '[ENTRY (KSTRING ' + text('option') + ') (DIRECT PNULL),ENTRY (KINT 7) (DIRECT (PARRAY n_array))]', 'eps')]:
        values += ['pconfigpack_bad_' + suffix + '_first = pconfigpack_value[.ITEMS = ' + first + ']',
            'pconfigpack_bad_' + suffix + '_second = pconfigpack_option[.ITEMS = ' + second + ']',
            'pconfigcall_bad_' + suffix + ' = pconfigcall_S[.PACKS = [pconfigpack_bad_' + suffix + '_first,pconfigpack_bad_' + suffix + '_second]]',
            '~$config_invoke_valid(S,pconfigcall_bad_' + suffix + ')',
            '~$config_ini_null_valid(S,pconfigcall_bad_' + suffix + ')']
    for suffix, item in [('carrier','DIRECT pvalue_bad'), ('undefined','DIRECT PUNDEFINED'),
            ('nested','DIRECT (PARRAY n_array)'), ('object','DIRECT (POBJECT 0)'),
            ('alias','ALIAS n_pack_old'), ('legacy','DIRECT (PSTRING ' + text('old86') + ')'),
            ('nan','DIRECT (PFLOAT 9221120237041090560)')]:
        values += ['pentry_' + suffix + '* = [ENTRY (KINT 0) (' + item + ')]',
            '~$config_ini_rejected_entries(S,pentry_' + suffix + '*)',
            'S_badarray_' + suffix + ' = S[.ARRAYS[n_array].ITEMS = pentry_' + suffix + '*]',
            '~$config_ini_rejected_array(S_badarray_' + suffix + ',n_array)',
            '~$config_ini_null_valid(S_badarray_' + suffix + ',pconfigcall_S)']
    for field in ('.LEVEL = 2', '.MESSAGE = ' + text('changed'), '.LINE = $(perrorcall_deprecated.LINE + 1)',
            '.EVENT = DIAGNOSTIC "Deprecated" perrorcall_deprecated.MESSAGE $(perrorcall_deprecated.LINE + 1)'):
        values += ['~$error_call_valid(S_expected,perrorcall_deprecated[' + field + '])']
    values += [*budget('S_pre'), *budget('S_between'), *budget('S_option_capture'), *budget('S_thrown'),
        *reach('S_recovery','S_after',4),
        'S_recovery.TODO = (CONFIG_INVOKE pconfigcall_recovery) :: ptask_recovery*',
        'pconfigcall_recovery.OWNER = eps', 'pconfigcall_recovery.SELECTION = (n_recovery_selection)',
        '$(n_recovery_selection < |S_recovery.SELECTEDCALLS|)',
        'S_recovery.SELECTEDCALLS[n_recovery_selection] = pselectedcall_recovery',
        'pselectedcall_recovery.ORIGINAL = ' + text('InI_SeT'),
        '$selected_entry_valid(S_recovery,pselectedcall_recovery)',
        'pconfigcall_recovery.INDEX = 2', 'pconfigcall_recovery.PACKS = eps', '~pconfigcall_recovery.NAMED',
        'pconfigcall_recovery.SENT = [NAMED_SENT (KNOWN pvalue_option),NAMED_SENT (KNOWN pvalue_precision)]',
        '$string_bytes(pvalue_option) = (' + text('precision') + ')',
        '$string_bytes(pvalue_precision) = (' + text('12') + ')',
        '$config_invoke_valid(S_recovery,pconfigcall_recovery)',
        '~$config_method_receiver(S_recovery,pconfigcall_recovery)', '~$config_strict(S_recovery,pconfigcall_recovery)',
        '~$config_ini_null_valid(S_recovery,pconfigcall_recovery)',
        'S_recovery.STORE[n_keep] = DEFINED pvalue_keep', '$config_nodes(pconfigcall_recovery) = eps',
        'S_recovery.PRECISIONINI = ' + text('10'), 'S_recovery.ERRORHANDLER.CALLBACK = eps',
        *common.public('S_recovery'), *common.step('S_recovered','S_recovery'),
        'S_recovered.TODO = ptask_recovery*', 'S_recovered.RESULT = KNOWN pvalue_old_precision',
        '$string_bytes(pvalue_old_precision) = (' + text('10') + ')', 'S_recovered.PRECISIONINI = ' + text('12'),
        *unchanged('S_recovered','S_recovery','STORE ENV OBJECTS USERCONSTANTS SELECTEDCALLS EVENTS'),
        *common.public('S_recovered'), 'S_final = $drive_steps(S_recovered,3000)',
        'S_final.COMPLETION = NORMAL', 'S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.USERCONSTANTS = [puserconstant_sibling]', 'S_final.PRECISIONINI = ' + text('12'),
        'S_final.ERRORHANDLER.CALLBACK = eps',
        *unchanged('S_final','S','AUTOLOAD CLASSNAMES CLASSCONSTANTCACHE FILEINCLUDEPATH'),
        '$test_outputs(S_final.EVENTS) = ' + text('B|O|D|8192|' + MESSAGE + '|I|99|1|1|handler-array86|0|two-pack-peer86|3479|Z|R|10|12|99'),
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
