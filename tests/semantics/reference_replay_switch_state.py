#!/usr/bin/env python3
"""Emit genuine no-FREE switch replay frontiers from accepted model packets.

This producer launches no PHP, compiler or model. Run its fixtures with the
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

HELPERS = r'''dec $switch_state_kind(ptask) : nat
def $switch_state_kind(SWITCH_REPLAY_END porigin) = 0
def $switch_state_kind(SWITCH_REPLAY_PHASE porigin) = 1
def $switch_state_kind(SWITCH_NEXT statement porigin poperand) = 2
def $switch_state_kind(FINALLY_ONLY porigin) = 3
def $switch_state_kind(ptask) = 4 -- otherwise
dec $switch_state_tasks(ptask*, nat) : ptask*
def $switch_state_tasks(eps, n_kind) = eps
def $switch_state_tasks(ptask_head :: ptask_tail*, n_kind) = ptask_head :: $switch_state_tasks(ptask_tail*, n_kind)
  -- if $switch_state_kind(ptask_head) = n_kind
def $switch_state_tasks(ptask_head :: ptask_tail*, n_kind) = $switch_state_tasks(ptask_tail*, n_kind)
  -- if $switch_state_kind(ptask_head) =/= n_kind
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    cases = {row['id']: row for row in json.loads(
        (ROOT / 'tests/semantics/reference_replay_switch_cases.json').read_text())['cases']}
    path = args.raw / 'report.json'
    report = json.loads(path.read_text())
    assert report['passed'] and report['source_agreements'] == report['model_evaluations'] == len(cases)
    assert report['revision'] == report['head_after'] and report['status_after'] == ''
    assert report['pins'] == report['pins_after']
    rows = {row['id']: row for row in report['records']}
    assert rows.keys() == cases.keys()
    args.output.mkdir(parents=True, exist_ok=True)
    records = []

    def initial(case):
        row = rows[case]
        source = cases[case]['source'].encode()
        assert row['pass'] and row['model']['status'] == 'normal'
        assert hashlib.sha256(source).hexdigest() == row['source_sha256'] == cases[case]['source_sha256']
        for key in ('stdout', 'stderr', 'exit_status'):
            assert row['native'][key] == row['model'][key]
        assert row['native']['exit_status'] == 0 and row['native']['stderr'] == ''
        stdout = base64.b64decode(row['native']['stdout'])
        assert stdout == cases[case]['native_stdout'].encode()
        directory = args.raw / case
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
        error = ['$lookup(' + error_scope + '.ENV, [101]) = (n_error_cell)',
                 error_scope + '.STORE[n_error_cell] = DEFINED (POBJECT n_error)',
                 'S.OBJECTS[n_error] = THROWABLE pthrowable_error',
                 'pthrowable_error.KIND = "TypeError"', '$throwable_live(S, n_error)']
        rejected = []
        for index, mutation in enumerate(bad):
            rejected += [f'S_bad{index} = ' + mutation + '[.COMPLETION = NORMAL]',
                         f'~$call_descriptors_valid(S_bad{index})',
                         f'S_rejected{index} = $drive(S_bad{index}, 0)',
                         f'S_rejected{index}.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"',
                         f'$drive(S_bad{index}, 10000) = S_rejected{index}']
        value = 'ok' if case == 'ref-replay-switch-cv-array-cow' else 'q'
        complete = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
                    'S_one = $replay_resume(S_zero, 1)',
                    'S_adjacent = $replay_resume(S_one, 10000)',
                    'S_frontier = $drive(S, 10001)', 'S_whole = $drive(S_start, 10001)',
                    'S_adjacent = S_frontier', 'S_frontier = S_whole',
                    'S_whole.COMPLETION = NORMAL', '$replay_outputs(S_whole.EVENTS) = ' + stdout,
                    'S_whole.CURRENT = eps', 'S_whole.FRAMES = eps', 'S_whole.TODO = eps',
                    'S_whole.HELD = eps', 'S_whole.ITERATORS = eps',
                    '$lookup(S_whole.ENV, [121]) = (n_y)', '$lookup(S_whole.ENV, [97]) = (n_y)',
                    'S_whole.STORE[n_y] = DEFINED (PSTRING $ptascii("' + value + '"))',
                    '~$throwable_live(S_whole, n_error)',
                    '$heap_valid($heap_graph(S_whole))', '$call_descriptors_valid(S_whole)']
        assertions = common + checks + error + rejected + complete
        stage_text = ('def $replay_stage(S) = true\n' +
                      ''.join('  -- if ' + condition + '\n' for condition in stage) +
                      'def $replay_stage(S) = false -- otherwise\n')
        out = args.output / (name + '.watsup')
        out.write_text(PREFIX + HELPERS + '\n' + stage_text + '\ndec $main() : bool\ndef $main() = true\n' +
                       ''.join('  -- if ' + condition + '\n' for condition in assertions))
        records.append({'id': name, 'source_id': case, 'fixture': str(out.resolve()),
                        'assertions': len(assertions), 'source_sha256': cases[case]['source_sha256']})

    def pair_checks(scope='S'):
        return ['$switch_state_tasks(' + scope + '.TODO, 0) = [SWITCH_REPLAY_END porigin_switch]',
                '$switch_state_tasks(' + scope + '.TODO, 1) = [SWITCH_REPLAY_PHASE porigin_switch]',
                '$switch_state_tasks(' + scope + '.TODO, 2) = eps',
                '$origin_node(S.SOURCES, porigin_switch) = (statement_switch)',
                '$switch_replay_site(' + scope + ', porigin_switch)',
                '$switch_replay_valid(' + scope + ', porigin_switch)',
                'ptask_end = SWITCH_REPLAY_END porigin_switch',
                'ptask_phase = SWITCH_REPLAY_PHASE porigin_switch',
                '$task_nodes(ptask_end) = eps', '$task_nodes(ptask_phase) = eps']

    def pair_bad(scope='S', saved=False):
        tasks = scope + '.TODO'
        def mutate(tasks_new):
            return ('S[.FRAMES = pframe[.TODO = ' + tasks_new + '] :: pframe_tail*]' if saved
                    else scope + '[.TODO = ' + tasks_new + ']')
        return [mutate('$replay_replace(' + tasks + ', ptask_end, eps)'),
                mutate('$replay_replace(' + tasks + ', ptask_phase, eps)'),
                mutate('$replay_replace(' + tasks + ', ptask_end, [ptask_end, ptask_end])'),
                mutate('$replay_replace(' + tasks + ', ptask_phase, [ptask_phase, ptask_phase])'),
                mutate('$replay_replace($replay_replace(' + tasks + ', ptask_phase, eps), ptask_end, [ptask_phase, ptask_end])'),
                mutate('$replay_replace(' + tasks + ', ptask_end, [SWITCH_REPLAY_END porigin_wrong])'),
                mutate('$replay_replace(' + tasks + ', ptask_phase, [SWITCH_REPLAY_PHASE porigin_wrong])')]

    f = ['$replay_function(S, [102])']
    after = 'S.TODO = (REF_REPLAY_AFTER porigin_source z (prefowner :: prefowner_tail*)) :: (REF_REPLAY_ORIGIN porigin_source z (prefowner :: prefowner_tail*)) :: (REF_REPLAY_PHASE porigin_source z (prefowner :: prefowner_tail*)) :: ptask_tail*'
    for case in cases:
        name = case.removeprefix('ref-replay-switch-')
        checks = [after, '$ref_replay_after_tasks(S, $ref_owner_origin(prefowner)) = GOTOTASKS ptask_source*',
                  '$switch_state_tasks(S.TODO, 0) = eps',
                  '$switch_state_tasks(ptask_source*, 0) = [SWITCH_REPLAY_END porigin_switch]',
                  '$switch_state_tasks(ptask_source*, 1) = [SWITCH_REPLAY_PHASE porigin_switch]',
                  '$tasks_nodes(ptask_source*) = eps',
                  'S_next = $drive_steps(S, 1)', 'S_next.TODO = ptask_source*',
                  'S_next.STORE = S.STORE', 'S_next.ARRAYS = S.ARRAYS',
                  'S_next.ALLOCATIONS = S.ALLOCATIONS', 'S_next.HELD = S.HELD',
                  'S_next.ITERATORS = S.ITERATORS', '$call_descriptors_valid(S_next)'] + pair_checks('S_next')
        checks += ['porigin_wrong = porigin_source',
                   'porigin_switch = PORIGIN n_unit pcpath_switch',
                   'porigin_source = PORIGIN n_unit pcpath_source',
                   '$effect_below(pcpath_switch ++ [PCFIELD 1], pcpath_source)']
        if name.startswith('const-'):
            checks += ['$origin_child((porigin_switch), [PCFIELD 0]) = (porigin_subject)',
                       '$compiled_read(S, porigin_subject) = (pvalue_subject)',
                       '~$switch_replay_subject(S[.POOLS = eps], porigin_switch)',
                       '$switch_bool_mode(S, porigin_switch) = ' + ('(true)' if name == 'const-bool' else 'eps')]
            if name == 'const-array':
                checks += ['pvalue_subject = PARRAY n_array', 'HARRAY n_array <- S.ALLOCATIONS']
            bad = pair_bad('S_next') + ['S_next[.POOLS = eps]']
        else:
            checks += ['statement_switch = NStmtSwitch (NExprVariable (BYTES text) metadata_subject) phpType60 metadata',
                       '$cv_name(BYTES text) = (n_name*)',
                       '~$scope_global(S[.ORIGIN = (porigin_switch)], [PCFIELD 0])',
                       '~$direct_this(BYTES text)', '$switch_bool_mode(S, porigin_switch) = eps']
            bad = pair_bad('S_next')
        fixture('restored-' + name, case, f + [after], checks, bad)

    case = 'ref-replay-switch-cv'
    prefix = str(list(b'K;F;C;F;A;'))
    fixture('current-before-fallthrough', case, f + ['$replay_outputs(S.EVENTS) = ' + prefix,
            '$switch_state_tasks(S.TODO, 0) = [SWITCH_REPLAY_END porigin_switch]'],
            pair_checks() + ['S.CURRENT = (pcallcontext)', 'porigin_wrong = pcallcontext.FUNCTION'], pair_bad())

    for case in ('ref-replay-switch-cv', 'ref-replay-switch-const-array'):
        stage = f + ['S.TODO = (SWITCH_REPLAY_END porigin_switch) :: (SWITCH_REPLAY_PHASE porigin_switch) :: ptask_tail*']
        checks = ['S.TODO = (SWITCH_REPLAY_END porigin_switch) :: (SWITCH_REPLAY_PHASE porigin_switch) :: ptask_tail*'] + pair_checks() + ['S.CURRENT = (pcallcontext)', 'porigin_wrong = pcallcontext.FUNCTION',
                 'S_next = $drive_steps(S, 1)', 'S_next.TODO = ptask_tail*',
                 '$switch_state_tasks(S_next.TODO, 0) = eps', '$switch_state_tasks(S_next.TODO, 1) = eps',
                 'S_next.STORE = S.STORE', 'S_next.ARRAYS = S.ARRAYS',
                 'S_next.ALLOCATIONS = S.ALLOCATIONS', 'S_next.REFCELLS = S.REFCELLS',
                 '$call_descriptors_valid(S_next)',
                 '$lookup(S.ENV, [101]) = (n_discard_error_cell)',
                 'S.STORE[n_discard_error_cell] = DEFINED (POBJECT n_discard_error)',
                 '$throwable_live(S, n_discard_error)',
                 'S_discard = $return_discard(S[.TODO = (THROW_SEARCH n_discard_error) :: (SWITCH_REPLAY_PHASE porigin_switch) :: ptask_tail*], ptask_end)',
                 'S_discard.TODO = (THROW_SEARCH n_discard_error) :: ptask_tail*',
                 'S_discard.ORIGIN = (porigin_switch)',
                 'S_discard.STORE = S.STORE', 'S_discard.ARRAYS = S.ARRAYS',
                 'S_discard.ALLOCATIONS = S.ALLOCATIONS', 'S_discard.REFCELLS = S.REFCELLS',
                 '$throwable_live(S_discard, n_discard_error)', '$heap_valid($heap_graph(S_discard))',
                 '$call_descriptors_valid(S_discard)']
        fixture('atomic-end-' + case.removeprefix('ref-replay-switch-'), case, stage, checks, pair_bad())

    case = 'ref-replay-switch-const-int'
    fixture('break-consumes-switch-depth', case, f + ['S.TODO = (STMT (NStmtBreak phpType5 metadata)) :: ptask_tail*'],
            ['S.TODO = (STMT (NStmtBreak phpType5 metadata)) :: ptask_tail*'] + pair_checks() + ['S.CURRENT = (pcallcontext)', 'porigin_wrong = pcallcontext.FUNCTION',
            '$jump_depth(phpType5) = 1', 'S_next = $drive_steps(S, 1)',
            '$switch_state_tasks(S_next.TODO, 0) = eps', '$switch_state_tasks(S_next.TODO, 1) = eps',
            '$call_descriptors_valid(S_next)'], pair_bad())

    case = 'ref-replay-switch-outer-catch'
    fixture('saved-switch-in-selected-catch', case, ['$replay_function(S, [103])',
            'S.FRAMES = pframe :: pframe_tail*', '$replay_outputs(S.EVENTS) = ' + str(list(b'K;F;G;C;F;A;'))],
            ['S.FRAMES = pframe :: pframe_tail*', 'pframe.CONTEXT = (pcallcontext)',
             'S_scope = $constant_frame_scope(S, pframe, pframe_tail*)',
             '$replay_function(S_scope, [102])'] + pair_checks('S_scope') + [
             'porigin_wrong = pcallcontext.FUNCTION', '$call_tasks_valid(S_scope, pframe.TODO)',
             '$switch_state_tasks(pframe.TODO, 3) = [FINALLY_ONLY porigin_outer]',
             '$finally_catch_origin(S_scope, porigin_outer, pframe.ORIGIN)',
             'pframe.ORIGIN =/= (porigin_outer)'], pair_bad('S_scope', saved=True), error_scope='S_scope')

    case = 'ref-replay-switch-goto-naked-saved'
    fixture('same-catch-goto-capability', case, f + ['S.TODO = (STMT (NStmtGoto phpType11 metadata)) :: ptask_tail*'], [
            'S.TODO = (STMT (NStmtGoto phpType11 metadata)) :: ptask_tail*',
            'S.ORIGIN = (porigin_goto)', '$goto_target(S, porigin_goto) = (pcpath_target)',
            '$goto_site(S, porigin_goto, pcpath_target)', '~$goto_exits_finally(S, porigin_goto, pcpath_target)',
            '$replay_guard(S.TODO) = (REF_REPLAY_ORIGIN porigin_source z (prefowner :: prefowner_tail*))',
            'porigin_owner = $ref_owner_origin(prefowner)', '~$finally_present(S, porigin_owner)',
            '$ref_replay_caught(S, porigin_owner)', '$switch_state_tasks(S.TODO, 0) = eps',
            'S_next = $drive_steps(S, 1)', '$call_descriptors_valid(S_next)',
            '$replay_guard(S_next.TODO) = (REF_REPLAY_ORIGIN porigin_source z (prefowner :: prefowner_tail*))',
            'S_next.STORE = S.STORE', 'S_next.ALLOCATIONS = S.ALLOCATIONS'], [
            'S[.TODO = $replay_replace(S.TODO, REF_REPLAY_PHASE porigin_source z (prefowner :: prefowner_tail*), eps)]',
            'S[.TODO = $replay_replace(S.TODO, REF_REPLAY_ORIGIN porigin_source z (prefowner :: prefowner_tail*), [REF_REPLAY_ORIGIN porigin_source $(z + 100) (prefowner :: prefowner_tail*)])]'])
    fixture('saved-pending-replay-after-goto', case, ['$replay_function(S, [103])',
            'S.FRAMES = pframe :: pframe_tail*', '$replay_outputs(S.EVENTS) = ' + str(list(b'K;G;C;L;'))], [
            'S.FRAMES = pframe :: pframe_tail*', 'S_scope = $constant_frame_scope(S, pframe, pframe_tail*)',
            '$replay_function(S_scope, [102])', '$switch_state_tasks(pframe.TODO, 0) = eps',
            '$replay_guard(pframe.TODO) = (REF_REPLAY_ORIGIN porigin_source z (prefowner :: prefowner_tail*))',
            'porigin_owner = $ref_owner_origin(prefowner)', '~$finally_present(S_scope, porigin_owner)',
            '$ref_replay_caught(S_scope, porigin_owner)', '$ref_replay_guard_valid(S_scope, porigin_source, z, prefowner :: prefowner_tail*)',
            '$call_tasks_valid(S_scope, pframe.TODO)'], [
            'S[.FRAMES = pframe[.TODO = $replay_replace(pframe.TODO, REF_REPLAY_PHASE porigin_source z (prefowner :: prefowner_tail*), eps)] :: pframe_tail*]',
            'S[.FRAMES = pframe[.TODO = $replay_replace(pframe.TODO, REF_REPLAY_ORIGIN porigin_source z (prefowner :: prefowner_tail*), [REF_REPLAY_ORIGIN porigin_source $(z + 100) (prefowner :: prefowner_tail*)])] :: pframe_tail*]'], error_scope='S_scope')

    (args.output / 'manifest.json').write_text(json.dumps({
        'source_reports': [str(path.resolve())], 'fixtures': len(records),
        'assertions': sum(row['assertions'] for row in records), 'records': records,
    }, indent=2) + '\n')
    print(json.dumps({'fixtures': len(records), 'assertions': sum(row['assertions'] for row in records)}))


if __name__ == '__main__':
    main()
