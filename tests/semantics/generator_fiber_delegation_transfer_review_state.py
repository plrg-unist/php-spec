#!/usr/bin/env python3
"""Reach native delegation resumers and claims across real Fiber transfers.

Defaults cover structure and short budgets for parked two-edge delegation and
one-edge unhandled injection. Both whole completions remain core-required and
explicitly selectable with --case.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_fiber_delegation_transfer_review_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {row['id']: row for row in json.loads(INPUT_BYTES[CATALOG])}
HANDLED = 'review-generator-fiber-delegation-transfer-handled'
UNHANDLED = 'review-generator-fiber-delegation-transfer-unhandled'
CURRENT_LINES = {name: next(i for i, line in enumerate(row['source'].splitlines(), 1)
                            if '$current = $parent->current();' in line)
                 for name, row in ROWS.items()}


def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


def events(parts):
    return 'S_done.EVENTS = [' + ', '.join(
        'OUTPUT (' + json.dumps(list(part.encode())) + ')' for part in parts) + ']'


# These are the actual native observations, separated at source echo operands.
EVENTS = {
    HANDLED: ['START|', 'FIBER|', 'PARENT|', 'MIDDLE|', 'CHILD|', 'pause55', '|',
              'PARKED|', '1', '|', '1', '|', 'INJECT|', 'CHILD-FINALLY|',
              'MIDDLE-FINALLY|', 'PARENT-CAUGHT|', '1', '|', '1', '|', '1', '|',
              'PARENT-FINALLY|', 'CURRENT|', '1', '|', 'REPLY|', '1', '|',
              'FIBER-DONE|', '1', '|', '1', '|', 'LIVE|', '1', '|', 'PARENT-END|',
              'TOKEN|', 'PARENT-DONE|', '0', '|', '1', '|', 'DROPPED|', '1', '|',
              'GIVEN|', '1', '|', 'E'],
    UNHANDLED: ['START|', 'FIBER|', 'PARENT|', 'CHILD|', 'pause55', '|', 'PARKED|',
                '1', '|', '1', '|', 'INJECT|', 'CHILD-FINALLY|', 'PARENT-FINALLY|',
                'TOKEN|', 'OUTER|', '1', '|', '1', '|', '1', '|', 'FIBER-DONE|',
                '1', '|', 'PARENT-DONE|', '0', '|', 'DROPPED|', '1', '|',
                'GIVEN|', '1', '|', 'E'],
}

# NORMAL public drive is preprocessing followed by drive_steps (40-control).
# Prove its fixed points once per input; retain exact budgets and full states.
ENDING = checks(r"""
$call_entry_check(S) = S
$literal_reference_debt_check($output_guard($sensitive_trace_freeze(S))) = S
S_zero = $drive_steps(S, 0)
S_zero.COMPLETION = BUDGET
S_zero[.COMPLETION = NORMAL] = S
S_one_budget = $drive_steps(S, 1)
S_one_budget.COMPLETION = BUDGET
S_one = S_one_budget[.COMPLETION = NORMAL]
$call_entry_check(S_one) = S_one
$literal_reference_debt_check($output_guard($sensitive_trace_freeze(S_one))) = S_one
S_two_budget = $drive_steps(S_one, 1)
$drive_steps(S, 2) = S_two_budget
$drive_steps(S_zero[.COMPLETION = NORMAL], 2) = S_two_budget
S_done = $drive_steps(S_one, 4000)
$drive_steps(S, 4000) = S_done
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.FRAMES = eps
S_done.CURRENT = eps
S_done.HELD = eps
S_done.ACTIVEFIBER = eps
S_done.FIBERCALLERS = eps
S_done.FIBERCLOSERS = eps
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
~((HOBJECT n_fiber) <- S_done.ALLOCATIONS)
~((HOBJECT n_child) <- S_done.ALLOCATIONS)
~((HOBJECT n_parent) <- S_done.ALLOCATIONS)
~((HOBJECT n_token) <- S_done.ALLOCATIONS)
~((HOBJECT n_given) <- S_done.ALLOCATIONS)
n_token <- S_done.DESTRUCTION.CALLED
$generator_saved_fiber_ids(S_done) = eps
$generator_from_saved_fiber_claims(S_done) = eps
""")


SHORT_ENDING = ENDING[:ENDING.index('S_done = $drive_steps(S_one, 4000)')]

def chain(middle, name):
    levels = ['child', 'middle', 'parent'] if middle else ['child', 'parent']
    frames = ', '.join('pframe_' + level for level in levels) + ', pframe_fiber'
    ids = '[' + ', '.join('n_' + level for level in levels) + ']'
    claims = '[' + ', '.join('n_' + level for level in levels[1:]) + ']'
    result = checks(f"""
