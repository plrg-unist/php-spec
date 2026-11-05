#!/usr/bin/env python3
"""Single attributed constants compile metadata without executing arguments."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from error_handler_run import recorded
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).with_name('single_attributed_constant')
b64 = lambda data: base64.b64encode(data).decode()
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--select', help='comma-separated case names')
    args = parser.parse_args(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    cases = json.loads((SOURCE / 'cases.json').read_text())
    names = args.select.split(',') if args.select else list(cases)
    assert names and len(set(names)) == len(names) and set(names) <= set(cases)
    hashes = json.loads((SOURCE / 'hashes.json').read_text())
    assert hashes == {name: sha(SOURCE / name) for name in hashes}
    assert sha(types.PHP) == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = [Path(__file__), SOURCE / 'cases.json', SOURCE / 'hashes.json',
        *(SOURCE / name for name in hashes), *modules, *(ROOT / path for path in (
            'spec/semantics/modules.json', 'spec/php.watsup', 'spec/schema.json', 'adapter/main.ml',
            'frontend/worker.php', 'frontend/RejectedHeaderParser.php', 'frontend/EvalLexer.php',
            'frontend/FileLexer.php', 'bin/php-semantics', '.tools/php/bin/php', '.tools/php-file.so',
            '_build/default/adapter/main.exe', 'tests/semantics/profile.json',
            'tests/semantics/static_types.py', 'tests/semantics/error_handler_run.py',
            'vendor/php-parser/lib/PhpParser/ParserAbstract.php', 'vendor/php-parser/lib/PhpParser/Parser/Php8.php'))]
    before = {str(path.relative_to(ROOT)): sha(path) for path in watched}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    profile = {**types.PROFILE, 'include_path': '.:'}
    flags = [flag for key, value in profile.items() for flag in ('-d', key + '=' + value)]
    report = {'head': head, 'inputs': before, 'profile': profile,
        'environment': {'LC_ALL': 'C', 'TZ': 'UTC'}, 'selected': names, 'records': [],
        'agreements': 0, 'refusal_controls': 0, 'passed': False}
    try:
        for name in names:
            case = cases[name]; path = SOURCE / case['source']; target = out / name; target.mkdir()
            row = {'id': name, 'source_sha256': sha(path)}; report['records'].append(row)
            native = recorded([str(types.PHP), '-n', *flags, str(path)], target / 'native', 15)
            row['native'] = native
            stdout = (target / 'native.stdout').read_bytes(); stderr = (target / 'native.stderr').read_bytes()
            assert not native['timeout'] and not native['group_after']
            assert stdout == case['stdout'].encode()
            if 'message' in case:
                assert native['exit'] == 255
                filename = (bytes(path) + b"(4) : eval()'d code" if case['mode'] == 'eval' else
                    bytes(SOURCE / case['unit']) if case['mode'] == 'file' else bytes(path))
                warning = b'declare(encoding=...) ignored because Zend multibyte feature is turned off by settings'
                prefix = b''.join(b'Warning: ' + warning + b' in ' + filename + b' on line '
                    + str(line).encode() + b'\n' for line in case.get('warning_lines', []))
                prefix += (b'Fatal error: ' + case['message'].encode() + b' in ' + filename
                    + b' on line ' + str(case['line']).encode() + b'\nStack trace:\n')
                assert stderr.startswith(prefix)
            else:
                assert native['exit'] == 0 and not stderr
            startup = {'error_reporting': b64(b'30719'), 'include_path': b64(b'.:')}
            (target / 'startup.json').write_text(json.dumps(startup) + '\n')
            extra = []
            if case['mode'] == 'file':
                child = SOURCE / case['unit']
                snapshot = {'version': 2, 'main': b64(bytes(path)), 'cwd': b64(bytes(ROOT)),
                    'include_path': b64(b'.:'), 'chdir_entries': [], 'entries': [
                    {'caller': b64(bytes(path)), 'requested': b64(bytes(child)), 'cwd': b64(bytes(ROOT)),
                     'include_path': b64(b'.:'), 'status': 'opened', 'resolved': b64(bytes(child)),
                     'opened': b64(bytes(child)), 'source': b64(child.read_bytes())}]}
                (target / 'snapshot.json').write_text(json.dumps(snapshot) + '\n')
                extra = ['--file-snapshot', str(target / 'snapshot.json')]
            model = recorded([str(ROOT / 'bin/php-semantics'), str(path), '--startup-ini',
                str(target / 'startup.json'), *extra, '--steps', '100000', '--timeout', '120'], target / 'model', 140)
            row['model'] = model
            outcome = json.loads((target / 'model.stdout').read_bytes()); row['status'] = outcome.get('status')
            assert not model['timeout'] and not model['group_after'] and not (target / 'model.stderr').read_bytes()
            assert outcome.get('frontend') == 'accepted' and outcome.get('checked') == 'program'
            if case['status'] == 'unsupported':
                row['passed'] = (model['exit'] == 1 and outcome['status'] == 'unsupported'
                    and outcome['reason'] == case.get('unsupported_reason', 'ordinary statement compilation'))
                report['refusal_controls'] += int(row['passed'])
            else:
                row['passed'] = (model['exit'] == 0 and outcome['status'] == case['status']
                    and outcome['reason'] is None and outcome['exit_status'] == native['exit']
                    and outcome['stdout'] == b64(stdout) and outcome['stderr'] == b64(stderr))
                if 'message' in case:
                    row['passed'] = row['passed'] and outcome['diagnostic'] == {
                        'class': case.get('diagnostic_class', 'CompileError'), 'message': b64(case['message'].encode()), 'line': case['line']}
                report['agreements'] += int(row['passed'])
            print(name, 'pass' if row['passed'] else 'fail', flush=True)
            assert row['passed'], outcome
        report['passed'] = len(report['records']) == len(names) and all(row['passed'] for row in report['records'])
    finally:
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(path.relative_to(ROOT)): sha(path) for path in watched}
        report['passed'] = report['passed'] and report['head_stable'] and report['inputs_stable']
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed']


if __name__ == '__main__': main()
