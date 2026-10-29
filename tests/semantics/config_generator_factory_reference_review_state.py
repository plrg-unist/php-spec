#!/usr/bin/env python3
"""A returned BYREF Generator has real INPUT/DATA and only a weak observer."""
from pathlib import Path
from types import SimpleNamespace

import config_generator_factory_reference_review_cases as cases
import list_missing_warning_protocol as shared
from array_generator_unpack_state_review import budget, finish, initial, owners, public, seek

NAME = 'config-generator-factory-reference-null-handler-return'
SOURCES = SimpleNamespace(CASES={NAME: cases.CASES[NAME]}, __file__=cases.__file__)
HELPERS = shared.HELPERS + r'''
dec $a76_peer_echo(pstate, ptbytes) : bool
def $a76_peer_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $a76_peer_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 1400) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask*
  -- if pconfiggenerator.ITEMS = eps
def $list_warning_frontier(S, 1401) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask*
  -- if |pconfiggenerator.ITEMS| = 1
def $list_warning_frontier(S, 1402) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "finish") :: ptask*
def $list_warning_frontier(S, 1403) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "input-release") :: ptask*
def $list_warning_frontier(S, 1404) = true
  -- if S.TODO = (GENERATOR_STORAGE_STEP pgenstorage) :: ptask*
  -- if pgenstorage.NEXT = 1
def $list_warning_frontier(S, 1405) = true
  -- if S.TODO = (GENERATOR_STORAGE_STEP pgenstorage) :: ptask*
  -- if pgenstorage.NEXT = 2
def $list_warning_frontier(S, 1406) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "storage-released") :: ptask*
def $list_warning_frontier(S, 1407) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "invoke") :: ptask*
def $list_warning_frontier(S, 1408) = $a76_peer_echo(S, $ptascii("H:"))
def $list_warning_frontier(S, 1409) = true
  -- if S.TODO = (CONFIG_INI_NULL_RESULT pconfigcall) :: ptask*
def $list_warning_frontier(S, 1410) = $a76_peer_echo(S, $ptascii("R:"))
'''


