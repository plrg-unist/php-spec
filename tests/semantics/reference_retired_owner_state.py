#!/usr/bin/env python3
"""Emit source-reached physical owner retirement fixtures; launch no processes."""
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

HELPERS = r'''dec $owner_stage(pstate, nat) : bool
dec $owner_find(pstate, nat, nat) : pstate
def $owner_find(S, n, n_stage) = S[.COMPLETION = NORMAL]
  -- if $owner_stage(S, n_stage)
  -- if S.COMPLETION = BUDGET
def $owner_find(S, n, n_stage) = $owner_find($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)), n_stage)
  -- if ~$owner_stage(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $replay_stage(S) = $owner_stage(S, 0)
dec $owner_kind(ptask) : nat
def $owner_kind(RETIRED_SWITCH_END pretiredowner) = 0
def $owner_kind(RETIRED_FOREACH_NEXT pretiredowner) = 1
def $owner_kind(RETIRED_OWNER_PHASE pretiredowner) = 2
def $owner_kind(SWITCH_NEXT statement porigin poperand) = 3
def $owner_kind(FOREACH_NEXT n pnode statement porigin? z) = 4
def $owner_kind(ptask) = 5 -- otherwise
dec $owner_tasks(ptask*, nat) : ptask*
def $owner_tasks(eps, n_kind) = eps
def $owner_tasks(ptask_head :: ptask_tail*, n_kind) = ptask_head :: $owner_tasks(ptask_tail*, n_kind)
  -- if $owner_kind(ptask_head) = n_kind
def $owner_tasks(ptask_head :: ptask_tail*, n_kind) = $owner_tasks(ptask_tail*, n_kind)
  -- if $owner_kind(ptask_head) =/= n_kind
dec $owner_error(pobject) : bool
def $owner_error(THROWABLE pthrowable) = true
def $owner_error(pobject) = false -- otherwise
dec $owner_errors_dead(pstate, pobject*, nat) : bool
def $owner_errors_dead(S, eps, n) = true
def $owner_errors_dead(S, pobject :: pobject_tail*, n) = (~$throwable_live(S, n) /\ $owner_errors_dead(S, pobject_tail*, $nabs($(n + 1))))
  -- if $owner_error(pobject)
def $owner_errors_dead(S, pobject :: pobject_tail*, n) = $owner_errors_dead(S, pobject_tail*, $nabs($(n + 1)))
  -- if ~$owner_error(pobject)
'''


