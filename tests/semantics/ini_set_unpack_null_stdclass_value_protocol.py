#!/usr/bin/env python3
"""A saved object identity keeps live properties across unpack and NULL handling."""
import json
import os
from pathlib import Path

import ini_set_owned_null_stdclass_value_protocol as shared
import ini_set_unpack_null_stdclass_value_sources as sources

driver, common, text, b64 = shared.driver, shared.common, shared.text, shared.b64
MESSAGE, VALUE_ERROR, OPTION_ERROR = shared.MESSAGE, shared.VALUE_ERROR, shared.OPTION_ERROR
reach, returned, budget, mark, unchanged = shared.reach, shared.returned, shared.budget, shared.mark, shared.unchanged
PREFIX = shared.shared.shared.shared.PREFIX + r"""
dec $test_ini_std_pack_builder(pstate) : bool
def $test_ini_std_pack_builder(S) = true
  -- if S.TODO = (ARRAY_NEXT n_builder phpType13*) :: ptask_tail*
  -- if |phpType13*| = 1
  -- if S.ARRAYS[n_builder].ITEMS = [ENTRY (KSTRING ($ptascii("value"))) (DIRECT (POBJECT n_object))]
def $test_ini_std_pack_builder(S) = false -- otherwise
dec $test_ini_std_pack_builder_seek(pstate, nat) : pstate
def $test_ini_std_pack_builder_seek(S, 0) = S
def $test_ini_std_pack_builder_seek(S, n) = S
  -- if $(n > 0)
  -- if $test_ini_std_pack_builder(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_ini_std_pack_builder_seek(S, n) = $test_ini_std_pack_builder_seek($drive_steps($test_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_ini_std_pack_builder(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def front(state, start, mode, selected):
    call, obj, pack = 'pconfigcall_' + state, 'n_object_' + state, 'pconfigpack_' + state
    items = ('[ENTRY (KSTRING ' + text('value') + ') (DIRECT (POBJECT ' + obj + ')),ENTRY (KSTRING ' + text('option') + ') (DIRECT PNULL)]'
        if mode == 'reversed' else '[ENTRY (KINT i_option_' + state + ') (DIRECT PNULL),ENTRY (' +
        ('KSTRING ' + text('value') if mode == 'mixed' else 'KINT i_value_' + state) + ') (DIRECT (POBJECT ' + obj + '))]')
    values = [*reach(state, start, 0), state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
        call + '.KIND = INTRINSIC_INI_SET', call + '.OWNER = eps', call + '.INDEX = 1',
        call + '.PACKS = [' + pack + ']', ('' if mode != 'numeric' else '~') + call + '.NAMED',
        call + '.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (POBJECT ' + obj + '))]',
        pack + '.INDEX = 0', pack + '.ARRAY = n_outer_' + state, pack + '.ITEMS = ' + items,
        '$intrinsic_count(' + state + ',' + call + '.SITE) = (1)',
        '$intrinsic_argument(' + state + ',' + call + '.SITE,0) = ((expression_pack_' + state + ',true,eps,' + pack + '.SITE,' + pack + '.LINE))',
        '$compiled_read(' + state + ',' + pack + '.SITE) = eps',
        '$config_pack_source_valid(' + state + ',' + call + ',' + pack + ')',
        '$config_invoke_valid(' + state + ',' + call + ')', '$config_selected_valid(' + state + ',' + call + ')',
        '$config_ini_rejected_stdclass(' + state + ',' + obj + ')',
        state + '.OBJECTS[' + obj + '] = STDINSTANCE', '(HOBJECT ' + obj + ') <- ' + state + '.ALLOCATIONS',
        '$object_table_at(' + state + '.OBJECTTABLES,' + obj + ') = eps',
        '~$config_ini_quiet_value(' + state + ',POBJECT ' + obj + ')',
        '$node_children(' + state + ',HOBJECT ' + obj + ') = eps',
        '$config_nodes(' + call + ') = [HOBJECT ' + obj + ']',
        '$task_nodes(CONFIG_INI_NULL_RESULT ' + call + ') = [HOBJECT ' + obj + ']',
        '~$config_method_receiver(' + state + ',' + call + ')',
        state + '.CURRENT = eps', state + '.FRAMES = eps', *common.public(state)]
    if selected:
        values += [call + '.SELECTION = (n_selection_' + state + ')',
            state + '.SELECTEDCALLS[n_selection_' + state + '].KIND = INTRINSIC_INI_SET',
            state + '.SELECTEDCALLS[n_selection_' + state + '].SITE = ' + call + '.SITE',
            state + '.SELECTEDCALLS[n_selection_' + state + '].LINE = ' + call + '.LINE']
    else:
        values += [call + '.SELECTION = eps']
    return values


def error(state, start, strict=False, default=False):
    values = shared.error(state, start, strict=strict, default=default)
    excluded = state + '_error.OBJECTS[n_owner_' + state + '] = INTRINSICCLOSURE INTRINSIC_INI_SET'
    assert values.count(excluded) == 1
    return [v for v in values if v != excluded]


def refusals(state, named):
    call, pack = 'pconfigcall_' + state, 'pconfigpack_' + state
    values = shared.shared.shared.refusals(state)
    for old, new in [('.INDEX = 1', '.INDEX = 2'), ('.NAMED = true', '.NAMED = ' + str(not named).lower())]:
        needle = '~$config_ini_null_valid(' + state + ',' + call + '[' + old + '])'
        assert values.count(needle) == 1
        values[values.index(needle)] = needle.replace(old, new)
    for field in ('.PACKS = eps', '.PACKS = [' + pack + ',' + pack + ']',
            '.PACKS = [' + pack + '[.INDEX = 1]]', '.PACKS = [' + pack + '[.LINE = $(' + pack + '.LINE + 1)]]',
            '.SELECTION = eps'):
        values += ['~$config_ini_null_valid(' + state + ',' + call + '[' + field + '])']
    return values


def recovery(start, old_precision, strict=False):
    return [*reach('S_recovery', start, 3),
        'S_recovery.TODO = (CONFIG_INVOKE pconfigcall_recovery) :: ptask_recovery*',
        'pconfigcall_recovery.OWNER = eps', 'pconfigcall_recovery.SELECTION = (n_selection_recovery)',
        'S_recovery.SELECTEDCALLS[n_selection_recovery].KIND = INTRINSIC_INI_SET',
        'S_recovery.SELECTEDCALLS[n_selection_recovery].SITE = pconfigcall_recovery.SITE',
        'S_recovery.SELECTEDCALLS[n_selection_recovery].LINE = pconfigcall_recovery.LINE',
        'pconfigcall_recovery.INDEX = 2', '~pconfigcall_recovery.NAMED', 'pconfigcall_recovery.PACKS = eps',
        'pconfigcall_recovery.SENT = [NAMED_SENT (KNOWN pvalue_precision),NAMED_SENT (KNOWN pvalue_new_precision)]',
        '$string_bytes(pvalue_precision) = (' + text('precision') + ')',
        '$string_bytes(pvalue_new_precision) = (' + text('11') + ')',
        '$config_invoke_valid(S_recovery,pconfigcall_recovery)', '$config_selected_valid(S_recovery,pconfigcall_recovery)',
        '$dynamic_scalar_define_arguments(S_recovery,pconfigcall_recovery,0)',
        ('~' if not strict else '') + '$config_strict(S_recovery,pconfigcall_recovery)',
        '~$config_ini_null_valid(S_recovery,pconfigcall_recovery)', '$config_nodes(pconfigcall_recovery) = eps',
        '$lookup(S_recovery.ENV,' + text('keep') + ') = (n_keep_recovery)',
        'S_recovery.STORE[n_keep_recovery] = DEFINED pvalue_keep_recovery',
        '$string_bytes(pvalue_keep_recovery) = (' + text('InI_SeT') + ')',
        'S_recovery.PRECISIONINI = ' + text(old_precision), 'S_recovery.ERRORHANDLER.CALLBACK = eps',
        *common.public('S_recovery'), *common.step('S_recovered', 'S_recovery'),
        'S_recovered.TODO = ptask_recovery*', 'S_recovered.RESULT = KNOWN pvalue_old_precision',
        '$string_bytes(pvalue_old_precision) = (' + text(old_precision) + ')', 'S_recovered.PRECISIONINI = ' + text('11'),
        *unchanged('S_recovered', 'S_recovery', 'STORE ENV OBJECTS USERCONSTANTS SELECTEDCALLS EVENTS'),
        *common.public('S_recovered')]


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET']
    if name == 'unpacked-stdclass-values-default-and-selected-mixed-shared-return':
        values += [*front('S_empty', 'S_initial', 'numeric', False), 'i_option_S_empty = 3', 'i_value_S_empty = 7',
            '$objectprops_at(S_empty.OBJECTPROPS,n_object_S_empty) = (eps)',
            '~$config_strict(S_empty,pconfigcall_S_empty)', '$config_ini_null_valid(S_empty,pconfigcall_S_empty)',
            '~$error_handler_eligible(S_empty,8192)', *error('S_empty', 'S_empty', default=True),
            *front('S_true', 'S_empty_error', 'mixed', True), 'i_option_S_true = 3',
            'n_object_S_true =/= n_object_S_empty',
            *mark('S_true', 'n_object_S_true', '(PSTRING_CARRIER INTERNED_STRING ' + text('initial77') + ')'),
            '$lookup(S_true.ENV,' + text('objectKeep') + ') = (n_object_keep)',
            'S_true.STORE[n_object_keep] = DEFINED (POBJECT n_object_S_true)',
            '$lookup(S_true.ENV,' + text('value') + ') = (n_value)', 'S_true.STORE[n_value] = DEFINED (POBJECT n_object_S_true)',
            '~$config_strict(S_true,pconfigcall_S_true)', *returned('S_true', '14', 'true', 'true77'),
            'S_true_return.STORE[n_object_keep] = DEFINED (POBJECT n_object_S_true)',
            'S_true_return.STORE[n_value] = DEFINED (PINT 0)', *error('S_true', 'S_true_resume'),
            *refusals('S_true', True), *budget('S_empty'), *budget('S_true_resume'),
            *recovery('S_true_error', '14'), 'S_final = $drive_steps(S_recovered,3000)', 'S_final.COMPLETION = NORMAL',
            '$test_outputs(S_final.EVENTS) = ' + text('B|' + VALUE_ERROR + '|99|M|H|8192|' + MESSAGE + '|' + VALUE_ERROR + '|E|I|true77|99|1|Z|R|14|11')]
    elif name == 'captured-string-unpack-stdclass-before-shared-option-and-live-value-effects':
        values += ['S_pre_found = $test_ini_std_pack_builder_seek(S_initial,3000)',
            r'S_pre_found.COMPLETION = NORMAL \/ S_pre_found.COMPLETION = BUDGET',
            'S_pre = S_pre_found[.COMPLETION = NORMAL]', '$test_ini_std_pack_builder(S_pre)',
            'S_pre.TODO = (ARRAY_NEXT n_builder phpType13*) :: ptask_pre*',
            'S_pre.ARRAYS[n_builder].ITEMS = [ENTRY (KSTRING ' + text('value') + ') (DIRECT (POBJECT n_captured))]',
            '(HARRAY n_builder) <- S_pre.ALLOCATIONS', '$node_children(S_pre,HARRAY n_builder) = [HOBJECT n_captured]',
            '(HARRAY n_builder) <- $tasks_nodes(S_pre.TODO)', 'S_pre.OBJECTS[n_captured] = STDINSTANCE',
            '$config_ini_rejected_stdclass(S_pre,n_captured)',
            *mark('S_pre', 'n_captured', 'pvalue_captured'),
            'pvalue_captured = PSTRING_CARRIER (REQUEST_STRING n_candidate) ' + text('captured-pack-object77'),
            '$string_carrier_valid(S_pre,pvalue_captured)',
            '$lookup(S_pre.ENV,' + text('call') + ') = (n_call)', 'S_pre.STORE[n_call] = DEFINED pvalue_original_call',
            '$string_bytes(pvalue_original_call) = (' + text('InI_SeT') + ')',
            '$lookup(S_pre.ENV,' + text('keep') + ') = (n_keep)', 'S_pre.STORE[n_keep] = DEFINED pvalue_original_call',
            '$lookup(S_pre.ENV,' + text('value') + ') = (n_value)', 'S_pre.STORE[n_value] = DEFINED (POBJECT n_captured)',
            '$lookup(S_pre.ENV,' + text('objectKeep') + ') = (n_object_keep)', 'S_pre.STORE[n_object_keep] = DEFINED (POBJECT n_captured)',
            '$lookup(S_pre.ENV,' + text('effects') + ') = (n_effects)', 'S_pre.STORE[n_effects] = DEFINED (PINT 0)',
            '$lookup(S_pre.ENV,' + text('warnings') + ') = (n_warnings)', 'S_pre.STORE[n_warnings] = DEFINED (PINT 0)',
            '$lookup(S_pre.ENV,' + text('result') + ') = (n_result)', 'S_pre.STORE[n_result] = DEFINED (PINT 99)',
            'S_pre.PRECISIONINI = ' + text('14'), '$test_outputs(S_pre.EVENTS) = ' + text('B|'), *common.public('S_pre'),
            *front('S', 'S_pre', 'reversed', True), 'n_object_S = n_captured', 'n_outer_S = n_builder',
            'S_pre.SELECTEDCALLS[n_selection_S].KIND = INTRINSIC_INI_SET',
            'S_pre.SELECTEDCALLS[n_selection_S].SITE = pconfigcall_S.SITE',
            'S_pre.SELECTEDCALLS[n_selection_S].LINE = pconfigcall_S.LINE',
            'S.SELECTEDCALLS[n_selection_S] = S_pre.SELECTEDCALLS[n_selection_S]',
            '~((HARRAY n_builder) <- S.ALLOCATIONS)', '$heap_count(HARRAY n_builder,$tasks_nodes(S.TODO)) = 0',
            '$heap_count(HOBJECT n_captured,$tasks_nodes(S.TODO)) = 1',
            'S.STORE[n_keep] = DEFINED pvalue_original_call', 'S.STORE[n_call] = DEFINED pvalue_live_call',
            '$string_bytes(pvalue_live_call) = (' + text('ini_get') + ')',
            'S.STORE[n_value] = DEFINED (PINT 0)', 'S.STORE[n_object_keep] = DEFINED (POBJECT n_captured)',
            *mark('S', 'n_captured', '(PSTRING_CARRIER INTERNED_STRING ' + text('option77') + ')'),
            'S.STORE[n_result] = DEFINED (PINT 99)', 'S.STORE[n_effects] = DEFINED (PINT 1)',
            'S.STORE[n_warnings] = DEFINED (PINT 0)', '~$config_strict(S,pconfigcall_S)',
            'S.PRECISIONINI = ' + text('7'), '$test_outputs(S.EVENTS) = ' + text('B|O|'),
            *returned('S', '8', 'false', 'handler77'), 'S_return.STORE[n_object_keep] = DEFINED (POBJECT n_captured)',
            'S_return.STORE[n_keep] = DEFINED pvalue_original_call', 'S_return.STORE[n_result] = DEFINED (PINT 99)',
            'S_return.STORE[n_effects] = DEFINED (PINT 1)',
            'S_return.STORE[n_call] = DEFINED pvalue_handler_call', '$string_bytes(pvalue_handler_call) = (' + text('constant') + ')',
            'S_return.STORE[n_value] = DEFINED pvalue_handler_value', '$string_bytes(pvalue_handler_value) = (' + text('handler-value77') + ')',
            '$heap_count(HOBJECT n_captured,$tasks_nodes(S_return.TODO)) = 1', *error('S', 'S_resume'),
            *refusals('S', True), *budget('S_pre'), *budget('S_resume'),
            *recovery('S_error', '8'), 'S_final = $drive_steps(S_recovered,3000)', 'S_final.COMPLETION = NORMAL',
            '$test_outputs(S_final.EVENTS) = ' + text('B|O|W|8192|' + MESSAGE + '|' + VALUE_ERROR + '|99|1|1|constant|handler-value77|handler77|8|Z|R|8|11')]
    else:
        assert name == 'strict-string-unpack-stdclass-option-after-shared-mark-and-pack-effects'
        values += [*front('S', 'S_initial', 'numeric', True), 'i_option_S = 5', 'i_value_S = 9',
            *mark('S', 'n_object_S', '(PSTRING_CARRIER INTERNED_STRING ' + text('strict77') + ')'),
            '$lookup(S.ENV,' + text('objectKeep') + ') = (n_object_keep)',
            'S.STORE[n_object_keep] = DEFINED (POBJECT n_object_S)',
            '$lookup(S.ENV,' + text('call') + ') = (n_call)', 'S.STORE[n_call] = DEFINED pvalue_live_call',
            '$string_bytes(pvalue_live_call) = (' + text('ini_get') + ')',
            '$lookup(S.ENV,' + text('value') + ') = (n_value)', 'S.STORE[n_value] = DEFINED (PINT 0)',
            '$lookup(S.ENV,' + text('pack') + ') = (n_pack_cell)', 'S.STORE[n_pack_cell] = DEFINED (PARRAY n_live_outer)',
            'n_live_outer =/= n_outer_S',
            'S.ARRAYS[n_live_outer].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 0)),ENTRY (KINT 1) (DIRECT (PINT 0))]',
            '$lookup(S.ENV,' + text('effects') + ') = (n_effects)', 'S.STORE[n_effects] = DEFINED (PINT 1)',
            '$lookup(S.ENV,' + text('warnings') + ') = (n_warnings)', 'S.STORE[n_warnings] = DEFINED (PINT 0)',
            '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            'S.PRECISIONINI = ' + text('9'), '$test_outputs(S.EVENTS) = ' + text('B|P|'),
            '$exit_strict(S,pconfigcall_S.SITE)', '$config_strict(S,pconfigcall_S)',
            '~$config_ini_null_valid(S,pconfigcall_S)', *error('S', 'S', strict=True), *budget('S'),
            *recovery('S_error', '9', strict=True), 'S_final = $drive_steps(S_recovered,3000)', 'S_final.COMPLETION = NORMAL',
            '$test_outputs(S_final.EVENTS) = ' + text('B|P|' + OPTION_ERROR + '|99|1|0|strict77|0|0|9|Z|R|9|11')]
    return values + ['S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.ERRORHANDLER.CALLBACK = eps', 'S_final.USERCONSTANTS = eps', *common.public('S_final')]


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(path.relative_to(driver.ROOT)): sources.family.sha(path)
        for path in (Path(__file__), Path(shared.__file__), Path(shared.shared.__file__),
            Path(shared.shared.shared.__file__), Path(shared.shared.shared.shared.__file__), Path(sources.__file__))})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
