#!/usr/bin/env python3
"""Two copied arguments and one retained BYREF cache own the same object."""
from pathlib import Path
from types import SimpleNamespace

import config_generator_reference_two_owning_review_cases as cases
import list_missing_warning_protocol as shared
from array_generator_unpack_state_review import finish, initial, owners, public, seek

NAME = 'config-generator-reference-two-owning-shared-typeerror'
SOURCES = SimpleNamespace(CASES={NAME: cases.CASES[NAME]}, __file__=cases.__file__)
HELPERS = shared.HELPERS + r'''
dec $a93_peer_echo(pstate, ptbytes) : bool
def $a93_peer_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $a93_peer_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 9300) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask*
  -- if pconfiggenerator.ITEMS = eps
def $list_warning_frontier(S, 9301) = $a93_peer_echo(S, $ptascii("M0:"))
def $list_warning_frontier(S, 9302) = $a93_peer_echo(S, $ptascii("W0:"))
def $list_warning_frontier(S, 9303) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask*
  -- if |pconfiggenerator.ITEMS| = 1
def $list_warning_frontier(S, 9304) = $a93_peer_echo(S, $ptascii("T;"))
def $list_warning_frontier(S, 9305) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "finish") :: ptask*
  -- if |pconfiggenerator.ITEMS| = 2
def $list_warning_frontier(S, 9306) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "invoke") :: ptask*
  -- if |pconfiggenerator.ITEMS| = 2
def $list_warning_frontier(S, 9307) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_GENERATOR pconfiggenerator "invoke") :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 9308) = $a93_peer_echo(S, $ptascii("E:"))
def $list_warning_frontier(S, 9309) = $a93_peer_echo(S, $ptascii("U:"))
def $list_warning_frontier(S, 9310) = $a93_peer_echo(S, $ptascii("V:"))
def $list_warning_frontier(S, 9311) = $a93_peer_echo(S, $ptascii("R:"))
'''


def cell(state, name, identifier):
    return f'$lookup($global_table_view({state}).ENV,$ptascii("{name}")) = ({identifier})'


def watch(state, name, cell_id, watch_id, value):
    return [cell(state, name, cell_id),
            f'{state}.STORE[{cell_id}] = DEFINED (POBJECT {watch_id})',
            f'$weakref_get({state},{watch_id}) = {value}']


