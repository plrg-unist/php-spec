#!/usr/bin/env python3
"""Source-reached destructor pruning cases and original-state fallback."""
import argparse
import base64
import hashlib
import json
import os
import signal
import subprocess
import tempfile
import time
from pathlib import Path

from recorded_worker import Worker
from method_runtime import owned_members
import destructor_state_review as destructor

ROOT = Path(__file__).resolve().parents[2]
ENV = {'PATH': '/usr/bin:/bin', 'LC_ALL': 'C', 'TZ': 'UTC', 'PYTHONDONTWRITEBYTECODE': '1'}

CASE = destructor.CASES['return-owner-release-retains-active-replacement-throwable']
SOURCE_ID = 'assigned-return-value-chains-local-cleanup-exception'
STAGE = [
    'S.TODO = (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: ptask_tail*',
    'pdestructionframe.VALUE = KNOWN (POBJECT n_returned)',
    'pdestructionframe.PENDING = (n_last)',
]
PREFIX = '''dec $boundary_stage(pstate) : bool
def $boundary_stage(S) = true
''' + ''.join('  -- if ' + check + '\n' for check in STAGE) + '''def $boundary_stage(S) = false -- otherwise
dec $boundary_seek(pstate, nat) : pstate
def $boundary_seek(S, n) = S -- if S.COMPLETION =/= NORMAL /\\ S.COMPLETION =/= BUDGET
def $boundary_seek(S, n) = S -- if $boundary_stage(S) -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET
def $boundary_seek(S, 0) = S -- if ~$boundary_stage(S) -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET
def $boundary_seek(S, n) = $boundary_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$boundary_stage(S) -- if $(n > 0) -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET
dec $boundary_store_defined(pstate) : bool
def $boundary_store_defined(S) = true -- if S_new = $destruction_store_new(S)
def $boundary_store_defined(S) = false -- otherwise
'''