S.COMPLETION = NORMAL
S.FIBERCLOSERS = eps
S.GC.ACTIVE = eps
S_live.CURRENT = (pcallcontext_child)
pcallcontext_child.NAME = $ptascii("DelegationLeaf55")
S_live.FRAMES = [{frames}]
pframe_fiber.TODO = [FIBER_FINISH n_fiber]
pframe_fiber.CONTEXT = eps
pframe_parent.TODO = (GENERATOR_RESUME pgeneratorop_parent) :: ptask_parent*
pframe_parent.CONTEXT = (pcallcontext_callback)
pframe_parent.ORIGIN = (pgeneratorop_parent.SITE)
pgeneratorop_parent.NAME = "current"
pgeneratorop_parent.LINE = {CURRENT_LINES[name]}
n_parent = pgeneratorop_parent.OBJECT
$lookup(S_live.ENV, $ptascii("token")) = (n_token_cell_child)
S_live.STORE[n_token_cell_child] = DEFINED (POBJECT n_token)
$object_name(S_live, n_token) = $ptascii("DelegationTransferToken55")
H = $heap_graph(S)
$heap_owners(H, HOBJECT n_token) = {len(levels)}
$heap_owners(H, HCELL n_token_cell_child) = 1
""")
    # Bind the actual task/context records before querying their object fields.
    for level, parent in zip(levels, levels[1:]):
        result += checks(f"""
pframe_{level}.TODO = (GENERATOR_RESUME pgeneratorop_{level}) :: (GENERATOR_FROM_RESULT n_{parent} porigin_{parent} n_{level}) :: ptask_{level}*
pframe_{level}.ORIGIN = (porigin_{parent})
pframe_{level}.CONTEXT = (pcallcontext_{parent})
pframe_{level}.LOCALS = (psymboltable_{parent})
pgeneratorop_{level}.SITE = porigin_{parent}
""")
    for level in levels:
        result += checks(f"""
S_live.OBJECTS[n_{level}] = GENERATOR pgenerator_{level}
pgenerator_{level}.PHASE = GENERATOR_RUNNING
pgenerator_{level}.FRAME = eps
pgenerator_{level}.PARKED = eps
pgenerator_{level}.RETURN = eps
pgenerator_{level}.VALUE = eps
pgenerator_{level}.REFCELL = eps
pgenerator_{level}.BORROWED = eps
pgenerator_{level}.CLOSURE = eps
pgenerator_{level}.ACCESS = eps
pgenerator_{level}.FUNCTION = pcallcontext_{level}.FUNCTION
pcallcontext_{level}.TARGET = pcallcontext_{level}.FUNCTION
pcallcontext_{level}.INSTANCE = eps
pgeneratorop_{level}.OBJECT = n_{level}
pgeneratorop_{level}.NAME = "current"
pgeneratorop_{level}.ARGUMENTS = eps
pgeneratorop_{level}.LOOP = eps
~pgeneratorop_{level}.ADVANCE
~pgeneratorop_{level}.STARTPACK
~pgeneratorop_{level}.BORROWED
(HOBJECT n_{level}) <- S.ALLOCATIONS
""")
    for level, parent in zip(levels, levels[1:]):
        result += checks(f"""
pgenerator_{parent}.DELEGATE = (pgeneratorfrom_{parent})
pgeneratorfrom_{parent}.SITE = porigin_{parent}
pgeneratorfrom_{parent}.INPUT = (POBJECT n_{level})
pgeneratorfrom_{parent}.POSITION = 0
pgeneratorfrom_{parent}.ACQUISITION = eps
pgeneratorfrom_{parent}.CURRENT = eps
pgenerator_{parent}.PENDING_INIT
$lookup(psymboltable_{parent}.ENV, $ptascii("token")) = (n_token_cell_{parent})
S_live.STORE[n_token_cell_{parent}] = DEFINED (POBJECT n_token)
$heap_owners(H, HCELL n_token_cell_{parent}) = 1
""")
    result += checks(f"""
