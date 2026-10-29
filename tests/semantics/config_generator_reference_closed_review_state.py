#!/usr/bin/env python3
"""A real storage pin retires the last local cell before NULL reception."""
from pathlib import Path
from types import SimpleNamespace

import config_generator_reference_closed_review_cases as cases
import list_missing_warning_protocol as shared
from array_generator_unpack_state_review import budget, finish, initial, owners, public, seek

NAME = 'config-generator-reference-closed-null-handler-return'
SOURCES = SimpleNamespace(CASES={NAME: cases.CASES[NAME]}, __file__=cases.__file__)
HELPERS = shared.HELPERS + r'''
dec $a73_peer_echo(pstate, ptbytes) : bool
def $a73_peer_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $a73_peer_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 1000) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask*
  -- if pconfiggenerator.ITEMS = eps
def $list_warning_frontier(S, 1001) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask*
  -- if |pconfiggenerator.ITEMS| = 1
def $list_warning_frontier(S, 1002) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "finish") :: ptask*
def $list_warning_frontier(S, 1003) = true
  -- if S.TODO = (GENERATOR_STORAGE_STEP pgenstorage) :: ptask*
  -- if pgenstorage.NEXT = 1
def $list_warning_frontier(S, 1004) = true
  -- if S.TODO = (GENERATOR_STORAGE_STEP pgenstorage) :: ptask*
  -- if pgenstorage.NEXT = 2
def $list_warning_frontier(S, 1005) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "storage-released") :: ptask*
def $list_warning_frontier(S, 1006) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "invoke") :: ptask*
def $list_warning_frontier(S, 1007) = $a73_peer_echo(S, $ptascii("H:"))
def $list_warning_frontier(S, 1008) = true
  -- if S.TODO = (CONFIG_INI_NULL_RESULT pconfigcall) :: ptask*
def $list_warning_frontier(S, 1009) = $a73_peer_echo(S, $ptascii("R:"))
'''


def cell(state, name, identifier):
    return f'$lookup($global_table_view({state}).ENV, $ptascii("{name}")) = ({identifier})'


