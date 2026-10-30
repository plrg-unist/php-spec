#!/usr/bin/env python3
"""A temporary final object cache and copied prefix retire before a saved catch."""
from pathlib import Path
from types import SimpleNamespace

import config_generator_owning_cache_cases as cases
import list_missing_warning_protocol as shared
from array_generator_unpack_state_review import finish, initial, owners, public, seek


NAME = 'config-generator-owning-cache-object-terminal-throw'
SOURCES = SimpleNamespace(CASES={NAME: cases.CASES[NAME]}, __file__=cases.__file__)
HELPERS = shared.HELPERS + r'''
dec $a79_echo(pstate, ptbytes) : bool
def $a79_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $a79_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 2100) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask*
  -- if pconfiggenerator.ITEMS = eps
def $list_warning_frontier(S, 2101) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask*
  -- if |pconfiggenerator.ITEMS| = 1
def $list_warning_frontier(S, 2102) = $a79_echo(S, $ptascii("T;"))
def $list_warning_frontier(S, 2103) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_GENERATOR pconfiggenerator "next") :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.OBJECTS[pconfiggenerator.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_CLOSED
def $list_warning_frontier(S, 2104) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_GENERATOR pconfiggenerator "input-release") :: ptask*
def $list_warning_frontier(S, 2105) = $a79_echo(S, $ptascii("S:"))
def $list_warning_frontier(S, 2106) = $a79_echo(S, $ptascii("R:"))
'''


def cell(state, name, identifier):
    return f'$lookup($global_table_view({state}).ENV,$ptascii("{name}")) = ({identifier})'


