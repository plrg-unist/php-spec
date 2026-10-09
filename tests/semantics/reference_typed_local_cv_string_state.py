"""Emit reached local-CV conversion, destructor and return-lifetime fixtures."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
from request_environment_state import request_fixture
from reference_typed_cv_string_state import PREFIX as ALIAS_PREFIX

PREFIX = ALIAS_PREFIX.replace('$tc_', '$lc_').replace('typed_ref_string_task', 'typed_cv_string_task') + r'''
dec $lc_copy_head(ptask, prefstringcv) : bool
def $lc_copy_head(REF_CV_STRING_COPY prefstringcv pvalue, prefstringcv) = true
def $lc_copy_head(ptask, prefstringcv) = false -- otherwise
dec $lc_copy_replace(ptask*, prefstringcv, ptask*) : ptask*
def $lc_copy_replace((REF_CV_STRING_COPY prefstringcv pvalue) :: ptask_tail*, prefstringcv, ptask_new*) = ptask_new* ++ ptask_tail*
def $lc_copy_replace(ptask :: ptask_tail*, prefstringcv, ptask_new*) = ptask :: $lc_copy_replace(ptask_tail*, prefstringcv, ptask_new*)
  -- if ~$lc_copy_head(ptask, prefstringcv)
def $lc_copy_replace(eps, prefstringcv, ptask_new*) = eps
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    catalogue = ROOT / 'tests/semantics/reference_typed_local_cv_string_cases.json'
    cases = {row['id']: row for row in json.loads(catalogue.read_text())}
    report_path = args.raw / 'report.json'
    report = json.loads(report_path.read_text())
    assert report['complete'] and report['pins'] == report['pins_after']
    assert report['head_after'] == report['revision'] and report['status_after'] == ''
    rows = {row['id']: row for row in report['records']}
    assert rows.keys() == cases.keys() and len(rows) == 5
    for case, row in rows.items():
        assert row['pass'] and row['model']['status'] == 'normal'
        assert all(row['native'][key] == row['model'][key] for key in ('stdout', 'stderr', 'exit_status'))
        assert base64.b64decode(row['native']['stdout']) == cases[case]['stdout'].encode()
        assert base64.b64decode(row['native']['stderr']) == cases[case]['stderr'].encode() == b''
        assert row['native']['exit_status'] == cases[case]['exit'] == 0
        assert hashlib.sha256(cases[case]['source'].encode()).hexdigest() == row['source_sha256']
    args.output.mkdir(parents=True, exist_ok=True)
    records = []

    def fixture(name, case, stages, checks, bad=(), terminal=()):
        directory = args.raw / case
        facts = json.loads((directory / 'request.json').read_text())
        assert Path(base64.b64decode(facts['file']).decode()).read_bytes() == cases[case]['source'].encode()
        parsed = json.loads((directory / 'parsed.json').read_text())
        checked = json.loads((directory / 'checked.json').read_text())
        state = json.loads((directory / 'state.json').read_text())
        assert parsed['accepted'] and checked['ok'] and checked['fixture'] and state['ok']
        start = ('$php_request_run(' + checked['fixture'] + ', 0, ' +
                 json.dumps(facts['file']) + ', ' + request_fixture(facts) + ')')
        stage_text = ''.join(f'def $lc_stage(S, {index}) = true\n' +
                             ''.join('  -- if ' + condition + '\n' for condition in conditions)
                             for index, conditions in stages.items())
        stage_text += 'def $lc_stage(S, n_stage) = false -- otherwise\n'
        assertions = ['S_initial = ' + start, 'S_initial.COMPLETION = BUDGET',
                      'S_start = S_initial[.COMPLETION = NORMAL]',
                      'S = $lc_find(S_start, 2000, 0)', 'S.COMPLETION = NORMAL',
                      '$lc_stage(S, 0)', '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))'] + checks
        for index, mutation in enumerate(bad):
            assertions += [f'S_bad{index} = ' + mutation + '[.COMPLETION = NORMAL]',
                           f'~$call_descriptors_valid(S_bad{index})',
                           f'S_rejected{index} = $drive(S_bad{index}, 0)',
                           f'S_rejected{index}.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"']
        assertions += ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
                       'S_one = $lc_resume(S_zero, 1)', 'S_adjacent = $lc_resume(S_one, 10000)',
                       'S_frontier = $drive(S, 10001)', 'S_whole = $drive(S_start, 10001)',
                       'S_adjacent = S_frontier', 'S_frontier = S_whole',
                       'S_whole.COMPLETION = NORMAL', '$lc_outputs(S_whole.EVENTS) = $ptascii(' + json.dumps(cases[case]['stdout']) + ')',
                       '$lc_diagnostics(S_whole.EVENTS) = eps', 'S_whole.CURRENT = eps',
                       'S_whole.FRAMES = eps', 'S_whole.TODO = eps', 'S_whole.HELD = eps',
                       'S_whole.RETIREDOWNERS = eps', '$lc_count(S_whole.TODO) = 0',
                       '$heap_valid($heap_graph(S_whole))', '$call_descriptors_valid(S_whole)'] + list(terminal)
        path = args.output / (name + '.watsup')
        path.write_text(PREFIX + '\n' + stage_text + '\ndec $main() : bool\ndef $main() = true\n' +
                        ''.join('  -- if ' + condition + '\n' for condition in assertions))
        records.append({'id': name, 'source_id': case, 'fixture': str(path.resolve()),
                        'fixture_sha256': sha(path), 'assertions': len(assertions)})

    capture = ['$lc_function(S, $ptascii("f"))', 'S.TODO = (RETURN_REF_FETCH z) :: ptask_tail*',
               '$typed_cv_string_capture(S, z) = (prefstringcv)']
    saved = ['$lc_function(S, $ptascii("O::__toString"))', 'S.FRAMES = pframe :: pframe_tail*',
             'pframe.TODO = (STRINGIFY_RESULT n_object porigin_source z_result) :: (REF_CV_STRING_FETCH prefstringcv) :: (REF_CV_STRING_THROW prefstringcv) :: ptask_conversion_tail*']
    ready = ['$lc_function(S, $ptascii("f"))',
             'S.TODO = (STRINGIFY_RESULT n_object porigin_source z_result) :: (REF_CV_STRING_FETCH prefstringcv) :: (REF_CV_STRING_THROW prefstringcv) :: ptask_conversion_tail*',
             'S.RESULT = KNOWN pvalue_text', '$string_bytes(pvalue_text) = ($ptascii("s"))']
    destructor = ['$lc_function(S, $ptascii("O::__destruct"))', 'S.FRAMES = pframe :: pframe_tail*',
                  'pframe.LOCALS = (psymboltable_f)', '$lookup(psymboltable_f.ENV, $ptascii("x")) = (n_cell)',
                  '$typed_cv_string_copy_at(pframe.TODO, n_cell) = ((prefstringcv, pvalue_text))',
                  '$lc_outputs(S.EVENTS) = $ptascii("T;")']
    copy_ready = ['$lc_function(S, $ptascii("f"))',
                  'S.TODO = (REF_CV_STRING_COPY prefstringcv pvalue_text) :: ptask_conversion_tail*',
                  '$lc_outputs(S.EVENTS) = $ptascii("T;D;")']

    def capture_checks(protected, used):
        checks = capture + ['S.ORIGIN = (prefstringcv.SOURCE)', 'prefstringcv.LINE = z',
            '$origin_node(S.SOURCES, prefstringcv.SOURCE) = (NStmtReturn (NExprVariable (BYTES text_x) metadata_variable) metadata)',
            '$base64(text_x) = $ptascii("x")', 'n_cell = prefstringcv.CELL', 'n_object = prefstringcv.OBJECT',
            '$lookup(S.ENV, $ptascii("x")) = (n_cell)', 'S.STORE[n_cell] = DEFINED (POBJECT n_object)',
            '(HCELL n_cell) <- S.ALLOCATIONS', '(HOBJECT n_object) <- S.ALLOCATIONS', '~(n_cell <- S.REFCELLS)',
            '$heap_owners($heap_graph(S), HCELL n_cell) = 1', '$node_children(S, HCELL n_cell) = [HOBJECT n_object]',
            '~$typed_reference_cell_source(S, n_cell)',
            ('$finally_return_pending(S)' if protected else '~$finally_return_pending(S)'),
            ('$reference_return_used(S)' if used else '~$reference_return_used(S)'),
            '$lc_outputs(S.EVENTS) = eps', '$lc_diagnostics(S.EVENTS) = eps',
            'S_begin = $drive_steps(S, 1)', 'S_begin.COMPLETION = BUDGET',
            'S_begin.TODO = (CALL_ARGS (METHOD_TARGET n_object porigin_method) eps 0 eps (prefstringcv.SOURCE) z) :: (STRINGIFY_RESULT n_object prefstringcv.SOURCE z) :: (REF_CV_STRING_FETCH prefstringcv) :: (REF_CV_STRING_THROW prefstringcv) :: ptask_conversion_tail*',
            'S_begin.STORE = S.STORE', 'S_begin.ALLOCATIONS = S.ALLOCATIONS',
            '$typed_cv_string_valid(S_begin, prefstringcv)',
            '$task_nodes(REF_CV_STRING_FETCH prefstringcv) = eps', '$task_nodes(REF_CV_STRING_THROW prefstringcv) = eps',
            '$task_nodes(STRINGIFY_RESULT n_object prefstringcv.SOURCE z) = [HOBJECT n_object]',
            '$call_descriptors_valid(S_begin)', '$heap_valid($heap_graph(S_begin))']
        checks += ['ptask_conversion_tail* = (REF_CV_STRING_TEMP prefstringcv) :: ptask_tail*',
                   'n_cell <- S_begin.REFCELLS', '$heap_owners($heap_graph(S_begin), HCELL n_cell) = 2',
                   '$task_nodes(REF_CV_STRING_TEMP prefstringcv) = [HCELL n_cell]', '$lc_count(S_begin.TODO) = 3'] if protected else [
                   'ptask_conversion_tail* = ptask_tail*', 'S_begin.REFCELLS = S.REFCELLS',
                   '$heap_owners($heap_graph(S_begin), HCELL n_cell) = 1', '$lc_count(S_begin.TODO) = 2']
        return checks

    def saved_checks(protected):
        return ['S_saved = $lc_find(S_begin, 2000, 1)', '$lc_function(S_saved, $ptascii("O::__toString"))',
            'S_saved.FRAMES = pframe :: pframe_tail*',
            'pframe.TODO = (STRINGIFY_RESULT n_object prefstringcv.SOURCE z) :: (REF_CV_STRING_FETCH prefstringcv) :: (REF_CV_STRING_THROW prefstringcv) :: ptask_conversion_tail*',
            'pframe.LOCALS = (psymboltable_f)', '$lookup(psymboltable_f.ENV, $ptascii("x")) = (n_cell)',
            'S_scope = $constant_frame_scope(S_saved, pframe, pframe_tail*)', '$lc_function(S_scope, $ptascii("f"))',
            '$typed_cv_string_valid(S_scope, prefstringcv)', 'S_saved.STORE[n_cell] = DEFINED (POBJECT n_object)',
            ('$heap_owners($heap_graph(S_saved), HCELL n_cell) = 2' if protected else '$heap_owners($heap_graph(S_saved), HCELL n_cell) = 1'),
            ('n_cell <- S_saved.REFCELLS' if protected else '~(n_cell <- S_saved.REFCELLS)'),
            '$node_children(S_saved, HCELL n_cell) = [HOBJECT n_object]',
            '$stringify_chain_valid(S_saved, S_saved.CURRENT, S_saved.FRAMES)',
            '$stringify_frames_pairs_valid(S_saved, S_saved.FRAMES)', '$call_descriptors_valid(S_saved)', '$heap_valid($heap_graph(S_saved))']

    for protected, used in [(False, False), (True, True)]:
        case = 'local-cv-string-' + ('protected-used' if protected else 'plain-unused')
        fixture(('protected-owning-temp' if protected else 'plain-borrowed-cv') + '-callback', case,
                {0: capture, 1: saved}, capture_checks(protected, used) + saved_checks(protected),
                terminal=(['$lookup(S_whole.ENV, $ptascii("r")) = (n_cell)',
                    'S_whole.STORE[n_cell] = DEFINED pvalue_written', '$string_bytes(pvalue_written) = ($ptascii("changed"))'] if used else [
                    '~((HCELL n_cell) <- S_whole.ALLOCATIONS)', '~(n_cell <- S_whole.REFCELLS)', '$lookup(S_whole.ENV, $ptascii("r")) = eps']))

    def destructor_checks(protected):
        checks = ['S_destructor = $lc_find(S_begin, 2000, 1)', '$lc_function(S_destructor, $ptascii("O::__destruct"))',
            'S_destructor.FRAMES = pframe :: pframe_tail*', 'pframe.LOCALS = (psymboltable_f)',
            '$lookup(psymboltable_f.ENV, $ptascii("x")) = (n_cell)',
            '$typed_cv_string_copy_at(pframe.TODO, n_cell) = ((prefstringcv, pvalue_text))',
            '$string_bytes(pvalue_text) = ($ptascii("s"))',
            'S_scope = $constant_frame_scope(S_destructor, pframe, pframe_tail*)', '$lc_function(S_scope, $ptascii("f"))',
            '$typed_cv_string_copy_valid(S_scope, prefstringcv, pvalue_text)',
            'S_destructor.STORE[n_cell] = DEFINED (POBJECT n_object)',
            '(HCELL n_cell) <- S_destructor.ALLOCATIONS', '(HOBJECT n_object) <- S_destructor.ALLOCATIONS',
            '$typed_cv_string_released_cell(S_destructor, n_cell)', '$node_children(S_destructor, HCELL n_cell) = eps',
            '$task_nodes(REF_CV_STRING_COPY prefstringcv pvalue_text) = $value_nodes(pvalue_text)',
            '~((HCELL n_cell) <- $task_nodes(REF_CV_STRING_COPY prefstringcv pvalue_text))',
            '~((HOBJECT n_object) <- $task_nodes(REF_CV_STRING_COPY prefstringcv pvalue_text))',
            ('$heap_owners($heap_graph(S_destructor), HCELL n_cell) = 2' if protected else '$heap_owners($heap_graph(S_destructor), HCELL n_cell) = 1'),
            '$lc_outputs(S_destructor.EVENTS) = $ptascii("T;")', '$call_descriptors_valid(S_destructor)', '$heap_valid($heap_graph(S_destructor))',
            'S_copy = $lc_find($drive_steps(S_destructor, 1), 2000, 2)',
            'S_copy.TODO = (REF_CV_STRING_COPY prefstringcv pvalue_text) :: ptask_conversion_tail*',
            'S_copy.ENV = psymboltable_f.ENV', '$lookup(S_copy.ENV, $ptascii("x")) = (n_cell)',
            'S_copy.STORE[n_cell] = DEFINED (POBJECT n_object)', '(HCELL n_cell) <- S_copy.ALLOCATIONS',
            '~((HOBJECT n_object) <- S_copy.ALLOCATIONS)', '$typed_cv_string_copy_valid(S_copy, prefstringcv, pvalue_text)',
            '$typed_cv_string_released_cell(S_copy, n_cell)', '$node_children(S_copy, HCELL n_cell) = eps',
            '$lc_outputs(S_copy.EVENTS) = $ptascii("T;D;")', '$call_descriptors_valid(S_copy)', '$heap_valid($heap_graph(S_copy))',
            'S_written = $drive_steps(S_copy, 1)', 'S_written.COMPLETION = BUDGET',
            'S_written.TODO = (RETURN_REF_UNWIND (REFERENCE n_cell) z false prefstringcv.SOURCE) :: ptask_tail*',
            'S_written.STORE[n_cell] = DEFINED pvalue_text', '|S_written.STORE| = |S_copy.STORE|',
            '$lc_count(S_written.TODO) = 0', 'n_cell <- S_written.REFCELLS',
            '$heap_owners($heap_graph(S_written), HCELL n_cell) = 2',
            '~((HOBJECT n_object) <- S_written.ALLOCATIONS)', '$lc_outputs(S_written.EVENTS) = $ptascii("T;D;")',
            '$call_descriptors_valid(S_written)', '$heap_valid($heap_graph(S_written))']
        return checks

    alias_terminal = ['$lookup(S_whole.ENV, $ptascii("r")) = (n_cell)', 'n_cell <- S_whole.REFCELLS',
                      'S_whole.STORE[n_cell] = DEFINED pvalue_written', '$string_bytes(pvalue_written) = ($ptascii("changed"))',
                      '$heap_owners($heap_graph(S_whole), HCELL n_cell) = 1', '~((HOBJECT n_object) <- S_whole.ALLOCATIONS)']
    for protected in (False, True):
        fixture(('protected' if protected else 'plain') + '-destructor-before-copy',
                'local-cv-string-' + ('protected' if protected else 'plain') + '-used',
                {0: capture, 1: destructor, 2: copy_ready}, capture_checks(protected, True) + destructor_checks(protected),
                terminal=alias_terminal)

    stages = {0: capture, 1: copy_ready, 2: ['$lc_function(S, $ptascii("f"))',
        '$lc_return_finally(S.TODO) = (FINALLY_REF_RETURN porigin_owner porigin_source poperand z_final)',
        '$lc_outputs(S.EVENTS) = $ptascii("T;D;")']}
    fixture('protected-unused-return-cleanup', 'local-cv-string-protected-unused', stages, capture_checks(True, False) + [
        'S_copy = $lc_find(S_begin, 2000, 1)',
        'S_copy.TODO = (REF_CV_STRING_COPY prefstringcv pvalue_text) :: ptask_conversion_tail*',
        'S_copy.STORE[n_cell] = DEFINED (POBJECT n_object)', '~((HOBJECT n_object) <- S_copy.ALLOCATIONS)',
        '$typed_cv_string_copy_valid(S_copy, prefstringcv, pvalue_text)', '$heap_owners($heap_graph(S_copy), HCELL n_cell) = 2',
        'S_written = $drive_steps(S_copy, 1)', 'S_written.TODO = (RETURN_REF_UNWIND (REFERENCE n_cell) z false prefstringcv.SOURCE) :: ptask_tail*',
        'S_written.STORE[n_cell] = DEFINED pvalue_text', '$lc_count(S_written.TODO) = 0',
        '$heap_owners($heap_graph(S_written), HCELL n_cell) = 2', '$call_descriptors_valid(S_written)', '$heap_valid($heap_graph(S_written))',
        'S_finally = $lc_find(S_written, 2000, 2)',
        '$lc_return_finally(S_finally.TODO) = (FINALLY_REF_RETURN porigin_owner prefstringcv.SOURCE (REFERENCE n_cell) z)',
        'S_finally.STORE[n_cell] = DEFINED pvalue_text', '$heap_owners($heap_graph(S_finally), HCELL n_cell) = 2',
        '$lc_count(S_finally.TODO) = 0', '$lc_outputs(S_finally.EVENTS) = $ptascii("T;D;")',
        '$call_descriptors_valid(S_finally)', '$heap_valid($heap_graph(S_finally))'],
        terminal=['~((HCELL n_cell) <- S_whole.ALLOCATIONS)',
                  '~((HOBJECT n_object) <- S_whole.ALLOCATIONS)', '$lookup(S_whole.ENV, $ptascii("r")) = eps'])

    error_ready = ['$lc_function(S, $ptascii("f"))',
        'S.TODO = (THROW_SEARCH n_old) :: (STRINGIFY_RESULT n_object porigin_source z_result) :: (REF_CV_STRING_FETCH prefstringcv) :: (REF_CV_STRING_THROW prefstringcv) :: ptask_conversion_tail*']
    error_finally = ['$lc_function(S, $ptascii("f"))', '$lc_throw_finally(S.TODO) = (FINALLY_RESUME porigin_owner (n_error))',
                     '$lc_outputs(S.EVENTS) = $ptascii("T;")']
    error_destructor = ['$lc_function(S, $ptascii("O::__destruct"))', '$lc_outputs(S.EVENTS) = $ptascii("T;F;")']
    error_resumed = ['$lc_function(S, $ptascii("f"))', 'S.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
                     'S.OBJECTS[n_error] = THROWABLE pthrowable_error', 'pthrowable_error.KIND = "TypeError"',
                     '$lc_outputs(S.EVENTS) = $ptascii("T;")']
    fixture('protected-callback-error-lifetime', 'local-cv-string-protected-used-callback-throw',
        {0: capture, 1: saved, 2: error_ready, 3: error_finally, 4: error_destructor, 5: error_resumed},
        capture_checks(True, True) + saved_checks(True) + [
        'S_error = $lc_find($drive_steps(S_saved, 1), 2000, 2)',
        'S_error.TODO = (THROW_SEARCH n_old) :: (STRINGIFY_RESULT n_object prefstringcv.SOURCE z) :: (REF_CV_STRING_FETCH prefstringcv) :: (REF_CV_STRING_THROW prefstringcv) :: ptask_conversion_tail*',
        'S_error.STORE[n_cell] = DEFINED (POBJECT n_object)', '$heap_owners($heap_graph(S_error), HCELL n_cell) = 2',
        '$typed_return_throw_pending(S_error)', '$throwable_live(S_error, n_old)',
        '$string_bytes($throwable_field(S_error, n_old, "message")) = ($ptascii("callback"))',
        '$call_descriptors_valid(S_error)', '$heap_valid($heap_graph(S_error))',
        'S_releasing = $drive_steps(S_error, 1)', 'S_releasing.COMPLETION = BUDGET',
        'S_releasing.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
        'pdestructionoperation.PENDING = (n_new)', 'pdestructionoperation.SOURCE = THROW_SEARCH n_old',
        'pdestructionoperation.CALLER = S_error.CURRENT', 'pdestructionoperation.ORIGIN = S_error.ORIGIN',
        '$heap_count(HCELL n_cell, $destruction_job_nodes(pdestructionrelease.JOBS)) = 1',
        '$heap_count(HOBJECT n_object, $destruction_job_nodes(pdestructionrelease.JOBS)) = 1',
        '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = [HOBJECT n_new]',
        '$lc_count(S_releasing.TODO) = 0', 'S_releasing.STORE[n_cell] = DEFINED (POBJECT n_object)',
        '$throwable_field(S_releasing, n_new, "previous") = POBJECT n_old',
        '$lc_outputs(S_releasing.EVENTS) = $ptascii("T;")',
        '$call_descriptors_valid(S_releasing)', '$heap_valid($heap_graph(S_releasing))',
        'S_new = $lc_find(S_releasing, 2000, 5)', 'S_new.TODO = (THROW_SEARCH n_new) :: ptask_tail*',
        'n_new =/= n_old', '$throwable_live(S_new, n_new)', '$throwable_live(S_new, n_old)',
        'S_new.OBJECTS[n_new] = THROWABLE pthrowable_new', 'pthrowable_new.KIND = "TypeError"',
        '$string_bytes($throwable_field(S_new, n_new, "message")) = ($ptascii("f(): Return value must be of type string, O returned"))',
        '$throwable_field(S_new, n_new, "previous") = POBJECT n_old', 'S_new.STORE[n_cell] = DEFINED (POBJECT n_object)',
        '$heap_owners($heap_graph(S_new), HCELL n_cell) = 1', '$node_children(S_new, HCELL n_cell) = [HOBJECT n_object]',
        '$lc_count(S_new.TODO) = 0', 'S_new.RESULT = KNOWN PNULL', '$lc_outputs(S_new.EVENTS) = $ptascii("T;")',
        '$call_descriptors_valid(S_new)', '$heap_valid($heap_graph(S_new))',
        'S_finally = $lc_find(S_new, 2000, 3)', '$lc_throw_finally(S_finally.TODO) = (FINALLY_RESUME porigin_owner (n_new))',
        '$lc_return_finally(S_finally.TODO) = eps', 'S_finally.STORE[n_cell] = DEFINED (POBJECT n_object)',
        '$heap_owners($heap_graph(S_finally), HCELL n_cell) = 1', '(HOBJECT n_object) <- S_finally.ALLOCATIONS',
        '$lc_count(S_finally.TODO) = 0', '$throwable_field(S_finally, n_new, "previous") = POBJECT n_old',
        '$call_descriptors_valid(S_finally)', '$heap_valid($heap_graph(S_finally))',
        'S_destructor = $lc_find($drive_steps(S_finally, 1), 2000, 4)',
        '$lc_outputs(S_destructor.EVENTS) = $ptascii("T;F;")', '~((HCELL n_cell) <- S_destructor.ALLOCATIONS)',
        '(HOBJECT n_object) <- S_destructor.ALLOCATIONS', '$throwable_live(S_destructor, n_new)',
        '$throwable_field(S_destructor, n_new, "previous") = POBJECT n_old',
        '$call_descriptors_valid(S_destructor)', '$heap_valid($heap_graph(S_destructor))'],
        terminal=['~((HCELL n_cell) <- S_whole.ALLOCATIONS)', '~((HOBJECT n_object) <- S_whole.ALLOCATIONS)',
        '$lookup(S_whole.ENV, $ptascii("e")) = eps', '$lookup(S_whole.ENV, $ptascii("p")) = eps',
        '~((HOBJECT n_new) <- S_whole.ALLOCATIONS)', '~((HOBJECT n_old) <- S_whole.ALLOCATIONS)'])

    call_prefix = '(CALL_ARGS (METHOD_TARGET n_object porigin_method) eps 0 eps (prefstringcv.SOURCE) z) :: (STRINGIFY_RESULT n_object prefstringcv.SOURCE z) :: '
    fixture('current-local-cv-certificates', 'local-cv-string-protected-used', {0: capture}, capture_checks(True, True), bad=[
        'S_begin[.TODO = ' + call_prefix + '(REF_CV_STRING_FETCH (prefstringcv[.LINE = $(z + 1)])) :: (REF_CV_STRING_THROW prefstringcv) :: ptask_conversion_tail*]',
        'S_begin[.TODO = ' + call_prefix + '(REF_CV_STRING_FETCH prefstringcv) :: (REF_CV_STRING_THROW prefstringcv) :: ptask_tail*]',
        'S_begin[.TODO = ' + call_prefix + '(REF_CV_STRING_FETCH prefstringcv) :: (REF_CV_STRING_THROW prefstringcv) :: (REF_CV_STRING_TEMP prefstringcv) :: ptask_conversion_tail*]',
        'S_begin[.TODO = ' + call_prefix + '(REF_CV_STRING_THROW prefstringcv) :: (REF_CV_STRING_FETCH prefstringcv) :: ptask_conversion_tail*]',
        'S_begin[.TODO = ' + call_prefix + '(REF_CV_STRING_FETCH prefstringcv) :: ptask_conversion_tail*]',
        'S_begin[.TODO = ' + call_prefix + '(REF_CV_STRING_FETCH (prefstringcv[.CELL = |S_begin.STORE|])) :: (REF_CV_STRING_THROW (prefstringcv[.CELL = |S_begin.STORE|])) :: ptask_conversion_tail*]',
        'S_begin[.TODO = ' + call_prefix + '(REF_CV_STRING_FETCH (prefstringcv[.SOURCE = porigin_method])) :: (REF_CV_STRING_THROW (prefstringcv[.SOURCE = porigin_method])) :: ptask_conversion_tail*]',
    ], terminal=alias_terminal)

    checks = capture_checks(True, True) + saved_checks(True) + [
        'pframe_saved = pframe', 'pframe_saved_tail* = pframe_tail*',
        'S_destructor = $lc_find($drive_steps(S_saved, 1), 2000, 2)', 'S_destructor.FRAMES = pframe_copy :: pframe_copy_tail*',
        '$typed_cv_string_copy_at(pframe_copy.TODO, n_cell) = ((prefstringcv, pvalue_text))',
        'S_copy_scope = $constant_frame_scope(S_destructor, pframe_copy, pframe_copy_tail*)',
        '$typed_cv_string_copy_valid(S_copy_scope, prefstringcv, pvalue_text)',
        '$node_children(S_destructor, HCELL n_cell) = eps', '$call_descriptors_valid(S_destructor)', '$heap_valid($heap_graph(S_destructor))',
        # Pure projection of a reached COPY continuation; this is not Fiber execution evidence.
        'pfibervm_copy = $fiber_vm(S_copy_scope)', '$typed_cv_string_released_vm(S_destructor, pfibervm_copy, n_cell)',
        '$fiber_vm_restore(S_destructor, pfibervm_copy).TODO = S_copy_scope.TODO',
        'S_copy = $lc_find($drive_steps(S_destructor, 1), 2000, 3)',
        'S_copy.TODO = (REF_CV_STRING_COPY prefstringcv pvalue_text) :: ptask_conversion_tail*',
        '~((HOBJECT n_object) <- S_copy.ALLOCATIONS)', '$typed_cv_string_copy_valid(S_copy, prefstringcv, pvalue_text)',
        '$call_descriptors_valid(S_copy)', '$heap_valid($heap_graph(S_copy))']
    copy_mutations = [
        'eps',
        '[REF_CV_STRING_COPY (prefstringcv[.LINE = $(z + 1)]) pvalue_text]',
        '[REF_CV_STRING_COPY prefstringcv (PINT 7)]',
        '[REF_CV_STRING_COPY prefstringcv pvalue_text, REF_CV_STRING_COPY prefstringcv pvalue_text]',
    ]
    saved_bad = [
        'S_saved[.FRAMES = pframe_saved[.TODO = (STRINGIFY_RESULT n_object prefstringcv.SOURCE z) :: (REF_CV_STRING_FETCH (prefstringcv[.CELL = |S_saved.STORE|])) :: (REF_CV_STRING_THROW prefstringcv) :: ptask_conversion_tail*] :: pframe_saved_tail*]',
        'S_saved[.FRAMES = pframe_saved[.TODO = (STRINGIFY_RESULT n_object prefstringcv.SOURCE z) :: (REF_CV_STRING_FETCH prefstringcv) :: (REF_CV_STRING_THROW prefstringcv) :: ptask_tail*] :: pframe_saved_tail*]',
    ]
    saved_bad += ['S_destructor[.FRAMES = pframe_copy[.TODO = $lc_copy_replace(pframe_copy.TODO, prefstringcv, ' + mutation + ')] :: pframe_copy_tail*]' for mutation in copy_mutations]
    saved_bad += [
        'S_copy[.TODO = (REF_CV_STRING_COPY prefstringcv pvalue_text) :: ptask_tail*]',
        'S_copy[.TODO = (REF_CV_STRING_COPY (prefstringcv[.SOURCE = porigin_method]) pvalue_text) :: ptask_conversion_tail*]',
    ]
    fixture('saved-local-cv-copy-admission', 'local-cv-string-protected-used',
            {0: capture, 1: saved, 2: destructor, 3: copy_ready}, checks, saved_bad, alias_terminal)

    manifest = {'producer': str(Path(__file__).resolve()), 'producer_sha256': sha(Path(__file__)),
                'helper': str((ROOT / 'tests/semantics/reference_typed_cv_string_state.py').resolve()),
                'helper_sha256': sha(ROOT / 'tests/semantics/reference_typed_cv_string_state.py'),
                'catalogue_sha256': sha(catalogue), 'model_report': str(report_path.resolve()),
                'model_report_sha256': sha(report_path), 'model_revision': report['revision'],
                'fixtures': records, 'assertions': sum(row['assertions'] for row in records),
                'scope': 'Sole local nonreference CV; protected owning TEMP, saved destructor release/COPY, initial callback error. Parked VM is helper-only. No released target or destructor-throw source credit.'}
    (args.output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'fixtures': len(records), 'assertions': manifest['assertions']}))


if __name__ == '__main__':
    main()
