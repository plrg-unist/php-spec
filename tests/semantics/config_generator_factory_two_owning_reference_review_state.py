#!/usr/bin/env python3
"""Two factory-copied arguments keep one object after the BYREF cache retires."""
from pathlib import Path
from types import SimpleNamespace

import config_generator_factory_two_owning_reference_review_cases as cases
import list_missing_warning_protocol as shared
from array_generator_unpack_state_review import budget, finish, initial, owners, public, seek

NAME = 'config-generator-factory-two-owning-reference-shared-typeerror'
SOURCES = SimpleNamespace(CASES={NAME: cases.CASES[NAME]}, __file__=cases.__file__)
HELPERS = shared.HELPERS + r'''
dec $a92_peer_echo(pstate, ptbytes) : bool
def $a92_peer_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $a92_peer_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 9200) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask*
  -- if pconfiggenerator.ITEMS = eps
def $list_warning_frontier(S, 9201) = $a92_peer_echo(S, $ptascii("M0:"))
def $list_warning_frontier(S, 9202) = $a92_peer_echo(S, $ptascii("W0:"))
def $list_warning_frontier(S, 9203) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask*
  -- if |pconfiggenerator.ITEMS| = 1
def $list_warning_frontier(S, 9204) = $a92_peer_echo(S, $ptascii("T;"))
def $list_warning_frontier(S, 9205) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "finish") :: ptask*
  -- if |pconfiggenerator.ITEMS| = 2
def $list_warning_frontier(S, 9206) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "input-release") :: ptask*
def $list_warning_frontier(S, 9207) = true
  -- if S.TODO = (GENERATOR_STORAGE_STEP pgenstorage) :: ptask*
  -- if pgenstorage.NEXT = 1
def $list_warning_frontier(S, 9208) = true
  -- if S.TODO = (GENERATOR_STORAGE_STEP pgenstorage) :: ptask*
  -- if pgenstorage.NEXT = 2
def $list_warning_frontier(S, 9209) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "storage-released") :: ptask*
def $list_warning_frontier(S, 9210) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "invoke") :: ptask*
def $list_warning_frontier(S, 9211) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_GENERATOR pconfiggenerator "invoke") :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 9212) = $a92_peer_echo(S, $ptascii("E:"))
def $list_warning_frontier(S, 9213) = $a92_peer_echo(S, $ptascii("U:"))
def $list_warning_frontier(S, 9214) = $a92_peer_echo(S, $ptascii("R:"))
'''


def watch(state, name, cell_id, watch_id, value):
    return [f'$lookup($global_table_view({state}).ENV,$ptascii("{name}")) = ({cell_id})',
            f'{state}.STORE[{cell_id}] = DEFINED (POBJECT {watch_id})',
            f'$weakref_get({state},{watch_id}) = {value}']


