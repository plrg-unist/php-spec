#!/usr/bin/env python3
"""A temporary Gen dies before TypeError while its copied object enters TraceArgs."""
from pathlib import Path
from types import SimpleNamespace

import config_generator_owning_temporary_cases as cases
import list_missing_warning_protocol as shared
from array_generator_unpack_state_review import budget, finish, initial, owners, public, seek


NAME = 'config-generator-owning-temporary-normal'
SOURCES = SimpleNamespace(CASES={NAME: cases.CASES[NAME]}, __file__=cases.__file__)
HELPERS = shared.HELPERS + r'''
dec $a78_echo(pstate, ptbytes) : bool
def $a78_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $a78_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 1800) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask*
  -- if pconfiggenerator.ITEMS = eps
def $list_warning_frontier(S, 1801) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask*
  -- if |pconfiggenerator.ITEMS| = 1
def $list_warning_frontier(S, 1802) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "finish") :: ptask*
def $list_warning_frontier(S, 1803) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "input-release") :: ptask*
def $list_warning_frontier(S, 1804) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "invoke") :: ptask*
def $list_warning_frontier(S, 1805) = true
  -- if S.TODO = (THROW_SEARCH n) :: (CONFIG_GENERATOR pconfiggenerator "invoke") :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 1806) = $a78_echo(S, $ptascii("C:"))
def $list_warning_frontier(S, 1807) = $a78_echo(S, $ptascii("U:"))
def $list_warning_frontier(S, 1808) = $a78_echo(S, $ptascii("R:"))
'''


def cell(state, name, identifier):
    return f'$lookup($global_table_view({state}).ENV,$ptascii("{name}")) = ({identifier})'


