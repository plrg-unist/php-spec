#!/usr/bin/env python3
"""Ownerless selection and unpacking preserve the original owning INI value."""
import json
import os
from pathlib import Path

import ini_set_owned_unpack_null_array_value_protocol as shared
import ini_set_unpack_null_array_value_sources as sources

driver, common, text, b64 = shared.driver, shared.common, shared.text, shared.b64
MESSAGE, VALUE_ERROR, OPTION_ERROR = shared.MESSAGE, shared.VALUE_ERROR, shared.OPTION_ERROR
PREFIX = shared.PREFIX
reach, returned, budget, literal = shared.reach, shared.returned, shared.budget, shared.literal
unchanged = shared.unchanged


def front(state, start, mode, selected):
    call, owner = 'pconfigcall_' + state, 'n_owner_' + state
    values = shared.front(state, start, mode)
    excluded = {state + '.OBJECTS[' + owner + '] = INTRINSICCLOSURE INTRINSIC_INI_SET',
        '(HOBJECT ' + owner + ') <- ' + state + '.ALLOCATIONS', call + '.SELECTION = eps'}
    assert excluded <= set(values)
    values = [v.replace(call + '.OWNER = (' + owner + ')', call + '.OWNER = eps').replace(
        '[HOBJECT ' + owner + ',HARRAY ', '[HARRAY ') for v in values if v not in excluded]
    values += ['~$config_method_receiver(' + state + ',' + call + ')']
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
    excluded = {state + '_error.OBJECTS[n_owner_' + state + '] = INTRINSICCLOSURE INTRINSIC_INI_SET',
        '(HOBJECT n_owner_' + state + ') <- ' + state + '_error.ALLOCATIONS'}
    assert excluded <= set(values)
    return [v for v in values if v not in excluded]


