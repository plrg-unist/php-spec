#!/usr/bin/env python3
"""Missing INI VALUE reads keep NULL across Warning callbacks and later reception."""
import json
import os
from pathlib import Path

import ini_set_null_option_protocol as shared
import ini_set_undefined_value_sources as sources

driver, common, text, b64 = shared.driver, shared.common, shared.text, shared.b64
MESSAGE = shared.MESSAGE
WARNING = 'Undefined variable $missing'
OPTION_ERROR = 'ini_set(): Argument #1 ($option) must be of type string, null given'
PREFIX = shared.PREFIX + r"""
dec $test_ini_read_front(pstate, nat) : bool
def $test_ini_read_front(S, 0) = true
  -- if S.TODO = (CONFIG_SEND pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET /\ pconfigcall.INDEX = 1
  -- if S.RESULT = VARIABLE $ptascii("missing") z
def $test_ini_read_front(S, 1) = true
  -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = ERROR_READ_RESULT perrorread
  -- if perrorread.ORIGINAL = CONFIG_SEND pconfigcall
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_ini_read_front(S, n_stage) = false -- otherwise
dec $test_ini_read_seek(pstate, nat, nat) : pstate
def $test_ini_read_seek(S, n_stage, 0) = S
def $test_ini_read_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_ini_read_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_ini_read_seek(S, n_stage, n) = $test_ini_read_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_ini_read_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def reach(state, start, stage):
    return [state + '_found = $test_ini_read_seek(' + start + ',' + str(stage) + ',3000)',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_ini_read_front(' + state + ',' + str(stage) + ')']


def cv(state, name, value, suffix):
    cell = 'n_' + name + '_' + suffix
    return ['$lookup(' + state + '.ENV,' + text(name) + ') = (' + cell + ')',
        state + '.STORE[' + cell + '] = DEFINED (' + value + ')']


def current_array(state, value, suffix):
    array = 'n_array_' + suffix
    return [*cv(state, 'missing', 'PARRAY ' + array, suffix),
        '(HARRAY ' + array + ') <- ' + state + '.ALLOCATIONS',
        state + '.ARRAYS[' + array + '].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT ' + str(value) + '))]',
        '$node_children(' + state + ',HARRAY ' + array + ') = eps']


def refusals(owned):
    values = []
    for label, field in (
            ('kind', '.KIND = INTRINSIC_INI_GET'), ('index0', '.INDEX = 0'),
            ('index2', '.INDEX = 2'), ('named', '.NAMED = true'),
            ('site', '.SITE = PORIGIN 0 eps'), ('line', '.LINE = $(pconfigcall.LINE + 1)'),
            ('empty', '.SENT = eps'), ('option', '.SENT = [NAMED_SENT (KNOWN (PBOOL false))]'),
            ('extra', '.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN PNULL)]'),
            ('pack', '.PACKS = [{INDEX 0,SITE pconfigcall.SITE,LINE pconfigcall.LINE,ARRAY 0,ITEMS eps}]'),
            ('owner', '.OWNER = ' + ('eps' if owned else '(|S.OBJECTS|)'))):
        values += ['pconfigcall_bad_' + label + ' = pconfigcall[' + field + ']',
            'perrorread_bad_' + label + ' = perrorread[.ORIGINAL = CONFIG_SEND pconfigcall_bad_' + label + '][.TASK = CONFIG_SEND pconfigcall_bad_' + label + ']',
            '~$error_read_valid(S,perrorread_bad_' + label + ')']
    for field in ('.RESULT = KNOWN (PINT 1)', '.TASK = DISCARD', '.NAME = ' + text('option'),
            '.LINE = $(z_value + 1)', '.INPUT = KNOWN PNULL'):
        values += ['~$error_read_valid(S,perrorread[' + field + '])']
    values += ['~$error_read_valid(S[.CODE = eps],perrorread)',
        '~$error_read_valid(S[.ORIGIN = eps],perrorread)',
        '$error_read_plan(S[.RESULT = KNOWN PNULL]) = eps',
        '~$error_read_source(S,perrorread[.INPUT = VARIABLE ' + text('option') + ' z_value][.NAME = ' + text('option') + '])']
    if owned:
        values += ['~$error_read_valid(S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_setter)],perrorread)',
            '~$error_read_valid(S,perrorread[.ORIGINAL = CONFIG_SEND pconfigcall[.OWNER = (n_getter)]][.TASK = CONFIG_SEND pconfigcall[.OWNER = (n_getter)]])']
    return values


def recovery(start, owned, strict, precision):
    values = [*shared.reach('S_recovery', start, 3),
        'S_recovery.TODO = (CONFIG_INVOKE pconfigcall_recovery) :: ptask_recovery*',
        'pconfigcall_recovery.KIND = INTRINSIC_INI_SET', 'pconfigcall_recovery.INDEX = 2',
        'pconfigcall_recovery.PACKS = eps', '~pconfigcall_recovery.NAMED',
        'pconfigcall_recovery.SENT = [NAMED_SENT (KNOWN pvalue_key),NAMED_SENT (KNOWN pvalue_value)]',
        '$string_bytes(pvalue_key) = (' + text('precision') + ')',
        '$string_bytes(pvalue_value) = (' + text('11') + ')',
        '$config_invoke_valid(S_recovery,pconfigcall_recovery)',
        '$dynamic_scalar_define_arguments(S_recovery,pconfigcall_recovery,0)',
        ('' if strict else '~') + '$config_strict(S_recovery,pconfigcall_recovery)',
        'S_recovery.ERRORHANDLER.CALLBACK = eps', 'S_recovery.PRECISIONINI = ' + text(precision)]
    if owned:
        values += ['pconfigcall_recovery.OWNER = (n_setter)', 'pconfigcall_recovery.SELECTION = eps']
    else:
        values += ['pconfigcall_recovery.OWNER = eps', 'pconfigcall_recovery.SELECTION = (n_recovery_selection)',
            'S_recovery.SELECTEDCALLS[n_recovery_selection].OWNER = eps']
    values += ['pconfigcall_recovery_null = pconfigcall_recovery[.INDEX = 1][.SENT = [NAMED_SENT (KNOWN PNULL)]]',
        '$config_pending_valid(S_recovery,pconfigcall_recovery_null,false)',
        '~$config_ini_named_stdclass_argument(S_recovery,pconfigcall_recovery_null,0)',
        'perrorread_recovery = perrorread[.ORIGINAL = CONFIG_SEND pconfigcall_recovery_null][.TASK = CONFIG_SEND pconfigcall_recovery_null]',
        '~$error_read_source(S_recovery,perrorread_recovery)',
        *common.public('S_recovery'), *common.step('S_recovered', 'S_recovery'),
        'S_recovered.TODO = ptask_recovery*', 'S_recovered.RESULT = KNOWN pvalue_old_precision',
        '$string_bytes(pvalue_old_precision) = (' + text(precision) + ')',
        'S_recovered.PRECISIONINI = ' + text('11'), 'S_recovered.PRECISIONMODIFIED',
        *common.public('S_recovered')]
    return values


def checks(program, path, name):
    ordinary = name == 'strict-owned-ini-undefined-value-warning-before-null-option-type-error'
    explicit = name == 'strict-explicit-ini-undefined-value-false-warning-then-weak-null-reception'
    owned = ordinary or explicit
    assert owned or name == 'selected-ini-undefined-value-warning-then-null-deprecated-keeps-fallback'
    initial_value, final_value = (61, 61) if ordinary else ((67, 69) if explicit else (51, 53))
    roots = '[HOBJECT n_setter]' if owned else 'eps'
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *reach('S', 'S_initial', 0),
        'S.TODO = (CONFIG_SEND pconfigcall) :: ptask_tail*',
        'pconfigcall.KIND = INTRINSIC_INI_SET', 'pconfigcall.INDEX = 1',
        'pconfigcall.PACKS = eps', '~pconfigcall.NAMED',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN PNULL)]', '~$pipe_site(S,pconfigcall.SITE)',
        '$intrinsic_count(S,pconfigcall.SITE) = (2)', '$config_pending_valid(S,pconfigcall,false)',
        '$intrinsic_argument(S,pconfigcall.SITE,0) = ((expression_option,false,eps,porigin_option,z_option))',
        '$intrinsic_argument(S,pconfigcall.SITE,1) = ((expression_value,false,eps,porigin_value,z_value))',
        '$compiled_read(S,porigin_option) = eps', '$compiled_read(S,porigin_value) = eps',
        'S.RESULT = VARIABLE ' + text('missing') + ' z_value',
        '$error_missing_operand(S,S.RESULT)', '~$error_simple_read(CONFIG_SEND pconfigcall)',
        '$error_read_shape(CONFIG_SEND pconfigcall,S.RESULT,S.BASE) = eps',
        '$error_read_state_shape(S,CONFIG_SEND pconfigcall,S.RESULT,S.BASE) = (perrorread)',
        'perrorread.ORIGINAL = CONFIG_SEND pconfigcall', 'perrorread.TASK = CONFIG_SEND pconfigcall',
        'perrorread.INPUT = S.RESULT', 'perrorread.BASE = S.BASE',
        'perrorread.NAME = ' + text('missing'), 'perrorread.LINE = z_value',
        'perrorread.RESULT = KNOWN PNULL', '$error_read_source(S,perrorread)',
        '$error_read_valid(S,perrorread)', '$error_read_plan(S) = (perrorread)',
        '$config_nodes(pconfigcall) = ' + roots, '$task_nodes(ERROR_READ_RESULT perrorread) = ' + roots,
        'S.CURRENT = eps', 'S.FRAMES = eps', '$test_outputs(S.EVENTS) = ' + text('B|'),
        *cv('S', 'result', 'PINT 99', 'initial'), *cv('S', 'warnings', 'PINT 0', 'initial'),
        *common.public('S')]
    if owned:
        values += ['pconfigcall.OWNER = (n_setter)', 'pconfigcall.SELECTION = eps',
            'S.OBJECTS[n_setter] = INTRINSICCLOSURE INTRINSIC_INI_SET', '(HOBJECT n_setter) <- S.ALLOCATIONS',
            *cv('S', 'keep', 'POBJECT n_setter', 'initial'),
            *cv('S', 'replacement', 'POBJECT n_getter', 'initial'),
            'S.OBJECTS[n_getter] = INTRINSICCLOSURE INTRINSIC_INI_GET', 'n_setter =/= n_getter',
            ('' if ordinary else '~') + '$config_strict(S,pconfigcall)',
            ('' if explicit else '~') + '$config_method_receiver(S,pconfigcall)']
    else:
        values += ['pconfigcall.OWNER = eps', 'pconfigcall.SELECTION = (n_selection)',
            'S.SELECTEDCALLS[n_selection].OWNER = eps', 'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_INI_SET',
            '~$config_strict(S,pconfigcall)', '~$config_method_receiver(S,pconfigcall)']
    values += [*refusals(owned), *shared.budget('S'), *common.step('S_warning', 'S'),
        'S_warning.TODO = (ERROR_HANDLER_INVOKE perrorcall_warning) :: ptask_tail*',
        'perrorcall_warning.RESUME = ERROR_READ_RESULT perrorread', 'perrorcall_warning.LEVEL = 2',
        'perrorcall_warning.LINE = z_value', 'perrorcall_warning.MESSAGE = ' + text(WARNING),
        'perrorcall_warning.EVENT = WARNING ' + text('missing') + ' z_value',
        '$error_call_valid(S_warning,perrorcall_warning)', 'S_warning.EVENTS = S.EVENTS',
        '$task_nodes(perrorcall_warning.RESUME) = ' + roots, *common.public('S_warning'),
        *reach('S_warning_return', 'S_warning', 1),
        'S_warning_return.TODO = (ERROR_HANDLER_RESULT perrorcall_warning_return) :: ptask_tail*',
        'perrorcall_warning_return[.TARGET = eps] = perrorcall_warning',
        'S_warning_return.RESULT = KNOWN (PBOOL ' + ('false' if explicit else 'true') + ')',
        'S_warning_return.CURRENT = eps', 'S_warning_return.FRAMES = eps',
        '$call_task_valid(S_warning_return,ERROR_HANDLER_RESULT perrorcall_warning_return)',
        '$error_read_valid(S_warning_return,perrorread)',
        *current_array('S_warning_return', initial_value, 'warning'),
        *cv('S_warning_return', 'warningKeep', 'PARRAY n_array_warning', 'warning'),
        *cv('S_warning_return', 'option', 'PSTRING_CARRIER INTERNED_STRING ' + text('precision'), 'warning'),
        *cv('S_warning_return', 'warnings', 'PINT 1', 'warning'),
        'S_warning_return.PRECISIONINI = ' + text('9' if ordinary else '14'),
        '~$destructor_operational(S_warning_return)', *common.public('S_warning_return')]
    if owned:
        values += [*cv('S_warning_return', 'call', 'POBJECT n_getter', 'warning'),
            'S_warning_return.OBJECTS[n_setter] = S.OBJECTS[n_setter]']
    else:
        values += [*cv('S_warning_return', 'call', 'PSTRING_CARRIER INTERNED_STRING ' + text('ini_get'), 'warning'),
            'S_warning_return.SELECTEDCALLS[n_selection] = S.SELECTEDCALLS[n_selection]']
    reported = '$error_default(S_warning_return,perrorcall_warning_return.EVENT,2)' if explicit else 'S_warning_return'
    values += ['S_warning_reported = ' + reported,
        'S_warning_expected = $error_handler_restore(S_warning_reported[.TODO = (ERROR_READ_RESULT perrorread) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)],perrorcall_warning_return.CALLBACK)',
        *common.step('S_resume', 'S_warning_return'), 'S_resume = S_warning_expected',
        'S_resume.TODO = (ERROR_READ_RESULT perrorread) :: ptask_tail*',
        '$error_read_valid(S_resume,perrorread)',
        '~$error_missing_operand(S_resume,perrorread.INPUT)', 'S_resume.STORE[n_missing_warning] = DEFINED (PARRAY n_array_warning)',
        '~$error_read_valid(S_resume,perrorread[.RESULT = KNOWN (PARRAY n_array_warning)])',
        *common.public('S_resume'),
        'S_unreceived = S_resume[.TODO = (CONFIG_SEND pconfigcall) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = perrorread.BASE]',
        '~$config_result_valid(S_unreceived)',
        'pconfigcall_complete = pconfigcall[.INDEX = 2][.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN PNULL)]]',
        *common.step('S_restored', 'S_resume'),
        'S_restored = S_resume[.TODO = (CONFIG_ARGS pconfigcall_complete) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$error_read_plan(S_restored) = eps', *common.public('S_restored'),
        *common.step('S_invoke', 'S_restored'),
        'S_invoke.TODO = (CONFIG_INVOKE pconfigcall_complete) :: ptask_tail*',
        '$config_invoke_valid(S_invoke,pconfigcall_complete)',
        '$config_nodes(pconfigcall_complete) = ' + roots, *common.public('S_invoke'), *shared.budget('S_resume')]
    if ordinary:
        values += ['$config_strict(S_invoke,pconfigcall_complete)', '~$config_ini_null_valid(S_invoke,pconfigcall_complete)',
            *common.step('S_error', 'S_invoke'), 'S_error.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
            '$object_name(S_error,n_error) = ' + text('TypeError'),
            '$string_bytes($throwable_field(S_error,n_error,"message")) = (' + text(OPTION_ERROR) + ')',
            '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
            'S_error.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_api))]',
            '$trace_array_field(S_error,n_api,' + text('function') + ') = PSTRING ' + text('ini_set'),
            '$trace_array_field(S_error,n_api,' + text('args') + ') = PARRAY n_args',
            'S_error.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT PNULL),ENTRY (KINT 1) (DIRECT PNULL)]',
            '$node_children(S_error,HARRAY n_args) = eps', 'S_error.EVENTS = S_invoke.EVENTS',
            'S_error.STORE = S_invoke.STORE', *common.public('S_error')]
        precision, ending = '9', 'S_error'
        expected = 'B|W|2|' + WARNING + '|' + OPTION_ERROR + '|I|N|N|99|1|61|G|precision|9|Z|R|9|11'
    else:
        dep_result = 'true' if explicit else 'false'
        precision = '10' if explicit else '8'
        values += ['$config_ini_null_valid(S_invoke,pconfigcall_complete)', '~$config_strict(S_invoke,pconfigcall_complete)',
            *common.step('S_deprecated', 'S_invoke'),
            'S_deprecated.TODO = (ERROR_HANDLER_INVOKE perrorcall_deprecated) :: ptask_tail*',
            'perrorcall_deprecated.RESUME = CONFIG_INI_NULL_RESULT pconfigcall_complete',
            'perrorcall_deprecated.LEVEL = 8192', 'perrorcall_deprecated.MESSAGE = ' + text(MESSAGE),
            '$error_call_valid(S_deprecated,perrorcall_deprecated)',
            *shared.reach('S_dep_entered', 'S_deprecated', 1), 'S_dep_entered.CURRENT = (pcallcontext_dep)',
            '$error_context_valid(S_dep_entered,pcallcontext_dep)',
            '$error_handler_trace_values(S_dep_entered,pcallcontext_dep,pconfigcall_complete) = [PNULL,PNULL]',
            *common.public('S_dep_entered'), *shared.reach('S_dep_return', 'S_dep_entered', 2),
            'S_dep_return.TODO = (ERROR_HANDLER_RESULT perrorcall_dep_return) :: ptask_tail*',
            'perrorcall_dep_return[.TARGET = eps] = perrorcall_deprecated',
            'S_dep_return.RESULT = KNOWN (PBOOL ' + dep_result + ')',
            *cv('S_dep_return', 'warnings', 'PINT 1', 'dep'),
            *cv('S_dep_return', 'deprecations', 'PINT 1', 'dep'),
            *current_array('S_dep_return', final_value, 'dep'), 'n_array_dep =/= n_array_warning',
            *cv('S_dep_return', 'warningKeep', 'PARRAY n_array_warning', 'dep'),
            'S_dep_return.ARRAYS[n_array_warning] = S_warning_return.ARRAYS[n_array_warning]',
            'S_dep_return.PRECISIONINI = ' + text(precision), '~$destructor_operational(S_dep_return)',
            '$config_ini_null_valid(S_dep_return,pconfigcall_complete)', *common.public('S_dep_return'),
            'S_dep_reported = ' + ('S_dep_return' if explicit else '$error_default(S_dep_return,perrorcall_dep_return.EVENT,8192)'),
            'S_dep_expected = $error_handler_restore(S_dep_reported[.TODO = (CONFIG_INI_NULL_RESULT pconfigcall_complete) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)],perrorcall_dep_return.CALLBACK)',
            *common.step('S_dep_resume', 'S_dep_return'), 'S_dep_resume = S_dep_expected',
            '$call_task_valid(S_dep_resume,CONFIG_INI_NULL_RESULT pconfigcall_complete)',
            *common.public('S_dep_resume'), *common.step('S_value', 'S_dep_resume'),
            'S_value.TODO = ptask_tail*', 'S_value.RESULT = KNOWN (PBOOL false)',
            'S_value.STORE = S_dep_resume.STORE', 'S_value.EVENTS = S_dep_resume.EVENTS',
            *common.public('S_value'), *shared.budget('S_dep_resume')]
        ending = 'S_value'
        expected = 'B|W|2|' + WARNING + '|D|8192|' + MESSAGE + '|F|Z|1|1|' + str(final_value) + '|' + str(initial_value)
        expected += '|G|precision|10|R|10|11' if explicit else '|constant|changed|8|R|8|11'
    values += [*recovery(ending, owned, owned, precision),
        'S_final = $drive_steps(S_recovered,3000)', 'S_final.COMPLETION = NORMAL',
        'S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.ERRORHANDLER.CALLBACK = eps', 'S_final.USERCONSTANTS = eps',
        '$test_outputs(S_final.EVENTS) = ' + text(expected), *common.public('S_final')]
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
