#!/usr/bin/env python3
"""A retained BYREF Generator releases its first copied object but keeps its final owning cell."""
from pathlib import Path
from types import SimpleNamespace

import config_generator_reference_two_owning_cases as cases
import list_missing_warning_protocol as shared
from array_generator_unpack_state_review import budget, finish, initial, owners, public, seek

NAME = 'config-generator-reference-two-owning-distinct-terminal-throw'
SOURCES = SimpleNamespace(CASES={NAME: cases.CASES[NAME]}, __file__=cases.__file__)
HELPERS = shared.HELPERS + r'''
dec $a93_author_echo(pstate, ptbytes) : bool
def $a93_author_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $a93_author_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 9300) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask*
  -- if pconfiggenerator.ITEMS = eps
def $list_warning_frontier(S, 9301) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask*
  -- if |pconfiggenerator.ITEMS| = 1
def $list_warning_frontier(S, 9302) = $a93_author_echo(S, $ptascii("W1:"))
def $list_warning_frontier(S, 9303) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_GENERATOR pconfiggenerator "next") :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.OBJECTS[pconfiggenerator.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_CLOSED
def $list_warning_frontier(S, 9304) = $a93_author_echo(S, $ptascii("S:"))
def $list_warning_frontier(S, 9307) = $a93_author_echo(S, $ptascii("V:"))
'''


