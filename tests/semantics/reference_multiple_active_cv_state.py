"""Emit source-reached two-history CV return state fixtures."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
from reference_active_finalizer_state import PREFIX, sha
from request_environment_state import request_fixture

PREFIX += r'''
dec $ma_history_head(pstate, ptask*, preqbytes, nat) : bool
def $ma_history_head(S, (FINALLY_REF_RETURN porigin_owner porigin_source (REFERENCE n_cell) z) :: (FINALLY_PHASE porigin_owner 3) :: (ORIGIN_RETURN porigin_restore?) :: ptask_tail*, n_name*, n_cell) = true
  -- if $origin_node(S.SOURCES, porigin_source) = (NStmtReturn (NExprVariable (BYTES text) metadata_variable) metadata_return)
  -- if $base64(text) = n_name*
def $ma_history_head(S, ptask*, n_name*, n_cell) = false -- otherwise
dec $ma_named_history(pstate, ptask*, preqbytes, nat) : bool
def $ma_named_history(S, eps, n_name*, n_cell) = false
def $ma_named_history(S, ptask :: ptask_tail*, n_name*, n_cell) = true
  -- if $ma_history_head(S, ptask :: ptask_tail*, n_name*, n_cell)
def $ma_named_history(S, ptask :: ptask_tail*, n_name*, n_cell) = $ma_named_history(S, ptask_tail*, n_name*, n_cell)
  -- if ~$ma_history_head(S, ptask :: ptask_tail*, n_name*, n_cell)
dec $ma_history_task(ptask) : bool
def $ma_history_task(REF_RETURN_PAIR_PENDING prefreturncursor_inner prefreturncursor_outer porigin_source z) = true
def $ma_history_task(REF_RETURN_PAIR prefreturncursor_inner prefreturncursor_outer porigin_source z) = true
def $ma_history_task(REF_REPLAY_TWO porigin_source poperand z prefowner* prefreturncursor_inner prefreturncursor_outer) = true
def $ma_history_task(FINALLY_REF_PAIR prefreturncursor_inner prefreturncursor_outer) = true
def $ma_history_task(FINALLY_REF_CONSUMED prefreturncursor) = true
def $ma_history_task(ptask) = false -- otherwise
dec $ma_history_count(ptask*) : nat
def $ma_history_count(eps) = 0
def $ma_history_count(ptask :: ptask_tail*) = $(1 + $ma_history_count(ptask_tail*)) -- if $ma_history_task(ptask)
def $ma_history_count(ptask :: ptask_tail*) = $ma_history_count(ptask_tail*) -- if ~$ma_history_task(ptask)
dec $ma_diagnostic(pevent) : bool
def $ma_diagnostic(DIAGNOSTIC text_level ptbytes_message z) = true
def $ma_diagnostic(DIAGNOSTIC_SOURCE n text_level ptbytes_message z) = true
def $ma_diagnostic(pevent) = false -- otherwise
dec $ma_diagnostics(pevent*) : nat
def $ma_diagnostics(eps) = 0
def $ma_diagnostics(pevent :: pevent_tail*) = $(1 + $ma_diagnostics(pevent_tail*)) -- if $ma_diagnostic(pevent)
def $ma_diagnostics(pevent :: pevent_tail*) = $ma_diagnostics(pevent_tail*) -- if ~$ma_diagnostic(pevent)
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw', type=Path, action='append', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    catalogue = ROOT / 'tests/semantics/reference_multiple_active_cv_cases.json'
    cases = {row['id']: row for row in json.loads(catalogue.read_text())}
    rows, reports = {}, []
    for raw in args.raw:
        path = raw / 'report.json'
        report = json.loads(path.read_text())
        assert report['complete'] and report['pins'] == report['pins_after']
        assert report['head_after'] == report['revision'] and report['status_after'] == ''
        reports.append({'path': str(path.resolve()), 'sha256': sha(path),
                        'revision': report['revision']})
        for row in report['records']:
            assert row['id'] not in rows and row['pass'] and row['model']['status'] == 'normal'
            assert all(row['native'][key] == row['model'][key]
                       for key in ('stdout', 'stderr', 'exit_status'))
            rows[row['id']] = row, raw
    assert rows.keys() == cases.keys()
    args.output.mkdir(parents=True, exist_ok=True)
    records = []

    def fixture(name, case, stages, checks, bad=(), terminal=()):
        row, raw = rows[case]
        directory = raw / case
        facts = json.loads((directory / 'request.json').read_text())
        source = Path(base64.b64decode(facts['file']).decode()).read_bytes()
        assert source == cases[case]['source'].encode()
        assert hashlib.sha256(source).hexdigest() == row['source_sha256']
        assert base64.b64decode(row['native']['stdout']) == cases[case]['stdout'].encode()
        assert base64.b64decode(row['native']['stderr']) == cases[case]['stderr'].encode()
        assert row['native']['exit_status'] == cases[case]['exit'] == 0
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
        assertions += ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
                       'S_one = $af_resume(S_zero, 1)', 'S_adjacent = $af_resume(S_one, 10000)',
                       'S_frontier = $drive(S, 10001)', 'S_whole = $drive(S_start, 10001)',
                       'S_adjacent = S_frontier', 'S_frontier = S_whole',
                       'S_whole.COMPLETION = NORMAL',
                       '$af_outputs(S_whole.EVENTS) = $ptascii(' + json.dumps(cases[case]['stdout']) + ')',
                       '$ma_diagnostics(S_whole.EVENTS) = 0',
                       'S_whole.CURRENT = eps', 'S_whole.FRAMES = eps', 'S_whole.TODO = eps',
                       'S_whole.HELD = eps', 'S_whole.RETIREDOWNERS = eps',
                       '$ma_history_count(S_whole.TODO) = 0', '$heap_valid($heap_graph(S_whole))', '$call_descriptors_valid(S_whole)'] + list(terminal)
        path = args.output / (name + '.watsup')
        path.write_text(PREFIX + '\n' + stage_text + '\ndec $main() : bool\ndef $main() = true\n' +
                        ''.join(('  -- ' if condition.startswith('PhpStep:') else '  -- if ') + condition + '\n' for condition in assertions))
        records.append({'id': name, 'source_id': case, 'fixture': str(path.resolve()),
                        'fixture_sha256': sha(path), 'assertions': len(assertions)})

    abrupt = 'active-finalizer-two-consumed-cv-histories'
    normal = 'active-finalizer-two-consumed-cv-histories-normal'
    globals = ['S.GLOBALTABLE = (psymboltable)', '$lookup(psymboltable.ENV, $ptascii("x")) = (n_x)',
               '$lookup(psymboltable.ENV, $ptascii("z")) = (n_z)', '$lookup(psymboltable.ENV, $ptascii("y")) = (n_y)',
               'n_x =/= n_z', 'n_x =/= n_y', 'n_z =/= n_y',
               'S.STORE[n_x] = DEFINED pvalue_x', '$string_bytes(pvalue_x) = ($ptascii("old"))',
               'S.STORE[n_z] = DEFINED pvalue_z', '$string_bytes(pvalue_z) = ($ptascii("mid"))']
    pre = ['S.TODO = (RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y) :: (FINALLY_REF_RETURN porigin_z_owner porigin_z (REFERENCE n_z) z_z) :: (FINALLY_PHASE porigin_z_owner 3) :: (ORIGIN_RETURN porigin_z_restore?) :: (FINALLY_REF_RETURN porigin_x_owner porigin_x (REFERENCE n_x) z_x) :: (FINALLY_PHASE porigin_x_owner 3) :: (ORIGIN_RETURN porigin_x_restore?) :: (TYPE_FALLTHROUGH porigin_function) :: (REF_RECHECK porigin_y porigin_first (REFERENCE n_y) z_y) :: eps']
    site = ['$origin_node(S.SOURCES, porigin_x) = (NStmtReturn (NExprVariable (BYTES text_x) metadata_x) metadata_return_x)',
            '$base64(text_x) = $ptascii("x")',
            '$origin_node(S.SOURCES, porigin_z) = (NStmtReturn (NExprVariable (BYTES text_z) metadata_z) metadata_return_z)',
            '$base64(text_z) = $ptascii("z")',
            '$origin_node(S.SOURCES, porigin_y) = (NStmtReturn (NExprVariable (BYTES text_y) metadata_y) metadata_return_y)',
            '$base64(text_y) = $ptascii("y")', 'z_x = 4', 'z_z = 4', 'z_y = 4',
            '$lookup(S.ENV, $ptascii("x")) = (n_x)', '$lookup(S.ENV, $ptascii("z")) = (n_z)', '$lookup(S.ENV, $ptascii("y")) = (n_y)',
            'prefreturncursor_z = { OWNER porigin_z_owner, SOURCE porigin_z, LINE z_z, OUTER porigin_z_restore? }',
            'prefreturncursor_x = { OWNER porigin_x_owner, SOURCE porigin_x, LINE z_x, OUTER porigin_x_restore? }',
            '$ref_return_pair_site(S, prefreturncursor_z, prefreturncursor_x, porigin_y, z_y)',
            '~$ref_return_cursor_single(S, porigin_z_owner, porigin_y)', '~$ref_return_cursor_single(S, porigin_x_owner, porigin_y)',
            '~$ref_return_cursor_clear(S, S.TODO)',
            '$ma_named_history(S, S.TODO, $ptascii("x"), n_x)', '$ma_named_history(S, S.TODO, $ptascii("z"), n_z)',
            '$heap_owners($heap_graph(S), HCELL n_x) = 3', '$heap_owners($heap_graph(S), HCELL n_z) = 3']
    terminal_pair = ['S.TODO = (RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y) :: (REF_RETURN_PAIR prefreturncursor_z prefreturncursor_x porigin_y z_y) :: (REF_RECHECK porigin_y porigin_first (REFERENCE n_y) z_y) :: eps']
    capture_checks = pre + site + globals + ['~$destructor_operational(S)',
        'S_partial = $drive_steps(S, 1)', 'S_partial.COMPLETION = BUDGET',
        'S_partial.TODO = (RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y) :: (FINALLY_REF_RETURN porigin_x_owner porigin_x (REFERENCE n_x) z_x) :: (FINALLY_PHASE porigin_x_owner 3) :: (ORIGIN_RETURN porigin_x_restore?) :: (TYPE_FALLTHROUGH porigin_function) :: (REF_RETURN_PAIR_PENDING prefreturncursor_z prefreturncursor_x porigin_y z_y) :: (REF_RECHECK porigin_y porigin_first (REFERENCE n_y) z_y) :: eps',
        '$ref_return_pair_pending_valid(S_partial, prefreturncursor_z, prefreturncursor_x, porigin_y, z_y)',
        '$task_nodes(REF_RETURN_PAIR_PENDING prefreturncursor_z prefreturncursor_x porigin_y z_y) = eps',
        '$ma_named_history(S_partial, S_partial.TODO, $ptascii("x"), n_x)',
        '~$ma_named_history(S_partial, S_partial.TODO, $ptascii("z"), n_z)',
        '(HCELL n_x) <- $tasks_nodes(S_partial.TODO)', '~((HCELL n_z) <- $tasks_nodes(S_partial.TODO))',
        '$heap_owners($heap_graph(S_partial), HCELL n_x) = 3', '$heap_owners($heap_graph(S_partial), HCELL n_z) = 2',
        '$heap_owners($heap_graph(S_partial), HCELL n_y) = $heap_owners($heap_graph(S), HCELL n_y)',
        'S_partial.STORE = S.STORE', 'S_partial.HELD = S.HELD', 'S_partial.FRAMES = S.FRAMES',
        '$call_descriptors_valid(S_partial)', '$heap_valid($heap_graph(S_partial))',
        'S_pair = $drive_steps(S_partial[.COMPLETION = NORMAL], 1)', 'S_pair.COMPLETION = BUDGET',
        'S_pair.TODO = [RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y, TYPE_FALLTHROUGH porigin_function, REF_RETURN_PAIR prefreturncursor_z prefreturncursor_x porigin_y z_y, REF_RECHECK porigin_y porigin_first (REFERENCE n_y) z_y]',
        '$ref_return_pair_valid(S_pair, prefreturncursor_z, prefreturncursor_x, porigin_y, z_y)',
        '$task_nodes(REF_RETURN_PAIR prefreturncursor_z prefreturncursor_x porigin_y z_y) = eps',
        '~((HCELL n_x) <- $tasks_nodes(S_pair.TODO))', '~((HCELL n_z) <- $tasks_nodes(S_pair.TODO))',
        '$heap_owners($heap_graph(S_pair), HCELL n_x) = 2', '$heap_owners($heap_graph(S_pair), HCELL n_z) = 2',
        '$heap_owners($heap_graph(S_pair), HCELL n_y) = $heap_owners($heap_graph(S), HCELL n_y)',
        'S_pair.STORE = S.STORE', 'S_pair.HELD = S.HELD', 'S_pair.FRAMES = S.FRAMES',
        '$call_descriptors_valid(S_pair)', '$heap_valid($heap_graph(S_pair))',
        'S_terminal = $af_find(S_pair, 2000, 1)', '$af_stage(S_terminal, 1)',
    ]
    fixture('ordered-pair-capture-and-error', abrupt, {0: pre, 1: terminal_pair}, capture_checks + [
        '$af_outputs(S.EVENTS) = $ptascii("O;P;M;P;I1;P;")', 'S.STORE[n_y] = DEFINED (POBJECT n_y_object)',
        'S_error = $drive_steps(S_terminal, 1)', 'S_error.COMPLETION = BUDGET',
        'S_error.TODO = [THROW_SEARCH n_error, REF_REPLAY_TWO porigin_y (REFERENCE n_y) z_y prefowner* prefreturncursor_z prefreturncursor_x]',
        '$throwable_live(S_error, n_error)', '$ref_replay_two_valid(S_error, porigin_y, REFERENCE n_y, z_y, prefowner*, prefreturncursor_z, prefreturncursor_x)',
        '$string_bytes($throwable_field(S_error, n_error, "message")) = ($ptascii("f(): Return value must be of type string, stdClass returned"))',
        '$throwable_previous_id(S_error, n_error) = eps',
        '$task_nodes(REF_REPLAY_TWO porigin_y (REFERENCE n_y) z_y prefowner* prefreturncursor_z prefreturncursor_x) = [HCELL n_y]',
        '~((HCELL n_x) <- $tasks_nodes(S_error.TODO))', '~((HCELL n_z) <- $tasks_nodes(S_error.TODO))',
        '$call_descriptors_valid(S_error)', '$heap_valid($heap_graph(S_error))',
        'prefowner* = prefowner_first :: eps',
        'S_expanded = $drive_steps(S_error[.COMPLETION = NORMAL], 1)', 'S_expanded.COMPLETION = BUDGET',
        'S_expanded.TODO = (THROW_SEARCH n_error) :: ($ref_replay_tasks(porigin_y, z_y, prefowner*) ++ $ref_consumed_pair_tasks(prefreturncursor_z, prefreturncursor_x))',
        'S_expanded.ORIGIN = ($ref_owner_origin(prefowner_first))',
        '$ref_consumed_pair_tail(S_expanded.TODO) = [FINALLY_REF_PAIR prefreturncursor_z prefreturncursor_x, FINALLY_PHASE porigin_z_owner 3, ORIGIN_RETURN porigin_z_restore?, FINALLY_REF_CONSUMED prefreturncursor_x, FINALLY_PHASE porigin_x_owner 3, ORIGIN_RETURN porigin_x_restore?]',
        '$ref_consumed_scope_tail(S_expanded.TODO) = $ref_consumed_pair_tail(S_expanded.TODO)',
        '$ref_consumed_tail(S_expanded.TODO) = [FINALLY_REF_CONSUMED prefreturncursor_x, FINALLY_PHASE porigin_x_owner 3, ORIGIN_RETURN porigin_x_restore?]',
        '$call_descriptors_valid(S_expanded)', '$heap_valid($heap_graph(S_expanded))',
    ], bad=[
        'S_partial[.TODO = $af_replace(S_partial.TODO, FINALLY_REF_RETURN porigin_x_owner porigin_x (REFERENCE n_x) z_x, eps)]',
        'S_partial[.TODO = $af_replace(S_partial.TODO, REF_RETURN_PAIR_PENDING prefreturncursor_z prefreturncursor_x porigin_y z_y, [REF_RETURN_PAIR_PENDING prefreturncursor_x prefreturncursor_z porigin_y z_y])]',
        'S_partial[.TODO = $af_replace(S_partial.TODO, REF_RETURN_PAIR_PENDING prefreturncursor_z prefreturncursor_x porigin_y z_y, [REF_RETURN_PAIR_PENDING prefreturncursor_z prefreturncursor_x porigin_y z_y, REF_RETURN_PAIR_PENDING prefreturncursor_z prefreturncursor_x porigin_y z_y])]',
        'S_terminal[.TODO = $af_replace(S_terminal.TODO, REF_RETURN_PAIR prefreturncursor_z prefreturncursor_x porigin_y z_y, [REF_RETURN_PAIR (prefreturncursor_z[.SOURCE = porigin_y]) prefreturncursor_x porigin_y z_y])]',
        'S_terminal[.TODO = $af_replace(S_terminal.TODO, REF_RETURN_PAIR prefreturncursor_z prefreturncursor_x porigin_y z_y, [REF_RETURN_PAIR prefreturncursor_z (prefreturncursor_x[.LINE = $(z_x + 1)]) porigin_y z_y])]',
        'S_terminal[.TODO = $af_replace(S_terminal.TODO, REF_RECHECK porigin_y porigin_first (REFERENCE n_y) z_y, eps)]',
        'S_error[.TODO = [THROW_SEARCH n_error, REF_REPLAY_TWO porigin_y (REFERENCE n_y) z_y prefowner* prefreturncursor_x prefreturncursor_z]]',
    ], terminal=['S_whole.STORE[n_x] = DEFINED pvalue_x', 'S_whole.STORE[n_z] = DEFINED pvalue_z'])

    saved_pair = ['$af_function(S, $ptascii("ping"))', 'S.FRAMES = pframe :: pframe_tail*',
                  '$af_outputs(S.EVENTS) = $ptascii("O;P;M;P;I1;P;I2;P;")',
                  '$ref_consumed_pair_tail(pframe.TODO) = [FINALLY_REF_PAIR prefreturncursor_z prefreturncursor_x, FINALLY_PHASE porigin_z_owner 3, ORIGIN_RETURN porigin_z_restore?, FINALLY_REF_CONSUMED prefreturncursor_x, FINALLY_PHASE porigin_x_owner 3, ORIGIN_RETURN porigin_x_restore?]']
    restored_pair = ['$af_function(S, $ptascii("f"))',
                     '$af_outputs(S.EVENTS) = $ptascii("O;P;M;P;I1;P;I2;P;")', '$ref_consumed_pair_tail(S.TODO) =/= eps']
    fixture('saved-pair-and-inner-error', abrupt, {0: saved_pair, 1: restored_pair}, saved_pair[1:] + globals + [
        'porigin_z_owner = prefreturncursor_z.OWNER', 'porigin_z_restore? = prefreturncursor_z.OUTER',
        'porigin_x_owner = prefreturncursor_x.OWNER', 'porigin_x_restore? = prefreturncursor_x.OUTER',
        'S_scope = $constant_frame_scope(S, pframe, pframe_tail*)', '$af_function(S_scope, $ptascii("f"))',
        '$lookup(S_scope.ENV, $ptascii("x")) = (n_x)', '$lookup(S_scope.ENV, $ptascii("z")) = (n_z)', '$lookup(S_scope.ENV, $ptascii("y")) = (n_y)',
        '$ref_return_pair_sites(S_scope, prefreturncursor_z, prefreturncursor_x)',
        '$call_tasks_valid(S_scope, pframe.TODO)', '$ref_consumed_scope_tail(pframe.TODO) = $ref_consumed_pair_tail(pframe.TODO)',
        '$af_error_finally(pframe.TODO) = (FINALLY_RESUME porigin_y_owner (n_error))',
        '$throwable_live(S_scope, n_error)', '$throwable_previous_id(S_scope, n_error) = eps',
        '$string_bytes($throwable_field(S_scope, n_error, "message")) = ($ptascii("f(): Return value must be of type string, stdClass returned"))',
        '$task_nodes(FINALLY_REF_PAIR prefreturncursor_z prefreturncursor_x) = eps',
        '$task_nodes(FINALLY_REF_CONSUMED prefreturncursor_x) = eps',
        '~((HCELL n_x) <- $tasks_nodes(pframe.TODO))', '~((HCELL n_z) <- $tasks_nodes(pframe.TODO))',
        '$heap_owners($heap_graph(S), HCELL n_x) = 2', '$heap_owners($heap_graph(S), HCELL n_z) = 2',
        'S_restored = $af_find($drive_steps(S, 1), 2000, 1)',
        'S_restored.TODO = pframe.TODO', 'S_restored.ORIGIN = pframe.ORIGIN',
        'S_restored.CURRENT = pframe.CONTEXT', 'S_restored.RETIREDOWNERS = pframe.RETIREDOWNERS',
        '$call_descriptors_valid(S_restored)', '$heap_valid($heap_graph(S_restored))',
    ], bad=[
        'S[.FRAMES = pframe[.TODO = $af_replace(pframe.TODO, FINALLY_REF_PAIR prefreturncursor_z prefreturncursor_x, [FINALLY_REF_PAIR prefreturncursor_z (prefreturncursor_x[.LINE = $(prefreturncursor_x.LINE + 1)])])] :: pframe_tail*]',
        'S[.FRAMES = pframe[.TODO = $af_replace(pframe.TODO, FINALLY_REF_CONSUMED prefreturncursor_x, eps)] :: pframe_tail*]',
        'S[.FRAMES = pframe[.TODO = $af_replace(pframe.TODO, FINALLY_PHASE porigin_z_owner 3, [FINALLY_PHASE porigin_z_owner 1])] :: pframe_tail*]',
        'S[.FRAMES = pframe[.TODO = $af_replace(pframe.TODO, FINALLY_REF_PAIR prefreturncursor_z prefreturncursor_x, [FINALLY_REF_PAIR prefreturncursor_z prefreturncursor_x, FINALLY_REF_PAIR prefreturncursor_z prefreturncursor_x])] :: pframe_tail*]',
    ])

    escaping = ['S.TODO = (THROW_SEARCH n_error) :: (FINALLY_REF_PAIR prefreturncursor_z prefreturncursor_x) :: (FINALLY_PHASE porigin_z_owner 3) :: (ORIGIN_RETURN porigin_z_restore?) :: (FINALLY_REF_CONSUMED prefreturncursor_x) :: (FINALLY_PHASE porigin_x_owner 3) :: (ORIGIN_RETURN porigin_x_restore?) :: eps',
                '$af_outputs(S.EVENTS) = $ptascii("O;P;M;P;I1;P;I2;P;")']
    fixture('uncaught-pair-z-then-x-exit', abrupt, {0: escaping}, escaping + globals + [
        'porigin_z_owner = prefreturncursor_z.OWNER', 'porigin_z_restore? = prefreturncursor_z.OUTER',
        'porigin_x_owner = prefreturncursor_x.OWNER', 'porigin_x_restore? = prefreturncursor_x.OUTER',
        '$throwable_live(S, n_error)', '$throwable_previous_id(S, n_error) = eps',
        'S.STORE[n_y] = DEFINED pvalue_y', '$string_bytes(pvalue_y) = ($ptascii("fixed"))',
        '$call_task_valid(S, FINALLY_REF_PAIR prefreturncursor_z prefreturncursor_x)',
        '~((HCELL n_x) <- $tasks_nodes(S.TODO))', '~((HCELL n_z) <- $tasks_nodes(S.TODO))',
        'S_middle = $drive_steps(S, 1)',
        'S_middle.TODO = [THROW_SEARCH n_error, FINALLY_REF_CONSUMED prefreturncursor_x, FINALLY_PHASE porigin_x_owner 3, ORIGIN_RETURN porigin_x_restore?]',
        'S_middle.ORIGIN = porigin_z_restore?', '$throwable_live(S_middle, n_error)',
        '$call_descriptors_valid(S_middle)', '$heap_valid($heap_graph(S_middle))',
        'S_exit = $drive_steps(S_middle[.COMPLETION = NORMAL], 1)', 'S_exit.TODO = [THROW_SEARCH n_error]',
        'S_exit.ORIGIN = porigin_x_restore?', '$ma_history_count(S_exit.TODO) = 0',
        '$throwable_live(S_exit, n_error)', 'S_exit.STORE[n_x] = DEFINED pvalue_x', 'S_exit.STORE[n_z] = DEFINED pvalue_z',
        '$call_descriptors_valid(S_exit)', '$heap_valid($heap_graph(S_exit))',
        'S_normal = S[.TODO = [FINALLY_REF_PAIR prefreturncursor_z prefreturncursor_x, FINALLY_PHASE porigin_z_owner 3, ORIGIN_RETURN porigin_z_restore?, FINALLY_REF_CONSUMED prefreturncursor_x, FINALLY_PHASE porigin_x_owner 3, ORIGIN_RETURN porigin_x_restore?]]',
        '$call_descriptors_valid(S_normal)', 'PhpStep: S_normal ~> S_boundary', 'S_boundary.TODO = eps',
        'S_boundary.COMPLETION = UNSUPPORTED "caught two-history reference return replay"',
    ])

    assigned = ['$lookup(S.ENV, $ptascii("r")) = (n_r)', '$lookup(S.ENV, $ptascii("y")) = (n_r)',
                'S.STORE[n_r] = DEFINED pvalue_r', '$string_bytes(pvalue_r) = ($ptascii("fixed"))']
    written = ['$lookup(S.ENV, $ptascii("r")) = (n_r)', '$lookup(S.ENV, $ptascii("y")) = (n_r)',
               'S.STORE[n_r] = DEFINED pvalue_r', '$string_bytes(pvalue_r) = ($ptascii("changed"))']
    old_saved = ['$af_function(S, $ptascii("ping"))', 'S.FRAMES = pframe :: pframe_tail*',
                 '$af_outputs(S.EVENTS) = $ptascii("O;P;M;P;I2;")']
    fixture('normal-pair-retirement-selected-y', normal, {0: pre, 1: terminal_pair, 2: assigned, 3: written, 4: old_saved}, capture_checks + [
        '$af_outputs(S.EVENTS) = $ptascii("O;P;M;P;I2;P;")',
        'S.STORE[n_y] = DEFINED pvalue_y', '$string_bytes(pvalue_y) = ($ptascii("fixed"))',
        'S_saved = $af_find(S_start, 2000, 4)', 'S_saved.FRAMES = pframe :: pframe_tail*',
        'S_scope = $constant_frame_scope(S_saved, pframe, pframe_tail*)',
        '$ma_named_history(S_scope, pframe.TODO, $ptascii("x"), n_x)', '$ma_named_history(S_scope, pframe.TODO, $ptascii("z"), n_z)',
        '$call_descriptors_valid(S_saved)', '$heap_valid($heap_graph(S_saved))',
        '~$destructor_operational(S_terminal)',
        'S_returned = $drive_steps(S_terminal, 1)', 'S_returned.RESULT = REFERENCE n_y',
        'S_returned.CURRENT = eps', 'S_returned.FRAMES = eps', '$ma_history_count(S_returned.TODO) = 0',
        'S_returned.STORE[n_y] = DEFINED pvalue_y', '$call_descriptors_valid(S_returned)', '$heap_valid($heap_graph(S_returned))',
        'S_r = $af_find(S_returned, 2000, 2)', '$lookup(S_r.ENV, $ptascii("r")) = (n_y)',
        '$lookup(S_r.ENV, $ptascii("y")) = (n_y)', '$ma_history_count(S_r.TODO) = 0',
        'S_written = $af_find($drive_steps(S_r, 1), 2000, 3)',
        '$lookup(S_written.ENV, $ptascii("r")) = (n_y)', '$lookup(S_written.ENV, $ptascii("y")) = (n_y)',
        'S_written.STORE[n_x] = DEFINED pvalue_x', 'S_written.STORE[n_z] = DEFINED pvalue_z',
        '$call_descriptors_valid(S_written)', '$heap_valid($heap_graph(S_written))',
    ], terminal=['$lookup(S_whole.ENV, $ptascii("r")) = (n_y)', '$lookup(S_whole.ENV, $ptascii("y")) = (n_y)',
                 'S_whole.STORE[n_x] = DEFINED pvalue_x', 'S_whole.STORE[n_z] = DEFINED pvalue_z',
                 'S_whole.STORE[n_y] = DEFINED pvalue_changed', '$string_bytes(pvalue_changed) = ($ptascii("changed"))'])

    manifest = {'source_reports': reports, 'catalogue_sha256': sha(catalogue),
                'fixtures': len(records), 'assertions': sum(row['assertions'] for row in records),
                'records': records}
    (args.output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'fixtures': manifest['fixtures'], 'assertions': manifest['assertions']}))


if __name__ == '__main__':
    main()
