#!/usr/bin/env python3
"""A temporary BYREF Generator retires its changed ARRAY before TypeError."""
from pathlib import Path
from types import SimpleNamespace

import config_generator_temporary_owning_reference_review_cases as cases
import list_missing_warning_protocol as shared
from array_generator_unpack_state_review import budget, finish, initial, owners, public, seek

NAME = 'config-generator-temporary-owning-reference-array-cow-typeerror'
SOURCES = SimpleNamespace(CASES={NAME: cases.CASES[NAME]}, __file__=cases.__file__)
HELPERS = shared.HELPERS + r'''
dec $a85_peer_echo(pstate, ptbytes) : bool
def $a85_peer_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $a85_peer_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 8500) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask*
  -- if pconfiggenerator.ITEMS = eps
def $list_warning_frontier(S, 8501) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask*
  -- if |pconfiggenerator.ITEMS| = 1
def $list_warning_frontier(S, 8502) = $a85_peer_echo(S, $ptascii("C:"))
def $list_warning_frontier(S, 8503) = $a85_peer_echo(S, $ptascii("T;"))
def $list_warning_frontier(S, 8504) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "finish") :: ptask*
  -- if |pconfiggenerator.ITEMS| = 2
def $list_warning_frontier(S, 8505) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "input-release") :: ptask*
def $list_warning_frontier(S, 8506) = true
  -- if S.TODO = (GENERATOR_STORAGE_STEP pgenstorage) :: ptask*
  -- if pgenstorage.NEXT = 1
def $list_warning_frontier(S, 8507) = true
  -- if S.TODO = (GENERATOR_STORAGE_STEP pgenstorage) :: ptask*
  -- if pgenstorage.NEXT = 2
def $list_warning_frontier(S, 8508) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "storage-released") :: ptask*
def $list_warning_frontier(S, 8509) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "invoke") :: ptask*
def $list_warning_frontier(S, 8510) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_GENERATOR pconfiggenerator "invoke") :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 8511) = $a85_peer_echo(S, $ptascii("E:"))
def $list_warning_frontier(S, 8512) = $a85_peer_echo(S, $ptascii("L:"))
def $list_warning_frontier(S, 8513) = $a85_peer_echo(S, $ptascii("R:"))
'''


def row(state, array, value, marker):
    return (f'{state}.ARRAYS[{array}].ITEMS = '
            f'[ENTRY (KINT 0) (DIRECT (PINT {value})), '
            f'ENTRY (KINT 1) (DIRECT (POBJECT {marker}))]')


def watch(state, name, cell_id, watch_id, value):
    return [f'$lookup($global_table_view({state}).ENV,$ptascii("{name}")) = ({cell_id})',
            f'{state}.STORE[{cell_id}] = DEFINED (POBJECT {watch_id})',
            f'$weakref_get({state},{watch_id}) = {value}']


