#!/usr/bin/env python3
"""Independent reached request-end FINAL and lower-route checks."""
import argparse

import fiber_state_review as review


def source(name):
    return (review.ROOT / 'tests/semantics' / name).read_text()


BASE_VALID = [
    '$call_descriptors_valid(S)',
    '$destruction_state_valid(S)',
    '$output_state_valid(S)',
    '$heap_valid($heap_graph(S))',
]
DONE = [
    'S_done = $drive(S, 4000)',
    'S_done.COMPLETION = NORMAL',
    'S_done.TODO = eps',
    'S_done.OUTPUTBUFFERS = eps',
    '$call_descriptors_valid(S_done)',
    '$destruction_state_valid(S_done)',
    '$heap_valid($heap_graph(S_done))',
]

review.CASES = {
    'final-invokable-entered-top-visible': {
        'source': source('output_request_end_peer_nested_invokable.php'),
        'stage': (
            'S.CURRENT = (pcallcontext) '
            '-- if $ob_user_context(pcallcontext, S.CURRENT, S.FRAMES) = (pobinvoke) '
            '-- if pobinvoke.CALL = OB_FINAL pobdrain'),
        'checks': [
            'S.DESTRUCTION.PHASE = DESTRUCTION_DONE',
            'S.SHUTDOWN.PHASE = SHUTDOWN_DONE',
            'S.OUTPUTBUFFERS = [poutputbuffer_upper, poutputbuffer_lower]',
            'poutputbuffer_upper.ID = 1 /\\ poutputbuffer_lower.ID = 0',
            'poutputbuffer_upper.HANDLER = (poutputhandler)',
            'pobdrain.SOURCE = poutputhandler',
            'pobdrain.IDS = [1,0]',
            'pobinvoke.BUFFER.ID = 1 /\\ pobinvoke.PHASE = 9',
            'pobinvoke.INPUT = PSTRING_CARRIER (REQUEST_STRING n_input) ([65,124,68,124])',
            'poutputhandler.ZOH = POBJECT n_handler',
            'n_handler <- S.DESTRUCTION.CALLED',
            '$heap_owners($heap_graph(S), HOBJECT n_handler) = 1',
            '$ob_user_context_valid(S, pcallcontext)',
            'pcallcontext.CALLSITE = eps /\\ pcallcontext.LINE = $(-1)',
            '$output_drain_active(S, pobdrain)',
            '$output_final_destructors(S)',
            'S.FRAMES = pframe :: pframe_tail*',
            'pframe.TODO = [OB_USER_RESULT pobinvoke, OUTPUT_DRAIN pobdrain]',
            'S_detached = S[.FRAMES = pframe[.TODO = [OB_USER_RESULT pobinvoke]] :: pframe_tail*]',
            '~$output_drain_active(S_detached, pobdrain)',
            '~$ob_user_invoke_valid(S, pobinvoke[.CALL = OB_FINAL pobdrain[.IDS = [999]]])',
            *BASE_VALID, *DONE,
        ],
    },
    'final-invokable-postpop-owner': {
        'source': source('output_request_end_peer_nested_invokable.php'),
        'stage': (
            'S.TODO = (OUTPUT_WRITE pobwrite) :: ptask_tail* '
            '-- if pobwrite.CALLER = OUTPUT_FINAL pobdrain '
            '-- if pobwrite.FINISH = OUTPUT_USER_DONE pobinvoke poutputbuffer_upper poboutput false '
            '-- if pobinvoke.CALL = OB_FINAL pobdrain'),
        'checks': [
            'S.DESTRUCTION.PHASE = DESTRUCTION_DONE',
            'S.OUTPUTBUFFERS = [poutputbuffer_lower]',
            'poutputbuffer_lower.ID = 0 /\\ poutputbuffer_upper.ID = 1',
            'poutputbuffer_upper.HANDLER = (poutputhandler)',
            'poutputhandler.ZOH = POBJECT n_handler',
            'pobdrain.IDS = [1,0] /\\ pobwrite.IDS = [0]',
            'pobwrite.TAIL = [OUTPUT_DRAIN pobdrain_next]',
            '$output_drain_active(S, pobdrain)',
            '$output_drain_active(S, pobdrain_next)',
            '$output_write_valid(S, pobwrite)',
            '$heap_count(HOBJECT n_handler, $task_nodes(OUTPUT_WRITE pobwrite)) = 1',
            '$heap_count(HOBJECT n_handler, $output_roots(S.OUTPUTBUFFERS)) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_handler) = 1',
            '~$output_write_valid(S, pobwrite[.TAIL = eps])',
            '~$output_write_valid(S, pobwrite[.FINISH = OUTPUT_USER_DONE pobinvoke poutputbuffer_upper[.ID = 0] poboutput false])',
            'S_detached = S[.TODO = [OUTPUT_WRITE pobwrite]]',
            '~$output_drain_active(S_detached, pobdrain)',
            *BASE_VALID, *DONE,
            '~((HOBJECT n_handler) <- S_done.ALLOCATIONS)',
        ],
    },
    'final-default-to-positive-write': {
        'source': source('output_request_end_peer_default_to_positive.php'),
        'stage': (
            'S.TODO = (OB_USER_SEND pobinvoke 0) :: ptask_tail* '
            '-- if pobinvoke.CALL = OB_WRITE pobwrite '
            '-- if pobwrite.CALLER = OUTPUT_FINAL pobdrain '
            '-- if pobwrite.FINISH = OUTPUT_FINAL_DONE pobdrain poutputbuffer_upper'),
        'checks': [
            'S.DESTRUCTION.PHASE = DESTRUCTION_DONE',
            'S.OUTPUTBUFFERS = [poutputbuffer_lower]',
            'poutputbuffer_upper.ID = 1 /\\ poutputbuffer_upper.HANDLER = eps',
            'poutputbuffer_lower.ID = 0 /\\ poutputbuffer_lower.CHUNK = 2',
            'poutputbuffer_lower.BYTES = ([97,98])',
            'pobinvoke.BUFFER.ID = 0 /\\ pobinvoke.PHASE = 1',
            'pobdrain.IDS = [1,0] /\\ pobwrite.IDS = [0]',
            'pobwrite.TAIL = [OUTPUT_DRAIN pobdrain_next]',
            '$output_drain_active(S, pobdrain)',
            '$output_write_valid(S, pobwrite)',
            '$ob_user_send_valid(S, pobinvoke, 0)',
            '$output_final_destructors(S)',
            *BASE_VALID, *DONE,
        ],
    },
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case) else 1)
