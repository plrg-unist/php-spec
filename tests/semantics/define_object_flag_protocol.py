#!/usr/bin/env python3
"""Reached certified-object flag phases, owner transfer and strict traces."""
import argparse
from pathlib import Path
import sys

import define_certified_instance_protocol as instance
import define_array_scalar_flag_protocol as scalar
import define_object_flag_sources as sources

define, packet, common = scalar.define, scalar.packet, scalar.common
ROOT, text = scalar.ROOT, scalar.text
PREFIX = instance.PREFIX + r'''
dec $test_object_flag_named(pconfigcall, preqbytes) : bool
def $test_object_flag_named(pconfigcall, preqbytes) = true
  -- if pconfigcall.KIND = INTRINSIC_DEFINE
  -- if $named_slot_at(pconfigcall.SENT,0) = NAMED_SENT (KNOWN pvalue_name)
  -- if $string_bytes(pvalue_name) = (preqbytes)
  -- if $named_slot_at(pconfigcall.SENT,1) = NAMED_SENT (KNOWN (POBJECT n_object))
def $test_object_flag_named(pconfigcall, preqbytes) = false -- otherwise
dec $test_object_flag_resume(ptask) : pconfigcall?
def $test_object_flag_resume(DYNAMIC_CONSTANT_CASE_WARNING pconfigcall) = (pconfigcall)
def $test_object_flag_resume(DYNAMIC_NULL_DEFINE_FLAG_RESULT pconfigcall) = (pconfigcall)
def $test_object_flag_resume(DYNAMIC_CONSTANT_DUPLICATE pconfigcall n_constants) = (pconfigcall)
def $test_object_flag_resume(DYNAMIC_NULL_DEFINE_FLAG_DUPLICATE pconfigcall n_constants) = (pconfigcall)
def $test_object_flag_resume(ptask) = eps -- otherwise
dec $test_object_flag_front(pstate, nat, preqbytes) : bool
def $test_object_flag_front(S,0,preqbytes) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if $test_object_flag_named(pconfigcall,preqbytes)
def $test_object_flag_front(S,1,preqbytes) = true
  -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if $test_object_flag_resume(perrorcall.RESUME) = (pconfigcall)
  -- if $test_object_flag_named(pconfigcall,preqbytes)
def $test_object_flag_front(S,2,preqbytes) = true
  -- if S.TODO = ptask :: ptask_tail*
  -- if $test_object_flag_resume(ptask) = (pconfigcall)
  -- if $test_object_flag_named(pconfigcall,preqbytes)
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


def same(state, old, fields):
    return [f'{state}.{field} = {old}.{field}' for field in fields]


def callback(state, start, target, marker, suffix):
    return [*reach(state + '_done', start, 1, target),
        f'{state}_done.TODO = (ERROR_HANDLER_RESULT perrorcall_{suffix}_done) :: ptask_{suffix}*',
        f'perrorcall_{suffix}_done.RESUME = {marker}',
        f'{state}_done.RESULT = KNOWN (PBOOL true)',
        *reach(state, state + '_done', 2, target),
        f'{state}.TODO = ({marker}) :: ptask_{suffix}*',
        f'$call_task_valid({state},{marker})',
        f'{state}.EVENTS = {state}_done.EVENTS']


def publish(state, start, cfg, name, obj, site, owners, suffix):
    return [f'$heap_owners($heap_graph({start}),HOBJECT {obj}) = {owners}',
        *common.step(state, start, 'PBOOL true'),
        f'{state}.TODO = ptask_{suffix}*',
        f'$user_constant_at({state}.USERCONSTANTS,{text(name)}) = (puserconstant_{suffix})',
        f'{state}.USERCONSTANTS = {start}.USERCONSTANTS ++ [puserconstant_{suffix}]',
        f'puserconstant_{suffix}.VALUE = POBJECT {obj}',
        f'puserconstant_{suffix}.CLASS = PVINSTANCE {obj} {site}',
        f'puserconstant_{suffix}.ORIGIN = {cfg}.SITE',
        f'puserconstant_{suffix}.READS = eps', f'puserconstant_{suffix}.RECEIVES = eps',
        f'$heap_graph({state}).EDGES = $heap_graph({start}).EDGES',
        f'$heap_owners($heap_graph({state}),HOBJECT {obj}) = {owners}',
        *same(state, start, ['ALLOCATIONS','OBJECTS','OBJECTPROPS','STORE','ARRAYS','CONSTANTOBJECTS'])]


def false_delivery(state, start, marker, obj, tail):
    return [f'n_owners_{state} = $heap_owners($heap_graph({start}),HOBJECT {obj})',
        *common.step(state + '_release', start),
        f'{state}_release.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_{state}) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_{state}) :: {tail}',
        f'pdestructionrelease_{state}.JOBS = [DESTRUCTION_VALUE (HOBJECT {obj})]',
        f'pdestructionoperation_{state}.SOURCE = {marker}',
        f'pdestructionoperation_{state}.VALUE = KNOWN (PBOOL false)',
        f'pdestructionoperation_{state}.PENDING = eps',
        *common.step(state + '_shared', state + '_release'),
        f'$heap_owners($heap_graph({state}_shared),HOBJECT {obj}) = $(n_owners_{state} - 1)',
        f'~({obj} <- {state}_shared.DESTRUCTION.CALLED)',
        *common.step(state + '_exit', state + '_shared'),
        *common.step(state, state + '_exit', 'PBOOL false'),
        f'{state}.TODO = {tail}', f'{state}.USERCONSTANTS = {start}.USERCONSTANTS',
        f'$heap_owners($heap_graph({state}),HOBJECT {obj}) = $(n_owners_{state} - 1)']


def literal(initial, stdout):
    suffix = b'D|41|D|43|'
    assert stdout.endswith(suffix)
    before = stdout[:-len(suffix)]
    values = [*initial, *reach('S', 'S_initial', 0, 'V79_TRUE'),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_initial*',
        '$dynamic_define_values(pconfigcall) = (($ptascii("V79_TRUE"),POBJECT n_left))',
        '$named_slot_at(pconfigcall.SENT,2) = NAMED_SENT (KNOWN (PBOOL true))',
        '$dynamic_constant_case_valid(S,pconfigcall)',
        *instance.certified('S','n_left','V79_LEFT','left'),
        *instance.certified('S','n_right','V79_RIGHT','right'),
        'n_left =/= n_right', 'S.USERCONSTANTS = [puserconstant_left,puserconstant_right]',
        '$lookup(S.ENV,$ptascii("candidate")) = (n_cv)',
        '$lookup(S.ENV,$ptascii("flag")) = (n_flag)',
        '$lookup(S.ENV,$ptascii("calls")) = (n_calls)',
        'S.STORE[n_cv] = DEFINED (POBJECT n_left)',
        'S.STORE[n_flag] = DEFINED (PBOOL true)',
        *instance.controls('n_left','pconstantobject_left'),
        'n_bad_string = |S.STRINGDATA|',
        'pconfigcall_bad = pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,0,KNOWN (PSTRING_CARRIER (REQUEST_STRING n_bad_string) ($ptascii("V79_TRUE"))))]',
        '$config_invoke_valid(S,pconfigcall_bad)',
        '~$dynamic_constant_case_valid(S,pconfigcall_bad)',
        '~$dynamic_constant_case_valid(S[.CONSTANTOBJECTS = eps],pconfigcall)',
        '~$dynamic_constant_case_valid(S,pconfigcall[.SENT = $named_slot_set(pconfigcall.SENT,2,KNOWN (PINT 1))])',
        'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]',
        'S_resume = $test_running(S_pause)', 'S_resume = S',
        *common.step('S_warning','S_resume'), *common.public('S_warning'),
        'S_warning.TODO = (ERROR_HANDLER_INVOKE perrorcall_true) :: ptask_initial*',
        'perrorcall_true.RESUME = DYNAMIC_CONSTANT_CASE_WARNING pconfigcall',
        'perrorcall_true.LEVEL = 2', '$error_call_valid(S_warning,perrorcall_true)',
        *same('S_warning','S',['ALLOCATIONS','OBJECTS','ARRAYS','STORE','USERCONSTANTS','EVENTS']),
        *callback('S_body','S_warning','V79_TRUE','DYNAMIC_CONSTANT_CASE_WARNING pconfigcall','true'),
        'S_body.STORE[n_cv] = DEFINED (POBJECT n_right)',
        'S_body.STORE[n_flag] = DEFINED (PBOOL false)',
        *instance.property_value('S_body','n_left',11,'true_body'),
        *publish('S_true','S_body','pconfigcall','V79_TRUE','n_left','porigin_left',2,'true'),
        *common.reach('S_query','S_true',0,'V79_TRUE'), *common.public('S_query'),
        'n_query_owners = $heap_owners($heap_graph(S_query),HOBJECT n_left)',
        *common.step('S_value','S_query','POBJECT n_left'),
        '$heap_owners($heap_graph(S_value),HOBJECT n_left) = $(n_query_owners + 1)',
        '$heap_graph(S_value).EDGES = $heap_graph(S_query).EDGES',
        'S_value.ALLOCATIONS = S_query.ALLOCATIONS',
        *reach('S_null','S_value',0,'V79_NULL'),
        'S_null.TODO = (CONFIG_INVOKE pconfigcall_null) :: ptask_null_initial*',
        '$dynamic_null_define_flag_values(pconfigcall_null) = (($ptascii("V79_NULL"),POBJECT n_left))',
        '$dynamic_null_define_flag_valid(S_null,pconfigcall_null)',
        '~$config_strict(S_null,pconfigcall_null)',
        'S_null.STORE[n_cv] = DEFINED (POBJECT n_left)', 'S_null.STORE[n_flag] = DEFINED PNULL',
        *common.step('S_deprecated','S_null'), *common.public('S_deprecated'),
        'S_deprecated.TODO = (ERROR_HANDLER_INVOKE perrorcall_null) :: ptask_null_initial*',
        'perrorcall_null.RESUME = DYNAMIC_NULL_DEFINE_FLAG_RESULT pconfigcall_null',
        'perrorcall_null.LEVEL = 8192', '$error_call_valid(S_deprecated,perrorcall_null)',
        *same('S_deprecated','S_null',['ALLOCATIONS','OBJECTS','ARRAYS','USERCONSTANTS','EVENTS']),
        *callback('S_null_body','S_deprecated','V79_NULL','DYNAMIC_NULL_DEFINE_FLAG_RESULT pconfigcall_null','null'),
        'S_null_body.STORE[n_cv] = DEFINED (POBJECT n_right)',
        'S_null_body.STORE[n_flag] = DEFINED (PBOOL true)',
        *instance.property_value('S_null_body','n_left',41,'null_body'),
        *publish('S_null_row','S_null_body','pconfigcall_null','V79_NULL','n_left','porigin_left',3,'null'),
        *reach('S_late','S_null_row',0,'V79_LATE'),
        'S_late.TODO = (CONFIG_INVOKE pconfigcall_late) :: ptask_late_initial*',
        '$dynamic_null_define_flag_values(pconfigcall_late) = (($ptascii("V79_LATE"),POBJECT n_right))',
        '$dynamic_null_define_flag_valid(S_late,pconfigcall_late)',
        '$source_constant_lookup(S_late,$ptascii("V79_LATE")) = eps',
        *common.step('S_late_dispatch','S_late'),
        *callback('S_late_body','S_late_dispatch','V79_LATE','DYNAMIC_NULL_DEFINE_FLAG_RESULT pconfigcall_late','late'),
        '$user_constant_at(S_late_body.USERCONSTANTS,$ptascii("V79_LATE")) = (puserconstant_late)',
        'S_late_body.USERCONSTANTS = S_late.USERCONSTANTS ++ [puserconstant_late]',
        'puserconstant_late.VALUE = PINT 17',
        'S_late_body.STORE[n_cv] = DEFINED (POBJECT n_left)',
        *instance.property_value('S_late_body','n_right',23,'late_body'),
        'n_constants = |S_late_body.USERCONSTANTS|', 'n_constants = 5',
        '$dynamic_null_define_flag_duplicate_valid(S_late_body,pconfigcall_late,n_constants)',
        *common.step('S_late_duplicate','S_late_body'), *common.public('S_late_duplicate'),
        'S_late_duplicate.TODO = (ERROR_HANDLER_INVOKE perrorcall_late_dup) :: ptask_late*',
        'perrorcall_late_dup.RESUME = DYNAMIC_NULL_DEFINE_FLAG_DUPLICATE pconfigcall_late n_constants',
        'perrorcall_late_dup.LEVEL = 2', '$error_call_valid(S_late_duplicate,perrorcall_late_dup)',
        *callback('S_late_pending','S_late_duplicate','V79_LATE','DYNAMIC_NULL_DEFINE_FLAG_DUPLICATE pconfigcall_late n_constants','late_dup'),
        *instance.property_value('S_late_pending','n_right',31,'late_changed'),
        '$heap_owners($heap_graph(S_late_pending),HOBJECT n_right) = 2',
        *false_delivery('S_late_false','S_late_pending','DYNAMIC_NULL_DEFINE_FLAG_DUPLICATE pconfigcall_late n_constants','n_right','ptask_late_dup*'),
        *reach('S_again','S_late_false',0,'V79_TRUE'),
        'S_again.TODO = (CONFIG_INVOKE pconfigcall_again) :: ptask_again_initial*',
        '$dynamic_define_values(pconfigcall_again) = (($ptascii("V79_TRUE"),POBJECT n_right))',
        '$dynamic_constant_case_valid(S_again,pconfigcall_again)',
        *common.step('S_again_warning','S_again'),
        *callback('S_again_body','S_again_warning','V79_TRUE','DYNAMIC_CONSTANT_CASE_WARNING pconfigcall_again','again'),
        'S_again_body.STORE[n_cv] = DEFINED (POBJECT n_left)',
        'S_again_body.STORE[n_flag] = DEFINED (PBOOL false)',
        *instance.property_value('S_again_body','n_right',37,'again_body'),
        '$dynamic_constant_duplicate_valid(S_again_body,pconfigcall_again,n_constants)',
        *common.step('S_again_duplicate','S_again_body'), *common.public('S_again_duplicate'),
        'S_again_duplicate.TODO = (ERROR_HANDLER_INVOKE perrorcall_again_dup) :: ptask_again*',
        'perrorcall_again_dup.RESUME = DYNAMIC_CONSTANT_DUPLICATE pconfigcall_again n_constants',
        'perrorcall_again_dup.LEVEL = 2', '$error_call_valid(S_again_duplicate,perrorcall_again_dup)',
        *callback('S_again_pending','S_again_duplicate','V79_TRUE','DYNAMIC_CONSTANT_DUPLICATE pconfigcall_again n_constants','again_dup'),
        *instance.property_value('S_again_pending','n_right',43,'again_changed'),
        *instance.property_value('S_again_pending','n_left',41,'old_preserved'),
        'S_again_pending.STORE[n_calls] = DEFINED (PINT 6)',
        *false_delivery('S_again_false','S_again_pending','DYNAMIC_CONSTANT_DUPLICATE pconfigcall_again n_constants','n_right','ptask_again_dup*'),
        'S_again_false.USERCONSTANTS = S_late_false.USERCONSTANTS',
        *instance.store('S_store_left','S_again_false','n_left',3,before),
        *instance.store('S_store_right','S_store_left_selected','n_right',1,before+b'D|41|'),
        *define.finish('S_store_right_selected',stdout),
        'S_final.USERCONSTANTS = S_again_false.USERCONSTANTS',
        'S_final.CONSTANTOBJECTS = S.CONSTANTOBJECTS',
        'S_final.DESTRUCTION.PHASE = DESTRUCTION_DONE',
        'n_left <- S_final.DESTRUCTION.CALLED', 'n_right <- S_final.DESTRUCTION.CALLED',
        '$heap_owners($heap_graph(S_final),HOBJECT n_left) = 3',
        '$heap_owners($heap_graph(S_final),HOBJECT n_right) = 1']
    return values


def strict(initial, stdout):
    values = [*initial, *reach('S','S_initial',0,'V79_STRICT'),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        'pconfigcall.SITE = PORIGIN 1 pcpath_call', 'pconfigcall.SELECTION = (n_selection)',
        '$dynamic_null_define_flag_values(pconfigcall) = (($ptascii("V79_STRICT"),POBJECT n_left))',
        '$dynamic_null_define_flag_valid(S,pconfigcall)', '$config_strict(S,pconfigcall)',
        '~$call_task_valid(S,DYNAMIC_NULL_DEFINE_FLAG_RESULT pconfigcall)',
        '$user_constant_at(S.USERCONSTANTS,$ptascii("V79_STRICT_LEFT")) = (puserconstant_left)',
        'puserconstant_left.VALUE = POBJECT n_left',
        'puserconstant_left.CLASS = PVSTDCLASS n_left porigin_left',
        '$global_std_record(S.CONSTANTSTDOBJECTS,n_left) = (pconstantstdobject_left)',
        '$global_std_completed(S,pconstantstdobject_left)',
        '$user_constant_at(S.USERCONSTANTS,$ptascii("V79_STRICT_RIGHT")) = (puserconstant_right)',
        'puserconstant_right.VALUE = POBJECT n_right', 'n_left =/= n_right',
        '$lookup(S.ENV,$ptascii("candidate")) = (n_cv)',
        '$lookup(S.ENV,$ptascii("flag")) = (n_flag)',
        '$lookup(S.ENV,$ptascii("api")) = (n_api)',
        '$lookup(S.ENV,$ptascii("calls")) = (n_calls)',
        'S.STORE[n_cv] = DEFINED (POBJECT n_right)',
        'S.STORE[n_flag] = DEFINED (PBOOL true)',
        'S.STORE[n_api] = DEFINED pvalue_api', '$string_bytes(pvalue_api) = ($ptascii("defined"))',
        'S.STORE[n_calls] = DEFINED (PINT 0)',
        *define.property_value('S','n_left',43,'strict_before'),
        '~$dynamic_null_define_flag_valid(S[.CONSTANTSTDOBJECTS = eps],pconfigcall)',
        '~$dynamic_null_define_flag_valid(S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_left)],pconfigcall)',
        'n_arrays = |S.ARRAYS|', 'n_error = |S.OBJECTS|',
        'n_owners = $heap_owners($heap_graph(S),HOBJECT n_left)', 'n_owners = 2',
        *common.step('S_error','S'), *common.public('S_error'),
        'S_error.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
        'S_error.OBJECTS[n_error] = THROWABLE pthrowable_error',
        'S_error.OBJECTS = S.OBJECTS ++ [THROWABLE pthrowable_error]',
        'pthrowable_error.KIND = "TypeError"',
        '$string_bytes($throwable_field(S_error,n_error,"message")) = ($ptascii("define(): Argument #3 ($case_insensitive) must be of type bool, null given"))',
        '$throwable_field(S_error,n_error,"previous") = PNULL',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
        '$entry_lookup(S_error.ARRAYS[n_trace].ITEMS,KINT 0) = (DIRECT (PARRAY n_frame))',
        '$trace_array_field(S_error,n_frame,$ptascii("function")) = PSTRING ($ptascii("define"))',
        '$trace_array_field(S_error,n_frame,$ptascii("args")) = PARRAY n_args',
        '$entry_lookup(S_error.ARRAYS[n_args].ITEMS,KINT 1) = (DIRECT (POBJECT n_left))',
        '$entry_lookup(S_error.ARRAYS[n_args].ITEMS,KINT 2) = (DIRECT PNULL)',
        'n_trace = n_arrays', 'n_args = $(n_arrays + 1)', 'n_frame = $(n_arrays + 2)',
        'n_eval = $(n_arrays + 3)',
        '$entry_lookup(S_error.ARRAYS[n_trace].ITEMS,KINT 1) = (DIRECT (PARRAY n_eval))',
        '$trace_array_field(S_error,n_eval,$ptascii("function")) = PSTRING ($ptascii("eval"))',
        'parray_trace = S_error.ARRAYS[n_trace]', 'parray_args = S_error.ARRAYS[n_args]',
        'parray_frame = S_error.ARRAYS[n_frame]', 'parray_eval = S_error.ARRAYS[n_eval]',
        'S_error.ARRAYS = S.ARRAYS ++ [parray_trace,parray_args,parray_frame,parray_eval]',
        'S_error.STORE = S.STORE', 'S_error.USERCONSTANTS = S.USERCONSTANTS',
        'S_error.EVENTS = S.EVENTS',
        '$heap_owners($heap_graph(S_error),HOBJECT n_left) = n_owners',
        *define.finish('S_error',stdout), 'S_final.USERCONSTANTS = S.USERCONSTANTS',
        'S_final.CONSTANTSTDOBJECTS = S.CONSTANTSTDOBJECTS',
        '$heap_owners($heap_graph(S_final),HOBJECT n_left) = 1',
        '$heap_owners($heap_graph(S_final),HOBJECT n_right) = 1',
        '~(HOBJECT n_error <- S_final.ALLOCATIONS)',
        '~(HARRAY n_trace <- S_final.ALLOCATIONS)', '~(HARRAY n_args <- S_final.ALLOCATIONS)',
        '~(HARRAY n_frame <- S_final.ALLOCATIONS)', '~(HARRAY n_eval <- S_final.ALLOCATIONS)']
    return values


scalar.sources, scalar.literal, scalar.strict, scalar.PREFIX = sources, literal, strict, PREFIX
packet.sources, packet.prepare = sources, scalar.prepare
packet_process = packet.process


def process(command, directory, timeout, cwd):
    if directory.parent.name == 'normal-object-warning-null-and-late-duplicate':
        timeout = 480
    return packet_process(command, directory, timeout, cwd)


packet.process = process
family_fingerprint = sources.family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(ROOT)): sources.family.sha(__file__)})


sources.family.fingerprint = fingerprint

if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--case', choices=sources.family.CASES)
    args, remaining = parser.parse_known_args()
    if args.case:
        sources.family.CASES = {args.case: sources.family.CASES[args.case]}
    sys.argv = [sys.argv[0], *remaining]
    raise SystemExit(0 if packet.main() else 1)
