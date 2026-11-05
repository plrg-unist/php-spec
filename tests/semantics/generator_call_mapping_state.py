#!/usr/bin/env python3
"""Check genuine named overwrite, prepared-prefix and Error-trace owners."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_call_mapping_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROW = next(r for r in json.loads(INPUT_BYTES[CATALOG])
           if r['id'] == 'i100-real-duplicate-named-after-reference-prefix')
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']


def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


STAGE = (
    'S.TODO = (CLOSURE_CALL_COPY_FORWARD pclosurecall n_copy n_done pnamedargs n_base) :: ptask_tail* '
    '-- if n_done = 1 -- if pclosurecall.ERROR = (preqbytes)')

CHECKS = checks(r'''
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
S.ACTIVEFIBER = eps
S.SOURCEPENDING = eps
S.CLOSURECALLRETAINED = eps
$closure_call_retained_valid(S)
$closure_call_copy_row(S, n_copy) = (pclosurebinding)
n_source = pclosurebinding.SOURCE
pclosurebinding.OBJECT = n_copy
pclosurebinding.SITE = pclosurecall.SITE
pclosurebinding.RECEIVER = (n_maker)
pclosurecall.FIRST = (POBJECT n_maker)
pclosurecall.RAW = [(KINT 1, KNOWN (POBJECT n_prefix)), (KSTRING $ptascii("slot"), KNOWN (POBJECT n_pending))]
preqbytes = $ptascii("Named parameter $slot overwrites previous argument")
pnamedargs.SLOTS = [NAMED_SENT (REFERENCE n_prefix_cell)]
pnamedargs.NAMED = eps
S.STORE[n_prefix_cell] = DEFINED (POBJECT n_prefix)
n_prefix_cell <- S.REFCELLS
$(n_prefix_cell >= n_base)
(HCELL n_prefix_cell) <- S.ALLOCATIONS
S.OBJECTS[n_copy] = REALCLOSURE porigin_function pitem* pstaticcell*
pstaticcell* = eps
$target_function(S, CLOSURE_TARGET n_copy) = (pfunction)
pfunction.ORIGIN = porigin_function
$function_generator(S, pfunction)
~pfunction.SIGNATURE.BYREF
$closure_call_reference_formal(pfunction.SIGNATURE.PARAMETERS)
~$closure_call_copy_created(S.OBJECTS, n_copy)
$object_name(S, n_maker) = $ptascii("MakerCancel100A")
$object_name(S, n_prefix) = $ptascii("PrefixCancel100A")
$object_name(S, n_pending) = $ptascii("PendingCancel100A")
$lookup(S.ENV, $ptascii("source")) = (n_source_cell)
S.STORE[n_source_cell] = DEFINED PNULL
$lookup(S.ENV, $ptascii("weakCapture")) = (n_weak_capture_cell)
S.STORE[n_weak_capture_cell] = DEFINED (POBJECT n_weak_capture)
S.OBJECTS[n_weak_capture] = WEAKREFERENCE (n_capture)
$object_name(S, n_capture) = $ptascii("CaptureCancel100A")
$heap_owners($heap_graph(S), HOBJECT n_copy) = 1
$heap_owners($heap_graph(S), HOBJECT n_source) = 1
$heap_owners($heap_graph(S), HOBJECT n_maker) = 2
$heap_owners($heap_graph(S), HOBJECT n_capture) = 2
$heap_owners($heap_graph(S), HOBJECT n_prefix) = 2
$heap_owners($heap_graph(S), HOBJECT n_pending) = 1
$heap_owners($heap_graph(S), HCELL n_prefix_cell) = 1
$closure_call_copy_forward_valid(S, pclosurecall, n_copy, n_done, pnamedargs, n_base)
~$closure_call_copy_result_valid(S, pclosurecall, n_copy)
$call_current_valid(S)
$call_frames_valid(S, S.FRAMES)
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
pclosurecall_bad_source = pclosurecall[.SOURCE = n_copy]
~$closure_call_copy_forward_valid(S, pclosurecall_bad_source, n_copy, n_done, pnamedargs, n_base)
pclosurecall_bad_error = pclosurecall[.ERROR = ($ptascii("wrong"))]
~$closure_call_copy_forward_valid(S, pclosurecall_bad_error, n_copy, n_done, pnamedargs, n_base)
pclosurecall_bad_site = pclosurecall[.SITE = PORIGIN 999 eps]
~$closure_call_copy_forward_valid(S, pclosurecall_bad_site, n_copy, n_done, pnamedargs, n_base)
~$closure_call_copy_forward_valid(S, pclosurecall, n_copy, 2, pnamedargs, n_base)
pnamedargs_bad = pnamedargs[.SLOTS = [NAMED_SENT (REFERENCE n_source_cell)]]
~$closure_call_copy_forward_valid(S, pclosurecall, n_copy, n_done, pnamedargs_bad, n_base)
~$closure_call_copy_forward_valid(S, pclosurecall, n_copy, n_done, {SLOTS eps, NAMED eps}, n_base)
PhpStep: S ~> S_error
S_error.COMPLETION = THROWING n_error
S_error.TODO = S.TODO
S_thrown = $literal_reference_debt_step(S, $sensitive_trace_freeze($source_exception_transition(S, $throwable_transition(S, S_error))))
S_thrown.COMPLETION = THROWING n_error
S_thrown.TODO = S.TODO
S_thrown.CLOSURECALLRETAINED = eps
S_pending = $throwable_begin(S_thrown)
S_pending.COMPLETION = NORMAL
S_pending.TODO = (THROW_SEARCH n_error) :: S.TODO
$source_exception_transition(S_pending, S_pending) = S_pending
$call_descriptors_valid(S_pending)
$heap_valid($heap_graph(S_pending))
$heap_owners($heap_graph(S_pending), HOBJECT n_source) = 1
$heap_owners($heap_graph(S_pending), HOBJECT n_copy) = 1
$heap_owners($heap_graph(S_pending), HOBJECT n_maker) = 3
$heap_owners($heap_graph(S_pending), HOBJECT n_prefix) = 3
$heap_owners($heap_graph(S_pending), HOBJECT n_pending) = 2
S_pop = S_pending[.TODO = (THROW_SEARCH n_error) :: ptask_tail*]
S_cancel = $return_discard(S_pop, CLOSURE_CALL_COPY_FORWARD pclosurecall n_copy n_done pnamedargs n_base)
S_cancel.CLOSURECALLRETAINED = [pclosurebinding]
S_cancel.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (THROW_SEARCH n_error) :: ptask_tail*
pdestructionrelease.JOBS = $destruction_values([HCELL n_prefix_cell, HOBJECT n_maker, HOBJECT n_prefix, HOBJECT n_pending, HOBJECT n_source])
S_cancel.COMPLETION = NORMAL
$closure_call_retained_nodes(S_cancel.CLOSURECALLRETAINED) = [HOBJECT n_copy]
$closure_call_retained_valid(S_cancel)
$heap_owners($heap_graph(S_cancel), HOBJECT n_copy) = 1
$heap_owners($heap_graph(S_cancel), HOBJECT n_source) = 1
$heap_owners($heap_graph(S_cancel), HOBJECT n_maker) = 3
$heap_owners($heap_graph(S_cancel), HOBJECT n_capture) = 2
$heap_owners($heap_graph(S_cancel), HOBJECT n_prefix) = 3
$heap_owners($heap_graph(S_cancel), HOBJECT n_pending) = 2
$heap_owners($heap_graph(S_cancel), HCELL n_prefix_cell) = 1
$heap_valid($heap_graph(S_cancel))
pclosurebinding_bad_source = pclosurebinding[.SOURCE = n_copy]
~$closure_call_retained_valid(S_cancel[.CLOSURECALLRETAINED = [pclosurebinding_bad_source]])
~$closure_call_retained_valid(S_cancel[.CLOSURECALLRETAINED = [pclosurebinding, pclosurebinding]])
~$closure_call_retained_valid(S_cancel[.ALLOCATIONS = $destruction_node_delete(S_cancel.ALLOCATIONS, HOBJECT n_copy)])
pgenerator_history = {FUNCTION porigin_function, FRAME eps, PHASE GENERATOR_CLOSED, FIRST false, PENDING_INIT false, PARKED eps, INDEX $(-1), VALUE eps, REFCELL eps, KEY eps, BORROWED eps, RETURN eps, CLOSURE (n_copy), DELEGATE eps, ACCESS eps, CREATION eps}
S_history = S_cancel[.OBJECTS = S_cancel.OBJECTS ++ [GENERATOR pgenerator_history]]
~$closure_call_retained_valid(S_history)
S_done = $drive(S, 4000)
S_pause = $drive(S, 0)
S_pause.COMPLETION = BUDGET
S_pause.TODO = S.TODO
S_pause.CLOSURECALLRETAINED = S.CLOSURECALLRETAINED
$drive(S_pause[.COMPLETION = NORMAL], 4000) = S_done
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.CURRENT = eps
S_done.FRAMES = eps
S_done.HELD = eps
S_done.ACTIVEFIBER = eps
S_done.CLOSURECALLRETAINED = [pclosurebinding]
S_done.ERRORHANDLER.CALLBACK = eps
S_done.EXITSTATUS = 0
S_done.SHUTDOWN.PHASE = SHUTDOWN_DONE
$closure_call_retained_valid(S_done)
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
~((HOBJECT n_source) <- S_done.ALLOCATIONS)
~((HOBJECT n_prefix) <- S_done.ALLOCATIONS)
~((HOBJECT n_pending) <- S_done.ALLOCATIONS)
~((HCELL n_prefix_cell) <- S_done.ALLOCATIONS)
~((HOBJECT n_error) <- S_done.ALLOCATIONS)
(HOBJECT n_copy) <- S_done.ALLOCATIONS
(HOBJECT n_maker) <- S_done.ALLOCATIONS
(HOBJECT n_capture) <- S_done.ALLOCATIONS
n_maker <- S_done.DESTRUCTION.CALLED
n_capture <- S_done.DESTRUCTION.CALLED
$heap_owners($heap_graph(S_done), HOBJECT n_copy) = 1
$heap_owners($heap_graph(S_done), HOBJECT n_maker) = 1
$heap_owners($heap_graph(S_done), HOBJECT n_capture) = 1
''')

CASES = {'i100-named-overwrite-prepared-prefix-cancel': {
    'source': ROW['source'], 'stage': STAGE, 'checks': CHECKS}}

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
        passed = review.run(selected, process_seconds=600)
    finally:
        review.recorded = original
    stable = INPUT_BYTES == {p: p.read_bytes() for p in INPUT_BYTES}
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=review.ROOT, text=True).strip()
    path = raw / 'report.json'
    report = json.loads(path.read_bytes())
    report.update(author_inputs={str(p): hashlib.sha256(data).hexdigest() for p, data in INPUT_BYTES.items()},
                  author_inputs_stable=stable, head_stable=head_stable,
                  passed=passed and stable and head_stable)
    path.write_text(json.dumps(report, indent=2) + '\n')
    return report['passed']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    raise SystemExit(0 if run(parser.parse_args().case) else 1)
