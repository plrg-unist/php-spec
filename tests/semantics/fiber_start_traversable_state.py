#!/usr/bin/env python3
"""Reached Iterator teardown and retired Generator-pack core forwarding."""
import argparse
import json
from pathlib import Path
import fiber_state_review as review

ROOT = Path(__file__).resolve().parents[2]
CATALOG = Path(__file__).with_name('fiber_start_traversable_cases.json')
SOURCE_BYTES = CATALOG.read_bytes()
SOURCES = {row['id']: row['source'] for row in json.loads(SOURCE_BYTES)}
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']


def events(*pieces):
    return 'S_done.EVENTS = [' + ', '.join(
        'OUTPUT $ptascii(' + json.dumps(piece) + ')' for piece in pieces) + ']'


UNWIND_EVENTS = events('W|', 'T|', 'I|', 'D', '0', '|', 'F|', 'C', '1', '|',
                       'iterator', '|', '1', '|', 'W|', 'T|', 'I|', 'F|',
                       'D', '1', '|', 'C', '1', '|', 'iterator', '|', '1', '|', 'END')


def unwind(named):
    slots = ('pfibertraversal.SENT.NAMED = [($ptascii("payload"), KNOWN (POBJECT n_arg))]'
             if named else 'pfibertraversal.SENT.SLOTS = [NAMED_SENT (KNOWN (POBJECT n_arg))]')
    item = ('ENTRY (KSTRING ($ptascii("payload"))) (DIRECT (POBJECT n_arg))'
            if named else 'ENTRY (KINT 0) (DIRECT (POBJECT n_arg))')
    ordered = ('HOBJECT pfiberstart.OBJECT, HOBJECT n_arg' if named else
               'HOBJECT n_arg, HOBJECT pfiberstart.OBJECT')
    checks = [
        'S.ACTIVEFIBER = eps', 'S.FIBERCALLERS = eps',
        'S.CURRENT = eps', 'S.FRAMES = eps',
        'pfiberstart = pfibertraversal.START', 'n_iterator = pfibertraversal.OBJECT',
        'pfibertraversal.CAPTURE = eps',
        'pfibertraversal.INPUT = KNOWN (POBJECT n_iterator)',
        'pfibertraversal.CURRENT = KNOWN PNULL',
        'pfiberstart.SENT = {SLOTS eps, NAMED eps}',
        'pfiberstart.INDEX = 0', 'pfiberstart.PACKS = eps', slots,
        f'pfibertraversal.ITEMS = [{item}]',
        '$intrinsic_count(S, pfiberstart.SITE) = (1)',
        'pfiberarray.KIND = INTRINSIC_FIBER_START',
        'pfiberarray.INPUT = (pfiberstart.OBJECT)',
        'pfiberarray.NAME = $ptascii("start")',
        '~((HARRAY pfiberarray.ARRAY) <- S.ALLOCATIONS)',
        '$lookup(S.ENV, $ptascii("pair")) = (n_pair)',
        'S.STORE[n_pair] = DEFINED PNULL',
        '$lookup(S.ENV, $ptascii("target")) = (n_target)',
        'S.STORE[n_target] = DEFINED PNULL',
        '$fiber_at(S, pfiberstart.OBJECT) = (pfiber)',
        'pfiber.STATUS = FIBER_SUSPENDED', '$useriter_instance(S, n_iterator)',
        '$fiber_traversal_input(S, pfibertraversal)',
        '$fiber_traversal_result_valid(S, pfibertraversal, "current")',
        '$fiber_traversal_call_count(S.TODO, pfiberstart.SITE) = 0',
        '$call_task_valid(S, FIBER_TRAVERSE_RESULT pfibertraversal "current")',
        '$fiber_traversal_nodes(pfibertraversal, true) = [HOBJECT n_iterator, HOBJECT n_iterator]',
        'H = $heap_graph(S)', '$heap_owners(H, HOBJECT n_iterator) = 2',
        '$heap_owners(H, HOBJECT pfiberstart.OBJECT) = 1',
        '$heap_owners(H, HOBJECT n_arg) = 1', *review.VALID,
        'S_removed = S[.TODO = (THROW_SEARCH n_throwable) :: '
        '(FIBER_ARRAY_START_RELEASE pfiberarray) :: ptask_tail*]',
        '$fiber_start_unpack_unwind_valid(S_removed, '
        'FIBER_TRAVERSE_RESULT pfibertraversal "current")',
    ]
    if not named:
        checks += [
            'pfibertraversal_bad = pfibertraversal[.LINE = $(pfibertraversal.LINE + 1)]',
            'S_bad = S[.TODO = (THROW_SEARCH n_throwable) :: '
            '(FIBER_TRAVERSE_RESULT pfibertraversal_bad "current") :: '
            '(FIBER_ARRAY_START_RELEASE pfiberarray) :: ptask_tail*]',
            '$heap_graph(S_bad) = H',
            '~$fiber_traversal_result_valid(S_bad, pfibertraversal_bad, "current")',
            '~$call_descriptors_valid(S_bad)',
            'S_duplicate = S[.TODO = (THROW_SEARCH n_throwable) :: '
            '(FIBER_TRAVERSE_RESULT pfibertraversal "current") :: '
            '(FIBER_ARGS pfiberstart) :: (FIBER_ARRAY_START_RELEASE pfiberarray) :: ptask_tail*]',
            '$fiber_start_unpack_count(S_duplicate.TODO, eps, pfiberstart.SITE) = 2',
            '~$fiber_traversal_result_valid(S_duplicate, pfibertraversal, "current")',
            '~$call_descriptors_valid(S_duplicate)',
        ]
    return checks + [
        *ZERO, 'S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
        'S_one = S_one_budget[.COMPLETION = NORMAL]',
        'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (THROW_SEARCH n_throwable) :: '
        '(FIBER_ARRAY_START_RELEASE pfiberarray) :: ptask_tail*',
        'pdestructionrelease.JOBS = $destruction_values([HOBJECT n_iterator, HOBJECT n_iterator, '
        + ordered + '])',
        'pdestructionrelease.CALLER = S.CURRENT', 'pdestructionrelease.ORIGIN = S.ORIGIN',
        'S_one.ALLOCATIONS = S.ALLOCATIONS',
        '$heap_owners($heap_graph(S_one), HOBJECT n_iterator) = 2',
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
    'traversable-positional-unwind-retires-iterator-before-payload-and-receiver': {
        'source': SOURCES['author-fiber-start-iterator-callback-throw-retires-current-before-selected-receiver'],
        'stage': ('S.TODO = (THROW_SEARCH n_throwable) :: '
                  '(FIBER_TRAVERSE_RESULT pfibertraversal "current") :: '
                  '(FIBER_ARRAY_START_RELEASE pfiberarray) :: ptask_tail* '
                  '-- if pfibertraversal.SENT.NAMED = eps'),
        'checks': unwind(False),
    },
    'traversable-named-unwind-retires-iterator-before-receiver-and-payload': {
        'source': SOURCES['author-fiber-start-iterator-callback-throw-retires-current-before-selected-receiver'],
        'stage': ('S.TODO = (THROW_SEARCH n_throwable) :: '
                  '(FIBER_TRAVERSE_RESULT pfibertraversal "current") :: '
                  '(FIBER_ARRAY_START_RELEASE pfiberarray) :: ptask_tail* '
                  '-- if pfibertraversal.SENT.SLOTS = eps'),
        'checks': unwind(True),
    },
    'traversable-core-forwarding-authenticates-retired-generator-history': {
        'source': SOURCES['author-fiber-start-generator-packs-forward-through-fcc-and-raw-core-start'],
        'stage': ('S.TODO = (FIBER_START_CORE_INVOKE n_runner n_capture pfiberstart) :: '
                  '(FIBER_START_CORE_RESULT n_runner n_capture pfiberstart) :: ptask_tail* '
                  '-- if S.FIBERCALLERS = [pfibercaller]'),
        'checks': [
            'ptask_tail* = [FIBER_FINISH n_runner]',
            'S.ACTIVEFIBER = (n_runner)', 'S.CURRENT = eps', 'S.FRAMES = eps',
            '$fiber_at(S, n_runner) = (pfiber_runner)',
            'pfiber_runner.RAW = POBJECT n_capture',
            'pfiber_runner.TARGET = (FIBER_API_TARGET n_capture)',
            'pfiber_runner.ENTRY = (pfiberstart.SENT)',
            'S.OBJECTS[n_capture] = FIBERAPICLOSURE pfibercapture',
            'pfibercapture.KIND = INTRINSIC_FIBER_START',
            'pfibercapture.INPUT = (n_target)', 'pfiberstart.OBJECT = n_target',
            'pfiberstart.INDEX = 2', 'pfiberstart.PACKS = eps',
            'pfiberstart.SENT.SLOTS = eps',
            'pfiberstart.SENT.NAMED = [($ptascii("value"), KNOWN (PSTRING ($ptascii("7")))), '
            '($ptascii("tail"), KNOWN (PSTRING ($ptascii("X"))))]',
            'pfibercaller.PREVIOUS = eps', 'pfibercaller.OBJECT = n_runner',
            'pfibercaller.API.OBJECT = n_runner',
            'pfibercaller.API.START = (pfiberstart.SENT)',
            'pfibercaller.API.SITE = pfiberstart.SITE',
            'pfibercaller.API.PACKS = [FIBER_TRAVERSABLE_PACK ptraversablepack]',
            'ptraversablepack.INDEX = 0', 'n_generator = ptraversablepack.OBJECT',
            'ptraversablepack.ITEMS = [ENTRY (KSTRING ($ptascii("value"))) (DIRECT (PSTRING ($ptascii("7")))), '
            'ENTRY (KSTRING ($ptascii("tail"))) (DIRECT (PSTRING ($ptascii("X"))))]',
            'S.OBJECTS[n_generator] = GENERATOR pgenerator',
            'pgenerator.PHASE = GENERATOR_CLOSED',
            '~((HOBJECT n_generator) <- S.ALLOCATIONS)',
            '$intrinsic_count(S, pfiberstart.SITE) = (1)',
            'pfibercaller.VM.TODO = (FIBER_WAIT pfibercaller.API) :: ptask_outer*',
            'S_outer = $fiber_vm_restore(S, pfibercaller.VM)[.ACTIVEFIBER = eps][.FIBERCALLERS = eps]',
            '$fiber_traversal_history(S_outer, pfiberstart.SITE, ptraversablepack)',
            '$fiber_api_valid(S_outer, pfibercaller.API)',
            '$fiber_start_shape(S_outer, pfiberstart.SITE, 1, pfiberstart.SENT, pfibercaller.API.PACKS)',
            '~$fiber_start_shape(S_outer, pfiberstart.SITE, 2, pfiberstart.SENT, pfibercaller.API.PACKS)',
            '$fiber_start_core_actor(S)', '$fiber_start_core_live(S, n_capture)',
            '$fiber_start_core_result_valid(S, n_runner, n_capture, pfiberstart)',
            '$task_nodes(FIBER_START_CORE_RESULT n_runner n_capture pfiberstart) = [HOBJECT n_capture]',
            '$node_children(S, HOBJECT n_capture) = [HOBJECT n_target]',
            'H = $heap_graph(S)', '$heap_owners(H, HOBJECT n_generator) = 0',
            '$heap_owners(H, HOBJECT n_capture) = 2',
            '$heap_owners(H, HOBJECT n_target) = 2',
            '$heap_owners(H, HOBJECT n_runner) = 2', *review.VALID,
            *outer_pack('missing', 'eps'),
            *outer_pack('line', '[FIBER_TRAVERSABLE_PACK ptraversablepack[.LINE = $(ptraversablepack.LINE + 1)]]'),
            *outer_pack('index', '[FIBER_TRAVERSABLE_PACK ptraversablepack[.INDEX = 1]]'),
            *outer_pack('duplicate', '[FIBER_TRAVERSABLE_PACK ptraversablepack, '
                        'FIBER_TRAVERSABLE_PACK ptraversablepack]'),
            *ZERO, 'S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
            'S_one = S_one_budget[.COMPLETION = NORMAL]',
            'S_one.ACTIVEFIBER = (n_target)',
            'S_one.FIBERCALLERS = [pfibercaller_inner, pfibercaller]',
            'pfibercaller_inner.PREVIOUS = (n_runner)',
            'pfibercaller_inner.API.START = (pfiberstart.SENT)',
            'pfibercaller_inner.API.PACKS = eps',
            '$fiber_caller_api_nodes(pfibercaller_inner) = eps',
            '$heap_owners($heap_graph(S_one), HOBJECT n_generator) = 0',
            '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
            'S_done = $drive(S_one, 4000)', *review.DONE,
            events('G|', 'C|', '7', '|', 'X', '|', '', '|', '1', '|', '17', '|',
                   'G|', 'C|', '9', '|', 'Q', '|', '', '|', '1', '|', '23'),
        ],
    },
}

