#!/usr/bin/env python3
"""Storage consumes a final ARRAY cache edge while its copied argument survives."""
from pathlib import Path
from types import SimpleNamespace

import config_generator_owning_cache_review_cases as cases
import list_missing_warning_protocol as shared
from array_generator_unpack_state_review import budget, finish, initial, owners, public, seek

NAME = 'config-generator-owning-cache-array-typeerror'
SOURCES = SimpleNamespace(CASES={NAME: cases.CASES[NAME]}, __file__=cases.__file__)
HELPERS = shared.HELPERS + r'''
dec $a79_peer_echo(pstate, ptbytes) : bool
def $a79_peer_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $a79_peer_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 2000) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask*
  -- if |pconfiggenerator.ITEMS| = 1
def $list_warning_frontier(S, 2001) = $a79_peer_echo(S, $ptascii("M:"))
def $list_warning_frontier(S, 2002) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "finish") :: ptask*
def $list_warning_frontier(S, 2003) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "input-release") :: ptask*
def $list_warning_frontier(S, 2004) = true
  -- if S.TODO = (GENERATOR_STORAGE_STEP pgenstorage) :: ptask*
  -- if pgenstorage.NEXT = 1
def $list_warning_frontier(S, 2005) = true
  -- if S.TODO = (GENERATOR_STORAGE_STEP pgenstorage) :: ptask*
  -- if pgenstorage.NEXT = 2
def $list_warning_frontier(S, 2006) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "storage-released") :: ptask*
def $list_warning_frontier(S, 2007) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "invoke") :: ptask*
def $list_warning_frontier(S, 2008) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_GENERATOR pconfiggenerator "invoke") :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 2009) = $a79_peer_echo(S, $ptascii("E:"))
def $list_warning_frontier(S, 2010) = $a79_peer_echo(S, $ptascii("R:"))
'''


def cell(state, name, identifier):
    return f'$lookup($global_table_view({state}).ENV,$ptascii("{name}")) = ({identifier})'


