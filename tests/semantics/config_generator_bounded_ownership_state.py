#!/usr/bin/env python3
"""Reach the crossed factory/alias ownership stages from the PHP source."""
from pathlib import Path
from types import SimpleNamespace

import config_generator_bounded_ownership_cases as cases
import list_missing_warning_protocol as shared
from array_generator_unpack_state_review import initial, owners, public, seek, finish

NAME = 'config-generator-bounded-factory-alias-normal'
SOURCES = SimpleNamespace(CASES={NAME: cases.CASES[NAME]}, __file__=cases.__file__)
HELPERS = shared.HELPERS + r'''
dec $bounded_echo(pstate, ptbytes) : bool
def $bounded_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $bounded_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 9300) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask*
  -- if pconfiggenerator.ITEMS = eps
def $list_warning_frontier(S, 9301) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask*
  -- if |pconfiggenerator.ITEMS| = 1
def $list_warning_frontier(S, 9302) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "finish") :: ptask*
  -- if |pconfiggenerator.ITEMS| = 2
def $list_warning_frontier(S, 9303) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "input-release") :: ptask*
def $list_warning_frontier(S, 9304) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "storage-released") :: ptask*
def $list_warning_frontier(S, 9305) = $bounded_echo(S, $ptascii("E:"))
def $list_warning_frontier(S, 9306) = $bounded_echo(S, $ptascii("U0:"))
def $list_warning_frontier(S, 9307) = $bounded_echo(S, $ptascii("U1:"))
'''


def alias(state, name, cell):
    return f'$lookup($global_table_view({state}).ENV,$ptascii("{name}")) = ({cell})'