def conditions(name, program, path, stdout):
    assert name == NAME
    checks = initial(program, path) + seek('S_initial', 9200, 'S_first') + [
        'S_first.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask_first*',
        'pconfiggenerator.OBJECT = n_generator',
        'pconfiggenerator.INPUT = KNOWN (POBJECT n_generator)',
        'pconfiggenerator.PRODUCER = eps',
        'pconfiggenerator.CALL.OWNER = eps',
        'pconfiggenerator.CALL.KIND = INTRINSIC_INI_SET',
        '$config_generator_owning_input(pconfiggenerator)',
        '$config_generator_input_nodes(pconfiggenerator) = [HOBJECT n_generator]',
        '$heap_count(HOBJECT n_generator,$config_generator_nodes(pconfiggenerator,"ready")) = 2',
        '$intrinsic_argument(S_first,pconfiggenerator.CALL.SITE,0) = ((expression,true,eps,PORIGIN n_source pcpath,z))',
        '$source_emission_noarg_call(S_first,n_source,pcpath,expression) = (z_call)',
        '$code_at(S_first.CODE,n_source) = (pcode)',
        '$source_unit(S_first.SOURCES,n_source) = (pcunit)',
        '$ppunpack_class(pcode,pcunit,pcpath) = (UNPACK_VAR)',
        '$code_name(pcode.NAMES,pcpath) = ((ptbytes_name,eps))',
        '$call_target(S_first,ptbytes_name,eps) = (pfunction_factory)',
        'S_first.OBJECTS[n_generator] = GENERATOR pgenerator_first',
        'pfunction_factory.SIGNATURE.PARAMETERS = eps',
        '~pfunction_factory.SIGNATURE.BYREF',
        '~$function_generator(S_first,pfunction_factory)',
        '$function_at($all_functions(S_first),pgenerator_first.FUNCTION) = (pfunction_generator)',
        'pfunction_generator.SIGNATURE.PARAMETERS = eps',
        'pfunction_generator.SIGNATURE.BYREF',
        '$function_generator(S_first,pfunction_generator)',
        'pfunction_generator =/= pfunction_factory',
        '~$config_generator_temporary_reference_input(S_first,pconfiggenerator)',
        '$config_generator_factory_reference_input(S_first,pconfiggenerator)',
        '~$config_generator_reference_owning_source(S_first,pconfiggenerator)',
        '$config_generator_history(S_first,pconfiggenerator)',
        'S_first.CURRENT = eps',
        'S_first.FRAMES = eps',
        'pgenerator_first.VALUE = eps',
        'pgenerator_first.REFCELL = (n_firstref)',
        'pgenerator_first.KEY = (PINT 0)',
        '$ordinary_reference_value(S_first,n_firstref) = (POBJECT n_shared)',
        '$config_generator_value(S_first,pconfiggenerator) = (POBJECT n_shared)',
        '$config_iterator_argument(S_first,POBJECT n_shared)',
        owners('S_first', 'HOBJECT n_generator', 2),
        owners('S_first', 'HOBJECT n_shared', 1),
    ] + watch('S_first', 'genWatch', 'n_genwatch_cell', 'n_genwatch',
              'POBJECT n_generator') + watch('S_first', 'payloadWatch', 'n_watch_cell',
              'n_watch', 'POBJECT n_shared') + [
        'S_debt = S_first[.LITERALREFDEBTS = [n_firstref]]',
        '$config_generator_value(S_debt,pconfiggenerator) = eps',
        'PhpStep: S_first ~> S_sent_first',
        'S_sent_first.TODO = (CONFIG_GENERATOR pconfiggenerator_one "next") :: ptask_first*',
        'pconfiggenerator_one = pconfiggenerator[.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_shared))]]',
        '$config_generator_factory_reference_input(S_sent_first,pconfiggenerator_one)',
        '$config_generator_temporary_reference_owning_first_items(S_sent_first,pconfiggenerator_one)',
        '~$config_generator_temporary_reference_two_owning_items(S_sent_first,pconfiggenerator_one)',
        '$config_generator_history(S_sent_first,pconfiggenerator_one)',
        '$task_nodes(CONFIG_GENERATOR pconfiggenerator_one "next") = [HOBJECT n_generator,HOBJECT n_generator,HOBJECT n_shared]',
        owners('S_sent_first', 'HOBJECT n_shared', 2),
        '$weakref_get(S_sent_first,n_genwatch) = POBJECT n_generator',
    ] + public('S_first') + public('S_sent_first') + seek('S_sent_first', 9201, 'S_mutated') + [
        '$ordinary_reference_value(S_mutated,n_firstref) = (POBJECT n_shared)',
        '$weakref_get(S_mutated,n_genwatch) = POBJECT n_generator',
        '$weakref_get(S_mutated,n_watch) = POBJECT n_shared',
        owners('S_mutated', 'HOBJECT n_shared', 2),
    ] + public('S_mutated') + seek('S_mutated', 9202, 'S_overwrite') + [
        '$ordinary_reference_value(S_overwrite,n_firstref) = (PINT 9)',
        '$weakref_get(S_overwrite,n_genwatch) = POBJECT n_generator',
        '$weakref_get(S_overwrite,n_watch) = POBJECT n_shared',
        owners('S_overwrite', 'HOBJECT n_shared', 2),
    ] + public('S_overwrite') + seek('S_overwrite', 9203, 'S_second') + [
        'S_second.TODO = (CONFIG_GENERATOR pconfiggenerator_one "ready") :: ptask_second*',
        'S_second.OBJECTS[n_generator] = GENERATOR pgenerator_second',
        'pgenerator_second.VALUE = eps',
        'pgenerator_second.REFCELL = (n_lastref)',
        'pgenerator_second.KEY = (PINT 1)',
        'n_lastref =/= n_firstref',
        '$ordinary_reference_value(S_second,n_lastref) = (POBJECT n_shared)',
        '$config_generator_factory_reference_input(S_second,pconfiggenerator_one)',
        '$config_generator_value(S_second,pconfiggenerator_one) = (POBJECT n_shared)',
        '$config_generator_temporary_reference_owning_first_items(S_second,pconfiggenerator_one)',
        '$config_generator_owning_items_live(S_second,pconfiggenerator_one.ITEMS)',
        '$weakref_get(S_second,n_watch) = POBJECT n_shared',
        '$weakref_get(S_second,n_genwatch) = POBJECT n_generator',
        owners('S_second', 'HOBJECT n_generator', 2),
        owners('S_second', 'HOBJECT n_shared', 2),
        'PhpStep: S_second ~> S_sent_second',
        'S_sent_second.TODO = (CONFIG_GENERATOR pconfiggenerator_two "next") :: ptask_second*',
        'pconfiggenerator_two = pconfiggenerator[.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_shared)),ENTRY (KINT 1) (DIRECT (POBJECT n_shared))]]',
        '$config_generator_temporary_reference_two_owning_items(S_sent_second,pconfiggenerator_two)',
        '$config_generator_temporary_reference_owning_last_items(S_sent_second,pconfiggenerator_two)',
        '$config_generator_history(S_sent_second,pconfiggenerator_two)',
        '$weakref_get(S_sent_second,n_genwatch) = POBJECT n_generator',
        owners('S_sent_second', 'HOBJECT n_shared', 3),
    ] + public('S_second') + public('S_sent_second') + seek('S_sent_second', 9204, 'S_terminal') + [
        '$ordinary_reference_value(S_terminal,n_lastref) = (POBJECT n_shared)',
        '$weakref_get(S_terminal,n_genwatch) = POBJECT n_generator',
        '$weakref_get(S_terminal,n_watch) = POBJECT n_shared',
        'S_terminal.PRECISIONINI = $ptascii("6")',
    ] + public('S_terminal') + seek('S_terminal', 9205, 'S_finish') + [
        'S_finish.TODO = (CONFIG_GENERATOR pconfiggenerator_two "finish") :: ptask_finish*',
        'S_finish.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
        'pgenerator_closed.PHASE = GENERATOR_CLOSED',
        'pgenerator_closed.FRAME = eps',
        'pgenerator_closed.VALUE = eps',
        'pgenerator_closed.REFCELL = (n_lastref)',
        'pgenerator_closed.KEY = (PINT 1)',
        '$ordinary_reference_value(S_finish,n_lastref) = (POBJECT n_shared)',
        '$node_children(S_finish,HOBJECT n_generator) = [HCELL n_lastref]',
        '$node_children(S_finish,HCELL n_lastref) = [HOBJECT n_shared]',
        '$config_generator_temporary_reference_two_owning_items(S_finish,pconfiggenerator_two)',
        '$config_generator_factory_reference_input(S_finish,pconfiggenerator_two)',
        '$config_generator_reference_history(S_finish,pconfiggenerator_two)',
        '$config_generator_temporary_reference_owning_storage(S_finish,pconfiggenerator_two)',
        '$config_generator_storage_child(S_finish,pconfiggenerator_two)',
        '$config_generator_finish_allowed(S_finish,pconfiggenerator_two)',
        '~$config_generator_temporary_reference_owning_first_completed(S_finish,pconfiggenerator_two)',
        owners('S_finish', 'HOBJECT n_generator', 2),
        owners('S_finish', 'HCELL n_lastref', 1),
        owners('S_finish', 'HOBJECT n_shared', 3),
        '$weakref_get(S_finish,n_watch) = POBJECT n_shared',
        '$weakref_get(S_finish,n_genwatch) = POBJECT n_generator',
    ] + public('S_finish') + budget('S_finish', 'S_data_budget') + seek('S_finish', 9206, 'S_input') + [
        'S_input.TODO = (CONFIG_GENERATOR pconfiggenerator_two "input-release") :: ptask_input*',
        '$config_generator_valid(S_input,pconfiggenerator_two,"input-release")',
        '$config_generator_nodes(pconfiggenerator_two,"input-release") = [HOBJECT n_generator,HOBJECT n_shared,HOBJECT n_shared]',
        '$ordinary_reference_value(S_input,n_lastref) = (POBJECT n_shared)',
        '$weakref_get(S_input,n_genwatch) = POBJECT n_generator',
        '$config_generator_temporary_reference_owning_storage(S_input,pconfiggenerator_two)',
        '$config_generator_last_input_allowed(S_input,pconfiggenerator_two)',
        '~$config_generator_finish_allowed(S_input,pconfiggenerator_two)',
        owners('S_input', 'HOBJECT n_generator', 1),
        owners('S_input', 'HCELL n_lastref', 1),
        owners('S_input', 'HOBJECT n_shared', 3),
        'S_input_debt = S_input[.LITERALREFDEBTS = [n_lastref]]',
        '~$config_generator_temporary_reference_owning_storage(S_input_debt,pconfiggenerator_two)',
        '~$config_generator_last_input_allowed(S_input_debt,pconfiggenerator_two)',
    ] + public('S_input') + budget('S_input', 'S_input_budget') + seek('S_input', 9207, 'S_slot1') + [
        'S_slot1.TODO = (GENERATOR_STORAGE_STEP pgenstorage_slot1) :: ptask_slot1*',
        'pgenstorage_slot1.OBJECT = n_generator',
        '$generator_storage_valid(S_slot1,pgenstorage_slot1)',
        '$ordinary_reference_value(S_slot1,n_lastref) = (POBJECT n_shared)',
        '$config_generator_reference_history(S_slot1,pconfiggenerator_two)',
        '$weakref_get(S_slot1,n_watch) = POBJECT n_shared',
        '$weakref_get(S_slot1,n_genwatch) = POBJECT n_generator',
        owners('S_slot1', 'HOBJECT n_generator', 1),
        owners('S_slot1', 'HCELL n_lastref', 1),
        owners('S_slot1', 'HOBJECT n_shared', 3),
    ] + public('S_slot1') + seek('S_slot1', 9208, 'S_slot2') + [
        'S_slot2.TODO = (GENERATOR_STORAGE_STEP pgenstorage_slot2) :: ptask_slot2*',
        'pgenstorage_slot2.OBJECT = n_generator',
        '$generator_storage_valid(S_slot2,pgenstorage_slot2)',
        '~((HCELL n_lastref) <- S_slot2.ALLOCATIONS)',
        '$node_children(S_slot2,HOBJECT n_generator) = eps',
        '(HOBJECT n_generator) <- S_slot2.ALLOCATIONS',
        '$weakref_get(S_slot2,n_watch) = POBJECT n_shared',
        '$weakref_get(S_slot2,n_genwatch) = POBJECT n_generator',
        owners('S_slot2', 'HOBJECT n_generator', 1),
        owners('S_slot2', 'HOBJECT n_shared', 2),
    ] + public('S_slot2') + seek('S_slot2', 9209, 'S_retired') + [
        'S_retired.TODO = (CONFIG_GENERATOR pconfiggenerator_two "storage-released") :: ptask_retired*',
        '~((HOBJECT n_generator) <- S_retired.ALLOCATIONS)',
        '~((HCELL n_lastref) <- S_retired.ALLOCATIONS)',
        '(HOBJECT n_shared) <- S_retired.ALLOCATIONS',
        '$weakref_get(S_retired,n_watch) = POBJECT n_shared',
        '$weakref_get(S_retired,n_genwatch) = PNULL',
        '$config_generator_factory_reference_input(S_retired,pconfiggenerator_two)',
        '$config_generator_reference_history(S_retired,pconfiggenerator_two)',
        '$config_generator_temporary_reference_two_owning_items(S_retired,pconfiggenerator_two)',
        '$config_generator_retired_scope(S_retired,pconfiggenerator_two)',
        '$config_generator_valid(S_retired,pconfiggenerator_two,"storage-released")',
        '~$config_generator_temporary_reference_owning_storage(S_retired,pconfiggenerator_two)',
        owners('S_retired', 'HOBJECT n_shared', 2),
    ] + public('S_retired') + seek('S_retired', 9210, 'S_invoke') + [
        'S_invoke.TODO = (CONFIG_GENERATOR pconfiggenerator_two "invoke") :: ptask_invoke*',
        '$config_generator_valid(S_invoke,pconfiggenerator_two,"invoke")',
        '$config_pack_prefix(pconfiggenerator_two.CALL,pconfiggenerator_two.ITEMS,false) = (pconfigcall_prefix)',
        'pconfigcall_prefix.SENT = [NAMED_SENT (KNOWN (POBJECT n_shared)),NAMED_SENT (KNOWN (POBJECT n_shared))]',
        '$weakref_get(S_invoke,n_watch) = POBJECT n_shared',
        '$weakref_get(S_invoke,n_genwatch) = PNULL',
        '~((HOBJECT n_generator) <- S_invoke.ALLOCATIONS)',
        '~((HCELL n_lastref) <- S_invoke.ALLOCATIONS)',
        owners('S_invoke', 'HOBJECT n_shared', 2),
        'PhpStep: S_invoke ~> S_error',
        'S_error.COMPLETION = THROWING n_error',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
        'S_error.ARRAYS[n_trace].ITEMS[0] = ENTRY (KINT 0) (DIRECT (PARRAY n_frame))',
        '$trace_array_field(S_error,n_frame,$ptascii("args")) = PARRAY n_args',
        'S_error.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_shared)),ENTRY (KINT 1) (DIRECT (POBJECT n_shared))]',
        '$weakref_get(S_error,n_watch) = POBJECT n_shared',
        '$weakref_get(S_error,n_genwatch) = PNULL',
    ] + public('S_invoke') + seek('S_invoke', 9211, 'S_throw') + [
        'S_throw.TODO = (THROW_SEARCH n_error) :: (CONFIG_GENERATOR pconfiggenerator_two "invoke") :: ptask_throw*',
        'S_popped = S_throw[.TODO = (THROW_SEARCH n_error) :: ptask_throw*]',
        '$config_generator_temporary_reference_two_owning_items(S_popped,pconfiggenerator_two)',
        '$config_generator_retired_scope(S_popped,pconfiggenerator_two)',
        '~$config_generator_temporary_reference_owning_storage(S_popped,pconfiggenerator_two)',
        '$config_generator_discard_allowed(S_popped,pconfiggenerator_two)',
        'S_raw = $config_generator_discard(S_popped,pconfiggenerator_two,"invoke")',
        'PhpStep: S_throw ~> S_raw',
        'S_raw.TODO = (THROW_SEARCH n_error) :: ptask_throw*',
        '$weakref_get(S_raw,n_watch) = POBJECT n_shared',
        '$weakref_get(S_raw,n_genwatch) = PNULL',
    ] + public('S_throw') + public('S_raw') + seek('S_raw', 9212, 'S_catch') + [
        'S_catch.PRECISIONINI = $ptascii("6")',
        '$weakref_get(S_catch,n_watch) = POBJECT n_shared',
        '$weakref_get(S_catch,n_genwatch) = PNULL',
        '~((HOBJECT n_generator) <- S_catch.ALLOCATIONS)',
        '~((HCELL n_lastref) <- S_catch.ALLOCATIONS)',
    ] + public('S_catch') + seek('S_catch', 9213, 'S_later') + [
        '$weakref_get(S_later,n_watch) = PNULL',
        '$weakref_get(S_later,n_genwatch) = PNULL',
        '~((HOBJECT n_shared) <- S_later.ALLOCATIONS)',
    ] + public('S_later') + seek('S_later', 9214, 'S_recovery') + [
        'S_recovery.PRECISIONINI = $ptascii("6")',
        '$weakref_get(S_recovery,n_genwatch) = PNULL',
        '$weakref_get(S_recovery,n_watch) = PNULL',
    ] + public('S_recovery')
    return checks + finish('S_recovery', stdout, [
        'HOBJECT n_generator', 'HCELL n_firstref', 'HCELL n_lastref',
        'HOBJECT n_shared', 'HOBJECT n_error'])


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(SOURCES, conditions, HELPERS, model_timeout=300,
        extra_inputs=(Path(__file__),
                      Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
