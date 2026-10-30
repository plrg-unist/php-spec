#!/usr/bin/env python3
"""An outside alias keeps an owning BYREF cell after Generator retirement."""
from pathlib import Path
from types import SimpleNamespace

import config_generator_reference_owning_alias_cases as cases
import list_missing_warning_protocol as shared
from array_generator_unpack_state_review import budget, finish, initial, owners, public, seek

NAME = 'config-generator-reference-owning-alias-object-terminal-throw'
SOURCES = SimpleNamespace(CASES={NAME: cases.CASES[NAME]}, __file__=cases.__file__)
HELPERS = shared.HELPERS + r'''
dec $a84_author_echo(pstate, ptbytes) : bool
def $a84_author_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $a84_author_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 2800) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask*
  -- if pconfiggenerator.ITEMS = eps
def $list_warning_frontier(S, 2801) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask*
  -- if |pconfiggenerator.ITEMS| = 1
def $list_warning_frontier(S, 2802) = $a84_author_echo(S, $ptascii("W:"))
def $list_warning_frontier(S, 2803) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_GENERATOR pconfiggenerator "next") :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.OBJECTS[pconfiggenerator.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_CLOSED
def $list_warning_frontier(S, 2804) = $a84_author_echo(S, $ptascii("S:"))
def $list_warning_frontier(S, 2805) = $a84_author_echo(S, $ptascii("G:"))
def $list_warning_frontier(S, 2806) = $a84_author_echo(S, $ptascii("A:"))
def $list_warning_frontier(S, 2807) = $a84_author_echo(S, $ptascii("U:"))
def $list_warning_frontier(S, 2808) = $a84_author_echo(S, $ptascii("R:"))
'''


def cell(state, name, identifier):
    return f'$lookup($global_table_view({state}).ENV,$ptascii("{name}")) = ({identifier})'