def conditions(name, program, path, stdout):
    assert name == NAME
    checks = initial(program, path) + seek('S_initial', 1800, 'S_option') + [
        'S_option.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask_option*',
        'pconfiggenerator.OBJECT = n_generator',
        'pconfiggenerator.INPUT = KNOWN (POBJECT n_generator)',
        'pconfiggenerator.PRODUCER = eps',
        'pconfiggenerator.CALL.OWNER = eps',
        'S_option.OBJECTS[n_generator] = GENERATOR pgenerator_option',
        'pgenerator_option.PHASE = GENERATOR_PAUSED',
        'pgenerator_option.REFCELL = eps',
        'pgenerator_option.VALUE = (POBJECT n_payload)',
        'pgenerator_option.KEY = (PINT 0)',
        '$config_generator_factory_owning_input(S_option,pconfiggenerator)',
        '$config_generator_owning_value_source(S_option,pconfiggenerator)',
        '$config_generator_value(S_option,pconfiggenerator) = (POBJECT n_payload)',
        '$intrinsic_argument(S_option,pconfiggenerator.CALL.SITE,0) = ((expression,true,eps,PORIGIN n_source pcpath,z))',
        '$source_emission_noarg_call(S_option,n_source,pcpath,expression) = (z_call)',
        '$code_at(S_option.CODE,n_source) = (pcode)',
        '$code_name(pcode.NAMES,pcpath) = ((ptbytes_factory,eps))',
        '$call_target(S_option,ptbytes_factory,eps) = (pfunction_factory)',
        'pfunction_factory.SIGNATURE.PARAMETERS = eps',
        '~pfunction_factory.SIGNATURE.BYREF',
        '~$function_generator(S_option,pfunction_factory)',
        '$function_at($all_functions(S_option),pgenerator_option.FUNCTION) = (pfunction_generator)',
        'pfunction_generator.SIGNATURE.PARAMETERS = eps',
        '~pfunction_generator.SIGNATURE.BYREF',
        '$function_generator(S_option,pfunction_generator)',
        'pfunction_generator =/= pfunction_factory',
        cell('S_option','genWatch','n_genwatch_cell'),
        'S_option.STORE[n_genwatch_cell] = DEFINED (POBJECT n_genwatch)',
        cell('S_option','payloadWatch','n_payloadwatch_cell'),
        'S_option.STORE[n_payloadwatch_cell] = DEFINED (POBJECT n_payloadwatch)',
        '$weakref_get(S_option,n_genwatch) = POBJECT n_generator',
        '$weakref_get(S_option,n_payloadwatch) = POBJECT n_payload',
        '$heap_count(HOBJECT n_payload,$pools_nodes(S_option.POOLS)) = 0',
        owners('S_option','HOBJECT n_generator',2),
        owners('S_option','HOBJECT n_payload',2),
        'PhpStep: S_option ~> S_first_sent',
        'S_first_sent.TODO = (CONFIG_GENERATOR pconfiggenerator_first "next") :: ptask_option*',
        'pconfiggenerator_first = pconfiggenerator[.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_payload))]]',
        '$config_generator_argument_nodes(pconfiggenerator_first) = [HOBJECT n_payload]',
    ] + public('S_option') + public('S_first_sent') + seek('S_first_sent', 1801, 'S_value') + [
        'S_value.TODO = (CONFIG_GENERATOR pconfiggenerator_first "ready") :: ptask_value*',
        'S_value.OBJECTS[n_generator] = GENERATOR pgenerator_value',
        'pgenerator_value.VALUE = (PINT 7)',
        '$weakref_get(S_value,n_payloadwatch) = POBJECT n_payload',
        '~$heap_member(HOBJECT n_payload,$heap_reach([HOBJECT n_generator],eps,$heap_graph(S_value).EDGES))',
        owners('S_value','HOBJECT n_generator',2),
        owners('S_value','HOBJECT n_payload',1),
        'PhpStep: S_value ~> S_second_sent',
        'S_second_sent.TODO = (CONFIG_GENERATOR pconfiggenerator_second "next") :: ptask_value*',
        'pconfiggenerator_second = pconfiggenerator[.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_payload)),ENTRY (KINT 1) (DIRECT (PINT 7))]]',
    ] + public('S_value') + seek('S_second_sent', 1802, 'S_finish') + [
        'S_finish.TODO = (CONFIG_GENERATOR pconfiggenerator_second "finish") :: ptask_finish*',
        'S_finish.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
        'pgenerator_closed.PHASE = GENERATOR_CLOSED',
        'pgenerator_closed.FRAME = eps',
        'pgenerator_closed.VALUE = (PINT 7)',
        '$node_children(S_finish,HOBJECT n_generator) = eps',
        '$config_generator_factory_owning_cleanup(S_finish,pconfiggenerator_second)',
        '$config_generator_finish_allowed(S_finish,pconfiggenerator_second)',
        '$config_generator_owning_items_live(S_finish,pconfiggenerator_second.ITEMS)',
        '$weakref_get(S_finish,n_genwatch) = POBJECT n_generator',
        '$weakref_get(S_finish,n_payloadwatch) = POBJECT n_payload',
        owners('S_finish','HOBJECT n_generator',2),
        owners('S_finish','HOBJECT n_payload',1),
    ] + public('S_finish') + budget('S_finish','S_finish_budget') + seek('S_finish',1803,'S_input') + [
        'S_input.TODO = (CONFIG_GENERATOR pconfiggenerator_second "input-release") :: ptask_input*',
        '$config_generator_valid(S_input,pconfiggenerator_second,"input-release")',
        '$config_generator_factory_owning_cleanup(S_input,pconfiggenerator_second)',
        '$config_generator_last_input_allowed(S_input,pconfiggenerator_second)',
        '~$config_generator_finish_allowed(S_input,pconfiggenerator_second)',
        '$weakref_get(S_input,n_genwatch) = POBJECT n_generator',
        '$weakref_get(S_input,n_payloadwatch) = POBJECT n_payload',
        owners('S_input','HOBJECT n_generator',1),
        owners('S_input','HOBJECT n_payload',1),
        'S_owning_cache = $generator_set(S_input,n_generator,pgenerator_closed[.VALUE = (POBJECT n_payload)])',
        '~$config_generator_factory_owning_cleanup(S_owning_cache,pconfiggenerator_second)',
        '~$config_generator_last_input_allowed(S_owning_cache,pconfiggenerator_second)',
    ] + public('S_input') + seek('S_input',1804,'S_invoke') + [
        'S_invoke.TODO = (CONFIG_GENERATOR pconfiggenerator_second "invoke") :: ptask_invoke*',
        '$config_generator_valid(S_invoke,pconfiggenerator_second,"invoke")',
        '$config_generator_factory_owning_cleanup(S_invoke,pconfiggenerator_second)',
        '$config_generator_retired_scope(S_invoke,pconfiggenerator_second)',
        '~((HOBJECT n_generator) <- S_invoke.ALLOCATIONS)',
        '$weakref_get(S_invoke,n_genwatch) = PNULL',
        '$weakref_get(S_invoke,n_payloadwatch) = POBJECT n_payload',
        owners('S_invoke','HOBJECT n_payload',1),
        '$config_pack_prefix(pconfiggenerator_second.CALL,pconfiggenerator_second.ITEMS,false) = (pconfigcall_prefix)',
        'pconfigcall = pconfigcall_prefix[.INDEX = 1]',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_payload)),NAMED_SENT (KNOWN (PINT 7))]',
        'PhpStep: S_invoke ~> S_error',
        'S_error.COMPLETION = THROWING n_error',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
        'S_error.ARRAYS[n_trace].ITEMS[0] = ENTRY (KINT 0) (DIRECT (PARRAY n_frame))',
        '$trace_array_field(S_error,n_frame,$ptascii("args")) = PARRAY n_args',
        'S_error.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_payload)),ENTRY (KINT 1) (DIRECT (PINT 7))]',
    ] + public('S_invoke') + seek('S_invoke',1805,'S_throw') + [
        'S_throw.TODO = (THROW_SEARCH n_error) :: (CONFIG_GENERATOR pconfiggenerator_second "invoke") :: ptask_throw*',
        '~((HOBJECT n_generator) <- S_throw.ALLOCATIONS)',
        '$weakref_get(S_throw,n_genwatch) = PNULL',
        '$weakref_get(S_throw,n_payloadwatch) = POBJECT n_payload',
        '$config_generator_retired_scope(S_throw,pconfiggenerator_second)',
        'S_popped = S_throw[.TODO = (THROW_SEARCH n_error) :: ptask_throw*]',
        '$config_generator_factory_owning_cleanup(S_popped,pconfiggenerator_second)',
        '$config_generator_discard_allowed(S_popped,pconfiggenerator_second)',
        owners('S_popped','HOBJECT n_generator',0),
        'S_raw = $config_generator_discard(S_popped,pconfiggenerator_second,"invoke")',
        'PhpStep: S_throw ~> S_raw',
        'S_raw.TODO = (THROW_SEARCH n_error) :: ptask_throw*',
        '$weakref_get(S_raw,n_payloadwatch) = POBJECT n_payload',
    ] + public('S_throw') + public('S_raw') + seek('S_raw',1806,'S_catch') + [
        cell('S_catch','result','n_result_cell'),
        'S_catch.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_catch.PRECISIONINI = $ptascii("14")',
        '$weakref_get(S_catch,n_genwatch) = PNULL',
        '$weakref_get(S_catch,n_payloadwatch) = POBJECT n_payload',
        '$lookup(S_catch.ENV,$ptascii("error")) = (n_error_cell)',
        'S_catch.STORE[n_error_cell] = DEFINED (POBJECT n_error)',
        owners('S_catch','HOBJECT n_payload',1),
    ] + public('S_catch') + seek('S_catch',1807,'S_empty') + [
        '$weakref_get(S_empty,n_payloadwatch) = PNULL',
        '~((HOBJECT n_payload) <- S_empty.ALLOCATIONS)',
        '~((HOBJECT n_error) <- S_empty.ALLOCATIONS)',
    ] + public('S_empty') + seek('S_empty',1808,'S_recovery') + [
        'S_recovery.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_recovery.PRECISIONINI = $ptascii("14")',
    ] + public('S_recovery')
    return checks + finish('S_recovery',stdout,['HOBJECT n_generator','HOBJECT n_payload','HOBJECT n_error'])


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(SOURCES,conditions,HELPERS,model_timeout=300,
        extra_inputs=(Path(__file__),Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
