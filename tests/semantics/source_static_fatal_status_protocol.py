#!/usr/bin/env python3
"""Fatal request status at real shutdown string, integer and default exits."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import source_static_fatal_protocol as fatal
from recorded_worker import Worker
from typed_static_invoke_set_protocol import process

retirement = fatal.retirement
ROOT, inputs, types = retirement.ROOT, retirement.inputs, retirement.types
seq, byte_expr, b64 = retirement.seq, retirement.byte_expr, retirement.b64
STAGES = {'eval-string': 'eval-fatal-shutdown-string',
    'file-zero': 'file-fatal-shutdown-zero', 'eval-default': 'eval-fatal-shutdown-default'}
PREFIX = r'''dec $stage(pstate,text) : bool
def $stage(S,"fatal") = true
  -- if S.TODO = (ERROR_TRIGGER_PHASE pconfigcall 1) :: ptask_tail*
def $stage(S,"exit") = true
  -- if S.TODO = (EXIT_INVOKE pexitcall) :: ptask_tail*
def $stage(S,text) = false -- otherwise
dec $seek(pstate,text,nat) : pstate
def $seek(S,text,n) = S -- if $stage(S,text)
def $seek(S,text,n) = $seek($drive_steps(S[.COMPLETION = NORMAL],1),text,$nabs($(n - 1)))
  -- if ~$stage(S,text) -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET -- if $(n > 0)
def $seek(S,text,n) = S -- otherwise
''' + retirement.PREFIX[retirement.PREFIX.index('dec $one'):]


def native_record(sources, case):
    suite = sources / 'static-native-v18'
    report = json.loads((suite / 'report.json').read_text())
    row, = [row for row in report['records'] if row['id'] == case]
    assert report['target'] == types.PROFILE
    assert report['runtime_sha256'] == hashlib.sha256(types.PHP.read_bytes()).hexdigest()
    directory = suite / case
    assert json.loads((directory / 'native/process.json').read_text())['exit_status'] == row['exit']
    assert (directory / 'native/stdout').read_bytes() == row['stdout'].encode()
    assert (directory / 'native/stderr').read_bytes() == row['stderr'].encode()
    for name, digest in row['originals'].items():
        assert hashlib.sha256((directory / name).read_bytes()).hexdigest() == digest
    return directory, row


def checks_for(name, native):
    status = native['exit']
    checks = ['S_ready.COMPLETION = NORMAL', 'S_ready.EXITSTATUS = 0',
        *fatal.reached('S', '$seek(S_ready,"fatal",1800)'),
        'S.TODO = (ERROR_TRIGGER_PHASE pconfigcall 1) :: ptask_fatal_tail*',
        '$error_trigger_level(S,pconfigcall) = (256)', 'S.EXITSTATUS = 0',
        '$source_static_user_source(S)', 'S.STATICS = [pstaticcell]',
        'S.STORE[pstaticcell.CELL] = DEFINED (POBJECT n_object)',
        '$weakref_find(S,S.ALLOCATIONS,n_object) = (n_weak)',
        '$weakref_get(S,n_weak) = POBJECT n_object',
        '$test_outputs(S.EVENTS) = $ptascii("B|")', *fatal.public('S'),
        *fatal.reached('S_frozen', '$drive_steps(S,1)'),
        'S_frozen.SHUTDOWN.PHASE = SHUTDOWN_RUNNING',
        'S_frozen.SHUTDOWN.COMPLETION = REQUESTFATAL ($ptascii("Error")) ($ptascii("stop")) 1',
        'S_frozen.EXITSTATUS = 255', 'S_frozen.CURRENT = eps', 'S_frozen.FRAMES = eps',
        'S_frozen.EVALCONTEXTS = eps', 'S_frozen.FILECONTEXTS = eps',
        'S_frozen.STATICS = S.STATICS', 'n_object <- S_frozen.DESTRUCTION.CALLED',
        '$weakref_get(S_frozen,n_weak) = POBJECT n_object',
        '$test_outputs(S_frozen.EVENTS) = $ptascii("B|")', *fatal.public('S_frozen'),
        *fatal.reached('S_exit', '$seek(S_frozen,"exit",1800)'),
        'S_exit.TODO = (EXIT_INVOKE pexitcall) :: ptask_exit_tail*',
        'S_exit.EXITSTATUS = 255', 'S_exit.CURRENT = (pcallcontext)',
        'S_exit.FRAMES = [pframe]', 'S_exit.SHUTDOWN.PHASE = SHUTDOWN_RUNNING',
        'S_exit.SHUTDOWN.INDEX = 0', '|S_exit.SHUTDOWN.ENTRIES| = 2',
        'S_exit.STATICS = S.STATICS', 'n_object <- S_exit.DESTRUCTION.CALLED',
        '$weakref_get(S_exit,n_weak) = POBJECT n_object',
        '$test_outputs(S_exit.EVENTS) = $ptascii("B|S|alive|")', *fatal.public('S_exit')]
    if name == 'eval-string':
        checks += ['pexitcall.SENT = [KNOWN pvalue_string]',
            '$string_bytes(pvalue_string) = ($ptascii("X|"))']
    else:
        checks += ['pexitcall.SENT = ' + ('[KNOWN (PINT 0)]' if name == 'file-zero' else 'eps')]
    checks += ['S_written = $one(S_exit)', 'S_written.COMPLETION = EXITED ' + str(status),
        'S_written.EXITSTATUS = ' + str(status), 'S_written.STATICS = S_exit.STATICS',
        'S_written.DESTRUCTION.CALLED = S_exit.DESTRUCTION.CALLED',
        'S_written.EVENTS = S_exit.EVENTS' + (' ++ [OUTPUT ($ptascii("X|"))]' if name == 'eval-string' else ''),
        '$weakref_get(S_written,n_weak) = POBJECT n_object',
        'S_final = $drive_steps(S_exit,1800)', 'S_final.COMPLETION = EXITED ' + str(status),
        'S_final.EXITSTATUS = ' + str(status), 'S_final.SHUTDOWN.PHASE = SHUTDOWN_DONE',
        'S_final.CURRENT = eps', 'S_final.FRAMES = eps', 'S_final.TODO = eps',
        'S_final.EVALCONTEXTS = eps', 'S_final.FILECONTEXTS = eps', 'S_final.STATICS = S.STATICS',
        'n_object <- S_final.DESTRUCTION.CALLED', '$weakref_get(S_final,n_weak) = POBJECT n_object',
        '$test_outputs(S_final.EVENTS) = $ptascii(' + json.dumps(native['stdout']) + ')', *fatal.public('S_final')]
    return checks


def prepare(out, sources, names):
    out.mkdir()
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = None
    try:
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for name in names:
            directory, native = native_record(sources, STAGES[name])
            main_path = directory / 'main.php'
            parsed = frontend.request({'op': 'parse', 'source': b64(main_path.read_bytes())})
            assert parsed['accepted'], parsed
            main_ast = parsed['ast']
            main_fixture = adapter.request({'op': 'check', 'ast': main_ast, 'fixture': True})['fixture']
            is_file = name == 'file-zero'
            if is_file:
                child_path = directory / 'unit.php'
                child_bytes = child_path.read_bytes()
                request = {'op': 'parse-file', 'id': '1', 'mode': 'file', 'profile': 'cli-raw-85',
                    'requested': b64(os.fsencode(child_path)), 'resolved': b64(os.fsencode(child_path)),
                    'opened': b64(os.fsencode(child_path)), 'source': b64(child_bytes)}
            else:
                evaluation, = [node for _, node, _ in retirement.nodes(main_ast['program']) if node['node'] == 'Expr_Eval']
                child_bytes = base64.b64decode(evaluation['fields'][0]['fields'][0]['bytes'])
                request = {'op': 'parse-eval', 'id': '1', 'mode': 'eval', 'profile': 'cli-raw-85', 'source': b64(child_bytes)}
            parsed = frontend.request(request)
            assert parsed['accepted'], parsed
            child_fixture = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})['fixture']
            checks = ['S_wait = $php_file_run(' + main_fixture + ',1800,' + byte_expr(os.fsencode(main_path)) + ',' + byte_expr(os.fsencode(directory)) + ')',
                'S_wait.COMPLETION = SOURCE_PENDING']
            if is_file:
                checks += ['S_wait.FILECONTEXTS = [pfilecontext_wait]',
                    'S_parse = $file_open_resume(S_wait,FILE_OPENED pfilecontext_wait.NONCE pfilecontext_wait.CALLER pfilecontext_wait.REQUESTED ' + seq(os.fsencode(child_path)) + ' ' + seq(os.fsencode(child_path)) + ' ' + seq(child_bytes) + ')',
                    'S_parse.COMPLETION = SOURCE_PENDING',
                    'S_ready = $file_parse_resume(S_parse,SOURCE_ACCEPT 1 ' + seq(child_bytes) + ' ' + child_fixture + ')']
            else:
                checks += ['S_ready = $eval_resume(S_wait,SOURCE_ACCEPT 1 ' + seq(child_bytes) + ' ' + child_fixture + ')']
            checks += checks_for(name, native)
            target = out / name
            target.mkdir()
            (target / 'protocol.watsup').write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
                ''.join('  -- if ' + item + '\n' for item in checks))
            (target / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
    finally:
        if adapter:
            adapter.close()
        frontend.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['fixtures', 'check'], required=True)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--stage', action='append', default=[])
    parser.add_argument('--attempt', type=int, default=1)
    args = parser.parse_args()
    names = args.stage or list(STAGES)
    assert args.attempt > 0 and names and len(set(names)) == len(names) and set(names) <= STAGES.keys()
    out, sources = args.output.resolve(), args.sources.resolve()
    paths = [Path(__file__), Path(fatal.__file__), Path(retirement.__file__), ROOT / 'tests/semantics/recorded_worker.py',
        ROOT / 'tests/semantics/_build/default/numeric_runner.exe', sources / 'static-native-v18/report.json', sources / 'static-native-v18/run.py']
    for name in names:
        directory = sources / 'static-native-v18' / STAGES[name]
        paths += [*sorted(directory.glob('*.php')),
            *[directory / 'native' / item for item in ['stdout', 'stderr', 'process.json', 'command.json']]]
        if args.phase == 'check':
            paths += [out / name / 'protocol.watsup', out / name / 'assertions.json']
    pins = lambda: dict(inputs.inputs(), **{str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths})
    before = pins()
    label = args.phase if args.attempt == 1 else args.phase + '-' + str(args.attempt)
    report = {'phase': args.phase, 'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'semantic_diff_sha256': hashlib.sha256(subprocess.check_output(['git', 'diff', 'HEAD', '--', 'spec/semantics'], cwd=ROOT)).hexdigest(),
        'inputs': before, 'profile': types.PROFILE, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC'},
        'records': [], 'result': 'fail', 'runtime_assertions': 0}
    try:
        if args.phase == 'fixtures':
            prepare(out, sources, names)
            report['result'] = 'pass'
        else:
            modules = [str(ROOT / name) for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
            for name in names:
                directory = out / name
                result = process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *modules, str(directory / 'protocol.watsup')],
                    directory / label, 90, ROOT)
                passed = result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
                count = len(json.loads((directory / 'assertions.json').read_text()))
                report['records'].append({'id': name, 'pass': passed, 'runtime_assertions': count})
                report['runtime_assertions'] += count if passed else 0
                print(name, passed, flush=True)
                if not passed:
                    break
            report['result'] = 'pass' if len(report['records']) == len(names) and all(row['pass'] for row in report['records']) else 'fail'
    finally:
        report['stable_inputs'] = before == pins()
        if not report['stable_inputs']:
            report['result'] = 'fail'
        (out / (label + '-report.json')).write_text(json.dumps(report, indent=2) + '\n')
    return report['result'] == 'pass'


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
