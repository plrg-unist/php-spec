"""Emit genuine array snapshot, COW and completed-CV owner checks."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

from array_reference_notice_review_cases import CASES
from reference_send_notice_review_state import PREFIX


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    report = json.loads((args.raw / 'report.json').read_text())
    assert report['all_pass'] and report['mode'] == 'SL'
    assert report['source_agreements'] == 3
    rows = {row['id']: row for row in report['records']}
    assert rows.keys() == CASES.keys()
    args.output.mkdir(parents=True, exist_ok=True)
    records = []

    def emit(case, stages, checks):
        row = rows[case]
        source = Path(row['source'])
        assert source.read_bytes() == CASES[case]
        assert hashlib.sha256(source.read_bytes()).hexdigest() == row['source_sha256']
        checked = json.loads((args.raw / case / 'checked.json').read_text())
        assert checked['ok'] and checked['fixture']
        stage_text = ''.join(f'def $rsn_stage(S, {index}) = true\n' +
                             ''.join('  -- if ' + c + '\n' for c in conditions)
                             for index, conditions in stages.items())
        stage_text += 'def $rsn_stage(S, n_stage) = false -- otherwise\n'
        filename = base64.b64encode(bytes(source)).decode()
        common = ['S_initial = $php_run(' + checked['fixture'] + ', 0, ' + json.dumps(filename) + ')',
                  'S_initial.COMPLETION = BUDGET', 'S_start = S_initial[.COMPLETION = NORMAL]']
        assertions = common + checks
        path = args.output / (case + '.watsup')
        path.write_text(PREFIX + stage_text + '\ndec $main() : bool\ndef $main() = true\n' +
                        ''.join('  -- if ' + c + '\n' for c in assertions))
        records.append({'id': case, 'fixture': str(path.resolve()),
                        'fixture_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                        'assertions': len(assertions), 'source_reached_conditions': len(assertions),
                        'derived_guard_conditions': 0, 'mode': 'AL'})

    stages = {
        0: ['S.TODO = (NAMED_SEND pcalltarget eps 0 pnamedargs porigin? z) :: ptask_tail*',
            'S.RESULT = KNOWN (PARRAY n)', '$rsn_outputs(S.EVENTS) = $ptascii("P;")'],
        1: ['S.TODO = (NAMED_ARGS pcalltarget eps 1 pnamedargs porigin? z) :: ptask_tail*',
            '$rsn_outputs(S.EVENTS) = $ptascii("P;H;")'],
        2: ['S.TODO = ACQUIRE_CALL :: ptask_tail*', 'S.RESULT = REFERENCE n',
            '$rsn_outputs(S.EVENTS) = $ptascii("P;H;F:5;")'],
    }
    checks = r'''
S = $rsn_find(S_start, 1000, 0)
$rsn_stage(S, 0)
S.TODO = (NAMED_SEND pcalltarget eps 0 pnamedargs (porigin_call) z_call) :: ptask_tail*
S.RESULT = KNOWN (PARRAY n_old)
$lookup(S.ENV, $ptascii("source")) = (n_source)
$lookup(S.ENV, $ptascii("copy")) = (n_copy)
n_source =/= n_copy
S.STORE[n_source] = DEFINED (PARRAY n_old)
S.STORE[n_copy] = DEFINED (PARRAY n_old)
S.ARRAYS[n_old].ITEMS = [ENTRY (KSTRING ($ptascii("k"))) (DIRECT (PINT 5))]
$heap_owners($heap_graph(S), HARRAY n_old) = 3
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
S_notice.STORE[n_private] = DEFINED (PARRAY n_old)
$task_nodes(perrorcall.RESUME) = [HCELL n_private]
$node_children(S_notice, HCELL n_private) = [HARRAY n_old]
$heap_owners($heap_graph(S_notice), HCELL n_private) = 1
$heap_owners($heap_graph(S_notice), HARRAY n_old) = 3
S_notice.HELD = S.HELD
S_notice.RESULT = KNOWN PNULL /\ S_notice.BASE = BASE_VALUE (KNOWN PNULL)
$error_call_valid(S_notice, perrorcall) /\ $call_descriptors_valid(S_notice)
$heap_valid($heap_graph(S_notice))
S_resume = $rsn_find(S_notice, 1000, 1)
$rsn_stage(S_resume, 1)
S_resume.TODO = perrorcall.RESUME :: ptask_tail*
$lookup(S_resume.ENV, $ptascii("source")) = eps
~((HCELL n_source) <- S_resume.ALLOCATIONS)
$heap_owners($heap_graph(S_resume), HCELL n_source) = 0
S_resume.STORE[n_copy] = DEFINED (PARRAY n_old)
S_resume.STORE[n_private] = DEFINED (PARRAY n_old)
S_resume.ARRAYS[n_old].ITEMS = [ENTRY (KSTRING ($ptascii("k"))) (DIRECT (PINT 5))]
$heap_owners($heap_graph(S_resume), HARRAY n_old) = 2
$heap_owners($heap_graph(S_resume), HCELL n_private) = 1
$call_descriptors_valid(S_resume) /\ $heap_valid($heap_graph(S_resume))
S_returned = $rsn_find(S_resume, 1000, 2)
$rsn_stage(S_returned, 2)
S_returned.RESULT = REFERENCE n_private
S_returned.STORE[n_private] = DEFINED (PARRAY n_new)
n_new =/= n_old
S_returned.ARRAYS[n_new].ITEMS = [ENTRY (KSTRING ($ptascii("k"))) (DIRECT (PINT 15))]
S_returned.ARRAYS[n_old].ITEMS = [ENTRY (KSTRING ($ptascii("k"))) (DIRECT (PINT 5))]
$heap_owners($heap_graph(S_returned), HCELL n_private) = 1
$heap_owners($heap_graph(S_returned), HARRAY n_old) = 1
$heap_owners($heap_graph(S_returned), HARRAY n_new) = 1
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
$rsn_outputs(S_full.EVENTS) = $ptascii("P;H;F:5;R:115:5:1;")
$rsn_diagnostics(S_full.EVENTS) = eps
$lookup(S_full.ENV, $ptascii("r")) = (n_private)
S_full.STORE[n_private] = DEFINED (PARRAY n_new)
S_full.ARRAYS[n_new].ITEMS = [ENTRY (KSTRING ($ptascii("k"))) (DIRECT (PINT 115))]
S_full.ARRAYS[n_old].ITEMS = [ENTRY (KSTRING ($ptascii("k"))) (DIRECT (PINT 5))]
$heap_owners($heap_graph(S_full), HCELL n_private) = 1
$heap_owners($heap_graph(S_full), HARRAY n_new) = 1
$heap_owners($heap_graph(S_full), HARRAY n_old) = 1
S_full.CURRENT = eps /\ S_full.FRAMES = eps /\ S_full.TODO = eps
S_full.HELD = eps /\ S_full.RETIREDOWNERS = eps
$call_descriptors_valid(S_full) /\ $heap_valid($heap_graph(S_full))
'''.strip().splitlines()
    emit('named-array-snapshot-cow', stages, checks)

    stages = {
        0: ['S.CURRENT = (pcallcontext)', 'pcallcontext.NAME = $ptascii("make")',
            'S.TODO = (RETURN_UNWIND (KNOWN (PARRAY n)) porigin?) :: ptask_tail*'],
        1: ['S.TODO = (NAMED_SEND pcalltarget eps 0 pnamedargs porigin? z) :: ptask_tail*',
            'S.RESULT = KNOWN (PARRAY n)'],
        2: ['S.TODO = (NAMED_ARGS pcalltarget eps 1 pnamedargs porigin? z) :: ptask_tail*',
            '$rsn_outputs(S.EVENTS) = $ptascii("P:7;H;")'],
    }
    checks = r'''
S_producer = $rsn_find(S_start, 1000, 0)
$rsn_stage(S_producer, 0)
$lookup(S_producer.ENV, $ptascii("slot")) = (n_original)
$heap_owners($heap_graph(S_producer), HCELL n_original) = 3
$call_descriptors_valid(S_producer) /\ $heap_valid($heap_graph(S_producer))
S = $rsn_find(S_producer, 1000, 1)
$rsn_stage(S, 1)
S.TODO = (NAMED_SEND pcalltarget eps 0 pnamedargs (porigin_call) z_call) :: ptask_tail*
S.RESULT = KNOWN (PARRAY n_snapshot)
$lookup(S.ENV, $ptascii("input")) = (n_original)
$lookup(S.ENV, $ptascii("keep")) = (n_original)
S.STORE[n_original] = DEFINED (PARRAY n_snapshot)
S.ARRAYS[n_snapshot].ITEMS = [ENTRY (KSTRING ($ptascii("k"))) (DIRECT (PINT 8))]
$heap_owners($heap_graph(S), HCELL n_original) = 2
$heap_owners($heap_graph(S), HARRAY n_snapshot) = 2
S.CURRENT = eps /\ S.FRAMES = eps
$named_reference_notice_pending(S)
$named_origin(S, (porigin_call), 0) = (porigin_producer)
$named_expression($named_source(S, (porigin_call), 0)) = NExprFuncCall phpType19 (SEQUENCE phpType7*) metadata_call
phpType7* = [NArg ABSENT (NExprVariable (BYTES text_input) metadata_input) (BOOLEAN false) (BOOLEAN false) metadata_arg]
$call_descriptors_valid(S) /\ $heap_valid($heap_graph(S))
n_private = |S.STORE|
n_private =/= n_original
S_step = $drive(S, 1)
S_step.COMPLETION = BUDGET
S_notice = S_step[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
perrorcall.RESUME = NAMED_ARGS pcalltarget eps 1 pnamedargs_after (porigin_call) z_call
pnamedargs_after.SLOTS = [NAMED_SENT (REFERENCE n_private)]
S_notice.STORE[n_private] = DEFINED (PARRAY n_snapshot)
$heap_owners($heap_graph(S_notice), HCELL n_private) = 1
$heap_owners($heap_graph(S_notice), HARRAY n_snapshot) = 2
$error_call_valid(S_notice, perrorcall) /\ $call_descriptors_valid(S_notice)
$heap_valid($heap_graph(S_notice))
S_resume = $rsn_find(S_notice, 1000, 2)
$rsn_stage(S_resume, 2)
S_resume.TODO = perrorcall.RESUME :: ptask_tail*
$lookup(S_resume.ENV, $ptascii("input")) = eps
$lookup(S_resume.ENV, $ptascii("keep")) = (n_original)
S_resume.STORE[n_original] = DEFINED (PARRAY n_mutated)
n_mutated =/= n_snapshot
S_resume.ARRAYS[n_mutated].ITEMS = [ENTRY (KSTRING ($ptascii("k"))) (DIRECT (PINT 40))]
S_resume.STORE[n_private] = DEFINED (PARRAY n_snapshot)
S_resume.ARRAYS[n_snapshot].ITEMS = [ENTRY (KSTRING ($ptascii("k"))) (DIRECT (PINT 8))]
$heap_owners($heap_graph(S_resume), HCELL n_original) = 1
$heap_owners($heap_graph(S_resume), HCELL n_private) = 1
$heap_owners($heap_graph(S_resume), HARRAY n_mutated) = 1
$heap_owners($heap_graph(S_resume), HARRAY n_snapshot) = 1
$named_reference_notice_source(S_resume, pcalltarget, 0, (porigin_call))
$error_call_valid(S_resume, perrorcall) /\ $call_descriptors_valid(S_resume)
$heap_valid($heap_graph(S_resume))
'''.strip().splitlines()
    emit('named-array-cv-producer-snapshot', stages, checks)
    (args.output / 'manifest.json').write_text(json.dumps({'source_revision': report['revision'],
        'source_mode': 'SL', 'fixture_mode': 'AL', 'records': records}, indent=2) + '\n')
    print(args.output, sum(row['assertions'] for row in records), flush=True)


if __name__ == '__main__':
    main()
