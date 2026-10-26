#!/usr/bin/env python3
"""Reach Closure capture cells in Fibers with a fixed 240s fixture budget."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import fiber_state_review as review
CATALOG = Path(__file__).with_name('generator_fiber_closure_transfer_cases.json')
INPUT_BYTES = {p:p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {r['id']:r for r in json.loads(INPUT_BYTES[CATALOG])}
VALUE = 'generator-fiber-closure-byvalue'
REFERENCE = 'generator-fiber-closure-byreference'
def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]
def events(parts):
    return 'S_done.EVENTS = [' + ', '.join('OUTPUT ('+json.dumps(list(p.encode()))+')' for p in parts) + ']'
PARTS = {
 VALUE:['START|','CALL|','GEN|','PARK|','1','1','1','RETARGET|','OLD|','1','RESUME|','CAPTURE|','1','1','VALUE|','1','FIBER|','1','1','B|','GEN-END|','CLOSED|','1','1','1','0','A|','DROP|','1','1','1','E'],
 REFERENCE:['START|','CALL|','GEN|','PARK|','1','1','1','RETARGET|','A|','OLD|','0','RESUME|','CAPTURE|','0','1','VALUE|','1','FIBER|','1','1','GEN-END|','CLOSED|','1','1','0','1','B|','DROP|','1','1','1','E'],
}
assert all(''.join(v)==ROWS[k]['native_stdout'] for k,v in PARTS.items())
STAGE = ('S.ACTIVEFIBER = eps -- if S.CURRENT = eps '
 '-- if $lookup(S.ENV, $ptascii("f")) = (n_fiber_cell) '
 '-- if S.STORE[n_fiber_cell] = DEFINED (POBJECT n_fiber) '
 '-- if S.OBJECTS[n_fiber] = FIBER pfiber '
 '-- if pfiber.STATUS = FIBER_SUSPENDED '
 '-- if $lookup(S.ENV, $ptascii("weakB")) = eps')
COMMON = checks(r"""
S.COMPLETION = NORMAL
S.FRAMES = eps
S.FIBERCALLERS = eps
S.FIBERCLOSERS = eps
S.GC.ACTIVE = eps
$lookup(S.ENV, $ptascii("g")) = (n_generator_cell)
S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator)
$lookup(S.ENV, $ptascii("token")) = (n_global)
S.STORE[n_global] = DEFINED (POBJECT n_token)
$lookup(S.ENV, $ptascii("factory")) = eps
$lookup(S.ENV, $ptascii("weakClosure")) = (n_weak_callee_cell)
S.STORE[n_weak_callee_cell] = DEFINED (POBJECT n_weak_callee)
S.OBJECTS[n_weak_callee] = WEAKREFERENCE (n_callee)
$lookup(S.ENV, $ptascii("weakA")) = (n_weak_token_cell)
S.STORE[n_weak_token_cell] = DEFINED (POBJECT n_weak_token)
S.OBJECTS[n_weak_token] = WEAKREFERENCE (n_token)
$object_name(S, n_token) = $ptascii("CaptureA57")
pfiber.VM = (pfibervm)
~pfibervm.GLOBAL
pfibervm.CURRENT = (pcallcontext_generator)
pfibervm.FRAMES = [pframe_generator, pframe_fiber]
pfibervm.TODO = (FIBER_CONTINUE pfiberapi) :: ptask_saved*
pfiberapi.KIND = (INTRINSIC_FIBER_SUSPEND)
pfiberapi.OBJECT = n_fiber
pfiberapi.SENT = (pvalue_pause)
$string_bytes(pvalue_pause) = ($ptascii("pause57"))
pframe_generator.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_generator*
pframe_generator.CONTEXT = (pcallcontext_callback)
pcallcontext_callback.NAME = $ptascii("Run57")
pframe_fiber.TODO = [FIBER_FINISH n_fiber]
pgeneratorop.OBJECT = n_generator
pgeneratorop.NAME = "current"
pgeneratorop.ARGUMENTS = eps
pgeneratorop.LOOP = eps
~pgeneratorop.ADVANCE
~pgeneratorop.BORROWED
~pgeneratorop.STARTPACK
S.OBJECTS[n_generator] = GENERATOR pgenerator
pgenerator.PHASE = GENERATOR_RUNNING
pgenerator.FRAME = eps
pgenerator.VALUE = eps
pgenerator.RETURN = eps
pgenerator.DELEGATE = eps
pgenerator.CLOSURE = (n_callee)
~pgenerator.PENDING_INIT
S.OBJECTS[n_callee] = REALCLOSURE pgenerator.FUNCTION pitem* eps
pcallcontext_generator.FUNCTION = pgenerator.FUNCTION
pcallcontext_generator.TARGET = CLOSURE_TARGET n_callee
pcallcontext_generator.INSTANCE = (n_callee)
$lookup(pfibervm.TABLE.ENV, $ptascii("token")) = (n_local)
S.STORE[n_local] = DEFINED (POBJECT n_token)
$node_children(S, HOBJECT n_generator) = eps
H = $heap_graph(S)
$heap_owners(H, HOBJECT n_generator) = 2
$heap_owners(H, HOBJECT n_callee) = 1
$heap_count(HOBJECT n_callee, $fiber_vm_nodes(pfibervm)) = 1
$generator_saved_fiber_ids(S) = [n_generator]
$generator_owners_valid(S)
S_view = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.COMPLETION = NORMAL]
$generator_active(S_view)
$generator_closure_valid(S_view, pgenerator)
$call_current_valid(S_view)
$generator_resume_pairs(S_view, S_view.CURRENT, S_view.FRAMES)
$fiber_generator_callee_valid(S_view, pgenerator, pcallcontext_generator)
$fiber_generator_body_id(S_view) = (n_generator)
$fiber_transfer_domain(S_view)
$generator_saved_fiber_ids(S_view) = eps
~$fiber_generator_transfer(S_view[.ACTIVEFIBER = eps])
$call_descriptors_valid(S)
$heap_valid(H)
""")
COPIED = checks(r"""
pitem* = [DIRECT (POBJECT n_token)]
n_local =/= n_global
$node_children(S, HOBJECT n_callee) = [HOBJECT n_token]
$node_children(S, HCELL n_local) = [HOBJECT n_token]
$node_children(S, HCELL n_global) = [HOBJECT n_token]
$heap_owners(H, HOBJECT n_token) = 3
$heap_owners(H, HCELL n_local) = 1
$heap_owners(H, HCELL n_global) = 1
""")
SHARED = checks(r"""
pitem* = [ALIAS n_global]
n_local = n_global
n_global <- S.REFCELLS
$node_children(S, HOBJECT n_callee) = [HCELL n_global]
$node_children(S, HCELL n_global) = [HOBJECT n_token]
$heap_owners(H, HCELL n_global) = 3
$heap_owners(H, HOBJECT n_token) = 1
""")
# These are constructed metadata refusals, not extra PHP source behaviors.
REFUSALS = checks(r"""
S_instance = S_view[.CURRENT = (pcallcontext_generator[.INSTANCE = eps])]
$fiber_generator_body_id(S_instance) = eps
S_callee = S_view[.OBJECTS = $object_set(S_view.OBJECTS, n_generator, GENERATOR pgenerator[.CLOSURE = eps])]
$heap_graph(S_callee) = $heap_graph(S_view)
$fiber_generator_body_id(S_callee) = eps
""")
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
$drive_steps(S, 2) = $drive_steps(S_one, 1)
S_done = $drive_steps(S_one, 4000)
$drive_steps(S, 4000) = S_done
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.CURRENT = eps
S_done.FRAMES = eps
S_done.ACTIVEFIBER = eps
S_done.FIBERCALLERS = eps
S_done.FIBERCLOSERS = eps
S_done.HELD = eps
~((HOBJECT n_generator) <- S_done.ALLOCATIONS)
~((HOBJECT n_callee) <- S_done.ALLOCATIONS)
~((HOBJECT n_fiber) <- S_done.ALLOCATIONS)
~((HOBJECT n_token) <- S_done.ALLOCATIONS)
n_token <- S_done.DESTRUCTION.CALLED
$generator_saved_fiber_ids(S_done) = eps
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
""")
CASES = {
 'generator-fiber-closure-copied-capture': {'source':ROWS[VALUE]['source'],'stage':STAGE,'checks':[*COMMON,*COPIED,*REFUSALS,*ENDING,events(PARTS[VALUE])]},
 'generator-fiber-closure-shared-capture': {'source':ROWS[REFERENCE]['source'],'stage':STAGE,'checks':[*COMMON,*SHARED,*REFUSALS,*ENDING,events(PARTS[REFERENCE])]},
}

def run(selected):
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
        passed = review.run(selected, process_seconds=240)
    finally:
        review.recorded = original
    stable = INPUT_BYTES == {p: p.read_bytes() for p in INPUT_BYTES}
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=review.ROOT, text=True).strip()
    path = raw / 'report.json'
    report = json.loads(path.read_bytes())
    report.update(author_inputs={str(p): hashlib.sha256(b).hexdigest() for p, b in INPUT_BYTES.items()},
                  author_inputs_stable=stable, head_stable=head_stable,
                  passed=passed and stable and head_stable)
    path.write_text(json.dumps(report, indent=2) + '\n')
    return passed and stable and head_stable


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    raise SystemExit(0 if run(parser.parse_args().case) else 1)