n_token_cell_child =/= n_token_cell_parent
pgenerator_child.DELEGATE = eps
~pgenerator_child.PENDING_INIT
$generator_resume_ids(S_live.TODO) = eps
$generator_saved_ids(S_live.FRAMES) = {ids}
$generator_from_claims(S_live.TODO) ++ $generator_from_saved_claims(S_live.FRAMES) = {claims}
$generator_resume_pairs(S_live, S_live.CURRENT, S_live.FRAMES)
$fiber_generator_body_id(S_live) = eps
$fiber_generator_chain_ids(S_live) = {ids}
$fiber_generator_delegation_ids(S_live) = {ids}
$fiber_generator_transfer(S_live)
$fiber_transfer_domain(S_live)
S_without_owner = S_live[.ACTIVEFIBER = eps]
~$fiber_generator_transfer(S_without_owner)
~$fiber_transfer_domain(S_without_owner)
S_projected = $constant_frame_scope(S_live, pframe_child, [{', '.join('pframe_' + level for level in levels[1:])}, pframe_fiber])[.TODO = ptask_child*]
S_projected.STORE = S_live.STORE
S_projected.OBJECTS = S_live.OBJECTS
S_projected.ALLOCATIONS = S_live.ALLOCATIONS
$fiber_generator_chain_ids(S_projected) = {claims}
""")
    if middle:
        result += checks(r"""
