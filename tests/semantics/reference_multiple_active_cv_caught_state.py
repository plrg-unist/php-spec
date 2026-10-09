"""Emit genuine caught-middle CV replay and caller-alias frontiers."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
from reference_multiple_active_cv_state import PREFIX, sha
from request_environment_state import request_fixture

PREFIX += r'''
dec $mc_task(ptask) : bool
def $mc_task(REF_RETURN_PAIR_CLEARED prefreturncursor_z prefreturncursor_x) = true
def $mc_task(REF_REPLAY_PAIR_CLEARED prefreturncursor_z prefreturncursor_x prefowner*) = true
def $mc_task(ptask) = true -- if $ma_history_task(ptask)
def $mc_task(ptask) = false -- otherwise
dec $mc_count(ptask*) : nat
def $mc_count(eps) = 0
def $mc_count(ptask :: ptask_tail*) = $(1 + $mc_count(ptask_tail*)) -- if $mc_task(ptask)
def $mc_count(ptask :: ptask_tail*) = $mc_count(ptask_tail*) -- if ~$mc_task(ptask)
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    catalogue = ROOT / 'tests/semantics/reference_multiple_active_cv_caught_cases.json'
    cases = json.loads(catalogue.read_text())
    assert len(cases) == 1
    case = cases[0]
    report_path = args.raw / 'report.json'
    report = json.loads(report_path.read_text())
    assert report['complete'] and report['pins'] == report['pins_after']
    assert report['head_after'] == report['revision'] and report['status_after'] == ''
    assert len(report['records']) == 1
    row = report['records'][0]
    assert row['id'] == case['id'] and row['pass'] and row['model']['status'] == 'normal'
    assert all(row['native'][key] == row['model'][key] for key in ('stdout', 'stderr', 'exit_status'))
    directory = args.raw / case['id']
    facts = json.loads((directory / 'request.json').read_text())
    source = Path(base64.b64decode(facts['file']).decode()).read_bytes()
    assert source == case['source'].encode()
    assert hashlib.sha256(source).hexdigest() == row['source_sha256']
    assert base64.b64decode(row['native']['stdout']) == case['stdout'].encode()
    assert base64.b64decode(row['native']['stderr']) == case['stderr'].encode()
    assert row['native']['exit_status'] == case['exit'] == 0
    parsed = json.loads((directory / 'parsed.json').read_text())
    checked = json.loads((directory / 'checked.json').read_text())
    state = json.loads((directory / 'state.json').read_text())
    assert parsed['accepted'] and checked['ok'] and checked['fixture'] and state['ok']
    start = ('$php_request_run(' + checked['fixture'] + ', 0, ' +
             json.dumps(facts['file']) + ', ' + request_fixture(facts) + ')')
    args.output.mkdir(parents=True, exist_ok=True)
    records = []

    def fixture(name, stages, checks, bad=(), helper=(), terminal=()):
        stage_text = ''.join(f'def $af_stage(S, {index}) = true\n' +
                             ''.join('  -- if ' + condition + '\n' for condition in conditions)
                             for index, conditions in stages.items())
        stage_text += 'def $af_stage(S, n_stage) = false -- otherwise\n'
        assertions = ['S_initial = ' + start, 'S_initial.COMPLETION = BUDGET',
                      'S_start = S_initial[.COMPLETION = NORMAL]',
                      'S = $af_find(S_start, 2000, 0)', 'S.COMPLETION = NORMAL',
                      '$af_stage(S, 0)', '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
        assertions += checks + list(helper)
        for index, mutation in enumerate(bad):
            assertions += [f'S_bad{index} = ' + mutation + '[.COMPLETION = NORMAL]',
                           f'~$call_descriptors_valid(S_bad{index})',
                           f'S_rejected{index} = $drive(S_bad{index}, 0)',
                           f'S_rejected{index}.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"']
        assertions += ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
                       'S_one = $af_resume(S_zero, 1)', 'S_adjacent = $af_resume(S_one, 10000)',
                       'S_frontier = $drive(S, 10001)', 'S_whole = $drive(S_start, 10001)',
                       'S_adjacent = S_frontier', 'S_frontier = S_whole', 'S_whole.COMPLETION = NORMAL',
                       '$af_outputs(S_whole.EVENTS) = $ptascii(' + json.dumps(case['stdout']) + ')',
                       '$ma_diagnostics(S_whole.EVENTS) = 0', 'S_whole.CURRENT = eps',
                       'S_whole.FRAMES = eps', 'S_whole.TODO = eps', 'S_whole.HELD = eps',
                       'S_whole.RETIREDOWNERS = eps', '$mc_count(S_whole.TODO) = 0',
                       '$call_descriptors_valid(S_whole)', '$heap_valid($heap_graph(S_whole))'] + list(terminal)
        path = args.output / (name + '.watsup')
        path.write_text(PREFIX + '\n' + stage_text + '\ndec $main() : bool\ndef $main() = true\n' +
                        ''.join(('  -- ' if c.startswith('PhpStep:') else '  -- if ') + c + '\n' for c in assertions))
        records.append({'id': name, 'source_id': case['id'], 'fixture': str(path.resolve()),
                        'fixture_sha256': sha(path), 'assertions': len(assertions)})

    before = ['$af_function(S, $ptascii("f"))',
              'S.TODO = (FINALLY_REF_PAIR prefreturncursor_z prefreturncursor_x) :: ptask_tail*',
              '$af_outputs(S.EVENTS) = $ptascii("O;P;M;P;I1;P;I2;P;C;A;")']
    common = ['S.GLOBALTABLE = (psymboltable)', '$lookup(psymboltable.ENV, $ptascii("x")) = (n_x)',
              '$lookup(psymboltable.ENV, $ptascii("z")) = (n_z)', '$lookup(psymboltable.ENV, $ptascii("y")) = (n_y)',
              'n_x =/= n_z', 'n_x =/= n_y', 'n_z =/= n_y',
              '$lookup(S.ENV, $ptascii("x")) = (n_x)', '$lookup(S.ENV, $ptascii("z")) = (n_z)',
              '$lookup(S.ENV, $ptascii("y")) = (n_y)',
              'S.STORE[n_x] = DEFINED pvalue_x', '$string_bytes(pvalue_x) = ($ptascii("old"))',
              'S.STORE[n_z] = DEFINED pvalue_z', '$string_bytes(pvalue_z) = ($ptascii("mid"))',
              'S.STORE[n_y] = DEFINED pvalue_y', '$string_bytes(pvalue_y) = ($ptascii("fixed"))',
              '$lookup(S.ENV, $ptascii("e")) = (n_e)', 'S.STORE[n_e] = DEFINED (POBJECT n_old)',
              '$throwable_live(S, n_old)', '$throwable_previous_id(S, n_old) = eps',
              '$string_bytes($throwable_field(S, n_old, "message")) = ($ptascii("f(): Return value must be of type string, stdClass returned"))',
              'S.TODO = (FINALLY_REF_PAIR prefreturncursor_z prefreturncursor_x) :: (FINALLY_PHASE porigin_z_owner 3) :: (ORIGIN_RETURN porigin_z_restore?) :: (FINALLY_REF_CONSUMED prefreturncursor_x) :: (FINALLY_PHASE porigin_x_owner 3) :: (ORIGIN_RETURN porigin_x_restore?) :: eps',
              'porigin_z_owner = prefreturncursor_z.OWNER', 'porigin_z_restore? = prefreturncursor_z.OUTER',
              'porigin_x_owner = prefreturncursor_x.OWNER', 'porigin_x_restore? = prefreturncursor_x.OUTER',
              'porigin_z = prefreturncursor_z.SOURCE', 'z_z = prefreturncursor_z.LINE', 'z_z = 4',
              '$origin_node(S.SOURCES, porigin_z) = (NStmtReturn (NExprVariable (BYTES text_z) metadata_z) metadata_return_z)',
              '$base64(text_z) = $ptascii("z")',
              '$origin_node(S.SOURCES, prefreturncursor_x.SOURCE) = (NStmtReturn (NExprVariable (BYTES text_x) metadata_x) metadata_return_x)',
              '$base64(text_x) = $ptascii("x")', '$ref_return_pair_cleared_site(S, prefreturncursor_z, prefreturncursor_x)',
              '~$destructor_operational(S)', '$tasks_nodes(S.TODO) = eps',
              '$heap_owners($heap_graph(S), HCELL n_x) = 2', '$heap_owners($heap_graph(S), HCELL n_z) = 2']
    cleared = ['S_cleared = $drive_steps(S, 1)', 'S_cleared.COMPLETION = BUDGET',
               'S_cleared.TODO = (RETURN_REF_UNWIND (KNOWN PNULL) z_z true porigin_z) :: (REF_RETURN_PAIR_CLEARED prefreturncursor_z prefreturncursor_x) :: (REF_RECHECK porigin_z porigin_z_owner (KNOWN PNULL) z_z) :: eps',
               'S_cleared.ORIGIN = porigin_x_restore?', 'S_cleared.STORE = S.STORE',
               'S_cleared.OBJECTS = S.OBJECTS', 'S_cleared.EVENTS = S.EVENTS',
               'S_cleared.FRAMES = S.FRAMES', 'S_cleared.CURRENT = S.CURRENT',
               'S_cleared.HELD = S.HELD', 'S_cleared.RETIREDOWNERS = S.RETIREDOWNERS',
               'S_cleared.RESULT = KNOWN PNULL', 'S_cleared.BASE = BASE_VALUE (KNOWN PNULL)',
               '$ref_return_pair_cleared_valid(S_cleared, prefreturncursor_z, prefreturncursor_x)',
               '$task_nodes(REF_RETURN_PAIR_CLEARED prefreturncursor_z prefreturncursor_x) = eps',
               '$tasks_nodes(S_cleared.TODO) = eps',
               '$heap_owners($heap_graph(S_cleared), HCELL n_x) = 2', '$heap_owners($heap_graph(S_cleared), HCELL n_z) = 2',
               '$throwable_live(S_cleared, n_old)', '$call_descriptors_valid(S_cleared)', '$heap_valid($heap_graph(S_cleared))']
    error = ['S_error = $drive_steps(S_cleared[.COMPLETION = NORMAL], 1)', 'S_error.COMPLETION = BUDGET',
             'S_error.TODO = (THROW_SEARCH n_new) :: (REF_REPLAY_PAIR_CLEARED prefreturncursor_z prefreturncursor_x prefowner*) :: eps',
             'n_new =/= n_old', '$throwable_live(S_error, n_new)', '$throwable_previous_id(S_error, n_new) = eps',
             '$string_bytes($throwable_field(S_error, n_new, "message")) = ($ptascii("f(): Return value must be of type string, null returned"))',
             '$throwable_field(S_error, n_new, "line") = PINT z_z',
             '$lookup(S_error.ENV, $ptascii("e")) = (n_e)', 'S_error.STORE[n_e] = DEFINED (POBJECT n_old)',
             '$throwable_live(S_error, n_old)', '$ref_replay_pair_cleared_valid(S_error, prefreturncursor_z, prefreturncursor_x, prefowner*)',
             '$task_nodes(REF_REPLAY_PAIR_CLEARED prefreturncursor_z prefreturncursor_x prefowner*) = eps',
             '~((HCELL n_x) <- $tasks_nodes(S_error.TODO))', '~((HCELL n_z) <- $tasks_nodes(S_error.TODO))',
             'S_error.STORE = S.STORE', 'S_error.EVENTS = S.EVENTS',
             '$call_descriptors_valid(S_error)', '$heap_valid($heap_graph(S_error))',
             'prefowner* = prefowner_first :: eps', '$ref_owner_origin(prefowner_first) = porigin_z_owner',
             'S_expanded = $drive_steps(S_error[.COMPLETION = NORMAL], 1)', 'S_expanded.COMPLETION = BUDGET',
             'S_expanded.TODO = (THROW_SEARCH n_new) :: ($ref_replay_tasks(porigin_z, z_z, prefowner*) ++ $ref_consumed_tasks(prefreturncursor_x))',
             '$ref_consumed_tail(S_expanded.TODO) = [FINALLY_REF_CONSUMED prefreturncursor_x, FINALLY_PHASE porigin_x_owner 3, ORIGIN_RETURN porigin_x_restore?]',
             '$ref_consumed_pair_tail(S_expanded.TODO) = eps', '$call_descriptors_valid(S_expanded)', '$heap_valid($heap_graph(S_expanded))']
    internal = ['S_internal = $finally_leave_ref_return(S, porigin_z_owner, porigin_z, KNOWN PNULL, z_z, true, (FINALLY_PHASE porigin_z_owner 3) :: (ORIGIN_RETURN porigin_z_restore?) :: (FINALLY_REF_CONSUMED prefreturncursor_x) :: (FINALLY_PHASE porigin_x_owner 3) :: (ORIGIN_RETURN porigin_x_restore?) :: eps)',
                'S_internal.TODO = (RETURN_REF_UNWIND (KNOWN PNULL) z_z true porigin_z) :: (FINALLY_REF_CONSUMED prefreturncursor_x) :: (FINALLY_PHASE porigin_x_owner 3) :: (ORIGIN_RETURN porigin_x_restore?) :: (REF_RECHECK porigin_z porigin_z_owner (KNOWN PNULL) z_z) :: eps',
                'S_internal.ORIGIN = porigin_z_restore?', 'S_internal.STORE = S.STORE', 'S_internal.OBJECTS = S.OBJECTS',
                'S_internal.EVENTS = S.EVENTS', 'S_internal.FRAMES = S.FRAMES', '$tasks_nodes(S_internal.TODO) = eps',
                '$heap_owners($heap_graph(S_internal), HCELL n_x) = 2', '$heap_owners($heap_graph(S_internal), HCELL n_z) = 2',
                '~$call_descriptors_valid(S_internal)',
                'S_missing = S_cleared[.TODO = (RETURN_REF_UNWIND (KNOWN PNULL) z_z true porigin_z) :: (REF_RECHECK porigin_z porigin_z_owner (KNOWN PNULL) z_z) :: eps][.COMPLETION = NORMAL]',
                '~$ref_return_pair_cleared_valid(S_missing, prefreturncursor_z, prefreturncursor_x)']
    fixture('caught-pair-cleared-terminal-and-fresh-error', {0: before}, common + cleared + error, helper=internal, bad=[
        'S_cleared[.TODO = $af_replace(S_cleared.TODO, REF_RETURN_PAIR_CLEARED prefreturncursor_z prefreturncursor_x, [REF_RETURN_PAIR_CLEARED prefreturncursor_x prefreturncursor_z])]',
        'S_cleared[.TODO = $af_replace(S_cleared.TODO, REF_RETURN_PAIR_CLEARED prefreturncursor_z prefreturncursor_x, [REF_RETURN_PAIR_CLEARED (prefreturncursor_z[.SOURCE = prefreturncursor_x.SOURCE]) prefreturncursor_x])]',
        'S_cleared[.TODO = $af_replace(S_cleared.TODO, REF_RETURN_PAIR_CLEARED prefreturncursor_z prefreturncursor_x, [REF_RETURN_PAIR_CLEARED prefreturncursor_z (prefreturncursor_x[.LINE = $(prefreturncursor_x.LINE + 1)])])]',
        'S_cleared[.TODO = $af_replace(S_cleared.TODO, REF_RETURN_PAIR_CLEARED prefreturncursor_z prefreturncursor_x, [REF_RETURN_PAIR_CLEARED prefreturncursor_z prefreturncursor_x, REF_RETURN_PAIR_CLEARED prefreturncursor_z prefreturncursor_x])]',
        'S_cleared[.TODO = $af_replace(S_cleared.TODO, REF_RECHECK porigin_z porigin_z_owner (KNOWN PNULL) z_z, [REF_RECHECK porigin_z porigin_x_owner (KNOWN PNULL) z_z])]',
        'S_cleared[.TODO = S_cleared.TODO ++ [FINALLY_PHASE porigin_z_owner 3]]',
        'S_cleared[.TODO = $af_replace(S_cleared.TODO, RETURN_REF_UNWIND (KNOWN PNULL) z_z true porigin_z, [RETURN_REF_UNWIND (KNOWN pvalue_z) z_z true porigin_z])]',
        'S_error[.TODO = [THROW_SEARCH n_new, REF_REPLAY_PAIR_CLEARED prefreturncursor_x prefreturncursor_z prefowner*]]',
        'S_error[.TODO = [THROW_SEARCH n_new, REF_REPLAY_PAIR_CLEARED prefreturncursor_z prefreturncursor_x eps]]',
    ])

    saved = ['$af_function(S, $ptascii("ping"))', 'S.FRAMES = pframe :: pframe_tail*',
             '$af_outputs(S.EVENTS) = $ptascii("O;P;M;P;I1;P;I2;P;C;A;M;P;")',
             '$ref_consumed_tail(pframe.TODO) = [FINALLY_REF_CONSUMED prefreturncursor_x, FINALLY_PHASE porigin_x_owner 3, ORIGIN_RETURN porigin_x_restore?]']
    restored = ['$af_function(S, $ptascii("f"))',
                '$af_outputs(S.EVENTS) = $ptascii("O;P;M;P;I1;P;I2;P;C;A;M;P;")',
                '$ref_consumed_tail(S.TODO) =/= eps']
    saved_checks = ['S.FRAMES = pframe :: pframe_tail*', 'S_scope = $constant_frame_scope(S, pframe, pframe_tail*)',
                    '$af_function(S_scope, $ptascii("f"))',
                    '$ref_consumed_tail(pframe.TODO) = [FINALLY_REF_CONSUMED prefreturncursor_x, FINALLY_PHASE porigin_x_owner 3, ORIGIN_RETURN porigin_x_restore?]',
                    'porigin_x_owner = prefreturncursor_x.OWNER', 'porigin_x_restore? = prefreturncursor_x.OUTER',
                    '$af_error_finally(pframe.TODO) = (FINALLY_RESUME porigin_z_owner (n_new))',
                    '$lookup(S_scope.ENV, $ptascii("e")) = (n_e)', 'S_scope.STORE[n_e] = DEFINED (POBJECT n_old)',
                    'n_old =/= n_new', '$throwable_live(S_scope, n_old)', '$throwable_live(S_scope, n_new)',
                    '$throwable_previous_id(S_scope, n_new) = eps',
                    '$string_bytes($throwable_field(S_scope, n_new, "message")) = ($ptascii("f(): Return value must be of type string, null returned"))',
                    '$throwable_field(S_scope, n_new, "line") = PINT 4',
                    '$string_bytes($throwable_field(S_scope, n_old, "message")) = ($ptascii("f(): Return value must be of type string, stdClass returned"))',
                    '$lookup(S_scope.ENV, $ptascii("x")) = (n_x)', '$lookup(S_scope.ENV, $ptascii("z")) = (n_z)',
                    '$lookup(S_scope.ENV, $ptascii("y")) = (n_y)', 'n_x =/= n_z', 'n_x =/= n_y', 'n_z =/= n_y',
                    '$ref_return_cursor_site(S_scope, prefreturncursor_x)',
                    '$ref_consumed_pair_tail(pframe.TODO) = eps', '$mc_count(pframe.TODO) = 1',
                    '~((HCELL n_x) <- $tasks_nodes(pframe.TODO))', '~((HCELL n_z) <- $tasks_nodes(pframe.TODO))',
                    '$heap_owners($heap_graph(S), HCELL n_x) = 2', '$heap_owners($heap_graph(S), HCELL n_z) = 2',
                    '$call_tasks_valid(S_scope, pframe.TODO)',
                    'S_restored = $af_find($drive_steps(S, 1), 2000, 1)',
                    'S_restored.TODO = pframe.TODO', 'S_restored.ORIGIN = pframe.ORIGIN',
                    'S_restored.CURRENT = pframe.CONTEXT', 'S_restored.RETIREDOWNERS = pframe.RETIREDOWNERS',
                    '$call_descriptors_valid(S_restored)', '$heap_valid($heap_graph(S_restored))']
    fixture('saved-middle-null-error-and-outer-history', {0: saved, 1: restored}, saved_checks, bad=[
        'S[.FRAMES = pframe[.TODO = $af_replace(pframe.TODO, FINALLY_REF_CONSUMED prefreturncursor_x, [FINALLY_REF_CONSUMED (prefreturncursor_x[.LINE = $(prefreturncursor_x.LINE + 1)])])] :: pframe_tail*]',
        'S[.FRAMES = pframe[.TODO = $af_replace(pframe.TODO, FINALLY_PHASE porigin_x_owner 3, [FINALLY_PHASE porigin_x_owner 1])] :: pframe_tail*]',
        'S[.FRAMES = pframe[.TODO = $af_replace(pframe.TODO, FINALLY_REF_CONSUMED prefreturncursor_x, [FINALLY_REF_CONSUMED prefreturncursor_x, FINALLY_REF_CONSUMED prefreturncursor_x])] :: pframe_tail*]',
        'S[.FRAMES = pframe[.TODO = $af_replace(pframe.TODO, FINALLY_RESUME porigin_z_owner (n_new), [FINALLY_RESUME porigin_z_owner eps])] :: pframe_tail*]',
    ])

    successful = ['$af_function(S, $ptascii("f"))',
                  'S.TODO = (RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y) :: (REF_RECHECK porigin_y porigin_y_owner (REFERENCE n_y) z_y) :: eps',
                  '$af_outputs(S.EVENTS) = $ptascii("O;P;M;P;I1;P;I2;P;C;A;M;P;I3;P;")']
    assigned = ['$lookup(S.ENV, $ptascii("r")) = (n_r)', '$lookup(S.ENV, $ptascii("y")) = (n_r)',
                'S.STORE[n_r] = DEFINED pvalue_r', '$string_bytes(pvalue_r) = ($ptascii("fixed"))']
    written = ['$lookup(S.ENV, $ptascii("r")) = (n_r)', '$lookup(S.ENV, $ptascii("y")) = (n_r)',
               'S.STORE[n_r] = DEFINED pvalue_r', '$string_bytes(pvalue_r) = ($ptascii("changed"))']
    fixture('caught-middle-replay-selected-y-and-history-retirement', {0: before, 1: successful, 2: assigned, 3: written}, common + cleared + error + [
        'S_success = $af_find(S_expanded, 2000, 1)', '$af_stage(S_success, 1)',
        'S_success.TODO = (RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y) :: (REF_RECHECK porigin_y porigin_y_owner (REFERENCE n_y) z_y) :: eps',
        'S_success.STORE[n_y] = DEFINED pvalue_fixed', '$string_bytes(pvalue_fixed) = ($ptascii("fixed"))',
        'S_success.STORE[n_x] = DEFINED pvalue_x', 'S_success.STORE[n_z] = DEFINED pvalue_z',
        '$mc_count(S_success.TODO) = 0', '~$destructor_operational(S_success)',
        '$call_descriptors_valid(S_success)', '$heap_valid($heap_graph(S_success))',
        'S_returned = $drive_steps(S_success, 1)', 'S_returned.RESULT = REFERENCE n_y',
        'S_returned.CURRENT = eps', 'S_returned.FRAMES = eps', '$mc_count(S_returned.TODO) = 0',
        '$call_descriptors_valid(S_returned)', '$heap_valid($heap_graph(S_returned))',
        'S_r = $af_find(S_returned, 2000, 2)', '$lookup(S_r.ENV, $ptascii("r")) = (n_y)',
        '$lookup(S_r.ENV, $ptascii("y")) = (n_y)',
        'S_written = $af_find($drive_steps(S_r, 1), 2000, 3)',
        '$lookup(S_written.ENV, $ptascii("r")) = (n_y)', '$lookup(S_written.ENV, $ptascii("y")) = (n_y)',
        'S_written.STORE[n_x] = DEFINED pvalue_x', 'S_written.STORE[n_z] = DEFINED pvalue_z',
        '$call_descriptors_valid(S_written)', '$heap_valid($heap_graph(S_written))',
    ], terminal=['$lookup(S_whole.ENV, $ptascii("r")) = (n_y)', '$lookup(S_whole.ENV, $ptascii("y")) = (n_y)',
                 'S_whole.STORE[n_x] = DEFINED pvalue_x', 'S_whole.STORE[n_z] = DEFINED pvalue_z',
                 'S_whole.STORE[n_y] = DEFINED pvalue_changed', '$string_bytes(pvalue_changed) = ($ptascii("changed"))'])
    manifest = {'source_reports': [{'path': str(report_path.resolve()), 'sha256': sha(report_path), 'revision': report['revision']}],
                'catalogue_sha256': sha(catalogue), 'fixtures': len(records),
                'assertions': sum(row['assertions'] for row in records), 'records': records}
    (args.output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'fixtures': manifest['fixtures'], 'assertions': manifest['assertions']}))


if __name__ == '__main__':
    main()
