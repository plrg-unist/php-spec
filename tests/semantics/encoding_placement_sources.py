#!/usr/bin/env python3
"""Native-first disabled-multibyte encoding placement in source units."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from error_handler_run import recorded

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).with_name('encoding_placement')
ORACLE = 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
HASHES = {
    'late.php': '86b170d1b2737035d6595b12ec93d807271a7c5ce7bbd583439eab50fe8c09e9',
    'namespace.php': '36b91de0c8fbfc72a618a67d2084cba9772c0c23576f334f22805abd0214c7f2',
    'include-main.php': '1ac4d59061a7e87065a25c8aaa2dad7d5ef89ec11a2e90c936033a6a957fa529',
    'child.php': '98b6c3055857e9dd80cb22e9f4c4a426659b2e5d0000f26f26f920872c2e14aa',
    'eval.php': '1d594c8b42b074c85da6d5490b3fd9ffa4ea44af49bc3430d89d7b96f7b6e39c',
}
MESSAGE = b'declare(encoding=...) ignored because Zend multibyte feature is turned off by settings'
FATAL = b'Encoding declaration pragma must be the very first statement in the script'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
b64 = lambda data: base64.b64encode(data).decode()


def expected(name):
    path = SOURCE / (name + '.php')
    if name in ('late', 'namespace'):
        line = b'3'; filename = bytes(path)
        warning = b'Warning: ' + MESSAGE + b' in ' + filename + b' on line ' + line + b'\n'
        fatal = b'Fatal error: ' + FATAL + b' in ' + filename + b' on line ' + line + b'\nStack trace:\n#0 {main}\n'
        return 255, b'', warning + fatal, 'static_rejection'
    if name == 'include-main':
        warning = b'Warning: ' + MESSAGE + b' in ' + bytes(SOURCE / 'child.php') + b' on line 2\n'
        return 0, b'M|C|R|', warning, 'normal'
    warning = b'Warning: ' + MESSAGE + b' in ' + bytes(path) + b"(3) : eval()'d code on line 1\n"
    return 0, b'B|E|A|', warning, 'normal'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--select', help='comma-separated case names')
    args = parser.parse_args()
    names = args.select.split(',') if args.select else ['late', 'namespace', 'include-main', 'eval']
    assert names and len(set(names)) == len(names) and set(names) <= {'late', 'namespace', 'include-main', 'eval'}
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    assert {name: sha(SOURCE / name) for name in HASHES} == HASHES
    assert sha(ROOT / '.tools/php/bin/php') == ORACLE
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text()); profile['include_path'] = '.:'
    flags = [x for key, value in profile.items() for x in ('-d', key + '=' + value)]
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    watched = [Path(__file__), ROOT / 'spec/semantics/92-strict-compiler.watsup',
               ROOT / 'spec/semantics/modules.json', ROOT / 'bin/php-semantics',
               ROOT / 'frontend/worker.php', ROOT / '.tools/php-file.so',
               ROOT / '_build/default/adapter/main.exe', ROOT / '.tools/php/bin/php',
               ROOT / 'tests/semantics/profile.json', *(SOURCE / name for name in HASHES)]
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
            if name == 'include-main':
                child = SOURCE / 'child.php'
                snapshot = {'version': 2, 'main': b64(bytes(path)), 'cwd': b64(bytes(ROOT)),
                    'include_path': b64(b'.:'), 'chdir_entries': [], 'entries': [
                    {'caller': b64(bytes(path)), 'requested': b64(bytes(child)),
                     'cwd': b64(bytes(ROOT)), 'include_path': b64(b'.:'), 'status': 'opened',
                     'resolved': b64(bytes(child)), 'opened': b64(bytes(child)),
                     'source': b64(child.read_bytes())}]}
                (case / 'snapshot.json').write_text(json.dumps(snapshot) + '\n')
                extra = ['--file-snapshot', str(case / 'snapshot.json')]
            model = recorded([str(ROOT / 'bin/php-semantics'), str(path), '--startup-ini',
                              str(case / 'startup.json'), *extra, '--steps', '100000', '--timeout', '120'],
                             case / 'model', 140)
            row['model'] = model
            outcome = json.loads((case / 'model.stdout').read_bytes())
            row['status'] = outcome.get('status'); row['reason'] = outcome.get('reason')
            row['passed'] = (model['exit'] == 0 and not model['timeout'] and not model['group_after']
                and (case / 'model.stderr').read_bytes() == b'' and outcome['frontend'] == 'accepted'
                and outcome['checked'] == 'program' and outcome['status'] == status
                and outcome['reason'] is None and outcome['exit_status'] == exit_status
                and outcome['stdout'] == b64(stdout) and outcome['stderr'] == b64(stderr))
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
