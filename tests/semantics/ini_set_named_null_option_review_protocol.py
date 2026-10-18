#!/usr/bin/env python3
"""Reversed named NULL INI arguments retain normalized captures across a throw."""
import json
import os
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import ini_set_named_null_option_review_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64
MESSAGE = 'ini_set(): Passing null to parameter #1 ($option) of type string is deprecated'
PREFIX = r"""
dec $test_ini_named_null_review_front(pstate, nat) : bool
def $test_ini_named_null_review_front(S, 0) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN PNULL), NAMED_SENT (KNOWN pvalue)]
def $test_ini_named_null_review_front(S, 1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_call(S,pcallcontext) = (perrorcall)
  -- if perrorcall.RESUME = CONFIG_INI_NULL_RESULT pconfigcall
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_ini_named_null_review_front(S, 2) = true
  -- if S.TODO = (THROW_VALUE porigin z) :: ptask_body*
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_call(S,pcallcontext) = (perrorcall)
  -- if perrorcall.RESUME = CONFIG_INI_NULL_RESULT pconfigcall
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_ini_named_null_review_front(S, 3) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = CONFIG_INI_NULL_RESULT pconfigcall
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_ini_named_null_review_front(S, 4) = true
  -- if S.TODO = (CONFIG_ARGS pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
  -- if pconfigcall.INDEX = 1
  -- if pconfigcall.NAMED
  -- if pconfigcall.SENT = [NAMED_HOLE,NAMED_SENT (KNOWN pvalue)]
def $test_ini_named_null_review_front(S, n_stage) = false -- otherwise
dec $test_ini_named_null_review_seek(pstate, nat, nat) : pstate
def $test_ini_named_null_review_seek(S, n_stage, 0) = S
def $test_ini_named_null_review_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_ini_named_null_review_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_ini_named_null_review_seek(S, n_stage, n) = $test_ini_named_null_review_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_ini_named_null_review_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def reach(state, start, stage):
    return [state + '_found = $test_ini_named_null_review_seek(' + start + ',' + str(stage) + ',3000)',
        state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_ini_named_null_review_front(' + state + ',' + str(stage) + ')']


def unchanged(after, before, fields):
    return [after + '.' + field + ' = ' + before + '.' + field for field in fields.split()]


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)',
        state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)',
        state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def checks(program, path, name):
    assert name == 'selected-reversed-named-null-option-throw-keeps-early-request'
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *reach('S_value', 'S_initial', 4),
        'S_value.TODO = (CONFIG_ARGS pconfigcall_value) :: ptask_value*',
        'pconfigcall_value.INDEX = 1', 'pconfigcall_value.NAMED',
        'pconfigcall_value.SENT = [NAMED_HOLE,NAMED_SENT (KNOWN pvalue_captured)]',
        'pvalue_captured = PSTRING_CARRIER (REQUEST_STRING n_candidate) ' + text('early-value63'),
        '$string_carrier_valid(S_value,pvalue_captured)',
        '$call_task_valid(S_value,CONFIG_ARGS pconfigcall_value)',
        '~$config_ini_null_valid(S_value,pconfigcall_value)',
        '$lookup(S_value.ENV,' + text('effects') + ') = (n_effects)',
        'S_value.STORE[n_effects] = DEFINED (PINT 1)',
        'S_value.PRECISIONINI = ' + text('14'),
        '$test_outputs(S_value.EVENTS) = ' + text('B|V|'),
        *reach('S', 'S_value', 0),
        'S.TODO = (CONFIG_INVOKE pconfigcall_S) :: ptask_S*',
        'pconfigcall_S.KIND = INTRINSIC_INI_SET', 'pconfigcall_S.INDEX = 2',
        'pconfigcall_S.OWNER = eps', 'pconfigcall_S.PACKS = eps', 'pconfigcall_S.NAMED',
        'pconfigcall_S.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN pvalue_captured)]',
        'pconfigcall_S = pconfigcall_value[.INDEX = 2][.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN pvalue_captured)]]',
        '$string_carrier_valid(S,pvalue_captured)', '$config_ini_quiet_value(S,pvalue_captured)',
        '$config_invoke_valid(S,pconfigcall_S)', '$config_ini_null_valid(S,pconfigcall_S)',
        '~$config_strict(S,pconfigcall_S)', '~$config_ini_unary_kind(pconfigcall_S.KIND)',
        'pconfigcall_S.SELECTION = (n_selection)', '$(n_selection < |S.SELECTEDCALLS|)',
        'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_INI_SET',
        '$intrinsic_count(S,pconfigcall_S.SITE) = (2)',
        '$intrinsic_argument(S,pconfigcall_S.SITE,0) = ((expression_value,false,preqbytes_value?,porigin_value,z_value))',
        'preqbytes_value? = (' + text('value') + ')',
        '$config_destination(INTRINSIC_INI_SET,preqbytes_value?,0) = (1)',
        '$intrinsic_argument(S,pconfigcall_S.SITE,1) = ((expression_option,false,preqbytes_option?,porigin_option,z_option))',
        'preqbytes_option? = (' + text('option') + ')',
        '$config_destination(INTRINSIC_INI_SET,preqbytes_option?,1) = (0)',
        '$dynamic_scalar_define_arguments(S,pconfigcall_S,0)',
        '$lookup(S.ENV,' + text('result') + ') = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 99)',
        '$lookup(S.ENV,' + text('effects') + ') = (n_effects)', 'S.STORE[n_effects] = DEFINED (PINT 2)',
        '$lookup(S.ENV,' + text('warnings') + ') = (n_warnings)', 'S.STORE[n_warnings] = DEFINED (PINT 0)',
        '$lookup(S.ENV,' + text('saved') + ') = (n_saved)', 'S.STORE[n_saved] = DEFINED PNULL',
        'S.PRECISIONINI = ' + text('7'), 'S.USERCONSTANTS = eps',
        '$test_outputs(S.EVENTS) = ' + text('B|V|O|'), *common.public('S')]
    for variable, spelling in [('call', 'ini_restore'), ('option', 'option-live63'), ('value', 'option-value63')]:
        values += ['$lookup(S.ENV,' + text(variable) + ') = (n_' + variable + ')',
            'S.STORE[n_' + variable + '] = DEFINED pvalue_before_' + variable,
            '$string_bytes(pvalue_before_' + variable + ') = (' + text(spelling) + ')']
    for variable, spelling in [('call', 'ini_get'), ('option', 'value-option63'), ('value', 'value-live63')]:
        values += ['S_value.STORE[n_' + variable + '] = DEFINED pvalue_partial_' + variable,
            '$string_bytes(pvalue_partial_' + variable + ') = (' + text(spelling) + ')']
    values += [*common.step('S_dispatch', 'S'),
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_deprecated) :: ptask_S*',
        'perrorcall_deprecated.RESUME = CONFIG_INI_NULL_RESULT pconfigcall_S',
        'perrorcall_deprecated.LEVEL = 8192',
        'perrorcall_deprecated.MESSAGE = $config_ini_null_message(pconfigcall_S)',
        'perrorcall_deprecated.MESSAGE = ' + text(MESSAGE),
        'perrorcall_deprecated.EVENT = DIAGNOSTIC "Deprecated" perrorcall_deprecated.MESSAGE pconfigcall_S.LINE',
        'perrorcall_deprecated.SITE = pconfigcall_S.SITE', 'perrorcall_deprecated.LINE = pconfigcall_S.LINE',
        '$error_call_valid(S_dispatch,perrorcall_deprecated)',
        '$call_task_valid(S_dispatch,ERROR_HANDLER_INVOKE perrorcall_deprecated)',
        *unchanged('S_dispatch', 'S', 'STORE ENV ARRAYS OBJECTS OBJECTPROPS USERCONSTANTS STRINGDATA EVENTS SELECTEDCALLS AUTOLOAD CLASSNAMES CLASSCONSTANTCACHE PRECISIONINI PRECISIONMODIFIED'),
        *common.public('S_dispatch'), *reach('S_handler', 'S_dispatch', 1),
        'S_handler.CURRENT = (pcallcontext_handler)',
        '$error_context_valid(S_handler,pcallcontext_handler)',
        '$error_context_trigger(S_handler,pcallcontext_handler) = (pconfigcall_S)',
        '$error_handler_trace_values(S_handler,pcallcontext_handler,pconfigcall_S) = [PNULL,pvalue_captured]',
        *common.public('S_handler'), *reach('S_throw', 'S_handler', 2),
        'S_throw.TODO = (THROW_VALUE porigin_throw z_throw) :: ptask_body*',
        'S_throw.CURRENT = (pcallcontext_handler)', 'S_throw.FRAMES = pframe_call :: pframe_outer*',
        'pframe_call.CONTEXT = S.CURRENT', 'pframe_call.LOCALS = ($active_table(S))',
        'pframe_call.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_S*',
        'perrorcall_entered.RESUME = perrorcall_deprecated.RESUME',
        'S_throw.STORE[n_saved] = DEFINED (POBJECT n_exception)',
        'S_throw.OBJECTS[n_exception] = THROWABLE pthrowable', 'pthrowable.KIND = "Exception"',
        '$string_bytes($throwable_field(S_throw,n_exception,"message")) = (' + text('named63-stop') + ')',
        '$throwable_field(S_throw,n_exception,"previous") = PNULL',
        '$throwable_field(S_throw,n_exception,"trace") = PARRAY n_trace',
        'S_throw.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_handler)),ENTRY (KINT 1) (DIRECT (PARRAY n_api)),ENTRY (KINT 2) (DIRECT (PARRAY n_caller))]',
        '$trace_array_field(S_throw,n_handler,' + text('function') + ') = PSTRING ' + text('iniNamedReviewDeprecated63'),
        '$trace_array_field(S_throw,n_api,' + text('function') + ') = PSTRING ' + text('ini_set'),
        '$trace_array_field(S_throw,n_api,' + text('line') + ') = PINT pconfigcall_S.LINE',
        '$trace_array_field(S_throw,n_api,' + text('args') + ') = PARRAY n_args',
        'S_throw.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT PNULL),ENTRY (KINT 1) (DIRECT pvalue_captured)]',
        '$node_children(S_throw,HARRAY n_args) = eps',
        '$trace_array_field(S_throw,n_caller,' + text('function') + ') = PSTRING ' + text('iniNamedReviewCaller63'),
        'S_throw.STORE[n_result] = DEFINED (PINT 99)', 'S_throw.STORE[n_effects] = DEFINED (PINT 2)',
        'S_throw.STORE[n_warnings] = DEFINED (PINT 1)',
        'S_throw.PRECISIONINI = ' + text('10'), 'S_throw.PRECISIONMODIFIED',
        'S_throw.USERCONSTANTS = [puserconstant_sibling]',
        'puserconstant_sibling.NAME = ' + text('SOURCE63PEER'), 'puserconstant_sibling.VALUE = PINT 2053',
        'puserconstant_sibling.CLASS = PVSCALAR',
        '$test_outputs(S_throw.EVENTS) = ' + text('B|V|O|D|8192|' + MESSAGE + '|'),
        *unchanged('S_throw', 'S', 'AUTOLOAD CLASSNAMES CLASSCONSTANTCACHE FILEINCLUDEPATH'),
        *common.public('S_throw'), *common.step('S_throwing', 'S_throw'),
        'S_throwing.TODO = (THROW_SEARCH n_exception) :: ptask_body*',
        *reach('S_thrown', 'S_throwing', 3),
        'S_thrown.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_S*',
        'S_thrown.CURRENT = S.CURRENT', 'S_thrown.ENV = S.ENV',
        'S_thrown.OBJECTS[n_exception] = THROWABLE pthrowable',
        'S_thrown.STORE[n_saved] = DEFINED (POBJECT n_exception)',
        'S_thrown.STORE[n_result] = DEFINED (PINT 99)', 'S_thrown.USERCONSTANTS = [puserconstant_sibling]',
        'S_thrown.PRECISIONINI = ' + text('10'), '$config_ini_null_valid(S_thrown,pconfigcall_S)',
        *common.public('S_thrown'),
        'S_discard = S_thrown[.TODO = (THROW_SEARCH n_exception) :: ptask_S*]',
        'S_expected = $error_handler_restore($identity_read_discard(S_discard,perrorcall_entered.RESUME),perrorcall_entered.CALLBACK)',
        '$error_read_discard(S_expected,perrorcall_entered.RESUME) = S_expected',
        *common.step('S_after', 'S_thrown'), 'S_after = S_expected',
        'S_after.TODO = (THROW_SEARCH n_exception) :: ptask_S*',
        '$throwable_live(S_after,n_exception)', 'S_after.STORE[n_result] = DEFINED (PINT 99)',
        'S_after.PRECISIONINI = ' + text('10'), 'S_after.USERCONSTANTS = [puserconstant_sibling]',
        '$source_constant_lookup(S_after,' + text('SOURCE63PEER') + ') = (VALUE (PINT 2053))',
        *common.public('S_after')]
    for variable, spelling in [('call', 'ini_get'), ('option', 'precision'), ('value', 'handler-value63')]:
        values += ['S_thrown.STORE[n_' + variable + '] = DEFINED pvalue_handler_' + variable,
            '$string_bytes(pvalue_handler_' + variable + ') = (' + text(spelling) + ')']
    for after, before in [('S_dispatch', 'S'), ('S_after', 'S_thrown')]:
        values += [after + '.FILEINCLUDEPATH = ' + before + '.FILEINCLUDEPATH']
    for field in ('.SITE = PORIGIN 0 eps', '.LINE = $(pconfigcall_S.LINE + 1)',
            '.SELECTION = eps', '.INDEX = 1', '.OWNER = (0)', '.NAMED = false', '.KIND = INTRINSIC_INI_GET'):
        values += ['~$config_ini_null_valid(S,pconfigcall_S[' + field + '])']
    values += ['~$config_sent_shape(S,pconfigcall_S[.NAMED = false])',
        '~$config_invoke_valid(S,pconfigcall_S[.NAMED = false])',
        '~$config_ini_null_valid(S,pconfigcall_S[.SENT = [NAMED_SENT (KNOWN pvalue_captured),NAMED_SENT (KNOWN PNULL)]])']
    for slots in ['pconfigcall_S.SENT[0:1]', 'pconfigcall_S.SENT ++ [NAMED_SENT (KNOWN PNULL)]']:
        values += ['~$config_ini_null_valid(S,pconfigcall_S[.SENT = ' + slots + '])']
    for value in ['PBOOL false', 'PSTRING_CARRIER INTERNED_STRING eps']:
        values += ['~$config_ini_null_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,0,KNOWN (' + value + '))])']
    values += ['pvalue_bad = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ' + text('early-value63'),
        '~$string_carrier_valid(S,pvalue_bad)',
        '~$config_ini_quiet_value(S,pvalue_bad)',
        '~$config_ini_null_valid(S,pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,1,KNOWN pvalue_bad)])',
        '~$config_ini_quiet_value(S,PSTRING ' + text('early-value63') + ')',
        '~$config_ini_quiet_value(S,PFLOAT 9221120237041090560)',
        '~$config_ini_quiet_value(S,PARRAY 0)', '~$config_ini_quiet_value(S,POBJECT 0)']
    for field in ('.LEVEL = 2', '.MESSAGE = ' + text('changed'), '.LINE = $(perrorcall_deprecated.LINE + 1)',
            '.EVENT = DIAGNOSTIC "Deprecated" perrorcall_deprecated.MESSAGE $(perrorcall_deprecated.LINE + 1)'):
        values += ['~$error_call_valid(S_expected,perrorcall_deprecated[' + field + '])']
    values += [*budget('S'), *budget('S_thrown'),
        'S_final = $drive_steps(S_after,3000)', 'S_final.COMPLETION = NORMAL',
        'S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        'S_final.USERCONSTANTS = [puserconstant_sibling]',
        'S_final.PRECISIONINI = ' + text('10'), 'S_final.ERRORHANDLER.CALLBACK = eps',
        *unchanged('S_final', 'S', 'AUTOLOAD CLASSNAMES CLASSCONSTANTCACHE FILEINCLUDEPATH'),
        '$test_outputs(S_final.EVENTS) = ' + text('B|V|O|D|8192|' + MESSAGE + '|I|99|2|1|ini_get|precision|handler-value63|10|2053|Z|10|99'),
        *common.public('S_final')]
    return values


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks
    driver.main()


if __name__ == '__main__':
    main()
