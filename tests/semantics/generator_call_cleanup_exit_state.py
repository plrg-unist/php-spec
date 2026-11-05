#!/usr/bin/env python3
"""Check copied warning retval exit, owner-preserving history and C cleanup."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_call_cleanup_exit_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROW = next(r for r in json.loads(INPUT_BYTES[CATALOG])
           if r['id'] == 'i103-fake-reference-prefix-retval-destructor-exit')
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']


def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


STAGE = (
    'S.TODO = [EXIT_UNWIND 29] -- if S.FRAMES = [pframe_cleanup] '
    '-- if pframe_cleanup.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: ptask_cleanup_tail* '
    '-- if pdestructorcall.OPERATION = (pdestructionoperation) '
    '-- if pdestructionoperation.SOURCE = ERROR_HANDLER_RESULT perrorcall '
    '-- if perrorcall.RESUME = CLOSURE_CALL_COPY_REFERENCE pclosurecall n_copy n_done pnamedargs n_base '
    '-- if n_done = 1')

CHECKS = checks(r'''
S.COMPLETION = NORMAL
S.EXITSTATUS = 29
S.ACTIVEFIBER = eps
S.SOURCEPENDING = eps
S.CLOSURECALLRETAINED = eps
S.CURRENT = (pcallcontext_retval)
pcallcontext_retval.TARGET = METHOD_TARGET n_retval porigin_dtor
$object_name(S, n_retval) = $ptascii("ReturnExit103A")
pdestructorcall.OBJECT = n_retval
pdestructorcall.USER
pdestructorcall.PENDING = eps
pdestructionoperation.PENDING = eps
pdestructionoperation.COMPLETION = NORMAL
pdestructionoperation.CLEANUP = (pdestructioncleanup)
pdestructioncleanup.SOURCE = ERROR_HANDLER_RESULT perrorcall
~pdestructioncleanup.RELEASED
$closure_call_copy_row(S, n_copy) = (pclosurebinding)
n_source = pclosurebinding.SOURCE
pclosurebinding.RECEIVER = (n_maker)
pclosurecall.FIRST = (POBJECT n_maker)
pclosurecall.RAW = [(KINT 1, KNOWN (POBJECT n_prefix)), (KINT 2, KNOWN (POBJECT n_pending))]
pnamedargs.SLOTS = [NAMED_SENT (REFERENCE n_prefix_cell)]
pnamedargs.NAMED = eps
S.STORE[n_prefix_cell] = DEFINED (POBJECT n_prefix)
n_prefix_cell <- S.REFCELLS
$(n_prefix_cell >= n_base)
S.OBJECTS[n_copy] = BOUNDFAKECLOSURE pboundfake
pboundfake.SOURCE = n_source
$target_function(S, CLOSURE_TARGET n_copy) = (pfunction)
$function_generator(S, pfunction)
~$closure_call_copy_created(S.OBJECTS, n_copy)
$target_receiver(S, CLOSURE_TARGET n_source) = (n_old)
$object_name(S, n_maker) = $ptascii("MakerExit103A")
$object_name(S, n_old) = $ptascii("MakerExit103A")
$object_name(S, n_prefix) = $ptascii("PrefixExit103A")
$object_name(S, n_pending) = $ptascii("PendingExit103A")
$heap_owners($heap_graph(S), HOBJECT n_copy) = 1
$heap_owners($heap_graph(S), HOBJECT n_source) = 1
$heap_owners($heap_graph(S), HOBJECT n_old) = 1
$heap_owners($heap_graph(S), HOBJECT n_maker) = 2
$heap_owners($heap_graph(S), HOBJECT n_prefix) = 2
$heap_owners($heap_graph(S), HOBJECT n_pending) = 1
$heap_owners($heap_graph(S), HOBJECT n_retval) = 2
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
S_scope = $restore_frame(S)
S_scope.CURRENT = eps
S_scope.FRAMES = eps
S_scope.ORIGIN = (pclosurecall.SITE)
S_scope.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: ptask_cleanup_tail*
S_scope.ERRORHANDLER.CALLBACK = eps
$lookup(S_scope.ENV, $ptascii("source")) = (n_source_cell)
S_scope.STORE[n_source_cell] = DEFINED PNULL
S_scope.CLOSURECALLRETAINED = eps
$heap_owners($heap_graph(S_scope), HOBJECT n_retval) = 1
$closure_call_copy_cleanup_exit(S_scope) = ((pdestructorcall, pdestructionoperation))
S_history = $eager_cleanup_history(S_scope, pdestructioncleanup)
S_rotated = $closure_call_copy_warning_history(S_history, perrorcall)
S_rotated.TODO = (ERROR_HANDLER_CLEAN perrorcall) :: ptask_rotated_tail*
S_rotated[.TODO = S_history.TODO] = S_history
$eager_removed($tasks_nodes(S_rotated.TODO), $tasks_nodes(S_history.TODO)) = eps
$eager_removed($tasks_nodes(S_history.TODO), $tasks_nodes(S_rotated.TODO)) = eps
$closure_call_copy_reference_valid(S_rotated, pclosurecall, n_copy, n_done, pnamedargs, n_base)
~$closure_call_copy_reference_valid(S_history, pclosurecall, n_copy, n_done, pnamedargs, n_base)
$call_task_valid(S_scope, ERROR_HANDLER_CLEAN perrorcall)
$eager_cleanup_valid(S_scope, pdestructioncleanup)
S_original = S_rotated[.TODO = (CLOSURE_CALL_COPY_RESULT pclosurecall n_copy) :: ptask_rotated_tail*]
H_original = $heap_prune($heap_graph(S_original))
~((HCELL n_prefix_cell) <- H_original.NODES)
S_scope.DESTRUCTION.RELEASES = pdestructionrelease_template :: pdestructionrelease_tail*
pdestructionrelease_other = pdestructionrelease_template[.JOBS = $destruction_values([HCELL n_prefix_cell])]
S_other = S_history[.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_other) :: S_history.TODO][.DESTRUCTION.RELEASES = pdestructionrelease_other :: S_history.DESTRUCTION.RELEASES]
S_other_rotated = $closure_call_copy_warning_history(S_other, perrorcall)
S_other_rotated.TODO = (ERROR_HANDLER_CLEAN perrorcall) :: ptask_other_tail*
$eager_removed($tasks_nodes(S_other_rotated.TODO), $tasks_nodes(S_other.TODO)) = eps
$eager_removed($tasks_nodes(S_other.TODO), $tasks_nodes(S_other_rotated.TODO)) = eps
$closure_call_copy_raw_valid(S_other_rotated, pclosurecall, n_copy)
~$closure_call_copy_reference_valid(S_other_rotated, pclosurecall, n_copy, n_done, pnamedargs, n_base)
H_other_original = $heap_prune($heap_graph(S_other_rotated[.TODO = (CLOSURE_CALL_COPY_RESULT pclosurecall n_copy) :: ptask_other_tail*]))
(HCELL n_prefix_cell) <- H_other_original.NODES
S_bad_registry = S_history[.DESTRUCTION.RELEASES = eps]
$closure_call_copy_warning_history(S_bad_registry, perrorcall) = S_bad_registry
pclosurecall_bad_source = pclosurecall[.SOURCE = n_copy]
perrorcall_bad_source = perrorcall[.RESUME = CLOSURE_CALL_COPY_REFERENCE pclosurecall_bad_source n_copy n_done pnamedargs n_base]
$closure_call_copy_warning_history(S_history, perrorcall_bad_source) = S_history
~$error_call_valid(S_history, perrorcall_bad_source)
pnamedargs_bad = pnamedargs[.SLOTS = [NAMED_SENT (REFERENCE n_source_cell)]]
~$closure_call_copy_reference_valid(S_rotated, pclosurecall, n_copy, n_done, pnamedargs_bad, n_base)
PhpStep: S ~> S_raw
pdestructionoperation_new = pdestructionoperation[.COMPLETION = EXITED 29]
pdestructorcall_new = pdestructorcall[.OPERATION = (pdestructionoperation_new)]
S_raw.COMPLETION = NORMAL
S_raw.CURRENT = eps
S_raw.FRAMES = eps
S_raw.ORIGIN = S_scope.ORIGIN
S_raw.CLOSURECALLRETAINED = eps
S_raw.TODO = (DESTRUCTOR_RESULT pdestructorcall_new) :: $destructor_operation_tasks(ptask_cleanup_tail*, pdestructionoperation, pdestructionoperation_new)
S_scope.DESTRUCTION.CALLS = pdestructorcall :: pdestructorcall_tail*
S_scope.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*
S_raw.DESTRUCTION.CALLS = pdestructorcall_new :: pdestructorcall_tail*
S_raw.DESTRUCTION.OPERATIONS = pdestructionoperation_new :: pdestructionoperation_tail*
S_raw.DESTRUCTION.CLEANUPS = S_scope.DESTRUCTION.CLEANUPS
S_raw.ERRORHANDLER.CALLBACK = eps
$closure_call_copy_cleanup_exit_rebase(S_scope, 29) = S_raw
S_changed = $literal_reference_debt_step(S, $sensitive_trace_freeze($source_exception_transition(S, $throwable_transition(S, S_raw))))
$call_descriptors_valid(S_changed)
$heap_valid($heap_graph(S_changed))
pgenerator_history = {FUNCTION pfunction.ORIGIN, FRAME eps, PHASE GENERATOR_CLOSED, FIRST false, PENDING_INIT false, PARKED eps, INDEX $(-1), VALUE eps, REFCELL eps, KEY eps, BORROWED eps, RETURN eps, CLOSURE (n_copy), DELEGATE eps, ACCESS eps, CREATION eps}
$closure_call_copy_cleanup_exit(S_scope[.OBJECTS = S_scope.OBJECTS ++ [GENERATOR pgenerator_history]]) = eps
$closure_call_copy_cleanup_exit(S_scope[.CLOSURECALLRETAINED = [pclosurebinding]]) = eps
pdestructionoperation_repeat = pdestructionoperation[.COMPLETION = EXITED 7]
pdestructorcall_repeat = pdestructorcall[.OPERATION = (pdestructionoperation_repeat)]
S_repeat = S_scope[.TODO = (DESTRUCTOR_RESULT pdestructorcall_repeat) :: $destructor_operation_tasks(ptask_cleanup_tail*, pdestructionoperation, pdestructionoperation_repeat)][.DESTRUCTION.CALLS = pdestructorcall_repeat :: pdestructorcall_tail*][.DESTRUCTION.OPERATIONS = pdestructionoperation_repeat :: pdestructionoperation_tail*]
$closure_call_copy_cleanup_exit(S_repeat) = ((pdestructorcall_repeat, pdestructionoperation_repeat))
S_repeat_result = $closure_call_copy_cleanup_exit_rebase(S_repeat, 29)
S_repeat_result.COMPLETION = UNSUPPORTED "Generator Closure::call repeated cleanup exit"
S_done = $drive(S, 4000)
S_pause = $drive(S, 0)
S_pause.COMPLETION = BUDGET
S_pause[.COMPLETION = NORMAL] = S
S_split = $drive(S, 1)
S_split.COMPLETION = BUDGET
S_split.CURRENT = eps
S_split.FRAMES = eps
S_split.CLOSURECALLRETAINED = eps
pdestructionoperation_new <- S_split.DESTRUCTION.OPERATIONS
$drive(S_split[.COMPLETION = NORMAL], 4000) = S_done
S_done.COMPLETION = EXITED 29
S_done.EXITSTATUS = 29
S_done.TODO = eps
S_done.CURRENT = eps
S_done.FRAMES = eps
S_done.HELD = eps
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
~((HOBJECT n_retval) <- S_done.ALLOCATIONS)
~((HCELL n_prefix_cell) <- S_done.ALLOCATIONS)
(HOBJECT n_copy) <- S_done.ALLOCATIONS
(HOBJECT n_maker) <- S_done.ALLOCATIONS
n_maker <- S_done.DESTRUCTION.CALLED
$heap_owners($heap_graph(S_done), HOBJECT n_copy) = 1
$heap_owners($heap_graph(S_done), HOBJECT n_maker) = 1
''')

CASES = {'i103-owned-warning-exit-parent-frame': {'source': ROW['source'], 'stage': STAGE, 'checks': CHECKS}}

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
