#!/usr/bin/env python3
"""A fresh INSTANCE has only its copied prefix after the scalar cache replaces it."""
from pathlib import Path
from types import SimpleNamespace

import config_generator_owning_value_review_cases as cases
import list_missing_warning_protocol as shared
from array_generator_unpack_state_review import budget, finish, initial, owners, public, seek

NAME = 'config-generator-owning-prefix-replaced-cache-throw'
SOURCES = SimpleNamespace(CASES={NAME: cases.CASES[NAME]}, __file__=cases.__file__)
HELPERS = shared.HELPERS + r'''
dec $a77_peer_echo(pstate, ptbytes) : bool
def $a77_peer_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $a77_peer_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 1700) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask*
  -- if pconfiggenerator.ITEMS = eps
def $list_warning_frontier(S, 1701) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask*
  -- if |pconfiggenerator.ITEMS| = 1
def $list_warning_frontier(S, 1702) = $a77_peer_echo(S, $ptascii("F:"))
def $list_warning_frontier(S, 1703) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_GENERATOR pconfiggenerator "next") :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.OBJECTS[pconfiggenerator.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_CLOSED
def $list_warning_frontier(S, 1704) = $a77_peer_echo(S, $ptascii("E:"))
def $list_warning_frontier(S, 1705) = $a77_peer_echo(S, $ptascii("U:"))
'''


