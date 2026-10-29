#!/usr/bin/env python3
"""Independent reached pending-Throwable and raw-zoh ordering checks."""
import argparse
from pathlib import Path

import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
VALID = [
    '$call_descriptors_valid(S)',
    '$destruction_state_valid(S)',
    '$output_state_valid(S)',
    '$heap_valid($heap_graph(S))',
]
OBSERVER = [
    'pobdeactivate.CALL.BUFFER.HANDLER = (poutputhandler)',
    'poutputhandler.ZOH = POBJECT n_owner',
    '$objectprops_at(S.OBJECTPROPS, n_owner) = (ppropertyslot_owner*)',
    '$property_slot_at(ppropertyslot_owner*, $ptascii("after")) = (ppropertyslot_after)',
    'ppropertyslot_after.STATE = PROP_VALUE (DIRECT (POBJECT n_after))',
    '(HOBJECT n_after) <- S.ALLOCATIONS',
    '~(n_after <- S.DESTRUCTION.CALLED)',
    '$heap_owners($heap_graph(S), HOBJECT n_owner) = 1',
    '$heap_owners($heap_graph(S), HOBJECT n_after) = 1',
]


def source(name):
    return (HERE / ('output_pending_release_' + name + '.php')).read_text()


def prefix(name, value):
    return f'{name}[0:{len(value)}] = $ptascii("{value}")'


