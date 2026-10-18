#!/usr/bin/env python3
"""Named INI source order, normalized slots and real NULL continuations."""
import json
import os
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import ini_set_named_null_option_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64
MESSAGE = 'ini_set(): Passing null to parameter #1 ($option) of type string is deprecated'
PREFIX = r"""
dec $test_ini_named_front(pstate, nat) : bool
def $test_ini_named_front(S, 0) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.NAMED
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN PNULL), NAMED_SENT (KNOWN pvalue)]
def $test_ini_named_front(S, 1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_call(S,pcallcontext) = (perrorcall)
  -- if perrorcall.RESUME = CONFIG_INI_NULL_RESULT pconfigcall
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.NAMED
def $test_ini_named_front(S, 2) = true
  -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = CONFIG_INI_NULL_RESULT pconfigcall
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.NAMED
def $test_ini_named_front(S, 3) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.INDEX = 1
  -- if pconfigcall.NAMED
  -- if pconfigcall.SENT = [NAMED_HOLE, NAMED_SENT (KNOWN pvalue)]
def $test_ini_named_front(S, n_stage) = false -- otherwise
dec $test_ini_named_seek(pstate, nat, nat) : pstate
def $test_ini_named_seek(S, n_stage, 0) = S
def $test_ini_named_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_ini_named_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_ini_named_seek(S, n_stage, n) = $test_ini_named_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_ini_named_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def reach(state, start, stage):
    return [state + '_found = $test_ini_named_seek(' + start + ',' + str(stage) + ',3000)',
        state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_ini_named_front(' + state + ',' + str(stage) + ')']


def unchanged(after, before, fields):
    return [after + '.' + field + ' = ' + before + '.' + field for field in fields.split()]


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)',
        state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)',
        state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def layout(state, mixed=False):
    call = 'pconfigcall_' + state
    values = []
    for i, (name, dest) in enumerate([(None, 0), ('value', 1)] if mixed else [('value', 1), ('option', 0)]):
        suffix = state + '_' + str(i)
        values += ['$intrinsic_argument(' + state + ',' + call + '.SITE,' + str(i) + ') = ((expression_' + suffix + ',false,preqbytes_' + suffix + '?,porigin_' + suffix + ',z_' + suffix + '))',
            'preqbytes_' + suffix + '? = ' + ('eps' if name is None else '(' + text(name) + ')'),
            '$config_destination(' + call + '.KIND,preqbytes_' + suffix + '?,' + str(i) + ') = (' + str(dest) + ')']
    return values


def front(state, start, candidate, mixed=False):
    call = 'pconfigcall_' + state
    return [*reach(state, start, 0), state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
        call + '.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (' + candidate + '))]',
        call + '.KIND = INTRINSIC_INI_SET', call + '.INDEX = 2', call + '.NAMED',
        call + '.OWNER = eps', call + '.PACKS = eps', '$config_invoke_valid(' + state + ',' + call + ')',
        '$dynamic_scalar_define_arguments(' + state + ',' + call + ',0)',
        *layout(state, mixed), *common.public(state)]


def refusals(state):
    call = 'pconfigcall_' + state
    values = []
    for field in ('.NAMED = false', '.OWNER = (0)', '.INDEX = 1', '.SITE = PORIGIN 0 eps',
            '.LINE = $(' + call + '.LINE + 1)', '.SELECTION = (|' + state + '.SELECTEDCALLS|)',
            '.SENT = ' + call + '.SENT[0:1]', '.SENT = ' + call + '.SENT ++ [NAMED_SENT (KNOWN PNULL)]'):
        values += ['~$config_ini_null_valid(' + state + ',' + call + '[' + field + '])']
    values += ['~$config_invoke_valid(' + state + ',' + call + '[.NAMED = false])',
        'pvalue_bad_' + state + ' = PSTRING_CARRIER (REQUEST_STRING (|' + state + '.STRINGDATA|)) ' + text('bad63'),
        '~$config_ini_null_valid(' + state + ',' + call + '[.SENT = $named_slot_set(' + call + '.SENT,1,KNOWN pvalue_bad_' + state + ')])']
    return values


def handled(state, candidate, warnings, precision, result):
    call, after = 'pconfigcall_' + state, state + '_after'
    dispatch, entered, returned, resume = [state + '_' + s for s in ('dispatch', 'entered', 'return', 'resume')]
    error, error_return = 'perrorcall_' + state, 'perrorcall_return_' + state
    values = ['$config_ini_null_valid(' + state + ',' + call + ')', '$error_handler_eligible(' + state + ',8192)',
        *common.step(dispatch, state), dispatch + '.TODO = (ERROR_HANDLER_INVOKE ' + error + ') :: ptask_' + state + '*',
        error + '.RESUME = CONFIG_INI_NULL_RESULT ' + call, error + '.LEVEL = 8192',
        error + '.MESSAGE = ' + text(MESSAGE), error + '.MESSAGE = $config_ini_null_message(' + call + ')',
        error + '.SITE = ' + call + '.SITE', error + '.LINE = ' + call + '.LINE',
        error + '.EVENT = DIAGNOSTIC "Deprecated" ' + error + '.MESSAGE ' + error + '.LINE',
        '$error_call_valid(' + dispatch + ',' + error + ')', *common.public(dispatch),
        *reach(entered, dispatch, 1), entered + '.CURRENT = (pcallcontext_' + state + ')',
        '$error_context_valid(' + entered + ',pcallcontext_' + state + ')',
        '$error_context_trigger(' + entered + ',pcallcontext_' + state + ') = (' + call + ')',
        '$error_handler_trace_values(' + entered + ',pcallcontext_' + state + ',' + call + ') = [PNULL,' + candidate + ']',
        *common.public(entered), *reach(returned, entered, 2),
        returned + '.TODO = (ERROR_HANDLER_RESULT ' + error_return + ') :: ptask_' + state + '*',
        error_return + '.RESUME = CONFIG_INI_NULL_RESULT ' + call,
        '$call_task_valid(' + returned + ',ERROR_HANDLER_RESULT ' + error_return + ')',
        returned + '.RESULT = KNOWN (PBOOL ' + result + ')',
        returned + '.CURRENT = ' + state + '.CURRENT', returned + '.ENV = ' + state + '.ENV',
        returned + '.FRAMES = ' + state + '.FRAMES', returned + '.PRECISIONINI = ' + text(precision),
        '$lookup(' + returned + '.ENV,' + text('warnings') + ') = (n_warnings_' + state + ')',
        returned + '.STORE[n_warnings_' + state + '] = DEFINED (PINT ' + str(warnings) + ')',
        *common.public(returned), *common.step(resume, returned),
        resume + '.TODO = (CONFIG_INI_NULL_RESULT ' + call + ') :: ptask_' + state + '*',
        resume + '.ERRORHANDLER.CALLBACK = (' + error_return + '.CALLBACK)',
        resume + '.RESULT = KNOWN PNULL', '$call_task_valid(' + resume + ',CONFIG_INI_NULL_RESULT ' + call + ')',
        *unchanged(resume, returned, 'STORE ENV ARRAYS OBJECTS STRINGDATA USERCONSTANTS PRECISIONINI PRECISIONMODIFIED'),
        resume + '.EVENTS = ' + returned + '.EVENTS' + (' ++ [DIAGNOSTIC "Deprecated" ' + error + '.MESSAGE ' + error + '.LINE]' if result == 'false' else ''),
        *common.public(resume), *common.step(after, resume),
        after + ' = ' + resume + '[.TODO = ptask_' + state + '*][.RESULT = KNOWN (PBOOL false)][.BASE = BASE_VALUE (KNOWN PNULL)]',
        *common.public(after)]
    return values


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET']
    if name == 'named-null-literal-handler-and-positional-prefix':
        candidate = 'PSTRING_CARRIER INTERNED_STRING ' + text('literal-value63')
        values += [*front('S', 'S_initial', candidate), '~$config_strict(S,pconfigcall_S)',
            '$compiled_read(S,porigin_S_0) = (PSTRING ' + text('literal-value63') + ')', '$compiled_read(S,porigin_S_1) = (PNULL)',
            *handled('S', candidate, 1, '14', 'true'),
            *front('S_mixed', 'S_after', 'PINT 2011', True),
            '$compiled_read(S_mixed,porigin_S_mixed_0) = (PNULL)',
            '$compiled_read(S_mixed,porigin_S_mixed_1) = (PINT 2011)',
            *handled('S_mixed', 'PINT 2011', 2, '14', 'true'),
            '~$dynamic_scalar_define_arguments(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,1,KNOWN (PINT 2011))],0)',
            '~$config_ini_null_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,1,KNOWN (PINT 2011))])',
            '~$dynamic_scalar_define_arguments(S_mixed,pconfigcall_S_mixed[.SENT = $named_slot_set(pconfigcall_S_mixed.SENT,1,KNOWN (PINT 2012))],0)',
            *refusals('S'), *refusals('S_mixed'), *budget('S'), *budget('S_mixed_resume'),
            'S_final = $drive_steps(S_mixed_after,3000)', 'S_final.COMPLETION = NORMAL',
            '$test_outputs(S_final.EVENTS) = ' + text('B|H|8192|' + MESSAGE + '|F|H|8192|' + MESSAGE + '|F|2|14'),
            'S_final.PRECISIONINI = ' + text('14')]
    else:
        strict = name == 'strict-reversed-named-null-before-handler-after-effects'
        assert strict or name == 'selected-reversed-named-null-false-handler-preserves-early-value'
        candidate = 'PINT 2039' if strict else 'pvalue_captured'
        values += [*reach('S_early', 'S_initial', 3),
            'S_early.TODO = (CONFIG_ARGS pconfigcall_early) :: ptask_early*',
            'pconfigcall_early.SENT = [NAMED_HOLE,NAMED_SENT (KNOWN (' + candidate + '))]',
            'pconfigcall_early.INDEX = 1', 'pconfigcall_early.NAMED',
            '$call_task_valid(S_early,CONFIG_ARGS pconfigcall_early)',
            'pconfigcall_early.SELECTION = (n_selection)', 'S_early.SELECTEDCALLS[n_selection].KIND = INTRINSIC_INI_SET',
            '$lookup(S_early.ENV,' + text('effects') + ') = (n_effects)', 'S_early.STORE[n_effects] = DEFINED (PINT 1)',
            '$test_outputs(S_early.EVENTS) = ' + text('B|V|'),
            'S_early.PRECISIONINI = ' + text('9' if strict else '6'),
            *front('S', 'S_early', candidate),
            'pconfigcall_S = pconfigcall_early[.INDEX = 2][.SENT = $named_slot_set(pconfigcall_early.SENT,0,KNOWN PNULL)]',
            'S.STORE[n_effects] = DEFINED (PINT 2)', '$test_outputs(S.EVENTS) = ' + text('B|V|O|'),
            '$compiled_read(S,porigin_S_0) = eps', '$compiled_read(S,porigin_S_1) = eps',
            '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            '$lookup(S.ENV,' + text('call') + ') = (n_call)', 'S.STORE[n_call] = DEFINED pvalue_live_call',
            '$string_bytes(pvalue_live_call) = (' + text('ini_get') + ')',
            '$lookup(S.ENV,' + text('value') + ') = (n_value)']
        if strict:
            values += ['$config_strict(S,pconfigcall_S)', '~$config_ini_null_valid(S,pconfigcall_S)',
                'S.STORE[n_value] = DEFINED (PINT 1)', 'S.PRECISIONINI = ' + text('9'),
                '$lookup(S.ENV,' + text('warnings') + ') = (n_warnings)', 'S.STORE[n_warnings] = DEFINED (PINT 0)',
                *common.step('S_error', 'S'), 'S_error.TODO = (THROW_SEARCH n_error) :: ptask_S*',
                'S_error.OBJECTS[n_error] = THROWABLE pthrowable_error', 'pthrowable_error.KIND = "TypeError"',
                '$string_bytes($throwable_field(S_error,n_error,"message")) = (' + text('ini_set(): Argument #1 ($option) must be of type string, null given') + ')',
                '$throwable_field(S_error,n_error,"previous") = PNULL',
                '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
                'S_error.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_api)),ENTRY (KINT 1) (DIRECT (PARRAY n_caller))]',
                '$trace_array_field(S_error,n_api,' + text('function') + ') = PSTRING ' + text('ini_set'),
                '$trace_array_field(S_error,n_api,' + text('args') + ') = PARRAY n_args',
                'S_error.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT PNULL),ENTRY (KINT 1) (DIRECT (PINT 2039))]',
                '$trace_array_field(S_error,n_caller,' + text('function') + ') = PSTRING ' + text('strictNamedNullCaller63'),
                *unchanged('S_error', 'S', 'STORE ENV STRINGDATA EVENTS USERCONSTANTS PRECISIONINI PRECISIONMODIFIED ERRORHANDLER'),
                *common.public('S_error'), *budget('S'),
                'S_final = $drive_steps(S_error,3000)', 'S_final.COMPLETION = NORMAL',
                '$test_outputs(S_final.EVENTS) = ' + text('B|V|O|ini_set(): Argument #1 ($option) must be of type string, null given|ini_set|N|2039|strictNamedNullCaller63|99|2|0|9|ini_get|precision|1|Z')]
        else:
            values += ['pvalue_captured = PSTRING_CARRIER (REQUEST_STRING n_candidate) ' + text('captured-value63'),
                '$string_carrier_valid(S,pvalue_captured)', '~$config_strict(S,pconfigcall_S)',
                'S.PRECISIONINI = ' + text('7'), 'S.STORE[n_value] = DEFINED pvalue_live_value',
                '$string_bytes(pvalue_live_value) = (' + text('after-option63') + ')',
                *handled('S', candidate, 1, '8', 'false'),
                'S_after.STORE[n_result] = DEFINED (PINT 99)',
                '$string_carrier_valid(S_after,pvalue_captured)', *refusals('S'), *budget('S'), *budget('S_resume'),
                'S_final = $drive_steps(S_after,3000)', 'S_final.COMPLETION = NORMAL',
                '$test_outputs(S_final.EVENTS) = ' + text('B|V|O|W|8192|' + MESSAGE + '|F|8|2|1|ini_restore|precision|handler-value63|Z')]
    values += ['S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.ERRORHANDLER.CALLBACK = eps', 'S_final.USERCONSTANTS = eps', *common.public('S_final')]
    return values


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