def conditions(name, program, path, stdout):
    assert name == NAME
    checks = initial(program, path) + seek('S_initial', 1700, 'S_option') + [
        'S_option.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask_option*',
        'pconfiggenerator.OBJECT = n_generator',
        'pconfiggenerator.INPUT = VARIABLE ($ptascii("gen")) z_input',
        'pconfiggenerator.PRODUCER = eps',
        'pconfiggenerator.CALL.OWNER = eps',
        '$config_generator_owning_value_source(S_option,pconfiggenerator)',
        'S_option.OBJECTS[n_generator] = GENERATOR pgenerator_option',
        'pgenerator_option.REFCELL = eps',
        'pgenerator_option.VALUE = (POBJECT n_payload)',
        '$config_generator_value(S_option,pconfiggenerator) = (POBJECT n_payload)',
        '$config_iterator_argument(S_option,POBJECT n_payload)',
        '$lookup($global_table_view(S_option).ENV,$ptascii("gen")) = (n_gen_cell)',
        'S_option.STORE[n_gen_cell] = DEFINED (POBJECT n_generator)',
        '$lookup($global_table_view(S_option).ENV,$ptascii("watch")) = (n_watch_cell)',
        'S_option.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)',
        '$weakref_get(S_option,n_watch) = POBJECT n_payload',
        '$heap_count(HOBJECT n_payload,$pools_nodes(S_option.POOLS)) = 0',
        owners('S_option', 'HOBJECT n_generator', 2),
        owners('S_option', 'HOBJECT n_payload', 2),
        'PhpStep: S_option ~> S_first_sent',
        'S_first_sent.TODO = (CONFIG_GENERATOR pconfiggenerator_first "next") :: ptask_option*',
        'pconfiggenerator_first = pconfiggenerator[.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_payload))]]',
        '$heap_count(HOBJECT n_payload,$task_nodes(CONFIG_GENERATOR pconfiggenerator_first "next")) = 1',
        '$config_generator_value(S_option,pconfiggenerator[.INPUT = KNOWN (POBJECT n_generator)]) = eps',
    ] + public('S_option') + public('S_first_sent') + seek('S_first_sent', 1701, 'S_value') + [
        'S_value.TODO = (CONFIG_GENERATOR pconfiggenerator_first "ready") :: ptask_value*',
        'S_value.OBJECTS[n_generator] = GENERATOR pgenerator_value',
        'pgenerator_value.VALUE = (PINT 7)',
        '$weakref_get(S_value,n_watch) = POBJECT n_payload',
        '~$heap_member(HOBJECT n_payload,$heap_reach([HOBJECT n_generator],eps,$heap_graph(S_value).EDGES))',
        owners('S_value', 'HOBJECT n_payload', 1),
        owners('S_value', 'HOBJECT n_generator', 2),
        'PhpStep: S_value ~> S_second_sent',
        'S_second_sent.TODO = (CONFIG_GENERATOR pconfiggenerator_second "next") :: ptask_value*',
        'pconfiggenerator_second = pconfiggenerator[.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_payload)),ENTRY (KINT 1) (DIRECT (PINT 7))]]',
    ] + public('S_value') + seek('S_second_sent', 1702, 'S_body') + [
        'S_body.FRAMES = pframe_body :: pframe_tail*',
        '$heap_count(HOBJECT n_payload,$frames_roots(S_body.FRAMES)) = 1',
        '$weakref_get(S_body,n_watch) = POBJECT n_payload',
        owners('S_body', 'HOBJECT n_payload', 1),
    ] + public('S_body') + seek('S_body', 1703, 'S_thrown') + [
        'S_thrown.TODO = (THROW_SEARCH n_exception) :: (CONFIG_GENERATOR pconfiggenerator_second "next") :: ptask_tail*',
        'S_thrown.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
        'pgenerator_closed.PHASE = GENERATOR_CLOSED',
        'pgenerator_closed.FRAME = eps',
        'pgenerator_closed.VALUE = (PINT 7)',
        '$node_children(S_thrown,HOBJECT n_generator) = eps',
        '$config_generator_history(S_thrown,pconfiggenerator_second)',
        '$config_generator_owning_items_live(S_thrown,pconfiggenerator_second.ITEMS)',
        '$lookup($global_table_view(S_thrown).ENV,$ptascii("saved")) = (n_saved_cell)',
        'S_thrown.STORE[n_saved_cell] = DEFINED (POBJECT n_exception)',
        '$lookup($global_table_view(S_thrown).ENV,$ptascii("result")) = (n_result_cell)',
        'S_thrown.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_thrown.PRECISIONINI = $ptascii("6")',
        owners('S_thrown', 'HOBJECT n_generator', 2),
        owners('S_thrown', 'HOBJECT n_payload', 1),
        'S_lost = S_thrown[.STORE[n_gen_cell] = DEFINED (PINT 17)]',
        '$config_generator_history(S_lost,pconfiggenerator_second)',
        '~$config_generator_finish_allowed(S_lost,pconfiggenerator_second)',
        'S_lost_popped = S_lost[.TODO = (THROW_SEARCH n_exception) :: ptask_tail*]',
        '~$config_generator_discard_allowed(S_lost_popped,pconfiggenerator_second)',
        '$objectprops_record_at(S_thrown.OBJECTPROPS,n_payload) = (pobjectprops_payload)',
        'pobjectprops_payload.SLOTS = [ppropertyslot_tag]',
        'S_cycle = S_thrown[.OBJECTPROPS = $objectprops_set(S_thrown.OBJECTPROPS,n_payload,[ppropertyslot_tag[.STATE = PROP_VALUE (DIRECT (POBJECT n_payload))]])]',
        '$config_generator_history(S_cycle,pconfiggenerator_second)',
        '~$config_generator_owning_items_live(S_cycle,pconfiggenerator_second.ITEMS)',
        'S_cycle_popped = S_cycle[.TODO = (THROW_SEARCH n_exception) :: ptask_tail*]',
        '~$config_generator_discard_allowed(S_cycle_popped,pconfiggenerator_second)',
        'S_popped = S_thrown[.TODO = (THROW_SEARCH n_exception) :: ptask_tail*]',
        owners('S_popped', 'HOBJECT n_generator', 1),
        owners('S_popped', 'HOBJECT n_payload', 0),
        '$config_generator_discard_allowed(S_popped,pconfiggenerator_second)',
        '~$destructor_operational(S_popped)',
        '$eager_operation_pending(S_popped) = (n_exception)',
        'S_raw = $config_generator_discard(S_popped,pconfiggenerator_second,"next")',
        'PhpStep: S_thrown ~> S_raw',
        'S_raw.TODO = (THROW_SEARCH n_exception) :: ptask_tail*',
        'S_raw.STORE = S_popped.STORE',
        'S_raw.EVENTS = S_popped.EVENTS',
        'S_raw.ALLOCATIONS = S_popped.ALLOCATIONS',
    ] + public('S_thrown') + public('S_lost') + public('S_cycle') + budget('S_thrown', 'S_abort_budget') + [
        'S_disposed = S_abort_budget_one[.COMPLETION = NORMAL]',
        '~((HOBJECT n_payload) <- S_disposed.ALLOCATIONS)',
        '(HOBJECT n_generator) <- S_disposed.ALLOCATIONS',
        '$weakref_get(S_disposed,n_watch) = PNULL',
        '$config_generator_history(S_disposed,pconfiggenerator_second)',
        '~$config_generator_owning_items_live(S_disposed,pconfiggenerator_second.ITEMS)',
        '$throwable_live(S_disposed,n_exception)',
        owners('S_disposed', 'HOBJECT n_generator', 1),
    ] + public('S_disposed') + seek('S_disposed', 1704, 'S_catch') + [
        '$lookup($global_table_view(S_catch).ENV,$ptascii("caught")) = (n_caught_cell)',
        'S_catch.STORE[n_caught_cell] = DEFINED (POBJECT n_exception)',
        'S_catch.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_catch.PRECISIONINI = $ptascii("6")',
        '$weakref_get(S_catch,n_watch) = PNULL',
        '$throwable_field(S_catch,n_exception,"previous") = PNULL',
        owners('S_catch', 'HOBJECT n_generator', 1),
    ] + public('S_catch') + seek('S_catch', 1705, 'S_unset') + [
        '~((HOBJECT n_generator) <- S_unset.ALLOCATIONS)',
        '~((HOBJECT n_payload) <- S_unset.ALLOCATIONS)',
        '$weakref_get(S_unset,n_watch) = PNULL',
    ] + public('S_unset')
    return checks + finish('S_unset', stdout, ['HOBJECT n_generator','HOBJECT n_payload','HOBJECT n_exception'])


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(SOURCES, conditions, HELPERS, model_timeout=300,
        extra_inputs=(Path(__file__),
                      Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