def conditions(name, program, path, stdout):
    assert name == NAME
    checks = initial(program, path) + seek('S_initial',2000,'S_value') + [
        'S_value.TODO = (CONFIG_GENERATOR pconfiggenerator_first "ready") :: ptask_value*',
        'pconfiggenerator_first.OBJECT = n_generator',
        'pconfiggenerator_first.INPUT = KNOWN (POBJECT n_generator)',
        'pconfiggenerator_first.PRODUCER = eps',
        'pconfiggenerator_first.CALL.OWNER = eps',
        'pconfiggenerator_first.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_option)]',
        '$string_bytes(pvalue_option) = ($ptascii("precision"))',
        '$config_generator_factory_owning_input(S_value,pconfiggenerator_first)',
        'S_value.OBJECTS[n_generator] = GENERATOR pgenerator_value',
        'pgenerator_value.PHASE = GENERATOR_PAUSED',
        'pgenerator_value.VALUE = (PARRAY n_option)',
        'pgenerator_value.KEY = (PINT 1)',
        'pgenerator_value.REFCELL = eps',
        '$config_generator_value(S_value,pconfiggenerator_first) = (PARRAY n_option)',
        'S_value.ARRAYS[n_option].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 13))]',
        '$heap_count(HARRAY n_option,$pools_nodes(S_value.POOLS)) = 0',
        cell('S_value','genWatch','n_genwatch_cell'),
        'S_value.STORE[n_genwatch_cell] = DEFINED (POBJECT n_genwatch)',
        '$weakref_get(S_value,n_genwatch) = POBJECT n_generator',
        cell('S_value','result','n_result_cell'),
        'S_value.STORE[n_result_cell] = DEFINED (PINT 99)',
        owners('S_value','HOBJECT n_generator',2),
        owners('S_value','HARRAY n_option',2),
        'PhpStep: S_value ~> S_sent',
        'S_sent.TODO = (CONFIG_GENERATOR pconfiggenerator "next") :: ptask_value*',
        'pconfiggenerator = pconfiggenerator_first[.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_option),ENTRY (KINT 1) (DIRECT (PARRAY n_option))]]',
        '$config_generator_argument_nodes(pconfiggenerator) = [HARRAY n_option]',
    ] + public('S_value') + public('S_sent') + seek('S_sent',2001,'S_body') + [
        '$lookup(S_body.ENV,$ptascii("row")) = (n_live_cell)',
        'S_body.STORE[n_live_cell] = DEFINED (PARRAY n_live)',
        'n_live =/= n_option',
        'S_body.ARRAYS[n_live].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 31))]',
        'S_body.ARRAYS[n_option].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 13))]',
        'S_body.OBJECTS[n_generator] = GENERATOR pgenerator_body',
        'pgenerator_body.VALUE = (PARRAY n_option)',
        '$heap_count(HARRAY n_option,$frames_roots(S_body.FRAMES)) = 1',
        owners('S_body','HARRAY n_option',2),
    ] + public('S_body') + seek('S_body',2002,'S_finish') + [
        'S_finish.TODO = (CONFIG_GENERATOR pconfiggenerator "finish") :: ptask_finish*',
        'S_finish.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
        'pgenerator_closed.PHASE = GENERATOR_CLOSED',
        'pgenerator_closed.FRAME = eps',
        'pgenerator_closed.VALUE = (PARRAY n_option)',
        'pgenerator_closed.KEY = (PINT 1)',
        '$node_children(S_finish,HOBJECT n_generator) = [HARRAY n_option]',
        '$config_generator_factory_cached_history(S_finish,pconfiggenerator)',
        '$config_generator_factory_cached_storage(S_finish,pconfiggenerator)',
        '$config_generator_finish_allowed(S_finish,pconfiggenerator)',
        '~((HARRAY n_live) <- S_finish.ALLOCATIONS)',
        'S_finish.PRECISIONINI = $ptascii("6")',
        owners('S_finish','HOBJECT n_generator',2),
        owners('S_finish','HARRAY n_option',2),
    ] + public('S_finish') + seek('S_finish',2003,'S_input') + [
        'S_input.TODO = (CONFIG_GENERATOR pconfiggenerator "input-release") :: ptask_input*',
        '$config_generator_valid(S_input,pconfiggenerator,"input-release")',
        '~$config_generator_finish_allowed(S_input,pconfiggenerator)',
        '$config_generator_last_input_allowed(S_input,pconfiggenerator)',
        '$config_generator_storage_child(S_input,pconfiggenerator)',
        owners('S_input','HOBJECT n_generator',1),
        owners('S_input','HARRAY n_option',2),
        # A late outside owner preserves the previously admitted release route.
        'S_retained = S_input[.STORE[n_result_cell] = DEFINED (POBJECT n_generator)]',
        owners('S_retained','HOBJECT n_generator',2),
        '$config_generator_factory_cached_history(S_retained,pconfiggenerator)',
        '$config_generator_finish_allowed(S_retained,pconfiggenerator)',
        '$config_generator_last_input_allowed(S_retained,pconfiggenerator)',
        'pconfiggenerator_bad = pconfiggenerator[.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_option),ENTRY (KINT 1) (DIRECT (PINT 7))]]',
        '$config_generator_history(S_input,pconfiggenerator_bad)',
        '~$config_generator_factory_cached_history(S_input,pconfiggenerator_bad)',
        '~$config_generator_last_input_allowed(S_input,pconfiggenerator_bad)',
    ] + public('S_input') + public('S_retained') + budget('S_input','S_release_budget') + seek('S_input',2004,'S_slot1') + [
        'S_slot1.TODO = (GENERATOR_STORAGE_STEP pgenstorage_slot1) :: ptask_slot1*',
        'pgenstorage_slot1.OBJECT = n_generator',
        '$generator_storage_valid(S_slot1,pgenstorage_slot1)',
        '$generator_storage_slot(pgenerator_closed,1) = [HARRAY n_option]',
        '$node_children(S_slot1,HOBJECT n_generator) = [HARRAY n_option]',
        '$weakref_get(S_slot1,n_genwatch) = POBJECT n_generator',
        owners('S_slot1','HOBJECT n_generator',1),
        owners('S_slot1','HARRAY n_option',2),
    ] + public('S_slot1') + seek('S_slot1',2005,'S_slot2') + [
        'S_slot2.TODO = (GENERATOR_STORAGE_STEP pgenstorage_slot2) :: ptask_slot2*',
        'pgenstorage_slot2.OBJECT = n_generator',
        '$generator_storage_valid(S_slot2,pgenstorage_slot2)',
        'S_slot2.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
        '$node_children(S_slot2,HOBJECT n_generator) = eps',
        '$weakref_get(S_slot2,n_genwatch) = POBJECT n_generator',
        'S_slot2.ARRAYS[n_option].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 13))]',
        owners('S_slot2','HOBJECT n_generator',1),
        owners('S_slot2','HARRAY n_option',1),
    ] + public('S_slot2') + seek('S_slot2',2006,'S_retired') + [
        'S_retired.TODO = (CONFIG_GENERATOR pconfiggenerator "storage-released") :: ptask_retired*',
        '~((HOBJECT n_generator) <- S_retired.ALLOCATIONS)',
        '$weakref_get(S_retired,n_genwatch) = PNULL',
        '$config_generator_factory_cached_history(S_retired,pconfiggenerator)',
        '~$config_generator_factory_cached_storage(S_retired,pconfiggenerator)',
        '$config_generator_retired_scope(S_retired,pconfiggenerator)',
        '$config_generator_valid(S_retired,pconfiggenerator,"storage-released")',
        '~$config_generator_retired_scope(S_retired[.CODE = eps],pconfiggenerator)',
        owners('S_retired','HARRAY n_option',1),
    ] + public('S_retired') + seek('S_retired',2007,'S_invoke') + [
        'S_invoke.TODO = (CONFIG_GENERATOR pconfiggenerator "invoke") :: ptask_invoke*',
        '$config_generator_valid(S_invoke,pconfiggenerator,"invoke")',
        'PhpStep: S_invoke ~> S_error',
        'S_error.COMPLETION = THROWING n_error',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
        'S_error.ARRAYS[n_trace].ITEMS[0] = ENTRY (KINT 0) (DIRECT (PARRAY n_frame))',
        '$trace_array_field(S_error,n_frame,$ptascii("args")) = PARRAY n_args',
        'S_error.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_option),ENTRY (KINT 1) (DIRECT (PARRAY n_option))]',
    ] + public('S_invoke') + seek('S_invoke',2008,'S_throw') + [
        'S_throw.TODO = (THROW_SEARCH n_error) :: (CONFIG_GENERATOR pconfiggenerator "invoke") :: ptask_throw*',
        'S_popped = S_throw[.TODO = (THROW_SEARCH n_error) :: ptask_throw*]',
        '$config_generator_factory_cached_history(S_popped,pconfiggenerator)',
        '$config_generator_discard_allowed(S_popped,pconfiggenerator)',
        owners('S_popped','HOBJECT n_generator',0),
        owners('S_popped','HARRAY n_option',1),
        'S_raw = $config_generator_discard(S_popped,pconfiggenerator,"invoke")',
        'PhpStep: S_throw ~> S_raw',
        'S_raw.TODO = (THROW_SEARCH n_error) :: ptask_throw*',
    ] + public('S_throw') + public('S_raw') + seek('S_raw',2009,'S_catch') + [
        '$lookup(S_catch.ENV,$ptascii("error")) = (n_error_cell)',
        'S_catch.STORE[n_error_cell] = DEFINED (POBJECT n_error)',
        'S_catch.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_catch.PRECISIONINI = $ptascii("6")',
        '$weakref_get(S_catch,n_genwatch) = PNULL',
        'S_catch.ARRAYS[n_option].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 13))]',
        owners('S_catch','HARRAY n_option',1),
    ] + public('S_catch') + seek('S_catch',2010,'S_recovery') + [
        '~((HARRAY n_option) <- S_recovery.ALLOCATIONS)',
        '~((HOBJECT n_error) <- S_recovery.ALLOCATIONS)',
        'S_recovery.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_recovery.PRECISIONINI = $ptascii("6")',
    ] + public('S_recovery')
    return checks + finish('S_recovery',stdout,['HOBJECT n_generator','HARRAY n_option','HARRAY n_live','HOBJECT n_error'])


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(SOURCES,conditions,HELPERS,model_timeout=300,
        extra_inputs=(Path(__file__),Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
