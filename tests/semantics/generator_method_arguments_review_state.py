#!/usr/bin/env python3
"""Transfer a retired packed input's real receiver and snapshot into Generator API."""
import hashlib
import json
from pathlib import Path
import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_method_arguments_review_cases.json')
ROW = next(row for row in json.loads(CATALOG.read_bytes())
           if row['id'] == 'i109-peer-packed-alias-sole-receiver')
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']
STAGE = (
    'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
    '-- if pconfigcall.KIND = INTRINSIC_GENERATOR_METHOD "send" eps '
    '-- if pconfigcall.OWNER = (n_generator) '
    '-- if $lookup(S.ENV, $ptascii("generator")) = (n_generator_cv) '
    '-- if S.STORE[n_generator_cv] = DEFINED PNULL')
CHECKS = [line.strip() for line in r'''
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
S.ACTIVEFIBER = eps
S.SOURCEPENDING = eps
pconfigcall.INDEX = 1
pconfigcall.NAMED
pconfigcall.SELECTION = eps
pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_token))]
pconfigcall.PACKS = [pconfigpack]
pconfigpack.INDEX = 0
pconfigpack.ITEMS = [ENTRY (KSTRING $ptascii("value")) (DIRECT (POBJECT n_token))]
~((HARRAY pconfigpack.ARRAY) <- S.ALLOCATIONS)
~((HARRAY pconfigpack.ARRAY) <- $task_nodes(CONFIG_INVOKE pconfigcall))
$lookup(S.ENV, $ptascii("pack")) = (n_pack_cv)
S.STORE[n_pack_cv] = DEFINED PNULL
$lookup(S.ENV, $ptascii("cell")) = (n_caller_cell)
S.STORE[n_caller_cell] = DEFINED (POBJECT n_token)
n_caller_cell <- S.REFCELLS
S.OBJECTS[n_generator] = GENERATOR pgenerator
pgenerator.PHASE = GENERATOR_FRESH
pgenerator.REFCELL = eps
pgenerator.CLOSURE = eps
$object_name(S, n_token) = $ptascii("Token109L")
$lookup(S.ENV, $ptascii("weakGenerator")) = (n_weak_generator_cv)
S.STORE[n_weak_generator_cv] = DEFINED (POBJECT n_weak_generator)
$weakref_get(S, n_weak_generator) = POBJECT n_generator
$lookup(S.ENV, $ptascii("weakToken")) = (n_weak_token_cv)
S.STORE[n_weak_token_cv] = DEFINED (POBJECT n_weak_token)
$weakref_get(S, n_weak_token) = POBJECT n_token
$config_nodes(pconfigcall) = [HOBJECT n_generator, HOBJECT n_token]
H = $heap_graph(S)
$heap_valid(H)
$call_descriptors_valid(S)
$heap_owners(H, HOBJECT n_generator) = 1
$heap_owners(H, HOBJECT n_token) = 2
$heap_owners(H, HCELL n_caller_cell) = 1
$call_task_valid(S, CONFIG_INVOKE pconfigcall)
~$call_task_valid(S, CONFIG_INVOKE pconfigcall[.OWNER = eps])
~$call_task_valid(S, CONFIG_INVOKE pconfigcall[.OWNER = (n_token)])
~$call_task_valid(S, CONFIG_INVOKE pconfigcall[.KIND = INTRINSIC_GENERATOR_METHOD "throw" eps])
~$call_task_valid(S, CONFIG_INVOKE pconfigcall[.INDEX = 0])
~$call_task_valid(S, CONFIG_INVOKE pconfigcall[.PACKS = eps])
~$call_task_valid(S, CONFIG_INVOKE pconfigcall[.LINE = $(pconfigcall.LINE + 1)])
~$call_task_valid(S, CONFIG_INVOKE pconfigcall[.PACKS = [pconfigpack[.ITEMS = [ENTRY (KSTRING $ptascii("value")) (DIRECT (PINT 41))]]]])
~$call_task_valid(S, CONFIG_INVOKE pconfigcall[.PACKS = [pconfigpack[.ITEMS = [ENTRY (KSTRING $ptascii("value")) (ALIAS n_caller_cell)]]]])
S_dead = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HOBJECT n_generator)]
~$call_task_valid(S_dead, CONFIG_INVOKE pconfigcall)
S_pause = $drive(S, 0)
S_pause.COMPLETION = BUDGET
S_pause[.COMPLETION = NORMAL] = S
PhpStep: S ~> S_normalized
S_normalized.TODO = (GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_token)])) :: ptask_tail*
pgeneratorop.OBJECT = n_generator
pgeneratorop.NAME = "send"
pgeneratorop.SITE = pconfigcall.SITE
pgeneratorop.LINE = pconfigcall.LINE
pgeneratorop.LOOP = eps
~pgeneratorop.ADVANCE
pgeneratorop.ARGUMENTS = eps
~pgeneratorop.STARTPACK
~pgeneratorop.BORROWED
$task_nodes(GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_token)])) = $config_nodes(pconfigcall)
S_normalized.EVENTS = S.EVENTS
S_normalized.STORE = S.STORE
S_normalized.ALLOCATIONS = S.ALLOCATIONS
$heap_owners($heap_graph(S_normalized), HOBJECT n_generator) = 1
$heap_owners($heap_graph(S_normalized), HOBJECT n_token) = 2
$call_task_valid(S_normalized, GENERATOR_ARGS pgeneratorop eps ([KNOWN (POBJECT n_token)]))
~$call_task_valid(S_normalized, GENERATOR_ARGS pgeneratorop[.NAME = "throw"] eps ([KNOWN (POBJECT n_token)]))
~$call_task_valid(S_normalized, GENERATOR_ARGS pgeneratorop eps ([REFERENCE n_caller_cell]))
$getter_arguments(S, pconfigcall.SITE) = PCALLARGUMENTS ([(NArg ABSENT expression_pack (BOOLEAN false) (BOOLEAN true) metadata_pack)]) 2
phpType7_value = NArg (NIdentifier (BYTES "dmFsdWU=") metadata_pack) expression_pack (BOOLEAN false) (BOOLEAN false) metadata_pack
phpType7_extra = NArg (NIdentifier (BYTES "ZXh0cmE=") metadata_pack) expression_pack (BOOLEAN false) (BOOLEAN false) metadata_pack
phpType7_exception = NArg (NIdentifier (BYTES "ZXhjZXB0aW9u") metadata_pack) expression_pack (BOOLEAN false) (BOOLEAN false) metadata_pack
$generator_api_extent("send", [phpType7_value], 1)
~$generator_api_extent("send", [phpType7_value], 0)
~$generator_api_extent("send", [phpType7_value], 2)
~$generator_api_extent("send", [phpType7_extra], 1)
$generator_api_extent("throw", [phpType7_exception], 1)
~$generator_api_extent("throw", [phpType7_value], 1)
$heap_valid($heap_graph(S_normalized))
$call_descriptors_valid(S_normalized)
'''.splitlines() if line.strip()]

review.CASES = {'i109-peer-retired-pack-normalization-owners': {
    'source': ROW['source'], 'stage': STAGE, 'checks': CHECKS}}

if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=600) else 1)
