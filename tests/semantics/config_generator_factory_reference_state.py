#!/usr/bin/env python3
"""A BYVAL factory result drops DATA then INPUT before a saved catch."""
from pathlib import Path
from types import SimpleNamespace

import config_generator_factory_reference_cases as cases
import list_missing_warning_protocol as shared
from array_generator_unpack_state_review import budget, finish, initial, owners, public, seek


NAME = 'config-generator-factory-reference-terminal-throw'
SOURCES = SimpleNamespace(CASES={NAME: cases.CASES[NAME]}, __file__=cases.__file__)
HELPERS = shared.HELPERS + r'''
dec $a76_echo(pstate, ptbytes) : bool
def $a76_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $a76_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 1510) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_GENERATOR pconfiggenerator "next") :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.OBJECTS[pconfiggenerator.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_CLOSED
def $list_warning_frontier(S, 1511) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_GENERATOR pconfiggenerator "input-release") :: ptask*
def $list_warning_frontier(S, 1513) = $a76_echo(S, $ptascii("C:"))
def $list_warning_frontier(S, 1514) = $a76_echo(S, $ptascii("R:"))
'''


def cell(state, name, identifier):
    return f'$lookup($global_table_view({state}).ENV, $ptascii("{name}")) = ({identifier})'


def conditions(name, program, path, stdout):
    assert name == NAME
    checks = initial(program, path) + seek('S_initial', 1510, 'S_thrown') + [
        'S_thrown.TODO = (THROW_SEARCH n_exception) :: (CONFIG_GENERATOR pconfiggenerator "next") :: ptask_tail*',
        'pconfiggenerator.OBJECT = n_generator',
        'pconfiggenerator.INPUT = KNOWN (POBJECT n_generator)',
        'pconfiggenerator.PRODUCER = eps',
        '$config_generator_owning_input(pconfiggenerator)',
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
        '$config_generator_factory_reference_input(S_thrown,pconfiggenerator)',
        '$intrinsic_argument(S_thrown,pconfiggenerator.CALL.SITE,0) = ((expression,true,eps,PORIGIN n_source pcpath,z))',
        '$source_emission_noarg_call(S_thrown,n_source,pcpath,expression) = (z_call)',
        '$code_at(S_thrown.CODE,n_source) = (pcode)',
        '$code_name(pcode.NAMES,pcpath) = ((ptbytes_name,eps))',
        '$call_target(S_thrown,ptbytes_name,eps) = (pfunction_factory)',
        'pfunction_factory.SIGNATURE.PARAMETERS = eps',
        '~pfunction_factory.SIGNATURE.BYREF',
        '~$function_generator(S_thrown,pfunction_factory)',
        '$function_at($all_functions(S_thrown),pgenerator_closed.FUNCTION) = (pfunction_generator)',
        'pfunction_generator.SIGNATURE.BYREF',
        '$function_generator(S_thrown,pfunction_generator)',
        'pfunction_factory =/= pfunction_generator',
        '~$config_generator_temporary_reference_input(S_thrown,pconfiggenerator)',
        '$config_generator_reference_history(S_thrown,pconfiggenerator)',
        '$config_generator_reference_storage(S_thrown,pconfiggenerator)',
        '$config_generator_valid(S_thrown,pconfiggenerator,"next")',
        cell('S_thrown', 'saved', 'n_saved_cell'),
        'S_thrown.STORE[n_saved_cell] = DEFINED (POBJECT n_exception)',
        '$throwable_live(S_thrown,n_exception)',
        '$throwable_field(S_thrown,n_exception,"previous") = PNULL',
        cell('S_thrown', 'result', 'n_result_cell'),
        'S_thrown.STORE[n_result_cell] = DEFINED (PINT 99)',
        cell('S_thrown', 'watch', 'n_watch_cell'),
        'S_thrown.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)',
        '$weakref_get(S_thrown,n_watch) = POBJECT n_generator',
        'S_thrown.PRECISIONINI = $ptascii("6")',
        owners('S_thrown', 'HOBJECT n_generator', 2),
        owners('S_thrown', 'HCELL n_value_cell', 1),
        'S_popped = S_thrown[.TODO = (THROW_SEARCH n_exception) :: ptask_tail*]',
        owners('S_popped', 'HOBJECT n_generator', 0),
        '$config_generator_discard_allowed(S_popped,pconfiggenerator)',
        '~$destructor_operational(S_popped)',
        '$eager_operation_pending(S_popped) = (n_exception)',
        'S_reintroduced = $config_generator_discard_state(S_popped,pconfiggenerator,"next")',
        'S_reintroduced.TODO = (THROW_SEARCH n_exception) :: (CONFIG_GENERATOR pconfiggenerator "input-release") :: ptask_tail*',
        'S_first_raw = $config_generator_discard(S_popped,pconfiggenerator,"next")',
        'S_first_raw = S_reintroduced',
        'PhpStep: S_thrown ~> S_first_raw',
    ] + public('S_thrown') + seek('S_thrown', 1511, 'S_input') + [
        'S_input.TODO = (THROW_SEARCH n_exception) :: (CONFIG_GENERATOR pconfiggenerator "input-release") :: ptask_input*',
        '$config_generator_valid(S_input,pconfiggenerator,"input-release")',
        '$ordinary_reference_value(S_input,n_value_cell) = (PINT 8)',
        '$weakref_get(S_input,n_watch) = POBJECT n_generator',
        owners('S_input', 'HOBJECT n_generator', 1),
        owners('S_input', 'HCELL n_value_cell', 1),
        'S_second_popped = S_input[.TODO = (THROW_SEARCH n_exception) :: ptask_input*]',
        owners('S_second_popped', 'HOBJECT n_generator', 0),
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
        '~((HCELL n_value_cell) <- S_disposed.ALLOCATIONS)',
        '$config_generator_retired_scope(S_disposed,pconfiggenerator)',
        '$weakref_get(S_disposed,n_watch) = PNULL',
        'S_disposed.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_disposed.PRECISIONINI = $ptascii("6")',
        '$throwable_live(S_disposed,n_exception)',
    ] + public('S_disposed') + seek('S_disposed', 1513, 'S_catch') + [
        '~((HOBJECT n_generator) <- S_catch.ALLOCATIONS)',
        '~((HCELL n_value_cell) <- S_catch.ALLOCATIONS)',
        '$ordinary_reference_value(S_catch,n_value_cell) = eps',
        '$weakref_get(S_catch,n_watch) = PNULL',
        cell('S_catch', 'caught', 'n_caught_cell'),
        'S_catch.STORE[n_caught_cell] = DEFINED (POBJECT n_exception)',
        'S_catch.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_catch.PRECISIONINI = $ptascii("6")',
        '$throwable_live(S_catch,n_exception)',
        '$throwable_field(S_catch,n_exception,"previous") = PNULL',
    ] + public('S_catch') + seek('S_catch', 1514, 'S_recovery') + [
        'S_recovery.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_recovery.PRECISIONINI = $ptascii("6")',
        '$weakref_get(S_recovery,n_watch) = PNULL',
    ] + public('S_recovery')
    return checks + finish('S_recovery', stdout, ['HOBJECT n_generator', 'HCELL n_value_cell'])


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(SOURCES, conditions, HELPERS, model_timeout=300,
        extra_inputs=(Path(__file__),
                      Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
