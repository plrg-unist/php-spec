#!/usr/bin/env python3
"""Check original and replacement receiver edges at a genuine bind copy."""
import hashlib
import json
from pathlib import Path
import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_api_binding_review_cases.json')
ROW = json.loads(CATALOG.read_bytes())[0]
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']
STAGE = (
    'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
    '-- if pconfigcall.KIND = INTRINSIC_CLOSURE_BIND '
    '-- if $fake_bind_source(pconfigcall) = (n_source) '
    '-- if $lookup(S.ENV, $ptascii("original")) = (n_source_cv) '
    '-- if S.STORE[n_source_cv] = DEFINED PNULL')
CHECKS = [line.strip() for line in r'''
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
S.GLOBAL
S.ACTIVEFIBER = eps
S.SOURCEPENDING = eps
pconfigcall.OWNER = eps
pconfigcall.SELECTION = eps
pconfigcall.INDEX = 3
~pconfigcall.NAMED
pconfigcall.PACKS = eps
pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_source)), NAMED_SENT (KNOWN (POBJECT n_receiver)), NAMED_SENT (KNOWN pvalue_scope)]
$string_bytes(pvalue_scope) = ($ptascii("static"))
$lookup(S.ENV, $ptascii("old")) = (n_old_cv)
S.STORE[n_old_cv] = DEFINED PNULL
$lookup(S.ENV, $ptascii("replacement")) = (n_receiver_cv)
S.STORE[n_receiver_cv] = DEFINED PNULL
S.OBJECTS[n_source] = GETTERCLOSURE n_old (GENERATOR_API_METHOD "send") "Generator" pgettersource
pgettersource = GENERATOR_CAPTURE pgeneratormethodselection
pgeneratormethodselection.OBJECT = n_old
S.OBJECTS[n_old] = GENERATOR pgenerator_old
pgenerator_old.PHASE = GENERATOR_PAUSED
S.OBJECTS[n_receiver] = GENERATOR pgenerator_receiver
pgenerator_receiver.PHASE = GENERATOR_FRESH
$closure_scope_at(S.CLOSURESCOPES, n_source) = eps
$getter_capture_live(S, n_source)
$config_nodes(pconfigcall) = [HOBJECT n_source, HOBJECT n_receiver]
$node_children(S, HOBJECT n_source) = [HOBJECT n_old]
$fake_bind_scope(S, n_source) = BIND_INTERNAL ($ptascii("Generator"))
$fake_bind_warning_message(S, n_source, (n_receiver), BIND_INTERNAL ($ptascii("Generator"))) = eps
$call_task_valid(S, CONFIG_INVOKE pconfigcall)
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
$heap_owners($heap_graph(S), HOBJECT n_source) = 1
$heap_owners($heap_graph(S), HOBJECT n_old) = 1
$heap_owners($heap_graph(S), HOBJECT n_receiver) = 1
S_terminal = S[.TODO = eps][.DESTRUCTION.PHASE = DESTRUCTION_PENDING][.SHUTDOWN.PHASE = SHUTDOWN_PENDING][.COMPILESTOP = false][.CONSTCONTEXT = eps]
$generator_request_terminal(S_terminal)
$generator_close_any_started(S_terminal, S_terminal.ALLOCATIONS)
$generator_request_fresh_any(S_terminal, S_terminal.ALLOCATIONS)
$generator_request_operational(S_terminal)
S_fresh_only = S_terminal[.ALLOCATIONS = $destruction_node_delete(S_terminal.ALLOCATIONS, HOBJECT n_old)]
$generator_request_operational(S_fresh_only)
S_started_only = S_terminal[.ALLOCATIONS = $destruction_node_delete(S_terminal.ALLOCATIONS, HOBJECT n_receiver)]
$generator_request_operational(S_started_only)
S_neither = S_fresh_only[.ALLOCATIONS = $destruction_node_delete(S_fresh_only.ALLOCATIONS, HOBJECT n_receiver)]
~$generator_request_operational(S_neither)
S_pause = $drive(S, 0)
S_pause.COMPLETION = BUDGET
S_pause[.COMPLETION = NORMAL] = S
n_copy = |S.OBJECTS|
PhpStep: S ~> S_copy
S_copy.COMPLETION = NORMAL
S_copy.OBJECTS[n_copy] = BOUNDFAKECLOSURE pboundfake
pboundfake.SOURCE = n_source
pboundfake.SITE = pconfigcall.SITE
pboundfake.ORIGINAL = eps
pboundfake.SCOPE = BIND_INTERNAL ($ptascii("Generator"))
pboundfake.CALLED = BIND_INTERNAL ($ptascii("Generator"))
pboundfake.RECEIVER = (n_receiver)
S_copy.RESULT = KNOWN (POBJECT n_copy)
S_copy.BASE = BASE_VALUE (KNOWN PNULL)
S_copy.TODO = ptask_tail*
S_copy.STORE = S.STORE
S_copy.EVENTS = S.EVENTS
S_copy.ALLOCATIONS = S.ALLOCATIONS ++ [HOBJECT n_copy]
$node_children(S_copy, HOBJECT n_copy) = [HOBJECT n_receiver]
$node_children(S_copy, HOBJECT n_source) = [HOBJECT n_old]
$heap_owners($heap_graph(S_copy), HOBJECT n_source) = 0
$heap_owners($heap_graph(S_copy), HOBJECT n_copy) = 1
$heap_owners($heap_graph(S_copy), HOBJECT n_receiver) = 1
$bound_fake_valid(S_copy, n_copy)
$generator_capture_saved(S_copy, n_copy)
$getter_capture_live(S_copy, n_copy)
$call_descriptors_valid(S_copy)
$heap_valid($heap_graph(S_copy))
pconfigcall.SITE = PORIGIN n_unit pcpath_bind
pcpath_bound = [PCFIELD 0, PCINDEX 15, PCFIELD 0, PCINDEX 1]
porigin_bound = PORIGIN n_unit pcpath_bound
$origin_node(S.SOURCES, porigin_bound) = (NExprFuncCall (NExprVariable (BYTES text_bound) metadata_name) (SEQUENCE phpType7*) metadata_call)
$base64(text_bound) = $ptascii("bound")
$code_at(S.CODE, n_unit) = (pcode)
$code_expression(pcode.EXPRESSIONS, pcpath_bound) = ((z_bound, false))
pgettercall = {SITE porigin_bound, RECEIVER n_receiver, BASE "Generator", METHOD GENERATOR_API_METHOD "send", CAPTURE (n_copy), INDEX 0, SENT eps, LINE z_bound}
S_cursor = S_copy[.ORIGIN = (porigin_bound)]
$getter_selected(S_cursor, pgettercall)
~$getter_call_valid(S_cursor, pgettercall)
S_history = S_copy[.ALLOCATIONS = $destruction_node_delete($destruction_node_delete(S_copy.ALLOCATIONS, HOBJECT n_source), HOBJECT n_old)]
$bound_fake_valid(S_history, n_copy)
$generator_capture_saved(S_history, n_copy)
$getter_capture_live(S_history, n_copy)
$generator_capture_target(S_history, n_copy) = ((n_receiver, "send"))
$node_children(S_history, HOBJECT n_copy) = [HOBJECT n_receiver]
S_all_dead = S_history[.ALLOCATIONS = $destruction_node_delete($destruction_node_delete(S_history.ALLOCATIONS, HOBJECT n_copy), HOBJECT n_receiver)]
$generator_capture_saved(S_all_dead, n_copy)
$generator_capture_target(S_all_dead, n_copy) = ((n_receiver, "send"))
~$getter_capture_live(S_all_dead, n_copy)
S_bad_scope = S_copy[.OBJECTS[n_copy] = BOUNDFAKECLOSURE pboundfake[.SCOPE = BIND_INTERNAL ($ptascii("Closure"))]]
~$bound_fake_valid(S_bad_scope, n_copy)
~$generator_capture_saved(S_bad_scope, n_copy)
S_bad_source = S_copy[.OBJECTS[n_copy] = BOUNDFAKECLOSURE pboundfake[.SOURCE = n_receiver]]
~$bound_fake_valid(S_bad_source, n_copy)
~$generator_capture_saved(S_bad_source, n_copy)
S_forged_source = S_copy[.OBJECTS[n_source] = GETTERCLOSURE n_old (GENERATOR_API_METHOD "send") "Generator" (GENERATOR_CAPTURE pgeneratormethodselection[.OBJECT = n_receiver])]
~$generator_capture_saved(S_forged_source, n_copy)
S_cycle = S_copy[.OBJECTS[n_copy] = BOUNDFAKECLOSURE pboundfake[.SOURCE = n_copy]]
~$bound_fake_valid(S_cycle, n_copy)
~$generator_capture_saved(S_cycle, n_copy)
$generator_capture_target(S_cycle, n_copy) = eps
'''.splitlines() if line.strip()]

review.CASES = {'i114-peer-original-and-copy-receiver-edges': {
    'source': ROW['source'], 'stage': STAGE, 'checks': CHECKS}}

if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=600) else 1)
