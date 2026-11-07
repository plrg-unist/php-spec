"""Emit source-reached interned snapshots, string fences and real-cell checks."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

from reference_send_notice_review_state import PREFIX
from string_reference_notice_review_cases import CASES, BOUNDARY_CONTROLS


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = json.loads((args.raw / 'report.json').read_text())
    assert report['all_pass'] and report['mode'] == 'SL'
    assert report['source_agreements'] == 2 and report['expected_unsupported_controls'] == 1
    rows = {row['id']: row for row in report['records']}
    assert rows.keys() == (CASES | BOUNDARY_CONTROLS).keys()
    args.output.mkdir(parents=True, exist_ok=True)
    records = []

    def emit(case, stages, checks, derived=0):
        row = rows[case]
        source = Path(row['source'])
        assert source.read_bytes() == CASES[case]
        assert hashlib.sha256(source.read_bytes()).hexdigest() == row['source_sha256']
        checked = json.loads((args.raw / case / 'checked.json').read_text())
        assert checked['ok'] and checked['fixture']
        text = ''.join(f'def $rsn_stage(S, {index}) = true\n' +
                       ''.join('  -- if ' + condition + '\n' for condition in conditions)
                       for index, conditions in stages.items())
        text += 'def $rsn_stage(S, n_stage) = false -- otherwise\n'
        filename = base64.b64encode(bytes(source)).decode()
        assertions = ['S_initial = $php_run(' + checked['fixture'] + ', 0, ' + json.dumps(filename) + ')',
                      'S_initial.COMPLETION = BUDGET', 'S_start = S_initial[.COMPLETION = NORMAL]'] + checks
        path = args.output / (case + '.watsup')
        path.write_text(PREFIX + text + '\ndec $main() : bool\ndef $main() = true\n' +
                        ''.join('  -- if ' + condition + '\n' for condition in assertions))
        records.append({'id': case, 'fixture': str(path.resolve()),
                        'fixture_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                        'assertions': len(assertions), 'source_reached_conditions': len(assertions) - derived,
                        'derived_guard_conditions': derived, 'mode': 'AL'})

    seed = 'PSTRING_CARRIER INTERNED_STRING ($ptascii("seed"))'
    seen = 'PSTRING_CARRIER INTERNED_STRING ($ptascii("seen"))'
    new = 'PSTRING_CARRIER INTERNED_STRING ($ptascii("new"))'
    alias = 'named-interned-prior-cell'
    stages = {
        0: ['S.TODO = (NAMED_SEND pcalltarget eps 1 pnamedargs porigin? z) :: ptask_tail*',
            'S.RESULT = KNOWN (' + seed + ')'],
        1: ['S.TODO = (RETURN_VALUE z) :: ptask_tail*', 'S.RESULT = KNOWN (PBOOL true)',
            'S.CURRENT = (pcallcontext)', 'pcallcontext.NAME = $ptascii("h")',
            '$rsn_outputs(S.EVENTS) = $ptascii("P;H;")'],
        2: ['S.TODO = (NAMED_ARGS pcalltarget eps 2 pnamedargs porigin? z) :: ptask_tail*',
            '$rsn_outputs(S.EVENTS) = $ptascii("P;H;")'],
        3: ['S.TODO = ACQUIRE_CALL :: ptask_tail*', 'S.RESULT = REFERENCE n',
            '$rsn_outputs(S.EVENTS) = $ptascii("P;H;F:seen-h:seed-f;")'],
    }
    checks = ['S = $rsn_find(S_start, 1000, 0)', '$rsn_stage(S, 0)',
        'S.TODO = (NAMED_SEND pcalltarget eps 1 pnamedargs (porigin_call) z_call) :: ptask_tail*',
        'pnamedargs.SLOTS = [NAMED_SENT (REFERENCE n_kept)]', 'pnamedargs.NAMED = eps',
        '$lookup(S.ENV, $ptascii("head")) = (n_kept)', '$lookup(S.ENV, $ptascii("hold")) = (n_kept)',
        '$lookup(S.ENV, $ptascii("replacement")) = (n_replacement)',
        '$lookup(S.ENV, $ptascii("source")) = (n_source)', 'n_kept =/= n_replacement',
        'S.STORE[n_kept] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("head")))',
        'S.STORE[n_source] = DEFINED (' + seed + ')',
        '$heap_owners($heap_graph(S), HCELL n_kept) = 3', '$named_reference_notice_pending(S)',
        '$parameter_backing_at(S.PARAMETERBACKINGS, n_kept) = eps',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'S_step = $drive_steps(S, 1)', 'S_step.COMPLETION = BUDGET',
        'S_notice = S_step[.COMPLETION = NORMAL]',
        'S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'n_private = |S.STORE|', r'n_private =/= n_kept /\ n_private =/= n_source',
        'perrorcall.RESUME = NAMED_ARGS pcalltarget eps 2 pnamedargs_after (porigin_call) z_call',
        'pnamedargs_after.SLOTS = [NAMED_SENT (REFERENCE n_kept)]',
        'pnamedargs_after.NAMED = [($ptascii("tail"), REFERENCE n_private)]',
        'S_notice.STORE[n_private] = DEFINED (' + seed + ')',
        '$string_carrier_valid(S_notice, ' + seed + ')',
        '$parameter_backing_at(S_notice.PARAMETERBACKINGS, n_private) = eps',
        '$heap_owners($heap_graph(S_notice), HCELL n_private) = 1',
        '$heap_owners($heap_graph(S_notice), HCELL n_kept) = 3',
        '$task_nodes(perrorcall.RESUME) = [HCELL n_kept, HCELL n_private]',
        '$node_children(S_notice, HCELL n_private) = eps',
        '$value_nodes(' + seed + ') = eps', 'S_notice.HELD = S.HELD',
        r'S_notice.RESULT = KNOWN PNULL /\ S_notice.BASE = BASE_VALUE (KNOWN PNULL)',
        '$error_call_valid(S_notice, perrorcall)', '$call_descriptors_valid(S_notice)',
        '$heap_valid($heap_graph(S_notice))',
        '$named_reference_notice_value(PSTRING_CARRIER INTERNED_STRING eps)',
        '~$named_reference_notice_value(PSTRING ($ptascii("seed")))',
        '~$named_reference_notice_value(PSTRING_CARRIER INTERNED_STRING ([0]))',
        '~$named_reference_notice_value(PSTRING_CARRIER INTERNED_STRING ([256]))',
        'S_empty = S_notice[.STORE = $set_cell(S_notice.STORE, n_private, DEFINED (PSTRING_CARRIER INTERNED_STRING eps))]',
        '$named_reference_notice_operand(S_empty, REFERENCE n_private)',
        '$target_function(S_notice, pcalltarget) = (pfunction)',
        'pparameterbacking = {FUNCTION pfunction.ORIGIN, INDEX 0, CELL n_private, LINE 1, VALUE eps}',
        'S_backed = S_empty[.PARAMETERBACKINGS = [pparameterbacking]]',
        '~$named_reference_notice_operand(S_backed, REFERENCE n_private)',
        'S_requested = $string_request(S_notice, $ptascii("seed"))',
        'S_requested.RESULT = KNOWN pvalue_request', '$string_carrier_valid(S_requested, pvalue_request)',
        '~$named_reference_notice_value(pvalue_request)',
        'S_request_cell = S_requested[.RESULT = KNOWN PNULL][.STORE = $set_cell(S_requested.STORE, n_private, DEFINED pvalue_request)]',
        '~$named_reference_notice_operand(S_request_cell, REFERENCE n_private)',
        '~$error_call_valid(S_request_cell, perrorcall)',
        'S_handler = $rsn_find(S_notice, 1000, 1)', '$rsn_stage(S_handler, 1)',
        'S_handler.GLOBALTABLE = (psymboltable)',
        '$lookup(psymboltable.ENV, $ptascii("head")) = (n_replacement)',
        '$lookup(psymboltable.ENV, $ptascii("hold")) = eps',
        'S_handler.STORE[n_kept] = DEFINED (' + seen + ')',
        'S_handler.STORE[n_source] = DEFINED (' + new + ')',
        'S_handler.STORE[n_private] = DEFINED (' + seed + ')',
        '$heap_owners($heap_graph(S_handler), HCELL n_kept) = 1',
        '$heap_owners($heap_graph(S_handler), HCELL n_private) = 1',
        '$call_descriptors_valid(S_handler)', '$heap_valid($heap_graph(S_handler))',
        'S_resume = $rsn_find(S_handler, 1000, 2)', '$rsn_stage(S_resume, 2)',
        'S_resume.TODO = perrorcall.RESUME :: ptask_tail*',
        'S_resume.STORE[n_private] = DEFINED (' + seed + ')',
        'S_resume.STORE[n_kept] = DEFINED (' + seen + ')',
        'S_resume.STRINGDATA = S_notice.STRINGDATA',
        '$call_descriptors_valid(S_resume)', '$heap_valid($heap_graph(S_resume))',
        'S_returned = $rsn_find(S_resume, 1000, 3)', '$rsn_stage(S_returned, 3)',
        'S_returned.RESULT = REFERENCE n_private',
        'S_returned.STORE[n_private] = DEFINED pvalue_tail',
        'pvalue_tail = PSTRING_CARRIER (REQUEST_STRING n_tail) ($ptascii("seed-f"))',
        '$string_carrier_valid(S_returned, pvalue_tail)',
        '$heap_owners($heap_graph(S_returned), HCELL n_private) = 1',
        '~((HCELL n_kept) <- S_returned.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_returned), HCELL n_kept) = 0',
        '$call_descriptors_valid(S_returned)', '$heap_valid($heap_graph(S_returned))',
        'S_zero = $drive(S_notice, 0)', 'S_zero.COMPLETION = BUDGET', 'S_zero.TODO = S_notice.TODO',
        'S_one = $rsn_resume(S_zero, 1)', 'S_two = $rsn_resume(S_one, 1)',
        'S_direct = $drive(S_notice, 2)', 'S_two = S_direct',
        'S_full = $drive(S_returned, 5000)', 'S_full.COMPLETION = NORMAL',
        '$rsn_outputs(S_full.EVENTS) = $ptascii("P;H;F:seen-h:seed-f;R:seed-f-r:root:root:1:new;")',
        '$rsn_diagnostics(S_full.EVENTS) = eps', '$lookup(S_full.ENV, $ptascii("r")) = (n_private)',
        'S_full.STORE[n_private] = DEFINED pvalue_final',
        '$string_bytes(pvalue_final) = ($ptascii("seed-f-r"))', '$string_carrier_valid(S_full, pvalue_final)',
        r'S_full.CURRENT = eps /\ S_full.FRAMES = eps /\ S_full.TODO = eps',
        r'S_full.HELD = eps /\ S_full.RETIREDOWNERS = eps',
        '$call_descriptors_valid(S_full)', '$heap_valid($heap_graph(S_full))']
    first_guard = checks.index('$named_reference_notice_value(PSTRING_CARRIER INTERNED_STRING eps)')
    last_guard = checks.index('~$error_call_valid(S_request_cell, perrorcall)')
    emit(alias, stages, checks, last_guard - first_guard + 1)

    false = 'positional-interned-false-line'
    stages = {0: ['S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*',
                  'S.RESULT = KNOWN (PBOOL false)', '$rsn_outputs(S.EVENTS) = $ptascii("P;H:8;")'],
              1: ['S.TODO = (CALL_ARGS pcalltarget phpType7* 1 poperand* porigin? z) :: ptask_tail*',
                  '$rsn_outputs(S.EVENTS) = $ptascii("P;H:8;")']}
    checks = ['S = $rsn_find(S_start, 1000, 0)', '$rsn_stage(S, 0)',
        'S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = CALL_ARGS pcalltarget phpType7* 1 ([REFERENCE n_private]) (porigin_call) 7',
        'perrorcall.LINE = 8', 'S.STORE[n_private] = DEFINED (' + seed + ')',
        '$heap_owners($heap_graph(S), HCELL n_private) = 1',
        '$rsn_diagnostics(S.EVENTS) = eps', '$error_call_valid(S, perrorcall)',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'S_resume = $rsn_find(S, 1000, 1)', '$rsn_stage(S_resume, 1)',
        'S_resume.TODO = perrorcall.RESUME :: ptask_tail*',
        'S_resume.STORE[n_private] = DEFINED (' + seed + ')',
        '$rsn_diagnostics(S_resume.EVENTS) = [DIAGNOSTIC "Notice" $ptascii("Only variables should be passed by reference") 8]',
        '$call_descriptors_valid(S_resume)', '$heap_valid($heap_graph(S_resume))',
        'S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET', 'S_zero.TODO = S.TODO',
        'S_one = $rsn_resume(S_zero, 1)', 'S_split = $rsn_resume(S_one, 5000)',
        'S_full = $drive(S, 5001)', 'S_split = S_full', 'S_full.COMPLETION = NORMAL',
        '$rsn_outputs(S_full.EVENTS) = $ptascii("P;H:8;T;F:seed-f:9;R:seed-f-r:new;")',
        '$rsn_diagnostics(S_full.EVENTS) = [DIAGNOSTIC "Notice" $ptascii("Only variables should be passed by reference") 8]',
        '$lookup(S_full.ENV, $ptascii("r")) = (n_private)',
        'S_full.STORE[n_private] = DEFINED pvalue_final',
        '$string_bytes(pvalue_final) = ($ptascii("seed-f-r"))', '$string_carrier_valid(S_full, pvalue_final)',
        r'S_full.CURRENT = eps /\ S_full.FRAMES = eps /\ S_full.TODO = eps',
        r'S_full.HELD = eps /\ S_full.RETIREDOWNERS = eps',
        '$call_descriptors_valid(S_full)', '$heap_valid($heap_graph(S_full))']
    emit(false, stages, checks)
    (args.output / 'manifest.json').write_text(json.dumps({'source_revision': report['revision'],
        'source_mode': 'SL', 'fixture_mode': 'AL', 'records': records}, indent=2) + '\n')
    print(args.output, sum(row['assertions'] for row in records), flush=True)


if __name__ == '__main__':
    main()