def conditions(name, program, path, stdout):
    assert name == NAME
    checks = initial(program, path) + seek('S_initial', 9300, 'S_first') + [
        'S_first.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask_first*',
        'pconfiggenerator.INPUT = KNOWN (POBJECT n_generator)',
        'pconfiggenerator.OBJECT = n_generator',
        'pconfiggenerator.CALL.KIND = INTRINSIC_INI_SET',
        '$config_generator_factory_reference_input(S_first,pconfiggenerator)',
        '$config_generator_reference_owning_item_source(S_first,pconfiggenerator)',
        'S_first.OBJECTS[n_generator] = GENERATOR pgenerator_first',
        'pgenerator_first.REFCELL = (n_firstref)',
        'pgenerator_first.KEY = (PINT 0)',
        '$ordinary_reference_value(S_first,n_firstref) = (POBJECT n_payload)',
        '$config_generator_value(S_first,pconfiggenerator) = (POBJECT n_payload)',
        owners('S_first', 'HOBJECT n_generator', 2),
        owners('S_first', 'HOBJECT n_payload', 1),
        'PhpStep: S_first ~> S_sent_first',
        'S_sent_first.TODO = (CONFIG_GENERATOR pconfiggenerator_one "next") :: ptask_first*',
        'pconfiggenerator_one = pconfiggenerator[.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_payload))]]',
        '$config_generator_history(S_sent_first,pconfiggenerator_one)',
        owners('S_sent_first', 'HOBJECT n_payload', 2),
    ] + public('S_first') + public('S_sent_first') + seek('S_sent_first', 9301, 'S_second') + [
        'S_second.TODO = (CONFIG_GENERATOR pconfiggenerator_one "ready") :: ptask_second*',
        'S_second.OBJECTS[n_generator] = GENERATOR pgenerator_second',
        'pgenerator_second.REFCELL = (n_lastref)',
        'pgenerator_second.KEY = (PINT 1)',
        'n_lastref =/= n_firstref',
        '$ordinary_reference_value(S_second,n_firstref) = (PINT 9)',
        '$ordinary_reference_value(S_second,n_lastref) = (POBJECT n_payload)',
        alias('S_second', 'alias0', 'n_lastref'),
        alias('S_second', 'alias1', 'n_lastref'),
        '$config_generator_reference_owning_item_source(S_second,pconfiggenerator_one)',
        '$config_generator_value(S_second,pconfiggenerator_one) = (POBJECT n_payload)',
        owners('S_second', 'HOBJECT n_generator', 2),
        owners('S_second', 'HOBJECT n_payload', 2),
        'PhpStep: S_second ~> S_sent_second',
        'S_sent_second.TODO = (CONFIG_GENERATOR pconfiggenerator_two "next") :: ptask_second*',
        'pconfiggenerator_two = pconfiggenerator[.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_payload)),ENTRY (KINT 1) (DIRECT (POBJECT n_payload))]]',
        '$config_generator_history(S_sent_second,pconfiggenerator_two)',
        '$config_generator_temporary_reference_two_owning_items(S_sent_second,pconfiggenerator_two)',
        owners('S_sent_second', 'HOBJECT n_payload', 3),
    ] + public('S_second') + public('S_sent_second') + seek('S_sent_second', 9302, 'S_finish') + [
        'S_finish.TODO = (CONFIG_GENERATOR pconfiggenerator_two "finish") :: ptask_finish*',
        'S_finish.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
        'pgenerator_closed.PHASE = GENERATOR_CLOSED',
        'pgenerator_closed.REFCELL = (n_lastref)',
        'pgenerator_closed.KEY = (PINT 1)',
        alias('S_finish', 'alias0', 'n_lastref'),
        alias('S_finish', 'alias1', 'n_lastref'),
        '$node_children(S_finish,HOBJECT n_generator) = [HCELL n_lastref]',
        '$node_children(S_finish,HCELL n_lastref) = [HOBJECT n_payload]',
        '$config_generator_temporary_reference_owning_storage(S_finish,pconfiggenerator_two)',
        '$config_generator_finish_allowed(S_finish,pconfiggenerator_two)',
        owners('S_finish', 'HOBJECT n_generator', 2),
        owners('S_finish', 'HCELL n_lastref', 3),
        owners('S_finish', 'HOBJECT n_payload', 3),
    ] + public('S_finish') + seek('S_finish', 9303, 'S_input') + [
        'S_input.TODO = (CONFIG_GENERATOR pconfiggenerator_two "input-release") :: ptask_input*',
        '$config_generator_last_input_allowed(S_input,pconfiggenerator_two)',
        '$config_generator_temporary_reference_owning_storage(S_input,pconfiggenerator_two)',
        owners('S_input', 'HOBJECT n_generator', 1),
        owners('S_input', 'HCELL n_lastref', 3),
        owners('S_input', 'HOBJECT n_payload', 3),
    ] + public('S_input') + seek('S_input', 9304, 'S_retired') + [
        'S_retired.TODO = (CONFIG_GENERATOR pconfiggenerator_two "storage-released") :: ptask_retired*',
        '~((HOBJECT n_generator) <- S_retired.ALLOCATIONS)',
        '(HCELL n_lastref) <- S_retired.ALLOCATIONS',
        '$config_generator_retired_scope(S_retired,pconfiggenerator_two)',
        '$config_generator_valid(S_retired,pconfiggenerator_two,"storage-released")',
        owners('S_retired', 'HCELL n_lastref', 2),
        owners('S_retired', 'HOBJECT n_payload', 3),
    ] + public('S_retired') + seek('S_retired', 9305, 'S_catch') + [
        alias('S_catch', 'alias0', 'n_lastref'),
        alias('S_catch', 'alias1', 'n_lastref'),
        '$ordinary_reference_value(S_catch,n_lastref) = (POBJECT n_payload)',
        '~((HOBJECT n_generator) <- S_catch.ALLOCATIONS)',
        owners('S_catch', 'HCELL n_lastref', 2),
    ] + public('S_catch') + seek('S_catch', 9306, 'S_after_first_unset') + [
        '$ordinary_reference_value(S_after_first_unset,n_lastref) = (POBJECT n_payload)',
        owners('S_after_first_unset', 'HCELL n_lastref', 1),
        owners('S_after_first_unset', 'HOBJECT n_payload', 1),
    ] + public('S_after_first_unset') + seek('S_after_first_unset', 9307, 'S_after_second_unset') + [
        '~((HCELL n_lastref) <- S_after_second_unset.ALLOCATIONS)',
        '~((HOBJECT n_payload) <- S_after_second_unset.ALLOCATIONS)',
    ] + public('S_after_second_unset')
    return checks + finish('S_after_second_unset', stdout, [
        'HOBJECT n_generator', 'HCELL n_firstref', 'HCELL n_lastref', 'HOBJECT n_payload'])


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(SOURCES, conditions, HELPERS, model_timeout=300,
        extra_inputs=(Path(__file__), Path(__file__).with_name('array_generator_unpack_state_review.py')))
        else 1)