NEGATIVE_SHA = {
    'switch-one-survivor-capture-negative': '2b148948dbd4794b1040ae802bf2c4013dd7221b8e5d106b2795f5c0551aff25',
    'switch-later-loss-no-read-end': '2a3eeea283275373aca86d5db7592e8dcc0fd44549d51e8c54e21985cd1c89a3',
    'foreach-later-loss-read-boundary': 'e88b1f90efb3a304b9713041f2ca91286d3d870a0bc9e094ef52141d220b7ca0',
    'switch-later-last-owner-loss-no-read-end': 'cc01a4796b28a06ffaf2c947de4de69e2a463025b52f001307097cf540f81158',
    'foreach-later-last-owner-loss-read-refusal': 'fcf6de1bb02c4ca71376c94e9e6a487e5d9e27c28dc4e2232e9c8628f338c4fa',
    'switch-shared-empty-capture-negative': 'd1ac7f68fdeeed1e5d19a25d5e04e55bc623c8af06cfaa89988930dda929853f',
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw', type=Path, required=True)
    parser.add_argument('--extended-raw', type=Path, required=True)
    parser.add_argument('--negative-raw', type=Path, required=True)
    parser.add_argument('--immutable-raw', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    cases = {}
    for name in ('reference_retired_owner_cases.json', 'reference_retired_owner_extended_cases.json'):
        cases.update({row['id']: row for row in json.loads((ROOT / 'tests/semantics' / name).read_text())['cases']})
    packets = {}
    report_paths = []
    for directory in (args.raw, args.extended_raw):
        path = directory / 'report.json'
        report = json.loads(path.read_text())
        assert report['passed'] and report['revision'] == report['head_after'] and report['status_after'] == ''
        assert report['pins'] == report['pins_after']
        for row in report['records']:
            assert row['coherent_pass'] and row['model']['status'] == 'normal'
            packets[row['id']] = (directory / row['id'], row)
        report_paths.append(str(path.resolve()))
    assert packets.keys() == cases.keys()
    negative = {}
    for directory in (args.negative_raw, args.immutable_raw):
        negative_path = directory / 'report.json'
        negative_report = json.loads(negative_path.read_text())
        assert negative_report['passed'] and negative_report['revision'] == negative_report['head_after']
        assert negative_report['status_after'] == '' and negative_report['pins'] == negative_report['pins_after']
        assert negative_report['model_evaluations'] == negative_report['native_observations'] == negative_report['source_agreements'] == 0
        report_paths.append(str(negative_path.resolve()))
        for row in negative_report['records']:
            assert row['id'] not in negative and row['source_sha256'] == NEGATIVE_SHA[row['id']]
            negative[row['id']] = (directory / row['id'], row)
    assert negative.keys() == NEGATIVE_SHA.keys()
    args.output.mkdir(parents=True, exist_ok=True)
    records = []

    def initial(case, negative_case=False):
        directory, row = negative[case] if negative_case else packets[case]
        source = (directory / 'source.php').read_bytes() if negative_case else cases[case]['source'].encode()
        assert hashlib.sha256(source).hexdigest() == row['source_sha256']
        if not negative_case:
            assert row['source_sha256'] == cases[case]['source_sha256']
            expected = cases[case]['expected_coherent_stdout'].encode()
            assert base64.b64decode(row['model']['stdout']) == expected
            assert row['model']['stderr'] == '' and row['model']['exit_status'] == 0
        else:
            assert row['parsed'] and row['checked_fixture'] and not row['native_observation'] and not row['model_evaluation']
        parsed = json.loads((directory / 'parsed.json').read_text())
        checked = json.loads((directory / 'checked.json').read_text())
        facts = json.loads((directory / 'request.json').read_text())
        assert parsed['accepted'] and checked['ok'] and checked['fixture']
        return ('$php_request_run(' + checked['fixture'] + ', 0, ' + json.dumps(facts['file']) +
                ', ' + request_fixture(facts) + ')')

    def fixture(name, case, stages, checks, bad=(), terminal=None, negative_case=False):
        common = ['S_initial = ' + initial(case, negative_case), 'S_initial.COMPLETION = BUDGET',
                  'S_start = S_initial[.COMPLETION = NORMAL]', 'S = $owner_find(S_start, 3000, 0)',
                  'S.COMPLETION = NORMAL', '$owner_stage(S, 0)', '$call_descriptors_valid(S)',
                  '$heap_valid($heap_graph(S))']
        rejected = []
        for i, mutation in enumerate(bad):
            rejected += [f'S_bad{i} = ' + mutation + '[.COMPLETION = NORMAL]',
                         f'~$call_descriptors_valid(S_bad{i})',
                         f'S_rejected{i} = $drive(S_bad{i}, 0)',
                         f'S_rejected{i}.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"',
                         f'$drive(S_bad{i}, 10000) = S_rejected{i}']
        complete = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
                    'S_one = $replay_resume(S_zero, 1)', 'S_adjacent = $replay_resume(S_one, 10000)',
                    'S_frontier = $drive(S, 10001)', 'S_whole = $drive(S_start, 10001)',
                    'S_adjacent = S_frontier', 'S_frontier = S_whole']
        if terminal is None:
            complete += ['S_whole.COMPLETION = NORMAL',
                         '$replay_outputs(S_whole.EVENTS) = ' + str(list(cases[case]['expected_coherent_stdout'].encode())),
                         'S_whole.CURRENT = eps', 'S_whole.FRAMES = eps', 'S_whole.TODO = eps',
                         'S_whole.RETIREDOWNERS = eps', 'S_whole.HELD = eps', 'S_whole.ITERATORS = eps',
                         '$lookup(S_whole.ENV, $ptascii("c")) = (n_c_terminal)',
                         'S_whole.STORE[n_c_terminal] = DEFINED (PARRAY n_array_terminal)',
                         'S_whole.ARRAYS[n_array_terminal].ITEMS[0] = ENTRY (KINT 0) (DIRECT (PINT 1))',
                         '$lookup(S_whole.ENV, $ptascii("' + ('r' if case == 'foreach-trace-args-constructor-saved-continue' else 'a') + '")) = (n_result_terminal)',
                         '$lookup(S_whole.ENV, $ptascii("' + ('x' if case == 'foreach-return-active-finalizer-inner-catch-saved' else 'y') + '")) = (n_selected_terminal)',
                         'n_result_terminal = n_selected_terminal',
                         'S_whole.STORE[n_selected_terminal] = DEFINED (PSTRING $ptascii("' + ('s' if case == 'foreach-return-active-finalizer-inner-catch-saved' else 'new' if case == 'foreach-pending-header-reference-return' else 'ok') + '"))',
                         '$owner_errors_dead(S_whole, S_whole.OBJECTS, 0)',
                         '$heap_valid($heap_graph(S_whole))', '$call_descriptors_valid(S_whole)']
        else:
            complete += terminal
        assertions = common + checks + rejected + complete
        stage_text = ''
        for k, conditions in stages.items():
            stage_text += f'def $owner_stage(S, {k}) = true\n' + ''.join('  -- if ' + x + '\n' for x in conditions)
        stage_text += 'def $owner_stage(S, n_stage) = false -- otherwise\n'
        out = args.output / (name + '.watsup')
        out.write_text(PREFIX + HELPERS + '\n' + stage_text + '\ndec $main() : bool\ndef $main() = true\n' +
                       ''.join('  -- ' + (x if x.startswith('PhpStep:') else 'if ' + x) + '\n' for x in assertions))
        records.append({'id': name, 'source_id': case, 'fixture': str(out.resolve()),
                        'source_sha256': (negative[case][1] if negative_case else cases[case])['source_sha256'],
                        'assertions': len(assertions), 'source_packets_only': negative_case})

    f = ['$replay_function(S, $ptascii("f"))']
    capture = ['S.TODO = (RETURN_REF_UNWIND poperand z b porigin_return) :: ptask_owner :: ptask_tail*',
               '$retired_capture(S, porigin_return, z, b, ptask_owner, ptask_tail*) = (pretiredowner)']

    def globals_same(scope, row='pretiredowner'):
        return ['S_globals = $global_table_view(' + scope + ')',
                '$lookup(S_globals.ENV, $ptascii("b")) = (n_b)',
                '$lookup(S_globals.ENV, $ptascii("c")) = (n_c)',
                'S_globals.STORE[n_b] = DEFINED (PARRAY ' + row + '.ARRAY)',
                'S_globals.STORE[n_c] = DEFINED (PARRAY ' + row + '.ARRAY)']

    capture_ids = ['switch-delayed-cow', 'foreach-value-delayed-cow', 'foreach-value-finalizer-cow',
                   'switch-before-first-finalizer', 'foreach-before-first-finalizer']
    for case in capture_ids:
        foreach = case.startswith('foreach')
        before = 3 if case == 'foreach-value-finalizer-cow' else 4
        checks = capture + ['S.RETIREDOWNERS = eps', '$task_nodes(ptask_owner) = [HARRAY pretiredowner.ARRAY]',
                           'pretiredowner.FIRSTRETURN = porigin_return', 'pretiredowner.LASTRETURN = porigin_return',
                           'pretiredowner.FIRSTLINE = z', 'pretiredowner.LASTLINE = z',
                           '$heap_owners($heap_graph(S), HARRAY pretiredowner.ARRAY) = ' + str(before)] + globals_same('S')
        if foreach:
            checks += ['ptask_owner = FOREACH_NEXT n_iter (HARRAY pretiredowner.ARRAY) statement (pretiredowner.OWNER) z_owner',
                       'pretiredowner.POSITION = (n_position)',
                       '$iterator_lookup(S.ITERATORS, n_iter) = (ITERATOR n_iter pretiredowner.ARRAY false ([(CURSOR pretiredowner.ARRAY n_position)]))']
        else:
            checks += ['ptask_owner = SWITCH_NEXT statement pretiredowner.OWNER (KNOWN (PARRAY pretiredowner.ARRAY))']
        if 'before-first-finalizer' in case:
            checks += ['b = false']
        if case == 'foreach-value-finalizer-cow':
            checks += ['$lookup(S_globals.ENV, $ptascii("src")) = (n_src)',
                       'S.STORE[n_src] = DEFINED (PARRAY n_rebound)', 'n_rebound =/= pretiredowner.ARRAY']
        checks += ['S_next = $drive_steps(S, 1)', 'S_next.RETIREDOWNERS = [pretiredowner]',
                   'S_next.STORE = S.STORE', 'S_next.ARRAYS = S.ARRAYS',
                   '$heap_owners($heap_graph(S_next), HARRAY pretiredowner.ARRAY) = ' + str(before - 1),
                   'HARRAY pretiredowner.ARRAY <- S_next.ALLOCATIONS', '$retired_row_valid(S_next, pretiredowner)',
                   '$retired_current_valid(S_next)', '$call_descriptors_valid(S_next)',
                   '$owner_tasks(S_next.TODO, 0) = eps', '$owner_tasks(S_next.TODO, 1) = eps',
                   '$owner_tasks(S_next.TODO, 2) = eps']
        if foreach:
            checks += ['$iterator_lookup(S_next.ITERATORS, n_iter) = eps']
        bad = ['S_next[.RETIREDOWNERS = [pretiredowner[.FIRSTLINE = $(z + 100)]]]',
               'S_next[.RETIREDOWNERS = [pretiredowner, pretiredowner]]']
        if 'before-first-finalizer' in case:
            checks += ['S_next.TODO = (RETURN_REF_UNWIND poperand z false porigin_return) :: ptask_next*']
            bad += ['S_next[.TODO = [RETURN_REF_UNWIND poperand z false porigin_return]]']
        fixture('first-release-' + case, case, {0: f + capture}, checks, bad)

    def pair(scope='S'):
        return [scope + '.RETIREDOWNERS = [pretiredowner]', '$retired_pair_valid(' + scope + ', pretiredowner)',
                'ptask_end = $retired_end_task(pretiredowner)', 'ptask_phase = RETIRED_OWNER_PHASE pretiredowner',
                '$task_nodes(ptask_end) = eps', '$task_nodes(ptask_phase) = eps',
                '$owner_tasks(' + scope + '.TODO, 2) = [ptask_phase]',
                '$owner_tasks(' + scope + '.TODO, 3) = eps', '$owner_tasks(' + scope + '.TODO, 4) = eps']

    def pair_bad(scope='S', saved=False):
        tasks = scope + '.TODO'
        def change(new, rows='[pretiredowner]'):
            return ('S[.FRAMES = pframe[.TODO = ' + new + '][.RETIREDOWNERS = ' + rows + '] :: pframe_tail*]'
                    if saved else scope + '[.TODO = ' + new + '][.RETIREDOWNERS = ' + rows + ']')
        return [change('$replay_replace(' + tasks + ', ptask_end, eps)'),
                change('$replay_replace(' + tasks + ', ptask_phase, eps)'),
                change('$replay_replace(' + tasks + ', ptask_end, [ptask_end, ptask_end])'),
                change('$replay_replace($replay_replace(' + tasks + ', ptask_phase, eps), ptask_end, [ptask_phase, ptask_end])'),
                change(tasks, 'eps'), change(tasks, '[pretiredowner, pretiredowner]'),
                change(tasks, '[pretiredowner[.ARRAY = |S.ARRAYS|]]'),
                change(tasks, '[pretiredowner[.LASTLINE = $(pretiredowner.LASTLINE + 100)]]'),
                change('$replay_replace($replay_replace(' + tasks + ', ptask_end, [$retired_end_task(pretiredowner[.ARRAY = |S.ARRAYS|])]), ptask_phase, [RETIRED_OWNER_PHASE pretiredowner[.ARRAY = |S.ARRAYS|]])', '[pretiredowner[.ARRAY = |S.ARRAYS|]]')]

    after = 'S.TODO = (REF_REPLAY_AFTER porigin_source z (prefowner :: prefowner_tail*)) :: (REF_REPLAY_ORIGIN porigin_source z (prefowner :: prefowner_tail*)) :: (REF_REPLAY_PHASE porigin_source z (prefowner :: prefowner_tail*)) :: ptask_tail*'
    for case in ('switch-delayed-cow', 'foreach-value-finalizer-cow'):
        checks = [after, 'S.RETIREDOWNERS = [pretiredowner]', '$retired_pending(S, pretiredowner, S.TODO)',
                  '$ref_replay_after_tasks(S, $ref_owner_origin(prefowner)) = GOTOTASKS ptask_source*',
                  '$retired_pair(ptask_source*, pretiredowner)', '$tasks_nodes(ptask_source*) = eps',
                  'S_next = $drive_steps(S, 1)', 'S_next.TODO = ptask_source*',
                  'S_next.STORE = S.STORE', 'S_next.ARRAYS = S.ARRAYS', 'S_next.ALLOCATIONS = S.ALLOCATIONS',
                  'S_next.ITERATORS = S.ITERATORS',
                  '$heap_owners($heap_graph(S_next), HARRAY pretiredowner.ARRAY) = $heap_owners($heap_graph(S), HARRAY pretiredowner.ARRAY)',
                  '$call_descriptors_valid(S_next)'] + pair('S_next')
        fixture('restore-borrowed-' + case, case, {0: f + [after]}, checks, pair_bad('S_next'))

    for case in ('foreach-two-return-sites', 'foreach-repeat-late'):
        stage = f + ['S.TODO = (RETURN_REF_UNWIND poperand z b porigin_new) :: (RETIRED_FOREACH_NEXT pretiredowner) :: (RETIRED_OWNER_PHASE pretiredowner) :: ptask_tail*',
                     'pretiredowner.POSITION = (2)']
        checks = stage[1:] + pair() + [
            'pretiredowner.FIRSTRETURN = pretiredowner.LASTRETURN',
            'pretiredowner_next = pretiredowner[.LASTRETURN = porigin_new][.LASTLINE = z]',
            'S_next = $drive_steps(S, 1)', 'S_next.RETIREDOWNERS = [pretiredowner_next]',
            'pretiredowner_next.FIRSTRETURN = pretiredowner.FIRSTRETURN',
            'pretiredowner_next.FIRSTLINE = pretiredowner.FIRSTLINE',
            'pretiredowner_next.ARRAY = pretiredowner.ARRAY', 'pretiredowner_next.POSITION = pretiredowner.POSITION',
            '$owner_tasks(S_next.TODO, 1) = eps', '$owner_tasks(S_next.TODO, 2) = eps',
            'S_next.STORE = S.STORE', 'S_next.ARRAYS = S.ARRAYS',
            'S_next.ITERATORS = S.ITERATORS', 'S_next.NEXTITER = S.NEXTITER',
            '$heap_owners($heap_graph(S_next), HARRAY pretiredowner.ARRAY) = $heap_owners($heap_graph(S), HARRAY pretiredowner.ARRAY)',
            '$call_descriptors_valid(S_next)']
        checks += ['porigin_new ' + ('=/=' if case == 'foreach-two-return-sites' else '=') + ' pretiredowner.LASTRETURN']
        fixture('borrowed-priority-' + case, case, {0: stage}, checks, pair_bad())

    case = 'foreach-return-active-finalizer-inner-catch-saved'
    stage = f + ['S.RETIREDOWNERS = [pretiredowner]',
                 'S.TODO = (THROW_SEARCH n_error) :: (TRY_END porigin_try) :: ptask_tail*',
                 'S.OBJECTS[n_error] = THROWABLE pthrowable', 'pthrowable.KIND = "Exception"']
    checks = stage[1:] + ['$retired_pending(S, pretiredowner, S.TODO)',
                         '$throwable_handler(S, n_error, porigin_try) = (n_index)',
                         '$retired_select_catch(S, porigin_try, n_index) = S',
                         'S_next = $drive_steps(S, 1)', 'S_next.RETIREDOWNERS = S.RETIREDOWNERS',
                         '$call_descriptors_valid(S_next)', '$throwable_live(S_next, n_error)']
    fixture('ordinary-catch-keeps-pending-owner', case, {0: stage}, checks)
    stage = ['$replay_function(S, $ptascii("ping"))', 'S.FRAMES = pframe :: pframe_tail*',
             'pframe.RETIREDOWNERS = [pretiredowner]']
    checks = stage[1:] + ['S.RETIREDOWNERS = eps', 'S_scope = $constant_frame_scope(S, pframe, pframe_tail*)',
                         '$replay_function(S_scope, $ptascii("f"))', 'S_scope.RETIREDOWNERS = [pretiredowner]',
                         '$retired_pending(S_scope, pretiredowner, pframe.TODO)',
                         '$retired_current_valid(S_scope)', '$call_tasks_valid(S_scope, pframe.TODO)',
                         'S.CURRENT = (pcallcontext)', 'pcallcontext.CALLSITE = pframe.ORIGIN',
                         '$heap_owners($heap_graph(S), HARRAY pretiredowner.ARRAY) = 3',
                         'S_restored = $owner_find($drive_steps(S, 1), 3000, 1)',
                         'S_restored.RETIREDOWNERS = pframe.RETIREDOWNERS',
                         '$call_descriptors_valid(S_restored)']
    bad = ['S[.RETIREDOWNERS = [pretiredowner]]',
           'S[.FRAMES = pframe[.RETIREDOWNERS = [pretiredowner[.LASTLINE = $(pretiredowner.LASTLINE + 100)]]] :: pframe_tail*]']
    fixture('saved-active-finalizer-pending-owner', case, {
        0: stage, 1: f + ['$replay_outputs(S.EVENTS) = ' + str(list(b'F;P;'))]}, checks, bad)

    for case, kind in (('switch-delayed-cow', 'RETIRED_SWITCH_END'),
                       ('foreach-value-finalizer-cow', 'RETIRED_FOREACH_NEXT')):
        if kind == 'RETIRED_SWITCH_END':
            stage = f + ['S.TODO = (STMT (NStmtBreak phpType5 metadata)) :: ptask_before*',
                         'S.RETIREDOWNERS = [pretiredowner]', '$retired_pair(S.TODO, pretiredowner)']
            suffix = ['$jump_depth(phpType5) = 1',
                      '$goto_saved(S.TODO, pretiredowner.OWNER) = GOTOTASKS ((RETIRED_SWITCH_END pretiredowner) :: (RETIRED_OWNER_PHASE pretiredowner) :: ptask_tail*)']
        else:
            stage = f + ['S.TODO = (' + kind + ' pretiredowner) :: (RETIRED_OWNER_PHASE pretiredowner) :: ptask_tail*',
                         'pretiredowner.POSITION = (n_position)', 'n_position = S.ARRAYS[pretiredowner.ARRAY].SERIAL']
            suffix = []
        checks = stage[1:] + suffix + pair() + ['S_next = $drive_steps(S, 1)', 'S_next.TODO = ptask_tail*',
            'S_next.RETIREDOWNERS = eps', 'S_next.STORE = S.STORE', 'S_next.ARRAYS = S.ARRAYS',
            '$heap_owners($heap_graph(S_next), HARRAY pretiredowner.ARRAY) = $heap_owners($heap_graph(S), HARRAY pretiredowner.ARRAY)',
            'S_next.ITERATORS = S.ITERATORS', '$call_descriptors_valid(S_next)']
        if kind == 'RETIRED_SWITCH_END':
            checks += ['$lookup(S.ENV, $ptascii("e")) = (n_e)',
                'S.STORE[n_e] = DEFINED (POBJECT n_discard_error)', '$throwable_live(S, n_discard_error)',
                'S_transfer = S[.TODO = (THROW_SEARCH n_discard_error) :: (RETIRED_OWNER_PHASE pretiredowner) :: ptask_tail*]',
                'S_discard = $return_discard(S_transfer, RETIRED_SWITCH_END pretiredowner)',
                'S_discard.TODO = (THROW_SEARCH n_discard_error) :: ptask_tail*',
                'S_discard.RETIREDOWNERS = eps', 'S_discard.STORE = S_transfer.STORE',
                'S_discard.ARRAYS = S_transfer.ARRAYS', 'S_discard.ITERATORS = S_transfer.ITERATORS',
                '$throwable_live(S_discard, n_discard_error)', '$heap_valid($heap_graph(S_discard))',
                '$heap_graph(S_discard) = $heap_graph(S_transfer)']
        fixture('no-second-release-' + case, case, {0: stage}, checks, pair_bad())

    case = 'foreach-trace-args-constructor-saved-continue'
    stage = ['$replay_function(S, $ptascii("trace_source"))',
             'S.TODO = (GETTER_INVOKE pgettercall) :: ptask_tail*',
             'pgettercall.METHOD = GET_TRACE']
    checks = stage[1:] + [
        '$throwable_field(S, pgettercall.RECEIVER, "trace") = PARRAY n_trace',
        'S.ARRAYS[n_trace].ITEMS[0] = ENTRY (KINT 0) (DIRECT (PARRAY n_frame))',
        '$trace_array_field(S, n_frame, $ptascii("args")) = PARRAY n_args',
        'S.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 1)), ENTRY (KINT 1) (DIRECT (PINT 2))]',
        'S.ARRAYS[n_args].POSITIONS = [POSITION (KINT 0) 0, POSITION (KINT 1) 1]',
        'S.ARRAYS[n_args].SERIAL = 2', '$retired_dense_array(S.ARRAYS[n_args])',
        'S_capture = $owner_find($drive_steps(S, 1), 3000, 1)',
        'S_capture.TODO = (RETURN_REF_UNWIND poperand z b porigin_return) :: ptask_owner :: ptask_capture*',
        '$retired_capture(S_capture, porigin_return, z, b, ptask_owner, ptask_capture*) = (pretiredowner)',
        'pretiredowner.ARRAY = n_args', 'pretiredowner.POSITION = (1)',
        '$task_nodes(ptask_owner) = [HARRAY n_args]',
        '$heap_owners($heap_graph(S_capture), HARRAY n_args) = 4',
        'S_removed = $drive_steps(S_capture, 1)', 'S_removed.RETIREDOWNERS = [pretiredowner]',
        '$heap_owners($heap_graph(S_removed), HARRAY n_args) = 3',
        '$call_descriptors_valid(S_capture)', '$call_descriptors_valid(S_removed)']
    fixture('dense-trace-args-first-release', case, {0: stage, 1: f + capture}, checks)

    stage = ['$replay_function(S, $ptascii("ping"))', 'S.FRAMES = pframe :: pframe_tail*',
             'pframe.RETIREDOWNERS = [pretiredowner]', 'pretiredowner.POSITION = (1)',
             '$retired_pair(pframe.TODO, pretiredowner)']
    checks = stage[1:] + ['S.RETIREDOWNERS = eps', 'S_scope = $constant_frame_scope(S, pframe, pframe_tail*)',
                         '$replay_function(S_scope, $ptascii("f"))'] + pair('S_scope') + [
        'S.CURRENT = (pcallcontext)', 'pcallcontext.CALLSITE = pframe.ORIGIN',
        'pframe.ORIGIN = (porigin_call)',
        '$origin_node(S.SOURCES, porigin_call) = (NExprFuncCall (NName (BYTES "cGluZw==") metadata_name) (SEQUENCE eps) metadata_call)',
        '$call_tasks_valid(S_scope, pframe.TODO)',
        'S_restored = $owner_find($drive_steps(S, 1), 3000, 1)',
        'S_restored.RETIREDOWNERS = pframe.RETIREDOWNERS',
        '$retired_pair_valid(S_restored, pretiredowner)', '$call_descriptors_valid(S_restored)']
    fixture('saved-installed-owner-pair', case, {
        0: stage, 1: f + ['$replay_outputs(S.EVENTS) = ' + str(list(b'F1;C1;F1;A1;P;'))]},
        checks, pair_bad('S_scope', saved=True))
    stage = f + ['S.TODO = (STMT (NStmtContinue phpType5 metadata)) :: ptask_tail*',
                 'S.RETIREDOWNERS = [pretiredowner]', 'pretiredowner.POSITION = (1)']
    checks = stage[1:] + pair() + [
        '$jump_depth(phpType5) = 1', 'S_next = $drive_steps(S, 1)',
        'S_next.RETIREDOWNERS = S.RETIREDOWNERS', '$retired_pair_valid(S_next, pretiredowner)',
        'S_next.ORIGIN = $goto_target_origin(S_next, pretiredowner.OWNER, S_next.TODO)',
        'S_next.ITERATORS = S.ITERATORS', 'S_next.NEXTITER = S.NEXTITER',
        '$heap_owners($heap_graph(S_next), HARRAY pretiredowner.ARRAY) = $heap_owners($heap_graph(S), HARRAY pretiredowner.ARRAY)',
        '$call_descriptors_valid(S_next)']
    fixture('continue-keeps-owner-region', case, {0: stage}, checks, pair_bad())

    case = 'switch-one-survivor-capture-negative'
    stage = f + ['S.TODO = (RETURN_REF_UNWIND poperand z b porigin_return) :: (SWITCH_NEXT statement porigin_owner (KNOWN (PARRAY n_array))) :: ptask_tail*']
    checks = stage[1:] + [
        '$retired_switch_var_site(S, porigin_owner)', '~$array_immutable(S, n_array)',
        '$heap_owners($heap_graph(S), HARRAY n_array) = 2',
        'ptask_owner = SWITCH_NEXT statement porigin_owner (KNOWN (PARRAY n_array))',
        '$task_nodes(ptask_owner) = [HARRAY n_array]',
        '$retired_capture(S, porigin_return, z, b, ptask_owner, ptask_tail*) = eps',
        'S.RETIREDOWNERS = eps', 'S_next = $drive_steps(S, 1)', 'S_next.RETIREDOWNERS = eps',
        '$heap_owners($heap_graph(S_next), HARRAY n_array) = 1',
        'S_next.STORE = S.STORE', 'S_next.ARRAYS = S.ARRAYS', '$call_descriptors_valid(S_next)']
    terminal = ['S_whole.COMPLETION = UNSUPPORTED "reference return replay requires runtime owner"',
                'S_whole.RETIREDOWNERS = eps', 'S_whole.TODO = eps']
    fixture('one-survivor-capture-refusal', case, {0: stage}, checks, terminal=terminal, negative_case=True)

    case = 'switch-shared-empty-capture-negative'
    stage = f + ['S.TODO = (RETURN_REF_UNWIND poperand z b porigin_return) :: (SWITCH_NEXT statement porigin_owner (KNOWN (PARRAY n_array))) :: ptask_tail*',
                 '$array_immutable(S, n_array)']
    checks = stage[1:] + ['$retired_switch_var_site(S, porigin_owner)',
        'S.ARRAYS[n_array].ITEMS = eps',
        'ptask_owner = SWITCH_NEXT statement porigin_owner (KNOWN (PARRAY n_array))',
        '$task_nodes(ptask_owner) = [HARRAY n_array]',
        '$($heap_owners($heap_graph(S), HARRAY n_array) >= 3)',
        '$retired_capture(S, porigin_return, z, b, ptask_owner, ptask_tail*) = eps',
        'S.RETIREDOWNERS = eps', 'S_next = $drive_steps(S, 1)', 'S_next.RETIREDOWNERS = eps',
        'S_next.STORE = S.STORE', 'S_next.ARRAYS = S.ARRAYS',
        '$heap_owners($heap_graph(S_next), HARRAY n_array) = $nabs($($heap_owners($heap_graph(S), HARRAY n_array) - 1))',
        '$call_descriptors_valid(S_next)']
    terminal = ['S_whole.COMPLETION = UNSUPPORTED "reference return replay requires runtime owner"',
                'S_whole.RETIREDOWNERS = eps', 'S_whole.TODO = eps']
    fixture('shared-empty-capture-refusal', case, {0: stage}, checks, terminal=terminal, negative_case=True)

    for case, zero in (('switch-later-loss-no-read-end', False),
                       ('switch-later-last-owner-loss-no-read-end', True)):
        stage = f + ['S.TODO = (STMT (NStmtBreak phpType5 metadata)) :: ptask_tail*',
                     'S.RETIREDOWNERS = [pretiredowner]']
        checks = stage[1:] + pair() + [
            '$heap_owners($heap_graph(S), HARRAY pretiredowner.ARRAY) = ' + ('0' if zero else '1'),
            '$retired_row_valid(S, pretiredowner)', '$jump_depth(phpType5) = 1',
            'S_next = $drive_steps(S, 1)', 'S_next.RETIREDOWNERS = eps',
            'S_next.STORE = S.STORE', 'S_next.ARRAYS = S.ARRAYS',
            '$heap_owners($heap_graph(S_next), HARRAY pretiredowner.ARRAY) = ' + ('0' if zero else '1'),
            'S_next.ITERATORS = S.ITERATORS', 'S_next.NEXTITER = S.NEXTITER',
            '$call_descriptors_valid(S_next)']
        checks += (['~(HARRAY pretiredowner.ARRAY <- S.ALLOCATIONS)',
                    '~(HARRAY pretiredowner.ARRAY <- S_next.ALLOCATIONS)', '~$retired_live(S, pretiredowner)']
                   if zero else ['HARRAY pretiredowner.ARRAY <- S.ALLOCATIONS', '$retired_live(S, pretiredowner)'])
        terminal = ['S_whole.COMPLETION = NORMAL', 'S_whole.RETIREDOWNERS = eps',
                    'S_whole.FRAMES = eps', 'S_whole.TODO = eps', 'S_whole.ITERATORS = eps',
                    '$heap_valid($heap_graph(S_whole))', '$call_descriptors_valid(S_whole)']
        fixture('later-owner-switch-end-' + ('zero' if zero else 'one'), case,
                {0: stage}, checks, pair_bad(), terminal=terminal, negative_case=True)

    case = 'foreach-later-loss-read-boundary'
    stage = f + ['S.TODO = (RETIRED_FOREACH_NEXT pretiredowner) :: (RETIRED_OWNER_PHASE pretiredowner) :: ptask_tail*',
                 'pretiredowner.POSITION = (1)',
                 '$heap_owners($heap_graph(S), HARRAY pretiredowner.ARRAY) = 1']
    checks = stage[1:] + pair() + [
        'S_globals = $global_table_view(S)', '$lookup(S_globals.ENV, $ptascii("src")) = (n_src)',
        'S.STORE[n_src] = DEFINED (PARRAY n_rebound)', 'n_rebound =/= pretiredowner.ARRAY',
        'S.ARRAYS[n_rebound].ITEMS[1] = ENTRY (KINT 1) (DIRECT (PINT 9))',
        'S.ARRAYS[pretiredowner.ARRAY].ITEMS[1] = ENTRY (KINT 1) (DIRECT (PINT 2))',
        '$retired_live(S, pretiredowner)', 'S_next = $drive_steps(S, 1)',
        'pretiredowner_next = pretiredowner[.POSITION = (2)]',
        'S_next.RETIREDOWNERS = [pretiredowner_next]', 'S_next.ARRAYS = S.ARRAYS',
        'S_next.ITERATORS = S.ITERATORS', 'S_next.NEXTITER = S.NEXTITER',
        '$heap_owners($heap_graph(S_next), HARRAY pretiredowner.ARRAY) = 1',
        'S_value = $owner_find(S_next, 100, 1)', '$lookup(S_value.ENV, $ptascii("v")) = (n_v)',
        'S_value.STORE[n_v] = DEFINED (PINT 2)', '$call_descriptors_valid(S_next)',
        '$call_descriptors_valid(S_value)',
        'pretiredowner_cursor = pretiredowner[.POSITION = ($nabs($(S.ARRAYS[pretiredowner.ARRAY].SERIAL + 1)))]',
        'S_cursor = S[.RETIREDOWNERS = [pretiredowner_cursor]][.TODO = (RETIRED_FOREACH_NEXT pretiredowner_cursor) :: (RETIRED_OWNER_PHASE pretiredowner_cursor) :: ptask_tail*]',
        '$retired_row_valid(S_cursor, pretiredowner_cursor)', '$retired_pair_valid(S_cursor, pretiredowner_cursor)',
        '$call_descriptors_valid(S_cursor)', '~$retired_live(S_cursor, pretiredowner_cursor)',
        '$heap_graph(S_cursor) = $heap_graph(S)',
        'PhpStep: S_cursor ~> S_cursor_next',
        'S_cursor_next.COMPLETION = UNSUPPORTED "reference replay requires live dense value-foreach array"',
        'S_cursor_next.STORE = S_cursor.STORE', 'S_cursor_next.ARRAYS = S_cursor.ARRAYS',
        'S_cursor_next.ITERATORS = S_cursor.ITERATORS', 'S_cursor_next.NEXTITER = S_cursor.NEXTITER',
        'S_cursor_next.RETIREDOWNERS = eps', 'S_cursor_next.TODO = eps',
        '$replay_outputs(S_cursor_next.EVENTS) = $replay_outputs(S_cursor.EVENTS)',
        '$heap_owners($heap_graph(S_cursor_next), HARRAY pretiredowner.ARRAY) = 1']
    terminal = ['S_whole.COMPLETION = NORMAL', 'S_whole.RETIREDOWNERS = eps', 'S_whole.FRAMES = eps',
                'S_whole.TODO = eps', 'S_whole.ITERATORS = eps', '$heap_valid($heap_graph(S_whole))',
                '$call_descriptors_valid(S_whole)']
    fixture('one-live-owner-reads-original-cursor', case, {0: stage, 1: f + [
        '$lookup(S.ENV, $ptascii("v")) = (n_v)', 'S.STORE[n_v] = DEFINED (PINT 2)']},
        checks, pair_bad() + ['S[.RETIREDOWNERS = [pretiredowner[.POSITION = (2)]]]',
                                'S[.RETIREDOWNERS = [pretiredowner[.ARRAY = n_rebound]]]'],
        terminal=terminal, negative_case=True)

    case = 'foreach-later-last-owner-loss-read-refusal'
    stage = f + ['S.TODO = (RETIRED_FOREACH_NEXT pretiredowner) :: (RETIRED_OWNER_PHASE pretiredowner) :: ptask_tail*',
                 'pretiredowner.POSITION = (1)', '~(HARRAY pretiredowner.ARRAY <- S.ALLOCATIONS)']
    checks = stage[1:] + pair() + ['$retired_row_valid(S, pretiredowner)', '~$retired_live(S, pretiredowner)',
        '$heap_owners($heap_graph(S), HARRAY pretiredowner.ARRAY) = 0',
        'PhpStep: S ~> S_next',
        'S_next.COMPLETION = UNSUPPORTED "reference replay requires live dense value-foreach array"',
        'S_next.RETIREDOWNERS = eps', 'S_next.TODO = eps', 'S_next.STORE = S.STORE',
        'S_next.ARRAYS = S.ARRAYS', 'S_next.ITERATORS = S.ITERATORS', 'S_next.NEXTITER = S.NEXTITER',
        '$replay_outputs(S_next.EVENTS) = $replay_outputs(S.EVENTS)',
        '~(HARRAY pretiredowner.ARRAY <- S_next.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_next), HARRAY pretiredowner.ARRAY) = 0']
    terminal = ['S_whole.COMPLETION = UNSUPPORTED "reference replay requires live dense value-foreach array"',
                'S_whole.RETIREDOWNERS = eps', 'S_whole.TODO = eps',
                '~(HARRAY pretiredowner.ARRAY <- S_whole.ALLOCATIONS)']
    fixture('collected-owner-refuses-foreach-read', case, {0: stage}, checks,
            pair_bad(), terminal=terminal, negative_case=True)

    (args.output / 'manifest.json').write_text(json.dumps({
        'source_reports': report_paths, 'fixtures': len(records),
        'assertions': sum(row['assertions'] for row in records), 'records': records,
    }, indent=2) + '\n')
    print(json.dumps({'fixtures': len(records), 'assertions': sum(row['assertions'] for row in records)}))


if __name__ == '__main__':
    main()
