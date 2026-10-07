#!/usr/bin/env python3
"""A saved destructor caller at the temporary Fiber transfer boundary."""
import json
from pathlib import Path

import shutdown_state_review as runner

SOURCE = next(row['source'] for row in json.loads(
    Path(__file__).with_name('eager_fatal_review_cases.json').read_text())
    if row['id'] == 'fiber-start-inside-destructor-helper-boundary')

runner.CASES = {
    'fiber-switch-retains-saved-destructor-protocol': {
        'source': SOURCE,
        'stage': 'S.TODO = (FIBER_ARGS pfiberstart) :: ptask_tail* -- if pfiberstart.INDEX = 0 -- if S.CURRENT = (pcallcontext)',
        'checks': [
            'S.CURRENT = (pcallcontext)',
            '$callable_at(S.CALLABLES, $ptascii("inner")) = (pcallcontext.FUNCTION)',
            'S.FRAMES = [pframe_saved, pframe_main]',
            'pframe_saved.CONTEXT = (pcallcontext_destructor)',
            'pframe_main.CONTEXT = eps',
            'S.DESTRUCTION.CALLS = [pdestructorcall]',
            'S.DESTRUCTION.OPERATIONS = [pdestructionoperation]',
            'pcallcontext_destructor.TARGET = pdestructorcall.TARGET',
            '$call_saved_context_valid(S, pframe_saved)',
            '$destructor_context_kind(S, pcallcontext_destructor)',
            '$heap_owners($heap_graph(S), HOBJECT pdestructorcall.OBJECT) = 2',
            '$fiber_start_valid(S, pfiberstart, false)',
            '$fiber_at(S, pfiberstart.OBJECT) = (pfiber)',
            'pfiber.STATUS = FIBER_INIT',
            '~$fiber_blocked(S)',
            '$fiber_destruction_pending(S)',
            '~$fiber_transfer_domain(S)',
            '$call_current_valid(S)', '$call_frames_valid(S, S.FRAMES)',
            '$call_descriptors_valid(S)', '$destruction_state_valid(S)',
            '$heap_valid($heap_graph(S))',
            'S.EVENTS = [OUTPUT $ptascii("M;"), OUTPUT $ptascii("D;")]',
            'S_paused = $drive(S, 0)', 'S_paused.COMPLETION = BUDGET',
            'S_paused.DESTRUCTION = S.DESTRUCTION',
            'PhpStep: S ~> S_next',
            'S_next = S[.COMPLETION = UNSUPPORTED "Fiber switch during automatic destruction"]',
            'S_next.ALLOCATIONS = S.ALLOCATIONS',
            'S_next.DESTRUCTION = S.DESTRUCTION',
            'S_paused[.COMPLETION = NORMAL] = S',
            '$fiber_start(S_paused[.COMPLETION = NORMAL], pfiberstart) = S_next',
        ],
    },
}

if __name__ == '__main__':
    raise SystemExit(0 if runner.run(None) else 1)
