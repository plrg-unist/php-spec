#!/usr/bin/env python3
"""Check genuine copied-call arity entry, receiver aliases and late cleanup."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_call_receive_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROW = next(r for r in json.loads(INPUT_BYTES[CATALOG])
           if r['id'] == 'i101-fake-arity-this-raw-alias-independent')
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']


def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


STAGE = (
    'S.TODO = (CLOSURE_CALL_COPY_FORWARD pclosurecall n_copy n_done pnamedargs n_base) :: ptask_tail* '
    '-- if n_done = 1 -- if n_done = |pclosurecall.RAW|')

CHECKS = checks(r'''
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
S.ACTIVEFIBER = eps
S.SOURCEPENDING = eps
S.CLOSURECALLRETAINED = eps
$closure_call_copy_row(S, n_copy) = (pclosurebinding)
n_source = pclosurebinding.SOURCE
pclosurebinding.OBJECT = n_copy
pclosurebinding.SITE = pclosurecall.SITE
pclosurebinding.RECEIVER = (n_maker)
pclosurecall.FIRST = (POBJECT n_maker)
pclosurecall.RECEIVER = (n_maker)
pclosurecall.RAW = [(KINT 1, KNOWN (POBJECT n_maker))]
pclosurecall.ERROR = eps
pnamedargs.SLOTS = [NAMED_SENT (KNOWN (POBJECT n_maker))]
pnamedargs.NAMED = eps
S.OBJECTS[n_copy] = BOUNDFAKECLOSURE pboundfake
pboundfake.SOURCE = n_source
$target_function(S, CLOSURE_TARGET n_copy) = (pfunction)
$function_generator(S, pfunction)
|pfunction.SIGNATURE.PARAMETERS| = 2
~$closure_call_reference_formal(pfunction.SIGNATURE.PARAMETERS)
~$closure_call_copy_created(S.OBJECTS, n_copy)
$target_receiver(S, CLOSURE_TARGET n_source) = (n_old)
n_old =/= n_maker
$object_name(S, n_maker) = $ptascii("MakerArity101A")
$object_name(S, n_old) = $ptascii("MakerArity101A")
$lookup(S.ENV, $ptascii("source")) = (n_source_cell)
S.STORE[n_source_cell] = DEFINED PNULL
$node_children(S, HOBJECT n_copy) = [HOBJECT n_maker]
$heap_count(HOBJECT n_maker, $closure_call_first_roots(pclosurecall.FIRST)) = 1
$heap_count(HOBJECT n_maker, $closure_call_raw_roots(pclosurecall.RAW)) = 1
$heap_owners($heap_graph(S), HOBJECT n_copy) = 1
$heap_owners($heap_graph(S), HOBJECT n_source) = 1
$heap_owners($heap_graph(S), HOBJECT n_old) = 1
$heap_owners($heap_graph(S), HOBJECT n_maker) = 4
$call_task_valid(S, CLOSURE_CALL_COPY_FORWARD pclosurecall n_copy n_done pnamedargs n_base)
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
pclosurecall_bad_source = pclosurecall[.SOURCE = n_copy]
~$closure_call_copy_forward_valid(S, pclosurecall_bad_source, n_copy, n_done, pnamedargs, n_base)
pnamedargs_bad = {SLOTS [NAMED_SENT (KNOWN (POBJECT n_old))], NAMED eps}
~$closure_call_copy_forward_valid(S, pclosurecall, n_copy, n_done, pnamedargs_bad, n_base)
PhpStep: S ~> S_raw
S_raw.COMPLETION = THROWN "ArgumentCountError" ptbytes_error z_error
S_raw.FRAMES = pframe_api :: S.FRAMES
pclosurecall_enter = pclosurecall[.SENT = pnamedargs]
pframe_api.TODO = (CLOSURE_CALL_COPY_RESULT pclosurecall_enter n_copy) :: ptask_tail*
pframe_api.CONTEXT = S.CURRENT
pframe_api.ORIGIN = S.ORIGIN
S_raw.CURRENT = (pcallcontext)
pcallcontext.TARGET = CLOSURE_TARGET n_copy
pcallcontext.INSTANCE = (n_copy)
pcallcontext.RECEIVER = (n_maker)
pcallcontext.CALLSITE = (pclosurecall.SITE)
pcallcontext.ARGC = 1
pcallcontext.WRAPPER = eps
$lookup(S_raw.ENV, $ptascii("first")) = (n_first_cell)
S_raw.STORE[n_first_cell] = DEFINED (POBJECT n_maker)
S_raw.CLOSURECALLRETAINED = eps
~$closure_call_copy_created(S_raw.OBJECTS, n_copy)
$throwable_continuation(S, S_raw) = S_raw
pframe_bad_result = pframe_api[.TODO = (CLOSURE_CALL_COPY_RESULT pclosurecall_enter n_source) :: ptask_tail*]
S_bad_result = $throwable_continuation(S, S_raw[.FRAMES = pframe_bad_result :: S.FRAMES])
S_bad_result.COMPLETION = UNSUPPORTED "unaudited Throwable frame transition"
pframe_bad_caller = pframe_api[.CONTEXT = (pcallcontext)]
S_bad_caller = $throwable_continuation(S, S_raw[.FRAMES = pframe_bad_caller :: S.FRAMES])
S_bad_caller.COMPLETION = UNSUPPORTED "unaudited Throwable frame transition"
S_error = $literal_reference_debt_step(S, $sensitive_trace_freeze($source_exception_transition(S, $throwable_transition(S, S_raw))))
S_error.COMPLETION = THROWING n_error
S_error.CLOSURECALLRETAINED = eps
S_error.FRAMES = S_raw.FRAMES
S_error.CURRENT = S_raw.CURRENT
S_error.OBJECTS[n_error] = THROWABLE pthrowable
pthrowable.KIND = "ArgumentCountError"
$throwable_field(S_error, n_error, "trace") = PARRAY n_trace
H_trace = $heap_prune($heap_graph(S_error)[.ROOTS = [HARRAY n_trace]])
$heap_owners(H_trace, HOBJECT n_maker) = 3
~((HOBJECT n_copy) <- H_trace.NODES)
~((HOBJECT n_source) <- H_trace.NODES)
~((HOBJECT n_old) <- H_trace.NODES)
S_begin = $throwable_begin(S_error)
S_begin.COMPLETION = NORMAL
S_begin.TODO = [THROW_SEARCH n_error]
$call_descriptors_valid(S_begin)
$heap_valid($heap_graph(S_begin))
S_done = $drive(S, 4000)
S_pause = $drive(S, 0)
S_pause.COMPLETION = BUDGET
S_pause.TODO = S.TODO
S_pause.CLOSURECALLRETAINED = eps
S_pause[.COMPLETION = NORMAL] = S
S_split = $drive(S, 1)
S_split.COMPLETION = BUDGET
S_split.TODO = [THROW_SEARCH n_error]
S_split.CLOSURECALLRETAINED = eps
$drive(S_split[.COMPLETION = NORMAL], 4000) = S_done
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
~((HOBJECT n_error) <- S_done.ALLOCATIONS)
~((HCELL n_first_cell) <- S_done.ALLOCATIONS)
(HOBJECT n_copy) <- S_done.ALLOCATIONS
(HOBJECT n_maker) <- S_done.ALLOCATIONS
n_old <- S_done.DESTRUCTION.CALLED
n_maker <- S_done.DESTRUCTION.CALLED
$heap_owners($heap_graph(S_done), HOBJECT n_copy) = 1
$heap_owners($heap_graph(S_done), HOBJECT n_maker) = 1
pclosurebinding_bad = pclosurebinding[.SOURCE = n_copy]
~$closure_call_retained_valid(S_done[.CLOSURECALLRETAINED = [pclosurebinding_bad]])
~$closure_call_retained_valid(S_done[.CLOSURECALLRETAINED = [pclosurebinding, pclosurebinding]])
pgenerator_history = {FUNCTION pfunction.ORIGIN, FRAME eps, PHASE GENERATOR_CLOSED, FIRST false, PENDING_INIT false, PARKED eps, INDEX $(-1), VALUE eps, REFCELL eps, KEY eps, BORROWED eps, RETURN eps, CLOSURE (n_copy), DELEGATE eps, ACCESS eps, CREATION eps}
~$closure_call_retained_valid(S_done[.OBJECTS = S_done.OBJECTS ++ [GENERATOR pgenerator_history]])
''')

CASES = {'i101-arity-entry-this-raw-alias': {
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
