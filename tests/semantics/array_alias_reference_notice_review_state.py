"""Emit real shared CELL payload ownership, COW and array-alias refusals."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

from array_alias_reference_notice_review_cases import CASES
from reference_send_notice_review_state import PREFIX

STAGES = {
    0: ['S.TODO = (NAMED_SEND pcalltarget eps 0 pnamedargs porigin? z) :: ptask_tail*',
        'S.RESULT = KNOWN (PARRAY n)', '$rsn_outputs(S.EVENTS) = $ptascii("P;")'],
    1: ['S.TODO = (NAMED_ARGS pcalltarget eps 1 pnamedargs porigin? z) :: ptask_tail*',
        '$rsn_outputs(S.EVENTS) = $ptascii("P;H;")'],
    2: ['S.TODO = ACQUIRE_CALL :: ptask_tail*', 'S.RESULT = REFERENCE n',
        '$rsn_outputs(S.EVENTS) = $ptascii("P;H;F:7:7;")'],
}

CHECKS = r'''
S = $rsn_find(S_start, 1000, 0)
$rsn_stage(S, 0)
S.TODO = (NAMED_SEND pcalltarget eps 0 pnamedargs (porigin_call) z_call) :: ptask_tail*
S.RESULT = KNOWN (PARRAY n_root)
$lookup(S.ENV, $ptascii("source")) = (n_source)
$lookup(S.ENV, $ptascii("copy")) = (n_copy)
$lookup(S.ENV, $ptascii("held")) = (n_leaf)
$lookup(S.ENV, $ptascii("snapshot")) = (n_snapshot)
$lookup(S.ENV, $ptascii("seed")) = (n_seed)
$lookup(S.ENV, $ptascii("leaf")) = eps
S.STORE[n_source] = DEFINED (PARRAY n_root)
S.STORE[n_copy] = DEFINED (PARRAY n_root)
S.STORE[n_leaf] = DEFINED (PARRAY n_old_child)
S.STORE[n_snapshot] = DEFINED (PARRAY n_old_child)
S.ARRAYS[n_root].ITEMS = [ENTRY (KSTRING ($ptascii("left"))) (ALIAS n_leaf), ENTRY (KSTRING ($ptascii("right"))) (ALIAS n_leaf)]
S.ARRAYS[n_old_child].ITEMS = [ENTRY (KSTRING ($ptascii("k"))) (DIRECT (PINT 5))]
$node_children(S, HARRAY n_root) = [HCELL n_leaf, HCELL n_leaf]
$node_children(S, HCELL n_leaf) = [HARRAY n_old_child]
$heap_owners($heap_graph(S), HARRAY n_root) = 3
$heap_owners($heap_graph(S), HCELL n_leaf) = 3
$heap_owners($heap_graph(S), HARRAY n_old_child) = 2
$call_reference_operand_valid(S, REFERENCE n_leaf)
~(n_old_child <- S.LITERALARRAYRETAINED) /\ ~(n_old_child <- S.LITERALARRAYDEBTS)
$heap_count(HARRAY n_old_child, S.NATIVEEXCESS) = 0
~$array_immutable(S, n_old_child)
~((HARRAY n_old_child) <- $heap_reach($pools_nodes(S.POOLS), eps, $allocation_edges(S, S.ALLOCATIONS)))
S.HELD = eps /\ S.BASE = BASE_VALUE (KNOWN PNULL)
$named_reference_notice_pending(S)
$call_descriptors_valid(S) /\ $heap_valid($heap_graph(S))
n_private = |S.STORE|
S_step = $drive(S, 1)
S_step.COMPLETION = BUDGET
S_notice = S_step[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
perrorcall.RESUME = NAMED_ARGS pcalltarget eps 1 pnamedargs_after (porigin_call) z_call
pnamedargs_after.SLOTS = [NAMED_SENT (REFERENCE n_private)]
pnamedargs_after.NAMED = eps
S_notice.STORE[n_private] = DEFINED (PARRAY n_root)
$task_nodes(perrorcall.RESUME) = [HCELL n_private]
$node_children(S_notice, HCELL n_private) = [HARRAY n_root]
$node_children(S_notice, HCELL n_leaf) = [HARRAY n_old_child]
$heap_owners($heap_graph(S_notice), HCELL n_private) = 1
$heap_owners($heap_graph(S_notice), HARRAY n_root) = 3
$heap_owners($heap_graph(S_notice), HCELL n_leaf) = 3
$heap_owners($heap_graph(S_notice), HARRAY n_old_child) = 2
S_notice.RESULT = KNOWN PNULL /\ S_notice.BASE = BASE_VALUE (KNOWN PNULL)
S_notice.HELD = S.HELD
$error_call_valid(S_notice, perrorcall) /\ $call_descriptors_valid(S_notice)
$heap_valid($heap_graph(S_notice))
S_handler = $rsn_find(S_notice, 1000, 1)
$rsn_stage(S_handler, 1)
S_handler.TODO = perrorcall.RESUME :: ptask_tail*
$lookup(S_handler.ENV, $ptascii("source")) = eps
$lookup(S_handler.ENV, $ptascii("held")) = eps
~((HCELL n_source) <- S_handler.ALLOCATIONS)
(HCELL n_leaf) <- S_handler.ALLOCATIONS
S_handler.STORE[n_copy] = DEFINED (PARRAY n_root)
S_handler.STORE[n_private] = DEFINED (PARRAY n_root)
S_handler.STORE[n_leaf] = DEFINED (PARRAY n_child)
n_child =/= n_old_child
S_handler.STORE[n_snapshot] = DEFINED (PARRAY n_old_child)
S_handler.ARRAYS[n_root].ITEMS = S.ARRAYS[n_root].ITEMS
S_handler.ARRAYS[n_old_child].ITEMS = S.ARRAYS[n_old_child].ITEMS
S_handler.ARRAYS[n_child].ITEMS = [ENTRY (KSTRING ($ptascii("k"))) (DIRECT (PINT 7))]
$node_children(S_handler, HCELL n_leaf) = [HARRAY n_child]
$heap_owners($heap_graph(S_handler), HCELL n_private) = 1
$heap_owners($heap_graph(S_handler), HARRAY n_root) = 2
$heap_owners($heap_graph(S_handler), HCELL n_leaf) = 2
$heap_owners($heap_graph(S_handler), HARRAY n_old_child) = 1
$heap_owners($heap_graph(S_handler), HARRAY n_child) = 1
$duplicate_item(S_handler, n_root, ALIAS n_leaf) = ALIAS n_leaf
$error_call_valid(S_handler, perrorcall) /\ $call_descriptors_valid(S_handler)
$heap_valid($heap_graph(S_handler))
S_returned = $rsn_find(S_handler, 1000, 2)
$rsn_stage(S_returned, 2)
S_returned.RESULT = REFERENCE n_private
S_returned.STORE[n_private] = DEFINED (PARRAY n_new_root)
n_new_root =/= n_root
S_returned.ARRAYS[n_new_root].ITEMS = S.ARRAYS[n_root].ITEMS
S_returned.ARRAYS[n_root].ITEMS = S.ARRAYS[n_root].ITEMS
S_returned.STORE[n_copy] = DEFINED (PARRAY n_root)
S_returned.STORE[n_leaf] = DEFINED (PARRAY n_child)
S_returned.ARRAYS[n_child].ITEMS = [ENTRY (KSTRING ($ptascii("k"))) (DIRECT (PINT 17))]
S_returned.ARRAYS[n_old_child].ITEMS = S.ARRAYS[n_old_child].ITEMS
$node_children(S_returned, HARRAY n_new_root) = [HCELL n_leaf, HCELL n_leaf]
$node_children(S_returned, HCELL n_leaf) = [HARRAY n_child]
$heap_owners($heap_graph(S_returned), HCELL n_private) = 1
$heap_owners($heap_graph(S_returned), HARRAY n_root) = 1
$heap_owners($heap_graph(S_returned), HARRAY n_new_root) = 1
$heap_owners($heap_graph(S_returned), HCELL n_leaf) = 4
$heap_owners($heap_graph(S_returned), HARRAY n_child) = 1
$heap_owners($heap_graph(S_returned), HARRAY n_old_child) = 1
$call_descriptors_valid(S_returned) /\ $heap_valid($heap_graph(S_returned))
S_zero = $drive(S_notice, 0)
S_zero.COMPLETION = BUDGET
S_zero[.COMPLETION = NORMAL] = S_notice
S_one = $rsn_resume(S_zero, 1)
S_two = $rsn_resume(S_one, 1)
S_two = $drive(S_notice, 2)
S_full = $drive(S_returned, 3000)
S_full.COMPLETION = NORMAL
$rsn_outputs(S_full.EVENTS) = $ptascii("P;H;F:7:7;R:117:117:117:117:5:1:1;")
$rsn_diagnostics(S_full.EVENTS) = eps
$lookup(S_full.ENV, $ptascii("r")) = (n_private)
S_full.STORE[n_private] = DEFINED (PARRAY n_new_root)
S_full.STORE[n_leaf] = DEFINED (PARRAY n_child)
S_full.ARRAYS[n_child].ITEMS = [ENTRY (KSTRING ($ptascii("k"))) (DIRECT (PINT 117))]
S_full.ARRAYS[n_old_child].ITEMS = S.ARRAYS[n_old_child].ITEMS
$heap_owners($heap_graph(S_full), HCELL n_private) = 1
$heap_owners($heap_graph(S_full), HARRAY n_root) = 1
$heap_owners($heap_graph(S_full), HARRAY n_new_root) = 1
$heap_owners($heap_graph(S_full), HCELL n_leaf) = 4
$heap_owners($heap_graph(S_full), HARRAY n_child) = 1
$heap_owners($heap_graph(S_full), HARRAY n_old_child) = 1
S_full.CURRENT = eps /\ S_full.FRAMES = eps /\ S_full.TODO = eps
S_full.HELD = eps /\ S_full.RETIREDOWNERS = eps
$call_descriptors_valid(S_full) /\ $heap_valid($heap_graph(S_full))
'''.strip().splitlines()

DERIVED = r'''
$named_reference_notice_entries(S, S.ARRAYS[n_root].ITEMS)
S_mix = S[.ARRAYS[n_root].ITEMS = [ENTRY (KINT 0) (ALIAS n_leaf), ENTRY (KINT 1) (DIRECT (PARRAY n_old_child))]]
$named_reference_notice_array(S_mix, PARRAY n_root)
S_root_cycle = S[.STORE = $set_cell(S.STORE, n_leaf, DEFINED (PARRAY n_root))]
~$named_reference_notice_array(S_root_cycle, PARRAY n_root)
S_child_cycle = S[.ARRAYS[n_old_child].ITEMS = [ENTRY (KINT 0) (ALIAS n_leaf)]]
~$named_reference_notice_array(S_child_cycle, PARRAY n_root)
~$named_reference_notice_pending(S_child_cycle)
S_cycle_step = $drive(S_child_cycle, 1)
S_cycle_step.COMPLETION = UNSUPPORTED "error-handler ingress requires a producer continuation"
S_retired_cell = S[.ALLOCATIONS = $call_remove_owner(S.ALLOCATIONS, HCELL n_leaf)]
~$named_reference_notice_array(S_retired_cell, PARRAY n_root)
S_retired_child = S[.ALLOCATIONS = $call_remove_owner(S.ALLOCATIONS, HARRAY n_old_child)]
~$named_reference_notice_array(S_retired_child, PARRAY n_root)
S_retained = S[.LITERALARRAYRETAINED = S.LITERALARRAYRETAINED ++ [n_old_child]]
~$named_reference_notice_array(S_retained, PARRAY n_root)
S_debt = S[.LITERALARRAYDEBTS = S.LITERALARRAYDEBTS ++ [n_old_child]]
~$named_reference_notice_array(S_debt, PARRAY n_root)
S_excess = S[.NATIVEEXCESS = S.NATIVEEXCESS ++ [HARRAY n_old_child]]
~$named_reference_notice_array(S_excess, PARRAY n_root)
S_empty = S[.ARRAYS[n_old_child] = $array_empty()]
$named_reference_notice_array(S_empty, PARRAY n_root)
S_immutable = S_empty[.GC.IMMUTABLE = S.GC.IMMUTABLE ++ [n_old_child]]
~$named_reference_notice_array(S_immutable, PARRAY n_root)
S.POOLS = ppool :: ppool_tail*
S_pool = S[.POOLS = ppool[.CONSTANTS = [PCONSTANT ([PCINDEX 0]) (PARRAY n_old_child)]] :: ppool_tail*]
~$named_reference_notice_array(S_pool, PARRAY n_root)
S_pool_parent = S[.POOLS = ppool[.CONSTANTS = [PCONSTANT ([PCINDEX 0]) (PARRAY n_root)]] :: ppool_tail*]
~$named_reference_notice_array(S_pool_parent, PARRAY n_root)
S_cell_retained = S[.LITERALREFRETAINED = [n_leaf]]
~$named_reference_notice_array(S_cell_retained, PARRAY n_root)
S_cell_debt = S[.LITERALREFDEBTS = [n_leaf]]
~$named_reference_notice_array(S_cell_debt, PARRAY n_root)
S_cell_excess = S[.NATIVEEXCESS = S.NATIVEEXCESS ++ [HCELL n_leaf]]
~$named_reference_notice_array(S_cell_excess, PARRAY n_root)
S_propref = S[.PROPREFS = [{CELL n_leaf, SOURCES eps}]]
~$named_reference_notice_array(S_propref, PARRAY n_root)
$target_function(S, pcalltarget) = (pfunction)
S_coercion = S[.REFCOERCIONS = [{CELL n_leaf, SITE pfunction.ORIGIN, LINE 0, VALUE eps}]]
~$named_reference_notice_array(S_coercion, PARRAY n_root)
S_backed = S[.PARAMETERBACKINGS = [{FUNCTION pfunction.ORIGIN, INDEX 0, CELL n_leaf, LINE 0, VALUE eps}]]
~$named_reference_notice_array(S_backed, PARRAY n_root)
S_container = S[.CONTAINERINITS = [{CELL n_leaf, ARRAY n_old_child, SITE pfunction.ORIGIN, LINE 0}]]
~$named_reference_notice_array(S_container, PARRAY n_root)
S_nul = S[.ARRAYS[n_old_child].ITEMS = [ENTRY (KINT 0) (DIRECT (PSTRING_CARRIER INTERNED_STRING ([0])))]]
~$named_reference_notice_array(S_nul, PARRAY n_root)
S_scalar = S[.STORE = $set_cell(S.STORE, n_leaf, DEFINED (PINT 5))]
$named_reference_notice_array(S_scalar, PARRAY n_root)
S_direct = S_cell_excess[.ARRAYS[n_root].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_old_child))]]
$named_reference_notice_array(S_direct, PARRAY n_root)
'''.strip().splitlines()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    report = json.loads((args.raw / 'report.json').read_text())
    assert report['all_pass'] and report['mode'] == 'SL' and report['source_agreements'] == 1
    assert len(report['records']) == 1
    row = report['records'][0]
    source = Path(row['source'])
    assert source.read_bytes() == CASES[row['id']]
    assert hashlib.sha256(source.read_bytes()).hexdigest() == row['source_sha256']
    checked = json.loads((args.raw / row['id'] / 'checked.json').read_text())
    assert checked['ok'] and checked['fixture']
    args.output.mkdir(parents=True, exist_ok=False)
    stages = ''.join(f'def $rsn_stage(S, {index}) = true\n' +
                     ''.join('  -- if ' + c + '\n' for c in checks)
                     for index, checks in STAGES.items())
    stages += 'def $rsn_stage(S, n_stage) = false -- otherwise\n'
    filename = base64.b64encode(bytes(source)).decode()
    common = ['S_initial = $php_run(' + checked['fixture'] + ', 0, ' + json.dumps(filename) + ')',
              'S_initial.COMPLETION = BUDGET', 'S_start = S_initial[.COMPLETION = NORMAL]']
    assertions = common + CHECKS + DERIVED
    fixture = args.output / (row['id'] + '.watsup')
    fixture.write_text(PREFIX + stages + '\ndec $main() : bool\ndef $main() = true\n' +
                       ''.join('  -- if ' + c + '\n' for c in assertions))
    manifest = {'source_revision': report['revision'], 'source_mode': 'SL',
                'fixture_mode': 'AL/cache=false/det=true', 'fixture': str(fixture.resolve()),
                'fixture_sha256': hashlib.sha256(fixture.read_bytes()).hexdigest(),
                'conditions': len(assertions), 'source_reached_conditions': len(common + CHECKS),
                'derived_guard_conditions': len(DERIVED)}
    (args.output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(args.output, len(assertions), flush=True)


if __name__ == '__main__':
    main()
