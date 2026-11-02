#!/usr/bin/env python3
"""A factory returned BYREF Generator leaves its owning cell with two aliases after abort."""
from pathlib import Path
from types import SimpleNamespace

import config_generator_factory_owning_alias_cases as cases
import list_missing_warning_protocol as shared
from array_generator_unpack_state_review import budget, finish, initial, owners, public, seek


NAME = 'config-generator-factory-owning-alias-object-terminal-throw'
SOURCES = SimpleNamespace(CASES={NAME: cases.CASES[NAME]}, __file__=cases.__file__)
HELPERS = shared.HELPERS + r'''
dec $a88_author_echo(pstate, ptbytes) : bool
def $a88_author_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $a88_author_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 2880) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_GENERATOR pconfiggenerator "next") :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.OBJECTS[pconfiggenerator.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_CLOSED
def $list_warning_frontier(S, 2881) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_GENERATOR pconfiggenerator "input-release") :: ptask*
def $list_warning_frontier(S, 2882) = $a88_author_echo(S, $ptascii("S:"))
def $list_warning_frontier(S, 2883) = $a88_author_echo(S, $ptascii("W:"))
def $list_warning_frontier(S, 2884) = $a88_author_echo(S, $ptascii("L:"))
def $list_warning_frontier(S, 2885) = $a88_author_echo(S, $ptascii("U:"))
def $list_warning_frontier(S, 2886) = $a88_author_echo(S, $ptascii("R:"))
'''


def cell(state, name, identifier):
    return f'$lookup($global_table_view({state}).ENV, $ptascii("{name}")) = ({identifier})'


