#!/usr/bin/env python3
"""Emit source-reached replay assertions from independently recorded model packets.

This producer starts no compiler, PHP or model. Run its output with the pinned
numeric runner in explicit --sl mode and the ordered current modules.json.
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

PREFIX = r'''dec $replay_stage(pstate) : bool
dec $replay_function(pstate, preqbytes) : bool
def $replay_function(S, n_name*) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $function_at($all_functions(S), pcallcontext.FUNCTION) = (pfunction)
  -- if pfunction.NAME = n_name*
def $replay_function(S, n_name*) = false -- otherwise
dec $replay_guard(ptask*) : ptask?
def $replay_guard((REF_REPLAY_ORIGIN porigin_source z prefowner*) :: ptask_tail*) = (REF_REPLAY_ORIGIN porigin_source z prefowner*)
def $replay_guard(ptask_head :: ptask_tail*) = $replay_guard(ptask_tail*)
  -- if $ref_replay_guard_owner(ptask_head) = eps
def $replay_guard(eps) = eps
dec $replay_error_head(ptask) : bool
def $replay_error_head(FINALLY_RESUME porigin (n)) = true
def $replay_error_head(ptask) = false -- otherwise
dec $replay_error(ptask*) : nat?
def $replay_error((FINALLY_RESUME porigin (n)) :: ptask_tail*) = (n)
def $replay_error(ptask_head :: ptask_tail*) = $replay_error(ptask_tail*)
  -- if ~$replay_error_head(ptask_head)
def $replay_error(eps) = eps
dec $replay_replace(ptask*, ptask, ptask*) : ptask*
def $replay_replace(eps, ptask_old, ptask_new*) = eps
def $replay_replace(ptask_old :: ptask_tail*, ptask_old, ptask_new*) = ptask_new* ++ ptask_tail*
def $replay_replace(ptask_head :: ptask_tail*, ptask_old, ptask_new*) = ptask_head :: $replay_replace(ptask_tail*, ptask_old, ptask_new*)
  -- if ptask_head =/= ptask_old
dec $replay_find(pstate, nat) : pstate
def $replay_find(S, n) = S[.COMPLETION = NORMAL]
  -- if $replay_stage(S)
  -- if S.COMPLETION = BUDGET
def $replay_find(S, n) = $replay_find($drive_steps(S[.COMPLETION = NORMAL], 1), n_next)
  -- if ~$replay_stage(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
  -- if n_next = $(n - 1)
dec $replay_resume(pstate, nat) : pstate
def $replay_resume(S, n) = $drive(S[.COMPLETION = NORMAL], n) -- if S.COMPLETION = BUDGET
def $replay_resume(S, n) = S -- otherwise
dec $replay_output(pevent) : nat*
def $replay_output(OUTPUT n*) = n*
def $replay_output(pevent) = eps -- otherwise
dec $replay_outputs(pevent*) : nat*
def $replay_outputs(eps) = eps
def $replay_outputs(pevent_head :: pevent_tail*) = $replay_output(pevent_head) ++ $replay_outputs(pevent_tail*)
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    cases = {row['id']: row for row in json.loads(
        (ROOT / 'tests/semantics/reference_replay_cases.json').read_text())['cases']}
    report = json.loads((args.raw / 'report.json').read_text())
    assert report['passed'] and report['source_agreements'] == len(cases)
    rows = {row['id']: row for row in report['records']}
    assert rows.keys() == cases.keys()
    args.output.mkdir(parents=True, exist_ok=True)
    records = []

    def initial(case):
        row = rows[case]
        assert row['pass']
        source = cases[case]['source'].encode()
        assert hashlib.sha256(source).hexdigest() == row['source_sha256']
        native = row['native']
        assert native['exit_status'] == 0 and base64.b64decode(native['stderr']) == b''
        stdout = base64.b64decode(native['stdout'])
        assert stdout == cases[case]['predicted_stdout'].encode()
        directory = args.raw / case
        checked = json.loads((directory / 'checked.json').read_text())
        parsed = json.loads((directory / 'parsed.json').read_text())
        assert parsed['accepted'] and checked['ok'] and checked['fixture']
        facts = json.loads((directory / 'request.json').read_text())
        return ('$php_request_run(' + checked['fixture'] + ', 0, ' +
                json.dumps(facts['file']) + ', ' + request_fixture(facts) + ')', str(list(stdout)))

    def fixture(name, case, stage, checks, bad=()):
        start, stdout = initial(case)
        stage_text = ('def $replay_stage(S) = true\n' +
                      ''.join('  -- if ' + condition + '\n' for condition in stage) +
                      'def $replay_stage(S) = false -- otherwise\n')
        common = ['S_initial = ' + start, 'S_initial.COMPLETION = BUDGET',
                  'S_start = S_initial[.COMPLETION = NORMAL]',
                  'S = $replay_find(S_start, 2000)', 'S.COMPLETION = NORMAL',
                  '$replay_stage(S)', '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
        rejected = []
        for index, mutation in enumerate(bad):
            rejected += [f'S_bad{index} = ' + mutation,
                         f'~$call_descriptors_valid(S_bad{index})',
                         f'S_rejected{index} = $drive(S_bad{index}, 0)',
                         f'S_rejected{index}.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"',
                         f'$drive(S_bad{index}, 10000) = S_rejected{index}']
        complete = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
                    'S_one = $replay_resume(S_zero, 1)',
                    'S_adjacent = $replay_resume(S_one, 10000)',
                    'S_frontier = $drive(S, 10001)',
                    'S_whole = $drive(S_start, 10001)',
                    'S_adjacent = S_frontier', 'S_frontier = S_whole',
                    'S_whole.COMPLETION = NORMAL', '$replay_outputs(S_whole.EVENTS) = ' + stdout,
                    'S_whole.CURRENT = eps', 'S_whole.FRAMES = eps', 'S_whole.TODO = eps',
                    'S_whole.HELD = eps', 'S_whole.ITERATORS = eps',
                    '$heap_valid($heap_graph(S_whole))', '$call_descriptors_valid(S_whole)']
        assertions = common + checks + rejected + complete
        path = args.output / (name + '.watsup')
        path.write_text(PREFIX + '\n' + stage_text + '\ndec $main() : bool\ndef $main() = true\n' +
                        ''.join('  -- if ' + condition + '\n' for condition in assertions))
        records.append({'id': name, 'source_id': case, 'fixture': str(path.resolve()),
                        'assertions': len(assertions)})

    def pair(owners, saved=False, retired=False):
        guard = f'REF_REPLAY_ORIGIN porigin_source z ({owners})'
        phase = f'REF_REPLAY_PHASE porigin_source z ({owners})'
        after = f'REF_REPLAY_AFTER porigin_source z ({owners})'
        todo = 'pframe.TODO' if saved else 'S.TODO'
        def state(tasks):
            return (f'S[.FRAMES = pframe[.TODO = {tasks}] :: pframe_tail*]' if saved
                    else f'S[.TODO = {tasks}]')
        checks = ['ptask_guard = ' + guard, 'ptask_phase = ' + phase,
                  '$task_nodes(ptask_guard) = eps', '$task_nodes(ptask_phase) = eps']
        mutations = [('ptask_guard', 'eps'), ('ptask_guard', '[ptask_guard, ptask_guard]'),
                     ('ptask_guard', '[ORIGIN_RETURN $ref_replay_outer(' + owners + ')]'),
                     ('ptask_guard', '[REF_REPLAY_ORIGIN porigin_source $(z + 100) (' + owners + ')]'),
                     ('ptask_guard', '[REF_REPLAY_ORIGIN porigin_owner z (' + owners + ')]'),
                     ('ptask_phase', 'eps'), ('ptask_phase', '[ptask_phase, ptask_phase]'),
                     ('ptask_phase', '[REF_REPLAY_PHASE porigin_source $(z + 100) (' + owners + ')]')]
        if retired:
            checks += ['ptask_after = ' + after, '$task_nodes(ptask_after) = eps']
            mutations += [('ptask_after', 'eps'), ('ptask_after', '[ptask_after, ptask_after]')]
        bad = [state(f'$replay_replace({todo}, {old}, {new})') for old, new in mutations]
        bad.append(state('$replay_replace($replay_replace(' + todo +
                         ', ptask_phase, eps), ptask_guard, [ptask_phase, ptask_guard])'))
        return checks, bad

    g = ['$replay_function(S, [103])']
    backing = 'parameter-backing-finally-required-recheck-unused'
    terminal = 'S.TODO = [RETURN_REF_UNWIND (REFERENCE n_cell) z true porigin_source, REF_RECHECK porigin_source porigin_first (REFERENCE n_cell) z]'
    fixture('terminal-backing-recheck', backing, g + [terminal], [terminal,
        '$ref_recheck_valid(S, porigin_source, porigin_first, REFERENCE n_cell, z)',
        '$ref_replay_owners(S, porigin_source) = porigin_first :: porigin_tail*',
        'S.GLOBALTABLE = (psymboltable)', '$lookup(psymboltable.ENV, [118]) = (n_cell)',
        'S.STORE[n_cell] = DEFINED (POBJECT n_value)',
        '$propref_at(S.PROPREFS, n_cell) = (ppropref)',
        '(HCELL n_cell) <- $heap_graph(S).ROOTS',
        'S_next = $drive_steps(S, 1)',
        'S_next.TODO = [THROW_SEARCH n, REF_REPLAY porigin_source (REFERENCE n_cell) z prefowner*]',
        'S_next.STORE[n_cell] = S.STORE[n_cell]', 'S_next.PROPREFS = S.PROPREFS',
        'S_next.PARAMETERBACKINGS = S.PARAMETERBACKINGS', 'S_next.REFCOERCIONS = S.REFCOERCIONS',
        '$call_descriptors_valid(S_next)', '$heap_valid($heap_graph(S_next))'], [
        'S[.TODO = [RETURN_REF_UNWIND (REFERENCE n_cell) z true porigin_source]]',
        'S[.TODO = [RETURN_REF_UNWIND (REFERENCE n_cell) z true porigin_source, REF_RECHECK porigin_source porigin_first (REFERENCE n_cell) $(z + 100)]]',
        'S[.TODO = [RETURN_REF_UNWIND (REFERENCE n_cell) z true porigin_source, REF_RECHECK porigin_source porigin_first (REFERENCE $(n_cell + 1)) z]]',
        'S[.TODO = [RETURN_REF_UNWIND (REFERENCE n_cell) z true porigin_source, REF_RECHECK porigin_source porigin_first (REFERENCE n_cell) z, REF_RECHECK porigin_source porigin_first (REFERENCE n_cell) z]]',
        'S[.TODO = [REF_RECHECK porigin_source porigin_first (REFERENCE n_cell) z]]'])

    minted = 'S.TODO = [THROW_SEARCH n, REF_REPLAY porigin_source poperand z prefowner*]'
    fixture('minted-one-use-witness', backing, g + [minted], [minted,
        '$ref_replay_valid(S, porigin_source, poperand, z, prefowner*)',
        'S.OBJECTS[n] = THROWABLE pthrowable', 'pthrowable.KIND = "TypeError"',
        'prefowner* = (REPLAY_TRY porigin_owner) :: eps',
        'poperand = REFERENCE n_cell',
        '$task_nodes(REF_REPLAY porigin_source poperand z prefowner*) = [HCELL n_cell]',
        'S_next = $drive_steps(S, 1)',
        'S_next.TODO = (THROW_SEARCH n) :: $ref_replay_tasks(porigin_source, z, prefowner*)',
        'S_next.STORE = S.STORE', 'S_next.PROPREFS = S.PROPREFS',
        '$call_descriptors_valid(S_next)', '$heap_valid($heap_graph(S_next))'], [
        'S[.TODO = [THROW_SEARCH n, REF_REPLAY porigin_source poperand $(z + 100) prefowner*]]',
        'S[.TODO = [THROW_SEARCH n, REF_REPLAY porigin_source poperand z eps]]',
        'S[.TODO = [THROW_SEARCH n, REF_REPLAY porigin_source poperand z ((REPLAY_TRY porigin_owner) :: (REPLAY_TRY porigin_owner) :: eps)]]',
        'S[.TODO = [THROW_SEARCH n, REF_REPLAY porigin_owner poperand z prefowner*]]'])
    nested = 'delayed-error-nested-finalizers-saved-call'
    owners = '(REPLAY_TRY porigin_inner) :: (REPLAY_TRY porigin_outer) :: eps'
    fixture('nested-owner-order', nested,
            g + ['S.TODO = [THROW_SEARCH n, REF_REPLAY porigin_source poperand z (' + owners + ')]'], [
        'S.TODO = [THROW_SEARCH n, REF_REPLAY porigin_source poperand z (' + owners + ')]',
        'porigin_inner =/= porigin_outer',
        '$ref_replay_contexts(S, porigin_source) = ' + owners,
        'S_next = $drive_steps(S, 1)',
        'S_next.ORIGIN = (porigin_inner)',
        '$call_descriptors_valid(S_next)', '$heap_valid($heap_graph(S_next))'], [
        'S[.TODO = [THROW_SEARCH n, REF_REPLAY porigin_source poperand z ((REPLAY_TRY porigin_outer) :: (REPLAY_TRY porigin_inner) :: eps)]]'])

    try_owner = '(REPLAY_TRY porigin_owner) :: eps'
    catch_owner = '(REPLAY_CATCH porigin_owner) :: eps'
    for name, case, kind, owners in (
        ('expanded-try', backing, 'TRY_END', try_owner),
        ('expanded-selected-catch', 'delayed-error-selected-catch-no-siblings', 'FINALLY_ONLY', catch_owner),
    ):
        tasks = f'[THROW_SEARCH n, {kind} porigin_owner, REF_REPLAY_ORIGIN porigin_source z ({owners}), REF_REPLAY_PHASE porigin_source z ({owners})]'
        checks, bad = pair(owners)
        other = 'FINALLY_ONLY' if kind == 'TRY_END' else 'TRY_END'
        fixture(name, case, g + ['S.TODO = ' + tasks], ['S.TODO = ' + tasks,
            'S.ORIGIN = (porigin_owner)', '$ref_replay_guard_valid(S, porigin_source, z, ' + owners + ')'] + checks,
            bad + [f'S[.TODO = [THROW_SEARCH n, {other} porigin_owner, REF_REPLAY_ORIGIN porigin_source z ({owners}), REF_REPLAY_PHASE porigin_source z ({owners})]]'])

    local = 'delayed-error-local-catch-after-continuation'
    for name, head, caught in (
        ('selected-local-catch', 'CATCH_BIND porigin_owner n_index n', 'S.ORIGIN = (porigin_owner)'),
        ('completed-local-catch', 'FINALLY_ONLY porigin_owner', 'S.ORIGIN =/= (porigin_owner)'),
    ):
        tasks = f'[{head}, FINALLY_ONLY porigin_owner, REF_REPLAY_ORIGIN porigin_source z ({try_owner}), REF_REPLAY_PHASE porigin_source z ({try_owner})]' if name == 'selected-local-catch' else f'[{head}, REF_REPLAY_ORIGIN porigin_source z ({try_owner}), REF_REPLAY_PHASE porigin_source z ({try_owner})]'
        checks, bad = pair(try_owner)
        fixture(name, local, g + ['S.TODO = ' + tasks], ['S.TODO = ' + tasks,
            '$ref_replay_caught(S, porigin_owner)', caught] + checks, bad)

    tasks = f'[FINALLY_RESUME porigin_owner (n_old), FINALLY_PHASE porigin_owner 1, REF_REPLAY_ORIGIN porigin_source z ({try_owner}), REF_REPLAY_PHASE porigin_source z ({try_owner})]'
    checks, bad = pair(try_owner)
    fixture('pending-error-after-second-repair', 'delayed-error-replay-repairs-cell',
            g + ['S.TODO = ' + tasks], ['S.TODO = ' + tasks,
        'S.GLOBALTABLE = (psymboltable)', '$lookup(psymboltable.ENV, [118]) = (n_v)',
        'S.STORE[n_v] = DEFINED (PSTRING $ptascii("fixed"))',
        '$throwable_live(S, n_old)', 'S_next = $drive_steps(S, 1)',
        'S_next.TODO = (THROW_SEARCH n_old) :: ptask_tail*'] + checks, bad + [
        'S[.TODO = $replay_replace(S.TODO, FINALLY_PHASE porigin_owner 1, [FINALLY_PHASE porigin_owner 0])]'])

    saved_owners = '(REPLAY_TRY porigin_owner) :: prefowner_tail*'
    saved_guard = f'REF_REPLAY_ORIGIN porigin_source z ({saved_owners})'
    checks, bad = pair(saved_owners, saved=True)
    fixture('saved-replay-finalizer', nested, [
        '$replay_function(S, [112,105,110,103])', 'S.FRAMES = pframe :: pframe_tail*',
        '$replay_guard(pframe.TODO) = (' + saved_guard + ')'], [
        'S.FRAMES = pframe :: pframe_tail*', '$replay_guard(pframe.TODO) = (' + saved_guard + ')',
        'S_scope = $constant_frame_scope(S, pframe, pframe_tail*)',
        '$replay_function(S_scope, [103])', '$call_tasks_valid(S_scope, pframe.TODO)',
        '$ref_replay_contexts(S_scope, porigin_source) = ' + saved_owners,
        '$ref_replay_guard_count(pframe.TODO, porigin_owner) = 1'] + checks, bad + [
        'S[.FRAMES = pframe[.ORIGIN = eps] :: pframe_tail*]',
        'S[.FRAMES = pframe[.TODO = $replay_replace(pframe.TODO, FINALLY_PHASE porigin_owner 1, eps)] :: pframe_tail*]'])

    saved_guard = f'REF_REPLAY_ORIGIN porigin_source z ({try_owner})'
    checks, bad = pair(try_owner, saved=True)
    fixture('saved-selected-local-catch', 'delayed-error-local-catch-saved-call', [
        '$replay_function(S, [112,105,110,103])', 'S.FRAMES = pframe :: pframe_tail*',
        '$replay_guard(pframe.TODO) = (' + saved_guard + ')'], [
        'S.FRAMES = pframe :: pframe_tail*', '$replay_guard(pframe.TODO) = (' + saved_guard + ')',
        'S_scope = $constant_frame_scope(S, pframe, pframe_tail*)',
        '$replay_function(S_scope, [103])', '$call_tasks_valid(S_scope, pframe.TODO)',
        '$ref_replay_contexts(S_scope, porigin_source) = ' + try_owner,
        '$replay_replace(pframe.TODO, FINALLY_ONLY porigin_owner, eps) =/= pframe.TODO',
        'S.GLOBALTABLE = (psymboltable)', '$lookup(psymboltable.ENV, [118]) = (n_v)',
        'S.STORE[n_v] = DEFINED (POBJECT n_value)'] + checks, bad + [
        'S[.FRAMES = pframe[.ORIGIN = eps] :: pframe_tail*]',
        'S[.FRAMES = pframe[.TODO = $replay_replace(pframe.TODO, FINALLY_ONLY porigin_owner, [TRY_END porigin_owner])] :: pframe_tail*]'])

    tasks = f'[REF_REPLAY_AFTER porigin_source z ({try_owner}), REF_REPLAY_ORIGIN porigin_source z ({try_owner}), REF_REPLAY_PHASE porigin_source z ({try_owner})]'
    checks, bad = pair(try_owner, retired=True)
    fixture('source-after-caught-try', local, g + ['S.TODO = ' + tasks], [
        'S.TODO = ' + tasks, 'S.ORIGIN = $ref_replay_outer(' + try_owner + ')',
        '$ref_replay_after_tasks(S, porigin_owner) = GOTOTASKS ptask_source*',
        'ptask_source* =/= eps', 'S_next = $drive_steps(S, 1)',
        'S_next.TODO = ptask_source*', 'S_next.STORE = S.STORE',
        '$call_descriptors_valid(S_next)', '$heap_valid($heap_graph(S_next))'] + checks, bad)

    for name, case, head in (
        ('new-return-overrides-pending-error', 'delayed-error-replay-return-override', 'RETURN_REF_UNWIND (REFERENCE n_cell) z true porigin_source'),
        ('new-throw-overrides-pending-error', 'delayed-error-replay-throw-override', 'THROW_SEARCH n'),
    ):
        tasks = f'[{head}, REF_REPLAY_AFTER porigin_source_old z_old ({try_owner}), REF_REPLAY_ORIGIN porigin_source_old z_old ({try_owner}), REF_REPLAY_PHASE porigin_source_old z_old ({try_owner})]'
        lifetime = (['$throwable_previous_id(S, n) = (n_old)',
                     '$throwable_live(S, n_old)',
                     'S.OBJECTS[n_old] = THROWABLE pthrowable_old',
                     'pthrowable_old.KIND = "TypeError"'] if name.startswith('new-throw') else [
                     'S.GLOBALTABLE = (psymboltable)',
                     '$lookup(psymboltable.ENV, $ptascii("replacement")) = (n_cell)',
                     '$lookup(psymboltable.ENV, [118]) = (n_v)', 'n_cell =/= n_v'])
        fixture(name, case, g + ['S.TODO = ' + tasks], ['S.TODO = ' + tasks] + lifetime + [
            'S_next = $drive_steps(S, 1)', 'S_next.TODO = [' + head + ']',
            '$call_descriptors_valid(S_next)', '$heap_valid($heap_graph(S_next))'])

    fixture('return-override-error-lifetime', 'delayed-error-replay-return-override', g + [
        'S.TODO = (RETURN_REF_FETCH z) :: ptask_tail*', '$replay_error(S.TODO) = (n_old)'], [
        'S.TODO = (RETURN_REF_FETCH z) :: ptask_tail*', '$replay_error(S.TODO) = (n_old)',
        '$throwable_live(S, n_old)', 'S.OBJECTS[n_old] = THROWABLE pthrowable_old',
        'pthrowable_old.KIND = "TypeError"',
        'S.GLOBALTABLE = (psymboltable)',
        '$lookup(psymboltable.ENV, $ptascii("replacement")) = (n_cell)',
        '$lookup(psymboltable.ENV, [118]) = (n_v)', 'n_cell =/= n_v',
        'S.STORE[n_cell] = DEFINED (PSTRING $ptascii("override"))',
        'S_next = $drive_steps(S, 1)',
        'S_next.TODO = (RETURN_REF_UNWIND (REFERENCE n_cell) z false porigin_source) :: ptask_after*',
        'S_done = $drive(S, 10001)', 'S_done.COMPLETION = NORMAL',
        '~$throwable_live(S_done, n_old)',
        'S_done.STORE[n_cell] = DEFINED (PSTRING $ptascii("changed"))'])

    (args.output / 'manifest.json').write_text(json.dumps({
        'source_report': str((args.raw / 'report.json').resolve()),
        'fixtures': len(records), 'assertions': sum(row['assertions'] for row in records),
        'records': records,
    }, indent=2) + '\n')
    print(json.dumps({'fixtures': len(records), 'assertions': sum(row['assertions'] for row in records)}))


if __name__ == '__main__':
    main()
