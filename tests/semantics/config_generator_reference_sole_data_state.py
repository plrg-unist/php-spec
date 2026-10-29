#!/usr/bin/env python3
"""Sole-DATA reference-cell release preserves a saved terminal Throwable."""
from pathlib import Path
from types import SimpleNamespace

import config_generator_reference_sole_data_cases as cases
import list_missing_warning_protocol as shared
from array_generator_unpack_state_review import budget, finish, initial, owners, public, seek


NAME = 'config-generator-reference-sole-data-terminal-throw'
SOURCES = SimpleNamespace(CASES={NAME: cases.CASES[NAME]}, __file__=cases.__file__)
HELPERS = shared.HELPERS + r'''
dec $a73_echo(pstate, ptbytes) : bool
def $a73_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $a73_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 1010) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_GENERATOR pconfiggenerator "next") :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.OBJECTS[pconfiggenerator.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_CLOSED
def $list_warning_frontier(S, 1011) = true
  -- if S.TODO = (GENERATOR_STORAGE_STEP pgenstorage) :: ptask*
  -- if pgenstorage.NEXT = 1
def $list_warning_frontier(S, 1012) = true
  -- if S.TODO = (GENERATOR_STORAGE_STEP pgenstorage) :: ptask*
  -- if pgenstorage.NEXT = 2
def $list_warning_frontier(S, 1013) = $a73_echo(S, $ptascii("C:"))
def $list_warning_frontier(S, 1014) = $a73_echo(S, $ptascii("R:"))
'''


def cell(state, name, identifier):
    return f'$lookup($global_table_view({state}).ENV, $ptascii("{name}")) = ({identifier})'


