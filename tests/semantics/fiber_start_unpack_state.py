#!/usr/bin/env python3
"""Reached unpack teardown order and packed outer-to-core START history."""
import argparse
import json
from pathlib import Path
import fiber_state_review as review

ROOT = Path(__file__).resolve().parents[2]
CATALOG = Path(__file__).with_name('fiber_start_unpack_cases.json')
SOURCE_BYTES = CATALOG.read_bytes()
SOURCES = {row['id']: row['source'] for row in json.loads(SOURCE_BYTES)}
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']


def events(*pieces):
    return 'S_done.EVENTS = [' + ', '.join(
        'OUTPUT $ptascii(' + json.dumps(piece) + ')' for piece in pieces) + ']'


UNWIND_EVENTS = events('P|', 'D', '0', '|', 'F|', 'C|', 'pack', '|', '1', '|',
                       'P|', 'F|', 'N', '1', '|', 'C|', 'pack', '|', '1', '|END')


def unwind(named):
    slot = ('pfiberstart.SENT.NAMED = [($ptascii("value"), KNOWN (POBJECT n_arg))]'
            if named else
            'pfiberstart.SENT.SLOTS = [NAMED_SENT (KNOWN (POBJECT n_arg))]')
    item = ('ENTRY (KSTRING ($ptascii("value"))) (DIRECT (POBJECT n_arg))'
            if named else 'ENTRY (KINT 0) (DIRECT (POBJECT n_arg))')
    jobs = ('[DESTRUCTION_VALUE (HOBJECT pfiberstart.OBJECT), DESTRUCTION_VALUE (HOBJECT n_arg)]'
            if named else
            '[DESTRUCTION_VALUE (HOBJECT n_arg), DESTRUCTION_VALUE (HOBJECT pfiberstart.OBJECT)]')
    checks = [
        'S.ACTIVEFIBER = eps', 'S.FIBERCALLERS = eps', 'S.CURRENT = eps',
        'S.FRAMES = eps', 'S.ORIGIN = (pfiberstart.SITE)', 'pfiberstart.INDEX = 1',
        '$intrinsic_count(S, pfiberstart.SITE) = (2)', slot,
        'pfiberstart.PACKS = [(FIBER_ARRAY_PACK pconfigpack)]', 'pconfigpack.INDEX = 0',
        f'pconfigpack.ITEMS = [{item}]',
        '~((HARRAY pconfigpack.ARRAY) <- S.ALLOCATIONS)',
        '$fiber_start_pack_source_valid(S, pfiberstart.SITE, pconfigpack)',
        '$fiber_start_shape(S, pfiberstart.SITE, 1, pfiberstart.SENT, pfiberstart.PACKS)',
        'S.OBJECTS[pfiberstart.OBJECT] = FIBER pfiber',
        'pfiber.STATUS = FIBER_SUSPENDED', 'pfiber.VM =/= eps',
        'pfiberarray.KIND = INTRINSIC_FIBER_START',
        'pfiberarray.INPUT = (pfiberstart.OBJECT)',
        'pfiberarray.NAME = $ptascii("start")',
        '~((HARRAY pfiberarray.ARRAY) <- S.ALLOCATIONS)',
        '$lookup(S.ENV, $ptascii("pair")) = (n_pair_cell)',
        'S.STORE[n_pair_cell] = DEFINED PNULL',
        '$lookup(S.ENV, $ptascii("target")) = (n_target_cell)',
        'S.STORE[n_target_cell] = DEFINED PNULL',
        '$fiber_array_start_source_valid(S, pfiberarray)',
        '$fiber_array_start_buffer_valid(S, pfiberarray, pfiberstart)',
        '$fiber_start_unpack_pending(S, eps, pfiberstart)',
        '$fiber_start_unpack_count(S.TODO, eps, pfiberstart.SITE) = 1',
        '$call_task_valid(S, FIBER_UNPACK_PREP eps pfiberstart)',
        '$task_nodes(FIBER_ARRAY_START_RELEASE pfiberarray) = eps',
        '$task_nodes(FIBER_UNPACK_PREP eps pfiberstart) = [HOBJECT pfiberstart.OBJECT, HOBJECT n_arg]',
        'H = $heap_graph(S)', '$heap_owners(H, HOBJECT pfiberstart.OBJECT) = 1',
        '$heap_owners(H, HOBJECT n_arg) = 1', '$heap_owners(H, HARRAY pconfigpack.ARRAY) = 0',
        *review.VALID,
        'S_after = S[.TODO = (THROW_SEARCH n_throwable) :: '
        '(FIBER_ARRAY_START_RELEASE pfiberarray) :: ptask_tail*]',
        '$fiber_start_unpack_unwind_valid(S_after, FIBER_UNPACK_PREP eps pfiberstart)',
    ]
    if not named:
        checks += [
            'pfiberstart_index = pfiberstart[.PACKS = [(FIBER_ARRAY_PACK pconfigpack[.INDEX = 1])]]',
            'S_index = S[.TODO = (THROW_SEARCH n_throwable) :: '
            '(FIBER_UNPACK_PREP eps pfiberstart_index) :: '
            '(FIBER_ARRAY_START_RELEASE pfiberarray) :: ptask_tail*]',
            '$heap_graph(S_index) = H',
            '~$fiber_start_unpack_pending(S_index, eps, pfiberstart_index)',
            '~$call_descriptors_valid(S_index)',
            'pfiberstart_line = pfiberstart[.PACKS = [(FIBER_ARRAY_PACK pconfigpack[.LINE = $(pconfigpack.LINE + 1)])]]',
            'S_line = S[.TODO = (THROW_SEARCH n_throwable) :: '
            '(FIBER_UNPACK_PREP eps pfiberstart_line) :: '
            '(FIBER_ARRAY_START_RELEASE pfiberarray) :: ptask_tail*]',
            '$heap_graph(S_line) = H',
            '~$fiber_start_unpack_pending(S_line, eps, pfiberstart_line)',
            '~$call_descriptors_valid(S_line)',
            'S_missing = S[.TODO = (THROW_SEARCH n_throwable) :: '
            '(FIBER_UNPACK_PREP eps pfiberstart) :: ptask_tail*]',
            '$heap_graph(S_missing) = H',
            '~$fiber_start_unpack_pending(S_missing, eps, pfiberstart)',
            '~$call_descriptors_valid(S_missing)',
            'S_duplicate = S[.TODO = (THROW_SEARCH n_throwable) :: '
            '(FIBER_UNPACK_PREP eps pfiberstart) :: (FIBER_ARGS pfiberstart) :: '
            '(FIBER_ARRAY_START_RELEASE pfiberarray) :: ptask_tail*]',
            '$fiber_start_unpack_count(S_duplicate.TODO, eps, pfiberstart.SITE) = 2',
            '$heap_owners($heap_graph(S_duplicate), HOBJECT pfiberstart.OBJECT) = 2',
            '$heap_owners($heap_graph(S_duplicate), HOBJECT n_arg) = 2',
            '~$fiber_start_unpack_pending(S_duplicate, eps, pfiberstart)',
            '~$call_descriptors_valid(S_duplicate)',
        ]
    return checks + [
        *ZERO, 'S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
        'S_one = S_one_budget[.COMPLETION = NORMAL]',
        'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (THROW_SEARCH n_throwable) :: '
        '(FIBER_ARRAY_START_RELEASE pfiberarray) :: ptask_tail*',
        f'pdestructionrelease.JOBS = {jobs}',
        'pdestructionrelease.CALLER = S.CURRENT', 'pdestructionrelease.ORIGIN = S.ORIGIN',
        'pdestructionrelease.CONSTCONTEXT = S.CONSTCONTEXT',
        'S_one.DESTRUCTION.RELEASES = pdestructionrelease :: S.DESTRUCTION.RELEASES',
        'S_one.ALLOCATIONS = S.ALLOCATIONS',
        '$heap_owners($heap_graph(S_one), HOBJECT pfiberstart.OBJECT) = 1',
        '$heap_owners($heap_graph(S_one), HOBJECT n_arg) = 1',
        '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
        'S_done = $drive(S_one, 4000)', *review.DONE, UNWIND_EVENTS,
    ]


