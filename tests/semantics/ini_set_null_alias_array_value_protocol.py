#!/usr/bin/env python3
"""A captured array keeps its container and shares the live primitive ref cell."""
import json
import os
from pathlib import Path

import ini_set_null_array_value_protocol as shared
import ini_set_unpack_null_stdclass_value_protocol as recovery_base
import ini_set_null_alias_array_value_sources as sources

driver, common, text, b64 = shared.driver, shared.common, shared.text, shared.b64
MESSAGE, VALUE_ERROR, OPTION_ERROR = shared.MESSAGE, shared.VALUE_ERROR, shared.OPTION_ERROR
reach, returned, budget, unchanged = shared.reach, shared.returned, shared.budget, shared.unchanged
PREFIX = shared.PREFIX + r"""
dec $test_ini_alias_leaf(pstate, nat, preqbytes) : bool
def $test_ini_alias_leaf(S, n_cell, n_leaf*) = true
  -- if $(n_cell < |S.STORE|)
  -- if S.STORE[n_cell] = DEFINED pvalue
  -- if $string_bytes(pvalue) = (n_leaf*)
def $test_ini_alias_leaf(S, n_cell, n_leaf*) = false -- otherwise
dec $test_ini_alias_leaf_seek(pstate, nat, preqbytes, nat) : pstate
def $test_ini_alias_leaf_seek(S, n_cell, n_leaf*, 0) = S
def $test_ini_alias_leaf_seek(S, n_cell, n_leaf*, n) = S
  -- if $(n > 0)
  -- if $test_ini_alias_leaf(S,n_cell,n_leaf*) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_ini_alias_leaf_seek(S, n_cell, n_leaf*, n) = $test_ini_alias_leaf_seek($drive_steps($test_running(S),1),n_cell,n_leaf*,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_ini_alias_leaf(S,n_cell,n_leaf*)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def shape(state, array, cell):
    return [state + '.ARRAYS[' + array + '].ITEMS = [ENTRY (KINT 0) (ALIAS ' + cell + ')]',
        '$node_children(' + state + ',HARRAY ' + array + ') = [HCELL ' + cell + ']',
        '$call_reference_operand_valid(' + state + ',REFERENCE ' + cell + ')',
        '(HCELL ' + cell + ') <- ' + state + '.ALLOCATIONS', cell + ' <- ' + state + '.REFCELLS',
        '$node_children(' + state + ',HCELL ' + cell + ') = eps',
        '$propref_at(' + state + '.PROPREFS,' + cell + ') = eps',
        '$reference_coercion_at(' + state + '.REFCOERCIONS,' + cell + ') = eps',
        state + '.PARAMETERBACKINGS = eps']


def leaf(state, cell, spelling, request=False):
    value = 'PSTRING_CARRIER ' + ('(REQUEST_STRING n_string_' + state + ')' if request else 'INTERNED_STRING') + ' ' + text(spelling)
    return [state + '.STORE[' + cell + '] = DEFINED (' + value + ')', '$string_carrier_valid(' + state + ',' + value + ')']


def current(state, original, cell, extras):
    array = 'n_current_' + state
    entries = '[ENTRY (KINT 0) (ALIAS ' + cell + ')' + ''.join(
        ',ENTRY (KINT ' + str(i) + ') (DIRECT (PINT ' + str(n) + '))' for i, n in enumerate(extras, 1)) + ']'
    return ['$lookup(' + state + '.ENV,' + text('arrayKeep') + ') = (n_keep_' + state + ')',
        state + '.STORE[n_keep_' + state + '] = DEFINED (PARRAY ' + array + ')', array + ' =/= ' + original,
        state + '.ARRAYS[' + array + '].ITEMS = ' + entries,
        '$node_children(' + state + ',HARRAY ' + array + ') = [HCELL ' + cell + ']']


def front(state, start, selected):
    call, array, cell = 'pconfigcall_' + state, 'n_array_' + state, 'n_ref_' + state
    values = shared.front(state, start)
    old = '$config_ini_rejected_array(' + state + ',' + array + ')'
    assert values.count(old) == 1
    values[values.index(old)] = '$config_ini_rejected_alias_array(' + state + ',' + array + ')'
    old = '$node_children(' + state + ',HARRAY ' + array + ') = eps'
    assert values.count(old) == 1
    values.remove(old)
    old = '$config_ini_pack_known(' + state + ',' + state + '.ARRAYS[' + array + '].ITEMS,$compiled_read(' + state + ',porigin_value_' + state + '))'
    assert values.count(old) == 1
    values[values.index(old)] = '$compiled_read(' + state + ',porigin_value_' + state + ') = eps'
    values += [*shape(state, array, cell), '~$config_ini_rejected_array(' + state + ',' + array + ')',
        '~$config_method_receiver(' + state + ',' + call + ')']
    if selected:
        values += [call + '.SELECTION = (n_selection_' + state + ')',
            state + '.SELECTEDCALLS[n_selection_' + state + '].OWNER = eps',
            state + '.SELECTEDCALLS[n_selection_' + state + '].KIND = INTRINSIC_INI_SET',
            state + '.SELECTEDCALLS[n_selection_' + state + '].SITE = ' + call + '.SITE',
            state + '.SELECTEDCALLS[n_selection_' + state + '].LINE = ' + call + '.LINE']
    else:
        values += [call + '.SELECTION = eps']
    return values


def error(state, start, strict=False, default=False):
    values = shared.error(state, start, 'unused81', strict=strict, default=default)
    old = state + '_error.ARRAYS[n_trace_' + state + '].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_api_' + state + ')),ENTRY (KINT 1) (DIRECT (PARRAY n_caller_' + state + '))]'
    assert values.count(old) == 1
    values[values.index(old)] = state + '_error.ARRAYS[n_trace_' + state + '].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_api_' + state + '))]'
    old = '$trace_array_field(' + state + '_error,n_caller_' + state + ',' + text('function') + ') = PSTRING ' + text('unused81')
    assert values.count(old) == 1
    values.remove(old)
    return values + [*shape(state + '_error', 'n_array_' + state, 'n_ref_' + state)]


def refusals(state):
    call, array, cell = 'pconfigcall_' + state, 'n_array_' + state, 'n_ref_' + state
    values = []
    for field in ('.SITE = PORIGIN 0 eps', '.LINE = $(' + call + '.LINE + 1)', '.INDEX = 1', '.NAMED = true',
            '.OWNER = (0)', '.KIND = INTRINSIC_INI_GET', '.SELECTION = (|' + state + '.SELECTEDCALLS|)',
            '.SENT = ' + call + '.SENT[0:1]'):
        values += ['~$config_ini_null_valid(' + state + ',' + call + '[' + field + '])']
    values += ['~$config_ini_null_valid(' + state + '[.CODE = eps],' + call + ')',
        '~$config_ini_rejected_alias_array(' + state + ',|' + state + '.ARRAYS|)',
        '~$config_ini_rejected_alias_array(' + state + '[.ALLOCATIONS = eps],' + array + ')',
        '~$config_ini_rejected_alias_array(' + state + '[.REFCELLS = eps],' + array + ')',
        '~$config_ini_rejected_alias_array(' + state + '[.STORE[' + cell + '] = UNDEFINED],' + array + ')',
        '~$config_ini_rejected_alias_array(' + state + '[.PROPREFS = [{CELL ' + cell + ',SOURCES eps}]],' + array + ')',
        '~$config_ini_rejected_alias_array(' + state + '[.REFCOERCIONS = [{CELL ' + cell + ',SITE ' + call + '.SITE,LINE ' + call + '.LINE,VALUE ' + text('bad81') + '}]],' + array + ')',
        '~$config_ini_rejected_alias_array(' + state + '[.PARAMETERBACKINGS = [{FUNCTION ' + call + '.SITE,INDEX 0,CELL ' + cell + ',LINE ' + call + '.LINE,VALUE ' + text('bad81') + '}]],' + array + ')']
    for value in ('PARRAY ' + array, 'POBJECT 0', 'PUNDEFINED', 'PFLOAT 9221120237041090560',
            'PSTRING ' + text('legacy81'), 'PSTRING_CARRIER (REQUEST_STRING (|' + state + '.STRINGDATA|)) ' + text('bad81')):
        values += ['~$config_ini_rejected_alias_array(' + state + '[.STORE[' + cell + '] = DEFINED (' + value + ')],' + array + ')']
    for entries in ('eps', '[ENTRY (KINT 1) (ALIAS ' + cell + ')]', '[ENTRY (KINT 0) (ALIAS (|' + state + '.STORE|))]'):
        values += ['~$config_ini_rejected_alias_array(' + state + '[.ARRAYS[' + array + '].ITEMS = ' + entries + '],' + array + ')']
    values += ['~$config_ini_rejected_alias_array(' + state + '[.ARRAYS[' + array + '].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]],' + array + ')',
        '$config_ini_rejected_array(' + state + '[.ARRAYS[' + array + '].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1))]],' + array + ')',
        '$config_ini_rejected_alias_array(' + state + '[.STORE[' + cell + '] = DEFINED (PINT 1)],' + array + ')']
    return values


def recovery(start, precision, strict=False):
    return [*recovery_base.recovery(start, precision, strict), 'S_recovery.SELECTEDCALLS[n_selection_recovery].OWNER = eps',
        'S_final = $drive_steps(S_recovered,3000)', 'S_final.COMPLETION = NORMAL']


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')', 'S_initial.COMPLETION = BUDGET']
    if name == 'null-alias-array-default-and-returned-trace-sees-later-cell-write':
        values += [*front('S_default', 'S_initial', False), *leaf('S_default', 'n_ref_S_default', 'runtime-array81', True),
            '$compiled_read(S_default,porigin_option_S_default) = (PNULL)', '$config_ini_null_valid(S_default,pconfigcall_S_default)',
            '~$error_handler_eligible(S_default,8192)', *error('S_default', 'S_default', default=True),
            *front('S_true', 'S_default_error', True), 'n_array_S_true = n_array_S_default', 'n_ref_S_true = n_ref_S_default',
            *leaf('S_true', 'n_ref_S_true', 'runtime-array81', True), *returned('S_true', 1, '9', 'true'),
            *leaf('S_true_return', 'n_ref_S_true', 'true-array81'), *current('S_true_return', 'n_array_S_true', 'n_ref_S_true', [41]),
            *error('S_true', 'S_true_resume'),
            'S_written_found = $test_ini_alias_leaf_seek(S_true_error,n_ref_S_true,' + text('after-error81') + ',3000)',
            r'S_written_found.COMPLETION = NORMAL \/ S_written_found.COMPLETION = BUDGET',
            'S_written = S_written_found[.COMPLETION = NORMAL]', '$test_ini_alias_leaf(S_written,n_ref_S_true,' + text('after-error81') + ')',
            *shape('S_written', 'n_array_S_true', 'n_ref_S_true'), *leaf('S_written', 'n_ref_S_true', 'after-error81'),
            *current('S_written', 'n_array_S_true', 'n_ref_S_true', [41]),
            '$throwable_field(S_written,n_error_S_true,"trace") = PARRAY n_trace_S_true',
            'S_written.ARRAYS[n_args_S_true].ITEMS = [ENTRY (KINT 0) (DIRECT (PSTRING eps)),ENTRY (KINT 1) (DIRECT (PARRAY n_array_S_true))]',
            '$lookup(S_written.ENV,' + text('trace') + ') = (n_observed_trace_cell)',
            'S_written.STORE[n_observed_trace_cell] = DEFINED (PARRAY n_observed_trace)',
            'S_written.ARRAYS[n_observed_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_observed_api))]',
            '$trace_array_field(S_written,n_observed_api,' + text('args') + ') = PARRAY n_observed_args',
            'S_written.ARRAYS[n_observed_args].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_observed_option),ENTRY (KINT 1) (DIRECT (PARRAY n_observed_value))]',
            '$string_bytes(pvalue_observed_option) = (eps)', *shape('S_written', 'n_observed_value', 'n_ref_S_true')[:2],
            '(HARRAY n_observed_value) <- S_written.ALLOCATIONS',
            *refusals('S_true'), *budget('S_default'), *budget('S_true_resume'), *budget('S_written'),
            *recovery('S_written', '9'), '$test_outputs(S_final.EVENTS) = ' + text('B|' + VALUE_ERROR + '|99|T|H|8192|' + MESSAGE + '|' + VALUE_ERROR + '|E|L|A|after-error81|after-error81|41|99|1|0|Z|R|9|11')]
    else:
        strict = name == 'strict-null-alias-array-rejects-option-after-shared-cell-and-container-effects'
        assert strict or name == 'captured-null-alias-array-before-reference-write-and-live-value-rebinding'
        values += ['S_pre_found = $test_ini_array_partial_seek(S_initial,3000)',
            r'S_pre_found.COMPLETION = NORMAL \/ S_pre_found.COMPLETION = BUDGET',
            'S_pre = S_pre_found[.COMPLETION = NORMAL]', '$test_ini_array_partial(S_pre)',
            'S_pre.TODO = (CONFIG_ARGS pconfigcall_pre) :: ptask_pre*', 'pconfigcall_pre.SELECTION = (n_selection)',
            'pconfigcall_pre.PACKS = eps', '~pconfigcall_pre.NAMED', '$config_pending_valid(S_pre,pconfigcall_pre,false)',
            '$call_task_valid(S_pre,CONFIG_ARGS pconfigcall_pre)', '$config_nodes(pconfigcall_pre) = eps',
            '$lookup(S_pre.ENV,' + text('value') + ') = (n_value)', 'S_pre.STORE[n_value] = DEFINED (PARRAY n_captured)',
            '$lookup(S_pre.ENV,' + text('arrayKeep') + ') = (n_keep)', 'S_pre.STORE[n_keep] = DEFINED (PARRAY n_captured)',
            '$lookup(S_pre.ENV,' + text('old') + ') = (n_old)', 'S_pre.STORE[n_old] = DEFINED (PARRAY n_captured)',
            *shape('S_pre', 'n_captured', 'n_ref_captured'), *leaf('S_pre', 'n_ref_captured', 'runtime-array81', True),
            '$lookup(S_pre.ENV,' + text('leaf') + ') = (n_ref_captured)', '$config_ini_rejected_alias_array(S_pre,n_captured)',
            '$lookup(S_pre.ENV,' + text('result') + ') = (n_result)', 'S_pre.STORE[n_result] = DEFINED (PINT 99)',
            '$lookup(S_pre.ENV,' + text('effects') + ') = (n_effects)', 'S_pre.STORE[n_effects] = DEFINED (PINT 0)',
            '$test_outputs(S_pre.EVENTS) = ' + text('B|'), *common.public('S_pre'), *front('S', 'S_pre', True),
            'pconfigcall_S = pconfigcall_pre[.INDEX = 2][.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (PARRAY n_captured))]]',
            'n_array_S = n_captured', 'n_ref_S = n_ref_captured', 'n_selection_S = n_selection',
            'S.SELECTEDCALLS[n_selection] = S_pre.SELECTEDCALLS[n_selection]',
            'S.STORE[n_value] = DEFINED (PINT 0)', 'S.STORE[n_old] = DEFINED (PARRAY n_captured)',
            'S.STORE[n_effects] = DEFINED (PINT 1)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            *current('S', 'n_captured', 'n_ref_captured', [31]), '$test_outputs(S.EVENTS) = ' + text('B|V|')]
        if strict:
            values += [*leaf('S', 'n_ref_captured', 'strict-array81'), '$config_strict(S,pconfigcall_S)',
                '~$config_ini_null_valid(S,pconfigcall_S)', 'S.PRECISIONINI = ' + text('9'), *error('S', 'S', strict=True),
                *budget('S_pre'), *budget('S'), *recovery('S_error', '9', True),
                '$test_outputs(S_final.EVENTS) = ' + text('B|V|' + OPTION_ERROR + '|99|1|0|strict-array81|31|A|0|9|Z|R|9|11')]
        else:
            values += [*leaf('S', 'n_ref_captured', 'value-array81'), '~$config_strict(S,pconfigcall_S)',
                'S.PRECISIONINI = ' + text('7'), *returned('S', 1, '8', 'false'),
                *leaf('S_return', 'n_ref_captured', 'handler-array81'), *current('S_return', 'n_captured', 'n_ref_captured', [31, 37]),
                'S_return.STORE[n_old] = DEFINED (PARRAY n_captured)',
                '$heap_count(HARRAY n_captured,$tasks_nodes(S_return.TODO)) = 1',
                *error('S', 'S_resume'), *refusals('S'), *budget('S_pre'), *budget('S_resume'),
                *recovery('S_error', '8'), '$test_outputs(S_final.EVENTS) = ' + text('B|V|W|8192|' + MESSAGE + '|' + VALUE_ERROR + '|99|1|1|handler-array81|handler-array81|31|37|A|constant|precision|handler-value81|8|Z|R|8|11')]
    return values + ['S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.ERRORHANDLER.CALLBACK = eps', 'S_final.USERCONSTANTS = eps', *common.public('S_final')]


def main():
    fingerprint = sources.family.fingerprint
    dependencies = (Path(__file__), Path(shared.__file__), Path(shared.shared.__file__), Path(recovery_base.__file__),
        Path(recovery_base.shared.__file__), Path(recovery_base.shared.shared.__file__), Path(recovery_base.shared.shared.shared.__file__), Path(sources.__file__))
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(path.relative_to(driver.ROOT)): sources.family.sha(path) for path in dependencies})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
