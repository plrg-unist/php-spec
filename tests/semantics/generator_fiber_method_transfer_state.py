#!/usr/bin/env python3
"""Check real method receiver transfer and sole yield-cache retirement (240s)."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import fiber_state_review as review
CATALOG = Path(__file__).with_name('generator_fiber_method_transfer_cases.json')
INPUT_BYTES = {p:p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {r['id']:r for r in json.loads(INPUT_BYTES[CATALOG])}
FRESH = 'generator-fiber-method-fresh-current'
CACHED = 'generator-fiber-method-cached-next-owning-cache'
def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]
def events(parts):
    return 'S_done.EVENTS = [' + ', '.join('OUTPUT ('+json.dumps(list(p.encode()))+')' for p in parts) + ']'
PARTS = {
 FRESH:['START|','CALL|','GEN|','1','PARK','1','1','1','ERROR','1','1','RESUME|','BODY','1','VALUE','1','FIBER','1','1','1','GEN-END|','OWNER|','CLOSED','1','0','DROP','1','E'],
 CACHED:['PRIME','SEED|','1','START|','CALL|','GEN|','1','PARK','1','1','1','ERROR','1','0','RESUME|','BODY','1','VALUE','1','FIBER','1','1','GEN-END|','CLOSED','1','1','CACHE','1','OWNER|','DROP','1','E'],
}
assert all(''.join(v)==ROWS[k]['native_stdout'] for k,v in PARTS.items())
PARK_STAGE = ('S.ACTIVEFIBER = eps -- if S.CURRENT = eps '
 '-- if $lookup(S.ENV, $ptascii("f")) = (n_fiber_cell) '
 '-- if S.STORE[n_fiber_cell] = DEFINED (POBJECT n_fiber) '
 '-- if S.OBJECTS[n_fiber] = FIBER pfiber '
 '-- if pfiber.STATUS = FIBER_SUSPENDED')
COMMON = checks(r"""
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
S.ACTIVEFIBER = eps
S.FIBERCALLERS = eps
S.FIBERCLOSERS = eps
S.GC.ACTIVE = eps
$lookup(S.ENV, $ptascii("g")) = (n_generator_cell)
S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator)
$lookup(S.ENV, $ptascii("weak")) = (n_weak_cell)
S.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)
S.OBJECTS[n_weak] = WEAKREFERENCE (n_receiver)
$lookup(S.ENV, $ptascii("owner")) = eps
S.OBJECTS[n_generator] = GENERATOR pgenerator
pgenerator.CLOSURE = eps
pgenerator.ACCESS = eps
pgenerator.DELEGATE = eps
pgenerator.FRAME = eps
pgenerator.REFCELL = eps
pgenerator.BORROWED = eps
S.OBJECTS[n_receiver] = INSTANCE porigin_class
$class_at(S.CLASSES, porigin_class) = (pclassdesc)
pclassdesc.NAME = $ptascii("MethodOwner58")
$node_children(S, HOBJECT n_receiver) = eps
~(n_receiver <- S.DESTRUCTION.CALLED)
H = $heap_graph(S)
$heap_owners(H, HOBJECT n_receiver) = 1
""")
PARKED = COMMON + checks(r"""
pgenerator.PHASE = GENERATOR_RUNNING
pgenerator.VALUE = eps
pgenerator.RETURN = eps
~pgenerator.PENDING_INIT
pfiber.VM = (pfibervm)
~pfibervm.GLOBAL
pfibervm.CURRENT = (pcallcontext_generator)
pfibervm.FRAMES = [pframe_generator, pframe_fiber]
pfibervm.TODO = (FIBER_CONTINUE pfiberapi) :: ptask_saved*
pfiberapi.KIND = (INTRINSIC_FIBER_SUSPEND)
pfiberapi.OBJECT = n_fiber
pfiberapi.SENT = (pvalue_pause)
$string_bytes(pvalue_pause) = ($ptascii("pause58"))
$value_nodes(pvalue_pause) = eps
pframe_generator.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_generator*
pframe_generator.ORIGIN = (pgeneratorop.SITE)
pframe_generator.CONTEXT = (pcallcontext_callback)
pcallcontext_callback.NAME = $ptascii("Run58")
pframe_fiber.TODO = [FIBER_FINISH n_fiber]
pgeneratorop.OBJECT = n_generator
pgeneratorop.NAME = "current"
pgeneratorop.ARGUMENTS = eps
pgeneratorop.LOOP = eps
~pgeneratorop.ADVANCE
~pgeneratorop.STARTPACK
~pgeneratorop.BORROWED
pcallcontext_generator.FUNCTION = pgenerator.FUNCTION
pcallcontext_generator.TARGET = METHOD_TARGET n_receiver pgenerator.FUNCTION
pcallcontext_generator.INSTANCE = eps
pcallcontext_generator.RECEIVER = (n_receiver)
pcallcontext_generator.LEXICAL_CLASS = (porigin_class)
pcallcontext_generator.CALLED_CLASS = (porigin_class)
$call_context_roots((pcallcontext_generator)) = [HOBJECT n_receiver]
$node_children(S, HOBJECT n_generator) = eps
$heap_owners(H, HOBJECT n_generator) = 2
$heap_count(HOBJECT n_receiver, $fiber_vm_nodes(pfibervm)) = 1
$generator_saved_fiber_ids(S) = [n_generator]
S_view = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.COMPLETION = NORMAL]
$call_current_valid(S_view)
$fiber_generator_callee_valid(S_view, pgenerator, pcallcontext_generator)
$fiber_generator_body_id(S_view) = (n_generator)
$fiber_generator_transfer(S_view)
$generator_resume_pairs(S_view, S_view.CURRENT, S_view.FRAMES)
$generator_saved_fiber_ids(S_view) = eps
~$fiber_generator_transfer(S_view[.ACTIVEFIBER = eps])
$generator_owners_valid(S)
$call_descriptors_valid(S)
$heap_valid(H)
""")
# Scoped metadata refusals, not claims of additional PHP source coverage.
REFUSALS = checks(r"""
pcallcontext_no_receiver = pcallcontext_generator[.RECEIVER = eps]
$call_context_roots((pcallcontext_no_receiver)) = [HOBJECT n_receiver]
S_no_receiver = S_view[.CURRENT = (pcallcontext_no_receiver)]
$heap_graph(S_no_receiver) = $heap_graph(S_view)
~$fiber_generator_callee_valid(S_no_receiver, pgenerator, pcallcontext_no_receiver)
$fiber_generator_body_id(S_no_receiver) = eps
pcallcontext_no_class = pcallcontext_generator[.CALLED_CLASS = eps]
S_no_class = S_view[.CURRENT = (pcallcontext_no_class)]
$heap_graph(S_no_class) = $heap_graph(S_view)
~$call_current_valid(S_no_class)
~$fiber_generator_callee_valid(S_no_class, pgenerator, pcallcontext_no_class)
$fiber_generator_body_id(S_no_class) = eps
""")
CACHE_LINE = next(i for i,line in enumerate(ROWS[CACHED]['source'].splitlines(),1) if line.startswith("echo 'CACHE'"))
CACHE_STAGE = ('S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
 '-- if pconfigcall.KIND = INTRINSIC_WEAKREF_GET '
 f'-- if pconfigcall.LINE = {CACHE_LINE}')
CLOSED_CACHE = COMMON + checks(r"""
pconfigcall.OWNER = (n_weak)
$lookup(S.ENV, $ptascii("f")) = eps
$lookup(S.ENV, $ptascii("result")) = eps
$lookup(S.ENV, $ptascii("error")) = eps
pgenerator.PHASE = GENERATOR_CLOSED
pgenerator.VALUE = (POBJECT n_receiver)
pgenerator.RETURN = (PINT 58)
$node_children(S, HOBJECT n_generator) = [HOBJECT n_receiver]
$heap_owners(H, HOBJECT n_generator) = 1
$heap_count(HOBJECT n_receiver, $machine_roots(S)) = 0
$generator_saved_fiber_ids(S) = eps
$call_descriptors_valid(S)
$heap_valid(H)
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
S_done.FRAMES = eps
S_done.CURRENT = eps
S_done.HELD = eps
S_done.ACTIVEFIBER = eps
S_done.FIBERCALLERS = eps
S_done.FIBERCLOSERS = eps
~((HOBJECT n_generator) <- S_done.ALLOCATIONS)
~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)
n_receiver <- S_done.DESTRUCTION.CALLED
$generator_saved_fiber_ids(S_done) = eps
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
""")
CASES = {
 'generator-fiber-method-fresh-receiver': {'source':ROWS[FRESH]['source'],'stage':PARK_STAGE,'checks':[*PARKED,*REFUSALS,*ENDING,events(PARTS[FRESH])]},
 'generator-fiber-method-closed-self-cache': {'source':ROWS[CACHED]['source'],'stage':CACHE_STAGE,'checks':[*CLOSED_CACHE,*ENDING,events(PARTS[CACHED])]},
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
