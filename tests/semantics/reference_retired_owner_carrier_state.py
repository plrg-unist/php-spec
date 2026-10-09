"""Emit the focused current-parent string-carrier owner bridge from pinned packets."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
from reference_retired_owner_state import PREFIX, HELPERS
from request_environment_state import request_fixture


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    case = 'foreach-return-active-finalizer-inner-catch-saved'
    report_path = args.raw / 'report.json'
    report = json.loads(report_path.read_text())
    assert report['passed'] and report['revision'] == report['head_after']
    assert report['status_after'] == '' and report['pins'] == report['pins_after']
    row = next(row for row in report['records'] if row['id'] == case)
    assert row['coherent_pass'] and row['native_match'] and not row['deliberate_divergence']
    catalogue = json.loads((ROOT / 'tests/semantics/reference_retired_owner_cases.json').read_text())
    original = next(row for row in catalogue['cases'] if row['id'] == case)
    assert hashlib.sha256(original['source'].encode()).hexdigest() == row['source_sha256'] == original['source_sha256']
    expected = original['expected_coherent_stdout'].encode()
    assert base64.b64decode(row['model']['stdout']) == expected
    assert row['model']['status'] == 'normal' and row['model']['stderr'] == '' and row['model']['exit_status'] == 0
    directory = args.raw / case
    parsed = json.loads((directory / 'parsed.json').read_text())
    checked = json.loads((directory / 'checked.json').read_text())
    facts = json.loads((directory / 'request.json').read_text())
    assert parsed['accepted'] and checked['ok'] and checked['fixture']
    initial = '$php_request_run(' + checked['fixture'] + ', 0, ' + json.dumps(facts['file']) + ', ' + request_fixture(facts) + ')'
    stages = {
        0: ['$replay_function(S, $ptascii("f"))',
            'S.TODO = (RETURN_REF_UNWIND poperand z false porigin_return) :: ptask_owner :: ptask_tail*',
            '$retired_capture(S, porigin_return, z, false, ptask_owner, ptask_tail*) = (pretiredowner)'],
        1: ['$replay_function(S, $ptascii("ping"))', 'S.FRAMES = pframe :: pframe_tail*',
            'pframe.RETIREDOWNERS = [pretiredowner]'],
        2: ['$replay_function(S, $ptascii("f"))',
            '$replay_outputs(S.EVENTS) = ' + str(list(b'F;P;'))],
    }
    checks = ['S_initial = ' + initial, 'S_initial.COMPLETION = BUDGET',
        'S_start = S_initial[.COMPLETION = NORMAL]', 'S = $owner_find(S_start, 3000, 0)',
        'S.COMPLETION = NORMAL', '$owner_stage(S, 0)', '$call_descriptors_valid(S)',
        'S.TODO = (RETURN_REF_UNWIND poperand z false porigin_return) :: ptask_owner :: ptask_tail*',
        '$retired_capture(S, porigin_return, z, false, ptask_owner, ptask_tail*) = (pretiredowner)',
        '$lookup(S.ENV, $ptascii("x")) = (n_x)', 'S.STORE[n_x] = DEFINED pvalue_x',
        'pvalue_x = PSTRING_CARRIER INTERNED_STRING $ptascii("s")',
        '$string_bytes(pvalue_x) = ($ptascii("s"))', '$retired_scalar(pvalue_x)',
        '$retired_dense_entries([ENTRY (KINT 0) (DIRECT pvalue_x)], [POSITION (KINT 0) 0], 0)',
        'pretiredowner.FIRSTRETURN = porigin_return', 'pretiredowner.LASTRETURN = porigin_return',
        'pretiredowner.FIRSTLINE = z', 'pretiredowner.LASTLINE = z', 'pretiredowner.POSITION = (n_position)',
        'ptask_owner = FOREACH_NEXT n_iter (HARRAY pretiredowner.ARRAY) statement (pretiredowner.OWNER) z_owner',
        '$iterator_lookup(S.ITERATORS, n_iter) = (ITERATOR n_iter pretiredowner.ARRAY false ([(CURSOR pretiredowner.ARRAY n_position)]))',
        '$task_nodes(ptask_owner) = [HARRAY pretiredowner.ARRAY]',
        '$heap_owners($heap_graph(S), HARRAY pretiredowner.ARRAY) = 4', 'S.RETIREDOWNERS = eps',
        'S_removed = $drive_steps(S, 1)', 'S_removed.RETIREDOWNERS = [pretiredowner]',
        'S_removed.STORE = S.STORE', 'S_removed.ARRAYS = S.ARRAYS',
        '$heap_owners($heap_graph(S_removed), HARRAY pretiredowner.ARRAY) = 3',
        '$iterator_lookup(S_removed.ITERATORS, n_iter) = eps', '$call_descriptors_valid(S_removed)',
        'S_saved = $owner_find(S_removed, 3000, 1)', 'S_saved.FRAMES = pframe :: pframe_tail*',
        'pframe.RETIREDOWNERS = [pretiredowner]', 'S_saved.RETIREDOWNERS = eps',
        'S_scope = $constant_frame_scope(S_saved, pframe, pframe_tail*)',
        '$replay_function(S_scope, $ptascii("f"))', 'S_scope.STORE[n_x] = DEFINED pvalue_x',
        '$retired_current_valid(S_scope)', '$call_tasks_valid(S_scope, pframe.TODO)',
        'S_saved.CURRENT = (pcallcontext)', 'pcallcontext.CALLSITE = pframe.ORIGIN',
        '$call_descriptors_valid(S_saved)', '$heap_valid($heap_graph(S_saved))',
        'S_restored = $owner_find($drive_steps(S_saved, 1), 3000, 2)',
        'S_restored.RETIREDOWNERS = pframe.RETIREDOWNERS',
        'S_restored.STORE[n_x] = DEFINED pvalue_x', '$retired_current_valid(S_restored)',
        '$call_descriptors_valid(S_restored)',
        'S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_adjacent = $replay_resume($replay_resume(S_zero, 1), 10000)',
        'S_frontier = $drive(S, 10001)', 'S_whole = $drive(S_start, 10001)',
        'S_adjacent = S_frontier', 'S_frontier = S_whole', 'S_whole.COMPLETION = NORMAL',
        '$replay_outputs(S_whole.EVENTS) = ' + str(list(expected)),
        '$lookup(S_whole.ENV, $ptascii("a")) = (n_x)',
        '$lookup(S_whole.ENV, $ptascii("x")) = (n_x)', 'S_whole.STORE[n_x] = DEFINED pvalue_x',
        'S_whole.CURRENT = eps', 'S_whole.FRAMES = eps', 'S_whole.TODO = eps',
        'S_whole.RETIREDOWNERS = eps', 'S_whole.HELD = eps', 'S_whole.ITERATORS = eps',
        '$owner_errors_dead(S_whole, S_whole.OBJECTS, 0)', '$heap_valid($heap_graph(S_whole))',
        '$call_descriptors_valid(S_whole)']
    stage_text = ''.join('def $owner_stage(S, ' + str(k) + ') = true\n' +
                         ''.join('  -- if ' + check + '\n' for check in conditions)
                         for k, conditions in stages.items())
    stage_text += 'def $owner_stage(S, n_stage) = false -- otherwise\n'
    args.output.mkdir(parents=True, exist_ok=True)
    fixture = args.output / 'retired-owner-string-carrier.watsup'
    fixture.write_text(PREFIX + HELPERS + '\n' + stage_text + '\ndec $main() : bool\ndef $main() = true\n' +
                       ''.join('  -- if ' + check + '\n' for check in checks))
    record = {'source_id': case, 'source_sha256': row['source_sha256'],
              'source_report': str(report_path.resolve()), 'fixtures': 1, 'assertions': len(checks),
              'helper_only_dense_entry_checks': 1, 'fixture': str(fixture.resolve()),
              'fixture_sha256': hashlib.sha256(fixture.read_bytes()).hexdigest()}
    (args.output / 'manifest.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record))


if __name__ == '__main__':
    main()
