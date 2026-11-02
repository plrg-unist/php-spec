#!/usr/bin/env python3
"""A temporary Gen's two discard stages retain then release its copied array."""
from pathlib import Path
from types import SimpleNamespace

import config_generator_owning_temporary_review_cases as cases
import list_missing_warning_protocol as shared
from array_generator_unpack_state_review import budget, finish, initial, owners, public, seek

NAME = 'config-generator-owning-temporary-array-cow-terminal-throw'
SOURCES = SimpleNamespace(CASES={NAME: cases.CASES[NAME]}, __file__=cases.__file__)
HELPERS = shared.HELPERS + r'''
dec $a78_peer_echo(pstate, ptbytes) : bool
def $a78_peer_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $a78_peer_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 1900) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask*
  -- if pconfiggenerator.ITEMS = eps
def $list_warning_frontier(S, 1901) = $a78_peer_echo(S, $ptascii("M:"))
def $list_warning_frontier(S, 1902) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask*
  -- if |pconfiggenerator.ITEMS| = 1
def $list_warning_frontier(S, 1903) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_GENERATOR pconfiggenerator "next") :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.OBJECTS[pconfiggenerator.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_CLOSED
def $list_warning_frontier(S, 1904) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_GENERATOR pconfiggenerator "input-release") :: ptask*
def $list_warning_frontier(S, 1905) = $a78_peer_echo(S, $ptascii("S:"))
def $list_warning_frontier(S, 1906) = $a78_peer_echo(S, $ptascii("R:"))
'''


def cell(state, name, identifier):
    return f'$lookup($global_table_view({state}).ENV,$ptascii("{name}")) = ({identifier})'


