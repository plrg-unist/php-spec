#!/usr/bin/env python3
"""Source-reached final drain completion, budgets and callback-local cleanup."""
import argparse
from pathlib import Path
import fiber_state_review as review

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
VALID = ['$output_state_valid(S)', '$destruction_state_valid(S)',
         '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
RESUME = ['S_zero = $drive_steps(S, 0)', 'S_zero.COMPLETION = BUDGET',
          'S_zero.TODO = S.TODO', 'S_zero.ALLOCATIONS = S.ALLOCATIONS',
          'S_done = $drive_steps(S, 4000)',
          '$drive_steps(S_zero[.COMPLETION = NORMAL], 4000) = S_done',
          'S_done.OUTPUTBUFFERS = eps', 'S_done.CURRENT = eps',
          'S_done.FRAMES = eps', 'S_done.TODO = eps',
          'S_done.SHUTDOWN.PHASE = SHUTDOWN_DONE',
          'S_done.DESTRUCTION.PHASE = DESTRUCTION_DONE',
          'S_done.DESTRUCTION.CALLS = eps', 'S_done.DESTRUCTION.RELEASES = eps',
          'S_done.DESTRUCTION.FRAMES = eps', 'S_done.DESTRUCTION.OPERATIONS = eps',
          'S_done.DESTRUCTION.CLEANUPS = eps',
          '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))']


def source(name):
    return (HERE / ('output_request_end_' + name + '.php')).read_text()


CASES = {
    'saved-exit-completion-and-budget-resume': {
        'source': source('exit_integer'),
        'stage': 'S.TODO = [OUTPUT_DRAIN pobdrain]',
        'checks': [
            'pobdrain.COMPLETION = EXITED 7', 'S.COMPLETION = NORMAL',
            'S.SHUTDOWN.PHASE = SHUTDOWN_DONE',
            'S.DESTRUCTION.PHASE = DESTRUCTION_DONE',
            'S.OUTPUTBUFFERS = [poutputbuffer_upper, poutputbuffer_lower]',
            'pobdrain.IDS = [poutputbuffer_upper.ID, poutputbuffer_lower.ID]',
            'poutputbuffer_upper.HANDLER = (pobdrain.SOURCE)',
            'poutputbuffer_lower.HANDLER = eps',
            '$output_drain_owned(S, pobdrain)', '$output_drain_active(S, pobdrain)',
            '$call_task_valid(S, OUTPUT_DRAIN pobdrain)',
            '~$output_drain_active(S[.TODO = eps], pobdrain)',
            '~$call_task_valid(S, OUTPUT_DRAIN pobdrain[.IDS = eps])',
            '~$output_drain_valid(S, pobdrain[.COMPLETION = BUDGET])',
            '~$output_drain_valid(S, pobdrain[.SOURCE = pobdrain.SOURCE[.NAME = $ptascii("wrong")]])',
            '$task_nodes(OUTPUT_DRAIN pobdrain) = $operand_nodes(pobdrain.VALUE) ++ $base_nodes(pobdrain.BASE)',
            *VALID, *RESUME, 'S_done.COMPLETION = EXITED 7',
            'S_done.RESULT = pobdrain.VALUE', 'S_done.BASE = pobdrain.BASE',
            'S_done.ORIGIN = pobdrain.ORIGIN',
        ],
    },
    'final-callback-local-destructor-after-request-phase': {
        'source': source('final_local_destructor'),
        'stage': 'S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail* '
                 '-- if S.DESTRUCTION.PHASE = DESTRUCTION_DONE '
                 '-- if $object_name(S, pdestructorcall.OBJECT) = $ptascii("LocalFinalOB01")',
        'checks': [
            '$output_final_destructors(S)', '$destructor_operational(S)',
            '$ob_user_running(S)',
            'pdestructorcall.OBJECT <- S.DESTRUCTION.CALLED',
            '(HOBJECT pdestructorcall.OBJECT) <- S.ALLOCATIONS',
            '~pdestructorcall.STORE',
            'S.DESTRUCTION.CALLS = pdestructorcall :: pdestructorcall_tail*',
            '$destructor_enter_valid(S, pdestructorcall)',
            '~$output_final_destructors(S[.TODO = eps][.FRAMES = eps][.DESTRUCTION.OPERATIONS = eps])',
            '~$destructor_operational(S[.TODO = eps][.FRAMES = eps][.DESTRUCTION.OPERATIONS = eps])',
            *VALID, *RESUME, 'S_done.COMPLETION = NORMAL',
            'pdestructorcall.OBJECT <- S_done.DESTRUCTION.CALLED',
            '~((HOBJECT pdestructorcall.OBJECT) <- S_done.ALLOCATIONS)',
            '~$output_final_destructors(S_done)', '~$destructor_operational(S_done)',
        ],
    },
    'sole-global-object-retires-before-final-but-scalar-survives': {
        'source': source('final_global_retirement'),
        'stage': 'S.TODO = (OB_USER_SEND pobinvoke 0) :: ptask_tail* '
                 '-- if pobinvoke.CALL = OB_FINAL pobdrain',
        'checks': [
            'S.DESTRUCTION.PHASE = DESTRUCTION_DONE',
            'S.SHUTDOWN.PHASE = SHUTDOWN_DONE',
            '~$destructor_classes(S.CLASSES)',
            'S.OBJECTS = [STDINSTANCE]',
            '~((HOBJECT 0) <- S.ALLOCATIONS)',
            '0 <- S.DESTRUCTION.CALLED',
            '$heap_owners($heap_graph(S), HOBJECT 0) = 0',
            '$lookup(S.ENV, $ptascii("object")) = eps',
            '$lookup(S.ENV, $ptascii("scalar")) = (n_scalar)',
            'S.STORE[n_scalar] = DEFINED pvalue_scalar',
            '$string_bytes(pvalue_scalar) = ($ptascii("S|"))',
            '~$output_request_destructors(S)',
            '~$destructor_operational(S)',
            '$output_final_destructors(S)',
            'pobinvoke.PHASE = 9',
            '$ob_user_send_valid(S, pobinvoke, 0)',
            *VALID, *RESUME, 'S_done.COMPLETION = NORMAL',
            '~((HOBJECT 0) <- S_done.ALLOCATIONS)',
            '~$output_request_destructors(S_done)',
            '~$destructor_operational(S_done)',
        ],
    },

}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    assert not args.case or set(args.case) <= CASES.keys()
    review.ROOT = ROOT
    review.CASES = CASES
    for name in args.case or list(CASES):
        assert review.run([name])
