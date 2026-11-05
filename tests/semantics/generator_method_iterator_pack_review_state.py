#!/usr/bin/env python3
"""Check the real direct SEND receiver pin after argv and cache retirement."""
import hashlib
import json
from pathlib import Path
import fiber_state_review as review

ROW = next(row for row in json.loads(Path(__file__).with_name(
    'generator_method_iterator_pack_cases.json').read_bytes())
    if row['id'] == 'i116-direct-send-argv-return-demand-and-throw')
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']
assert ROW['source_sha256'] == 'c5e1acc71a2b4ad5d702a63867f0b52aa8161d4f31cef3f7fe2fe2b98f169cad'
STAGE = (
    'S.TODO = (GENERATOR_API_RESULT pgeneratorop (POBJECT n_return)) :: ptask_tail* '
    '-- if pgeneratorop.ARGUMENTS = [POBJECT n_argument] '
    '-- if ~((HOBJECT n_argument) <- S.ALLOCATIONS) '
    '-- if ~$reference_call_used(S, pgeneratorop.SITE) '
    '-- if $lookup(S.ENV, $ptascii("throwing")) = (n_throwing) '
    '-- if S.STORE[n_throwing] = DEFINED (PBOOL false)')
CHECKS = [line.strip() for line in r'''
S.COMPLETION = NORMAL
S.CURRENT = (pcallcontext)
$function_at($all_functions(S), pcallcontext.FUNCTION) = (pfunction)
pfunction.NAME = $ptascii("run116D")
S.ACTIVEFIBER = eps
S.SOURCEPENDING = eps
S.RESULT = KNOWN PNULL
S.BASE = BASE_VALUE (KNOWN PNULL)
S.DESTRUCTION.RELEASES = eps
S.DESTRUCTION.CALLS = eps
pgeneratorop.NAME = "send"
pgeneratorop.OBJECT = n_target
pgeneratorop.SELECTION = eps
pgeneratorop.LOOP = eps
~pgeneratorop.STARTPACK
~pgeneratorop.BORROWED
~pgeneratorop.ADVANCE
S.ORIGIN = (pgeneratorop.SITE)
S.OBJECTS[n_target] = GENERATOR pgenerator
pgenerator.PHASE = GENERATOR_CLOSED
$node_children(S, HOBJECT n_target) = eps
$object_name(S, n_argument) = $ptascii("Argument116D")
$object_name(S, n_return) = $ptascii("Return116D")
$node_children(S, HOBJECT n_return) = eps
S_global = $global_table_view(S)
$lookup(S_global.ENV, $ptascii("target")) = (n_target_cv)
S.STORE[n_target_cv] = DEFINED PNULL
$lookup(S_global.ENV, $ptascii("weakTarget")) = (n_weak_target_cv)
S.STORE[n_weak_target_cv] = DEFINED (POBJECT n_weak_target)
$weakref_get(S, n_weak_target) = POBJECT n_target
$lookup(S_global.ENV, $ptascii("weakArgument")) = (n_weak_argument_cv)
S.STORE[n_weak_argument_cv] = DEFINED (POBJECT n_weak_argument)
$weakref_get(S, n_weak_argument) = PNULL
$lookup(S_global.ENV, $ptascii("weakReturn")) = (n_weak_return_cv)
S.STORE[n_weak_return_cv] = DEFINED (POBJECT n_weak_return)
$weakref_get(S, n_weak_return) = POBJECT n_return
$task_nodes(GENERATOR_API_RESULT pgeneratorop (POBJECT n_return)) = [HOBJECT n_target, HOBJECT n_return]
$task_nodes(GENERATOR_API_RETURN pgeneratorop (POBJECT n_return)) = [HOBJECT n_return]
$heap_owners($heap_graph(S), HOBJECT n_target) = 1
$heap_owners($heap_graph(S), HOBJECT n_argument) = 0
$heap_owners($heap_graph(S), HOBJECT n_return) = 1
$generator_api_result_saved(S, pgeneratorop)
$call_task_valid(S, GENERATOR_API_RESULT pgeneratorop (POBJECT n_return))
~$call_task_valid(S, GENERATOR_API_RESULT pgeneratorop (POBJECT n_argument))
~$call_task_valid(S, GENERATOR_API_RESULT pgeneratorop[.OBJECT = n_return] (POBJECT n_return))
~$call_task_valid(S, GENERATOR_API_RESULT pgeneratorop[.ARGUMENTS = eps] (POBJECT n_return))
~$call_task_valid(S, GENERATOR_API_RESULT pgeneratorop[.NAME = "throw"] (POBJECT n_return))
~$call_task_valid(S, GENERATOR_API_RESULT pgeneratorop[.ADVANCE = true] (POBJECT n_return))
~$call_task_valid(S, GENERATOR_API_RESULT pgeneratorop[.BORROWED = true] (POBJECT n_return))
~$call_task_valid(S, GENERATOR_API_RESULT pgeneratorop[.STARTPACK = true] (POBJECT n_return))
pgeneratorop.SITE = PORIGIN n_unit pcpath_call
porigin_argument = PORIGIN n_unit (pcpath_call ++ [PCFIELD 2, PCINDEX 0, PCFIELD 1])
pconfigcall_direct = {SITE pgeneratorop.SITE, KIND INTRINSIC_GENERATOR_METHOD "send" eps, INDEX 0, SENT eps, NAMED false, OWNER (n_target), SELECTION eps, LINE pgeneratorop.LINE, PACKS eps}
~$generator_iterator_site(S, pconfigcall_direct)
~$config_iterator_owner_live(S, pconfigcall_direct)
~$call_task_valid(S, GENERATOR_API_RESULT pgeneratorop[.SITE = porigin_argument] (POBJECT n_return))
~$call_task_valid(S[.ORIGIN = eps], GENERATOR_API_RESULT pgeneratorop (POBJECT n_return))
~$call_task_valid(S[.ORIGIN = eps], GENERATOR_API_RETURN pgeneratorop (POBJECT n_return))
S_no_receiver = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HOBJECT n_target)]
$generator_api_result_saved(S_no_receiver, pgeneratorop)
~$call_task_valid(S_no_receiver, GENERATOR_API_RESULT pgeneratorop (POBJECT n_return))
$call_task_valid(S_no_receiver, GENERATOR_API_RETURN pgeneratorop (POBJECT n_return))
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
S_pause = $drive(S, 0)
S_pause.COMPLETION = BUDGET
S_pause[.COMPLETION = NORMAL] = S
PhpStep: S ~> S_drop
S_drop.TODO = (GENERATOR_API_RESULT pgeneratorop PNULL) :: ptask_tail*
S_drop.OBJECTS = S.OBJECTS
S_drop.ALLOCATIONS = S.ALLOCATIONS
S_drop.STORE = S.STORE
S_drop.EVENTS = S.EVENTS
$heap_owners($heap_graph(S_drop), HOBJECT n_target) = 1
$heap_owners($heap_graph(S_drop), HOBJECT n_argument) = 0
$heap_owners($heap_graph(S_drop), HOBJECT n_return) = 0
$call_task_valid(S_drop, GENERATOR_API_RESULT pgeneratorop PNULL)
S_budget = $drive(S, 1)
S_budget.COMPLETION = BUDGET
$heap_owners($heap_graph(S_budget), HOBJECT n_target) = 1
~((HOBJECT n_argument) <- S_budget.ALLOCATIONS)
$call_descriptors_valid(S_budget)
$heap_valid($heap_graph(S_budget))
$drive(S_pause[.COMPLETION = NORMAL], 1) = S_budget
'''.splitlines() if line.strip()]

review.CASES = {'i116-peer-direct-send-retired-argv-return-pin': {
    'source': ROW['source'], 'stage': STAGE, 'checks': CHECKS}}

if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=600) else 1)
