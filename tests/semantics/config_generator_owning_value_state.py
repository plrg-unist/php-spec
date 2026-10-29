#!/usr/bin/env python3
"""A copied array option survives Generator cache replacement and reaches TypeError."""
from pathlib import Path
from types import SimpleNamespace

import config_generator_owning_value_cases as cases
import list_missing_warning_protocol as shared
from array_generator_unpack_state_review import budget, finish, initial, owners, public, seek


NAME = 'config-generator-owning-array-cow'
SOURCES = SimpleNamespace(CASES={NAME: cases.CASES[NAME]}, __file__=cases.__file__)
HELPERS = shared.HELPERS + r'''
dec $a77_echo(pstate, ptbytes) : bool
def $a77_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $a77_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 1600) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "next") :: ptask*
  -- if |pconfiggenerator.ITEMS| = 1
def $list_warning_frontier(S, 1601) = $a77_echo(S, $ptascii("F;"))
def $list_warning_frontier(S, 1602) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "finish") :: ptask*
def $list_warning_frontier(S, 1603) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "invoke") :: ptask*
def $list_warning_frontier(S, 1604) = $a77_echo(S, $ptascii("C:A:"))
def $list_warning_frontier(S, 1605) = $a77_echo(S, $ptascii("R:"))
'''


def cell(state, name, identifier):
    return f'$lookup($global_table_view({state}).ENV, $ptascii("{name}")) = ({identifier})'


