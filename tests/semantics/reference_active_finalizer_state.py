"""Emit source-reached consumed-finalizer cursor fixtures from accepted packets."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
from request_environment_state import request_fixture

PREFIX = r'''dec $af_function(pstate, preqbytes) : bool
def $af_function(S, n_name*) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $function_at($all_functions(S), pcallcontext.FUNCTION) = (pfunction)
  -- if pfunction.NAME = n_name*
def $af_function(S, n_name*) = false -- otherwise
dec $af_pending_head(ptask) : bool
def $af_pending_head(FINALLY_REF_RETURN porigin_owner porigin_source poperand z) = true
def $af_pending_head(ptask) = false -- otherwise
dec $af_pending(ptask*) : ptask?
def $af_pending(eps) = eps
def $af_pending((FINALLY_REF_RETURN porigin_owner porigin_source poperand z) :: ptask_tail*) = (FINALLY_REF_RETURN porigin_owner porigin_source poperand z)
def $af_pending(ptask :: ptask_tail*) = $af_pending(ptask_tail*) -- if ~$af_pending_head(ptask)
dec $af_cursor_head(ptask) : bool
def $af_cursor_head(REF_RETURN_CURSOR prefreturncursor porigin z) = true
def $af_cursor_head(REF_REPLAY_ACTIVE porigin poperand z prefowner* prefreturncursor) = true
def $af_cursor_head(FINALLY_REF_CONSUMED prefreturncursor) = true
def $af_cursor_head(ptask) = false -- otherwise
dec $af_cursor_count(ptask*) : nat
def $af_cursor_count(eps) = 0
def $af_cursor_count(ptask :: ptask_tail*) = $(1 + $af_cursor_count(ptask_tail*)) -- if $af_cursor_head(ptask)
def $af_cursor_count(ptask :: ptask_tail*) = $af_cursor_count(ptask_tail*) -- if ~$af_cursor_head(ptask)
dec $af_error_finally_head(ptask) : bool
def $af_error_finally_head(FINALLY_RESUME porigin (n)) = true
def $af_error_finally_head(ptask) = false -- otherwise
dec $af_error_finally(ptask*) : ptask?
def $af_error_finally(eps) = eps
def $af_error_finally((FINALLY_RESUME porigin (n)) :: ptask_tail*) = (FINALLY_RESUME porigin (n))
def $af_error_finally(ptask :: ptask_tail*) = $af_error_finally(ptask_tail*) -- if ~$af_error_finally_head(ptask)
dec $af_output(pevent) : nat*
def $af_output(OUTPUT n*) = n*
def $af_output(pevent) = eps -- otherwise
dec $af_outputs(pevent*) : nat*
def $af_outputs(eps) = eps
def $af_outputs(pevent :: pevent_tail*) = $af_output(pevent) ++ $af_outputs(pevent_tail*)
dec $af_stage(pstate, nat) : bool
dec $af_find(pstate, nat, nat) : pstate
def $af_find(S, n, n_stage) = S[.COMPLETION = NORMAL]
  -- if $af_stage(S, n_stage)
  -- if S.COMPLETION = BUDGET
def $af_find(S, n, n_stage) = $af_find($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)), n_stage)
  -- if ~$af_stage(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
dec $af_resume(pstate, nat) : pstate
def $af_resume(S, n) = $drive(S[.COMPLETION = NORMAL], n) -- if S.COMPLETION = BUDGET
def $af_resume(S, n) = S -- otherwise
dec $af_replace(ptask*, ptask, ptask*) : ptask*
def $af_replace(eps, ptask_old, ptask_new*) = eps
def $af_replace(ptask_old :: ptask_tail*, ptask_old, ptask_new*) = ptask_new* ++ ptask_tail*
def $af_replace(ptask :: ptask_tail*, ptask_old, ptask_new*) = ptask :: $af_replace(ptask_tail*, ptask_old, ptask_new*) -- if ptask =/= ptask_old
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw', type=Path, action='append', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    catalogue = ROOT / 'tests/semantics/reference_active_finalizer_cases.json'
    cases = {row['id']: row for row in json.loads(catalogue.read_text())['cases']}
    rows, reports = {}, []
    for raw in args.raw:
        report_path = raw / 'report.json'
        report = json.loads(report_path.read_text())
        assert report['complete'] and report['pins'] == report['pins_after']
        assert report['head_after'] == report['revision'] and report['status_after'] == ''
        reports.append({'path': str(report_path.resolve()), 'sha256': sha(report_path),
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
        assert hashlib.sha256(source).hexdigest() == row['source_sha256'] == cases[case]['source_sha256']
        assert base64.b64decode(row['native']['stdout']) == cases[case]['stdout'].encode()
        assert base64.b64decode(row['native']['stderr']) == cases[case]['stderr'].encode() == b''
        assert row['native']['exit_status'] == 0
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
                       'S_whole.COMPLETION = NORMAL', '$af_outputs(S_whole.EVENTS) = $ptascii(' + json.dumps(cases[case]['stdout']) + ')',
                       'S_whole.CURRENT = eps', 'S_whole.FRAMES = eps', 'S_whole.TODO = eps',
                       'S_whole.HELD = eps', 'S_whole.RETIREDOWNERS = eps',
                       '$af_cursor_count(S_whole.TODO) = 0', '$heap_valid($heap_graph(S_whole))',
                       '$call_descriptors_valid(S_whole)'] + list(terminal)
        path = args.output / (name + '.watsup')
        path.write_text(PREFIX + '\n' + stage_text + '\ndec $main() : bool\ndef $main() = true\n' +
                        ''.join('  -- if ' + condition + '\n' for condition in assertions))
        records.append({'id': name, 'source_id': case, 'fixture': str(path.resolve()),
                        'fixture_sha256': sha(path), 'assertions': len(assertions)})

    uncaught = 'active-finalizer-uncaught'
    local = 'active-finalizer-local-catch'
    saved_normal = 'active-finalizer-saved-and-normal'
    capture = ['S.TODO = (RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y) :: (FINALLY_REF_RETURN porigin_outer porigin_x (REFERENCE n_x) z_x) :: (FINALLY_PHASE porigin_outer 3) :: (ORIGIN_RETURN porigin_restore?) :: ptask_tail*',
               '$origin_node(S.SOURCES, porigin_x) = (NStmtReturn (NExprVariable (BYTES text_x) metadata_x) metadata_return_x)',
               '$base64(text_x) = $ptascii("x")']
    globals = ['S.GLOBALTABLE = (psymboltable)', '$lookup(psymboltable.ENV, $ptascii("x")) = (n_x)',
               '$lookup(psymboltable.ENV, $ptascii("y")) = (n_y)', 'n_x =/= n_y',
               'S.STORE[n_x] = DEFINED pvalue_x', '$string_bytes(pvalue_x) = ($ptascii("old"))']
    for case in (uncaught, local):
        terminal = ['S.TODO = [RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y, REF_RETURN_CURSOR prefreturncursor porigin_y z_y, REF_RECHECK porigin_y porigin_first (REFERENCE n_y) z_y]']
        fixture('capture-' + case, case, {0: capture, 1: terminal}, capture + globals + [
            '$af_outputs(S.EVENTS) = $ptascii("O;P;I1;")',
            'S.STORE[n_y] = DEFINED (POBJECT n_y_object)',
            'S.CURRENT = (pcallcontext)', '$function_at($all_functions(S), pcallcontext.FUNCTION) = (pfunction)',
            'prefreturncursor = { OWNER porigin_outer, SOURCE porigin_x, LINE z_x, OUTER porigin_restore? }',
            'S_next = $drive_steps(S, 1)', 'S_next.COMPLETION = BUDGET',
            'S_captured = S_next[.COMPLETION = NORMAL]', '$call_descriptors_valid(S_captured)',
            'S_captured.TODO = [RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y, TYPE_FALLTHROUGH pfunction.ORIGIN, REF_RETURN_CURSOR prefreturncursor porigin_y z_y, REF_RECHECK porigin_y porigin_first (REFERENCE n_y) z_y]',
            '$ref_return_cursor_valid(S_captured, prefreturncursor, porigin_y, z_y)',
            '$ref_return_cursor_single(S_captured, porigin_outer, porigin_y)',
            '~$ref_return_cursor_single(S_captured, porigin_first, porigin_y)',
            '~$ref_return_cursor_clear(S, S.TODO)',
            '$af_cursor_count(S_captured.TODO) = 1',
            '$task_nodes(REF_RETURN_CURSOR prefreturncursor porigin_y z_y) = eps',
            '~((HCELL n_x) <- $tasks_nodes(S_captured.TODO))',
            '$heap_owners($heap_graph(S), HCELL n_x) = $($heap_owners($heap_graph(S_captured), HCELL n_x) + 1)',
            '$heap_owners($heap_graph(S), HCELL n_y) = $heap_owners($heap_graph(S_captured), HCELL n_y)',
            'S_captured.STORE = S.STORE', 'S_captured.HELD = S.HELD',
            'S_terminal = $af_find(S_next, 2000, 1)', '$call_descriptors_valid(S_terminal)',
            'S_terminal.TODO = [RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y, REF_RETURN_CURSOR prefreturncursor porigin_y z_y, REF_RECHECK porigin_y porigin_first (REFERENCE n_y) z_y]',
            'S_error = $drive_steps(S_terminal, 1)', 'S_error.COMPLETION = BUDGET',
            'S_error.TODO = [THROW_SEARCH n_error, REF_REPLAY_ACTIVE porigin_y (REFERENCE n_y) z_y prefowner* prefreturncursor]',
            '$throwable_live(S_error, n_error)', '$ref_replay_active_valid(S_error, porigin_y, REFERENCE n_y, z_y, prefowner*, prefreturncursor)',
            '$call_descriptors_valid(S_error)', '$heap_valid($heap_graph(S_error))',
            '$string_bytes($throwable_field(S_error, n_error, "message")) = ($ptascii("f(): Return value must be of type string, stdClass returned"))',
            '$task_nodes(REF_REPLAY_ACTIVE porigin_y (REFERENCE n_y) z_y prefowner* prefreturncursor) = [HCELL n_y]',
            '$af_pending(S_error.TODO) = eps', 'S_error.STORE[n_x] = DEFINED pvalue_x',
            'prefowner* = prefowner_first :: prefowner_tail*',
            'S_expanded = $drive_steps(S_error[.COMPLETION = NORMAL], 1)',
            'S_expanded.COMPLETION = BUDGET',
            'S_expanded.TODO = (THROW_SEARCH n_error) :: ($ref_replay_tasks(porigin_y, z_y, prefowner*) ++ $ref_consumed_tasks(prefreturncursor))',
            'S_expanded.ORIGIN = ($ref_owner_origin(prefowner_first))',
            '$call_descriptors_valid(S_expanded)', '$heap_valid($heap_graph(S_expanded))',
            '$ref_consumed_tail(S_expanded.TODO) = [FINALLY_REF_CONSUMED prefreturncursor, FINALLY_PHASE prefreturncursor.OWNER 3, ORIGIN_RETURN prefreturncursor.OUTER]',
        ], bad=[
            'S_terminal[.TODO = [RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y, REF_RETURN_CURSOR (prefreturncursor[.LINE = $(z_x + 1)]) porigin_y z_y, REF_RECHECK porigin_y porigin_first (REFERENCE n_y) z_y]]',
            'S_terminal[.TODO = [RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y, REF_RETURN_CURSOR (prefreturncursor[.SOURCE = porigin_y]) porigin_y z_y, REF_RECHECK porigin_y porigin_first (REFERENCE n_y) z_y]]',
            'S_terminal[.TODO = [RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y, REF_RETURN_CURSOR prefreturncursor porigin_y z_y, REF_RETURN_CURSOR prefreturncursor porigin_y z_y, REF_RECHECK porigin_y porigin_first (REFERENCE n_y) z_y]]',
            'S_terminal[.TODO = [RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y, REF_RECHECK porigin_y porigin_first (REFERENCE n_y) z_y, REF_RETURN_CURSOR prefreturncursor porigin_y z_y]]',
            'S_terminal[.TODO = [RETURN_REF_UNWIND (REFERENCE n_y) z_y false porigin_y, REF_RETURN_CURSOR prefreturncursor porigin_y z_y, REF_RECHECK porigin_y porigin_first (REFERENCE n_y) z_y]]',
            'S_terminal[.TODO = [RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y, REF_RETURN_CURSOR prefreturncursor porigin_y z_y, REF_RECHECK porigin_y porigin_first (REFERENCE n_x) z_y]]',
            'S_error[.TODO = [THROW_SEARCH n_error, REF_REPLAY_ACTIVE porigin_y (REFERENCE n_y) z_y prefowner* (prefreturncursor[.LINE = $(z_x + 1)])]]',
            'S_error[.TODO = [THROW_SEARCH n_error, REF_REPLAY_ACTIVE porigin_y (REFERENCE n_y) z_y prefowner* (prefreturncursor[.SOURCE = porigin_y])]]',
        ], terminal=['S_whole.STORE[n_x] = DEFINED pvalue_x'])

    pending_saved = ['$af_function(S, $ptascii("ping"))', 'S.FRAMES = pframe :: pframe_tail*',
                     '$af_pending(pframe.TODO) = (FINALLY_REF_RETURN porigin_outer porigin_x (REFERENCE n_x) z_x)',
                     '$af_outputs(S.EVENTS) = $ptascii("O;P;")']
    restored_pending = ['$af_function(S, $ptascii("f"))',
                        '$af_pending(S.TODO) = (FINALLY_REF_RETURN porigin_outer porigin_x (REFERENCE n_x) z_x)',
                        '$af_outputs(S.EVENTS) = $ptascii("O;P;")']
    fixture('saved-original-pending-outcome', uncaught, {0: pending_saved, 1: restored_pending}, pending_saved[1:] + [
        'S_scope = $constant_frame_scope(S, pframe, pframe_tail*)', '$af_function(S_scope, $ptascii("f"))',
        '$call_tasks_valid(S_scope, pframe.TODO)', '$finally_phase_at(pframe.TODO, FINALLY_REF_RETURN porigin_outer porigin_x (REFERENCE n_x) z_x, 3)',
        'S.CURRENT = (pcallcontext_ping)', 'pcallcontext_ping.CALLSITE = pframe.ORIGIN',
        '$af_cursor_count(pframe.TODO) = 0',
        'S_scope.GLOBALTABLE = (psymboltable)', '$lookup(psymboltable.ENV, $ptascii("x")) = (n_x)',
        'S_scope.STORE[n_x] = DEFINED pvalue_x',
        '(HCELL n_x) <- $tasks_nodes(pframe.TODO)',
        'S_restored = $af_find($drive_steps(S, 1), 2000, 1)', 'S_restored.TODO = pframe.TODO',
        'S_restored.ORIGIN = pframe.ORIGIN', 'S_restored.CURRENT = pframe.CONTEXT',
        'S_restored.RETIREDOWNERS = pframe.RETIREDOWNERS', '$call_descriptors_valid(S_restored)',
    ], bad=[
        'S[.FRAMES = pframe[.TODO = $af_replace(pframe.TODO, FINALLY_PHASE porigin_outer 3, [FINALLY_PHASE porigin_outer 1])] :: pframe_tail*]',
        'S[.FRAMES = pframe[.TODO = $af_replace(pframe.TODO, FINALLY_REF_RETURN porigin_outer porigin_x (REFERENCE n_x) z_x, eps)] :: pframe_tail*]',
    ], terminal=['S_whole.STORE[n_x] = DEFINED pvalue_x'])

    escaping = ['S.TODO = [THROW_SEARCH n_error, FINALLY_REF_CONSUMED prefreturncursor, FINALLY_PHASE porigin_owner 3, ORIGIN_RETURN porigin_restore?]',
                'porigin_owner = prefreturncursor.OWNER', 'porigin_restore? = prefreturncursor.OUTER',
                '$af_outputs(S.EVENTS) = $ptascii("O;P;I1;I2;")']
    fixture('uncaught-consumed-cursor-escape', uncaught, {0: escaping}, escaping + [
        'S.GLOBALTABLE = (psymboltable)', '$lookup(psymboltable.ENV, $ptascii("x")) = (n_x)',
        '$lookup(psymboltable.ENV, $ptascii("y")) = (n_y)', 'n_x =/= n_y',
        'S.STORE[n_x] = DEFINED pvalue_x', 'S.STORE[n_y] = DEFINED pvalue_y',
        '$throwable_live(S, n_error)', 'S.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "TypeError"',
        '$af_pending(S.TODO) = eps', '$task_nodes(FINALLY_REF_CONSUMED prefreturncursor) = eps',
        '~((HCELL n_x) <- $tasks_nodes(S.TODO))',
        'S_next = $drive_steps(S, 1)', 'S_next.TODO = [THROW_SEARCH n_error]',
        '$af_cursor_count(S_next.TODO) = 0', '$af_outputs(S_next.EVENTS) = $af_outputs(S.EVENTS)',
        '$throwable_live(S_next, n_error)', 'S_next.STORE[n_x] = DEFINED pvalue_x',
        '$heap_valid($heap_graph(S_next))', '$call_descriptors_valid(S_next)',
    ], bad=[
        'S[.TODO = [THROW_SEARCH n_error, FINALLY_REF_CONSUMED prefreturncursor, FINALLY_PHASE prefreturncursor.OWNER 1, ORIGIN_RETURN prefreturncursor.OUTER]]',
        'S[.TODO = [THROW_SEARCH n_error, FINALLY_REF_CONSUMED (prefreturncursor[.LINE = $(prefreturncursor.LINE + 1)]), FINALLY_PHASE prefreturncursor.OWNER 3, ORIGIN_RETURN prefreturncursor.OUTER]]',
    ], terminal=['S_whole.STORE[n_x] = DEFINED pvalue_x',
                 '$lookup(S_whole.ENV, $ptascii("e")) = (n_e)', 'S_whole.STORE[n_e] = DEFINED (POBJECT n_error)',
                 '$throwable_live(S_whole, n_error)'])

    consumed_normal = ['S.TODO = [FINALLY_REF_CONSUMED prefreturncursor, FINALLY_PHASE porigin_owner 3, ORIGIN_RETURN porigin_restore?]',
                       'porigin_owner = prefreturncursor.OWNER', 'porigin_restore? = prefreturncursor.OUTER',
                       '$af_outputs(S.EVENTS) = $ptascii("O;P;I1;I2;C;A;")']
    fixture('caught-consumed-null-resumption', local, {0: consumed_normal}, consumed_normal + [
        'S.GLOBALTABLE = (psymboltable)', '$lookup(psymboltable.ENV, $ptascii("x")) = (n_x)',
        '$lookup(psymboltable.ENV, $ptascii("y")) = (n_y)', 'n_x =/= n_y', 'S.STORE[n_x] = DEFINED pvalue_x',
        '$lookup(S.ENV, $ptascii("e")) = (n_e)', 'S.STORE[n_e] = DEFINED (POBJECT n_inner_error)',
        '$throwable_live(S, n_inner_error)', '$af_error_finally(S.TODO) = eps', '$af_pending(S.TODO) = eps',
        '$task_nodes(FINALLY_REF_CONSUMED prefreturncursor) = eps',
        '~((HCELL n_x) <- $tasks_nodes(S.TODO))',
        'S_null = $drive_steps(S, 1)',
        'S_null.TODO = [RETURN_REF_UNWIND (KNOWN PNULL) prefreturncursor.LINE true prefreturncursor.SOURCE, REF_RECHECK prefreturncursor.SOURCE prefreturncursor.OWNER (KNOWN PNULL) prefreturncursor.LINE]',
        '$call_descriptors_valid(S_null)', '$af_cursor_count(S_null.TODO) = 0',
        '$tasks_nodes(S_null.TODO) = eps', 'S_null.STORE[n_x] = DEFINED pvalue_x',
        'S_null_error = $drive_steps(S_null[.COMPLETION = NORMAL], 1)',
        'S_null_error.TODO = [THROW_SEARCH n_null_error, REF_REPLAY prefreturncursor.SOURCE (KNOWN PNULL) prefreturncursor.LINE prefowner*]',
        'n_null_error =/= n_inner_error', '$throwable_live(S_null_error, n_null_error)',
        '$throwable_live(S_null_error, n_inner_error)', 'S_null_error.OBJECTS[n_null_error] = THROWABLE pthrowable_null',
        'pthrowable_null.KIND = "TypeError"', '$throwable_field(S_null_error, n_null_error, "line") = PINT prefreturncursor.LINE',
        '$string_bytes($throwable_field(S_null_error, n_null_error, "message")) = ($ptascii("f(): Return value must be of type string, null returned"))',
        '$call_descriptors_valid(S_null_error)', '$heap_valid($heap_graph(S_null_error))',
        '$af_outputs(S_null_error.EVENTS) = $af_outputs(S.EVENTS)',
    ], bad=[
        'S[.TODO = [FINALLY_REF_CONSUMED prefreturncursor, FINALLY_PHASE prefreturncursor.OWNER 3]]',
        'S[.TODO = [FINALLY_REF_CONSUMED prefreturncursor, FINALLY_REF_CONSUMED prefreturncursor, FINALLY_PHASE prefreturncursor.OWNER 3, ORIGIN_RETURN prefreturncursor.OUTER]]',
        'S[.TODO = [FINALLY_PHASE prefreturncursor.OWNER 3, FINALLY_REF_CONSUMED prefreturncursor, ORIGIN_RETURN prefreturncursor.OUTER]]',
    ], terminal=['$lookup(S_whole.ENV, $ptascii("r")) = (n_y)', 'S_whole.STORE[n_x] = DEFINED pvalue_x',
                 'S_whole.STORE[n_y] = DEFINED pvalue_changed', '$string_bytes(pvalue_changed) = ($ptascii("changed"))'])

    outer_saved = ['$af_function(S, $ptascii("ping"))', 'S.FRAMES = pframe :: pframe_tail*',
                   '$af_error_finally(pframe.TODO) = (FINALLY_RESUME porigin_outer (n_null_error))',
                   '$af_outputs(S.EVENTS) = $ptascii("O;P;I1;I2;C;A;O;P;")']
    outer_restored = ['$af_function(S, $ptascii("f"))',
                      '$af_error_finally(S.TODO) = (FINALLY_RESUME porigin_outer (n_null_error))',
                      '$af_outputs(S.EVENTS) = $ptascii("O;P;I1;I2;C;A;O;P;")']
    fixture('saved-second-outer-error-finalizer', local, {0: outer_saved, 1: outer_restored}, outer_saved[1:] + [
        'S_scope = $constant_frame_scope(S, pframe, pframe_tail*)', '$af_function(S_scope, $ptascii("f"))',
        '$call_tasks_valid(S_scope, pframe.TODO)', '$finally_phase_at(pframe.TODO, FINALLY_RESUME porigin_outer (n_null_error), 1)',
        '$af_cursor_count(pframe.TODO) = 0', '$af_pending(pframe.TODO) = eps',
        'S.CURRENT = (pcallcontext_ping)', 'pcallcontext_ping.CALLSITE = pframe.ORIGIN',
        '$throwable_live(S_scope, n_null_error)',
        'S_scope.GLOBALTABLE = (psymboltable)', '$lookup(psymboltable.ENV, $ptascii("x")) = (n_x)',
        '$lookup(psymboltable.ENV, $ptascii("y")) = (n_y)', 'S_scope.STORE[n_x] = DEFINED pvalue_x',
        '~((HCELL n_x) <- $tasks_nodes(pframe.TODO))',
        'S_restored = $af_find($drive_steps(S, 1), 2000, 1)', 'S_restored.TODO = pframe.TODO',
        'S_restored.ORIGIN = pframe.ORIGIN', 'S_restored.CURRENT = pframe.CONTEXT', '$call_descriptors_valid(S_restored)',
    ], bad=[
        'S[.FRAMES = pframe[.TODO = $af_replace(pframe.TODO, FINALLY_PHASE porigin_outer 1, [FINALLY_PHASE porigin_outer 3])] :: pframe_tail*]',
    ], terminal=['$lookup(S_whole.ENV, $ptascii("r")) = (n_y)', 'S_whole.STORE[n_x] = DEFINED pvalue_x',
                 'S_whole.STORE[n_y] = DEFINED pvalue_changed', '$string_bytes(pvalue_changed) = ($ptascii("changed"))'])

    consumed_saved = ['$af_function(S, $ptascii("ping"))', 'S.FRAMES = pframe :: pframe_tail*',
                      '$ref_consumed_tail(pframe.TODO) = [FINALLY_REF_CONSUMED prefreturncursor, FINALLY_PHASE porigin_owner 3, ORIGIN_RETURN porigin_restore?]',
                      'porigin_owner = prefreturncursor.OWNER', 'porigin_restore? = prefreturncursor.OUTER',
                      '$af_outputs(S.EVENTS) = $ptascii("O;P;I1;P;I2;P;")']
    consumed_restored = ['$af_function(S, $ptascii("f"))',
                         '$ref_consumed_tail(S.TODO) = [FINALLY_REF_CONSUMED prefreturncursor, FINALLY_PHASE porigin_owner 3, ORIGIN_RETURN porigin_restore?]',
                         'porigin_owner = prefreturncursor.OWNER', 'porigin_restore? = prefreturncursor.OUTER',
                         '$af_outputs(S.EVENTS) = $ptascii("O;P;I1;P;I2;P;")']
    fixture('saved-consumed-cursor-and-inner-error', saved_normal, {0: consumed_saved, 1: consumed_restored}, consumed_saved[1:] + [
        'S_scope = $constant_frame_scope(S, pframe, pframe_tail*)', '$af_function(S_scope, $ptascii("f"))',
        '$call_tasks_valid(S_scope, pframe.TODO)', '$af_pending(pframe.TODO) = eps',
        '$af_cursor_count(pframe.TODO) = 1', '$task_nodes(FINALLY_REF_CONSUMED prefreturncursor) = eps',
        '$af_error_finally(pframe.TODO) = (FINALLY_RESUME porigin_inner (n_inner_error))',
        '$finally_phase_at(pframe.TODO, FINALLY_RESUME porigin_inner (n_inner_error), 1)',
        '$throwable_live(S_scope, n_inner_error)',
        'S.CURRENT = (pcallcontext_ping)', 'pcallcontext_ping.CALLSITE = pframe.ORIGIN',
        'S_scope.GLOBALTABLE = (psymboltable)', '$lookup(psymboltable.ENV, $ptascii("x")) = (n_x)',
        '$lookup(psymboltable.ENV, $ptascii("y")) = (n_y)', 'n_x =/= n_y',
        'S_scope.STORE[n_x] = DEFINED pvalue_x', 'S_scope.STORE[n_y] = DEFINED (POBJECT n_y_object)',
        '~((HCELL n_x) <- $tasks_nodes(pframe.TODO))',
        'S_restored = $af_find($drive_steps(S, 1), 2000, 1)', 'S_restored.TODO = pframe.TODO',
        'S_restored.ORIGIN = pframe.ORIGIN', 'S_restored.CURRENT = pframe.CONTEXT',
        '$ref_consumed_tail(S_restored.TODO) = $ref_consumed_tail(pframe.TODO)',
        '$call_descriptors_valid(S_restored)', '$throwable_live(S_restored, n_inner_error)',
    ], bad=[
        'S[.FRAMES = pframe[.TODO = $af_replace(pframe.TODO, FINALLY_REF_CONSUMED prefreturncursor, [FINALLY_REF_CONSUMED (prefreturncursor[.LINE = $(prefreturncursor.LINE + 1)])])] :: pframe_tail*]',
        'S[.FRAMES = pframe[.TODO = $af_replace(pframe.TODO, FINALLY_PHASE prefreturncursor.OWNER 3, [FINALLY_PHASE prefreturncursor.OWNER 1])] :: pframe_tail*]',
        'S[.FRAMES = pframe[.TODO = $af_replace(pframe.TODO, FINALLY_REF_CONSUMED prefreturncursor, [FINALLY_REF_CONSUMED prefreturncursor, FINALLY_REF_CONSUMED prefreturncursor])] :: pframe_tail*]',
        'S[.FRAMES = pframe[.TODO = $af_replace(pframe.TODO, ORIGIN_RETURN prefreturncursor.OUTER, eps)] :: pframe_tail*]',
    ], terminal=['$lookup(S_whole.ENV, $ptascii("r")) = (n_y)', 'S_whole.STORE[n_x] = DEFINED pvalue_x',
                 'S_whole.STORE[n_y] = DEFINED pvalue_changed', '$string_bytes(pvalue_changed) = ($ptascii("changed"))'])

    normal_cursor = ['S.TODO = [RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y, REF_RETURN_CURSOR prefreturncursor porigin_y z_y, REF_RECHECK porigin_y porigin_first (REFERENCE n_y) z_y]',
                     '$af_outputs(S.EVENTS) = $ptascii("O;P;I1;P;I2;P;R;O;P;I3;P;")']
    fixture('normal-cursor-retirement-selected-y', saved_normal, {0: normal_cursor}, normal_cursor + [
        'S.GLOBALTABLE = (psymboltable)', '$lookup(psymboltable.ENV, $ptascii("x")) = (n_x)',
        '$lookup(psymboltable.ENV, $ptascii("y")) = (n_y)', 'n_x =/= n_y',
        'S.STORE[n_x] = DEFINED pvalue_x', 'S.STORE[n_y] = DEFINED pvalue_y',
        '$string_bytes(pvalue_y) = ($ptascii("fixed"))',
        'S_checked = $finally_ref_recheck(S, REFERENCE n_y, z_y)', 'S_checked.COMPLETION = NORMAL',
        'S_checked.STORE[n_y] = DEFINED pvalue_y', 'S_checked.STORE = S.STORE',
        '$task_nodes(REF_RETURN_CURSOR prefreturncursor porigin_y z_y) = eps',
        '~((HCELL n_x) <- $tasks_nodes(S.TODO))',
        'S_next = $drive_steps(S, 1)', 'S_next.RESULT = REFERENCE n_y',
        'S_next.CURRENT = eps', '$af_cursor_count(S_next.TODO) = 0',
        'S_next.STORE[n_x] = DEFINED pvalue_x', 'S_next.STORE[n_y] = DEFINED pvalue_y',
        '$call_descriptors_valid(S_next)', '$heap_valid($heap_graph(S_next))',
    ], terminal=['$lookup(S_whole.ENV, $ptascii("r")) = (n_y)',
                 '$lookup(S_whole.ENV, $ptascii("y")) = (n_y)', 'S_whole.STORE[n_x] = DEFINED pvalue_x',
                 'S_whole.STORE[n_y] = DEFINED pvalue_changed', 'pvalue_changed =/= pvalue_y',
                 '$string_bytes(pvalue_changed) = ($ptascii("changed"))'])

    manifest = {'source_reports': reports, 'catalogue_sha256': sha(catalogue),
                'fixtures': len(records), 'assertions': sum(row['assertions'] for row in records),
                'records': records}
    (args.output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'fixtures': manifest['fixtures'], 'assertions': manifest['assertions']}))


if __name__ == '__main__':
    main()
