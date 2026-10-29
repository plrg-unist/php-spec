#!/usr/bin/env python3
"""Reached reference-cell reads, copied sends and retained DATA retirement."""
from pathlib import Path
from types import SimpleNamespace

import config_generator_reference_scalar_review_cases as cases
import list_missing_warning_protocol as shared
from array_generator_unpack_state_review import budget, finish, initial, owners, public, seek


NAME = 'config-generator-reference-scalar-copies-before-later-cell-writes'
SOURCES = SimpleNamespace(CASES={NAME: cases.CASES[NAME]}, __file__=cases.__file__)
HELPERS = shared.HELPERS + r'''
dec $a72_peer_echo(pstate, ptbytes) : bool
def $a72_peer_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $a72_peer_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 990) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask*
  -- if pconfiggenerator.ITEMS = eps
def $list_warning_frontier(S, 991) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask*
  -- if |pconfiggenerator.ITEMS| = 1
def $list_warning_frontier(S, 992) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "finish") :: ptask*
  -- if |pconfiggenerator.ITEMS| = 2
def $list_warning_frontier(S, 993) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "invoke") :: ptask*
  -- if |pconfiggenerator.ITEMS| = 2
def $list_warning_frontier(S, 994) = $a72_peer_echo(S, $ptascii("A:"))
def $list_warning_frontier(S, 995) = $a72_peer_echo(S, $ptascii("R:"))
'''


def cell(state, name, identifier):
    return f'$lookup($global_table_view({state}).ENV, $ptascii("{name}")) = ({identifier})'


