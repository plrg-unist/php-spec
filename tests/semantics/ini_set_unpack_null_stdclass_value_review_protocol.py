#!/usr/bin/env python3
"""Unpack keeps the shared object pointer while later property writes remain live."""
import json
import os
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import ini_set_unpack_null_stdclass_value_review_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64
MESSAGE = 'ini_set(): Passing null to parameter #1 ($option) of type string is deprecated'
PREFIX = r"""
dec $test_ini_unpack_std_review_front(pstate, nat) : bool
def $test_ini_unpack_std_review_front(S, 0) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (POBJECT n_object))]
def $test_ini_unpack_std_review_front(S, 1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_call(S,pcallcontext) = (perrorcall)
  -- if perrorcall.RESUME = CONFIG_INI_NULL_RESULT pconfigcall
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_ini_unpack_std_review_front(S, 2) = true
  -- if S.TODO = (THROW_VALUE porigin z) :: ptask_body*
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_call(S,pcallcontext) = (perrorcall)
  -- if perrorcall.RESUME = CONFIG_INI_NULL_RESULT pconfigcall
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_ini_unpack_std_review_front(S, 3) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = CONFIG_INI_NULL_RESULT pconfigcall
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_ini_unpack_std_review_front(S, 4) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_option),NAMED_SENT (KNOWN pvalue)]
  -- if $string_bytes(pvalue_option) = ($ptascii("precision"))
  -- if $string_bytes(pvalue) = ($ptascii("12"))
def $test_ini_unpack_std_review_front(S, 5) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.INDEX = 0
  -- if pconfigcall.SENT = eps
def $test_ini_unpack_std_review_front(S, 6) = true
  -- if S.TODO = (CONFIG_UNPACK_NEXT pconfigcall (KNOWN (PARRAY n_pack)) 0) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_ini_unpack_std_review_front(S, n_stage) = false -- otherwise
dec $test_ini_unpack_std_review_seek(pstate, nat, nat) : pstate
def $test_ini_unpack_std_review_seek(S, n_stage, 0) = S
def $test_ini_unpack_std_review_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_ini_unpack_std_review_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_ini_unpack_std_review_seek(S, n_stage, n) = $test_ini_unpack_std_review_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_ini_unpack_std_review_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def reach(state, start, stage):
    return [state + '_found = $test_ini_unpack_std_review_seek(' + start + ',' + str(stage) + ',3000)',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_ini_unpack_std_review_front(' + state + ',' + str(stage) + ')']


def unchanged(after, before, fields):
    return [after + '.' + field + ' = ' + before + '.' + field for field in fields.split()]


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)',
        state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)',
        state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def checks(program, path, name):
    assert name == 'selected-unpack-null-stdclass-throw-keeps-shared-object'
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *reach('S_pre', 'S_initial', 5),
        'S_pre.TODO = (CONFIG_ARGS pconfigcall_pre) :: ptask_S*',
        'pconfigcall_pre.KIND = INTRINSIC_INI_SET', 'pconfigcall_pre.OWNER = eps',
        'pconfigcall_pre.SELECTION = (n_selection)', 'pconfigcall_pre.INDEX = 0',
        'pconfigcall_pre.PACKS = eps', '~pconfigcall_pre.NAMED', 'pconfigcall_pre.SENT = eps',
        '$call_task_valid(S_pre,CONFIG_ARGS pconfigcall_pre)', '$config_pending_valid(S_pre,pconfigcall_pre,true)',
        '$lookup(S_pre.ENV,' + text('value') + ') = (n_value)', 'S_pre.STORE[n_value] = DEFINED (POBJECT n_object)',
        'S_pre.OBJECTS[n_object] = STDINSTANCE',
        '$object_table_at(S_pre.OBJECTTABLES,n_object) = eps',
        '$objectprops_at(S_pre.OBJECTPROPS,n_object) = ([ppropertyslot_mark])',
        'ppropertyslot_mark.DECL = eps', 'ppropertyslot_mark.NAME = ' + text('mark'),
        'ppropertyslot_mark.STATE = PROP_VALUE (DIRECT pvalue_leaf)',
        'pvalue_leaf = PSTRING_CARRIER (REQUEST_STRING n_candidate) ' + text('unpack-stdclass-peer77'),
        '$string_carrier_valid(S_pre,pvalue_leaf)', '(HOBJECT n_object) <- S_pre.ALLOCATIONS',
        '$lookup(S_pre.ENV,' + text('objectKeep') + ') = (n_object_keep)', 'S_pre.STORE[n_object_keep] = DEFINED (POBJECT n_object)',
        '$lookup(S_pre.ENV,' + text('pack') + ') = (n_pack_cell)', 'S_pre.STORE[n_pack_cell] = DEFINED (PARRAY n_outer)',
        '$lookup(S_pre.ENV,' + text('packOld') + ') = (n_pack_old)', 'S_pre.STORE[n_pack_old] = DEFINED (PARRAY n_outer)',
        '(HARRAY n_outer) <- S_pre.ALLOCATIONS',
        'pentry_snapshot* = [ENTRY (KSTRING ' + text('value') + ') (DIRECT (POBJECT n_object)),ENTRY (KSTRING ' + text('option') + ') (DIRECT PNULL)]',
        'S_pre.ARRAYS[n_outer].ITEMS = pentry_snapshot*', '$node_children(S_pre,HARRAY n_outer) = [HOBJECT n_object]',
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
        'pconfigcall_capture.PACKS = [pconfigpack]',
        'pconfigcall_capture = pconfigcall_pre[.PACKS = [pconfigpack]]',
        'pconfigpack.INDEX = 0', 'pconfigpack.ARRAY = n_outer', 'pconfigpack.ITEMS = pentry_snapshot*',
        '$config_pack_source_valid(S_capture,pconfigcall_capture,pconfigpack)',
        '$config_unpack_valid(S_capture,pconfigcall_capture,KNOWN (PARRAY n_outer),0)',
        '$call_task_valid(S_capture,CONFIG_UNPACK_NEXT pconfigcall_capture (KNOWN (PARRAY n_outer)) 0)',
        'pconfigpack.ITEMS = $config_pack_capture(S_capture,S_capture.ARRAYS[n_outer].ITEMS)',
        '$config_nodes(pconfigcall_capture) = eps',
        '$task_nodes(CONFIG_UNPACK_NEXT pconfigcall_capture (KNOWN (PARRAY n_outer)) 0) = [HARRAY n_outer]',
        '$node_children(S_capture,HARRAY n_outer) = [HOBJECT n_object]',
        'S_capture.OBJECTS[n_object] = STDINSTANCE',
        '$object_table_at(S_capture.OBJECTTABLES,n_object) = eps',
        '$objectprops_at(S_capture.OBJECTPROPS,n_object) = ([ppropertyslot_pack])',
        'ppropertyslot_pack.STATE = PROP_VALUE (DIRECT pvalue_pack_mark)',
        'ppropertyslot_pack = ppropertyslot_mark[.STATE = PROP_VALUE (DIRECT pvalue_pack_mark)]',
        '$string_bytes(pvalue_pack_mark) = (' + text('pack-mark77') + ')',
        '$string_carrier_valid(S_capture,pvalue_pack_mark)',
        'S_capture.STORE[n_pack_cell] = DEFINED (PARRAY n_outer)', 'S_capture.STORE[n_pack_old] = DEFINED (PARRAY n_outer)',
        'S_capture.STORE[n_object_keep] = DEFINED (POBJECT n_object)',
        'S_capture.STORE[n_value] = DEFINED (PINT 997)', 'S_capture.STORE[n_effects] = DEFINED (PINT 1)',
        'S_capture.STORE[n_call] = DEFINED pvalue_live_call',
        '$string_bytes(pvalue_live_call) = (' + text('ini_get') + ')',
        'S_capture.STORE[n_keep] = DEFINED pvalue_keep',
        'S_capture.SELECTEDCALLS[n_selection] = pselectedcall', 'S_capture.PRECISIONINI = ' + text('14'),
        '$test_outputs(S_capture.EVENTS) = ' + text('B|P|'), *common.public('S_capture'),
        *common.step('S_first', 'S_capture'),
        'pconfigcall_first = pconfigcall_capture[.NAMED = true][.SENT = [NAMED_HOLE,NAMED_SENT (KNOWN (POBJECT n_object))]]',
        'S_first.TODO = (CONFIG_UNPACK_NEXT pconfigcall_first (KNOWN (PARRAY n_outer)) 1) :: ptask_S*',
        '$config_unpack_valid(S_first,pconfigcall_first,KNOWN (PARRAY n_outer),1)',
        '$config_nodes(pconfigcall_first) = [HOBJECT n_object]',
        '$task_nodes(CONFIG_UNPACK_NEXT pconfigcall_first (KNOWN (PARRAY n_outer)) 1) = [HOBJECT n_object,HARRAY n_outer]',
        *common.public('S_first'), *common.step('S_second', 'S_first'),
        'pconfigcall_second = pconfigcall_first[.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (POBJECT n_object))]]',
        'S_second.TODO = (CONFIG_UNPACK_NEXT pconfigcall_second (KNOWN (PARRAY n_outer)) 2) :: ptask_S*',
        '$config_unpack_valid(S_second,pconfigcall_second,KNOWN (PARRAY n_outer),2)',
        '$task_nodes(CONFIG_UNPACK_NEXT pconfigcall_second (KNOWN (PARRAY n_outer)) 2) = [HOBJECT n_object,HARRAY n_outer]',
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
        '$config_ini_rejected_stdclass(S,n_object)', '$config_ini_null_valid(S,pconfigcall_S)',
        '~$config_ini_quiet_value(S,POBJECT n_object)', '~$config_strict(S,pconfigcall_S)',
        '~$config_method_receiver(S,pconfigcall_S)', '~$exit_method_site(S,pconfigcall_S.SITE)', '~$exit_strict(S,pconfigcall_S.SITE)',
        'pconfigcall_S.SELECTION = (n_selection)', 'S.SELECTEDCALLS[n_selection] = pselectedcall',
        '$config_nodes(pconfigcall_S) = [HOBJECT n_object]',
        '$task_nodes(CONFIG_INI_NULL_RESULT pconfigcall_S) = [HOBJECT n_object]',
        '~((HARRAY n_outer) <- $config_nodes(pconfigcall_S))', '$node_children(S,HOBJECT n_object) = eps',
        'S.OBJECTS[n_object] = STDINSTANCE',
        '$object_table_at(S.OBJECTTABLES,n_object) = eps',
        '$objectprops_at(S.OBJECTPROPS,n_object) = ([ppropertyslot_pack])',
        '$config_ini_rejected_slots(S,[ppropertyslot_pack])',
        'S.ARRAYS[n_outer].ITEMS = pentry_snapshot*', 'S.STORE[n_pack_old] = DEFINED (PARRAY n_outer)',
        'S.STORE[n_keep] = DEFINED pvalue_keep',
        'S.PRECISIONINI = ' + text('14'), 'S.USERCONSTANTS = eps', 'S.CURRENT = eps', 'S.FRAMES = eps',
        *unchanged('S','S_capture','STORE ENV EVENTS PRECISIONINI USERCONSTANTS'),
        '$test_outputs(S.EVENTS) = ' + text('B|P|'), *common.public('S'),
        *common.step('S_dispatch', 'S'),
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_deprecated) :: ptask_S*',
        'perrorcall_deprecated.RESUME = CONFIG_INI_NULL_RESULT pconfigcall_S',
        'perrorcall_deprecated.LEVEL = 8192', 'perrorcall_deprecated.MESSAGE = ' + text(MESSAGE),
        'perrorcall_deprecated.MESSAGE = $config_ini_null_message(pconfigcall_S)',
        'perrorcall_deprecated.EVENT = DIAGNOSTIC "Deprecated" perrorcall_deprecated.MESSAGE pconfigcall_S.LINE',
        'perrorcall_deprecated.SITE = pconfigcall_S.SITE', 'perrorcall_deprecated.LINE = pconfigcall_S.LINE',
        '$error_call_valid(S_dispatch,perrorcall_deprecated)',
        *unchanged('S_dispatch', 'S', 'STORE ENV ARRAYS OBJECTS OBJECTPROPS OBJECTTABLES USERCONSTANTS STRINGDATA EVENTS SELECTEDCALLS PRECISIONINI'),
        *common.public('S_dispatch'), *reach('S_handler', 'S_dispatch', 1),
        'S_handler.CURRENT = (pcallcontext_handler)', '$error_context_valid(S_handler,pcallcontext_handler)',
        '$error_context_trigger(S_handler,pcallcontext_handler) = (pconfigcall_S)',
        '$error_handler_trace_values(S_handler,pcallcontext_handler,pconfigcall_S) = [PNULL,POBJECT n_object]',
        *common.public('S_handler'), *reach('S_throw', 'S_handler', 2),
        'S_throw.TODO = (THROW_VALUE porigin_throw z_throw) :: ptask_body*',
        'S_throw.CURRENT = (pcallcontext_handler)', 'S_throw.FRAMES = [pframe_call]',
        'pframe_call.CONTEXT = eps', 'pframe_call.LOCALS = eps',
        'pframe_call.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_S*',
        'perrorcall_entered.RESUME = CONFIG_INI_NULL_RESULT pconfigcall_S',
        'S_throw.STORE[n_saved] = DEFINED (POBJECT n_exception)',
        'S_throw.OBJECTS[n_exception] = THROWABLE pthrowable', 'pthrowable.KIND = "Exception"',
        '$string_bytes($throwable_field(S_throw,n_exception,"message")) = (' + text('unpack-stdclass77-stop') + ')',
        '$throwable_field(S_throw,n_exception,"previous") = PNULL',
        '$throwable_field(S_throw,n_exception,"trace") = PARRAY n_trace',
        'S_throw.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_handler)),ENTRY (KINT 1) (DIRECT (PARRAY n_api))]',
        '$trace_array_field(S_throw,n_handler,' + text('function') + ') = PSTRING ' + text('iniUnpackStdclassReviewDeprecated77'),
        '$trace_array_field(S_throw,n_api,' + text('function') + ') = PSTRING ' + text('ini_set'),
        '$trace_array_field(S_throw,n_api,' + text('line') + ') = PINT pconfigcall_S.LINE',
        '$trace_array_field(S_throw,n_api,' + text('args') + ') = PARRAY n_args',
        'S_throw.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT PNULL),ENTRY (KINT 1) (DIRECT (POBJECT n_object))]',
        '$node_children(S_throw,HARRAY n_args) = [HOBJECT n_object]',
        'n_exception =/= n_object', 'S_throw.OBJECTS[n_object] = STDINSTANCE',
        '$object_table_at(S_throw.OBJECTTABLES,n_object) = eps',
        '$objectprops_at(S_throw.OBJECTPROPS,n_object) = ([ppropertyslot_handler])',
        'ppropertyslot_handler.STATE = PROP_VALUE (DIRECT pvalue_handler_mark)',
        'ppropertyslot_handler = ppropertyslot_mark[.STATE = PROP_VALUE (DIRECT pvalue_handler_mark)]',
        '$string_bytes(pvalue_handler_mark) = (' + text('handler-mark77') + ')',
        '$string_carrier_valid(S_throw,pvalue_handler_mark)',
        '$config_ini_rejected_stdclass(S_throw,n_object)', '$node_children(S_throw,HOBJECT n_object) = eps',
        '(HOBJECT n_object) <- S_throw.ALLOCATIONS',
        'S_throw.STORE[n_pack_old] = DEFINED (PARRAY n_outer)', 'S_throw.STORE[n_keep] = DEFINED pvalue_keep',
        'S_throw.STORE[n_result] = DEFINED (PINT 99)', 'S_throw.STORE[n_effects] = DEFINED (PINT 1)',
        'S_throw.STORE[n_warnings] = DEFINED (PINT 1)', 'S_throw.STORE[n_value] = DEFINED (PINT 123)',
        'S_throw.PRECISIONINI = ' + text('10'),
        'S_throw.USERCONSTANTS = [puserconstant_sibling]', 'puserconstant_sibling.NAME = ' + text('SOURCE77PEER'),
        'puserconstant_sibling.VALUE = PINT 2939', 'puserconstant_sibling.CLASS = PVSCALAR',
        'S_throw.STORE[n_object_keep] = DEFINED (POBJECT n_object)',
        'S_throw.ARRAYS[n_outer].ITEMS = pentry_snapshot*',
        '$node_children(S_throw,HARRAY n_outer) = [HOBJECT n_object]',
        'S_throw.STORE[n_pack_cell] = DEFINED (PARRAY n_pack_live)', 'n_pack_live =/= n_outer',
        '$entry_lookup(S_throw.ARRAYS[n_pack_live].ITEMS,KSTRING ' + text('value') + ') = (DIRECT (PINT 0))',
        '$entry_lookup(S_throw.ARRAYS[n_pack_live].ITEMS,KSTRING ' + text('option') + ') = (DIRECT pvalue_pack_option)',
        '$string_bytes(pvalue_pack_option) = (' + text('precision') + ')',
        '$config_pack_capture(S_throw,S_throw.ARRAYS[n_pack_live].ITEMS) =/= pconfigpack.ITEMS',
        '(HOBJECT n_object) <- $gc_physical_nodes(S_throw.GC.BUFFER)',
        '$test_outputs(S_throw.EVENTS) = ' + text('B|P|D|8192|' + MESSAGE + '|'),
        *unchanged('S_throw', 'S', 'AUTOLOAD CLASSNAMES CLASSCONSTANTCACHE FILEINCLUDEPATH'),
        *common.public('S_throw'), *common.step('S_throwing', 'S_throw'),
        'S_throwing.TODO = (THROW_SEARCH n_exception) :: ptask_body*', *reach('S_thrown', 'S_throwing', 3),
        'S_thrown.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_S*',
        'S_thrown.CURRENT = S.CURRENT', 'S_thrown.ENV = S.ENV',
        'S_thrown.STORE[n_saved] = DEFINED (POBJECT n_exception)',
        'S_thrown.STORE[n_result] = DEFINED (PINT 99)', 'S_thrown.USERCONSTANTS = [puserconstant_sibling]',
        'S_thrown.PRECISIONINI = ' + text('10'), '$config_ini_null_valid(S_thrown,pconfigcall_S)',
        '(HOBJECT n_object) <- $gc_physical_nodes(S_thrown.GC.BUFFER)',
        'S_thrown.STORE[n_keep] = DEFINED pvalue_keep', *common.public('S_thrown'),
        'S_discard = S_thrown[.TODO = (THROW_SEARCH n_exception) :: ptask_S*]',
        'S_expected = $error_handler_restore($identity_read_discard(S_discard,perrorcall_entered.RESUME),perrorcall_entered.CALLBACK)',
        '$gc_buffer_add(S_expected.GC,HOBJECT n_object) = S_expected.GC',
        '$error_read_discard(S_expected,perrorcall_entered.RESUME) = S_expected',
        *common.step('S_after', 'S_thrown'), 'S_after = S_expected',
        '$throwable_live(S_after,n_exception)', 'S_after.STORE[n_result] = DEFINED (PINT 99)',
        'S_after.STORE[n_pack_old] = DEFINED (PARRAY n_outer)',
        'S_after.STORE[n_keep] = DEFINED pvalue_keep', *common.public('S_after')]
    values += ['S_thrown.STORE[n_call] = DEFINED pvalue_handler_call',
        '$string_bytes(pvalue_handler_call) = (' + text('constant') + ')']
    for field in ('.SITE = PORIGIN 0 eps', '.LINE = $(pconfigcall_S.LINE + 1)',
            '.SELECTION = (|S.SELECTEDCALLS|)', '.SELECTION = eps', '.INDEX = 2',
            '.NAMED = false', '.KIND = INTRINSIC_INI_GET',
            '.SENT = pconfigcall_S.SENT[0:1]', '.SENT = pconfigcall_S.SENT ++ [NAMED_SENT (KNOWN PNULL)]'):
        values += ['~$config_ini_null_valid(S,pconfigcall_S[' + field + '])']
    values += ['~$config_ini_null_valid(S[.CODE = eps],pconfigcall_S)',
        '~$config_ini_null_valid(S,pconfigcall_S[.OWNER = (|S.OBJECTS|)])',
        '~$config_ini_null_valid(S[.ALLOCATIONS = eps],pconfigcall_S)',
        '~$config_ini_rejected_stdclass(S,|S.OBJECTS|)', '~$config_ini_rejected_stdclass(S[.OBJECTS = eps],n_object)',
        '~$config_ini_rejected_stdclass(S[.OBJECTPROPS = eps],n_object)',
        '~$config_ini_rejected_stdclass(S[.OBJECTS[n_object] = INTRINSICCLOSURE INTRINSIC_INI_SET],n_object)',
        'S_table = S[.OBJECTTABLES = S.OBJECTTABLES ++ [{OBJECT n_object,TABLE 0}]]',
        '~$config_ini_rejected_stdclass(S_table,n_object)', '~$config_ini_null_valid(S_table,pconfigcall_S)',
        'pvalue_bad = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ' + text('unpack-stdclass-peer77'),
        '~$string_carrier_valid(S,pvalue_bad)']
    for field in ('.PACKS = eps', '.PACKS = [pconfigpack,pconfigpack]'):
        values += ['~$config_ini_null_valid(S,pconfigcall_S[' + field + '])']
    for field in ('.INDEX = 1', '.SITE = PORIGIN 0 eps', '.LINE = $(pconfigpack.LINE + 1)', '.ARRAY = |S.ARRAYS|'):
        values += ['~$config_ini_null_valid(S,pconfigcall_S[.PACKS = [pconfigpack[' + field + ']]])']
    for suffix, items, named in [
            ('numeric', '[ENTRY (KINT 3) (DIRECT PNULL),ENTRY (KINT 7) (DIRECT (POBJECT n_object))]', False),
            ('forward', '[ENTRY (KSTRING ' + text('option') + ') (DIRECT PNULL),ENTRY (KSTRING ' + text('value') + ') (DIRECT (POBJECT n_object))]', True),
            ('mixed', '[ENTRY (KINT 3) (DIRECT PNULL),ENTRY (KSTRING ' + text('value') + ') (DIRECT (POBJECT n_object))]', True)]:
        values += ['pconfigpack_' + suffix + ' = pconfigpack[.ITEMS = ' + items + ']',
            'pconfigcall_' + suffix + ' = pconfigcall_S[.NAMED = ' + str(named).lower() + '][.PACKS = [pconfigpack_' + suffix + ']]',
            '$config_invoke_valid(S,pconfigcall_' + suffix + ')', '$config_ini_null_valid(S,pconfigcall_' + suffix + ')']
    for suffix, items in [
            ('unknown', '[ENTRY (KSTRING ' + text('other') + ') (DIRECT (POBJECT n_object)),ENTRY (KSTRING ' + text('option') + ') (DIRECT PNULL)]'),
            ('duplicate', '[ENTRY (KSTRING ' + text('value') + ') (DIRECT (POBJECT n_object)),ENTRY (KSTRING ' + text('value') + ') (DIRECT PNULL)]'),
            ('late_numeric', '[ENTRY (KSTRING ' + text('value') + ') (DIRECT (POBJECT n_object)),ENTRY (KINT 3) (DIRECT PNULL)]')]:
        values += ['pconfigpack_' + suffix + ' = pconfigpack[.ITEMS = ' + items + ']',
            'pconfigcall_' + suffix + ' = pconfigcall_S[.PACKS = [pconfigpack_' + suffix + ']]',
            '~$config_invoke_valid(S,pconfigcall_' + suffix + ')', '~$config_ini_null_valid(S,pconfigcall_' + suffix + ')']
    for suffix, state in [('carrier', 'PROP_VALUE (DIRECT pvalue_bad)'),
            ('undefined', 'PROP_VALUE (DIRECT PUNDEFINED)'), ('initial', 'PROP_INITIAL'),
            ('unset', 'PROP_UNSET'), ('deferred', 'PROP_DEFERRED (PORIGIN 0 eps)'),
            ('nested', 'PROP_VALUE (DIRECT (PARRAY n_outer))'),
            ('object', 'PROP_VALUE (DIRECT (POBJECT n_object))'),
            ('alias', 'PROP_VALUE (ALIAS n_pack_old)'),
            ('legacy', 'PROP_VALUE (DIRECT (PSTRING ' + text('old77') + '))'),
            ('nan', 'PROP_VALUE (DIRECT (PFLOAT 9221120237041090560))')]:
        values += ['ppropertyslot_' + suffix + ' = ppropertyslot_mark[.STATE = ' + state + ']',
            '~$config_ini_rejected_slots(S,[ppropertyslot_' + suffix + '])',
            'S_badprop_' + suffix + ' = S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS,n_object,[ppropertyslot_' + suffix + '])]',
            '~$config_ini_rejected_stdclass(S_badprop_' + suffix + ',n_object)',
            '~$config_ini_null_valid(S_badprop_' + suffix + ',pconfigcall_S)']
    values += ['ppropertyslot_declared = ppropertyslot_mark[.DECL = (PORIGIN 0 eps)]',
        '~$config_ini_rejected_slots(S,[ppropertyslot_declared])',
        'S_declared = S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS,n_object,[ppropertyslot_declared])]',
        '~$config_ini_rejected_stdclass(S_declared,n_object)',
        '~$config_ini_null_valid(S_declared,pconfigcall_S)', '$config_ini_rejected_slots(S,eps)']
    for field in ('.LEVEL = 2', '.MESSAGE = ' + text('changed'), '.LINE = $(perrorcall_deprecated.LINE + 1)',
            '.EVENT = DIAGNOSTIC "Deprecated" perrorcall_deprecated.MESSAGE $(perrorcall_deprecated.LINE + 1)'):
        values += ['~$error_call_valid(S_expected,perrorcall_deprecated[' + field + '])']
    values += [*budget('S_pre'), *budget('S_capture'), *budget('S_thrown'), *reach('S_recovery', 'S_after', 4),
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
        'S_recovery.STORE[n_keep] = DEFINED pvalue_keep',
        '$config_nodes(pconfigcall_recovery) = eps',
        'S_recovery.PRECISIONINI = ' + text('10'), 'S_recovery.ERRORHANDLER.CALLBACK = eps',
        *common.public('S_recovery'), *common.step('S_recovered', 'S_recovery'),
        'S_recovered.TODO = ptask_recovery*', 'S_recovered.RESULT = KNOWN pvalue_old_precision',
        '$string_bytes(pvalue_old_precision) = (' + text('10') + ')', 'S_recovered.PRECISIONINI = ' + text('12'),
        *unchanged('S_recovered', 'S_recovery', 'STORE ENV OBJECTS OBJECTPROPS OBJECTTABLES USERCONSTANTS SELECTEDCALLS EVENTS'),
        *common.public('S_recovered'), 'S_final = $drive_steps(S_recovered,3000)',
        'S_final.COMPLETION = NORMAL', 'S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.USERCONSTANTS = [puserconstant_sibling]', 'S_final.PRECISIONINI = ' + text('12'),
        'S_final.ERRORHANDLER.CALLBACK = eps',
        *unchanged('S_final', 'S', 'AUTOLOAD CLASSNAMES CLASSCONSTANTCACHE FILEINCLUDEPATH'),
        '$test_outputs(S_final.EVENTS) = ' + text('B|P|D|8192|' + MESSAGE + '|I|99|1|1|S|handler-mark77|0|10|2939|Z|R|10|12|99'),
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
