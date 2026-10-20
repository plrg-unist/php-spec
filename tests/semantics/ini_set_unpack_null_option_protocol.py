#!/usr/bin/env python3
"""Direct and selected INI calls resume captured unpacked NULL options."""
import json
import os
from pathlib import Path

import ini_set_owned_null_option_protocol as owned
import ini_set_null_option_protocol as shared
import ini_set_unpack_null_option_sources as sources

driver, common, text, b64 = shared.driver, shared.common, shared.text, shared.b64
MESSAGE = shared.MESSAGE
reach, budget, unchanged = shared.reach, shared.budget, shared.unchanged
PREFIX = shared.PREFIX + r"""
dec $test_ini_unpack_array_partial(pstate) : bool
def $test_ini_unpack_array_partial(S) = true
  -- if S.TODO = (ARRAY_NEXT n_array phpType13*) :: ptask_tail*
  -- if |phpType13*| = 1
  -- if S.ARRAYS[n_array].ITEMS = [ENTRY (KSTRING ($ptascii("value"))) (DIRECT pvalue)]
def $test_ini_unpack_array_partial(S) = false -- otherwise
dec $test_ini_unpack_array_seek(pstate, nat) : pstate
def $test_ini_unpack_array_seek(S, 0) = S
def $test_ini_unpack_array_seek(S, n) = S
  -- if $(n > 0)
  -- if $test_ini_unpack_array_partial(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_ini_unpack_array_seek(S, n) = $test_ini_unpack_array_seek($drive_steps($test_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_ini_unpack_array_partial(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def entries(candidate, order):
    option = 'ENTRY (KSTRING (' + text('option') + ')) (DIRECT PNULL)'
    value = 'ENTRY (KSTRING (' + text('value') + ')) (DIRECT (' + candidate + '))'
    if order == 'reversed':
        return '[' + value + ',' + option + ']'
    if order == 'mixed':
        return '[ENTRY (KINT 0) (DIRECT PNULL),' + value + ']'
    assert order in ('numeric', 'strict')
    first, second = (3, 7) if order == 'numeric' else (5, 9)
    return '[ENTRY (KINT ' + str(first) + ') (DIRECT PNULL),ENTRY (KINT ' + str(second) + ') (DIRECT (' + candidate + '))]'


def front(state, start, candidate, order, selected=False):
    call, pack = 'pconfigcall_' + state, 'pconfigpack_' + state
    values = [*reach(state, start, 0), state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
        call + '.KIND = INTRINSIC_INI_SET', call + '.OWNER = eps', call + '.INDEX = 1',
        ('' if order in ('reversed', 'mixed') else '~') + call + '.NAMED',
        call + '.PACKS = [' + pack + ']', pack + '.INDEX = 0',
        pack + '.ITEMS = ' + entries(candidate, order),
        call + '.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (' + candidate + '))]',
        '$config_invoke_valid(' + state + ',' + call + ')',
        '$config_selected_valid(' + state + ',' + call + ')',
        '$config_pack_source_valid(' + state + ',' + call + ',' + pack + ')',
        '$config_ini_quiet_value(' + state + ',' + candidate + ')',
        '$config_ini_pack_known(' + state + ',' + pack + '.ITEMS,$compiled_read(' + state + ',' + pack + '.SITE))',
        '$intrinsic_argument(' + state + ',' + call + '.SITE,0) = ((expression_pack_' + state + ',true,eps,' + pack + '.SITE,' + pack + '.LINE))',
        '$intrinsic_count(' + state + ',' + call + '.SITE) = (1)',
        '$config_nodes(' + call + ') = eps', '$task_nodes(CONFIG_INI_NULL_RESULT ' + call + ') = eps',
        *common.public(state)]
    if selected:
        values += [call + '.SELECTION = (n_selection_' + state + ')',
            state + '.SELECTEDCALLS[n_selection_' + state + '].KIND = INTRINSIC_INI_SET',
            state + '.SELECTEDCALLS[n_selection_' + state + '].SITE = ' + call + '.SITE',
            state + '.SELECTEDCALLS[n_selection_' + state + '].LINE = ' + call + '.LINE']
    else:
        values += [call + '.SELECTION = eps']
    return values


def handled(state, candidate, warnings, precision, result):
    # Reuse the returning-handler proof without the retained Closure projections.
    excluded = {
        state + '_entered.OBJECTS[n_owner_' + state + '] = INTRINSICCLOSURE INTRINSIC_INI_SET',
        '$getclass_live_object(' + state + '_after,n_owner_' + state + ')',
    }
    return [value.replace('$test_ini_owned_seek', '$test_ini_null_seek').replace(
        '$test_ini_owned_front', '$test_ini_null_front')
        for value in owned.handled(state, candidate, warnings, precision, result) if value not in excluded]


def literal(state):
    pack = 'pconfigpack_' + state
    return ['$compiled_read(' + state + ',' + pack + '.SITE) = (PARRAY n_known_' + state + ')',
        '$($heap_count(HARRAY n_known_' + state + ',$pools_nodes(' + state + '.POOLS)) > 0)',
        '$dynamic_array_same_entries(' + state + ',' + pack + '.ITEMS,' + state + '.ARRAYS[n_known_' + state + '].ITEMS)']


def refusals(state, named):
    call, pack = 'pconfigcall_' + state, 'pconfigpack_' + state
    values = []
    for field in ('.OWNER = (|' + state + '.OBJECTS|)', '.NAMED = ' + ('false' if named else 'true'),
            '.LINE = $(' + call + '.LINE + 1)', '.SITE = PORIGIN 0 eps', '.INDEX = 2',
            '.SELECTION = (|' + state + '.SELECTEDCALLS|)', '.PACKS = eps',
            '.PACKS = [' + pack + ',' + pack + ']', '.PACKS = [' + pack + '[.INDEX = 1]]',
            '.PACKS = [' + pack + '[.LINE = $(' + pack + '.LINE + 1)]]',
            '.SENT = ' + call + '.SENT[0:1]', '.SENT = ' + call + '.SENT ++ [NAMED_SENT (KNOWN PNULL)]'):
        values += ['~$config_ini_null_valid(' + state + ',' + call + '[' + field + '])']
    values += ['~$config_ini_null_valid(' + state + '[.CODE = eps],' + call + ')',
        '~$config_ini_null_valid(' + state + ',' + call + '[.KIND = INTRINSIC_INI_GET])']
    for value in ('PSTRING ' + text('12'), 'PFLOAT 9221120237041090560',
            'PSTRING_CARRIER (REQUEST_STRING (|' + state + '.STRINGDATA|)) ' + text('bad68'), 'POBJECT 0', 'PARRAY 0'):
        values += ['~$config_ini_quiet_value(' + state + ',' + value + ')',
            '~$config_ini_null_valid(' + state + ',' + call + '[.SENT = $named_slot_set(' + call + '.SENT,1,KNOWN (' + value + '))])']
    return values


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET']
    if name == 'direct-unpack-null-default-and-named-mixed-true-handlers':
        values += [*front('S', 'S_initial', 'PINT 2293', 'numeric'), *literal('S'),
            '~$config_strict(S,pconfigcall_S)', '$config_ini_null_valid(S,pconfigcall_S)',
            '~$error_handler_eligible(S,8192)', *common.step('S_after', 'S'),
            'S_after.TODO = ptask_S*', 'S_after.RESULT = KNOWN (PBOOL false)',
            'S_after.BASE = BASE_VALUE (KNOWN PNULL)',
            'S_after.EVENTS = S.EVENTS ++ [DIAGNOSTIC "Deprecated" $config_ini_null_message(pconfigcall_S) pconfigcall_S.LINE]',
            *unchanged('S_after', 'S', 'STORE ENV OBJECTS STRINGDATA USERCONSTANTS PRECISIONINI PRECISIONMODIFIED'),
            *front('S_named', 'S_after', 'PINT 2297', 'reversed'), *literal('S_named'),
            *handled('S_named', 'PINT 2297', 1, '14', 'true'),
            *front('S_mixed', 'S_named_after', 'PINT 2309', 'mixed'), *literal('S_mixed'),
            *handled('S_mixed', 'PINT 2309', 2, '14', 'true'),
            'pconfigpack_forged = pconfigpack_S[.ITEMS = ' + entries('PINT 2294', 'numeric') + ']',
            'pconfigcall_forged = pconfigcall_S[.PACKS = [pconfigpack_forged]][.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (PINT 2294))]]',
            '$config_invoke_valid(S,pconfigcall_forged)',
            '~$config_ini_pack_known(S,pconfigpack_forged.ITEMS,$compiled_read(S,pconfigpack_S.SITE))',
            '~$config_ini_null_valid(S,pconfigcall_forged)',
            *refusals('S_named', True), *refusals('S', False), *budget('S'), *budget('S_mixed_resume'),
            'S_final = $drive_steps(S_mixed_after,3000)', 'S_final.COMPLETION = NORMAL',
            '$test_outputs(S_final.EVENTS) = ' + text('B|F|H|8192|' + MESSAGE + '|F|H|8192|' + MESSAGE + '|F|2|14|Z')]
    elif name == 'captured-selected-unpack-null-before-later-array-option-effects':
        values += ['S_pre_found = $test_ini_unpack_array_seek(S_initial,3000)',
            r'S_pre_found.COMPLETION = NORMAL \/ S_pre_found.COMPLETION = BUDGET',
            'S_pre = S_pre_found[.COMPLETION = NORMAL]', '$test_ini_unpack_array_partial(S_pre)',
            'S_pre.TODO = (ARRAY_NEXT n_builder phpType13_remaining*) :: ptask_pre*',
            'S_pre.ARRAYS[n_builder].ITEMS = [ENTRY (KSTRING (' + text('value') + ')) (DIRECT pvalue_captured)]',
            'pvalue_captured = PSTRING_CARRIER (REQUEST_STRING n_candidate) ' + text('captured-unpack68'),
            '$string_carrier_valid(S_pre,pvalue_captured)', '(HARRAY n_builder) <- S_pre.ALLOCATIONS',
            '(HARRAY n_builder) <- $tasks_nodes(S_pre.TODO)',
            '$lookup(S_pre.ENV,' + text('call') + ') = (n_call)', 'S_pre.STORE[n_call] = DEFINED pvalue_pre_call',
            '$string_bytes(pvalue_pre_call) = (' + text('ini_get') + ')',
            '$lookup(S_pre.ENV,' + text('value') + ') = (n_value)', 'S_pre.STORE[n_value] = DEFINED pvalue_pre_value',
            '$string_bytes(pvalue_pre_value) = (' + text('after-value68') + ')',
            '$lookup(S_pre.ENV,' + text('effects') + ') = (n_effects)', 'S_pre.STORE[n_effects] = DEFINED (PINT 1)',
            'S_pre.PRECISIONINI = ' + text('6'), '$test_outputs(S_pre.EVENTS) = ' + text('B|V|'),
            *common.public('S_pre'), *front('S', 'S_pre', 'pvalue_captured', 'reversed', True),
            'pconfigpack_S.ARRAY = n_builder', '~((HARRAY n_builder) <- S.ALLOCATIONS)',
            '$compiled_read(S,pconfigpack_S.SITE) = eps',
            'S.STORE[n_call] = DEFINED pvalue_live_call', '$string_bytes(pvalue_live_call) = (' + text('constant') + ')',
            'S.STORE[n_value] = DEFINED pvalue_live_value', '$string_bytes(pvalue_live_value) = (' + text('after-option68') + ')',
            'S.STORE[n_effects] = DEFINED (PINT 2)', 'S.PRECISIONINI = ' + text('7'),
            '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            '$test_outputs(S.EVENTS) = ' + text('B|V|O|'), '~$config_strict(S,pconfigcall_S)',
            *handled('S', 'pvalue_captured', 1, '8', 'false'),
            'S_return.STORE[n_result] = DEFINED (PINT 99)', 'S_return.STORE[n_effects] = DEFINED (PINT 2)',
            '$config_ini_null_valid(S_return,pconfigcall_S)',
            '$lookup(S_return.ENV,' + text('option') + ') = (n_option)',
            'S_return.STORE[n_option] = DEFINED pvalue_handler_option', '$string_bytes(pvalue_handler_option) = (' + text('precision') + ')',
            'S_return.STORE[n_call] = DEFINED pvalue_handler_call', '$string_bytes(pvalue_handler_call) = (' + text('ini_get') + ')',
            'S_return.STORE[n_value] = DEFINED pvalue_handler_value', '$string_bytes(pvalue_handler_value) = (' + text('handler-unpack68') + ')',
            *refusals('S', True), *budget('S_pre'), *budget('S_resume'),
            'S_final = $drive_steps(S_after,3000)', 'S_final.COMPLETION = NORMAL',
            'S_final.PRECISIONINI = ' + text('11'),
            '$test_outputs(S_final.EVENTS) = ' + text('B|V|O|W|8192|' + MESSAGE + '|F|8|2|1|ini_get|precision|handler-unpack68|Z|R|8|11')]
    else:
        assert name == 'strict-selected-unpack-null-keeps-early-numeric-api-value'
        values += [*front('S', 'S_initial', 'PINT 2321', 'strict', True),
            '$config_strict(S,pconfigcall_S)', '~$config_ini_null_valid(S,pconfigcall_S)',
            '$compiled_read(S,pconfigpack_S.SITE) = eps',
            '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            '$lookup(S.ENV,' + text('effects') + ') = (n_effects)', 'S.STORE[n_effects] = DEFINED (PINT 1)',
            '$lookup(S.ENV,' + text('warnings') + ') = (n_warnings)', 'S.STORE[n_warnings] = DEFINED (PINT 0)',
            '$lookup(S.ENV,' + text('call') + ') = (n_call)', 'S.STORE[n_call] = DEFINED pvalue_live_call',
            '$string_bytes(pvalue_live_call) = (' + text('constant') + ')',
            '$lookup(S.ENV,' + text('value') + ') = (n_value)', 'S.STORE[n_value] = DEFINED (PINT 0)',
            'S.PRECISIONINI = ' + text('9'), '$test_outputs(S.EVENTS) = ' + text('B|P|'),
            *common.step('S_error', 'S'), 'S_error.TODO = (THROW_SEARCH n_error) :: ptask_S*',
            'S_error.OBJECTS[n_error] = THROWABLE pthrowable_error', 'pthrowable_error.KIND = "TypeError"',
            '$string_bytes($throwable_field(S_error,n_error,"message")) = (' + text('ini_set(): Argument #1 ($option) must be of type string, null given') + ')',
            '$throwable_field(S_error,n_error,"previous") = PNULL',
            '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
            'S_error.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_api)),ENTRY (KINT 1) (DIRECT (PARRAY n_caller))]',
            '$trace_array_field(S_error,n_api,' + text('function') + ') = PSTRING ' + text('ini_set'),
            '$trace_array_field(S_error,n_api,' + text('args') + ') = PARRAY n_args',
            'S_error.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT PNULL),ENTRY (KINT 1) (DIRECT (PINT 2321))]',
            '$node_children(S_error,HARRAY n_args) = eps',
            '$trace_array_field(S_error,n_caller,' + text('function') + ') = PSTRING ' + text('strictUnpackNullCaller68'),
            'S_error.STORE[n_result] = DEFINED (PINT 99)',
            *unchanged('S_error', 'S', 'STORE ENV EVENTS PRECISIONINI ERRORHANDLER'),
            *common.public('S_error'), *budget('S'),
            'S_final = $drive_steps(S_error,3000)', 'S_final.COMPLETION = NORMAL',
            'S_final.PRECISIONINI = ' + text('9'),
            '$test_outputs(S_final.EVENTS) = ' + text('B|P|ini_set(): Argument #1 ($option) must be of type string, null given|N|2321|99|1|0|constant|0|9|Z')]
    values += ['S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.ERRORHANDLER.CALLBACK = eps', 'S_final.USERCONSTANTS = eps', *common.public('S_final')]
    return values


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(path.relative_to(driver.ROOT)): sources.family.sha(path)
        for path in (Path(__file__), Path(owned.__file__), Path(shared.__file__), Path(sources.__file__))})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
