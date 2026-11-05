#!/usr/bin/env python3
"""Count distinct outer argv/capture and inner copies at genuine forwarding."""
import hashlib
import json
from pathlib import Path
import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_explicit_invoke_review_cases.json')
ROW = json.loads(CATALOG.read_bytes())[0]
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']
STAGE = (
    'S.TODO = (CONFIG_INVOKE pconfigcall) :: (GETTER_CAPTURE_RESULT n_capture porigin_invoke) :: ptask_tail* '
    '-- if porigin_invoke = pconfigcall.SITE '
    '-- if pconfigcall.KIND = INTRINSIC_GENERATOR_METHOD "send" (pgeneratormethodselection) '
    '-- if pgeneratormethodselection.CAPTURE = (n_capture) '
    '-- if $lookup(S.ENV, $ptascii("capture")) = (n_capture_cv) '
    '-- if S.STORE[n_capture_cv] = DEFINED PNULL')
CHECKS = [line.strip() for line in r'''
S.COMPLETION = NORMAL
S.ACTIVEFIBER = eps
S.SOURCEPENDING = eps
S.CURRENT = (pcallcontext)
$function_at($all_functions(S), pcallcontext.FUNCTION) = (pfunction)
pfunction.NAME = $ptascii("run113P")
pcallcontext.ARGC = 0
pcallcontext.INSTANCE = eps
S_global = $global_table_view(S)
$lookup(S_global.ENV, $ptascii("generator")) = (n_generator_cv)
S.STORE[n_generator_cv] = DEFINED PNULL
$lookup(S_global.ENV, $ptascii("pack")) = (n_pack_cv)
S.STORE[n_pack_cv] = DEFINED PNULL
$lookup(S_global.ENV, $ptascii("token")) = (n_token_cv)
S.STORE[n_token_cv] = DEFINED PNULL
pconfigcall.OWNER = (n_generator)
pgeneratormethodselection.OBJECT = n_generator
pgeneratormethodselection.SITE = porigin_invoke
pgeneratormethodselection.LINE = pconfigcall.LINE
pgeneratormethodselection.NAME = $ptascii("send")
pconfigcall.SELECTION = eps
pconfigcall.INDEX = 1
pconfigcall.NAMED
pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_token))]
pconfigcall.PACKS = [pconfigpack]
pconfigpack.ITEMS = [ENTRY (KSTRING $ptascii("value")) (DIRECT (POBJECT n_token))]
~((HARRAY pconfigpack.ARRAY) <- S.ALLOCATIONS)
S.OBJECTS[n_generator] = GENERATOR pgenerator
pgenerator.PHASE = GENERATOR_FRESH
S.OBJECTS[n_capture] = GETTERCLOSURE n_generator (GENERATOR_API_METHOD "send") "Generator" pgettersource
$getter_capture_live(S, n_capture)
$object_name(S, n_token) = $ptascii("Token113P")
$lookup(S_global.ENV, $ptascii("weakGenerator")) = (n_weak_generator_cv)
S.STORE[n_weak_generator_cv] = DEFINED (POBJECT n_weak_generator)
$weakref_get(S, n_weak_generator) = POBJECT n_generator
$lookup(S_global.ENV, $ptascii("weakCapture")) = (n_weak_capture_cv)
S.STORE[n_weak_capture_cv] = DEFINED (POBJECT n_weak_capture)
$weakref_get(S, n_weak_capture) = POBJECT n_capture
$lookup(S_global.ENV, $ptascii("weakToken")) = (n_weak_token_cv)
S.STORE[n_weak_token_cv] = DEFINED (POBJECT n_weak_token)
$weakref_get(S, n_weak_token) = POBJECT n_token
$origin_node(S.SOURCES, porigin_invoke) = (NExprMethodCall expression_receiver (NIdentifier (BYTES text_method) metadata_name) (SEQUENCE phpType7*) metadata_call)
$ptlc($base64(text_method)) = $ptascii("__invoke")
$generator_capture_wrapper_site(S, porigin_invoke)
$config_nodes(pconfigcall) = [HOBJECT n_token]
$task_nodes(GETTER_CAPTURE_RESULT n_capture porigin_invoke) = [HOBJECT n_capture]
$node_children(S, HOBJECT n_capture) = [HOBJECT n_generator]
H = $heap_graph(S)
$heap_valid(H)
$call_descriptors_valid(S)
$heap_owners(H, HOBJECT n_capture) = 1
$heap_owners(H, HOBJECT n_generator) = 1
$heap_owners(H, HOBJECT n_token) = 1
$call_task_valid(S, CONFIG_INVOKE pconfigcall)
~$call_task_valid(S, CONFIG_INVOKE pconfigcall[.OWNER = (n_capture)])
~$call_task_valid(S, CONFIG_INVOKE pconfigcall[.KIND = INTRINSIC_GENERATOR_METHOD "throw" (pgeneratormethodselection)])
~$call_task_valid(S, CONFIG_INVOKE pconfigcall[.KIND = INTRINSIC_GENERATOR_METHOD "send" (pgeneratormethodselection[.CAPTURE = eps])])
S_pause = $drive(S, 0)
S_pause.COMPLETION = BUDGET
S_pause[.COMPLETION = NORMAL] = S
PhpStep: S ~> S_inner
S_inner.TODO = (GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_token)])) :: (GETTER_CAPTURE_RESULT n_capture porigin_invoke) :: (GENERATOR_INVOKE_RESULT pconfigcall true PNULL) :: ptask_tail*
pgeneratorop.OBJECT = n_generator
pgeneratorop.NAME = "send"
pgeneratorop.SITE = porigin_invoke
pgeneratorop.SELECTION = (pgeneratormethodselection)
~pgeneratorop.BORROWED
~pgeneratorop.STARTPACK
pgeneratorop.ARGUMENTS = eps
$generator_operation_nodes(pgeneratorop) = eps
$task_nodes(GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_token)])) = [HOBJECT n_token]
$task_nodes(GENERATOR_INVOKE_RESULT pconfigcall true PNULL) = [HOBJECT n_capture, HOBJECT n_token]
S_inner.EVENTS = S.EVENTS
S_inner.STORE = S.STORE
S_inner.ALLOCATIONS = S.ALLOCATIONS
$heap_owners($heap_graph(S_inner), HOBJECT n_capture) = 2
$heap_owners($heap_graph(S_inner), HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_inner), HOBJECT n_token) = 2
$call_task_valid(S_inner, GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_token)]))
$call_task_valid(S_inner, GENERATOR_INVOKE_RESULT pconfigcall true PNULL)
~$call_task_valid(S_inner, GENERATOR_INVOKE_RESULT pconfigcall true (POBJECT n_token))
~$call_task_valid(S_inner, GENERATOR_INVOKE_RESULT pconfigcall[.LINE = $(pconfigcall.LINE + 1)] true PNULL)
S_dead = S_inner[.ALLOCATIONS = $destruction_node_delete(S_inner.ALLOCATIONS, HOBJECT n_capture)]
~$call_task_valid(S_dead, GENERATOR_INVOKE_RESULT pconfigcall true PNULL)
$generator_invoke_saved_valid(S_dead, pconfigcall)
$heap_valid($heap_graph(S_inner))
$call_descriptors_valid(S_inner)
'''.splitlines() if line.strip()]

review.CASES = {'i113-peer-outer-to-inner-copies': {
    'source': ROW['source'], 'stage': STAGE, 'checks': CHECKS}}

if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=600) else 1)
