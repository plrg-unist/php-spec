#!/usr/bin/env python3
"""A saved unpack snapshot owns its earlier array while the shared cell remains live."""
import json
import os
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import ini_set_unpack_null_alias_array_value_review_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64
MESSAGE = 'ini_set(): Passing null to parameter #1 ($option) of type string is deprecated'
PREFIX = r"""
dec $test_ini_unpack_alias_array_review_front(pstate, nat) : bool
def $test_ini_unpack_alias_array_review_front(S, 0) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (PARRAY n_array))]
def $test_ini_unpack_alias_array_review_front(S, 1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_call(S,pcallcontext) = (perrorcall)
  -- if perrorcall.RESUME = CONFIG_INI_NULL_RESULT pconfigcall
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_ini_unpack_alias_array_review_front(S, 2) = true
  -- if S.TODO = (THROW_VALUE porigin z) :: ptask_body*
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_call(S,pcallcontext) = (perrorcall)
  -- if perrorcall.RESUME = CONFIG_INI_NULL_RESULT pconfigcall
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_ini_unpack_alias_array_review_front(S, 3) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = CONFIG_INI_NULL_RESULT pconfigcall
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_ini_unpack_alias_array_review_front(S, 4) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_option),NAMED_SENT (KNOWN pvalue)]
  -- if $string_bytes(pvalue_option) = ($ptascii("precision"))
  -- if $string_bytes(pvalue) = ($ptascii("12"))
def $test_ini_unpack_alias_array_review_front(S, 5) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.INDEX = 0
  -- if pconfigcall.SENT = eps
def $test_ini_unpack_alias_array_review_front(S, 6) = true
  -- if S.TODO = (CONFIG_UNPACK_NEXT pconfigcall (KNOWN (PARRAY n_pack)) 0) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_ini_unpack_alias_array_review_front(S, n_stage) = false -- otherwise
dec $test_ini_unpack_alias_array_review_seek(pstate, nat, nat) : pstate
def $test_ini_unpack_alias_array_review_seek(S, n_stage, 0) = S
def $test_ini_unpack_alias_array_review_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_ini_unpack_alias_array_review_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_ini_unpack_alias_array_review_seek(S, n_stage, n) = $test_ini_unpack_alias_array_review_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_ini_unpack_alias_array_review_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def reach(state, start, stage):
    return [state + '_found = $test_ini_unpack_alias_array_review_seek(' + start + ',' + str(stage) + ',3000)',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_ini_unpack_alias_array_review_front(' + state + ',' + str(stage) + ')']


def unchanged(after, before, fields):
    return [after + '.' + field + ' = ' + before + '.' + field for field in fields.split()]


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)',
        state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)',
        state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def checks(program, path, name):
    assert name == 'selected-unpack-alias-array-throw-keeps-old-pack-and-live-cell'
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *reach('S_pre', 'S_initial', 5),
        'S_pre.TODO = (CONFIG_ARGS pconfigcall_pre) :: ptask_S*',
        'pconfigcall_pre.KIND = INTRINSIC_INI_SET', 'pconfigcall_pre.OWNER = eps',
        'pconfigcall_pre.INDEX = 0', 'pconfigcall_pre.PACKS = eps', '~pconfigcall_pre.NAMED',
        'pconfigcall_pre.SENT = eps',
        '$call_task_valid(S_pre,CONFIG_ARGS pconfigcall_pre)',
        '$config_pending_valid(S_pre,pconfigcall_pre,true)',
        'pconfigcall_pre.SELECTION = (n_selection)', '$(n_selection < |S_pre.SELECTEDCALLS|)',
        'S_pre.SELECTEDCALLS[n_selection] = pselectedcall',
        'pselectedcall.NONCE = n_selection', 'pselectedcall.OWNER = eps', 'pselectedcall.KIND = INTRINSIC_INI_SET',
        'pselectedcall.SITE = pconfigcall_pre.SITE', 'pselectedcall.LINE = pconfigcall_pre.LINE',
        'pselectedcall.DEPTH = |S_pre.FRAMES|',
        'pselectedcall.ORIGINAL = ' + text('InI_SeT'), 'pselectedcall.LOOKUP = ' + text('InI_SeT'),
        '$selected_entry_valid(S_pre,pselectedcall)',
        '$lookup(S_pre.ENV,' + text('value') + ') = (n_value)',
        'S_pre.STORE[n_value] = DEFINED (PARRAY n_array)',
        'S_pre.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (ALIAS n_leaf)]',
        '$lookup(S_pre.ENV,' + text('leaf') + ') = (n_leaf)',
        'S_pre.STORE[n_leaf] = DEFINED pvalue_leaf',
        'pvalue_leaf = PSTRING_CARRIER (REQUEST_STRING n_candidate) ' + text('unpack-alias-array-peer84'),
        '$call_reference_operand_valid(S_pre,REFERENCE n_leaf)',
        '$config_ini_rejected_alias_array(S_pre,n_array)',
        '$node_children(S_pre,HARRAY n_array) = [HCELL n_leaf]', '$node_children(S_pre,HCELL n_leaf) = eps',
        '$string_carrier_valid(S_pre,pvalue_leaf)', '(HARRAY n_array) <- S_pre.ALLOCATIONS',
        '$lookup(S_pre.ENV,' + text('arrayKeep') + ') = (n_array_keep)',
        'S_pre.STORE[n_array_keep] = DEFINED (PARRAY n_array)',
        '$lookup(S_pre.ENV,' + text('pack') + ') = (n_pack_cell)',
        'S_pre.STORE[n_pack_cell] = DEFINED (PARRAY n_outer)',
        '$lookup(S_pre.ENV,' + text('packOld') + ') = (n_pack_old)',
        'S_pre.STORE[n_pack_old] = DEFINED (PARRAY n_outer)',
        '(HARRAY n_outer) <- S_pre.ALLOCATIONS',
        'pentry_snapshot* = [ENTRY (KSTRING ' + text('value') + ') (DIRECT (PARRAY n_array)),ENTRY (KSTRING ' + text('option') + ') (DIRECT PNULL)]',
        'S_pre.ARRAYS[n_outer].ITEMS = pentry_snapshot*',
        '$node_children(S_pre,HARRAY n_outer) = [HARRAY n_array]',
        '$lookup(S_pre.ENV,' + text('call') + ') = (n_call)',
        'S_pre.STORE[n_call] = DEFINED pvalue_keep', '$string_bytes(pvalue_keep) = (' + text('InI_SeT') + ')',
        '$lookup(S_pre.ENV,' + text('keep') + ') = (n_keep)', 'S_pre.STORE[n_keep] = DEFINED pvalue_keep',
        '$lookup(S_pre.ENV,' + text('option') + ') = (n_option)', 'S_pre.STORE[n_option] = DEFINED PNULL',
        '$lookup(S_pre.ENV,' + text('effects') + ') = (n_effects)', 'S_pre.STORE[n_effects] = DEFINED (PINT 0)',
        '$lookup(S_pre.ENV,' + text('warnings') + ') = (n_warnings)', 'S_pre.STORE[n_warnings] = DEFINED (PINT 0)',
        '$lookup(S_pre.ENV,' + text('saved') + ') = (n_saved)', 'S_pre.STORE[n_saved] = DEFINED PNULL',
        '$lookup(S_pre.ENV,' + text('result') + ') = (n_result)', 'S_pre.STORE[n_result] = DEFINED (PINT 99)',
        '$config_nodes(pconfigcall_pre) = eps', '$task_nodes(CONFIG_ARGS pconfigcall_pre) = eps',
        '$test_outputs(S_pre.EVENTS) = ' + text('B|'),
        *common.public('S_pre'), *reach('S_capture', 'S_pre', 6),
        'S_capture.TODO = (CONFIG_UNPACK_NEXT pconfigcall_capture (KNOWN (PARRAY n_outer)) 0) :: ptask_S*',
        'pconfigcall_capture.PACKS = [pconfigpack]',
        'pconfigcall_capture = pconfigcall_pre[.PACKS = [pconfigpack]]',
        'pconfigpack.INDEX = 0', 'pconfigpack.ARRAY = n_outer', 'pconfigpack.ITEMS = pentry_snapshot*',
        '$config_pack_source_valid(S_capture,pconfigcall_capture,pconfigpack)',
        '$config_unpack_valid(S_capture,pconfigcall_capture,KNOWN (PARRAY n_outer),0)',
        '$call_task_valid(S_capture,CONFIG_UNPACK_NEXT pconfigcall_capture (KNOWN (PARRAY n_outer)) 0)',
        'pconfigpack.ITEMS = $config_pack_capture(S_capture,S_capture.ARRAYS[n_outer].ITEMS)',
        '$config_nodes(pconfigcall_capture) = eps',
        '$task_nodes(CONFIG_UNPACK_NEXT pconfigcall_capture (KNOWN (PARRAY n_outer)) 0) = [HARRAY n_outer]',
        '$node_children(S_capture,HARRAY n_outer) = [HARRAY n_array]',
        '$node_children(S_capture,HARRAY n_array) = [HCELL n_leaf]',
        '$node_children(S_capture,HCELL n_leaf) = eps',
        'S_capture.ARRAYS[n_array] = S_pre.ARRAYS[n_array]',
        'S_capture.STORE[n_leaf] = DEFINED pvalue_pack',
        '$string_bytes(pvalue_pack) = (' + text('pack-array84') + ')',
        '$string_carrier_valid(S_capture,pvalue_pack)',
        '$config_ini_rejected_alias_array(S_capture,n_array)',
        'S_capture.STORE[n_array_keep] = DEFINED (PARRAY n_mutated)', 'n_mutated =/= n_array',
        'S_capture.ARRAYS[n_mutated].ITEMS = [ENTRY (KINT 0) (ALIAS n_leaf),ENTRY (KINT 1) (DIRECT (PINT 31))]',
        '$node_children(S_capture,HARRAY n_mutated) = [HCELL n_leaf]',
        'S_capture.STORE[n_pack_cell] = DEFINED (PARRAY n_outer)',
        'S_capture.STORE[n_pack_old] = DEFINED (PARRAY n_outer)',
        'S_capture.STORE[n_value] = DEFINED (PINT 0)', 'S_capture.STORE[n_effects] = DEFINED (PINT 1)',
        'S_capture.STORE[n_result] = DEFINED (PINT 99)',
        'S_capture.STORE[n_call] = DEFINED pvalue_call_live',
        '$string_bytes(pvalue_call_live) = (' + text('ini_get') + ')',
        'S_capture.STORE[n_option] = DEFINED pvalue_option_live',
        '$string_bytes(pvalue_option_live) = (' + text('precision') + ')',
        'S_capture.STORE[n_keep] = DEFINED pvalue_keep',
        'S_capture.SELECTEDCALLS[n_selection] = pselectedcall',
        'S_capture.PRECISIONINI = ' + text('14'), '$test_outputs(S_capture.EVENTS) = ' + text('B|P|'),
        *common.public('S_capture'), *common.step('S_first', 'S_capture'),
        'pconfigcall_first = pconfigcall_capture[.NAMED = true][.SENT = [NAMED_HOLE,NAMED_SENT (KNOWN (PARRAY n_array))]]',
        'S_first.TODO = (CONFIG_UNPACK_NEXT pconfigcall_first (KNOWN (PARRAY n_outer)) 1) :: ptask_S*',
        '$config_unpack_valid(S_first,pconfigcall_first,KNOWN (PARRAY n_outer),1)',
        '$config_nodes(pconfigcall_first) = [HARRAY n_array]',
        '$task_nodes(CONFIG_UNPACK_NEXT pconfigcall_first (KNOWN (PARRAY n_outer)) 1) = [HARRAY n_array,HARRAY n_outer]',
        *common.public('S_first'), *common.step('S_second', 'S_first'),
        'pconfigcall_second = pconfigcall_first[.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (PARRAY n_array))]]',
        'S_second.TODO = (CONFIG_UNPACK_NEXT pconfigcall_second (KNOWN (PARRAY n_outer)) 2) :: ptask_S*',
        '$config_unpack_valid(S_second,pconfigcall_second,KNOWN (PARRAY n_outer),2)',
        '$task_nodes(CONFIG_UNPACK_NEXT pconfigcall_second (KNOWN (PARRAY n_outer)) 2) = [HARRAY n_array,HARRAY n_outer]',
        *common.public('S_second'), *common.step('S_args', 'S_second'),
        'pconfigcall_S = pconfigcall_second[.INDEX = 1]', 'S_args.TODO = (CONFIG_ARGS pconfigcall_S) :: ptask_S*',
        '$call_task_valid(S_args,CONFIG_ARGS pconfigcall_S)', *common.step('S', 'S_args'),
        'S.TODO = (CONFIG_INVOKE pconfigcall_S) :: ptask_S*',
        '$config_invoke_valid(S,pconfigcall_S)', '$config_selected_valid(S,pconfigcall_S)',
        'pconfigcall_S.PACKS = [pconfigpack]', 'pconfigcall_S.INDEX = 1', 'pconfigcall_S.NAMED',
        '$intrinsic_count(S,pconfigcall_S.SITE) = (1)',
        '$intrinsic_argument(S,pconfigcall_S.SITE,0) = ((expression_pack,true,eps,pconfigpack.SITE,pconfigpack.LINE))',
        '$compiled_read(S,pconfigpack.SITE) = eps',
        '$config_source_replay(S,pconfigcall_S,pconfigcall_S[.INDEX = 0][.SENT = eps][.NAMED = false][.PACKS = eps],pconfigcall_S.PACKS) = ((pconfigcall_replayed,eps))',
        'pconfigcall_replayed = pconfigcall_S[.PACKS = eps]',
        '$config_ini_rejected_alias_array(S,n_array)', '~$config_ini_rejected_array(S,n_array)',
        '$config_ini_null_valid(S,pconfigcall_S)',
        '~$config_ini_quiet_value(S,PARRAY n_array)', '~$config_strict(S,pconfigcall_S)',
        '~$config_method_receiver(S,pconfigcall_S)',
        '$propref_at(S.PROPREFS,n_leaf) = eps', '$reference_coercion_at(S.REFCOERCIONS,n_leaf) = eps',
        'S.PARAMETERBACKINGS = eps', '$call_reference_operand_valid(S,REFERENCE n_leaf)',
        'S.SELECTEDCALLS[n_selection] = pselectedcall',
        '$config_nodes(pconfigcall_S) = [HARRAY n_array]',
        '$task_nodes(CONFIG_INI_NULL_RESULT pconfigcall_S) = [HARRAY n_array]',
        '~((HARRAY n_outer) <- $config_nodes(pconfigcall_S))',
        '$node_children(S,HARRAY n_outer) = [HARRAY n_array]',
        '$node_children(S,HARRAY n_array) = [HCELL n_leaf]', '$node_children(S,HCELL n_leaf) = eps',
        'S.ARRAYS[n_array] = S_pre.ARRAYS[n_array]', 'S.ARRAYS[n_outer].ITEMS = pentry_snapshot*',
        'S.STORE[n_leaf] = DEFINED pvalue_pack', '$config_ini_quiet_value(S,pvalue_pack)',
        '$entry_lookup(S.ARRAYS[n_array].ITEMS,KINT 1) = eps',
        'S.STORE[n_keep] = DEFINED pvalue_keep',
        'S.PRECISIONINI = ' + text('14'), 'S.USERCONSTANTS = eps', 'S.CURRENT = eps', 'S.FRAMES = eps',
        *unchanged('S', 'S_capture', 'STORE ENV EVENTS PRECISIONINI USERCONSTANTS'),
        '$test_outputs(S.EVENTS) = ' + text('B|P|'), *common.public('S'),
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
        '$error_handler_trace_values(S_handler,pcallcontext_handler,pconfigcall_S) = [PNULL,PARRAY n_array]',
        *common.public('S_handler'), *reach('S_throw', 'S_handler', 2),
        'S_throw.TODO = (THROW_VALUE porigin_throw z_throw) :: ptask_body*',
        'S_throw.CURRENT = (pcallcontext_handler)', 'S_throw.FRAMES = [pframe_call]',
        'pframe_call.CONTEXT = eps', 'pframe_call.LOCALS = eps',
        'pframe_call.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_S*',
        'perrorcall_entered.RESUME = CONFIG_INI_NULL_RESULT pconfigcall_S',
        'S_throw.STORE[n_saved] = DEFINED (POBJECT n_exception)',
        'S_throw.OBJECTS[n_exception] = THROWABLE pthrowable', 'pthrowable.KIND = "Exception"',
        '$string_bytes($throwable_field(S_throw,n_exception,"message")) = (' + text('unpack-alias-array84-stop') + ')',
        '$throwable_field(S_throw,n_exception,"previous") = PNULL',
        '$throwable_field(S_throw,n_exception,"trace") = PARRAY n_trace',
        'S_throw.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_handler)),ENTRY (KINT 1) (DIRECT (PARRAY n_api))]',
        '$trace_array_field(S_throw,n_handler,' + text('function') + ') = PSTRING ' + text('iniUnpackAliasArrayReviewDeprecated84'),
        '$trace_array_field(S_throw,n_api,' + text('function') + ') = PSTRING ' + text('ini_set'),
        '$trace_array_field(S_throw,n_api,' + text('line') + ') = PINT pconfigcall_S.LINE',
        '$trace_array_field(S_throw,n_api,' + text('args') + ') = PARRAY n_args',
        'S_throw.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT PNULL),ENTRY (KINT 1) (DIRECT (PARRAY n_array))]',
        '$node_children(S_throw,HARRAY n_args) = [HARRAY n_array]',
        'S_throw.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (ALIAS n_leaf)]',
        'S_throw.ARRAYS[n_array] = S_pre.ARRAYS[n_array]',
        '$node_children(S_throw,HARRAY n_array) = [HCELL n_leaf]',
        'S_throw.STORE[n_leaf] = DEFINED pvalue_after',
        '$string_bytes(pvalue_after) = (' + text('after-exception84') + ')',
        '$config_ini_quiet_value(S_throw,pvalue_after)',
        '$call_reference_operand_valid(S_throw,REFERENCE n_leaf)',
        '$node_children(S_throw,HCELL n_leaf) = eps', '~$gc_possible_root(S_throw,HCELL n_leaf)',
        '(HARRAY n_array) <- S_throw.ALLOCATIONS',
        'S_throw.STORE[n_pack_old] = DEFINED (PARRAY n_outer)', 'S_throw.STORE[n_keep] = DEFINED pvalue_keep',
        'S_throw.STORE[n_result] = DEFINED (PINT 99)', 'S_throw.STORE[n_effects] = DEFINED (PINT 1)',
        'S_throw.STORE[n_warnings] = DEFINED (PINT 1)', 'S_throw.STORE[n_value] = DEFINED (PINT 123)',
        'S_throw.PRECISIONINI = ' + text('10'),
        'S_throw.USERCONSTANTS = [puserconstant_sibling]', 'puserconstant_sibling.NAME = ' + text('SOURCE84PEER'),
        'puserconstant_sibling.VALUE = PINT 3359', 'puserconstant_sibling.CLASS = PVSCALAR',
        'S_throw.STORE[n_array_keep] = DEFINED (PARRAY n_mutated)',
        'S_throw.ARRAYS[n_mutated].ITEMS = [ENTRY (KINT 0) (ALIAS n_leaf),ENTRY (KINT 1) (DIRECT (PINT 31)),ENTRY (KINT 2) (DIRECT (PINT 37))]',
        '$node_children(S_throw,HARRAY n_mutated) = [HCELL n_leaf]',
        '$entry_lookup(S_throw.ARRAYS[n_array].ITEMS,KINT 1) = eps',
        '$config_ini_rejected_alias_array(S_throw,n_array)',
        'S_throw.ARRAYS[n_outer].ITEMS = pentry_snapshot*',
        '$node_children(S_throw,HARRAY n_outer) = [HARRAY n_array]',
        'S_throw.STORE[n_pack_cell] = DEFINED (PARRAY n_pack_live)', 'n_pack_live =/= n_outer',
        '$entry_lookup(S_throw.ARRAYS[n_pack_live].ITEMS,KSTRING ' + text('value') + ') = (DIRECT (PINT 0))',
        '$entry_lookup(S_throw.ARRAYS[n_pack_live].ITEMS,KSTRING ' + text('option') + ') = (DIRECT pvalue_pack_option)',
        '$string_bytes(pvalue_pack_option) = (' + text('precision') + ')',
        '$config_pack_capture(S_throw,S_throw.ARRAYS[n_pack_live].ITEMS) =/= pconfigpack.ITEMS',
        '(HARRAY n_array) <- $gc_physical_nodes(S_throw.GC.BUFFER)',
        '$test_outputs(S_throw.EVENTS) = ' + text('B|P|D|8192|' + MESSAGE + '|'),
        *unchanged('S_throw', 'S', 'AUTOLOAD CLASSNAMES CLASSCONSTANTCACHE FILEINCLUDEPATH'),
        *common.public('S_throw'), *common.step('S_throwing', 'S_throw'),
        'S_throwing.TODO = (THROW_SEARCH n_exception) :: ptask_body*', *reach('S_thrown', 'S_throwing', 3),
        'S_thrown.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_S*',
        'S_thrown.CURRENT = S.CURRENT', 'S_thrown.ENV = S.ENV',
        'S_thrown.STORE[n_saved] = DEFINED (POBJECT n_exception)',
        'S_thrown.STORE[n_result] = DEFINED (PINT 99)', 'S_thrown.USERCONSTANTS = [puserconstant_sibling]',
        'S_thrown.PRECISIONINI = ' + text('10'), '$config_ini_null_valid(S_thrown,pconfigcall_S)',
        'S_thrown.STORE[n_leaf] = DEFINED pvalue_after',
        'S_thrown.ARRAYS[n_array] = S_pre.ARRAYS[n_array]',
        'S_thrown.STORE[n_array_keep] = DEFINED (PARRAY n_mutated)',
        '(HARRAY n_array) <- $gc_physical_nodes(S_thrown.GC.BUFFER)', *common.public('S_thrown'),
        'S_discard = S_thrown[.TODO = (THROW_SEARCH n_exception) :: ptask_S*]',
        'S_expected = $error_handler_restore($identity_read_discard(S_discard,perrorcall_entered.RESUME),perrorcall_entered.CALLBACK)',
        '$gc_buffer_add(S_expected.GC,HARRAY n_array) = S_expected.GC',
        '$error_read_discard(S_expected,perrorcall_entered.RESUME) = S_expected',
        *common.step('S_after', 'S_thrown'), 'S_after = S_expected',
        '$throwable_live(S_after,n_exception)', 'S_after.STORE[n_result] = DEFINED (PINT 99)',
        'S_after.STORE[n_pack_old] = DEFINED (PARRAY n_outer)',
        'S_after.ARRAYS[n_outer].ITEMS = pentry_snapshot*',
        'S_after.STORE[n_leaf] = DEFINED pvalue_after', '$node_children(S_after,HARRAY n_array) = [HCELL n_leaf]',
        *common.public('S_after')]
    for variable, spelling in [('call', 'constant'), ('option', 'handler-option84')]:
        values += ['S_thrown.STORE[n_' + variable + '] = DEFINED pvalue_handler_' + variable,
            '$string_bytes(pvalue_handler_' + variable + ') = (' + text(spelling) + ')']
    for field in ('.SITE = PORIGIN 0 eps', '.LINE = $(pconfigcall_S.LINE + 1)',
            '.SELECTION = (|S.SELECTEDCALLS|)', '.SELECTION = eps', '.INDEX = 2', '.OWNER = (0)',
            '.NAMED = false', '.KIND = INTRINSIC_INI_GET',
            '.SENT = pconfigcall_S.SENT[0:1]', '.SENT = pconfigcall_S.SENT ++ [NAMED_SENT (KNOWN PNULL)]'):
        values += ['~$config_ini_null_valid(S,pconfigcall_S[' + field + '])']
    values += ['~$config_ini_null_valid(S[.CODE = eps],pconfigcall_S)',
        '~$config_ini_null_valid(S[.ALLOCATIONS = eps],pconfigcall_S)',
        '~$config_ini_rejected_alias_array(S,|S.ARRAYS|)', '~$config_ini_rejected_alias_array(S[.ARRAYS = eps],n_array)',
        '~$config_ini_rejected_alias_array(S[.REFCELLS = eps],n_array)',
        '~$config_ini_rejected_alias_array(S[.STORE[n_leaf] = UNDEFINED],n_array)',
        '~$config_ini_rejected_alias_array(S[.PROPREFS = [{CELL n_leaf,SOURCES eps}]],n_array)',
        '~$config_ini_rejected_alias_array(S[.REFCOERCIONS = [{CELL n_leaf,SITE pconfigcall_S.SITE,LINE pconfigcall_S.LINE,VALUE ' + text('pack-array84') + '}]],n_array)',
        '~$config_ini_rejected_alias_array(S[.PARAMETERBACKINGS = [{FUNCTION pconfigcall_S.SITE,INDEX 0,CELL n_leaf,LINE pconfigcall_S.LINE,VALUE ' + text('pack-array84') + '}]],n_array)',
        'pvalue_bad = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ' + text('unpack-alias-array-peer84'),
        '~$string_carrier_valid(S,pvalue_bad)']
    for field in ('.PACKS = eps', '.PACKS = [pconfigpack,pconfigpack]'):
        values += ['~$config_ini_null_valid(S,pconfigcall_S[' + field + '])']
    for field in ('.INDEX = 1', '.SITE = PORIGIN 0 eps', '.LINE = $(pconfigpack.LINE + 1)', '.ARRAY = |S.ARRAYS|'):
        values += ['~$config_ini_null_valid(S,pconfigcall_S[.PACKS = [pconfigpack[' + field + ']]])']
    for suffix, items, named in [
            ('numeric', '[ENTRY (KINT 3) (DIRECT PNULL),ENTRY (KINT 7) (DIRECT (PARRAY n_array))]', False),
            ('forward', '[ENTRY (KSTRING ' + text('option') + ') (DIRECT PNULL),ENTRY (KSTRING ' + text('value') + ') (DIRECT (PARRAY n_array))]', True),
            ('mixed', '[ENTRY (KINT 3) (DIRECT PNULL),ENTRY (KSTRING ' + text('value') + ') (DIRECT (PARRAY n_array))]', True)]:
        values += ['pconfigpack_' + suffix + ' = pconfigpack[.ITEMS = ' + items + ']',
            'pconfigcall_' + suffix + ' = pconfigcall_S[.NAMED = ' + str(named).lower() + '][.PACKS = [pconfigpack_' + suffix + ']]',
            '$config_invoke_valid(S,pconfigcall_' + suffix + ')', '$config_ini_null_valid(S,pconfigcall_' + suffix + ')']
    for suffix, items in [
            ('unknown', '[ENTRY (KSTRING ' + text('other') + ') (DIRECT (PARRAY n_array)),ENTRY (KSTRING ' + text('option') + ') (DIRECT PNULL)]'),
            ('duplicate', '[ENTRY (KSTRING ' + text('value') + ') (DIRECT (PARRAY n_array)),ENTRY (KSTRING ' + text('value') + ') (DIRECT PNULL)]'),
            ('late_numeric', '[ENTRY (KSTRING ' + text('value') + ') (DIRECT (PARRAY n_array)),ENTRY (KINT 3) (DIRECT PNULL)]'),
            ('snapshot_alias', '[ENTRY (KSTRING ' + text('value') + ') (ALIAS n_value),ENTRY (KSTRING ' + text('option') + ') (DIRECT PNULL)]')]:
        values += ['pconfigpack_' + suffix + ' = pconfigpack[.ITEMS = ' + items + ']',
            'pconfigcall_' + suffix + ' = pconfigcall_S[.PACKS = [pconfigpack_' + suffix + ']]',
            '~$config_invoke_valid(S,pconfigcall_' + suffix + ')', '~$config_ini_null_valid(S,pconfigcall_' + suffix + ')']
    for suffix, item in [('carrier', 'DIRECT pvalue_bad'), ('undefined', 'DIRECT PUNDEFINED'),
            ('nested', 'DIRECT (PARRAY n_array)'), ('object', 'DIRECT (POBJECT 0)'),
            ('alias', 'ALIAS n_pack_old'), ('legacy', 'DIRECT (PSTRING ' + text('old84') + ')'),
            ('nan', 'DIRECT (PFLOAT 9221120237041090560)')]:
        values += ['pentry_' + suffix + '* = [ENTRY (KINT 0) (' + item + ')]',
            '~$config_ini_rejected_entries(S,pentry_' + suffix + '*)',
            'S_badarray_' + suffix + ' = S[.ARRAYS[n_array].ITEMS = pentry_' + suffix + '*]',
            '~$config_ini_rejected_array(S_badarray_' + suffix + ',n_array)',
            '~$config_ini_rejected_alias_array(S_badarray_' + suffix + ',n_array)',
            '~$config_ini_null_valid(S_badarray_' + suffix + ',pconfigcall_S)']
    values += ['S_badkey = S[.ARRAYS[n_array].ITEMS = [ENTRY (KINT 1) (ALIAS n_leaf)]]',
        '~$config_ini_rejected_alias_array(S_badkey,n_array)', '~$config_ini_null_valid(S_badkey,pconfigcall_S)',
        'S_badtwo = S[.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (ALIAS n_leaf),ENTRY (KINT 1) (DIRECT (PINT 31))]]',
        '~$config_ini_rejected_alias_array(S_badtwo,n_array)', '~$config_ini_null_valid(S_badtwo,pconfigcall_S)',
        'S_direct = S[.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 31))]]',
        '$config_ini_rejected_array(S_direct,n_array)', '~$config_ini_rejected_alias_array(S_direct,n_array)',
        '$config_ini_null_valid(S_direct,pconfigcall_S)']
    for suffix, value in [('carrier', 'pvalue_bad'), ('undefined', 'PUNDEFINED'), ('array', 'PARRAY n_array'),
            ('object', 'POBJECT 0'), ('legacy', 'PSTRING ' + text('old84')), ('nan', 'PFLOAT 9221120237041090560')]:
        values += ['S_badleaf_' + suffix + ' = S[.STORE[n_leaf] = DEFINED (' + value + ')]',
            '~$config_ini_rejected_alias_array(S_badleaf_' + suffix + ',n_array)',
            '~$config_ini_null_valid(S_badleaf_' + suffix + ',pconfigcall_S)']
    for field in ('.LEVEL = 2', '.MESSAGE = ' + text('changed'), '.LINE = $(perrorcall_deprecated.LINE + 1)',
            '.EVENT = DIAGNOSTIC "Deprecated" perrorcall_deprecated.MESSAGE $(perrorcall_deprecated.LINE + 1)'):
        values += ['~$error_call_valid(S_expected,perrorcall_deprecated[' + field + '])']
    values += [*budget('S_pre'), *budget('S_capture'), *budget('S_first'), *budget('S_thrown'), *reach('S_recovery', 'S_after', 4),
        'S_recovery.TODO = (CONFIG_INVOKE pconfigcall_recovery) :: ptask_recovery*',
        'pconfigcall_recovery.OWNER = eps', 'pconfigcall_recovery.SELECTION = (n_recovery_selection)',
        'n_recovery_selection =/= n_selection',
        'pconfigcall_recovery.INDEX = 2', 'pconfigcall_recovery.PACKS = eps', '~pconfigcall_recovery.NAMED',
        'pconfigcall_recovery.SENT = [NAMED_SENT (KNOWN pvalue_option),NAMED_SENT (KNOWN pvalue_precision)]',
        '$string_bytes(pvalue_option) = (' + text('precision') + ')',
        '$string_bytes(pvalue_precision) = (' + text('12') + ')',
        '$config_invoke_valid(S_recovery,pconfigcall_recovery)',
        '~$config_method_receiver(S_recovery,pconfigcall_recovery)', '~$config_strict(S_recovery,pconfigcall_recovery)',
        '~$config_ini_null_valid(S_recovery,pconfigcall_recovery)',
        'S_recovery.STORE[n_keep] = DEFINED pvalue_keep',
        'S_recovery.SELECTEDCALLS[n_recovery_selection].OWNER = eps',
        'S_recovery.STORE[n_leaf] = DEFINED pvalue_after',
        'S_recovery.ARRAYS[n_array] = S_pre.ARRAYS[n_array]',
        'S_recovery.PRECISIONINI = ' + text('10'), 'S_recovery.ERRORHANDLER.CALLBACK = eps',
        *common.public('S_recovery'), *common.step('S_recovered', 'S_recovery'),
        'S_recovered.TODO = ptask_recovery*', 'S_recovered.RESULT = KNOWN pvalue_old_precision',
        '$string_bytes(pvalue_old_precision) = (' + text('10') + ')', 'S_recovered.PRECISIONINI = ' + text('12'),
        *unchanged('S_recovered', 'S_recovery', 'STORE ENV OBJECTS USERCONSTANTS SELECTEDCALLS EVENTS'),
        'S_recovered.ARRAYS[n_array] = S_pre.ARRAYS[n_array]',
        '$node_children(S_recovered,HARRAY n_array) = [HCELL n_leaf]',
        *common.public('S_recovered'), 'S_final = $drive_steps(S_recovered,3000)',
        'S_final.COMPLETION = NORMAL', 'S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.USERCONSTANTS = [puserconstant_sibling]', 'S_final.PRECISIONINI = ' + text('12'),
        'S_final.ERRORHANDLER.CALLBACK = eps',
        *unchanged('S_final', 'S', 'AUTOLOAD CLASSNAMES CLASSCONSTANTCACHE FILEINCLUDEPATH'),
        '$test_outputs(S_final.EVENTS) = ' + text('B|P|D|8192|' + MESSAGE + '|I|99|1|1|after-exception84|37|0|C|3359|Z|R|10|12|99'),
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
