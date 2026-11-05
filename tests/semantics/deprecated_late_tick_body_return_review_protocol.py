#!/usr/bin/env python3
"""Check ignored body-result ownership before the real null-C receiver return."""
from pathlib import Path
import json

import fiber_state_review as review


HERE = Path(__file__).parent
ROOT_SOURCE = next(row['source'] for row in
                   json.loads((HERE / 'destructor_cases.json').read_text())
                   if row['id'] == 'destructor-return-is-unused')
DERIVED = {}


def source(name):
    return (HERE / f'deprecated_late_tick_body_return_{name}.php').read_text()


TICK = ['pdestructorcall.OPERATION = (pdestructionoperation)',
        'pdestructionoperation.SOURCE = EXECUTOR_TICK_RELEASE pexecutortick true',
        'pdestructorcall.OBJECT = n_arg', '~pdestructorcall.USER',
        'pdestructorcall.CALLER = eps', 'pdestructorcall.PENDING = eps',
        'pdestructionoperation.COMPLETION = NORMAL',
        'pdestructionoperation.PENDING = eps', 'S.DESTRUCTION.ABANDONED = eps']
VALID = ['$executor_tick_valid(S, pexecutortick)', '$executor_tick_scope(S)',
         '$eager_operation_source_valid(S, pdestructionoperation)',
         '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
         '$exit_status_valid(S)']
DONE = ['S_done = $drive_steps(S, 4000)', 'S_done.TODO = eps',
        'S_done.CURRENT = eps', 'S_done.FRAMES = eps',
        'S_done.TICKENTRIES = eps', 'S_done.SHUTDOWN.ENTRIES = eps',
        'S_done.DESTRUCTION.CALLS = eps', 'S_done.DESTRUCTION.RELEASES = eps',
        'S_done.DESTRUCTION.FRAMES = eps', 'S_done.DESTRUCTION.OPERATIONS = eps',
        'S_done.DESTRUCTION.ABANDONED = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$exit_status_valid(S_done)']
ROOT = ['pdestructorcall.OBJECT = n_arg', '~pdestructorcall.USER',
        'pdestructorcall.CALLER = eps', 'pdestructorcall.ORIGIN = eps',
        'pdestructorcall.CONSTCONTEXT = eps', 'pdestructorcall.FRAME = eps',
        'pdestructorcall.OPERATION = eps', 'pdestructorcall.PENDING = eps',
        'S.CURRENT = eps', 'S.FRAMES = eps', 'S.COMPLETION = NORMAL',
        'S.EXITSTATUS = 0', 'S.DESTRUCTION.ABANDONED = eps',
        '$destructor_call_live(S, pdestructorcall)',
        '$destructor_c_return_source(S.TODO, pdestructorcall)',
        '$destruction_state_valid(S)', '$call_descriptors_valid(S)',
        '$heap_valid($heap_graph(S))', '$exit_status_valid(S)']


def phase(completion, status):
    return [f'pexecutortick.COMPLETION = {completion}',
            f'S.SHUTDOWN.COMPLETION = {completion}',
            f'S.DESTRUCTION.COMPLETION = {completion}',
            f'S.EXITSTATUS = {status}', 'S.COMPLETION = NORMAL']


def entered(name, returned_class, completion, status, owners):
    return {
        'source': source(name),
        'stage': 'S.TODO = (DESTRUCTOR_ENTER pdestructorcall_returned) :: ptask_tail* '
                 f'-- if $object_name(S, pdestructorcall_returned.OBJECT) = $ptascii("{returned_class}")',
        'checks': [
            'S.DESTRUCTION.CALLS = [pdestructorcall_returned, pdestructorcall]',
            *TICK, *phase(completion, status),
            'S.CURRENT = eps', 'S.FRAMES = eps',
            'n_returned = pdestructorcall_returned.OBJECT',
            '~pdestructorcall_returned.USER', 'pdestructorcall_returned.CALLER = eps',
            'pdestructorcall_returned.OPERATION = (pdestructionoperation)',
            'pdestructorcall_returned.PENDING = eps',
            'pexecutortick.ENTRY.ENTRY.ARGS = [POBJECT n_arg, POBJECT n_later]',
            '$callback_cache_nodes(pexecutortick.ENTRY.ENTRY) = [HOBJECT n_callback, HOBJECT n_callback]',
            '$node_children(S, HOBJECT n_arg) = [HOBJECT n_held]',
            f'$heap_owners($heap_graph(S), HOBJECT n_arg) = {owners}',
            '$heap_owners($heap_graph(S), HOBJECT n_returned) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_held) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_later) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 2',
            '~(n_held <- S.DESTRUCTION.CALLED)',
            '$destructor_call_live(S, pdestructorcall)',
            '$destructor_c_return_source(S.TODO, pdestructorcall)',
            '~$destructor_c_return_valid(S, pdestructorcall)',
            '$destructor_enter_valid(S, pdestructorcall_returned)',
            'S.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("A;")]',
            *VALID,
        ],
    }