n_token_cell_child =/= n_token_cell_middle
n_token_cell_middle =/= n_token_cell_parent
S_projected_parent = $constant_frame_scope(S_projected, pframe_middle, [pframe_parent, pframe_fiber])[.TODO = ptask_middle*]
$fiber_generator_chain_ids(S_projected_parent) = [n_parent]
""")
    return result


PARKED = checks(r"""
S.CURRENT = eps
S.FRAMES = eps
S.FIBERCALLERS = eps
pfiber.VM = (pfibervm)
~pfibervm.GLOBAL
pfibervm.TODO = (FIBER_CONTINUE pfiberapi) :: ptask_saved*
pfiberapi.OBJECT = n_fiber
pfiberapi.KIND = (INTRINSIC_FIBER_SUSPEND)
pfiberapi.SENT = (pvalue_pause)
$string_bytes(pvalue_pause) = ($ptascii("pause55"))
$value_nodes(pvalue_pause) = eps
S_live = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.COMPLETION = NORMAL]
$lookup(S.ENV, $ptascii("given")) = (n_given_cell)
S.STORE[n_given_cell] = DEFINED (POBJECT n_given)
$lookup(S.ENV, $ptascii("weak")) = (n_weak_cell)
S.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)
S.OBJECTS[n_weak] = WEAKREFERENCE (n_token)
""") + chain(True, HANDLED) + checks(r"""
$throwable_live(S, n_given)
$throwable_field(S, n_given, "previous") = PNULL
$heap_owners(H, HOBJECT n_given) = 1
$generator_saved_fiber_ids(S) = [n_child, n_middle, n_parent]
$generator_from_saved_fiber_claims(S) = [n_middle, n_parent]
$foreach_aggregate_close_vm_ids(S, pfibervm) = [n_child, n_middle, n_parent]
$yield_from_iterator_warning_vm_claims(S, pfibervm) = [n_middle, n_parent]
$generator_owners_valid(S)
$generator_from_state_valid(S)
$generator_saved_fiber_ids(S_live) = eps
$generator_from_saved_fiber_claims(S_live) = eps
H_live = $heap_graph(S_live)
S_line = S_live[.FRAMES = [pframe_child[.TODO = (GENERATOR_RESUME pgeneratorop_child[.LINE = $(pgeneratorop_child.LINE + 1)]) :: (GENERATOR_FROM_RESULT n_middle porigin_middle n_child) :: ptask_child*], pframe_middle, pframe_parent, pframe_fiber]]
$heap_graph(S_line) = H_live
$fiber_generator_delegation_ids(S_line) = eps
S_site = S_live[.FRAMES = [pframe_child[.ORIGIN = (pgeneratorop_parent.SITE)], pframe_middle, pframe_parent, pframe_fiber]]
$heap_graph(S_site) = H_live
$fiber_generator_delegation_ids(S_site) = eps
S_missing = S_live[.FRAMES = [pframe_child, pframe_middle[.TODO = (GENERATOR_RESUME pgeneratorop_middle) :: ptask_middle*], pframe_parent, pframe_fiber]]
$fiber_generator_delegation_ids(S_missing) = eps
S_extra = S_live[.TODO = (GENERATOR_FROM_RESULT n_parent porigin_parent n_middle) :: S_live.TODO]
$fiber_generator_delegation_ids(S_extra) = eps
S_hidden = S_live[.TODO = (AT pgeneratorop_parent.SITE (GENERATOR_RESUME pgeneratorop_parent)) :: S_live.TODO]
$generator_resume_ids(S_hidden.TODO) = eps
~$generator_flat_tasks(S_hidden.TODO)
$fiber_generator_delegation_ids(S_hidden) = eps
S_link = S_live[.OBJECTS = $object_set(S_live.OBJECTS, n_middle, GENERATOR pgenerator_middle[.DELEGATE = (pgeneratorfrom_middle[.INPUT = (POBJECT n_parent)])])]
$fiber_generator_delegation_ids(S_link) = eps
S_duplicate = S[.OBJECTS = $object_set(S.OBJECTS, n_given, FIBER pfiber)]
$generator_saved_fiber_ids(S_duplicate) = [n_child, n_middle, n_parent, n_child, n_middle, n_parent]
$generator_from_saved_fiber_claims(S_duplicate) = [n_middle, n_parent, n_middle, n_parent]
~$generator_owners_valid(S_duplicate)
~$generator_from_state_valid(S_duplicate)
""")

INJECTED = checks(r"""
S_live = S
S.OBJECTS[n_fiber] = FIBER pfiber
pfiber.STATUS = FIBER_RUNNING
pfiber.VM = eps
pfibercaller.OBJECT = n_fiber
pfibercaller.API.KIND = (INTRINSIC_FIBER_THROW)
pfibercaller.API.SENT = (POBJECT n_given)
S_global = $global_table_view(S)
$lookup(S_global.ENV, $ptascii("given")) = (n_given_cell)
S.STORE[n_given_cell] = DEFINED (POBJECT n_given)
$throwable_live(S, n_given)
$throwable_field(S, n_given, "previous") = PNULL
$string_bytes($throwable_field(S, n_given, "message")) = ($ptascii("supplied55"))
""") + chain(False, UNHANDLED) + checks(r"""
$heap_owners(H, HOBJECT n_given) = 3
$heap_count(HOBJECT n_given, $task_nodes(THROW_SEARCH n_given)) = 1
$heap_count(HOBJECT n_given, $fiber_api_nodes(pfibercaller.API)) = 1
$generator_saved_fiber_ids(S) = eps
$generator_from_saved_fiber_claims(S) = eps
$generator_owners_valid(S)
$generator_from_state_valid(S)
$fiber_api_valid(S, pfibercaller.API)
S_origin = S[.FRAMES = [pframe_child[.ORIGIN = eps], pframe_parent, pframe_fiber]]
$heap_graph(S_origin) = H
$fiber_generator_delegation_ids(S_origin) = eps
S_target = S[.CURRENT = (pcallcontext_child[.TARGET = pcallcontext_parent.FUNCTION])]
$heap_graph(S_target) = H
$fiber_generator_delegation_ids(S_target) = eps
S_duplicate = S[.FRAMES = [pframe_child, pframe_parent, pframe_parent, pframe_fiber]]
$generator_saved_ids(S_duplicate.FRAMES) = [n_child, n_parent, n_parent]
$fiber_generator_delegation_ids(S_duplicate) = eps
""")

# Completion binds its own source-reached IDs. Different recipe paths do not
# establish cross-recipe state identity; whole/split equality stays within one.
COMPLETION_BINDINGS = checks(r"""
pfiber.VM = (pfibervm)
pfibervm.FRAMES = [pframe_child, pframe_middle, pframe_parent, pframe_fiber]
pframe_child.TODO = (GENERATOR_RESUME pgeneratorop_child) :: (GENERATOR_FROM_RESULT n_middle porigin_middle n_child) :: ptask_child*
pframe_middle.TODO = (GENERATOR_RESUME pgeneratorop_middle) :: (GENERATOR_FROM_RESULT n_parent porigin_parent n_middle) :: ptask_middle*
$lookup(S.ENV, $ptascii("given")) = (n_given_cell)
S.STORE[n_given_cell] = DEFINED (POBJECT n_given)
$lookup(S.ENV, $ptascii("weak")) = (n_weak_cell)
S.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)
S.OBJECTS[n_weak] = WEAKREFERENCE (n_token)
""")

CASES = {
    'generator-fiber-delegation-two-edge-parked-structure': {
        'source': ROWS[HANDLED]['source'],
        'stage': ('S.ACTIVEFIBER = eps -- if $lookup(S.ENV, $ptascii("f")) = (n_fiber_cell) '
                  '-- if S.STORE[n_fiber_cell] = DEFINED (POBJECT n_fiber) '
                  '-- if S.OBJECTS[n_fiber] = FIBER pfiber '
                  '-- if pfiber.STATUS = FIBER_SUSPENDED'),
        'checks': [*PARKED, '$call_descriptors_valid(S)', '$heap_valid(H)', *SHORT_ENDING],
    },
    'generator-fiber-delegation-two-edge-parked-completion': {
        'source': ROWS[HANDLED]['source'],
        'stage': ('S.ACTIVEFIBER = eps -- if $lookup(S.ENV, $ptascii("f")) = (n_fiber_cell) '
                  '-- if S.STORE[n_fiber_cell] = DEFINED (POBJECT n_fiber) '
                  '-- if S.OBJECTS[n_fiber] = FIBER pfiber '
                  '-- if pfiber.STATUS = FIBER_SUSPENDED'),
        'checks': [*COMPLETION_BINDINGS, *ENDING,
                   '~((HOBJECT n_middle) <- S_done.ALLOCATIONS)', events(EVENTS[HANDLED])],
    },
    'generator-fiber-delegation-one-edge-injected-unhandled': {
        'source': ROWS[UNHANDLED]['source'],
        'stage': ('S.TODO = (THROW_SEARCH n_given) :: ptask_tail* '
                  '-- if S.ACTIVEFIBER = (n_fiber) '
                  '-- if S.FIBERCALLERS = [pfibercaller] '
                  '-- if S.CURRENT = (pcallcontext_child) '
                  '-- if pcallcontext_child.NAME = $ptascii("DelegationLeaf55")'),
        'checks': [*INJECTED, '$call_descriptors_valid(S)', '$heap_valid(H)', *SHORT_ENDING],
    },
    'generator-fiber-delegation-one-edge-injected-completion': {
        'source': ROWS[UNHANDLED]['source'],
        'stage': ('S.TODO = (THROW_SEARCH n_given) :: ptask_tail* '
                  '-- if S.ACTIVEFIBER = (n_fiber) '
                  '-- if S.FIBERCALLERS = [pfibercaller] '
                  '-- if S.CURRENT = (pcallcontext_child) '
                  '-- if pcallcontext_child.NAME = $ptascii("DelegationLeaf55")'),
        'checks': [
            'S.FRAMES = [pframe_child, pframe_parent, pframe_fiber]',
            'pframe_child.TODO = (GENERATOR_RESUME pgeneratorop_child) :: (GENERATOR_FROM_RESULT n_parent porigin_parent n_child) :: ptask_child*',
            '$lookup(S.ENV, $ptascii("token")) = (n_token_cell)',
            'S.STORE[n_token_cell] = DEFINED (POBJECT n_token)',
            *ENDING, events(EVENTS[UNHANDLED])],
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
    selected = parser.parse_args().case
    if selected is None:
        # Whole completions remain core-required, explicitly selectable.
        selected = ['generator-fiber-delegation-two-edge-parked-structure',
                    'generator-fiber-delegation-one-edge-injected-unhandled']
    raise SystemExit(0 if run(selected) else 1)
