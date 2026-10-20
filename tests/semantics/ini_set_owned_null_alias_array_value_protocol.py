#!/usr/bin/env python3
"""The captured receiver and by-value array retain a shared primitive cell."""
import json
import os
from pathlib import Path

import ini_set_null_alias_array_value_protocol as shared
import ini_set_owned_null_stdclass_value_protocol as owner
import ini_set_owned_null_alias_array_value_sources as sources

driver, common, text, b64 = shared.driver, shared.common, shared.text, shared.b64
MESSAGE, VALUE_ERROR, OPTION_ERROR = shared.MESSAGE, shared.VALUE_ERROR, shared.OPTION_ERROR
reach, returned, budget, unchanged = shared.reach, shared.returned, shared.budget, shared.unchanged
shape, leaf, current = shared.shape, shared.leaf, shared.current
assert owner.PREFIX.startswith(shared.shared.shared.PREFIX)
PREFIX = shared.PREFIX + owner.PREFIX[len(shared.shared.shared.PREFIX):]


def front(state, start, explicit=False):
    call, held, array = 'pconfigcall_' + state, 'n_owner_' + state, 'n_array_' + state
    values = shared.front(state, start, False)
    replacements = {
        call + '.OWNER = eps': call + '.OWNER = (' + held + ')',
        '$config_nodes(' + call + ') = [HARRAY ' + array + ']':
            '$config_nodes(' + call + ') = [HOBJECT ' + held + ',HARRAY ' + array + ']',
        '$task_nodes(CONFIG_INI_NULL_RESULT ' + call + ') = [HARRAY ' + array + ']':
            '$task_nodes(CONFIG_INI_NULL_RESULT ' + call + ') = [HOBJECT ' + held + ',HARRAY ' + array + ']',
        '~$config_method_receiver(' + state + ',' + call + ')':
            ('' if explicit else '~') + '$config_method_receiver(' + state + ',' + call + ')',
    }
    for old, new in replacements.items():
        assert values.count(old) == 1
        values[values.index(old)] = new
    return values + [state + '.OBJECTS[' + held + '] = INTRINSICCLOSURE INTRINSIC_INI_SET',
        '(HOBJECT ' + held + ') <- ' + state + '.ALLOCATIONS',
        '$node_children(' + state + ',HOBJECT ' + held + ') = eps',
        '$config_selected_valid(' + state + ',' + call + ')',
        '~$pipe_site(' + state + ',' + call + '.SITE)', state + '.CURRENT = eps', state + '.FRAMES = eps']


def error(state, start, explicit=False, strict=False, default=False):
    values = owner.error(state, start, explicit=explicit, strict=strict, default=default)
    for old in [
            '$objectprops_at(' + state + '_error.OBJECTPROPS,n_object_' + state + ') = $objectprops_at(' + start + '.OBJECTPROPS,n_object_' + state + ')',
            '$object_table_at(' + state + '_error.OBJECTTABLES,n_object_' + state + ') = eps']:
        assert values.count(old) == 1
        values.remove(old)
    values = [v.replace('POBJECT n_object_' + state, 'PARRAY n_array_' + state).replace(
        'HOBJECT n_object_' + state, 'HARRAY n_array_' + state) for v in values]
    return values + [state + '_error.ARRAYS[n_array_' + state + '] = ' + start + '.ARRAYS[n_array_' + state + ']',
        *shape(state + '_error', 'n_array_' + state, 'n_ref_' + state)]


def refusals(state):
    call, held = 'pconfigcall_' + state, 'n_owner_' + state
    values = shared.refusals(state)
    old = '~$config_ini_null_valid(' + state + ',' + call + '[.OWNER = (0)])'
    assert values.count(old) == 1
    values[values.index(old)] = '~$config_ini_null_valid(' + state + ',' + call + '[.OWNER = eps])'
    return values + ['~$config_ini_null_valid(' + state + ',' + call + '[.OWNER = (|' + state + '.OBJECTS|)])',
        '~$config_ini_null_valid(' + state + '[.OBJECTS[' + held + '] = INTRINSICCLOSURE INTRINSIC_INI_GET],' + call + ')',
        '~$config_ini_null_valid(' + state + '[.ALLOCATIONS = eps],' + call + ')']


def recovery(start, held, precision, strict=False):
    return [*owner.recovery(start, held, precision, False),
        ('' if strict else '~') + '$config_strict(S_recovery,pconfigcall_recovery)',
        '$config_nodes(pconfigcall_recovery) = [HOBJECT ' + held + ']',
        'S_final = $drive_steps(S_recovered,3000)', 'S_final.COMPLETION = NORMAL']


