#!/usr/bin/env python3
"""Native-first backtick comparisons; the model receives finite pipe facts only."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import resource
import struct
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PROFILE = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
FLAGS = [argument for key, value in PROFILE.items() for argument in ('-d', key + '=' + value)]
ENV = [(b'LC_ALL', b'C'), (b'TZ', b'UTC'), (b'PATH', b'/usr/bin:/bin'),
       (b'SHELL_TEST', b'first'), (b'SHELL_TEST', b'last')]
DEPRECATED = b'The backtick (`) operator is deprecated, use shell_exec() instead'


def opened(command, stdout=b'', stderr=b''):
    return {'command': command, 'opened': True, 'stdout': stdout, 'stderr': stderr}


CASES = {
    'literal': (b"<?php\necho `printf 'literal\\n'`;\n", b'literal\n',
                [opened(b"printf 'literal\n'", b'literal\n')]),
    'root-namespace': (b"<?php\nnamespace N; function shell_exec($s) { return 'wrong'; }\necho `printf root`;\n",
                       b'root', [opened(b'printf root', b'root')]),
    'empty-output': (b"<?php\necho `:` === null ? 'null|' : 'bad|';\necho `exit 7` === null ? 'null' : 'bad';\n",
                     b'null|null', [opened(b':'), opened(b'exit 7')]),
    'binary-output': (b"<?php\n$s = `printf 'A\\\\000B'`; echo $s === \"A\\0B\" ? 'binary' : 'bad';\n",
                      b'binary', [opened(b"printf 'A\\000B'", b'A\0B')]),
    'stderr-output': (b"<?php\necho `printf out; printf err >&2`;\n", b'out',
                      [opened(b'printf out; printf err >&2', b'out', b'err')]),
    'scalar-interpolation': (b"<?php\n$n = 12; $b = true; $nothing = null; echo `printf '$n/$b/$nothing'`;\n",
                             b'12/1/', [opened(b"printf '12/1/'", b'12/1/')]),
    'stringable-once': (b"<?php\nclass C { function __toString(): string { echo 'T'; return 'ok'; } }\n$c = new C; echo `printf {$c}`;\n",
                        b'Tok', [opened(b'printf ok', b'ok')]),
    'array-handler': (b"<?php\n$x = []; set_error_handler(function() { global $x; $x = 'changed'; echo 'H'; return true; });\necho `printf {$x}`, '/', $x;\n",
                      b'HArray/changed', [opened(b'printf Array', b'Array')]),
    'undefined-handler': (b"<?php\nset_error_handler(function() { global $missing; $missing = 'late'; echo 'H'; return true; });\necho `printf '{$missing}!'`;\n",
                          b'Hlate!', [opened(b"printf 'late!'", b'late!')]),
    'command-empty': (b"<?php\ntry { echo ``; } catch (ValueError $e) { echo $e->getMessage(), '|', $e->getTrace()[0]['function']; }\n",
                      b'shell_exec(): Argument #1 ($command) must not be empty|shell_exec', []),
    'command-nul': (b"<?php\n$x = \"printf X\\0\"; try { echo `{$x}`; } catch (ValueError $e) { echo $e->getMessage(), '|', $e->getTrace()[0]['function']; }\n",
                    b'shell_exec(): Argument #1 ($command) must not contain any null bytes|shell_exec', []),
    'empty-trace': (b'<?php\n``;\n', b'', []),
    'nul-trace': (b'<?php\n$x = "printf X\\0"; `{$x}`;\n', b'', []),
    'compile-dead': (b"<?php\nif (false) { echo `printf BAD`; }\nfunction unused() { return `printf BAD`; }\necho 'safe';\n",
                     b'safe', []),
    'suppressed-deprecation': (b"<?php\n@`printf ok`; echo 'done';\n", b'done',
                               [opened(b'printf ok', b'ok')]),
    'cast-throw': (b"<?php\nclass C { function __toString(): string { echo 'T'; throw new Exception('cast'); } }\n$c = new C; try { echo `printf {$c}`; } catch (Exception $e) { echo $e->getMessage(); }\n",
                   b'Tcast', []),
    'read-throw': (b"<?php\n$shared = new Exception('read'); set_error_handler(function() { global $shared; throw $shared; });\ntry { echo `{$missing}`; } catch (Exception $e) { echo $e === $shared ? 'same' : 'bad'; }\n",
                   b'same', []),
    'pipe-failure-default': (b"<?php\n$x = `printf X`; echo $x === false ? 'false' : 'bad';\n", b'false',
                             [{'command': b'printf X', 'opened': False}]),
    'pipe-failure-handler': (b"<?php\nset_error_handler(function($n, $m) { echo $n, ':', $m, '|'; return true; });\n$x = `printf X`; echo $x === false ? 'false' : 'bad';\n",
                             b"2:shell_exec(): Unable to execute 'printf X'|false",
                             [{'command': b'printf X', 'opened': False}]),
    'pipe-failure-throw': (b"<?php\n$shared = new Exception('shared'); set_error_handler(function() { global $shared; throw $shared; });\ntry { echo `printf X`; } catch (Exception $e) { echo $e === $shared ? 'same' : 'bad'; }\n",
                           b'same', [{'command': b'printf X', 'opened': False}]),
}


def b64(value):
    return base64.b64encode(value).decode()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fingerprint():
    modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
    names = ['spec/php.watsup', 'spec/semantics/modules.json', *modules, 'adapter/main.ml',
             'bin/php-semantics', '.tools/php/bin/php', '.tools/php-file.so',
             '.tools/request-clock.so', '_build/default/adapter/main.exe',
             'vendor/php-src/Zend/zend_compile.c', 'vendor/php-src/ext/standard/exec.c',
             'tests/semantics/profile.json', 'tests/semantics/shell_sources.py']
    return {name: sha(ROOT / name) for name in names}


def request(path, cwd):
    return {'env': [[b64(name), b64(value)] for name, value in ENV],
            'argv': [b64(os.fsencode(path))], 'file': b64(os.fsencode(path)),
            'seconds': '0', 'microseconds': 0, 'variables': b64(b'EGPCS'), 'jit': True,
            'cwd': b64(os.fsencode(cwd))}


def snapshot(path, directory, facts):
    entries = []
    for index, fact in enumerate(facts):
        entry = {'id': str(index), 'cwd': b64(os.fsencode(directory)),
                 'env': [[b64(name), b64(value)] for name, value in ENV],
                 'command': b64(fact['command']), 'opened': fact['opened']}
        if fact['opened']:
            entry.update(stdout=b64(fact['stdout']), stderr=b64(fact['stderr']))
        entries.append(entry)
    return {'version': 2, 'main': b64(os.fsencode(path)), 'cwd': b64(os.fsencode(directory)),
            'include_path': b64(b'.:'), 'entries': [], 'chdir_entries': [], 'shell_entries': entries}


def run(command, directory, name, *, native=False, failure=False):
    environment = {'LC_ALL': 'C', 'TZ': 'UTC'}
    kwargs = {}
    if native:
        entries = [name + b'=' + value for name, value in ENV]
        packet = b'PHPRQ001' + struct.pack('<qII', 0, 0, len(entries)) + b''.join(
            struct.pack('<I', len(entry)) + entry for entry in entries)
        payload_path = directory / 'request.bin'; payload_path.write_bytes(packet)
        payload = payload_path.open('rb')
        os.dup2(payload.fileno(), 198)
        environment = {'LD_PRELOAD': str(ROOT / '.tools/request-clock.so')}
        kwargs['pass_fds'] = (198,)
        if failure:
            kwargs['preexec_fn'] = lambda: resource.setrlimit(resource.RLIMIT_NOFILE, (4, 4))
    (directory / (name + '.command.json')).write_text(json.dumps(
        {'argv': command, 'cwd': str(directory), 'env': environment,
         'RLIMIT_NOFILE': [4, 4] if failure else None}) + '\n')
    try:
        result = subprocess.run(command, cwd=directory, env=environment,
                                capture_output=True, timeout=90, **kwargs)
    finally:
        if native:
            os.close(198); payload.close()
    for suffix, data in [('stdout', result.stdout), ('stderr', result.stderr)]:
        (directory / (name + '.' + suffix)).write_bytes(data)
    (directory / (name + '.exit')).write_text(str(result.returncode) + '\n')
    return result


def native_case(name, directory, path):
    result = run([str(ROOT / '.tools/php/bin/php'), '-n', *FLAGS, '-d',
                  'variables_order=EGPCS', str(path)], directory, 'native', native=True,
                 failure=name.startswith('pipe-failure'))
    expected = CASES[name][1]
    assert result.stdout == expected, (name, result.stdout, expected)
    expected_exit = 255 if name in ('empty-trace', 'nul-trace') else 0
    assert result.returncode == expected_exit, (name, result.returncode, result.stderr)
    return result


def model_case(name, directory, path, facts):
    context_path = directory / 'request.json'
    context_path.write_text(json.dumps(request(path, directory)) + '\n')
    snapshot_path = directory / 'snapshot.json'
    snapshot_path.write_text(json.dumps(snapshot(path, directory, facts)) + '\n')
    result = run([str(ROOT / 'bin/php-semantics'), str(path), '--request-context',
                  str(context_path), '--file-snapshot', str(snapshot_path), '--timeout', '60'],
                 directory, 'model')
    assert result.returncode == 0 and not result.stderr, (name, result.stdout, result.stderr)
    outcome = json.loads(result.stdout)
    assert outcome['status'] == ('php_error' if name in ('empty-trace', 'nul-trace') else 'normal'), outcome
    assert outcome['reason'] is None
    return outcome


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--select', help='comma-separated exact IDs')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    selected = args.select.split(',') if args.select else list(CASES)
    assert selected and len(set(selected)) == len(selected) and all(name in CASES for name in selected)
    out = args.output or Path(tempfile.mkdtemp(prefix='shell-sources-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    before = fingerprint()
    report = {'revision': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD']).decode().strip(),
              'before': before, 'profile': PROFILE, 'selected': selected, 'records': [],
              'passed': False, 'completed': False}
    print(out, flush=True)
    try:
        for name in selected:
            source, expected, facts = CASES[name]
            directory = out / name; directory.mkdir()
            path = directory / 'source.php'; path.write_bytes(source)
            observed = native_case(name, directory, path)
            outcome = model_case(name, directory, path, facts)
            assert base64.b64decode(outcome['stdout'], validate=True) == observed.stdout, (name, outcome)
            assert base64.b64decode(outcome['stderr'], validate=True) == observed.stderr, (
                name, base64.b64decode(outcome['stderr']), observed.stderr)
            assert outcome['exit_status'] == observed.returncode
            report['records'].append({'case': name, 'source_sha256': sha(path),
                                      'status': outcome['status'], 'exit_status': observed.returncode,
                                      'stdout_sha256': hashlib.sha256(observed.stdout).hexdigest(),
                                      'stderr_sha256': hashlib.sha256(observed.stderr).hexdigest()})
            print(name, outcome['status'], flush=True)
        report.update(passed=True, completed=True)
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        report['after'] = fingerprint()
        report['passed'] = report['passed'] and report['before'] == report['after']
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['passed'], flush=True)
    assert report['passed'] and report['completed']


if __name__ == '__main__':
    main()
