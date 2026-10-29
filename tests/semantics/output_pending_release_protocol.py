#!/usr/bin/env python3
"""Reached pending Throwable decrement and active buffer cleanup checks."""
import argparse
from pathlib import Path
import fiber_state_review as review

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
review.ROOT = ROOT
review.CASES = {
    'sole-restored-final-throw-enters-pending-release': {
        'source': (HERE / 'output_pending_release_sole.php').read_text(),
        'stage': 'S.TODO = [THROW_SEARCH n, OB_USER_RESULT pobinvoke, OUTPUT_DRAIN pobdrain]',
        'checks': [
            'pobinvoke.CALL = OB_FINAL pobdrain',
            'S.COMPLETION = NORMAL /\\ ~S.OUTPUTBLOCKED',
            'S.CURRENT = eps /\\ S.FRAMES = eps /\\ S.EXCEPTIONHANDLER = eps',
            '$call_task_valid(S, OB_USER_RESULT pobinvoke)',
            '$throwable_live(S, n)',
            'S.OBJECTS[n] = THROWABLE pthrowable',
            '$throwable_field(S, n, "previous") = PNULL',
            '$ob_user_scalar($throwable_field(S, n, "message"))',
            '$throwable_terminal_renderable(S, n, eps)',
            '~$shutdown_render_ready(S[.COMPLETION = UNCAUGHT n])',
            '$output_final_throw_ready(S, pobinvoke, n)',
            'S_pending = $output_final_throw(S, pobinvoke, n)',
            'S_pending.TODO = [OUTPUT_FINAL_PENDING pobdeactivate n true]',
            '$output_pending_active(S_pending, pobdeactivate)',
            '$call_task_valid(S_pending, OUTPUT_FINAL_PENDING pobdeactivate n true)',
        ],
    },
    'sole-pending-drop-starts-real-release': {
        'source': (HERE / 'output_pending_release_sole.php').read_text(),
        'stage': 'S.TODO = [OUTPUT_FINAL_PENDING pobdeactivate n true]',
        'checks': [
            '$call_task_valid(S, OUTPUT_FINAL_PENDING pobdeactivate n true)',
            '$output_pending_active(S, pobdeactivate)',
            '$heap_owners($heap_graph(S), HOBJECT n) = 1',
            'S_drop = S[.TODO = [OUTPUT_FINAL_PENDING pobdeactivate n false]]',
            '$destructor_operational(S_drop)',
            '$output_pending_active(S_drop, pobdeactivate)',
            '$call_task_valid(S_drop, OUTPUT_FINAL_PENDING pobdeactivate n false)',
            'S_release = $destruction_transition(S, S_drop)',
            'S_release.DESTRUCTION.OPERATIONS = [pdestructionoperation]',
            'pdestructionoperation.SOURCE = OUTPUT_FINAL_PENDING pobdeactivate n true',
            'pdestructionoperation.PENDING = eps',
            '$eager_operation_source_guard(S_release, pdestructionoperation)',
            '$call_descriptors_valid(S_release)',
            '$destruction_state_valid(S_release)',
            '$heap_valid($heap_graph(S_release))',
            'S_gc = $literal_reference_debt_step(S, S_drop)',
            '$call_descriptors_valid(S_gc)',
            'S_next = $drive_steps(S, 1)',
            'S_next.COMPLETION = BUDGET',
        ],
    },
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case) else 1)
