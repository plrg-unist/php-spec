#!/usr/bin/env python3
"""Independent reached checks for FINAL fatal buffer deactivation."""
import argparse

import fiber_state_review as review


SOURCE = (review.ROOT / 'tests/semantics/output_final_throw_late_capture.php').read_text()
VALID = [
    '$call_descriptors_valid(S)',
    '$destruction_state_valid(S)',
    '$output_state_valid(S)',
    '$heap_valid($heap_graph(S))',
]

review.CASES = {
    'late-fatal-cache-before-active-off-release': {
        'source': SOURCE,
        'stage': 'S.TODO = [OUTPUT_FINAL_DEACTIVATE pobdeactivate] -- if pobdeactivate.INDEX = 0',
        'checks': [
            'S.CURRENT = eps /\\ S.FRAMES = eps',
            'S.COMPLETION = NORMAL /\\ S.EXITSTATUS = 255',
            'S.SHUTDOWN.PHASE = SHUTDOWN_DONE /\\ S.DESTRUCTION.PHASE = DESTRUCTION_DONE',
            'S.OUTPUTBUFFERS = eps',
            'pobdeactivate.BUFFERS = [poutputbuffer_upper, poutputbuffer_lower]',
            'poutputbuffer_upper.ID = 1 /\\ poutputbuffer_lower.ID = 0 /\\ poutputbuffer_lower.HANDLER = eps',
            'poutputbuffer_upper.HANDLER = (poutputhandler)',
            'poutputhandler.ZOH = POBJECT n_owner',
            '$object_name(S, n_owner) = $ptascii("LateOwnerOB02")',
            'poutputbuffer_lower.BYTES = $ptascii("B|")',
            'pobdeactivate.CALL.CALL = OB_FINAL pobdrain',
            'pobdrain.IDS = [1,0]',
            '$shutdown_frozen(pobdeactivate.COMPLETION)',
            'n_objects = |S.OBJECTS|',
            'n_exception = $nabs($(n_objects - 1))',
            'S.OBJECTS[n_exception] = THROWABLE pthrowable',
            '$throwable_field(S, n_exception, "string") = PSTRING preqbytes_cached',
            'preqbytes_cached =/= eps',
            '$output_deactivate_active(S, pobdeactivate)',
            '$call_task_valid(S, OUTPUT_FINAL_DEACTIVATE pobdeactivate)',
            '$heap_count(HOBJECT n_owner, $task_nodes(OUTPUT_FINAL_DEACTIVATE pobdeactivate)) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_owner) = 1',
            '~$output_deactivate_active(S, pobdeactivate[.INDEX = 1])',
            '~$output_deactivate_valid(S[.OUTPUTBUFFERS = [poutputbuffer_lower]], pobdeactivate)',
            *VALID,
        ],
    },
    'late-fatal-upper-retired-before-lower': {
        'source': SOURCE,
        'stage': 'S.TODO = [OUTPUT_FINAL_DEACTIVATE pobdeactivate] -- if pobdeactivate.INDEX = 1',
        'checks': [
            'S.CURRENT = eps /\\ S.FRAMES = eps',
            'S.COMPLETION = NORMAL /\\ S.EXITSTATUS = 255',
            'S.OUTPUTBUFFERS = eps',
            'pobdeactivate.BUFFERS = [poutputbuffer_upper, poutputbuffer_lower]',
            'poutputbuffer_upper.HANDLER = (poutputhandler)',
            'poutputhandler.ZOH = POBJECT n_owner',
            'poutputbuffer_lower.ID = 0 /\\ poutputbuffer_lower.HANDLER = eps',
            'poutputbuffer_lower.BYTES = $ptascii("B|")',
            '~((HOBJECT n_owner) <- S.ALLOCATIONS)',
            '$heap_count(HOBJECT n_owner, $task_nodes(OUTPUT_FINAL_DEACTIVATE pobdeactivate)) = 0',
            '$output_deactivate_active(S, pobdeactivate)',
            '$call_task_valid(S, OUTPUT_FINAL_DEACTIVATE pobdeactivate)',
            '~$output_deactivate_active(S, pobdeactivate[.INDEX = 0])',
            *VALID,
            'S_done = $drive_steps(S, 4000)',
            'S_done.TODO = eps /\\ S_done.OUTPUTBUFFERS = eps',
            'S_done.COMPLETION = pobdeactivate.COMPLETION',
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
