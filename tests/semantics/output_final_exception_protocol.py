#!/usr/bin/env python3
"""Source-reached selected FINAL handler body and ignored-return bailout owners."""
import argparse
from pathlib import Path
import fiber_state_review as review
from fiber_state_review import VALID

HERE = Path(__file__).resolve().parent
review.ROOT = HERE.parents[1]


def original(name):
    return (HERE / ('output_final_exception_' + name + '.php')).read_text()


COMMON = [
    'S.CURRENT = eps /\\ S.FRAMES = eps /\\ S.ORIGIN = eps',
    'S.COMPLETION = NORMAL /\\ S.EXITSTATUS = 255',
    'S.OUTPUTBUFFERS = eps /\\ S.EXCEPTIONHANDLER = eps',
    'S.OBJECTS[3] = THROWABLE pthrowable_original',
    '$throwable_field(S, 3, "message") = pvalue_original',
    '$string_bytes(pvalue_original) = ($ptascii("final-primary"))',
    '$throwable_field(S, 3, "string") = PSTRING eps',
    '$heap_owners($heap_graph(S), HOBJECT 3) = 1',
    '$heap_count(HOBJECT 3, $eager_abandoned_roots(S.DESTRUCTION.ABANDONED)) = 1',
    '(HOBJECT 2) <- S.ALLOCATIONS /\\ ~(2 <- S.DESTRUCTION.CALLED)',
    '$heap_owners($heap_graph(S), HOBJECT 2) = 1',
    '$heap_owners($heap_graph(S), HOBJECT 0) = 1',
    '$heap_owners($heap_graph(S), HOBJECT 1) = 1',
    '~(1 <- S.DESTRUCTION.CALLED)',
    'S.EVENTS = [STDERR preqbytes_fatal]',
    '$call_task_valid(S, OUTPUT_FINAL_DEACTIVATE pobdeactivate)',
    '$destruction_state_valid(S)',
    *VALID,
]
FINISH = [
    'S_zero = $drive_steps(S, 0)',
    'S_zero.COMPLETION = BUDGET /\\ S_zero.TODO = S.TODO',
    'S_zero.ALLOCATIONS = S.ALLOCATIONS',
    'S_done = $drive_steps(S, 600)',
    '$drive_steps(S_zero[.COMPLETION = NORMAL], 600) = S_done',
    'S_done.COMPLETION = pobdeactivate.COMPLETION /\\ S_done.EXITSTATUS = 255',
    'S_done.TODO = eps /\\ S_done.OUTPUTBUFFERS = eps',
    'S_done.EVENTS = [STDERR preqbytes_fatal, OUTPUT $ptascii("A|")]',
    '~((HOBJECT 0) <- S_done.ALLOCATIONS) /\\ ~((HOBJECT 1) <- S_done.ALLOCATIONS)',
    '(HOBJECT 2) <- S_done.ALLOCATIONS /\\ ~(2 <- S_done.DESTRUCTION.CALLED)',
    '(HOBJECT 3) <- S_done.ALLOCATIONS',
    '$heap_owners($heap_graph(S_done), HOBJECT 3) = 1',
    '$call_descriptors_valid(S_done)',
    '$destruction_state_valid(S_done)',
    '$heap_valid($heap_graph(S_done))',
]
review.CASES = {
    'body-throw-keeps-original-c-local-through-raw-release': {
        'source': original('throw'),
        'stage': 'S.TODO = [OUTPUT_FINAL_DEACTIVATE pobdeactivate] -- if pobdeactivate.INDEX = 0',
        'checks': [
            *COMMON,
            'S.DESTRUCTION.ABANDONED = [pdestructioncleanup]',
            'pdestructioncleanup.SOURCE = EXCEPTION_HANDLER_RESULT pexceptioncall',
            'pexceptioncall.OBJECT = 3 /\\ pexceptioncall.ORIGIN = eps',
            '~pdestructioncleanup.RELEASED',
            '$eager_cleanup_valid(S, pdestructioncleanup)',
            'pdestructioncleanup_wrong = pdestructioncleanup[.SOURCE = EXCEPTION_HANDLER_RESULT pexceptioncall[.OBJECT = 2]]',
            '~$eager_cleanup_valid(S, pdestructioncleanup_wrong)',
            *FINISH,
        ],
    },
    'ignored-return-dtor-bailout-keeps-both-real-receivers': {
        'source': original('result_throw'),
        'stage': 'S.TODO = [OUTPUT_FINAL_DEACTIVATE pobdeactivate] -- if pobdeactivate.INDEX = 0',
        'checks': [
            *COMMON,
            '$object_name(S, 4) = $ptascii("HandlerResultOB04")',
            '(HOBJECT 4) <- S.ALLOCATIONS /\\ 4 <- S.DESTRUCTION.CALLED',
            '$heap_owners($heap_graph(S), HOBJECT 4) = 2',
            '$heap_count(HOBJECT 4, $eager_abandoned_roots(S.DESTRUCTION.ABANDONED)) = 2',
            'S.DESTRUCTION.ABANDONED = [pdestructioncleanup_original, pdestructioncleanup_return]',
            'pdestructioncleanup_original.SOURCE = EXCEPTION_HANDLER_RESULT pexceptioncall',
            'pexceptioncall.OBJECT = 3',
            'pdestructioncleanup_return.SOURCE = DESTRUCTOR_RESULT pdestructorcall',
            'pdestructorcall.OBJECT = 4 /\\ ~pdestructorcall.USER',
            'pdestructorcall.OPERATION = (pdestructionoperation)',
            'pdestructionoperation.SOURCE = EXCEPTION_HANDLER_RESULT pexceptioncall',
            '$eager_cleanup_valid(S, pdestructioncleanup_original)',
            '$eager_cleanup_valid(S, pdestructioncleanup_return)',
            *FINISH,
            '(HOBJECT 4) <- S_done.ALLOCATIONS',
            '$heap_owners($heap_graph(S_done), HOBJECT 4) = 2',
        ],
    },
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case) else 1)
