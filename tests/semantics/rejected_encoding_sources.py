#!/usr/bin/env python3
"""Original rejected units preserve parser warnings, exceptions and once state."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from error_handler_run import recorded

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).with_name('rejected_encoding')
CASES = json.loads((SOURCE / 'cases.json').read_text())
HASHES = json.loads((SOURCE / 'hashes.json').read_text())
ORACLE = 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
MESSAGE = b'declare(encoding=...) ignored because Zend multibyte feature is turned off by settings'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
b64 = lambda data: base64.b64encode(data).decode()


def expected(name, source=SOURCE, cases=CASES):
    case = cases[name]
    path = source / name / 'main.php'
    filename = (bytes(source / name / 'unit.php') if case['mode'] == 'file' else
                bytes(path) + b"(4) : eval()'d code")
    caught = (case['kind'].encode() + b'|' + str(case['line']).encode() + b'|'
              + case['message'].encode() + b'|' + filename + b'|F|')
    stdout = b'M|' + caught + (b'1|' + caught if name == 'include-once-retry' else b'') + b'A|'
    stderr = b''.join(b'Warning: ' + MESSAGE + b' in ' + filename + b' on line '
                      + str(line).encode() + b'\n' for line in case['warning_lines'])
    return stdout, stderr


def main(source=SOURCE, extra_inputs=()):
    cases = json.loads((source / 'cases.json').read_text())
    hashes = json.loads((source / 'hashes.json').read_text())
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--select', help='comma-separated case names')
    args = parser.parse_args(); names = args.select.split(',') if args.select else list(cases)
    assert names and len(set(names)) == len(names) and set(names) <= set(cases)
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    assert {name: sha(source / name) for name in hashes} == hashes
    assert sha(ROOT / '.tools/php/bin/php') == ORACLE
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text()); profile['include_path'] = '.:'
    flags = [flag for key, value in profile.items() for flag in ('-d', key + '=' + value)]
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = [Path(__file__), *extra_inputs, source / 'hashes.json', *(source / name for name in hashes), *modules,
        *(ROOT / path for path in ('spec/semantics/modules.json', 'spec/schema.json', 'adapter/main.ml',
          'bin/php-semantics', 'frontend/worker.php', 'frontend/RejectedHeaderParser.php', 'frontend/FileLexer.php',
          'frontend/EvalLexer.php', '.tools/php-file.so', '_build/default/adapter/main.exe', '.tools/php/bin/php',
          'tests/semantics/profile.json', 'tests/semantics/error_handler_run.py'))]
    inputs = {str(path.relative_to(ROOT)): sha(path) for path in watched}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': inputs, 'profile': profile, 'oracle_sha256': ORACLE,
        'environment': {'LC_ALL': 'C', 'TZ': 'UTC'}, 'selected': names, 'records': [],
        'agreements': 0, 'refusal_controls': 0, 'passed': False}
    try:
        for name in names:
            case = cases[name]; path = source / name / 'main.php'
            target = out / name; target.mkdir(); stdout, stderr = expected(name, source, cases)
            row = {'id': name, 'source_sha256': sha(path)}; report['records'].append(row)
            row['native'] = recorded([str(ROOT / '.tools/php/bin/php'), '-n', *flags, str(path)], target / 'native', 15)
            assert row['native']['exit'] == 0 and not row['native']['timeout'] and not row['native']['group_after']
            assert (target / 'native.stdout').read_bytes() == stdout and (target / 'native.stderr').read_bytes() == stderr
            (target / 'startup.json').write_text(json.dumps({'error_reporting': b64(b'30719'), 'include_path': b64(b'.:')}) + '\n')
            extra = []
            if case['mode'] == 'file':
                child = source / name / 'unit.php'
                snapshot = {'version': 2, 'main': b64(bytes(path)), 'cwd': b64(bytes(ROOT)),
                    'include_path': b64(b'.:'), 'chdir_entries': [], 'entries': [
                    {'caller': b64(bytes(path)), 'requested': b64(bytes(child)), 'cwd': b64(bytes(ROOT)),
                     'include_path': b64(b'.:'), 'status': 'opened', 'resolved': b64(bytes(child)),
                     'opened': b64(bytes(child)), 'source': b64(child.read_bytes())}]}
                (target / 'snapshot.json').write_text(json.dumps(snapshot) + '\n')
                extra = ['--file-snapshot', str(target / 'snapshot.json')]
            row['model'] = recorded([str(ROOT / 'bin/php-semantics'), str(path), '--startup-ini',
                str(target / 'startup.json'), *extra, '--steps', '100000', '--timeout', '120'], target / 'model', 140)
            outcome = json.loads((target / 'model.stdout').read_bytes()); row['status'] = outcome.get('status')
            assert not row['model']['timeout'] and not row['model']['group_after'] and not (target / 'model.stderr').read_bytes()
            if case['status'] == 'unsupported':
                row['passed'] = (row['model']['exit'] == 1 and outcome['status'] == 'unsupported'
                    and outcome['reason'] == 'eval parser service stderr outside supported encoding declarations')
                report['refusal_controls'] += int(row['passed'])
            else:
                row['passed'] = (row['model']['exit'] == 0 and outcome.get('frontend') == 'accepted'
                    and outcome.get('checked') == 'program' and outcome['status'] == 'normal'
                    and outcome['reason'] is None and outcome['exit_status'] == 0
                    and outcome['stdout'] == b64(stdout) and outcome['stderr'] == b64(stderr))
                report['agreements'] += int(row['passed'])
            print(name, 'pass' if row['passed'] else 'fail', flush=True)
            if not row['passed']: break
        report['passed'] = len(report['records']) == len(names) and all(row['passed'] for row in report['records'])
    finally:
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = inputs == {str(path.relative_to(ROOT)): sha(path) for path in watched}
        report['passed'] = report['passed'] and report['head_stable'] and report['inputs_stable']
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed']


if __name__ == '__main__':
    main()