def conditions(name, program, path, stdout):
    assert name == NAME
    checks = initial(program, path) + seek('S_initial', 1600, 'S_first') + [
        'S_first.TODO = (CONFIG_GENERATOR pconfiggenerator_first "next") :: ptask_first*',
        'pconfiggenerator_first.OBJECT = n_generator',
        'pconfiggenerator_first.INPUT = VARIABLE ($ptascii("gen")) z_input',
        'pconfiggenerator_first.PRODUCER = eps',
        'pconfiggenerator_first.ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_option))]',
        'S_first.ARRAYS[n_option].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 4))]',
        '$config_generator_owning_value_source(S_first,pconfiggenerator_first)',
        '$config_generator_history(S_first,pconfiggenerator_first)',
        '$config_generator_argument_nodes(pconfiggenerator_first) = [HARRAY n_option]',
        '$config_generator_owning_items_live(S_first,pconfiggenerator_first.ITEMS)',
        'pconfiggenerator_first.CALL.OWNER = eps',
        '$task_nodes(CONFIG_GENERATOR pconfiggenerator_first "next") = [HOBJECT n_generator,HARRAY n_option]',
        cell('S_first', 'gen', 'n_gen_cell'),
        'S_first.STORE[n_gen_cell] = DEFINED (POBJECT n_generator)',
        owners('S_first', 'HOBJECT n_generator', 2),
    ] + public('S_first') + budget('S_first', 'S_first_budget')
    checks += seek('S_first', 1601, 'S_terminal') + [
        'S_terminal.ARRAYS[n_option].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 4))]',
        '$lookup(S_terminal.ENV,$ptascii("array")) = (n_live_cell)',
        'S_terminal.STORE[n_live_cell] = DEFINED (PARRAY n_live)',
        'n_live =/= n_option',
        'S_terminal.ARRAYS[n_live].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 5))]',
        owners('S_terminal', 'HARRAY n_option', 1),
    ] + public('S_terminal') + seek('S_terminal', 1602, 'S_finish') + [
        'S_finish.TODO = (CONFIG_GENERATOR pconfiggenerator_finish "finish") :: ptask_finish*',
        'pconfiggenerator_finish.ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_option)),ENTRY (KINT 1) (DIRECT (PINT 7))]',
        'pconfiggenerator_finish.OBJECT = n_generator',
        'pconfiggenerator_finish.CALL.OWNER = eps',
        '$config_generator_owning_value_source(S_finish,pconfiggenerator_finish)',
        '$config_generator_valid(S_finish,pconfiggenerator_finish,"finish")',
        '$config_generator_argument_nodes(pconfiggenerator_finish) = [HARRAY n_option]',
        '$config_generator_owning_items_live(S_finish,pconfiggenerator_finish.ITEMS)',
        '$config_generator_finish_allowed(S_finish,pconfiggenerator_finish)',
        'S_finish.ARRAYS[n_option].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 4))]',
        'S_finish.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
        'pgenerator_closed.PHASE = GENERATOR_CLOSED',
        owners('S_finish', 'HOBJECT n_generator', 2),
        owners('S_finish', 'HARRAY n_option', 1),
        'S_lost = S_finish[.STORE[n_gen_cell] = DEFINED PNULL]',
        '~$config_generator_finish_allowed(S_lost,pconfiggenerator_finish)',
        'S_cycle = S_finish[.ARRAYS[n_option].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_option))]]',
        '~$config_iterator_argument(S_cycle,PARRAY n_option)',
        '~$config_generator_owning_items_live(S_cycle,pconfiggenerator_finish.ITEMS)',
        '~$config_generator_finish_allowed(S_cycle,pconfiggenerator_finish)',
        'S_debt = S_finish[.LITERALARRAYDEBTS = n_option :: S_finish.LITERALARRAYDEBTS]',
        '~$config_generator_owning_items_live(S_debt,pconfiggenerator_finish.ITEMS)',
        '~$config_generator_finish_allowed(S_debt,pconfiggenerator_finish)',
    ] + public('S_finish') + seek('S_finish', 1603, 'S_invoke') + [
        'S_invoke.TODO = (CONFIG_GENERATOR pconfiggenerator_invoke "invoke") :: ptask_invoke*',
        'pconfiggenerator_invoke.ITEMS = pconfiggenerator_finish.ITEMS',
        '$config_generator_valid(S_invoke,pconfiggenerator_invoke,"invoke")',
        '$config_generator_argument_nodes(pconfiggenerator_invoke) = [HARRAY n_option]',
        '$config_pack_prefix(pconfiggenerator_invoke.CALL,pconfiggenerator_invoke.ITEMS,false) = (pconfigcall_prefix)',
        'pconfigcall = pconfigcall_prefix[.INDEX = 1]',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN (PARRAY n_option)),NAMED_SENT (KNOWN (PINT 7))]',
        '$config_nodes(pconfigcall) = [HARRAY n_option]',
        owners('S_invoke', 'HOBJECT n_generator', 1),
        owners('S_invoke', 'HARRAY n_option', 1),
        'PhpStep: S_invoke ~> S_error',
        'S_error.COMPLETION = THROWING n_error',
        '$throwable_field(S_error,n_error,"previous") = PNULL',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
        'S_error.ARRAYS[n_trace].ITEMS[0] = ENTRY (KINT 0) (DIRECT (PARRAY n_frame))',
        '$trace_array_field(S_error,n_frame,$ptascii("args")) = PARRAY n_args',
        'S_error.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_option)),ENTRY (KINT 1) (DIRECT (PINT 7))]',
        'S_error.ARRAYS[n_option].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 4))]',
    ] + public('S_invoke')
    checks += seek('S_invoke', 1604, 'S_catch') + [
        cell('S_catch', 'result', 'n_result_cell'),
        'S_catch.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_catch.PRECISIONINI = $ptascii("14")',
        '$lookup(S_catch.ENV,$ptascii("error")) = (n_error_cell)',
        'S_catch.STORE[n_error_cell] = DEFINED (POBJECT n_error)',
        'S_catch.ARRAYS[n_option].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 4))]',
        owners('S_catch', 'HARRAY n_option', 1),
    ] + public('S_catch') + seek('S_catch', 1605, 'S_recovery') + [
        'S_recovery.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_recovery.PRECISIONINI = $ptascii("14")',
    ] + public('S_recovery')
    return checks + finish('S_recovery', stdout, ['HOBJECT n_generator','HARRAY n_option','HOBJECT n_error'])


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(SOURCES, conditions, HELPERS, model_timeout=300,
        extra_inputs=(Path(__file__),
                      Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
