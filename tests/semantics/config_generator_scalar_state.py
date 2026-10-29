#!/usr/bin/env python3
"""Reached float snapshots cross terminal Generator effects before INI reception."""
from pathlib import Path
from types import SimpleNamespace

import config_generator_scalar_cases as cases
import list_missing_warning_protocol as shared
from array_generator_unpack_state_review import budget, finish, initial, owners, public, seek

NAME = 'config-generator-scalar-float-post-terminal-precision'
SOURCES = SimpleNamespace(CASES={NAME: cases.CASES[NAME]}, __file__=cases.__file__)
HELPERS = shared.HELPERS + r'''
dec $a71_echo(pstate, ptbytes) : bool
def $a71_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $a71_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 990) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask*
  -- if |pconfiggenerator.ITEMS| = 1
def $list_warning_frontier(S, 991) = $a71_echo(S, $ptascii("T:"))
def $list_warning_frontier(S, 992) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "finish") :: ptask*
def $list_warning_frontier(S, 993) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "invoke") :: ptask*
def $list_warning_frontier(S, 994) = $a71_echo(S, $ptascii("A:"))
def $list_warning_frontier(S, 995) = $a71_echo(S, $ptascii("R:"))
'''


def cell(state, name, identifier):
    return f'$lookup($global_table_view({state}).ENV, $ptascii("{name}")) = ({identifier})'


