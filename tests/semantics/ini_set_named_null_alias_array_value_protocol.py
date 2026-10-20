#!/usr/bin/env python3
"""Named sends retain an earlier array whose shared element remains live."""
import json
import os
from pathlib import Path

import ini_set_owned_null_alias_array_value_protocol as held
import ini_set_named_null_alias_array_value_sources as sources

shared, owner = held.shared, held.owner
driver, common, text, b64 = held.driver, held.common, held.text, held.b64
MESSAGE, VALUE_ERROR, OPTION_ERROR = held.MESSAGE, held.VALUE_ERROR, held.OPTION_ERROR
reach, returned, budget = held.reach, held.returned, held.budget
shape, leaf, current = held.shape, held.leaf, held.current
PREFIX = held.PREFIX + r"""
dec $test_ini_named_alias_partial(pstate) : bool
def $test_ini_named_alias_partial(S) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.INDEX = 1 /\ pconfigcall.NAMED
  -- if pconfigcall.SENT = [NAMED_HOLE,NAMED_SENT (KNOWN (PARRAY n_array))]
def $test_ini_named_alias_partial(S) = false -- otherwise
dec $test_ini_named_alias_partial_seek(pstate, nat) : pstate
def $test_ini_named_alias_partial_seek(S, 0) = S
def $test_ini_named_alias_partial_seek(S, n) = S
  -- if $(n > 0)
  -- if $test_ini_named_alias_partial(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_ini_named_alias_partial_seek(S, n) = $test_ini_named_alias_partial_seek($drive_steps($test_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_ini_named_alias_partial(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def front(state, start, mode='reversed', owned=False, explicit=False, selected=False):
    call = 'pconfigcall_' + state
    values = held.front(state, start, explicit) if owned else shared.front(state, start, selected)
    old = '~' + call + '.NAMED'
    assert values.count(old) == 1
    values[values.index(old)] = call + '.NAMED'
    for old in [
            '$intrinsic_argument(' + state + ',' + call + '.SITE,0) = ((expression_option_' + state + ',false,eps,porigin_option_' + state + ',z_option_' + state + '))',
            '$intrinsic_argument(' + state + ',' + call + '.SITE,1) = ((expression_value_' + state + ',false,eps,porigin_value_' + state + ',z_value_' + state + '))',
            '$compiled_read(' + state + ',porigin_value_' + state + ') = eps']:
        assert values.count(old) == 1
        values.remove(old)
    value_index = 0 if mode == 'reversed' else 1
    return values + [*owner.written(state, mode),
        '$compiled_read(' + state + ',porigin_' + state + '_' + str(value_index) + ') = eps']


def error(state, start, owned=False, explicit=False, strict=False):
    if owned:
        return held.error(state, start, explicit=explicit, strict=strict)
    assert not explicit
    return shared.error(state, start, strict=strict)


def refusals(state, owned=False):
    call = 'pconfigcall_' + state
    values = held.refusals(state) if owned else shared.refusals(state)
    old = '~$config_ini_null_valid(' + state + ',' + call + '[.NAMED = true])'
    assert values.count(old) == 1
    values[values.index(old)] = '~$config_ini_null_valid(' + state + ',' + call + '[.NAMED = false])'
    if not owned:
        old = '~$config_ini_null_valid(' + state + ',' + call + '[.OWNER = (0)])'
        assert values.count(old) == 1
        values[values.index(old)] = '~$config_ini_null_valid(' + state + ',' + call + '[.OWNER = (|' + state + '.OBJECTS|)])'
    return values + ['~$config_ini_named_stdclass_argument(' + state + ',' + call + ',2)',
        'S_direct_' + state + ' = ' + state + '[.ARRAYS[n_array_' + state + '].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 31))]]',
        '$config_ini_rejected_array(S_direct_' + state + ',n_array_' + state + ')',
        '~$config_ini_rejected_alias_array(S_direct_' + state + ',n_array_' + state + ')',
        '$config_ini_null_valid(S_direct_' + state + ',' + call + ')']


def partial(owned):
    roots = '[HOBJECT n_owner_pre,HARRAY n_captured]' if owned else '[HARRAY n_captured]'
    values = ['S_pre_found = $test_ini_named_alias_partial_seek(S_initial,3000)',
        r'S_pre_found.COMPLETION = NORMAL \/ S_pre_found.COMPLETION = BUDGET',
        'S_pre = S_pre_found[.COMPLETION = NORMAL]', '$test_ini_named_alias_partial(S_pre)',
        'S_pre.TODO = (CONFIG_ARGS pconfigcall_pre) :: ptask_pre*', 'pconfigcall_pre.KIND = INTRINSIC_INI_SET',
        'pconfigcall_pre.PACKS = eps', 'pconfigcall_pre.INDEX = 1', 'pconfigcall_pre.NAMED',
        'pconfigcall_pre.SENT = [NAMED_HOLE,NAMED_SENT (KNOWN (PARRAY n_captured))]',
        '$config_pending_valid(S_pre,pconfigcall_pre,false)', '$call_task_valid(S_pre,CONFIG_ARGS pconfigcall_pre)']
    if owned:
        values += ['pconfigcall_pre.OWNER = (n_owner_pre)', 'pconfigcall_pre.SELECTION = eps',
            'S_pre.OBJECTS[n_owner_pre] = INTRINSICCLOSURE INTRINSIC_INI_SET',
            '(HOBJECT n_owner_pre) <- S_pre.ALLOCATIONS',
            '$lookup(S_pre.ENV,' + text('keep') + ') = (n_keep)', 'S_pre.STORE[n_keep] = DEFINED (POBJECT n_owner_pre)',
            '$lookup(S_pre.ENV,' + text('call') + ') = (n_call)', 'S_pre.STORE[n_call] = DEFINED (POBJECT n_owner_pre)',
            '$lookup(S_pre.ENV,' + text('replacement') + ') = (n_replacement_cell)',
            'S_pre.STORE[n_replacement_cell] = DEFINED (POBJECT n_replacement)',
            'S_pre.OBJECTS[n_replacement] = INTRINSICCLOSURE INTRINSIC_INI_GET', 'n_replacement =/= n_owner_pre']
    else:
        values += ['pconfigcall_pre.OWNER = eps', 'pconfigcall_pre.SELECTION = (n_selection_pre)',
            'S_pre.SELECTEDCALLS[n_selection_pre].OWNER = eps',
            'S_pre.SELECTEDCALLS[n_selection_pre].KIND = INTRINSIC_INI_SET',
            'S_pre.SELECTEDCALLS[n_selection_pre].ORIGINAL = ' + text('InI_SeT'),
            '$lookup(S_pre.ENV,' + text('call') + ') = (n_call)',
            'S_pre.STORE[n_call] = DEFINED pvalue_keep', '$string_bytes(pvalue_keep) = (' + text('InI_SeT') + ')']
    return values + ['$config_nodes(pconfigcall_pre) = ' + roots, '$task_nodes(CONFIG_ARGS pconfigcall_pre) = ' + roots,
        '$lookup(S_pre.ENV,' + text('value') + ') = (n_value)', 'S_pre.STORE[n_value] = DEFINED (PARRAY n_captured)',
        '$lookup(S_pre.ENV,' + text('arrayKeep') + ') = (n_keep_array)', 'S_pre.STORE[n_keep_array] = DEFINED (PARRAY n_captured)',
        '$lookup(S_pre.ENV,' + text('old') + ') = (n_old)', 'S_pre.STORE[n_old] = DEFINED (PARRAY n_captured)',
        '$lookup(S_pre.ENV,' + text('leaf') + ') = (n_ref_captured)',
        *shape('S_pre', 'n_captured', 'n_ref_captured'), *leaf('S_pre', 'n_ref_captured', 'runtime-named-array83', True),
        '(HARRAY n_captured) <- S_pre.ALLOCATIONS', '$config_ini_rejected_alias_array(S_pre,n_captured)',
        '$lookup(S_pre.ENV,' + text('option') + ') = (n_option)', 'S_pre.STORE[n_option] = DEFINED PNULL',
        '$lookup(S_pre.ENV,' + text('effects') + ') = (n_effects)', 'S_pre.STORE[n_effects] = DEFINED (PINT 0)',
        '$lookup(S_pre.ENV,' + text('warnings') + ') = (n_warnings)', 'S_pre.STORE[n_warnings] = DEFINED (PINT 0)',
        '$lookup(S_pre.ENV,' + text('result') + ') = (n_result)', 'S_pre.STORE[n_result] = DEFINED (PINT 99)',
        'S_pre.PRECISIONINI = ' + text('14'), '$test_outputs(S_pre.EVENTS) = ' + text('B|'), *common.public('S_pre')]


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')', 'S_initial.COMPLETION = BUDGET']
    if name == 'named-alias-array-true-handlers-and-live-api-wrapper-trace':
        values += [*front('S_first', 'S_initial'), *leaf('S_first', 'n_ref_S_first', 'runtime-named-array83', True),
            '$compiled_read(S_first,porigin_S_first_1) = (PNULL)',
            '$lookup(S_first.ENV,' + text('keep') + ') = (n_keep_first)',
            'S_first.STORE[n_keep_first] = DEFINED (POBJECT n_setter_first)',
            'S_first.OBJECTS[n_setter_first] = INTRINSICCLOSURE INTRINSIC_INI_SET',
            *returned('S_first', 1, '14', 'true'), *leaf('S_first_return', 'n_ref_S_first', 'true-array83'),
            *current('S_first_return', 'n_array_S_first', 'n_ref_S_first', [43]), *error('S_first', 'S_first_resume'),
            *front('S_true', 'S_first_error', 'mixed', owned=True, explicit=True),
            'n_owner_S_true = n_setter_first', 'n_array_S_true = n_array_S_first', 'n_ref_S_true = n_ref_S_first',
            '$compiled_read(S_true,porigin_S_true_0) = (PNULL)', *leaf('S_true', 'n_ref_S_true', 'true-array83'),
            *returned('S_true', 2, '14', 'true'), *leaf('S_true_return', 'n_ref_S_true', 'true-array83'),
            *current('S_true_return', 'n_array_S_true', 'n_ref_S_true', [43, 43]), *error('S_true', 'S_true_resume', owned=True, explicit=True),
            'S_written_found = $test_ini_alias_leaf_seek(S_true_error,n_ref_S_true,' + text('after-error83') + ',3000)',
            r'S_written_found.COMPLETION = NORMAL \/ S_written_found.COMPLETION = BUDGET',
            'S_written = S_written_found[.COMPLETION = NORMAL]', '$test_ini_alias_leaf(S_written,n_ref_S_true,' + text('after-error83') + ')',
            *shape('S_written', 'n_array_S_true', 'n_ref_S_true'), *leaf('S_written', 'n_ref_S_true', 'after-error83'),
            *current('S_written', 'n_array_S_true', 'n_ref_S_true', [43, 43]),
            '$throwable_field(S_written,n_error_S_true,"trace") = PARRAY n_trace_S_true',
            'S_written.ARRAYS[n_args_S_true].ITEMS = [ENTRY (KINT 0) (DIRECT (PSTRING eps)),ENTRY (KINT 1) (DIRECT (PARRAY n_array_S_true))]',
            'S_written.ARRAYS[n_wrapper_args_S_true].ITEMS = [ENTRY (KINT 0) (DIRECT PNULL),ENTRY (KINT 1) (DIRECT (PARRAY n_array_S_true))]',
            '$lookup(S_written.ENV,' + text('trace') + ') = (n_observed_trace_cell)',
            'S_written.STORE[n_observed_trace_cell] = DEFINED (PARRAY n_observed_trace)',
            'S_written.ARRAYS[n_observed_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_observed_api)),ENTRY (KINT 1) (DIRECT (PARRAY n_observed_wrapper))]',
            '$trace_array_field(S_written,n_observed_api,' + text('args') + ') = PARRAY n_observed_args',
            'S_written.ARRAYS[n_observed_args].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_observed_option),ENTRY (KINT 1) (DIRECT (PARRAY n_observed_value))]',
            '$string_bytes(pvalue_observed_option) = (eps)', *shape('S_written', 'n_observed_value', 'n_ref_S_true')[:2],
            '(HARRAY n_observed_value) <- S_written.ALLOCATIONS',
            '$trace_array_field(S_written,n_observed_wrapper,' + text('function') + ') = PSTRING ' + text('__invoke'),
            '$trace_array_field(S_written,n_observed_wrapper,' + text('args') + ') = PARRAY n_observed_wrapper_args',
            'S_written.ARRAYS[n_observed_wrapper_args].ITEMS = [ENTRY (KINT 0) (DIRECT PNULL),ENTRY (KINT 1) (DIRECT (PARRAY n_observed_wrapper_value))]',
            *shape('S_written', 'n_observed_wrapper_value', 'n_ref_S_true')[:2], '(HARRAY n_observed_wrapper_value) <- S_written.ALLOCATIONS',
            *refusals('S_first'), *refusals('S_true', True), *budget('S_first_resume'), *budget('S_true_resume'), *budget('S_written'),
            *held.recovery('S_written', 'n_setter_first', '14'),
            '$test_outputs(S_final.EVENTS) = ' + text('B|H|8192|' + MESSAGE + '|' + VALUE_ERROR + '|99|T|H|8192|' + MESSAGE + '|' + VALUE_ERROR + '|E|W|N|L|L|A|43|99|2|Z|R|14|11')]
    else:
        strict = name == 'strict-owned-named-alias-array-then-same-owner-explicit-weak'
        assert strict or name == 'named-alias-array-captured-before-option-cell-and-container-effects'
        values += [*partial(strict), *front('S', 'S_pre', owned=strict, selected=not strict),
            'n_array_S = n_captured', 'n_ref_S = n_ref_captured',
            'pconfigcall_S = pconfigcall_pre[.INDEX = 2][.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (PARRAY n_captured))]]',
            '$compiled_read(S,porigin_S_1) = eps', 'S.STORE[n_value] = DEFINED (PINT 0)',
            'S.STORE[n_old] = DEFINED (PARRAY n_captured)', 'S.STORE[n_effects] = DEFINED (PINT 1)',
            'S.STORE[n_warnings] = DEFINED (PINT 0)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            'S.STORE[n_option] = DEFINED pvalue_option', '$string_bytes(pvalue_option) = (' + text('precision') + ')',
            *current('S', 'n_captured', 'n_ref_captured', [31]), '$test_outputs(S.EVENTS) = ' + text('B|O|')]
        if strict:
            values += ['n_owner_S = n_owner_pre', 'S.STORE[n_call] = DEFINED (POBJECT n_replacement)',
                'S.STORE[n_keep] = DEFINED (POBJECT n_owner_pre)', *leaf('S', 'n_ref_captured', 'strict-array83'),
                'S.PRECISIONINI = ' + text('9'), '$exit_strict(S,pconfigcall_S.SITE)', '$config_strict(S,pconfigcall_S)',
                '~$config_ini_null_valid(S,pconfigcall_S)', *error('S', 'S', owned=True, strict=True),
                *front('S_weak', 'S_error', owned=True, explicit=True),
                'n_owner_S_weak = n_owner_pre', 'n_array_S_weak = n_captured', 'n_ref_S_weak = n_ref_captured',
                '$compiled_read(S_weak,porigin_S_weak_1) = (PNULL)',
                '$exit_strict(S_weak,pconfigcall_S_weak.SITE)', '~$config_strict(S_weak,pconfigcall_S_weak)',
                *leaf('S_weak', 'n_ref_captured', 'strict-array83'), *returned('S_weak', 1, '9', 'true'),
                *leaf('S_weak_return', 'n_ref_captured', 'weak-array83'), *current('S_weak_return', 'n_captured', 'n_ref_captured', [31]),
                *error('S_weak', 'S_weak_resume', owned=True, explicit=True),
                *budget('S_pre'), *budget('S'), *budget('S_weak_resume'), *held.recovery('S_weak_error', 'n_owner_pre', '9', True),
                '$test_outputs(S_final.EVENTS) = ' + text('B|O|' + OPTION_ERROR + '|99|1|0|strict-array83|31|A|0|9|E|H|8192|' + MESSAGE + '|' + VALUE_ERROR + '|99|1|weak-array83|weak-array83|31|Z|R|9|11')]
        else:
            values += ['n_selection_S = n_selection_pre', 'S.SELECTEDCALLS[n_selection_S] = S_pre.SELECTEDCALLS[n_selection_pre]',
                'S.STORE[n_call] = DEFINED pvalue_call', '$string_bytes(pvalue_call) = (' + text('ini_get') + ')',
                *leaf('S', 'n_ref_captured', 'option-array83'), 'S.PRECISIONINI = ' + text('7'),
                '~$config_strict(S,pconfigcall_S)', *returned('S', 1, '8', 'false'),
                *leaf('S_return', 'n_ref_captured', 'handler-array83'), *current('S_return', 'n_captured', 'n_ref_captured', [31, 37]),
                '$heap_count(HARRAY n_captured,$tasks_nodes(S_return.TODO)) = 1', *error('S', 'S_resume'),
                *refusals('S'), *budget('S_pre'), *budget('S_resume'), *shared.recovery('S_error', '8'),
                '$test_outputs(S_final.EVENTS) = ' + text('B|O|W|8192|' + MESSAGE + '|' + VALUE_ERROR + '|99|1|1|handler-array83|handler-array83|31|37|A|constant|precision|handler-value83|8|Z|R|8|11')]
    return values + ['S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.ERRORHANDLER.CALLBACK = eps', 'S_final.USERCONSTANTS = eps', *common.public('S_final')]


def main():
    fingerprint = sources.family.fingerprint
    dependencies = (Path(__file__), Path(held.__file__), Path(shared.__file__), Path(shared.shared.__file__),
        Path(shared.shared.shared.__file__), Path(owner.__file__), Path(owner.shared.__file__), Path(owner.shared.shared.__file__),
        Path(shared.recovery_base.__file__), Path(sources.__file__))
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(path.relative_to(driver.ROOT)): sources.family.sha(path) for path in dependencies})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
