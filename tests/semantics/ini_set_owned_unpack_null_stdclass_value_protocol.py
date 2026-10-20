#!/usr/bin/env python3
"""Unpack retains a callable owner and the same live shared stdClass value."""
import json
import os
from pathlib import Path

import ini_set_unpack_null_stdclass_value_protocol as base
import ini_set_owned_null_stdclass_value_protocol as shared
import ini_set_owned_unpack_null_stdclass_value_sources as sources

driver, common, text, b64 = shared.driver, shared.common, shared.text, shared.b64
MESSAGE, VALUE_ERROR, OPTION_ERROR = shared.MESSAGE, shared.VALUE_ERROR, shared.OPTION_ERROR
reach, returned, budget, mark, error = shared.reach, shared.returned, shared.budget, shared.mark, shared.error
PREFIX = base.PREFIX + r"""
dec $test_ini_owned_std_pack_pending(pstate) : bool
def $test_ini_owned_std_pack_pending(S) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.OWNER = (n_owner)
  -- if pconfigcall.INDEX = 0
  -- if pconfigcall.PACKS = eps
  -- if pconfigcall.SENT = eps
def $test_ini_owned_std_pack_pending(S) = false -- otherwise
dec $test_ini_owned_std_pack_pending_seek(pstate, nat) : pstate
def $test_ini_owned_std_pack_pending_seek(S, 0) = S
def $test_ini_owned_std_pack_pending_seek(S, n) = S
  -- if $(n > 0)
  -- if $test_ini_owned_std_pack_pending(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_ini_owned_std_pack_pending_seek(S, n) = $test_ini_owned_std_pack_pending_seek($drive_steps($test_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_ini_owned_std_pack_pending(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def front(state, start, mode):
    call, owner, obj = 'pconfigcall_' + state, 'n_owner_' + state, 'n_object_' + state
    values = base.front(state, start, mode, False)
    for old, new in [(call + '.OWNER = eps', call + '.OWNER = (' + owner + ')'),
            ('$config_nodes(' + call + ') = [HOBJECT ' + obj + ']',
             '$config_nodes(' + call + ') = [HOBJECT ' + owner + ',HOBJECT ' + obj + ']'),
            ('$task_nodes(CONFIG_INI_NULL_RESULT ' + call + ') = [HOBJECT ' + obj + ']',
             '$task_nodes(CONFIG_INI_NULL_RESULT ' + call + ') = [HOBJECT ' + owner + ',HOBJECT ' + obj + ']')]:
        assert values.count(old) == 1
        values[values.index(old)] = new
    old = '~$config_method_receiver(' + state + ',' + call + ')'
    assert values.count(old) == 1
    values.remove(old)
    return values + [owner + ' =/= ' + obj,
        state + '.OBJECTS[' + owner + '] = INTRINSICCLOSURE INTRINSIC_INI_SET',
        '(HOBJECT ' + owner + ') <- ' + state + '.ALLOCATIONS', '$getclass_live_object(' + state + ',' + owner + ')']


def refusals(state, named):
    call, owner, obj = 'pconfigcall_' + state, 'n_owner_' + state, 'n_object_' + state
    values = base.refusals(state, named)
    for field in ('.OWNER = (0)', '.SELECTION = eps'):
        old = '~$config_ini_null_valid(' + state + ',' + call + '[' + field + '])'
        assert values.count(old) == 1
        values.remove(old)
    return values + ['~$config_ini_null_valid(' + state + ',' + call + '[.OWNER = eps])',
        '~$config_ini_null_valid(' + state + ',' + call + '[.OWNER = (' + obj + ')])',
        '~$config_ini_null_valid(' + state + ',' + call + '[.OWNER = (|' + state + '.OBJECTS|)])',
        '~$config_ini_null_valid(' + state + '[.OBJECTS[' + owner + '] = INTRINSICCLOSURE INTRINSIC_INI_GET],' + call + ')']


def recovery(start, owner, old_precision, strict=False):
    return [*shared.recovery(start, owner, old_precision, False),
        ('~' if not strict else '') + '$config_strict(S_recovery,pconfigcall_recovery)',
        '$config_nodes(pconfigcall_recovery) = [HOBJECT ' + owner + ']']


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET']
    if name == 'owned-unpacked-stdclass-default-and-explicit-return-share-api-wrapper-value':
        values += [*front('S_empty', 'S_initial', 'numeric'), 'i_option_S_empty = 3', 'i_value_S_empty = 7',
            '$objectprops_at(S_empty.OBJECTPROPS,n_object_S_empty) = (eps)',
            '~$config_method_receiver(S_empty,pconfigcall_S_empty)', '~$config_strict(S_empty,pconfigcall_S_empty)',
            '$config_ini_null_valid(S_empty,pconfigcall_S_empty)', '~$error_handler_eligible(S_empty,8192)',
            *error('S_empty', 'S_empty', default=True), *front('S_true', 'S_empty_error', 'reversed'),
            'n_owner_S_true = n_owner_S_empty', 'n_object_S_true =/= n_object_S_empty',
            *mark('S_true', 'n_object_S_true', '(PSTRING_CARRIER INTERNED_STRING ' + text('initial78') + ')'),
            '$lookup(S_true.ENV,' + text('objectKeep') + ') = (n_object_keep)',
            'S_true.STORE[n_object_keep] = DEFINED (POBJECT n_object_S_true)',
            '$lookup(S_true.ENV,' + text('value') + ') = (n_value)', 'S_true.STORE[n_value] = DEFINED (POBJECT n_object_S_true)',
            '$config_method_receiver(S_true,pconfigcall_S_true)', '~$config_strict(S_true,pconfigcall_S_true)',
            *returned('S_true', '14', 'true', 'true78'),
            'S_true_return.STORE[n_object_keep] = DEFINED (POBJECT n_object_S_true)',
            'S_true_return.STORE[n_value] = DEFINED (PINT 0)', *error('S_true', 'S_true_resume', explicit=True),
            *refusals('S_true', True), *budget('S_empty'), *budget('S_true_resume'),
            *recovery('S_true_error', 'n_owner_S_empty', '14'),
            'S_final = $drive_steps(S_recovered,3000)', 'S_final.COMPLETION = NORMAL',
            '$test_outputs(S_final.EVENTS) = ' + text('B|' + VALUE_ERROR + '|99|E|H|8192|' + MESSAGE + '|' + VALUE_ERROR + '|E|W|N|I|I|true78|99|1|Z|R|14|11')]
    elif name == 'captured-owned-unpack-stdclass-before-shared-option-and-live-value-effects':
        values += ['S_pre_found = $test_ini_std_pack_builder_seek(S_initial,3000)',
            r'S_pre_found.COMPLETION = NORMAL \/ S_pre_found.COMPLETION = BUDGET',
            'S_pre = S_pre_found[.COMPLETION = NORMAL]', '$test_ini_std_pack_builder(S_pre)',
            'S_pre.TODO = (ARRAY_NEXT n_builder phpType13*) :: ptask_pre*',
            'S_pre.ARRAYS[n_builder].ITEMS = [ENTRY (KSTRING ' + text('value') + ') (DIRECT (POBJECT n_captured))]',
            '(HARRAY n_builder) <- S_pre.ALLOCATIONS', '$node_children(S_pre,HARRAY n_builder) = [HOBJECT n_captured]',
            '(HARRAY n_builder) <- $tasks_nodes(S_pre.TODO)', 'S_pre.OBJECTS[n_captured] = STDINSTANCE',
            '$config_ini_rejected_stdclass(S_pre,n_captured)', *mark('S_pre', 'n_captured', 'pvalue_captured'),
            'pvalue_captured = PSTRING_CARRIER (REQUEST_STRING n_mark) ' + text('captured-owned-pack-object78'),
            '$string_carrier_valid(S_pre,pvalue_captured)',
            '$lookup(S_pre.ENV,' + text('call') + ') = (n_call)', 'S_pre.STORE[n_call] = DEFINED (POBJECT n_owner_pre)',
            'S_pre.OBJECTS[n_owner_pre] = INTRINSICCLOSURE INTRINSIC_INI_SET', 'n_owner_pre =/= n_captured',
            '$lookup(S_pre.ENV,' + text('keep') + ') = (n_keep)', 'S_pre.STORE[n_keep] = DEFINED (POBJECT n_owner_pre)',
            '$lookup(S_pre.ENV,' + text('replacement') + ') = (n_replacement)', 'S_pre.STORE[n_replacement] = DEFINED (POBJECT n_live)',
            'S_pre.OBJECTS[n_live] = INTRINSICCLOSURE INTRINSIC_INI_GET', 'n_live =/= n_owner_pre',
            '$heap_count(HOBJECT n_owner_pre,$tasks_nodes(S_pre.TODO)) = 1',
            '$lookup(S_pre.ENV,' + text('value') + ') = (n_value)', 'S_pre.STORE[n_value] = DEFINED (POBJECT n_captured)',
            '$lookup(S_pre.ENV,' + text('objectKeep') + ') = (n_object_keep)', 'S_pre.STORE[n_object_keep] = DEFINED (POBJECT n_captured)',
            '$lookup(S_pre.ENV,' + text('effects') + ') = (n_effects)', 'S_pre.STORE[n_effects] = DEFINED (PINT 0)',
            '$lookup(S_pre.ENV,' + text('warnings') + ') = (n_warnings)', 'S_pre.STORE[n_warnings] = DEFINED (PINT 0)',
            '$lookup(S_pre.ENV,' + text('result') + ') = (n_result)', 'S_pre.STORE[n_result] = DEFINED (PINT 99)',
            'S_pre.PRECISIONINI = ' + text('14'), '$test_outputs(S_pre.EVENTS) = ' + text('B|'), *common.public('S_pre'),
            *front('S', 'S_pre', 'reversed'), 'n_owner_S = n_owner_pre', 'n_object_S = n_captured', 'n_outer_S = n_builder',
            '~((HARRAY n_builder) <- S.ALLOCATIONS)', '$heap_count(HARRAY n_builder,$tasks_nodes(S.TODO)) = 0',
            '$heap_count(HOBJECT n_owner_pre,$tasks_nodes(S.TODO)) = 1',
            '$heap_count(HOBJECT n_captured,$tasks_nodes(S.TODO)) = 1',
            'S.STORE[n_call] = DEFINED (POBJECT n_live)', 'S.STORE[n_keep] = DEFINED (POBJECT n_owner_pre)',
            'S.STORE[n_value] = DEFINED (PINT 0)', 'S.STORE[n_object_keep] = DEFINED (POBJECT n_captured)',
            *mark('S', 'n_captured', '(PSTRING_CARRIER INTERNED_STRING ' + text('option78') + ')'),
            'S.STORE[n_result] = DEFINED (PINT 99)', 'S.STORE[n_effects] = DEFINED (PINT 1)', 'S.STORE[n_warnings] = DEFINED (PINT 0)',
            '~$config_method_receiver(S,pconfigcall_S)', '~$config_strict(S,pconfigcall_S)',
            'S.PRECISIONINI = ' + text('7'), '$test_outputs(S.EVENTS) = ' + text('B|O|'),
            *returned('S', '8', 'false', 'handler78'),
            'S_return.STORE[n_keep] = DEFINED (POBJECT n_owner_pre)', 'S_return.STORE[n_object_keep] = DEFINED (POBJECT n_captured)',
            'S_return.STORE[n_result] = DEFINED (PINT 99)', 'S_return.STORE[n_effects] = DEFINED (PINT 1)',
            'S_return.STORE[n_call] = DEFINED pvalue_handler_call', '$string_bytes(pvalue_handler_call) = (' + text('constant') + ')',
            'S_return.STORE[n_value] = DEFINED pvalue_handler_value', '$string_bytes(pvalue_handler_value) = (' + text('handler-value78') + ')',
            '$heap_count(HOBJECT n_owner_pre,$tasks_nodes(S_return.TODO)) = 1',
            '$heap_count(HOBJECT n_captured,$tasks_nodes(S_return.TODO)) = 1', *error('S', 'S_resume'),
            *refusals('S', True), *budget('S_pre'), *budget('S_resume'),
            *recovery('S_error', 'n_owner_pre', '8'), 'S_final = $drive_steps(S_recovered,3000)',
            'S_final.COMPLETION = NORMAL',
            '$test_outputs(S_final.EVENTS) = ' + text('B|O|W|8192|' + MESSAGE + '|' + VALUE_ERROR + '|99|1|1|constant|handler-value78|handler78|8|Z|R|8|11')]
    else:
        assert name == 'strict-owned-unpack-stdclass-option-before-weak-explicit-mixed-value-error'
        values += ['S_pre_found = $test_ini_owned_std_pack_pending_seek(S_initial,3000)',
            r'S_pre_found.COMPLETION = NORMAL \/ S_pre_found.COMPLETION = BUDGET',
            'S_pre = S_pre_found[.COMPLETION = NORMAL]', '$test_ini_owned_std_pack_pending(S_pre)',
            'S_pre.TODO = (CONFIG_ARGS pconfigcall_pre) :: ptask_pre*', 'pconfigcall_pre.OWNER = (n_owner_pre)',
            'pconfigcall_pre.SELECTION = eps', '$config_pending_valid(S_pre,pconfigcall_pre,true)',
            '$call_task_valid(S_pre,CONFIG_ARGS pconfigcall_pre)', '$config_nodes(pconfigcall_pre) = [HOBJECT n_owner_pre]',
            '$task_nodes(CONFIG_ARGS pconfigcall_pre) = [HOBJECT n_owner_pre]',
            'S_pre.OBJECTS[n_owner_pre] = INTRINSICCLOSURE INTRINSIC_INI_SET',
            '$lookup(S_pre.ENV,' + text('keep') + ') = (n_keep)', 'S_pre.STORE[n_keep] = DEFINED (POBJECT n_owner_pre)',
            '$lookup(S_pre.ENV,' + text('call') + ') = (n_call)', 'S_pre.STORE[n_call] = DEFINED (POBJECT n_owner_pre)',
            '$lookup(S_pre.ENV,' + text('replacement') + ') = (n_replacement)', 'S_pre.STORE[n_replacement] = DEFINED (POBJECT n_live)',
            'S_pre.OBJECTS[n_live] = INTRINSICCLOSURE INTRINSIC_INI_GET', 'n_live =/= n_owner_pre',
            '$lookup(S_pre.ENV,' + text('value') + ') = (n_value)', 'S_pre.STORE[n_value] = DEFINED (POBJECT n_captured)',
            'S_pre.OBJECTS[n_captured] = STDINSTANCE', 'n_captured =/= n_owner_pre',
            '$lookup(S_pre.ENV,' + text('objectKeep') + ') = (n_object_keep)', 'S_pre.STORE[n_object_keep] = DEFINED (POBJECT n_captured)',
            *mark('S_pre', 'n_captured', '(PSTRING_CARRIER INTERNED_STRING ' + text('before78') + ')'),
            '$lookup(S_pre.ENV,' + text('effects') + ') = (n_effects)', 'S_pre.STORE[n_effects] = DEFINED (PINT 0)',
            '$lookup(S_pre.ENV,' + text('warnings') + ') = (n_warnings)', 'S_pre.STORE[n_warnings] = DEFINED (PINT 0)',
            '$lookup(S_pre.ENV,' + text('result') + ') = (n_result)', 'S_pre.STORE[n_result] = DEFINED (PINT 99)',
            'S_pre.PRECISIONINI = ' + text('14'), '$test_outputs(S_pre.EVENTS) = ' + text('B|'), *common.public('S_pre'),
            *front('S', 'S_pre', 'numeric'), 'n_owner_S = n_owner_pre', 'n_object_S = n_captured',
            'i_option_S = 5', 'i_value_S = 9', *mark('S', 'n_captured', '(PSTRING_CARRIER INTERNED_STRING ' + text('strict78') + ')'),
            'S.STORE[n_keep] = DEFINED (POBJECT n_owner_pre)', 'S.STORE[n_call] = DEFINED (POBJECT n_live)',
            'S.STORE[n_value] = DEFINED (PINT 0)', 'S.STORE[n_object_keep] = DEFINED (POBJECT n_captured)',
            '$lookup(S.ENV,' + text('pack') + ') = (n_pack_cell)', 'S.STORE[n_pack_cell] = DEFINED (PARRAY n_live_outer)',
            'n_live_outer =/= n_outer_S',
            'S.ARRAYS[n_live_outer].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 0)),ENTRY (KINT 1) (DIRECT (PINT 0))]',
            'S.STORE[n_effects] = DEFINED (PINT 1)', 'S.STORE[n_warnings] = DEFINED (PINT 0)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            'S.PRECISIONINI = ' + text('9'), '$test_outputs(S.EVENTS) = ' + text('B|P|'),
            '~$config_method_receiver(S,pconfigcall_S)', '$exit_strict(S,pconfigcall_S.SITE)', '$config_strict(S,pconfigcall_S)',
            '~$config_ini_null_valid(S,pconfigcall_S)', *error('S', 'S', strict=True),
            *front('S_mixed', 'S_error', 'mixed'), 'i_option_S_mixed = 3', 'n_owner_S_mixed = n_owner_pre',
            'n_object_S_mixed =/= n_captured', '$objectprops_at(S_mixed.OBJECTPROPS,n_object_S_mixed) = (eps)',
            '$config_method_receiver(S_mixed,pconfigcall_S_mixed)', '$exit_strict(S_mixed,pconfigcall_S_mixed.SITE)',
            '~$config_strict(S_mixed,pconfigcall_S_mixed)',
            *returned('S_mixed', '8', 'true', 'unused78', empty=True), *error('S_mixed', 'S_mixed_resume', explicit=True),
            *budget('S_pre'), *budget('S'), *budget('S_mixed_resume'),
            *recovery('S_mixed_error', 'n_owner_pre', '8', strict=True),
            'S_final = $drive_steps(S_recovered,3000)', 'S_final.COMPLETION = NORMAL',
            '$test_outputs(S_final.EVENTS) = ' + text('B|P|' + OPTION_ERROR + '|99|1|0|strict78|0|0|9|E|H|8192|' + MESSAGE + '|' + VALUE_ERROR + '|99|1|1|8|Z|R|8|11')]
    return values + ['S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.ERRORHANDLER.CALLBACK = eps', 'S_final.USERCONSTANTS = eps', *common.public('S_final')]


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(path.relative_to(driver.ROOT)): sources.family.sha(path)
        for path in (Path(__file__), Path(base.__file__), Path(shared.__file__), Path(shared.shared.__file__),
            Path(shared.shared.shared.__file__), Path(shared.shared.shared.shared.__file__), Path(sources.__file__))})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
