#!/usr/bin/env python3
"""Original multiline encoding headers, reduction order and dynamic identities."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from error_handler_run import recorded

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).with_name('encoding_headers')
HASHES = json.loads((SOURCE / 'hashes.json').read_text())
ORACLE = 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
MESSAGE = b'declare(encoding=...) ignored because Zend multibyte feature is turned off by settings'
FATAL = b'Encoding declaration pragma must be the very first statement in the script'
FOO = b"Unsupported declare 'Foo'"
CASES = {
    'same-ast-a': (b'B|', [2], None), 'same-ast-b': (b'B|', [3], None),
    'late-lines': (b'', [6], (FATAL, 4)), 'mixed-lines': (b'OK|', [5], None),
    'repeated-lines': (b'OK|', [5, 5], None),
    'strict-block-lines': (b'', [5], (b'strict_types declaration must not use block mode', 3)),
    'header-comment': (b'B|', [4], None), 'nested-body': (b'', [4, 7], (FATAL, 6)),
    'nested-header': (b'', [7, 9], (b'declare(Foo) value must be a literal', 3)),
    'nested-header-repeat': (b'', [4, 6, 6], (b'declare(Foo) value must be a literal', 3)),
    'heredoc': (b'H|', [5], None), 'parenthesized-literal': (b'P|', [4], None),
    'terminator-newline': (b'N|', [2], None), 'crlf': (b'C|', [4], None),
    'comment-brace': (b'B|', [2], None), 'comment-colon': (b'B|', [2], None),
    'include-normal': (b'M|C|7|A|', [5], None), 'include-late': (b'M|', [5], (FATAL, 4)),
    'once-normal': (b'M|C|7|R|1|C|7|A|', [5], None),
    'eval-normal': (b'M|E|8|A|', [4, 4], None), 'eval-late': (b'M|', [4], (FATAL, 3)),
}
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
b64 = lambda data: base64.b64encode(data).decode()


def expected(name):
    stdout, lines, fatal = CASES[name]
    path = bytes(SOURCE / (name + '.php'))
    if name in ('include-normal', 'once-normal'):
        path = bytes(SOURCE / 'normal-child.php')
    elif name == 'include-late':
        path = bytes(SOURCE / 'late-child.php')
    elif name.startswith('eval-'):
        path += b"(6) : eval()'d code"
    def warning(message, line):
        return b'Warning: ' + message + b' in ' + path + b' on line ' + str(line).encode() + b'\n'
    stderr = b''.join(warning(MESSAGE, line) for line in lines)
    if name in ('mixed-lines', 'include-normal', 'once-normal'):
        stderr += warning(FOO, 3)
    if name == 'once-normal':
        stderr *= 2
    if fatal is not None:
        message, line = fatal
        stderr += b'Fatal error: ' + message + b' in ' + path + b' on line ' + str(line).encode() + b'\nStack trace:\n#0 {main}\n'
    return (255 if fatal else 0), stdout, stderr, ('static_rejection' if fatal else 'normal')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--select', help='comma-separated case names')
    args = parser.parse_args(); names = args.select.split(',') if args.select else list(CASES)
    assert names and len(set(names)) == len(names) and set(names) <= set(CASES)
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    assert {name: sha(SOURCE / name) for name in HASHES} == HASHES
    assert sha(ROOT / '.tools/php/bin/php') == ORACLE
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text()); profile['include_path'] = '.:'
    flags = [x for key, value in profile.items() for x in ('-d', key + '=' + value)]
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    watched = [Path(__file__), SOURCE / 'hashes.json', *(SOURCE / name for name in HASHES),
        *(ROOT / path for path in ['spec/semantics/92-strict-compiler.watsup',
          'spec/semantics/93-strict-declarations.watsup', 'spec/semantics/194-compiler-preflight.watsup',
          'spec/semantics/modules.json', 'spec/php.watsup', 'spec/schema.json', 'bin/php-semantics',
          'frontend/worker.php', 'frontend/FileLexer.php', 'frontend/EvalLexer.php', '.tools/php-file.so',
          '_build/default/adapter/main.exe', '.tools/php/bin/php', 'tests/semantics/profile.json',
          'tests/semantics/error_handler_run.py'])]
    inputs = {str(path.relative_to(ROOT)): sha(path) for path in watched}
    report = {'head': head, 'inputs': inputs, 'profile': profile, 'oracle_sha256': ORACLE,
        'environment': {'LC_ALL': 'C', 'TZ': 'UTC'}, 'selected': names,
        'records': [], 'agreements': 0, 'passed': False}
    try:
        for name in names:
            path = SOURCE / (name + '.php'); case = out / name; case.mkdir()
            exit_status, stdout, stderr, status = expected(name)
            row = {'id': name, 'source_sha256': sha(path)}; report['records'].append(row)
            native = recorded([str(ROOT / '.tools/php/bin/php'), '-n', *flags, str(path)], case / 'native', 15)
            row['native'] = native
            assert native['exit'] == exit_status and not native['timeout'] and not native['group_after']
            assert (case / 'native.stdout').read_bytes() == stdout and (case / 'native.stderr').read_bytes() == stderr
            (case / 'startup.json').write_text(json.dumps({'error_reporting': b64(b'30719'), 'include_path': b64(b'.:')}) + '\n')
            extra = []
            if name.startswith('include-') or name == 'once-normal':
                child = SOURCE / ('late-child.php' if name == 'include-late' else 'normal-child.php')
                snapshot = {'version': 2, 'main': b64(bytes(path)), 'cwd': b64(bytes(ROOT)),
                    'include_path': b64(b'.:'), 'chdir_entries': [], 'entries': [
                    {'caller': b64(bytes(path)), 'requested': b64(bytes(child)),
                     'cwd': b64(bytes(ROOT)), 'include_path': b64(b'.:'), 'status': 'opened',
                     'resolved': b64(bytes(child)), 'opened': b64(bytes(child)), 'source': b64(child.read_bytes())}]}
                (case / 'snapshot.json').write_text(json.dumps(snapshot) + '\n')
                extra = ['--file-snapshot', str(case / 'snapshot.json')]
            model = recorded([str(ROOT / 'bin/php-semantics'), str(path), '--startup-ini',
                str(case / 'startup.json'), *extra, '--steps', '100000', '--timeout', '120'], case / 'model', 140)
            row['model'] = model
            outcome = json.loads((case / 'model.stdout').read_bytes())
            row['status'] = outcome.get('status'); row['reason'] = outcome.get('reason')
            row['passed'] = (model['exit'] == 0 and not model['timeout'] and not model['group_after']
                and not (case / 'model.stderr').read_bytes() and outcome['frontend'] == 'accepted'
                and outcome['checked'] == 'program' and outcome['status'] == status and outcome['reason'] is None
                and outcome['exit_status'] == exit_status and outcome['stdout'] == b64(stdout) and outcome['stderr'] == b64(stderr))
            report['agreements'] += int(row['passed'])
            print(name, 'pass' if row['passed'] else 'fail', flush=True)
        report['passed'] = report['agreements'] == len(names)
    finally:
        report['inputs_stable'] = inputs == {str(path.relative_to(ROOT)): sha(path) for path in watched}
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['passed'] = report['passed'] and report['inputs_stable'] and report['head_stable']
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed']


if __name__ == '__main__':
    main()