def conditions(name, program, path, stdout):
    assert name == NAME
    checks = initial(program, path) + seek('S_initial', 1400, 'S_option') + [
        'S_option.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask_option*',
        'pconfiggenerator.OBJECT = n_generator',
        'pconfiggenerator.INPUT = KNOWN (POBJECT n_generator)',
        'pconfiggenerator.PRODUCER = eps',
        'pconfiggenerator.CALL.OWNER = (n_callee)',
        'pconfiggenerator.CALL.KIND = INTRINSIC_INI_SET',
        '$config_generator_owning_input(pconfiggenerator)',
        '$config_generator_input_nodes(pconfiggenerator) = [HOBJECT n_generator]',
        '$heap_count(HOBJECT n_generator,$config_generator_nodes(pconfiggenerator,"ready")) = 2',
        'S_option.OBJECTS[n_generator] = GENERATOR pgenerator_option',
        'pgenerator_option.VALUE = eps',
        'pgenerator_option.REFCELL = (n_option_cell)',
        '$ordinary_reference_value(S_option,n_option_cell) = (PNULL)',
        '$intrinsic_argument(S_option,pconfiggenerator.CALL.SITE,0) = ((expression,true,eps,PORIGIN n_source pcpath,z))',
        '$source_emission_noarg_call(S_option,n_source,pcpath,expression) = (z_call)',
        '$code_at(S_option.CODE,n_source) = (pcode)',
        '$source_unit(S_option.SOURCES,n_source) = (pcunit)',
        '$ppunpack_class(pcode,pcunit,pcpath) = (UNPACK_VAR)',
        '$code_name(pcode.NAMES,pcpath) = ((ptbytes_name,eps))',
        '$call_target(S_option,ptbytes_name,eps) = (pfunction_factory)',
        'pfunction_factory.SIGNATURE.PARAMETERS = eps',
        '~pfunction_factory.SIGNATURE.BYREF',
        '~$function_generator(S_option,pfunction_factory)',
        '$function_at($all_functions(S_option),pgenerator_option.FUNCTION) = (pfunction_generator)',
        'pfunction_generator.SIGNATURE.PARAMETERS = eps',
        'pfunction_generator.SIGNATURE.BYREF',
        '$function_generator(S_option,pfunction_generator)',
        'pfunction_generator =/= pfunction_factory',
        '~$config_generator_reference_input(pconfiggenerator)',
        '~$config_generator_temporary_reference_input(S_option,pconfiggenerator)',
        '$config_generator_factory_reference_input(S_option,pconfiggenerator)',
        '$config_generator_history(S_option,pconfiggenerator)',
        'S_option.CURRENT = eps',
        'S_option.FRAMES = eps',
        '$lookup($global_table_view(S_option).ENV,$ptascii("watch")) = (n_watch_cell)',
        'S_option.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)',
        '$weakref_get(S_option,n_watch) = POBJECT n_generator',
        '$lookup($global_table_view(S_option).ENV,$ptascii("result")) = (n_result_cell)',
        'S_option.STORE[n_result_cell] = DEFINED (PINT 99)',
        owners('S_option', 'HOBJECT n_generator', 2),
        'PhpStep: S_option ~> S_first_sent',
        'S_first_sent.TODO = (CONFIG_GENERATOR pconfiggenerator_first "next") :: ptask_option*',
        'pconfiggenerator_first = pconfiggenerator[.ITEMS = [ENTRY (KINT 0) (DIRECT PNULL)]]',
        '~$config_generator_history(S_option[.CODE = eps],pconfiggenerator)',
        '~$config_generator_history(S_option[.SOURCES = eps],pconfiggenerator)',
        '~$config_generator_input(S_option,pconfiggenerator[.INPUT = KNOWN (POBJECT n_callee)])',
    ] + public('S_option') + seek('S_first_sent', 1401, 'S_value') + [
        'S_value.TODO = (CONFIG_GENERATOR pconfiggenerator_first "ready") :: ptask_value*',
        'S_value.OBJECTS[n_generator] = GENERATOR pgenerator_value',
        'pgenerator_value.REFCELL = (n_value_cell)',
        '$ordinary_reference_value(S_value,n_value_cell) = (PINT 13)',
        '$config_generator_value(S_value,pconfiggenerator_first) = (PINT 13)',
        owners('S_value', 'HOBJECT n_generator', 2),
        'PhpStep: S_value ~> S_second_sent',
        'S_second_sent.TODO = (CONFIG_GENERATOR pconfiggenerator_second "next") :: ptask_value*',
        'pconfiggenerator_second = pconfiggenerator[.ITEMS = [ENTRY (KINT 0) (DIRECT PNULL),ENTRY (KINT 1) (DIRECT (PINT 13))]]',
    ] + public('S_value') + seek('S_second_sent', 1402, 'S_finish') + [
        'S_finish.TODO = (CONFIG_GENERATOR pconfiggenerator_second "finish") :: ptask_finish*',
        'S_finish.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
        'pgenerator_closed.PHASE = GENERATOR_CLOSED',
        'pgenerator_closed.FRAME = eps',
        'pgenerator_closed.REFCELL = (n_value_cell)',
        '$ordinary_reference_value(S_finish,n_value_cell) = (PINT 31)',
        '$node_children(S_finish,HOBJECT n_generator) = [HCELL n_value_cell]',
        '$config_generator_reference_storage(S_finish,pconfiggenerator_second)',
        '$config_generator_finish_allowed(S_finish,pconfiggenerator_second)',
        'S_finish.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_finish.PRECISIONINI = $ptascii("19")',
        owners('S_finish', 'HOBJECT n_generator', 2),
        owners('S_finish', 'HCELL n_value_cell', 1),
    ] + public('S_finish') + budget('S_finish', 'S_data_budget') + seek('S_finish', 1403, 'S_input') + [
        'S_input.TODO = (CONFIG_GENERATOR pconfiggenerator_second "input-release") :: ptask_input*',
        '$config_generator_nodes(pconfiggenerator_second,"input-release") = $config_generator_input_nodes(pconfiggenerator_second) ++ $config_nodes(pconfiggenerator_second.CALL)',
        '$config_generator_valid(S_input,pconfiggenerator_second,"input-release")',
        '$ordinary_reference_value(S_input,n_value_cell) = (PINT 31)',
        '~$generator_storage_active(S_input,n_generator)',
        owners('S_input', 'HOBJECT n_generator', 1),
        owners('S_input', 'HCELL n_value_cell', 1),
        'S_owning = S_input[.STORE[n_value_cell] = DEFINED (POBJECT n_callee)]',
        '~$config_generator_finish_allowed(S_owning,pconfiggenerator_second)',
        'S_debt = S_input[.LITERALREFDEBTS = [n_value_cell]]',
        '~$config_generator_finish_allowed(S_debt,pconfiggenerator_second)',
    ] + public('S_input') + budget('S_input', 'S_input_budget') + seek('S_input', 1404, 'S_slot1') + [
        'S_slot1.TODO = (GENERATOR_STORAGE_STEP pgenstorage_slot1) :: ptask_slot1*',
        'pgenstorage_slot1.OBJECT = n_generator',
        '$generator_storage_valid(S_slot1,pgenstorage_slot1)',
        '$ordinary_reference_value(S_slot1,n_value_cell) = (PINT 31)',
        '$weakref_get(S_slot1,n_watch) = POBJECT n_generator',
        owners('S_slot1', 'HOBJECT n_generator', 1),
        owners('S_slot1', 'HCELL n_value_cell', 1),
    ] + public('S_slot1') + seek('S_slot1', 1405, 'S_slot2') + [
        'S_slot2.TODO = (GENERATOR_STORAGE_STEP pgenstorage_slot2) :: ptask_slot2*',
        'pgenstorage_slot2.OBJECT = n_generator',
        '$generator_storage_valid(S_slot2,pgenstorage_slot2)',
        '~((HCELL n_value_cell) <- S_slot2.ALLOCATIONS)',
        '$ordinary_reference_value(S_slot2,n_value_cell) = eps',
        '$node_children(S_slot2,HOBJECT n_generator) = eps',
        '(HOBJECT n_generator) <- S_slot2.ALLOCATIONS',
        '$weakref_get(S_slot2,n_watch) = POBJECT n_generator',
        owners('S_slot2', 'HOBJECT n_generator', 1),
    ] + public('S_slot2') + seek('S_slot2', 1406, 'S_retired') + [
        'S_retired.TODO = (CONFIG_GENERATOR pconfiggenerator_second "storage-released") :: ptask_retired*',
        '~((HOBJECT n_generator) <- S_retired.ALLOCATIONS)',
        '~((HCELL n_value_cell) <- S_retired.ALLOCATIONS)',
        '$config_generator_retired_scope(S_retired,pconfiggenerator_second)',
        '$weakref_get(S_retired,n_watch) = PNULL',
        '$config_generator_valid(S_retired,pconfiggenerator_second,"storage-released")',
    ] + public('S_retired') + seek('S_retired', 1407, 'S_invoke') + [
        'S_invoke.TODO = (CONFIG_GENERATOR pconfiggenerator_second "invoke") :: ptask_invoke*',
        '$config_pack_prefix(pconfiggenerator_second.CALL,pconfiggenerator_second.ITEMS,false) = (pconfigcall_prefix)',
        'pconfigcall = pconfigcall_prefix[.INDEX = 1]',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (PINT 13))]',
        '$config_selected_valid(S_invoke,pconfigcall)',
    ] + public('S_invoke') + seek('S_invoke', 1408, 'S_handler') + [
        'S_handler.CURRENT = (pcallcontext_handler)',
        '$error_context_call(S_handler,pcallcontext_handler) = (perrorcall)',
        'perrorcall.RESUME = CONFIG_INI_NULL_RESULT pconfigcall',
        '$weakref_get(S_handler,n_watch) = PNULL',
        '~((HOBJECT n_generator) <- S_handler.ALLOCATIONS)',
        '~((HCELL n_value_cell) <- S_handler.ALLOCATIONS)',
        'S_handler.STORE[n_result_cell] = DEFINED (PINT 99)',
    ] + public('S_handler') + seek('S_handler', 1409, 'S_null') + [
        'S_null.TODO = (CONFIG_INI_NULL_RESULT pconfigcall) :: ptask_null*',
        '$config_ini_null_valid(S_null,pconfigcall)',
        'S_null.STORE[n_result_cell] = DEFINED (PINT 99)',
    ] + public('S_null') + seek('S_null', 1410, 'S_return') + [
        'S_return.STORE[n_result_cell] = DEFINED (PBOOL false)',
        'S_return.PRECISIONINI = $ptascii("19")',
        '$weakref_get(S_return,n_watch) = PNULL',
    ] + public('S_return')
    return checks + finish('S_return', stdout, ['HOBJECT n_generator', 'HCELL n_value_cell'])


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(SOURCES, conditions, HELPERS, model_timeout=300,
        extra_inputs=(Path(__file__),
                      Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
