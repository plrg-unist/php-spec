#!/usr/bin/env python3
"""A final copied reference ARRAY keeps 13 after its shared cell changes."""
from pathlib import Path
from types import SimpleNamespace

import config_generator_reference_owning_cache_review_cases as cases
import list_missing_warning_protocol as shared
from array_generator_unpack_state_review import finish, initial, owners, public, seek

NAME = 'config-generator-reference-owning-cache-array-cow-typeerror'
SOURCES = SimpleNamespace(CASES={NAME: cases.CASES[NAME]}, __file__=cases.__file__)
HELPERS = shared.HELPERS + r'''
dec $a82_peer_echo(pstate, ptbytes) : bool
def $a82_peer_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $a82_peer_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 2700) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask*
  -- if pconfiggenerator.ITEMS = eps
def $list_warning_frontier(S, 2701) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask*
  -- if |pconfiggenerator.ITEMS| = 1
def $list_warning_frontier(S, 2702) = $a82_peer_echo(S, $ptascii("C:"))
def $list_warning_frontier(S, 2703) = $a82_peer_echo(S, $ptascii("T;"))
def $list_warning_frontier(S, 2704) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "finish") :: ptask*
  -- if |pconfiggenerator.ITEMS| = 2
def $list_warning_frontier(S, 2705) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "invoke") :: ptask*
  -- if |pconfiggenerator.ITEMS| = 2
def $list_warning_frontier(S, 2706) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_GENERATOR pconfiggenerator "invoke") :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 2707) = $a82_peer_echo(S, $ptascii("E:"))
def $list_warning_frontier(S, 2708) = $a82_peer_echo(S, $ptascii("V:"))
def $list_warning_frontier(S, 2709) = $a82_peer_echo(S, $ptascii("R:"))
'''


def cell(state, name, identifier):
    return f'$lookup($global_table_view({state}).ENV,$ptascii("{name}")) = ({identifier})'


def row(state, array, value):
    return f'{state}.ARRAYS[{array}].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT {value}))]'


