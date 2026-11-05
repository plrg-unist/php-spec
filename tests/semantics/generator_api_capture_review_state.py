#!/usr/bin/env python3
"""Count the active Generator API capture instead of a duplicate receiver."""
import hashlib
import json
from pathlib import Path
import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_api_capture_review_cases.json')
ROW = json.loads(CATALOG.read_bytes())[0]
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']
STAGE = (
    'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
    '-- if pconfigcall.KIND = INTRINSIC_GENERATOR_METHOD "send" (pgeneratormethodselection) '
    '-- if pgeneratormethodselection.CAPTURE = (n_capture) '
    '-- if pconfigcall.OWNER = (n_generator) '
    '-- if $lookup(S.ENV, $ptascii("capture")) = (n_capture_cv) '
    '-- if S.STORE[n_capture_cv] = DEFINED PNULL')
CHECKS = [line.strip() for line in r'''
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
S.ACTIVEFIBER = eps
S.SOURCEPENDING = eps
pgeneratormethodselection.SITE = pconfigcall.SITE
pgeneratormethodselection.OBJECT = n_generator
pgeneratormethodselection.LINE = pconfigcall.LINE
pgeneratormethodselection.NAME = $ptascii("send")
pconfigcall.SELECTION = eps
pconfigcall.INDEX = 1
pconfigcall.NAMED
pconfigcall.SENT = [NAMED_SENT (KNOWN (PINT 41))]
pconfigcall.PACKS = [pconfigpack]
pconfigpack.ITEMS = [ENTRY (KSTRING $ptascii("value")) (DIRECT (PINT 41))]
(HARRAY pconfigpack.ARRAY) <- S.ALLOCATIONS
(HARRAY pconfigpack.ARRAY) <- $pools_nodes(S.POOLS)
$lookup(S.ENV, $ptascii("generator")) = (n_generator_cv)
S.STORE[n_generator_cv] = DEFINED PNULL
$lookup(S.ENV, $ptascii("method")) = (n_method_cv)
S.STORE[n_method_cv] = DEFINED pvalue_method
$string_bytes(pvalue_method) = ($ptascii("throw"))
S.OBJECTS[n_generator] = GENERATOR pgenerator
pgenerator.PHASE = GENERATOR_FRESH
S.OBJECTS[n_capture] = GETTERCLOSURE n_generator (GENERATOR_API_METHOD "send") "Generator" (GENERATOR_CAPTURE pgeneratormethodselection_creation)
pgeneratormethodselection_creation.SITE = porigin_capture
pgeneratormethodselection_creation.OBJECT = n_generator
pgeneratormethodselection_creation.NAME = $ptascii("SeNd")
pgeneratormethodselection_creation.CAPTURE = eps
$generator_capture_site(S, porigin_capture, pgeneratormethodselection_creation.NAME, pgeneratormethodselection_creation.LINE)
$origin_node(S.SOURCES, porigin_capture) = (NExprMethodCall expression_receiver expression_name (SEQUENCE ([(NVariadicPlaceholder metadata_placeholder)])) metadata_capture)
$property_computed_name(expression_name)
$closure_callable(S, n_capture)
$getter_capture_live(S, n_capture)
$object_name(S, n_capture) = $ptascii("Closure")
$node_children(S, HOBJECT n_capture) = [HOBJECT n_generator]
$lookup(S.ENV, $ptascii("weakGenerator")) = (n_weak_generator_cv)
S.STORE[n_weak_generator_cv] = DEFINED (POBJECT n_weak_generator)
$weakref_get(S, n_weak_generator) = POBJECT n_generator
$lookup(S.ENV, $ptascii("weakCapture")) = (n_weak_capture_cv)
S.STORE[n_weak_capture_cv] = DEFINED (POBJECT n_weak_capture)
$weakref_get(S, n_weak_capture) = POBJECT n_capture
ptask_tail* = (GETTER_CAPTURE_RESULT n_capture pconfigcall.SITE) :: ptask_after*
$task_nodes(GETTER_CAPTURE_RESULT n_capture pconfigcall.SITE) = [HOBJECT n_capture]
$config_nodes(pconfigcall) = eps
$origin_node(S.SOURCES, pconfigcall.SITE) = (NExprFuncCall expression_callee (SEQUENCE phpType7*) metadata_call)
$dynamic_site(S, (pconfigcall.SITE))
H = $heap_graph(S)
$heap_valid(H)
$call_descriptors_valid(S)
$heap_owners(H, HOBJECT n_generator) = 1
$heap_owners(H, HOBJECT n_capture) = 1
$heap_owners(H, HARRAY pconfigpack.ARRAY) = 1
$call_task_valid(S, CONFIG_INVOKE pconfigcall)
$call_task_valid(S, GETTER_CAPTURE_RESULT n_capture pconfigcall.SITE)
~$call_task_valid(S, CONFIG_INVOKE pconfigcall[.OWNER = (n_capture)])
~$call_task_valid(S, CONFIG_INVOKE pconfigcall[.KIND = INTRINSIC_GENERATOR_METHOD "throw" (pgeneratormethodselection)])
~$call_task_valid(S, CONFIG_INVOKE pconfigcall[.KIND = INTRINSIC_GENERATOR_METHOD "send" (pgeneratormethodselection[.CAPTURE = eps])])
~$call_task_valid(S, CONFIG_INVOKE pconfigcall[.KIND = INTRINSIC_GENERATOR_METHOD "send" (pgeneratormethodselection[.CAPTURE = (n_generator)])])
~$call_task_valid(S, CONFIG_INVOKE pconfigcall[.KIND = INTRINSIC_GENERATOR_METHOD "send" (pgeneratormethodselection[.SITE = porigin_capture])])
~$call_task_valid(S, CONFIG_INVOKE pconfigcall[.LINE = $(pconfigcall.LINE + 1)])
S_unrooted = S[.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_after*]
~$call_task_valid(S_unrooted, CONFIG_INVOKE pconfigcall)
S_dead = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HOBJECT n_capture)]
~$call_task_valid(S_dead, CONFIG_INVOKE pconfigcall)
$generator_selected_method(S_dead, pconfigcall.SITE, n_generator, $ptascii("send"), pconfigcall.LINE, (pgeneratormethodselection))
S_pause = $drive(S, 0)
S_pause.COMPLETION = BUDGET
S_pause[.COMPLETION = NORMAL] = S
PhpStep: S ~> S_normalized
S_normalized.TODO = (GENERATOR_ARGS pgeneratorop eps ([KNOWN (PINT 41)])) :: ptask_tail*
pgeneratorop.OBJECT = n_generator
pgeneratorop.NAME = "send"
pgeneratorop.SITE = pconfigcall.SITE
pgeneratorop.SELECTION = (pgeneratormethodselection)
~pgeneratorop.BORROWED
~pgeneratorop.STARTPACK
$generator_operation_nodes(pgeneratorop) = eps
$task_nodes(GENERATOR_ARGS pgeneratorop eps ([KNOWN (PINT 41)])) = eps
S_normalized.EVENTS = S.EVENTS
S_normalized.STORE = S.STORE
S_normalized.ALLOCATIONS = S.ALLOCATIONS
$heap_owners($heap_graph(S_normalized), HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_normalized), HOBJECT n_capture) = 1
$call_task_valid(S_normalized, GENERATOR_ARGS pgeneratorop eps ([KNOWN (PINT 41)]))
~$call_task_valid(S_normalized, GENERATOR_ARGS pgeneratorop[.SELECTION = eps] eps ([KNOWN (PINT 41)]))
~$call_task_valid(S_normalized, GENERATOR_ARGS pgeneratorop[.NAME = "throw"] eps ([KNOWN (PINT 41)]))
$heap_valid($heap_graph(S_normalized))
$call_descriptors_valid(S_normalized)
'''.splitlines() if line.strip()]

review.CASES = {'i112-peer-active-capture-only-owner': {
    'source': ROW['source'], 'stage': STAGE, 'checks': CHECKS}}

if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=600) else 1)
