#!/usr/bin/env python3
"""Independent required-hole throw, trace ownership and copy retention checks."""
import hashlib
import json
from pathlib import Path
import subprocess
import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_call_mapping_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROW = next(r for r in json.loads(INPUT_BYTES[CATALOG])
           if r['id'] == 'i100-real-named-hole-required-independent')
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']

STAGE = ('S.TODO = [NAMED_PREFLIGHT porigin_function 0] '
         '-- if S.CURRENT = (pcallcontext) '
         '-- if $context_target(pcallcontext) = CLOSURE_TARGET n_copy '
         '-- if S.FRAMES = pframe :: pframe_tail* '
         '-- if pframe.TODO = (CLOSURE_CALL_COPY_RESULT pclosurecall n_copy) :: ptask_tail*')

CHECKS = [line.strip() for line in r'''
S.COMPLETION = NORMAL
S.ACTIVEFIBER = eps
S.SOURCEPENDING = eps
S.CLOSURECALLRETAINED = eps
$named_preflight_valid(S, porigin_function, 0)
$receiving_function(S, porigin_function) = (pfunction)
$function_generator(S, pfunction)
~$closure_call_reference_formal(pfunction.SIGNATURE.PARAMETERS)
pcallcontext.ARGC = 2
pcallcontext.CALLSITE = (pclosurecall.SITE)
~$named_defined(S, $ptascii("first"))
$named_defined(S, $ptascii("second"))
$default_at(pfunction.DEFAULTS, 0) = eps
$closure_call_copy_result_valid(S, pclosurecall, n_copy)
$closure_call_copy_row(S, n_copy) = (pclosurebinding)
~$closure_call_copy_created(S.OBJECTS, n_copy)
n_source = pclosurebinding.SOURCE
pclosurebinding.RECEIVER = (n_maker)
pclosurecall.FIRST = (POBJECT n_maker)
pclosurecall.ERROR = eps
pclosurecall.RAW = [(KSTRING $ptascii("second"), KNOWN (POBJECT n_pending))]
pclosurecall.SENT.SLOTS = [NAMED_HOLE, NAMED_SENT (KNOWN (POBJECT n_pending))]
pclosurecall.SENT.NAMED = eps
$lookup(S.ENV, $ptascii("second")) = (n_second_cell)
S.STORE[n_second_cell] = DEFINED (POBJECT n_pending)
S.OBJECTS[n_copy] = REALCLOSURE porigin_function pitem* eps
$closure_items_nodes(pitem*) = [HOBJECT n_capture]
$target_receiver(S, CLOSURE_TARGET n_source) = (n_old)
$object_name(S, n_old) = $ptascii("OldCancel100H")
$object_name(S, n_maker) = $ptascii("MakerCancel100H")
$object_name(S, n_pending) = $ptascii("PendingCancel100H")
$object_name(S, n_capture) = $ptascii("CaptureCancel100H")
$node_children(S, HOBJECT n_copy) = [HOBJECT n_capture, HOBJECT n_maker]
~$closure_call_copy_cancel_pending(S, CLOSURE_CALL_COPY_RESULT pclosurecall n_copy)
$call_current_valid(S)
$call_frames_valid(S, S.FRAMES)
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
PhpStep: S ~> S_raw
S_raw.COMPLETION = THROWN "ArgumentCountError" ptbytes_error z_error
S_raw.CLOSURECALLRETAINED = eps
S_materialized = $throwable_transition(S, S_raw)
S_materialized.COMPLETION = THROWING n_error
S_materialized.CLOSURECALLRETAINED = eps
S_materialized.TODO = eps
S_materialized.OBJECTS[n_error] = THROWABLE pthrowable
pthrowable.KIND = "ArgumentCountError"
S_retained = $source_exception_transition(S, S_materialized)
S_retained.CLOSURECALLRETAINED = [pclosurebinding]
S_retained.TODO = S_materialized.TODO
S_retained.OBJECTS = S_materialized.OBJECTS
S_retained.STORE = S_materialized.STORE
S_retained.ENV = S_materialized.ENV
S_retained.FRAMES = S_materialized.FRAMES
S_retained.CURRENT = S_materialized.CURRENT
$closure_call_retained_valid(S_retained)
$closure_call_retained_nodes(S_retained.CLOSURECALLRETAINED) = [HOBJECT n_copy]
$closure_call_copy_cancel_pending(S_retained, CLOSURE_CALL_COPY_RESULT pclosurecall n_copy)
$throwable_field(S_retained, n_error, "trace") = PARRAY n_trace
pnode_trace* = $heap_reach([HARRAY n_trace], eps, $heap_graph(S_retained).EDGES)
(HOBJECT n_pending) <- pnode_trace*
(HOBJECT n_maker) <- pnode_trace*
~((HOBJECT n_copy) <- pnode_trace*)
~((HOBJECT n_source) <- pnode_trace*)
~((HOBJECT n_old) <- pnode_trace*)
~((HOBJECT n_capture) <- pnode_trace*)
S_begin = $throwable_begin($literal_reference_debt_step(S, $sensitive_trace_freeze(S_retained)))
S_begin.COMPLETION = NORMAL
S_begin.TODO = [THROW_SEARCH n_error]
$call_descriptors_valid(S_begin)
$heap_valid($heap_graph(S_begin))
S_supplied = $write_name(S, $ptascii("first"), PNULL)
S_supplied.COMPLETION = NORMAL
$named_preflight_valid(S_supplied, porigin_function, 0)
$named_defined(S_supplied, $ptascii("first"))
$source_exception_transition(S_supplied, S_materialized) = S_materialized
S_wrong_site = S[.CURRENT = (pcallcontext[.CALLSITE = (PORIGIN 999 eps)])]
$source_exception_transition(S_wrong_site, S_materialized) = S_materialized
S_done = $drive(S, 4000)
S_pause = $drive(S, 0)
S_pause.COMPLETION = BUDGET
S_pause.TODO = S.TODO
S_pause.CLOSURECALLRETAINED = eps
$drive(S_pause[.COMPLETION = NORMAL], 4000) = S_done
S_done.COMPLETION = NORMAL
S_done.EXITSTATUS = 0
S_done.TODO = eps
S_done.CURRENT = eps
S_done.FRAMES = eps
S_done.HELD = eps
S_done.SHUTDOWN.PHASE = SHUTDOWN_DONE
S_done.CLOSURECALLRETAINED = [pclosurebinding]
$closure_call_retained_valid(S_done)
~$closure_call_copy_created(S_done.OBJECTS, n_copy)
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
~((HOBJECT n_source) <- S_done.ALLOCATIONS)
~((HOBJECT n_old) <- S_done.ALLOCATIONS)
~((HOBJECT n_pending) <- S_done.ALLOCATIONS)
~((HOBJECT n_error) <- S_done.ALLOCATIONS)
~((HCELL n_second_cell) <- S_done.ALLOCATIONS)
(HOBJECT n_copy) <- S_done.ALLOCATIONS
(HOBJECT n_maker) <- S_done.ALLOCATIONS
(HOBJECT n_capture) <- S_done.ALLOCATIONS
n_maker <- S_done.DESTRUCTION.CALLED
n_capture <- S_done.DESTRUCTION.CALLED
$heap_owners($heap_graph(S_done), HOBJECT n_copy) = 1
$heap_owners($heap_graph(S_done), HOBJECT n_maker) = 1
$heap_owners($heap_graph(S_done), HOBJECT n_capture) = 1
'''.splitlines() if line.strip()]

CASES = {'i100-required-hole-throw-independent': {
    'source': ROW['source'], 'stage': STAGE, 'checks': CHECKS}}

if __name__ == '__main__':
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=review.ROOT, text=True).strip()
    review.CASES = CASES
    original = review.recorded
    raw = None

    def recorded(command, directory, stem, environment, cap):
        global raw
        raw = directory.parent
        return original(command, directory, stem, environment, cap)

    review.recorded = recorded
    try:
        passed = review.run(list(CASES), process_seconds=600)
    finally:
        review.recorded = original
    stable = INPUT_BYTES == {p: p.read_bytes() for p in INPUT_BYTES}
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=review.ROOT, text=True).strip()
    path = raw / 'report.json'
    report = json.loads(path.read_bytes())
    report.update(peer_inputs={str(p): hashlib.sha256(data).hexdigest() for p, data in INPUT_BYTES.items()},
                  peer_inputs_stable=stable, head_stable=head_stable,
                  passed=passed and stable and head_stable)
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if report['passed'] else 1)
