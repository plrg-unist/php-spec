#!/usr/bin/env python3
"""DATA dies while outside aliases keep the cell live through a NULL handler."""
from pathlib import Path
from types import SimpleNamespace

import config_generator_reference_outside_alias_review_cases as cases
import list_missing_warning_protocol as shared
from array_generator_unpack_state_review import budget, finish, initial, owners, public, seek

NAME = 'config-generator-reference-outside-alias-null-handler-return'
SOURCES = SimpleNamespace(CASES={NAME: cases.CASES[NAME]}, __file__=cases.__file__)
HELPERS = shared.HELPERS + r'''
dec $a74_peer_echo(pstate, ptbytes) : bool
def $a74_peer_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $a74_peer_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 1100) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask*
  -- if pconfiggenerator.ITEMS = eps
def $list_warning_frontier(S, 1101) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask*
  -- if |pconfiggenerator.ITEMS| = 1
def $list_warning_frontier(S, 1102) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "finish") :: ptask*
def $list_warning_frontier(S, 1103) = true
  -- if S.TODO = (GENERATOR_STORAGE_STEP pgenstorage) :: ptask*
  -- if pgenstorage.NEXT = 1
def $list_warning_frontier(S, 1104) = true
  -- if S.TODO = (GENERATOR_STORAGE_STEP pgenstorage) :: ptask*
  -- if pgenstorage.NEXT = 2
def $list_warning_frontier(S, 1105) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "storage-released") :: ptask*
def $list_warning_frontier(S, 1106) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "invoke") :: ptask*
def $list_warning_frontier(S, 1107) = $a74_peer_echo(S, $ptascii("H:"))
def $list_warning_frontier(S, 1108) = $a74_peer_echo(S, $ptascii("M:"))
def $list_warning_frontier(S, 1109) = true
  -- if S.TODO = (CONFIG_INI_NULL_RESULT pconfigcall) :: ptask*
def $list_warning_frontier(S, 1110) = $a74_peer_echo(S, $ptascii("R:"))
'''


def cell(state, name, identifier):
    return f'$lookup($global_table_view({state}).ENV, $ptascii("{name}")) = ({identifier})'