def conditions(name, program, path, stdout):
    assert name == NAME
    checks = initial(program, path) + seek('S_initial', 1010, 'S_thrown') + [
        'S_thrown.TODO = (THROW_SEARCH n_exception) :: (CONFIG_GENERATOR pconfiggenerator "next") :: ptask_tail*',
        'pconfiggenerator.OBJECT = n_generator',
        'pconfiggenerator.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_option),ENTRY (KINT 1) (DIRECT (PINT 7))]',
        '$string_bytes(pvalue_option) = ($ptascii("precision"))',
        'S_thrown.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
        'pgenerator_closed.PHASE = GENERATOR_CLOSED',
        'pgenerator_closed.FRAME = eps',
        'pgenerator_closed.VALUE = eps',
        'pgenerator_closed.RETURN = eps',
        'pgenerator_closed.REFCELL = (n_value_cell)',
        'pgenerator_closed.KEY = (PINT 1)',
        '$ordinary_reference_value(S_thrown,n_value_cell) = (PINT 8)',
        '$node_children(S_thrown,HOBJECT n_generator) = [HCELL n_value_cell]',
        '$config_generator_reference_history(S_thrown,pconfiggenerator)',
        '$config_generator_reference_storage(S_thrown,pconfiggenerator)',
        '$config_generator_valid(S_thrown,pconfiggenerator,"next")',
        cell('S_thrown', 'input', 'n_input_cell'),
        'S_thrown.STORE[n_input_cell] = DEFINED (PINT 17)',
        cell('S_thrown', 'watch', 'n_watch_cell'),
        'S_thrown.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)',
        '$weakref_get(S_thrown,n_watch) = POBJECT n_generator',
        cell('S_thrown', 'saved', 'n_saved_cell'),
        'S_thrown.STORE[n_saved_cell] = DEFINED (POBJECT n_exception)',
        '$throwable_live(S_thrown,n_exception)',
        '$throwable_field(S_thrown,n_exception,"previous") = PNULL',
        cell('S_thrown', 'result', 'n_result_cell'),
        'S_thrown.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_thrown.PRECISIONINI = $ptascii("6")',
        owners('S_thrown', 'HOBJECT n_generator', 1),
        owners('S_thrown', 'HCELL n_value_cell', 1),
        'S_popped = S_thrown[.TODO = (THROW_SEARCH n_exception) :: ptask_tail*]',
        owners('S_popped', 'HOBJECT n_generator', 0),
        '$config_generator_reference_storage(S_popped,pconfiggenerator)',
        '$config_generator_discard_allowed(S_popped,pconfiggenerator)',
        '$throwable_live(S_popped,n_exception)',
    ] + public('S_thrown') + budget('S_thrown', 'S_release_budget') + seek(
        'S_thrown', 1011, 'S_slot1') + [
        'S_slot1.TODO = (GENERATOR_STORAGE_STEP pgenstorage_slot1) :: ptask_slot1*',
        'pgenstorage_slot1.OBJECT = n_generator',
        'pgenstorage_slot1.NEXT = 1',
        '$generator_storage_valid(S_slot1,pgenstorage_slot1)',
        'S_slot1.DESTRUCTION.OPERATIONS = pdestructionoperation_slot1 :: pdestructionoperation_tail*',
        'pdestructionoperation_slot1.PENDING = (n_exception)',
        'pdestructionoperation_slot1.SOURCE = CONFIG_GENERATOR pconfiggenerator "next"',
        '$ordinary_reference_value(S_slot1,n_value_cell) = (PINT 8)',
        '$throwable_live(S_slot1,n_exception)',
        '$weakref_get(S_slot1,n_watch) = POBJECT n_generator',
        owners('S_slot1', 'HCELL n_value_cell', 1),
    ] + public('S_slot1') + seek('S_slot1', 1012, 'S_slot2') + [
        'S_slot2.TODO = (GENERATOR_STORAGE_STEP pgenstorage_slot2) :: ptask_slot2*',
        'pgenstorage_slot2.OBJECT = n_generator',
        'pgenstorage_slot2.NEXT = 2',
        '$generator_storage_valid(S_slot2,pgenstorage_slot2)',
        'S_slot2.DESTRUCTION.OPERATIONS = pdestructionoperation_slot2 :: pdestructionoperation_tail2*',
        'pdestructionoperation_slot2.PENDING = (n_exception)',
        'pdestructionoperation_slot2.SOURCE = CONFIG_GENERATOR pconfiggenerator "next"',
        '~((HCELL n_value_cell) <- S_slot2.ALLOCATIONS)',
        '$ordinary_reference_value(S_slot2,n_value_cell) = eps',
        '(HOBJECT n_generator) <- S_slot2.ALLOCATIONS',
        '$throwable_live(S_slot2,n_exception)',
        '$weakref_get(S_slot2,n_watch) = POBJECT n_generator',
    ] + public('S_slot2') + seek('S_slot2', 1013, 'S_catch') + [
        '~((HOBJECT n_generator) <- S_catch.ALLOCATIONS)',
        '~((HCELL n_value_cell) <- S_catch.ALLOCATIONS)',
        '$weakref_get(S_catch,n_watch) = PNULL',
        '$ordinary_reference_value(S_catch,n_value_cell) = eps',
        cell('S_catch', 'caught', 'n_caught_cell'),
        'S_catch.STORE[n_caught_cell] = DEFINED (POBJECT n_exception)',
        'S_catch.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_catch.PRECISIONINI = $ptascii("6")',
        '$throwable_live(S_catch,n_exception)',
        '$throwable_field(S_catch,n_exception,"previous") = PNULL',
    ] + public('S_catch') + seek('S_catch', 1014, 'S_recovery') + [
        '$weakref_get(S_recovery,n_watch) = PNULL',
        'S_recovery.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_recovery.PRECISIONINI = $ptascii("6")',
    ] + public('S_recovery')
    return checks + finish('S_recovery', stdout, ['HOBJECT n_generator', 'HCELL n_value_cell'])


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(SOURCES, conditions, HELPERS, model_timeout=300,
        extra_inputs=(Path(__file__),
                      Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
