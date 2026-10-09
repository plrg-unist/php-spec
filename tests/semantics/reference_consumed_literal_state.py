"""Emit source-reached immutable-literal consumed-finalizer state fixtures."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
from reference_active_finalizer_state import PREFIX as ACTIVE_PREFIX
from request_environment_state import request_fixture

MESSAGE = '$ptascii("Only variable references should be returned by reference")'
PREFIX = ACTIVE_PREFIX + r'''
dec $cl_diagnostic(pevent) : pevent*
def $cl_diagnostic(DIAGNOSTIC text n* z) = [DIAGNOSTIC text n* z]
def $cl_diagnostic(DIAGNOSTIC_SOURCE n_unit text n* z) = [DIAGNOSTIC text n* z]
def $cl_diagnostic(DISPLAY_STDOUT pevent) = $cl_diagnostic(pevent)
def $cl_diagnostic(pevent) = eps -- otherwise
dec $cl_diagnostics(pevent*) : pevent*
def $cl_diagnostics(eps) = eps
def $cl_diagnostics(pevent :: pevent_tail*) = $cl_diagnostic(pevent) ++ $cl_diagnostics(pevent_tail*)
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw', type=Path, action='append', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    catalogue = ROOT / 'tests/semantics/reference_consumed_literal_cases.json'
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
                       '$cl_diagnostics(S_whole.EVENTS) = [DIAGNOSTIC "Notice" (' + MESSAGE + ') z_old]',
                       'S_whole.CURRENT = eps', 'S_whole.FRAMES = eps', 'S_whole.TODO = eps',
                       'S_whole.HELD = eps', 'S_whole.RETIREDOWNERS = eps',
                       '$heap_valid($heap_graph(S_whole))', '$call_descriptors_valid(S_whole)'] + list(terminal)
        path = args.output / (name + '.watsup')
        path.write_text(PREFIX + '\n' + stage_text + '\ndec $main() : bool\ndef $main() = true\n' +
                        ''.join('  -- if ' + condition + '\n' for condition in assertions))
        records.append({'id': name, 'source_id': case, 'fixture': str(path.resolve()),
                        'fixture_sha256': sha(path), 'assertions': len(assertions)})

    original = 'active-finalizer-consumed-literal-local-catch'
    saved = 'active-finalizer-consumed-literal-saved-replay'
    literal = ['pvalue_old = PSTRING_CARRIER INTERNED_STRING ($ptascii("old"))',
               '$origin_node(S.SOURCES, porigin_old) = (NStmtReturn (NScalarString phpType33 metadata_string) metadata_return)',
               '$evaluate(NScalarString phpType33 metadata_string) = VALUE pvalue_source',
               '$string_literal_value(pvalue_source) = pvalue_old', 'z_old = 4']
    globals = ['S.GLOBALTABLE = (psymboltable)', '$lookup(psymboltable.ENV, $ptascii("x")) = (n_x)',
               '$lookup(psymboltable.ENV, $ptascii("y")) = (n_y)', 'n_x =/= n_y',
               'S.STORE[n_x] = DEFINED pvalue_x', '$string_bytes(pvalue_x) = ($ptascii("old"))']
    capture = ['S.TODO = (RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y) :: (FINALLY_REF_RETURN porigin_outer porigin_old (KNOWN pvalue_old) z_old) :: (FINALLY_PHASE porigin_outer 3) :: (ORIGIN_RETURN porigin_restore?) :: ptask_tail*']
    current = ['S.TODO = [RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y, REF_RETURN_CURSOR prefreturncursor porigin_y z_y, REF_RECHECK porigin_y porigin_first (REFERENCE n_y) z_y]']
    fixture('literal-capture-and-active-error', original, {0: capture, 1: current}, capture + literal + globals + [
        '$af_outputs(S.EVENTS) = $ptascii("O;P;I1;")', '$cl_diagnostics(S.EVENTS) = eps',
        '$reference_notice_count(S.TODO) = 0', 'S.STORE[n_y] = DEFINED (POBJECT n_y_object)',
        'S.CURRENT = (pcallcontext)', '$function_at($all_functions(S), pcallcontext.FUNCTION) = (pfunction)',
        'prefreturncursor = { OWNER porigin_outer, SOURCE porigin_old, LINE z_old, OUTER porigin_restore? }',
        '$ref_return_cursor_literal(S, prefreturncursor) = (pvalue_old)',
        '$ref_return_cursor_old_operand(S, prefreturncursor, KNOWN pvalue_old)',
        # This changed operand is a helper-only capture refusal, not a forged public-state rejection.
        'pvalue_bad = PSTRING_CARRIER INTERNED_STRING ($ptascii("changed"))',
        '~$ref_return_cursor_old_operand(S, prefreturncursor, KNOWN pvalue_bad)',
        'S_fallback = $ref_return_cursor_capture(S, porigin_outer, porigin_old, KNOWN pvalue_bad, z_old, porigin_y, REFERENCE n_y, z_y, true, (FINALLY_PHASE porigin_outer 3) :: (ORIGIN_RETURN porigin_restore?) :: ptask_tail*)',
        '$af_cursor_count(S_fallback.TODO) = 0', 'S_fallback.STORE = S.STORE',
        'S_captured = $drive_steps(S, 1)', 'S_captured.COMPLETION = BUDGET',
        'S_captured.TODO = [RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y, TYPE_FALLTHROUGH pfunction.ORIGIN, REF_RETURN_CURSOR prefreturncursor porigin_y z_y, REF_RECHECK porigin_y porigin_first (REFERENCE n_y) z_y]',
        '$call_descriptors_valid(S_captured)', '$heap_valid($heap_graph(S_captured))',
        '$ref_return_cursor_valid(S_captured, prefreturncursor, porigin_y, z_y)',
        '$ref_return_cursor_single(S_captured, porigin_outer, porigin_y)',
        '$af_cursor_count(S_captured.TODO) = 1', '$reference_notice_count(S_captured.TODO) = 0',
        '$task_nodes(REF_RETURN_CURSOR prefreturncursor porigin_y z_y) = eps',
        '~((HCELL n_x) <- $tasks_nodes(S_captured.TODO))',
        '$heap_owners($heap_graph(S_captured), HCELL n_x) = $heap_owners($heap_graph(S), HCELL n_x)',
        '$heap_owners($heap_graph(S_captured), HCELL n_y) = $heap_owners($heap_graph(S), HCELL n_y)',
        'S_captured.STORE = S.STORE', 'S_captured.HELD = S.HELD',
        'S_terminal = $af_find(S_captured, 2000, 1)',
        'S_terminal.TODO = [RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y, REF_RETURN_CURSOR prefreturncursor porigin_y z_y, REF_RECHECK porigin_y porigin_first (REFERENCE n_y) z_y]',
        '$call_descriptors_valid(S_terminal)', '$heap_valid($heap_graph(S_terminal))',
        'S_error = $drive_steps(S_terminal, 1)', 'S_error.COMPLETION = BUDGET',
        'S_error.TODO = [THROW_SEARCH n_error, REF_REPLAY_ACTIVE porigin_y (REFERENCE n_y) z_y prefowner* prefreturncursor]',
        '$throwable_live(S_error, n_error)', 'S_error.OBJECTS[n_error] = THROWABLE pthrowable',
        'pthrowable.KIND = "TypeError"',
        '$string_bytes($throwable_field(S_error, n_error, "message")) = ($ptascii("f(): Return value must be of type string, stdClass returned"))',
        '$ref_replay_active_valid(S_error, porigin_y, REFERENCE n_y, z_y, prefowner*, prefreturncursor)',
        '$call_descriptors_valid(S_error)', '$heap_valid($heap_graph(S_error))',
        '$task_nodes(REF_REPLAY_ACTIVE porigin_y (REFERENCE n_y) z_y prefowner* prefreturncursor) = [HCELL n_y]',
        '$reference_notice_count(S_error.TODO) = 0', '$cl_diagnostics(S_error.EVENTS) = eps',
        '$af_pending(S_error.TODO) = eps', 'S_error.STORE[n_x] = DEFINED pvalue_x',
        'prefowner* = prefowner_first :: prefowner_tail*',
        'S_expanded = $drive_steps(S_error[.COMPLETION = NORMAL], 1)',
        'S_expanded.TODO = (THROW_SEARCH n_error) :: ($ref_replay_tasks(porigin_y, z_y, prefowner*) ++ $ref_consumed_tasks(prefreturncursor))',
        '$ref_consumed_tail(S_expanded.TODO) = [FINALLY_REF_CONSUMED prefreturncursor, FINALLY_PHASE prefreturncursor.OWNER 3, ORIGIN_RETURN prefreturncursor.OUTER]',
        '$task_nodes(FINALLY_REF_CONSUMED prefreturncursor) = eps',
        '$call_descriptors_valid(S_expanded)', '$heap_valid($heap_graph(S_expanded))',
        '$reference_notice_count(S_expanded.TODO) = 0', '$throwable_live(S_expanded, n_error)',
    ], bad=[
        'S_terminal[.TODO = [RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y, REF_RETURN_CURSOR (prefreturncursor[.LINE = $(z_old + 1)]) porigin_y z_y, REF_RECHECK porigin_y porigin_first (REFERENCE n_y) z_y]]',
        'S_terminal[.TODO = [RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y, REF_RETURN_CURSOR (prefreturncursor[.SOURCE = porigin_y]) porigin_y z_y, REF_RECHECK porigin_y porigin_first (REFERENCE n_y) z_y]]',
        'S_terminal[.TODO = [RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y, REF_RETURN_CURSOR prefreturncursor porigin_y z_y, REF_RETURN_CURSOR prefreturncursor porigin_y z_y, REF_RECHECK porigin_y porigin_first (REFERENCE n_y) z_y]]',
        'S_terminal[.TODO = [RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y, REF_RECHECK porigin_y porigin_first (REFERENCE n_y) z_y, REF_RETURN_CURSOR prefreturncursor porigin_y z_y]]',
        'S_terminal[.TODO = [RETURN_REF_UNWIND (REFERENCE n_y) z_y true porigin_y, REF_RETURN_CURSOR prefreturncursor porigin_y z_y, REF_RECHECK porigin_y porigin_first (REFERENCE n_x) z_y]]',
        'S_error[.TODO = [THROW_SEARCH n_error, REF_REPLAY_ACTIVE porigin_y (REFERENCE n_y) z_y prefowner* (prefreturncursor[.LINE = $(z_old + 1)])]]',
        'S_error[.TODO = [THROW_SEARCH n_error, REF_REPLAY_ACTIVE porigin_y (REFERENCE n_y) z_y prefowner* (prefreturncursor[.SOURCE = porigin_y])]]',
    ])

    saved_stage = ['$af_function(S, $ptascii("ping"))', 'S.FRAMES = pframe :: pframe_tail*',
                   '$ref_consumed_tail(pframe.TODO) = [FINALLY_REF_CONSUMED prefreturncursor, FINALLY_PHASE porigin_owner 3, ORIGIN_RETURN porigin_restore?]',
                   'porigin_owner = prefreturncursor.OWNER', 'porigin_restore? = prefreturncursor.OUTER',
                   '$af_outputs(S.EVENTS) = $ptascii("O;P;I1;I2;P;")']
    restored_stage = ['$af_function(S, $ptascii("f"))',
                      '$ref_consumed_tail(S.TODO) = [FINALLY_REF_CONSUMED prefreturncursor, FINALLY_PHASE porigin_owner 3, ORIGIN_RETURN porigin_restore?]',
                      'porigin_owner = prefreturncursor.OWNER', 'porigin_restore? = prefreturncursor.OUTER',
                      '$af_outputs(S.EVENTS) = $ptascii("O;P;I1;I2;P;")']
    fixture('saved-literal-consumed-error', saved, {0: saved_stage, 1: restored_stage}, saved_stage[1:] + [
        'S_scope = $constant_frame_scope(S, pframe, pframe_tail*)', '$af_function(S_scope, $ptascii("f"))',
        'porigin_old = prefreturncursor.SOURCE', 'z_old = prefreturncursor.LINE',
        '$origin_node(S.SOURCES, porigin_old) = (NStmtReturn (NScalarString phpType33 metadata_string) metadata_return)',
        '$ref_return_cursor_literal(S_scope, prefreturncursor) = (pvalue_old)',
        'pvalue_old = PSTRING_CARRIER INTERNED_STRING ($ptascii("old"))', 'z_old = 4',
        '$ref_return_cursor_site(S_scope, prefreturncursor)', '$call_tasks_valid(S_scope, pframe.TODO)',
        '$af_pending(pframe.TODO) = eps', '$af_cursor_count(pframe.TODO) = 1',
        '$reference_notice_count(pframe.TODO) = 0', '$cl_diagnostics(S.EVENTS) = eps',
        '$task_nodes(FINALLY_REF_CONSUMED prefreturncursor) = eps',
        '$af_error_finally(pframe.TODO) = (FINALLY_RESUME porigin_inner (n_error))',
        '$finally_phase_at(pframe.TODO, FINALLY_RESUME porigin_inner (n_error), 1)',
        '$throwable_live(S_scope, n_error)', 'S_scope.OBJECTS[n_error] = THROWABLE pthrowable',
        'pthrowable.KIND = "TypeError"',
        'S.CURRENT = (pcallcontext_ping)', 'pcallcontext_ping.CALLSITE = pframe.ORIGIN',
        'S_scope.GLOBALTABLE = (psymboltable)', '$lookup(psymboltable.ENV, $ptascii("x")) = (n_x)',
        '$lookup(psymboltable.ENV, $ptascii("y")) = (n_y)', 'n_x =/= n_y',
        'S_scope.STORE[n_x] = DEFINED pvalue_x', '$string_bytes(pvalue_x) = ($ptascii("old"))',
        'S_scope.STORE[n_y] = DEFINED (POBJECT n_y_object)',
        '~((HCELL n_x) <- $tasks_nodes(pframe.TODO))',
        'S_restored = $af_find($drive_steps(S, 1), 2000, 1)',
        'S_restored.TODO = pframe.TODO', 'S_restored.ORIGIN = pframe.ORIGIN',
        'S_restored.CURRENT = pframe.CONTEXT', 'S_restored.RETIREDOWNERS = pframe.RETIREDOWNERS',
        '$ref_consumed_tail(S_restored.TODO) = $ref_consumed_tail(pframe.TODO)',
        '$ref_return_cursor_literal(S_restored, prefreturncursor) = (pvalue_old)',
        '$reference_notice_count(S_restored.TODO) = 0', '$throwable_live(S_restored, n_error)',
        '$call_descriptors_valid(S_restored)', '$heap_valid($heap_graph(S_restored))',
    ], bad=[
        'S[.FRAMES = pframe[.TODO = $af_replace(pframe.TODO, FINALLY_REF_CONSUMED prefreturncursor, [FINALLY_REF_CONSUMED (prefreturncursor[.LINE = $(z_old + 1)])])] :: pframe_tail*]',
        'S[.FRAMES = pframe[.TODO = $af_replace(pframe.TODO, FINALLY_REF_CONSUMED prefreturncursor, [FINALLY_REF_CONSUMED (prefreturncursor[.SOURCE = porigin_inner])])] :: pframe_tail*]',
        'S[.FRAMES = pframe[.TODO = $af_replace(pframe.TODO, FINALLY_PHASE prefreturncursor.OWNER 3, [FINALLY_PHASE prefreturncursor.OWNER 1])] :: pframe_tail*]',
        'S[.FRAMES = pframe[.TODO = $af_replace(pframe.TODO, FINALLY_REF_CONSUMED prefreturncursor, [FINALLY_REF_CONSUMED prefreturncursor, FINALLY_REF_CONSUMED prefreturncursor])] :: pframe_tail*]',
        'S[.FRAMES = pframe[.TODO = $af_replace(pframe.TODO, ORIGIN_RETURN prefreturncursor.OUTER, eps)] :: pframe_tail*]',
    ])

    normal = ['S.TODO = [FINALLY_REF_CONSUMED prefreturncursor, FINALLY_PHASE porigin_owner 3, ORIGIN_RETURN porigin_restore?]',
              'porigin_owner = prefreturncursor.OWNER', 'porigin_restore? = prefreturncursor.OUTER',
              '$af_outputs(S.EVENTS) = $ptascii("O;P;I1;I2;C;A;")']
    notice_result = ['S.TODO = [REF_RETURN_NOTICE_RESULT porigin_old (KNOWN pvalue_old) z_old REF_NOTICE_VALUE]']
    caller_old = ['S.CURRENT = eps', '$lookup(S.ENV, $ptascii("r")) = (n_r)',
                  'S.STORE[n_r] = DEFINED pvalue_r', '$string_bytes(pvalue_r) = ($ptascii("old"))',
                  '$af_outputs(S.EVENTS) = $ptascii("O;P;I1;I2;C;A;r=old;")']
    caller_written = ['S.CURRENT = eps', '$lookup(S.ENV, $ptascii("r")) = (n_r)',
                      'S.STORE[n_r] = DEFINED pvalue_r', '$string_bytes(pvalue_r) = ($ptascii("changed"))',
                      '$af_outputs(S.EVENTS) = $ptascii("O;P;I1;I2;C;A;r=old;")']
    fixture('caught-literal-resume-notice-and-fresh-result', original,
            {0: normal, 1: notice_result, 2: caller_old, 3: caller_written}, normal + globals + [
        'porigin_old = prefreturncursor.SOURCE', 'z_old = prefreturncursor.LINE', 'z_old = 4',
        '$ref_return_cursor_literal(S, prefreturncursor) = (pvalue_old)',
        'pvalue_old = PSTRING_CARRIER INTERNED_STRING ($ptascii("old"))',
        '$lookup(S.ENV, $ptascii("e")) = (n_e)', 'S.STORE[n_e] = DEFINED (POBJECT n_error)',
        '$throwable_live(S, n_error)', '$af_error_finally(S.TODO) = eps', '$af_pending(S.TODO) = eps',
        '$reference_notice_count(S.TODO) = 0', '$cl_diagnostics(S.EVENTS) = eps',
        '$task_nodes(FINALLY_REF_CONSUMED prefreturncursor) = eps', '$tasks_nodes(S.TODO) = eps',
        'S_literal = $drive_steps(S, 1)',
        'S_literal.TODO = [RETURN_REF_UNWIND (KNOWN pvalue_old) z_old true porigin_old, REF_RETURN_NOTICE porigin_old z_old REF_NOTICE_VALUE, REF_RECHECK porigin_old prefreturncursor.OWNER (KNOWN pvalue_old) z_old]',
        '$reference_notice_count(S_literal.TODO) = 1', '$af_cursor_count(S_literal.TODO) = 0',
        '$tasks_nodes(S_literal.TODO) = eps', '$cl_diagnostics(S_literal.EVENTS) = eps',
        'S_literal.STORE = S.STORE', '$af_outputs(S_literal.EVENTS) = $af_outputs(S.EVENTS)',
        '$call_descriptors_valid(S_literal)', '$heap_valid($heap_graph(S_literal))',
        'S_begin = $drive_steps(S_literal[.COMPLETION = NORMAL], 1)',
        'S_begin.TODO = [REF_RETURN_NOTICE_BEGIN porigin_old (KNOWN pvalue_old) z_old REF_NOTICE_VALUE]',
        'S_begin.ORIGIN = ($reference_notice_boundary(S_begin))',
        '$cl_diagnostics(S_begin.EVENTS) = eps', '$task_nodes(REF_RETURN_NOTICE_BEGIN porigin_old (KNOWN pvalue_old) z_old REF_NOTICE_VALUE) = eps',
        '$call_descriptors_valid(S_begin)', '$heap_valid($heap_graph(S_begin))',
        'S_result = $af_find(S_begin, 2000, 1)',
        'S_result.TODO = [REF_RETURN_NOTICE_RESULT porigin_old (KNOWN pvalue_old) z_old REF_NOTICE_VALUE]',
        'S_result.EVENTS[0:|S.EVENTS|] = S.EVENTS',
        '|S_result.EVENTS| = $(|S.EVENTS| + 1)',
        '$cl_diagnostics(S_result.EVENTS) = [DIAGNOSTIC "Notice" (' + MESSAGE + ') z_old]',
        '$af_outputs(S_result.EVENTS) = $af_outputs(S.EVENTS)',
        'S_result.REFCELLS = S.REFCELLS', 'S_result.STORE = S.STORE',
        '$call_descriptors_valid(S_result)', '$heap_valid($heap_graph(S_result))',
        '~$destructor_operational(S_result)',
        'S_returned = $drive_steps(S_result, 1)', 'S_returned.RESULT = REFERENCE n_r',
        'S_returned.CURRENT = eps', 'S_returned.FRAMES = eps',
        'n_r =/= n_x', 'n_r =/= n_y', 'n_r = |S_result.STORE|',
        'S_returned.STORE[n_r] = DEFINED pvalue_old', 'n_r <- S_returned.REFCELLS',
        '(HCELL n_r) <- S_returned.ALLOCATIONS', '$af_cursor_count(S_returned.TODO) = 0',
        '$call_descriptors_valid(S_returned)', '$heap_valid($heap_graph(S_returned))',
        'S_r = $af_find(S_returned, 2000, 2)', '$lookup(S_r.ENV, $ptascii("r")) = (n_r)',
        '$lookup(S_r.ENV, $ptascii("x")) = (n_x)', '$lookup(S_r.ENV, $ptascii("y")) = (n_y)',
        'S_r.STORE[n_r] = DEFINED pvalue_old', 'S_r.STORE[n_x] = DEFINED pvalue_x',
        'S_r.STORE[n_y] = DEFINED pvalue_y', '$string_bytes(pvalue_y) = ($ptascii("fixed"))',
        'S_written = $af_find($drive_steps(S_r, 1), 2000, 3)',
        '$lookup(S_written.ENV, $ptascii("r")) = (n_r)',
        'S_written.STORE[n_r] = DEFINED pvalue_changed', '$string_bytes(pvalue_changed) = ($ptascii("changed"))',
        'S_written.STORE[n_x] = DEFINED pvalue_x', 'S_written.STORE[n_y] = DEFINED pvalue_y',
        '$cl_diagnostics(S_written.EVENTS) = [DIAGNOSTIC "Notice" (' + MESSAGE + ') z_old]',
        '$call_descriptors_valid(S_written)', '$heap_valid($heap_graph(S_written))',
    ], bad=[
        'S[.TODO = [FINALLY_REF_CONSUMED (prefreturncursor[.LINE = $(z_old + 1)]), FINALLY_PHASE prefreturncursor.OWNER 3, ORIGIN_RETURN prefreturncursor.OUTER]]',
        'S[.TODO = [FINALLY_REF_CONSUMED prefreturncursor, FINALLY_REF_CONSUMED prefreturncursor, FINALLY_PHASE prefreturncursor.OWNER 3, ORIGIN_RETURN prefreturncursor.OUTER]]',
        'S_literal[.TODO = [RETURN_REF_UNWIND (KNOWN pvalue_old) z_old true porigin_old, REF_RECHECK porigin_old prefreturncursor.OWNER (KNOWN pvalue_old) z_old]]',
        'S_literal[.TODO = [RETURN_REF_UNWIND (KNOWN pvalue_old) z_old true porigin_old, REF_RETURN_NOTICE porigin_old $(z_old + 1) REF_NOTICE_VALUE, REF_RECHECK porigin_old prefreturncursor.OWNER (KNOWN pvalue_old) z_old]]',
        'S_literal[.TODO = [RETURN_REF_UNWIND (KNOWN pvalue_old) z_old true porigin_old, REF_RETURN_NOTICE porigin_old z_old REF_NOTICE_VALUE, REF_RETURN_NOTICE porigin_old z_old REF_NOTICE_VALUE, REF_RECHECK porigin_old prefreturncursor.OWNER (KNOWN pvalue_old) z_old]]',
        'S_literal[.TODO = [RETURN_REF_UNWIND (KNOWN pvalue_old) z_old true porigin_old, REF_RETURN_NOTICE porigin_old z_old REF_NOTICE_NULL, REF_RECHECK porigin_old prefreturncursor.OWNER (KNOWN pvalue_old) z_old]]',
    ])

    manifest = {'source_reports': reports, 'catalogue_sha256': sha(catalogue),
                'fixtures': len(records), 'assertions': sum(row['assertions'] for row in records),
                'records': records}
    (args.output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'fixtures': manifest['fixtures'], 'assertions': manifest['assertions']}))


if __name__ == '__main__':
    main()