def conditions(name, program, path, stdout):
    assert name == NAME
    checks = initial(program, path) + seek('S_initial', 1100, 'S_option') + [
        'S_option.TODO = (CONFIG_GENERATOR pconfiggenerator_option "ready") :: ptask_option*',
        'pconfiggenerator_option.OBJECT = n_generator',
        'pconfiggenerator_option.CALL.OWNER = (n_callee)',
        'S_option.OBJECTS[n_generator] = GENERATOR pgenerator_option',
        'pgenerator_option.VALUE = eps',
        'pgenerator_option.REFCELL = (n_option_cell)',
        '$ordinary_reference_value(S_option,n_option_cell) = (PNULL)',
        cell('S_option', 'value', 'n_value_cell'),
        cell('S_option', 'alias', 'n_value_cell'),
        'S_option.STORE[n_value_cell] = DEFINED (PINT 13)',
        cell('S_option', 'input', 'n_input_cell'),
        'S_option.STORE[n_input_cell] = DEFINED (PINT 17)',
        cell('S_option', 'watch', 'n_watch_cell'),
        'S_option.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)',
        cell('S_option', 'result', 'n_result_cell'),
        'S_option.STORE[n_result_cell] = DEFINED (PINT 99)',
        owners('S_option', 'HOBJECT n_generator', 1),
        'PhpStep: S_option ~> S_first_sent',
        'S_first_sent.TODO = (CONFIG_GENERATOR pconfiggenerator_first "next") :: ptask_option*',
        'pconfiggenerator_first = pconfiggenerator_option[.ITEMS = [ENTRY (KINT 3) (DIRECT PNULL)]]',
    ] + public('S_option') + seek('S_first_sent', 1101, 'S_value') + [
        'S_value.TODO = (CONFIG_GENERATOR pconfiggenerator_value "ready") :: ptask_value*',
        'pconfiggenerator_value = pconfiggenerator_first',
        'S_value.OBJECTS[n_generator] = GENERATOR pgenerator_value',
        'pgenerator_value.VALUE = eps',
        'pgenerator_value.REFCELL = (n_value_cell)',
        '$ordinary_reference_value(S_value,n_value_cell) = (PINT 13)',
        '$config_generator_value(S_value,pconfiggenerator_value) = (PINT 13)',
        'S_value.STORE[n_option_cell] = DEFINED pvalue_option_live',
        '$string_bytes(pvalue_option_live) = ($ptascii("precision"))',
        'PhpStep: S_value ~> S_second_sent',
        'S_second_sent.TODO = (CONFIG_GENERATOR pconfiggenerator_second "next") :: ptask_value*',
        'pconfiggenerator_second = pconfiggenerator_value[.ITEMS = [ENTRY (KINT 3) (DIRECT PNULL),ENTRY (KINT 3) (DIRECT (PINT 13))]]',
    ] + public('S_value') + seek('S_second_sent', 1102, 'S_finish') + [
        'S_finish.TODO = (CONFIG_GENERATOR pconfiggenerator_finish "finish") :: ptask_finish*',
        'pconfiggenerator_finish = pconfiggenerator_second',
        'S_finish.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
        'pgenerator_closed.PHASE = GENERATOR_CLOSED',
        'pgenerator_closed.FRAME = eps',
        'pgenerator_closed.REFCELL = (n_value_cell)',
        '$ordinary_reference_value(S_finish,n_value_cell) = (PINT 31)',
        '$node_children(S_finish,HOBJECT n_generator) = [HCELL n_value_cell]',
        '$config_generator_reference_storage(S_finish,pconfiggenerator_finish)',
        'S_finish.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_finish.PRECISIONINI = $ptascii("19")',
        owners('S_finish', 'HOBJECT n_generator', 1),
        owners('S_finish', 'HCELL n_value_cell', 3),
        # Owning/debt payloads at DATA release are constructed refusal controls.
        'S_owning = S_finish[.STORE[n_value_cell] = DEFINED (POBJECT n_watch)]',
        '~$config_generator_finish_allowed(S_owning,pconfiggenerator_finish)',
        'S_debt = S_finish[.LITERALREFDEBTS = [n_value_cell]]',
        '~$config_generator_finish_allowed(S_debt,pconfiggenerator_finish)',
    ] + public('S_finish') + budget('S_finish', 'S_release_budget') + seek(
        'S_finish', 1103, 'S_slot1') + [
        'S_slot1.TODO = (GENERATOR_STORAGE_STEP pgenstorage_slot1) :: ptask_slot1*',
        'pgenstorage_slot1.OBJECT = n_generator',
        '$generator_storage_valid(S_slot1,pgenstorage_slot1)',
        '$ordinary_reference_value(S_slot1,n_value_cell) = (PINT 31)',
        owners('S_slot1', 'HOBJECT n_generator', 1),
        owners('S_slot1', 'HCELL n_value_cell', 3),
    ] + public('S_slot1') + seek('S_slot1', 1104, 'S_slot2') + [
        'S_slot2.TODO = (GENERATOR_STORAGE_STEP pgenstorage_slot2) :: ptask_slot2*',
        'pgenstorage_slot2.OBJECT = n_generator',
        '$generator_storage_valid(S_slot2,pgenstorage_slot2)',
        '(HCELL n_value_cell) <- S_slot2.ALLOCATIONS',
        '$ordinary_reference_value(S_slot2,n_value_cell) = (PINT 31)',
        '$node_children(S_slot2,HOBJECT n_generator) = eps',
        '$weakref_get(S_slot2,n_watch) = POBJECT n_generator',
        owners('S_slot2', 'HOBJECT n_generator', 1),
        owners('S_slot2', 'HCELL n_value_cell', 2),
    ] + public('S_slot2') + seek('S_slot2', 1105, 'S_retired') + [
        'S_retired.TODO = (CONFIG_GENERATOR pconfiggenerator_retired "storage-released") :: ptask_retired*',
        'pconfiggenerator_retired = pconfiggenerator_finish',
        '~((HOBJECT n_generator) <- S_retired.ALLOCATIONS)',
        '(HCELL n_value_cell) <- S_retired.ALLOCATIONS',
        '$weakref_get(S_retired,n_watch) = PNULL',
        '$ordinary_reference_value(S_retired,n_value_cell) = (PINT 31)',
        '$config_generator_retired_scope(S_retired,pconfiggenerator_retired)',
        '$config_generator_valid(S_retired,pconfiggenerator_retired,"storage-released")',
        owners('S_retired', 'HCELL n_value_cell', 2),
    ] + public('S_retired') + seek('S_retired', 1106, 'S_invoke') + [
        'S_invoke.TODO = (CONFIG_GENERATOR pconfiggenerator_invoke "invoke") :: ptask_invoke*',
        'pconfiggenerator_invoke = pconfiggenerator_finish',
        '$config_pack_prefix(pconfiggenerator_invoke.CALL,pconfiggenerator_invoke.ITEMS,false) = (pconfigcall_prefix)',
        'pconfigcall = pconfigcall_prefix[.INDEX = 1]',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (PINT 13))]',
        '$config_selected_valid(S_invoke,pconfigcall)',
    ] + public('S_invoke') + seek('S_invoke', 1107, 'S_handler') + [
        'S_handler.CURRENT = (pcallcontext_handler)',
        '$error_context_call(S_handler,pcallcontext_handler) = (perrorcall)',
        'perrorcall.RESUME = CONFIG_INI_NULL_RESULT pconfigcall',
        '$weakref_get(S_handler,n_watch) = PNULL',
        '$ordinary_reference_value(S_handler,n_value_cell) = (PINT 31)',
    ] + public('S_handler') + seek('S_handler', 1108, 'S_mutated') + [
        cell('S_mutated', 'value', 'n_value_cell'),
        cell('S_mutated', 'alias', 'n_value_cell'),
        '$ordinary_reference_value(S_mutated,n_value_cell) = (PARRAY n_array)',
        'S_mutated.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 41))]',
        '~$config_iterator_scalar(S_mutated,PARRAY n_array)',
        '$config_generator_value(S_mutated,pconfiggenerator_retired) = eps',
        '$config_generator_retired_scope(S_mutated,pconfiggenerator_retired)',
        '$weakref_get(S_mutated,n_watch) = PNULL',
        'S_mutated.STORE[n_result_cell] = DEFINED (PINT 99)',
    ] + public('S_mutated') + seek('S_mutated', 1109, 'S_null') + [
        'S_null.TODO = (CONFIG_INI_NULL_RESULT pconfigcall) :: ptask_null*',
        '$config_ini_null_valid(S_null,pconfigcall)',
        '$ordinary_reference_value(S_null,n_value_cell) = (PARRAY n_array)',
        'S_null.STORE[n_result_cell] = DEFINED (PINT 99)',
        '$weakref_get(S_null,n_watch) = PNULL',
    ] + public('S_null') + seek('S_null', 1110, 'S_return') + [
        'S_return.STORE[n_result_cell] = DEFINED (PBOOL false)',
        'S_return.PRECISIONINI = $ptascii("19")',
        '$ordinary_reference_value(S_return,n_value_cell) = (PARRAY n_array)',
        '$weakref_get(S_return,n_watch) = PNULL',
    ] + public('S_return')
    return checks + finish('S_return', stdout, ['HOBJECT n_generator'])


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(SOURCES, conditions, HELPERS, model_timeout=300,
        extra_inputs=(Path(__file__),
                      Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