def conditions(name, program, path, stdout):
    assert name == NAME
    checks = initial(program, path) + seek('S_initial', 2700, 'S_option') + [
        'S_option.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask_option*',
        'pconfiggenerator.OBJECT = n_generator',
        'pconfiggenerator.INPUT = VARIABLE ($ptascii("gen")) z_input',
        'pconfiggenerator.PRODUCER = eps',
        'pconfiggenerator.CALL.OWNER = eps',
        '$config_generator_reference_owning_source(S_option,pconfiggenerator)',
        'S_option.OBJECTS[n_generator] = GENERATOR pgenerator_option',
        'pgenerator_option.REFCELL = (n_slot)',
        'pgenerator_option.VALUE = eps',
        'pgenerator_option.KEY = (PINT 0)',
        '$generator_reference_producer(S_option,pgenerator_option)',
        cell('S_option', 'slot', 'n_slot'),
        cell('S_option', 'alias', 'n_slot'),
        'n_slot <- S_option.REFCELLS',
        '(HCELL n_slot) <- S_option.ALLOCATIONS',
        '$ordinary_reference_value(S_option,n_slot) = (pvalue_option)',
        '$string_bytes(pvalue_option) = ($ptascii("precision"))',
        '$config_generator_value(S_option,pconfiggenerator) = (pvalue_option)',
        cell('S_option', 'genWatch', 'n_genwatch_cell'),
        'S_option.STORE[n_genwatch_cell] = DEFINED (POBJECT n_genwatch)',
        '$weakref_get(S_option,n_genwatch) = POBJECT n_generator',
        owners('S_option', 'HOBJECT n_generator', 2),
        'PhpStep: S_option ~> S_first_sent',
        'S_first_sent.TODO = (CONFIG_GENERATOR pconfiggenerator_first "next") :: ptask_option*',
        'pconfiggenerator_first = pconfiggenerator[.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_option)]]',
        '$config_generator_history(S_first_sent,pconfiggenerator_first)',
    ] + public('S_option') + public('S_first_sent') + seek('S_first_sent', 2701, 'S_value') + [
        'S_value.TODO = (CONFIG_GENERATOR pconfiggenerator_first "ready") :: ptask_value*',
        'S_value.OBJECTS[n_generator] = GENERATOR pgenerator_value',
        'pgenerator_value.REFCELL = (n_slot)',
        'pgenerator_value.VALUE = eps',
        'pgenerator_value.KEY = (PINT 1)',
        cell('S_value', 'slot', 'n_slot'),
        cell('S_value', 'alias', 'n_slot'),
        '$ordinary_reference_value(S_value,n_slot) = (PARRAY n_old)',
        row('S_value', 'n_old', 13),
        '$config_generator_value(S_value,pconfiggenerator_first) = (PARRAY n_old)',
        '$config_iterator_argument(S_value,PARRAY n_old)',
        '$heap_count(HARRAY n_old,$pools_nodes(S_value.POOLS)) = 0',
        owners('S_value', 'HOBJECT n_generator', 2),
        owners('S_value', 'HARRAY n_old', 1),
        'S_debt = S_value[.LITERALREFDEBTS = [n_slot]]',
        '$config_generator_value(S_debt,pconfiggenerator_first) = eps',
        'PhpStep: S_value ~> S_second_sent',
        'S_second_sent.TODO = (CONFIG_GENERATOR pconfiggenerator_second "next") :: ptask_value*',
        'pconfiggenerator_second = pconfiggenerator[.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_option),ENTRY (KINT 1) (DIRECT (PARRAY n_old))]]',
        '$config_generator_reference_owning_last(S_second_sent,pconfiggenerator_second,PARRAY n_old)',
        '$config_generator_reference_owning_last_items(S_second_sent,pconfiggenerator_second)',
        '$config_generator_history(S_second_sent,pconfiggenerator_second)',
        '$task_nodes(CONFIG_GENERATOR pconfiggenerator_second "next") = [HOBJECT n_generator,HARRAY n_old]',
        owners('S_second_sent', 'HARRAY n_old', 2),
    ] + public('S_value') + public('S_second_sent') + seek('S_second_sent', 2702, 'S_mutated') + [
        cell('S_mutated', 'slot', 'n_slot'),
        cell('S_mutated', 'alias', 'n_slot'),
        'S_mutated.STORE[n_slot] = DEFINED (PARRAY n_new)',
        'n_new =/= n_old',
        row('S_mutated', 'n_old', 13),
        row('S_mutated', 'n_new', 31),
        '$node_children(S_mutated,HCELL n_slot) = [HARRAY n_new]',
        owners('S_mutated', 'HARRAY n_old', 1),
        owners('S_mutated', 'HARRAY n_new', 1),
    ] + public('S_mutated') + seek('S_mutated', 2703, 'S_terminal') + [
        cell('S_terminal', 'slot', 'n_slot'),
        cell('S_terminal', 'alias', 'n_slot'),
        '$ordinary_reference_value(S_terminal,n_slot) = (PINT 9)',
        row('S_terminal', 'n_old', 13),
        '~((HARRAY n_new) <- S_terminal.ALLOCATIONS)',
        'S_terminal.PRECISIONINI = $ptascii("6")',
    ] + public('S_terminal') + seek('S_terminal', 2704, 'S_finish') + [
        'S_finish.TODO = (CONFIG_GENERATOR pconfiggenerator_second "finish") :: ptask_finish*',
        'S_finish.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
        'pgenerator_closed.PHASE = GENERATOR_CLOSED',
        'pgenerator_closed.FRAME = eps',
        'pgenerator_closed.VALUE = eps',
        'pgenerator_closed.REFCELL = (n_slot)',
        'pgenerator_closed.KEY = (PINT 1)',
        '$ordinary_reference_value(S_finish,n_slot) = (PINT 9)',
        '$node_children(S_finish,HOBJECT n_generator) = [HCELL n_slot]',
        '$config_generator_reference_owning_last_items(S_finish,pconfiggenerator_second)',
        '$config_generator_reference_storage(S_finish,pconfiggenerator_second)',
        '$config_generator_finish_allowed(S_finish,pconfiggenerator_second)',
        '~$config_generator_owning_input(pconfiggenerator_second)',
        row('S_finish', 'n_old', 13),
        owners('S_finish', 'HOBJECT n_generator', 2),
        owners('S_finish', 'HCELL n_slot', 3),
        owners('S_finish', 'HARRAY n_old', 1),
        'S_unclean = S_finish[.STORE[n_slot] = DEFINED (PARRAY n_old)]',
        '$config_generator_history(S_unclean,pconfiggenerator_second)',
        '$config_generator_owning_items_live(S_unclean,pconfiggenerator_second.ITEMS)',
        '~$config_generator_reference_storage(S_unclean,pconfiggenerator_second)',
        '~$config_generator_finish_allowed(S_unclean,pconfiggenerator_second)',
        cell('S_finish', 'saved', 'n_saved_cell'),
        'S_finish.STORE[n_saved_cell] = DEFINED (POBJECT n_saved)',
        'S_unclean_popped = S_unclean[.TODO = (THROW_SEARCH n_saved) :: ptask_finish*]',
        '~$config_generator_discard_allowed(S_unclean_popped,pconfiggenerator_second)',
    ] + public('S_finish') + seek('S_finish', 2705, 'S_invoke') + [
        'S_invoke.TODO = (CONFIG_GENERATOR pconfiggenerator_second "invoke") :: ptask_finish*',
        '(HOBJECT n_generator) <- S_invoke.ALLOCATIONS',
        '(HCELL n_slot) <- S_invoke.ALLOCATIONS',
        '$config_generator_valid(S_invoke,pconfiggenerator_second,"invoke")',
        '$config_generator_reference_storage(S_invoke,pconfiggenerator_second)',
        '$ordinary_reference_value(S_invoke,n_slot) = (PINT 9)',
        '$weakref_get(S_invoke,n_genwatch) = POBJECT n_generator',
        row('S_invoke', 'n_old', 13),
        owners('S_invoke', 'HOBJECT n_generator', 1),
        owners('S_invoke', 'HARRAY n_old', 1),
        '$task_nodes(CONFIG_GENERATOR pconfiggenerator_second "invoke") = [HARRAY n_old]',
        '$config_pack_prefix(pconfiggenerator_second.CALL,pconfiggenerator_second.ITEMS,false) = (pconfigcall_prefix)',
        'pconfigcall_prefix.SENT = [NAMED_SENT (KNOWN pvalue_option),NAMED_SENT (KNOWN (PARRAY n_old))]',
        'PhpStep: S_invoke ~> S_error',
        'S_error.COMPLETION = THROWING n_error',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
        'S_error.ARRAYS[n_trace].ITEMS[0] = ENTRY (KINT 0) (DIRECT (PARRAY n_frame))',
        '$trace_array_field(S_error,n_frame,$ptascii("args")) = PARRAY n_args',
        'S_error.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_trace_option),ENTRY (KINT 1) (DIRECT (PARRAY n_old))]',
        '$string_bytes(pvalue_trace_option) = ($ptascii("precision"))',
        row('S_error', 'n_old', 13),
    ] + public('S_invoke') + seek('S_invoke', 2706, 'S_throw') + [
        'S_throw.TODO = (THROW_SEARCH n_error) :: (CONFIG_GENERATOR pconfiggenerator_second "invoke") :: ptask_throw*',
        'S_popped = S_throw[.TODO = (THROW_SEARCH n_error) :: ptask_throw*]',
        '$config_generator_reference_storage(S_popped,pconfiggenerator_second)',
        '$config_generator_discard_allowed(S_popped,pconfiggenerator_second)',
        'S_raw = $config_generator_discard(S_popped,pconfiggenerator_second,"invoke")',
        'PhpStep: S_throw ~> S_raw',
        'S_raw.TODO = (THROW_SEARCH n_error) :: ptask_throw*',
    ] + public('S_throw') + public('S_raw') + seek('S_raw', 2707, 'S_catch') + [
        cell('S_catch', 'error', 'n_error_cell'),
        'S_catch.STORE[n_error_cell] = DEFINED (POBJECT n_error)',
        cell('S_catch', 'slot', 'n_slot'),
        cell('S_catch', 'alias', 'n_slot'),
        '$ordinary_reference_value(S_catch,n_slot) = (PINT 9)',
        row('S_catch', 'n_old', 13),
        '$weakref_get(S_catch,n_genwatch) = POBJECT n_generator',
        cell('S_catch', 'result', 'n_result_cell'),
        'S_catch.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_catch.PRECISIONINI = $ptascii("6")',
        owners('S_catch', 'HOBJECT n_generator', 1),
    ] + public('S_catch') + seek('S_catch', 2708, 'S_unset_gen') + [
        '~((HOBJECT n_generator) <- S_unset_gen.ALLOCATIONS)',
        '$weakref_get(S_unset_gen,n_genwatch) = PNULL',
        '(HCELL n_slot) <- S_unset_gen.ALLOCATIONS',
        '$ordinary_reference_value(S_unset_gen,n_slot) = (PINT 9)',
        cell('S_unset_gen', 'slot', 'n_slot'),
        cell('S_unset_gen', 'alias', 'n_slot'),
        '~((HARRAY n_old) <- S_unset_gen.ALLOCATIONS)',
    ] + public('S_unset_gen') + seek('S_unset_gen', 2709, 'S_recovery') + [
        '$ordinary_reference_value(S_recovery,n_slot) = (PINT 9)',
        'S_recovery.PRECISIONINI = $ptascii("6")',
    ] + public('S_recovery')
    return checks + finish('S_recovery', stdout, [
        'HOBJECT n_generator', 'HCELL n_slot', 'HARRAY n_old',
        'HARRAY n_new', 'HOBJECT n_error'])


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(SOURCES, conditions, HELPERS, model_timeout=300,
        extra_inputs=(Path(__file__),
                      Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