def conditions(name, program, path, stdout):
    assert name == NAME
    checks = initial(program, path) + seek('S_initial', 1900, 'S_option') + [
        'S_option.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask_option*',
        'pconfiggenerator.OBJECT = n_generator',
        'pconfiggenerator.INPUT = KNOWN (POBJECT n_generator)',
        'pconfiggenerator.PRODUCER = eps',
        'pconfiggenerator.CALL.OWNER = eps',
        '$config_generator_factory_owning_input(S_option,pconfiggenerator)',
        'S_option.OBJECTS[n_generator] = GENERATOR pgenerator_option',
        'pgenerator_option.VALUE = (PARRAY n_option)',
        'pgenerator_option.KEY = (PINT 0)',
        'pgenerator_option.REFCELL = eps',
        'S_option.ARRAYS[n_option].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 13))]',
        '$config_generator_value(S_option,pconfiggenerator) = (PARRAY n_option)',
        '$heap_count(HARRAY n_option,$pools_nodes(S_option.POOLS)) = 0',
        cell('S_option','genWatch','n_genwatch_cell'),
        'S_option.STORE[n_genwatch_cell] = DEFINED (POBJECT n_genwatch)',
        '$weakref_get(S_option,n_genwatch) = POBJECT n_generator',
        owners('S_option','HOBJECT n_generator',2),
        owners('S_option','HARRAY n_option',2),
        'PhpStep: S_option ~> S_first_sent',
        'S_first_sent.TODO = (CONFIG_GENERATOR pconfiggenerator_first "next") :: ptask_option*',
        'pconfiggenerator_first = pconfiggenerator[.ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_option))]]',
        '$config_generator_argument_nodes(pconfiggenerator_first) = [HARRAY n_option]',
    ] + public('S_option') + public('S_first_sent') + seek('S_first_sent',1901,'S_mutated') + [
        '$lookup(S_mutated.ENV,$ptascii("row")) = (n_live_cell)',
        'S_mutated.STORE[n_live_cell] = DEFINED (PARRAY n_live)',
        'n_live =/= n_option',
        'S_mutated.ARRAYS[n_live].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 31))]',
        'S_mutated.ARRAYS[n_option].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 13))]',
        'S_mutated.OBJECTS[n_generator] = GENERATOR pgenerator_mutated',
        'pgenerator_mutated.VALUE = (PARRAY n_option)',
        '$heap_count(HARRAY n_option,$frames_roots(S_mutated.FRAMES)) = 1',
        owners('S_mutated','HARRAY n_option',2),
    ] + public('S_mutated') + seek('S_mutated',1902,'S_value') + [
        'S_value.TODO = (CONFIG_GENERATOR pconfiggenerator_first "ready") :: ptask_value*',
        'S_value.OBJECTS[n_generator] = GENERATOR pgenerator_value',
        'pgenerator_value.VALUE = (PINT 7)',
        'pgenerator_value.KEY = (PINT 1)',
        '~$heap_member(HARRAY n_option,$heap_reach([HOBJECT n_generator],eps,$heap_graph(S_value).EDGES))',
        '$heap_count(HARRAY n_option,$pools_nodes(S_value.POOLS)) = 0',
        owners('S_value','HARRAY n_option',1),
        owners('S_value','HOBJECT n_generator',2),
        'PhpStep: S_value ~> S_second_sent',
        'S_second_sent.TODO = (CONFIG_GENERATOR pconfiggenerator_second "next") :: ptask_value*',
        'pconfiggenerator_second = pconfiggenerator[.ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_option)),ENTRY (KINT 1) (DIRECT (PINT 7))]]',
    ] + public('S_value') + seek('S_second_sent',1903,'S_thrown') + [
        'S_thrown.TODO = (THROW_SEARCH n_exception) :: (CONFIG_GENERATOR pconfiggenerator_second "next") :: ptask_tail*',
        'S_thrown.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
        'pgenerator_closed.PHASE = GENERATOR_CLOSED',
        'pgenerator_closed.FRAME = eps',
        'pgenerator_closed.VALUE = (PINT 7)',
        'pgenerator_closed.KEY = (PINT 1)',
        '$node_children(S_thrown,HOBJECT n_generator) = eps',
        '$config_generator_factory_owning_cleanup(S_thrown,pconfiggenerator_second)',
        '$config_generator_owning_items_live(S_thrown,pconfiggenerator_second.ITEMS)',
        '~((HARRAY n_live) <- S_thrown.ALLOCATIONS)',
        cell('S_thrown','saved','n_saved_cell'),
        'S_thrown.STORE[n_saved_cell] = DEFINED (POBJECT n_exception)',
        cell('S_thrown','result','n_result_cell'),
        'S_thrown.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_thrown.PRECISIONINI = $ptascii("6")',
        owners('S_thrown','HOBJECT n_generator',2),
        owners('S_thrown','HARRAY n_option',1),
        'S_first_popped = S_thrown[.TODO = (THROW_SEARCH n_exception) :: ptask_tail*]',
        owners('S_first_popped','HOBJECT n_generator',0),
        owners('S_first_popped','HARRAY n_option',0),
        '$config_generator_factory_owning_cleanup(S_first_popped,pconfiggenerator_second)',
        '$config_generator_discard_allowed(S_first_popped,pconfiggenerator_second)',
        '~$destructor_operational(S_first_popped)',
        '$eager_operation_pending(S_first_popped) = (n_exception)',
        'S_first_raw = $config_generator_discard(S_first_popped,pconfiggenerator_second,"next")',
        'S_first_raw = $config_generator_discard_state(S_first_popped,pconfiggenerator_second,"next")',
        'S_first_raw.TODO = (THROW_SEARCH n_exception) :: (CONFIG_GENERATOR pconfiggenerator_second "input-release") :: ptask_tail*',
        'PhpStep: S_thrown ~> S_first_raw',
        owners('S_first_raw','HOBJECT n_generator',1),
        owners('S_first_raw','HARRAY n_option',1),
    ] + public('S_thrown') + public('S_first_raw') + seek('S_thrown',1904,'S_input') + [
        'S_input.TODO = (THROW_SEARCH n_exception) :: (CONFIG_GENERATOR pconfiggenerator_second "input-release") :: ptask_input*',
        '$config_generator_valid(S_input,pconfiggenerator_second,"input-release")',
        '$weakref_get(S_input,n_genwatch) = POBJECT n_generator',
        'S_input.ARRAYS[n_option].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 13))]',
        owners('S_input','HOBJECT n_generator',1),
        owners('S_input','HARRAY n_option',1),
        'S_second_popped = S_input[.TODO = (THROW_SEARCH n_exception) :: ptask_input*]',
        owners('S_second_popped','HOBJECT n_generator',0),
        owners('S_second_popped','HARRAY n_option',0),
        '$config_generator_factory_owning_cleanup(S_second_popped,pconfiggenerator_second)',
        '$config_generator_discard_allowed(S_second_popped,pconfiggenerator_second)',
        'S_second_raw = $config_generator_discard(S_second_popped,pconfiggenerator_second,"input-release")',
        'S_second_raw.TODO = (THROW_SEARCH n_exception) :: ptask_input*',
        'S_second_raw.STORE = S_second_popped.STORE',
        'S_second_raw.EVENTS = S_second_popped.EVENTS',
        'S_second_raw.ALLOCATIONS = S_second_popped.ALLOCATIONS',
        'PhpStep: S_input ~> S_second_raw',
    ] + public('S_input') + budget('S_input','S_release_budget') + [
        'S_disposed = S_release_budget_one[.COMPLETION = NORMAL]',
        '~((HOBJECT n_generator) <- S_disposed.ALLOCATIONS)',
        '~((HARRAY n_option) <- S_disposed.ALLOCATIONS)',
        '$weakref_get(S_disposed,n_genwatch) = PNULL',
        '$config_generator_history(S_disposed,pconfiggenerator_second)',
        '$config_generator_factory_owning_cleanup(S_disposed,pconfiggenerator_second)',
        '~$config_generator_owning_items_live(S_disposed,pconfiggenerator_second.ITEMS)',
        '$throwable_live(S_disposed,n_exception)',
    ] + public('S_disposed') + seek('S_disposed',1905,'S_catch') + [
        cell('S_catch','caught','n_caught_cell'),
        'S_catch.STORE[n_caught_cell] = DEFINED (POBJECT n_exception)',
        'S_catch.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_catch.PRECISIONINI = $ptascii("6")',
        '$weakref_get(S_catch,n_genwatch) = PNULL',
        '$throwable_field(S_catch,n_exception,"previous") = PNULL',
    ] + public('S_catch') + seek('S_catch',1906,'S_recovery') + [
        'S_recovery.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_recovery.PRECISIONINI = $ptascii("6")',
    ] + public('S_recovery')
    return checks + finish('S_recovery',stdout,['HOBJECT n_generator','HARRAY n_option','HOBJECT n_exception'])


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(SOURCES,conditions,HELPERS,model_timeout=300,
        extra_inputs=(Path(__file__),Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
