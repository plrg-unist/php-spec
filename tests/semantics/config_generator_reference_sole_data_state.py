#!/usr/bin/env python3
"""Quiet terminal release preserves a saved Throwable and retires the cell."""
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
        '~$destructor_operational(S_popped)',
        '$eager_operation_pending(S_popped) = (n_exception)',
        '$throwable_live(S_popped,n_exception)',
        'S_raw = $config_generator_discard(S_popped,pconfiggenerator,"next")',
        'PhpStep: S_thrown ~> S_raw',
        'S_raw.TODO = (THROW_SEARCH n_exception) :: ptask_tail*',
        'S_raw.DESTRUCTION.OPERATIONS = S_popped.DESTRUCTION.OPERATIONS',
        'S_raw.STORE = S_popped.STORE',
        'S_raw.EVENTS = S_popped.EVENTS',
        'S_raw.ALLOCATIONS = S_popped.ALLOCATIONS',
        '$throwable_live(S_raw,n_exception)',
    ] + public('S_thrown') + budget('S_thrown', 'S_release_budget') + [
        'S_disposed = S_release_budget_one[.COMPLETION = NORMAL]',
        'S_disposed.TODO = (THROW_SEARCH n_exception) :: ptask_tail*',
        '~((HOBJECT n_generator) <- S_disposed.ALLOCATIONS)',
        '~((HCELL n_value_cell) <- S_disposed.ALLOCATIONS)',
        '$weakref_get(S_disposed,n_watch) = PNULL',
        '$ordinary_reference_value(S_disposed,n_value_cell) = eps',
        '$config_generator_reference_history(S_disposed,pconfiggenerator)',
        '$config_generator_retired_scope(S_disposed,pconfiggenerator)',
        'S_disposed.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_disposed.PRECISIONINI = $ptascii("6")',
        '$throwable_live(S_disposed,n_exception)',
        '$throwable_field(S_disposed,n_exception,"previous") = PNULL',
    ] + public('S_disposed') + seek('S_disposed', 1013, 'S_catch') + [
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
