#!/usr/bin/env python3
"""Focused automatic-constructor and replacement-exception release checks."""
import argparse

from destructor_state_review import SOURCES, VALID, REPLAY
import shutdown_state_review as runner

runner.CASES = {
    'replacement-exception-owns-remaining-local-loop': {
        'source': SOURCES['remaining-locals-chain-replacement-throwables'],
        'stage': 'S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
                 '(DESTRUCTOR_FRAME_EXIT pdestructionframe) :: ptask_tail* '
                 '-- if pdestructionframe.PENDING = (n_replacement) '
                 '-- if $throwable_field(S, n_replacement, "message") = '
                 'PSTRING $ptascii("b")',
        'checks': [
            'S.DESTRUCTION.FRAMES = [pdestructionframe]',
            'pdestructionrelease.CALLER = S.CURRENT',
            'pdestructionframe.CALLER = S.CURRENT',
            'pdestructionframe.VALUE = KNOWN PNULL',
            '$throwable_field(S, n_replacement, "previous") = POBJECT n_parent',
            '$throwable_field(S, n_parent, "message") = PSTRING $ptascii("parent")',
            '$heap_owners($heap_graph(S), HOBJECT n_replacement) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_parent) = 1',
            'pdestructionrelease.JOBS =/= eps',
            '$destructor_release_valid(S, pdestructionrelease)',
            '$destructor_frame_valid(S, pdestructionframe)',
            '~$destructor_frame_valid(S, pdestructionframe[.PENDING = (n_parent)])',
            '~$destructor_frame_valid(S, pdestructionframe[.CALLER = eps])',
            *VALID, *REPLAY,
            '~((HOBJECT n_replacement) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_parent) <- S_done.ALLOCATIONS)',
        ],
    },
    'automatic-internal-constructor-failure-is-marked': {
        'source': SOURCES['failed-internal-constructor-skips-user-destructor'],
        'stage': 'S.TODO = (CATCH_BIND porigin n_index n_exception) :: ptask_tail*',
        'checks': [
            'S.DESTRUCTION.PHASE = DESTRUCTION_PENDING',
            '0 <- S.DESTRUCTION.CALLED',
            '~((HOBJECT 0) <- S.ALLOCATIONS)',
            'S.DESTRUCTION.CALLS = eps',
            'S.DESTRUCTION.RELEASES = eps',
            *VALID, *REPLAY,
            'S_done.EVENTS = [OUTPUT $ptascii("C;")]',
        ],
    },
    'manual-internal-constructor-failure-is-unmarked': {
        'source': SOURCES['failed-manual-internal-constructor-keeps-user-destructor'],
        'stage': 'S.TODO = (CATCH_BIND porigin n_index n_exception) :: ptask_tail*',
        'checks': [
            'S.DESTRUCTION.PHASE = DESTRUCTION_PENDING',
            '~(0 <- S.DESTRUCTION.CALLED)',
            '(HOBJECT 0) <- S.ALLOCATIONS',
            '$heap_owners($heap_graph(S), HOBJECT 0) = 1',
            'S.DESTRUCTION.CALLS = eps',
            'S.DESTRUCTION.RELEASES = eps',
            *VALID, *REPLAY,
            'S_done.EVENTS = [OUTPUT $ptascii("C;"), OUTPUT $ptascii("D;")]',
            '~((HOBJECT 0) <- S_done.ALLOCATIONS)',
        ],
    },
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if runner.run(args.case) else 1)
