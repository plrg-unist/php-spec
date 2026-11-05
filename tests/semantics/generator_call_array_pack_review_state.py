#!/usr/bin/env python3
"""Reach retired packed inputs before a copied Generator's detached reference."""
import hashlib
import json
from pathlib import Path
import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_call_array_pack_review_cases.json')
ROW = next(row for row in json.loads(CATALOG.read_bytes())
           if row['id'] == 'i108-peer-real-multipack-named-receiver-detached-reference')
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']

STAGE = (
    'S.TODO = (ERROR_HANDLER_CLEAN perrorcall) :: ptask_tail* '
    '-- if perrorcall.RESUME = CLOSURE_CALL_COPY_REFERENCE pclosurecall n_copy 0 pnamedargs n_base '
    '-- if pclosurecall.FIRST = (POBJECT n_maker) '
    '-- if $object_name(S, n_maker) = $ptascii("Maker108R")')
CHECKS = [line.strip() for line in r'''
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
S.ACTIVEFIBER = eps
S.CLOSURECALLRETAINED = eps
S.ERRORHANDLER.CALLBACK = eps
S.DESTRUCTION.CLEANUPS = pdestructioncleanup :: pdestructioncleanup_tail*
pdestructioncleanup.SOURCE = ERROR_HANDLER_RESULT perrorcall
~pdestructioncleanup.RELEASED
pnamedargs.SLOTS = eps
pnamedargs.NAMED = eps
pclosurecall.INDEX = 2
pclosurecall.PACKS = [pconfigpack_first, pconfigpack_last]
pconfigpack_first.INDEX = 0
pconfigpack_last.INDEX = 1
pconfigpack_first.ITEMS = [ENTRY (KSTRING $ptascii("newThis")) (DIRECT (POBJECT n_maker)), ENTRY (KSTRING $ptascii("second")) (DIRECT (PINT 23))]
pconfigpack_last.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_token))]
pclosurecall.RAW = [(KINT 1, KNOWN (POBJECT n_token)), (KSTRING $ptascii("second"), KNOWN (PINT 23))]
pclosurecall.SENT.SLOTS = [NAMED_SENT (KNOWN (POBJECT n_token)), NAMED_SENT (KNOWN (PINT 23))]
pclosurecall.SENT.NAMED = eps
pclosurecall.ERROR = eps
~((HARRAY pconfigpack_first.ARRAY) <- S.ALLOCATIONS)
~((HARRAY pconfigpack_last.ARRAY) <- S.ALLOCATIONS)
~((HARRAY pconfigpack_first.ARRAY) <- $task_nodes(perrorcall.RESUME))
~((HARRAY pconfigpack_last.ARRAY) <- $task_nodes(perrorcall.RESUME))
$lookup(S.ENV, $ptascii("packFirst")) = (n_first_cv)
$lookup(S.ENV, $ptascii("packLast")) = (n_last_cv)
S.STORE[n_first_cv] = DEFINED PNULL
S.STORE[n_last_cv] = DEFINED PNULL
$lookup(S.ENV, $ptascii("cell")) = (n_caller_cell)
S.STORE[n_caller_cell] = DEFINED (PINT 41)
n_caller_cell <- S.REFCELLS
$lookup(S.ENV, $ptascii("source")) = (n_source_cv)
S.STORE[n_source_cv] = DEFINED PNULL
$closure_call_copy_row(S, n_copy) = (pclosurebinding)
n_source = pclosurebinding.SOURCE
pclosurebinding.RECEIVER = (n_maker)
S.OBJECTS[n_copy] = REALCLOSURE porigin_function pitem* eps
$closure_items_nodes(pitem*) = [HOBJECT n_capture]
$node_children(S, HOBJECT n_copy) = [HOBJECT n_capture, HOBJECT n_maker]
$target_receiver(S, CLOSURE_TARGET n_source) = (n_old)
$object_name(S, n_old) = $ptascii("Old108R")
$object_name(S, n_token) = $ptascii("Token108R")
H = $heap_graph(S)
$heap_valid(H)
$call_descriptors_valid(S)
$heap_owners(H, HOBJECT n_copy) = 1
$heap_owners(H, HOBJECT n_source) = 1
$heap_owners(H, HOBJECT n_old) = 1
$heap_owners(H, HOBJECT n_maker) = 2
$heap_owners(H, HOBJECT n_capture) = 2
$heap_owners(H, HOBJECT n_token) = 1
$closure_call_copy_raw_arguments_valid(S, pclosurecall)
$closure_call_copy_named(S, pclosurecall)
~$closure_call_copy_raw_arguments_valid(S, pclosurecall[.PACKS = eps])
~$closure_call_copy_raw_arguments_valid(S, pclosurecall[.PACKS = [pconfigpack_first]])
~$closure_call_copy_raw_arguments_valid(S, pclosurecall[.PACKS = [pconfigpack_last, pconfigpack_first]])
~$closure_call_copy_raw_arguments_valid(S, pclosurecall[.PACKS = [pconfigpack_first, pconfigpack_last[.ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 41))]]]])
~$closure_call_copy_raw_arguments_valid(S, pclosurecall[.RAW = [(KINT 1, KNOWN (PINT 41)), (KSTRING $ptascii("second"), KNOWN (PINT 23))]])
~$closure_call_copy_raw_valid(S, pclosurecall[.SOURCE = n_copy], n_copy)
~$closure_call_copy_raw_valid(S, pclosurecall[.FIRST = (POBJECT n_old)], n_copy)
S_pause = $drive(S, 0)
S_pause.COMPLETION = BUDGET
S_pause[.COMPLETION = NORMAL] = S
PhpStep: S ~> S_restored
S_restored.TODO = (CLOSURE_CALL_COPY_REFERENCE pclosurecall n_copy 0 pnamedargs n_base) :: ptask_tail*
S_restored.DESTRUCTION.CLEANUPS = pdestructioncleanup_tail*
S_restored.ERRORHANDLER.CALLBACK = (perrorcall.CALLBACK)
$string_bytes(perrorcall.CALLBACK) = $ptascii("Warning108R")
$call_task_valid(S_restored, perrorcall.RESUME)
PhpStep: S_restored ~> S_wrapped
S_wrapped.TODO = (CLOSURE_CALL_COPY_FORWARD pclosurecall n_copy 1 pnamedargs_wrapped n_base) :: ptask_tail*
pnamedargs_wrapped.SLOTS = [NAMED_SENT (REFERENCE n_fresh_cell)]
pnamedargs_wrapped.NAMED = eps
n_fresh_cell = |S_restored.STORE|
n_fresh_cell =/= n_caller_cell
S_wrapped.STORE[n_fresh_cell] = DEFINED (POBJECT n_token)
n_fresh_cell <- S_wrapped.REFCELLS
S_wrapped.STORE[n_caller_cell] = DEFINED (PINT 41)
$call_task_valid(S_wrapped, CLOSURE_CALL_COPY_FORWARD pclosurecall n_copy 1 pnamedargs_wrapped n_base)
~$call_task_valid(S_wrapped, CLOSURE_CALL_COPY_FORWARD pclosurecall n_copy 1 pnamedargs_wrapped[.SLOTS = [NAMED_SENT (REFERENCE n_caller_cell)]] n_base)
$heap_valid($heap_graph(S_wrapped))
$call_descriptors_valid(S_wrapped)
'''.splitlines() if line.strip()]

review.CASES = {'i108-peer-retired-packs-before-detached-reference': {
    'source': ROW['source'], 'stage': STAGE, 'checks': CHECKS}}

if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=600) else 1)
