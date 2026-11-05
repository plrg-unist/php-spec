#!/usr/bin/env python3
"""Check copied warning exit, ordered prepared-prefix cleanup and handler restore."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_call_exit_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROW = next(r for r in json.loads(INPUT_BYTES[CATALOG])
           if r['id'] == 'i102-real-reference-prefix-warning-exit')
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']


def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


STAGE = (
    'S.TODO = [EXIT_UNWIND 23] '
    '-- if S.FRAMES = [pframe_api] '
    '-- if pframe_api.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail* '
    '-- if perrorcall.RESUME = CLOSURE_CALL_COPY_REFERENCE pclosurecall n_copy n_done pnamedargs n_base '
    '-- if n_done = 1')

CHECKS = checks(r"""
S.COMPLETION = NORMAL
S.EXITSTATUS = 23
S.ACTIVEFIBER = eps
S.SOURCEPENDING = eps
S.CLOSURECALLRETAINED = eps
S.CURRENT = (pcallcontext_handler)
$target_function(S, pcallcontext_handler.TARGET) = (pfunction_handler)
pfunction_handler.NAME = $ptascii("Warn102A")
S_scope = $restore_frame(S)
S_scope.CURRENT = eps
S_scope.FRAMES = eps
S_scope.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
S_scope.ORIGIN = (pclosurecall.SITE)
S_scope.ERRORHANDLER.CALLBACK = eps
$string_bytes(perrorcall.CALLBACK) = ($ptascii("Warn102A"))
$call_task_valid(S_scope, ERROR_HANDLER_RESULT perrorcall)
$closure_call_copy_exit_head(S_scope)
$closure_call_copy_exit_pending(S)
$closure_call_copy_exit_pending(S_scope)
$closure_call_copy_exit_supported(ERROR_HANDLER_RESULT perrorcall)
$closure_call_copy_row(S_scope, n_copy) = (pclosurebinding)
n_source = pclosurebinding.SOURCE
pclosurebinding.OBJECT = n_copy
pclosurebinding.SITE = pclosurecall.SITE
pclosurebinding.RECEIVER = (n_maker)
pclosurecall.FIRST = (POBJECT n_maker)
pclosurecall.RAW = [(KINT 1, KNOWN (POBJECT n_prefix)), (KINT 2, KNOWN (POBJECT n_pending))]
pnamedargs.SLOTS = [NAMED_SENT (REFERENCE n_prefix_cell)]
pnamedargs.NAMED = eps
S_scope.STORE[n_prefix_cell] = DEFINED (POBJECT n_prefix)
n_prefix_cell <- S_scope.REFCELLS
$(n_prefix_cell >= n_base)
(HCELL n_prefix_cell) <- S_scope.ALLOCATIONS
S_scope.OBJECTS[n_copy] = REALCLOSURE porigin_function pitem* pstaticcell*
$target_function(S_scope, CLOSURE_TARGET n_copy) = (pfunction)
pfunction.ORIGIN = porigin_function
$function_generator(S_scope, pfunction)
$closure_call_reference_formal(pfunction.SIGNATURE.PARAMETERS)
~$closure_call_copy_created(S_scope.OBJECTS, n_copy)
$target_receiver(S_scope, CLOSURE_TARGET n_source) = (n_old)
n_old =/= n_maker
$object_name(S_scope, n_old) = $ptascii("OldExit102A")
$object_name(S_scope, n_maker) = $ptascii("MakerExit102A")
$object_name(S_scope, n_prefix) = $ptascii("PrefixExit102A")
$object_name(S_scope, n_pending) = $ptascii("PendingExit102A")
$lookup(S_scope.ENV, $ptascii("source")) = (n_source_cell)
S_scope.STORE[n_source_cell] = DEFINED PNULL
$lookup(S_scope.ENV, $ptascii("weakCapture")) = (n_weak_capture_cell)
S_scope.STORE[n_weak_capture_cell] = DEFINED (POBJECT n_weak_capture)
S_scope.OBJECTS[n_weak_capture] = WEAKREFERENCE (n_capture)
$object_name(S_scope, n_capture) = $ptascii("CaptureExit102A")
$heap_owners($heap_graph(S), HOBJECT n_copy) = 1
$heap_owners($heap_graph(S), HOBJECT n_source) = 1
$heap_owners($heap_graph(S), HOBJECT n_old) = 1
$heap_owners($heap_graph(S), HOBJECT n_maker) = 2
$heap_owners($heap_graph(S), HOBJECT n_capture) = 2
$heap_owners($heap_graph(S), HOBJECT n_prefix) = 2
$heap_owners($heap_graph(S), HOBJECT n_pending) = 1
$heap_owners($heap_graph(S), HCELL n_prefix_cell) = 1
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
PhpStep: S ~> S_raw
S_raw = $exit_start_unwind(S_scope, 23)
S_raw.COMPLETION = NORMAL
S_raw.CURRENT = eps
S_raw.FRAMES = eps
S_raw.ORIGIN = eps
S_raw.TRACE = eps
S_raw.ERRORORIGIN = eps
S_raw.CLOSURECALLRETAINED = [pclosurebinding]
S_raw.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: [EXIT_UNWIND 23]
pdestructionrelease.JOBS = $destruction_values([HCELL n_prefix_cell, HOBJECT n_maker, HOBJECT n_prefix, HOBJECT n_pending, HOBJECT n_source])
S_raw.ERRORHANDLER.CALLBACK = (perrorcall.CALLBACK)
S_raw.ERRORHANDLERS = S.ERRORHANDLERS
S_cancel = $literal_reference_debt_step(S, $sensitive_trace_freeze($source_exception_transition(S, $throwable_transition(S, S_raw))))
$closure_call_retained_nodes(S_cancel.CLOSURECALLRETAINED) = [HOBJECT n_copy]
$closure_call_retained_valid(S_cancel)
$heap_owners($heap_graph(S_cancel), HOBJECT n_copy) = 1
$heap_owners($heap_graph(S_cancel), HOBJECT n_source) = 1
$heap_owners($heap_graph(S_cancel), HOBJECT n_maker) = 2
$heap_owners($heap_graph(S_cancel), HOBJECT n_capture) = 2
$heap_owners($heap_graph(S_cancel), HOBJECT n_prefix) = 2
$heap_owners($heap_graph(S_cancel), HCELL n_prefix_cell) = 1
$call_descriptors_valid(S_cancel)
$heap_valid($heap_graph(S_cancel))
S_exit_base = S_raw[.TODO = [EXIT_UNWIND 23]][.CLOSURECALLRETAINED = eps][.DESTRUCTION.RELEASES = S_scope.DESTRUCTION.RELEASES]
$closure_call_copy_exit_task(S_scope, S_exit_base, ERROR_HANDLER_RESULT perrorcall) = S_raw
pclosurecall_bad_source = pclosurecall[.SOURCE = n_copy]
perrorcall_bad_source = perrorcall[.RESUME = CLOSURE_CALL_COPY_REFERENCE pclosurecall_bad_source n_copy n_done pnamedargs n_base]
~$call_task_valid(S_scope, ERROR_HANDLER_RESULT perrorcall_bad_source)
$closure_call_copy_exit_task(S_scope, S_exit_base, ERROR_HANDLER_RESULT perrorcall_bad_source) = S_exit_base
pnamedargs_bad = pnamedargs[.SLOTS = [NAMED_SENT (REFERENCE n_source_cell)]]
perrorcall_bad_prefix = perrorcall[.RESUME = CLOSURE_CALL_COPY_REFERENCE pclosurecall n_copy n_done pnamedargs_bad n_base]
~$call_task_valid(S_scope, ERROR_HANDLER_RESULT perrorcall_bad_prefix)
$closure_call_copy_exit_task(S_scope, S_exit_base, ERROR_HANDLER_RESULT perrorcall_bad_prefix) = S_exit_base
pgenerator_history = {FUNCTION porigin_function, FRAME eps, PHASE GENERATOR_CLOSED, FIRST false, PENDING_INIT false, PARKED eps, INDEX $(-1), VALUE eps, REFCELL eps, KEY eps, BORROWED eps, RETURN eps, CLOSURE (n_copy), DELEGATE eps, ACCESS eps, CREATION eps}
S_history = S_scope[.OBJECTS = S_scope.OBJECTS ++ [GENERATOR pgenerator_history]]
$call_task_valid(S_history, ERROR_HANDLER_RESULT perrorcall)
~$closure_call_copy_cancel_pending(S_history, CLOSURE_CALL_COPY_RESULT pclosurecall n_copy)
$closure_call_copy_exit_task(S_history, S_exit_base, ERROR_HANDLER_RESULT perrorcall) = S_exit_base
S_done = $drive(S, 4000)
S_pause = $drive(S, 0)
S_pause.COMPLETION = BUDGET
S_pause[.COMPLETION = NORMAL] = S
S_split = $drive(S, 1)
S_split.COMPLETION = BUDGET
S_split.CLOSURECALLRETAINED = [pclosurebinding]
S_split.TODO = S_cancel.TODO
$drive(S_split[.COMPLETION = NORMAL], 4000) = S_done
S_done.COMPLETION = EXITED 23
S_done.EXITSTATUS = 23
S_done.TODO = eps
S_done.CURRENT = eps
S_done.FRAMES = eps
S_done.HELD = eps
S_done.ACTIVEFIBER = eps
S_done.SHUTDOWN.PHASE = SHUTDOWN_DONE
S_done.CLOSURECALLRETAINED = [pclosurebinding]
S_done.ERRORHANDLER.CALLBACK = (perrorcall.CALLBACK)
$closure_call_retained_valid(S_done)
~$closure_call_copy_created(S_done.OBJECTS, n_copy)
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
~((HOBJECT n_source) <- S_done.ALLOCATIONS)
~((HOBJECT n_old) <- S_done.ALLOCATIONS)
~((HOBJECT n_prefix) <- S_done.ALLOCATIONS)
~((HOBJECT n_pending) <- S_done.ALLOCATIONS)
~((HCELL n_prefix_cell) <- S_done.ALLOCATIONS)
(HOBJECT n_copy) <- S_done.ALLOCATIONS
(HOBJECT n_maker) <- S_done.ALLOCATIONS
(HOBJECT n_capture) <- S_done.ALLOCATIONS
n_old <- S_done.DESTRUCTION.CALLED
n_maker <- S_done.DESTRUCTION.CALLED
n_capture <- S_done.DESTRUCTION.CALLED
$heap_owners($heap_graph(S_done), HOBJECT n_copy) = 1
$heap_owners($heap_graph(S_done), HOBJECT n_maker) = 1
$heap_owners($heap_graph(S_done), HOBJECT n_capture) = 1
""")

CASES = {'i102-warning-exit-prepared-prefix': {
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
