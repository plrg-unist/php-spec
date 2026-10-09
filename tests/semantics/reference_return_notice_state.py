#!/usr/bin/env python3
"""Emit genuine deferred-Notice fronts from passed independent source packets.

This producer runs no PHP, compiler or model. Its checked fixtures require the
pinned numeric runner in explicit SL mode, with the ordered current modules.
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
from request_environment_state import request_fixture

MESSAGE = '$ptascii("Only variable references should be returned by reference")'
UNUSED = 'ref-unused-value-finally'
UNUSED_SHA = 'a6864c6840cc2ad71b991de473986a812064a8dfc8b38ea6db59f50b7f2fa983'
PREFIX = r'''dec $notice_stage(pstate, nat) : bool
dec $notice_function(pstate, preqbytes) : bool
def $notice_function(S, n_name*) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $function_at($all_functions(S), pcallcontext.FUNCTION) = (pfunction)
  -- if pfunction.NAME = n_name*
def $notice_function(S, n_name*) = false -- otherwise
dec $notice_find(pstate, nat, nat) : pstate
def $notice_find(S, n, n_stage) = S[.COMPLETION = NORMAL]
  -- if $notice_stage(S, n_stage)
  -- if S.COMPLETION = BUDGET
def $notice_find(S, n, n_stage) = $notice_find($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)), n_stage)
  -- if ~$notice_stage(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
dec $notice_resume(pstate, nat) : pstate
def $notice_resume(S, n) = $drive(S[.COMPLETION = NORMAL], n) -- if S.COMPLETION = BUDGET
def $notice_resume(S, n) = S -- otherwise
dec $notice_replace(ptask*, ptask, ptask*) : ptask*
def $notice_replace(eps, ptask_old, ptask_new*) = eps
def $notice_replace(ptask_old :: ptask_tail*, ptask_old, ptask_new*) = ptask_new* ++ ptask_tail*
def $notice_replace(ptask_head :: ptask_tail*, ptask_old, ptask_new*) = ptask_head :: $notice_replace(ptask_tail*, ptask_old, ptask_new*)
  -- if ptask_head =/= ptask_old
dec $notice_output(pevent) : nat*
def $notice_output(OUTPUT n*) = n*
def $notice_output(pevent) = eps -- otherwise
dec $notice_outputs(pevent*) : nat*
def $notice_outputs(eps) = eps
def $notice_outputs(pevent_head :: pevent_tail*) = $notice_output(pevent_head) ++ $notice_outputs(pevent_tail*)
dec $notice_diagnostic(pevent) : pevent*
def $notice_diagnostic(DIAGNOSTIC text n* z) = [DIAGNOSTIC text n* z]
def $notice_diagnostic(DIAGNOSTIC_SOURCE n_unit text n* z) = [DIAGNOSTIC text n* z]
def $notice_diagnostic(DISPLAY_STDOUT pevent) = $notice_diagnostic(pevent)
def $notice_diagnostic(pevent) = eps -- otherwise
dec $notice_diagnostics(pevent*) : pevent*
def $notice_diagnostics(eps) = eps
def $notice_diagnostics(pevent_head :: pevent_tail*) = $notice_diagnostic(pevent_head) ++ $notice_diagnostics(pevent_tail*)
dec $notice_finally_head(ptask) : bool
def $notice_finally_head(FINALLY_REF_RETURN porigin_owner porigin_source poperand z) = true
def $notice_finally_head(ptask) = false -- otherwise
dec $notice_finally(ptask*) : ptask?
def $notice_finally(eps) = eps
def $notice_finally((FINALLY_REF_RETURN porigin_owner porigin_source poperand z) :: ptask_tail*) = (FINALLY_REF_RETURN porigin_owner porigin_source poperand z)
def $notice_finally(ptask_head :: ptask_tail*) = $notice_finally(ptask_tail*)
  -- if ~$notice_finally_head(ptask_head)
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw', type=Path, action='append', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    catalogue = json.loads((ROOT / 'tests/semantics/reference_return_notice_cases.json').read_text())
    cases = {row['id']: row for row in catalogue['cases']}
    assert len(cases) == 6
    rows = {}
    reports = []
    inputs = [(raw, raw / 'report.json', json.loads((raw / 'report.json').read_text()))
              for raw in args.raw]
    completed = [report for _, _, report in inputs if report.get('passed')]
    assert len(completed) == 1
    final = completed[0]
    assert final['pins'] == final['pins_after'] and final['status_after'] == ''
    assert final['head_after'] == final['revision']
    for raw, path, report in inputs:
        if not report.get('passed'):
            assert final['retained_first_three'] == str(path.resolve())
            assert final['pins'][str(path.resolve())] == hashlib.sha256(path.read_bytes()).hexdigest()
            assert report['model_evaluations'] == report['source_agreements'] == 3
            for worker in ('frontend-wire', 'adapter-wire'):
                close = json.loads((raw / worker / 'close.json').read_text())
                assert close['exit_status'] == 0
        reports.append({'path': str(path.resolve()),
                        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                        'revision': report['revision']})
        for row in report['records']:
            if row['pass']:
                assert row['id'] not in rows
                assert row['model']['status'] == 'normal'
                assert all(row['model'][key] == row['native'][key]
                           for key in ('stdout', 'stderr', 'exit_status'))
                rows[row['id']] = (row, raw)
    assert rows.keys() == {*cases, UNUSED}
    args.output.mkdir(parents=True, exist_ok=True)
    records = []

    def initial(case):
        row, raw = rows[case]
        directory = raw / case
        facts = json.loads((directory / 'request.json').read_text())
        source = Path(base64.b64decode(facts['file']).decode()).read_bytes()
        assert hashlib.sha256(source).hexdigest() == row['source_sha256']
        if case == UNUSED:
            assert row['source_sha256'] == UNUSED_SHA
        else:
            assert source == cases[case]['source'].encode()
            assert row['source_sha256'] == cases[case]['source_sha256']
            assert base64.b64decode(row['native']['stdout']) == cases[case]['stdout'].encode()
            assert base64.b64decode(row['native']['stderr']) == cases[case]['stderr'].encode()
        assert row['native']['exit_status'] == 0
        parsed = json.loads((directory / 'parsed.json').read_text())
        checked = json.loads((directory / 'checked.json').read_text())
        executed = json.loads((directory / 'state.json').read_text())
        assert parsed['accepted'] and checked['ok'] and checked['fixture'] and executed['ok']
        return ('$php_request_run(' + checked['fixture'] + ', 0, ' +
                json.dumps(facts['file']) + ', ' + request_fixture(facts) + ')',
                str(list(base64.b64decode(row['native']['stdout']))))

    def fixture(name, case, stages, checks, bad=(), terminal=()):
        start, stdout = initial(case)
        stage_text = ''.join('def $notice_stage(S, ' + str(k) + ') = true\n' +
                             ''.join('  -- if ' + condition + '\n' for condition in conditions)
                             for k, conditions in stages.items())
        stage_text += 'def $notice_stage(S, n_stage) = false -- otherwise\n'
        common = ['S_initial = ' + start, 'S_initial.COMPLETION = BUDGET',
                  'S_start = S_initial[.COMPLETION = NORMAL]',
                  'S = $notice_find(S_start, 2000, 0)', 'S.COMPLETION = NORMAL',
                  '$notice_stage(S, 0)', '$call_descriptors_valid(S)',
                  '$heap_valid($heap_graph(S))']
        rejected = []
        for index, mutation in enumerate(bad):
            rejected += [f'S_bad{index} = ' + mutation + '[.COMPLETION = NORMAL]',
                         f'~$call_descriptors_valid(S_bad{index})',
                         f'S_rejected{index} = $drive(S_bad{index}, 0)',
                         f'S_rejected{index}.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"',
                         f'$drive(S_bad{index}, 10000) = S_rejected{index}']
        complete = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
                    'S_one = $notice_resume(S_zero, 1)',
                    'S_adjacent = $notice_resume(S_one, 10000)',
                    'S_frontier = $drive(S, 10001)', 'S_whole = $drive(S_start, 10001)',
                    'S_adjacent = S_frontier', 'S_frontier = S_whole',
                    'S_whole.COMPLETION = NORMAL', '$notice_outputs(S_whole.EVENTS) = ' + stdout,
                    'S_whole.CURRENT = eps', 'S_whole.FRAMES = eps', 'S_whole.TODO = eps',
                    'S_whole.HELD = eps', 'S_whole.RETIREDOWNERS = eps',
                    'S_whole.ITERATORS = eps', '$heap_valid($heap_graph(S_whole))',
                    '$call_descriptors_valid(S_whole)'] + list(terminal)
        assertions = common + checks + rejected + complete
        path = args.output / (name + '.watsup')
        path.write_text(PREFIX + '\n' + stage_text + '\ndec $main() : bool\ndef $main() = true\n' +
                        ''.join('  -- if ' + condition + '\n' for condition in assertions))
        records.append({'id': name, 'source_id': case, 'fixture': str(path.resolve()),
                        'fixture_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                        'assertions': len(assertions)})

    f = '$notice_function(S, $ptascii("f"))'
    for name, case, ingress, kind, value in (
        ('protected-value', 'protected-literal-handler', 'RETURN_REF_VALUE', 'REF_NOTICE_VALUE', 'PINT 1'),
        ('protected-bare', 'protected-bare-handler', 'RETURN_REF_NULL', 'REF_NOTICE_NULL', 'PNULL'),
        ('protected-explicit-null', 'protected-null-literal-handler', 'RETURN_REF_VALUE', 'REF_NOTICE_VALUE', 'PNULL'),
    ):
        marker = f'REF_RETURN_NOTICE porigin_source z {kind}'
        unwind = f'RETURN_REF_UNWIND (KNOWN ({value})) z false porigin_source'
        stages = {
            0: [f, f'S.TODO = ({ingress} z) :: ptask_tail*'],
            1: [f, '$notice_finally(S.TODO) = (FINALLY_REF_RETURN porigin_owner porigin_source poperand z)',
                '$notice_outputs(S.EVENTS) = eps'],
            2: [f, f'S.TODO = [RETURN_REF_UNWIND (KNOWN ({value})) z true porigin_source, {marker}, REF_RECHECK porigin_source porigin_first (KNOWN ({value})) z]'],
        }
        checks = [f'S.TODO = ({ingress} z) :: ptask_tail*', 'z = 1', '$reference_return_used(S)',
                  'S.ORIGIN = (porigin_source)', '$notice_outputs(S.EVENTS) = eps',
                  '$notice_diagnostics(S.EVENTS) = eps', '$reference_notice_count(S.TODO) = 0']
        checks += (['S.RESULT = KNOWN (' + value + ')',
                    '$reference_return_value_valid(S, z)'] if ingress == 'RETURN_REF_VALUE' else [
                    '$origin_node(S.SOURCES, porigin_source) = (NStmtReturn ABSENT metadata)',
                    '$reference_return_null_valid(S, z)'])
        checks += ['S_next = $drive_steps(S, 1)', f'S_next.TODO = ({unwind}) :: ptask_pending*',
                   '$reference_notice_count(S_next.TODO) = 1',
                   f'$reference_notice_end(S_next.TODO, porigin_source, z, {kind})',
                   f'$task_nodes({marker}) = eps', 'S_next.STORE = S.STORE',
                   'S_next.REFCELLS = S.REFCELLS', '$notice_outputs(S_next.EVENTS) = eps',
                   '$notice_diagnostics(S_next.EVENTS) = eps', '$call_descriptors_valid(S_next)',
                   'S_finally = $notice_find(S_next, 2000, 1)',
                   '$notice_finally(S_finally.TODO) = (FINALLY_REF_RETURN porigin_owner porigin_source poperand z)',
                   f'poperand = KNOWN ({value})',
                   '$finally_ref_source_valid(S_finally, porigin_owner, porigin_source, z)',
                   '$notice_outputs(S_finally.EVENTS) = eps',
                   '$notice_diagnostics(S_finally.EVENTS) = eps',
                   f'$reference_notice_end(S_finally.TODO, porigin_source, z, {kind})',
                   '$call_descriptors_valid(S_finally)', '$heap_valid($heap_graph(S_finally))',
                   'S_terminal = $notice_find($drive_steps(S_finally, 1), 2000, 2)',
                   f'S_terminal.TODO = [RETURN_REF_UNWIND (KNOWN ({value})) z true porigin_source, {marker}, REF_RECHECK porigin_source porigin_first (KNOWN ({value})) z]',
                   '$notice_outputs(S_terminal.EVENTS) = $ptascii("F;")',
                   '$notice_diagnostics(S_terminal.EVENTS) = eps',
                   '$ref_recheck_valid(S_terminal, porigin_source, porigin_first, KNOWN (' + value + '), z)',
                   'S_begin = $drive_steps(S_terminal, 1)',
                   f'S_begin.TODO = [REF_RETURN_NOTICE_BEGIN porigin_source (KNOWN ({value})) z {kind}]',
                   'S_begin.ORIGIN = ($reference_notice_boundary(S_begin))',
                   'S_begin.RETIREDOWNERS = eps', 'S_begin.HELD = eps',
                   '$reference_notice_count(S_begin.TODO) = 0',
                   '$notice_outputs(S_begin.EVENTS) = $ptascii("F;")',
                   '$notice_diagnostics(S_begin.EVENTS) = eps', 'S_begin.REFCELLS = S.REFCELLS',
                   '$call_descriptors_valid(S_begin)', '$heap_valid($heap_graph(S_begin))',
                   'ptask_notice = ' + marker]
        bad = [
            'S_next[.TODO = $notice_replace(S_next.TODO, ptask_notice, eps)]',
            'S_next[.TODO = $notice_replace(S_next.TODO, ptask_notice, [ptask_notice, ptask_notice])]',
            f'S_next[.TODO = $notice_replace(S_next.TODO, ptask_notice, [REF_RETURN_NOTICE porigin_source $(z + 100) {kind}])]',
            f'S_next[.TODO = $notice_replace(S_next.TODO, ptask_notice, [REF_RETURN_NOTICE ($reference_notice_boundary(S_next)) z {kind}])]',
            f'S_next[.TODO = (ptask_notice) :: $reference_notice_clean(S_next.TODO)]',
        ]
        other = 'REF_NOTICE_VALUE' if kind == 'REF_NOTICE_NULL' else 'REF_NOTICE_NULL'
        bad.append(f'S_next[.TODO = $notice_replace(S_next.TODO, ptask_notice, [REF_RETURN_NOTICE porigin_source z {other}])]')
        fixture(name, case, stages, checks, bad,
                ['$notice_diagnostics(S_whole.EVENTS) = eps',
                 '$lookup(S_whole.ENV, $ptascii("r")) = (n_r)',
                 'n_r <- S_whole.REFCELLS', 'S_whole.STORE[n_r] = DEFINED (' + value + ')'])

    implicit = 'implicit-after-finally-handler'
    marker = 'REF_RETURN_NOTICE porigin_source z REF_NOTICE_NULL'
    fixture('implicit-null-boundary', implicit, {
        0: [f, 'S.TODO = (RETURN_REF_NULL z) :: eps'],
    }, ['S.TODO = (RETURN_REF_NULL z) :: eps', 'S.CURRENT = (pcallcontext)',
        '$function_at($all_functions(S), pcallcontext.FUNCTION) = (pfunction)',
        'S.ORIGIN = (pfunction.ORIGIN)', 'porigin_source = pfunction.ORIGIN',
        'z = pfunction.ENDLINE', 'z = 1', 'pfunction.SIGNATURE.BYREF',
        'porigin_source = PORIGIN n_unit pcpath_source', '$reference_return_used(S)',
        '$reference_return_null_valid(S, z)', '~$goto_scope_valid(S, porigin_source)',
        '$notice_outputs(S.EVENTS) = $ptascii("T;F;")', '$notice_diagnostics(S.EVENTS) = eps',
        'S_next = $drive_steps(S, 1)',
        'S_next.TODO = [RETURN_REF_UNWIND (KNOWN PNULL) z false porigin_source, ' + marker + ']',
        '$reference_notice_source(S_next, porigin_source, KNOWN PNULL, z, REF_NOTICE_NULL)',
        '$call_descriptors_valid(S_next)',
        'S_begin = $drive_steps(S_next[.COMPLETION = NORMAL], 1)',
        'ptask_begin = REF_RETURN_NOTICE_BEGIN porigin_source (KNOWN PNULL) z REF_NOTICE_NULL',
        'S_begin.TODO = [ptask_begin]', 'S_begin.ORIGIN = (pfunction.ORIGIN)',
        '$notice_outputs(S_begin.EVENTS) = $ptascii("T;F;")', '$notice_diagnostics(S_begin.EVENTS) = eps',
        'S_begin.RETIREDOWNERS = eps', 'S_begin.HELD = eps',
        '$call_descriptors_valid(S_begin)', '$heap_valid($heap_graph(S_begin))'], [
        'S_begin[.TODO = [REF_RETURN_NOTICE_BEGIN porigin_source (KNOWN PNULL) $(z + 100) REF_NOTICE_NULL]]',
        'S_begin[.TODO = [REF_RETURN_NOTICE_BEGIN porigin_source (KNOWN PNULL) z REF_NOTICE_VALUE]]',
        'S_begin[.ORIGIN = eps]',
        'S_begin[.ORIGIN = (PORIGIN n_unit (pcpath_source ++ [PCFIELD 100]))]',
        'S_begin[.TODO = [REF_RETURN_NOTICE_BEGIN (PORIGIN n_unit (pcpath_source ++ [PCFIELD 100])) (KNOWN PNULL) z REF_NOTICE_NULL]]',
        'S_begin[.TODO = [ptask_begin, ptask_begin]]',
        'S_begin[.TODO = [ptask_begin, RETURN_NULL]]',
        'S_next[.TODO = [RETURN_REF_UNWIND (KNOWN PNULL) z false porigin_source]]',
    ], ['$notice_diagnostics(S_whole.EVENTS) = eps'])

    def saved_checks(throw=False):
        checks = ['S.FRAMES = pframe :: pframe_tail*', 'pframe.TODO = [ERROR_HANDLER_RESULT perrorcall]',
                  'perrorcall.RESUME = REF_RETURN_NOTICE_RESULT porigin_source poperand z REF_NOTICE_VALUE',
                  'poperand = KNOWN (PINT 1)', 'z = 1',
                  'S_scope = $constant_frame_scope(S, pframe, pframe_tail*)',
                  '$notice_function(S_scope, $ptascii("f"))',
                  'porigin_boundary = $reference_notice_boundary(S_scope)',
                  'pframe.ORIGIN = (porigin_boundary)', 'perrorcall.SITE = porigin_boundary',
                  'perrorcall.LINE = z', 'perrorcall.LEVEL = 8',
                  'perrorcall.MESSAGE = ' + MESSAGE,
                  'perrorcall.EVENT = DIAGNOSTIC "Notice" (' + MESSAGE + ') z',
                  '$reference_notice_source(S_scope, porigin_source, poperand, z, REF_NOTICE_VALUE)',
                  '$error_call_valid(S_scope, perrorcall)', '$call_tasks_valid(S_scope, pframe.TODO)',
                  'perrorcall.TARGET = (pcalltarget)', '$target_function(S, pcalltarget) = (pfunction_handler)',
                  'pfunction_handler.NAME = $ptascii("notice20")',
                  'S.CURRENT = (pcallcontext_handler)', 'pcallcontext_handler.CALLSITE = pframe.ORIGIN',
                  'pcallcontext_handler.LINE = z', 'pframe.RETIREDOWNERS = eps',
                  '$reference_notice_count(pframe.TODO) = 0', '$notice_finally(pframe.TODO) = eps',
                  '$notice_outputs(S.EVENTS) = $ptascii("F;")', '$notice_diagnostics(S.EVENTS) = eps',
                  '$task_nodes(perrorcall.RESUME) = $operand_nodes(poperand)']
        if throw:
            checks += ['S_throw = $notice_find($drive_steps(S, 1), 2000, 1)',
                       'S_throw.TODO = [THROW_SEARCH n_error, ERROR_HANDLER_RESULT perrorcall]',
                       '$notice_function(S_throw, $ptascii("f"))',
                       '$notice_outputs(S_throw.EVENTS) = $ptascii("F;H;")',
                       '$throwable_live(S_throw, n_error)',
                       'S_throw.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "Exception"',
                       '$call_descriptors_valid(S_throw)', '$heap_valid($heap_graph(S_throw))',
                       'n_r = |S_throw.STORE|',
                       'S_left = $drive_steps(S_throw, 1)',
                       'S_left.TODO = (THROW_SEARCH n_error) :: ptask_caller*',
                       'S_left.CURRENT = eps', 'S_left.FRAMES = eps',
                       'S_left.RESULT = KNOWN PNULL', 'S_left.HELD = eps',
                       'S_left.BASE = BASE_VALUE (KNOWN PNULL)', 'S_left.RETIREDOWNERS = eps',
                       '|S_left.STORE| = $(n_r + 1)', 'S_left.STORE[n_r] = DEFINED (PINT 1)',
                       '~$heap_member(HCELL n_r, S_left.ALLOCATIONS)',
                       '$reference_notice_count(S_left.TODO) = 0', '$notice_finally(S_left.TODO) = eps',
                       '$notice_outputs(S_left.EVENTS) = $ptascii("F;H;")',
                       '$throwable_live(S_left, n_error)', '$call_descriptors_valid(S_left)',
                       '$heap_valid($heap_graph(S_left))']
        else:
            checks += ['S_restored = $notice_find($drive_steps(S, 1), 2000, 1)',
                       'S_restored.TODO = [REF_RETURN_NOTICE_RESULT porigin_source poperand z REF_NOTICE_VALUE]',
                       'S_restored.ORIGIN = pframe.ORIGIN', 'S_restored.RETIREDOWNERS = pframe.RETIREDOWNERS',
                       '$notice_outputs(S_restored.EVENTS) = $ptascii("F;H;")',
                       '$notice_diagnostics(S_restored.EVENTS) = eps',
                       '$call_descriptors_valid(S_restored)', '$heap_valid($heap_graph(S_restored))',
                       'S_materialized = $drive_steps(S_restored, 1)',
                       'S_materialized.CURRENT = eps', 'S_materialized.FRAMES = eps',
                       'S_materialized.RESULT = REFERENCE n_r',
                       'n_r <- S_materialized.REFCELLS', 'S_materialized.STORE[n_r] = DEFINED (PINT 1)',
                       '$call_descriptors_valid(S_materialized)', '$heap_valid($heap_graph(S_materialized))']
        return checks

    saved_stage = ['$notice_function(S, $ptascii("notice20"))',
                   'S.FRAMES = pframe :: pframe_tail*',
                   'pframe.TODO = [ERROR_HANDLER_RESULT perrorcall]',
                   'perrorcall.RESUME = REF_RETURN_NOTICE_RESULT porigin_source poperand z REF_NOTICE_VALUE',
                   '$notice_outputs(S.EVENTS) = $ptascii("F;")']
    changed_call = [
        'perrorcall[.LINE = $(z + 100)]',
        'perrorcall[.RESUME = REF_RETURN_NOTICE_RESULT porigin_source poperand $(z + 100) REF_NOTICE_VALUE]',
        'perrorcall[.RESUME = REF_RETURN_NOTICE_RESULT porigin_source poperand z REF_NOTICE_NULL]',
        'perrorcall[.RESUME = REF_RETURN_NOTICE_RESULT porigin_boundary poperand z REF_NOTICE_VALUE]',
        'perrorcall[.EVENT = DIAGNOSTIC "Notice" (' + MESSAGE + ') $(z + 100)]',
    ]
    saved_bad = ['S[.FRAMES = pframe[.TODO = [ERROR_HANDLER_RESULT ' + call + ']] :: pframe_tail*]'
                 for call in changed_call]
    saved_bad.append('S[.FRAMES = pframe[.ORIGIN = eps] :: pframe_tail*]')
    fixture('saved-terminal-handler', 'protected-literal-handler', {
        0: saved_stage,
        1: [f, 'S.TODO = [REF_RETURN_NOTICE_RESULT porigin_source poperand z REF_NOTICE_VALUE]'],
    }, saved_checks(), saved_bad + [
        'S_restored[.TODO = [REF_RETURN_NOTICE_RESULT porigin_source poperand z REF_NOTICE_VALUE, REF_RETURN_NOTICE_RESULT porigin_source poperand z REF_NOTICE_VALUE]]',
        'S_restored[.TODO = [REF_RETURN_NOTICE_RESULT porigin_source poperand z REF_NOTICE_VALUE, RETURN_NULL]]',
    ], ['$notice_diagnostics(S_whole.EVENTS) = eps'])
    fixture('throwing-terminal-handler', 'protected-literal-handler-throw', {
        0: saved_stage,
        1: [f, 'S.TODO = [THROW_SEARCH n_error, ERROR_HANDLER_RESULT perrorcall]'],
    }, saved_checks(True), (), ['$notice_diagnostics(S_whole.EVENTS) = eps',
                                '$lookup(S_whole.ENV, $ptascii("r")) = eps'])

    case = 'protected-value-overridden-by-variable-return'
    fixture('cancelled-by-variable-return', case, {
        0: [f, 'S.TODO = (RETURN_REF_FETCH z_new) :: ptask_tail*',
            '$reference_notice_count(S.TODO) = 1'],
        1: [f, 'S.TODO = (RETURN_REF_UNWIND (REFERENCE n_x) z_new b porigin_new) :: ptask_tail*',
            '$reference_notice_count(S.TODO) = 0'],
    }, ['S.TODO = (RETURN_REF_FETCH z_new) :: ptask_tail*', 'z_new = 1',
        'S.ORIGIN = (porigin_new)', '$reference_return_fetch_valid(S, z_new)',
        '$reference_notice_first(S.TODO) = REF_NOTICE_PENDING porigin_old (KNOWN (PINT 1)) z_old',
        'porigin_new =/= porigin_old', 'z_old = 1',
        '$reference_notice_end(S.TODO, porigin_old, z_old, REF_NOTICE_VALUE)',
        '$notice_outputs(S.EVENTS) = $ptascii("F;")', '$notice_diagnostics(S.EVENTS) = eps',
        'S.GLOBALTABLE = (psymboltable)', '$lookup(psymboltable.ENV, $ptascii("x")) = (n_x)',
        'S.STORE[n_x] = DEFINED pvalue_old',
        'S_new = $drive_steps(S, 1)',
        'S_new.TODO = (RETURN_REF_UNWIND (REFERENCE n_x) z_new false porigin_new) :: ptask_new*',
        '$reference_notice_count(S_new.TODO) = 0',
        'S_new.STORE[n_x] = DEFINED pvalue_old', '$call_descriptors_valid(S_new)',
        '$heap_valid($heap_graph(S_new))',
        'S_terminal = $notice_find(S_new, 2000, 1)',
        '$notice_diagnostics(S_terminal.EVENTS) = eps',
        '$reference_return_notice(S_terminal[.ORIGIN = (porigin_new)], REFERENCE n_x) = false',
        '$call_descriptors_valid(S_terminal)', '$heap_valid($heap_graph(S_terminal))'], (), [
        '$notice_diagnostics(S_whole.EVENTS) = eps',
        '$lookup(S_whole.ENV, $ptascii("r")) = (n_x)',
        '$lookup(S_whole.ENV, $ptascii("x")) = (n_x)', 'n_x <- S_whole.REFCELLS',
        'S_whole.STORE[n_x] = DEFINED pvalue_new',
        '$string_bytes(pvalue_new) = ($ptascii("new"))'])

    fixture('protected-unused-value', UNUSED, {
        0: [f, 'S.TODO = [RETURN_REF_UNWIND (KNOWN pvalue) z true porigin_source, REF_RETURN_NOTICE porigin_source z REF_NOTICE_VALUE, REF_RECHECK porigin_source porigin_first (KNOWN pvalue) z]'],
        1: [f, 'S.TODO = [REF_RETURN_NOTICE_RESULT porigin_source (KNOWN pvalue) z REF_NOTICE_VALUE]'],
    }, ['S.TODO = [RETURN_REF_UNWIND (KNOWN pvalue) z true porigin_source, REF_RETURN_NOTICE porigin_source z REF_NOTICE_VALUE, REF_RECHECK porigin_source porigin_first (KNOWN pvalue) z]',
        'z = 1', '~$reference_return_used(S)', '$reference_verifies(S)',
        '$string_bytes(pvalue) = ($ptascii("s"))',
        '$reference_return_value_valid(S[.ORIGIN = (porigin_source)], z)',
        '$ref_recheck_valid(S, porigin_source, porigin_first, KNOWN pvalue, z)',
        '$notice_outputs(S.EVENTS) = $ptascii("F;")', '$notice_diagnostics(S.EVENTS) = eps',
        'S_begin = $drive_steps(S, 1)',
        'S_begin.TODO = [REF_RETURN_NOTICE_BEGIN porigin_source (KNOWN pvalue) z REF_NOTICE_VALUE]',
        'S_begin.ORIGIN = ($reference_notice_boundary(S_begin))',
        'S_begin.RETIREDOWNERS = eps', 'S_begin.HELD = eps',
        'S_begin.REFCELLS = S.REFCELLS', 'S_begin.STORE = S.STORE',
        '$notice_diagnostics(S_begin.EVENTS) = eps',
        '$call_descriptors_valid(S_begin)', '$heap_valid($heap_graph(S_begin))',
        'S_result = $notice_find(S_begin, 2000, 1)',
        'S_result.TODO = [REF_RETURN_NOTICE_RESULT porigin_source (KNOWN pvalue) z REF_NOTICE_VALUE]',
        'S_result.EVENTS = S.EVENTS ++ [DIAGNOSTIC "Notice" (' + MESSAGE + ') z]',
        'S_result.REFCELLS = S.REFCELLS', '$call_descriptors_valid(S_result)',
        '$heap_valid($heap_graph(S_result))',
        'S_left = $drive_steps(S_result, 1)', 'S_left.CURRENT = eps', 'S_left.FRAMES = eps',
        'S_left.RESULT = KNOWN PNULL', 'S_left.REFCELLS = S.REFCELLS',
        '$call_descriptors_valid(S_left)', '$heap_valid($heap_graph(S_left))'], (), [
        'S_whole.EVENTS = [OUTPUT $ptascii("F;"), DIAGNOSTIC "Notice" (' + MESSAGE + ') 1, OUTPUT $ptascii("OK;")]',
        'S_whole.REFCELLS = eps'])

    manifest = {'source_reports': reports, 'fixtures': len(records),
                'assertions': sum(row['assertions'] for row in records), 'records': records,
                'source_cases': 6, 'protected_unused_compatibility_cases': 1}
    (args.output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'fixtures': manifest['fixtures'], 'assertions': manifest['assertions']}))


if __name__ == '__main__':
    main()
