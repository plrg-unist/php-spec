#!/usr/bin/env python3
"""Check the real capture, borrowed newThis and two distinct argv owners."""
import hashlib
import json
from pathlib import Path
import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_api_call_review_cases.json')
ROW = json.loads(CATALOG.read_bytes())[0]
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']
STAGE = (
    'S.TODO = (CLOSURE_CALL_INVOKE pclosurecall) :: ptask_tail* '
    '-- if pclosurecall.NATIVE = ("send") '
    '-- if $lookup(S.ENV, $ptascii("capture")) = (n_capture_cv) '
    '-- if S.STORE[n_capture_cv] = DEFINED PNULL')
CHECKS = [line.strip() for line in r'''
S.COMPLETION = NORMAL
S.CURRENT = (pcallcontext)
$function_at($all_functions(S), pcallcontext.FUNCTION) = (pfunction)
pfunction.NAME = $ptascii("run115P")
pcallcontext.CACHE = eps
pcallcontext.ARGC = 0
pcallcontext.INSTANCE = eps
S.ACTIVEFIBER = eps
S.SOURCEPENDING = eps
S_global = $global_table_view(S)
$lookup(S_global.ENV, $ptascii("old")) = (n_old_cv)
S.STORE[n_old_cv] = DEFINED PNULL
$lookup(S_global.ENV, $ptascii("replacement")) = (n_new_cv)
S.STORE[n_new_cv] = DEFINED PNULL
pclosurecall.SOURCE = n_capture
pclosurecall.FIRST = (POBJECT n_new)
pclosurecall.RECEIVER = (n_new)
pclosurecall.INDEX = 2
pclosurecall.PACKS = eps
pclosurecall.ERROR = eps
pclosurecall.RAW = [(KINT 1, KNOWN (POBJECT n_token))]
pclosurecall.SENT = {SLOTS ([NAMED_SENT (KNOWN (POBJECT n_token))]), NAMED eps}
porigin_call = pclosurecall.SITE
S.OBJECTS[n_capture] = GETTERCLOSURE n_old (GENERATOR_API_METHOD "send") "Generator" (GENERATOR_CAPTURE pgeneratormethodselection_origin)
~pgeneratormethodselection_origin.TEMPORARY
S.OBJECTS[n_old] = GENERATOR pgenerator_old
pgenerator_old.PHASE = GENERATOR_PAUSED
S.OBJECTS[n_new] = GENERATOR pgenerator_new
pgenerator_new.PHASE = GENERATOR_FRESH
$object_name(S, n_token) = $ptascii("Token115P")
$lookup(S_global.ENV, $ptascii("weakOld")) = (n_weak_old_cv)
S.STORE[n_weak_old_cv] = DEFINED (POBJECT n_weak_old)
$weakref_get(S, n_weak_old) = POBJECT n_old
$lookup(S_global.ENV, $ptascii("weakNew")) = (n_weak_new_cv)
S.STORE[n_weak_new_cv] = DEFINED (POBJECT n_weak_new)
$weakref_get(S, n_weak_new) = POBJECT n_new
$lookup(S_global.ENV, $ptascii("weakCapture")) = (n_weak_capture_cv)
S.STORE[n_weak_capture_cv] = DEFINED (POBJECT n_weak_capture)
$weakref_get(S, n_weak_capture) = POBJECT n_capture
$lookup(S_global.ENV, $ptascii("weakToken")) = (n_weak_token_cv)
S.STORE[n_weak_token_cv] = DEFINED (POBJECT n_weak_token)
$weakref_get(S, n_weak_token) = POBJECT n_token
$getter_capture_live(S, n_capture)
$node_children(S, HOBJECT n_capture) = [HOBJECT n_old]
$task_nodes(CLOSURE_CALL_INVOKE pclosurecall) = [HOBJECT n_capture, HOBJECT n_new, HOBJECT n_token]
$heap_owners($heap_graph(S), HOBJECT n_capture) = 1
$heap_owners($heap_graph(S), HOBJECT n_old) = 1
$heap_owners($heap_graph(S), HOBJECT n_new) = 1
$heap_owners($heap_graph(S), HOBJECT n_token) = 1
$call_task_valid(S, CLOSURE_CALL_INVOKE pclosurecall)
~$call_task_valid(S, CLOSURE_CALL_INVOKE pclosurecall[.NATIVE = eps])
~$call_task_valid(S, CLOSURE_CALL_INVOKE pclosurecall[.NATIVE = ("throw")])
$generator_call_saved_valid(S, pclosurecall)
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
S_pause = $drive(S, 0)
S_pause.COMPLETION = BUDGET
S_pause[.COMPLETION = NORMAL] = S
PhpStep: S ~> S_inner
S_inner.TODO = (GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_token)])) :: (GENERATOR_CALL_RESULT pclosurecall true PNULL) :: ptask_tail*
pgeneratorop.OBJECT = n_new
pgeneratorop.NAME = "send"
pgeneratorop.SITE = porigin_call
pgeneratorop.LINE = pclosurecall.LINE
pgeneratorop.ARGUMENTS = eps
~pgeneratorop.ADVANCE
~pgeneratorop.BORROWED
~pgeneratorop.STARTPACK
pgeneratorop.LOOP = eps
pgeneratorop.SELECTION = (pgeneratormethodselection)
pgeneratormethodselection.TEMPORARY
pgeneratormethodselection.CAPTURE = (n_capture)
pgeneratormethodselection.OBJECT = n_new
pgeneratormethodselection.NAME = $ptascii("send")
$generator_call_selection(pclosurecall) = pgeneratormethodselection
$generator_operation_nodes(pgeneratorop) = eps
$task_nodes(GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_token)])) = [HOBJECT n_token]
$task_nodes(GENERATOR_CALL_RESULT pclosurecall true PNULL) = [HOBJECT n_capture, HOBJECT n_new, HOBJECT n_token]
S_inner.OBJECTS = S.OBJECTS
S_inner.ALLOCATIONS = S.ALLOCATIONS
S_inner.STORE = S.STORE
S_inner.EVENTS = S.EVENTS
S_inner.CLOSURESCOPES = S.CLOSURESCOPES
S_inner.CLOSUREBINDINGS = S.CLOSUREBINDINGS
S_inner.CLOSURECACHES = S.CLOSURECACHES
S_inner.CLOSURECALLCACHES = S.CLOSURECALLCACHES
S_inner.DESTRUCTION.HANDLES = S.DESTRUCTION.HANDLES
$heap_owners($heap_graph(S_inner), HOBJECT n_capture) = 1
$heap_owners($heap_graph(S_inner), HOBJECT n_old) = 1
$heap_owners($heap_graph(S_inner), HOBJECT n_new) = 1
$heap_owners($heap_graph(S_inner), HOBJECT n_token) = 2
$call_task_valid(S_inner, GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_token)]))
$call_task_valid(S_inner, GENERATOR_CALL_RESULT pclosurecall true PNULL)
~$call_task_valid(S_inner, GENERATOR_ARGS pgeneratorop[.SELECTION = (pgeneratormethodselection[.TEMPORARY = false])] eps ([KNOWN (POBJECT n_token)]))
~$call_task_valid(S_inner, GENERATOR_CALL_RESULT pclosurecall true (POBJECT n_token))
S_other_origin = S_inner[.ORIGIN = eps]
$generator_call_saved_valid(S_other_origin, pclosurecall)
$generator_call_outer(S_other_origin, pgeneratormethodselection) = (pclosurecall)
~$call_task_valid(S_other_origin, GENERATOR_CALL_RESULT pclosurecall true PNULL)
~$call_task_valid(S_other_origin, GENERATOR_CALL_RETURN pclosurecall PNULL)
S_no_outer = S_inner[.TODO = (GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_token)])) :: ptask_tail*]
~$call_task_valid(S_no_outer, GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_token)]))
S_wrong_outer = S_inner[.TODO = (GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_token)])) :: (GENERATOR_CALL_RESULT pclosurecall[.LINE = $(pclosurecall.LINE + 1)] true PNULL) :: ptask_tail*]
~$call_task_valid(S_wrong_outer, GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_token)]))
S_dead_token = S_inner[.ALLOCATIONS = $destruction_node_delete(S_inner.ALLOCATIONS, HOBJECT n_token)]
$generator_call_saved_valid(S_dead_token, pclosurecall)
~$call_task_valid(S_dead_token, GENERATOR_CALL_RESULT pclosurecall true PNULL)
S_bad_birth = S_inner[.OBJECTS[n_capture] = GETTERCLOSURE n_old (GENERATOR_API_METHOD "send") "Generator" (GENERATOR_CAPTURE pgeneratormethodselection_origin[.TEMPORARY = true])]
~$generator_capture_saved(S_bad_birth, n_capture)
$call_descriptors_valid(S_inner)
$heap_valid($heap_graph(S_inner))
S_inner_pause = $drive(S_inner, 0)
S_inner_pause.COMPLETION = BUDGET
S_inner_pause[.COMPLETION = NORMAL] = S_inner
S_one = $drive(S, 1)
S_one.COMPLETION = BUDGET
S_one.TODO = S_inner.TODO
$heap_owners($heap_graph(S_one), HOBJECT n_capture) = 1
$heap_owners($heap_graph(S_one), HOBJECT n_new) = 1
$heap_owners($heap_graph(S_one), HOBJECT n_token) = 2
$call_descriptors_valid(S_one)
$heap_valid($heap_graph(S_one))
$drive(S_pause[.COMPLETION = NORMAL], 1) = S_one
'''.splitlines() if line.strip()]

review.CASES = {'i115-peer-native-inner-argv': {
    'source': ROW['source'], 'stage': STAGE, 'checks': CHECKS}}

if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=600) else 1)