def outer_pack(name, expression):
    return [
        f'pfiberapi_{name} = pfibercaller.API[.PACKS = {expression}]',
        f'pfibercaller_{name} = pfibercaller[.API = pfiberapi_{name}]'
        f'[.VM.TODO = (FIBER_WAIT pfiberapi_{name}) :: ptask_outer*]',
        f'S_{name} = S[.FIBERCALLERS = [pfibercaller_{name}]]',
        f'$heap_graph(S_{name}) = H',
        f'~$fiber_start_core_result_valid(S_{name}, n_runner, n_capture, pfiberstart)',
        f'~$call_descriptors_valid(S_{name})',
    ]


CASES = {
    'start-unpack-positional-unwind-releases-payload-before-last-receiver': {
        'source': SOURCES['author-fiber-start-unpack-abrupt-positional-and-named-owner-order'],
        'stage': ('S.TODO = (THROW_SEARCH n_throwable) :: (FIBER_UNPACK_PREP eps pfiberstart) :: '
                  '(FIBER_ARRAY_START_RELEASE pfiberarray) :: ptask_tail* '
                  '-- if pfiberstart.SENT.NAMED = eps -- if pfiberstart.INDEX = 1'),
        'checks': unwind(False),
    },
    'start-unpack-named-unwind-releases-last-receiver-before-payload': {
        'source': SOURCES['author-fiber-start-unpack-abrupt-positional-and-named-owner-order'],
        'stage': ('S.TODO = (THROW_SEARCH n_throwable) :: (FIBER_UNPACK_PREP eps pfiberstart) :: '
                  '(FIBER_ARRAY_START_RELEASE pfiberarray) :: ptask_tail* '
                  '-- if pfiberstart.SENT.SLOTS = eps -- if pfiberstart.INDEX = 1'),
        'checks': unwind(True),
    },
    'start-unpack-core-copy-keeps-outer-pack-authority-only-in-outer-api': {
        'source': SOURCES['peer-fiber-start-unpack-forwards-named-buffer-through-fcc-and-raw-core'],
        'stage': ('S.TODO = (FIBER_START_CORE_INVOKE n_runner n_capture pfiberstart) :: '
                  '(FIBER_START_CORE_RESULT n_runner n_capture pfiberstart) :: ptask_tail* '
                  '-- if S.FIBERCALLERS = [pfibercaller]'),
        'checks': [
            'ptask_tail* = [FIBER_FINISH n_runner]',
            'S.ACTIVEFIBER = (n_runner)', 'S.CURRENT = eps', 'S.FRAMES = eps',
            'S.ORIGIN = (pfiberstart.SITE)',
            '$fiber_at(S, n_runner) = (pfiber_runner)',
            'pfiber_runner.RAW = POBJECT n_capture',
            'pfiber_runner.TARGET = (FIBER_API_TARGET n_capture)',
            'pfiber_runner.ENTRY = (pfiberstart.SENT)',
            'pfiber_runner.STATUS = FIBER_RUNNING',
            'S.OBJECTS[n_capture] = FIBERAPICLOSURE pfibercapture',
            'pfibercapture.KIND = INTRINSIC_FIBER_START',
            'pfibercapture.INPUT = (n_target)', 'pfiberstart.OBJECT = n_target',
            'pfiberstart.INDEX = 2', 'pfiberstart.PACKS = eps',
            'pfiberstart.SENT.SLOTS = eps',
            'pfiberstart.SENT.NAMED = [($ptascii("value"), KNOWN (PSTRING ($ptascii("7")))), '
            '($ptascii("tail"), KNOWN (PSTRING ($ptascii("X"))))]',
            'pfibercaller.OBJECT = n_runner', 'pfibercaller.PREVIOUS = eps',
            'pfibercaller.API.OBJECT = n_runner',
            'pfibercaller.API.START = (pfiberstart.SENT)',
            'pfibercaller.API.SITE = pfiberstart.SITE',
            'pfibercaller.API.LINE = pfiberstart.LINE',
            'pfibercaller.API.PACKS = [(FIBER_ARRAY_PACK pconfigpack)]', 'pconfigpack.INDEX = 0',
            'pconfigpack.ITEMS = [ENTRY (KSTRING ($ptascii("value"))) (DIRECT (PSTRING ($ptascii("7")))), '
            'ENTRY (KSTRING ($ptascii("tail"))) (DIRECT (PSTRING ($ptascii("X"))))]',
            '(HARRAY pconfigpack.ARRAY) <- S.ALLOCATIONS',
            '$intrinsic_count(S, pfiberstart.SITE) = (1)',
            'pfibercaller.VM.TODO = (FIBER_WAIT pfibercaller.API) :: ptask_outer*',
            'S_outer = $fiber_vm_restore(S, pfibercaller.VM)[.ACTIVEFIBER = eps][.FIBERCALLERS = eps]',
            '$fiber_api_valid(S_outer, pfibercaller.API)',
            '$fiber_start_pack_source_valid(S_outer, pfiberstart.SITE, pconfigpack)',
            '$fiber_start_shape(S_outer, pfiberstart.SITE, 1, pfiberstart.SENT, [(FIBER_ARRAY_PACK pconfigpack)])',
            '~$fiber_start_shape(S_outer, pfiberstart.SITE, 2, pfiberstart.SENT, [(FIBER_ARRAY_PACK pconfigpack)])',
            '$fiber_start_core_actor(S)', '$fiber_start_core_live(S, n_capture)',
            '$fiber_start_core_result_valid(S, n_runner, n_capture, pfiberstart)',
            '$call_task_valid(S, FIBER_START_CORE_INVOKE n_runner n_capture pfiberstart)',
            '$task_nodes(FIBER_START_CORE_INVOKE n_runner n_capture pfiberstart) = eps',
            '$task_nodes(FIBER_START_CORE_RESULT n_runner n_capture pfiberstart) = [HOBJECT n_capture]',
            '$node_children(S, HOBJECT n_capture) = [HOBJECT n_target]',
            'psymboltable_global = $fiber_globals(S)',
            '$lookup(psymboltable_global.ENV, $ptascii("capture")) = (n_capture_cell)',
            'S.STORE[n_capture_cell] = DEFINED (POBJECT n_capture)',
            '$lookup(psymboltable_global.ENV, $ptascii("target")) = (n_target_cell)',
            'S.STORE[n_target_cell] = DEFINED (POBJECT n_target)',
            '$lookup(psymboltable_global.ENV, $ptascii("runner")) = (n_runner_cell)',
            'S.STORE[n_runner_cell] = DEFINED (POBJECT n_runner)',
            'H = $heap_graph(S)', '$heap_owners(H, HOBJECT n_capture) = 3',
            '$heap_owners(H, HOBJECT n_target) = 2', '$heap_owners(H, HOBJECT n_runner) = 2',
            '$heap_owners(H, HARRAY pconfigpack.ARRAY) = 1',
            '$heap_count(HARRAY pconfigpack.ARRAY, $pools_nodes(S.POOLS)) = 1', *review.VALID,
            *outer_pack('missing', 'eps'),
            *outer_pack('duplicate', '[(FIBER_ARRAY_PACK pconfigpack), (FIBER_ARRAY_PACK pconfigpack)]'),
            *outer_pack('line', '[(FIBER_ARRAY_PACK pconfigpack[.LINE = $(pconfigpack.LINE + 1)])]'),
            *outer_pack('index', '[(FIBER_ARRAY_PACK pconfigpack[.INDEX = 1])]'),
            'pfiberstart_inner = pfiberstart[.PACKS = [(FIBER_ARRAY_PACK pconfigpack)]]',
            'S_inner = S[.TODO = [FIBER_START_CORE_INVOKE n_runner n_capture pfiberstart_inner, '
            'FIBER_START_CORE_RESULT n_runner n_capture pfiberstart_inner, FIBER_FINISH n_runner]]',
            '$heap_graph(S_inner) = H',
            '~$fiber_start_core_result_valid(S_inner, n_runner, n_capture, pfiberstart_inner)',
            '~$call_descriptors_valid(S_inner)', *ZERO,
            'S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
            'S_one = S_one_budget[.COMPLETION = NORMAL]',
            'S_one.ACTIVEFIBER = (n_target)',
            'S_one.FIBERCALLERS = [pfibercaller_inner, pfibercaller]',
            'pfibercaller_inner.PREVIOUS = (n_runner)',
            'pfibercaller_inner.API.START = (pfiberstart.SENT)',
            'pfibercaller_inner.API.PACKS = eps',
            '$fiber_caller_api_nodes(pfibercaller_inner) = eps',
            '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
            'S_wait = $fiber_vm_restore(S_one, pfibercaller_inner.VM)'
            '[.ACTIVEFIBER = (n_runner)][.FIBERCALLERS = [pfibercaller]]',
            '$fiber_start_core_wait_valid(S_wait, pfibercaller_inner.API)',
            '$fiber_api_valid(S_wait, pfibercaller_inner.API)',
            'S_done = $drive(S_one, 4000)', *review.DONE,
            events('F|', '7', '|', 'X', '|', '1', '|', 'Y', '|', '1', '|', '17', '|',
                   'A|', '9', '|', 'Q', '|', '1', '|', 'Z', '|', '1', '|', '23'),
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
    review.__file__ = str(Path(__file__).resolve())
    passed = all(review.run([name]) for name in args.case or list(CASES))
    assert CATALOG.read_bytes() == SOURCE_BYTES, 'START unpack catalog changed during run'
    raise SystemExit(0 if passed else 1)
