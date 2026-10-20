#!/usr/bin/env python3
"""Unpack capture preserves an earlier container and its shared live cell."""
import json
import os
from pathlib import Path

import ini_set_owned_unpack_null_array_value_protocol as pack
import ini_set_owned_null_alias_array_value_protocol as held
import ini_set_unpack_null_alias_array_value_sources as sources

alias = held.shared
driver, common, text, b64 = held.driver, held.common, held.text, held.b64
MESSAGE, VALUE_ERROR, OPTION_ERROR = held.MESSAGE, held.VALUE_ERROR, held.OPTION_ERROR
reach, returned, budget = held.reach, held.returned, held.budget
shape, leaf, current = held.shape, held.leaf, held.current
assert pack.PREFIX.startswith(pack.base.PREFIX)
PREFIX = alias.PREFIX + pack.PREFIX[len(pack.base.PREFIX):] + r"""
dec $test_ini_alias_pack_partial(pstate) : bool
def $test_ini_alias_pack_partial(S) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.INDEX = 0 /\ pconfigcall.PACKS = eps
  -- if pconfigcall.SENT = eps
def $test_ini_alias_pack_partial(S) = false -- otherwise
dec $test_ini_alias_pack_partial_seek(pstate, nat) : pstate
def $test_ini_alias_pack_partial_seek(S, 0) = S
def $test_ini_alias_pack_partial_seek(S, n) = S
  -- if $(n > 0)
  -- if $test_ini_alias_pack_partial(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_ini_alias_pack_partial_seek(S, n) = $test_ini_alias_pack_partial_seek($drive_steps($test_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_ini_alias_pack_partial(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def front(state, start, mode, owned=False, explicit=False, selected=False):
    call, owner, array = 'pconfigcall_' + state, 'n_owner_' + state, 'n_array_' + state
    values = pack.front(state, start, mode)
    old = '$config_ini_rejected_array(' + state + ',' + array + ')'
    assert values.count(old) == 1
    values[values.index(old)] = '$config_ini_rejected_alias_array(' + state + ',' + array + ')'
    old = '$node_children(' + state + ',HARRAY ' + array + ') = eps'
    assert values.count(old) == 1
    values.remove(old)
    old = '$config_ini_pack_known(' + state + ',pconfigpack_' + state + '.ITEMS,$compiled_read(' + state + ',pconfigpack_' + state + '.SITE))'
    assert values.count(old) == 1
    values[values.index(old)] = '$compiled_read(' + state + ',pconfigpack_' + state + '.SITE) = eps'
    if not owned:
        excluded = {state + '.OBJECTS[' + owner + '] = INTRINSICCLOSURE INTRINSIC_INI_SET',
            '(HOBJECT ' + owner + ') <- ' + state + '.ALLOCATIONS'}
        assert excluded <= set(values)
        values = [v.replace(call + '.OWNER = (' + owner + ')', call + '.OWNER = eps').replace(
            '[HOBJECT ' + owner + ',HARRAY ', '[HARRAY ') for v in values if v not in excluded]
    if selected:
        assert not owned
        values.remove(call + '.SELECTION = eps')
        values += [call + '.SELECTION = (n_selection_' + state + ')',
            state + '.SELECTEDCALLS[n_selection_' + state + '].OWNER = eps',
            state + '.SELECTEDCALLS[n_selection_' + state + '].KIND = INTRINSIC_INI_SET',
            state + '.SELECTEDCALLS[n_selection_' + state + '].SITE = ' + call + '.SITE',
            state + '.SELECTEDCALLS[n_selection_' + state + '].LINE = ' + call + '.LINE']
    return values + [*shape(state, array, 'n_ref_' + state),
        '~$config_ini_rejected_array(' + state + ',' + array + ')',
        ('' if explicit else '~') + '$config_method_receiver(' + state + ',' + call + ')',
        '~$pipe_site(' + state + ',' + call + '.SITE)']


def error(state, start, owned=False, explicit=False, strict=False, default=False):
    if owned:
        return held.error(state, start, explicit=explicit, strict=strict, default=default)
    assert not explicit
    return alias.error(state, start, strict=strict, default=default)


def refusals(state, named, owned=False):
    values = pack.refusals(state, named)
    if not owned:
        excluded = {'~$config_ini_null_valid(' + state + ',pconfigcall_' + state + '[.OWNER = eps])',
            '~$config_ini_null_valid(' + state + '[.OBJECTS[n_owner_' + state + '] = INTRINSICCLOSURE INTRINSIC_INI_GET],pconfigcall_' + state + ')'}
        assert excluded <= set(values)
        values = [v for v in values if v not in excluded]
    return values + [v for v in alias.refusals(state) if not v.startswith('~$config_ini_null_valid(')]


def before_option():
    values = ['S_pre_found = $test_ini_owned_array_pack_builder_seek(S_initial,3000)',
        r'S_pre_found.COMPLETION = NORMAL \/ S_pre_found.COMPLETION = BUDGET',
        'S_pre = S_pre_found[.COMPLETION = NORMAL]', '$test_ini_owned_array_pack_builder(S_pre)',
        'S_pre.TODO = (ARRAY_NEXT n_builder phpType13*) :: ptask_pre*',
        'S_pre.ARRAYS[n_builder].ITEMS = [ENTRY (KSTRING ' + text('value') + ') (DIRECT (PARRAY n_captured))]',
        '(HARRAY n_builder) <- S_pre.ALLOCATIONS', '$node_children(S_pre,HARRAY n_builder) = [HARRAY n_captured]',
        '$heap_count(HARRAY n_builder,$tasks_nodes(S_pre.TODO)) = 1',
        '$heap_count(HARRAY n_captured,$tasks_nodes(S_pre.TODO)) = 0',
        *shape('S_pre', 'n_captured', 'n_ref_captured'), *leaf('S_pre', 'n_ref_captured', 'captured-pack-array84', True)]
    for variable in ('call', 'keep', 'value', 'arrayKeep', 'old', 'leaf', 'option', 'effects', 'warnings', 'result'):
        values += ['$lookup(S_pre.ENV,' + text(variable) + ') = (n_' + variable + ')']
    return values + ['n_leaf = n_ref_captured', 'S_pre.STORE[n_call] = DEFINED pvalue_original_call',
        '$string_bytes(pvalue_original_call) = (' + text('InI_SeT') + ')',
        'S_pre.STORE[n_keep] = DEFINED pvalue_original_call',
        'S_pre.STORE[n_value] = DEFINED (PARRAY n_captured)', 'S_pre.STORE[n_arrayKeep] = DEFINED (PARRAY n_captured)',
        'S_pre.STORE[n_old] = DEFINED (PARRAY n_captured)', 'S_pre.STORE[n_option] = DEFINED PNULL',
        'S_pre.STORE[n_effects] = DEFINED (PINT 0)', 'S_pre.STORE[n_warnings] = DEFINED (PINT 0)',
        'S_pre.STORE[n_result] = DEFINED (PINT 99)', 'S_pre.PRECISIONINI = ' + text('14'),
        '$test_outputs(S_pre.EVENTS) = ' + text('B|'), *common.public('S_pre')]


def before_pack():
    values = ['S_pre_found = $test_ini_alias_pack_partial_seek(S_initial,3000)',
        r'S_pre_found.COMPLETION = NORMAL \/ S_pre_found.COMPLETION = BUDGET',
        'S_pre = S_pre_found[.COMPLETION = NORMAL]', '$test_ini_alias_pack_partial(S_pre)',
        'S_pre.TODO = (CONFIG_ARGS pconfigcall_pre) :: ptask_pre*',
        'pconfigcall_pre.OWNER = (n_owner_pre)', 'pconfigcall_pre.SELECTION = eps',
        '$config_pending_valid(S_pre,pconfigcall_pre,true)', '$call_task_valid(S_pre,CONFIG_ARGS pconfigcall_pre)',
        '$config_nodes(pconfigcall_pre) = [HOBJECT n_owner_pre]',
        'S_pre.OBJECTS[n_owner_pre] = INTRINSICCLOSURE INTRINSIC_INI_SET']
    for variable in ('call', 'keep', 'value', 'arrayKeep', 'old', 'leaf', 'pack', 'packOld', 'replacement', 'effects', 'warnings', 'result'):
        values += ['$lookup(S_pre.ENV,' + text(variable) + ') = (n_' + variable + ')']
    return values + ['S_pre.STORE[n_call] = DEFINED (POBJECT n_owner_pre)',
        'S_pre.STORE[n_keep] = DEFINED (POBJECT n_owner_pre)',
        'S_pre.STORE[n_replacement] = DEFINED (POBJECT n_getter_pre)',
        'S_pre.OBJECTS[n_getter_pre] = INTRINSICCLOSURE INTRINSIC_INI_GET',
        'S_pre.STORE[n_value] = DEFINED (PARRAY n_captured)', 'S_pre.STORE[n_arrayKeep] = DEFINED (PARRAY n_captured)',
        'S_pre.STORE[n_old] = DEFINED (PARRAY n_captured)', 'n_leaf = n_ref_captured',
        *shape('S_pre', 'n_captured', 'n_ref_captured'), *leaf('S_pre', 'n_ref_captured', 'strict-pack-array84', True),
        'S_pre.STORE[n_pack] = DEFINED (PARRAY n_outer_pre)', 'S_pre.STORE[n_packOld] = DEFINED (PARRAY n_outer_pre)',
        'S_pre.ARRAYS[n_outer_pre].ITEMS = [ENTRY (KINT 5) (DIRECT PNULL),ENTRY (KINT 9) (DIRECT (PARRAY n_captured))]',
        '$node_children(S_pre,HARRAY n_outer_pre) = [HARRAY n_captured]',
        'S_pre.STORE[n_effects] = DEFINED (PINT 0)', 'S_pre.STORE[n_warnings] = DEFINED (PINT 0)',
        'S_pre.STORE[n_result] = DEFINED (PINT 99)', 'S_pre.PRECISIONINI = ' + text('14'),
        '$test_outputs(S_pre.EVENTS) = ' + text('B|'), *common.public('S_pre')]


def observed():
    values = ['S_written_found = $test_ini_alias_leaf_seek(S_true_error,n_ref_S_true,' + text('after-error84') + ',3000)',
        r'S_written_found.COMPLETION = NORMAL \/ S_written_found.COMPLETION = BUDGET',
        'S_written = S_written_found[.COMPLETION = NORMAL]', '$test_ini_alias_leaf(S_written,n_ref_S_true,' + text('after-error84') + ')',
        *shape('S_written', 'n_array_S_true', 'n_ref_S_true'), *leaf('S_written', 'n_ref_S_true', 'after-error84'),
        *current('S_written', 'n_array_S_true', 'n_ref_S_true', [43]),
        '$throwable_field(S_written,n_error_S_true,"trace") = PARRAY n_trace_S_true',
        'S_written.ARRAYS[n_args_S_true].ITEMS = [ENTRY (KINT 0) (DIRECT (PSTRING eps)),ENTRY (KINT 1) (DIRECT (PARRAY n_array_S_true))]',
        'S_written.ARRAYS[n_wrapper_args_S_true].ITEMS = [ENTRY (KINT 0) (DIRECT PNULL),ENTRY (KINT 1) (DIRECT (PARRAY n_array_S_true))]',
        '$lookup(S_written.ENV,' + text('trace') + ') = (n_observed_trace_cell)',
        'S_written.STORE[n_observed_trace_cell] = DEFINED (PARRAY n_observed_trace)',
        'S_written.ARRAYS[n_observed_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_observed_api)),ENTRY (KINT 1) (DIRECT (PARRAY n_observed_wrapper))]',
        '$trace_array_field(S_written,n_observed_wrapper,' + text('function') + ') = PSTRING ' + text('__invoke')]
    for suffix, option in [('api', 'pvalue_observed_option'), ('wrapper', 'PNULL')]:
        values += ['$trace_array_field(S_written,n_observed_' + suffix + ',' + text('args') + ') = PARRAY n_observed_' + suffix + '_args',
            'S_written.ARRAYS[n_observed_' + suffix + '_args].ITEMS = [ENTRY (KINT 0) (DIRECT ' + option + '),ENTRY (KINT 1) (DIRECT (PARRAY n_observed_' + suffix + '_value))]',
            *shape('S_written', 'n_observed_' + suffix + '_value', 'n_ref_S_true')[:2],
            '(HARRAY n_observed_' + suffix + '_value) <- S_written.ALLOCATIONS']
    return values + ['$string_bytes(pvalue_observed_option) = (eps)']


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')', 'S_initial.COMPLETION = BUDGET']
    if name == 'unpacked-alias-array-default-and-explicit-live-api-wrapper-cell':
        values += [*front('S_default', 'S_initial', 'numeric'), 'i_option_S_default = 3', 'i_value_S_default = 7',
            *leaf('S_default', 'n_ref_S_default', 'runtime-unpack-array84', True),
            '$lookup(S_default.ENV,' + text('keep') + ') = (n_keep_default)',
            'S_default.STORE[n_keep_default] = DEFINED (POBJECT n_setter_default)',
            'S_default.OBJECTS[n_setter_default] = INTRINSICCLOSURE INTRINSIC_INI_SET',
            '~$config_strict(S_default,pconfigcall_S_default)', '$config_ini_null_valid(S_default,pconfigcall_S_default)',
            '~$error_handler_eligible(S_default,8192)', *error('S_default', 'S_default', default=True),
            *front('S_true', 'S_default_error', 'reversed', owned=True, explicit=True),
            'n_owner_S_true = n_setter_default', 'n_array_S_true = n_array_S_default', 'n_ref_S_true = n_ref_S_default',
            *leaf('S_true', 'n_ref_S_true', 'runtime-unpack-array84', True), '~$config_strict(S_true,pconfigcall_S_true)',
            *returned('S_true', 1, '14', 'true'), *leaf('S_true_return', 'n_ref_S_true', 'true-array84'),
            *current('S_true_return', 'n_array_S_true', 'n_ref_S_true', [43]),
            *error('S_true', 'S_true_resume', owned=True, explicit=True), *observed(),
            *refusals('S_default', False), *refusals('S_true', True, True),
            *budget('S_default'), *budget('S_true_resume'), *budget('S_written'),
            *held.recovery('S_written', 'n_setter_default', '14'),
            '$test_outputs(S_final.EVENTS) = ' + text('B|' + VALUE_ERROR + '|99|E|H|8192|' + MESSAGE + '|' + VALUE_ERROR + '|E|W|N|L|L|A|43|99|1|Z|R|14|11')]
    elif name == 'captured-unpack-alias-array-before-option-cell-and-live-value-effects':
        values += [*before_option(), *front('S', 'S_pre', 'reversed', selected=True),
            'n_array_S = n_captured', 'n_ref_S = n_ref_captured', 'n_outer_S = n_builder',
            'S.SELECTEDCALLS[n_selection_S] = S_pre.SELECTEDCALLS[n_selection_S]',
            '~((HARRAY n_builder) <- S.ALLOCATIONS)', '$heap_count(HARRAY n_builder,$tasks_nodes(S.TODO)) = 0',
            '$heap_count(HARRAY n_captured,$tasks_nodes(S.TODO)) = 1',
            '$heap_count(HCELL n_ref_captured,$tasks_nodes(S.TODO)) = 0',
            'S.ARRAYS[n_captured] = S_pre.ARRAYS[n_captured]',
            'S.STORE[n_value] = DEFINED (PINT 0)', 'S.STORE[n_old] = DEFINED (PARRAY n_captured)',
            'S.STORE[n_call] = DEFINED pvalue_live_call', '$string_bytes(pvalue_live_call) = (' + text('ini_get') + ')',
            'S.STORE[n_keep] = DEFINED pvalue_original_call', 'S.STORE[n_effects] = DEFINED (PINT 1)',
            'S.STORE[n_warnings] = DEFINED (PINT 0)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            *leaf('S', 'n_ref_captured', 'option-array84'), *current('S', 'n_captured', 'n_ref_captured', [31]),
            'S.PRECISIONINI = ' + text('14'), '$test_outputs(S.EVENTS) = ' + text('B|O|'), '~$config_strict(S,pconfigcall_S)',
            *returned('S', 1, '8', 'false'), *leaf('S_return', 'n_ref_captured', 'handler-array84'),
            *current('S_return', 'n_captured', 'n_ref_captured', [31, 37]),
            '$heap_count(HARRAY n_captured,$tasks_nodes(S_return.TODO)) = 1',
            *error('S', 'S_resume'), *refusals('S', True), *budget('S_pre'), *budget('S_resume'),
            *alias.recovery('S_error', '8'),
            '$test_outputs(S_final.EVENTS) = ' + text('B|O|W|8192|' + MESSAGE + '|' + VALUE_ERROR + '|99|1|1|handler-array84|handler-array84|31|37|A|constant|precision|handler-value84|8|Z|R|8|11')]
    else:
        assert name == 'strict-owned-unpack-alias-array-then-same-owner-explicit-mixed-weak'
        values += [*before_pack(), *front('S', 'S_pre', 'numeric', owned=True),
            'i_option_S = 5', 'i_value_S = 9', 'n_owner_S = n_owner_pre',
            'n_array_S = n_captured', 'n_ref_S = n_ref_captured', 'n_outer_S = n_outer_pre',
            'pconfigcall_S = pconfigcall_pre[.INDEX = 1][.PACKS = [pconfigpack_S]][.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (PARRAY n_captured))]]',
            '$config_nodes(pconfigcall_S) = [HOBJECT n_owner_pre,HARRAY n_captured]',
            '$heap_count(HARRAY n_outer_pre,$tasks_nodes(S.TODO)) = 0',
            'S.STORE[n_packOld] = DEFINED (PARRAY n_outer_pre)',
            'S.ARRAYS[n_outer_pre] = S_pre.ARRAYS[n_outer_pre]',
            'S.STORE[n_pack] = DEFINED (PARRAY n_live_pack)', 'n_live_pack =/= n_outer_pre',
            'S.ARRAYS[n_live_pack].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 0)),ENTRY (KINT 1) (DIRECT (PINT 0))]',
            'S.STORE[n_value] = DEFINED (PINT 0)', 'S.STORE[n_call] = DEFINED (POBJECT n_getter_pre)',
            'S.STORE[n_keep] = DEFINED (POBJECT n_owner_pre)', 'S.STORE[n_effects] = DEFINED (PINT 1)',
            'S.STORE[n_warnings] = DEFINED (PINT 0)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            *leaf('S', 'n_ref_captured', 'strict-array84'), *current('S', 'n_captured', 'n_ref_captured', [31]),
            'S.PRECISIONINI = ' + text('14'), '$test_outputs(S.EVENTS) = ' + text('B|P|'),
            '$exit_strict(S,pconfigcall_S.SITE)', '$config_strict(S,pconfigcall_S)', '~$config_ini_null_valid(S,pconfigcall_S)',
            *error('S', 'S', owned=True, strict=True), *front('S_weak', 'S_error', 'mixed', owned=True, explicit=True),
            'i_option_S_weak = 3', 'n_owner_S_weak = n_owner_pre', 'n_array_S_weak = n_captured', 'n_ref_S_weak = n_ref_captured',
            '$exit_strict(S_weak,pconfigcall_S_weak.SITE)', '~$config_strict(S_weak,pconfigcall_S_weak)',
            *leaf('S_weak', 'n_ref_captured', 'strict-array84'), *returned('S_weak', 1, '8', 'true'),
            *leaf('S_weak_return', 'n_ref_captured', 'weak-array84'), *current('S_weak_return', 'n_captured', 'n_ref_captured', [31]),
            *error('S_weak', 'S_weak_resume', owned=True, explicit=True), *refusals('S_weak', True, True),
            *budget('S_pre'), *budget('S'), *budget('S_weak_resume'), *held.recovery('S_weak_error', 'n_owner_pre', '8', True),
            '$test_outputs(S_final.EVENTS) = ' + text('B|P|' + OPTION_ERROR + '|99|1|0|strict-array84|31|0|0|14|E|H|8192|' + MESSAGE + '|' + VALUE_ERROR + '|99|1|1|weak-array84|weak-array84|31|8|Z|R|8|11')]
    return values + ['S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.ERRORHANDLER.CALLBACK = eps', 'S_final.USERCONSTANTS = eps', *common.public('S_final')]


def main():
    fingerprint = sources.family.fingerprint
    dependencies = (Path(__file__), Path(pack.__file__), Path(pack.shared.__file__), Path(pack.shared.shared.__file__),
        Path(pack.base.__file__), Path(held.__file__), Path(alias.__file__), Path(alias.shared.__file__),
        Path(held.owner.__file__), Path(held.owner.shared.__file__), Path(held.owner.shared.shared.__file__),
        Path(alias.recovery_base.__file__), Path(sources.__file__))
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(path.relative_to(driver.ROOT)): sources.family.sha(path) for path in dependencies})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
