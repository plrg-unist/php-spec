#!/usr/bin/env python3
"""Reach live Middle cache cleanup after CURRENT retires its closed-child prefix."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_refresh_unused_current_review_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {row['id']: row for row in json.loads(INPUT_BYTES[CATALOG])}
NORMAL = 'review-refresh-unused-current-physical-finally-slot-clear'
THROWING = 'review-refresh-unused-current-physical-finally-slot-throw'
PREFIX = ['P|', 'U|', 'M|', 'C|', 'YIELDED|', 'INIT-M|', 'L|', 'H|',
          'S|', 'TAKE|', 'CLEARED|']
EVENTS = {
    NORMAL: PREFIX + ['J|', 'D|', 'J-END|', 'K|', 'CALLER|', 'E'],
    THROWING: PREFIX + ['J|', 'D|', 'K|', 'CAUGHT|', '1', '|', '1', '|',
                        '1', '|', '0', '|', '1', '|', 'E'],
}


def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


def events(state, parts):
    return state + '.EVENTS = [' + ', '.join('OUTPUT $ptascii(' + json.dumps(part) + ')' for part in parts) + ']'


STAGE = ('S.CURRENT = (pcallcontext) -- if pcallcontext.RECEIVER = (n_cache) '
         '-- if $object_name(S, n_cache) = $ptascii("RefreshUnusedCurrentObjectCache52")')
COMMON = checks(r"""
S.COMPLETION = NORMAL
S.ACTIVEFIBER = eps
S.GC.ACTIVE = eps
S.GENERATORINPUTS = eps
S.GENERATORRETURNRETAINED = eps
S.GENERATORLOOPRETAINED = eps
S.FRAMES = [pframe_finally, pframe_root]
pframe_finally.CONTEXT = (pcallcontext_middle)
pframe_finally.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: ptask_finally_tail*
pdestructorcall.OBJECT = n_cache
pdestructorcall.PENDING = eps
pdestructorcall.OPERATION = (pdestructionoperation_store)
S.DESTRUCTION.OPERATIONS = [pdestructionoperation_store, pdestructionoperation_current]
pdestructionoperation_store.CALLER = (pcallcontext_middle)
pdestructionoperation_store.VALUE = KNOWN PNULL
pdestructionoperation_store.PENDING = eps
pdestructionoperation_store.COMPLETION = NORMAL
pdestructionoperation_store.SOURCE = ptask_store
~$eager_explicit_task(ptask_store)
pdestructionoperation_current.SOURCE = GENERATOR_ARGS pgeneratorop eps eps
pgeneratorop.NAME = "current"
pgeneratorop.LINE = 13
pgeneratorop.ARGUMENTS = eps
pgeneratorop.LOOP = eps
~pgeneratorop.BORROWED
~pgeneratorop.STARTPACK
~pgeneratorop.ADVANCE
n_upper = pgeneratorop.OBJECT
pdestructionoperation_current.VALUE = KNOWN PNULL
pdestructionoperation_current.PENDING = eps
pdestructionoperation_current.CALLER = eps
pdestructionoperation_current.COMPLETION = NORMAL
pdestructionoperation_current.CLEANUP = eps
pdestructionoperation_current.NOGC = eps
~$reference_call_used(S, pgeneratorop.SITE)
pframe_root.CONTEXT = eps
pframe_root.TODO = (GENERATOR_CLOSE_DONE pgenclose) :: ptask_root_tail*
n_middle = pgenclose.OBJECT
n_middle =/= n_upper
S.OBJECTS[n_middle] = GENERATOR pgenerator_middle
pgenerator_middle.PHASE = GENERATOR_RUNNING
~pgenerator_middle.PENDING_INIT
pgenerator_middle.FRAME = eps
pgenerator_middle.PARKED = eps
pgenerator_middle.FUNCTION = pcallcontext_middle.FUNCTION
pgenerator_middle.DELEGATE = (pgeneratorfrom_middle)
pgeneratorfrom_middle.INPUT = eps
pgeneratorfrom_middle.CURRENT = (REFERENCE n_slot)
S_global = $global_table_view(S)
$lookup(S_global.ENV, $ptascii("slot")) = (n_slot)
S.STORE[n_slot] = DEFINED PNULL
n_slot <- S.REFCELLS
$node_children(S, HCELL n_slot) = eps
$heap_owners($heap_graph(S), HCELL n_slot) = 2
$heap_owners($heap_graph(S), HOBJECT n_cache) = 2
$heap_owners($heap_graph(S), HOBJECT n_middle) = 1
$generator_storage_for(S, n_middle) = eps
S.OBJECTS[n_upper] = GENERATOR pgenerator_upper
pgenerator_upper.PHASE = GENERATOR_CLOSING
~pgenerator_upper.PENDING_INIT
pgenerator_upper.FRAME = eps
$generator_return_closing(S, n_upper)
$generator_close_claims(ptask_root_tail*) = [n_upper]
$heap_owners($heap_graph(S), HOBJECT n_upper) = 1
pgenclose.CONTEXT = pcallcontext_middle
pgenclose.SITE = pgeneratorfrom_middle.SITE
pgenclose.STAGE = CLOSE_BODY porigin_finally
pgenclose.PENDING = eps
$task_nodes(GENERATOR_CLOSE_DONE pgenclose) = [HOBJECT n_middle]
$generator_return_closing(S, n_middle)
S_finally = $constant_frame_scope(S, pframe_finally, [pframe_root])
$generator_close_saved(S_finally, S_finally.CURRENT, S_finally.FRAMES) = (pgenclose)
$generator_close_active(S_finally)
$lookup(S_global.ENV, $ptascii("given")) = (n_given_cell)
S.STORE[n_given_cell] = DEFINED (POBJECT n_given)
$throwable_live(S, n_given)
$string_bytes($throwable_field(S, n_given, "message")) = ($ptascii("outside52"))
$throwable_field(S, n_given, "previous") = PNULL
$heap_owners($heap_graph(S), HOBJECT n_given) = 1
$destructor_operation_for(S_finally) = (pdestructionoperation_store)
$destructor_selected_pending(S_finally, eps) = eps
$lookup(S_global.ENV, $ptascii("upper")) = eps
$lookup(S_global.ENV, $ptascii("middle")) = eps
$lookup(S_global.ENV, $ptascii("child")) = eps
$destructor_operation_live(S, pdestructionoperation_store)
~$destructor_operation_valid(S, pdestructionoperation_store)
$destructor_operation_valid(S_finally, pdestructionoperation_store)
$destructor_operation_live(S, pdestructionoperation_current)
$destructor_call_live(S, pdestructorcall)
$destructor_context_valid(S, pcallcontext)
pdestructionoperation_bad = pdestructionoperation_store[.SOURCE = DESTRUCTOR_GLOBALS]
S_bad = S[.DESTRUCTION.OPERATIONS = [pdestructionoperation_bad, pdestructionoperation_current]]
$heap_graph(S_bad) = $heap_graph(S)
~$destructor_operation_live(S_bad, pdestructionoperation_bad)
~$call_descriptors_valid(S_bad)
S_badphase = $generator_set(S_finally, n_middle, pgenerator_middle[.PHASE = GENERATOR_DELEGATING])
$heap_graph(S_badphase) = $heap_graph(S_finally)
~$generator_close_active(S_badphase)
~$call_descriptors_valid(S_badphase)
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
S_zero = $drive(S, 0)
S_zero.COMPLETION = BUDGET
S_zero[.COMPLETION = NORMAL] = S
S_one_budget = $drive_steps(S, 1)
S_one_budget.COMPLETION = BUDGET
S_one = S_one_budget[.COMPLETION = NORMAL]
S_two_budget = $drive_steps(S_one, 1)
$drive(S, 2) = S_two_budget
$drive_steps(S_zero[.COMPLETION = NORMAL], 2) = S_two_budget
S_done = $drive(S_one, 4000)
$drive(S, 4000) = S_done
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.FRAMES = eps
S_done.CURRENT = eps
S_done.HELD = eps
S_done.GENERATORRETURNRETAINED = eps
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
$heap_owners($heap_graph(S_done), HOBJECT n_cache) = 0
$heap_owners($heap_graph(S_done), HCELL n_slot) = 0
$heap_owners($heap_graph(S_done), HOBJECT n_given) = 0
~((HCELL n_slot) <- S_done.ALLOCATIONS)
~((HOBJECT n_middle) <- S_done.ALLOCATIONS)
~((HOBJECT n_upper) <- S_done.ALLOCATIONS)
~((HOBJECT n_cache) <- S_done.ALLOCATIONS)
~((HOBJECT n_given) <- S_done.ALLOCATIONS)
n_cache <- S_done.DESTRUCTION.CALLED
""")
CASES = {
    'refresh-unused-current-normal-cache-inside-live-middle-finally': {
        'source': ROWS[NORMAL]['source'],
        'stage': STAGE,
        'checks': [*COMMON, events('S', PREFIX + ['J|']), events('S_done', EVENTS[NORMAL])],
    },
    'refresh-unused-current-throwing-cache-inside-live-middle-finally': {
        'source': ROWS[THROWING]['source'],
        'stage': STAGE,
        'checks': [*COMMON, events('S', PREFIX + ['J|']), events('S_done', EVENTS[THROWING])],
    },
}


def run(selected):
    assert all(''.join(parts) == ROWS[name]['native_stdout'] for name, parts in EVENTS.items())
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=review.ROOT, text=True).strip()
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
    stable = INPUT_BYTES == {p: p.read_bytes() for p in INPUT_BYTES}
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=review.ROOT, text=True).strip()
    path = raw / 'report.json'
    report = json.loads(path.read_bytes())
    report.update(independent_inputs={str(p): hashlib.sha256(b).hexdigest() for p, b in INPUT_BYTES.items()},
                  independent_inputs_stable=stable, head_stable=head_stable,
                  passed=passed and stable and head_stable)
    path.write_text(json.dumps(report, indent=2) + '\n')
    return passed and stable and head_stable


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    raise SystemExit(0 if run(parser.parse_args().case) else 1)
