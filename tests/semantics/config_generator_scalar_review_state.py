#!/usr/bin/env python3
"""Reached Generator scalar copies, retired DATA and weak NULL-option reception."""
from pathlib import Path
from types import SimpleNamespace

import config_generator_scalar_review_cases as cases
import list_missing_warning_protocol as shared
from array_generator_unpack_state_review import finish, initial, owners, public, seek


NAME = 'config-generator-scalar-null-option-handler-return'
SOURCES = SimpleNamespace(CASES={NAME: cases.CASES[NAME]}, __file__=cases.__file__)
HELPERS = shared.HELPERS + r'''
dec $a71_peer_echo(pstate, ptbytes) : bool
def $a71_peer_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $a71_peer_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 980) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask*
  -- if pconfiggenerator.ITEMS = eps
  -- if S.OBJECTS[pconfiggenerator.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.VALUE = (PNULL)
def $list_warning_frontier(S, 981) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask*
  -- if |pconfiggenerator.ITEMS| = 1
  -- if S.OBJECTS[pconfiggenerator.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.VALUE = (PINT 13)
def $list_warning_frontier(S, 982) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "finish") :: ptask*
  -- if |pconfiggenerator.ITEMS| = 2
def $list_warning_frontier(S, 983) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "invoke") :: ptask*
  -- if |pconfiggenerator.ITEMS| = 2
def $list_warning_frontier(S, 984) = true
  -- if S.TODO = (CONFIG_INI_NULL_RESULT pconfigcall) :: ptask*
def $list_warning_frontier(S, 985) = $a71_peer_echo(S, $ptascii("H:"))
def $list_warning_frontier(S, 986) = $a71_peer_echo(S, $ptascii("R:"))
'''


def cell(state, name, identifier):
    return f'$lookup($global_table_view({state}).ENV, $ptascii("{name}")) = ({identifier})'