def assertions(checked, source):
    return [
        'S_initial = $php_run(' + checked['fixture'] + ', 0, ' + json.dumps(base64.b64encode(bytes(source)).decode()) + ')',
        'S_initial.COMPLETION = NORMAL \\/ S_initial.COMPLETION = BUDGET',
        'S_found = $boundary_seek(S_initial, 4000)',
        'S_found.COMPLETION = NORMAL \\/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]',
        *STAGE,
        'S.DESTRUCTION.FRAMES = [pdestructionframe]',
        'S.CURRENT = (pcallcontext)',
        'pdestructionframe.CALLER = S.CURRENT',
        '$throwable_field(S, n_last, "message") = PSTRING $ptascii("a")',
        '$throwable_previous_id(S, n_last) = (n_earlier)',
        '$throwable_field(S, n_earlier, "message") = PSTRING $ptascii("b")',
        '$heap_owners($heap_graph(S), HOBJECT n_last) = 1',
        '$heap_owners($heap_graph(S), HOBJECT n_returned) = 1',
        '$destructor_frame_valid(S, pdestructionframe)',
        *destructor.VALID,
        'PhpStep: S ~> S_step',
        'S_step.TODO = (THROW_SEARCH n_last) :: ptask_tail*',
        'S_step.DESTRUCTION.FRAMES = eps',
        '$heap_owners($heap_graph(S_step), HOBJECT n_last) = 1',
        '$heap_owners($heap_graph(S_step), HOBJECT n_returned) = 0',
        '~(n_returned <- S_step.DESTRUCTION.CALLED)',
        '$destruction_store_new(S_step) = S_step',
        'S_new = $request_fatal_state($destruction_store_new(S_step))',
        'S_new = S_step',
        'pnode_live* = $gc_prune_nodes(S_step)',
        '$destructor_waiting(S_new, $destruction_nodes_delete(S_new.ALLOCATIONS, pnode_live*))',
        '$destructor_operational(S_new)',
        '$destruction_prune_case(S_new, pnode_live*) = PRUNE_BEGIN_RELEASE',
        'S_begin = $destruction_prune(S_step, pnode_live*)',
        'S_begin = $destructor_release_begin(S_new, $destruction_values($gc_zero(S_new, $heap_graph(S_new), S_new.ALLOCATIONS)))',
        'S_begin.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: S_step.TODO',
        'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_returned)]',
        'pdestructionrelease.CALLER = S_step.CURRENT',
        'pdestructionrelease.ORIGIN = S_step.ORIGIN',
        'pdestructionrelease.CONSTCONTEXT = S_step.CONSTCONTEXT',
        'S_begin.DESTRUCTION.RELEASES = pdestructionrelease :: S_step.DESTRUCTION.RELEASES',
        'S_begin.FRAMES = S_step.FRAMES',
        'S_begin.CURRENT = S_step.CURRENT',
        'S_begin.PARAMETERRECEIVES = S_step.PARAMETERRECEIVES',
        '$heap_owners($heap_graph(S_begin), HOBJECT n_last) = 1',
        '$call_task_valid(S_begin, DESTRUCTOR_RELEASE pdestructionrelease)',
        'PhpStep: S_begin ~> S_selected',
        'S_selected.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_selected*',
        'pdestructorcall.OBJECT = n_returned',
        'pdestructorcall.PENDING = (n_last)',
        '$destructor_enter_valid(S_selected, pdestructorcall)',
        'pdestructorcall_clear = pdestructorcall[.PENDING = eps]',
        'S_clear = S_selected[.DESTRUCTION.CALLS = [pdestructorcall_clear]][.TODO = (DESTRUCTOR_ENTER pdestructorcall_clear) :: ptask_selected*]',
        '~$destructor_enter_valid(S_clear, pdestructorcall_clear)',
        '$heap_owners($heap_graph(S_selected), HOBJECT n_last) = 1',
        '$call_descriptors_valid(S_selected)',
        'S_unsupported = S_step[.COMPLETION = UNSUPPORTED "boundary control"]',
        '$destruction_prune_case(S_unsupported, pnode_live*) = PRUNE_KEEP_UNSUPPORTED',
        '$destruction_prune(S_unsupported, pnode_live*) = S_unsupported',
        'S_refuse = S_step[.DESTRUCTION.PHASE = DESTRUCTION_DONE]',
        '$destructor_waiting(S_refuse, $destruction_nodes_delete(S_refuse.ALLOCATIONS, pnode_live*))',
        '~$destructor_operational(S_refuse)',
        '$destruction_prune_case(S_refuse, pnode_live*) = PRUNE_REFUSE_RELEASE',
        '$destruction_prune(S_refuse, pnode_live*) = S_refuse[.COMPLETION = UNSUPPORTED "ordinary destructor release before request stage"]',
        'S_fatal = S_step[.COMPLETION = FATAL $ptascii("boundary control") 255]',
        'S_fatal_new = $request_fatal_state($destruction_store_new(S_fatal))',
        'S_fatal_new.DESTRUCTION.CALLED = $destructor_all(0, |S_fatal_new.OBJECTS|)',
        'S_fatal_new =/= S_fatal',
        '~$destructor_waiting(S_fatal_new, $destruction_nodes_delete(S_fatal_new.ALLOCATIONS, pnode_live*))',
        '$destruction_prune_case(S_fatal_new, pnode_live*) = PRUNE_DROP_STORE',
        'S_drop = $destruction_prune(S_fatal, pnode_live*)',
        'S_drop = $prune_live($destruction_store_drop(S_fatal_new, $gc_release_order(S_fatal_new, $heap_graph(S_fatal_new))), pnode_live*)',
        'S_drop.TODO = S_fatal.TODO',
        'S_drop.CURRENT = S_fatal.CURRENT',
        'S_drop.FRAMES = S_fatal.FRAMES',
        'S_drop.CONSTCONTEXT = S_fatal.CONSTCONTEXT',
        'S_drop.PARAMETERRECEIVES = S_fatal.PARAMETERRECEIVES',
        '$heap_owners($heap_graph(S_drop), HOBJECT n_last) = 1',
        'S_bad = S_fatal[.DESTRUCTION.HANDLES = S_fatal.DESTRUCTION.HANDLES ++ [S_fatal.DESTRUCTION.NEXT]]',
        '$(|S_bad.DESTRUCTION.HANDLES| > |S_bad.OBJECTS|)',
        '~$destruction_state_valid(S_bad)',
        '~$boundary_store_defined(S_bad)',
        'S_bad_marked = $request_fatal_state(S_bad)',
        'n_returned <- S_bad_marked.DESTRUCTION.CALLED',
        '~(n_returned <- S_bad.DESTRUCTION.CALLED)',
        'S_fallback = $destruction_prune(S_bad, pnode_live*)',
        'S_fallback = $prune_live(S_bad, pnode_live*)',
        'S_fallback =/= $prune_live(S_bad_marked, pnode_live*)',
        'S_fallback.DESTRUCTION = S_bad.DESTRUCTION',
        'S_fallback.TODO = S_bad.TODO',
        'S_fallback.CURRENT = S_bad.CURRENT',
        'S_fallback.FRAMES = S_bad.FRAMES',
        'S_fallback.PARAMETERRECEIVES = S_bad.PARAMETERRECEIVES',
        '$heap_owners($heap_graph(S_fallback), HOBJECT n_last) = 1',
        'S_done = $drive(S_selected, 2000)',
        'S_done.COMPLETION = NORMAL',
        *destructor.DONE,
    ]