def conditions(name, program, path, stdout):
    assert name == NAME
    checks = initial(program, path) + seek('S_initial', 2800, 'S_option') + [
        'S_option.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask_option*',
        'pconfiggenerator.OBJECT = n_generator',
        'pconfiggenerator.INPUT = VARIABLE ($ptascii("gen")) z_input',
        'pconfiggenerator.PRODUCER = eps',
        'pconfiggenerator.CALL.OWNER = eps',
        '$config_generator_reference_owning_source(S_option,pconfiggenerator)',
        'S_option.OBJECTS[n_generator] = GENERATOR pgenerator_option',
        'pgenerator_option.VALUE = eps',
        'pgenerator_option.KEY = (PINT 0)',
        'pgenerator_option.REFCELL = (n_optionref)',
        '$ordinary_reference_value(S_option,n_optionref) = (pvalue_option)',
        '$string_bytes(pvalue_option) = ($ptascii("precision"))',
        '$config_generator_value(S_option,pconfiggenerator) = (pvalue_option)',
        '$lookup($global_table_view(S_option).ENV,$ptascii("gen")) = (n_gen_cell)',
        'S_option.STORE[n_gen_cell] = DEFINED (POBJECT n_generator)',
        '$lookup($global_table_view(S_option).ENV,$ptascii("genWatch")) = (n_genwatch_cell)',
        'S_option.STORE[n_genwatch_cell] = DEFINED (POBJECT n_genwatch)',
        '$weakref_get(S_option,n_genwatch) = POBJECT n_generator',
        cell('S_option', 'slot', 'n_payloadref'),
        cell('S_option', 'alias', 'n_payloadref'),
        owners('S_option', 'HOBJECT n_generator', 2),
        'PhpStep: S_option ~> S_first_sent',
        'S_first_sent.TODO = (CONFIG_GENERATOR pconfiggenerator_first "next") :: ptask_option*',
        'pconfiggenerator_first = pconfiggenerator[.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_option)]]',
        '$config_generator_history(S_first_sent,pconfiggenerator_first)',
    ] + public('S_option') + public('S_first_sent') + seek('S_first_sent', 2801, 'S_value') + [
        'S_value.TODO = (CONFIG_GENERATOR pconfiggenerator_first "ready") :: ptask_value*',
        'S_value.OBJECTS[n_generator] = GENERATOR pgenerator_value',
        'pgenerator_value.VALUE = eps',
        'pgenerator_value.KEY = (PINT 1)',
        'pgenerator_value.REFCELL = (n_payloadref)',
        'n_payloadref =/= n_optionref',
        cell('S_value', 'slot', 'n_payloadref'),
        cell('S_value', 'alias', 'n_payloadref'),
        '$ordinary_reference_value(S_value,n_payloadref) = (POBJECT n_payload)',
        '$config_generator_value(S_value,pconfiggenerator_first) = (POBJECT n_payload)',
        '$config_iterator_argument(S_value,POBJECT n_payload)',
        '$lookup($global_table_view(S_value).ENV,$ptascii("payloadWatch")) = (n_payloadwatch_cell)',
        'S_value.STORE[n_payloadwatch_cell] = DEFINED (POBJECT n_payloadwatch)',
        '$weakref_get(S_value,n_payloadwatch) = POBJECT n_payload',
        '$heap_count(HOBJECT n_payload,$pools_nodes(S_value.POOLS)) = 0',
        owners('S_value', 'HOBJECT n_generator', 2),
        owners('S_value', 'HCELL n_payloadref', 3),
        owners('S_value', 'HOBJECT n_payload', 1),
        'PhpStep: S_value ~> S_second_sent',
        'S_second_sent.TODO = (CONFIG_GENERATOR pconfiggenerator_second "next") :: ptask_value*',
        'pconfiggenerator_second = pconfiggenerator[.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_option),ENTRY (KINT 1) (DIRECT (POBJECT n_payload))]]',
        '$config_generator_reference_owning_last_items(S_second_sent,pconfiggenerator_second)',
        '$config_generator_history(S_second_sent,pconfiggenerator_second)',
        owners('S_second_sent', 'HOBJECT n_payload', 2),
    ] + public('S_value') + public('S_second_sent') + seek('S_second_sent', 2802, 'S_body') + [
        'S_body.OBJECTS[n_generator] = GENERATOR pgenerator_body',
        'pgenerator_body.REFCELL = (n_payloadref)',
        '$ordinary_reference_value(S_body,n_payloadref) = (POBJECT n_payload)',
        '$weakref_get(S_body,n_payloadwatch) = POBJECT n_payload',
        owners('S_body', 'HOBJECT n_payload', 2),
    ] + public('S_body') + seek('S_body', 2803, 'S_thrown') + [
        'S_thrown.TODO = (THROW_SEARCH n_exception) :: (CONFIG_GENERATOR pconfiggenerator_second "next") :: ptask_tail*',
        'S_thrown.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
        'pgenerator_closed.PHASE = GENERATOR_CLOSED',
        'pgenerator_closed.FRAME = eps',
        'pgenerator_closed.VALUE = eps',
        'pgenerator_closed.REFCELL = (n_payloadref)',
        'pgenerator_closed.KEY = (PINT 1)',
        cell('S_thrown', 'slot', 'n_payloadref'),
        cell('S_thrown', 'alias', 'n_payloadref'),
        '$ordinary_reference_value(S_thrown,n_payloadref) = (POBJECT n_payload)',
        '$node_children(S_thrown,HOBJECT n_generator) = [HCELL n_payloadref]',
        '$node_children(S_thrown,HCELL n_payloadref) = [HOBJECT n_payload]',
        '$config_generator_reference_history(S_thrown,pconfiggenerator_second)',
        '$config_generator_reference_owning_last_items(S_thrown,pconfiggenerator_second)',
        '~$config_generator_reference_storage(S_thrown,pconfiggenerator_second)',
        '$config_generator_reference_owning_live_storage(S_thrown,pconfiggenerator_second)',
        '$config_generator_finish_allowed(S_thrown,pconfiggenerator_second)',
        '$lookup($global_table_view(S_thrown).ENV,$ptascii("saved")) = (n_saved_cell)',
        'S_thrown.STORE[n_saved_cell] = DEFINED (POBJECT n_exception)',
        '$lookup($global_table_view(S_thrown).ENV,$ptascii("result")) = (n_result_cell)',
        'S_thrown.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_thrown.PRECISIONINI = $ptascii("6")',
        '$weakref_get(S_thrown,n_genwatch) = POBJECT n_generator',
        '$weakref_get(S_thrown,n_payloadwatch) = POBJECT n_payload',
        owners('S_thrown', 'HOBJECT n_generator', 2),
        owners('S_thrown', 'HCELL n_payloadref', 3),
        owners('S_thrown', 'HOBJECT n_payload', 2),
        'S_lost = S_thrown[.STORE[n_gen_cell] = DEFINED (PINT 17)]',
        '$config_generator_history(S_lost,pconfiggenerator_second)',
        '~$config_generator_reference_owning_live_storage(S_lost,pconfiggenerator_second)',
        '~$config_generator_finish_allowed(S_lost,pconfiggenerator_second)',
        'S_lost_popped = S_lost[.TODO = (THROW_SEARCH n_exception) :: ptask_tail*]',
        '~$config_generator_discard_allowed(S_lost_popped,pconfiggenerator_second)',
        'S_popped = S_thrown[.TODO = (THROW_SEARCH n_exception) :: ptask_tail*]',
        owners('S_popped', 'HOBJECT n_generator', 1),
        owners('S_popped', 'HCELL n_payloadref', 3),
        owners('S_popped', 'HOBJECT n_payload', 1),
        '$config_generator_reference_owning_live_storage(S_popped,pconfiggenerator_second)',
        '$config_generator_discard_allowed(S_popped,pconfiggenerator_second)',
        '~$destructor_operational(S_popped)',
        '$eager_operation_pending(S_popped) = (n_exception)',
        'S_raw = $config_generator_discard(S_popped,pconfiggenerator_second,"next")',
        'PhpStep: S_thrown ~> S_raw',
        'S_raw.TODO = (THROW_SEARCH n_exception) :: ptask_tail*',
        'S_raw.STORE = S_popped.STORE',
        'S_raw.EVENTS = S_popped.EVENTS',
        'S_raw.ALLOCATIONS = S_popped.ALLOCATIONS',
    ] + public('S_thrown') + budget('S_thrown', 'S_abort_budget') + [
        'S_disposed = S_abort_budget_one[.COMPLETION = NORMAL]',
        '(HOBJECT n_payload) <- S_disposed.ALLOCATIONS',
        '(HOBJECT n_generator) <- S_disposed.ALLOCATIONS',
        '$weakref_get(S_disposed,n_payloadwatch) = POBJECT n_payload',
        '$config_generator_reference_history(S_disposed,pconfiggenerator_second)',
        '$config_generator_reference_owning_live_storage(S_disposed,pconfiggenerator_second)',
        '$throwable_live(S_disposed,n_exception)',
        owners('S_disposed', 'HOBJECT n_generator', 1),
        owners('S_disposed', 'HCELL n_payloadref', 3),
        owners('S_disposed', 'HOBJECT n_payload', 1),
    ] + public('S_disposed') + seek('S_disposed', 2804, 'S_catch') + [
        '$lookup($global_table_view(S_catch).ENV,$ptascii("caught")) = (n_caught_cell)',
        'S_catch.STORE[n_caught_cell] = DEFINED (POBJECT n_exception)',
        'S_catch.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_catch.PRECISIONINI = $ptascii("6")',
        '$weakref_get(S_catch,n_payloadwatch) = POBJECT n_payload',
        '$weakref_get(S_catch,n_genwatch) = POBJECT n_generator',
        '$throwable_field(S_catch,n_exception,"previous") = PNULL',
        '~$destructor_operational(S_catch)',
        owners('S_catch', 'HOBJECT n_generator', 1),
        owners('S_catch', 'HCELL n_payloadref', 3),
        owners('S_catch', 'HOBJECT n_payload', 1),
    ] + public('S_catch') + seek('S_catch', 2805, 'S_gen_unset') + [
        '~((HOBJECT n_generator) <- S_gen_unset.ALLOCATIONS)',
        '(HCELL n_payloadref) <- S_gen_unset.ALLOCATIONS',
        '(HOBJECT n_payload) <- S_gen_unset.ALLOCATIONS',
        cell('S_gen_unset', 'slot', 'n_payloadref'),
        cell('S_gen_unset', 'alias', 'n_payloadref'),
        '$ordinary_reference_value(S_gen_unset,n_payloadref) = (POBJECT n_payload)',
        '$weakref_get(S_gen_unset,n_genwatch) = PNULL',
        '$weakref_get(S_gen_unset,n_payloadwatch) = POBJECT n_payload',
        owners('S_gen_unset', 'HCELL n_payloadref', 2),
        owners('S_gen_unset', 'HOBJECT n_payload', 1),
    ] + public('S_gen_unset') + seek('S_gen_unset', 2806, 'S_alias') + [
        cell('S_alias', 'slot', 'n_payloadref'),
        cell('S_alias', 'alias', 'n_payloadref'),
        '$ordinary_reference_value(S_alias,n_payloadref) = (POBJECT n_payload)',
        '$weakref_get(S_alias,n_payloadwatch) = POBJECT n_payload',
        owners('S_alias', 'HCELL n_payloadref', 2),
        owners('S_alias', 'HOBJECT n_payload', 1),
    ] + public('S_alias') + seek('S_alias', 2807, 'S_unset') + [
        '~((HOBJECT n_generator) <- S_unset.ALLOCATIONS)',
        '~((HCELL n_payloadref) <- S_unset.ALLOCATIONS)',
        '~((HOBJECT n_payload) <- S_unset.ALLOCATIONS)',
        '$weakref_get(S_unset,n_genwatch) = PNULL',
        '$weakref_get(S_unset,n_payloadwatch) = PNULL',
    ] + public('S_unset') + seek('S_unset', 2808, 'S_recovery') + [
        'S_recovery.PRECISIONINI = $ptascii("6")',
    ] + public('S_recovery')
    return checks + finish('S_recovery', stdout,
                           ['HOBJECT n_generator', 'HCELL n_payloadref',
                            'HOBJECT n_payload', 'HOBJECT n_exception'])


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(SOURCES, conditions, HELPERS, model_timeout=300,
        extra_inputs=(Path(__file__),
                      Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