# Keep each original fact while separating repeated admission and full resume
# costs. The shared terminal stream covers both positional and named calls.
POSITIONAL = CASES.pop(
    'traversable-positional-unwind-retires-iterator-before-payload-and-receiver')
NAMED = CASES.pop(
    'traversable-named-unwind-retires-iterator-before-receiver-and-payload')
POS_CHECKS = POSITIONAL['checks']
NAMED_CHECKS = NAMED['checks']
POS_LINE = POS_CHECKS.index(
    'pfibertraversal_bad = pfibertraversal[.LINE = $(pfibertraversal.LINE + 1)]')
POS_DUPLICATE = next(i for i, check in enumerate(POS_CHECKS)
                     if check.startswith('S_duplicate = '))
POS_ZERO = POS_CHECKS.index(ZERO[0])
POS_ONE = POS_CHECKS.index('S_one_budget = $drive_steps(S, 1)')
POS_RESUME = POS_CHECKS.index('S_done = $drive(S_one, 4000)')
NAMED_REMOVED = next(i for i, check in enumerate(NAMED_CHECKS)
                     if check.startswith('S_removed = '))
NAMED_ZERO = NAMED_CHECKS.index(ZERO[0])
NAMED_RESUME = NAMED_CHECKS.index('S_done = $drive(S_one, 4000)')
COUNTEREXAMPLE = ['H = $heap_graph(S)', *review.VALID[2:]]
CASES.update({
    'author-positional-release-order': {
        **POSITIONAL,
        'checks': POS_CHECKS[:POS_LINE] + POS_CHECKS[POS_ZERO:POS_RESUME],
    },
    'author-positional-wrong-line': {
        **POSITIONAL,
        'checks': COUNTEREXAMPLE + POS_CHECKS[POS_LINE:POS_DUPLICATE] + ZERO,
    },
    'author-positional-duplicate-schedule': {
        **POSITIONAL,
        'checks': ['pfiberstart = pfibertraversal.START', *COUNTEREXAMPLE,
                   *POS_CHECKS[POS_DUPLICATE:POS_ZERO], *ZERO],
    },
    'author-positional-terminal-fields-and-shared-events': {
        **POSITIONAL,
        'checks': POS_CHECKS[POS_ONE:POS_ONE + 3]
                  + [POS_CHECKS[POS_RESUME], *review.DONE[:-2], UNWIND_EVENTS],
    },
    'author-authentic-terminal-global-and-heap': {
        'source': POSITIONAL['source'],
        'stage': 'S.TODO = eps -- if (OUTPUT $ptascii("END")) <- S.EVENTS',
        'checks': ['S_done = S', *review.DONE[-2:], UNWIND_EVENTS],
    },
    'author-named-authentic-unwind-prefix': {
        **NAMED, 'checks': NAMED_CHECKS[:NAMED_REMOVED],
    },
    'author-named-one-discard-release-order': {
        **NAMED,
        'checks': ['pfiberstart = pfibertraversal.START',
                   'n_iterator = pfibertraversal.OBJECT',
                   'pfibertraversal.SENT.NAMED = [($ptascii("payload"), KNOWN (POBJECT n_arg))]',
                   *NAMED_CHECKS[NAMED_REMOVED:NAMED_ZERO],
                   *NAMED_CHECKS[NAMED_ZERO + len(ZERO):NAMED_RESUME]],
    },
    'author-named-zero-budget-preserves-authentic-state': {
        **NAMED, 'checks': ZERO,
    },
})

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    assert not args.case or set(args.case) <= CASES.keys()
    review.ROOT = ROOT
    review.CASES = CASES
    review.__file__ = str(Path(__file__).resolve())
    passed = all(review.run([name]) for name in args.case or list(CASES))
    assert CATALOG.read_bytes() == SOURCE_BYTES, 'Traversable START catalog changed during run'
    raise SystemExit(0 if passed else 1)
