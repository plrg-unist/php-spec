#!/usr/bin/env python3
"""Reached captured-object publication, receive cancellation and shutdown roots."""
from pathlib import Path

import define_certified_instance_protocol as instance
import define_stdclass_array_duplicate_protocol as prior
import define_object_flag_review_sources as sources

define, packet, common = prior.define, prior.packet, prior.common
ROOT, text, term = prior.ROOT, prior.text, prior.term
TRUE_TARGET, NULL_TARGET = 'V79_REVIEW_TRUE', 'V79_REVIEW_NULL'
PREFIX = instance.PREFIX + r'''
dec $test_object_flag_front(pstate, nat, preqbytes) : bool
def $test_object_flag_front(S,0,preqbytes) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if $dynamic_define_values(pconfigcall) = ((preqbytes,POBJECT n_object))
def $test_object_flag_front(S,1,preqbytes) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_CONSTANT_CASE_WARNING pconfigcall
  -- if $dynamic_define_values(pconfigcall) = ((preqbytes,POBJECT n_object))
def $test_object_flag_front(S,2,preqbytes) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if $dynamic_null_define_flag_values(pconfigcall) = ((preqbytes,POBJECT n_object))
def $test_object_flag_front(S,3,preqbytes) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = DYNAMIC_NULL_DEFINE_FLAG_RESULT pconfigcall
  -- if $dynamic_null_define_flag_values(pconfigcall) = ((preqbytes,POBJECT n_object))
def $test_object_flag_front(S,4,preqbytes) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: ptask_tail*
def $test_object_flag_front(S,n_phase,preqbytes) = false -- otherwise
dec $test_object_flag_seek(pstate, nat, preqbytes, nat) : pstate
def $test_object_flag_seek(S,n_phase,preqbytes,0) = S
def $test_object_flag_seek(S,n_phase,preqbytes,n) = S
  -- if $(n > 0)
  -- if $test_object_flag_front(S,n_phase,preqbytes) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_object_flag_seek(S,n_phase,preqbytes,n) = $test_object_flag_seek($drive_steps($test_running(S),1),n_phase,preqbytes,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_object_flag_front(S,n_phase,preqbytes)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase, target):
    return [f'{state}_found = $test_object_flag_seek({start},{phase},{text(target)},5000)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_object_flag_front({state},{phase},{text(target)})', *common.public(state)]


def trace(state, error, suffix, message, flag):
    return [f'{state}.OBJECTS[{error}] = THROWABLE pthrowable_{suffix}',
        f'pthrowable_{suffix}.KIND = "Exception"',
        f'$string_bytes($throwable_field({state},{error},"message")) = ({text(message)})',
        f'$throwable_field({state},{error},"previous") = PNULL',
        f'$throwable_chain_valid({state},{error})',
        f'$throwable_field({state},{error},"trace") = PARRAY n_trace_{suffix}',
        f'$entry_lookup({state}.ARRAYS[n_trace_{suffix}].ITEMS,KINT 1) = (DIRECT (PARRAY n_frame_{suffix}))',
        f'$trace_array_field({state},n_frame_{suffix},$ptascii("function")) = PSTRING ($ptascii("define"))',
        f'$trace_array_field({state},n_frame_{suffix},$ptascii("args")) = PARRAY n_args_{suffix}',
        f'$entry_lookup({state}.ARRAYS[n_args_{suffix}].ITEMS,KINT 1) = (DIRECT (POBJECT n_object))',
        f'$entry_lookup({state}.ARRAYS[n_args_{suffix}].ITEMS,KINT 2) = (DIRECT ({flag}))',
        f'$heap_edge_owners(HOBJECT n_object,$heap_graph({state}).EDGES,[HARRAY n_args_{suffix}]) = 1']


def after_discard(state, start, error, tail, target):
    return [*common.step(state + '_drop', start),
        *reach(state, state + '_drop', 4, target),
        f'{state}.TODO = (THROW_SEARCH {error}) :: {tail}',
        f'{state}.RESULT = {start}.RESULT', f'{state}.EVENTS = {start}.EVENTS',
        *[f'{state}.{field} = {start}.{field}' for field in
          ['OBJECTS', 'OBJECTPROPS', 'OBJECTTABLES', 'PROPREFS', 'STORE', 'ARRAYS', 'ALLOCATIONS']],
        f'$heap_graph({state}).EDGES = $heap_graph({start}).EDGES',
        f'~(n_object <- {state}.DESTRUCTION.CALLED)']


def checks(initial, name, stdout):
    suffix = b'D|53|D|23|'
    assert stdout.endswith(suffix)
    before = stdout[:-len(suffix)]
    values = [*initial, *reach('S', 'S_initial', 0, TRUE_TARGET),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        '$config_invoke_valid(S,pconfigcall)',
        '$dynamic_define_values(pconfigcall) = ((' + text(TRUE_TARGET) + ',POBJECT n_object))',
        '$named_slot_at(pconfigcall.SENT,2) = NAMED_SENT (KNOWN (PBOOL true))',
        '$dynamic_constant_case_valid(S,pconfigcall)',
        *instance.certified('S', 'n_object', 'V79_REVIEW_LEFT', 'left'),
        *instance.certified('S', 'n_right', 'V79_REVIEW_RIGHT', 'right'),
        'n_object =/= n_right', *instance.controls('n_object', 'pconstantobject_left'),
        *instance.property_value('S', 'n_object', 17, 'left_before'),
        *instance.property_value('S', 'n_right', 23, 'right_before'),
        '$lookup(S.ENV,$ptascii("candidate")) = (n_candidate)',
        'S.STORE[n_candidate] = DEFINED (POBJECT n_object)',
        '$lookup(S.ENV,$ptascii("flag")) = (n_flag)',
        'S.STORE[n_flag] = DEFINED (PBOOL true)',
        '$lookup(S.ENV,$ptascii("result")) = (n_result)',
        'S.STORE[n_result] = DEFINED pvalue_sentinel',
        '$string_bytes(pvalue_sentinel) = ($ptascii("kept"))',
        '$named_slot_at(pconfigcall.SENT,0) = NAMED_SENT (KNOWN pvalue_name)',
        'n_bad_name = |S.STRINGDATA|',
        'pvalue_bad_name = PSTRING_CARRIER (REQUEST_STRING n_bad_name) ' + text(TRUE_TARGET),
        '~$string_carrier_valid(S,pvalue_bad_name)',
        'pconfigcall_bad_name = pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,0,KNOWN pvalue_bad_name)]',
        '$config_invoke_valid(S,pconfigcall_bad_name)',
        '~$dynamic_constant_case_valid(S,pconfigcall_bad_name)',
        'pconfigcall_int = pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,2,KNOWN (PINT 1))]',
        '~$dynamic_scalar_define_flag_valid(S,pconfigcall_int)',
        # Pure receipt refusals never enter the driver.
        '~$dynamic_constant_case_valid(S_missing,pconfigcall)',
        '~$dynamic_constant_case_valid(S_incomplete,pconfigcall)',
        '~$dynamic_constant_case_valid(S_dead,pconfigcall)',
        'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]',
        'S_resume = $test_running(S_pause)', 'S_resume = S',
        *common.step('S_dispatch', 'S_resume'), *common.public('S_dispatch'),
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_case) :: ptask_tail*',
        'perrorcall_case.RESUME = DYNAMIC_CONSTANT_CASE_WARNING pconfigcall',
        'perrorcall_case.LEVEL = 2', '$error_call_valid(S_dispatch,perrorcall_case)',
        'S_dispatch.USERCONSTANTS = S.USERCONSTANTS',
        'S_dispatch.ARRAYS = S.ARRAYS', 'S_dispatch.ALLOCATIONS = S.ALLOCATIONS',
        *reach('S_throw', 'S_dispatch', 1, TRUE_TARGET),
        'S_throw.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall_throw) :: ptask_after*',
        'perrorcall_throw.RESUME = perrorcall_case.RESUME',
        *trace('S_throw', 'n_error', 'true', 'V79_TRUE', 'PBOOL true'),
        '$dynamic_constant_case_valid(S_throw,pconfigcall)',
        'S_throw.STORE[n_candidate] = DEFINED (POBJECT n_right)',
        'S_throw.STORE[n_flag] = DEFINED (PBOOL false)',
        *instance.property_value('S_throw', 'n_object', 41, 'after_true'),
        'S_throw.USERCONSTANTS = S.USERCONSTANTS',
        'n_throw_owners = $heap_owners($heap_graph(S_throw),HOBJECT n_object)',
        *after_discard('S_after', 'S_throw', 'n_error', 'ptask_after*', TRUE_TARGET),
        '$user_constant_at(S_after.USERCONSTANTS,' + text(TRUE_TARGET) + ') = (puserconstant_row)',
        'S_after.USERCONSTANTS = S.USERCONSTANTS ++ [puserconstant_row]',
        'puserconstant_row.VALUE = POBJECT n_object',
        'puserconstant_row.CLASS = PVINSTANCE n_object porigin_left',
        'puserconstant_row.ORIGIN = pconfigcall.SITE',
        'puserconstant_row.READS = eps', 'puserconstant_row.RECEIVES = eps',
        '$heap_owners($heap_graph(S_after),HOBJECT n_object) = n_throw_owners',
        'S_after.ERRORHANDLER.CALLBACK = (perrorcall_throw.CALLBACK)',
        # Pure existing-key composition; no callback or execution credit is inferred.
        'S_existing = $error_handler_restore(S_throw[.USERCONSTANTS = S_after.USERCONSTANTS],perrorcall_throw.CALLBACK)',
        '$dynamic_constant_case_valid(S_existing,pconfigcall)',
        '$error_handler_eligible(S_existing,2)',
        'S_existing_pending = $dynamic_constant_case_pending(S_existing,pconfigcall)',
        'S_existing_pending = S_existing[.ERRORFATALTRACE = eps]',
        *common.reach('S_query', 'S_after', 0, TRUE_TARGET), *common.public('S_query'),
        'n_query_owners = $heap_owners($heap_graph(S_query),HOBJECT n_object)',
        *common.step('S_value', 'S_query', 'POBJECT n_object'),
        '$heap_owners($heap_graph(S_value),HOBJECT n_object) = $(n_query_owners + 1)',
        'S_value.ALLOCATIONS = S_query.ALLOCATIONS',
        '$heap_graph(S_value).EDGES = $heap_graph(S_query).EDGES',
        *reach('S_null', 'S_value', 2, NULL_TARGET),
        'S_null.TODO = (CONFIG_INVOKE pconfigcall_null) :: ptask_null*',
        '$dynamic_null_define_flag_values(pconfigcall_null) = ((' + text(NULL_TARGET) + ',POBJECT n_object))',
        '$dynamic_null_define_flag_valid(S_null,pconfigcall_null)',
        '~$config_strict(S_null,pconfigcall_null)',
        '$named_slot_at(pconfigcall_null.SENT,2) = NAMED_SENT (KNOWN PNULL)',
        'S_null.USERCONSTANTS = S_after.USERCONSTANTS',
        '$source_constant_lookup(S_null,' + text(NULL_TARGET) + ') = eps',
        *instance.property_value('S_null', 'n_object', 43, 'after_reference'),
        'S_null.STORE[n_candidate] = DEFINED (POBJECT n_object)',
        'S_null.STORE[n_flag] = DEFINED PNULL',
        '~(HOBJECT n_error <- S_null.ALLOCATIONS)',
        *common.step('S_null_dispatch', 'S_null'), *common.public('S_null_dispatch'),
        'S_null_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_null) :: ptask_null*',
        'perrorcall_null.RESUME = DYNAMIC_NULL_DEFINE_FLAG_RESULT pconfigcall_null',
        'perrorcall_null.LEVEL = 8192', '$error_call_valid(S_null_dispatch,perrorcall_null)',
        'S_null_dispatch.USERCONSTANTS = S_null.USERCONSTANTS',
        'S_null_dispatch.ARRAYS = S_null.ARRAYS',
        'S_null_dispatch.ALLOCATIONS = S_null.ALLOCATIONS',
        *reach('S_null_throw', 'S_null_dispatch', 3, NULL_TARGET),
        'S_null_throw.TODO = (THROW_SEARCH n_null_error) :: (ERROR_HANDLER_RESULT perrorcall_null_throw) :: ptask_null_after*',
        'perrorcall_null_throw.RESUME = perrorcall_null.RESUME',
        *trace('S_null_throw', 'n_null_error', 'null', 'V79_NULL', 'PNULL'),
        '$dynamic_null_define_flag_valid(S_null_throw,pconfigcall_null)',
        'S_null_throw.STORE[n_candidate] = DEFINED (POBJECT n_right)',
        'S_null_throw.STORE[n_flag] = DEFINED (PBOOL true)',
        *instance.property_value('S_null_throw', 'n_object', 53, 'after_null'),
        'S_null_throw.USERCONSTANTS = S_after.USERCONSTANTS',
        'n_null_owners = $heap_owners($heap_graph(S_null_throw),HOBJECT n_object)',
        # A normal receiver could publish; this projection is neither public nor driven.
        'S_eligible = $dynamic_null_define_flag_finish(S_null_throw[.TODO = (DYNAMIC_NULL_DEFINE_FLAG_RESULT pconfigcall_null) :: ptask_null_after*],pconfigcall_null)',
        '$user_constant_at(S_eligible.USERCONSTANTS,' + text(NULL_TARGET) + ') = (puserconstant_eligible)',
        'puserconstant_eligible.VALUE = POBJECT n_object',
        *after_discard('S_cancelled', 'S_null_throw', 'n_null_error', 'ptask_null_after*', NULL_TARGET),
        'S_cancelled.USERCONSTANTS = S_after.USERCONSTANTS',
        '$source_constant_lookup(S_cancelled,' + text(NULL_TARGET) + ') = eps',
        '$heap_owners($heap_graph(S_cancelled),HOBJECT n_object) = $(n_null_owners - 1)',
        'S_cancelled.ERRORHANDLER.CALLBACK = (perrorcall_null_throw.CALLBACK)',
        *instance.store('S_store_left', 'S_cancelled', 'n_object', 2, before),
        *instance.property_value('S_store_left', 'n_object', 53, 'store_left'),
        *instance.store('S_store_right', 'S_store_left_selected', 'n_right', 1, before + b'D|53|'),
        'n_object <- S_store_right.DESTRUCTION.CALLED',
        *define.finish('S_store_right_selected', stdout),
        'S_final.USERCONSTANTS = S_after.USERCONSTANTS',
        '$heap_owners($heap_graph(S_final),HOBJECT n_object) = 2',
        '$heap_owners($heap_graph(S_final),HOBJECT n_right) = 1',
        'n_object <- S_final.DESTRUCTION.CALLED', 'n_right <- S_final.DESTRUCTION.CALLED',
        '~(HOBJECT n_error <- S_final.ALLOCATIONS)',
        '~(HOBJECT n_null_error <- S_final.ALLOCATIONS)']
    return values


prior.sources, prior.checks, prior.PREFIX = sources, checks, PREFIX
packet.sources, packet.prepare = sources, prior.prepare
packet_process = packet.process


def process(command, directory, timeout, cwd):
    if directory.parent.name == 'captured-object-true-publication-and-null-cancellation':
        timeout = 240
    return packet_process(command, directory, timeout, cwd)


packet.process = process
family_fingerprint = sources.family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(ROOT)): sources.family.sha(__file__)})


sources.family.fingerprint = fingerprint

if __name__ == '__main__':
    raise SystemExit(0 if packet.main() else 1)