def conditions(name, program, path, stdout):
    assert name == NAME
    checks = initial(program, path) + seek('S_initial', 2880, 'S_thrown') + [
        'S_thrown.TODO = (THROW_SEARCH n_exception) :: (CONFIG_GENERATOR pconfiggenerator "next") :: ptask_tail*',
        'pconfiggenerator.OBJECT = n_generator',
        'pconfiggenerator.INPUT = KNOWN (POBJECT n_generator)',
        'pconfiggenerator.PRODUCER = eps',
        'pconfiggenerator.CALL.OWNER = eps',
        '$config_generator_owning_input(pconfiggenerator)',
        'pconfiggenerator.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_option),ENTRY (KINT 1) (DIRECT (POBJECT n_payload))]',
        '$string_bytes(pvalue_option) = ($ptascii("precision"))',
        '$config_generator_factory_reference_input(S_thrown,pconfiggenerator)',
        '~$config_generator_temporary_reference_input(S_thrown,pconfiggenerator)',
        '$config_generator_temporary_reference_owning_last_items(S_thrown,pconfiggenerator)',
        'S_thrown.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
        'pgenerator_closed.PHASE = GENERATOR_CLOSED',
        'pgenerator_closed.FRAME = eps',
        'pgenerator_closed.VALUE = eps',
        'pgenerator_closed.RETURN = eps',
        'pgenerator_closed.REFCELL = (n_payloadref)',
        'pgenerator_closed.KEY = (PINT 1)',
        '$ordinary_reference_value(S_thrown,n_payloadref) = (POBJECT n_payload)',
        '$node_children(S_thrown,HOBJECT n_generator) = [HCELL n_payloadref]',
        '$node_children(S_thrown,HCELL n_payloadref) = [HOBJECT n_payload]',
        cell('S_thrown', 'slot', 'n_payloadref'),
        cell('S_thrown', 'alias', 'n_payloadref'),
        '$config_generator_reference_history(S_thrown,pconfiggenerator)',
        '$config_generator_temporary_reference_owning_storage(S_thrown,pconfiggenerator)',
        '$config_generator_finish_allowed(S_thrown,pconfiggenerator)',
        '$config_generator_valid(S_thrown,pconfiggenerator,"next")',
        cell('S_thrown', 'payloadWatch', 'n_watch_cell'),
        'S_thrown.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)',
        '$weakref_get(S_thrown,n_watch) = POBJECT n_payload',
        cell('S_thrown', 'genWatch', 'n_genwatch_cell'),
        'S_thrown.STORE[n_genwatch_cell] = DEFINED (POBJECT n_genwatch)',
        '$weakref_get(S_thrown,n_genwatch) = POBJECT n_generator',
        '$heap_count(HOBJECT n_payload,$pools_nodes(S_thrown.POOLS)) = 0',
        cell('S_thrown', 'saved', 'n_saved_cell'),
        'S_thrown.STORE[n_saved_cell] = DEFINED (POBJECT n_exception)',
        '$throwable_live(S_thrown,n_exception)',
        '$throwable_field(S_thrown,n_exception,"previous") = PNULL',
        cell('S_thrown', 'result', 'n_result_cell'),
        'S_thrown.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_thrown.PRECISIONINI = $ptascii("6")',
        owners('S_thrown', 'HOBJECT n_generator', 2),
        owners('S_thrown', 'HCELL n_payloadref', 3),
        owners('S_thrown', 'HOBJECT n_payload', 2),
        'S_popped = S_thrown[.TODO = (THROW_SEARCH n_exception) :: ptask_tail*]',
        owners('S_popped', 'HOBJECT n_generator', 0),
        owners('S_popped', 'HCELL n_payloadref', 3),
        owners('S_popped', 'HOBJECT n_payload', 1),
        '$weakref_get(S_popped,n_genwatch) = POBJECT n_generator',
        '$config_generator_temporary_reference_owning_storage(S_popped,pconfiggenerator)',
        '$config_generator_discard_allowed(S_popped,pconfiggenerator)',
        '~$destructor_operational(S_popped)',
        '$eager_operation_pending(S_popped) = (n_exception)',
        'S_reintroduced = $config_generator_discard_state(S_popped,pconfiggenerator,"next")',
        'S_reintroduced.TODO = (THROW_SEARCH n_exception) :: (CONFIG_GENERATOR pconfiggenerator "input-release") :: ptask_tail*',
        'S_first_raw = $config_generator_discard(S_popped,pconfiggenerator,"next")',
        'S_first_raw = S_reintroduced',
        'PhpStep: S_thrown ~> S_first_raw',
    ] + public('S_thrown') + seek('S_thrown', 2881, 'S_input') + [
        'S_input.TODO = (THROW_SEARCH n_exception) :: (CONFIG_GENERATOR pconfiggenerator "input-release") :: ptask_input*',
        '$config_generator_valid(S_input,pconfiggenerator,"input-release")',
        '$ordinary_reference_value(S_input,n_payloadref) = (POBJECT n_payload)',
        '$config_generator_temporary_reference_owning_storage(S_input,pconfiggenerator)',
        owners('S_input', 'HOBJECT n_generator', 1),
        owners('S_input', 'HCELL n_payloadref', 3),
        owners('S_input', 'HOBJECT n_payload', 2),
        '$weakref_get(S_input,n_genwatch) = POBJECT n_generator',
        'S_second_popped = S_input[.TODO = (THROW_SEARCH n_exception) :: ptask_input*]',
        owners('S_second_popped', 'HOBJECT n_generator', 0),
        owners('S_second_popped', 'HCELL n_payloadref', 3),
        owners('S_second_popped', 'HOBJECT n_payload', 1),
        '$config_generator_discard_allowed(S_second_popped,pconfiggenerator)',
        'S_second_raw = $config_generator_discard(S_second_popped,pconfiggenerator,"input-release")',
        'S_second_raw.TODO = (THROW_SEARCH n_exception) :: ptask_input*',
        'S_second_raw.STORE = S_second_popped.STORE',
        'S_second_raw.EVENTS = S_second_popped.EVENTS',
        'S_second_raw.ALLOCATIONS = S_second_popped.ALLOCATIONS',
        '$throwable_live(S_second_raw,n_exception)',
        'PhpStep: S_input ~> S_second_raw',
    ] + public('S_input') + budget('S_input', 'S_release_budget') + [
        'S_disposed = S_release_budget_one[.COMPLETION = NORMAL]',
        'S_disposed.TODO = (THROW_SEARCH n_exception) :: ptask_input*',
        '~((HOBJECT n_generator) <- S_disposed.ALLOCATIONS)',
        '(HCELL n_payloadref) <- S_disposed.ALLOCATIONS',
        '(HOBJECT n_payload) <- S_disposed.ALLOCATIONS',
        cell('S_disposed', 'slot', 'n_payloadref'),
        cell('S_disposed', 'alias', 'n_payloadref'),
        '$weakref_get(S_disposed,n_watch) = POBJECT n_payload',
        '$weakref_get(S_disposed,n_genwatch) = PNULL',
        owners('S_disposed', 'HCELL n_payloadref', 2),
        owners('S_disposed', 'HOBJECT n_payload', 1),
        '$config_generator_reference_history(S_disposed,pconfiggenerator)',
        '$config_generator_temporary_reference_owning_last_items(S_disposed,pconfiggenerator)',
        '$config_generator_retired_scope(S_disposed,pconfiggenerator)',
        '~$config_generator_temporary_reference_owning_storage(S_disposed,pconfiggenerator)',
        'S_disposed.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_disposed.PRECISIONINI = $ptascii("6")',
        '$throwable_live(S_disposed,n_exception)',
    ] + public('S_disposed') + seek('S_disposed', 2882, 'S_catch') + [
        '~((HOBJECT n_generator) <- S_catch.ALLOCATIONS)',
        '(HCELL n_payloadref) <- S_catch.ALLOCATIONS',
        '(HOBJECT n_payload) <- S_catch.ALLOCATIONS',
        '$weakref_get(S_catch,n_watch) = POBJECT n_payload',
        '$weakref_get(S_catch,n_genwatch) = PNULL',
        cell('S_catch', 'slot', 'n_payloadref'),
        cell('S_catch', 'alias', 'n_payloadref'),
        owners('S_catch', 'HCELL n_payloadref', 2),
        owners('S_catch', 'HOBJECT n_payload', 1),
        cell('S_catch', 'caught', 'n_caught_cell'),
        'S_catch.STORE[n_caught_cell] = DEFINED (POBJECT n_exception)',
        'S_catch.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_catch.PRECISIONINI = $ptascii("6")',
        '$throwable_live(S_catch,n_exception)',
        '$throwable_field(S_catch,n_exception,"previous") = PNULL',
    ] + public('S_catch') + seek('S_catch', 2883, 'S_after') + [
        '$weakref_get(S_after,n_watch) = POBJECT n_payload',
        '$weakref_get(S_after,n_genwatch) = PNULL',
        owners('S_after', 'HCELL n_payloadref', 2),
        'S_after.STORE[n_result_cell] = DEFINED (PINT 99)',
    ] + public('S_after') + seek('S_after', 2884, 'S_slot_unset') + [
        '$lookup($global_table_view(S_slot_unset).ENV,$ptascii("slot")) = eps',
        cell('S_slot_unset', 'alias', 'n_payloadref'),
        '$weakref_get(S_slot_unset,n_watch) = POBJECT n_payload',
        '$weakref_get(S_slot_unset,n_genwatch) = PNULL',
        owners('S_slot_unset', 'HCELL n_payloadref', 1),
        owners('S_slot_unset', 'HOBJECT n_payload', 1),
    ] + public('S_slot_unset') + seek('S_slot_unset', 2885, 'S_alias_unset') + [
        '$lookup($global_table_view(S_alias_unset).ENV,$ptascii("alias")) = eps',
        '~((HCELL n_payloadref) <- S_alias_unset.ALLOCATIONS)',
        '~((HOBJECT n_payload) <- S_alias_unset.ALLOCATIONS)',
        '$weakref_get(S_alias_unset,n_watch) = PNULL',
        '$weakref_get(S_alias_unset,n_genwatch) = PNULL',
    ] + public('S_alias_unset') + seek('S_alias_unset', 2886, 'S_recovery') + [
        'S_recovery.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_recovery.PRECISIONINI = $ptascii("6")',
    ] + public('S_recovery')
    return checks + finish('S_recovery', stdout,
                           ['HOBJECT n_generator', 'HCELL n_payloadref',
                            'HOBJECT n_payload', 'HOBJECT n_exception'])


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(SOURCES, conditions, HELPERS, model_timeout=300,
        extra_inputs=(Path(__file__),
                      Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