def prepare(out):
    out.mkdir(parents=True, exist_ok=True)
    source = out / 'source.php'
    source.write_text(CASE['source'])
    original = next(row for row in json.loads((ROOT / 'tests/semantics/destructor_review_cases.json').read_text()) if row['id'] == SOURCE_ID)
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
    flags = [arg for key, value in profile.items() for arg in ['-d', key + '=' + value]]
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *flags, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter-check')
    try:
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
        assert parsed['accepted']
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok']
    finally:
        frontend.close()
        adapter.close()
    checks = assertions(checked, source)
    fixture = out / 'protocol.watsup'
    fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- ' + ('' if check.startswith('PhpStep:') else 'if ') + check + '\n' for check in checks))
    (out / 'prepared.json').write_text(json.dumps({
        'source': str(source), 'fixture': str(fixture), 'checked': checked,
        'assertions': len(checks), 'original': 'destructor_state_review.py: return-owner-release-retains-active-replacement-throwable',
        'expected_stdout': base64.b64encode(original['stdout'].encode()).decode(),
        'expected_stderr': base64.b64encode(original['stderr'].encode()).decode(),
        'expected_exit': original['exit'], 'application_evaluations': 0,
        'scope': 'Authentic FRAME_EXIT/raw PhpStep release and pending Throwable. Direct controlled completion/phase/handles mutations are only branch/fallback counterexamples; they earn no admission or source agreement credit. Selected-RHS Unmatch fallback is statically reviewed, not exercised by this fixture.',
    }, indent=2) + '\n')
    return json.loads((out / 'prepared.json').read_text())


def run(out, prepared):
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    command = [str(runner), '--sl', *map(str, modules), prepared['fixture']]
    watched = [*modules, ROOT / 'spec/semantics/modules.json', runner,
               Path(prepared['source']), Path(prepared['fixture']), Path(__file__)]
    fingerprint = lambda: {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    before = fingerprint()
    raw = Path(tempfile.mkdtemp(prefix='numeric-', dir=out))
    record = {'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip(),
              'mode': 'strictSL/dettrue/cachefalse', 'assertions': prepared['assertions'],
              'command': command, 'cwd': str(ROOT), 'environment': ENV, 'timeout': 120,
              'inputs': before, 'started_at': time.time(), 'exit': None}
    with (raw / 'stdout').open('xb') as stdout, (raw / 'stderr').open('xb') as stderr:
        process = subprocess.Popen(command, cwd=ROOT, env=ENV, stdout=stdout, stderr=stderr, start_new_session=True)
        record.update(pid=process.pid, owned_pgid=process.pid)
        (raw / 'report.json').write_text(json.dumps(record, indent=2) + '\n')
        try:
            record['exit'] = process.wait(timeout=120)
        except subprocess.TimeoutExpired:
            record['timed_out'] = True
        finally:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            record['cleanup_exit'] = process.wait(timeout=5)
            record['owned_group_after'] = owned_members(process.pid)
    record['seconds'] = time.time() - record['started_at']
    record['inputs_unchanged'] = before == fingerprint()
    record['passed'] = (record['exit'] == record['cleanup_exit'] == 0 and record['inputs_unchanged']
                        and not record['owned_group_after'] and (raw / 'stdout').read_bytes() == b'true\n'
                        and (raw / 'stderr').read_bytes() == b'')
    (raw / 'report.json').write_text(json.dumps(record, indent=2) + '\n')
    assert record['passed'], str(raw)
    return raw


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    paths = parser.add_mutually_exclusive_group()
    paths.add_argument('--prepare-only', type=Path)
    paths.add_argument('--work', type=Path)
    args = parser.parse_args()
    out = (args.prepare_only or args.work or Path(tempfile.mkdtemp(prefix='destruction-prune-', dir=ROOT / '.tools'))).resolve()
    prepared = (json.loads((out / 'prepared.json').read_text())
                if args.work and (out / 'prepared.json').exists() else prepare(out))
    if not args.prepare_only:
        out = run(out, prepared)
    print(out, prepared['assertions'], flush=True)


if __name__ == '__main__':
    main()