def conditions(name, program, path, stdout):
    assert name == NAME
    checks = initial(program, path) + seek('S_initial', 980, 'S_option') + [
        'S_option.TODO = (CONFIG_GENERATOR pconfiggenerator_option "ready") :: ptask_option*',
        'pconfiggenerator_option.ITEMS = eps',
        'pconfiggenerator_option.PRODUCER = eps',
        'pconfiggenerator_option.INPUT = VARIABLE ($ptascii("input")) z_input',
        'pconfiggenerator_option.CALL.KIND = INTRINSIC_INI_SET',
        'pconfiggenerator_option.CALL.OWNER = (n_owner)',
        'pconfiggenerator_option.OBJECT = n_generator',
        'S_option.OBJECTS[n_generator] = GENERATOR pgenerator_option',
        'pgenerator_option.PHASE = GENERATOR_PAUSED',
        'pgenerator_option.REFCELL = eps',
        'pgenerator_option.VALUE = (PNULL)',
        'pgenerator_option.KEY = (PINT 3)',
        '$config_generator_valid(S_option,pconfiggenerator_option,"ready")',
        '$config_generator_send_allowed(S_option,pconfiggenerator_option)',
        owners('S_option', 'HOBJECT n_generator', 1),
        cell('S_option', 'input', 'n_input_cell'),
        'S_option.STORE[n_input_cell] = DEFINED (PINT 17)',
        cell('S_option', 'watch', 'n_watch_cell'),
        'S_option.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)',
        '$weakref_get(S_option,n_watch) = POBJECT n_generator',
        cell('S_option', 'option', 'n_option_cell'),
        'S_option.STORE[n_option_cell] = DEFINED PNULL',
        cell('S_option', 'value', 'n_value_cell'),
        'S_option.STORE[n_value_cell] = DEFINED (PINT 13)',
        cell('S_option', 'result', 'n_result_cell'),
        'S_option.STORE[n_result_cell] = DEFINED (PINT 99)',
    ] + public('S_option') + [
        'PhpStep: S_option ~> S_first_sent',
        'S_first_sent.TODO = (CONFIG_GENERATOR pconfiggenerator_first "next") :: ptask_option*',
        'pconfiggenerator_first = pconfiggenerator_option[.ITEMS = [ENTRY (KINT 3) (DIRECT PNULL)]]',
        '$config_generator_history(S_first_sent,pconfiggenerator_first)',
    ] + seek('S_first_sent', 981, 'S_value') + [
        'S_value.TODO = (CONFIG_GENERATOR pconfiggenerator_value "ready") :: ptask_value*',
        'pconfiggenerator_value = pconfiggenerator_first',
        'S_value.OBJECTS[n_generator] = GENERATOR pgenerator_value',
        'pgenerator_value.PHASE = GENERATOR_PAUSED',
        'pgenerator_value.REFCELL = eps',
        'pgenerator_value.VALUE = (PINT 13)',
        'pgenerator_value.KEY = (PINT 3)',
        '$config_generator_valid(S_value,pconfiggenerator_value,"ready")',
        '$config_generator_send_allowed(S_value,pconfiggenerator_value)',
        'S_value.STORE[n_option_cell] = DEFINED pvalue_option_live',
        '$string_bytes(pvalue_option_live) = ($ptascii("precision"))',
        'S_value.STORE[n_value_cell] = DEFINED (PINT 13)',
        # Constructed by-reference cache remains outside this by-value slice.
        'S_ref = S_value[.OBJECTS[n_generator] = GENERATOR pgenerator_value[.VALUE = eps][.REFCELL = (n_value_cell)]]',
        '~$config_generator_send_allowed(S_ref,pconfiggenerator_value)',
        'S_forged = S_value[.CODE = eps]',
        '~$config_generator_history(S_forged,pconfiggenerator_value)',
    ] + public('S_value') + [
        'PhpStep: S_value ~> S_second_sent',
        'S_second_sent.TODO = (CONFIG_GENERATOR pconfiggenerator_second "next") :: ptask_value*',
        'pconfiggenerator_second = pconfiggenerator_value[.ITEMS = [ENTRY (KINT 3) (DIRECT PNULL),ENTRY (KINT 3) (DIRECT (PINT 13))]]',
        '$config_generator_history(S_second_sent,pconfiggenerator_second)',
    ] + seek('S_second_sent', 982, 'S_finish') + [
        'S_finish.TODO = (CONFIG_GENERATOR pconfiggenerator_finish "finish") :: ptask_finish*',
        'pconfiggenerator_finish = pconfiggenerator_second',
        'S_finish.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
        'pgenerator_closed.PHASE = GENERATOR_CLOSED',
        '$config_generator_valid(S_finish,pconfiggenerator_finish,"finish")',
        'S_finish.PRECISIONINI = $ptascii("19")',
        'S_finish.STORE[n_value_cell] = DEFINED (PINT 31)',
        'S_finish.STORE[n_result_cell] = DEFINED (PINT 99)',
        owners('S_finish', 'HOBJECT n_generator', 1),
    ] + public('S_finish') + seek('S_finish', 983, 'S_invoke') + [
        'S_invoke.TODO = (CONFIG_GENERATOR pconfiggenerator_invoke "invoke") :: ptask_invoke*',
        'pconfiggenerator_invoke = pconfiggenerator_finish',
        '~((HOBJECT n_generator) <- S_invoke.ALLOCATIONS)',
        '$weakref_get(S_invoke,n_watch) = PNULL',
        '$config_generator_retired_scope(S_invoke,pconfiggenerator_invoke)',
        '$config_generator_valid(S_invoke,pconfiggenerator_invoke,"invoke")',
        '$config_pack_prefix(pconfiggenerator_invoke.CALL,pconfiggenerator_invoke.ITEMS,false) = (pconfigcall_prefix)',
        'pconfigcall = pconfigcall_prefix[.INDEX = 1]',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (KNOWN (PINT 13))]',
        'pconfigcall.KIND = INTRINSIC_INI_SET',
    ] + public('S_invoke') + seek('S_invoke', 985, 'S_handler') + [
        'S_handler.CURRENT = (pcallcontext_handler)',
        '$error_context_call(S_handler,pcallcontext_handler) = (perrorcall)',
        'perrorcall.RESUME = CONFIG_INI_NULL_RESULT pconfigcall',
        'perrorcall.LEVEL = 8192',
        'perrorcall.MESSAGE = $config_ini_null_message(pconfigcall)',
        '$weakref_get(S_handler,n_watch) = PNULL',
        'S_handler.STORE[n_result_cell] = DEFINED (PINT 99)',
    ] + public('S_handler') + seek('S_handler', 984, 'S_null') + [
        'S_null.TODO = (CONFIG_INI_NULL_RESULT pconfigcall) :: ptask_null*',
        '$config_ini_null_valid(S_null,pconfigcall)',
        '~$config_invoke_valid(S_null,pconfigcall)',
        '$weakref_get(S_null,n_watch) = PNULL',
        'S_null.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_null.PRECISIONINI = $ptascii("19")',
    ] + public('S_null') + seek('S_null', 986, 'S_return') + [
        'S_return.STORE[n_result_cell] = DEFINED (PBOOL false)',
        'S_return.PRECISIONINI = $ptascii("19")',
        '$weakref_get(S_return,n_watch) = PNULL',
    ] + public('S_return')
    return checks + finish('S_return', stdout, ['HOBJECT n_generator'])


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(SOURCES, conditions, HELPERS, model_timeout=300,
        extra_inputs=(Path(__file__),
                      Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