def conditions(name, program, path, stdout):
    assert name == NAME
    checks = initial(program, path) + seek('S_initial', 8500, 'S_option') + [
        'S_option.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask_option*',
        'pconfiggenerator.OBJECT = n_generator',
        'pconfiggenerator.INPUT = KNOWN (POBJECT n_generator)',
        'pconfiggenerator.PRODUCER = eps',
        'pconfiggenerator.CALL.OWNER = eps',
        'pconfiggenerator.CALL.KIND = INTRINSIC_INI_SET',
        '$config_generator_owning_input(pconfiggenerator)',
        '$config_generator_input_nodes(pconfiggenerator) = [HOBJECT n_generator]',
        '$heap_count(HOBJECT n_generator,$config_generator_nodes(pconfiggenerator,"ready")) = 2',
        '$intrinsic_argument(S_option,pconfiggenerator.CALL.SITE,0) = ((expression,true,eps,PORIGIN n_source pcpath,z))',
        '$source_emission_noarg_call(S_option,n_source,pcpath,expression) = (z_call)',
        '$code_at(S_option.CODE,n_source) = (pcode)',
        '$source_unit(S_option.SOURCES,n_source) = (pcunit)',
        '$ppunpack_class(pcode,pcunit,pcpath) = (UNPACK_VAR)',
        '$code_name(pcode.NAMES,pcpath) = ((ptbytes_name,eps))',
        '$call_target(S_option,ptbytes_name,eps) = (pfunction)',
        'S_option.OBJECTS[n_generator] = GENERATOR pgenerator_option',
        '$function_at($all_functions(S_option),pgenerator_option.FUNCTION) = (pfunction)',
        'pfunction.SIGNATURE.PARAMETERS = eps',
        'pfunction.SIGNATURE.BYREF',
        '$function_generator(S_option,pfunction)',
        '$config_generator_temporary_reference_input(S_option,pconfiggenerator)',
        'pgenerator_option.VALUE = eps',
        'pgenerator_option.REFCELL = (n_optionref)',
        'pgenerator_option.KEY = (PINT 0)',
        '$ordinary_reference_value(S_option,n_optionref) = (pvalue_option)',
        '$string_bytes(pvalue_option) = ($ptascii("precision"))',
        '$config_generator_value(S_option,pconfiggenerator) = (pvalue_option)',
        '$lookup($global_table_view(S_option).ENV,$ptascii("result")) = (n_result_cell)',
        'S_option.STORE[n_result_cell] = DEFINED (PINT 99)',
        owners('S_option', 'HOBJECT n_generator', 2),
        'PhpStep: S_option ~> S_first_sent',
        'S_first_sent.TODO = (CONFIG_GENERATOR pconfiggenerator_first "next") :: ptask_option*',
        'pconfiggenerator_first = pconfiggenerator[.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_option)]]',
        '~$config_generator_history(S_option[.CODE = eps],pconfiggenerator)',
        '~$config_generator_history(S_option[.SOURCES = eps],pconfiggenerator)',
    ] + public('S_option') + public('S_first_sent') + seek('S_first_sent', 8501, 'S_value') + [
        'S_value.TODO = (CONFIG_GENERATOR pconfiggenerator_first "ready") :: ptask_value*',
        'S_value.OBJECTS[n_generator] = GENERATOR pgenerator_value',
        'pgenerator_value.VALUE = eps',
        'pgenerator_value.REFCELL = (n_payloadref)',
        'pgenerator_value.KEY = (PINT 1)',
        'n_payloadref =/= n_optionref',
        '$ordinary_reference_value(S_value,n_payloadref) = (PARRAY n_old)',
        row('S_value', 'n_old', 13, 'n_oldmarker'),
        '$config_generator_value(S_value,pconfiggenerator_first) = (PARRAY n_old)',
        '$config_iterator_argument(S_value,PARRAY n_old)',
        owners('S_value', 'HOBJECT n_generator', 2),
        owners('S_value', 'HARRAY n_old', 1),
        owners('S_value', 'HOBJECT n_oldmarker', 1),
    ] + watch('S_value', 'oldWatch', 'n_oldwatch_cell', 'n_oldwatch',
              'POBJECT n_oldmarker') + [
        'S_debt = S_value[.LITERALREFDEBTS = [n_payloadref]]',
        '$config_generator_value(S_debt,pconfiggenerator_first) = eps',
        'PhpStep: S_value ~> S_second_sent',
        'S_second_sent.TODO = (CONFIG_GENERATOR pconfiggenerator_second "next") :: ptask_value*',
        'pconfiggenerator_second = pconfiggenerator[.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_option),ENTRY (KINT 1) (DIRECT (PARRAY n_old))]]',
        '$config_generator_temporary_reference_owning_last_items(S_second_sent,pconfiggenerator_second)',
        '$config_generator_history(S_second_sent,pconfiggenerator_second)',
        '$task_nodes(CONFIG_GENERATOR pconfiggenerator_second "next") = [HOBJECT n_generator,HOBJECT n_generator,HARRAY n_old]',
        owners('S_second_sent', 'HARRAY n_old', 2),
    ] + public('S_value') + public('S_second_sent') + seek('S_second_sent', 8502, 'S_mutated') + [
        '$ordinary_reference_value(S_mutated,n_payloadref) = (PARRAY n_new)',
        'n_new =/= n_old',
        row('S_mutated', 'n_old', 13, 'n_oldmarker'),
        row('S_mutated', 'n_new', 31, 'n_newmarker'),
        '$node_children(S_mutated,HCELL n_payloadref) = [HARRAY n_new]',
        owners('S_mutated', 'HARRAY n_old', 1),
        owners('S_mutated', 'HARRAY n_new', 1),
        owners('S_mutated', 'HOBJECT n_oldmarker', 1),
        owners('S_mutated', 'HOBJECT n_newmarker', 1),
        '$weakref_get(S_mutated,n_oldwatch) = POBJECT n_oldmarker',
    ] + watch('S_mutated', 'newWatch', 'n_newwatch_cell', 'n_newwatch',
              'POBJECT n_newmarker') + public('S_mutated') + seek('S_mutated', 8503, 'S_terminal') + [
        'S_terminal.PRECISIONINI = $ptascii("6")',
        '$ordinary_reference_value(S_terminal,n_payloadref) = (PARRAY n_new)',
        '$weakref_get(S_terminal,n_oldwatch) = POBJECT n_oldmarker',
        '$weakref_get(S_terminal,n_newwatch) = POBJECT n_newmarker',
    ] + public('S_terminal') + seek('S_terminal', 8504, 'S_finish') + [
        'S_finish.TODO = (CONFIG_GENERATOR pconfiggenerator_second "finish") :: ptask_finish*',
        'S_finish.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
        'pgenerator_closed.PHASE = GENERATOR_CLOSED',
        'pgenerator_closed.FRAME = eps',
        'pgenerator_closed.VALUE = eps',
        'pgenerator_closed.REFCELL = (n_payloadref)',
        'pgenerator_closed.KEY = (PINT 1)',
        '$ordinary_reference_value(S_finish,n_payloadref) = (PARRAY n_new)',
        '$node_children(S_finish,HOBJECT n_generator) = [HCELL n_payloadref]',
        '$node_children(S_finish,HCELL n_payloadref) = [HARRAY n_new]',
        row('S_finish', 'n_old', 13, 'n_oldmarker'),
        row('S_finish', 'n_new', 31, 'n_newmarker'),
        '$config_generator_temporary_reference_owning_last_items(S_finish,pconfiggenerator_second)',
        '$config_generator_reference_history(S_finish,pconfiggenerator_second)',
        '$config_generator_temporary_reference_owning_storage(S_finish,pconfiggenerator_second)',
        '$config_generator_storage_child(S_finish,pconfiggenerator_second)',
        '$config_generator_finish_allowed(S_finish,pconfiggenerator_second)',
        '~$config_generator_reference_owning_last_items(S_finish,pconfiggenerator_second)',
        owners('S_finish', 'HOBJECT n_generator', 2),
        owners('S_finish', 'HCELL n_payloadref', 1),
        owners('S_finish', 'HARRAY n_old', 1),
        owners('S_finish', 'HARRAY n_new', 1),
        owners('S_finish', 'HOBJECT n_oldmarker', 1),
        owners('S_finish', 'HOBJECT n_newmarker', 1),
        'S_finish.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_finish.PRECISIONINI = $ptascii("6")',
    ] + public('S_finish') + budget('S_finish', 'S_data_budget') + seek('S_finish', 8505, 'S_input') + [
        'S_input.TODO = (CONFIG_GENERATOR pconfiggenerator_second "input-release") :: ptask_input*',
        '$config_generator_valid(S_input,pconfiggenerator_second,"input-release")',
        '$config_generator_nodes(pconfiggenerator_second,"input-release") = [HOBJECT n_generator,HARRAY n_old]',
        '$ordinary_reference_value(S_input,n_payloadref) = (PARRAY n_new)',
        '$config_generator_temporary_reference_owning_storage(S_input,pconfiggenerator_second)',
        '$config_generator_last_input_allowed(S_input,pconfiggenerator_second)',
        '~$config_generator_finish_allowed(S_input,pconfiggenerator_second)',
        '~$generator_storage_active(S_input,n_generator)',
        owners('S_input', 'HOBJECT n_generator', 1),
        owners('S_input', 'HCELL n_payloadref', 1),
        owners('S_input', 'HARRAY n_old', 1),
        owners('S_input', 'HARRAY n_new', 1),
        'S_input_debt = S_input[.LITERALREFDEBTS = [n_payloadref]]',
        '~$config_generator_temporary_reference_owning_storage(S_input_debt,pconfiggenerator_second)',
        '~$config_generator_last_input_allowed(S_input_debt,pconfiggenerator_second)',
    ] + public('S_input') + budget('S_input', 'S_input_budget') + seek('S_input', 8506, 'S_slot1') + [
        'S_slot1.TODO = (GENERATOR_STORAGE_STEP pgenstorage_slot1) :: ptask_slot1*',
        'pgenstorage_slot1.OBJECT = n_generator',
        '$generator_storage_valid(S_slot1,pgenstorage_slot1)',
        '$ordinary_reference_value(S_slot1,n_payloadref) = (PARRAY n_new)',
        '$config_generator_reference_history(S_slot1,pconfiggenerator_second)',
        '~$config_generator_temporary_reference_owning_storage(S_slot1,pconfiggenerator_second)',
        '$weakref_get(S_slot1,n_oldwatch) = POBJECT n_oldmarker',
        '$weakref_get(S_slot1,n_newwatch) = POBJECT n_newmarker',
        owners('S_slot1', 'HOBJECT n_generator', 1),
        owners('S_slot1', 'HCELL n_payloadref', 1),
        owners('S_slot1', 'HARRAY n_old', 1),
        owners('S_slot1', 'HARRAY n_new', 1),
    ] + public('S_slot1') + seek('S_slot1', 8507, 'S_slot2') + [
        'S_slot2.TODO = (GENERATOR_STORAGE_STEP pgenstorage_slot2) :: ptask_slot2*',
        'pgenstorage_slot2.OBJECT = n_generator',
        '$generator_storage_valid(S_slot2,pgenstorage_slot2)',
        '~((HCELL n_payloadref) <- S_slot2.ALLOCATIONS)',
        '~((HARRAY n_new) <- S_slot2.ALLOCATIONS)',
        '~((HOBJECT n_newmarker) <- S_slot2.ALLOCATIONS)',
        '$node_children(S_slot2,HOBJECT n_generator) = eps',
        '(HOBJECT n_generator) <- S_slot2.ALLOCATIONS',
        '(HARRAY n_old) <- S_slot2.ALLOCATIONS',
        '$weakref_get(S_slot2,n_oldwatch) = POBJECT n_oldmarker',
        '$weakref_get(S_slot2,n_newwatch) = PNULL',
        owners('S_slot2', 'HOBJECT n_generator', 1),
        owners('S_slot2', 'HARRAY n_old', 1),
    ] + public('S_slot2') + seek('S_slot2', 8508, 'S_retired') + [
        'S_retired.TODO = (CONFIG_GENERATOR pconfiggenerator_second "storage-released") :: ptask_retired*',
        '~((HOBJECT n_generator) <- S_retired.ALLOCATIONS)',
        '~((HCELL n_payloadref) <- S_retired.ALLOCATIONS)',
        '~((HARRAY n_new) <- S_retired.ALLOCATIONS)',
        '$weakref_get(S_retired,n_oldwatch) = POBJECT n_oldmarker',
        '$weakref_get(S_retired,n_newwatch) = PNULL',
        '$config_generator_reference_history(S_retired,pconfiggenerator_second)',
        '$config_generator_temporary_reference_owning_last_items(S_retired,pconfiggenerator_second)',
        '$config_generator_retired_scope(S_retired,pconfiggenerator_second)',
        '$config_generator_valid(S_retired,pconfiggenerator_second,"storage-released")',
        '~$config_generator_temporary_reference_owning_storage(S_retired,pconfiggenerator_second)',
    ] + public('S_retired') + seek('S_retired', 8509, 'S_invoke') + [
        'S_invoke.TODO = (CONFIG_GENERATOR pconfiggenerator_second "invoke") :: ptask_invoke*',
        '$config_generator_valid(S_invoke,pconfiggenerator_second,"invoke")',
        '$config_pack_prefix(pconfiggenerator_second.CALL,pconfiggenerator_second.ITEMS,false) = (pconfigcall_prefix)',
        'pconfigcall_prefix.SENT = [NAMED_SENT (KNOWN pvalue_option),NAMED_SENT (KNOWN (PARRAY n_old))]',
        '$weakref_get(S_invoke,n_oldwatch) = POBJECT n_oldmarker',
        '$weakref_get(S_invoke,n_newwatch) = PNULL',
        '~((HOBJECT n_generator) <- S_invoke.ALLOCATIONS)',
        '~((HCELL n_payloadref) <- S_invoke.ALLOCATIONS)',
        'PhpStep: S_invoke ~> S_error',
        'S_error.COMPLETION = THROWING n_error',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
        'S_error.ARRAYS[n_trace].ITEMS[0] = ENTRY (KINT 0) (DIRECT (PARRAY n_frame))',
        '$trace_array_field(S_error,n_frame,$ptascii("args")) = PARRAY n_args',
        'S_error.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_trace_option),ENTRY (KINT 1) (DIRECT (PARRAY n_old))]',
        '$string_bytes(pvalue_trace_option) = ($ptascii("precision"))',
        row('S_error', 'n_old', 13, 'n_oldmarker'),
        '$weakref_get(S_error,n_oldwatch) = POBJECT n_oldmarker',
        '$weakref_get(S_error,n_newwatch) = PNULL',
    ] + public('S_invoke') + seek('S_invoke', 8510, 'S_throw') + [
        'S_throw.TODO = (THROW_SEARCH n_error) :: (CONFIG_GENERATOR pconfiggenerator_second "invoke") :: ptask_throw*',
        'S_popped = S_throw[.TODO = (THROW_SEARCH n_error) :: ptask_throw*]',
        '$config_generator_temporary_reference_owning_last_items(S_popped,pconfiggenerator_second)',
        '$config_generator_retired_scope(S_popped,pconfiggenerator_second)',
        '~$config_generator_temporary_reference_owning_storage(S_popped,pconfiggenerator_second)',
        '$config_generator_discard_allowed(S_popped,pconfiggenerator_second)',
        'S_raw = $config_generator_discard(S_popped,pconfiggenerator_second,"invoke")',
        'PhpStep: S_throw ~> S_raw',
        'S_raw.TODO = (THROW_SEARCH n_error) :: ptask_throw*',
        '$weakref_get(S_raw,n_oldwatch) = POBJECT n_oldmarker',
        '$weakref_get(S_raw,n_newwatch) = PNULL',
    ] + public('S_throw') + public('S_raw') + seek('S_raw', 8511, 'S_catch') + [
        'S_catch.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_catch.PRECISIONINI = $ptascii("6")',
        '$weakref_get(S_catch,n_oldwatch) = POBJECT n_oldmarker',
        '$weakref_get(S_catch,n_newwatch) = PNULL',
        '~((HOBJECT n_generator) <- S_catch.ALLOCATIONS)',
        '~((HCELL n_payloadref) <- S_catch.ALLOCATIONS)',
    ] + public('S_catch') + seek('S_catch', 8512, 'S_later') + [
        '$weakref_get(S_later,n_oldwatch) = PNULL',
        '$weakref_get(S_later,n_newwatch) = PNULL',
        '~((HARRAY n_old) <- S_later.ALLOCATIONS)',
        '~((HOBJECT n_oldmarker) <- S_later.ALLOCATIONS)',
        '~((HARRAY n_new) <- S_later.ALLOCATIONS)',
        '~((HOBJECT n_newmarker) <- S_later.ALLOCATIONS)',
    ] + public('S_later') + seek('S_later', 8513, 'S_recovery') + [
        'S_recovery.PRECISIONINI = $ptascii("6")',
    ] + public('S_recovery')
    return checks + finish('S_recovery', stdout, [
        'HOBJECT n_generator', 'HCELL n_payloadref', 'HARRAY n_old',
        'HARRAY n_new', 'HOBJECT n_oldmarker', 'HOBJECT n_newmarker',
        'HOBJECT n_error'])


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(SOURCES, conditions, HELPERS, model_timeout=300,
        extra_inputs=(Path(__file__),
                      Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
