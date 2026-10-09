"""Emit reached aliased-CV Stringable return states from accepted model packets."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
from request_environment_state import request_fixture

PREFIX = r'''dec $tc_function(pstate, preqbytes) : bool
def $tc_function(S, n_name*) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $function_at($all_functions(S), pcallcontext.FUNCTION) = (pfunction)
  -- if pfunction.NAME = n_name*
def $tc_function(S, n_name*) = false -- otherwise
dec $tc_output(pevent) : nat*
def $tc_output(OUTPUT n*) = n*
def $tc_output(pevent) = eps -- otherwise
dec $tc_outputs(pevent*) : nat*
def $tc_outputs(eps) = eps
def $tc_outputs(pevent :: pevent_tail*) = $tc_output(pevent) ++ $tc_outputs(pevent_tail*)
dec $tc_diagnostics(pevent*) : pevent*
dec $tc_diagnostic(pevent) : bool
def $tc_diagnostic(DIAGNOSTIC text n_message* z) = true
def $tc_diagnostic(pevent) = false -- otherwise
def $tc_diagnostics(eps) = eps
def $tc_diagnostics((DIAGNOSTIC text n_message* z) :: pevent_tail*) = (DIAGNOSTIC text n_message* z) :: $tc_diagnostics(pevent_tail*)
def $tc_diagnostics(pevent :: pevent_tail*) = $tc_diagnostics(pevent_tail*) -- if ~$tc_diagnostic(pevent)
dec $tc_count(ptask*) : nat
def $tc_count(eps) = 0
def $tc_count(ptask :: ptask_tail*) = $(1 + $tc_count(ptask_tail*)) -- if $typed_ref_string_task(ptask)
def $tc_count(ptask :: ptask_tail*) = $tc_count(ptask_tail*) -- if ~$typed_ref_string_task(ptask)
dec $tc_return_finally(ptask*) : ptask?
dec $tc_return_finally_head(ptask) : bool
def $tc_return_finally_head(FINALLY_REF_RETURN porigin_owner porigin_source poperand z) = true
def $tc_return_finally_head(ptask) = false -- otherwise
def $tc_return_finally(eps) = eps
def $tc_return_finally((FINALLY_REF_RETURN porigin_owner porigin_source poperand z) :: ptask_tail*) = (FINALLY_REF_RETURN porigin_owner porigin_source poperand z)
def $tc_return_finally(ptask :: ptask_tail*) = $tc_return_finally(ptask_tail*) -- if ~$tc_return_finally_head(ptask)
dec $tc_throw_finally(ptask*) : ptask?
dec $tc_throw_finally_head(ptask) : bool
def $tc_throw_finally_head(FINALLY_RESUME porigin_owner (n_error)) = true
def $tc_throw_finally_head(ptask) = false -- otherwise
def $tc_throw_finally(eps) = eps
def $tc_throw_finally((FINALLY_RESUME porigin_owner (n_error)) :: ptask_tail*) = (FINALLY_RESUME porigin_owner (n_error))
def $tc_throw_finally(ptask :: ptask_tail*) = $tc_throw_finally(ptask_tail*) -- if ~$tc_throw_finally_head(ptask)
dec $tc_stage(pstate, nat) : bool
dec $tc_find(pstate, nat, nat) : pstate
def $tc_find(S, n, n_stage) = S[.COMPLETION = NORMAL]
  -- if $tc_stage(S, n_stage)
  -- if S.COMPLETION = BUDGET
def $tc_find(S, n, n_stage) = $tc_find($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)), n_stage)
  -- if ~$tc_stage(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
dec $tc_resume(pstate, nat) : pstate
def $tc_resume(S, n) = $drive(S[.COMPLETION = NORMAL], n) -- if S.COMPLETION = BUDGET
def $tc_resume(S, n) = S -- otherwise
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    catalogue = ROOT / 'tests/semantics/reference_typed_cv_string_cases.json'
    cases = {row['id']: row for row in json.loads(catalogue.read_text())}
    report_path = args.raw / 'report.json'
    report = json.loads(report_path.read_text())
    assert report['complete'] and report['pins'] == report['pins_after']
    assert report['head_after'] == report['revision'] and report['status_after'] == ''
    rows = {row['id']: row for row in report['records']}
    assert rows.keys() == cases.keys() and len(rows) == 13
    for case, row in rows.items():
        assert row['pass'] and row['model']['status'] == 'normal'
        assert all(row['native'][key] == row['model'][key]
                   for key in ('stdout', 'stderr', 'exit_status'))
        assert base64.b64decode(row['native']['stdout']) == cases[case]['stdout'].encode()
        assert base64.b64decode(row['native']['stderr']) == cases[case]['stderr'].encode() == b''
        assert row['native']['exit_status'] == cases[case]['exit'] == 0
        assert hashlib.sha256(cases[case]['source'].encode()).hexdigest() == row['source_sha256']
    args.output.mkdir(parents=True, exist_ok=True)
    records = []

    def fixture(name, case, stages, checks, bad=(), terminal=()):
        directory = args.raw / case
        facts = json.loads((directory / 'request.json').read_text())
        source = Path(base64.b64decode(facts['file']).decode()).read_bytes()
        assert source == cases[case]['source'].encode()
        parsed = json.loads((directory / 'parsed.json').read_text())
        checked = json.loads((directory / 'checked.json').read_text())
        state = json.loads((directory / 'state.json').read_text())
        assert parsed['accepted'] and checked['ok'] and checked['fixture'] and state['ok']
        start = ('$php_request_run(' + checked['fixture'] + ', 0, ' +
                 json.dumps(facts['file']) + ', ' + request_fixture(facts) + ')')
        stage_text = ''.join(f'def $tc_stage(S, {index}) = true\n' +
                             ''.join('  -- if ' + condition + '\n' for condition in conditions)
                             for index, conditions in stages.items())
        stage_text += 'def $tc_stage(S, n_stage) = false -- otherwise\n'
        assertions = ['S_initial = ' + start, 'S_initial.COMPLETION = BUDGET',
                      'S_start = S_initial[.COMPLETION = NORMAL]',
                      'S = $tc_find(S_start, 2000, 0)', 'S.COMPLETION = NORMAL',
                      '$tc_stage(S, 0)', '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
        assertions += checks
        for index, mutation in enumerate(bad):
            assertions += [f'S_bad{index} = ' + mutation + '[.COMPLETION = NORMAL]',
                           f'~$call_descriptors_valid(S_bad{index})',
                           f'S_rejected{index} = $drive(S_bad{index}, 0)',
                           f'S_rejected{index}.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"']
        assertions += ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
                       'S_one = $tc_resume(S_zero, 1)', 'S_adjacent = $tc_resume(S_one, 10000)',
                       'S_frontier = $drive(S, 10001)', 'S_whole = $drive(S_start, 10001)',
                       'S_adjacent = S_frontier', 'S_frontier = S_whole',
                       'S_whole.COMPLETION = NORMAL', '$tc_outputs(S_whole.EVENTS) = $ptascii(' + json.dumps(cases[case]['stdout']) + ')',
                       '$tc_diagnostics(S_whole.EVENTS) = eps', 'S_whole.CURRENT = eps',
                       'S_whole.FRAMES = eps', 'S_whole.TODO = eps', 'S_whole.HELD = eps',
                       'S_whole.RETIREDOWNERS = eps', '$tc_count(S_whole.TODO) = 0',
                       '$heap_valid($heap_graph(S_whole))', '$call_descriptors_valid(S_whole)'] + list(terminal)
        path = args.output / (name + '.watsup')
        path.write_text(PREFIX + '\n' + stage_text + '\ndec $main() : bool\ndef $main() = true\n' +
                        ''.join('  -- if ' + condition + '\n' for condition in assertions))
        records.append({'id': name, 'source_id': case, 'fixture': str(path.resolve()),
                        'fixture_sha256': sha(path), 'assertions': len(assertions)})

    capture = ['$tc_function(S, $ptascii("f"))', 'S.TODO = (RETURN_REF_FETCH z) :: ptask_tail*',
               '$typed_ref_string_capture(S, z) = (prefstringcv)']
    capture_checks = capture + ['S.ORIGIN = (prefstringcv.SOURCE)', 'prefstringcv.LINE = z',
        '$origin_node(S.SOURCES, prefstringcv.SOURCE) = (NStmtReturn (NExprVariable (BYTES text_x) metadata_variable) metadata)',
        '$base64(text_x) = $ptascii("x")', 'n_cell = prefstringcv.CELL', 'n_object = prefstringcv.OBJECT',
        '$lookup(S.ENV, $ptascii("x")) = (n_cell)', 'S.STORE[n_cell] = DEFINED (POBJECT n_object)',
        '(HCELL n_cell) <- S.ALLOCATIONS', 'n_cell <- S.REFCELLS', '~$typed_reference_cell_source(S, n_cell)',
        'S.GLOBALTABLE = (psymboltable_global)', '$lookup(psymboltable_global.ENV, $ptascii("x")) = (n_cell)',
        '$tc_outputs(S.EVENTS) = eps', '$tc_diagnostics(S.EVENTS) = eps',
        'S_begin = $drive_steps(S, 1)', 'S_begin.COMPLETION = BUDGET',
        'S_begin.TODO = (CALL_ARGS (METHOD_TARGET n_object porigin_method) eps 0 eps (prefstringcv.SOURCE) z) :: (STRINGIFY_RESULT n_object prefstringcv.SOURCE z) :: (REF_STRING_FETCH prefstringcv) :: (REF_STRING_THROW prefstringcv) :: ptask_tail*',
        'S_begin.STORE = S.STORE', 'S_begin.REFCELLS = S.REFCELLS',
        '$typed_ref_string_valid(S_begin, prefstringcv)', '$tc_count(S_begin.TODO) = 2',
        '$task_nodes(REF_STRING_FETCH prefstringcv) = eps', '$task_nodes(REF_STRING_THROW prefstringcv) = eps',
        '$task_nodes(STRINGIFY_RESULT n_object prefstringcv.SOURCE z) = [HOBJECT n_object]',
        '$call_descriptors_valid(S_begin)', '$heap_valid($heap_graph(S_begin))']
    ready = ['$tc_function(S, $ptascii("f"))',
             'S.TODO = (STRINGIFY_RESULT n_object porigin_source z_result) :: (REF_STRING_FETCH prefstringcv) :: (REF_STRING_THROW prefstringcv) :: ptask_result_tail*',
             'S.RESULT = KNOWN pvalue_text', '$string_bytes(pvalue_text) = (n_text*)']

    fixture('capture-selected-cv', 'baseline/typed-return-reference-control',
            {0: capture, 1: ready}, capture_checks + [
                'S_result = $tc_find(S_begin, 2000, 1)',
                'S_result.TODO = (STRINGIFY_RESULT n_object prefstringcv.SOURCE z) :: (REF_STRING_FETCH prefstringcv) :: (REF_STRING_THROW prefstringcv) :: ptask_tail*',
                '$lookup(S_result.ENV, $ptascii("x")) = (n_cell)',
                'S_result.RESULT = KNOWN pvalue_text', '$string_bytes(pvalue_text) = ($ptascii("x"))',
                'S_result.STORE[n_cell] = DEFINED (POBJECT n_object)',
                '$call_descriptors_valid(S_result)', '$heap_valid($heap_graph(S_result))',
                'S_converted = $drive_steps(S_result, 1)',
                'S_converted.TODO = (RETURN_REF_UNWIND (REFERENCE n_cell) z false prefstringcv.SOURCE) :: ptask_tail*',
                'S_converted.STORE[n_cell] = DEFINED pvalue_text', '|S_converted.STORE| = |S_result.STORE|',
                '$tc_count(S_converted.TODO) = 0', '$call_descriptors_valid(S_converted)',
                '$heap_valid($heap_graph(S_converted))'], bad=[
                'S_begin[.TODO = (CALL_ARGS (METHOD_TARGET n_object porigin_method) eps 0 eps (prefstringcv.SOURCE) z) :: (STRINGIFY_RESULT n_object prefstringcv.SOURCE z) :: (REF_STRING_FETCH (prefstringcv[.LINE = $(z + 1)])) :: (REF_STRING_THROW prefstringcv) :: ptask_tail*]',
                'S_result[.TODO = (STRINGIFY_RESULT n_object prefstringcv.SOURCE z) :: (REF_STRING_FETCH (prefstringcv[.CELL = |S_result.STORE|])) :: (REF_STRING_THROW prefstringcv) :: ptask_tail*]',
                'S_result[.TODO = (STRINGIFY_RESULT n_object prefstringcv.SOURCE z) :: (REF_STRING_THROW prefstringcv) :: (REF_STRING_FETCH prefstringcv) :: ptask_tail*]',
                'S_result[.TODO = (STRINGIFY_RESULT n_object prefstringcv.SOURCE z) :: (REF_STRING_FETCH prefstringcv) :: ptask_tail*]',
                'S_result[.TODO = (STRINGIFY_RESULT n_object prefstringcv.SOURCE z) :: (REF_STRING_FETCH prefstringcv) :: (REF_STRING_THROW prefstringcv) :: (REF_STRING_THROW prefstringcv) :: ptask_tail*]',
            ], terminal=['$lookup(S_whole.ENV, $ptascii("x")) = (n_cell)',
                         '$lookup(S_whole.ENV, $ptascii("y")) = (n_cell)', 'S_whole.STORE[n_cell] = DEFINED pvalue_text'])

    saved = ['$tc_function(S, $ptascii("O::__toString"))', 'S.FRAMES = pframe :: pframe_tail*',
             'pframe.TODO = (STRINGIFY_RESULT n_object porigin_source z_result) :: (REF_STRING_FETCH prefstringcv) :: (REF_STRING_THROW prefstringcv) :: ptask_result_tail*']
    for kind in ('rebind', 'unset'):
        namespace = ['S.GLOBALTABLE = (psymboltable_changed)', '$lookup(psymboltable_changed.ENV, $ptascii("other")) = (n_other)',
                     'n_other =/= prefstringcv.CELL']
        namespace += (['$lookup(psymboltable_changed.ENV, $ptascii("x")) = (n_other)'] if kind == 'rebind'
                      else ['$lookup(psymboltable_changed.ENV, $ptascii("x")) = eps'])
        stages = {0: capture, 1: saved + namespace, 2: ready}
        checks = capture_checks + ['S_saved = $tc_find(S_begin, 2000, 1)',
            '$tc_function(S_saved, $ptascii("O::__toString"))', 'S_saved.FRAMES = pframe :: pframe_tail*',
            'pframe.TODO = (STRINGIFY_RESULT n_object prefstringcv.SOURCE z) :: (REF_STRING_FETCH prefstringcv) :: (REF_STRING_THROW prefstringcv) :: ptask_tail*',
            'pframe.LOCALS = (psymboltable_f)', '$lookup(psymboltable_f.ENV, $ptascii("x")) = (n_cell)',
            'S_scope = $constant_frame_scope(S_saved, pframe, pframe_tail*)',
            '$parameter_string_frame_scope(S_saved, pframe, pframe_tail*) = S_scope',
            '$tc_function(S_scope, $ptascii("f"))', '$lookup(S_scope.ENV, $ptascii("x")) = (n_cell)',
            '$typed_ref_string_valid(S_scope, prefstringcv)', '$call_tasks_valid(S_scope, pframe.TODO)',
            '$stringify_chain_valid(S_saved, S_saved.CURRENT, S_saved.FRAMES)',
            '$stringify_frames_pairs_valid(S_saved, S_saved.FRAMES)',
            '$call_descriptors_valid(S_saved)', '$heap_valid($heap_graph(S_saved))',
            'S_saved.CURRENT = (pcallcontext_callback)', 'pcallcontext_callback.CALLSITE = pframe.ORIGIN',
            'pcallcontext_callback.LINE = z', '$context_target(pcallcontext_callback) = METHOD_TARGET n_object porigin_method',
            'S_saved.GLOBALTABLE = (psymboltable_changed)', '$lookup(psymboltable_changed.ENV, $ptascii("other")) = (n_other)',
            'n_other =/= n_cell', 'S_saved.STORE[n_other] = DEFINED pvalue_other', '$string_bytes(pvalue_other) = ($ptascii("o"))',
            'S_saved.STORE[n_cell] = DEFINED (POBJECT n_object)', '$tc_outputs(S_saved.EVENTS) = $ptascii("T;")',
            '$tc_count(S_saved.TODO) = 0', '$tc_count(pframe.TODO) = 2',
            '~((HCELL n_cell) <- $tasks_nodes(pframe.TODO))',
            'S_result = $tc_find($drive_steps(S_saved, 1), 2000, 2)',
            'S_result.TODO = pframe.TODO', 'S_result.ORIGIN = pframe.ORIGIN', 'S_result.CURRENT = pframe.CONTEXT',
            'S_result.ENV = psymboltable_f.ENV', '$lookup(S_result.ENV, $ptascii("x")) = (n_cell)',
            'S_result.RESULT = KNOWN pvalue_text', '$string_bytes(pvalue_text) = ($ptascii("s"))',
            'S_result.STORE[n_cell] = DEFINED (POBJECT n_object)',
            '$call_descriptors_valid(S_result)', '$heap_valid($heap_graph(S_result))',
            'S_converted = $drive_steps(S_result, 1)',
            'S_converted.TODO = (RETURN_REF_UNWIND (REFERENCE n_cell) z false prefstringcv.SOURCE) :: ptask_tail*',
            'S_converted.STORE[n_cell] = DEFINED pvalue_text', 'S_converted.STORE[n_other] = DEFINED pvalue_other',
            '|S_converted.STORE| = |S_result.STORE|', '$tc_count(S_converted.TODO) = 0',
            '$call_descriptors_valid(S_converted)', '$heap_valid($heap_graph(S_converted))']
        checks += [('$lookup(psymboltable_changed.ENV, $ptascii("x")) = (n_other)' if kind == 'rebind'
                    else '$lookup(psymboltable_changed.ENV, $ptascii("x")) = eps')]
        bad = ['S_saved[.FRAMES = pframe[.TODO = (STRINGIFY_RESULT n_object prefstringcv.SOURCE z) :: (REF_STRING_FETCH (prefstringcv[.SOURCE = porigin_method])) :: (REF_STRING_THROW prefstringcv) :: ptask_tail*] :: pframe_tail*]',
               'S_saved[.FRAMES = pframe[.TODO = (STRINGIFY_RESULT n_object prefstringcv.SOURCE z) :: (REF_STRING_FETCH prefstringcv) :: (REF_STRING_THROW (prefstringcv[.LINE = $(z + 1)])) :: ptask_tail*] :: pframe_tail*]',
               'S_saved[.FRAMES = pframe[.TODO = (STRINGIFY_RESULT n_object prefstringcv.SOURCE z) :: (REF_STRING_THROW prefstringcv) :: (REF_STRING_FETCH prefstringcv) :: ptask_tail*] :: pframe_tail*]']
        if kind == 'rebind':
            checks += ['$call_reference_operand_valid(S_scope, REFERENCE n_other)', '~$typed_reference_cell_source(S_scope, n_other)',
                       'prefstringcv_wrongcell = prefstringcv[.CELL = n_other]',
                       'pframe_wrongcell = pframe[.TODO = (STRINGIFY_RESULT n_object prefstringcv.SOURCE z) :: (REF_STRING_FETCH prefstringcv_wrongcell) :: (REF_STRING_THROW prefstringcv_wrongcell) :: ptask_tail*]',
                       'S_saved_wrongcell = S_saved[.FRAMES = pframe_wrongcell :: pframe_tail*]',
                       'S_scope_wrongcell = $constant_frame_scope(S_saved_wrongcell, pframe_wrongcell, pframe_tail*)',
                       '$lookup(S_scope_wrongcell.ENV, $ptascii("x")) = (n_cell)',
                       '$typed_ref_string_shape(S_scope_wrongcell, prefstringcv_wrongcell)',
                       '~$typed_ref_string_valid(S_scope_wrongcell, prefstringcv_wrongcell)',
                       'S_result_wrongcell = S_result[.TODO = pframe_wrongcell.TODO]',
                       '$lookup(S_result_wrongcell.ENV, $ptascii("x")) = (n_cell)',
                       '$typed_ref_string_shape(S_result_wrongcell, prefstringcv_wrongcell)',
                       '~$typed_ref_string_valid(S_result_wrongcell, prefstringcv_wrongcell)']
            bad += ['S_saved_wrongcell', 'S_result_wrongcell']
        final = ['$lookup(S_whole.ENV, $ptascii("old")) = (n_cell)', '$lookup(S_whole.ENV, $ptascii("r")) = (n_cell)',
                 'S_whole.STORE[n_cell] = DEFINED pvalue_written', '$string_bytes(pvalue_written) = ($ptascii("q"))',
                 '$lookup(S_whole.ENV, $ptascii("other")) = (n_other)', 'S_whole.STORE[n_other] = DEFINED pvalue_other',
                 ('$lookup(S_whole.ENV, $ptascii("x")) = (n_other)' if kind == 'rebind'
                  else '$lookup(S_whole.ENV, $ptascii("x")) = eps')]
        fixture(kind + '-saved-selected-cell', 'cv-binding/' + kind + '-protected-used', stages, checks, bad, final)

    for kind, protected in [('rebind', False), ('unset', True)]:
        case = 'cv-binding/' + kind + ('-protected-unused' if protected else '-plain-unused')
        checks = capture_checks + ['~$reference_return_used(S)', 'S_result = $tc_find(S_begin, 2000, 1)',
            'S_result.TODO = (STRINGIFY_RESULT n_object prefstringcv.SOURCE z) :: (REF_STRING_FETCH prefstringcv) :: (REF_STRING_THROW prefstringcv) :: ptask_tail*',
            '$lookup(S_result.ENV, $ptascii("x")) = (n_cell)', 'S_result.RESULT = KNOWN pvalue_text',
            '$string_bytes(pvalue_text) = ($ptascii("s"))', 'S_result.STORE[n_cell] = DEFINED (POBJECT n_object)',
            '$call_descriptors_valid(S_result)', '$heap_valid($heap_graph(S_result))',
            'S_converted = $drive_steps(S_result, 1)', 'S_converted.STORE[n_cell] = DEFINED pvalue_text',
            '|S_converted.STORE| = |S_result.STORE|', 'S_converted.REFCELLS = S_result.REFCELLS',
            '$tc_count(S_converted.TODO) = 0', '$call_descriptors_valid(S_converted)', '$heap_valid($heap_graph(S_converted))']
        operand = '(REFERENCE n_cell)' if protected else '(KNOWN PNULL)'
        checks += [f'S_converted.TODO = (RETURN_REF_UNWIND {operand} z false prefstringcv.SOURCE) :: ptask_tail*']
        stages = {0: capture, 1: ready}
        if protected:
            stages[2] = ['$tc_function(S, $ptascii("f"))', '$tc_return_finally(S.TODO) = (FINALLY_REF_RETURN porigin_owner porigin_source poperand z_final)',
                         '$tc_outputs(S.EVENTS) = $ptascii("T;")']
            checks += ['S_finally = $tc_find(S_converted, 2000, 2)',
                       '$tc_return_finally(S_finally.TODO) = (FINALLY_REF_RETURN porigin_owner prefstringcv.SOURCE (REFERENCE n_cell) z)',
                       '$lookup(S_finally.ENV, $ptascii("x")) = (n_cell)', 'S_finally.STORE[n_cell] = DEFINED pvalue_text',
                       '$call_descriptors_valid(S_finally)', '$heap_valid($heap_graph(S_finally))',
                       '$tc_count(S_finally.TODO) = 0', '$tc_diagnostics(S_finally.EVENTS) = eps']
        fixture(('protected' if protected else 'plain') + '-unused-conversion', case, stages, checks,
                terminal=['$lookup(S_whole.ENV, $ptascii("old")) = (n_cell)', 'S_whole.STORE[n_cell] = DEFINED pvalue_text',
                          '$lookup(S_whole.ENV, $ptascii("r")) = eps'])

    error_ready = ['$tc_function(S, $ptascii("f"))',
                   'S.TODO = (THROW_SEARCH n_old) :: (STRINGIFY_RESULT n_object porigin_source z_result) :: (REF_STRING_FETCH prefstringcv) :: (REF_STRING_THROW prefstringcv) :: ptask_result_tail*']
    for protected, used in [(True, True), (False, False)]:
        case = 'live-error/' + ('protected' if protected else 'plain') + ('-used' if used else '-unused')
        saved_written = saved + ['S.STORE[prefstringcv.CELL] = DEFINED (PINT 7)', '$tc_outputs(S.EVENTS) = $ptascii("T;")']
        stages = {0: capture, 1: saved_written, 2: error_ready}
        checks = capture_checks + ['S_saved = $tc_find(S_begin, 2000, 1)',
            'S_saved.FRAMES = pframe :: pframe_tail*',
            'pframe.TODO = (STRINGIFY_RESULT n_object prefstringcv.SOURCE z) :: (REF_STRING_FETCH prefstringcv) :: (REF_STRING_THROW prefstringcv) :: ptask_tail*',
            'pframe.LOCALS = (psymboltable_f)', '$lookup(psymboltable_f.ENV, $ptascii("x")) = (n_cell)',
            'S_scope = $constant_frame_scope(S_saved, pframe, pframe_tail*)',
            '$typed_ref_string_valid(S_scope, prefstringcv)', 'S_saved.STORE[n_cell] = DEFINED (PINT 7)',
            '$stringable_instance(S_saved, n_object)', '$tc_outputs(S_saved.EVENTS) = $ptascii("T;")',
            '$stringify_chain_valid(S_saved, S_saved.CURRENT, S_saved.FRAMES)',
            '$call_descriptors_valid(S_saved)', '$heap_valid($heap_graph(S_saved))',
            'S_error = $tc_find($drive_steps(S_saved, 1), 2000, 2)',
            'S_error.TODO = (THROW_SEARCH n_old) :: (STRINGIFY_RESULT n_object prefstringcv.SOURCE z) :: (REF_STRING_FETCH prefstringcv) :: (REF_STRING_THROW prefstringcv) :: ptask_tail*',
            'S_error.ENV = psymboltable_f.ENV', '$lookup(S_error.ENV, $ptascii("x")) = (n_cell)',
            'S_error.STORE[n_cell] = DEFINED (PINT 7)', '$typed_return_throw_pending(S_error)',
            '$throwable_live(S_error, n_old)', '$string_bytes($throwable_field(S_error, n_old, "message")) = ($ptascii("callback"))',
            '$call_descriptors_valid(S_error)', '$heap_valid($heap_graph(S_error))',
            'S_new = $drive_steps(S_error, 1)', 'S_new.TODO = (THROW_SEARCH n_new) :: ptask_tail*',
            'n_new =/= n_old', '$throwable_live(S_new, n_new)', '$throwable_live(S_new, n_old)',
            'S_new.OBJECTS[n_new] = THROWABLE pthrowable_new', 'pthrowable_new.KIND = "TypeError"',
            '$string_bytes($throwable_field(S_new, n_new, "message")) = ($ptascii("f(): Return value must be of type string, int returned"))',
            '$throwable_field(S_new, n_new, "previous") = POBJECT n_old',
            'S_new.STORE[n_cell] = DEFINED (PINT 7)', '$tc_count(S_new.TODO) = 0',
            'S_new.RESULT = KNOWN PNULL', 'S_new.BASE = BASE_VALUE (KNOWN PNULL)',
            '$tc_diagnostics(S_new.EVENTS) = eps', '$tc_outputs(S_new.EVENTS) = $ptascii("T;")',
            '$call_descriptors_valid(S_new)', '$heap_valid($heap_graph(S_new))']
        if protected:
            stages[3] = ['$tc_function(S, $ptascii("f"))', '$tc_throw_finally(S.TODO) = (FINALLY_RESUME porigin_owner (n_error))',
                         '$tc_outputs(S.EVENTS) = $ptascii("T;")']
            checks += ['S_finally = $tc_find(S_new, 2000, 3)',
                       '$tc_throw_finally(S_finally.TODO) = (FINALLY_RESUME porigin_owner (n_new))',
                       'S_finally.STORE[n_cell] = DEFINED (PINT 7)', '$tc_return_finally(S_finally.TODO) = eps',
                       '$tc_count(S_finally.TODO) = 0', '$throwable_live(S_finally, n_new)',
                       '$throwable_field(S_finally, n_new, "previous") = POBJECT n_old',
                       '$call_descriptors_valid(S_finally)', '$heap_valid($heap_graph(S_finally))']
        fixture(('protected' if protected else 'plain') + '-live-value-callback-error', case, stages, checks, bad=[
            'S_error[.TODO = (THROW_SEARCH n_old) :: (STRINGIFY_RESULT n_object prefstringcv.SOURCE z) :: (REF_STRING_FETCH (prefstringcv[.OBJECT = n_old])) :: (REF_STRING_THROW prefstringcv) :: ptask_tail*]',
            'S_error[.TODO = (THROW_SEARCH n_old) :: (STRINGIFY_RESULT n_object prefstringcv.SOURCE z) :: (REF_STRING_THROW prefstringcv) :: (REF_STRING_FETCH prefstringcv) :: ptask_tail*]',
        ], terminal=['$lookup(S_whole.ENV, $ptascii("x")) = (n_cell)', 'S_whole.STORE[n_cell] = DEFINED (PINT 7)',
                     '$lookup(S_whole.ENV, $ptascii("e")) = (n_error_cell)', 'S_whole.STORE[n_error_cell] = DEFINED (POBJECT n_new)',
                     '$throwable_live(S_whole, n_new)', '$throwable_field(S_whole, n_new, "previous") = POBJECT n_old'])

    # Source and marker forgeries share the genuine pre-callback current frame.
    fixture('current-certificate-admission', 'cv-binding/rebind-plain-used', {0: capture}, capture_checks + [
        'S.CURRENT = (pcallcontext_f)', '$function_at($all_functions(S), pcallcontext_f.FUNCTION) = (pfunction_f)',
        'prefstringcv_line = prefstringcv[.LINE = $(z + 1)]',
        'prefstringcv_source = prefstringcv[.SOURCE = porigin_method]',
        'prefstringcv_object = prefstringcv[.OBJECT = |S.OBJECTS|]',
    ], bad=[
        'S_begin[.TODO = (CALL_ARGS (METHOD_TARGET n_object porigin_method) eps 0 eps (prefstringcv.SOURCE) z) :: (STRINGIFY_RESULT n_object prefstringcv.SOURCE z) :: (REF_STRING_FETCH prefstringcv_line) :: (REF_STRING_THROW prefstringcv_line) :: ptask_tail*]',
        'S_begin[.TODO = (CALL_ARGS (METHOD_TARGET n_object porigin_method) eps 0 eps (prefstringcv.SOURCE) z) :: (STRINGIFY_RESULT n_object prefstringcv.SOURCE z) :: (REF_STRING_FETCH prefstringcv_source) :: (REF_STRING_THROW prefstringcv_source) :: ptask_tail*]',
        'S_begin[.TODO = (CALL_ARGS (METHOD_TARGET n_object porigin_method) eps 0 eps (prefstringcv.SOURCE) z) :: (STRINGIFY_RESULT n_object prefstringcv.SOURCE z) :: (REF_STRING_FETCH prefstringcv_object) :: (REF_STRING_THROW prefstringcv_object) :: ptask_tail*]',
        'S_begin[.ORIGIN = (porigin_method)]',
        'S_begin[.TODO = (CALL_ARGS (METHOD_TARGET n_object porigin_method) eps 0 eps (prefstringcv.SOURCE) z) :: (STRINGIFY_RESULT n_object prefstringcv.SOURCE z) :: (REF_STRING_FETCH prefstringcv) :: (REF_STRING_FETCH prefstringcv) :: (REF_STRING_THROW prefstringcv) :: ptask_tail*]',
    ])
    manifest = {'producer': str(Path(__file__).resolve()), 'producer_sha256': sha(Path(__file__)),
                'catalogue_sha256': sha(catalogue),
                'model_report': str(report_path.resolve()), 'model_report_sha256': sha(report_path),
                'model_revision': report['revision'], 'fixtures': records,
                'assertions': sum(row['assertions'] for row in records),
                'scope': 'Aliased, live unconstrained CV cells; metadata is non-owning. No released nonreference-CV or destructor timing claim.'}
    (args.output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'fixtures': len(records), 'assertions': manifest['assertions']}))


if __name__ == '__main__':
    main()
