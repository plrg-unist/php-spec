#!/usr/bin/env python3
"""A captured getter is rejected as a value, then remains a real callable."""
import json
import os
from pathlib import Path

import ini_set_null_stdclass_value_protocol as shared
import ini_set_unpack_null_stdclass_value_protocol as base
import ini_set_null_getter_closure_value_sources as sources

driver, common, text, b64 = shared.driver, shared.common, shared.text, shared.b64
MESSAGE, VALUE_ERROR, OPTION_ERROR = shared.MESSAGE, shared.VALUE_ERROR, shared.OPTION_ERROR
reach, budget, unchanged = shared.reach, shared.budget, shared.unchanged
PREFIX = shared.PREFIX + r"""
dec $test_ini_value_getter_front(pstate) : bool
def $test_ini_value_getter_front(S) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_GET
  -- if pconfigcall.OWNER = (n_object)
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue)]
  -- if $string_bytes(pvalue) = ($ptascii("precision"))
def $test_ini_value_getter_front(S) = false -- otherwise
dec $test_ini_value_getter_seek(pstate, nat) : pstate
def $test_ini_value_getter_seek(S, 0) = S
def $test_ini_value_getter_seek(S, n) = S
  -- if $(n > 0)
  -- if $test_ini_value_getter_front(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_ini_value_getter_seek(S, n) = $test_ini_value_getter_seek($drive_steps($test_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_ini_value_getter_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def front(state, start, selected):
    call, obj = 'pconfigcall_' + state, 'n_object_' + state
    values = [*reach(state, start, 0), state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
        call + '.KIND = INTRINSIC_INI_SET', call + '.OWNER = eps', call + '.PACKS = eps',
        call + '.INDEX = 2', '~' + call + '.NAMED',
        call + '.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (POBJECT ' + obj + '))]',
        '$config_invoke_valid(' + state + ',' + call + ')', '$config_selected_valid(' + state + ',' + call + ')',
        '$config_ini_rejected_getter_closure(' + state + ',' + obj + ')',
        state + '.OBJECTS[' + obj + '] = INTRINSICCLOSURE INTRINSIC_INI_GET',
        '(HOBJECT ' + obj + ') <- ' + state + '.ALLOCATIONS', '$closure_live_object_valid(' + state + ',' + obj + ')',
        '$node_children(' + state + ',HOBJECT ' + obj + ') = eps',
        '~$config_ini_quiet_value(' + state + ',POBJECT ' + obj + ')',
        '~$config_ini_rejected_stdclass(' + state + ',' + obj + ')',
        '$objectprops_at(' + state + '.OBJECTPROPS,' + obj + ') = eps',
        '$object_table_at(' + state + '.OBJECTTABLES,' + obj + ') = eps',
        '$config_nodes(' + call + ') = [HOBJECT ' + obj + ']',
        '$task_nodes(CONFIG_INI_NULL_RESULT ' + call + ') = [HOBJECT ' + obj + ']',
        '$intrinsic_argument(' + state + ',' + call + '.SITE,0) = ((expression_option_' + state + ',false,eps,porigin_option_' + state + ',z_option_' + state + '))',
        '$intrinsic_argument(' + state + ',' + call + '.SITE,1) = ((expression_value_' + state + ',false,eps,porigin_value_' + state + ',z_value_' + state + '))',
        '$compiled_read(' + state + ',porigin_value_' + state + ') = eps',
        '$config_ini_named_stdclass_argument(' + state + ',' + call + ',0)',
        '$config_ini_named_stdclass_argument(' + state + ',' + call + ',1)',
        '~$config_method_receiver(' + state + ',' + call + ')',
        state + '.CURRENT = eps', state + '.FRAMES = eps', *common.public(state)]
    if selected:
        values += [call + '.SELECTION = (n_selection_' + state + ')',
            state + '.SELECTEDCALLS[n_selection_' + state + '].OWNER = eps',
            state + '.SELECTEDCALLS[n_selection_' + state + '].KIND = INTRINSIC_INI_SET',
            state + '.SELECTEDCALLS[n_selection_' + state + '].SITE = ' + call + '.SITE',
            state + '.SELECTEDCALLS[n_selection_' + state + '].LINE = ' + call + '.LINE']
    else:
        values += [call + '.SELECTION = eps']
    return values


def returned(state, precision, result):
    values = shared.returned(state, precision, result, 'unused79')
    old = shared.mark(state + '_return', 'n_object_' + state,
        '(PSTRING_CARRIER INTERNED_STRING ' + text('unused79') + ')')[0]
    assert values.count(old) == 1
    values[values.index(old)] = state + '_return.OBJECTS[n_object_' + state + '] = INTRINSICCLOSURE INTRINSIC_INI_GET'
    return values


def error(state, start, strict=False, default=False):
    return [*base.error(state, start, strict=strict, default=default),
        state + '_error.OBJECTS[n_object_' + state + '] = INTRINSICCLOSURE INTRINSIC_INI_GET']


def refusals(state):
    call, obj = 'pconfigcall_' + state, 'n_object_' + state
    values = []
    for field in ('.SITE = PORIGIN 0 eps', '.LINE = $(' + call + '.LINE + 1)', '.INDEX = 1',
            '.OWNER = (' + obj + ')', '.NAMED = true', '.KIND = INTRINSIC_INI_GET',
            '.SELECTION = (|' + state + '.SELECTEDCALLS|)', '.SENT = ' + call + '.SENT[0:1]'):
        values += ['~$config_ini_null_valid(' + state + ',' + call + '[' + field + '])']
    values += ['~$config_ini_null_valid(' + state + '[.CODE = eps],' + call + ')',
        '~$config_ini_rejected_getter_closure(' + state + ',|' + state + '.OBJECTS|)',
        '~$config_ini_rejected_getter_closure(' + state + '[.ALLOCATIONS = eps],' + obj + ')']
    for kind in ('STDINSTANCE', 'INTRINSICCLOSURE INTRINSIC_INI_SET', 'NAMEDCLOSURE (PORIGIN 0 eps)'):
        values += ['~$config_ini_rejected_getter_closure(' + state + '[.OBJECTS[' + obj + '] = ' + kind + '],' + obj + ')']
    return values


def getter(state, start, obj, precision, strict=False):
    call, after = 'pconfigcall_' + state, state + '_after'
    return [state + '_found = $test_ini_value_getter_seek(' + start + ',3000)',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]', '$test_ini_value_getter_front(' + state + ')',
        state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
        call + '.OWNER = (' + obj + ')', call + '.SELECTION = eps', call + '.INDEX = 1',
        '~' + call + '.NAMED', call + '.PACKS = eps',
        call + '.SENT = [NAMED_SENT (KNOWN pvalue_key_' + state + ')]',
        '$string_bytes(pvalue_key_' + state + ') = (' + text('precision') + ')',
        '$config_invoke_valid(' + state + ',' + call + ')', '$config_selected_valid(' + state + ',' + call + ')',
        '$config_ini_rejected_getter_closure(' + state + ',' + obj + ')',
        '$config_nodes(' + call + ') = [HOBJECT ' + obj + ']',
        ('~' if not strict else '') + '$config_strict(' + state + ',' + call + ')',
        '~$config_ini_null_valid(' + state + ',' + call + ')', state + '.ERRORHANDLER.CALLBACK = eps',
        state + '.PRECISIONINI = ' + text(precision), *common.public(state), *common.step(after, state),
        after + '.TODO = ptask_' + state + '*', after + '.RESULT = KNOWN pvalue_precision_' + state,
        '$string_bytes(pvalue_precision_' + state + ') = (' + text(precision) + ')',
        *unchanged(after, state, 'STORE ENV OBJECTS OBJECTPROPS OBJECTTABLES USERCONSTANTS SELECTEDCALLS EVENTS PRECISIONINI'),
        *common.public(after)]


def setter(start, old_precision, strict=False):
    values = base.recovery(start, old_precision, strict)
    old = '$lookup(S_recovery.ENV,' + text('keep') + ') = (n_keep_recovery)'
    assert values.count(old) == 1
    values[values.index(old)] = old.replace(text('keep'), text('callKeep'))
    return values + ['S_recovery.SELECTEDCALLS[n_selection_recovery].OWNER = eps']


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET']
    if name == 'null-getter-closure-default-and-true-handler-keep-original-value':
        values += [*front('S_default', 'S_initial', False), '$compiled_read(S_default,porigin_option_S_default) = (PNULL)',
            '~$config_strict(S_default,pconfigcall_S_default)', '$config_ini_null_valid(S_default,pconfigcall_S_default)',
            '~$error_handler_eligible(S_default,8192)', *error('S_default', 'S_default', default=True),
            *front('S_true', 'S_default_error', True), 'n_object_S_true = n_object_S_default',
            '$compiled_read(S_true,porigin_option_S_true) = (PNULL)',
            '$lookup(S_true.ENV,' + text('getterKeep') + ') = (n_getter_keep)',
            'S_true.STORE[n_getter_keep] = DEFINED (POBJECT n_object_S_true)',
            '$lookup(S_true.ENV,' + text('value') + ') = (n_value)', 'S_true.STORE[n_value] = DEFINED (POBJECT n_object_S_true)',
            '~$config_strict(S_true,pconfigcall_S_true)', *returned('S_true', '9', 'true'),
            'S_true_return.STORE[n_getter_keep] = DEFINED (POBJECT n_object_S_true)',
            'S_true_return.STORE[n_value] = DEFINED (PINT 0)', *error('S_true', 'S_true_resume'),
            *refusals('S_true'), *budget('S_default'), *budget('S_true_resume'),
            *setter('S_true_error', '9'), *getter('S_get_final', 'S_recovered', 'n_object_S_true', '11'),
            'S_final = $drive_steps(S_get_final_after,3000)', 'S_final.COMPLETION = NORMAL',
            '$test_outputs(S_final.EVENTS) = ' + text('B|' + VALUE_ERROR + '|99|T|H|8192|' + MESSAGE + '|' + VALUE_ERROR + '|E|I|99|1|0|Z|R|9|11')]
    else:
        strict = name == 'strict-null-getter-option-rejection-after-value-effects'
        assert strict or name == 'captured-selected-null-getter-before-value-and-callee-rebinding'
        values += ['S_pre_found = $test_ini_std_partial_seek(S_initial,3000)',
            r'S_pre_found.COMPLETION = NORMAL \/ S_pre_found.COMPLETION = BUDGET',
            'S_pre = S_pre_found[.COMPLETION = NORMAL]', '$test_ini_std_partial(S_pre)',
            'S_pre.TODO = (CONFIG_ARGS pconfigcall_pre) :: ptask_pre*', 'pconfigcall_pre.SELECTION = (n_selection)',
            'pconfigcall_pre.PACKS = eps', '~pconfigcall_pre.NAMED', '$config_pending_valid(S_pre,pconfigcall_pre,false)',
            '$call_task_valid(S_pre,CONFIG_ARGS pconfigcall_pre)', '$config_nodes(pconfigcall_pre) = eps',
            '$lookup(S_pre.ENV,' + text('value') + ') = (n_value)', 'S_pre.STORE[n_value] = DEFINED (POBJECT n_captured)',
            'S_pre.OBJECTS[n_captured] = INTRINSICCLOSURE INTRINSIC_INI_GET',
            '$config_ini_rejected_getter_closure(S_pre,n_captured)',
            '$lookup(S_pre.ENV,' + text('getterKeep') + ') = (n_getter_keep)', 'S_pre.STORE[n_getter_keep] = DEFINED (POBJECT n_captured)',
            '$lookup(S_pre.ENV,' + text('call') + ') = (n_call)', 'S_pre.STORE[n_call] = DEFINED pvalue_original_call',
            '$string_bytes(pvalue_original_call) = (' + text('InI_SeT') + ')',
            '$lookup(S_pre.ENV,' + text('callKeep') + ') = (n_call_keep)', 'S_pre.STORE[n_call_keep] = DEFINED pvalue_original_call',
            '$lookup(S_pre.ENV,' + text('option') + ') = (n_option)', 'S_pre.STORE[n_option] = DEFINED PNULL',
            '$lookup(S_pre.ENV,' + text('effects') + ') = (n_effects)', 'S_pre.STORE[n_effects] = DEFINED (PINT 0)',
            '$lookup(S_pre.ENV,' + text('warnings') + ') = (n_warnings)', 'S_pre.STORE[n_warnings] = DEFINED (PINT 0)',
            '$lookup(S_pre.ENV,' + text('result') + ') = (n_result)', 'S_pre.STORE[n_result] = DEFINED (PINT 99)',
            'S_pre.SELECTEDCALLS[n_selection].OWNER = eps',
            'S_pre.SELECTEDCALLS[n_selection].KIND = INTRINSIC_INI_SET',
            'S_pre.SELECTEDCALLS[n_selection].SITE = pconfigcall_pre.SITE',
            'S_pre.SELECTEDCALLS[n_selection].LINE = pconfigcall_pre.LINE',
            'S_pre.PRECISIONINI = ' + text('14'), '$test_outputs(S_pre.EVENTS) = ' + text('B|'), *common.public('S_pre'),
            *front('S', 'S_pre', True), 'n_object_S = n_captured', 'n_selection_S = n_selection',
            'pconfigcall_S = pconfigcall_pre[.INDEX = 2][.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (POBJECT n_captured))]]',
            'S.SELECTEDCALLS[n_selection] = S_pre.SELECTEDCALLS[n_selection]',
            'S.STORE[n_getter_keep] = DEFINED (POBJECT n_captured)', 'S.STORE[n_value] = DEFINED (PINT 0)',
            'S.STORE[n_call] = DEFINED pvalue_live_call', '$string_bytes(pvalue_live_call) = (' + text('ini_get') + ')',
            'S.STORE[n_call_keep] = DEFINED pvalue_original_call',
            'S.STORE[n_option] = DEFINED pvalue_live_option', '$string_bytes(pvalue_live_option) = (' + text('precision') + ')',
            'S.STORE[n_result] = DEFINED (PINT 99)', 'S.STORE[n_effects] = DEFINED (PINT 1)', 'S.STORE[n_warnings] = DEFINED (PINT 0)',
            '$test_outputs(S.EVENTS) = ' + text('B|V|')]
        if strict:
            values += ['S.PRECISIONINI = ' + text('9'), '$exit_strict(S,pconfigcall_S.SITE)', '$config_strict(S,pconfigcall_S)',
                '~$config_ini_null_valid(S,pconfigcall_S)', *error('S', 'S', strict=True), *budget('S_pre'), *budget('S')]
        else:
            values += ['S.PRECISIONINI = ' + text('7'), '~$config_strict(S,pconfigcall_S)',
                *returned('S', '8', 'false'), 'S_return.STORE[n_getter_keep] = DEFINED (POBJECT n_captured)',
                'S_return.STORE[n_call] = DEFINED pvalue_handler_call', '$string_bytes(pvalue_handler_call) = (' + text('constant') + ')',
                'S_return.STORE[n_option] = DEFINED pvalue_handler_option', '$string_bytes(pvalue_handler_option) = (' + text('precision') + ')',
                'S_return.STORE[n_value] = DEFINED pvalue_handler_value', '$string_bytes(pvalue_handler_value) = (' + text('handler-value79') + ')',
                'S_return.STORE[n_result] = DEFINED (PINT 99)', 'S_return.STORE[n_effects] = DEFINED (PINT 1)',
                *error('S', 'S_resume'), *refusals('S'), *budget('S_pre'), *budget('S_resume')]
        old = '9' if strict else '8'
        values += [*getter('S_get_before', 'S_error', 'n_captured', old, strict),
            *setter('S_get_before_after', old, strict), *getter('S_get_final', 'S_recovered', 'n_captured', '11', strict),
            'S_final = $drive_steps(S_get_final_after,3000)', 'S_final.COMPLETION = NORMAL',
            '$test_outputs(S_final.EVENTS) = ' + text('B|V|' + (
                OPTION_ERROR + '|99|1|0|ini_get|precision|0|9|Z|G|9|R|9|11' if strict else
                'W|8192|' + MESSAGE + '|' + VALUE_ERROR + '|99|1|1|constant|precision|handler-value79|8|Z|G|8|R|8|11'))]
    return values + ['S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.ERRORHANDLER.CALLBACK = eps', 'S_final.USERCONSTANTS = eps', *common.public('S_final')]


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(path.relative_to(driver.ROOT)): sources.family.sha(path)
        for path in (Path(__file__), Path(base.__file__), Path(base.shared.__file__), Path(base.shared.shared.__file__),
            Path(shared.__file__), Path(shared.shared.__file__), Path(sources.__file__))})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
