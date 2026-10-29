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
    'terminal-allocator-mode-keeps-request-data-and-first-duplicate': {
        'source': original('false'),
        'stage': 'S.TODO = [OUTPUT_DRAIN pobdrain] -- if S.OUTPUTBUFFERS = eps',
        'checks': [
            'S.CURRENT = eps /\\ S.FRAMES = eps /\\ S.REQUEST = eps',
            'S.COMPLETION = NORMAL /\\ pobdrain.COMPLETION = NORMAL',
            '~$executor_free_endpoint(S)',
            '$executor_allocator_fast(S.REQUEST)',
            'S_done = $drive_steps(S, 1)',
            'S_done.COMPLETION = NORMAL /\\ S_done.EXITSTATUS = 0',
            'S_done.EVENTS = [OUTPUT $ptascii("B|T|H:final-primary|P|A|")]',
            '$executor_free_endpoint(S_done)',
            'preqbytes_file = $call_sourcefile(S.FILES, PORIGIN 0 eps)',
            'preqbytes_allocator = $ptascii("USE_ZEND_ALLOC")',
            'Q = {ENV eps, ARGV [preqbytes_file], FILE preqbytes_file, SECONDS 0, MICROSECONDS 0, VARIABLES $ptascii("EGPCS"), JIT true, CWD eps}',
            '$request_valid(Q)',
            '$executor_allocator_fast((Q))',
            'Q_one = Q[.ENV = [(preqbytes_allocator, $ptascii("1"))]]',
            '$request_valid(Q_one)',
            '$executor_allocator_fast((Q_one))',
            'Q_zero = Q[.ENV = [(preqbytes_allocator, $ptascii("0"))]]',
            '$request_valid(Q_zero)',
            '~$executor_allocator_fast((Q_zero))',
            'Q_first_one = Q[.ENV = [(preqbytes_allocator, $ptascii("1")), (preqbytes_allocator, $ptascii("0"))]]',
            '$request_valid(Q_first_one)',
            '$executor_allocator_fast((Q_first_one))',
            'Q_first_zero = Q[.ENV = [(preqbytes_allocator, $ptascii("0")), (preqbytes_allocator, $ptascii("1"))]]',
            '$request_valid(Q_first_zero)',
            '~$executor_allocator_fast((Q_first_zero))',
            'Q_large = Q[.ENV = [(preqbytes_allocator, $ptascii("4294967296"))]]',
            '$request_valid(Q_large)',
            '$executor_allocator_fast((Q_large))',
            'Q_signed = Q[.ENV = [(preqbytes_allocator, [9] ++ $ptascii("-2tail"))]]',
            '$request_valid(Q_signed)',
            '$executor_allocator_fast((Q_signed))',
            'Q_off = Q[.ENV = [(preqbytes_allocator, $ptascii("off"))]]',
            '$request_valid(Q_off)',
            '~$executor_allocator_fast((Q_off))',
            'Q_empty = Q[.ENV = [(preqbytes_allocator, eps)]]',
            '$request_valid(Q_empty)',
            '~$executor_allocator_fast((Q_empty))',
            'Q_hex = Q[.ENV = [(preqbytes_allocator, $ptascii("0x1"))]]',
            '$request_valid(Q_hex)',
            '~$executor_allocator_fast((Q_hex))',
            '$output_executor_finish(S[.REQUEST = (Q_zero)]) = S[.REQUEST = (Q_zero)]',
            'S_slow = S_done[.REQUEST = (Q_zero)]',
            'S_refused = $output_executor_finish(S_slow)',
            'S_refused.COMPLETION = UNSUPPORTED "nonfast executor table and storage release"',
            'S_refused.REQUEST = (Q_zero)',
            'S_refused.EVENTS = S_slow.EVENTS /\\ S_refused.ALLOCATIONS = S_slow.ALLOCATIONS',
            'S_refused.DESTRUCTION.CALLED = S_slow.DESTRUCTION.CALLED',
            '$output_executor_finish(S_slow[.COMPLETION = BUDGET]) = S_slow[.COMPLETION = BUDGET]',
            '$drive_steps(S[.REQUEST = (Q_zero)], 1) = S_refused',
            '$drive_steps(S[.REQUEST = (Q_large)], 1) = S_done[.REQUEST = (Q_large)]',
            '$call_descriptors_valid(S_done)',
            '$destruction_state_valid(S_done)',
            '$heap_valid($heap_graph(S_done))',
        ],
    },
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
