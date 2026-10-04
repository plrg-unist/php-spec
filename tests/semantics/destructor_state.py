#!/usr/bin/env python3
"""Focused automatic-constructor and replacement-exception release checks."""
import argparse

from destructor_state_review import SOURCES, VALID, REPLAY
import shutdown_state_review as runner

runner.CASES = {
    'unused-return-keeps-callee-scope-before-locals': {
        'source': '<?php class L{function __destruct(){echo "L;";}}class C{private function __destruct(){echo "C:",get_called_class(),";";}static function make(){$l=new L;return new C;}}class P{function __destruct(){echo "P;";C::make();echo "TAIL;";}}$p=new P;',
        'stage': 'S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: '
                 '(DESTRUCTOR_RELEASE pdestructionrelease) :: '
                 '[RETURN_UNWIND (KNOWN PNULL) porigin_source?] '
                 '-- if S.CURRENT = (pcallcontext) '
                 '-- if $class_method_origin(S.CLASSES, pcallcontext.FUNCTION) = (pmethoddesc_caller) '
                 '-- if pmethoddesc_caller.NAME = $ptascii("make")',
        'checks': [
            'pdestructorcall.CALLER = (pcallcontext)',
            'pdestructorcall.ORIGIN = S.ORIGIN',
            'pdestructorcall.CONSTCONTEXT = eps',
            'pdestructorcall.PENDING = eps', 'pdestructorcall.FRAME = eps',
            'pdestructionrelease.CALLER = S.CURRENT',
            'pdestructionrelease.JOBS = eps',
            '$lookup(S.ENV, $ptascii("l")) = (n_local)',
            'S.STORE[n_local] = DEFINED (POBJECT n_local_object)',
            '$heap_owners($heap_graph(S), HOBJECT n_local_object) = 1',
            '$heap_owners($heap_graph(S), HOBJECT pdestructorcall.OBJECT) = 2',
            '$class_named(S.CLASSNAMES, $ptascii("c")) = (porigin_class)',
            'pcallcontext.LEXICAL_CLASS = (porigin_class)',
            'pcallcontext.CALLED_CLASS = (porigin_class)',
            '$destructor_method(S, pdestructorcall.OBJECT) = (pmethoddesc)',
            'pmethoddesc.VISIBILITY = PRIVATE',
            '$method_accessible(S, pmethoddesc, $method_current_scope(S))',
            '$return_unwind_source_valid(S, porigin_source?)',
            '$destructor_enter_valid(S, pdestructorcall)',
            '~$destructor_enter_valid(S, pdestructorcall[.CALLER = eps])',
            '~$destructor_enter_valid(S, pdestructorcall[.ORIGIN = eps])',
            *VALID, *REPLAY,
            '~((HOBJECT n_local_object) <- S_done.ALLOCATIONS)',
            '~((HOBJECT pdestructorcall.OBJECT) <- S_done.ALLOCATIONS)',
            'S_done.EVENTS = [OUTPUT $ptascii("P;"), OUTPUT $ptascii("C:"), '
            'OUTPUT $ptascii("C"), OUTPUT $ptascii(";"), OUTPUT $ptascii("L;"), '
            'OUTPUT $ptascii("TAIL;")]',
        ],
    },
    'replacement-exception-owns-remaining-local-loop': {
        'source': SOURCES['remaining-locals-chain-replacement-throwables'],
        'stage': 'S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
                 '(DESTRUCTOR_FRAME_EXIT pdestructionframe) :: ptask_tail* '
                 '-- if pdestructionframe.PENDING = (n_replacement) '
                 '-- if $throwable_field(S, n_replacement, "message") = '
                 'PSTRING $ptascii("b") '
                 '-- if $function_at($all_functions(S), pdestructionframe.FUNCTION) = (pfunction) '
                 '-- if pfunction.NAME = $ptascii("drop")',
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
