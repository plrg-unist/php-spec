#!/usr/bin/env python3
"""Genuine interpolation callback stages, captured owners and borrowed CV controls."""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import subprocess
import tempfile

from error_handler_run import recorded
from recorded_worker import Worker

R = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).with_name('interpolation')
b64 = lambda value: base64.b64encode(value).decode()

HELPERS = r'''
dec $interpolation_control_left(pinterpolation) : bool
def $interpolation_control_left(pinterpolation) = ((pinterpolation.MODE = 2 /\ pinterpolation.INDEX = 0) \/ (pinterpolation.MODE = 3 /\ pinterpolation.INDEX = 1))
dec $interpolation_control_ready(pstate, nat, nat) : bool
def $interpolation_control_ready(S, n_mode, 0) = true
  -- if S.TODO = (CALL_ARGS (METHOD_TARGET n porigin_method) eps 0 eps (porigin_child) z) :: (STRINGIFY_RESULT n porigin_child z) :: (INTERPOLATE_AFTER pinterpolation) :: (INTERPOLATE_FINISH porigin_finish) :: ptask_tail*
  -- if porigin_finish = pinterpolation.SITE
  -- if pinterpolation.MODE = n_mode
  -- if $interpolation_control_left(pinterpolation)
def $interpolation_control_ready(S, n_mode, 1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (STRINGIFY_RESULT n porigin_child z) :: (INTERPOLATE_AFTER pinterpolation) :: (INTERPOLATE_FINISH porigin_finish) :: ptask_tail*
  -- if porigin_finish = pinterpolation.SITE
  -- if pinterpolation.MODE = n_mode
  -- if $interpolation_control_left(pinterpolation)
def $interpolation_control_ready(S, n_mode, 2) = true
  -- if S.CURRENT = eps
  -- if S.RESULT = KNOWN (PSTRING $ptascii("first"))
  -- if S.TODO = (STRINGIFY_RESULT n porigin_child z) :: (INTERPOLATE_AFTER pinterpolation) :: (INTERPOLATE_FINISH porigin_finish) :: ptask_tail*
  -- if porigin_finish = pinterpolation.SITE
  -- if pinterpolation.MODE = n_mode
  -- if $interpolation_control_left(pinterpolation)
def $interpolation_control_ready(S, 0, 3) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = INTERPOLATE_ARRAY_RESULT pinterpolation (VARIABLE n_name* z)
def $interpolation_control_ready(S, 0, 4) = true
  -- if S.TODO = (INTERPOLATE_ARRAY_RESULT pinterpolation (VARIABLE n_name* z)) :: ptask_tail*
def $interpolation_control_ready(S, 0, 5) = true
  -- if S.TODO = (INTERPOLATE_COLLECT porigin 0 eps) :: ptask_tail*
def $interpolation_control_ready(S, 0, 6) = true
  -- if S.TODO = (INTERPOLATE_RESOLVE pinterpolation n_name*) :: ptask_tail*
def $interpolation_control_ready(S, n_mode, n_stage) = false -- otherwise

dec $interpolation_control_seek(pstate, nat, nat, nat) : pstate
def $interpolation_control_seek(S, n_mode, n_stage, n) = S -- if $interpolation_control_ready(S, n_mode, n_stage)
def $interpolation_control_seek(S, n_mode, n_stage, n) = S
  -- if ~$interpolation_control_ready(S, n_mode, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $interpolation_control_seek(S, n_mode, n_stage, 0) = S
  -- if ~$interpolation_control_ready(S, n_mode, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $interpolation_control_seek(S, n_mode, n_stage, n) = $interpolation_control_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_mode, n_stage, $nabs($(n - 1)))
  -- if ~$interpolation_control_ready(S, n_mode, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
'''

