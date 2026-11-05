#!/usr/bin/env python3
"""Independent repeated-copy cancellation ownership and shutdown checks."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path.cwd() / 'tests/semantics'))
import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_call_cancellation_review_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROW = next(r for r in json.loads(INPUT_BYTES[CATALOG])
           if r['id'] == 'i99-repeated-real-retval-fiber-cancellation-independent')
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']

OUTPUT_HELPER = ('dec $i99_review_output(pevent*) : ptbytes\n'
                 'def $i99_review_output(eps) = eps\n'
                 'def $i99_review_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $i99_review_output(pevent*)\n')

CHECKS = [line.strip() for line in r'''
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
S.ACTIVEFIBER = eps
S.FIBERCALLERS = eps
S.FIBERCLOSERS = eps
S.GENERATORINPUTS = eps
S.DESTRUCTION.RELEASES = eps
S.DESTRUCTION.CALLS = eps
S.DESTRUCTION.OPERATIONS = eps
S.DESTRUCTION.CLEANUPS = eps
S.CLOSURECALLRETAINED = [pclosurebinding_first, pclosurebinding_second]
n_copy_first = pclosurebinding_first.OBJECT
n_copy_second = pclosurebinding_second.OBJECT
$(n_copy_first < n_copy_second)
n_source = pclosurebinding_first.SOURCE
pclosurebinding_second.SOURCE = n_source
pclosurebinding_first.SITE = pclosurebinding_second.SITE
$(n_source < n_copy_first)
S.OBJECTS[n_source] = REALCLOSURE porigin_function pitem_source* pstaticcell_source*
S.OBJECTS[n_copy_first] = REALCLOSURE porigin_function pitem_first* eps
S.OBJECTS[n_copy_second] = REALCLOSURE porigin_function pitem_second* eps
~((HOBJECT n_source) <- S.ALLOCATIONS)
(HOBJECT n_copy_first) <- S.ALLOCATIONS
(HOBJECT n_copy_second) <- S.ALLOCATIONS
$closure_call_copy_row(S, n_copy_first) = (pclosurebinding_first)
$closure_call_copy_row(S, n_copy_second) = (pclosurebinding_second)
$closure_binding_at(S.CLOSUREBINDINGS, n_copy_first) = (pclosurebinding_first)
$closure_binding_at(S.CLOSUREBINDINGS, n_copy_second) = (pclosurebinding_second)
$closure_call_retained_valid(S)
$closure_call_retained_nodes(S.CLOSURECALLRETAINED) = [HOBJECT n_copy_first, HOBJECT n_copy_second]
~$closure_call_copy_created(S.OBJECTS, n_copy_first)
~$closure_call_copy_created(S.OBJECTS, n_copy_second)
pclosurebinding_first.RECEIVER = (n_maker_first)
pclosurebinding_second.RECEIVER = (n_maker_second)
n_maker_first =/= n_maker_second
$class_named(S.CLASSNAMES, $ptlc($ptascii("MakerRepeat99R"))) = (porigin_maker)
pclosurebinding_first.LEXICAL = (porigin_maker)
pclosurebinding_first.CALLED = (porigin_maker)
pclosurebinding_second.LEXICAL = (porigin_maker)
pclosurebinding_second.CALLED = (porigin_maker)
S.OBJECTS[n_maker_first] = INSTANCE porigin_maker
S.OBJECTS[n_maker_second] = INSTANCE porigin_maker
$closure_items_nodes(pitem_first*) = [HOBJECT n_capture]
$closure_items_nodes(pitem_second*) = [HOBJECT n_capture]
$object_name(S, n_capture) = $ptascii("CaptureRepeat99R")
$node_children(S, HOBJECT n_copy_first) = [HOBJECT n_capture, HOBJECT n_maker_first]
$node_children(S, HOBJECT n_copy_second) = [HOBJECT n_capture, HOBJECT n_maker_second]
$lookup(S.ENV, $ptascii("weakMaker1")) = (n_weak_maker_first_cell)
S.STORE[n_weak_maker_first_cell] = DEFINED (POBJECT n_weak_maker_first)
$weakref_get(S, n_weak_maker_first) = POBJECT n_maker_first
$lookup(S.ENV, $ptascii("weakMaker2")) = (n_weak_maker_second_cell)
S.STORE[n_weak_maker_second_cell] = DEFINED (POBJECT n_weak_maker_second)
$weakref_get(S, n_weak_maker_second) = POBJECT n_maker_second
$lookup(S.ENV, $ptascii("weakCapture")) = (n_weak_capture_cell)
S.STORE[n_weak_capture_cell] = DEFINED (POBJECT n_weak_capture)
$weakref_get(S, n_weak_capture) = POBJECT n_capture
$lookup(S.ENV, $ptascii("weakOld")) = (n_weak_old_cell)
S.STORE[n_weak_old_cell] = DEFINED (POBJECT n_weak_old)
$weakref_get(S, n_weak_old) = PNULL
$lookup(S.ENV, $ptascii("weakSource")) = (n_weak_source_cell)
S.STORE[n_weak_source_cell] = DEFINED (POBJECT n_weak_source)
$weakref_get(S, n_weak_source) = PNULL
$lookup(S.ENV, $ptascii("weakToken1")) = (n_weak_token_first_cell)
S.STORE[n_weak_token_first_cell] = DEFINED (POBJECT n_weak_token_first)
$weakref_get(S, n_weak_token_first) = PNULL
$lookup(S.ENV, $ptascii("weakToken2")) = (n_weak_token_second_cell)
S.STORE[n_weak_token_second_cell] = DEFINED (POBJECT n_weak_token_second)
$weakref_get(S, n_weak_token_second) = PNULL
$lookup(S.ENV, $ptascii("weakReturned")) = (n_weak_retval_cell)
S.STORE[n_weak_retval_cell] = DEFINED (POBJECT n_weak_retval)
$weakref_get(S, n_weak_retval) = PNULL
$lookup(S.ENV, $ptascii("g")) = (n_g_cell)
S.STORE[n_g_cell] = DEFINED PNULL
$lookup(S.ENV, $ptascii("source")) = (n_source_cell)
S.STORE[n_source_cell] = DEFINED PNULL
S.ERRORHANDLER.CALLBACK = (pvalue_handler)
$string_bytes(pvalue_handler) = ($ptascii("WarnRepeat99R"))
H = $heap_graph(S)
$heap_owners(H, HOBJECT n_source) = 0
$heap_owners(H, HOBJECT n_copy_first) = 1
$heap_owners(H, HOBJECT n_copy_second) = 1
$heap_owners(H, HOBJECT n_maker_first) = 1
$heap_owners(H, HOBJECT n_maker_second) = 1
$heap_owners(H, HOBJECT n_capture) = 2
~(n_maker_first <- S.DESTRUCTION.CALLED)
~(n_maker_second <- S.DESTRUCTION.CALLED)
~(n_capture <- S.DESTRUCTION.CALLED)
$call_descriptors_valid(S)
$heap_valid(H)
S_duplicate = S[.CLOSURECALLRETAINED = [pclosurebinding_first, pclosurebinding_second, pclosurebinding_first]]
~$closure_call_retained_valid(S_duplicate)
S_wrong_source = S[.CLOSURECALLRETAINED = [pclosurebinding_first[.SOURCE = n_copy_first], pclosurebinding_second]]
~$closure_call_retained_valid(S_wrong_source)
S_wrong_receiver = S[.CLOSURECALLRETAINED = [pclosurebinding_first[.RECEIVER = (n_maker_second)], pclosurebinding_second]]
~$closure_call_retained_valid(S_wrong_receiver)
S_missing_copy = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HOBJECT n_copy_first)]
~$closure_call_retained_valid(S_missing_copy)
S_reverse = S[.CLOSURECALLRETAINED = [pclosurebinding_second, pclosurebinding_first]]
$closure_call_retained_valid(S_reverse)
$heap_owners($heap_graph(S_reverse), HOBJECT n_capture) = 2
S_zero = $drive_steps(S, 0)
S_zero.COMPLETION = BUDGET
S_zero.TODO = S.TODO
S_one = $drive_steps(S, 1)
S_one.COMPLETION = BUDGET
S_done = $drive_steps(S, 4000)
S_done = $drive_steps(S_one[.COMPLETION = NORMAL], 4000)
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.CURRENT = eps
S_done.FRAMES = eps
S_done.CLOSURECALLRETAINED = S.CLOSURECALLRETAINED
$closure_call_retained_valid(S_done)
n_capture <- S_done.DESTRUCTION.CALLED
n_maker_first <- S_done.DESTRUCTION.CALLED
n_maker_second <- S_done.DESTRUCTION.CALLED
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
'''.splitlines() if line.strip()]

CHECKS += ['S_done.EXITSTATUS = 0', 'S_done.SHUTDOWN.PHASE = SHUTDOWN_DONE',
           '$i99_review_output(S_done.EVENTS) = $ptascii(' + json.dumps(ROW['native_stdout']) + ')']

CASES = {'i99-repeated-retained-copy-ownership-independent': {
    'source': ROW['source'],
    'stage': 'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* -- if pconfigcall.KIND = INTRINSIC_RESTORE_ERROR_HANDLER -- if S.CURRENT = eps -- if S.FRAMES = eps',
    'checks': CHECKS,
}}

if __name__ == '__main__':
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=review.ROOT, text=True).strip()
    review.CASES = CASES
    original = review.recorded
    raw = None
    def recorded(command, directory, stem, environment, cap):
        global raw
        raw = directory.parent
        if stem == 'model':
            fixture = Path(command[-1])
            fixture.write_text(OUTPUT_HELPER + fixture.read_text())
        return original(command, directory, stem, environment, cap)
    review.recorded = recorded
    try:
        passed = review.run(list(CASES), process_seconds=1800)
    finally:
        review.recorded = original
    stable = INPUT_BYTES == {p: p.read_bytes() for p in INPUT_BYTES}
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=review.ROOT, text=True).strip()
    report_path = raw / 'report.json'
    report = json.loads(report_path.read_bytes())
    report.update(peer_inputs={str(p): hashlib.sha256(data).hexdigest() for p, data in INPUT_BYTES.items()},
                  peer_inputs_stable=stable, head_stable=head_stable,
                  passed=passed and stable and head_stable)
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if report['passed'] else 1)
