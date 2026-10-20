#!/usr/bin/env python3
"""Unpacking retires the outer pack while retaining the captured array value."""
import json
import os
from pathlib import Path

import ini_set_owned_named_null_array_value_protocol as shared
import ini_set_null_option_protocol as base
import ini_set_owned_unpack_null_array_value_sources as sources

driver, common, text, b64 = shared.driver, shared.common, shared.text, shared.b64
MESSAGE, VALUE_ERROR, OPTION_ERROR = shared.MESSAGE, shared.VALUE_ERROR, shared.OPTION_ERROR
reach, budget, unchanged, returned = base.reach, base.budget, base.unchanged, shared.returned
PREFIX = base.PREFIX + r"""
dec $test_ini_owned_array_pack_builder(pstate) : bool
def $test_ini_owned_array_pack_builder(S) = true
  -- if S.TODO = (ARRAY_NEXT n_builder phpType13*) :: ptask_tail*
  -- if |phpType13*| = 1
  -- if S.ARRAYS[n_builder].ITEMS = [ENTRY (KSTRING ($ptascii("value"))) (DIRECT (PARRAY n_inner))]
def $test_ini_owned_array_pack_builder(S) = false -- otherwise
dec $test_ini_owned_array_pack_builder_seek(pstate, nat) : pstate
def $test_ini_owned_array_pack_builder_seek(S, 0) = S
def $test_ini_owned_array_pack_builder_seek(S, n) = S
  -- if $(n > 0)
  -- if $test_ini_owned_array_pack_builder(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_ini_owned_array_pack_builder_seek(S, n) = $test_ini_owned_array_pack_builder_seek($drive_steps($test_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_ini_owned_array_pack_builder(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def front(state, start, mode):
    call, owner, array, pack = ['pconfigcall_' + state, 'n_owner_' + state, 'n_array_' + state, 'pconfigpack_' + state]
    items = ('[ENTRY (KSTRING ' + text('value') + ') (DIRECT (PARRAY ' + array + ')),ENTRY (KSTRING ' + text('option') + ') (DIRECT PNULL)]'
        if mode == 'reversed' else '[ENTRY (KINT i_option_' + state + ') (DIRECT PNULL),ENTRY (' +
        ('KSTRING ' + text('value') if mode == 'mixed' else 'KINT i_value_' + state) + ') (DIRECT (PARRAY ' + array + '))]')
    return [*reach(state, start, 0), state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
        call + '.KIND = INTRINSIC_INI_SET', call + '.OWNER = (' + owner + ')', call + '.SELECTION = eps',
        call + '.INDEX = 1', call + '.PACKS = [' + pack + ']',
        ('' if mode != 'numeric' else '~') + call + '.NAMED',
        call + '.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (PARRAY ' + array + '))]',
        pack + '.INDEX = 0', pack + '.ARRAY = n_outer_' + state, pack + '.ITEMS = ' + items,
        '$intrinsic_count(' + state + ',' + call + '.SITE) = (1)',
        '$intrinsic_argument(' + state + ',' + call + '.SITE,0) = ((expression_pack_' + state + ',true,eps,' + pack + '.SITE,' + pack + '.LINE))',
        '$config_pack_source_valid(' + state + ',' + call + ',' + pack + ')',
        '$config_invoke_valid(' + state + ',' + call + ')', '$config_selected_valid(' + state + ',' + call + ')',
        '$config_ini_pack_known(' + state + ',' + pack + '.ITEMS,$compiled_read(' + state + ',' + pack + '.SITE))',
        state + '.OBJECTS[' + owner + '] = INTRINSICCLOSURE INTRINSIC_INI_SET',
        '(HOBJECT ' + owner + ') <- ' + state + '.ALLOCATIONS',
        '$config_ini_rejected_array(' + state + ',' + array + ')', '(HARRAY ' + array + ') <- ' + state + '.ALLOCATIONS',
        '~$config_ini_quiet_value(' + state + ',PARRAY ' + array + ')',
        '$config_nodes(' + call + ') = [HOBJECT ' + owner + ',HARRAY ' + array + ']',
        '$task_nodes(CONFIG_INI_NULL_RESULT ' + call + ') = [HOBJECT ' + owner + ',HARRAY ' + array + ']',
        '$node_children(' + state + ',HARRAY ' + array + ') = eps',
        state + '.CURRENT = eps', state + '.FRAMES = eps', *common.public(state)]


def literal(state, key):
    pack, array = 'pconfigpack_' + state, 'n_array_' + state
    return ['$compiled_read(' + state + ',' + pack + '.SITE) = (PARRAY n_known_pack_' + state + ')',
        '$($heap_count(HARRAY n_known_pack_' + state + ',$pools_nodes(' + state + '.POOLS)) > 0)',
        '$entry_lookup(' + state + '.ARRAYS[n_known_pack_' + state + '].ITEMS,' + key + ') = (DIRECT (PARRAY n_known_inner_' + state + '))',
        '$dynamic_array_same(' + state + ',PARRAY ' + array + ',PARRAY n_known_inner_' + state + ')',
        '$array_immutable(' + state + ',' + array + ') = $array_immutable(' + state + ',n_known_inner_' + state + ')',
        '$dynamic_array_same_entries(' + state + ',' + pack + '.ITEMS,' + state + '.ARRAYS[n_known_pack_' + state + '].ITEMS)']


def error(state, start, explicit=False, strict=False, default=False):
    values = shared.error(state, start, explicit, strict)
    if default:
        expected = state + '_error.EVENTS = ' + start + '.EVENTS'
        assert values.count(expected) == 1
        values[values.index(expected)] += ' ++ [DIAGNOSTIC "Deprecated" $config_ini_null_message(pconfigcall_' + state + ') pconfigcall_' + state + '.LINE]'
    return values


def recovery(start, owner, old_precision):
    values = shared.recovery(start, owner, old_precision)
    expected = 'pconfigcall_recovery.NAMED'
    assert values.count(expected) == 1
    values[values.index(expected)] = '~' + expected
    return values


def refusals(state, named):
    call, pack, owner = 'pconfigcall_' + state, 'pconfigpack_' + state, 'n_owner_' + state
    values = []
    for field in ('.SITE = PORIGIN 0 eps', '.LINE = $(' + call + '.LINE + 1)', '.INDEX = 2',
            '.OWNER = eps', '.OWNER = (|' + state + '.OBJECTS|)', '.SELECTION = (|' + state + '.SELECTEDCALLS|)',
            '.NAMED = ' + str(not named).lower(), '.KIND = INTRINSIC_INI_GET', '.PACKS = eps',
            '.PACKS = [' + pack + ',' + pack + ']', '.SENT = ' + call + '.SENT[0:1]',
            '.SENT = ' + call + '.SENT ++ [NAMED_SENT (KNOWN PNULL)]'):
        values += ['~$config_ini_null_valid(' + state + ',' + call + '[' + field + '])']
    for field in ('.INDEX = 1', '.LINE = $(' + pack + '.LINE + 1)', '.ARRAY = |' + state + '.ARRAYS|'):
        values += ['~$config_ini_null_valid(' + state + ',' + call + '[.PACKS = [' + pack + '[' + field + ']]])']
    return values + ['~$config_ini_null_valid(' + state + '[.CODE = eps],' + call + ')',
        '~$config_ini_null_valid(' + state + '[.ALLOCATIONS = eps],' + call + ')',
        '~$config_ini_null_valid(' + state + '[.OBJECTS[' + owner + '] = INTRINSICCLOSURE INTRINSIC_INI_GET],' + call + ')']


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET']
    if name == 'owned-unpack-array-values-default-and-explicit-return-normalize-inner-value':
        values += [*front('S_default', 'S_initial', 'numeric'), 'i_option_S_default = 3', 'i_value_S_default = 7',
            'S_default.ARRAYS[n_array_S_default].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 2777))]',
            *literal('S_default', 'KINT 7'), '~$config_method_receiver(S_default,pconfigcall_S_default)',
            '~$config_strict(S_default,pconfigcall_S_default)', '$config_ini_null_valid(S_default,pconfigcall_S_default)',
            '~$error_handler_eligible(S_default,8192)', *error('S_default', 'S_default', default=True),
            *front('S_true', 'S_default_error', 'reversed'), 'n_owner_S_true = n_owner_S_default',
            'S_true.ARRAYS[n_array_S_true].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 2783))]',
            *literal('S_true', 'KSTRING ' + text('value')), '$config_method_receiver(S_true,pconfigcall_S_true)',
            '~$config_strict(S_true,pconfigcall_S_true)', *returned('S_true', 1, '14', 'true'),
            *error('S_true', 'S_true_resume', explicit=True),
            'S_forged = $allocate_array(S_true,$array_insert($array_empty(),KINT 0,DIRECT (PINT 2784)))',
            'S_forged.RESULT = KNOWN (PARRAY n_forged)',
            'pconfigpack_forged = pconfigpack_S_true[.ITEMS = [ENTRY (KSTRING ' + text('value') + ') (DIRECT (PARRAY n_forged)),ENTRY (KSTRING ' + text('option') + ') (DIRECT PNULL)]]',
            'pconfigcall_forged = pconfigcall_S_true[.PACKS = [pconfigpack_forged]][.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (PARRAY n_forged))]]',
            '$config_invoke_valid(S_forged,pconfigcall_forged)', '$config_ini_rejected_array(S_forged,n_forged)',
            '~$dynamic_array_same(S_forged,PARRAY n_forged,PARRAY n_known_inner_S_true)',
            '~$config_ini_pack_known(S_forged,pconfigpack_forged.ITEMS,$compiled_read(S_forged,pconfigpack_forged.SITE))',
            '~$config_ini_null_valid(S_forged,pconfigcall_forged)',
            *refusals('S_true', True), *budget('S_default'), *budget('S_true_resume'),
            *recovery('S_true_error', 'n_owner_S_default', '14'),
            'S_final = $drive_steps(S_recovered,3000)', 'S_final.COMPLETION = NORMAL',
            '$test_outputs(S_final.EVENTS) = ' + text('B|' + VALUE_ERROR + '|99|T|H|8192|' + MESSAGE + '|' + VALUE_ERROR + '|E|W|N|2783|2783|99|1|Z|R|14|11')]
    elif name == 'captured-owned-unpack-array-before-later-option-cow-and-pack-retirement':
        values += ['S_pre_found = $test_ini_owned_array_pack_builder_seek(S_initial,3000)',
            r'S_pre_found.COMPLETION = NORMAL \/ S_pre_found.COMPLETION = BUDGET',
            'S_pre = S_pre_found[.COMPLETION = NORMAL]', '$test_ini_owned_array_pack_builder(S_pre)',
            'S_pre.TODO = (ARRAY_NEXT n_builder phpType13*) :: ptask_pre*',
            'S_pre.ARRAYS[n_builder].ITEMS = [ENTRY (KSTRING ' + text('value') + ') (DIRECT (PARRAY n_captured))]',
            '(HARRAY n_builder) <- S_pre.ALLOCATIONS',
            '$node_children(S_pre,HARRAY n_builder) = [HARRAY n_captured]',
            '(HARRAY n_builder) <- $tasks_nodes(S_pre.TODO)',
            '$lookup(S_pre.ENV,' + text('call') + ') = (n_call)', 'S_pre.STORE[n_call] = DEFINED (POBJECT n_owner_pre)',
            '$lookup(S_pre.ENV,' + text('keep') + ') = (n_keep)', 'S_pre.STORE[n_keep] = DEFINED (POBJECT n_owner_pre)',
            'S_pre.OBJECTS[n_owner_pre] = INTRINSICCLOSURE INTRINSIC_INI_SET',
            '(HOBJECT n_owner_pre) <- $tasks_nodes(S_pre.TODO)',
            '$lookup(S_pre.ENV,' + text('replacement') + ') = (n_replacement)',
            'S_pre.STORE[n_replacement] = DEFINED (POBJECT n_live)', 'n_live =/= n_owner_pre',
            'S_pre.OBJECTS[n_live] = INTRINSICCLOSURE INTRINSIC_INI_GET',
            '$lookup(S_pre.ENV,' + text('value') + ') = (n_value)', 'S_pre.STORE[n_value] = DEFINED (PARRAY n_captured)',
            '$lookup(S_pre.ENV,' + text('arrayKeep') + ') = (n_array_keep)', 'S_pre.STORE[n_array_keep] = DEFINED (PARRAY n_captured)',
            'S_pre.ARRAYS[n_captured].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_captured)]',
            'pvalue_captured = PSTRING_CARRIER (REQUEST_STRING n_candidate) ' + text('captured-unpack-array75'),
            '$string_carrier_valid(S_pre,pvalue_captured)',
            '$lookup(S_pre.ENV,' + text('effects') + ') = (n_effects)', 'S_pre.STORE[n_effects] = DEFINED (PINT 0)',
            '$lookup(S_pre.ENV,' + text('warnings') + ') = (n_warnings)', 'S_pre.STORE[n_warnings] = DEFINED (PINT 0)',
            '$lookup(S_pre.ENV,' + text('result') + ') = (n_result)', 'S_pre.STORE[n_result] = DEFINED (PINT 99)',
            'S_pre.PRECISIONINI = ' + text('14'), '$test_outputs(S_pre.EVENTS) = ' + text('B|'), *common.public('S_pre'),
            *front('S', 'S_pre', 'reversed'), 'n_owner_S = n_owner_pre', 'n_array_S = n_captured',
            'n_outer_S = n_builder', '~((HARRAY n_builder) <- S.ALLOCATIONS)',
            '$compiled_read(S,pconfigpack_S.SITE) = eps',
            'S.ARRAYS[n_captured].ITEMS = S_pre.ARRAYS[n_captured].ITEMS',
            '$heap_count(HARRAY n_builder,$tasks_nodes(S.TODO)) = 0',
            '$heap_count(HARRAY n_captured,$tasks_nodes(S.TODO)) = 1',
            '$heap_count(HOBJECT n_owner_pre,$tasks_nodes(S.TODO)) = 1',
            'S.STORE[n_call] = DEFINED (POBJECT n_live)', 'S.STORE[n_keep] = DEFINED (POBJECT n_owner_pre)',
            'S.STORE[n_value] = DEFINED (PINT 0)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            'S.STORE[n_effects] = DEFINED (PINT 1)', 'S.STORE[n_warnings] = DEFINED (PINT 0)',
            'S.STORE[n_array_keep] = DEFINED (PARRAY n_option_array)', 'n_option_array =/= n_captured',
            'S.ARRAYS[n_option_array].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_option)]',
            '$string_bytes(pvalue_option) = (' + text('option-array75') + ')',
            '~$config_method_receiver(S,pconfigcall_S)', '~$config_strict(S,pconfigcall_S)',
            'S.PRECISIONINI = ' + text('7'), '$test_outputs(S.EVENTS) = ' + text('B|O|'),
            *returned('S', 1, '8', 'false'), 'S_return.STORE[n_result] = DEFINED (PINT 99)',
            'S_return.STORE[n_effects] = DEFINED (PINT 1)', 'S_return.STORE[n_keep] = DEFINED (POBJECT n_owner_pre)',
            'S_return.STORE[n_array_keep] = DEFINED (PARRAY n_handler_array)', 'n_handler_array =/= n_captured',
            'S_return.ARRAYS[n_handler_array].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_handler_array)]',
            '$string_bytes(pvalue_handler_array) = (' + text('handler-array75') + ')',
            'S_return.STORE[n_call] = DEFINED pvalue_handler_call', '$string_bytes(pvalue_handler_call) = (' + text('constant') + ')',
            'S_return.STORE[n_value] = DEFINED pvalue_handler_value', '$string_bytes(pvalue_handler_value) = (' + text('handler-value75') + ')',
            '$heap_count(HARRAY n_captured,$tasks_nodes(S_return.TODO)) = 1',
            *error('S', 'S_resume'), '$string_carrier_valid(S_error,pvalue_captured)',
            *refusals('S', True), *budget('S_pre'), *budget('S_resume'),
            *recovery('S_error', 'n_owner_pre', '8'),
            'S_final = $drive_steps(S_recovered,3000)', 'S_final.COMPLETION = NORMAL',
            '$test_outputs(S_final.EVENTS) = ' + text('B|O|W|8192|' + MESSAGE + '|' + VALUE_ERROR + '|99|1|1|constant|handler-value75|handler-array75|8|Z|R|8|11')]
    else:
        assert name == 'strict-owned-unpack-array-option-before-weak-explicit-mixed-value-error'
        values += [*front('S', 'S_initial', 'numeric'), 'i_option_S = 5', 'i_value_S = 9',
            'S.ARRAYS[n_array_S].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 2797))]',
            '$compiled_read(S,pconfigpack_S.SITE) = eps',
            '$lookup(S.ENV,' + text('call') + ') = (n_call)', 'S.STORE[n_call] = DEFINED (POBJECT n_live)',
            'n_live =/= n_owner_S', 'S.OBJECTS[n_live] = INTRINSICCLOSURE INTRINSIC_INI_GET',
            '$lookup(S.ENV,' + text('keep') + ') = (n_keep)', 'S.STORE[n_keep] = DEFINED (POBJECT n_owner_S)',
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
            '~$config_method_receiver(S,pconfigcall_S)', '~$config_ini_null_valid(S,pconfigcall_S)',
            *error('S', 'S', strict=True), *front('S_wrapper', 'S_error', 'mixed'),
            'i_option_S_wrapper = 3', 'n_owner_S_wrapper = n_owner_S',
            'S_wrapper.ARRAYS[n_array_S_wrapper].ITEMS = eps', *literal('S_wrapper', 'KSTRING ' + text('value')),
            '$config_method_receiver(S_wrapper,pconfigcall_S_wrapper)', '$exit_strict(S_wrapper,pconfigcall_S_wrapper.SITE)',
            '~$config_strict(S_wrapper,pconfigcall_S_wrapper)',
            *returned('S_wrapper', 1, '8', 'true'), *error('S_wrapper', 'S_wrapper_resume', explicit=True),
            *budget('S'), *budget('S_wrapper_resume'),
            'S_final = $drive_steps(S_wrapper_error,3000)', 'S_final.COMPLETION = NORMAL',
            '$test_outputs(S_final.EVENTS) = ' + text('B|P|' + OPTION_ERROR + '|99|1|0|0|0|0|9|E|H|8192|' + MESSAGE + '|' + VALUE_ERROR + '|99|1|1|8|Z')]
    return values + ['S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.ERRORHANDLER.CALLBACK = eps', 'S_final.USERCONSTANTS = eps', *common.public('S_final')]


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(path.relative_to(driver.ROOT)): sources.family.sha(path)
        for path in (Path(__file__), Path(shared.__file__), Path(shared.shared.__file__),
            Path(shared.shared.shared.__file__), Path(base.__file__), Path(sources.__file__))})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
