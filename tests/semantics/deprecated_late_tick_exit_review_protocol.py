#!/usr/bin/env python3
"""Check saved main exit through temporary normal tick-owner cleanup."""
from pathlib import Path

import fiber_state_review as review


HERE = Path(__file__).parent


def source(name):
    return (HERE / f'deprecated_late_tick_exit_review_{name}.php').read_text()


PREFIX = ('S.TODO = [DESTRUCTOR_RELEASE pdestructionrelease, '
          'DESTRUCTOR_OPERATION_EXIT pdestructionoperation, '
          'EXECUTOR_TICK_RELEASE pexecutortick false] '
          '-- if pdestructionoperation.SOURCE = EXECUTOR_TICK_RELEASE pexecutortick true ')
VALID = ['$executor_tick_valid(S, pexecutortick)',
         '$eager_operation_source_valid(S, pdestructionoperation)',
         '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
         '$exit_status_valid(S)']
DONE = ['S_done = $drive_steps(S, 4000)', 'S_done.TICKENTRIES = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))']


def saved_exit(status):
    return [f'pexecutortick.COMPLETION = EXITED {status}',
            f'S.SHUTDOWN.COMPLETION = EXITED {status}',
            f'S.DESTRUCTION.COMPLETION = EXITED {status}',
            f'S.EXITSTATUS = {status}', 'S.COMPLETION = NORMAL']


# Changed task/status/phase copies are complementary, explicitly derived guards.
DERIVED = {'integer-exit-keeps-copied-array-and-closure-owners': 6,
           'cacheless-exit-retains-full-status-before-rendering': 1,
           'normal-completion-keeps-phase-authority-with-any-valid-status': 5}

