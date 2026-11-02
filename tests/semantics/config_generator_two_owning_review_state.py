#!/usr/bin/env python3
"""One cached object loses its cache edge while both copied slot owners remain."""
from pathlib import Path
from types import SimpleNamespace

import config_generator_two_owning_review_cases as cases
import list_missing_warning_protocol as shared
from array_generator_unpack_state_review import budget, finish, initial, owners, public, seek

NAME = 'config-generator-two-owning-same-object-typeerror'
SOURCES = SimpleNamespace(CASES={NAME: cases.CASES[NAME]}, __file__=cases.__file__)
HELPERS = shared.HELPERS + r'''
dec $a80_peer_echo(pstate, ptbytes) : bool
def $a80_peer_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $a80_peer_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 2300) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask*
  -- if |pconfiggenerator.ITEMS| = 1
def $list_warning_frontier(S, 2301) = $a80_peer_echo(S, $ptascii("T;"))
def $list_warning_frontier(S, 2302) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "finish") :: ptask*
def $list_warning_frontier(S, 2303) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "input-release") :: ptask*
def $list_warning_frontier(S, 2304) = true
  -- if S.TODO = (GENERATOR_STORAGE_STEP pgenstorage) :: ptask*
  -- if pgenstorage.NEXT = 1
def $list_warning_frontier(S, 2305) = true
  -- if S.TODO = (GENERATOR_STORAGE_STEP pgenstorage) :: ptask*
  -- if pgenstorage.NEXT = 2
def $list_warning_frontier(S, 2306) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "storage-released") :: ptask*
def $list_warning_frontier(S, 2307) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "invoke") :: ptask*
def $list_warning_frontier(S, 2308) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_GENERATOR pconfiggenerator "invoke") :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 2309) = $a80_peer_echo(S, $ptascii("E:"))
def $list_warning_frontier(S, 2310) = $a80_peer_echo(S, $ptascii("U:"))
def $list_warning_frontier(S, 2311) = $a80_peer_echo(S, $ptascii("R:"))
'''


def cell(state, name, identifier):
    return f'$lookup($global_table_view({state}).ENV,$ptascii("{name}")) = ({identifier})'