review.ROOT = ROOT
review.CASES = {
    'peer-reported-pending-root-still-retains-trace-child': {
        'source': source('peer'),
        'stage': 'S.TODO = [OUTPUT_FINAL_PENDING pobdeactivate n_pending true]',
        'checks': [
            'S.CURRENT = eps /\\ S.FRAMES = eps /\\ S.ORIGIN = eps',
            'S.COMPLETION = NORMAL /\\ S.EXITSTATUS = 255',
            'S.RESULT = KNOWN PNULL /\\ S.BASE = BASE_VALUE (KNOWN PNULL)',
            'S.OUTPUTBUFFERS = [poutputbuffer_upper, poutputbuffer_lower]',
            'poutputbuffer_upper.BYTES = $ptascii("T|")',
            'poutputbuffer_lower.BYTES = $ptascii("B|")',
            'pobdeactivate.COMPLETION = REQUESTFATAL $ptascii("Exception") $ptascii("trace-owned") 25',
            'S.EVENTS = [STDERR preqbytes_report]',
            prefix('preqbytes_report', 'Fatal error: Uncaught Exception: trace-owned in '),
            '$throwable_field(S, n_pending, "string") = PSTRING preqbytes_cached',
            'preqbytes_cached =/= eps',
            '$heap_owners($heap_graph(S), HOBJECT n_pending) = 1',
            '$heap_count(HOBJECT n_pending, $task_nodes(OUTPUT_FINAL_PENDING pobdeactivate n_pending true)) = 1',
            '$heap_count(HOBJECT n_pending, $task_nodes(OUTPUT_FINAL_PENDING pobdeactivate n_pending false)) = 0',
            '$throwable_field(S, n_pending, "trace") = PARRAY n_trace',
            '$entry_lookup(S.ARRAYS[n_trace].ITEMS, KINT 0) = (DIRECT (PARRAY n_frame))',
            '$trace_array_field(S, n_frame, $ptascii("args")) = PARRAY n_args',
            '$entry_lookup(S.ARRAYS[n_args].ITEMS, KINT 0) = (DIRECT (POBJECT n_child))',
            '$object_name(S, n_child) = $ptascii("TraceOwnedOB03")',
            '(HOBJECT n_child) <- S.ALLOCATIONS',
            '~(n_child <- S.DESTRUCTION.CALLED)',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 1',
            '$lookup(S.ENV, $ptascii("stage")) = (n_stage)',
            'S.STORE[n_stage] = DEFINED pvalue_stage',
            '$string_bytes(pvalue_stage) = ($ptascii("pending"))',
            *OBSERVER,
            '$object_name(S, n_after) = $ptascii("AfterZohOB03")',
            '$ob_user_running(S) /\\ $output_final_destructors(S)',
            '$call_task_valid(S, OUTPUT_FINAL_PENDING pobdeactivate n_pending true)',
            '~$output_pending_active(S[.TODO = eps], pobdeactivate)',
            '~$call_task_valid(S[.OUTPUTBUFFERS = eps], OUTPUT_FINAL_PENDING pobdeactivate n_pending true)',
            '~$call_task_valid(S, OUTPUT_FINAL_PENDING pobdeactivate[.COMPLETION = NORMAL] n_pending true)',
            'S_wrong_cause = $throwable_constructor_field(S, n_pending, "message", PSTRING $ptascii("wrong-cause"))',
            '~$call_task_valid(S_wrong_cause, OUTPUT_FINAL_PENDING pobdeactivate n_pending true)',
            *VALID,
        ],
    },
    'peer-child-cleanup-has-no-pending-exception-and-keeps-output-running': {
        'source': source('peer'),
        'stage': 'S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail* '
                 '-- if $object_name(S, pdestructorcall.OBJECT) = $ptascii("TraceOwnedOB03") '
                 '-- if pdestructorcall.OPERATION = (pdestructionoperation) '
                 '-- if pdestructionoperation.SOURCE = OUTPUT_FINAL_PENDING pobdeactivate n_pending true',
        'checks': [
            'S.COMPLETION = NORMAL /\\ S.EXITSTATUS = 255',
            'S.SHUTDOWN.PHASE = SHUTDOWN_DONE /\\ S.DESTRUCTION.PHASE = DESTRUCTION_DONE',
            'S.OUTPUTBUFFERS = [poutputbuffer_upper, poutputbuffer_lower]',
            'poutputbuffer_upper.BYTES = $ptascii("T|")',
            'poutputbuffer_lower.BYTES = $ptascii("B|")',
            'pdestructorcall.CALLER = eps /\\ ~pdestructorcall.USER',
            'pdestructorcall.PENDING = eps /\\ pdestructionoperation.PENDING = eps',
            'pdestructionoperation.COMPLETION = NORMAL',
            'pdestructorcall.OBJECT <- S.DESTRUCTION.CALLED',
            '$ob_user_running(S) /\\ $output_final_destructors(S)',
            '$eager_operation_source_guard(S, pdestructionoperation)',
            '$destructor_enter_valid(S, pdestructorcall)',
            '$lookup(S.ENV, $ptascii("stage")) = (n_stage)',
            'S.STORE[n_stage] = DEFINED pvalue_stage',
            '$string_bytes(pvalue_stage) = ($ptascii("pending"))',
            *OBSERVER,
            *VALID,
            'S_zero = $drive_steps(S, 0)',
            'S_zero.COMPLETION = BUDGET /\\ S_zero.TODO = S.TODO',
            'S_zero.ALLOCATIONS = S.ALLOCATIONS /\\ S_zero.DESTRUCTION = S.DESTRUCTION',
            'S_done = $drive_steps(S, 600)',
            '$drive_steps(S_zero[.COMPLETION = NORMAL], 600) = S_done',
            'S_done.COMPLETION = pobdeactivate.COMPLETION',
            'S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps',
            'S_done.OUTPUTBUFFERS = eps /\\ S_done.EXITSTATUS = 255',
            'S.EVENTS = [STDERR preqbytes_report]',
            'S_done.EVENTS = [STDERR preqbytes_report, OUTPUT $ptascii("A:"), OUTPUT $ptascii("released"), OUTPUT $ptascii("|")]',
            '~((HOBJECT n_after) <- S_done.ALLOCATIONS)',
            '$call_descriptors_valid(S_done)',
            '$destruction_state_valid(S_done)',
            '$heap_valid($heap_graph(S_done))',
        ],
    },
    'secondary-fatal-is-reported-before-raw-owner-observer': {
        'source': source('throw'),
        'stage': 'S.TODO = [OUTPUT_FINAL_DEACTIVATE pobdeactivate] '
                 '-- if pobdeactivate.INDEX = 0',
        'checks': [
            'S.CURRENT = eps /\\ S.FRAMES = eps /\\ S.ORIGIN = eps',
            'S.COMPLETION = NORMAL /\\ S.EXITSTATUS = 255',
            'S.OUTPUTBUFFERS = eps',
            '~$ob_user_running(S)',
            'pobdeactivate.COMPLETION = REQUESTFATAL $ptascii("Exception") $ptascii("pending-destructor") 3',
            'S.EVENTS = [STDERR preqbytes_first, STDERR preqbytes_second]',
            prefix('preqbytes_first', 'Fatal error: Uncaught Exception: pending-release in '),
            prefix('preqbytes_second', 'Fatal error: Uncaught Exception: pending-destructor in '),
            *OBSERVER,
            '$object_name(S, n_after) = $ptascii("AfterPendingOB03")',
            'S.DESTRUCTION.ABANDONED = [pdestructioncleanup]',
            'pdestructioncleanup.SOURCE = DESTRUCTOR_RESULT pdestructorcall',
            'pdestructorcall.OPERATION = (pdestructionoperation)',
            'pdestructionoperation.SOURCE = OUTPUT_FINAL_PENDING pobdeactivate_original n_original true',
            'pobdeactivate_original.COMPLETION = REQUESTFATAL $ptascii("Exception") $ptascii("pending-release") 9',
            '$eager_cleanup_valid(S, pdestructioncleanup)',
            'pdestructorcall_wrong = pdestructorcall[.OPERATION = (pdestructionoperation[.SOURCE = OUTPUT_FINAL_PENDING pobdeactivate_original[.COMPLETION = NORMAL] n_original true])]',
            'pdestructioncleanup_wrong = pdestructioncleanup[.SOURCE = DESTRUCTOR_RESULT pdestructorcall_wrong]',
            '~$eager_cleanup_valid(S[.DESTRUCTION.ABANDONED = [pdestructioncleanup_wrong]], pdestructioncleanup_wrong)',
            '$output_deactivate_active(S, pobdeactivate)',
            *VALID,
            'S_done = $drive_steps(S, 600)',
            'S_done.COMPLETION = pobdeactivate.COMPLETION',
            'S_done.TODO = eps /\\ S_done.OUTPUTBUFFERS = eps',
            'S_done.EVENTS = [STDERR preqbytes_first, STDERR preqbytes_second, OUTPUT $ptascii("A|")]',
            'n_after <- S_done.DESTRUCTION.CALLED',
            '~((HOBJECT n_owner) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_after) <- S_done.ALLOCATIONS)',
            '$call_descriptors_valid(S_done)',
            '$destruction_state_valid(S_done)',
            '$heap_valid($heap_graph(S_done))',
        ],
    },
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case) else 1)
