#!/usr/bin/env python3
"""Local NUL include/require failures, with no finite file-provider entry."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import error_handler_run as recorder

ROOT = Path(__file__).resolve().parents[2]
recorder.ROOT = ROOT
CATALOGUE = Path(__file__).with_name('source_nul_cases.json')
b64 = lambda value: base64.b64encode(value).decode()
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fingerprint():
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    paths = [*modules, CATALOGUE, Path(__file__).resolve(), *[ROOT / p for p in (
        'spec/semantics/modules.json', 'bin/php-semantics', '_build/default/adapter/main.exe',
        '.tools/php/bin/php', '.tools/php-file.so', 'tests/semantics/profile.json',
        'tests/semantics/error_handler_run.py', 'spec/schema.json', 'frontend/worker.php',
        'frontend/target.php', 'frontend/FileLexer.php', 'frontend/EvalLexer.php',
        'frontend/wire.php', 'frontend/wire.py')]]
    return {str(p.relative_to(ROOT)): sha(p) for p in paths}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    out = args.output or Path(tempfile.mkdtemp(prefix='source-nul-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    profile = dict(json.loads((ROOT / 'tests/semantics/profile.json').read_bytes()), include_path='.:')
    flags = [piece for key, value in profile.items() for piece in ('-d', key + '=' + value)]
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip()
    report = {'revision': revision, 'profile': profile, 'before': fingerprint(),
              'rows': [], 'source_agreements': 0, 'passed': False}
    print(out, flush=True)
    try:
        for case in json.loads(CATALOGUE.read_bytes()):
            directory = out / case['id']; directory.mkdir()
            source = directory / 'main.php'; source.write_text(case['source'])
            snapshot = directory / 'snapshot.json'
            snapshot.write_text(json.dumps({'version': 1, 'main': b64(bytes(source.resolve())),
                'cwd': b64(bytes(ROOT)), 'include_path': b64(b'.:'), 'entries': []}) + '\n')
            row = {'id': case['id'], 'source_sha256': sha(source), 'passed': False}
            report['rows'].append(row)
            native = recorder.recorded([str(ROOT / '.tools/php/bin/php'), '-n', *flags, str(source)], directory / 'native', 10)
            row['native'] = native
            expected = case['stdout'].replace('{file}', str(source.resolve())).encode()
            assert native['exit'] == case['exit'] and not native['timeout'] and not native['group_after']
            assert (directory / 'native.stdout').read_bytes() == expected
            assert (directory / 'native.stderr').read_bytes() == case['stderr'].encode()
            model = recorder.recorded([str(ROOT / 'bin/php-semantics'), str(source), '--file-snapshot',
                str(snapshot), '--steps', '10000', '--timeout', '45'], directory / 'model', 60)
            row['model'] = model
            outcome = json.loads((directory / 'model.stdout').read_bytes()); row['outcome'] = outcome
            assert model['exit'] == 0 and not model['timeout'] and not model['group_after']
            assert (directory / 'model.stderr').read_bytes() == b''
            assert outcome['status'] == 'normal' and outcome['reason'] is None
            assert outcome['exit_status'] == case['exit']
            assert outcome['frontend'] == 'accepted' and outcome['checked'] == 'program'
            assert base64.b64decode(outcome['stdout'], validate=True) == expected
            assert base64.b64decode(outcome['stderr'], validate=True) == case['stderr'].encode()
            row['passed'] = True; report['source_agreements'] += 1
        report['passed'] = True
    finally:
        report['inputs_stable'] = report['before'] == fingerprint()
        report['head_stable'] = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip()
        report['passed'] = report['passed'] and report['inputs_stable'] and report['head_stable']
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed']


if __name__ == '__main__':
    main()