def partial():
    return ['S_pre_found = $test_ini_owned_std_partial_seek(S_initial,0,3000)',
        r'S_pre_found.COMPLETION = NORMAL \/ S_pre_found.COMPLETION = BUDGET',
        'S_pre = S_pre_found[.COMPLETION = NORMAL]', '$test_ini_owned_std_partial(S_pre,0)',
        'S_pre.TODO = (CONFIG_ARGS pconfigcall_pre) :: ptask_pre*', 'pconfigcall_pre.OWNER = (n_owner_pre)',
        'pconfigcall_pre.SELECTION = eps', 'pconfigcall_pre.PACKS = eps', 'pconfigcall_pre.INDEX = 1',
        '~pconfigcall_pre.NAMED', 'pconfigcall_pre.SENT = [NAMED_SENT (KNOWN PNULL)]',
        '$config_pending_valid(S_pre,pconfigcall_pre,false)', '$call_task_valid(S_pre,CONFIG_ARGS pconfigcall_pre)',
        '$config_nodes(pconfigcall_pre) = [HOBJECT n_owner_pre]',
        '$task_nodes(CONFIG_ARGS pconfigcall_pre) = [HOBJECT n_owner_pre]',
        'S_pre.OBJECTS[n_owner_pre] = INTRINSICCLOSURE INTRINSIC_INI_SET',
        '(HOBJECT n_owner_pre) <- S_pre.ALLOCATIONS', '$node_children(S_pre,HOBJECT n_owner_pre) = eps',
        '$lookup(S_pre.ENV,' + text('call') + ') = (n_call)', 'S_pre.STORE[n_call] = DEFINED (POBJECT n_owner_pre)',
        '$lookup(S_pre.ENV,' + text('keep') + ') = (n_keep)', 'S_pre.STORE[n_keep] = DEFINED (POBJECT n_owner_pre)',
        '$lookup(S_pre.ENV,' + text('replacement') + ') = (n_replacement_cell)',
        'S_pre.STORE[n_replacement_cell] = DEFINED (POBJECT n_replacement)',
        'S_pre.OBJECTS[n_replacement] = INTRINSICCLOSURE INTRINSIC_INI_GET', 'n_replacement =/= n_owner_pre',
        '(HOBJECT n_replacement) <- S_pre.ALLOCATIONS',
        '$lookup(S_pre.ENV,' + text('value') + ') = (n_value)', 'S_pre.STORE[n_value] = DEFINED (PARRAY n_captured)',
        '$lookup(S_pre.ENV,' + text('arrayKeep') + ') = (n_keep_array)', 'S_pre.STORE[n_keep_array] = DEFINED (PARRAY n_captured)',
        '$lookup(S_pre.ENV,' + text('old') + ') = (n_old)', 'S_pre.STORE[n_old] = DEFINED (PARRAY n_captured)',
        '$lookup(S_pre.ENV,' + text('leaf') + ') = (n_ref_captured)',
        *shape('S_pre', 'n_captured', 'n_ref_captured'), *leaf('S_pre', 'n_ref_captured', 'runtime-owned-array82', True),
        '(HARRAY n_captured) <- S_pre.ALLOCATIONS', '$config_ini_rejected_alias_array(S_pre,n_captured)',
        '$lookup(S_pre.ENV,' + text('option') + ') = (n_option)', 'S_pre.STORE[n_option] = DEFINED PNULL',
        '$lookup(S_pre.ENV,' + text('effects') + ') = (n_effects)', 'S_pre.STORE[n_effects] = DEFINED (PINT 0)',
        '$lookup(S_pre.ENV,' + text('warnings') + ') = (n_warnings)', 'S_pre.STORE[n_warnings] = DEFINED (PINT 0)',
        '$lookup(S_pre.ENV,' + text('result') + ') = (n_result)', 'S_pre.STORE[n_result] = DEFINED (PINT 99)',
        'S_pre.PRECISIONINI = ' + text('14'), '$test_outputs(S_pre.EVENTS) = ' + text('B|'), *common.public('S_pre')]


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')', 'S_initial.COMPLETION = BUDGET']
    if name == 'owned-null-alias-array-api-and-wrapper-see-post-trace-cell-write':
        values += [*front('S_default', 'S_initial'), *leaf('S_default', 'n_ref_S_default', 'runtime-owned-array82', True),
            '$compiled_read(S_default,porigin_option_S_default) = (PNULL)', '$config_ini_null_valid(S_default,pconfigcall_S_default)',
            '~$error_handler_eligible(S_default,8192)', *error('S_default', 'S_default', default=True),
            *front('S_true', 'S_default_error', True), 'n_owner_S_true = n_owner_S_default',
            'n_array_S_true = n_array_S_default', 'n_ref_S_true = n_ref_S_default',
            *leaf('S_true', 'n_ref_S_true', 'runtime-owned-array82', True), *returned('S_true', 1, '9', 'true'),
            *leaf('S_true_return', 'n_ref_S_true', 'true-array82'), *current('S_true_return', 'n_array_S_true', 'n_ref_S_true', [43]),
            *error('S_true', 'S_true_resume', explicit=True),
            'S_written_found = $test_ini_alias_leaf_seek(S_true_error,n_ref_S_true,' + text('after-error82') + ',3000)',
            r'S_written_found.COMPLETION = NORMAL \/ S_written_found.COMPLETION = BUDGET',
            'S_written = S_written_found[.COMPLETION = NORMAL]', '$test_ini_alias_leaf(S_written,n_ref_S_true,' + text('after-error82') + ')',
            *shape('S_written', 'n_array_S_true', 'n_ref_S_true'), *leaf('S_written', 'n_ref_S_true', 'after-error82'),
            *current('S_written', 'n_array_S_true', 'n_ref_S_true', [43]),
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
            *refusals('S_true'), *budget('S_default'), *budget('S_true_resume'), *budget('S_written'),
            *recovery('S_written', 'n_owner_S_default', '9'),
            '$test_outputs(S_final.EVENTS) = ' + text('B|' + VALUE_ERROR + '|99|T|H|8192|' + MESSAGE + '|' + VALUE_ERROR + '|E|W|N|L|L|A|43|99|1|Z|R|9|11')]
    else:
        strict = name == 'strict-owned-null-alias-array-then-same-owner-explicit-weak-reception'
        assert strict or name == 'captured-owned-null-alias-array-before-live-owner-and-cell-writes'
        values += [*partial(), *front('S', 'S_pre'), 'n_owner_S = n_owner_pre', 'n_array_S = n_captured', 'n_ref_S = n_ref_captured',
            'pconfigcall_S = pconfigcall_pre[.INDEX = 2][.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (PARRAY n_captured))]]',
            'S.STORE[n_call] = DEFINED (POBJECT n_replacement)', 'S.STORE[n_keep] = DEFINED (POBJECT n_owner_pre)',
            'S.STORE[n_old] = DEFINED (PARRAY n_captured)', 'S.STORE[n_value] = DEFINED (PINT 0)',
            'S.STORE[n_option] = DEFINED pvalue_option', '$string_bytes(pvalue_option) = (' + text('precision') + ')',
            'S.STORE[n_effects] = DEFINED (PINT 1)', 'S.STORE[n_warnings] = DEFINED (PINT 0)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            *current('S', 'n_captured', 'n_ref_captured', [31]), '$test_outputs(S.EVENTS) = ' + text('B|V|')]
        if strict:
            values += [*leaf('S', 'n_ref_captured', 'strict-array82'), 'S.PRECISIONINI = ' + text('9'),
                '$exit_strict(S,pconfigcall_S.SITE)', '$config_strict(S,pconfigcall_S)', '~$config_ini_null_valid(S,pconfigcall_S)',
                *error('S', 'S', strict=True), *front('S_weak', 'S_error', True),
                'n_owner_S_weak = n_owner_pre', 'n_array_S_weak = n_captured', 'n_ref_S_weak = n_ref_captured',
                '$exit_strict(S_weak,pconfigcall_S_weak.SITE)', '~$config_strict(S_weak,pconfigcall_S_weak)',
                *leaf('S_weak', 'n_ref_captured', 'strict-array82'), *returned('S_weak', 1, '9', 'true'),
                *leaf('S_weak_return', 'n_ref_captured', 'weak-array82'),
                *current('S_weak_return', 'n_captured', 'n_ref_captured', [31]), *error('S_weak', 'S_weak_resume', explicit=True),
                *budget('S_pre'), *budget('S'), *budget('S_weak_resume'), *recovery('S_weak_error', 'n_owner_pre', '9', True),
                '$test_outputs(S_final.EVENTS) = ' + text('B|V|' + OPTION_ERROR + '|99|1|0|strict-array82|31|A|0|9|E|H|8192|' + MESSAGE + '|' + VALUE_ERROR + '|99|1|weak-array82|weak-array82|31|Z|R|9|11')]
        else:
            values += [*leaf('S', 'n_ref_captured', 'value-array82'), 'S.PRECISIONINI = ' + text('7'),
                '~$config_strict(S,pconfigcall_S)', *returned('S', 1, '8', 'false'),
                *leaf('S_return', 'n_ref_captured', 'handler-array82'), *current('S_return', 'n_captured', 'n_ref_captured', [31, 37]),
                'S_return.STORE[n_old] = DEFINED (PARRAY n_captured)', 'S_return.STORE[n_keep] = DEFINED (POBJECT n_owner_pre)',
                '$heap_count(HOBJECT n_owner_pre,$tasks_nodes(S_return.TODO)) = 1',
                '$heap_count(HARRAY n_captured,$tasks_nodes(S_return.TODO)) = 1',
                *error('S', 'S_resume'), *refusals('S'), *budget('S_pre'), *budget('S_resume'),
                *recovery('S_error', 'n_owner_pre', '8'),
                '$test_outputs(S_final.EVENTS) = ' + text('B|V|W|8192|' + MESSAGE + '|' + VALUE_ERROR + '|99|1|1|handler-array82|handler-array82|31|37|A|constant|precision|handler-value82|8|Z|R|8|11')]
    return values + ['S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.ERRORHANDLER.CALLBACK = eps', 'S_final.USERCONSTANTS = eps', *common.public('S_final')]


def main():
    fingerprint = sources.family.fingerprint
    dependencies = (Path(__file__), Path(shared.__file__), Path(shared.shared.__file__), Path(shared.shared.shared.__file__),
        Path(owner.__file__), Path(owner.shared.__file__), Path(owner.shared.shared.__file__), Path(sources.__file__))
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(path.relative_to(driver.ROOT)): sources.family.sha(path) for path in dependencies})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
