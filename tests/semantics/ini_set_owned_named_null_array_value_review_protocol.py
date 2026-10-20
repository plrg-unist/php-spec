#!/usr/bin/env python3
"""An explicit named intrinsic call holds its owner and earlier array through throw."""
import json
import os
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import ini_set_owned_named_null_array_value_review_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64
MESSAGE = 'ini_set(): Passing null to parameter #1 ($option) of type string is deprecated'
PREFIX = r"""
dec $test_ini_owned_named_null_array_review_front(pstate, nat) : bool
def $test_ini_owned_named_null_array_review_front(S, 0) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (PARRAY n_array))]
def $test_ini_owned_named_null_array_review_front(S, 1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_call(S,pcallcontext) = (perrorcall)
  -- if perrorcall.RESUME = CONFIG_INI_NULL_RESULT pconfigcall
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_ini_owned_named_null_array_review_front(S, 2) = true
  -- if S.TODO = (THROW_VALUE porigin z) :: ptask_body*
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_call(S,pcallcontext) = (perrorcall)
  -- if perrorcall.RESUME = CONFIG_INI_NULL_RESULT pconfigcall
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_ini_owned_named_null_array_review_front(S, 3) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = CONFIG_INI_NULL_RESULT pconfigcall
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_ini_owned_named_null_array_review_front(S, 4) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_option),NAMED_SENT (KNOWN pvalue)]
  -- if $string_bytes(pvalue_option) = ($ptascii("precision"))
  -- if $string_bytes(pvalue) = ($ptascii("12"))
def $test_ini_owned_named_null_array_review_front(S, 5) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.INDEX = 0
  -- if pconfigcall.SENT = eps
def $test_ini_owned_named_null_array_review_front(S, 6) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.INDEX = 1 /\ pconfigcall.NAMED
  -- if pconfigcall.SENT = [NAMED_HOLE,NAMED_SENT (KNOWN (PARRAY n_array))]
def $test_ini_owned_named_null_array_review_front(S, n_stage) = false -- otherwise
dec $test_ini_owned_named_null_array_review_seek(pstate, nat, nat) : pstate
def $test_ini_owned_named_null_array_review_seek(S, n_stage, 0) = S
def $test_ini_owned_named_null_array_review_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_ini_owned_named_null_array_review_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_ini_owned_named_null_array_review_seek(S, n_stage, n) = $test_ini_owned_named_null_array_review_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_ini_owned_named_null_array_review_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def reach(state, start, stage):
    return [state + '_found = $test_ini_owned_named_null_array_review_seek(' + start + ',' + str(stage) + ',3000)',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_ini_owned_named_null_array_review_front(' + state + ',' + str(stage) + ')']


def unchanged(after, before, fields):
    return [after + '.' + field + ' = ' + before + '.' + field for field in fields.split()]


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)',
        state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)',
        state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def checks(program, path, name):
    assert name == 'strict-explicit-owned-named-null-array-throw-keeps-owner-and-captured-value'
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *reach('S_pre', 'S_initial', 5),
        'S_pre.TODO = (CONFIG_ARGS pconfigcall_pre) :: ptask_S*',
        'pconfigcall_pre.KIND = INTRINSIC_INI_SET', 'pconfigcall_pre.OWNER = (n_owner)',
        'pconfigcall_pre.SELECTION = eps',
        'S_pre.OBJECTS[n_owner] = INTRINSICCLOSURE INTRINSIC_INI_SET',
        '(HOBJECT n_owner) <- S_pre.ALLOCATIONS',
        'pconfigcall_pre.INDEX = 0', 'pconfigcall_pre.PACKS = eps', '~pconfigcall_pre.NAMED',
        'pconfigcall_pre.SENT = eps',
        '$call_task_valid(S_pre,CONFIG_ARGS pconfigcall_pre)',
        '$config_pending_valid(S_pre,pconfigcall_pre,false)',
        '$lookup(S_pre.ENV,' + text('value') + ') = (n_value)',
        'S_pre.STORE[n_value] = DEFINED (PARRAY n_array)',
        'S_pre.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_leaf)]',
        'pvalue_leaf = PSTRING_CARRIER (REQUEST_STRING n_candidate) ' + text('owned-named-array73'),
        '$string_carrier_valid(S_pre,pvalue_leaf)', '(HARRAY n_array) <- S_pre.ALLOCATIONS',
        '$lookup(S_pre.ENV,' + text('arrayKeep') + ') = (n_array_keep)',
        'S_pre.STORE[n_array_keep] = DEFINED (PARRAY n_array)',
        '$lookup(S_pre.ENV,' + text('old') + ') = (n_old)',
        'S_pre.STORE[n_old] = DEFINED (PARRAY n_array)',
        '$lookup(S_pre.ENV,' + text('call') + ') = (n_call)',
        'S_pre.STORE[n_call] = DEFINED (POBJECT n_owner)',
        '$lookup(S_pre.ENV,' + text('keep') + ') = (n_keep)', 'S_pre.STORE[n_keep] = DEFINED (POBJECT n_owner)',
        '$lookup(S_pre.ENV,' + text('option') + ') = (n_option)', 'S_pre.STORE[n_option] = DEFINED PNULL',
        '$lookup(S_pre.ENV,' + text('effects') + ') = (n_effects)', 'S_pre.STORE[n_effects] = DEFINED (PINT 0)',
        '$lookup(S_pre.ENV,' + text('warnings') + ') = (n_warnings)', 'S_pre.STORE[n_warnings] = DEFINED (PINT 0)',
        '$lookup(S_pre.ENV,' + text('saved') + ') = (n_saved)', 'S_pre.STORE[n_saved] = DEFINED PNULL',
        '$lookup(S_pre.ENV,' + text('result') + ') = (n_result)', 'S_pre.STORE[n_result] = DEFINED (PINT 99)',
        '$config_nodes(pconfigcall_pre) = [HOBJECT n_owner]', '$test_outputs(S_pre.EVENTS) = ' + text('B|'),
        *common.public('S_pre'), *reach('S_value', 'S_pre', 6),
        'S_value.TODO = (CONFIG_ARGS pconfigcall_value) :: ptask_S*',
        'pconfigcall_value = pconfigcall_pre[.INDEX = 1][.NAMED = true][.SENT = [NAMED_HOLE,NAMED_SENT (KNOWN (PARRAY n_array))]]',
        '$call_task_valid(S_value,CONFIG_ARGS pconfigcall_value)',
        '$config_pending_valid(S_value,pconfigcall_value,false)',
        '$config_nodes(pconfigcall_value) = [HOBJECT n_owner,HARRAY n_array]',
        '$task_nodes(CONFIG_ARGS pconfigcall_value) = [HOBJECT n_owner,HARRAY n_array]',
        '~$config_ini_null_valid(S_value,pconfigcall_value)',
        'S_value.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_leaf)]',
        'S_value.STORE[n_array_keep] = DEFINED (PARRAY n_array)', 'S_value.STORE[n_old] = DEFINED (PARRAY n_array)',
        'S_value.STORE[n_value] = DEFINED (PARRAY n_array)', 'S_value.STORE[n_effects] = DEFINED (PINT 0)',
        'S_value.STORE[n_result] = DEFINED (PINT 99)',
        'S_value.STORE[n_call] = DEFINED (POBJECT n_owner)',
        'S_value.STORE[n_option] = DEFINED PNULL',
        'S_value.PRECISIONINI = ' + text('14'),
        'S_value.STORE[n_keep] = DEFINED (POBJECT n_owner)',
        'S_value.OBJECTS[n_owner] = INTRINSICCLOSURE INTRINSIC_INI_SET',
        '$test_outputs(S_value.EVENTS) = ' + text('B|'), *common.public('S_value'),
        *reach('S', 'S_value', 0), 'S.TODO = (CONFIG_INVOKE pconfigcall_S) :: ptask_S*',
        'pconfigcall_S = pconfigcall_value[.INDEX = 2][.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (PARRAY n_array))]]',
        '$config_invoke_valid(S,pconfigcall_S)', '$config_selected_valid(S,pconfigcall_S)',
        '$config_ini_rejected_array(S,n_array)', '$config_ini_null_valid(S,pconfigcall_S)',
        '~$config_ini_quiet_value(S,PARRAY n_array)', '~$config_strict(S,pconfigcall_S)',
        '$config_method_receiver(S,pconfigcall_S)',
        '$exit_method_site(S,pconfigcall_S.SITE)', '$exit_strict(S,pconfigcall_S.SITE)',
        'pconfigcall_S.OWNER = (n_owner)', 'pconfigcall_S.SELECTION = eps',
        'S.OBJECTS[n_owner] = INTRINSICCLOSURE INTRINSIC_INI_SET',
        'S.STORE[n_keep] = DEFINED (POBJECT n_owner)',
        '$intrinsic_count(S,pconfigcall_S.SITE) = (2)',
        '$intrinsic_argument(S,pconfigcall_S.SITE,0) = ((expression_value,false,preqbytes_value?,porigin_value,z_value))',
        'preqbytes_value? = (' + text('value') + ')',
        '$config_destination(INTRINSIC_INI_SET,preqbytes_value?,0) = (1)',
        '$intrinsic_argument(S,pconfigcall_S.SITE,1) = ((expression_option,false,preqbytes_option?,porigin_option,z_option))',
        'preqbytes_option? = (' + text('option') + ')',
        '$config_destination(INTRINSIC_INI_SET,preqbytes_option?,1) = (0)',
        '$compiled_read(S,porigin_option) = eps', '$compiled_read(S,porigin_value) = eps',
        '$config_ini_pack_known(S,S.ARRAYS[n_array].ITEMS,eps)',
        '$config_ini_named_array_argument(S,pconfigcall_S,n_array,0)',
        '$config_ini_named_array_argument(S,pconfigcall_S,n_array,1)',
        '~$config_ini_named_array_argument(S,pconfigcall_S,n_array,2)',
        '$config_nodes(pconfigcall_S) = [HOBJECT n_owner,HARRAY n_array]',
        '$task_nodes(CONFIG_INI_NULL_RESULT pconfigcall_S) = [HOBJECT n_owner,HARRAY n_array]',
        '$node_children(S,HARRAY n_array) = eps',
        'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_leaf)]',
        'S.STORE[n_array_keep] = DEFINED (PARRAY n_option_array)', 'n_option_array =/= n_array',
        'S.ARRAYS[n_option_array].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_option_leaf)]',
        '$string_bytes(pvalue_option_leaf) = (' + text('option-array73') + ')',
        'S.STORE[n_old] = DEFINED (PARRAY n_array)',
        'S.STORE[n_value] = DEFINED (PINT 997)',
        'S.STORE[n_call] = DEFINED (POBJECT n_live)',
        'S.OBJECTS[n_live] = INTRINSICCLOSURE INTRINSIC_INI_GET', 'n_live =/= n_owner',
        '(HOBJECT n_live) <- S.ALLOCATIONS',
        'S.STORE[n_option] = DEFINED pvalue_option_live', '$string_bytes(pvalue_option_live) = (' + text('precision') + ')',
        'S.STORE[n_effects] = DEFINED (PINT 1)', 'S.STORE[n_result] = DEFINED (PINT 99)',
        'S.PRECISIONINI = ' + text('14'), 'S.USERCONSTANTS = eps',
        'S.CURRENT = eps', 'S.FRAMES = eps',
        '$test_outputs(S.EVENTS) = ' + text('B|O|'), *common.public('S'),
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
        '$string_bytes($throwable_field(S_throw,n_exception,"message")) = (' + text('owned-named-array73-stop') + ')',
        '$throwable_field(S_throw,n_exception,"previous") = PNULL',
        '$throwable_field(S_throw,n_exception,"trace") = PARRAY n_trace',
        'S_throw.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_handler)),ENTRY (KINT 1) (DIRECT (PARRAY n_api)),ENTRY (KINT 2) (DIRECT (PARRAY n_invoke))]',
        '$trace_array_field(S_throw,n_handler,' + text('function') + ') = PSTRING ' + text('iniOwnedNamedArrayReviewDeprecated73'),
        '$trace_array_field(S_throw,n_api,' + text('function') + ') = PSTRING ' + text('ini_set'),
        '$trace_array_field(S_throw,n_api,' + text('line') + ') = PINT pconfigcall_S.LINE',
        '$trace_array_field(S_throw,n_api,' + text('args') + ') = PARRAY n_args',
        'S_throw.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT PNULL),ENTRY (KINT 1) (DIRECT (PARRAY n_array))]',
        '$node_children(S_throw,HARRAY n_args) = [HARRAY n_array]',
        '$trace_array_field(S_throw,n_invoke,' + text('function') + ') = PSTRING ' + text('__invoke'),
        '$trace_array_field(S_throw,n_invoke,' + text('class') + ') = PSTRING ' + text('Closure'),
        '$trace_array_field(S_throw,n_invoke,' + text('type') + ') = PSTRING ' + text('->'),
        '$trace_array_field(S_throw,n_invoke,' + text('line') + ') = PINT pconfigcall_S.LINE',
        '$trace_array_field(S_throw,n_invoke,' + text('args') + ') = PARRAY n_invoke_args',
        'S_throw.ARRAYS[n_invoke_args].ITEMS = [ENTRY (KINT 0) (DIRECT PNULL),ENTRY (KINT 1) (DIRECT (PARRAY n_array))]',
        '$node_children(S_throw,HARRAY n_invoke_args) = [HARRAY n_array]',
        'S_throw.OBJECTS[n_owner] = INTRINSICCLOSURE INTRINSIC_INI_SET',
        'S_throw.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_leaf)]',
        '$string_carrier_valid(S_throw,pvalue_leaf)', '(HARRAY n_array) <- S_throw.ALLOCATIONS',
        'S_throw.STORE[n_old] = DEFINED (PARRAY n_array)', 'S_throw.STORE[n_keep] = DEFINED (POBJECT n_owner)',
        'S_throw.STORE[n_result] = DEFINED (PINT 99)', 'S_throw.STORE[n_effects] = DEFINED (PINT 1)',
        'S_throw.STORE[n_warnings] = DEFINED (PINT 1)', 'S_throw.STORE[n_value] = DEFINED (PINT 123)',
        'S_throw.PRECISIONINI = ' + text('10'),
        'S_throw.USERCONSTANTS = [puserconstant_sibling]', 'puserconstant_sibling.NAME = ' + text('SOURCE73PEER'),
        'puserconstant_sibling.VALUE = PINT 2677', 'puserconstant_sibling.CLASS = PVSCALAR',
        'S_throw.STORE[n_array_keep] = DEFINED (PARRAY n_mutated)', 'n_mutated =/= n_array',
        'S_throw.ARRAYS[n_mutated].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_mutated)]',
        '$string_bytes(pvalue_mutated) = (' + text('handler-array73') + ')',
        '(HARRAY n_array) <- $gc_physical_nodes(S_throw.GC.BUFFER)',
        '(HOBJECT n_owner) <- $gc_physical_nodes(S_throw.GC.BUFFER)',
        '$test_outputs(S_throw.EVENTS) = ' + text('B|O|D|8192|' + MESSAGE + '|'),
        *unchanged('S_throw', 'S', 'AUTOLOAD CLASSNAMES CLASSCONSTANTCACHE FILEINCLUDEPATH'),
        *common.public('S_throw'), *common.step('S_throwing', 'S_throw'),
        'S_throwing.TODO = (THROW_SEARCH n_exception) :: ptask_body*', *reach('S_thrown', 'S_throwing', 3),
        'S_thrown.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_S*',
        'S_thrown.CURRENT = S.CURRENT', 'S_thrown.ENV = S.ENV',
        'S_thrown.STORE[n_saved] = DEFINED (POBJECT n_exception)',
        'S_thrown.STORE[n_result] = DEFINED (PINT 99)', 'S_thrown.USERCONSTANTS = [puserconstant_sibling]',
        'S_thrown.PRECISIONINI = ' + text('10'), '$config_ini_null_valid(S_thrown,pconfigcall_S)',
        '(HARRAY n_array) <- $gc_physical_nodes(S_thrown.GC.BUFFER)',
        '(HOBJECT n_owner) <- $gc_physical_nodes(S_thrown.GC.BUFFER)',
        'S_thrown.OBJECTS[n_owner] = INTRINSICCLOSURE INTRINSIC_INI_SET',
        'S_thrown.STORE[n_keep] = DEFINED (POBJECT n_owner)', *common.public('S_thrown'),
        'S_discard = S_thrown[.TODO = (THROW_SEARCH n_exception) :: ptask_S*]',
        'S_expected = $error_handler_restore($identity_read_discard(S_discard,perrorcall_entered.RESUME),perrorcall_entered.CALLBACK)',
        '$gc_buffer_add(S_expected.GC,HARRAY n_array) = S_expected.GC',
        '$gc_buffer_add(S_expected.GC,HOBJECT n_owner) = S_expected.GC',
        '$error_read_discard(S_expected,perrorcall_entered.RESUME) = S_expected',
        *common.step('S_after', 'S_thrown'), 'S_after = S_expected',
        '$throwable_live(S_after,n_exception)', 'S_after.STORE[n_result] = DEFINED (PINT 99)',
        'S_after.STORE[n_old] = DEFINED (PARRAY n_array)',
        'S_after.STORE[n_keep] = DEFINED (POBJECT n_owner)',
        'S_after.OBJECTS[n_owner] = INTRINSICCLOSURE INTRINSIC_INI_SET', *common.public('S_after')]
    for variable, spelling in [('call', 'constant'), ('option', 'handler-option73')]:
        values += ['S_thrown.STORE[n_' + variable + '] = DEFINED pvalue_handler_' + variable,
            '$string_bytes(pvalue_handler_' + variable + ') = (' + text(spelling) + ')']
    for field in ('.SITE = PORIGIN 0 eps', '.LINE = $(pconfigcall_S.LINE + 1)',
            '.SELECTION = (|S.SELECTEDCALLS|)', '.INDEX = 1', '.OWNER = (n_live)', '.OWNER = eps',
            '.NAMED = false', '.KIND = INTRINSIC_INI_GET',
            '.SENT = pconfigcall_S.SENT[0:1]', '.SENT = pconfigcall_S.SENT ++ [NAMED_SENT (KNOWN PNULL)]'):
        values += ['~$config_ini_null_valid(S,pconfigcall_S[' + field + '])']
    values += ['~$config_ini_null_valid(S[.CODE = eps],pconfigcall_S)',
        '~$config_ini_null_valid(S,pconfigcall_S[.OWNER = (|S.OBJECTS|)])',
        '~$config_ini_null_valid(S[.OBJECTS[n_owner] = INTRINSICCLOSURE INTRINSIC_INI_GET],pconfigcall_S)',
        '~$config_ini_null_valid(S[.ALLOCATIONS = eps],pconfigcall_S)',
        '~$config_ini_rejected_array(S,|S.ARRAYS|)', '~$config_ini_rejected_array(S[.ARRAYS = eps],n_array)',
        'pconfigpack_bad = {INDEX 0,SITE pconfigcall_S.SITE,LINE pconfigcall_S.LINE,ARRAY n_array,ITEMS S.ARRAYS[n_array].ITEMS}',
        '~$config_ini_null_valid(S,pconfigcall_S[.PACKS = [pconfigpack_bad]])',
        'pvalue_bad = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ' + text('owned-named-array73'),
        '~$string_carrier_valid(S,pvalue_bad)']
    for suffix, item in [('carrier', 'DIRECT pvalue_bad'), ('undefined', 'DIRECT PUNDEFINED'),
            ('nested', 'DIRECT (PARRAY n_array)'), ('object', 'DIRECT (POBJECT 0)'),
            ('alias', 'ALIAS n_old'), ('legacy', 'DIRECT (PSTRING ' + text('old73') + ')'),
            ('nan', 'DIRECT (PFLOAT 9221120237041090560)')]:
        values += ['pentry_' + suffix + '* = [ENTRY (KINT 0) (' + item + ')]',
            '~$config_ini_rejected_entries(S,pentry_' + suffix + '*)',
            'S_badarray_' + suffix + ' = S[.ARRAYS[n_array].ITEMS = pentry_' + suffix + '*]',
            '~$config_ini_rejected_array(S_badarray_' + suffix + ',n_array)',
            '~$config_ini_null_valid(S_badarray_' + suffix + ',pconfigcall_S)']
    for field in ('.LEVEL = 2', '.MESSAGE = ' + text('changed'), '.LINE = $(perrorcall_deprecated.LINE + 1)',
            '.EVENT = DIAGNOSTIC "Deprecated" perrorcall_deprecated.MESSAGE $(perrorcall_deprecated.LINE + 1)'):
        values += ['~$error_call_valid(S_expected,perrorcall_deprecated[' + field + '])']
    values += [*budget('S_pre'), *budget('S_value'), *budget('S_thrown'), *reach('S_recovery', 'S_after', 4),
        'S_recovery.TODO = (CONFIG_INVOKE pconfigcall_recovery) :: ptask_recovery*',
        'pconfigcall_recovery.OWNER = (n_owner)', 'pconfigcall_recovery.SELECTION = eps',
        'pconfigcall_recovery.INDEX = 2', 'pconfigcall_recovery.PACKS = eps', '~pconfigcall_recovery.NAMED',
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
        '$string_bytes(pvalue_old_precision) = (' + text('10') + ')', 'S_recovered.PRECISIONINI = ' + text('12'),
        *unchanged('S_recovered', 'S_recovery', 'STORE ENV OBJECTS USERCONSTANTS SELECTEDCALLS EVENTS'),
        *common.public('S_recovered'), 'S_final = $drive_steps(S_recovered,3000)',
        'S_final.COMPLETION = NORMAL', 'S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.USERCONSTANTS = [puserconstant_sibling]', 'S_final.PRECISIONINI = ' + text('12'),
        'S_final.ERRORHANDLER.CALLBACK = eps',
        *unchanged('S_final', 'S', 'AUTOLOAD CLASSNAMES CLASSCONSTANTCACHE FILEINCLUDEPATH'),
        '$test_outputs(S_final.EVENTS) = ' + text('B|O|D|8192|' + MESSAGE + '|I|99|1|1|handler-array73|owned-named-array73|10|2677|Z|R|10|12|99'),
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
