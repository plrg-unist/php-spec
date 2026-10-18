#!/usr/bin/env python3
"""Reach close-time copied-return transfer and ordinary COMPLETE consumption."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_owning_detached_return_cases.json')
INPUTS = [Path(__file__), CATALOG, Path(review.__file__)]
ROWS = {row['id']: row for row in json.loads(CATALOG.read_bytes())}
CLOSE = 'generator-owning-detached-return-object-close'
CONSUME = 'generator-owning-detached-return-array-next-consumption'
EVENTS = {
    CLOSE: ['P|','G|','C|','L|','V|','HELD|','K|','1','|','M|',
            'T|','10','|','NOFRAME|','NOPREV|','F|','A|','E','R|'],
    CONSUME: ['P|','G|','C|','L|','M|','T|','7','|','NOFRAME|','N|',
              'BODY|','1','|','R|','DROP|','CURRENT|','31','|','1','|',
              'N2|','TAIL|','F|','DONE|','0','|','1','|','E'],
}
assert all(''.join(parts) == ROWS[name]['native_stdout'] for name, parts in EVENTS.items())


def outputs(parts):
    return '[' + ', '.join('OUTPUT $ptascii(' + json.dumps(part) + ')' for part in parts) + ']'


VALID = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
BUDGET = [
    'S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
    'S_zero[.COMPLETION = NORMAL] = S',
    'S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
    'S_one = S_one_budget[.COMPLETION = NORMAL]', 'S_one.EVENTS = S.EVENTS',
    '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
    'S_two_budget = $drive_steps(S_one, 1)', '$drive(S, 2) = S_two_budget',
    '$drive_steps(S_zero[.COMPLETION = NORMAL], 2) = S_two_budget',
]
DONE = [
    'S_done = $drive(S_one, 4000)', 'S_done.COMPLETION = NORMAL',
    'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps',
    'S_done.HELD = eps', '$call_descriptors_valid(S_done)',
    '$heap_valid($heap_graph(S_done))',
]

CASES = {
    'owning-return-close-transfers-the-physical-count': {
        'source': ROWS[CLOSE]['source'],
        'stage': ('S.TODO = (GENERATOR_CLOSE_RELEASE pgenrelease) :: ptask_caller* '
                  '-- if pgenrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n_parent)) :: pdestructionjob_tail* '
                  '-- if $generator_return_waiting(S, n_parent) '
                  '-- if S_unheld = S[.TODO = (GENERATOR_CLOSE_RELEASE pgenrelease[.JOBS = pdestructionjob_tail*]) :: ptask_caller*] '
                  '-- if $heap_owners($heap_graph(S_unheld), HOBJECT n_parent) = 0'),
        'checks': [
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.ACTIVEFIBER = eps',
            'S.GC.ACTIVE = eps', 'S.GENERATORRETURNRETAINED = eps',
            'S.GENERATORINPUTS = eps', 'S.GENERATORLOOPRETAINED = eps',
            'S.OBJECTS[n_parent] = GENERATOR pgenerator_parent',
            'pgenerator_parent.PHASE = GENERATOR_DELEGATING',
            '~pgenerator_parent.PENDING_INIT', 'pgenerator_parent.PARKED = eps',
            'pgenerator_parent.DELEGATE = (pgeneratorfrom)',
            'pgeneratorfrom.INPUT = eps', 'pgeneratorfrom.ACQUISITION = eps',
            'pgeneratorfrom.CURRENT = (KNOWN (POBJECT n_cache))',
            'pgeneratorfrom.POSITION = 1', 'pgenerator_parent.FRAME = (pframe_parent)',
            'pframe_parent.ORIGIN = (pgeneratorfrom.SITE)', 'pframe_parent.HELD = eps',
            'pframe_parent.TODO = ptask_complete :: ptask_return_tail*',
            'ptask_complete = GENERATOR_FROM_COMPLETE n_parent pgeneratorfrom.SITE n_child (POBJECT n_return)',
            '$generator_input_tail(S, pgeneratorfrom.SITE, ptask_return_tail*)',
            '$tasks_nodes(ptask_return_tail*) = eps',
            '$generator_return_site(S, n_parent, pgeneratorfrom.SITE)',
            '$generator_return_receipt(S, n_parent, pgeneratorfrom.SITE, n_child, POBJECT n_return)',
            '$generator_from_complete_valid(S, n_parent, pgeneratorfrom.SITE, n_child, POBJECT n_return)',
            'S.OBJECTS[n_child] = GENERATOR pgenerator_child',
            'pgenerator_child.PHASE = GENERATOR_CLOSED',
            'pgenerator_child.RETURN = (POBJECT n_return)',
            '~((HOBJECT n_child) <- S.ALLOCATIONS)',
            '$object_name(S, n_return) = $ptascii("DetachedReturn27")',
            '$object_name(S, n_cache) = $ptascii("DetachedCache27")',
            '$task_nodes(ptask_complete) = [HOBJECT n_return]',
            '$heap_count(HOBJECT n_return, $machine_roots(S)) = 0',
            '$heap_count(HOBJECT n_return, $node_children(S, HOBJECT n_parent)) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_return) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_cache) = 1',
            '~(n_return <- S.DESTRUCTION.CALLED)', '~(n_cache <- S.DESTRUCTION.CALLED)',
            '$generator_unpack_delegate(S, n_parent)',
            '~$generator_unpack_detached(S, n_parent)',
            '~$generator_unpack_chain(S, n_parent, |S.OBJECTS|)',
            'pframe_parent.TODO = ptask_complete :: (ORIGIN_RETURN (porigin_assign)) :: (WRITE_NAME n_target* z_target) :: ptask_used_tail*',
            'pframe_wrong = pframe_parent[.TODO = ptask_complete :: (ORIGIN_RETURN (porigin_assign)) :: (WRITE_NAME $ptascii("wrong27") z_target) :: ptask_used_tail*]',
            'S_wrong = $generator_set(S, n_parent, pgenerator_parent[.FRAME = (pframe_wrong)])',
            '$heap_graph(S_wrong) = $heap_graph(S)',
            '~$generator_return_waiting(S_wrong, n_parent)',
            '~$generator_unpack_delegate(S_wrong, n_parent)',
            'S_held = $generator_set(S, n_parent, pgenerator_parent[.FRAME = (pframe_parent[.HELD = [HOBJECT n_return]])])',
            '~$generator_return_waiting(S_held, n_parent)',
            'S_double = $generator_set(S, n_parent, pgenerator_parent[.FRAME = (pframe_parent[.TODO = pframe_parent.TODO ++ [ptask_complete]])])',
            '~$generator_return_waiting(S_double, n_parent)',
            'pgeneratorfrom.SITE = PORIGIN n_unit pcpath_site',
            'porigin_wrong = PORIGIN n_unit (pcpath_site ++ [PCFIELD 999])',
            '~$generator_return_receipt(S, n_parent, porigin_wrong, n_child, POBJECT n_return)',
            '~$generator_return_receipt(S, n_parent, pgeneratorfrom.SITE, n_child, PINT 1)',
            'pconfigcall_gc = {SITE pgeneratorfrom.SITE, KIND INTRINSIC_GC_COLLECT, INDEX 0, SENT eps, NAMED false, OWNER eps, SELECTION eps, LINE 10, PACKS eps}',
            'S_gc = S[.TODO = (CONFIG_INVOKE pconfigcall_gc) :: S.TODO]',
            '$heap_graph(S_gc) = $heap_graph(S)',
            'S_gc_stop = $gc_begin(S_gc, pconfigcall_gc)',
            'S_gc_stop.COMPLETION = UNSUPPORTED "owning detached Generator return collection"',
            'S_gc_stop[.COMPLETION = NORMAL] = S_gc',
            'S.EVENTS = ' + outputs(EVENTS[CLOSE][:15]),
            *VALID, *BUDGET,
            'S_one.GENERATORRETURNRETAINED = [ptask_complete]',
            '$generator_return_retained_record(S_one, ptask_complete)',
            '$generator_return_retained_valid(S_one, S_one.GENERATORRETURNRETAINED)',
            '~$generator_return_retained_valid(S_one, [ptask_complete, ptask_complete])',
            '~$generator_return_retained_record(S_one, GENERATOR_FROM_COMPLETE n_parent porigin_wrong n_child (POBJECT n_return))',
            'S_one.TODO = (GENERATOR_CLOSE_RELEASE pgenrelease_inputs) :: (GENERATOR_CLOSE_ENTER pgenclose) :: (GENERATOR_CLOSE_RELEASE pgenrelease[.JOBS = pdestructionjob_tail*]) :: ptask_caller*',
            'pgenrelease_inputs.JOBS = eps', 'pgenclose.OBJECT = n_parent',
            'pgenclose.FRAME = (pframe_parent[.TODO = ptask_return_tail*])',
            'pgenclose.STAGE = CLOSE_QUEUED', 'pgenclose.SITE = pgeneratorfrom.SITE',
            'S_one.OBJECTS[n_parent] = GENERATOR pgenerator_parent[.FRAME = eps][.PHASE = GENERATOR_CLOSING]',
            '$tasks_nodes(S_one.GENERATORRETURNRETAINED) = [HOBJECT n_return]',
            '$heap_count(HOBJECT n_return, $machine_roots(S_one)) = 1',
            '$heap_count(HOBJECT n_return, $node_children(S_one, HOBJECT n_parent)) = 0',
            '$heap_owners($heap_graph(S_one), HOBJECT n_return) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_cache) = 1',
            'S_one.STORE = S.STORE', 'S_one.ARRAYS = S.ARRAYS',
            'S_one.ALLOCATIONS = S.ALLOCATIONS', 'S_one.GC = S.GC',
            *DONE, 'S_done.EVENTS = ' + outputs(EVENTS[CLOSE]),
            'S_done.GENERATORRETURNRETAINED = [ptask_complete]',
            '$generator_return_retained_record(S_done, ptask_complete)',
            '$heap_owners($heap_graph(S_done), HOBJECT n_return) = 1',
            'n_return <- S_done.DESTRUCTION.CALLED', 'n_cache <- S_done.DESTRUCTION.CALLED',
            '~((HOBJECT n_parent) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_cache) <- S_done.ALLOCATIONS)',
        ],
    },
    'owning-array-complete-consumes-into-the-real-result': {
        'source': ROWS[CONSUME]['source'],
        'stage': ('S.TODO = (GENERATOR_FROM_COMPLETE n_parent porigin_site n_child (PARRAY n_array)) :: ptask_return_tail* '
                  '-- if S.CURRENT = (pcallcontext) '
                  '-- if S.OBJECTS[n_parent] = GENERATOR pgenerator_parent '
                  '-- if pgenerator_parent.PHASE = GENERATOR_RUNNING'),
        'checks': [
            'pcallcontext.FUNCTION = pgenerator_parent.FUNCTION',
            'pgenerator_parent.FRAME = eps', 'pgenerator_parent.PARKED = eps',
            'S.GENERATORRETURNRETAINED = eps', 'S.GENERATORINPUTS = eps',
            'S.GENERATORLOOPRETAINED = eps', 'S.GC.ACTIVE = eps',
            'S.RESULT = KNOWN PNULL', 'pgenerator_parent.DELEGATE = (pgeneratorfrom)',
            'pgeneratorfrom.SITE = porigin_site', 'pgeneratorfrom.INPUT = eps',
            'pgeneratorfrom.ACQUISITION = eps', 'pgeneratorfrom.CURRENT = (KNOWN (PINT 9))',
            'S.OBJECTS[n_child] = GENERATOR pgenerator_child',
            'pgenerator_child.PHASE = GENERATOR_CLOSED',
            'pgenerator_child.RETURN = (PARRAY n_array)',
            '~((HOBJECT n_child) <- S.ALLOCATIONS)',
            '$generator_return_site(S, n_parent, porigin_site)',
            '$generator_return_receipt(S, n_parent, porigin_site, n_child, PARRAY n_array)',
            '$generator_from_complete_valid(S, n_parent, porigin_site, n_child, PARRAY n_array)',
            '~$generator_return_waiting(S, n_parent)',
            '$generator_input_tail(S, porigin_site, ptask_return_tail*)',
            '$tasks_nodes(ptask_return_tail*) = eps',
            'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_return))]',
            '$object_name(S, n_return) = $ptascii("DetachedArrayReturn27")',
            '$heap_owners($heap_graph(S), HARRAY n_array) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_return) = 1',
            '$task_nodes(GENERATOR_FROM_COMPLETE n_parent porigin_site n_child (PARRAY n_array)) = [HARRAY n_array]',
            '$node_children(S, HARRAY n_array) = [HOBJECT n_return]',
            '~(n_return <- S.DESTRUCTION.CALLED)',
            'S.EVENTS = ' + outputs(EVENTS[CONSUME][:10]),
            *VALID, *BUDGET,
            'S_one.TODO = ptask_return_tail*', 'S_one.ORIGIN = (porigin_site)',
            'S_one.RESULT = KNOWN (PARRAY n_array)',
            'S_one.BASE = BASE_VALUE (KNOWN PNULL)',
            'S_one.GENERATORRETURNRETAINED = eps',
            'S_one.OBJECTS = S.OBJECTS', 'S_one.STORE = S.STORE',
            'S_one.ARRAYS = S.ARRAYS', 'S_one.ALLOCATIONS = S.ALLOCATIONS',
            'S_one.FRAMES = S.FRAMES', 'S_one.CURRENT = S.CURRENT', 'S_one.GC = S.GC',
            '$heap_owners($heap_graph(S_one), HARRAY n_array) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_return) = 1',
            '$node_children(S_one, HARRAY n_array) = [HOBJECT n_return]',
            '~(n_return <- S_one.DESTRUCTION.CALLED)',
            *DONE, 'S_done.EVENTS = ' + outputs(EVENTS[CONSUME]),
            'S_done.GENERATORRETURNRETAINED = eps',
            '~((HARRAY n_array) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_return) <- S_done.ALLOCATIONS)',
            'n_return <- S_done.DESTRUCTION.CALLED',
            '~((HOBJECT n_parent) <- S_done.ALLOCATIONS)',
        ],
    },
}


CASES['retained-return-valid-in-real-force-close-finally'] = {
    'source': ROWS[CLOSE]['source'],
    'stage': ('S.GENERATORRETURNRETAINED = [(GENERATOR_FROM_COMPLETE n_parent porigin_site n_child (POBJECT n_return))] '
              '-- if S.CURRENT = (pcallcontext) '
              '-- if S.OBJECTS[n_parent] = GENERATOR pgenerator_parent '
              '-- if pgenerator_parent.PHASE = GENERATOR_RUNNING '
              '-- if S.FRAMES = pframe_caller :: pframe_outer* '
              '-- if pframe_caller.TODO = (GENERATOR_CLOSE_DONE pgenclose) :: ptask_caller* '
              '-- if pgenclose.OBJECT = n_parent'),
    'checks': [
        'pcallcontext.FUNCTION = pgenerator_parent.FUNCTION',
        'pcallcontext = pgenclose.CONTEXT', 'pgenerator_parent.FRAME = eps',
        'pgenerator_parent.PARKED = eps', 'pgenclose.SITE = porigin_site',
        'pgenclose.FRAME = eps', 'pgenclose.STAGE = CLOSE_BODY porigin_finally',
        '$generator_close_saved(S, S.CURRENT, S.FRAMES) = (pgenclose)',
        '$generator_close_active(S)', '$generator_return_closing(S, n_parent)',
        'ptask_complete = GENERATOR_FROM_COMPLETE n_parent porigin_site n_child (POBJECT n_return)',
        '$generator_return_retained_record(S, ptask_complete)',
        '$generator_return_retained_valid(S, S.GENERATORRETURNRETAINED)',
        '$tasks_nodes(S.GENERATORRETURNRETAINED) = [HOBJECT n_return]',
        '$heap_owners($heap_graph(S), HOBJECT n_return) = 1',
        '~(n_return <- S.DESTRUCTION.CALLED)',
        'pgenerator_parent.DELEGATE = (pgeneratorfrom)',
        'pgeneratorfrom.CURRENT = (KNOWN (POBJECT n_cache))',
        '$heap_owners($heap_graph(S), HOBJECT n_cache) = 1',
        '~(n_cache <- S.DESTRUCTION.CALLED)',
        '~((HOBJECT n_child) <- S.ALLOCATIONS)',
        'S_noclaim = S[.FRAMES = eps]',
        '~$generator_return_closing(S_noclaim, n_parent)',
        '~$generator_return_retained_record(S_noclaim, ptask_complete)',
        '~$call_descriptors_valid(S_noclaim)',
        'porigin_site = PORIGIN n_unit pcpath_site',
        'porigin_wrong = PORIGIN n_unit (pcpath_site ++ [PCFIELD 999])',
        'S_badsite = S[.FRAMES = pframe_caller[.TODO = (GENERATOR_CLOSE_DONE pgenclose[.SITE = porigin_wrong]) :: ptask_caller*] :: pframe_outer*]',
        '$heap_graph(S_badsite) = $heap_graph(S)',
        '~$call_descriptors_valid(S_badsite)',
        'S.EVENTS = ' + outputs(EVENTS[CLOSE][:15]),
        *VALID, *[clause for clause in BUDGET if clause != 'S_one.EVENTS = S.EVENTS'],
        'S_one.GENERATORRETURNRETAINED = S.GENERATORRETURNRETAINED',
        '$heap_owners($heap_graph(S_one), HOBJECT n_return) = 1',
        *DONE, 'S_done.EVENTS = ' + outputs(EVENTS[CLOSE]),
        'S_done.GENERATORRETURNRETAINED = [ptask_complete]',
        '$generator_return_retained_record(S_done, ptask_complete)',
        'n_return <- S_done.DESTRUCTION.CALLED',
    ],
}


def run(selected):
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=review.ROOT, text=True).strip()
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path): digest(path) for path in INPUTS}
    review.CASES = CASES
    original = review.recorded
    raw = None

    def recorded(command, directory, stem, environment, cap):
        nonlocal raw
        raw = directory.parent
        return original(command, directory, stem, environment, cap)

    review.recorded = recorded
    try:
        passed = review.run(selected)
    finally:
        review.recorded = original
    stable = before == {str(path): digest(path) for path in INPUTS}
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=review.ROOT, text=True).strip()
    path = raw / 'report.json'
    report = json.loads(path.read_bytes())
    report.update(author_inputs=before, author_inputs_stable=stable, head_stable=head_stable,
                  passed=passed and stable and head_stable)
    path.write_text(json.dumps(report, indent=2) + '\n')
    return passed and stable and head_stable


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    raise SystemExit(0 if run(parser.parse_args().case) else 1)
