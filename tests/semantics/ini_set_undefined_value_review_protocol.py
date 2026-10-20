#!/usr/bin/env python3
"""The first undefined-argument Warning keeps its old receiver until cancellation."""
import json
import os
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import ini_set_undefined_value_review_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64
MESSAGE = 'Undefined variable $missing'
PREFIX = r"""
dec $test_ini_missing_review_front(pstate, nat) : bool
def $test_ini_missing_review_front(S, 0) = true
  -- if S.TODO = (CONFIG_SEND pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.INDEX = 1
  -- if S.RESULT = VARIABLE ptbytes z
def $test_ini_missing_review_front(S, 1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_call(S,pcallcontext) = (perrorcall)
  -- if perrorcall.RESUME = ERROR_READ_RESULT perrorread
  -- if perrorread.ORIGINAL = CONFIG_SEND pconfigcall
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_ini_missing_review_front(S, 2) = true
  -- if S.TODO = (THROW_VALUE porigin z) :: ptask_body*
  -- if $test_ini_missing_review_front(S,1)
def $test_ini_missing_review_front(S, 3) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ERROR_READ_RESULT perrorread
  -- if perrorread.ORIGINAL = CONFIG_SEND pconfigcall
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_ini_missing_review_front(S, 4) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_option),NAMED_SENT (KNOWN pvalue)]
  -- if $string_bytes(pvalue_option) = ($ptascii("precision"))
  -- if $string_bytes(pvalue) = ($ptascii("12"))
def $test_ini_missing_review_front(S, n_stage) = false -- otherwise
dec $test_ini_missing_review_seek(pstate, nat, nat) : pstate
def $test_ini_missing_review_seek(S, n_stage, 0) = S
def $test_ini_missing_review_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_ini_missing_review_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_ini_missing_review_seek(S, n_stage, n) = $test_ini_missing_review_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_ini_missing_review_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def reach(state, start, stage):
    return [state + '_found = $test_ini_missing_review_seek(' + start + ',' + str(stage) + ',3000)',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_ini_missing_review_front(' + state + ',' + str(stage) + ')']


def unchanged(after, before, fields):
    return [after + '.' + field + ' = ' + before + '.' + field for field in fields.split()]


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)',
        state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)',
        state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def checks(program, path, name):
    assert name == 'owned-first-warning-throw-cancels-null-option-reception'
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *reach('S', 'S_initial', 0),
        'S.TODO = (CONFIG_SEND pconfigcall) :: ptask_tail*',
        'pconfigcall.KIND = INTRINSIC_INI_SET', 'pconfigcall.OWNER = (n_owner)',
        'pconfigcall.SELECTION = eps', 'pconfigcall.INDEX = 1', 'pconfigcall.PACKS = eps', '~pconfigcall.NAMED',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN PNULL)]',
        '$intrinsic_count(S,pconfigcall.SITE) = (2)',
        '$intrinsic_argument(S,pconfigcall.SITE,0) = ((expression_option,false,eps,porigin_option,z_option))',
        '$intrinsic_argument(S,pconfigcall.SITE,1) = ((expression_value,false,eps,porigin_value,z_value))',
        '$compiled_read(S,porigin_option) = eps', '$compiled_read(S,porigin_value) = eps',
        '$config_ini_named_stdclass_argument(S,pconfigcall,0)',
        'S.RESULT = VARIABLE ' + text('missing') + ' z_value', 'pbase = S.BASE',
        'S.ORIGIN = (pconfigcall.SITE)', '$config_pending_valid(S,pconfigcall,false)',
        '$call_task_valid(S,CONFIG_SEND pconfigcall)', '$config_selected_valid(S,pconfigcall)',
        '~$config_invoke_valid(S,pconfigcall)', '~$config_ini_null_valid(S,pconfigcall)',
        '$config_method_receiver(S,pconfigcall)', '$exit_strict(S,pconfigcall.SITE)', '~$config_strict(S,pconfigcall)',
        '~$pipe_site(S,pconfigcall.SITE)', '$error_missing_operand(S,S.RESULT)',
        '$error_read_plan(S) = (perrorread)',
        'perrorread.ORIGINAL = CONFIG_SEND pconfigcall', 'perrorread.TASK = CONFIG_SEND pconfigcall',
        'perrorread.INPUT = S.RESULT', 'perrorread.RESULT = KNOWN PNULL', 'perrorread.BASE = pbase',
        'perrorread.NAME = ' + text('missing'), 'perrorread.LINE = z_value',
        '$error_read_state_shape(S,perrorread.ORIGINAL,perrorread.INPUT,perrorread.BASE) = (perrorread)',
        '$error_read_shape(perrorread.ORIGINAL,perrorread.INPUT,perrorread.BASE) = eps',
        '$error_read_source(S,perrorread)', '$error_read_valid(S,perrorread)', '$error_read_pending(S)',
        '$operand_nodes(perrorread.RESULT) = eps', '$base_nodes(perrorread.BASE) = eps',
        '$config_nodes(pconfigcall) = [HOBJECT n_owner]',
        '$task_nodes(CONFIG_SEND pconfigcall) = [HOBJECT n_owner]',
        '$task_nodes(ERROR_READ_RESULT perrorread) = [HOBJECT n_owner]',
        'S.OBJECTS[n_owner] = INTRINSICCLOSURE INTRINSIC_INI_SET', '(HOBJECT n_owner) <- S.ALLOCATIONS',
        '$node_children(S,HOBJECT n_owner) = eps',
        '$lookup(S.ENV,' + text('call') + ') = (n_call)', 'S.STORE[n_call] = DEFINED (POBJECT n_owner)',
        '$lookup(S.ENV,' + text('keep') + ') = (n_keep)', 'S.STORE[n_keep] = DEFINED (POBJECT n_owner)',
        '$lookup(S.ENV,' + text('replacement') + ') = (n_replacement)',
        'S.STORE[n_replacement] = DEFINED (POBJECT n_getter)', 'n_getter =/= n_owner',
        'S.OBJECTS[n_getter] = INTRINSICCLOSURE INTRINSIC_INI_GET',
        '$lookup(S.ENV,' + text('option') + ') = (n_option)', 'S.STORE[n_option] = DEFINED PNULL',
        '$lookup(S.ENV,' + text('warningKeep') + ') = (n_warning_keep)', 'S.STORE[n_warning_keep] = DEFINED PNULL',
        '$lookup(S.ENV,' + text('warnings') + ') = (n_warnings)', 'S.STORE[n_warnings] = DEFINED (PINT 0)',
        '$lookup(S.ENV,' + text('deprecated') + ') = (n_deprecated)', 'S.STORE[n_deprecated] = DEFINED (PINT 0)',
        '$lookup(S.ENV,' + text('saved') + ') = (n_saved)', 'S.STORE[n_saved] = DEFINED PNULL',
        '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
        'S.PRECISIONINI = ' + text('14'), 'S.USERCONSTANTS = eps', 'S.CURRENT = eps', 'S.FRAMES = eps',
        '$test_outputs(S.EVENTS) = ' + text('B|'), *common.public('S'),
        *common.step('S_dispatch','S'),
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ERROR_READ_RESULT perrorread', 'perrorcall.LEVEL = 2',
        'perrorcall.MESSAGE = ' + text(MESSAGE), 'perrorcall.LINE = z_value',
        'perrorcall.SITE = pconfigcall.SITE', 'perrorcall.EVENT = WARNING ' + text('missing') + ' z_value',
        '$error_call_valid(S_dispatch,perrorcall)',
        *unchanged('S_dispatch','S','STORE ENV ARRAYS OBJECTS USERCONSTANTS EVENTS PRECISIONINI'),
        *common.public('S_dispatch'), *reach('S_handler','S_dispatch',1),
        'S_handler.CURRENT = (pcallcontext_handler)', '$error_context_valid(S_handler,pcallcontext_handler)',
        '$error_context_call(S_handler,pcallcontext_handler) = (perrorcall_entered)',
        'perrorcall_entered.RESUME = ERROR_READ_RESULT perrorread',
        '$error_context_trigger(S_handler,pcallcontext_handler) = eps',
        '$task_nodes(perrorcall_entered.RESUME) = [HOBJECT n_owner]',
        *common.public('S_handler'), *reach('S_throw','S_handler',2),
        'S_throw.TODO = (THROW_VALUE porigin_throw z_throw) :: ptask_body*',
        'S_throw.CURRENT = (pcallcontext_handler)', 'S_throw.FRAMES = [pframe_global]',
        'pframe_global.CONTEXT = eps', 'pframe_global.LOCALS = eps',
        'pframe_global.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'S_throw.STORE[n_saved] = DEFINED (POBJECT n_exception)',
        'S_throw.OBJECTS[n_exception] = THROWABLE pthrowable', 'pthrowable.KIND = "Exception"',
        '$string_bytes($throwable_field(S_throw,n_exception,"message")) = (' + text('undefined-value85-stop') + ')',
        '$throwable_field(S_throw,n_exception,"previous") = PNULL',
        '$throwable_field(S_throw,n_exception,"trace") = PARRAY n_trace',
        'S_throw.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_handler))]',
        '$trace_array_field(S_throw,n_handler,' + text('function') + ') = PSTRING ' + text('iniUndefinedValueReviewWarning85'),
        '$node_children(S_throw,HARRAY n_trace) = [HARRAY n_handler]',
        '$lookup(S_throw.ENV,' + text('missing') + ') = (n_missing)',
        'S_throw.STORE[n_missing] = DEFINED (PARRAY n_current)',
        'S_throw.STORE[n_warning_keep] = DEFINED (PARRAY n_current)',
        'S_throw.ARRAYS[n_current].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 71))]',
        '(HARRAY n_current) <- S_throw.ALLOCATIONS', '$node_children(S_throw,HARRAY n_current) = eps',
        'S_throw.STORE[n_call] = DEFINED (POBJECT n_getter)',
        'S_throw.STORE[n_option] = DEFINED pvalue_option_live', '$string_bytes(pvalue_option_live) = (' + text('precision') + ')',
        'S_throw.STORE[n_keep] = DEFINED (POBJECT n_owner)',
        'S_throw.STORE[n_result] = DEFINED (PINT 99)', 'S_throw.STORE[n_warnings] = DEFINED (PINT 1)',
        'S_throw.STORE[n_deprecated] = DEFINED (PINT 0)', 'S_throw.PRECISIONINI = ' + text('10'),
        'S_throw.USERCONSTANTS = [puserconstant]', 'puserconstant.NAME = ' + text('SOURCE85PEER'),
        'puserconstant.VALUE = PINT 3419', 'puserconstant.CLASS = PVSCALAR',
        '(HOBJECT n_owner) <- $gc_physical_nodes(S_throw.GC.BUFFER)',
        '$test_outputs(S_throw.EVENTS) = ' + text('B|W|2|' + MESSAGE + '|'),
        *common.public('S_throw'), *common.step('S_throwing','S_throw'),
        'S_throwing.TODO = (THROW_SEARCH n_exception) :: ptask_body*', *reach('S_thrown','S_throwing',3),
        'S_thrown.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'S_thrown.CURRENT = eps', 'S_thrown.FRAMES = eps',
        '$lookup(S_thrown.ENV,' + text('missing') + ') = (n_missing)',
        'S_thrown.STORE[n_missing] = DEFINED (PARRAY n_current)',
        'S_thrown.STORE[n_keep] = DEFINED (POBJECT n_owner)',
        'S_thrown.STORE[n_result] = DEFINED (PINT 99)', 'S_thrown.STORE[n_deprecated] = DEFINED (PINT 0)',
        '$error_read_valid(S_thrown,perrorread)', '~$error_missing_operand(S_thrown,perrorread.INPUT)',
        '(HOBJECT n_owner) <- $gc_physical_nodes(S_thrown.GC.BUFFER)',
        '$task_nodes(ERROR_HANDLER_RESULT perrorcall_entered) = [HOBJECT n_owner]', *common.public('S_thrown'),
        'S_discard = S_thrown[.TODO = (THROW_SEARCH n_exception) :: ptask_tail*]',
        'S_expected = $error_handler_restore($identity_read_discard(S_discard,perrorcall_entered.RESUME),perrorcall_entered.CALLBACK)',
        '$gc_buffer_add(S_expected.GC,HOBJECT n_owner) = S_expected.GC',
        '$error_read_discard(S_expected,perrorcall_entered.RESUME) = S_expected',
        *common.step('S_after','S_thrown'), 'S_after = S_expected', '$throwable_live(S_after,n_exception)',
        'S_after.STORE[n_missing] = DEFINED (PARRAY n_current)',
        'S_after.STORE[n_result] = DEFINED (PINT 99)', 'S_after.STORE[n_deprecated] = DEFINED (PINT 0)',
        '$test_outputs(S_after.EVENTS) = ' + text('B|W|2|' + MESSAGE + '|'), *common.public('S_after')]
    for field in ('.KIND = INTRINSIC_INI_GET', '.INDEX = 0', '.INDEX = 2', '.NAMED = true',
            '.OWNER = eps', '.OWNER = (n_getter)', '.OWNER = (|S.OBJECTS|)',
            '.SELECTION = (|S.SELECTEDCALLS|)', '.SITE = PORIGIN 0 eps', '.LINE = $(pconfigcall.LINE + 1)',
            '.SENT = eps', '.SENT = [NAMED_SENT (KNOWN (PINT 0))]'):
        values += ['perrorread_bad_' + str(len(values)) + ' = perrorread[.ORIGINAL = CONFIG_SEND pconfigcall[' + field + ']][.TASK = CONFIG_SEND pconfigcall[' + field + ']]']
        bad = 'perrorread_bad_' + str(len(values)-1)
        values += ['~$error_read_valid(S,' + bad + ')']
    values += ['pconfigpack_bad = {INDEX 0,SITE porigin_value,LINE z_value,ARRAY n_current,ITEMS eps}',
        '~$error_read_valid(S,perrorread[.ORIGINAL = CONFIG_SEND pconfigcall[.PACKS = [pconfigpack_bad]]][.TASK = CONFIG_SEND pconfigcall[.PACKS = [pconfigpack_bad]]])',
        '~$error_read_valid(S[.CODE = eps],perrorread)',
        '~$error_read_valid(S,perrorread[.NAME = ' + text('other') + '])',
        '~$error_read_valid(S,perrorread[.LINE = $(z_value + 1)])',
        '~$error_read_valid(S,perrorread[.RESULT = KNOWN (PINT 71)])',
        '~$error_read_valid(S,perrorread[.INPUT = KNOWN PNULL])',
        '~$error_read_valid(S,perrorread[.INPUT = REFERENCE n_missing])',
        '$error_read_state_shape(S,CONFIG_SEND pconfigcall,KNOWN PNULL,pbase) = eps']
    for field in ('.LEVEL = 8192', '.MESSAGE = ' + text('changed'), '.LINE = $(z_value + 1)',
            '.EVENT = WARNING ' + text('other') + ' z_value'):
        values += ['~$error_call_valid(S_dispatch,perrorcall[' + field + '])']
    values += [*budget('S'), *budget('S_dispatch'), *budget('S_thrown'), *reach('S_recovery','S_after',4),
        'S_recovery.TODO = (CONFIG_INVOKE pconfigcall_recovery) :: ptask_recovery*',
        'pconfigcall_recovery.KIND = INTRINSIC_INI_SET', 'pconfigcall_recovery.OWNER = (n_owner)',
        'pconfigcall_recovery.SELECTION = eps', 'pconfigcall_recovery.INDEX = 2', 'pconfigcall_recovery.PACKS = eps',
        '~pconfigcall_recovery.NAMED', '~$config_method_receiver(S_recovery,pconfigcall_recovery)',
        '$config_strict(S_recovery,pconfigcall_recovery)', '$config_invoke_valid(S_recovery,pconfigcall_recovery)',
        'pconfigcall_recovery.SENT = [NAMED_SENT (KNOWN pvalue_precision),NAMED_SENT (KNOWN pvalue_new_precision)]',
        '$string_bytes(pvalue_precision) = (' + text('precision') + ')', '$string_bytes(pvalue_new_precision) = (' + text('12') + ')',
        'S_recovery.PRECISIONINI = ' + text('10'), 'S_recovery.ERRORHANDLER.CALLBACK = eps',
        'S_recovery.STORE[n_keep] = DEFINED (POBJECT n_owner)',
        'S_recovery.STORE[n_missing] = DEFINED (PARRAY n_current)',
        '$config_nodes(pconfigcall_recovery) = [HOBJECT n_owner]',
        *common.public('S_recovery'), *common.step('S_recovered','S_recovery'),
        'S_recovered.TODO = ptask_recovery*', 'S_recovered.RESULT = KNOWN pvalue_old_precision',
        '$string_bytes(pvalue_old_precision) = (' + text('10') + ')', 'S_recovered.PRECISIONINI = ' + text('12'),
        *unchanged('S_recovered','S_recovery','STORE ENV OBJECTS ARRAYS USERCONSTANTS EVENTS'),
        *common.public('S_recovered'), 'S_final = $drive_steps(S_recovered,3000)',
        'S_final.COMPLETION = NORMAL', 'S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.ERRORHANDLER.CALLBACK = eps', 'S_final.USERCONSTANTS = [puserconstant]',
        'S_final.PRECISIONINI = ' + text('12'),
        '$test_outputs(S_final.EVENTS) = ' + text('B|W|2|' + MESSAGE + '|I|99|1|0|71|71|S|3419|Z|R|10|12|99'),
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
