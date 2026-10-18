#!/usr/bin/env python3
"""Reached quiet object flags, duplicate ownership and raw strict traces."""
import argparse
from pathlib import Path
import sys

import define_object_flag_protocol as previous
import define_object_scalar_flag_sources as sources

instance, scalar = previous.instance, previous.scalar
define, packet, common = previous.define, previous.packet, previous.common
ROOT, text = previous.ROOT, previous.text
PREFIX = instance.PREFIX + r'''
dec $test_object_scalar_named(pconfigcall, preqbytes) : bool
def $test_object_scalar_named(pconfigcall, preqbytes) = true
  -- if pconfigcall.KIND = INTRINSIC_DEFINE
  -- if $dynamic_scalar_define_flag_values(pconfigcall) = ((preqbytes,POBJECT n_object,pvalue_flag))
def $test_object_scalar_named(pconfigcall, preqbytes) = false -- otherwise
dec $test_object_scalar_resume(ptask) : pconfigcall?
def $test_object_scalar_resume(DYNAMIC_SCALAR_DEFINE_FLAG_RESULT pconfigcall) = (pconfigcall)
def $test_object_scalar_resume(DYNAMIC_SCALAR_DEFINE_FLAG_DUPLICATE pconfigcall n_constants) = (pconfigcall)
def $test_object_scalar_resume(ptask) = eps -- otherwise
dec $test_object_scalar_front(pstate, nat, preqbytes) : bool
def $test_object_scalar_front(S,0,preqbytes) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if $test_object_scalar_named(pconfigcall,preqbytes)
def $test_object_scalar_front(S,1,preqbytes) = true
  -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if $test_object_scalar_resume(perrorcall.RESUME) = (pconfigcall)
  -- if $test_object_scalar_named(pconfigcall,preqbytes)
def $test_object_scalar_front(S,2,preqbytes) = true
  -- if S.TODO = ptask :: ptask_tail*
  -- if $test_object_scalar_resume(ptask) = (pconfigcall)
  -- if $test_object_scalar_named(pconfigcall,preqbytes)
def $test_object_scalar_front(S,n_phase,preqbytes) = false -- otherwise
dec $test_object_scalar_seek(pstate, nat, preqbytes, nat) : pstate
def $test_object_scalar_seek(S,n_phase,preqbytes,0) = S
def $test_object_scalar_seek(S,n_phase,preqbytes,n) = S
  -- if $(n > 0)
  -- if $test_object_scalar_front(S,n_phase,preqbytes) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_object_scalar_seek(S,n_phase,preqbytes,n) = $test_object_scalar_seek($drive_steps($test_running(S),1),n_phase,preqbytes,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_object_scalar_front(S,n_phase,preqbytes)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def reach(state, start, phase, target):
    return [f'{state}_found = $test_object_scalar_seek({start},{phase},{text(target)},500)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_object_scalar_front({state},{phase},{text(target)})']


def callback(state, start, marker, target, suffix):
    return [*reach(state + '_done', start, 1, target),
        f'{state}_done.TODO = (ERROR_HANDLER_RESULT perrorcall_{suffix}_done) :: ptask_{suffix}*',
        f'perrorcall_{suffix}_done.RESUME = {marker}',
        f'{state}_done.RESULT = KNOWN (PBOOL true)',
        *reach(state, state + '_done', 2, target),
        f'{state}.TODO = ({marker}) :: ptask_{suffix}*',
        f'$call_task_valid({state},{marker})',
        f'{state}.EVENTS = {state}_done.EVENTS']


def literal(initial, stdout):
    values = [*initial, *reach('S', 'S_initial', 0, 'V80_FALSE'), *common.public('S'),
        'S.TODO = (CONFIG_INVOKE pconfigcall_false) :: ptask_false*',
        '$dynamic_scalar_define_flag_values(pconfigcall_false) = (($ptascii("V80_FALSE"),POBJECT n_left,PINT 0))',
        '$dynamic_scalar_define_flag_valid(S,pconfigcall_false)',
        '~$dynamic_scalar_define_flag_case_valid(S,pconfigcall_false)',
        *instance.certified('S','n_left','V80_LEFT','left'),
        *instance.certified('S','n_right','V80_RIGHT','right'),
        'n_left =/= n_right', 'S.USERCONSTANTS = [puserconstant_left,puserconstant_right]',
        '$lookup(S.ENV,$ptascii("candidate")) = (n_cv)',
        '$lookup(S.ENV,$ptascii("flag")) = (n_flag)',
        '$lookup(S.ENV,$ptascii("api")) = (n_api)',
        '$lookup(S.ENV,$ptascii("calls")) = (n_calls)',
        'S.STORE[n_cv] = DEFINED (POBJECT n_left)',
        'S.STORE[n_flag] = DEFINED (PINT 0)',
        '$heap_owners($heap_graph(S),HOBJECT n_left) = 3',
        *instance.controls('n_left','pconstantobject_left'),
        '~$dynamic_scalar_define_flag_valid(S_missing,pconfigcall_false)',
        '~$dynamic_scalar_define_flag_valid(S_incomplete,pconfigcall_false)',
        '~$dynamic_scalar_define_flag_valid(S_dead,pconfigcall_false)',
        'n_bad_string = |S.STRINGDATA|',
        'pvalue_bad_name = PSTRING_CARRIER (REQUEST_STRING n_bad_string) ($ptascii("V80_FALSE"))',
        'pconfigcall_bad_name = pconfigcall_false[.SENT = $named_slot_set(pconfigcall_false.SENT,0,KNOWN pvalue_bad_name)]',
        '$config_invoke_valid(S,pconfigcall_bad_name)',
        '~$dynamic_scalar_define_flag_valid(S,pconfigcall_bad_name)',
        'pconfigcall_bad_flag = pconfigcall_false[.SENT = $named_slot_set(pconfigcall_false.SENT,2,KNOWN (PSTRING_CARRIER (REQUEST_STRING n_bad_string) ($ptascii("false"))))]',
        '~$dynamic_scalar_define_flag_valid(S,pconfigcall_bad_flag)',
        'pconfigcall_inf = pconfigcall_false[.SENT = $named_slot_set(pconfigcall_false.SENT,2,KNOWN (PFLOAT 9218868437227405312))]',
        '$dynamic_scalar_define_flag_call(pconfigcall_inf)',
        '~$dynamic_scalar_define_flag_valid(S,pconfigcall_inf)',
        'pconfigcall_primitive_inf = pconfigcall_inf[.SENT = $named_slot_set(pconfigcall_inf.SENT,1,KNOWN (PINT 17))]',
        '$dynamic_scalar_define_flag_valid(S,pconfigcall_primitive_inf)',
        'pconfigcall_raw = pconfigcall_false[.SENT = $named_slot_set(pconfigcall_false.SENT,2,KNOWN (PSTRING ($ptascii("0"))))]',
        '$dynamic_scalar_define_flag_valid(S,pconfigcall_raw)',
        'pconfigcall_bad_bytes = pconfigcall_false[.SENT = $named_slot_set(pconfigcall_false.SENT,2,KNOWN (PSTRING ([256])))]',
        '~$dynamic_scalar_define_flag_valid(S,pconfigcall_bad_bytes)',
        *common.step('S_row','S','PBOOL true'),
        'S_row.TODO = ptask_false*',
        '$user_constant_at(S_row.USERCONSTANTS,$ptascii("V80_FALSE")) = (puserconstant_row)',
        'S_row.USERCONSTANTS = S.USERCONSTANTS ++ [puserconstant_row]',
        'puserconstant_row.VALUE = POBJECT n_left',
        'puserconstant_row.CLASS = PVINSTANCE n_left porigin_left',
        'puserconstant_row.ORIGIN = pconfigcall_false.SITE',
        'S_row.ALLOCATIONS = S.ALLOCATIONS', 'S_row.ARRAYS = S.ARRAYS',
        'S_row.OBJECTS = S.OBJECTS', 'S_row.OBJECTPROPS = S.OBJECTPROPS',
        'S_row.STORE = S.STORE', 'S_row.CONSTANTOBJECTS = S.CONSTANTOBJECTS',
        '$heap_graph(S_row).EDGES = $heap_graph(S).EDGES',
        '$heap_owners($heap_graph(S_row),HOBJECT n_left) = 3',
        *reach('S_true','S_row',0,'V80_LATE'),
        'S_true.TODO = (CONFIG_INVOKE pconfigcall_true) :: ptask_true*',
        'pvalue_flag = PFLOAT 4612811918334230528',
        '$dynamic_scalar_define_flag_values(pconfigcall_true) = (($ptascii("V80_LATE"),POBJECT n_right,pvalue_flag))',
        'pconfigcall_true.SELECTION = (n_selection)',
        '$dynamic_scalar_define_flag_valid(S_true,pconfigcall_true)',
        '$dynamic_scalar_define_flag_case_valid(S_true,pconfigcall_true)',
        '~$dynamic_scalar_define_flag_valid(S_true,pconfigcall_true[.SELECTION = eps])',
        'S_true.STORE[n_cv] = DEFINED (POBJECT n_right)',
        'S_true.STORE[n_flag] = DEFINED pvalue_flag',
        'S_true.USERCONSTANTS = S_row.USERCONSTANTS',
        '$source_constant_lookup(S_true,$ptascii("V80_LATE")) = eps',
        '$heap_owners($heap_graph(S_true),HOBJECT n_right) = 3',
        'S_pause = $drive_steps(S_true,0)', 'S_pause = S_true[.COMPLETION = BUDGET]',
        '$test_running(S_pause) = S_true',
        *common.step('S_warning','S_true'),
        '$drive_steps($test_running(S_pause),1) = S_warning_found',
        'S_warning.TODO = (ERROR_HANDLER_INVOKE perrorcall_first) :: ptask_true*',
        'perrorcall_first.RESUME = DYNAMIC_SCALAR_DEFINE_FLAG_RESULT pconfigcall_true',
        'S_warning.ALLOCATIONS = S_true.ALLOCATIONS',
        'S_warning.ARRAYS = S_true.ARRAYS', 'S_warning.OBJECTS = S_true.OBJECTS',
        'S_warning.STORE = S_true.STORE', 'S_warning.USERCONSTANTS = S_true.USERCONSTANTS',
        *callback('S_resume','S_warning',
            'DYNAMIC_SCALAR_DEFINE_FLAG_RESULT pconfigcall_true','V80_LATE','first'),
        'S_resume.STORE[n_cv] = DEFINED (POBJECT n_left)',
        'S_resume.STORE[n_flag] = DEFINED pvalue_current_flag',
        '$string_bytes(pvalue_current_flag) = ($ptascii("0"))',
        'S_resume.STORE[n_api] = DEFINED pvalue_current_api',
        '$string_bytes(pvalue_current_api) = ($ptascii("constant"))',
        'S_resume.STORE[n_calls] = DEFINED (PINT 1)',
        '$dynamic_scalar_define_flag_values(pconfigcall_true) = (($ptascii("V80_LATE"),POBJECT n_right,pvalue_flag))',
        '$user_constant_at(S_resume.USERCONSTANTS,$ptascii("V80_LATE")) = (puserconstant_late)',
        'S_resume.USERCONSTANTS = S_true.USERCONSTANTS ++ [puserconstant_late]',
        'puserconstant_late.VALUE = PINT 17',
        'n_constants = |S_resume.USERCONSTANTS|', 'n_constants = 4',
        '$dynamic_scalar_define_flag_duplicate_valid(S_resume,pconfigcall_true,n_constants)',
        '~$dynamic_scalar_define_flag_duplicate_valid(S_resume,pconfigcall_true,3)',
        *instance.property_value('S_resume','n_right',23,'first_candidate'),
        '$heap_owners($heap_graph(S_resume),HOBJECT n_right) = 2',
        *common.step('S_duplicate','S_resume'),
        'S_duplicate.TODO = (ERROR_HANDLER_INVOKE perrorcall_duplicate) :: ptask_true*',
        'perrorcall_duplicate.RESUME = DYNAMIC_SCALAR_DEFINE_FLAG_DUPLICATE pconfigcall_true n_constants',
        'S_duplicate.USERCONSTANTS = S_resume.USERCONSTANTS',
        'S_duplicate.ALLOCATIONS = S_resume.ALLOCATIONS',
        *callback('S_reject','S_duplicate',
            'DYNAMIC_SCALAR_DEFINE_FLAG_DUPLICATE pconfigcall_true n_constants','V80_LATE','second'),
        'S_reject.USERCONSTANTS = S_resume.USERCONSTANTS',
        'S_reject.STORE[n_calls] = DEFINED (PINT 2)',
        *instance.property_value('S_reject','n_right',31,'second_candidate'),
        *common.public('S_reject'),
        *previous.false_delivery('S_false','S_reject',
            'DYNAMIC_SCALAR_DEFINE_FLAG_DUPLICATE pconfigcall_true n_constants','n_right','ptask_second*'),
        *define.finish('S_false',stdout),
        'S_final.USERCONSTANTS = S_reject.USERCONSTANTS',
        'S_final.CONSTANTOBJECTS = S.CONSTANTOBJECTS',
        '$heap_owners($heap_graph(S_final),HOBJECT n_left) = 2',
        '$heap_owners($heap_graph(S_final),HOBJECT n_right) = 1',
        'n_left <- S_final.DESTRUCTION.CALLED', 'n_right <- S_final.DESTRUCTION.CALLED',
        *instance.property_value('S_final','n_left',7,'final_left'),
        *instance.property_value('S_final','n_right',31,'final_right')]
    return values


def strict(initial, stdout):
    return [*initial, *reach('S','S_initial',0,'V80_STRICT'), *common.public('S'),
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        'pconfigcall.SITE = PORIGIN 1 pcpath_call', 'pconfigcall.SELECTION = (n_selection)',
        '$dynamic_scalar_define_flag_values(pconfigcall) = (($ptascii("V80_STRICT"),POBJECT n_left,pvalue_flag))',
        '$string_bytes(pvalue_flag) = ($ptascii("false"))',
        '$dynamic_constant_class(pvalue_flag) = (PVSTRING false)',
        '$string_carrier_valid(S,pvalue_flag)',
        '$dynamic_scalar_define_flag_valid(S,pconfigcall)', '$config_strict(S,pconfigcall)',
        '~$dynamic_scalar_define_flag_case_valid(S,pconfigcall)',
        '$user_constant_at(S.USERCONSTANTS,$ptascii("V80_STRICT_LEFT")) = (puserconstant_left)',
        'puserconstant_left.VALUE = POBJECT n_left',
        'puserconstant_left.CLASS = PVSTDCLASS n_left porigin_left',
        '$global_std_record(S.CONSTANTSTDOBJECTS,n_left) = (pconstantstdobject_left)',
        '$global_std_completed(S,pconstantstdobject_left)',
        '$user_constant_at(S.USERCONSTANTS,$ptascii("V80_STRICT_RIGHT")) = (puserconstant_right)',
        'puserconstant_right.VALUE = POBJECT n_right', 'n_left =/= n_right',
        '$lookup(S.ENV,$ptascii("candidate")) = (n_cv)',
        '$lookup(S.ENV,$ptascii("flag")) = (n_flag)',
        '$lookup(S.ENV,$ptascii("api")) = (n_api)',
        '$lookup(S.ENV,$ptascii("calls")) = (n_calls)',
        'S.STORE[n_cv] = DEFINED (POBJECT n_right)',
        'S.STORE[n_flag] = DEFINED (PINT 0)',
        'S.STORE[n_api] = DEFINED pvalue_api', '$string_bytes(pvalue_api) = ($ptascii("defined"))',
        'S.STORE[n_calls] = DEFINED (PINT 0)',
        *define.property_value('S','n_left',43,'strict_before'),
        '~$dynamic_scalar_define_flag_valid(S[.CONSTANTSTDOBJECTS = eps],pconfigcall)',
        '~$dynamic_scalar_define_flag_valid(S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_left)],pconfigcall)',
        'n_arrays = |S.ARRAYS|', 'n_error = |S.OBJECTS|',
        'n_owners = $heap_owners($heap_graph(S),HOBJECT n_left)', 'n_owners = 2',
        *common.step('S_error','S'), *common.public('S_error'),
        'S_error.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
        'S_error.OBJECTS[n_error] = THROWABLE pthrowable_error',
        'S_error.OBJECTS = S.OBJECTS ++ [THROWABLE pthrowable_error]',
        'pthrowable_error.KIND = "TypeError"',
        '$string_bytes($throwable_field(S_error,n_error,"message")) = ($ptascii("define(): Argument #3 ($case_insensitive) must be of type bool, string given"))',
        '$throwable_field(S_error,n_error,"previous") = PNULL',
        '$throwable_field(S_error,n_error,"trace") = PARRAY n_trace',
        '$entry_lookup(S_error.ARRAYS[n_trace].ITEMS,KINT 0) = (DIRECT (PARRAY n_frame))',
        '$trace_array_field(S_error,n_frame,$ptascii("function")) = PSTRING ($ptascii("define"))',
        '$trace_array_field(S_error,n_frame,$ptascii("args")) = PARRAY n_args',
        '$entry_lookup(S_error.ARRAYS[n_args].ITEMS,KINT 1) = (DIRECT (POBJECT n_left))',
        '$entry_lookup(S_error.ARRAYS[n_args].ITEMS,KINT 2) = (DIRECT pvalue_flag)',
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


scalar.sources, scalar.literal, scalar.strict, scalar.PREFIX = sources, literal, strict, PREFIX
packet.sources, packet.prepare = sources, scalar.prepare
packet_process = packet.process


def process(command, directory, timeout, cwd):
    if directory.parent.name == 'quiet-object-false-and-late-truthy-duplicate':
        timeout = 240
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
