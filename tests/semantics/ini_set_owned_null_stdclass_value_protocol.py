#!/usr/bin/env python3
"""The held intrinsic and shared stdClass remain distinct reception owners."""
import json
import os
from pathlib import Path

import ini_set_named_null_stdclass_value_protocol as shared
import ini_set_owned_null_stdclass_value_sources as sources

driver, common, text, b64 = shared.driver, shared.common, shared.text, shared.b64
MESSAGE, VALUE_ERROR, OPTION_ERROR = shared.MESSAGE, shared.VALUE_ERROR, shared.OPTION_ERROR
reach, returned, budget, mark = shared.reach, shared.returned, shared.budget, shared.mark
unchanged = shared.shared.unchanged
PREFIX = shared.shared.shared.PREFIX + r"""
dec $test_ini_owned_std_partial(pstate, nat) : bool
def $test_ini_owned_std_partial(S, 0) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.OWNER = (n_owner)
  -- if pconfigcall.INDEX = 1 /\ ~pconfigcall.NAMED
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN PNULL)]
def $test_ini_owned_std_partial(S, 1) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.OWNER = (n_owner)
  -- if pconfigcall.INDEX = 1 /\ pconfigcall.NAMED
  -- if pconfigcall.SENT = [NAMED_HOLE,NAMED_SENT (KNOWN (POBJECT n_object))]
def $test_ini_owned_std_partial(S, n_stage) = false -- otherwise
dec $test_ini_owned_std_partial_seek(pstate, nat, nat) : pstate
def $test_ini_owned_std_partial_seek(S, n_stage, 0) = S
def $test_ini_owned_std_partial_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_ini_owned_std_partial(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_ini_owned_std_partial_seek(S, n_stage, n) = $test_ini_owned_std_partial_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_ini_owned_std_partial(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def written(state, mode):
    call = 'pconfigcall_' + state
    layout = {'positional': [(0, 0, None), (1, 1, None)],
        'reversed': [(0, 1, 'value'), (1, 0, 'option')], 'mixed': [(0, 0, None), (1, 1, 'value')]}[mode]
    values = []
    for index, destination, name in layout:
        suffix = '_' + state + '_' + str(index)
        values += ['$intrinsic_argument(' + state + ',' + call + '.SITE,' + str(index) + ') = ((expression' + suffix + ',false,preqbytes' + suffix + '?,porigin' + suffix + ',z' + suffix + '))',
            'preqbytes' + suffix + '? = ' + ('eps' if name is None else '(' + text(name) + ')'),
            '$config_destination(' + call + '.KIND,preqbytes' + suffix + '?,' + str(index) + ') = (' + str(destination) + ')',
            '$config_ini_named_stdclass_argument(' + state + ',' + call + ',' + str(index) + ')']
    return values


def front(state, start, mode):
    call, owner, obj = 'pconfigcall_' + state, 'n_owner_' + state, 'n_object_' + state
    return [*reach(state, start, 0), state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
        call + '.KIND = INTRINSIC_INI_SET', call + '.OWNER = (' + owner + ')', call + '.SELECTION = eps',
        call + '.PACKS = eps', call + '.INDEX = 2', ('~' if mode == 'positional' else '') + call + '.NAMED',
        call + '.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (POBJECT ' + obj + '))]',
        owner + ' =/= ' + obj, state + '.OBJECTS[' + owner + '] = INTRINSICCLOSURE INTRINSIC_INI_SET',
        '(HOBJECT ' + owner + ') <- ' + state + '.ALLOCATIONS', '$getclass_live_object(' + state + ',' + owner + ')',
        state + '.OBJECTS[' + obj + '] = STDINSTANCE', '(HOBJECT ' + obj + ') <- ' + state + '.ALLOCATIONS',
        '$config_invoke_valid(' + state + ',' + call + ')', '$config_selected_valid(' + state + ',' + call + ')',
        '$config_ini_rejected_stdclass(' + state + ',' + obj + ')',
        '$object_table_at(' + state + '.OBJECTTABLES,' + obj + ') = eps', '$node_children(' + state + ',HOBJECT ' + obj + ') = eps',
        '$config_nodes(' + call + ') = [HOBJECT ' + owner + ',HOBJECT ' + obj + ']',
        '$task_nodes(CONFIG_INI_NULL_RESULT ' + call + ') = [HOBJECT ' + owner + ',HOBJECT ' + obj + ']',
        state + '.CURRENT = eps', state + '.FRAMES = eps', *written(state, mode), *common.public(state)]


def error(state, start, explicit=False, strict=False, default=False):
    call, owner, obj, out = 'pconfigcall_' + state, 'n_owner_' + state, 'n_object_' + state, state + '_error'
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
        out + '.ARRAYS[n_args_' + state + '].ITEMS = [ENTRY (KINT 0) (DIRECT (' + option + ')),ENTRY (KINT 1) (DIRECT (POBJECT ' + obj + '))]',
        '$node_children(' + out + ',HARRAY n_args_' + state + ') = [HOBJECT ' + obj + ']',
        '$objectprops_at(' + out + '.OBJECTPROPS,' + obj + ') = $objectprops_at(' + start + '.OBJECTPROPS,' + obj + ')',
        '$object_table_at(' + out + '.OBJECTTABLES,' + obj + ') = eps', '(HOBJECT ' + obj + ') <- ' + out + '.ALLOCATIONS',
        out + '.OBJECTS[' + owner + '] = INTRINSICCLOSURE INTRINSIC_INI_SET',
        out + '.EVENTS = ' + start + '.EVENTS' + (' ++ [DIAGNOSTIC "Deprecated" $config_ini_null_message(' + call + ') ' + call + '.LINE]' if default else ''),
        *unchanged(out, start, 'STORE ENV ERRORHANDLER USERCONSTANTS SELECTEDCALLS PRECISIONINI')]
    if explicit:
        values += ['$trace_array_field(' + out + ',n_wrapper_' + state + ',' + text('function') + ') = PSTRING ' + text('__invoke'),
            '$trace_array_field(' + out + ',n_wrapper_' + state + ',' + text('class') + ') = PSTRING ' + text('Closure'),
            '$trace_array_field(' + out + ',n_wrapper_' + state + ',' + text('type') + ') = PSTRING ' + text('->'),
            '$trace_array_field(' + out + ',n_wrapper_' + state + ',' + text('args') + ') = PARRAY n_wrapper_args_' + state,
            out + '.ARRAYS[n_wrapper_args_' + state + '].ITEMS = [ENTRY (KINT 0) (DIRECT PNULL),ENTRY (KINT 1) (DIRECT (POBJECT ' + obj + '))]',
            '$node_children(' + out + ',HARRAY n_wrapper_args_' + state + ') = [HOBJECT ' + obj + ']']
    return values + common.public(out)


def refusals(state):
    call, owner, obj = 'pconfigcall_' + state, 'n_owner_' + state, 'n_object_' + state
    return [*[v for v in shared.shared.refusals(state) if '.OWNER = (0)' not in v and '.NAMED = true' not in v],
        '~$config_ini_null_valid(' + state + ',' + call + '[.OWNER = eps])',
        '~$config_ini_null_valid(' + state + ',' + call + '[.OWNER = (' + obj + ')])',
        '~$config_ini_null_valid(' + state + ',' + call + '[.OWNER = (|' + state + '.OBJECTS|)])',
        '~$config_ini_null_valid(' + state + '[.OBJECTS[' + owner + '] = INTRINSICCLOSURE INTRINSIC_INI_GET],' + call + ')',
        '~$config_ini_named_stdclass_argument(' + state + ',' + call + ',2)']


def recovery(start, owner, old_precision, named):
    return [*reach('S_recovery', start, 3), 'S_recovery.TODO = (CONFIG_INVOKE pconfigcall_recovery) :: ptask_recovery*',
        'pconfigcall_recovery.OWNER = (' + owner + ')', 'pconfigcall_recovery.SELECTION = eps',
        'pconfigcall_recovery.INDEX = 2', ('' if named else '~') + 'pconfigcall_recovery.NAMED', 'pconfigcall_recovery.PACKS = eps',
        'pconfigcall_recovery.SENT = [NAMED_SENT (KNOWN pvalue_precision),NAMED_SENT (KNOWN pvalue_new_precision)]',
        '$string_bytes(pvalue_precision) = (' + text('precision') + ')', '$string_bytes(pvalue_new_precision) = (' + text('11') + ')',
        '$config_invoke_valid(S_recovery,pconfigcall_recovery)', '~$config_method_receiver(S_recovery,pconfigcall_recovery)',
        'S_recovery.OBJECTS[' + owner + '] = INTRINSICCLOSURE INTRINSIC_INI_SET',
        '~$config_ini_named_stdclass_argument(S_recovery,pconfigcall_recovery,0)',
        '~$config_ini_named_stdclass_argument(S_recovery,pconfigcall_recovery,1)',
        'S_recovery.PRECISIONINI = ' + text(old_precision), 'S_recovery.ERRORHANDLER.CALLBACK = eps',
        *common.public('S_recovery'), *common.step('S_recovered', 'S_recovery'),
        'S_recovered.TODO = ptask_recovery*', 'S_recovered.RESULT = KNOWN pvalue_old_precision',
        '$string_bytes(pvalue_old_precision) = (' + text(old_precision) + ')', 'S_recovered.PRECISIONINI = ' + text('11'),
        *unchanged('S_recovered', 'S_recovery', 'STORE ENV OBJECTS USERCONSTANTS SELECTEDCALLS EVENTS'), *common.public('S_recovered')]


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')', 'S_initial.COMPLETION = BUDGET']
    if name == 'owned-stdclass-values-default-and-explicit-return-keep-shared-trace-value':
        values += [*front('S_default', 'S_initial', 'positional'), '$config_ini_null_valid(S_default,pconfigcall_S_default)',
            '~$error_handler_eligible(S_default,8192)', '$compiled_read(S_default,porigin_S_default_0) = (PNULL)',
            *mark('S_default', 'n_object_S_default', '(PSTRING_CARRIER INTERNED_STRING ' + text('initial74') + ')'),
            *error('S_default', 'S_default', default=True), *front('S_true', 'S_default_error', 'reversed'),
            'n_owner_S_true = n_owner_S_default', 'n_object_S_true = n_object_S_default',
            '$config_method_receiver(S_true,pconfigcall_S_true)', '~$config_strict(S_true,pconfigcall_S_true)',
            *returned('S_true', '14', 'true', 'true74'), *error('S_true', 'S_true_resume', explicit=True),
            *refusals('S_true'), *budget('S_default'), *budget('S_true_resume'),
            *recovery('S_true_error', 'n_owner_S_default', '14', False),
            'S_final = $drive_steps(S_recovered,3000)', 'S_final.COMPLETION = NORMAL',
            '$test_outputs(S_final.EVENTS) = ' + text('B|' + VALUE_ERROR + '|99|T|H|8192|' + MESSAGE + '|' + VALUE_ERROR + '|E|W|N|I|I|true74|true74|99|1|Z|R|14|11')]
    else:
        strict = name == 'strict-owned-stdclass-option-before-weak-explicit-mixed-value-rejection'
        assert strict or name == 'captured-owned-stdclass-before-option-shared-write-and-live-owner-replacement'
        stage = 0 if strict else 1
        values += ['S_pre_found = $test_ini_owned_std_partial_seek(S_initial,' + str(stage) + ',3000)',
            r'S_pre_found.COMPLETION = NORMAL \/ S_pre_found.COMPLETION = BUDGET',
            'S_pre = S_pre_found[.COMPLETION = NORMAL]', '$test_ini_owned_std_partial(S_pre,' + str(stage) + ')',
            'S_pre.TODO = (CONFIG_ARGS pconfigcall_pre) :: ptask_pre*', 'pconfigcall_pre.OWNER = (n_owner_pre)',
            'pconfigcall_pre.SELECTION = eps', 'pconfigcall_pre.PACKS = eps', 'pconfigcall_pre.INDEX = 1',
            '$config_pending_valid(S_pre,pconfigcall_pre,false)', '$call_task_valid(S_pre,CONFIG_ARGS pconfigcall_pre)',
            'S_pre.OBJECTS[n_owner_pre] = INTRINSICCLOSURE INTRINSIC_INI_SET',
            '$lookup(S_pre.ENV,' + text('call') + ') = (n_call)', 'S_pre.STORE[n_call] = DEFINED (POBJECT n_owner_pre)',
            '$lookup(S_pre.ENV,' + text('keep') + ') = (n_keep)', 'S_pre.STORE[n_keep] = DEFINED (POBJECT n_owner_pre)',
            '$lookup(S_pre.ENV,' + text('replacement') + ') = (n_replacement)', 'S_pre.STORE[n_replacement] = DEFINED (POBJECT n_live)',
            'S_pre.OBJECTS[n_live] = INTRINSICCLOSURE INTRINSIC_INI_GET', 'n_live =/= n_owner_pre',
            '$lookup(S_pre.ENV,' + text('value') + ') = (n_value)', 'S_pre.STORE[n_value] = DEFINED (POBJECT n_captured)',
            'S_pre.OBJECTS[n_captured] = STDINSTANCE', 'n_captured =/= n_owner_pre',
            '$lookup(S_pre.ENV,' + text('objectKeep') + ') = (n_object_keep)', 'S_pre.STORE[n_object_keep] = DEFINED (POBJECT n_captured)',
            '$lookup(S_pre.ENV,' + text('old') + ') = (n_old)', 'S_pre.STORE[n_old] = DEFINED (POBJECT n_captured)',
            '$lookup(S_pre.ENV,' + text('effects') + ') = (n_effects)', 'S_pre.STORE[n_effects] = DEFINED (PINT 0)',
            '$lookup(S_pre.ENV,' + text('warnings') + ') = (n_warnings)', 'S_pre.STORE[n_warnings] = DEFINED (PINT 0)',
            '$lookup(S_pre.ENV,' + text('result') + ') = (n_result)', 'S_pre.STORE[n_result] = DEFINED (PINT 99)',
            'S_pre.PRECISIONINI = ' + text('14'), '$test_outputs(S_pre.EVENTS) = ' + text('B|'), *common.public('S_pre')]
        if strict:
            values += ['pconfigcall_pre.SENT = [NAMED_SENT (KNOWN PNULL)]', '~pconfigcall_pre.NAMED',
                '$config_nodes(pconfigcall_pre) = [HOBJECT n_owner_pre]',
                *mark('S_pre', 'n_captured', '(PSTRING_CARRIER INTERNED_STRING ' + text('strict74') + ')')]
        else:
            values += ['pconfigcall_pre.SENT = [NAMED_HOLE,NAMED_SENT (KNOWN (POBJECT n_captured))]', 'pconfigcall_pre.NAMED',
                '$config_nodes(pconfigcall_pre) = [HOBJECT n_owner_pre,HOBJECT n_captured]',
                '$task_nodes(CONFIG_ARGS pconfigcall_pre) = [HOBJECT n_owner_pre,HOBJECT n_captured]',
                *mark('S_pre', 'n_captured', 'pvalue_captured'),
                'pvalue_captured = PSTRING_CARRIER (REQUEST_STRING n_mark) ' + text('owned-stdclass74'),
                '$string_carrier_valid(S_pre,pvalue_captured)']
        values += [*front('S', 'S_pre', 'positional' if strict else 'reversed'),
            'n_owner_S = n_owner_pre', 'n_object_S = n_captured',
            'pconfigcall_S = pconfigcall_pre[.INDEX = 2][.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (POBJECT n_captured))]]',
            'S.STORE[n_call] = DEFINED (POBJECT n_live)', 'S.STORE[n_keep] = DEFINED (POBJECT n_owner_pre)',
            'S.STORE[n_object_keep] = DEFINED (POBJECT n_captured)', 'S.STORE[n_old] = DEFINED (POBJECT n_captured)',
            'S.STORE[n_value] = DEFINED (PINT 0)', 'S.STORE[n_result] = DEFINED (PINT 99)',
            'S.STORE[n_effects] = DEFINED (PINT 1)', 'S.STORE[n_warnings] = DEFINED (PINT 0)',
            '~$config_method_receiver(S,pconfigcall_S)']
        if strict:
            values += [*mark('S', 'n_captured', '(PSTRING_CARRIER INTERNED_STRING ' + text('strict-value74') + ')'),
                '$compiled_read(S,porigin_S_0) = (PNULL)', '$compiled_read(S,porigin_S_1) = eps',
                '$config_strict(S,pconfigcall_S)', '~$config_ini_null_valid(S,pconfigcall_S)',
                'S.PRECISIONINI = ' + text('9'), '$test_outputs(S.EVENTS) = ' + text('B|V|'),
                *error('S', 'S', strict=True), *front('S_mixed', 'S_error', 'mixed'), 'n_owner_S_mixed = n_owner_pre',
                'n_object_S_mixed =/= n_captured', '$objectprops_at(S_mixed.OBJECTPROPS,n_object_S_mixed) = (eps)',
                '$config_method_receiver(S_mixed,pconfigcall_S_mixed)', '$exit_strict(S_mixed,pconfigcall_S_mixed.SITE)',
                '~$config_strict(S_mixed,pconfigcall_S_mixed)',
                *returned('S_mixed', '8', 'true', 'unused74', empty=True), *error('S_mixed', 'S_mixed_resume', explicit=True),
                *budget('S_pre'), *budget('S'), *budget('S_mixed_resume'),
                'S_final = $drive_steps(S_mixed_error,3000)', 'S_final.COMPLETION = NORMAL',
                '$test_outputs(S_final.EVENTS) = ' + text('B|V|' + OPTION_ERROR + '|99|1|0|S|strict-value74|0|9|E|H|8192|' + MESSAGE + '|' + VALUE_ERROR + '|99|1|1|8|Z')]
        else:
            values += [*mark('S', 'n_captured', '(PSTRING_CARRIER INTERNED_STRING ' + text('option74') + ')'),
                '$compiled_read(S,porigin_S_0) = eps', '$compiled_read(S,porigin_S_1) = eps',
                '~$config_strict(S,pconfigcall_S)', 'S.PRECISIONINI = ' + text('7'), '$test_outputs(S.EVENTS) = ' + text('B|O|'),
                *returned('S', '8', 'false', 'handler74'),
                'S_return.STORE[n_keep] = DEFINED (POBJECT n_owner_pre)', 'S_return.STORE[n_old] = DEFINED (POBJECT n_captured)',
                'S_return.STORE[n_object_keep] = DEFINED (POBJECT n_captured)',
                'S_return.STORE[n_result] = DEFINED (PINT 99)', 'S_return.STORE[n_effects] = DEFINED (PINT 1)',
                '$heap_count(HOBJECT n_captured,$tasks_nodes(S_return.TODO)) = 1',
                '$heap_count(HOBJECT n_owner_pre,$tasks_nodes(S_return.TODO)) = 1',
                *error('S', 'S_resume'), *refusals('S'), *budget('S_pre'), *budget('S_resume'),
                *recovery('S_error', 'n_owner_pre', '8', True),
                'S_final = $drive_steps(S_recovered,3000)', 'S_final.COMPLETION = NORMAL',
                '$test_outputs(S_final.EVENTS) = ' + text('B|O|W|8192|' + MESSAGE + '|' + VALUE_ERROR + '|99|1|1|constant|precision|handler-value74|S|handler74|handler74|8|Z|R|8|11')]
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
