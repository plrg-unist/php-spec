#!/usr/bin/env python3
"""Emit focused scalar replay assertions from accepted source/model packets.

This producer launches no PHP, compiler or model. Execute its fixtures with the
pinned numeric runner in explicit --sl mode and the ordered modules.json.
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
from reference_replay_state import PREFIX
from request_environment_state import request_fixture

HELPERS = r'''dec $scalar_task_kind(ptask) : nat
def $scalar_task_kind(LOOP_NEXT statement porigin?) = 0
def $scalar_task_kind(LOOP_TEST statement porigin?) = 1
def $scalar_task_kind(TRY_END porigin) = 2
def $scalar_task_kind(FINALLY_ONLY porigin) = 3
def $scalar_task_kind(ORIGIN_RETURN porigin?) = 4
def $scalar_task_kind(FINALLY_JUMP porigin porigin_source n_depth n_original b) = 5
def $scalar_task_kind(ptask) = 6 -- otherwise
dec $scalar_tasks(ptask*, nat) : ptask*
def $scalar_tasks(eps, n_kind) = eps
def $scalar_tasks(ptask_head :: ptask_tail*, n_kind) = ptask_head :: $scalar_tasks(ptask_tail*, n_kind)
  -- if $scalar_task_kind(ptask_head) = n_kind
def $scalar_tasks(ptask_head :: ptask_tail*, n_kind) = $scalar_tasks(ptask_tail*, n_kind)
  -- if $scalar_task_kind(ptask_head) =/= n_kind
dec $scalar_loop_kind(statement) : nat
def $scalar_loop_kind(NStmtWhile expression phpType23 metadata) = 0
def $scalar_loop_kind(NStmtDo phpType23 expression metadata) = 1
def $scalar_loop_kind(NStmtFor phpType25_1 phpType25_2 phpType25_3 phpType23 metadata) = 2
def $scalar_loop_kind(statement) = 3 -- otherwise
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw', type=Path, action='append', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    cases = {row['id']: row for row in json.loads(
        (ROOT / 'tests/semantics/reference_replay_scalar_cases.json').read_text())['cases']}
    rows, directories, reports = {}, {}, []
    for raw in args.raw:
        path = raw / 'report.json'
        report = json.loads(path.read_text())
        assert report['passed'] and report['source_agreements'] == report['model_evaluations']
        assert report['revision'] == report['head_after'] and report['status_after'] == ''
        assert report['pins'] == report['pins_after']
        reports.append(str(path.resolve()))
        if 'records' in report:
            incoming = report['records']
        else:
            proposal = json.loads((raw / 'proposal.json').read_text())
            incoming = [{'id': proposal['id'], 'source_sha256': proposal['source_sha256'],
                         'native': report['native'], 'model': report['model'], 'pass': report['passed']}]
        for row in incoming:
            case = row['id']
            assert case in cases and case not in rows and row['pass']
            assert row['model']['status'] == cases[case]['status'] == 'normal'
            for key in ('stdout', 'stderr', 'exit_status'):
                assert row['native'][key] == row['model'][key]
            assert row['native']['exit_status'] == 0 and row['native']['stderr'] == ''
            rows[case] = row
            directories[case] = raw / case if 'records' in report else raw
    assert rows.keys() == cases.keys()
    args.output.mkdir(parents=True, exist_ok=True)
    records = []

    def initial(case):
        row = rows[case]
        source = cases[case]['source'].encode()
        assert hashlib.sha256(source).hexdigest() == row['source_sha256'] == cases[case]['source_sha256']
        stdout = base64.b64decode(row['native']['stdout'])
        assert stdout == cases[case]['native_stdout'].encode()
        directory = directories[case]
        parsed = json.loads((directory / 'parsed.json').read_text())
        checked = json.loads((directory / 'checked.json').read_text())
        assert parsed['accepted'] and checked['ok'] and checked['fixture']
        facts = json.loads((directory / 'request.json').read_text())
        return ('$php_request_run(' + checked['fixture'] + ', 0, ' +
                json.dumps(facts['file']) + ', ' + request_fixture(facts) + ')', str(list(stdout)))

    def fixture(name, case, stage, checks, bad=(), error_scope='S'):
        start, stdout = initial(case)
        common = ['S_initial = ' + start, 'S_initial.COMPLETION = BUDGET',
                  'S_start = S_initial[.COMPLETION = NORMAL]',
                  'S = $replay_find(S_start, 2000)', 'S.COMPLETION = NORMAL',
                  '$replay_stage(S)', '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
        error = [] if error_scope is None else [
            '$lookup(' + error_scope + '.ENV, [101]) = (n_error_cell)',
            error_scope + '.STORE[n_error_cell] = DEFINED (POBJECT n_error)',
            'S.OBJECTS[n_error] = THROWABLE pthrowable_error',
            'pthrowable_error.KIND = "TypeError"', '$throwable_live(S, n_error)']
        rejected = []
        for index, mutation in enumerate(bad):
            rejected += [f'S_bad{index} = ' + mutation + '[.COMPLETION = NORMAL]', f'~$call_descriptors_valid(S_bad{index})',
                         f'S_rejected{index} = $drive(S_bad{index}, 0)',
                         f'S_rejected{index}.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"',
                         f'$drive(S_bad{index}, 10000) = S_rejected{index}']
        complete = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
                    'S_one = $replay_resume(S_zero, 1)',
                    'S_adjacent = $replay_resume(S_one, 10000)',
                    'S_frontier = $drive(S, 10001)', 'S_whole = $drive(S_start, 10001)',
                    'S_adjacent = S_frontier', 'S_frontier = S_whole',
                    'S_whole.COMPLETION = NORMAL', '$replay_outputs(S_whole.EVENTS) = ' + stdout,
                    'S_whole.CURRENT = eps', 'S_whole.FRAMES = eps', 'S_whole.TODO = eps',
                    'S_whole.HELD = eps', 'S_whole.ITERATORS = eps',
                    '$lookup(S_whole.ENV, [121]) = (n_y)', '$lookup(S_whole.ENV, [97]) = (n_y)',
                    'S_whole.STORE[n_y] = DEFINED (PSTRING $ptascii("q"))',
                    '$heap_valid($heap_graph(S_whole))', '$call_descriptors_valid(S_whole)']
        complete += ['~$throwable_live(S_whole, n_error)']
        assertions = common + checks + error + rejected + complete
        stage_text = ('def $replay_stage(S) = true\n' +
                      ''.join('  -- if ' + condition + '\n' for condition in stage) +
                      'def $replay_stage(S) = false -- otherwise\n')
        path = args.output / (name + '.watsup')
        path.write_text(PREFIX + HELPERS + '\n' + stage_text + '\ndec $main() : bool\ndef $main() = true\n' +
                        ''.join('  -- if ' + condition + '\n' for condition in assertions))
        records.append({'id': name, 'source_id': case, 'fixture': str(path.resolve()),
                        'assertions': len(assertions), 'source_sha256': cases[case]['source_sha256']})

    def guard_mutations(tasks='S.TODO'):
        guard = 'REF_REPLAY_ORIGIN porigin_source z prefowner*'
        phase = 'REF_REPLAY_PHASE porigin_source z prefowner*'
        return [f'S[.TODO = $replay_replace({tasks}, {guard}, eps)]',
                f'S[.TODO = $replay_replace({tasks}, {phase}, eps)]',
                f'S[.TODO = $replay_replace({tasks}, {guard}, [REF_REPLAY_ORIGIN porigin_source $(z + 100) prefowner*])]',
                f'S[.TODO = $replay_replace($replay_replace({tasks}, {phase}, eps), {guard}, [{phase}, {guard}])]']

    f = ['$replay_function(S, [102])']
    after = 'S.TODO = (REF_REPLAY_AFTER porigin_source z prefowner*) :: (REF_REPLAY_ORIGIN porigin_source z prefowner*) :: (REF_REPLAY_PHASE porigin_source z prefowner*) :: ptask_tail*'
    rebuilt = [after, 'prefowner* = prefowner_first :: prefowner_tail*',
               'porigin_owner = $ref_owner_origin(prefowner_first)',
               '$scalar_tasks(S.TODO, 0) = eps',
               '$ref_replay_after_tasks(S, porigin_owner) = GOTOTASKS ptask_source*',
               '$scalar_tasks(ptask_source*, 0) = [LOOP_NEXT statement_loop (porigin_loop)]',
               '$origin_node(S.SOURCES, porigin_loop) = (statement_loop)',
               '$tasks_nodes(ptask_source*) = eps', 'S_next = $drive_steps(S, 1)',
               'S_next.TODO = ptask_source*', 'S_next.STORE = S.STORE',
               'S_next.ARRAYS = S.ARRAYS', 'S_next.ALLOCATIONS = S.ALLOCATIONS',
               'S_next.HELD = S.HELD', 'S_next.ITERATORS = S.ITERATORS',
               '$call_descriptors_valid(S_next)', '$heap_valid($heap_graph(S_next))',
               'ptask_loop = LOOP_NEXT statement_loop (porigin_loop)']
    loop_bad = ['S_next[.TODO = $replay_replace(S_next.TODO, ptask_loop, [LOOP_NEXT statement_loop eps])]',
                'S_next[.TODO = $replay_replace(S_next.TODO, ptask_loop, [LOOP_NEXT statement_loop (porigin_source)])]']
    for name, kind in (('for', 2), ('while', 0), ('do', 1)):
        fixture('restored-' + name, 'ref-replay-scalar-' + name, f + [after], rebuilt + [
            'prefowner* = (REPLAY_TRY porigin_owner) :: eps',
            '$scalar_loop_kind(statement_loop) = ' + str(kind),
            'porigin_source = PORIGIN n_unit pcpath_source', 'porigin_loop = PORIGIN n_unit pcpath_loop',
            '$effect_below(pcpath_loop ++ [PCFIELD $loop_body_field(statement_loop)], pcpath_source)'],
            guard_mutations() + loop_bad)

    for name, flag in (('break2', 'false'), ('continue2', 'true')):
        head = f'FINALLY_JUMP porigin_owner porigin_jump 2 2 {flag}'
        fixture('pending-' + name, 'ref-replay-scalar-' + name, f + [
            'S.TODO = (' + head + ') :: ptask_tail*',
            '$replay_guard(S.TODO) = (REF_REPLAY_ORIGIN porigin_source z prefowner*)'], [
            'S.TODO = (' + head + ') :: ptask_tail*',
            '$replay_guard(S.TODO) = (REF_REPLAY_ORIGIN porigin_source z prefowner*)',
            '$scalar_tasks(S.TODO, 0) = eps',
            '$ref_replay_after_tasks(S, porigin_owner) = GOTOTASKS ptask_source*',
            '$scalar_tasks(ptask_source*, 0) = [LOOP_NEXT statement_inner (porigin_inner), LOOP_NEXT statement_outer (porigin_outer)]',
            '$scalar_loop_kind(statement_inner) = 0', '$scalar_loop_kind(statement_outer) = 2',
            '$origin_node(S.SOURCES, porigin_inner) = (statement_inner)',
            '$origin_node(S.SOURCES, porigin_outer) = (statement_outer)',
            'porigin_inner = PORIGIN n_unit pcpath_inner', 'porigin_outer = PORIGIN n_unit pcpath_outer',
            '$effect_below(pcpath_outer ++ [PCFIELD 3], pcpath_inner)',
            '$tasks_nodes(ptask_source*) = eps', 'S_next = $drive_steps(S, 1)',
            '$scalar_tasks(S_next.TODO, 0) = ' + ('[LOOP_NEXT statement_outer (porigin_outer)]' if flag == 'true' else 'eps'),
            '$replay_guard(S_next.TODO) = eps', '$call_descriptors_valid(S_next)',
            '$heap_valid($heap_graph(S_next))'], guard_mutations() + [
            f'S[.TODO = $replay_replace(S.TODO, {head}, [FINALLY_JUMP porigin_owner porigin_jump 1 2 {flag}])]',
            f'S[.TODO = $replay_replace(S.TODO, {head}, [FINALLY_JUMP porigin_owner porigin_source 2 2 {flag}])]'])

    for name, constructor in (
        ('method', 'NStmtClassMethod phpType14 phpType24 phpType4 phpType11 phpType16 phpType18 phpType47 metadata_function'),
        ('closure', 'NExprClosure phpType14 phpType4_static phpType4_ref phpType16 phpType21 phpType18 phpType23 metadata_function'),
    ):
        fixture('saved-' + name + '-update', 'ref-replay-scalar-' + name, [
            '$replay_function(S, [117,112,100])', 'S.FRAMES = pframe :: pframe_tail*',
            '$replay_outputs(S.EVENTS) = ' + str(list(b'I;F;C;F;A0;'))], [
            'S.FRAMES = pframe :: pframe_tail*', 'pframe.CONTEXT = (pcallcontext)',
            'S_scope = $constant_frame_scope(S, pframe, pframe_tail*)',
            '$origin_node(S.SOURCES, pcallcontext.FUNCTION) = (' + constructor + ')',
            '$target_function(S_scope, $context_target(pcallcontext)) = (pfunction)',
            'pfunction.ORIGIN = pcallcontext.FUNCTION',
            '$scalar_tasks(pframe.TODO, 1) = [LOOP_TEST statement_loop (porigin_loop)]',
            '$scalar_loop_kind(statement_loop) = 2', '$origin_node(S.SOURCES, porigin_loop) = (statement_loop)',
            '$call_tasks_valid(S_scope, pframe.TODO)', '$replay_guard(pframe.TODO) = eps',
            '$lookup(S_scope.ENV, [105]) = (n_i)', 'S_scope.STORE[n_i] = DEFINED (PINT 1)',
            'ptask_test = LOOP_TEST statement_loop (porigin_loop)', '$task_nodes(ptask_test) = eps'], [
            'S[.FRAMES = pframe[.CONTEXT = (pcallcontext[.FUNCTION = porigin_loop])] :: pframe_tail*]',
            'S[.FRAMES = pframe[.CONTEXT = (pcallcontext[.NAME = [117,112,100]])] :: pframe_tail*]',
            'S[.FRAMES = pframe[.TODO = $replay_replace(pframe.TODO, ptask_test, [LOOP_NEXT statement_loop eps])] :: pframe_tail*]'],
            error_scope='S_scope')

    for name, kind in (('outer-try', 'TRY_END'), ('outer-catch', 'FINALLY_ONLY')):
        fixture('restored-' + name, 'ref-replay-scalar-' + name, f + [after], rebuilt + [
            'prefowner* = (REPLAY_TRY porigin_owner) :: (prefowner_outer) :: eps',
            'porigin_outer = $ref_owner_origin(prefowner_outer)',
            'prefowner_outer = ' + ('REPLAY_TRY' if kind == 'TRY_END' else 'REPLAY_CATCH') + ' porigin_outer',
            '$scalar_tasks(ptask_source*, ' + ('2' if kind == 'TRY_END' else '3') + ') = [' + kind + ' porigin_outer]',
            '$scalar_tasks(ptask_source*, ' + ('3' if kind == 'TRY_END' else '2') + ') = eps',
            '$scalar_loop_kind(statement_loop) = 2'], guard_mutations() + loop_bad)

    plain = 'S.TODO = (THROW_SEARCH n_error) :: (REF_REPLAY_AFTER porigin_source z prefowner*) :: (REF_REPLAY_ORIGIN porigin_source z prefowner*) :: (REF_REPLAY_PHASE porigin_source z prefowner*) :: ptask_tail*'
    fixture('plain-try-origin-restoration', 'ref-replay-scalar-naked-break', f + [plain], [plain,
        'prefowner* = prefowner_first :: prefowner_tail*',
        '$ref_replay_after_tasks(S, $ref_owner_origin(prefowner_first)) = GOTOTASKS ptask_source*',
        '$scalar_tasks(ptask_source*, 2) = (TRY_END porigin_plain) :: ptask_tries*',
        '~$finally_present(S, porigin_plain)',
        'ptask_origin = ORIGIN_RETURN $goto_prior_origin(porigin_plain)',
        '$replay_replace(ptask_source*, ptask_origin, eps) =/= ptask_source*',
        '$call_tasks_valid(S[.ORIGIN = $goto_target_origin(S, $ref_owner_origin(prefowner_first), ptask_source*)][.TODO = ptask_source*], ptask_source*)',
        '$scalar_tasks(ptask_source*, 0) = [LOOP_NEXT statement_loop (porigin_loop)]',
        '$tasks_nodes(ptask_source*) = eps', '$throwable_live(S, n_error)',
        'S.OBJECTS[n_error] = THROWABLE pthrowable_error', 'pthrowable_error.KIND = "TypeError"'],
        guard_mutations(), error_scope=None)

    fixture('return-overrides-pending-jump', 'ref-replay-scalar-jump-override-return', f + [
        'S.TODO = (RETURN_REF_FETCH z_return) :: ptask_tail*',
        '$scalar_tasks(S.TODO, 5) = [FINALLY_JUMP porigin_owner porigin_jump 1 1 false]'], [
        'S.TODO = (RETURN_REF_FETCH z_return) :: ptask_tail*',
        '$scalar_tasks(S.TODO, 5) = [FINALLY_JUMP porigin_owner porigin_jump 1 1 false]',
        'S.GLOBALTABLE = (psymboltable)', '$lookup(psymboltable.ENV, [121]) = (n_cell)',
        'S.STORE[n_cell] = DEFINED (PSTRING $ptascii("over"))',
        'S_next = $drive_steps(S, 1)',
        'S_next.TODO = (RETURN_REF_UNWIND (REFERENCE n_cell) z_return false porigin_return) :: ptask_next*',
        '$call_descriptors_valid(S_next)', '$heap_valid($heap_graph(S_next))'])

    goto_case = 'ref-replay-scalar-goto-from-delayed-catch'
    before = 'S.TODO = (GOTO_UNWIND porigin_goto pcpath_goto pcpath_target) :: (FINALLY_ONLY porigin_owner) :: (REF_REPLAY_ORIGIN porigin_source z prefowner*) :: (REF_REPLAY_PHASE porigin_source z prefowner*) :: ptask_tail*'
    fixture('goto-before-outgoing-finalizer', goto_case, f + [before], [before,
        'prefowner* = (REPLAY_TRY porigin_owner) :: eps',
        'porigin_goto = PORIGIN n_unit pcpath_goto', '$goto_site(S, porigin_goto, pcpath_target)',
        '$goto_exits_finally(S, porigin_goto, pcpath_target)', '$scalar_tasks(S.TODO, 0) = eps',
        '$replay_outputs(S.EVENTS) = ' + str(list(b'I;F;C;')),
        'S_next = $drive_steps(S, 1)',
        '$replay_guard(S_next.TODO) = (REF_REPLAY_ORIGIN porigin_source z prefowner*)',
        '$call_descriptors_valid(S_next)', '$heap_valid($heap_graph(S_next))'], guard_mutations() + [
        'S[.TODO = $replay_replace(S.TODO, GOTO_UNWIND porigin_goto pcpath_goto pcpath_target, [GOTO_UNWIND porigin_goto pcpath_goto eps])]'])

    crossed = 'S.TODO = (GOTO_UNWIND porigin_goto pcpath_goto pcpath_target) :: (REF_REPLAY_AFTER porigin_source z prefowner*) :: (REF_REPLAY_ORIGIN porigin_source z prefowner*) :: (REF_REPLAY_PHASE porigin_source z prefowner*) :: ptask_tail*'
    fixture('goto-restores-consumed-loop', goto_case, f + [crossed], [crossed,
        'prefowner* = (REPLAY_TRY porigin_owner) :: eps',
        '$replay_outputs(S.EVENTS) = ' + str(list(b'I;F;C;F;')),
        '$ref_replay_after_tasks(S, porigin_owner) = GOTOTASKS ptask_source*',
        '$scalar_tasks(ptask_source*, 0) = [LOOP_NEXT statement_loop (porigin_loop)]',
        '$origin_node(S.SOURCES, porigin_loop) = (statement_loop)', '$tasks_nodes(ptask_source*) = eps',
        'S_next = $drive_steps(S, 1)',
        'S_next.TODO = (GOTO_UNWIND porigin_goto pcpath_goto pcpath_target) :: ptask_source*',
        'S_next.STORE = S.STORE', 'S_next.ALLOCATIONS = S.ALLOCATIONS',
        'S_next.HELD = S.HELD', 'S_next.ITERATORS = S.ITERATORS',
        '$call_descriptors_valid(S_next)', '$heap_valid($heap_graph(S_next))'], guard_mutations())

    label = 'S.TODO = (STMT (NStmtLabel (NIdentifier (BYTES "TA==") metadata_identifier) metadata_label)) :: ptask_tail*'
    fixture('goto-authenticated-label', goto_case, f + [label], [label,
        'S.ORIGIN = (porigin_label)', '$origin_node(S.SOURCES, porigin_label) = (NStmtLabel (NIdentifier (BYTES "TA==") metadata_identifier) metadata_label)',
        '$goto_label_valid(S, NStmtLabel (NIdentifier (BYTES "TA==") metadata_identifier) metadata_label, S.ORIGIN)',
        '$scalar_tasks(S.TODO, 0) = eps', '$scalar_tasks(S.TODO, 1) = eps', '$replay_guard(S.TODO) = eps',
        '$lookup(S.ENV, [105]) = (n_i)', 'S.STORE[n_i] = DEFINED (PINT 0)',
        '$replay_outputs(S.EVENTS) = ' + str(list(b'I;F;C;F;'))], [
        'S[.ORIGIN = eps]',
        'S[.TODO = (STMT (NStmtLabel (NIdentifier (BYTES "bWlzc2luZw==") metadata_identifier) metadata_label)) :: ptask_tail*]'])

    direct = 'S.TODO = (GOTO_UNWIND porigin_goto pcpath_goto pcpath_target) :: (REF_REPLAY_ORIGIN porigin_source z prefowner*) :: (REF_REPLAY_PHASE porigin_source z prefowner*) :: ptask_tail*'
    fixture('goto-crosses-direct-replay-pair', 'ref-replay-scalar-goto-direct-replay-pair', f + [direct], [direct,
        'prefowner* = prefowner_first :: prefowner_outer :: prefowner_tail*',
        '~$finally_present(S, $ref_owner_origin(prefowner_first))',
        '$finally_present(S, $ref_owner_origin(prefowner_outer))',
        '$goto_exits_finally(S, porigin_goto, pcpath_target)', '$goto_site(S, porigin_goto, pcpath_target)',
        '$scalar_tasks(S.TODO, 0) = eps',
        '$replay_outputs(S.EVENTS) = ' + str(list(b'I;F;G;F;C;')),
        'S_next = $drive_steps(S, 1)',
        'S_next.TODO = (GOTO_UNWIND porigin_goto pcpath_goto pcpath_target) :: (REF_REPLAY_AFTER porigin_source z prefowner*) :: (REF_REPLAY_ORIGIN porigin_source z prefowner*) :: (REF_REPLAY_PHASE porigin_source z prefowner*) :: ptask_tail*',
        'S_next.STORE = S.STORE', 'S_next.ALLOCATIONS = S.ALLOCATIONS',
        'S_next.HELD = S.HELD', 'S_next.ITERATORS = S.ITERATORS',
        '$call_descriptors_valid(S_next)', '$heap_valid($heap_graph(S_next))'], guard_mutations() + [
        'S[.TODO = $replay_replace(S.TODO, GOTO_UNWIND porigin_goto pcpath_goto pcpath_target, [GOTO_UNWIND porigin_goto pcpath_goto eps])]'])

    (args.output / 'manifest.json').write_text(json.dumps({
        'source_reports': reports, 'fixtures': len(records),
        'assertions': sum(row['assertions'] for row in records), 'records': records,
    }, indent=2) + '\n')
    print(json.dumps({'fixtures': len(records), 'assertions': sum(row['assertions'] for row in records)}))


if __name__ == '__main__':
    main()
