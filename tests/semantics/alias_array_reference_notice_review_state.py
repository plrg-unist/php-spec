"""Emit real singleton leaf ownership, COW unwrapping and reference-return checks."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

from alias_array_reference_notice_review_cases import CASES
from reference_send_notice_review_state import PREFIX

STAGES = {
    0: ['S.TODO = (NAMED_SEND pcalltarget eps 0 pnamedargs porigin? z) :: ptask_tail*',
        'S.RESULT = KNOWN (PARRAY n)', '$rsn_outputs(S.EVENTS) = $ptascii("P;")'],
    1: ['S.TODO = (NAMED_ARGS pcalltarget eps 1 pnamedargs porigin? z) :: ptask_tail*',
        '$rsn_outputs(S.EVENTS) = $ptascii("P;H;")'],
    2: ['S.TODO = ACQUIRE_CALL :: ptask_tail*', 'S.RESULT = REFERENCE n',
        '$rsn_outputs(S.EVENTS) = $ptascii("P;H;F:7;")'],
}

CHECKS = r'''
S = $rsn_find(S_start, 1000, 0)
$rsn_stage(S, 0)
S.TODO = (NAMED_SEND pcalltarget eps 0 pnamedargs (porigin_call) z_call) :: ptask_tail*
S.RESULT = KNOWN (PARRAY n_old)
$lookup(S.ENV, $ptascii("x")) = (n_leaf)
$lookup(S.ENV, $ptascii("source")) = (n_source)
$lookup(S.ENV, $ptascii("copy")) = (n_copy)
n_source =/= n_copy /\ n_source =/= n_leaf
S.STORE[n_leaf] = DEFINED (PINT 5)
S.STORE[n_source] = DEFINED (PARRAY n_old)
S.STORE[n_copy] = DEFINED (PARRAY n_old)
S.ARRAYS[n_old].ITEMS = [ENTRY (KSTRING ($ptascii("k"))) (ALIAS n_leaf)]
$call_reference_operand_valid(S, REFERENCE n_leaf)
$heap_owners($heap_graph(S), HARRAY n_old) = 3
$heap_owners($heap_graph(S), HCELL n_leaf) = 2
$heap_count(HCELL n_leaf, S.NATIVEEXCESS) = 0
S.HELD = eps /\ S.BASE = BASE_VALUE (KNOWN PNULL)
$named_reference_notice_pending(S)
$call_descriptors_valid(S) /\ $heap_valid($heap_graph(S))
n_private = |S.STORE|
n_private =/= n_leaf
S_step = $drive(S, 1)
S_step.COMPLETION = BUDGET
S_notice = S_step[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
perrorcall.RESUME = NAMED_ARGS pcalltarget eps 1 pnamedargs_after (porigin_call) z_call
pnamedargs_after.SLOTS = [NAMED_SENT (REFERENCE n_private)]
pnamedargs_after.NAMED = eps
S_notice.STORE[n_private] = DEFINED (PARRAY n_old)
$task_nodes(perrorcall.RESUME) = [HCELL n_private]
$node_children(S_notice, HCELL n_private) = [HARRAY n_old]
$node_children(S_notice, HARRAY n_old) = [HCELL n_leaf]
$heap_owners($heap_graph(S_notice), HCELL n_private) = 1
$heap_owners($heap_graph(S_notice), HARRAY n_old) = 3
$heap_owners($heap_graph(S_notice), HCELL n_leaf) = 2
S_notice.HELD = S.HELD
S_notice.RESULT = KNOWN PNULL /\ S_notice.BASE = BASE_VALUE (KNOWN PNULL)
$error_call_valid(S_notice, perrorcall) /\ $call_descriptors_valid(S_notice)
$heap_valid($heap_graph(S_notice))
S_resume = $rsn_find(S_notice, 1000, 1)
$rsn_stage(S_resume, 1)
S_resume.TODO = perrorcall.RESUME :: ptask_tail*
$lookup(S_resume.ENV, $ptascii("x")) = eps
$lookup(S_resume.ENV, $ptascii("source")) = eps
~((HCELL n_source) <- S_resume.ALLOCATIONS)
(HCELL n_leaf) <- S_resume.ALLOCATIONS
$call_reference_operand_valid(S_resume, REFERENCE n_leaf)
S_resume.STORE[n_leaf] = DEFINED (PINT 7)
S_resume.STORE[n_copy] = DEFINED (PARRAY n_old)
S_resume.STORE[n_private] = DEFINED (PARRAY n_old)
S_resume.ARRAYS[n_old].ITEMS = S.ARRAYS[n_old].ITEMS
$heap_owners($heap_graph(S_resume), HARRAY n_old) = 2
$heap_owners($heap_graph(S_resume), HCELL n_leaf) = 1
$heap_count(HCELL n_leaf, S_resume.NATIVEEXCESS) = 0
$duplicate_item(S_resume, n_old, ALIAS n_leaf) = DIRECT (PINT 7)
$error_call_valid(S_resume, perrorcall) /\ $call_descriptors_valid(S_resume)
$heap_valid($heap_graph(S_resume))
S_returned = $rsn_find(S_resume, 1000, 2)
$rsn_stage(S_returned, 2)
S_returned.RESULT = REFERENCE n_private
S_returned.STORE[n_private] = DEFINED (PARRAY n_new)
n_new =/= n_old
S_returned.ARRAYS[n_new].ITEMS = [ENTRY (KSTRING ($ptascii("k"))) (DIRECT (PINT 17))]
S_returned.ARRAYS[n_old].ITEMS = S.ARRAYS[n_old].ITEMS
S_returned.STORE[n_leaf] = DEFINED (PINT 7)
$node_children(S_returned, HARRAY n_new) = eps
$node_children(S_returned, HARRAY n_old) = [HCELL n_leaf]
$heap_owners($heap_graph(S_returned), HCELL n_private) = 1
$heap_owners($heap_graph(S_returned), HARRAY n_old) = 1
$heap_owners($heap_graph(S_returned), HARRAY n_new) = 1
$heap_owners($heap_graph(S_returned), HCELL n_leaf) = 1
$heap_count(HCELL n_leaf, S_returned.NATIVEEXCESS) = 0
$call_descriptors_valid(S_returned) /\ $heap_valid($heap_graph(S_returned))
S_zero = $drive(S_notice, 0)
S_zero.COMPLETION = BUDGET
S_zero[.COMPLETION = NORMAL] = S_notice
S_one = $rsn_resume(S_zero, 1)
S_one.COMPLETION = BUDGET
S_two = $rsn_resume(S_one, 1)
S_two.COMPLETION = BUDGET
S_direct = $drive(S_notice, 2)
S_two = S_direct
S_full = $drive(S_returned, 5000)
S_full.COMPLETION = NORMAL
$rsn_outputs(S_full.EVENTS) = $ptascii("P;H;F:7;R:117:7:1:1;")
$rsn_diagnostics(S_full.EVENTS) = eps
$lookup(S_full.ENV, $ptascii("r")) = (n_private)
S_full.STORE[n_private] = DEFINED (PARRAY n_new)
S_full.ARRAYS[n_new].ITEMS = [ENTRY (KSTRING ($ptascii("k"))) (DIRECT (PINT 117))]
S_full.ARRAYS[n_old].ITEMS = S.ARRAYS[n_old].ITEMS
S_full.STORE[n_leaf] = DEFINED (PINT 7)
$heap_owners($heap_graph(S_full), HCELL n_private) = 1
$heap_owners($heap_graph(S_full), HARRAY n_new) = 1
$heap_owners($heap_graph(S_full), HARRAY n_old) = 1
$heap_owners($heap_graph(S_full), HCELL n_leaf) = 1
S_full.CURRENT = eps /\ S_full.FRAMES = eps /\ S_full.TODO = eps
S_full.HELD = eps /\ S_full.RETIREDOWNERS = eps
$call_descriptors_valid(S_full) /\ $heap_valid($heap_graph(S_full))
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
    args.output.mkdir(parents=True, exist_ok=True)
    stage_text = ''.join(f'def $rsn_stage(S, {index}) = true\n' +
                         ''.join('  -- if ' + c + '\n' for c in conditions)
                         for index, conditions in STAGES.items())
    stage_text += 'def $rsn_stage(S, n_stage) = false -- otherwise\n'
    filename = base64.b64encode(bytes(source)).decode()
    assertions = ['S_initial = $php_run(' + checked['fixture'] + ', 0, ' + json.dumps(filename) + ')',
                  'S_initial.COMPLETION = BUDGET', 'S_start = S_initial[.COMPLETION = NORMAL]'] + CHECKS
    path = args.output / (row['id'] + '.watsup')
    path.write_text(PREFIX + stage_text + '\ndec $main() : bool\ndef $main() = true\n' +
                    ''.join('  -- if ' + c + '\n' for c in assertions))
    record = {'id': row['id'], 'fixture': str(path.resolve()),
              'fixture_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
              'assertions': len(assertions), 'source_reached_conditions': len(assertions),
              'derived_guard_conditions': 0, 'mode': 'AL'}
    (args.output / 'manifest.json').write_text(json.dumps({'source_revision': report['revision'],
        'source_mode': 'SL', 'fixture_mode': 'AL', 'records': [record]}, indent=2) + '\n')
    print(args.output, len(assertions), flush=True)


if __name__ == '__main__':
    main()
