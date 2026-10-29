#!/usr/bin/env python3
"""Reached scalar cell reads, DIRECT snapshots and terminal CONFIG reception."""
from pathlib import Path
from types import SimpleNamespace

import config_generator_reference_scalar_cases as cases
import list_missing_warning_protocol as shared
from array_generator_unpack_state_review import budget, finish, initial, owners, public, seek

NAME = 'config-generator-reference-scalar-float-live-alias-snapshot'
SOURCES = SimpleNamespace(CASES={NAME: cases.CASES[NAME]}, __file__=cases.__file__)
HELPERS = shared.HELPERS + r'''
dec $a72_echo(pstate, ptbytes) : bool
def $a72_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $a72_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 970) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask*
  -- if pconfiggenerator.ITEMS = eps
def $list_warning_frontier(S, 971) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask*
  -- if |pconfiggenerator.ITEMS| = 1
def $list_warning_frontier(S, 972) = $a72_echo(S, $ptascii("T:"))
def $list_warning_frontier(S, 973) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "finish") :: ptask*
def $list_warning_frontier(S, 974) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "invoke") :: ptask*
def $list_warning_frontier(S, 975) = $a72_echo(S, $ptascii("A:"))
def $list_warning_frontier(S, 976) = $a72_echo(S, $ptascii("R:"))
'''


def cell(state, name, identifier):
    return f'$lookup($global_table_view({state}).ENV, $ptascii("{name}")) = ({identifier})'