def conditions(name, program, path, stdout):
    assert name == NAME
    checks = initial(program, path) + seek('S_initial', 2100, 'S_option') + [
        'S_option.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask_option*',
        'pconfiggenerator.OBJECT = n_generator',
        'pconfiggenerator.INPUT = KNOWN (POBJECT n_generator)',
        'pconfiggenerator.PRODUCER = eps',
        'pconfiggenerator.CALL.OWNER = eps',
        '$config_generator_factory_owning_input(S_option,pconfiggenerator)',
        'S_option.OBJECTS[n_generator] = GENERATOR pgenerator_option',
        'pgenerator_option.VALUE = (pvalue_option)',
        'pgenerator_option.KEY = (PINT 0)',
        'pgenerator_option.REFCELL = eps',
        '$config_iterator_scalar(S_option,pvalue_option)',
        '$value_nodes(pvalue_option) = eps',
        '$config_generator_value(S_option,pconfiggenerator) = (pvalue_option)',
        cell('S_option','genWatch','n_genwatch_cell'),
        'S_option.STORE[n_genwatch_cell] = DEFINED (POBJECT n_genwatch)',
        cell('S_option','payloadWatch','n_payloadwatch_cell'),
        'S_option.STORE[n_payloadwatch_cell] = DEFINED (PNULL)',
        '$weakref_get(S_option,n_genwatch) = POBJECT n_generator',
        owners('S_option','HOBJECT n_generator',2),
        'PhpStep: S_option ~> S_first_sent',
        'S_first_sent.TODO = (CONFIG_GENERATOR pconfiggenerator_first "next") :: ptask_option*',
        'pconfiggenerator_first = pconfiggenerator[.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_option)]]',
    ] + public('S_option') + public('S_first_sent') + seek('S_first_sent',2101,'S_value') + [
        'S_value.TODO = (CONFIG_GENERATOR pconfiggenerator_first "ready") :: ptask_value*',
        'S_value.OBJECTS[n_generator] = GENERATOR pgenerator_value',
        'pgenerator_value.VALUE = (POBJECT n_payload)',
        'pgenerator_value.KEY = (PINT 1)',
        '$config_generator_value(S_value,pconfiggenerator_first) = (POBJECT n_payload)',
        '$config_iterator_argument(S_value,POBJECT n_payload)',
        'S_value.STORE[n_payloadwatch_cell] = DEFINED (POBJECT n_payloadwatch)',
        '$weakref_get(S_value,n_payloadwatch) = POBJECT n_payload',
        '$heap_count(HOBJECT n_payload,$pools_nodes(S_value.POOLS)) = 0',
        owners('S_value','HOBJECT n_generator',2),
        owners('S_value','HOBJECT n_payload',2),
        'PhpStep: S_value ~> S_second_sent',
        'S_second_sent.TODO = (CONFIG_GENERATOR pconfiggenerator_second "next") :: ptask_value*',
        'pconfiggenerator_second = pconfiggenerator[.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_option),ENTRY (KINT 1) (DIRECT (POBJECT n_payload))]]',
        '$config_generator_argument_nodes(pconfiggenerator_second) = [HOBJECT n_payload]',
    ] + public('S_value') + public('S_second_sent') + seek('S_second_sent',2102,'S_body') + [
        'S_body.OBJECTS[n_generator] = GENERATOR pgenerator_body',
        'pgenerator_body.VALUE = (POBJECT n_payload)',
        '$heap_count(HOBJECT n_payload,$frames_roots(S_body.FRAMES)) = 1',
        '$weakref_get(S_body,n_payloadwatch) = POBJECT n_payload',
        'S_body.PRECISIONINI = $ptascii("6")',
        owners('S_body','HOBJECT n_payload',2),
    ] + public('S_body') + seek('S_body',2103,'S_thrown') + [
        'S_thrown.TODO = (THROW_SEARCH n_exception) :: (CONFIG_GENERATOR pconfiggenerator_second "next") :: ptask_tail*',
        'S_thrown.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
        'pgenerator_closed.PHASE = GENERATOR_CLOSED',
        'pgenerator_closed.FRAME = eps',
        'pgenerator_closed.VALUE = (POBJECT n_payload)',
        'pgenerator_closed.KEY = (PINT 1)',
        '$node_children(S_thrown,HOBJECT n_generator) = [HOBJECT n_payload]',
        '$config_generator_factory_cached_history(S_thrown,pconfiggenerator_second)',
        '$config_generator_factory_cached_storage(S_thrown,pconfiggenerator_second)',
        '$config_generator_owning_items_live(S_thrown,pconfiggenerator_second.ITEMS)',
        cell('S_thrown','saved','n_saved_cell'),
        'S_thrown.STORE[n_saved_cell] = DEFINED (POBJECT n_exception)',
        cell('S_thrown','result','n_result_cell'),
        'S_thrown.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_thrown.PRECISIONINI = $ptascii("6")',
        '$weakref_get(S_thrown,n_genwatch) = POBJECT n_generator',
        '$weakref_get(S_thrown,n_payloadwatch) = POBJECT n_payload',
        owners('S_thrown','HOBJECT n_generator',2),
        owners('S_thrown','HOBJECT n_payload',2),
        'S_first_popped = S_thrown[.TODO = (THROW_SEARCH n_exception) :: ptask_tail*]',
        '$config_generator_factory_cached_history(S_first_popped,pconfiggenerator_second)',
        '$config_generator_discard_allowed(S_first_popped,pconfiggenerator_second)',
        '~$destructor_operational(S_first_popped)',
        '$eager_operation_pending(S_first_popped) = (n_exception)',
        'S_first_raw = $config_generator_discard(S_first_popped,pconfiggenerator_second,"next")',
        'S_first_raw = $config_generator_discard_state(S_first_popped,pconfiggenerator_second,"next")',
        'S_first_raw.TODO = (THROW_SEARCH n_exception) :: (CONFIG_GENERATOR pconfiggenerator_second "input-release") :: ptask_tail*',
        'PhpStep: S_thrown ~> S_first_raw',
        owners('S_first_raw','HOBJECT n_generator',1),
        '$config_generator_factory_cached_storage(S_first_raw,pconfiggenerator_second)',
    ] + public('S_thrown') + public('S_first_raw') + seek('S_thrown',2104,'S_input') + [
        'S_input.TODO = (THROW_SEARCH n_exception) :: (CONFIG_GENERATOR pconfiggenerator_second "input-release") :: ptask_input*',
        '$config_generator_valid(S_input,pconfiggenerator_second,"input-release")',
        '$config_generator_factory_cached_storage(S_input,pconfiggenerator_second)',
        '$weakref_get(S_input,n_genwatch) = POBJECT n_generator',
        '$weakref_get(S_input,n_payloadwatch) = POBJECT n_payload',
        owners('S_input','HOBJECT n_generator',1),
        owners('S_input','HOBJECT n_payload',2),
        'S_second_popped = S_input[.TODO = (THROW_SEARCH n_exception) :: ptask_input*]',
        '$config_generator_factory_cached_storage(S_second_popped,pconfiggenerator_second)',
        '$config_generator_discard_allowed(S_second_popped,pconfiggenerator_second)',
        'S_second_raw = $config_generator_discard(S_second_popped,pconfiggenerator_second,"input-release")',
        'S_second_raw.TODO = (THROW_SEARCH n_exception) :: ptask_input*',
        'S_second_raw.STORE = S_second_popped.STORE',
        'S_second_raw.EVENTS = S_second_popped.EVENTS',
        'S_second_raw.ALLOCATIONS = S_second_popped.ALLOCATIONS',
        'PhpStep: S_input ~> S_second_raw',
    ] + public('S_input') + public('S_second_raw') + seek('S_second_raw',2105,'S_catch') + [
        cell('S_catch','caught','n_caught_cell'),
        'S_catch.STORE[n_caught_cell] = DEFINED (POBJECT n_exception)',
        'S_catch.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_catch.PRECISIONINI = $ptascii("6")',
        '$weakref_get(S_catch,n_genwatch) = PNULL',
        '$weakref_get(S_catch,n_payloadwatch) = PNULL',
        '~((HOBJECT n_generator) <- S_catch.ALLOCATIONS)',
        '~((HOBJECT n_payload) <- S_catch.ALLOCATIONS)',
        '$config_generator_factory_cached_history(S_catch,pconfiggenerator_second)',
        '$throwable_field(S_catch,n_exception,"previous") = PNULL',
    ] + public('S_catch') + seek('S_catch',2106,'S_recovery') + [
        'S_recovery.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_recovery.PRECISIONINI = $ptascii("6")',
    ] + public('S_recovery')
    return checks + finish('S_recovery',stdout,['HOBJECT n_generator','HOBJECT n_payload','HOBJECT n_exception'])


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(SOURCES,conditions,HELPERS,model_timeout=300,
        extra_inputs=(Path(__file__),Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
