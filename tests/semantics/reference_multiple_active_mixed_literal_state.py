"""Emit source-reached immutable-literal/CV return history fixtures."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
from reference_multiple_active_cv_caught_state import PREFIX, sha
from request_environment_state import request_fixture


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    catalogue = ROOT / 'tests/semantics/reference_multiple_active_mixed_literal_cases.json'
    cases = {row['id']: row for row in json.loads(catalogue.read_text())}
    report_path = args.raw / 'report.json'
    report = json.loads(report_path.read_text())
    assert report['complete'] and report['pins'] == report['pins_after']
    assert report['head_after'] == report['revision'] and report['status_after'] == ''
    rows = {row['id']: row for row in report['records']}
    assert rows.keys() == cases.keys()
    args.output.mkdir(parents=True, exist_ok=True)
    records = []

    def fixture(name, case_id, stages, checks, bad=(), terminal=(), budget=True):
        row, case = rows[case_id], cases[case_id]
        assert row['pass'] and row['model']['status'] == 'normal'
        assert all(row['native'][key] == row['model'][key] for key in ('stdout', 'stderr', 'exit_status'))
        directory = args.raw / case_id
        facts = json.loads((directory / 'request.json').read_text())
        source = Path(base64.b64decode(facts['file']).decode()).read_bytes()
        assert source == case['source'].encode()
        assert hashlib.sha256(source).hexdigest() == row['source_sha256']
        assert base64.b64decode(row['native']['stdout']) == case['stdout'].encode()
        assert base64.b64decode(row['native']['stderr']) == case['stderr'].encode() == b''
        assert row['native']['exit_status'] == case['exit'] == 0
        parsed = json.loads((directory / 'parsed.json').read_text())
        checked = json.loads((directory / 'checked.json').read_text())
        state = json.loads((directory / 'state.json').read_text())
        assert parsed['accepted'] and checked['ok'] and checked['fixture'] and state['ok']
        start = ('$php_request_run(' + checked['fixture'] + ', 0, ' +
                 json.dumps(facts['file']) + ', ' + request_fixture(facts) + ')')
        stage_text = ''.join(f'def $af_stage(S, {index}) = true\n' +
                             ''.join('  -- if ' + condition + '\n' for condition in conditions)
                             for index, conditions in stages.items())
        stage_text += 'def $af_stage(S, n_stage) = false -- otherwise\n'
        assertions = ['S_initial = ' + start, 'S_initial.COMPLETION = BUDGET',
                      'S_start = S_initial[.COMPLETION = NORMAL]',
                      'S = $af_find(S_start, 2000, 0)', 'S.COMPLETION = NORMAL',
                      '$af_stage(S, 0)', '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
        assertions += checks
        for index, mutation in enumerate(bad):
            assertions += [f'S_bad{index} = ' + mutation + '[.COMPLETION = NORMAL]',
                           f'~$call_descriptors_valid(S_bad{index})',
                           f'S_rejected{index} = $drive(S_bad{index}, 0)',
                           f'S_rejected{index}.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"']
        if budget:
            assertions += ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
                           'S_one = $af_resume(S_zero, 1)', 'S_adjacent = $af_resume(S_one, 10000)',
                           'S_frontier = $drive(S, 10001)', 'S_whole = $drive(S_start, 10001)',
                           'S_adjacent = S_frontier', 'S_frontier = S_whole']
        else:
            assertions += ['S_whole = $drive(S, 10001)']
        assertions += ['S_whole.COMPLETION = NORMAL',
                       '$af_outputs(S_whole.EVENTS) = $ptascii(' + json.dumps(case['stdout']) + ')',
                       '$ma_diagnostics(S_whole.EVENTS) = 0', 'S_whole.CURRENT = eps',
                       'S_whole.FRAMES = eps', 'S_whole.TODO = eps', 'S_whole.HELD = eps',
                       'S_whole.RETIREDOWNERS = eps', '$mc_count(S_whole.TODO) = 0',
                       '$reference_notice_count(S_whole.TODO) = 0',
                       '$call_descriptors_valid(S_whole)', '$heap_valid($heap_graph(S_whole))'] + list(terminal)
        path = args.output / (name + '.watsup')
        path.write_text(PREFIX + '\n' + stage_text + '\ndec $main() : bool\ndef $main() = true\n' +
                        ''.join('  -- if ' + condition + '\n' for condition in assertions))
        records.append({'id': name, 'source_id': case_id, 'fixture': str(path.resolve()),
                        'fixture_sha256': sha(path), 'assertions': len(assertions),
                        'public_refusals': len(bad)})

    primary = 'active-finalizer-mixed-literal-cv-histories-local-catch'
    globals = ['S.GLOBALTABLE = (psymboltable)', '$lookup(psymboltable.ENV, $ptascii("x")) = (n_x)',
               '$lookup(psymboltable.ENV, $ptascii("z")) = (n_z)', '$lookup(psymboltable.ENV, $ptascii("y")) = (n_y)',
               'n_x =/= n_z', 'n_x =/= n_y', 'n_z =/= n_y',
               'S.STORE[n_x] = DEFINED pvalue_x', '$string_bytes(pvalue_x) = ($ptascii("old"))',
               'S.STORE[n_z] = DEFINED pvalue_z', '$string_bytes(pvalue_z) = ($ptascii("mid"))',
               '$lookup(S.ENV, $ptascii("z")) = (n_z)', '$lookup(S.ENV, $ptascii("y")) = (n_y)']
    pre = ['S.TODO = (RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y) :: (FINALLY_REF_RETURN porigin_z_owner porigin_z (REFERENCE n_z) z_z) :: (FINALLY_PHASE porigin_z_owner 3) :: (ORIGIN_RETURN porigin_z_restore?) :: (FINALLY_REF_RETURN porigin_o_owner porigin_o (KNOWN pvalue_old) z_o) :: (FINALLY_PHASE porigin_o_owner 3) :: (ORIGIN_RETURN porigin_o_restore?) :: (TYPE_FALLTHROUGH porigin_function) :: (REF_RECHECK porigin_y porigin_first (REFERENCE n_y) z_y) :: eps']
    literal = ['$origin_node(S.SOURCES, porigin_o) = (NStmtReturn (NScalarString (BYTES text_o) metadata_o) metadata_return_o)',
               '$base64(text_o) = $ptascii("old")', 'pvalue_old = PSTRING_CARRIER INTERNED_STRING ($ptascii("old"))',
               'prefreturncursor_o = { OWNER porigin_o_owner, SOURCE porigin_o, LINE z_o, OUTER porigin_o_restore? }',
               '$ref_return_cursor_literal(S, prefreturncursor_o) = (pvalue_old)',
               '$ref_return_pair_outer_operand(S, prefreturncursor_o, KNOWN pvalue_old)',
               '$operand_nodes(KNOWN pvalue_old) = eps',
               '$task_nodes(FINALLY_REF_RETURN porigin_o_owner porigin_o (KNOWN pvalue_old) z_o) = eps',
               '~((HCELL n_x) <- $tasks_nodes(S.TODO))', '$reference_notice_count(S.TODO) = 0']
    terminal_pair = ['S.TODO = (RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y) :: (REF_RETURN_PAIR prefreturncursor_z prefreturncursor_o porigin_y z_y) :: (REF_RECHECK porigin_y porigin_first (REFERENCE n_y) z_y) :: eps']
    capture = pre + globals + literal + [
        '$af_outputs(S.EVENTS) = $ptascii("O;P;M;P;I1;P;")', '~$destructor_operational(S)',
        '$origin_node(S.SOURCES, porigin_z) = (NStmtReturn (NExprVariable (BYTES text_z) metadata_z) metadata_return_z)',
        '$base64(text_z) = $ptascii("z")',
        '$origin_node(S.SOURCES, porigin_y) = (NStmtReturn (NExprVariable (BYTES text_y) metadata_y) metadata_return_y)',
        '$base64(text_y) = $ptascii("y")', 'z_o = 4', 'z_z = 4', 'z_y = 4',
        'prefreturncursor_z = { OWNER porigin_z_owner, SOURCE porigin_z, LINE z_z, OUTER porigin_z_restore? }',
        '$ref_return_pair_site(S, prefreturncursor_z, prefreturncursor_o, porigin_y, z_y)',
        'S.STORE[n_y] = DEFINED (POBJECT n_y_object)',
        '$heap_owners($heap_graph(S), HCELL n_z) = 3',
        'S_partial = $drive_steps(S, 1)', 'S_partial.COMPLETION = BUDGET',
        'S_partial.TODO = (RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y) :: (FINALLY_REF_RETURN porigin_o_owner porigin_o (KNOWN pvalue_old) z_o) :: (FINALLY_PHASE porigin_o_owner 3) :: (ORIGIN_RETURN porigin_o_restore?) :: (TYPE_FALLTHROUGH porigin_function) :: (REF_RETURN_PAIR_PENDING prefreturncursor_z prefreturncursor_o porigin_y z_y) :: (REF_RECHECK porigin_y porigin_first (REFERENCE n_y) z_y) :: eps',
        '$ref_return_pair_pending_valid(S_partial, prefreturncursor_z, prefreturncursor_o, porigin_y, z_y)',
        '$task_nodes(REF_RETURN_PAIR_PENDING prefreturncursor_z prefreturncursor_o porigin_y z_y) = eps',
        '$reference_notice_count(S_partial.TODO) = 0', '~((HCELL n_z) <- $tasks_nodes(S_partial.TODO))',
        '~((HCELL n_x) <- $tasks_nodes(S_partial.TODO))', '$heap_owners($heap_graph(S_partial), HCELL n_z) = 2',
        'S_partial.STORE = S.STORE', 'S_partial.EVENTS = S.EVENTS', 'S_partial.FRAMES = S.FRAMES',
        '$call_descriptors_valid(S_partial)', '$heap_valid($heap_graph(S_partial))',
        'S_pair = $drive_steps(S_partial[.COMPLETION = NORMAL], 1)', 'S_pair.COMPLETION = BUDGET',
        'S_pair.TODO = [RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y, TYPE_FALLTHROUGH porigin_function, REF_RETURN_PAIR prefreturncursor_z prefreturncursor_o porigin_y z_y, REF_RECHECK porigin_y porigin_first (REFERENCE n_y) z_y]',
        '$ref_return_pair_valid(S_pair, prefreturncursor_z, prefreturncursor_o, porigin_y, z_y)',
        '$task_nodes(REF_RETURN_PAIR prefreturncursor_z prefreturncursor_o porigin_y z_y) = eps',
        '$reference_notice_count(S_pair.TODO) = 0', '~((HCELL n_z) <- $tasks_nodes(S_pair.TODO))',
        '~((HCELL n_x) <- $tasks_nodes(S_pair.TODO))',
        'S_pair.STORE = S.STORE', 'S_pair.EVENTS = S.EVENTS', 'S_pair.FRAMES = S.FRAMES',
        '$call_descriptors_valid(S_pair)', '$heap_valid($heap_graph(S_pair))',
        'S_terminal = $af_find(S_pair, 2000, 1)', '$af_stage(S_terminal, 1)',
        'S_error = $drive_steps(S_terminal, 1)', 'S_error.COMPLETION = BUDGET',
        'S_error.TODO = [THROW_SEARCH n_error, REF_REPLAY_TWO porigin_y (REFERENCE n_y) z_y prefowner* prefreturncursor_z prefreturncursor_o]',
        '$throwable_live(S_error, n_error)', '$throwable_previous_id(S_error, n_error) = eps',
        '$string_bytes($throwable_field(S_error, n_error, "message")) = ($ptascii("f(): Return value must be of type string, stdClass returned"))',
        '$throwable_field(S_error, n_error, "line") = PINT z_y',
        '$ref_replay_two_valid(S_error, porigin_y, REFERENCE n_y, z_y, prefowner*, prefreturncursor_z, prefreturncursor_o)',
        '$task_nodes(REF_REPLAY_TWO porigin_y (REFERENCE n_y) z_y prefowner* prefreturncursor_z prefreturncursor_o) = [HCELL n_y]',
        '$reference_notice_count(S_error.TODO) = 0', '$call_descriptors_valid(S_error)', '$heap_valid($heap_graph(S_error))',
        'prefowner* = [REPLAY_TRY porigin_first, REPLAY_TRY porigin_catch]',
        '$ref_replay_contexts(S_terminal, porigin_y) = prefowner*',
        '$ref_replay_owners(S_terminal, porigin_y) = porigin_first :: eps',
        '$throwable_try_valid(S_terminal, porigin_catch)',
        '~$finally_present(S_terminal, porigin_catch)',
        'S_expanded = $drive_steps(S_error[.COMPLETION = NORMAL], 1)', 'S_expanded.COMPLETION = BUDGET',
        'S_expanded.TODO = (THROW_SEARCH n_error) :: ($ref_replay_tasks(porigin_y, z_y, prefowner*) ++ $ref_consumed_pair_tasks(prefreturncursor_z, prefreturncursor_o))',
        '$ref_consumed_pair_tail(S_expanded.TODO) = [FINALLY_REF_PAIR prefreturncursor_z prefreturncursor_o, FINALLY_PHASE porigin_z_owner 3, ORIGIN_RETURN porigin_z_restore?, FINALLY_REF_CONSUMED prefreturncursor_o, FINALLY_PHASE porigin_o_owner 3, ORIGIN_RETURN porigin_o_restore?]',
        '$reference_notice_count(S_expanded.TODO) = 0', '$call_descriptors_valid(S_expanded)', '$heap_valid($heap_graph(S_expanded))']
    fixture('mixed-literal-pair-capture-and-y-error', primary, {0: pre, 1: terminal_pair}, capture, bad=[
        'S_partial[.TODO = $af_replace(S_partial.TODO, FINALLY_REF_RETURN porigin_o_owner porigin_o (KNOWN pvalue_old) z_o, [FINALLY_REF_RETURN porigin_o_owner porigin_o (KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("other")))) z_o])]',
        'S_partial[.TODO = $af_replace(S_partial.TODO, FINALLY_REF_RETURN porigin_o_owner porigin_o (KNOWN pvalue_old) z_o, [FINALLY_REF_RETURN porigin_o_owner porigin_y (KNOWN pvalue_old) z_o])]',
        'S_partial[.TODO = $af_replace(S_partial.TODO, FINALLY_REF_RETURN porigin_o_owner porigin_o (KNOWN pvalue_old) z_o, [FINALLY_REF_RETURN porigin_o_owner porigin_o (KNOWN pvalue_old) $(z_o + 1)])]',
        'S_partial[.TODO = S_partial.TODO ++ [REF_RETURN_NOTICE porigin_o z_o REF_NOTICE_VALUE, REF_RETURN_NOTICE porigin_o z_o REF_NOTICE_VALUE]]',
        'S_partial[.TODO = $af_replace(S_partial.TODO, REF_RETURN_PAIR_PENDING prefreturncursor_z prefreturncursor_o porigin_y z_y, [REF_RETURN_PAIR_PENDING prefreturncursor_o prefreturncursor_z porigin_y z_y])]',
    ], terminal=['S_whole.STORE[n_x] = DEFINED pvalue_x', 'S_whole.STORE[n_z] = DEFINED pvalue_z'], budget=False)

    before = ['$af_function(S, $ptascii("f"))',
              'S.TODO = (FINALLY_REF_PAIR prefreturncursor_z prefreturncursor_o) :: ptask_tail*',
              '$af_outputs(S.EVENTS) = $ptascii("O;P;M;P;I1;P;I2;P;C;A;")']
    common = globals + [
        'S.TODO = [FINALLY_REF_PAIR prefreturncursor_z prefreturncursor_o, FINALLY_PHASE porigin_z_owner 3, ORIGIN_RETURN porigin_z_restore?, FINALLY_REF_CONSUMED prefreturncursor_o, FINALLY_PHASE porigin_o_owner 3, ORIGIN_RETURN porigin_o_restore?]',
        'porigin_z_owner = prefreturncursor_z.OWNER', 'porigin_z_restore? = prefreturncursor_z.OUTER',
        'porigin_z = prefreturncursor_z.SOURCE', 'z_z = prefreturncursor_z.LINE', 'z_z = 4',
        'porigin_o_owner = prefreturncursor_o.OWNER', 'porigin_o = prefreturncursor_o.SOURCE',
        'z_o = prefreturncursor_o.LINE', 'z_o = 4', 'porigin_o_restore? = prefreturncursor_o.OUTER',
        '$origin_node(S.SOURCES, porigin_o) = (NStmtReturn (NScalarString (BYTES text_o) metadata_o) metadata_return_o)',
        '$base64(text_o) = $ptascii("old")',
        '$ref_return_cursor_literal(S, prefreturncursor_o) = (PSTRING_CARRIER INTERNED_STRING ($ptascii("old")))',
        'S.STORE[n_y] = DEFINED pvalue_fixed', '$string_bytes(pvalue_fixed) = ($ptascii("fixed"))',
        '$lookup(S.ENV, $ptascii("e")) = (n_e)', 'S.STORE[n_e] = DEFINED (POBJECT n_old)',
        '$throwable_live(S, n_old)', '$throwable_previous_id(S, n_old) = eps',
        '$ref_return_pair_cleared_site(S, prefreturncursor_z, prefreturncursor_o)',
        '~$destructor_operational(S)', '$tasks_nodes(S.TODO) = eps', '$reference_notice_count(S.TODO) = 0']
    cleared = ['S_cleared = $drive_steps(S, 1)', 'S_cleared.COMPLETION = BUDGET',
               'S_cleared.TODO = [RETURN_REF_UNWIND (KNOWN PNULL) z_z true porigin_z, REF_RETURN_PAIR_CLEARED prefreturncursor_z prefreturncursor_o, REF_RECHECK porigin_z porigin_z_owner (KNOWN PNULL) z_z]',
               'S_cleared.ORIGIN = porigin_o_restore?', 'S_cleared.STORE = S.STORE',
               'S_cleared.EVENTS = S.EVENTS', 'S_cleared.FRAMES = S.FRAMES',
               'S_cleared.HELD = S.HELD', 'S_cleared.RETIREDOWNERS = S.RETIREDOWNERS',
               'S_cleared.RESULT = KNOWN PNULL', 'S_cleared.BASE = BASE_VALUE (KNOWN PNULL)',
               '$ref_return_pair_cleared_valid(S_cleared, prefreturncursor_z, prefreturncursor_o)',
               '$tasks_nodes(S_cleared.TODO) = eps', '$reference_notice_count(S_cleared.TODO) = 0',
               '$call_descriptors_valid(S_cleared)', '$heap_valid($heap_graph(S_cleared))']
    fresh = ['S_error = $drive_steps(S_cleared[.COMPLETION = NORMAL], 1)', 'S_error.COMPLETION = BUDGET',
             'S_error.TODO = [THROW_SEARCH n_new, REF_REPLAY_PAIR_CLEARED prefreturncursor_z prefreturncursor_o prefowner*]',
             'n_new =/= n_old', '$throwable_live(S_error, n_new)', '$throwable_previous_id(S_error, n_new) = eps',
             '$string_bytes($throwable_field(S_error, n_new, "message")) = ($ptascii("f(): Return value must be of type string, null returned"))',
             '$throwable_field(S_error, n_new, "line") = PINT z_z',
             '$ref_replay_pair_cleared_valid(S_error, prefreturncursor_z, prefreturncursor_o, prefowner*)',
             '$task_nodes(REF_REPLAY_PAIR_CLEARED prefreturncursor_z prefreturncursor_o prefowner*) = eps',
             'S_error.STORE = S.STORE', 'S_error.EVENTS = S.EVENTS', '$reference_notice_count(S_error.TODO) = 0',
             '$call_descriptors_valid(S_error)', '$heap_valid($heap_graph(S_error))',
             'prefowner* = prefowner_first :: eps', '$ref_owner_origin(prefowner_first) = porigin_z_owner',
             'S_expanded = $drive_steps(S_error[.COMPLETION = NORMAL], 1)', 'S_expanded.COMPLETION = BUDGET',
             'S_expanded.TODO = (THROW_SEARCH n_new) :: ($ref_replay_tasks(porigin_z, z_z, prefowner*) ++ $ref_consumed_tasks(prefreturncursor_o))',
             '$reference_notice_count(S_expanded.TODO) = 0', '$call_descriptors_valid(S_expanded)', '$heap_valid($heap_graph(S_expanded))']
    selected = ['$af_function(S, $ptascii("f"))',
                'S.TODO = [RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y, REF_RECHECK porigin_y porigin_y_owner (REFERENCE n_y) z_y]',
                '$af_outputs(S.EVENTS) = $ptascii("O;P;M;P;I1;P;I2;P;C;A;M;P;I3;P;")']
    assigned = ['$lookup(S.ENV, $ptascii("r")) = (n_r)', '$lookup(S.ENV, $ptascii("y")) = (n_r)',
                'S.STORE[n_r] = DEFINED pvalue_r', '$string_bytes(pvalue_r) = ($ptascii("fixed"))']
    selected_checks = ['S_success = $af_find(S_expanded, 2000, 1)', '$af_stage(S_success, 1)',
                       '$mc_count(S_success.TODO) = 0', '$reference_notice_count(S_success.TODO) = 0',
                       'S_success.STORE[n_x] = DEFINED pvalue_x', 'S_success.STORE[n_z] = DEFINED pvalue_z',
                       '$call_descriptors_valid(S_success)', '$heap_valid($heap_graph(S_success))',
                       'S_returned = $drive_steps(S_success, 1)', 'S_returned.RESULT = REFERENCE n_y',
                       'S_returned.CURRENT = eps', 'S_returned.FRAMES = eps', '$mc_count(S_returned.TODO) = 0',
                       '$reference_notice_count(S_returned.TODO) = 0',
                       'S_r = $af_find(S_returned, 2000, 2)', '$lookup(S_r.ENV, $ptascii("r")) = (n_y)',
                       '$lookup(S_r.ENV, $ptascii("y")) = (n_y)']
    fixture('mixed-literal-cleared-replay-and-selected-y', primary, {0: before, 1: selected, 2: assigned},
            common + cleared + fresh + selected_checks, bad=[
        'S_cleared[.TODO = $af_replace(S_cleared.TODO, REF_RETURN_PAIR_CLEARED prefreturncursor_z prefreturncursor_o, [REF_RETURN_PAIR_CLEARED prefreturncursor_z (prefreturncursor_o[.SOURCE = porigin_z])])]',
        'S_cleared[.TODO = $af_replace(S_cleared.TODO, REF_RETURN_PAIR_CLEARED prefreturncursor_z prefreturncursor_o, [REF_RETURN_PAIR_CLEARED prefreturncursor_z (prefreturncursor_o[.LINE = $(z_o + 1)])])]',
        'S_cleared[.TODO = S_cleared.TODO ++ [REF_RETURN_NOTICE porigin_o z_o REF_NOTICE_VALUE]]',
    ], terminal=['$lookup(S_whole.ENV, $ptascii("r")) = (n_y)', '$lookup(S_whole.ENV, $ptascii("y")) = (n_y)',
                 'S_whole.STORE[n_x] = DEFINED pvalue_x', 'S_whole.STORE[n_z] = DEFINED pvalue_z',
                 'S_whole.STORE[n_y] = DEFINED pvalue_changed', '$string_bytes(pvalue_changed) = ($ptascii("changed"))'])

    saved = ['$af_function(S, $ptascii("ping"))', 'S.FRAMES = pframe :: pframe_tail*',
             '$af_outputs(S.EVENTS) = $ptascii("O;P;M;P;I1;P;I2;P;C;A;M;P;")',
             '$ref_consumed_tail(pframe.TODO) = [FINALLY_REF_CONSUMED prefreturncursor_o, FINALLY_PHASE porigin_o_owner 3, ORIGIN_RETURN porigin_o_restore?]']
    restored = ['$af_function(S, $ptascii("f"))',
                '$af_outputs(S.EVENTS) = $ptascii("O;P;M;P;I1;P;I2;P;C;A;M;P;")', '$ref_consumed_tail(S.TODO) =/= eps']
    fixture('mixed-literal-saved-null-replay-history', primary, {0: saved, 1: restored}, saved[1:] + [
        'S_scope = $constant_frame_scope(S, pframe, pframe_tail*)', '$af_function(S_scope, $ptascii("f"))',
        'porigin_o_owner = prefreturncursor_o.OWNER', 'porigin_o_restore? = prefreturncursor_o.OUTER',
        '$ref_return_cursor_literal(S_scope, prefreturncursor_o) = (PSTRING_CARRIER INTERNED_STRING ($ptascii("old")))',
        '$af_error_finally(pframe.TODO) = (FINALLY_RESUME porigin_z_owner (n_new))',
        '$lookup(S_scope.ENV, $ptascii("e")) = (n_e)', 'S_scope.STORE[n_e] = DEFINED (POBJECT n_old)',
        'n_old =/= n_new', '$throwable_live(S_scope, n_old)', '$throwable_live(S_scope, n_new)',
        '$throwable_previous_id(S_scope, n_new) = eps',
        '$string_bytes($throwable_field(S_scope, n_new, "message")) = ($ptascii("f(): Return value must be of type string, null returned"))',
        '$throwable_field(S_scope, n_new, "line") = PINT 4',
        '$ref_consumed_pair_tail(pframe.TODO) = eps', '$mc_count(pframe.TODO) = 1',
        '$reference_notice_count(pframe.TODO) = 0', '$task_nodes(FINALLY_REF_CONSUMED prefreturncursor_o) = eps',
        '$call_tasks_valid(S_scope, pframe.TODO)',
        'S_restored = $af_find($drive_steps(S, 1), 2000, 1)',
        'S_restored.TODO = pframe.TODO', 'S_restored.ORIGIN = pframe.ORIGIN',
        'S_restored.CURRENT = pframe.CONTEXT', 'S_restored.RETIREDOWNERS = pframe.RETIREDOWNERS',
        '$reference_notice_count(S_restored.TODO) = 0', '$call_descriptors_valid(S_restored)', '$heap_valid($heap_graph(S_restored))',
    ], bad=[
        'S[.FRAMES = pframe[.TODO = $af_replace(pframe.TODO, FINALLY_REF_CONSUMED prefreturncursor_o, [FINALLY_REF_CONSUMED (prefreturncursor_o[.LINE = $(prefreturncursor_o.LINE + 1)])])] :: pframe_tail*]',
        'S[.FRAMES = pframe[.TODO = pframe.TODO ++ [REF_RETURN_NOTICE prefreturncursor_o.SOURCE prefreturncursor_o.LINE REF_NOTICE_VALUE]] :: pframe_tail*]',
    ])

    rethrow = 'active-finalizer-mixed-literal-cv-inner-catch-rethrows'
    escape = ['$af_function(S, $ptascii("f"))', 'S.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
              '$af_outputs(S.EVENTS) = $ptascii("O;P;M;P;I1;P;I2;P;")', '$ref_consumed_pair_tail(S.TODO) =/= eps',
              '$lookup(S.ENV, $ptascii("e")) = (n_e)', 'S.STORE[n_e] = DEFINED (POBJECT n_error)']
    fixture('mixed-literal-error-escape-retires-history', rethrow, {0: escape}, escape[1:] + globals + [
        'S.STORE[n_y] = DEFINED pvalue_fixed', '$string_bytes(pvalue_fixed) = ($ptascii("fixed"))',
        '$ref_consumed_pair_tail(S.TODO) = [FINALLY_REF_PAIR prefreturncursor_z prefreturncursor_o, FINALLY_PHASE porigin_z_owner 3, ORIGIN_RETURN porigin_z_restore?, FINALLY_REF_CONSUMED prefreturncursor_o, FINALLY_PHASE porigin_o_owner 3, ORIGIN_RETURN porigin_o_restore?]',
        'porigin_z_owner = prefreturncursor_z.OWNER', 'porigin_z_restore? = prefreturncursor_z.OUTER',
        'porigin_o_owner = prefreturncursor_o.OWNER', 'porigin_o_restore? = prefreturncursor_o.OUTER',
        '$ref_return_cursor_literal(S, prefreturncursor_o) = (PSTRING_CARRIER INTERNED_STRING ($ptascii("old")))',
        '$throwable_live(S, n_error)', '$throwable_previous_id(S, n_error) = eps',
        '$string_bytes($throwable_field(S, n_error, "message")) = ($ptascii("f(): Return value must be of type string, stdClass returned"))',
        '$reference_notice_count(S.TODO) = 0',
    ], terminal=['S_whole.STORE[n_x] = DEFINED pvalue_x', 'S_whole.STORE[n_z] = DEFINED pvalue_z',
                 'S_whole.STORE[n_y] = DEFINED pvalue_fixed', '$lookup(S_whole.ENV, $ptascii("r")) = eps'])

    succeeds = 'active-finalizer-mixed-literal-cv-inner-y-succeeds'
    success_pair = terminal_pair + ['$af_outputs(S.EVENTS) = $ptascii("O;P;M;P;I1;P;")']
    fixture('mixed-literal-first-y-success-retires-history', succeeds, {0: success_pair}, terminal_pair + globals + [
        'S.STORE[n_y] = DEFINED pvalue_fixed', '$string_bytes(pvalue_fixed) = ($ptascii("fixed"))',
        '$ref_return_cursor_literal(S, prefreturncursor_o) = (PSTRING_CARRIER INTERNED_STRING ($ptascii("old")))',
        '$reference_notice_count(S.TODO) = 0', '$task_nodes(REF_RETURN_PAIR prefreturncursor_z prefreturncursor_o porigin_y z_y) = eps',
        'S_returned = $drive_steps(S, 1)', 'S_returned.RESULT = REFERENCE n_y',
        'S_returned.CURRENT = eps', 'S_returned.FRAMES = eps', '$mc_count(S_returned.TODO) = 0',
        '$reference_notice_count(S_returned.TODO) = 0', '$call_descriptors_valid(S_returned)', '$heap_valid($heap_graph(S_returned))',
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