CHECKS = [
    'pstartup = {REPORTING ($ptascii("30719")), INCLUDEPATH $ptascii(".:")}',
    'S_initial = $php_startup_run($interpolation_owner_program(), 0, "@OWNER@", pstartup)',
    '$call_descriptors_valid(S_initial)',
    'S_pending = $interpolation_control_seek(S_initial, 2, 0, 1000)',
    '$interpolation_control_ready(S_pending, 2, 0)',
    '$call_descriptors_valid(S_pending)',
    '$heap_valid($heap_graph(S_pending))',
    'S_pending.TODO = (CALL_ARGS (METHOD_TARGET n_left porigin_method) eps 0 eps (porigin_child) z) :: (STRINGIFY_RESULT n_left porigin_child z) :: (INTERPOLATE_AFTER pinterpolation_fast) :: (INTERPOLATE_FINISH porigin_finish_fast) :: ptask_tail*',
    'porigin_finish_fast = pinterpolation_fast.SITE',
    'pinterpolation_fast.VALUES = [KNOWN (POBJECT n_old)]',
    '$stringify_pending(S_pending, METHOD_TARGET n_left porigin_method, porigin_child)',
    '(HOBJECT n_left) <- $heap_graph(S_pending).ROOTS',
    '(HOBJECT n_old) <- $heap_graph(S_pending).ROOTS',
    '~$heap_valid($heap_graph(S_pending[.ALLOCATIONS = $call_remove_owner(S_pending.ALLOCATIONS, HOBJECT n_old)]))',
    '~$call_descriptors_valid(S_pending[.ORIGIN = (pinterpolation_fast.SITE)])',
    '~$call_descriptors_valid(S_pending[.TODO = (CALL_ARGS (METHOD_TARGET n_left porigin_method) eps 0 eps (porigin_child) $(z + 1)) :: (STRINGIFY_RESULT n_left porigin_child $(z + 1)) :: (INTERPOLATE_AFTER pinterpolation_fast) :: (INTERPOLATE_FINISH pinterpolation_fast.SITE) :: ptask_tail*])',
    '~$call_descriptors_valid(S_pending[.TODO = (CALL_ARGS (METHOD_TARGET n_left porigin_method) eps 0 eps (porigin_child) z) :: (STRINGIFY_RESULT n_left porigin_child z) :: (INTERPOLATE_AFTER pinterpolation_fast[.MODE = 3]) :: (INTERPOLATE_FINISH pinterpolation_fast.SITE) :: ptask_tail*])',
    '~$call_descriptors_valid(S_pending[.TODO = (CALL_ARGS (METHOD_TARGET n_left porigin_method) eps 0 eps (porigin_child) z) :: (STRINGIFY_RESULT n_left porigin_child z) :: (INTERPOLATE_AFTER pinterpolation_fast[.INDEX = 1]) :: (INTERPOLATE_FINISH pinterpolation_fast.SITE) :: ptask_tail*])',
    '~$call_descriptors_valid(S_pending[.TODO = (CALL_ARGS (METHOD_TARGET n_left porigin_method) eps 0 eps (porigin_child) z) :: (STRINGIFY_RESULT n_left porigin_child z) :: (INTERPOLATE_AFTER pinterpolation_fast[.VALUES = eps]) :: (INTERPOLATE_FINISH pinterpolation_fast.SITE) :: ptask_tail*])',
    '~$call_descriptors_valid(S_pending[.TODO = (CALL_ARGS (METHOD_TARGET n_left porigin_method) eps 0 eps (porigin_child) z) :: (STRINGIFY_RESULT n_left porigin_child z) :: (INTERPOLATE_AFTER pinterpolation_fast) :: (INTERPOLATE_FINISH porigin_child) :: ptask_tail*])',
    'S_entered = $interpolation_control_seek(S_initial, 2, 1, 1000)',
    '$interpolation_control_ready(S_entered, 2, 1)',
    '$call_descriptors_valid(S_entered)',
    '$heap_valid($heap_graph(S_entered))',
    'S_entered.CURRENT = (pcallcontext)',
    'S_entered.FRAMES = pframe :: pframe_tail*',
    '$stringify_context_frame_valid(S_entered, pcallcontext, pframe)',
    '~$call_descriptors_valid(S_entered[.CURRENT = (pcallcontext[.LINE = $(pcallcontext.LINE + 1)])])',
    '~$call_descriptors_valid(S_entered[.CURRENT = (pcallcontext[.RECEIVER = ($(n_left + 1))])])',
    '~$call_descriptors_valid(S_entered[.FRAMES = pframe[.TODO = (STRINGIFY_RESULT n_left porigin_child z) :: (INTERPOLATE_AFTER pinterpolation_fast) :: ptask_tail*] :: pframe_tail*])',
    'S_result = $interpolation_control_seek(S_initial, 2, 2, 1000)',
    '$interpolation_control_ready(S_result, 2, 2)',
    '$call_descriptors_valid(S_result)',
    '$heap_valid($heap_graph(S_result))',
    'S_result.TODO = (STRINGIFY_RESULT n_left porigin_child z) :: (INTERPOLATE_AFTER pinterpolation_fast) :: (INTERPOLATE_FINISH pinterpolation_fast.SITE) :: ptask_tail*',
    '$lookup(S_result.ENV, $ptascii("earlier")) = (n_earlier)',
    'S_result.STORE[n_earlier] = DEFINED (PINT 17)',
    '(HOBJECT n_left) <- S_result.ALLOCATIONS',
    '(HOBJECT n_old) <- $heap_graph(S_result).ROOTS',
    '$drive_steps(S_result[.COMPLETION = NORMAL], 0) = S_result[.COMPLETION = BUDGET]',
    'S_after = $drive_steps(S_result[.COMPLETION = NORMAL], 1)',
    'S_after.TODO = (INTERPOLATE_AFTER pinterpolation_fast) :: (INTERPOLATE_FINISH pinterpolation_fast.SITE) :: ptask_tail*',
    '$call_descriptors_valid(S_after)',
    '$heap_valid($heap_graph(S_after))',
    '~((HOBJECT n_left) <- S_after.ALLOCATIONS)',
    '(HOBJECT n_old) <- $heap_graph(S_after).ROOTS',
    '~$call_descriptors_valid(S_after[.TODO = (INTERPOLATE_AFTER pinterpolation_fast) :: ptask_tail*])',
    '~$call_descriptors_valid(S_after[.TODO = (INTERPOLATE_AFTER pinterpolation_fast[.TEXT = ([256])]) :: (INTERPOLATE_FINISH pinterpolation_fast.SITE) :: ptask_tail*])',
    '~$call_descriptors_valid(S_after[.TODO = (INTERPOLATE_AFTER pinterpolation_fast) :: (INTERPOLATE_FINISH porigin_child) :: (INTERPOLATE_AFTER pinterpolation_fast) :: (INTERPOLATE_FINISH pinterpolation_fast.SITE) :: ptask_tail*])',
    'S_rope = $interpolation_control_seek(S_initial, 3, 0, 2000)',
    '$interpolation_control_ready(S_rope, 3, 0)',
    '$call_descriptors_valid(S_rope)',
    '$heap_valid($heap_graph(S_rope))',
    'S_rope.TODO = (CALL_ARGS (METHOD_TARGET n_rope porigin_method_rope) eps 0 eps (porigin_rope) z_rope) :: (STRINGIFY_RESULT n_rope porigin_rope z_rope) :: (INTERPOLATE_AFTER pinterpolation_rope) :: (INTERPOLATE_FINISH porigin_finish_rope) :: ptask_rope_tail*',
    'porigin_finish_rope = pinterpolation_rope.SITE',
    'pinterpolation_rope.VALUES = eps',
    'S_rope_result = $interpolation_control_seek(S_initial, 3, 2, 2000)',
    '$interpolation_control_ready(S_rope_result, 3, 2)',
    '$call_descriptors_valid(S_rope_result)',
    '$heap_valid($heap_graph(S_rope_result))',
    'S_rope_after = $drive_steps(S_rope_result[.COMPLETION = NORMAL], 1)',
    '$call_descriptors_valid(S_rope_after)',
    '~((HOBJECT n_rope) <- S_rope_after.ALLOCATIONS)',
    'S_borrow_initial = $php_startup_run($interpolation_borrow_program(), 0, "@BORROW@", pstartup)',
    'S_borrow = $interpolation_control_seek(S_borrow_initial, 0, 3, 1000)',
    '$interpolation_control_ready(S_borrow, 0, 3)',
    '$call_descriptors_valid(S_borrow)',
    '$heap_valid($heap_graph(S_borrow))',
    'S_borrow.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_borrow_tail*',
    'perrorcall.RESUME = INTERPOLATE_ARRAY_RESULT pinterpolation_borrow (VARIABLE n_missing* z_missing)',
    '$task_nodes(perrorcall.RESUME) = eps',
    '$interpolation_reread(S_borrow, pinterpolation_borrow, n_missing*) = VARIABLE n_missing* z_missing',
    '$lookup(S_borrow.ENV, n_missing*) = (n_missing_cell)',
    'S_borrow.STORE[n_missing_cell] = DEFINED (PARRAY n_array)',
    '~((HARRAY n_array) <- $heap_graph(S_borrow).ROOTS)',
    'S_borrow.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_owner))]',
    '(HOBJECT n_owner) <- S_borrow.ALLOCATIONS',
    'S_borrow_result = $interpolation_control_seek(S_borrow_initial, 0, 4, 1500)',
    '$interpolation_control_ready(S_borrow_result, 0, 4)',
    '$call_descriptors_valid(S_borrow_result)',
    '$heap_valid($heap_graph(S_borrow_result))',
    '$task_nodes(INTERPOLATE_ARRAY_RESULT pinterpolation_borrow (VARIABLE n_missing* z_missing)) = eps',
    '~((HARRAY n_array) <- S_borrow_result.ALLOCATIONS)',
    '~((HOBJECT n_owner) <- S_borrow_result.ALLOCATIONS)',
    'S_borrow_done = $drive_steps(S_borrow_result[.COMPLETION = NORMAL], 1000)',
    'S_borrow_done.COMPLETION = NORMAL',
    '$call_descriptors_valid(S_borrow_done)',
    '$heap_valid($heap_graph(S_borrow_done))',
    'S_borrow_done.EVENTS = [OUTPUT $ptascii("U|"), OUTPUT $ptascii("A|"), OUTPUT $ptascii("PArray|"), OUTPUT $ptascii("free"), OUTPUT $ptascii("|END")]',
    'S_absent_initial = $php_startup_run($interpolation_absent_program(), 0, "@ABSENT@", pstartup)',
    'S_literal = $interpolation_control_seek(S_absent_initial, 0, 5, 1000)',
    '$interpolation_control_ready(S_literal, 0, 5)',
    'S_literal.TODO = (INTERPOLATE_COLLECT porigin_literal 0 eps) :: ptask_literal_tail*',
    '$call_descriptors_valid(S_literal)',
    '~$call_task_valid(S_literal, INTERPOLATE_CAPTURE porigin_literal 0 eps)',
    'S_literal_value = $drive_steps(S_literal[.COMPLETION = NORMAL], 1)',
    'S_literal_value.TODO = (INTERPOLATE_COLLECT porigin_literal 1 ([KNOWN (PSTRING $ptascii("P"))])) :: ptask_literal_tail*',
    '$call_descriptors_valid(S_literal_value)',
    '~$call_task_valid(S_literal_value, INTERPOLATE_COLLECT porigin_literal 1 ([KNOWN (PSTRING $ptascii("Q"))]))',
    'S_resolve = $interpolation_control_seek(S_absent_initial, 0, 6, 1000)',
    '$interpolation_control_ready(S_resolve, 0, 6)',
    '$call_descriptors_valid(S_resolve)',
    'S_resolve.TODO = (INTERPOLATE_RESOLVE pinterpolation_absent n_absent*) :: ptask_absent_tail*',
    '$interpolation_reread(S_resolve, pinterpolation_absent, n_absent*) = KNOWN PNULL',
    '~$call_task_valid(S_resolve, INTERPOLATE_RESOLVE pinterpolation_absent[.VALUES = [KNOWN PNULL]] n_absent*)',
    '~$call_task_valid(S_resolve[.ORIGIN = ($interpolation_child(pinterpolation_absent.SITE, pinterpolation_absent.INDEX))], INTERPOLATE_RESOLVE pinterpolation_absent n_absent*)',
    'S_absent_done = $drive_steps(S_resolve[.COMPLETION = NORMAL], 1000)',
    'S_absent_done.COMPLETION = NORMAL',
    'S_absent_done.EVENTS = [OUTPUT $ptascii("P")]',
    '$call_descriptors_valid(S_absent_done)',
    '$heap_valid($heap_graph(S_absent_done))',
]