def conditions(name, program, path, stdout):
    assert name == NAME
    checks = initial(program, path) + seek('S_initial', 9300, 'S_option') + [
        'S_option.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask_option*',
        'pconfiggenerator.OBJECT = n_generator',
        'pconfiggenerator.INPUT = VARIABLE ($ptascii("gen")) z_input',
        'pconfiggenerator.PRODUCER = eps',
        'pconfiggenerator.CALL.OWNER = eps',
        '$config_generator_reference_owning_source(S_option,pconfiggenerator)',
        'S_option.OBJECTS[n_generator] = GENERATOR pgenerator_option',
        'pgenerator_option.VALUE = eps',
        'pgenerator_option.KEY = (PINT 0)',
        'pgenerator_option.REFCELL = (n_firstref)',
        '$ordinary_reference_value(S_option,n_firstref) = (POBJECT n_first)',
        '$config_generator_value(S_option,pconfiggenerator) = (POBJECT n_first)',
        '$config_iterator_argument(S_option,POBJECT n_first)',
        '$heap_count(HOBJECT n_first,$pools_nodes(S_option.POOLS)) = 0',
        '$lookup($global_table_view(S_option).ENV,$ptascii("firstWatch")) = (n_firstwatch_cell)',
        'S_option.STORE[n_firstwatch_cell] = DEFINED (POBJECT n_firstwatch)',
        '$weakref_get(S_option,n_firstwatch) = POBJECT n_first',
        '$lookup($global_table_view(S_option).ENV,$ptascii("gen")) = (n_gen_cell)',
        'S_option.STORE[n_gen_cell] = DEFINED (POBJECT n_generator)',
        '$lookup($global_table_view(S_option).ENV,$ptascii("genWatch")) = (n_genwatch_cell)',
        'S_option.STORE[n_genwatch_cell] = DEFINED (POBJECT n_genwatch)',
        '$weakref_get(S_option,n_genwatch) = POBJECT n_generator',
        owners('S_option', 'HOBJECT n_generator', 2),
        owners('S_option', 'HOBJECT n_first', 1),
        'PhpStep: S_option ~> S_first_sent',
        'S_first_sent.TODO = (CONFIG_GENERATOR pconfiggenerator_first "next") :: ptask_option*',
        'pconfiggenerator_first = pconfiggenerator[.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_first))]]',
        '$config_generator_reference_owning_first(S_first_sent,pconfiggenerator_first,POBJECT n_first)',
        '$config_generator_history(S_first_sent,pconfiggenerator_first)',
        owners('S_first_sent', 'HOBJECT n_first', 2),
    ] + public('S_option') + public('S_first_sent') + seek('S_first_sent', 9301, 'S_value') + [
        'S_value.TODO = (CONFIG_GENERATOR pconfiggenerator_first "ready") :: ptask_value*',
        'S_value.OBJECTS[n_generator] = GENERATOR pgenerator_value',
        'pgenerator_value.VALUE = eps',
        'pgenerator_value.KEY = (PINT 1)',
        'pgenerator_value.REFCELL = (n_lastref)',
        'n_lastref =/= n_firstref',
        '$ordinary_reference_value(S_value,n_firstref) = (PINT 9)',
        '$ordinary_reference_value(S_value,n_lastref) = (POBJECT n_last)',
        '$config_generator_value(S_value,pconfiggenerator_first) = (POBJECT n_last)',
        '$config_iterator_argument(S_value,POBJECT n_last)',
        '$lookup($global_table_view(S_value).ENV,$ptascii("lastWatch")) = (n_lastwatch_cell)',
        'S_value.STORE[n_lastwatch_cell] = DEFINED (POBJECT n_lastwatch)',
        '$weakref_get(S_value,n_lastwatch) = POBJECT n_last',
        '$heap_count(HOBJECT n_last,$pools_nodes(S_value.POOLS)) = 0',
        'n_first =/= n_last',
        '$weakref_get(S_value,n_firstwatch) = POBJECT n_first',
        owners('S_value', 'HOBJECT n_generator', 2),
        owners('S_value', 'HOBJECT n_first', 1),
        owners('S_value', 'HOBJECT n_last', 1),
        'PhpStep: S_value ~> S_second_sent',
        'S_second_sent.TODO = (CONFIG_GENERATOR pconfiggenerator_second "next") :: ptask_value*',
        'pconfiggenerator_second = pconfiggenerator[.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_first)),ENTRY (KINT 1) (DIRECT (POBJECT n_last))]]',
        '$config_generator_reference_two_owning_items(S_second_sent,pconfiggenerator_second)',
        '$config_generator_reference_owning_last_items(S_second_sent,pconfiggenerator_second)',
        '$config_generator_history(S_second_sent,pconfiggenerator_second)',
        owners('S_second_sent', 'HOBJECT n_first', 1),
        owners('S_second_sent', 'HOBJECT n_last', 2),
    ] + public('S_value') + public('S_second_sent') + seek('S_second_sent', 9302, 'S_body') + [
        'S_body.OBJECTS[n_generator] = GENERATOR pgenerator_body',
        'pgenerator_body.REFCELL = (n_lastref)',
        '$ordinary_reference_value(S_body,n_firstref) = (PINT 9)',
        '$ordinary_reference_value(S_body,n_lastref) = (POBJECT n_last)',
        '$weakref_get(S_body,n_lastwatch) = POBJECT n_last',
        '$weakref_get(S_body,n_firstwatch) = POBJECT n_first',
        owners('S_body', 'HOBJECT n_first', 1),
        owners('S_body', 'HOBJECT n_last', 2),
    ] + public('S_body') + seek('S_body', 9303, 'S_thrown') + [
        'S_thrown.TODO = (THROW_SEARCH n_exception) :: (CONFIG_GENERATOR pconfiggenerator_second "next") :: ptask_tail*',
        'S_thrown.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
        'pgenerator_closed.PHASE = GENERATOR_CLOSED',
        'pgenerator_closed.FRAME = eps',
        'pgenerator_closed.VALUE = eps',
        'pgenerator_closed.REFCELL = (n_lastref)',
        'pgenerator_closed.KEY = (PINT 1)',
        '$ordinary_reference_value(S_thrown,n_lastref) = (POBJECT n_last)',
        '$node_children(S_thrown,HOBJECT n_generator) = [HCELL n_lastref]',
        '$node_children(S_thrown,HCELL n_lastref) = [HOBJECT n_last]',
        '$config_generator_reference_two_owning_items(S_thrown,pconfiggenerator_second)',
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
        '$weakref_get(S_thrown,n_firstwatch) = POBJECT n_first',
        '$weakref_get(S_thrown,n_lastwatch) = POBJECT n_last',
        owners('S_thrown', 'HOBJECT n_generator', 2),
        owners('S_thrown', 'HCELL n_lastref', 1),
        owners('S_thrown', 'HOBJECT n_first', 1),
        owners('S_thrown', 'HOBJECT n_last', 2),
        'S_lost = S_thrown[.STORE[n_gen_cell] = DEFINED (PINT 17)]',
        '$config_generator_history(S_lost,pconfiggenerator_second)',
        '~$config_generator_reference_owning_live_storage(S_lost,pconfiggenerator_second)',
        '~$config_generator_finish_allowed(S_lost,pconfiggenerator_second)',
        'S_lost_popped = S_lost[.TODO = (THROW_SEARCH n_exception) :: ptask_tail*]',
        '~$config_generator_discard_allowed(S_lost_popped,pconfiggenerator_second)',
        'S_popped = S_thrown[.TODO = (THROW_SEARCH n_exception) :: ptask_tail*]',
        owners('S_popped', 'HOBJECT n_generator', 1),
        owners('S_popped', 'HOBJECT n_first', 0),
        owners('S_popped', 'HOBJECT n_last', 1),
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
        '~((HOBJECT n_first) <- S_disposed.ALLOCATIONS)',
        '(HOBJECT n_last) <- S_disposed.ALLOCATIONS',
        '(HOBJECT n_generator) <- S_disposed.ALLOCATIONS',
        '$weakref_get(S_disposed,n_firstwatch) = PNULL',
        '$weakref_get(S_disposed,n_lastwatch) = POBJECT n_last',
        '$config_generator_reference_history(S_disposed,pconfiggenerator_second)',
        '$config_generator_reference_owning_live_storage(S_disposed,pconfiggenerator_second)',
        '$throwable_live(S_disposed,n_exception)',
        owners('S_disposed', 'HOBJECT n_generator', 1),
        owners('S_disposed', 'HOBJECT n_last', 1),
    ] + public('S_disposed') + seek('S_disposed', 9304, 'S_catch') + [
        '$lookup($global_table_view(S_catch).ENV,$ptascii("caught")) = (n_caught_cell)',
        'S_catch.STORE[n_caught_cell] = DEFINED (POBJECT n_exception)',
        'S_catch.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_catch.PRECISIONINI = $ptascii("6")',
        '$weakref_get(S_catch,n_firstwatch) = PNULL',
        '$weakref_get(S_catch,n_lastwatch) = POBJECT n_last',
        '$weakref_get(S_catch,n_genwatch) = POBJECT n_generator',
        '$throwable_field(S_catch,n_exception,"previous") = PNULL',
        '~$destructor_operational(S_catch)',
        owners('S_catch', 'HOBJECT n_generator', 1),
        owners('S_catch', 'HOBJECT n_last', 1),
    ] + public('S_catch') + seek('S_catch', 9307, 'S_unset') + [
        '~((HOBJECT n_generator) <- S_unset.ALLOCATIONS)',
        '~((HCELL n_lastref) <- S_unset.ALLOCATIONS)',
        '~((HOBJECT n_first) <- S_unset.ALLOCATIONS)',
        '~((HOBJECT n_last) <- S_unset.ALLOCATIONS)',
        '$weakref_get(S_unset,n_genwatch) = PNULL',
        '$weakref_get(S_unset,n_firstwatch) = PNULL',
        '$weakref_get(S_unset,n_lastwatch) = PNULL',
    ] + public('S_unset')
    return checks + finish('S_unset', stdout,
                           ['HOBJECT n_generator', 'HCELL n_firstref', 'HCELL n_lastref',
                            'HOBJECT n_first', 'HOBJECT n_last', 'HOBJECT n_exception'])


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(SOURCES, conditions, HELPERS, model_timeout=300,
        extra_inputs=(Path(__file__),
                      Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
