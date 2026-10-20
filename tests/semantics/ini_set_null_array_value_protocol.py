#!/usr/bin/env python3
"""NULL option handling precedes rejection of the retained original array value."""
import json
import os
from pathlib import Path

import ini_set_null_option_protocol as shared
import ini_set_null_array_value_sources as sources

driver, common, text, b64 = shared.driver, shared.common, shared.text, shared.b64
MESSAGE = shared.MESSAGE
VALUE_ERROR = 'ini_set(): Argument #2 ($value) must be of type string|int|float|bool|null'
OPTION_ERROR = 'ini_set(): Argument #1 ($option) must be of type string, null given'
reach, budget, unchanged = shared.reach, shared.budget, shared.unchanged
PREFIX = shared.PREFIX + r"""
dec $test_ini_array_partial(pstate) : bool
def $test_ini_array_partial(S) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET /\ pconfigcall.OWNER = eps
  -- if pconfigcall.INDEX = 1
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN PNULL)]
def $test_ini_array_partial(S) = false -- otherwise
dec $test_ini_array_partial_seek(pstate, nat) : pstate
def $test_ini_array_partial_seek(S, 0) = S
def $test_ini_array_partial_seek(S, n) = S
  -- if $(n > 0)
  -- if $test_ini_array_partial(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_ini_array_partial_seek(S, n) = $test_ini_array_partial_seek($drive_steps($test_running(S),1),$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_ini_array_partial(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def front(state, start):
    call, array = 'pconfigcall_' + state, 'n_array_' + state
    return [*reach(state, start, 0), state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
        call + '.KIND = INTRINSIC_INI_SET', call + '.OWNER = eps', call + '.PACKS = eps',
        call + '.INDEX = 2', '~' + call + '.NAMED',
        call + '.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (PARRAY ' + array + '))]',
        '$config_invoke_valid(' + state + ',' + call + ')',
        '$config_ini_rejected_array(' + state + ',' + array + ')',
        '~$config_ini_quiet_value(' + state + ',PARRAY ' + array + ')',
        '(HARRAY ' + array + ') <- ' + state + '.ALLOCATIONS',
        '$node_children(' + state + ',HARRAY ' + array + ') = eps',
        '$config_nodes(' + call + ') = [HARRAY ' + array + ']',
        '$task_nodes(CONFIG_INI_NULL_RESULT ' + call + ') = [HARRAY ' + array + ']',
        '$intrinsic_argument(' + state + ',' + call + '.SITE,0) = ((expression_option_' + state + ',false,eps,porigin_option_' + state + ',z_option_' + state + '))',
        '$intrinsic_argument(' + state + ',' + call + '.SITE,1) = ((expression_value_' + state + ',false,eps,porigin_value_' + state + ',z_value_' + state + '))',
        '$config_ini_pack_known(' + state + ',' + state + '.ARRAYS[' + array + '].ITEMS,$compiled_read(' + state + ',porigin_value_' + state + '))',
        *common.public(state)]


def returned(state, warnings, precision, result):
    call, array = 'pconfigcall_' + state, 'n_array_' + state
    dispatch, entered, returned, resume = [state + '_' + suffix for suffix in ('dispatch', 'entered', 'return', 'resume')]
    error, ret = 'perrorcall_' + state, 'perrorcall_return_' + state
    event = 'DIAGNOSTIC "Deprecated" ' + error + '.MESSAGE ' + error + '.LINE'
    return ['$config_ini_null_valid(' + state + ',' + call + ')', '$error_handler_eligible(' + state + ',8192)',
        *common.step(dispatch, state), dispatch + '.TODO = (ERROR_HANDLER_INVOKE ' + error + ') :: ptask_' + state + '*',
        error + '.RESUME = CONFIG_INI_NULL_RESULT ' + call, error + '.LEVEL = 8192',
        error + '.MESSAGE = ' + text(MESSAGE), error + '.SITE = ' + call + '.SITE', error + '.LINE = ' + call + '.LINE',
        error + '.EVENT = ' + event, '$error_call_valid(' + dispatch + ',' + error + ')', *common.public(dispatch),
        *reach(entered, dispatch, 1), entered + '.CURRENT = (pcallcontext_' + state + ')',
        '$error_context_valid(' + entered + ',pcallcontext_' + state + ')',
        '$error_handler_trace_values(' + entered + ',pcallcontext_' + state + ',' + call + ') = [PNULL,PARRAY ' + array + ']',
        *common.public(entered), *reach(returned, entered, 2),
        returned + '.TODO = (ERROR_HANDLER_RESULT ' + ret + ') :: ptask_' + state + '*',
        ret + '.RESUME = CONFIG_INI_NULL_RESULT ' + call,
        '$call_task_valid(' + returned + ',ERROR_HANDLER_RESULT ' + ret + ')',
        returned + '.RESULT = KNOWN (PBOOL ' + result + ')', returned + '.CURRENT = ' + state + '.CURRENT',
        returned + '.ENV = ' + state + '.ENV', returned + '.FRAMES = ' + state + '.FRAMES',
        returned + '.PRECISIONINI = ' + text(precision),
        '$lookup(' + returned + '.ENV,' + text('warnings') + ') = (n_warnings_' + state + ')',
        returned + '.STORE[n_warnings_' + state + '] = DEFINED (PINT ' + str(warnings) + ')',
        returned + '.ARRAYS[' + array + '].ITEMS = ' + state + '.ARRAYS[' + array + '].ITEMS',
        '$config_ini_null_valid(' + returned + ',' + call + ')', *common.public(returned),
        state + '_expected = $error_handler_restore(' + returned + '[.TODO = (CONFIG_INI_NULL_RESULT ' + call + ') :: ptask_' + state + '*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]' + ('[.EVENTS = ' + returned + '.EVENTS ++ [' + event + ']]' if result == 'false' else '') + ',' + ret + '.CALLBACK)',
        *common.step(resume, returned), resume + ' = ' + state + '_expected',
        '$call_task_valid(' + resume + ',CONFIG_INI_NULL_RESULT ' + call + ')', *common.public(resume)]


def error(state, start, caller, strict=False, default=False):
    call, array, out = 'pconfigcall_' + state, 'n_array_' + state, state + '_error'
    option = 'PNULL' if strict else 'PSTRING eps'
    return [*common.step(out, start), out + '.TODO = (THROW_SEARCH n_error_' + state + ') :: ptask_' + state + '*',
        out + '.OBJECTS[n_error_' + state + '] = THROWABLE pthrowable_' + state,
        'pthrowable_' + state + '.KIND = "TypeError"', 'pthrowable_' + state + '.ORIGIN = (' + call + '.SITE)',
        '$string_bytes($throwable_field(' + out + ',n_error_' + state + ',"message")) = (' + text(OPTION_ERROR if strict else VALUE_ERROR) + ')',
        '$throwable_field(' + out + ',n_error_' + state + ',"previous") = PNULL',
        '$throwable_field(' + out + ',n_error_' + state + ',"line") = PINT ' + call + '.LINE',
        '$throwable_field(' + out + ',n_error_' + state + ',"trace") = PARRAY n_trace_' + state,
        out + '.ARRAYS[n_trace_' + state + '].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_api_' + state + ')),ENTRY (KINT 1) (DIRECT (PARRAY n_caller_' + state + '))]',
        '$trace_array_field(' + out + ',n_api_' + state + ',' + text('function') + ') = PSTRING ' + text('ini_set'),
        '$trace_array_field(' + out + ',n_api_' + state + ',' + text('args') + ') = PARRAY n_args_' + state,
        out + '.ARRAYS[n_args_' + state + '].ITEMS = [ENTRY (KINT 0) (DIRECT (' + option + ')),ENTRY (KINT 1) (DIRECT (PARRAY ' + array + '))]',
        '$node_children(' + out + ',HARRAY n_args_' + state + ') = [HARRAY ' + array + ']',
        '$trace_array_field(' + out + ',n_caller_' + state + ',' + text('function') + ') = PSTRING ' + text(caller),
        out + '.ARRAYS[' + array + '].ITEMS = ' + start + '.ARRAYS[' + array + '].ITEMS',
        '(HARRAY ' + array + ') <- ' + out + '.ALLOCATIONS',
        out + '.EVENTS = ' + start + '.EVENTS' + (' ++ [DIAGNOSTIC "Deprecated" $config_ini_null_message(' + call + ') ' + call + '.LINE]' if default else ''),
        *unchanged(out, start, 'STORE ENV ERRORHANDLER USERCONSTANTS SELECTEDCALLS PRECISIONINI'), *common.public(out)]


def refusals(state):
    call, array = 'pconfigcall_' + state, 'n_array_' + state
    values = []
    for field in ('.SITE = PORIGIN 0 eps', '.LINE = $(' + call + '.LINE + 1)', '.INDEX = 1',
            '.OWNER = (0)', '.NAMED = true', '.KIND = INTRINSIC_INI_GET',
            '.SELECTION = (|' + state + '.SELECTEDCALLS|)', '.SENT = ' + call + '.SENT[0:1]'):
        values += ['~$config_ini_null_valid(' + state + ',' + call + '[' + field + '])']
    values += ['~$config_ini_rejected_array(' + state + ',|' + state + '.ARRAYS|)',
        '~$config_ini_rejected_array(' + state + '[.ALLOCATIONS = eps],' + array + ')',
        '~$config_ini_null_valid(' + state + '[.CODE = eps],' + call + ')']
    for item in ('DIRECT PUNDEFINED', 'ALIAS 0', 'DIRECT (PARRAY 0)', 'DIRECT (POBJECT 0)',
            'DIRECT (PSTRING ' + text('legacy69') + ')',
            'DIRECT (PSTRING_CARRIER (REQUEST_STRING (|' + state + '.STRINGDATA|)) ' + text('bad69') + ')'):
        entries = '[ENTRY (KINT 0) (' + item + ')]'
        values += ['~$config_ini_rejected_entries(' + state + ',' + entries + ')',
            '~$config_ini_rejected_array(' + state + '[.ARRAYS[' + array + '].ITEMS = ' + entries + '],' + array + ')']
    return values


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET']
    if name == 'null-array-value-default-and-true-handler-convert-option-before-error':
        values += [*front('S_empty', 'S_initial'), 'S_empty.ARRAYS[n_array_S_empty].ITEMS = eps',
            'pconfigcall_S_empty.SELECTION = eps', '$compiled_read(S_empty,porigin_option_S_empty) = (PNULL)',
            '$config_ini_null_valid(S_empty,pconfigcall_S_empty)', '~$error_handler_eligible(S_empty,8192)',
            *error('S_empty', 'S_empty', 'nullArrayDefaultCaller69', default=True),
            *front('S_true', 'S_empty_error'),
            'S_true.ARRAYS[n_array_S_true].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 2333))]',
            '$compiled_read(S_true,porigin_value_S_true) = (PARRAY n_known)',
            '$($heap_count(HARRAY n_known,$pools_nodes(S_true.POOLS)) > 0)',
            *returned('S_true', 1, '14', 'true'), *error('S_true', 'S_true_resume', 'nullArrayDefaultCaller69'),
            'S_forged = $allocate_array(S_true,$array_insert($array_empty(),KINT 0,DIRECT (PINT 2334)))',
            'S_forged.RESULT = KNOWN (PARRAY n_forged)',
            'pconfigcall_forged = pconfigcall_S_true[.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (PARRAY n_forged))]]',
            '$config_invoke_valid(S_forged,pconfigcall_forged)', '$config_ini_rejected_array(S_forged,n_forged)',
            '~$config_ini_pack_known(S_forged,S_forged.ARRAYS[n_forged].ITEMS,$compiled_read(S_forged,porigin_value_S_true))',
            '~$config_ini_null_valid(S_forged,pconfigcall_forged)', *refusals('S_true'), *budget('S_empty'), *budget('S_true_resume'),
            'S_final = $drive_steps(S_true_error,3000)', 'S_final.COMPLETION = NORMAL',
            '$test_outputs(S_final.EVENTS) = ' + text('B|' + VALUE_ERROR + '|99|T|H|8192|' + MESSAGE + '|' + VALUE_ERROR + '|E|2333|99|1|14|Z')]
    else:
        strict = name == 'strict-null-array-value-rejects-option-after-value-effects'
        assert strict or name == 'selected-null-array-value-false-handler-keeps-captured-array-after-cow'
        values += ['S_pre_found = $test_ini_array_partial_seek(S_initial,3000)',
            r'S_pre_found.COMPLETION = NORMAL \/ S_pre_found.COMPLETION = BUDGET',
            'S_pre = S_pre_found[.COMPLETION = NORMAL]', '$test_ini_array_partial(S_pre)',
            'S_pre.TODO = (CONFIG_ARGS pconfigcall_pre) :: ptask_pre*',
            'pconfigcall_pre.SELECTION = (n_selection)',
            '$lookup(S_pre.ENV,' + text('value') + ') = (n_value)', 'S_pre.STORE[n_value] = DEFINED (PARRAY n_captured)',
            '$lookup(S_pre.ENV,' + text('arrayKeep') + ') = (n_keep)', 'S_pre.STORE[n_keep] = DEFINED (PARRAY n_captured)',
            '$lookup(S_pre.ENV,' + text('result') + ') = (n_result)', 'S_pre.STORE[n_result] = DEFINED (PINT 99)',
            '$lookup(S_pre.ENV,' + text('effects') + ') = (n_effects)', 'S_pre.STORE[n_effects] = DEFINED (PINT 0)',
            '$test_outputs(S_pre.EVENTS) = ' + text('B|'), *front('S', 'S_pre'),
            'pconfigcall_S = pconfigcall_pre[.INDEX = 2][.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (PARRAY n_captured))]]',
            'n_array_S = n_captured', 'S.STORE[n_effects] = DEFINED (PINT 1)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            '$compiled_read(S,porigin_value_S) = eps', '$test_outputs(S.EVENTS) = ' + text('B|V|')]
        if strict:
            values += ['S.ARRAYS[n_array_S].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 2371))]',
                '$config_strict(S,pconfigcall_S)', '~$config_ini_null_valid(S,pconfigcall_S)',
                'S.STORE[n_value] = DEFINED (PINT 0)', 'S.PRECISIONINI = ' + text('9'),
                *error('S', 'S', 'strictNullArrayCaller69', strict=True),
                *budget('S'), 'S_final = $drive_steps(S_error,3000)', 'S_final.COMPLETION = NORMAL',
                '$test_outputs(S_final.EVENTS) = ' + text('B|V|' + OPTION_ERROR + '|99|1|0|constant|precision|0|2371|9|Z')]
        else:
            values += ['S.ARRAYS[n_array_S].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_captured),ENTRY (KINT 1) (DIRECT (PINT 2351))]',
                'pvalue_captured = PSTRING_CARRIER (REQUEST_STRING n_candidate) ' + text('captured-array69'),
                '$string_carrier_valid(S,pvalue_captured)', '~$config_strict(S,pconfigcall_S)',
                'S.STORE[n_value] = DEFINED (PINT 2357)', 'S.PRECISIONINI = ' + text('7'),
                *returned('S', 1, '8', 'false'),
                'S_return.STORE[n_result] = DEFINED (PINT 99)', 'S_return.STORE[n_effects] = DEFINED (PINT 1)',
                'S_return.STORE[n_keep] = DEFINED (PARRAY n_mutated)', 'n_mutated =/= n_array_S',
                '$entry_lookup(S_return.ARRAYS[n_mutated].ITEMS,KINT 0) = (DIRECT pvalue_keep)',
                '$string_bytes(pvalue_keep) = (' + text('handler-keep69') + ')',
                '$entry_lookup(S_return.ARRAYS[n_mutated].ITEMS,KINT 1) = (DIRECT (PINT 2351))',
                '$heap_count(HARRAY n_array_S,$tasks_nodes(S_return.TODO)) = 1',
                *error('S', 'S_resume', 'nullArrayCaller69'),
                '$string_carrier_valid(S_error,pvalue_captured)', *refusals('S'), *budget('S_pre'), *budget('S_resume'),
                'S_final = $drive_steps(S_error,3000)', 'S_final.COMPLETION = NORMAL', 'S_final.PRECISIONINI = ' + text('11'),
                '$test_outputs(S_final.EVENTS) = ' + text('B|V|W|8192|' + MESSAGE + '|' + VALUE_ERROR + '|99|1|1|constant|precision|handler-value69|handler-keep69|2351|8|Z|R|8|11')]
    values += ['S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.ERRORHANDLER.CALLBACK = eps', 'S_final.USERCONSTANTS = eps', *common.public('S_final')]
    return values


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(path.relative_to(driver.ROOT)): sources.family.sha(path)
        for path in (Path(__file__), Path(shared.__file__), Path(sources.__file__))})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