def conditions(name, program, path, stdout):
    assert name == NAME
    checks = initial(program, path) + seek('S_initial', 990, 'S_option') + [
        'S_option.TODO = (CONFIG_GENERATOR pconfiggenerator_option "ready") :: ptask_option*',
        'pconfiggenerator_option.ITEMS = eps',
        'pconfiggenerator_option.PRODUCER = eps',
        'pconfiggenerator_option.INPUT = VARIABLE ($ptascii("input")) z_input',
        'pconfiggenerator_option.CALL.KIND = INTRINSIC_INI_SET',
        'pconfiggenerator_option.CALL.OWNER = (n_owner)',
        'pconfiggenerator_option.OBJECT = n_generator',
        'S_option.OBJECTS[n_generator] = GENERATOR pgenerator_option',
        'pgenerator_option.PHASE = GENERATOR_PAUSED',
        'pgenerator_option.VALUE = eps',
        'pgenerator_option.REFCELL = (n_option_cell)',
        'pgenerator_option.BORROWED = eps',
        'pgenerator_option.KEY = (PINT 3)',
        '$function_at($all_functions(S_option),pgenerator_option.FUNCTION) = (pfunction)',
        'pfunction.SIGNATURE.BYREF',
        '$generator_reference_valid(S_option,GENERATOR pgenerator_option)',
        '$config_generator_valid(S_option,pconfiggenerator_option,"ready")',
        '$config_generator_send_allowed(S_option,pconfiggenerator_option)',
        '$ordinary_reference_value(S_option,n_option_cell) = (pvalue_option)',
        '$string_bytes(pvalue_option) = ($ptascii("precision"))',
        '$config_generator_value(S_option,pconfiggenerator_option) = (pvalue_option)',
        'n_option_cell <- S_option.REFCELLS',
        '(HCELL n_option_cell) <- S_option.ALLOCATIONS',
        cell('S_option', 'option', 'n_option_cell'),
        cell('S_option', 'input', 'n_input_cell'),
        'S_option.STORE[n_input_cell] = DEFINED (PINT 17)',
        cell('S_option', 'hold', 'n_hold_cell'),
        'S_option.STORE[n_hold_cell] = DEFINED (POBJECT n_generator)',
        cell('S_option', 'watch', 'n_watch_cell'),
        'S_option.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)',
        '$weakref_get(S_option,n_watch) = POBJECT n_generator',
        cell('S_option', 'value', 'n_value_cell'),
        'S_option.STORE[n_value_cell] = DEFINED (PINT 13)',
        cell('S_option', 'result', 'n_result_cell'),
        'S_option.STORE[n_result_cell] = DEFINED (PINT 99)',
        owners('S_option', 'HOBJECT n_generator', 2),
    ] + public('S_option') + [
        'PhpStep: S_option ~> S_first_sent',
        'S_first_sent.TODO = (CONFIG_GENERATOR pconfiggenerator_first "next") :: ptask_option*',
        'pconfiggenerator_first = pconfiggenerator_option[.ITEMS = [ENTRY (KINT 3) (DIRECT pvalue_option)]]',
        'S_first_sent.STORE[n_option_cell] = DEFINED pvalue_option',
        '$config_generator_history(S_first_sent,pconfiggenerator_first)',
    ] + seek('S_first_sent', 991, 'S_value') + [
        'S_value.TODO = (CONFIG_GENERATOR pconfiggenerator_value "ready") :: ptask_value*',
        'pconfiggenerator_value = pconfiggenerator_first',
        'S_value.OBJECTS[n_generator] = GENERATOR pgenerator_value',
        'pgenerator_value.PHASE = GENERATOR_PAUSED',
        'pgenerator_value.VALUE = eps',
        'pgenerator_value.REFCELL = (n_value_cell)',
        'pgenerator_value.BORROWED = eps',
        'pgenerator_value.KEY = (PINT 3)',
        'n_value_cell <- S_value.REFCELLS',
        '(HCELL n_value_cell) <- S_value.ALLOCATIONS',
        '$ordinary_reference_value(S_value,n_value_cell) = (PINT 17)',
        '$config_generator_value(S_value,pconfiggenerator_value) = (PINT 17)',
        '$config_generator_send_allowed(S_value,pconfiggenerator_value)',
        'S_value.STORE[n_option_cell] = DEFINED pvalue_option_live',
        '$string_bytes(pvalue_option_live) = ($ptascii("serialize_precision"))',
        # Constructed controls have no source-agreement or reached-path credit.
        'S_nocell = S_value[.REFCELLS = eps]',
        '$config_generator_value(S_nocell,pconfiggenerator_value) = eps',
        'S_undefined = S_value[.STORE[n_value_cell] = UNDEFINED]',
        '$config_generator_value(S_undefined,pconfiggenerator_value) = eps',
        'S_debt = S_value[.LITERALREFDEBTS = [n_value_cell]]',
        '$config_generator_value(S_debt,pconfiggenerator_value) = eps',
        'S_mixed = S_value[.OBJECTS[n_generator] = GENERATOR pgenerator_value[.VALUE = (PINT 17)]]',
        '$config_generator_value(S_mixed,pconfiggenerator_value) = eps',
        '~$config_generator_history(S_value[.CODE = eps],pconfiggenerator_value)',
        '~$config_generator_history(S_value,pconfiggenerator_value[.INPUT = KNOWN (POBJECT n_generator)])',
    ] + public('S_value') + [
        'PhpStep: S_value ~> S_second_sent',
        'S_second_sent.TODO = (CONFIG_GENERATOR pconfiggenerator_second "next") :: ptask_value*',
        'pconfiggenerator_second = pconfiggenerator_value[.ITEMS = [ENTRY (KINT 3) (DIRECT pvalue_option),ENTRY (KINT 3) (DIRECT (PINT 17))]]',
        'S_second_sent.STORE[n_value_cell] = DEFINED (PINT 17)',
    ] + seek('S_second_sent', 992, 'S_finish') + [
        'S_finish.TODO = (CONFIG_GENERATOR pconfiggenerator_finish "finish") :: ptask_finish*',
        'pconfiggenerator_finish = pconfiggenerator_second',
        'S_finish.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
        'pgenerator_closed.PHASE = GENERATOR_CLOSED',
        'pgenerator_closed.FRAME = eps',
        'S_finish.PRECISIONINI = $ptascii("7")',
        'S_finish.STORE[n_value_cell] = DEFINED (PINT 31)',
        'S_finish.STORE[n_result_cell] = DEFINED (PINT 99)',
        '$config_generator_valid(S_finish,pconfiggenerator_finish,"finish")',
        owners('S_finish', 'HOBJECT n_generator', 2),
    ] + public('S_finish') + seek('S_finish', 993, 'S_invoke') + [
        'S_invoke.TODO = (CONFIG_GENERATOR pconfiggenerator_invoke "invoke") :: ptask_invoke*',
        'pconfiggenerator_invoke = pconfiggenerator_finish',
        '(HOBJECT n_generator) <- S_invoke.ALLOCATIONS',
        '$weakref_get(S_invoke,n_watch) = POBJECT n_generator',
        '$config_generator_valid(S_invoke,pconfiggenerator_invoke,"invoke")',
        'S_invoke.PRECISIONINI = $ptascii("7")',
        'S_invoke.STORE[n_value_cell] = DEFINED (PINT 31)',
        'S_invoke.STORE[n_result_cell] = DEFINED (PINT 99)',
        '$config_pack_prefix(pconfiggenerator_invoke.CALL,pconfiggenerator_invoke.ITEMS,false) = (pconfigcall_prefix)',
        'pconfigcall_prefix.SENT = [NAMED_SENT (KNOWN pvalue_option),NAMED_SENT (KNOWN (PINT 17))]',
        owners('S_invoke', 'HOBJECT n_generator', 1),
    ] + public('S_invoke') + seek('S_invoke', 994, 'S_return') + [
        'S_return.STORE[n_result_cell] = DEFINED pvalue_result',
        '$string_bytes(pvalue_result) = ($ptascii("7"))',
        'S_return.PRECISIONINI = $ptascii("17")',
        'S_return.STORE[n_value_cell] = DEFINED (PINT 31)',
        '$weakref_get(S_return,n_watch) = POBJECT n_generator',
        owners('S_return', 'HOBJECT n_generator', 1),
    ] + public('S_return') + seek('S_return', 995, 'S_released') + [
        '~((HOBJECT n_generator) <- S_released.ALLOCATIONS)',
        '$weakref_get(S_released,n_watch) = PNULL',
        'S_released.STORE[n_value_cell] = DEFINED (PINT 31)',
    ] + public('S_released')
    return checks + budget('S_option', 'S_send_budget') + finish(
        'S_released', stdout, ['HOBJECT n_generator'])


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(SOURCES, conditions, HELPERS, model_timeout=300,
        extra_inputs=(Path(__file__),
                      Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
