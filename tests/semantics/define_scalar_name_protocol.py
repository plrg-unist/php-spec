#!/usr/bin/env python3
"""Reached define publication, historical keys and captured duplicate warnings."""
import argparse
import json
import os
from pathlib import Path
import sys

import global_constant_scalar_name_protocol as driver
import define_scalar_name_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64
FLOAT25 = 'PFLOAT 4612811918334230528'

PREFIX = r"""
dec $test_define_front(pstate, nat, pvalue, pvalue) : bool
def $test_define_front(S, 0, pvalue_name, pvalue) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_DEFINE
  -- if pconfigcall.SENT = (NAMED_SENT (KNOWN pvalue_name)) :: (NAMED_SENT (KNOWN pvalue)) :: pnamedslot*
def $test_define_front(S, 1, pvalue_name, pvalue) = true
  -- if S.TODO = (DYNAMIC_SCALAR_DEFINE_DUPLICATE pconfigcall pvalue_received z n_constants) :: ptask_tail*
  -- if pconfigcall.SENT = (NAMED_SENT (KNOWN pvalue_name)) :: (NAMED_SENT (KNOWN pvalue)) :: pnamedslot*
def $test_define_front(S, 2, pvalue_name, pvalue) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_CONSTANT
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_query)]
  -- if $string_bytes(pvalue_query) = ($ptascii("2.5"))
  -- if $precision_value(S) = 1
def $test_define_front(S, 3, pvalue_name, pvalue) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_call(S,pcallcontext) = (perrorcall)
  -- if perrorcall.RESUME = DYNAMIC_SCALAR_DEFINE_DUPLICATE pconfigcall pvalue_received z n_constants
  -- if pconfigcall.SENT = (NAMED_SENT (KNOWN pvalue_name)) :: (NAMED_SENT (KNOWN pvalue)) :: pnamedslot*
def $test_define_front(S, n_stage, pvalue_name, pvalue) = false -- otherwise
dec $test_define_seek(pstate, nat, pvalue, pvalue, nat) : pstate
def $test_define_seek(S, n_stage, pvalue_name, pvalue, 0) = S
def $test_define_seek(S, n_stage, pvalue_name, pvalue, n) = S
  -- if $(n > 0)
  -- if $test_define_front(S,n_stage,pvalue_name,pvalue) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_define_seek(S, n_stage, pvalue_name, pvalue, n) = $test_define_seek($drive_steps($test_running(S),1),n_stage,pvalue_name,pvalue,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_define_front(S,n_stage,pvalue_name,pvalue)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def reach(state, start, name, value, stage=0):
    return [state + '_found = $test_define_seek(' + start + ',' + str(stage) + ',' + name + ',' + value + ',3000)',
        state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_define_front(' + state + ',' + str(stage) + ',' + name + ',' + value + ')', *common.public(state)]


def front(state, start, name, value):
    call = 'pconfigcall_' + state
    return [*reach(state, start, name, value),
        state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
        call + '.KIND = INTRINSIC_DEFINE', call + '.OWNER = eps', call + '.PACKS = eps',
        '$dynamic_scalar_define_values(' + call + ') = ((' + name + ',' + value + '))',
        '$config_invoke_valid(' + state + ',' + call + ')',
        '$dynamic_scalar_define_call(' + call + ')', '$dynamic_scalar_define_valid(' + state + ',' + call + ')']


def unchanged(after, before, fields):
    return [after + '.' + field + ' = ' + before + '.' + field for field in fields.split()]


def publish(state, name, value, key):
    call, converted, after, row = 'pconfigcall_' + state, state + '_converted', state + '_value', 'puserconstant_' + state
    return ['~$config_strict(' + state + ',' + call + ')',
        converted + ' = $typed_apply(' + state + ',TYPESTRING (' + name + '),' + call + '.LINE)',
        converted + '.COMPLETION = NORMAL', converted + '.RESULT = KNOWN pvalue_' + converted,
        '$string_bytes(pvalue_' + converted + ') = (' + text(key) + ')',
        '$string_carrier_valid(' + converted + ',pvalue_' + converted + ')',
        '$dynamic_scalar_define_received(' + converted + ',' + call + ',pvalue_' + converted + ',$precision_value(' + state + '))',
        *common.step(after, state, 'PBOOL true'), after + '.TODO = ptask_' + state + '*',
        '$(|' + after + '.USERCONSTANTS| = |' + state + '.USERCONSTANTS| + 1)',
        row + ' = ' + after + '.USERCONSTANTS[|' + state + '.USERCONSTANTS|]',
        after + '.USERCONSTANTS = ' + state + '.USERCONSTANTS ++ [' + row + ']',
        row + '.NAME = ' + text(key), row + '.ORIGIN = ' + call + '.SITE',
        row + '.VALUE = ' + value, row + '.CLASS = PVSCALAR', row + '.READS = eps', row + '.RECEIVES = eps',
        '$user_constants_valid(' + after + ',' + after + '.USERCONSTANTS)',
        after + '.STRINGDATA = ' + converted + '.STRINGDATA',
        *unchanged(after, state, 'STORE ENV ARRAYS OBJECTS OBJECTPROPS REFCELLS ALLOCATIONS SELECTEDCALLS SOURCES POOLS FILES STATICS PRECISIONINI')]


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)',
        state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)',
        state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET']
    if name == 'weak-scalar-name-publication':
        values += [*front('S', 'S_initial', 'PINT 37', 'PINT 137'),
            '$lookup(S.ENV,' + text('name') + ') = (n_name_cell)', 'S.STORE[n_name_cell] = DEFINED (PINT 37)',
            *publish('S', 'PINT 37', 'PINT 137', '37'),
            *front('S_float', 'S_value', FLOAT25, 'PINT 125'),
            '$intrinsic_argument(S_float,pconfigcall_S_float.SITE,0) = ((expression,false,preqbytes?,porigin_argument,z))',
            '$compiled_read(S_float,porigin_argument) = (' + FLOAT25 + ')',
            *publish('S_float', FLOAT25, 'PINT 125', '2.5'),
            '$dynamic_scalar_define_received(S_float_converted,pconfigcall_S_float,pvalue_S_float_converted,14)',
            '~$dynamic_scalar_define_received(S_float_converted,pconfigcall_S_float,pvalue_S_float_converted,1)',
            '$dynamic_scalar_float_name(' + text('2.5') + ',4612811918334230528,0)',
            '~$dynamic_scalar_name_possible(' + text('bogus') + ',(' + FLOAT25 + '))',
            *reach('S_later', 'S_float_value', 'PNULL', 'PNULL', 2),
            '$user_constant_at(S_later.USERCONSTANTS,' + text('2.5') + ') = (puserconstant_S_float)',
            '$user_constants_valid(S_later,S_later.USERCONSTANTS)',
            '~$user_constants_valid(S_float_value[.USERCONSTANTS = S_float.USERCONSTANTS ++ [puserconstant_S_float[.NAME = ' + text('bogus') + ']]],S_float.USERCONSTANTS ++ [puserconstant_S_float[.NAME = ' + text('bogus') + ']])']
        for index, forged in ((0, 'PINT 25'), (1, 'PINT 126')):
            call = 'pconfigcall_bad_' + str(index)
            bad = 'S_bad_' + str(index)
            values += [call + ' = pconfigcall_S_float[.SENT = $named_slot_set(pconfigcall_S_float.SENT,' + str(index) + ',KNOWN (' + forged + '))]',
                '$config_invoke_valid(S_float,' + call + ')', '~$dynamic_scalar_define_valid(S_float,' + call + ')',
                bad + ' = $drive_steps(S_float[.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_S_float*],1)',
                bad + '.COMPLETION = UNSUPPORTED "scalar define name reception"']
        for change in ('.SITE = PORIGIN 0 eps', '.LINE = $(pconfigcall_S.LINE + 1)', '.SELECTION = (0)'):
            values += ['~$dynamic_scalar_define_valid(S,pconfigcall_S[' + change + '])']
        for raw in ('PNULL', 'PSTRING ' + text('37'), 'PARRAY 0', 'POBJECT 0'):
            values += ['~$dynamic_scalar_define_call(pconfigcall_S[.SENT = $named_slot_set(pconfigcall_S.SENT,0,KNOWN (' + raw + '))])']
        values += ['~$dynamic_scalar_define_call(pconfigcall_S[.OWNER = (0)])',
            '~$dynamic_scalar_define_call(pconfigcall_S[.SENT = pconfigcall_S.SENT ++ [NAMED_SENT (KNOWN (PBOOL true))]])']
    elif name == 'captured-name-value-and-duplicate-warning':
        values += [*front('S', 'S_initial', 'PINT 38', 'PINT 138'),
            'pconfigcall_S.SELECTION = (n_selection)', '$(n_selection < |S.SELECTEDCALLS|)',
            'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_DEFINE',
            '$lookup(S.ENV,' + text('call') + ') = (n_callee_cell)', 'S.STORE[n_callee_cell] = DEFINED pvalue_callee',
            '$string_bytes(pvalue_callee) = (' + text('constant') + ')',
            '$test_outputs(S.EVENTS) = ' + text('B|N|V|'), *publish('S', 'PINT 38', 'PINT 138', '38'),
            *front('S_duplicate', 'S_value', 'PINT 38', 'PINT 999'),
            'S_duplicate_converted = $typed_apply(S_duplicate,TYPESTRING (PINT 38),pconfigcall_S_duplicate.LINE)',
            'S_duplicate_converted.RESULT = KNOWN pvalue_received',
            *common.step('S_warning', 'S_duplicate'),
            *reach('S_handler', 'S_warning', 'PINT 38', 'PINT 999', 3),
            'S_handler.CURRENT = (pcallcontext_handler)',
            '$error_context_call(S_handler,pcallcontext_handler) = (perrorcall_handler)',
            'perrorcall_handler.RESUME = DYNAMIC_SCALAR_DEFINE_DUPLICATE pconfigcall_S_duplicate pvalue_received 14 n_constants',
            '$error_context_valid(S_handler,pcallcontext_handler)',
            'pconfigcall_api = pconfigcall_S_duplicate[.SENT = $named_slot_set(pconfigcall_S_duplicate.SENT,0,KNOWN pvalue_received)]',
            '$error_context_trigger(S_handler,pcallcontext_handler) = (pconfigcall_api)',
            '$error_handler_trace_values(S_handler,pcallcontext_handler,pconfigcall_api) = [pvalue_received, (PINT 999), (PBOOL false)]',
            *reach('S_resume', 'S_handler', 'PINT 38', 'PINT 999', 1),
            'S_resume.TODO = (DYNAMIC_SCALAR_DEFINE_DUPLICATE pconfigcall_S_duplicate pvalue_received 14 n_constants) :: ptask_resume*',
            '$dynamic_scalar_define_duplicate_valid(S_resume,pconfigcall_S_duplicate,pvalue_received,14,n_constants)',
            '$lookup(S_resume.ENV,' + text('name') + ') = (n_name_cell)', 'S_resume.STORE[n_name_cell] = DEFINED (PINT 39)',
            '$lookup(S_resume.ENV,' + text('candidate') + ') = (n_value_cell)', 'S_resume.STORE[n_value_cell] = DEFINED (PINT 777)',
            '$user_constant_at(S_resume.USERCONSTANTS,' + text('38') + ') = (puserconstant_S)',
            '$user_constant_at(S_resume.USERCONSTANTS,' + text('39') + ') = eps',
            '~$dynamic_scalar_define_duplicate_valid(S_resume,pconfigcall_S_duplicate,pvalue_received,-2,n_constants)',
            '~$dynamic_scalar_define_duplicate_valid(S_resume,pconfigcall_S_duplicate,pvalue_received,14,0)',
            '~$dynamic_scalar_define_duplicate_valid(S_resume,pconfigcall_S_duplicate[.LINE = $(pconfigcall_S_duplicate.LINE + 1)],pvalue_received,14,n_constants)',
            'pvalue_invalid = PSTRING_CARRIER (REQUEST_STRING (|S_resume.STRINGDATA|)) ' + text('38'),
            '~$dynamic_scalar_define_duplicate_valid(S_resume,pconfigcall_S_duplicate,pvalue_invalid,14,n_constants)',
            '~$call_descriptors_valid(S_resume[.TODO = (DYNAMIC_SCALAR_DEFINE_DUPLICATE pconfigcall_S_duplicate pvalue_invalid 14 n_constants) :: ptask_resume*])',
            *common.step('S_return', 'S_resume', 'PBOOL false'), 'S_return.TODO = ptask_resume*',
            *unchanged('S_return', 'S_resume', 'STORE ENV USERCONSTANTS STRINGDATA SELECTEDCALLS'), *budget('S_resume')]
    else:
        assert name == 'strict-name-errors-after-all-argument-effects'
        values += [*front('S', 'S_initial', 'PINT 37', 'PINT 137'),
            '$config_strict(S,pconfigcall_S)', '$config_conversion(S,pconfigcall_S,PINT 37) = TYPEREJECT',
            '$test_outputs(S.EVENTS) = ' + text('B|N|V|'), 'S.USERCONSTANTS = eps',
            '$lookup(S.ENV,' + text('result') + ') = (n_result_cell)', 'S.STORE[n_result_cell] = DEFINED (PINT 99)',
            *common.step('S_error', 'S'),
            'S_error.TODO = (THROW_SEARCH n_error) :: ptask_error*',
            'S_error.OBJECTS[n_error] = THROWABLE pthrowable_error', 'pthrowable_error.KIND = "TypeError"',
            'pthrowable_error.ORIGIN = (pconfigcall_S.SITE)',
            '$string_bytes($throwable_field(S_error,n_error,"message")) = (' + text('define(): Argument #1 ($constant_name) must be of type string, int given') + ')',
            '$throwable_field(S_error,n_error,"line") = PINT pconfigcall_S.LINE',
            '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
            'S_error.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_frame))]',
            '$trace_array_field(S_error,n_frame,' + text('function') + ') = PSTRING ' + text('define'),
            '$trace_array_field(S_error,n_frame,' + text('args') + ') = PARRAY n_args',
            'S_error.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 37)), ENTRY (KINT 1) (DIRECT (PINT 137))]',
            *unchanged('S_error', 'S', 'USERCONSTANTS STORE STRINGDATA SELECTEDCALLS EVENTS'), *common.public('S_error')]
    return values + budget('S')


fingerprint = sources.family.fingerprint


def inputs():
    return dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})


sources.family.fingerprint = inputs
driver.sources, driver.PREFIX, driver.checks = sources, PREFIX, checks

if __name__ == '__main__':
    selection = argparse.ArgumentParser(add_help=False)
    selection.add_argument('--case', action='append', default=[])
    selected, remaining = selection.parse_known_args()
    assert len(selected.case) == len(set(selected.case)) and set(selected.case) <= sources.family.CASES.keys()
    if selected.case:
        sources.family.CASES = {name: sources.family.CASES[name] for name in selected.case}
    sys.argv = [sys.argv[0], *remaining]
    driver.main()