def refusals(state, named):
    values = shared.refusals(state, named)
    excluded = {'~$config_ini_null_valid(' + state + ',pconfigcall_' + state + '[.OWNER = eps])',
        '~$config_ini_null_valid(' + state + '[.OBJECTS[n_owner_' + state + '] = INTRINSICCLOSURE INTRINSIC_INI_GET],pconfigcall_' + state + ')'}
    assert excluded <= set(values)
    return [v for v in values if v not in excluded]


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
        '~$config_ini_null_valid(S_recovery,pconfigcall_recovery)',
        '$config_nodes(pconfigcall_recovery) = eps',
        '$lookup(S_recovery.ENV,' + text('keep') + ') = (n_keep_recovery)',
        'S_recovery.STORE[n_keep_recovery] = DEFINED pvalue_keep_recovery',
        '$string_bytes(pvalue_keep_recovery) = (' + text('InI_SeT') + ')',
        'S_recovery.PRECISIONINI = ' + text(old_precision), 'S_recovery.ERRORHANDLER.CALLBACK = eps',
        *common.public('S_recovery'), *common.step('S_recovered', 'S_recovery'),
        'S_recovered.TODO = ptask_recovery*', 'S_recovered.RESULT = KNOWN pvalue_old_precision',
        '$string_bytes(pvalue_old_precision) = (' + text(old_precision) + ')',
        'S_recovered.PRECISIONINI = ' + text('11'),
        *unchanged('S_recovered', 'S_recovery', 'STORE ENV OBJECTS USERCONSTANTS SELECTEDCALLS EVENTS'),
        *common.public('S_recovered')]


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET']
    if name == 'unpacked-array-values-direct-default-and-selected-mixed-return':
        values += [*front('S_default', 'S_initial', 'numeric', False), 'i_option_S_default = 3', 'i_value_S_default = 7',
            'S_default.ARRAYS[n_array_S_default].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 2833))]',
            *literal('S_default', 'KINT 7'), '~$config_strict(S_default,pconfigcall_S_default)',
            '$config_ini_null_valid(S_default,pconfigcall_S_default)', '~$error_handler_eligible(S_default,8192)',
            *error('S_default', 'S_default', default=True), *front('S_true', 'S_default_error', 'mixed', True),
            'i_option_S_true = 3', 'S_true.ARRAYS[n_array_S_true].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 2843))]',
            *literal('S_true', 'KSTRING ' + text('value')), '~$config_strict(S_true,pconfigcall_S_true)',
            *returned('S_true', 1, '14', 'true'), *error('S_true', 'S_true_resume'),
            'S_forged = $allocate_array(S_true,$array_insert($array_empty(),KINT 0,DIRECT (PINT 2844)))',
            'S_forged.RESULT = KNOWN (PARRAY n_forged)',
            'pconfigpack_forged = pconfigpack_S_true[.ITEMS = [ENTRY (KINT 3) (DIRECT PNULL),ENTRY (KSTRING ' + text('value') + ') (DIRECT (PARRAY n_forged))]]',
            'pconfigcall_forged = pconfigcall_S_true[.PACKS = [pconfigpack_forged]][.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (PARRAY n_forged))]]',
            '$config_invoke_valid(S_forged,pconfigcall_forged)', '$config_ini_rejected_array(S_forged,n_forged)',
            '~$dynamic_array_same(S_forged,PARRAY n_forged,PARRAY n_known_inner_S_true)',
            '~$config_ini_pack_known(S_forged,pconfigpack_forged.ITEMS,$compiled_read(S_forged,pconfigpack_forged.SITE))',
            '~$config_ini_null_valid(S_forged,pconfigcall_forged)',
            *refusals('S_true', True), *budget('S_default'), *budget('S_true_resume'),
            *recovery('S_true_error', '14'), 'S_final = $drive_steps(S_recovered,3000)', 'S_final.COMPLETION = NORMAL',
            '$test_outputs(S_final.EVENTS) = ' + text('B|' + VALUE_ERROR + '|99|M|H|8192|' + MESSAGE + '|' + VALUE_ERROR + '|E|2843|99|1|Z|R|14|11')]
    elif name == 'captured-string-unpack-array-before-option-cow-and-live-callee-rebinding':
        values += ['S_pre_found = $test_ini_owned_array_pack_builder_seek(S_initial,3000)',
            r'S_pre_found.COMPLETION = NORMAL \/ S_pre_found.COMPLETION = BUDGET',
            'S_pre = S_pre_found[.COMPLETION = NORMAL]', '$test_ini_owned_array_pack_builder(S_pre)',
            'S_pre.TODO = (ARRAY_NEXT n_builder phpType13*) :: ptask_pre*',
            'S_pre.ARRAYS[n_builder].ITEMS = [ENTRY (KSTRING ' + text('value') + ') (DIRECT (PARRAY n_captured))]',
            '(HARRAY n_builder) <- S_pre.ALLOCATIONS', '$node_children(S_pre,HARRAY n_builder) = [HARRAY n_captured]',
            '(HARRAY n_builder) <- $tasks_nodes(S_pre.TODO)',
            '$lookup(S_pre.ENV,' + text('call') + ') = (n_call)', 'S_pre.STORE[n_call] = DEFINED pvalue_original_call',
            '$string_bytes(pvalue_original_call) = (' + text('InI_SeT') + ')',
            '$lookup(S_pre.ENV,' + text('keep') + ') = (n_keep)', 'S_pre.STORE[n_keep] = DEFINED pvalue_original_call',
            '$lookup(S_pre.ENV,' + text('value') + ') = (n_value)', 'S_pre.STORE[n_value] = DEFINED (PARRAY n_captured)',
            '$lookup(S_pre.ENV,' + text('arrayKeep') + ') = (n_array_keep)', 'S_pre.STORE[n_array_keep] = DEFINED (PARRAY n_captured)',
            'S_pre.ARRAYS[n_captured].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_captured)]',
            'pvalue_captured = PSTRING_CARRIER (REQUEST_STRING n_candidate) ' + text('captured-unpack-array76'),
            '$string_carrier_valid(S_pre,pvalue_captured)',
            '$lookup(S_pre.ENV,' + text('effects') + ') = (n_effects)', 'S_pre.STORE[n_effects] = DEFINED (PINT 0)',
            '$lookup(S_pre.ENV,' + text('warnings') + ') = (n_warnings)', 'S_pre.STORE[n_warnings] = DEFINED (PINT 0)',
            '$lookup(S_pre.ENV,' + text('result') + ') = (n_result)', 'S_pre.STORE[n_result] = DEFINED (PINT 99)',
            'S_pre.PRECISIONINI = ' + text('14'), '$test_outputs(S_pre.EVENTS) = ' + text('B|'), *common.public('S_pre'),
            *front('S', 'S_pre', 'reversed', True), 'n_array_S = n_captured', 'n_outer_S = n_builder',
            'S_pre.SELECTEDCALLS[n_selection_S].KIND = INTRINSIC_INI_SET',
            'S_pre.SELECTEDCALLS[n_selection_S].SITE = pconfigcall_S.SITE',
            'S_pre.SELECTEDCALLS[n_selection_S].LINE = pconfigcall_S.LINE',
            'S.SELECTEDCALLS[n_selection_S] = S_pre.SELECTEDCALLS[n_selection_S]',
            '~((HARRAY n_builder) <- S.ALLOCATIONS)', '$compiled_read(S,pconfigpack_S.SITE) = eps',
            'S.ARRAYS[n_captured].ITEMS = S_pre.ARRAYS[n_captured].ITEMS',
            '$heap_count(HARRAY n_builder,$tasks_nodes(S.TODO)) = 0',
            '$heap_count(HARRAY n_captured,$tasks_nodes(S.TODO)) = 1',
            'S.STORE[n_keep] = DEFINED pvalue_original_call', 'S.STORE[n_call] = DEFINED pvalue_live_call',
            '$string_bytes(pvalue_live_call) = (' + text('ini_get') + ')',
            'S.STORE[n_value] = DEFINED (PINT 0)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            'S.STORE[n_effects] = DEFINED (PINT 1)', 'S.STORE[n_warnings] = DEFINED (PINT 0)',
            'S.STORE[n_array_keep] = DEFINED (PARRAY n_option_array)', 'n_option_array =/= n_captured',
            'S.ARRAYS[n_option_array].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_option)]',
            '$string_bytes(pvalue_option) = (' + text('option-array76') + ')',
            '~$config_strict(S,pconfigcall_S)', 'S.PRECISIONINI = ' + text('7'),
            '$test_outputs(S.EVENTS) = ' + text('B|O|'), *returned('S', 1, '8', 'false'),
            'S_return.STORE[n_result] = DEFINED (PINT 99)', 'S_return.STORE[n_effects] = DEFINED (PINT 1)',
            'S_return.STORE[n_keep] = DEFINED pvalue_original_call',
            'S_return.STORE[n_array_keep] = DEFINED (PARRAY n_handler_array)', 'n_handler_array =/= n_captured',
            'S_return.ARRAYS[n_handler_array].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_handler_array)]',
            '$string_bytes(pvalue_handler_array) = (' + text('handler-array76') + ')',
            'S_return.STORE[n_call] = DEFINED pvalue_handler_call', '$string_bytes(pvalue_handler_call) = (' + text('constant') + ')',
            'S_return.STORE[n_value] = DEFINED pvalue_handler_value', '$string_bytes(pvalue_handler_value) = (' + text('handler-value76') + ')',
            '$heap_count(HARRAY n_captured,$tasks_nodes(S_return.TODO)) = 1',
            *error('S', 'S_resume'), '$string_carrier_valid(S_error,pvalue_captured)',
            *refusals('S', True), *budget('S_pre'), *budget('S_resume'),
            *recovery('S_error', '8'), 'S_final = $drive_steps(S_recovered,3000)', 'S_final.COMPLETION = NORMAL',
            '$test_outputs(S_final.EVENTS) = ' + text('B|O|W|8192|' + MESSAGE + '|' + VALUE_ERROR + '|99|1|1|constant|handler-value76|handler-array76|8|Z|R|8|11')]
    else:
        assert name == 'strict-string-unpack-array-option-after-pack-and-live-value-effects'
        values += [*front('S', 'S_initial', 'numeric', True), 'i_option_S = 5', 'i_value_S = 9',
            'S.ARRAYS[n_array_S].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 2857))]',
            '$compiled_read(S,pconfigpack_S.SITE) = eps',
            '$lookup(S.ENV,' + text('call') + ') = (n_call)', 'S.STORE[n_call] = DEFINED pvalue_live_call',
            '$string_bytes(pvalue_live_call) = (' + text('ini_get') + ')',
            '$lookup(S.ENV,' + text('keep') + ') = (n_keep)', 'S.STORE[n_keep] = DEFINED pvalue_original_call',
            '$string_bytes(pvalue_original_call) = (' + text('InI_SeT') + ')',
            '$lookup(S.ENV,' + text('value') + ') = (n_value)', 'S.STORE[n_value] = DEFINED (PINT 0)',
            '$lookup(S.ENV,' + text('arrayKeep') + ') = (n_array_keep)',
            'S.STORE[n_array_keep] = DEFINED (PARRAY n_live_inner)', 'n_live_inner =/= n_array_S',
            'S.ARRAYS[n_live_inner].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 0))]',
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
            '$test_outputs(S_final.EVENTS) = ' + text('B|P|' + OPTION_ERROR + '|99|1|0|0|0|0|9|Z|R|9|11')]
    return values + ['S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.ERRORHANDLER.CALLBACK = eps', 'S_final.USERCONSTANTS = eps', *common.public('S_final')]


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(path.relative_to(driver.ROOT)): sources.family.sha(path)
        for path in (Path(__file__), Path(shared.__file__), Path(shared.shared.__file__),
            Path(shared.shared.shared.__file__), Path(shared.shared.shared.shared.__file__),
            Path(shared.base.__file__), Path(sources.__file__))})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