def conditions(name, program, path, stdout):
    assert name == NAME
    checks = initial(program, path) + seek('S_initial', 970, 'S_option') + [
        'S_option.TODO = (CONFIG_GENERATOR pconfiggenerator_option "ready") :: ptask_option*',
        'pconfiggenerator_option.ITEMS = eps',
        'pconfiggenerator_option.PRODUCER = eps',
        'pconfiggenerator_option.INPUT = VARIABLE ($ptascii("input")) z_input',
        'pconfiggenerator_option.CALL.KIND = INTRINSIC_INI_SET',
        'pconfiggenerator_option.CALL.OWNER = (n_callee)',
        'pconfiggenerator_option.OBJECT = n_generator',
        'S_option.OBJECTS[n_generator] = GENERATOR pgenerator_option',
        'pgenerator_option.PHASE = GENERATOR_PAUSED',
        'pgenerator_option.BORROWED = eps',
        'pgenerator_option.VALUE = eps',
        'pgenerator_option.REFCELL = (n_option_cell)',
        'pgenerator_option.KEY = (PINT 0)',
        '$generator_reference_producer(S_option,pgenerator_option)',
        '$config_generator_reference_input(pconfiggenerator_option)',
        '$config_generator_valid(S_option,pconfiggenerator_option,"ready")',
        '$config_generator_send_allowed(S_option,pconfiggenerator_option)',
        '$ordinary_reference_value(S_option,n_option_cell) = (pvalue_name)',
        '$string_bytes(pvalue_name) = ($ptascii("precision"))',
        '$config_generator_value(S_option,pconfiggenerator_option) = (pvalue_name)',
        cell('S_option', 'option', 'n_option_cell'),
        'S_option.STORE[n_option_cell] = DEFINED pvalue_name',
        cell('S_option', 'value', 'n_value_cell'),
        cell('S_option', 'valueAlias', 'n_value_cell'),
        'S_option.STORE[n_value_cell] = DEFINED (PFLOAT 4608238818662570491)',
        cell('S_option', 'watch', 'n_watch_cell'),
        'S_option.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)',
        '$weakref_get(S_option,n_watch) = POBJECT n_generator',
        cell('S_option', 'result', 'n_result_cell'),
        'S_option.STORE[n_result_cell] = DEFINED (PINT 99)',
        owners('S_option', 'HOBJECT n_generator', 3),
        'PhpStep: S_option ~> S_first_sent',
        'S_first_sent.TODO = (CONFIG_GENERATOR pconfiggenerator_first "next") :: ptask_option*',
        'pconfiggenerator_first = pconfiggenerator_option[.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_name)]]',
        '$config_generator_history(S_first_sent,pconfiggenerator_first)',
    ] + public('S_option') + public('S_first_sent') + seek('S_first_sent', 971, 'S_value') + [
        'S_value.TODO = (CONFIG_GENERATOR pconfiggenerator_value "ready") :: ptask_value*',
        'pconfiggenerator_value = pconfiggenerator_first',
        'S_value.OBJECTS[n_generator] = GENERATOR pgenerator_value',
        'pgenerator_value.PHASE = GENERATOR_PAUSED',
        'pgenerator_value.BORROWED = eps',
        'pgenerator_value.VALUE = eps',
        'pgenerator_value.REFCELL = (n_value_cell)',
        'pgenerator_value.KEY = (PINT 1)',
        '$generator_reference_producer(S_value,pgenerator_value)',
        '$ordinary_reference_value(S_value,n_value_cell) = (PFLOAT 4608238818662570491)',
        '$config_generator_value(S_value,pconfiggenerator_value) = (PFLOAT 4608238818662570491)',
        '$config_generator_valid(S_value,pconfiggenerator_value,"ready")',
        '$config_generator_send_allowed(S_value,pconfiggenerator_value)',
        'S_value.STORE[n_option_cell] = DEFINED pvalue_live_name',
        '$string_bytes(pvalue_live_name) = ($ptascii("serialize_precision"))',
        cell('S_value', 'input', 'n_input_cell'),
        'S_value.STORE[n_input_cell] = DEFINED (PINT 17)',
        cell('S_value', 'hold', 'n_hold_cell'),
        'S_value.STORE[n_hold_cell] = DEFINED (POBJECT n_generator)',
        cell('S_value', 'call', 'n_call_cell'),
        'S_value.STORE[n_call_cell] = DEFINED (POBJECT n_new_callee)',
        'S_value.OBJECTS[n_new_callee] = INTRINSICCLOSURE INTRINSIC_INI_GET',
        cell('S_value', 'keep', 'n_keep_cell'),
        'S_value.STORE[n_keep_cell] = DEFINED (POBJECT n_callee)',
        'S_value.OBJECTS[n_callee] = INTRINSICCLOSURE INTRINSIC_INI_SET',
        'n_new_callee =/= n_callee',
        owners('S_value', 'HOBJECT n_generator', 2),
        owners('S_value', 'HOBJECT n_callee', 2),
        owners('S_value', 'HOBJECT n_new_callee', 1),
        # Constructed denial controls do not claim additional source reachability.
        'S_dead = S_value[.ALLOCATIONS = eps]',
        '$ordinary_reference_value(S_dead,n_value_cell) = eps',
        '$config_generator_value(S_dead,pconfiggenerator_value) = eps',
        '~$config_generator_send_allowed(S_dead,pconfiggenerator_value)',
        'S_unregistered = S_value[.REFCELLS = eps]',
        '$config_generator_value(S_unregistered,pconfiggenerator_value) = eps',
        'S_snapshot = S_value[.OBJECTS[n_generator] = GENERATOR pgenerator_value[.VALUE = (PFLOAT 4608238818662570491)][.REFCELL = eps]]',
        '$config_generator_value(S_snapshot,pconfiggenerator_value) = eps',
        'S_owning = S_value[.STORE[n_value_cell] = DEFINED (POBJECT n_generator)]',
        '$config_generator_value(S_owning,pconfiggenerator_value) = eps',
        'S_forged = S_value[.CODE = eps]',
        '~$config_generator_history(S_forged,pconfiggenerator_value)',
        'pconfiggenerator_temporary = pconfiggenerator_value[.INPUT = KNOWN (POBJECT n_generator)]',
        '~$config_generator_reference_input(pconfiggenerator_temporary)',
        '~$config_generator_history(S_value,pconfiggenerator_temporary)',
    ] + public('S_value') + budget('S_value', 'S_budget') + [
        'PhpStep: S_value ~> S_second_sent',
        'S_second_sent.TODO = (CONFIG_GENERATOR pconfiggenerator_second "next") :: ptask_value*',
        'pconfiggenerator_second = pconfiggenerator_value[.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_name),ENTRY (KINT 1) (DIRECT (PFLOAT 4608238818662570491))]]',
        '$config_generator_history(S_second_sent,pconfiggenerator_second)',
        '$task_nodes(CONFIG_GENERATOR pconfiggenerator_second "next") = [HOBJECT n_generator,HOBJECT n_callee]',
    ] + public('S_second_sent') + seek('S_second_sent', 972, 'S_terminal') + [
        'S_terminal.PRECISIONINI = $ptascii("14")',
        'S_terminal.STORE[n_value_cell] = DEFINED (PFLOAT 4608238818662570491)',
        'S_terminal.STORE[n_result_cell] = DEFINED (PINT 99)',
    ] + seek('S_terminal', 973, 'S_finish') + [
        'S_finish.TODO = (CONFIG_GENERATOR pconfiggenerator_finish "finish") :: ptask_finish*',
        'pconfiggenerator_finish = pconfiggenerator_second',
        'S_finish.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
        'pgenerator_closed.PHASE = GENERATOR_CLOSED',
        'pgenerator_closed.REFCELL = (n_value_cell)',
        '$config_generator_valid(S_finish,pconfiggenerator_finish,"finish")',
        '$config_generator_finish_allowed(S_finish,pconfiggenerator_finish)',
        'S_finish.PRECISIONINI = $ptascii("3")',
        'S_finish.STORE[n_value_cell] = DEFINED (PFLOAT 4616752568008179712)',
        'S_finish.STORE[n_result_cell] = DEFINED (PINT 99)',
        owners('S_finish', 'HOBJECT n_generator', 2),
    ] + public('S_finish') + seek('S_finish', 974, 'S_invoke') + [
        'S_invoke.TODO = (CONFIG_GENERATOR pconfiggenerator_invoke "invoke") :: ptask_invoke*',
        'pconfiggenerator_invoke = pconfiggenerator_second',
        '$config_generator_valid(S_invoke,pconfiggenerator_invoke,"invoke")',
        '$config_pack_prefix(pconfiggenerator_invoke.CALL,pconfiggenerator_invoke.ITEMS,false) = (pconfigcall_prefix)',
        'pconfigcall = pconfigcall_prefix[.INDEX = 1]',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_name),NAMED_SENT (KNOWN (PFLOAT 4608238818662570491))]',
        '$config_selected_valid(S_invoke,pconfigcall)',
        '$config_nodes(pconfigcall) = [HOBJECT n_callee]',
        '$weakref_get(S_invoke,n_watch) = POBJECT n_generator',
        owners('S_invoke', 'HOBJECT n_generator', 1),
        'PhpStep: S_invoke ~> S_api',
        'S_api.PRECISIONINI = $ptascii("1.23")',
        'S_api.RESULT = KNOWN pvalue_previous',
        '$string_bytes(pvalue_previous) = ($ptascii("3"))',
    ] + public('S_invoke') + public('S_api') + seek('S_api', 975, 'S_output') + [
        'S_output.STORE[n_result_cell] = DEFINED pvalue_previous',
        'S_output.STORE[n_value_cell] = DEFINED (PFLOAT 4616752568008179712)',
        '$weakref_get(S_output,n_watch) = POBJECT n_generator',
    ] + public('S_output') + seek('S_output', 976, 'S_release') + [
        '$weakref_get(S_release,n_watch) = PNULL',
        '~((HOBJECT n_generator) <- S_release.ALLOCATIONS)',
    ] + public('S_release')
    return checks + finish('S_release', stdout, ['HOBJECT n_generator','HOBJECT n_watch',
        'HOBJECT n_callee','HOBJECT n_new_callee'])


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(SOURCES, conditions, HELPERS, model_timeout=300,
        extra_inputs=(Path(__file__),
                      Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
