#!/usr/bin/env python3
"""An outside aliased cell keeps the changed ARRAY after Generator retirement."""
from pathlib import Path
from types import SimpleNamespace

import config_generator_reference_owning_alias_review_cases as cases
import list_missing_warning_protocol as shared
from array_generator_unpack_state_review import finish, initial, owners, public, seek

NAME = 'config-generator-reference-owning-alias-array-cow-typeerror'
SOURCES = SimpleNamespace(CASES={NAME: cases.CASES[NAME]}, __file__=cases.__file__)
HELPERS = shared.HELPERS + r'''
dec $a84_peer_echo(pstate, ptbytes) : bool
def $a84_peer_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $a84_peer_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 8400) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask*
  -- if pconfiggenerator.ITEMS = eps
def $list_warning_frontier(S, 8401) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask*
  -- if |pconfiggenerator.ITEMS| = 1
def $list_warning_frontier(S, 8402) = $a84_peer_echo(S, $ptascii("C:"))
def $list_warning_frontier(S, 8403) = $a84_peer_echo(S, $ptascii("T;"))
def $list_warning_frontier(S, 8404) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "finish") :: ptask*
  -- if |pconfiggenerator.ITEMS| = 2
def $list_warning_frontier(S, 8405) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "invoke") :: ptask*
  -- if |pconfiggenerator.ITEMS| = 2
def $list_warning_frontier(S, 8406) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_GENERATOR pconfiggenerator "invoke") :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 8407) = $a84_peer_echo(S, $ptascii("E:"))
def $list_warning_frontier(S, 8408) = $a84_peer_echo(S, $ptascii("L:"))
def $list_warning_frontier(S, 8409) = $a84_peer_echo(S, $ptascii("G:"))
def $list_warning_frontier(S, 8410) = $a84_peer_echo(S, $ptascii("A:"))
def $list_warning_frontier(S, 8411) = $a84_peer_echo(S, $ptascii("U:"))
def $list_warning_frontier(S, 8412) = $a84_peer_echo(S, $ptascii("R:"))
'''


def cell(state, name, identifier):
    return f'$lookup($global_table_view({state}).ENV,$ptascii("{name}")) = ({identifier})'


def row(state, array, value, marker):
    return (f'{state}.ARRAYS[{array}].ITEMS = '
            f'[ENTRY (KINT 0) (DIRECT (PINT {value})), '
            f'ENTRY (KINT 1) (DIRECT (POBJECT {marker}))]')


def watch(state, name, cell_id, watch_id, value):
    return [cell(state, name, cell_id),
            f'{state}.STORE[{cell_id}] = DEFINED (POBJECT {watch_id})',
            f'$weakref_get({state},{watch_id}) = {value}']