def conditions(name, program, path, stdout):
    assert name == NAME
    checks = initial(program, path) + seek('S_initial', 9300, 'S_first') + [
        'S_first.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask_first*',
        'pconfiggenerator.OBJECT = n_generator',
        'pconfiggenerator.INPUT = VARIABLE ($ptascii("gen")) z_input',
        'pconfiggenerator.PRODUCER = eps',
        'pconfiggenerator.CALL.OWNER = eps',
        'pconfiggenerator.CALL.KIND = INTRINSIC_INI_SET',
        '$config_generator_reference_owning_source(S_first,pconfiggenerator)',
        '$config_generator_input_nodes(pconfiggenerator) = eps',
        '~$config_generator_temporary_reference_input(S_first,pconfiggenerator)',
        '~$config_generator_factory_reference_input(S_first,pconfiggenerator)',
        '$config_generator_history(S_first,pconfiggenerator)',
        cell('S_first', 'gen', 'n_gen_cell'),
        'S_first.STORE[n_gen_cell] = DEFINED (POBJECT n_generator)',
        'S_first.OBJECTS[n_generator] = GENERATOR pgenerator_first',
        'pgenerator_first.VALUE = eps',
        'pgenerator_first.REFCELL = (n_firstref)',
        'pgenerator_first.KEY = (PINT 0)',
        '$generator_reference_producer(S_first,pgenerator_first)',
        '$ordinary_reference_value(S_first,n_firstref) = (POBJECT n_shared)',
        '$config_generator_value(S_first,pconfiggenerator) = (POBJECT n_shared)',
        '$config_iterator_argument(S_first,POBJECT n_shared)',
        owners('S_first', 'HOBJECT n_generator', 2),
        owners('S_first', 'HOBJECT n_shared', 1),
    ] + watch('S_first', 'genWatch', 'n_genwatch_cell', 'n_genwatch',
              'POBJECT n_generator') + watch('S_first', 'payloadWatch',
              'n_watch_cell', 'n_watch', 'POBJECT n_shared') + [
        'S_debt = S_first[.LITERALREFDEBTS = [n_firstref]]',
        '$config_generator_value(S_debt,pconfiggenerator) = eps',
        'PhpStep: S_first ~> S_sent_first',
        'S_sent_first.TODO = (CONFIG_GENERATOR pconfiggenerator_one "next") :: ptask_first*',
        'pconfiggenerator_one = pconfiggenerator[.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_shared))]]',
        '$config_generator_reference_owning_first(S_sent_first,pconfiggenerator_one,POBJECT n_shared)',
        '~$config_generator_reference_two_owning_items(S_sent_first,pconfiggenerator_one)',
        '$config_generator_history(S_sent_first,pconfiggenerator_one)',
        '$task_nodes(CONFIG_GENERATOR pconfiggenerator_one "next") = [HOBJECT n_generator,HOBJECT n_shared]',
        owners('S_sent_first', 'HOBJECT n_shared', 2),
        '$weakref_get(S_sent_first,n_genwatch) = POBJECT n_generator',
    ] + public('S_first') + public('S_sent_first') + seek('S_sent_first', 9301, 'S_mutated') + [
        '$ordinary_reference_value(S_mutated,n_firstref) = (POBJECT n_shared)',
        '$weakref_get(S_mutated,n_watch) = POBJECT n_shared',
        owners('S_mutated', 'HOBJECT n_shared', 2),
    ] + public('S_mutated') + seek('S_mutated', 9302, 'S_overwrite') + [
        '$ordinary_reference_value(S_overwrite,n_firstref) = (PINT 9)',
        '$weakref_get(S_overwrite,n_watch) = POBJECT n_shared',
        owners('S_overwrite', 'HOBJECT n_shared', 2),
    ] + public('S_overwrite') + seek('S_overwrite', 9303, 'S_second') + [
        'S_second.TODO = (CONFIG_GENERATOR pconfiggenerator_one "ready") :: ptask_second*',
        'S_second.OBJECTS[n_generator] = GENERATOR pgenerator_second',
        'pgenerator_second.VALUE = eps',
        'pgenerator_second.REFCELL = (n_lastref)',
        'pgenerator_second.KEY = (PINT 1)',
        'n_lastref =/= n_firstref',
        '$ordinary_reference_value(S_second,n_lastref) = (POBJECT n_shared)',
        '$config_generator_reference_owning_first(S_second,pconfiggenerator_one,POBJECT n_shared)',
        '$config_generator_value(S_second,pconfiggenerator_one) = (POBJECT n_shared)',
        '$config_generator_owning_items_live(S_second,pconfiggenerator_one.ITEMS)',
        owners('S_second', 'HOBJECT n_generator', 2),
        owners('S_second', 'HOBJECT n_shared', 2),
        'PhpStep: S_second ~> S_sent_second',
        'S_sent_second.TODO = (CONFIG_GENERATOR pconfiggenerator_two "next") :: ptask_second*',
        'pconfiggenerator_two = pconfiggenerator[.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_shared)),ENTRY (KINT 1) (DIRECT (POBJECT n_shared))]]',
        '$config_generator_reference_two_owning_items(S_sent_second,pconfiggenerator_two)',
        '$config_generator_reference_owning_last_items(S_sent_second,pconfiggenerator_two)',
        '$config_generator_history(S_sent_second,pconfiggenerator_two)',
        owners('S_sent_second', 'HOBJECT n_shared', 3),
    ] + public('S_second') + public('S_sent_second') + seek('S_sent_second', 9304, 'S_terminal') + [
        '$ordinary_reference_value(S_terminal,n_lastref) = (POBJECT n_shared)',
        '$weakref_get(S_terminal,n_genwatch) = POBJECT n_generator',
        '$weakref_get(S_terminal,n_watch) = POBJECT n_shared',
        'S_terminal.PRECISIONINI = $ptascii("6")',
    ] + public('S_terminal') + seek('S_terminal', 9305, 'S_finish') + [
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
        '$config_generator_reference_two_owning_items(S_finish,pconfiggenerator_two)',
        '$config_generator_reference_history(S_finish,pconfiggenerator_two)',
        '$config_generator_reference_owning_live_storage(S_finish,pconfiggenerator_two)',
        '$config_generator_finish_allowed(S_finish,pconfiggenerator_two)',
        '~$config_generator_temporary_reference_owning_last_items(S_finish,pconfiggenerator_two)',
        cell('S_finish', 'gen', 'n_gen_cell'),
        'S_finish.STORE[n_gen_cell] = DEFINED (POBJECT n_generator)',
        owners('S_finish', 'HOBJECT n_generator', 2),
        owners('S_finish', 'HCELL n_lastref', 1),
        owners('S_finish', 'HOBJECT n_shared', 3),
        '$weakref_get(S_finish,n_genwatch) = POBJECT n_generator',
        '$weakref_get(S_finish,n_watch) = POBJECT n_shared',
    ] + public('S_finish') + seek('S_finish', 9306, 'S_invoke') + [
        'S_invoke.TODO = (CONFIG_GENERATOR pconfiggenerator_two "invoke") :: ptask_invoke*',
        '$config_generator_valid(S_invoke,pconfiggenerator_two,"invoke")',
        '$config_generator_reference_owning_live_storage(S_invoke,pconfiggenerator_two)',
        '$ordinary_reference_value(S_invoke,n_lastref) = (POBJECT n_shared)',
        '$task_nodes(CONFIG_GENERATOR pconfiggenerator_two "invoke") = [HOBJECT n_shared,HOBJECT n_shared]',
        '$config_pack_prefix(pconfiggenerator_two.CALL,pconfiggenerator_two.ITEMS,false) = (pconfigcall_prefix)',
        'pconfigcall_prefix.SENT = [NAMED_SENT (KNOWN (POBJECT n_shared)),NAMED_SENT (KNOWN (POBJECT n_shared))]',
        owners('S_invoke', 'HOBJECT n_generator', 1),
        owners('S_invoke', 'HCELL n_lastref', 1),
        owners('S_invoke', 'HOBJECT n_shared', 3),
        '$weakref_get(S_invoke,n_genwatch) = POBJECT n_generator',
        '$weakref_get(S_invoke,n_watch) = POBJECT n_shared',
        'PhpStep: S_invoke ~> S_error',
        'S_error.COMPLETION = THROWING n_error',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
        'S_error.ARRAYS[n_trace].ITEMS[0] = ENTRY (KINT 0) (DIRECT (PARRAY n_frame))',
        '$trace_array_field(S_error,n_frame,$ptascii("args")) = PARRAY n_args',
        'S_error.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_shared)),ENTRY (KINT 1) (DIRECT (POBJECT n_shared))]',
        '$weakref_get(S_error,n_genwatch) = POBJECT n_generator',
        '$weakref_get(S_error,n_watch) = POBJECT n_shared',
    ] + public('S_invoke') + seek('S_invoke', 9307, 'S_throw') + [
        'S_throw.TODO = (THROW_SEARCH n_error) :: (CONFIG_GENERATOR pconfiggenerator_two "invoke") :: ptask_throw*',
        'S_popped = S_throw[.TODO = (THROW_SEARCH n_error) :: ptask_throw*]',
        '$config_generator_reference_two_owning_items(S_popped,pconfiggenerator_two)',
        '$config_generator_reference_owning_live_storage(S_popped,pconfiggenerator_two)',
        '$config_generator_discard_allowed(S_popped,pconfiggenerator_two)',
        owners('S_popped', 'HOBJECT n_generator', 1),
        owners('S_popped', 'HCELL n_lastref', 1),
        'S_raw = $config_generator_discard(S_popped,pconfiggenerator_two,"invoke")',
        'PhpStep: S_throw ~> S_raw',
        'S_raw.TODO = (THROW_SEARCH n_error) :: ptask_throw*',
        '$weakref_get(S_raw,n_genwatch) = POBJECT n_generator',
        '$weakref_get(S_raw,n_watch) = POBJECT n_shared',
    ] + public('S_throw') + public('S_raw') + seek('S_raw', 9308, 'S_catch') + [
        cell('S_catch', 'error', 'n_error_cell'),
        'S_catch.STORE[n_error_cell] = DEFINED (POBJECT n_error)',
        'S_catch.STORE[n_gen_cell] = DEFINED (POBJECT n_generator)',
        '$ordinary_reference_value(S_catch,n_lastref) = (POBJECT n_shared)',
        '$weakref_get(S_catch,n_genwatch) = POBJECT n_generator',
        '$weakref_get(S_catch,n_watch) = POBJECT n_shared',
        owners('S_catch', 'HOBJECT n_generator', 1),
        owners('S_catch', 'HCELL n_lastref', 1),
        owners('S_catch', 'HOBJECT n_shared', 3),
        cell('S_catch', 'result', 'n_result_cell'),
        'S_catch.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_catch.PRECISIONINI = $ptascii("6")',
    ] + public('S_catch') + seek('S_catch', 9309, 'S_later') + [
        '$weakref_get(S_later,n_genwatch) = POBJECT n_generator',
        '$weakref_get(S_later,n_watch) = POBJECT n_shared',
        '$ordinary_reference_value(S_later,n_lastref) = (POBJECT n_shared)',
        '(HOBJECT n_generator) <- S_later.ALLOCATIONS',
        '(HCELL n_lastref) <- S_later.ALLOCATIONS',
        '(HOBJECT n_shared) <- S_later.ALLOCATIONS',
        owners('S_later', 'HOBJECT n_generator', 1),
        owners('S_later', 'HCELL n_lastref', 1),
        owners('S_later', 'HOBJECT n_shared', 1),
        '~$destructor_operational(S_later)',
    ] + public('S_later') + seek('S_later', 9310, 'S_unset_gen') + [
        '~((HOBJECT n_generator) <- S_unset_gen.ALLOCATIONS)',
        '~((HCELL n_lastref) <- S_unset_gen.ALLOCATIONS)',
        '~((HOBJECT n_shared) <- S_unset_gen.ALLOCATIONS)',
        '$weakref_get(S_unset_gen,n_genwatch) = PNULL',
        '$weakref_get(S_unset_gen,n_watch) = PNULL',
    ] + public('S_unset_gen') + seek('S_unset_gen', 9311, 'S_recovery') + [
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