# Original111 unique premises;25 setup/binding premises repeat across groups.
GROUPS = {'pending': list(range(0, 20)), 'entered': list(range(0, 10)) + list(range(20, 30)),
          'result': list(range(0, 10)) + list(range(30, 49)), 'rope': [0, 1, 2] + list(range(49, 63)),
          'borrow': [0] + list(range(63, 89)), 'absent': [0] + list(range(89, 111))}


def render(fixtures, sources, group):
    setup = ''.join('dec $interpolation_' + name + '_program() : program\n'
                    + 'def $interpolation_' + name + '_program() = ' + fixture + '\n'
                    for name, fixture in fixtures.items())
    checks = list(CHECKS)
    for name, path in sources.items():
        checks = [check.replace('@' + name.upper() + '@', b64(bytes(path))) for check in checks]
    selected = [checks[index] for index in GROUPS[group]]
    return (setup + HELPERS + '\ndec $main() : bool\ndef $main() = true\n'
            + ''.join('  -- if ' + check + '\n' for check in selected)
            + 'def $main() = false -- otherwise\n', len(selected))


def prepare(out):
    sources = {'owner': SOURCES / 'owner-cardinality.php', 'borrow': SOURCES / 'undefined-array-owner.php',
               'absent': SOURCES / 'absent.php'}
    profile = json.loads((R / 'tests/semantics/profile.json').read_text())
    flags = [arg for key, value in profile.items() for arg in ('-d', key + '=' + value)]
    frontend = Worker([str(R / '.tools/php/bin/php'), '-n', *flags, '-d',
                       'extension=' + str(R / '.tools/php-file.so'), str(R / 'frontend/worker.php')], out / 'frontend')
    try:
        parsed = {name: frontend.request({'op': 'parse', 'source': b64(source.read_bytes())})
                  for name, source in sources.items()}
        assert all(row['accepted'] for row in parsed.values())
    finally:
        frontend.close()
    adapter = Worker([str(R / '_build/default/adapter/main.exe'), str(R)], out / 'syntax-adapter')
    try:
        fixtures = {name: adapter.request({'op': 'check', 'ast': row['ast'], 'fixture': True})['fixture']
                    for name, row in parsed.items()}
    finally:
        adapter.close()
    counts = {}
    for group in GROUPS:
        fixture, count = render(fixtures, sources, group)
        (out / (group + '.watsup')).write_text(fixture); counts[group] = count
    (out / 'prepared.json').write_text(json.dumps({'sources': {name: str(path) for name, path in sources.items()},
        'counts': counts, 'original_indices': {name: [index + 1 for index in indices] for name, indices in GROUPS.items()},
        'unique_premises': 111, 'repeated_setup': 25}) + '\n')
    return counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', choices=GROUPS)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    out = Path(tempfile.mkdtemp(prefix='interpolation-protocol-', dir=R / '.tools')); print(out, flush=True)
    modules = [R / name for name in json.loads((R / 'spec/semantics/modules.json').read_bytes())]
    runner = R / 'tests/semantics/_build/default/numeric_runner.exe'
    watched = [*modules, R / 'spec/semantics/modules.json', Path(__file__), runner,
               R / 'tests/semantics/error_handler_run.py', R / 'tests/semantics/recorded_worker.py',
               R / 'frontend/worker.php', R / '_build/default/adapter/main.exe',
               R / 'tests/semantics/profile.json', *sorted(SOURCES.glob('*.php'))]
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path.relative_to(R)): digest(path) for path in watched}
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip()
    counts = prepare(out)
    rows = []
    if not args.prepare_only:
        for group in ([args.group] if args.group else GROUPS):
            process = recorded([str(runner), *map(str, modules), str(out / (group + '.watsup'))], out / group, 90)
            passed = (process['exit'] == 0 and not process['timeout']
                      and (out / (group + '.stdout')).read_bytes() == b'true\n'
                      and not (out / (group + '.stderr')).read_bytes())
            rows.append({'group': group, 'conditions': counts[group], 'pass': passed, 'process': process})
            print(group, passed, flush=True)
    assert before == {str(path.relative_to(R)): digest(path) for path in watched}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip()
    (out / 'report.json').write_text(json.dumps({'revision': revision, 'inputs': before, 'rows': rows,
        'unique_premises': 111, 'repeated_setup': 25, 'prepare_only': args.prepare_only,
        'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'PHP_SPEC_SCRIPT_ENCODING': 'absent'}}, indent=2) + '\n')
    return all(row['pass'] for row in rows)


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