def conditions(name, program, path, stdout):
    assert name == NAME
    checks = initial(program, path) + seek('S_initial', 1000, 'S_option') + [
        'S_option.TODO = (CONFIG_GENERATOR pconfiggenerator_option "ready") :: ptask_option*',
        'pconfiggenerator_option.OBJECT = n_generator',
        'pconfiggenerator_option.CALL.OWNER = (n_callee)',
        'S_option.OBJECTS[n_generator] = GENERATOR pgenerator_option',
        'pgenerator_option.PHASE = GENERATOR_PAUSED',
        'pgenerator_option.VALUE = eps',
        'pgenerator_option.REFCELL = (n_option_cell)',
        'pgenerator_option.FRAME = (pframe_option)',
        'pframe_option.LOCALS = (psymboltable_option)',
        '$lookup(psymboltable_option.ENV,$ptascii("option")) = (n_option_cell)',
        '$lookup($global_table_view(S_option).ENV,$ptascii("option")) = eps',
        '$ordinary_reference_value(S_option,n_option_cell) = (PNULL)',
        '$config_generator_value(S_option,pconfiggenerator_option) = (PNULL)',
        '$config_generator_valid(S_option,pconfiggenerator_option,"ready")',
        cell('S_option', 'input', 'n_input_cell'),
        'S_option.STORE[n_input_cell] = DEFINED (PINT 17)',
        cell('S_option', 'watch', 'n_watch_cell'),
        'S_option.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)',
        cell('S_option', 'result', 'n_result_cell'),
        'S_option.STORE[n_result_cell] = DEFINED (PINT 99)',
        cell('S_option', 'after', 'n_after_cell'),
        'S_option.STORE[n_after_cell] = DEFINED (PINT 0)',
        owners('S_option', 'HOBJECT n_generator', 1),
        'PhpStep: S_option ~> S_first_sent',
        'S_first_sent.TODO = (CONFIG_GENERATOR pconfiggenerator_first "next") :: ptask_option*',
        'pconfiggenerator_first = pconfiggenerator_option[.ITEMS = [ENTRY (KINT 3) (DIRECT PNULL)]]',
    ] + public('S_option') + seek('S_first_sent', 1001, 'S_value') + [
        'S_value.TODO = (CONFIG_GENERATOR pconfiggenerator_value "ready") :: ptask_value*',
        'pconfiggenerator_value = pconfiggenerator_first',
        'S_value.OBJECTS[n_generator] = GENERATOR pgenerator_value',
        'pgenerator_value.VALUE = eps',
        'pgenerator_value.REFCELL = (n_value_cell)',
        'pgenerator_value.FRAME = (pframe_value)',
        'pframe_value.LOCALS = (psymboltable_value)',
        '$lookup(psymboltable_value.ENV,$ptascii("value")) = (n_value_cell)',
        '$lookup($global_table_view(S_value).ENV,$ptascii("value")) = eps',
        '$ordinary_reference_value(S_value,n_value_cell) = (PINT 13)',
        '$config_generator_value(S_value,pconfiggenerator_value) = (PINT 13)',
        'S_value.STORE[n_option_cell] = DEFINED pvalue_option_live',
        '$string_bytes(pvalue_option_live) = ($ptascii("precision"))',
        'PhpStep: S_value ~> S_second_sent',
        'S_second_sent.TODO = (CONFIG_GENERATOR pconfiggenerator_second "next") :: ptask_value*',
        'pconfiggenerator_second = pconfiggenerator_value[.ITEMS = [ENTRY (KINT 3) (DIRECT PNULL),ENTRY (KINT 3) (DIRECT (PINT 13))]]',
    ] + public('S_value') + seek('S_second_sent', 1002, 'S_finish') + [
        'S_finish.TODO = (CONFIG_GENERATOR pconfiggenerator_finish "finish") :: ptask_finish*',
        'pconfiggenerator_finish = pconfiggenerator_second',
        'S_finish.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
        'pgenerator_closed.PHASE = GENERATOR_CLOSED',
        'pgenerator_closed.FRAME = eps',
        'pgenerator_closed.VALUE = eps',
        'pgenerator_closed.REFCELL = (n_value_cell)',
        '$ordinary_reference_value(S_finish,n_value_cell) = (PINT 31)',
        '$node_children(S_finish,HOBJECT n_generator) = [HCELL n_value_cell]',
        'S_finish.STORE[n_after_cell] = DEFINED (PINT 31)',
        'S_finish.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_finish.PRECISIONINI = $ptascii("19")',
        '~((HCELL n_option_cell) <- S_finish.ALLOCATIONS)',
        '$config_generator_finish_allowed(S_finish,pconfiggenerator_finish)',
        owners('S_finish', 'HOBJECT n_generator', 1),
        owners('S_finish', 'HCELL n_value_cell', 1),
        # Constructed guards have no additional source-agreement credit.
        'S_owning = S_finish[.STORE[n_value_cell] = DEFINED (POBJECT n_watch)]',
        '~$config_generator_finish_allowed(S_owning,pconfiggenerator_finish)',
        'S_debt = S_finish[.LITERALREFDEBTS = [n_value_cell]]',
        '~$config_generator_finish_allowed(S_debt,pconfiggenerator_finish)',
        'S_unregistered = S_finish[.REFCELLS = eps]',
        '~$config_generator_finish_allowed(S_unregistered,pconfiggenerator_finish)',
    ] + public('S_finish') + budget('S_finish', 'S_release_budget') + seek(
        'S_finish', 1003, 'S_slot1') + [
        'S_slot1.TODO = (GENERATOR_STORAGE_STEP pgenstorage_slot1) :: ptask_slot1*',
        'pgenstorage_slot1.OBJECT = n_generator',
        'pgenstorage_slot1.NEXT = 1',
        '$generator_storage_valid(S_slot1,pgenstorage_slot1)',
        '$generator_storage_slot(pgenerator_closed,1) = [HCELL n_value_cell]',
        '$ordinary_reference_value(S_slot1,n_value_cell) = (PINT 31)',
        '$weakref_get(S_slot1,n_watch) = POBJECT n_generator',
        owners('S_slot1', 'HOBJECT n_generator', 1),
        owners('S_slot1', 'HCELL n_value_cell', 1),
    ] + public('S_slot1') + seek('S_slot1', 1004, 'S_slot2') + [
        'S_slot2.TODO = (GENERATOR_STORAGE_STEP pgenstorage_slot2) :: ptask_slot2*',
        'pgenstorage_slot2.OBJECT = n_generator',
        'pgenstorage_slot2.NEXT = 2',
        '$generator_storage_valid(S_slot2,pgenstorage_slot2)',
        '~((HCELL n_value_cell) <- S_slot2.ALLOCATIONS)',
        'S_slot2.STORE[n_value_cell] = DEFINED (PINT 31)',
        '$ordinary_reference_value(S_slot2,n_value_cell) = eps',
        '(HOBJECT n_generator) <- S_slot2.ALLOCATIONS',
        '$weakref_get(S_slot2,n_watch) = POBJECT n_generator',
        owners('S_slot2', 'HOBJECT n_generator', 1),
    ] + public('S_slot2') + seek('S_slot2', 1005, 'S_retired') + [
        'S_retired.TODO = (CONFIG_GENERATOR pconfiggenerator_retired "storage-released") :: ptask_retired*',
        'pconfiggenerator_retired = pconfiggenerator_finish',
        '~((HOBJECT n_generator) <- S_retired.ALLOCATIONS)',
        '~((HCELL n_value_cell) <- S_retired.ALLOCATIONS)',
        '$weakref_get(S_retired,n_watch) = PNULL',
        '$ordinary_reference_value(S_retired,n_value_cell) = eps',
        '$config_generator_value(S_retired,pconfiggenerator_retired) = eps',
        '$config_generator_history(S_retired,pconfiggenerator_retired)',
        '$config_generator_retired_scope(S_retired,pconfiggenerator_retired)',
        '~$config_generator_scope(S_retired,pconfiggenerator_retired)',
        '$config_generator_valid(S_retired,pconfiggenerator_retired,"storage-released")',
        '~$config_generator_retired_scope(S_retired[.CODE = eps],pconfiggenerator_retired)',
        'S_badid = S_retired[.OBJECTS[n_generator] = GENERATOR pgenerator_closed[.REFCELL = (|S_retired.STORE|)]]',
        '~$config_generator_retired_scope(S_badid,pconfiggenerator_retired)',
    ] + public('S_retired') + seek('S_retired', 1006, 'S_invoke') + [
        'S_invoke.TODO = (CONFIG_GENERATOR pconfiggenerator_invoke "invoke") :: ptask_invoke*',
        'pconfiggenerator_invoke = pconfiggenerator_finish',
        '$config_generator_valid(S_invoke,pconfiggenerator_invoke,"invoke")',
        '$config_pack_prefix(pconfiggenerator_invoke.CALL,pconfiggenerator_invoke.ITEMS,false) = (pconfigcall_prefix)',
        'pconfigcall = pconfigcall_prefix[.INDEX = 1]',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (PINT 13))]',
        '$config_selected_valid(S_invoke,pconfigcall)',
        '$weakref_get(S_invoke,n_watch) = PNULL',
        'S_invoke.STORE[n_result_cell] = DEFINED (PINT 99)',
    ] + public('S_invoke') + seek('S_invoke', 1007, 'S_handler') + [
        'S_handler.CURRENT = (pcallcontext_handler)',
        '$error_context_call(S_handler,pcallcontext_handler) = (perrorcall)',
        'perrorcall.RESUME = CONFIG_INI_NULL_RESULT pconfigcall',
        'perrorcall.LEVEL = 8192',
        'perrorcall.MESSAGE = $config_ini_null_message(pconfigcall)',
        '$weakref_get(S_handler,n_watch) = PNULL',
        '$ordinary_reference_value(S_handler,n_value_cell) = eps',
        'S_handler.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_handler.STORE[n_after_cell] = DEFINED (PINT 31)',
    ] + public('S_handler') + seek('S_handler', 1008, 'S_null') + [
        'S_null.TODO = (CONFIG_INI_NULL_RESULT pconfigcall) :: ptask_null*',
        '$config_ini_null_valid(S_null,pconfigcall)',
        '$weakref_get(S_null,n_watch) = PNULL',
        '$ordinary_reference_value(S_null,n_value_cell) = eps',
        'S_null.PRECISIONINI = $ptascii("19")',
        'S_null.STORE[n_result_cell] = DEFINED (PINT 99)',
    ] + public('S_null') + seek('S_null', 1009, 'S_return') + [
        'S_return.STORE[n_result_cell] = DEFINED (PBOOL false)',
        'S_return.PRECISIONINI = $ptascii("19")',
        '$weakref_get(S_return,n_watch) = PNULL',
        '$ordinary_reference_value(S_return,n_value_cell) = eps',
    ] + public('S_return')
    return checks + finish('S_return', stdout, [
        'HOBJECT n_generator', 'HCELL n_value_cell', 'HCELL n_option_cell'])


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(SOURCES, conditions, HELPERS, model_timeout=300,
        extra_inputs=(Path(__file__),
                      Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