def conditions(name, program, path, stdout):
    assert name == NAME
    checks = initial(program, path) + seek('S_initial', 990, 'S_value') + [
        'S_value.TODO = (CONFIG_GENERATOR pconfiggenerator_value "ready") :: ptask_value*',
        'pconfiggenerator_value.OBJECT = n_generator',
        'pconfiggenerator_value.INPUT = VARIABLE ($ptascii("input")) z_input',
        'pconfiggenerator_value.PRODUCER = eps',
        'pconfiggenerator_value.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_name)]',
        '$string_bytes(pvalue_name) = ($ptascii("precision"))',
        'pconfiggenerator_value.CALL.OWNER = (n_callee)',
        'pconfiggenerator_value.CALL.KIND = INTRINSIC_INI_SET',
        'pconfiggenerator_value.CALL.SELECTION = eps',
        'S_value.OBJECTS[n_callee] = INTRINSICCLOSURE INTRINSIC_INI_SET',
        '$config_selected_valid(S_value, pconfiggenerator_value.CALL)',
        'S_value.OBJECTS[n_generator] = GENERATOR pgenerator_value',
        'pgenerator_value.PHASE = GENERATOR_PAUSED',
        'pgenerator_value.BORROWED = eps',
        'pgenerator_value.REFCELL = eps',
        'pgenerator_value.VALUE = (PFLOAT 4608238818662570491)',
        'pgenerator_value.KEY = (PINT 1)',
        '$config_generator_valid(S_value, pconfiggenerator_value, "ready")',
        '$config_generator_send_allowed(S_value, pconfiggenerator_value)',
        cell('S_value', 'value', 'n_value_cell'),
        'S_value.STORE[n_value_cell] = DEFINED (PFLOAT 4608238818662570491)',
        cell('S_value', 'input', 'n_input_cell'),
        'S_value.STORE[n_input_cell] = DEFINED (PINT 17)',
        cell('S_value', 'hold', 'n_hold_cell'),
        'S_value.STORE[n_hold_cell] = DEFINED (POBJECT n_generator)',
        cell('S_value', 'call', 'n_call_cell'),
        'S_value.STORE[n_call_cell] = DEFINED (POBJECT n_new_callee)',
        'S_value.OBJECTS[n_new_callee] = INTRINSICCLOSURE INTRINSIC_INI_GET',
        'n_new_callee =/= n_callee',
        cell('S_value', 'keep', 'n_keep_cell'),
        'S_value.STORE[n_keep_cell] = DEFINED (POBJECT n_callee)',
        cell('S_value', 'watch', 'n_watch_cell'),
        'S_value.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)',
        '$weakref_get(S_value, n_watch) = POBJECT n_generator',
        cell('S_value', 'result', 'n_result_cell'),
        'S_value.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_value.PRECISIONINI = $ptascii("14")',
        owners('S_value', 'HOBJECT n_generator', 2),
        owners('S_value', 'HOBJECT n_callee', 2),
        owners('S_value', 'HOBJECT n_new_callee', 1),
    ] + public('S_value') + budget('S_value', 'S_budget') + [
        'PhpStep: S_value ~> S_sent',
        'S_sent.TODO = (CONFIG_GENERATOR pconfiggenerator_sent "next") :: ptask_value*',
        'pconfiggenerator_sent = pconfiggenerator_value[.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_name),ENTRY (KINT 1) (DIRECT (PFLOAT 4608238818662570491))]]',
        '$config_generator_history(S_sent, pconfiggenerator_sent)',
        '$task_nodes(CONFIG_GENERATOR pconfiggenerator_sent "next") = [HOBJECT n_generator,HOBJECT n_callee]',
    ] + public('S_sent') + seek('S_sent', 991, 'S_terminal') + [
        'S_terminal.PRECISIONINI = $ptascii("14")',
        'S_terminal.STORE[n_value_cell] = DEFINED (PFLOAT 4608238818662570491)',
        'S_terminal.STORE[n_result_cell] = DEFINED (PINT 99)',
    ] + public('S_terminal') + seek('S_terminal', 992, 'S_finish') + [
        'S_finish.TODO = (CONFIG_GENERATOR pconfiggenerator_finish "finish") :: ptask_finish*',
        'pconfiggenerator_finish = pconfiggenerator_sent',
        'S_finish.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
        'pgenerator_closed.PHASE = GENERATOR_CLOSED',
        '$config_generator_valid(S_finish, pconfiggenerator_finish, "finish")',
        'S_finish.PRECISIONINI = $ptascii("3")',
        'S_finish.STORE[n_value_cell] = DEFINED (PFLOAT 4616752568008179712)',
        'S_finish.STORE[n_result_cell] = DEFINED (PINT 99)',
        owners('S_finish', 'HOBJECT n_generator', 2),
    ] + public('S_finish') + seek('S_finish', 993, 'S_invoke') + [
        'S_invoke.TODO = (CONFIG_GENERATOR pconfiggenerator_invoke "invoke") :: ptask_invoke*',
        'pconfiggenerator_invoke = pconfiggenerator_sent',
        '$config_generator_valid(S_invoke, pconfiggenerator_invoke, "invoke")',
        '$config_pack_prefix(pconfiggenerator_invoke.CALL,pconfiggenerator_invoke.ITEMS,false) = (pconfigcall_prefix)',
        'pconfigcall = pconfigcall_prefix[.INDEX = 1]',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue_name),NAMED_SENT (KNOWN (PFLOAT 4608238818662570491))]',
        '$config_selected_valid(S_invoke, pconfigcall)',
        '$config_nodes(pconfigcall) = [HOBJECT n_callee]',
        '$weakref_get(S_invoke,n_watch) = POBJECT n_generator',
        owners('S_invoke', 'HOBJECT n_generator', 1),
        owners('S_invoke', 'HOBJECT n_callee', 2),
        'PhpStep: S_invoke ~> S_api',
        'S_api.PRECISIONINI = $ptascii("1.23")',
        'S_api.RESULT = KNOWN pvalue_previous',
        '$string_bytes(pvalue_previous) = ($ptascii("3"))',
        owners('S_api', 'HOBJECT n_callee', 1),
    ] + public('S_invoke') + public('S_api') + seek('S_api', 994, 'S_output') + [
        'S_output.STORE[n_result_cell] = DEFINED pvalue_previous',
        'S_output.STORE[n_value_cell] = DEFINED (PFLOAT 4616752568008179712)',
        '$weakref_get(S_output,n_watch) = POBJECT n_generator',
    ] + public('S_output') + seek('S_output', 995, 'S_release') + [
        '$weakref_get(S_release,n_watch) = PNULL',
        '~((HOBJECT n_generator) <- S_release.ALLOCATIONS)',
    ] + public('S_release')
    return checks + finish('S_release', stdout, ['HOBJECT n_generator','HOBJECT n_watch',
        'HOBJECT n_callee','HOBJECT n_new_callee'])


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(SOURCES, conditions, HELPERS, model_timeout=300,
        extra_inputs=(Path(__file__),
                      Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
