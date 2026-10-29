#!/usr/bin/env python3
"""Independent reached handled-FINAL cleanup, forwarding and owner checks."""
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


def source(name):
    return (HERE / ('output_final_exception_' + name + '.php')).read_text()


review.ROOT = ROOT
review.CASES = {
    'peer-handler-return-and-original-retire-before-undefined-result': {
        'source': source('peer'),
        'stage': 'S.TODO = [OUTPUT_FINAL_EXCEPTION pobinvoke true, OUTPUT_DRAIN pobdrain]',
        'checks': [
            'pobinvoke.CALL = OB_FINAL pobdrain',
            'S.CURRENT = eps /\\ S.FRAMES = eps /\\ S.ORIGIN = eps',
            'S.COMPLETION = NORMAL /\\ S.EXITSTATUS = 0',
            'S.RESULT = KNOWN PNULL /\\ S.BASE = BASE_VALUE (KNOWN PNULL)',
            'S.EXCEPTIONHANDLER = eps /\\ S.EXCEPTIONHANDLERS = eps',
            'S.EVENTS = eps /\\ S.DESTRUCTION.ABANDONED = eps',
            'S.DESTRUCTION.CALLS = eps /\\ S.DESTRUCTION.RELEASES = eps',
            'S.DESTRUCTION.FRAMES = eps /\\ S.DESTRUCTION.OPERATIONS = eps /\\ S.DESTRUCTION.CLEANUPS = eps',
            'S.OUTPUTBUFFERS = [poutputbuffer_upper, poutputbuffer_lower]',
            'poutputbuffer_upper.BYTES = $ptascii("T|H:1|C|R|P|")',
            'poutputbuffer_lower.BYTES = $ptascii("B|")',
            'poutputbuffer_upper.HANDLER = (poutputhandler)',
            'poutputhandler.ZOH = POBJECT n_raw',
            '$objectprops_at(S.OBJECTPROPS, n_raw) = (ppropertyslot_raw*)',
            '$property_slot_at(ppropertyslot_raw*, $ptascii("after")) = (ppropertyslot_after)',
            'ppropertyslot_after.STATE = PROP_VALUE (DIRECT (POBJECT n_after))',
            '$object_name(S, n_after) = $ptascii("RawObserverOB04")',
            '~(n_after <- S.DESTRUCTION.CALLED)',
            '$heap_owners($heap_graph(S), HOBJECT n_raw) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_after) = 1',
            '$heap_count(HOBJECT n_raw, $task_nodes(OUTPUT_FINAL_EXCEPTION pobinvoke true)) = 0',
            '$ob_user_running(S) /\\ $output_final_destructors(S)',
            '$call_task_valid(S, OUTPUT_FINAL_EXCEPTION pobinvoke true)',
            'pobinvoke_owned = pobinvoke[.VALUE = POBJECT n_raw]',
            '~$call_task_valid(S[.TODO = [OUTPUT_FINAL_EXCEPTION pobinvoke_owned true, OUTPUT_DRAIN pobdrain]], OUTPUT_FINAL_EXCEPTION pobinvoke_owned true)',
            'z_wrong_phase = $(pobinvoke.PHASE + 1)',
            'pobinvoke_phase = pobinvoke[.PHASE = z_wrong_phase][.SENT = [KNOWN pobinvoke.INPUT, KNOWN (PINT z_wrong_phase)]]',
            '~$call_task_valid(S[.TODO = [OUTPUT_FINAL_EXCEPTION pobinvoke_phase true, OUTPUT_DRAIN pobdrain]], OUTPUT_FINAL_EXCEPTION pobinvoke_phase true)',
            'pobinvoke_input = pobinvoke[.INPUT = PSTRING $ptascii("wrong-input")][.SENT = [KNOWN (PSTRING $ptascii("wrong-input")), KNOWN (PINT pobinvoke.PHASE)]]',
            '~$call_task_valid(S[.TODO = [OUTPUT_FINAL_EXCEPTION pobinvoke_input true, OUTPUT_DRAIN pobdrain]], OUTPUT_FINAL_EXCEPTION pobinvoke_input true)',
            '~$call_task_valid(S[.TODO = [OUTPUT_FINAL_EXCEPTION pobinvoke true]], OUTPUT_FINAL_EXCEPTION pobinvoke true)',
            *VALID,
            'S_zero = $drive_steps(S, 0)',
            'S_zero.COMPLETION = BUDGET /\\ S_zero.TODO = S.TODO',
            'S_zero.ALLOCATIONS = S.ALLOCATIONS',
            'S_done = $drive_steps(S, 600)',
            '$drive_steps(S_zero[.COMPLETION = NORMAL], 600) = S_done',
            'S_done.COMPLETION = NORMAL /\\ S_done.EXITSTATUS = 0',
            'S_done.TODO = eps /\\ S_done.OUTPUTBUFFERS = eps',
            'S_done.EVENTS = [OUTPUT $ptascii("B|T|H:1|C|R|P|A|")]',
            '~((HOBJECT n_raw) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_after) <- S_done.ALLOCATIONS)',
            '$call_descriptors_valid(S_done)',
            '$destruction_state_valid(S_done)',
            '$heap_valid($heap_graph(S_done))',
        ],
    },
    'lower-user-route-keeps-raw-top-through-forwarding': {
        'source': source('lower_peer'),
        'stage': 'S.TODO = (OUTPUT_WRITE pobwrite) :: ptask_tail* '
                 '-- if pobwrite.CALLER = OUTPUT_FINAL pobdrain '
                 '-- if pobwrite.FINISH = OUTPUT_FINAL_DONE pobdrain poutputbuffer_raw '
                 '-- if pobwrite.INDEX = 0 '
                 '-- if poutputbuffer_raw.ID = 1',
        'checks': [
            'S.CURRENT = eps /\\ S.FRAMES = eps',
            'S.COMPLETION = NORMAL /\\ S.EXITSTATUS = 0',
            'S.EVENTS = eps /\\ S.DESTRUCTION.ABANDONED = eps',
            'S.OUTPUTBUFFERS = [poutputbuffer_lower]',
            'poutputbuffer_lower.ID = 0 /\\ poutputbuffer_lower.HANDLER = (poutputhandler_lower)',
            'poutputbuffer_lower.BYTES = $ptascii("B|")',
            'pobwrite.BYTES = $ptascii("T|H:1|P|")',
            'poutputbuffer_raw.BYTES = pobwrite.BYTES',
            '$long_and(poutputbuffer_raw.FLAGS, 12288) = 12288',
            'poutputbuffer_raw.HANDLER = (poutputhandler_raw)',
            'poutputhandler_raw.ZOH = POBJECT n_raw',
            '$objectprops_at(S.OBJECTPROPS, n_raw) = (ppropertyslot_raw*)',
            '$property_slot_at(ppropertyslot_raw*, $ptascii("after")) = (ppropertyslot_after)',
            'ppropertyslot_after.STATE = PROP_VALUE (DIRECT (POBJECT n_after))',
            '$object_name(S, n_after) = $ptascii("LowerRawObserverOB04")',
            '~(n_after <- S.DESTRUCTION.CALLED)',
            '$heap_owners($heap_graph(S), HOBJECT n_raw) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_after) = 1',
            '$heap_count(HOBJECT n_raw, $task_nodes(OUTPUT_WRITE pobwrite)) = 1',
            '~$ob_user_running(S)',
            '$output_write_valid(S, pobwrite)',
            'pobwrite_wrong = pobwrite[.BYTES = $ptascii("wrong-bytes")]',
            '~$output_write_valid(S[.TODO = (OUTPUT_WRITE pobwrite_wrong) :: ptask_tail*], pobwrite_wrong)',
            *VALID,
            'S_done = $drive_steps(S, 600)',
            'S_done.COMPLETION = NORMAL /\\ S_done.EXITSTATUS = 0',
            'S_done.TODO = eps /\\ S_done.OUTPUTBUFFERS = eps',
            'S_done.EVENTS = [OUTPUT $ptascii("L[B|T|H:1|P|A|]")]',
            '~((HOBJECT n_raw) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_after) <- S_done.ALLOCATIONS)',
            '$call_descriptors_valid(S_done)',
            '$destruction_state_valid(S_done)',
            '$heap_valid($heap_graph(S_done))',
        ],
    },
    'warning-abort-retains-the-real-original-c-owner': {
        'source': source('owner_peer'),
        'stage': 'S.TODO = [OUTPUT_FINAL_DEACTIVATE pobdeactivate] '
                 '-- if pobdeactivate.INDEX = 0',
        'checks': [
            'S.CURRENT = eps /\\ S.FRAMES = eps /\\ S.ORIGIN = eps',
            'S.COMPLETION = NORMAL /\\ S.EXITSTATUS = 255',
            'S.OUTPUTBUFFERS = eps /\\ ~$ob_user_running(S)',
            'S.OBJECTS[3] = THROWABLE pthrowable_original',
            'pthrowable_original.KIND = "Exception"',
            '$throwable_field(S, 3, "message") = pvalue_original_message',
            '$string_bytes(pvalue_original_message) = ($ptascii("cursor-primary"))',
            '$throwable_field(S, 3, "string") = PSTRING eps',
            '(HOBJECT 3) <- S.ALLOCATIONS',
            '$heap_owners($heap_graph(S), HOBJECT 3) = 1',
            '$heap_count(HOBJECT 3, $eager_abandoned_roots(S.DESTRUCTION.ABANDONED)) = 1',
            '$heap_count(HOBJECT 3, $task_nodes(OUTPUT_FINAL_DEACTIVATE pobdeactivate)) = 0',
            '$object_name(S, 2) = $ptascii("CursorTraceOwnerOB04")',
            '(HOBJECT 2) <- S.ALLOCATIONS /\\ ~(2 <- S.DESTRUCTION.CALLED)',
            '$heap_owners($heap_graph(S), HOBJECT 2) = 1',
            '$lookup(S.ENV, $ptascii("cursor_stage")) = (n_stage)',
            'S.STORE[n_stage] = DEFINED pvalue_stage',
            '$string_bytes(pvalue_stage) = ($ptascii("live"))',
            '$object_name(S, 0) = $ptascii("CursorFinalOwnerOB04")',
            '$object_name(S, 1) = $ptascii("CursorRawObserverOB04")',
            '(HOBJECT 1) <- S.ALLOCATIONS /\\ ~(1 <- S.DESTRUCTION.CALLED)',
            '$heap_owners($heap_graph(S), HOBJECT 0) = 1',
            '$heap_owners($heap_graph(S), HOBJECT 1) = 1',
            'S.EVENTS = [STDERR preqbytes_fatal]',
            'preqbytes_fatal[0:52] = $ptascii("Fatal error: Uncaught Exception: owner-secondary in ")',
            '$shutdown_frozen(pobdeactivate.COMPLETION)',
            *VALID,
            'S_done = $drive_steps(S, 600)',
            'S_done.COMPLETION = pobdeactivate.COMPLETION',
            'S_done.TODO = eps /\\ S_done.OUTPUTBUFFERS = eps',
            'S_done.EVENTS = [STDERR preqbytes_fatal, OUTPUT $ptascii("A:"), OUTPUT $ptascii("live"), OUTPUT $ptascii("|")]',
            '~((HOBJECT 0) <- S_done.ALLOCATIONS)',
            '~((HOBJECT 1) <- S_done.ALLOCATIONS)',
            '(HOBJECT 2) <- S_done.ALLOCATIONS /\\ ~(2 <- S_done.DESTRUCTION.CALLED)',
            '(HOBJECT 3) <- S_done.ALLOCATIONS',
            '$heap_owners($heap_graph(S_done), HOBJECT 3) = 1',
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