review.CASES = {
    'fresh-body-result-transfers-before-inner-c-decrement': {
        'source': source('object'),
        'stage': 'S.TODO = (DESTRUCTOR_C_RETURN pdestructorcall) :: (DESTRUCTOR_RESULT pdestructorcall) :: ptask_tail* -- if S.RESULT = KNOWN (POBJECT n_returned) -- if $object_name(S, n_returned) = $ptascii("BodyReturn22Value")',
        'checks': [
            *TICK, *phase('NORMAL', 0), 'S.CURRENT = eps', 'S.FRAMES = eps',
            'S.DESTRUCTION.CALLS = [pdestructorcall]',
            'S.BASE = BASE_VALUE (KNOWN PNULL)',
            'pexecutortick.ENTRY.ENTRY.ARGS = [POBJECT n_arg, POBJECT n_later]',
            '$callback_cache_nodes(pexecutortick.ENTRY.ENTRY) = [HOBJECT n_callback, HOBJECT n_callback]',
            '$node_children(S, HOBJECT n_arg) = [HOBJECT n_held]',
            '$heap_owners($heap_graph(S), HOBJECT n_arg) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_returned) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_held) = 1',
            '~(n_returned <- S.DESTRUCTION.CALLED)',
            '$destructor_c_return_valid(S, pdestructorcall)',
            'S.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("A;")]',
            *VALID,
            'PhpStep: S ~> S_release',
            'S_release.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_result) :: (DESTRUCTOR_C_RETURN pdestructorcall) :: (DESTRUCTOR_RESULT pdestructorcall) :: ptask_tail*',
            'pdestructionrelease_result.JOBS = [DESTRUCTION_VALUE (HOBJECT n_returned)]',
            'S_release.RESULT = KNOWN PNULL', 'S_release.BASE = BASE_VALUE (KNOWN PNULL)',
            'S_release.DESTRUCTION.CALLS = S.DESTRUCTION.CALLS',
            '$heap_owners($heap_graph(S_release), HOBJECT n_arg) = 2',
            '$heap_owners($heap_graph(S_release), HOBJECT n_returned) = 1',
            '$destructor_c_return_valid(S_release, pdestructorcall)',
            '$destructor_release_valid(S_release, pdestructionrelease_result)',
            '$call_descriptors_valid(S_release)', '$heap_valid($heap_graph(S_release))',
            'S_paused = $drive(S_release, 0)', 'S_paused.COMPLETION = BUDGET',
            'S_paused.TODO = S_release.TODO',
            '$heap_owners($heap_graph(S_paused), HOBJECT n_arg) = 2',
            '$heap_owners($heap_graph(S_paused), HOBJECT n_returned) = 1',
            *DONE, 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
            '~((HOBJECT n_arg) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_returned) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_callback) <- S_done.ALLOCATIONS)',
            'S_done.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("A;"), OUTPUT $ptascii("R;"), OUTPUT $ptascii("K;"), OUTPUT $ptascii("L;"), OUTPUT $ptascii("C;")]',
            '$drive_steps(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
        ],
    },
    'fresh-returned-object-keeps-both-original-c-protections':
        entered('object', 'BodyReturn22Value', 'NORMAL', 0, 2),
    'array-result-keeps-alias-and-direct-slot-multiplicity': {
        'source': source('array'),
        'stage': 'S.TODO = (DESTRUCTOR_C_RETURN pdestructorcall) :: (DESTRUCTOR_RESULT pdestructorcall) :: ptask_tail* -- if S.RESULT = KNOWN (PARRAY n_returned_array)',
        'checks': [
            *TICK, *phase('EXITED 263', 263), 'S.CURRENT = eps', 'S.FRAMES = eps',
            'S.DESTRUCTION.CALLS = [pdestructorcall]',
            'S.ARRAYS[n_returned_array].ITEMS = [ENTRY (KINT 0) (ALIAS n_alias), ENTRY (KINT 1) (DIRECT (POBJECT n_returned)), ENTRY (KINT 2) (DIRECT (POBJECT n_returned))]',
            'n_alias <- S.REFCELLS', 'S.STORE[n_alias] = DEFINED (POBJECT n_returned)',
            '$node_children(S, HARRAY n_returned_array) = [HCELL n_alias, HOBJECT n_returned, HOBJECT n_returned]',
            '$node_children(S, HOBJECT n_returned) = [HOBJECT n_arg]',
            '$node_children(S, HOBJECT n_arg) = [HOBJECT n_held]',
            '$heap_owners($heap_graph(S), HARRAY n_returned_array) = 1',
            '$heap_owners($heap_graph(S), HCELL n_alias) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_returned) = 3',
            '$heap_owners($heap_graph(S), HOBJECT n_arg) = 3',
            '$heap_owners($heap_graph(S), HOBJECT n_held) = 1',
            '$destructor_c_return_valid(S, pdestructorcall)',
            *VALID,
            'PhpStep: S ~> S_release',
            'S_release.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_result) :: (DESTRUCTOR_C_RETURN pdestructorcall) :: (DESTRUCTOR_RESULT pdestructorcall) :: ptask_tail*',
            'pdestructionrelease_result.JOBS = [DESTRUCTION_VALUE (HARRAY n_returned_array)]',
            'S_release.RESULT = KNOWN PNULL', 'S_release.EXITSTATUS = 263',
            '$heap_owners($heap_graph(S_release), HARRAY n_returned_array) = 1',
            '$heap_owners($heap_graph(S_release), HOBJECT n_arg) = 3',
            '$destructor_release_valid(S_release, pdestructionrelease_result)',
            '$call_descriptors_valid(S_release)', '$heap_valid($heap_graph(S_release))',
        ],
    },
    'array-returned-object-keeps-two-c-plus-real-owner-field':
        entered('array', 'BodyArray22Value', 'EXITED 263', 263, 3),
    'returned-closure-capture-runs-before-original-held-child': {
        **entered('review_closure', 'BodyClosure22Returned', 'NORMAL', 0, 2),
        'checks': [
            *entered('review_closure', 'BodyClosure22Returned', 'NORMAL', 0, 2)['checks'],
            *DONE, 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
            '~((HOBJECT n_arg) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_returned) <- S_done.ALLOCATIONS)',
            'S_done.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("A;"), OUTPUT $ptascii("R;"), OUTPUT $ptascii("K;"), OUTPUT $ptascii("L;"), OUTPUT $ptascii("C;")]',
        ],
    },
    'shared-return-result-drops-once-before-later-argument-destruction': {
        'source': source('review_retained'),
        'stage': 'S.TODO = (DESTRUCTOR_C_RETURN pdestructorcall) :: (DESTRUCTOR_RESULT pdestructorcall) :: ptask_tail* -- if S.RESULT = KNOWN (POBJECT n_returned) -- if $object_name(S, n_returned) = $ptascii("BodyRetained22Returned")',
        'checks': [
            *TICK, *phase('NORMAL', 0), 'S.CURRENT = eps', 'S.FRAMES = eps',
            'S.DESTRUCTION.CALLS = [pdestructorcall]',
            'pexecutortick.ENTRY.ENTRY.ARGS = [POBJECT n_arg, POBJECT n_returned]',
            '$callback_cache_nodes(pexecutortick.ENTRY.ENTRY) = [HOBJECT n_callback, HOBJECT n_callback]',
            '$node_children(S, HOBJECT n_arg) = [HOBJECT n_held, HOBJECT n_returned]',
            '$heap_owners($heap_graph(S), HOBJECT n_arg) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_returned) = 3',
            '~(n_returned <- S.DESTRUCTION.CALLED)',
            'S.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("A;")]',
            *VALID,
            'PhpStep: S ~> S_release',
            'S_release.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_result) :: (DESTRUCTOR_C_RETURN pdestructorcall) :: (DESTRUCTOR_RESULT pdestructorcall) :: ptask_tail*',
            'pdestructionrelease_result.JOBS = [DESTRUCTION_VALUE (HOBJECT n_returned)]',
            'S_release.RESULT = KNOWN PNULL',
            'PhpStep: S_release ~> S_raw',
            'S_shared = $literal_reference_debt_step(S_release, $sensitive_trace_freeze($source_exception_transition(S_release, $throwable_transition(S_release, S_raw))))',
            'S_shared.TODO = (DESTRUCTOR_RELEASE (pdestructionrelease_result[.JOBS = eps])) :: (DESTRUCTOR_C_RETURN pdestructorcall) :: (DESTRUCTOR_RESULT pdestructorcall) :: ptask_tail*',
            '$heap_owners($heap_graph(S_shared), HOBJECT n_arg) = 2',
            '$heap_owners($heap_graph(S_shared), HOBJECT n_returned) = 2',
            '~(n_returned <- S_shared.DESTRUCTION.CALLED)',
            'S_shared.EVENTS = S.EVENTS',
            '$destructor_c_return_valid(S_shared, pdestructorcall)',
            '$call_descriptors_valid(S_shared)', '$heap_valid($heap_graph(S_shared))',
            '$gc_state_valid(S_shared)',
            *DONE, 'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0',
            '~((HOBJECT n_arg) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_returned) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_callback) <- S_done.ALLOCATIONS)',
            'S_done.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("A;"), OUTPUT $ptascii("K;"), OUTPUT $ptascii("R;"), OUTPUT $ptascii("C;")]',
        ],
    },
    'root-local-cleanup-keeps-body-result-and-original-c-owner': {
        'source': ROOT_SOURCE,
        'stage': 'S.TODO = (DESTRUCTOR_ENTER pdestructorcall_local) :: ptask_tail* -- if $object_name(S, pdestructorcall_local.OBJECT) = $ptascii("L")',
        'checks': [
            'S.DESTRUCTION.CALLS = [pdestructorcall_local, pdestructorcall]',
            *ROOT,
            'pdestructorcall_local.FRAME = (pdestructionframe)',
            'S.DESTRUCTION.FRAMES = [pdestructionframe]',
            'pdestructionframe.VALUE = KNOWN (POBJECT n_returned)',
            'pdestructionframe.PENDING = eps',
            '$object_name(S, n_returned) = $ptascii("R")',
            '$heap_owners($heap_graph(S), HOBJECT n_arg) = 2',
            '$heap_owners($heap_graph(S), HOBJECT pdestructorcall_local.OBJECT) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_returned) = 1',
            '~(n_returned <- S.DESTRUCTION.CALLED)',
            '$destructor_enter_valid(S, pdestructorcall_local)',
            'S.EVENTS = [OUTPUT $ptascii("P;")]',
        ],
    },
    'root-returned-object-keeps-original-c-owner-after-local-cleanup': {
        'source': ROOT_SOURCE,
        'stage': 'S.TODO = (DESTRUCTOR_ENTER pdestructorcall_returned) :: ptask_tail* -- if $object_name(S, pdestructorcall_returned.OBJECT) = $ptascii("R")',
        'checks': [
            'S.DESTRUCTION.CALLS = [pdestructorcall_returned, pdestructorcall]',
            *ROOT,
            'n_returned = pdestructorcall_returned.OBJECT',
            'S.DESTRUCTION.FRAMES = eps',
            '$heap_owners($heap_graph(S), HOBJECT n_arg) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_returned) = 2',
            '$destructor_enter_valid(S, pdestructorcall_returned)',
            'S.EVENTS = [OUTPUT $ptascii("P;"), OUTPUT $ptascii("L;")]',
            'S_done = $drive_steps(S, 4000)', 'S_done.COMPLETION = NORMAL',
            'S_done.EXITSTATUS = 0', 'S_done.TODO = eps',
            'S_done.DESTRUCTION.CALLS = eps', 'S_done.DESTRUCTION.RELEASES = eps',
            'S_done.DESTRUCTION.FRAMES = eps', 'S_done.DESTRUCTION.ABANDONED = eps',
            '~((HOBJECT n_arg) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_returned) <- S_done.ALLOCATIONS)',
            '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
            '$exit_status_valid(S_done)',
            'S_done.EVENTS = [OUTPUT $ptascii("P;"), OUTPUT $ptascii("L;"), OUTPUT $ptascii("R;")]',
        ],
    },
}
review.CASES['array-returned-object-keeps-two-c-plus-real-owner-field']['checks'].insert(
    -len(VALID), '$node_children(S, HOBJECT n_returned) = [HOBJECT n_arg]')


if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=240) else 1)