review.CASES = {
    'integer-exit-keeps-copied-array-and-closure-owners': {
        'source': source('integer_closure'),
        'stage': PREFIX + '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HARRAY n_payload), DESTRUCTION_VALUE (HARRAY n_payload), DESTRUCTION_VALUE (HOBJECT n_callback)] -- if pexecutortick.ENTRY = ptickentry',
        'checks': [
            *saved_exit(7), 'ptickentry.ENTRY.ARGS = [PARRAY n_payload, PARRAY n_payload]',
            '$callback_cache_nodes(ptickentry.ENTRY) = [HOBJECT n_callback]',
            '$node_children(S, HARRAY n_payload) = [HCELL n_cell]',
            'S.STORE[n_cell] = DEFINED (POBJECT n_arg)',
            '$node_children(S, HOBJECT n_callback) = [HOBJECT n_capture]',
            '$heap_owners($heap_graph(S), HARRAY n_payload) = 2',
            '$heap_owners($heap_graph(S), HCELL n_cell) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_arg) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_capture) = 1',
            'pdestructionoperation.COMPLETION = NORMAL',
            'pdestructionoperation.PENDING = eps',
            '~$executor_tick_valid(S, pexecutortick[.COMPLETION = NORMAL])',
            '~$executor_tick_valid(S, pexecutortick[.COMPLETION = EXITED 9])',
            '~$executor_tick_valid(S[.EXITSTATUS = 9], pexecutortick)',
            '~$executor_tick_valid(S[.SHUTDOWN.COMPLETION = NORMAL], pexecutortick)',
            '~$executor_tick_valid(S[.DESTRUCTION.COMPLETION = NORMAL], pexecutortick)',
            '~$eager_operation_source_valid(S, pdestructionoperation[.COMPLETION = EXITED 7])',
            'S.EVENTS = [OUTPUT $ptascii("B;F;")]', *VALID,
        ],
    },
    'integer-exit-survives-array-cell-and-argument-retirement': {
        'source': source('integer_closure'),
        'stage': PREFIX + '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_callback)] -- if pexecutortick.ENTRY = ptickentry -- if ptickentry.ENTRY.ARGS = [PARRAY n_payload, PARRAY n_payload]',
        'checks': [
            *saved_exit(7),
            'S.ARRAYS[n_payload].ITEMS = [ENTRY (KINT 0) (ALIAS n_cell)]',
            'S.STORE[n_cell] = DEFINED (POBJECT n_arg)',
            '~((HARRAY n_payload) <- S.ALLOCATIONS)',
            '~((HCELL n_cell) <- S.ALLOCATIONS)',
            '~((HOBJECT n_arg) <- S.ALLOCATIONS)',
            '$node_children(S, HOBJECT n_callback) = [HOBJECT n_capture]',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_capture) = 1',
            'S.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("A;")]',
            'pdestructionoperation.COMPLETION = NORMAL', *VALID,
            'S_paused = $drive(S, 0)', 'S_paused.COMPLETION = BUDGET',
            'S_paused.TODO = S.TODO', 'S_paused.EXITSTATUS = 7',
            *DONE, 'S_done.COMPLETION = EXITED 7', 'S_done.EXITSTATUS = 7',
            '$drive_steps(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
            'S_done.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("A;"), OUTPUT $ptascii("K;")]',
        ],
    },
    'string-exit-keeps-bound-fcc-and-receiver-owners': {
        'source': source('string_bound'),
        'stage': PREFIX + '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_arg), DESTRUCTION_VALUE (HOBJECT n_receiver), DESTRUCTION_VALUE (HOBJECT n_callback)] -- if pexecutortick.ENTRY = ptickentry',
        'checks': [
            *saved_exit(0),
            '$callback_cache_nodes(ptickentry.ENTRY) = [HOBJECT n_receiver, HOBJECT n_callback]',
            'pexecutortick.RECEIVER = (n_receiver)',
            '$node_children(S, HOBJECT n_callback) = [HOBJECT n_receiver]',
            '$heap_owners($heap_graph(S), HOBJECT n_receiver) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_arg) = 1',
            'S.EVENTS = [OUTPUT $ptascii("B;E;F;")]',
            'pdestructionoperation.COMPLETION = NORMAL', *VALID, *DONE,
            'S_done.COMPLETION = EXITED 0', 'S_done.EXITSTATUS = 0',
            'S_done.EVENTS = [OUTPUT $ptascii("B;E;F;"), OUTPUT $ptascii("A;"), OUTPUT $ptascii("R;")]',
        ],
    },
    'raw-invokable-retains-exit-through-final-fcc-slot': {
        'source': (HERE / 'deprecated_late_tick_exit_raw.php').read_text(),
        'stage': PREFIX + '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_callback)] -- if pexecutortick.ENTRY = ptickentry -- if ptickentry.ENTRY.TARGET = METHOD_TARGET n_callback porigin_callback',
        'checks': [
            *saved_exit(7),
            '$callback_cache_nodes(ptickentry.ENTRY) = [HOBJECT n_callback, HOBJECT n_callback]',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 1',
            '~(n_callback <- S.DESTRUCTION.CALLED)',
            'S.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("A;")]',
            'pdestructionoperation.COMPLETION = NORMAL', *VALID, *DONE,
            'S_done.COMPLETION = EXITED 7', 'S_done.EXITSTATUS = 7',
            'S_done.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("A;"), OUTPUT $ptascii("C;")]',
        ],
    },
    'cacheless-exit-retains-full-status-before-rendering': {
        'source': (HERE / 'deprecated_late_tick_exit_cacheless.php').read_text(),
        'stage': 'S.TODO = [EXECUTOR_TICK_RELEASE pexecutortick true]',
        'checks': [
            *saved_exit(263),
            'S.TICKENTRIES = eps', '$executor_tick_nodes(pexecutortick.ENTRY) = eps',
            '$call_task_valid(S, EXECUTOR_TICK_RELEASE pexecutortick true)',
            '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
            '$exit_status_valid(S)',
            '~$executor_tick_valid(S, pexecutortick[.COMPLETION = EXITED 7])',
            *DONE, 'S_done.COMPLETION = EXITED 263', 'S_done.EXITSTATUS = 263',
            'S_done.EVENTS = [OUTPUT $ptascii("B;F;")]',
        ],
    },
    'normal-completion-keeps-phase-authority-with-any-valid-status': {
        'source': (HERE / 'deprecated_late_tick_named_scalar.php').read_text(),
        'stage': 'S.TODO = [EXECUTOR_TICK_RELEASE pexecutortick true]',
        'checks': [
            'pexecutortick.COMPLETION = NORMAL',
            'S.SHUTDOWN.COMPLETION = NORMAL', 'S.DESTRUCTION.COMPLETION = NORMAL',
            'S.EXITSTATUS = 0', '$call_task_valid(S, EXECUTOR_TICK_RELEASE pexecutortick true)',
            '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
            'S_nonzero = S[.EXITSTATUS = 7]',
            '$exit_status_valid(S_nonzero)', '$call_descriptors_valid(S_nonzero)',
            '$executor_tick_valid(S_nonzero, pexecutortick)',
            '~$executor_tick_valid(S, pexecutortick[.COMPLETION = EXITED 0])',
            *DONE, 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
            'S_done.EVENTS = [OUTPUT $ptascii("B;F;")]',
        ],
    },
}


if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=240) else 1)
