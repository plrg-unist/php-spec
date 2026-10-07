#!/usr/bin/env python3
"""Check active directory facts and exclude loader markers from parked Fibers."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
from recorded_worker import Worker
from method_runtime import owned_members

ENV = {'PATH': '/usr/bin:/bin', 'LC_ALL': 'C', 'TZ': 'UTC',
       'PYTHONDONTWRITEBYTECODE': '1', 'GIT_OPTIONAL_LOCKS': '0'}


def b64(data):
    return base64.b64encode(data).decode()


def seq(data):
    return '(' + str(list(data)) + ')'


def prepare(OUT):
    OUT.mkdir(parents=True, exist_ok=True)
    destination = OUT / 'destination'
    destination.mkdir(exist_ok=True)
    cwd, requested = os.fsencode(ROOT), os.fsencode(destination.resolve())
    assert ROOT.is_dir() and destination.is_dir()
    source = (b'<?php\nclass ChdirReview296 {\n'
              b'public function __toString(): string { echo "S|"; return "__DEST__"; }\n}\n'
              b'function parkedChdirReview296() {\n'
              b'$f = new Fiber(static function() { echo chdir(new ChdirReview296) ? "T|" : "F|"; });\n'
              b'$f->start(); echo "M";\n}\nparkedChdirReview296();\n').replace(b'__DEST__', requested)
    path = OUT / 'source.php'
    path.write_bytes(source)
    snapshot = {'version': 2, 'main': b64(os.fsencode(path)), 'cwd': b64(cwd),
                'include_path': b64(b'.:'), 'entries': [], 'chdir_entries': [
                    {'cwd': b64(cwd), 'requested': b64(requested),
                     'status': 'success', 'next_cwd': b64(requested)}]}
    (OUT / 'snapshot.json').write_text(json.dumps(snapshot, indent=2) + '\n')
    frontend_command = [str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')]
    adapter_command = [str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)]
    frontend = Worker(frontend_command, OUT / 'frontend')
    adapter = Worker(adapter_command, OUT / 'adapter-check')
    try:
        parsed = frontend.request({'op': 'parse', 'source': b64(source)})
        assert parsed['accepted'], parsed
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok'], checked
    finally:
        frontend.close()
        adapter.close()
    response = 'DIR_CHANGED pdircontext.NONCE ' + seq(cwd) + ' ' + seq(requested) + ' ' + seq(requested)
    checks = [
        'S = $php_file_run(' + checked['fixture'] + ', 1000, $base64(' + json.dumps(snapshot['main']) + '), ' + seq(cwd) + ')',
        'S.COMPLETION = SOURCE_PENDING',
        'S.EVENTS = [OUTPUT $ptascii("S|")]',
        'S.DIRCONTEXT = (pdircontext)',
        'S.TODO = (CHDIR_AWAIT pdircontext.CALL pdircontext.NONCE) :: ptask_tail*',
        'pdircontext.CWD = ' + seq(cwd),
        'pdircontext.REQUESTED = ' + seq(requested),
        'pdircontext.FRAMEOWNER = |S.FRAMES|',
        'S.DIRSEQ = $(pdircontext.NONCE + 1)',
        'S.SOURCEPENDING = eps',
        '$source_pending_state_valid(S)',
        'S.EVALCONTEXTS = eps /\\ S.FILECONTEXTS = eps',
        'S.ACTIVEFIBER = (n_fiber)',
        'S.OBJECTS[n_fiber] = FIBER pfiber',
        'pfiber.STATUS = FIBER_RUNNING',
        'S.FIBERCALLERS = [pfibercaller]',
        'pfibercaller.OBJECT = n_fiber',
        'pfibervm = pfibercaller.VM',
        '~pfibervm.GLOBAL',
        'pfibervm.TODO = (FIBER_WAIT pfibercaller.API) :: ptask_parked*',
        'pfibervm.FRAMES = [pframe]',
        'S.DIRCONVSEQ = 1',
        'S.DIRCONVERSIONS = [pdirconversion]',
        'pdircontext.CONVERSION = (0)',
        'pdirconversion.RESULT = ' + seq(requested),
        'pdirconversion.OWNERDEPTH = pdircontext.FRAMEOWNER',
        '$dir_pending_state_valid(S)',
        '$dir_state_valid(S)',
        '$heap_valid($heap_graph(S))',
        'S_uncleared = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = pfibercaller.PREVIOUS][.FIBERCALLERS = eps][.COMPLETION = NORMAL][.EVALCONTEXTS = eps][.FILECONTEXTS = eps]',
        'S_uncleared.DIRCONTEXT = S.DIRCONTEXT',
        '~$dir_state_valid(S_uncleared)',
        'S_view = S_uncleared[.DIRCONTEXT = eps]',
        '$source_pending_state_valid(S_view)',
        '$dir_state_valid(S_view)',
        '$call_descriptors_scoped_valid(S, S_view)',
        '$fiber_vm_valid(S, pfibervm, pfibercaller.PREVIOUS, eps)',
        '$call_descriptors_valid(S)',
        'S_bad_owner = S[.DIRCONTEXT = (pdircontext[.FRAMEOWNER = $(pdircontext.FRAMEOWNER + 1)])]',
        '$heap_valid($heap_graph(S_bad_owner))',
        '~$dir_pending_state_valid(S_bad_owner)',
        '~$dir_state_valid(S_bad_owner)',
        '~$call_descriptors_scoped_valid(S_bad_owner, S_view)',
        '~$call_descriptors_valid(S_bad_owner)',
        'S_bad_log = S[.DIRCONVERSIONS = [pdirconversion, pdirconversion]]',
        '$dir_pending_state_valid(S_bad_log)',
        '~$dir_state_valid(S_bad_log)',
        '~$call_descriptors_scoped_valid(S_bad_log, S_view)',
        'pfibervm_direct = pfibervm[.TODO = (FIBER_WAIT pfibercaller.API) :: (CHDIR_AWAIT pdircontext.CALL pdircontext.NONCE) :: ptask_parked*]',
        'S_direct = S[.FIBERCALLERS = [pfibercaller[.VM = pfibervm_direct]]]',
        '$heap_valid($heap_graph(S_direct))',
        '~$fiber_vm_valid(S, pfibervm_direct, pfibercaller.PREVIOUS, eps)',
        '~$call_descriptors_valid(S_direct)',
        'pfibervm_hidden = pfibervm[.TODO = (FIBER_WAIT pfibercaller.API) :: (CHOOSE ([CHDIR_AWAIT pdircontext.CALL pdircontext.NONCE]) eps 1) :: ptask_parked*]',
        'S_hidden = S[.FIBERCALLERS = [pfibercaller[.VM = pfibervm_hidden]]]',
        '$heap_valid($heap_graph(S_hidden))',
        '~$fiber_vm_valid(S, pfibervm_hidden, pfibercaller.PREVIOUS, eps)',
        '~$call_descriptors_valid(S_hidden)',
        'pfibervm_frame = pfibervm[.FRAMES = [pframe[.TODO = (CHDIR_AWAIT pdircontext.CALL pdircontext.NONCE) :: pframe.TODO]]]',
        'S_frame = S[.FIBERCALLERS = [pfibercaller[.VM = pfibervm_frame]]]',
        '$heap_valid($heap_graph(S_frame))',
        '~$fiber_vm_valid(S, pfibervm_frame, pfibercaller.PREVIOUS, eps)',
        '~$call_descriptors_valid(S_frame)',
        '$dir_response_valid(S, ' + response + ')',
        '~$dir_response_valid(S_bad_owner, ' + response + ')',
        'S_done = $dir_continue(S, ' + response + ')',
        'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps',
        'S_done.EVENTS = [OUTPUT $ptascii("S|"), OUTPUT $ptascii("T|"), OUTPUT $ptascii("M")]',
        'S_done.FILECWD = (' + seq(requested) + ')',
        'S_done.DIRCONTEXT = eps /\\ S_done.EVALCONTEXTS = eps /\\ S_done.FILECONTEXTS = eps',
        'S_done.SOURCEPENDING = eps /\\ S_done.ACTIVEFIBER = eps /\\ S_done.FIBERCALLERS = eps',
        '$call_descriptors_valid(S_done)',
        '$heap_valid($heap_graph(S_done))',
    ]
    fixture = OUT / 'protocol.watsup'
    fixture.write_text('dec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + check + '\n' for check in checks))
    report = {'scope': 'Checked preparation only; no model or native execution credit.',
              'source': str(path), 'fixture': str(fixture), 'snapshot': str(OUT / 'snapshot.json'),
              'assertions': len(checks), 'expected_stdout': b64(b'S|T|M'),
              'preparation_commands': [frontend_command, adapter_command],
              'files': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in [path, fixture, OUT / 'snapshot.json', Path(__file__)]}}
    (OUT / 'prepared.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


def run(out, prepared):
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    command = [str(runner), '--sl', *map(str, modules), prepared['fixture']]
    source_files = [out / name for name in ['source.php', 'snapshot.json', 'protocol.watsup']]
    before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files}
    assert all(before[name] == prepared['files'][name] for name in before)
    watched = [*modules, ROOT / 'spec/semantics/modules.json', runner]
    before_model = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}
    raw = Path(tempfile.mkdtemp(prefix='numeric-', dir=out))
    semantic_diff = subprocess.check_output(['git', 'diff', 'HEAD', '--', 'spec'], cwd=ROOT, env=ENV)
    (raw / 'semantics.diff').write_bytes(semantic_diff)
    record = {'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, env=ENV).decode().strip(),
              'mode': 'strictSL/dettrue/cachefalse', 'assertions': prepared['assertions'],
              'command': command, 'cwd': str(ROOT), 'environment': ENV, 'timeout_seconds': 120,
              'runner_sha256': hashlib.sha256(runner.read_bytes()).hexdigest(),
              'test_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'prepared_files': before, 'inputs': before_model, 'started_at': time.time(), 'exit': None,
              'semantics_diff_sha256': hashlib.sha256(semantic_diff).hexdigest()}
    with (raw / 'stdout').open('xb') as stdout, (raw / 'stderr').open('xb') as stderr:
        process = subprocess.Popen(command, cwd=ROOT, env=ENV, stdout=stdout, stderr=stderr, start_new_session=True)
        record.update(pid=process.pid, owned_pgid=process.pid)
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
    record['ended_at'] = time.time()
    record['prepared_files_unchanged'] = before == {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files}
    record['inputs_unchanged'] = before_model == {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}
    record['passed'] = (record['exit'] == record['cleanup_exit'] == 0 and record['prepared_files_unchanged'] and record['inputs_unchanged']
                        and not record['owned_group_after'] and (raw / 'stdout').read_bytes() == b'true\n'
                        and (raw / 'stderr').read_bytes() == b'')
    (raw / 'report.json').write_text(json.dumps(record, indent=2) + '\n')
    assert record['passed'], record
    return raw


def main():
    parser = argparse.ArgumentParser()
    paths = parser.add_mutually_exclusive_group()
    paths.add_argument('--prepare-only', type=Path)
    paths.add_argument('--work', type=Path)
    arguments = parser.parse_args()
    out = (arguments.prepare_only or arguments.work or Path(tempfile.mkdtemp(prefix='fiber-chdir-scope-', dir=ROOT / '.tools'))).resolve()
    prepared = (json.loads((out / 'prepared.json').read_text())
                if arguments.work and (out / 'prepared.json').exists() else prepare(out))
    if not arguments.prepare_only:
        out = run(out, prepared)
    print(out, prepared['assertions'], flush=True)


if __name__ == '__main__':
    main()
