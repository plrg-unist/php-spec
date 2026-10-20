#!/usr/bin/env python3
"""Named array reception retains the intrinsic owner and earlier array value."""
import json
import os
from pathlib import Path

import ini_set_named_null_array_value_protocol as shared
import ini_set_owned_named_null_array_value_sources as sources

driver, common, text, b64 = shared.driver, shared.common, shared.text, shared.b64
MESSAGE, VALUE_ERROR, OPTION_ERROR = shared.MESSAGE, shared.VALUE_ERROR, shared.OPTION_ERROR
reach, returned, budget, written = shared.reach, shared.returned, shared.budget, shared.written
unchanged = shared.shared.unchanged
PREFIX = shared.shared.shared.PREFIX + r"""
dec $test_ini_owned_named_array_partial(pstate) : bool
def $test_ini_owned_named_array_partial(S) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.OWNER = (n_owner)
  -- if pconfigcall.INDEX = 1 /\ pconfigcall.NAMED
  -- if pconfigcall.SENT = [NAMED_HOLE,NAMED_SENT (KNOWN (PARRAY n_array))]
def $test_ini_owned_named_array_partial(S) = false -- otherwise
dec $test_ini_owned_named_array_partial_seek(pstate, nat) : pstate
def $test_ini_owned_named_array_partial_seek(S, 0) = S
def $test_ini_owned_named_array_partial_seek(S, n) = S
  -- if $(n > 0)
  -- if $test_ini_owned_named_array_partial(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_ini_owned_named_array_partial_seek(S, n) = $test_ini_owned_named_array_partial_seek($drive_steps($test_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_ini_owned_named_array_partial(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def front(state, start, mixed=False):
    call, owner, array = 'pconfigcall_' + state, 'n_owner_' + state, 'n_array_' + state
    return [*reach(state, start, 0), state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
        call + '.KIND = INTRINSIC_INI_SET', call + '.OWNER = (' + owner + ')', call + '.SELECTION = eps',
        call + '.PACKS = eps', call + '.INDEX = 2', call + '.NAMED',
        call + '.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (PARRAY ' + array + '))]',
        state + '.OBJECTS[' + owner + '] = INTRINSICCLOSURE INTRINSIC_INI_SET',
        '(HOBJECT ' + owner + ') <- ' + state + '.ALLOCATIONS', '$getclass_live_object(' + state + ',' + owner + ')',
        '$config_invoke_valid(' + state + ',' + call + ')', '$config_selected_valid(' + state + ',' + call + ')',
        '$config_ini_rejected_array(' + state + ',' + array + ')',
        '$config_nodes(' + call + ') = [HOBJECT ' + owner + ',HARRAY ' + array + ']',
        '$task_nodes(CONFIG_INI_NULL_RESULT ' + call + ') = [HOBJECT ' + owner + ',HARRAY ' + array + ']',
        '$node_children(' + state + ',HARRAY ' + array + ') = eps',
        state + '.CURRENT = eps', state + '.FRAMES = eps', *written(state, mixed), *common.public(state)]


def error(state, start, explicit=False, strict=False):
    call, owner, array, out = 'pconfigcall_' + state, 'n_owner_' + state, 'n_array_' + state, state + '_error'
    option = 'PNULL' if strict else 'PSTRING eps'
    frames = '[ENTRY (KINT 0) (DIRECT (PARRAY n_api_' + state + '))' + (
        ',ENTRY (KINT 1) (DIRECT (PARRAY n_wrapper_' + state + '))' if explicit else '') + ']'
    values = [*common.step(out, start), out + '.TODO = (THROW_SEARCH n_error_' + state + ') :: ptask_' + state + '*',
        out + '.OBJECTS[n_error_' + state + '] = THROWABLE pthrowable_' + state,
        'pthrowable_' + state + '.KIND = "TypeError"', 'pthrowable_' + state + '.ORIGIN = (' + call + '.SITE)',
        '$string_bytes($throwable_field(' + out + ',n_error_' + state + ',"message")) = (' + text(OPTION_ERROR if strict else VALUE_ERROR) + ')',
        '$throwable_field(' + out + ',n_error_' + state + ',"previous") = PNULL',
        '$throwable_field(' + out + ',n_error_' + state + ',"line") = PINT ' + call + '.LINE',
        '$throwable_field(' + out + ',n_error_' + state + ',"trace") = PARRAY n_trace_' + state,
        out + '.ARRAYS[n_trace_' + state + '].ITEMS = ' + frames,
        '$trace_array_field(' + out + ',n_api_' + state + ',' + text('function') + ') = PSTRING ' + text('ini_set'),
        '$trace_array_field(' + out + ',n_api_' + state + ',' + text('args') + ') = PARRAY n_args_' + state,
        out + '.ARRAYS[n_args_' + state + '].ITEMS = [ENTRY (KINT 0) (DIRECT (' + option + ')),ENTRY (KINT 1) (DIRECT (PARRAY ' + array + '))]',
        '$node_children(' + out + ',HARRAY n_args_' + state + ') = [HARRAY ' + array + ']',
        out + '.ARRAYS[' + array + '].ITEMS = ' + start + '.ARRAYS[' + array + '].ITEMS',
        '(HARRAY ' + array + ') <- ' + out + '.ALLOCATIONS',
        out + '.OBJECTS[' + owner + '] = INTRINSICCLOSURE INTRINSIC_INI_SET',
        '(HOBJECT ' + owner + ') <- ' + out + '.ALLOCATIONS',
        out + '.EVENTS = ' + start + '.EVENTS',
        *unchanged(out, start, 'STORE ENV ERRORHANDLER USERCONSTANTS SELECTEDCALLS PRECISIONINI')]
    if explicit:
        values += ['$trace_array_field(' + out + ',n_wrapper_' + state + ',' + text('function') + ') = PSTRING ' + text('__invoke'),
            '$trace_array_field(' + out + ',n_wrapper_' + state + ',' + text('class') + ') = PSTRING ' + text('Closure'),
            '$trace_array_field(' + out + ',n_wrapper_' + state + ',' + text('type') + ') = PSTRING ' + text('->'),
            '$trace_array_field(' + out + ',n_wrapper_' + state + ',' + text('args') + ') = PARRAY n_wrapper_args_' + state,
            out + '.ARRAYS[n_wrapper_args_' + state + '].ITEMS = [ENTRY (KINT 0) (DIRECT PNULL),ENTRY (KINT 1) (DIRECT (PARRAY ' + array + '))]',
            '$node_children(' + out + ',HARRAY n_wrapper_args_' + state + ') = [HARRAY ' + array + ']']
    return values + common.public(out)


def refusals(state):
    call, owner = 'pconfigcall_' + state, 'n_owner_' + state
    return [*[v for v in shared.refusals(state) if '.OWNER = (0)' not in v],
        '~$config_ini_null_valid(' + state + ',' + call + '[.OWNER = eps])',
        '~$config_ini_null_valid(' + state + ',' + call + '[.OWNER = (|' + state + '.OBJECTS|)])',
        '~$config_ini_null_valid(' + state + '[.OBJECTS[' + owner + '] = INTRINSICCLOSURE INTRINSIC_INI_GET],' + call + ')',
        '~$config_ini_null_valid(' + state + '[.ALLOCATIONS = eps],' + call + ')']


def recovery(start, owner, old_precision):
    return [*reach('S_recovery', start, 3),
        'S_recovery.TODO = (CONFIG_INVOKE pconfigcall_recovery) :: ptask_recovery*',
        'pconfigcall_recovery.OWNER = (' + owner + ')', 'pconfigcall_recovery.SELECTION = eps',
        'pconfigcall_recovery.INDEX = 2', 'pconfigcall_recovery.NAMED', 'pconfigcall_recovery.PACKS = eps',
        'pconfigcall_recovery.SENT = [NAMED_SENT (KNOWN pvalue_precision),NAMED_SENT (KNOWN pvalue_new_precision)]',
        '$string_bytes(pvalue_precision) = (' + text('precision') + ')',
        '$string_bytes(pvalue_new_precision) = (' + text('11') + ')',
        '$config_invoke_valid(S_recovery,pconfigcall_recovery)',
        '~$config_method_receiver(S_recovery,pconfigcall_recovery)',
        'S_recovery.OBJECTS[' + owner + '] = INTRINSICCLOSURE INTRINSIC_INI_SET',
        '$config_nodes(pconfigcall_recovery) = [HOBJECT ' + owner + ']',
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
    if name == 'owned-named-array-values-return-through-api-and-wrapper-frames':
        values += [*front('S_explicit', 'S_initial'), '$config_method_receiver(S_explicit,pconfigcall_S_explicit)',
            '~$config_strict(S_explicit,pconfigcall_S_explicit)',
            'S_explicit.ARRAYS[n_array_S_explicit].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 2617))]',
            '$compiled_read(S_explicit,porigin_S_explicit_0) = (PARRAY n_known)',
            '$compiled_read(S_explicit,porigin_S_explicit_1) = (PNULL)',
            '$($heap_count(HARRAY n_known,$pools_nodes(S_explicit.POOLS)) > 0)',
            *returned('S_explicit', 1, '14', 'true'), *error('S_explicit', 'S_explicit_resume', explicit=True),
            *front('S_mixed', 'S_explicit_error', mixed=True), 'n_owner_S_mixed = n_owner_S_explicit',
            '~$config_method_receiver(S_mixed,pconfigcall_S_mixed)',
            'S_mixed.ARRAYS[n_array_S_mixed].ITEMS = eps',
            '$compiled_read(S_mixed,porigin_S_mixed_0) = (PNULL)',
            '$compiled_read(S_mixed,porigin_S_mixed_1) = (PARRAY n_empty)',
            *returned('S_mixed', 2, '14', 'true'), *error('S_mixed', 'S_mixed_resume'),
            'S_forged = $allocate_array(S_explicit,$array_insert($array_empty(),KINT 0,DIRECT (PINT 2618)))',
            'S_forged.RESULT = KNOWN (PARRAY n_forged)',
            'pconfigcall_forged = pconfigcall_S_explicit[.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (PARRAY n_forged))]]',
            '$config_invoke_valid(S_forged,pconfigcall_forged)', '$config_ini_rejected_array(S_forged,n_forged)',
            '~$config_ini_named_array_argument(S_forged,pconfigcall_forged,n_forged,0)',
            '$config_ini_named_array_argument(S_forged,pconfigcall_forged,n_forged,1)',
            '~$config_ini_null_valid(S_forged,pconfigcall_forged)',
            *refusals('S_explicit'), *budget('S_explicit'), *budget('S_mixed_resume'),
            *recovery('S_mixed_error', 'n_owner_S_explicit', '14'),
            'S_final = $drive_steps(S_recovered,3000)', 'S_final.COMPLETION = NORMAL',
            '$test_outputs(S_final.EVENTS) = ' + text('B|H|8192|' + MESSAGE + '|' + VALUE_ERROR + '|E|W|N|2617|2617|99|1|M|H|8192|' + MESSAGE + '|' + VALUE_ERROR + '|99|2|Z|R|14|11')]
    else:
        strict = name == 'strict-owned-named-array-option-before-weak-explicit-value-error'
        assert strict or name == 'captured-owned-named-array-before-live-owner-replacement-and-cow'
        values += ['S_pre_found = $test_ini_owned_named_array_partial_seek(S_initial,3000)',
            r'S_pre_found.COMPLETION = NORMAL \/ S_pre_found.COMPLETION = BUDGET',
            'S_pre = S_pre_found[.COMPLETION = NORMAL]', '$test_ini_owned_named_array_partial(S_pre)',
            'S_pre.TODO = (CONFIG_ARGS pconfigcall_pre) :: ptask_pre*',
            'pconfigcall_pre.OWNER = (n_owner_pre)', 'pconfigcall_pre.SELECTION = eps',
            'pconfigcall_pre.PACKS = eps', 'pconfigcall_pre.INDEX = 1', 'pconfigcall_pre.NAMED',
            'pconfigcall_pre.SENT = [NAMED_HOLE,NAMED_SENT (KNOWN (PARRAY n_captured))]',
            '$config_pending_valid(S_pre,pconfigcall_pre,false)', '$call_task_valid(S_pre,CONFIG_ARGS pconfigcall_pre)',
            '$config_nodes(pconfigcall_pre) = [HOBJECT n_owner_pre,HARRAY n_captured]',
            '$task_nodes(CONFIG_ARGS pconfigcall_pre) = [HOBJECT n_owner_pre,HARRAY n_captured]',
            'S_pre.OBJECTS[n_owner_pre] = INTRINSICCLOSURE INTRINSIC_INI_SET',
            '$lookup(S_pre.ENV,' + text('call') + ') = (n_call)', 'S_pre.STORE[n_call] = DEFINED (POBJECT n_owner_pre)',
            '$lookup(S_pre.ENV,' + text('keep') + ') = (n_keep)', 'S_pre.STORE[n_keep] = DEFINED (POBJECT n_owner_pre)',
            '$lookup(S_pre.ENV,' + text('replacement') + ') = (n_replacement)',
            'S_pre.STORE[n_replacement] = DEFINED (POBJECT n_live)',
            'S_pre.OBJECTS[n_live] = INTRINSICCLOSURE INTRINSIC_INI_GET', 'n_live =/= n_owner_pre',
            '$lookup(S_pre.ENV,' + text('arrayKeep') + ') = (n_array_keep)',
            'S_pre.STORE[n_array_keep] = DEFINED (PARRAY n_captured)',
            '$lookup(S_pre.ENV,' + text('old') + ') = (n_old)', 'S_pre.STORE[n_old] = DEFINED (PARRAY n_captured)',
            '$lookup(S_pre.ENV,' + text('value') + ') = (n_value)', 'S_pre.STORE[n_value] = DEFINED (PARRAY n_captured)',
            '$lookup(S_pre.ENV,' + text('effects') + ') = (n_effects)', 'S_pre.STORE[n_effects] = DEFINED (PINT 0)',
            '$lookup(S_pre.ENV,' + text('warnings') + ') = (n_warnings)', 'S_pre.STORE[n_warnings] = DEFINED (PINT 0)',
            '$lookup(S_pre.ENV,' + text('result') + ') = (n_result)', 'S_pre.STORE[n_result] = DEFINED (PINT 99)',
            'S_pre.PRECISIONINI = ' + text('14'), '$test_outputs(S_pre.EVENTS) = ' + text('B|'), *common.public('S_pre'),
            *front('S', 'S_pre'), 'n_owner_S = n_owner_pre', 'n_array_S = n_captured',
            'pconfigcall_S = pconfigcall_pre[.INDEX = 2][.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (PARRAY n_captured))]]',
            '$compiled_read(S,porigin_S_0) = eps', '$compiled_read(S,porigin_S_1) = eps',
            'S.STORE[n_call] = DEFINED (POBJECT n_live)', 'S.STORE[n_keep] = DEFINED (POBJECT n_owner_pre)',
            'S.OBJECTS[n_live] = INTRINSICCLOSURE INTRINSIC_INI_GET',
            'S.STORE[n_value] = DEFINED (PINT 0)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            'S.STORE[n_effects] = DEFINED (PINT 1)', 'S.STORE[n_warnings] = DEFINED (PINT 0)',
            'S.STORE[n_old] = DEFINED (PARRAY n_captured)',
            'S.STORE[n_array_keep] = DEFINED (PARRAY n_after_option)', 'n_after_option =/= n_captured',
            'S.ARRAYS[n_captured].ITEMS = S_pre.ARRAYS[n_captured].ITEMS',
            '$heap_count(HARRAY n_captured,$tasks_nodes(S.TODO)) = 1',
            '$heap_count(HOBJECT n_owner_pre,$tasks_nodes(S.TODO)) = 1',
            '~$config_method_receiver(S,pconfigcall_S)', '$test_outputs(S.EVENTS) = ' + text('B|O|')]
        if strict:
            values += ['S_pre.ARRAYS[n_captured].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 2633))]',
                'S.ARRAYS[n_after_option].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 0))]',
                '$exit_strict(S,pconfigcall_S.SITE)', '$config_strict(S,pconfigcall_S)',
                '~$config_ini_null_valid(S,pconfigcall_S)', 'S.PRECISIONINI = ' + text('9'),
                *error('S', 'S', strict=True), *front('S_wrapper', 'S_error', mixed=True),
                'n_owner_S_wrapper = n_owner_pre',
                'S_wrapper.ARRAYS[n_array_S_wrapper].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 2641))]',
                '$config_method_receiver(S_wrapper,pconfigcall_S_wrapper)',
                '$exit_strict(S_wrapper,pconfigcall_S_wrapper.SITE)', '~$config_strict(S_wrapper,pconfigcall_S_wrapper)',
                '$compiled_read(S_wrapper,porigin_S_wrapper_0) = (PNULL)',
                '$compiled_read(S_wrapper,porigin_S_wrapper_1) = (PARRAY n_known_wrapper)',
                *returned('S_wrapper', 1, '8', 'true'), *error('S_wrapper', 'S_wrapper_resume', explicit=True),
                *budget('S_pre'), *budget('S'), *budget('S_wrapper_resume'),
                'S_final = $drive_steps(S_wrapper_error,3000)', 'S_final.COMPLETION = NORMAL',
                '$test_outputs(S_final.EVENTS) = ' + text('B|O|' + OPTION_ERROR + '|99|1|0|0|2633|9|E|H|8192|' + MESSAGE + '|' + VALUE_ERROR + '|99|1|1|0|8|Z')]
        else:
            values += ['S_pre.ARRAYS[n_captured].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_captured)]',
                'pvalue_captured = PSTRING_CARRIER (REQUEST_STRING n_candidate) ' + text('captured-owned-array73'),
                '$string_carrier_valid(S_pre,pvalue_captured)',
                'S.ARRAYS[n_after_option].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_option_array)]',
                '$string_bytes(pvalue_option_array) = (' + text('option-array73') + ')',
                '~$config_strict(S,pconfigcall_S)', 'S.PRECISIONINI = ' + text('7'),
                *returned('S', 1, '8', 'false'), 'S_return.STORE[n_result] = DEFINED (PINT 99)',
                'S_return.STORE[n_effects] = DEFINED (PINT 1)',
                'S_return.STORE[n_keep] = DEFINED (POBJECT n_owner_pre)',
                'S_return.STORE[n_old] = DEFINED (PARRAY n_captured)',
                'S_return.STORE[n_array_keep] = DEFINED (PARRAY n_handler_keep)', 'n_handler_keep =/= n_captured',
                'S_return.ARRAYS[n_handler_keep].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_handler_array)]',
                '$string_bytes(pvalue_handler_array) = (' + text('handler-array73') + ')',
                'S_return.STORE[n_call] = DEFINED pvalue_handler_call', '$string_bytes(pvalue_handler_call) = (' + text('constant') + ')',
                'S_return.STORE[n_value] = DEFINED pvalue_handler_value', '$string_bytes(pvalue_handler_value) = (' + text('handler-value73') + ')',
                *error('S', 'S_resume'), '$string_carrier_valid(S_error,pvalue_captured)',
                *refusals('S'), *budget('S_pre'), *budget('S_resume'),
                *recovery('S_error', 'n_owner_pre', '8'),
                'S_final = $drive_steps(S_recovered,3000)', 'S_final.COMPLETION = NORMAL',
                '$test_outputs(S_final.EVENTS) = ' + text('B|O|W|8192|' + MESSAGE + '|' + VALUE_ERROR + '|99|1|1|constant|precision|handler-value73|handler-array73|captured-owned-array73|8|Z|R|8|11')]
    values += ['S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.ERRORHANDLER.CALLBACK = eps', 'S_final.USERCONSTANTS = eps', *common.public('S_final')]
    return values


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(path.relative_to(driver.ROOT)): sources.family.sha(path)
        for path in (Path(__file__), Path(shared.__file__), Path(shared.shared.__file__),
            Path(shared.shared.shared.__file__), Path(sources.__file__))})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