def conditions(name, program, path, stdout):
    assert name == NAME
    checks = initial(program, path) + seek('S_initial', 8400, 'S_option') + [
        'S_option.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask_option*',
        'pconfiggenerator.OBJECT = n_generator',
        'pconfiggenerator.INPUT = VARIABLE ($ptascii("gen")) z_input',
        'pconfiggenerator.PRODUCER = eps',
        'pconfiggenerator.CALL.OWNER = eps',
        '$config_generator_reference_owning_source(S_option,pconfiggenerator)',
        'S_option.OBJECTS[n_generator] = GENERATOR pgenerator_option',
        'pgenerator_option.REFCELL = (n_optionref)',
        'pgenerator_option.VALUE = eps',
        'pgenerator_option.KEY = (PINT 0)',
        '$generator_reference_producer(S_option,pgenerator_option)',
        '$ordinary_reference_value(S_option,n_optionref) = (pvalue_option)',
        '$string_bytes(pvalue_option) = ($ptascii("precision"))',
        '$config_generator_value(S_option,pconfiggenerator) = (pvalue_option)',
    ] + watch('S_option', 'genWatch', 'n_genwatch_cell', 'n_genwatch',
              'POBJECT n_generator') + [
        owners('S_option', 'HOBJECT n_generator', 2),
        'PhpStep: S_option ~> S_first_sent',
        'S_first_sent.TODO = (CONFIG_GENERATOR pconfiggenerator_first "next") :: ptask_option*',
        'pconfiggenerator_first = pconfiggenerator[.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_option)]]',
        '$config_generator_history(S_first_sent,pconfiggenerator_first)',
    ] + public('S_option') + public('S_first_sent') + seek('S_first_sent', 8401, 'S_value') + [
        'S_value.TODO = (CONFIG_GENERATOR pconfiggenerator_first "ready") :: ptask_value*',
        'S_value.OBJECTS[n_generator] = GENERATOR pgenerator_value',
        'pgenerator_value.REFCELL = (n_payloadref)',
        'n_payloadref =/= n_optionref',
        'pgenerator_value.VALUE = eps',
        'pgenerator_value.KEY = (PINT 1)',
        '$ordinary_reference_value(S_value,n_payloadref) = (PARRAY n_old)',
        cell('S_value', 'slot', 'n_payloadref'),
        cell('S_value', 'alias', 'n_payloadref'),
        row('S_value', 'n_old', 13, 'n_oldmarker'),
        '$config_generator_value(S_value,pconfiggenerator_first) = (PARRAY n_old)',
        '$config_iterator_argument(S_value,PARRAY n_old)',
        '$heap_count(HARRAY n_old,$pools_nodes(S_value.POOLS)) = 0',
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
        '$config_generator_reference_owning_last(S_second_sent,pconfiggenerator_second,PARRAY n_old)',
        '$config_generator_reference_owning_last_items(S_second_sent,pconfiggenerator_second)',
        '$config_generator_history(S_second_sent,pconfiggenerator_second)',
        '$task_nodes(CONFIG_GENERATOR pconfiggenerator_second "next") = [HOBJECT n_generator,HARRAY n_old]',
        owners('S_second_sent', 'HARRAY n_old', 2),
    ] + public('S_value') + public('S_second_sent') + seek('S_second_sent', 8402, 'S_mutated') + [
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
              'POBJECT n_newmarker') + public('S_mutated') + seek('S_mutated', 8403, 'S_terminal') + [
        '$ordinary_reference_value(S_terminal,n_payloadref) = (PARRAY n_new)',
        row('S_terminal', 'n_old', 13, 'n_oldmarker'),
        row('S_terminal', 'n_new', 31, 'n_newmarker'),
        'S_terminal.PRECISIONINI = $ptascii("6")',
        '$weakref_get(S_terminal,n_oldwatch) = POBJECT n_oldmarker',
        '$weakref_get(S_terminal,n_newwatch) = POBJECT n_newmarker',
    ] + public('S_terminal') + seek('S_terminal', 8404, 'S_finish') + [
        'S_finish.TODO = (CONFIG_GENERATOR pconfiggenerator_second "finish") :: ptask_finish*',
        'S_finish.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
        'pgenerator_closed.PHASE = GENERATOR_CLOSED',
        'pgenerator_closed.FRAME = eps',
        'pgenerator_closed.VALUE = eps',
        'pgenerator_closed.REFCELL = (n_payloadref)',
        'pgenerator_closed.KEY = (PINT 1)',
        '$ordinary_reference_value(S_finish,n_payloadref) = (PARRAY n_new)',
        cell('S_finish', 'slot', 'n_payloadref'),
        cell('S_finish', 'alias', 'n_payloadref'),
        '$node_children(S_finish,HOBJECT n_generator) = [HCELL n_payloadref]',
        '$node_children(S_finish,HCELL n_payloadref) = [HARRAY n_new]',
        row('S_finish', 'n_old', 13, 'n_oldmarker'),
        row('S_finish', 'n_new', 31, 'n_newmarker'),
        '$config_generator_reference_owning_last_items(S_finish,pconfiggenerator_second)',
        '~$config_generator_reference_storage(S_finish,pconfiggenerator_second)',
        '$config_generator_reference_owning_live_storage(S_finish,pconfiggenerator_second)',
        '$config_generator_finish_allowed(S_finish,pconfiggenerator_second)',
        '~$config_generator_owning_input(pconfiggenerator_second)',
        owners('S_finish', 'HOBJECT n_generator', 2),
        owners('S_finish', 'HCELL n_payloadref', 3),
        owners('S_finish', 'HARRAY n_old', 1),
        owners('S_finish', 'HARRAY n_new', 1),
        owners('S_finish', 'HOBJECT n_oldmarker', 1),
        owners('S_finish', 'HOBJECT n_newmarker', 1),
        cell('S_finish', 'gen', 'n_gen_cell'),
        'S_finish.STORE[n_gen_cell] = DEFINED (POBJECT n_generator)',
        cell('S_finish', 'saved', 'n_saved_cell'),
        'S_finish.STORE[n_saved_cell] = DEFINED (POBJECT n_saved)',
        'S_no_cv = S_finish[.STORE[n_gen_cell] = DEFINED PNULL][.HELD = S_finish.HELD ++ [HOBJECT n_generator]]',
        '$config_generator_reference_history(S_no_cv,pconfiggenerator_second)',
        '$heap_owners($heap_graph(S_no_cv), HOBJECT n_generator) = 2',
        '~$config_generator_reference_owning_live_storage(S_no_cv,pconfiggenerator_second)',
        '~$config_generator_finish_allowed(S_no_cv,pconfiggenerator_second)',
        'S_no_cv_popped = S_no_cv[.TODO = (THROW_SEARCH n_saved) :: ptask_finish*]',
        '~$config_generator_discard_allowed(S_no_cv_popped,pconfiggenerator_second)',
    ] + public('S_finish') + seek('S_finish', 8405, 'S_invoke') + [
        'S_invoke.TODO = (CONFIG_GENERATOR pconfiggenerator_second "invoke") :: ptask_finish*',
        '$config_generator_valid(S_invoke,pconfiggenerator_second,"invoke")',
        '$config_generator_reference_owning_live_storage(S_invoke,pconfiggenerator_second)',
        '$ordinary_reference_value(S_invoke,n_payloadref) = (PARRAY n_new)',
        '$weakref_get(S_invoke,n_genwatch) = POBJECT n_generator',
        '$weakref_get(S_invoke,n_oldwatch) = POBJECT n_oldmarker',
        '$weakref_get(S_invoke,n_newwatch) = POBJECT n_newmarker',
        row('S_invoke', 'n_old', 13, 'n_oldmarker'),
        row('S_invoke', 'n_new', 31, 'n_newmarker'),
        owners('S_invoke', 'HOBJECT n_generator', 1),
        owners('S_invoke', 'HCELL n_payloadref', 3),
        owners('S_invoke', 'HARRAY n_old', 1),
        owners('S_invoke', 'HARRAY n_new', 1),
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
        row('S_error', 'n_old', 13, 'n_oldmarker'),
        row('S_error', 'n_new', 31, 'n_newmarker'),
        '$weakref_get(S_error,n_oldwatch) = POBJECT n_oldmarker',
        '$weakref_get(S_error,n_newwatch) = POBJECT n_newmarker',
    ] + public('S_invoke') + seek('S_invoke', 8406, 'S_throw') + [
        'S_throw.TODO = (THROW_SEARCH n_error) :: (CONFIG_GENERATOR pconfiggenerator_second "invoke") :: ptask_throw*',
        'S_popped = S_throw[.TODO = (THROW_SEARCH n_error) :: ptask_throw*]',
        '$config_generator_reference_owning_live_storage(S_popped,pconfiggenerator_second)',
        '$config_generator_discard_allowed(S_popped,pconfiggenerator_second)',
        owners('S_popped', 'HOBJECT n_generator', 1),
        owners('S_popped', 'HCELL n_payloadref', 3),
        'S_raw = $config_generator_discard(S_popped,pconfiggenerator_second,"invoke")',
        'PhpStep: S_throw ~> S_raw',
        'S_raw.TODO = (THROW_SEARCH n_error) :: ptask_throw*',
        '~$generator_storage_active(S_raw,n_generator)',
        '(HOBJECT n_generator) <- S_raw.ALLOCATIONS',
        owners('S_raw', 'HCELL n_payloadref', 3),
    ] + public('S_throw') + public('S_raw') + seek('S_raw', 8407, 'S_catch') + [
        cell('S_catch', 'error', 'n_error_cell'),
        'S_catch.STORE[n_error_cell] = DEFINED (POBJECT n_error)',
        '$ordinary_reference_value(S_catch,n_payloadref) = (PARRAY n_new)',
        cell('S_catch', 'slot', 'n_payloadref'),
        cell('S_catch', 'alias', 'n_payloadref'),
        row('S_catch', 'n_old', 13, 'n_oldmarker'),
        row('S_catch', 'n_new', 31, 'n_newmarker'),
        '$weakref_get(S_catch,n_oldwatch) = POBJECT n_oldmarker',
        '$weakref_get(S_catch,n_newwatch) = POBJECT n_newmarker',
        '$weakref_get(S_catch,n_genwatch) = POBJECT n_generator',
        cell('S_catch', 'result', 'n_result_cell'),
        'S_catch.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_catch.PRECISIONINI = $ptascii("6")',
        owners('S_catch', 'HOBJECT n_generator', 1),
        owners('S_catch', 'HCELL n_payloadref', 3),
    ] + public('S_catch') + seek('S_catch', 8408, 'S_later') + [
        '$weakref_get(S_later,n_oldwatch) = PNULL',
        '$weakref_get(S_later,n_newwatch) = POBJECT n_newmarker',
        '$weakref_get(S_later,n_genwatch) = POBJECT n_generator',
        '~((HARRAY n_old) <- S_later.ALLOCATIONS)',
        '~((HOBJECT n_oldmarker) <- S_later.ALLOCATIONS)',
        '(HARRAY n_new) <- S_later.ALLOCATIONS',
        '(HOBJECT n_newmarker) <- S_later.ALLOCATIONS',
        '$ordinary_reference_value(S_later,n_payloadref) = (PARRAY n_new)',
        cell('S_later', 'slot', 'n_payloadref'),
        cell('S_later', 'alias', 'n_payloadref'),
        owners('S_later', 'HOBJECT n_generator', 1),
        owners('S_later', 'HCELL n_payloadref', 3),
        owners('S_later', 'HARRAY n_new', 1),
        '~$destructor_operational(S_later)',
    ] + public('S_later') + seek('S_later', 8409, 'S_unset_gen') + [
        '~((HOBJECT n_generator) <- S_unset_gen.ALLOCATIONS)',
        '(HCELL n_payloadref) <- S_unset_gen.ALLOCATIONS',
        '(HARRAY n_new) <- S_unset_gen.ALLOCATIONS',
        '(HOBJECT n_newmarker) <- S_unset_gen.ALLOCATIONS',
        '$weakref_get(S_unset_gen,n_genwatch) = PNULL',
        '$weakref_get(S_unset_gen,n_oldwatch) = PNULL',
        '$weakref_get(S_unset_gen,n_newwatch) = POBJECT n_newmarker',
        '$ordinary_reference_value(S_unset_gen,n_payloadref) = (PARRAY n_new)',
        cell('S_unset_gen', 'slot', 'n_payloadref'),
        cell('S_unset_gen', 'alias', 'n_payloadref'),
        owners('S_unset_gen', 'HCELL n_payloadref', 2),
        owners('S_unset_gen', 'HARRAY n_new', 1),
    ] + public('S_unset_gen') + seek('S_unset_gen', 8410, 'S_unset_slot') + [
        '$lookup($global_table_view(S_unset_slot).ENV,$ptascii("slot")) = eps',
        cell('S_unset_slot', 'alias', 'n_payloadref'),
        '$ordinary_reference_value(S_unset_slot,n_payloadref) = (PARRAY n_new)',
        '$weakref_get(S_unset_slot,n_newwatch) = POBJECT n_newmarker',
        owners('S_unset_slot', 'HCELL n_payloadref', 1),
        owners('S_unset_slot', 'HARRAY n_new', 1),
    ] + public('S_unset_slot') + seek('S_unset_slot', 8411, 'S_unset_alias') + [
        '$lookup($global_table_view(S_unset_alias).ENV,$ptascii("alias")) = eps',
        '~((HCELL n_payloadref) <- S_unset_alias.ALLOCATIONS)',
        '~((HARRAY n_new) <- S_unset_alias.ALLOCATIONS)',
        '~((HOBJECT n_newmarker) <- S_unset_alias.ALLOCATIONS)',
        '$weakref_get(S_unset_alias,n_newwatch) = PNULL',
    ] + public('S_unset_alias') + seek('S_unset_alias', 8412, 'S_recovery') + [
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