def conditions(name, program, path, stdout):
    assert name == NAME
    checks = initial(program, path) + seek('S_initial',2300,'S_value') + [
        'S_value.TODO = (CONFIG_GENERATOR pconfiggenerator_first "ready") :: ptask_value*',
        'pconfiggenerator_first.OBJECT = n_generator',
        'pconfiggenerator_first.INPUT = KNOWN (POBJECT n_generator)',
        'pconfiggenerator_first.PRODUCER = eps',
        'pconfiggenerator_first.CALL.OWNER = eps',
        'pconfiggenerator_first.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_payload))]',
        '$config_generator_factory_owning_input(S_value,pconfiggenerator_first)',
        'S_value.OBJECTS[n_generator] = GENERATOR pgenerator_value',
        'pgenerator_value.PHASE = GENERATOR_PAUSED',
        'pgenerator_value.VALUE = (POBJECT n_payload)',
        'pgenerator_value.KEY = (PINT 1)',
        'pgenerator_value.REFCELL = eps',
        '$config_generator_value(S_value,pconfiggenerator_first) = (POBJECT n_payload)',
        '$heap_count(HOBJECT n_payload,$pools_nodes(S_value.POOLS)) = 0',
        cell('S_value','genWatch','n_genwatch_cell'),
        'S_value.STORE[n_genwatch_cell] = DEFINED (POBJECT n_genwatch)',
        cell('S_value','payloadWatch','n_payloadwatch_cell'),
        'S_value.STORE[n_payloadwatch_cell] = DEFINED (POBJECT n_payloadwatch)',
        '$weakref_get(S_value,n_genwatch) = POBJECT n_generator',
        '$weakref_get(S_value,n_payloadwatch) = POBJECT n_payload',
        cell('S_value','result','n_result_cell'),
        'S_value.STORE[n_result_cell] = DEFINED (PINT 99)',
        owners('S_value','HOBJECT n_generator',2),
        owners('S_value','HOBJECT n_payload',3),
        'PhpStep: S_value ~> S_sent',
        'S_sent.TODO = (CONFIG_GENERATOR pconfiggenerator "next") :: ptask_value*',
        'pconfiggenerator = pconfiggenerator_first[.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_payload)),ENTRY (KINT 1) (DIRECT (POBJECT n_payload))]]',
        '$config_generator_argument_nodes(pconfiggenerator) = [HOBJECT n_payload,HOBJECT n_payload]',
        '$heap_count(HOBJECT n_payload,$task_nodes(CONFIG_GENERATOR pconfiggenerator "next")) = 2',
    ] + public('S_value') + public('S_sent') + seek('S_sent',2301,'S_body') + [
        'S_body.OBJECTS[n_generator] = GENERATOR pgenerator_body',
        'pgenerator_body.VALUE = (POBJECT n_payload)',
        '$heap_count(HOBJECT n_payload,$frames_roots(S_body.FRAMES)) = 2',
        '$objectprops_record_at(S_body.OBJECTPROPS,n_payload) = (pobjectprops_payload)',
        'pobjectprops_payload.SLOTS = [ppropertyslot_tag]',
        'ppropertyslot_tag.STATE = PROP_VALUE (DIRECT (PINT 31))',
        'S_body.PRECISIONINI = $ptascii("6")',
        owners('S_body','HOBJECT n_payload',3),
    ] + public('S_body') + seek('S_body',2302,'S_finish') + [
        'S_finish.TODO = (CONFIG_GENERATOR pconfiggenerator "finish") :: ptask_finish*',
        'S_finish.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
        'pgenerator_closed.PHASE = GENERATOR_CLOSED',
        'pgenerator_closed.FRAME = eps',
        'pgenerator_closed.VALUE = (POBJECT n_payload)',
        'pgenerator_closed.KEY = (PINT 1)',
        '$node_children(S_finish,HOBJECT n_generator) = [HOBJECT n_payload]',
        '$config_generator_factory_cached_history(S_finish,pconfiggenerator)',
        '$config_generator_factory_cached_storage(S_finish,pconfiggenerator)',
        '$config_generator_finish_allowed(S_finish,pconfiggenerator)',
        owners('S_finish','HOBJECT n_generator',2),
        owners('S_finish','HOBJECT n_payload',3),
    ] + public('S_finish') + seek('S_finish',2303,'S_input') + [
        'S_input.TODO = (CONFIG_GENERATOR pconfiggenerator "input-release") :: ptask_input*',
        '$config_generator_valid(S_input,pconfiggenerator,"input-release")',
        '~$config_generator_finish_allowed(S_input,pconfiggenerator)',
        '$config_generator_last_input_allowed(S_input,pconfiggenerator)',
        owners('S_input','HOBJECT n_generator',1),
        owners('S_input','HOBJECT n_payload',3),
    ] + public('S_input') + budget('S_input','S_release_budget') + seek('S_input',2304,'S_slot1') + [
        'S_slot1.TODO = (GENERATOR_STORAGE_STEP pgenstorage_slot1) :: ptask_slot1*',
        'pgenstorage_slot1.OBJECT = n_generator',
        '$generator_storage_valid(S_slot1,pgenstorage_slot1)',
        '$generator_storage_slot(pgenerator_closed,1) = [HOBJECT n_payload]',
        '$node_children(S_slot1,HOBJECT n_generator) = [HOBJECT n_payload]',
        '$weakref_get(S_slot1,n_genwatch) = POBJECT n_generator',
        '$weakref_get(S_slot1,n_payloadwatch) = POBJECT n_payload',
        owners('S_slot1','HOBJECT n_generator',1),
        owners('S_slot1','HOBJECT n_payload',3),
    ] + public('S_slot1') + seek('S_slot1',2305,'S_slot2') + [
        'S_slot2.TODO = (GENERATOR_STORAGE_STEP pgenstorage_slot2) :: ptask_slot2*',
        'pgenstorage_slot2.OBJECT = n_generator',
        '$generator_storage_valid(S_slot2,pgenstorage_slot2)',
        'S_slot2.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
        '$node_children(S_slot2,HOBJECT n_generator) = eps',
        '$weakref_get(S_slot2,n_genwatch) = POBJECT n_generator',
        '$weakref_get(S_slot2,n_payloadwatch) = POBJECT n_payload',
        owners('S_slot2','HOBJECT n_generator',1),
        owners('S_slot2','HOBJECT n_payload',2),
    ] + public('S_slot2') + seek('S_slot2',2306,'S_retired') + [
        'S_retired.TODO = (CONFIG_GENERATOR pconfiggenerator "storage-released") :: ptask_retired*',
        '~((HOBJECT n_generator) <- S_retired.ALLOCATIONS)',
        '$weakref_get(S_retired,n_genwatch) = PNULL',
        '$weakref_get(S_retired,n_payloadwatch) = POBJECT n_payload',
        '$config_generator_retired_scope(S_retired,pconfiggenerator)',
        '$config_generator_valid(S_retired,pconfiggenerator,"storage-released")',
        owners('S_retired','HOBJECT n_payload',2),
    ] + public('S_retired') + seek('S_retired',2307,'S_invoke') + [
        'S_invoke.TODO = (CONFIG_GENERATOR pconfiggenerator "invoke") :: ptask_invoke*',
        '$config_generator_valid(S_invoke,pconfiggenerator,"invoke")',
        'PhpStep: S_invoke ~> S_error',
        'S_error.COMPLETION = THROWING n_error',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
        'S_error.ARRAYS[n_trace].ITEMS[0] = ENTRY (KINT 0) (DIRECT (PARRAY n_frame))',
        '$trace_array_field(S_error,n_frame,$ptascii("args")) = PARRAY n_args',
        'S_error.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_payload)),ENTRY (KINT 1) (DIRECT (POBJECT n_payload))]',
    ] + public('S_invoke') + seek('S_invoke',2308,'S_throw') + [
        'S_throw.TODO = (THROW_SEARCH n_error) :: (CONFIG_GENERATOR pconfiggenerator "invoke") :: ptask_throw*',
        'S_popped = S_throw[.TODO = (THROW_SEARCH n_error) :: ptask_throw*]',
        '$config_generator_discard_allowed(S_popped,pconfiggenerator)',
        owners('S_popped','HOBJECT n_generator',0),
        owners('S_popped','HOBJECT n_payload',2),
        'S_raw = $config_generator_discard(S_popped,pconfiggenerator,"invoke")',
        'PhpStep: S_throw ~> S_raw',
        'S_raw.TODO = (THROW_SEARCH n_error) :: ptask_throw*',
    ] + public('S_throw') + public('S_raw') + seek('S_raw',2309,'S_catch') + [
        '$lookup(S_catch.ENV,$ptascii("error")) = (n_error_cell)',
        'S_catch.STORE[n_error_cell] = DEFINED (POBJECT n_error)',
        'S_catch.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_catch.PRECISIONINI = $ptascii("6")',
        '$weakref_get(S_catch,n_genwatch) = PNULL',
        '$weakref_get(S_catch,n_payloadwatch) = POBJECT n_payload',
        '$objectprops_record_at(S_catch.OBJECTPROPS,n_payload) = (pobjectprops_payload)',
        owners('S_catch','HOBJECT n_payload',2),
    ] + public('S_catch') + seek('S_catch',2310,'S_empty') + [
        '~((HOBJECT n_payload) <- S_empty.ALLOCATIONS)',
        '~((HOBJECT n_error) <- S_empty.ALLOCATIONS)',
        '$weakref_get(S_empty,n_payloadwatch) = PNULL',
        '$config_generator_factory_cached_history(S_empty,pconfiggenerator)',
        '~$config_generator_owning_items_live(S_empty,pconfiggenerator.ITEMS)',
    ] + public('S_empty') + seek('S_empty',2311,'S_recovery') + [
        'S_recovery.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_recovery.PRECISIONINI = $ptascii("6")',
    ] + public('S_recovery')
    return checks + finish('S_recovery',stdout,['HOBJECT n_generator','HOBJECT n_payload','HOBJECT n_error'])


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(SOURCES,conditions,HELPERS,model_timeout=300,
        extra_inputs=(Path(__file__),Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
