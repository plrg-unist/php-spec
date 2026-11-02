#!/usr/bin/env python3
"""Exact file/eval preamble sources through the checked dynamic source service."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from error_handler_run import recorded

ROOT = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).with_name('source_preamble')
ORACLE = 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
HASHES = {
    'main-shebang.php': '96db8e76dc3495b320ca1acd85265ee34d2f61b745fd3f1ca8f390b7a8dd5fcc',
    'main-bom.php': 'a2f0f5c766af05ad23cadb2cc64e484ca6dcaadfd54b5a793a6b40004e4ec5aa',
    'ticks-shebang.php': '089da1d53e4679bae25ceccd7ab7dc2e07c663f4fb67825576b5b3d37a0c9b1d',
    'ticks-bom.php': 'a055d1f5bd87d7f3a627620956d7d9c40f2f5daccfdfd6de01560d6d37425122',
    'eval-preamble.php': '6314300c180508de6da1a20dae8ce50fc1c07cde72dcef2dbc30b3fd16930521',
    'include-main.php': 'd4466be1f9389b6a0e7712ee7f8c70fe9c34a6847a30f2a22a7b48910136b4ad',
    'child-shebang.php': '2d7f6ff645d8ca0d79f424720657f9c1cea343668dedd4425a1ad9473dbc4a5c',
    'child-bom.php': '7526828f775843311712a136decb7668b30e39c7d6e3d561996dce8904efc4f0',
    'tick-include/main.php': '4e098e46dab8ffe1e75f4f471e9d8b8ef7a9829f77b5ccb6cff38d4484c51a1c',
    'tick-include/child.php': '0520b1c90e5832a3ef5f20189136566a7cc0f8599aa58721eb8c274e056231ce',
}
EXPECTED = {
    'main-shebang': b'M2|',
    'main-bom': b'\xef\xbb\xbfM1|',
    'ticks-shebang': b'T|A|T|B|T|',
    'ticks-bom': b'\xef\xbb\xbfT|A|T|B|T|',
    'eval-preamble': b'P1:syntax error, unexpected token "echo"|S2|',
    'include-main': b'M|S2:1|R5|\xef\xbb\xbfC1:1|B7|',
    'tick-include/main': b'M|T|C|T|R5|',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def b64(value):
    return base64.b64encode(value).decode()


def snapshot(name, source):
    children = {'include-main': ['child-shebang.php', 'child-bom.php'],
                'tick-include/main': ['child.php']}.get(name, [])
    if not children:
        return None
    return {'version': 2, 'main': b64(bytes(source)), 'cwd': b64(bytes(ROOT)),
            'include_path': b64(b'.:'), 'chdir_entries': [], 'entries': [
                {'caller': b64(bytes(source)), 'requested': b64(bytes(source.parent / child)),
                 'cwd': b64(bytes(ROOT)), 'include_path': b64(b'.:'),
                 'status': 'opened', 'resolved': b64(bytes(source.parent / child)),
                 'opened': b64(bytes(source.parent / child)),
                 'source': b64((source.parent / child).read_bytes())} for child in children]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['native', 'model'], required=True)
    parser.add_argument('--select', help='comma-separated exact case names')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    selected = args.select.split(',') if args.select else list(EXPECTED)
    assert selected and len(set(selected)) == len(selected) and set(selected) <= EXPECTED.keys()
    assert sha(ROOT / '.tools/php/bin/php') == ORACLE
    assert {name: sha(SOURCES / name) for name in HASHES} == HASHES
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=True)
    report_path = out / (args.phase + '-report.json')
    assert not report_path.exists()
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    profile['include_path'] = '.:'
    flags = [piece for key, value in profile.items() for piece in ('-d', key + '=' + value)]
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    watched = [ROOT / 'spec/semantics/393-ticks.watsup', ROOT / 'spec/semantics/modules.json',
               ROOT / 'bin/php-semantics', ROOT / 'frontend/worker.php',
               ROOT / '.tools/php-file.so', ROOT / '_build/default/adapter/main.exe',
               ROOT / 'tests/semantics/profile.json',
               Path(__file__), *(SOURCES / name for name in HASHES)]
    inputs = {str(path.relative_to(ROOT)): sha(path) for path in watched}
    report = {'phase': args.phase, 'revision': revision, 'inputs': inputs, 'oracle_sha256': ORACLE,
              'profile': profile, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC'},
              'selected': selected, 'records': [], 'agreements': 0, 'passed': False}
    try:
        for name in selected:
            source = SOURCES / (name + '.php')
            directory = out / name.replace('/', '-'); directory.mkdir(exist_ok=True)
            row = {'id': name, 'source_sha256': sha(source), 'expected_stdout_base64': b64(EXPECTED[name])}
            report['records'].append(row)
            startup = {'error_reporting': b64(b'30719'), 'include_path': b64(b'.:')}
            (directory / 'startup.json').write_text(json.dumps(startup) + '\n')
            facts = snapshot(name, source)
            if facts is not None:
                (directory / 'snapshot.json').write_text(json.dumps(facts) + '\n')
            if args.phase == 'native':
                command = [str(ROOT / '.tools/php/bin/php'), '-n', *flags, str(source)]
                process = recorded(command, directory / 'native', 20)
                row['native'] = process
                assert process['exit'] == 0 and not process['timeout'] and not process['group_after']
                assert (directory / 'native.stdout').read_bytes() == EXPECTED[name]
                assert (directory / 'native.stderr').read_bytes() == b''
            else:
                native = json.loads((out / 'native-report.json').read_bytes())
                assert native['passed'] and native['inputs'] == inputs and native['selected'] == selected
                model_args = ['--file-snapshot', str(directory / 'snapshot.json')] if facts else []
                command = [str(ROOT / 'bin/php-semantics'), str(source), '--startup-ini',
                           str(directory / 'startup.json'), *model_args, '--steps', '100000', '--timeout', '120']
                process = recorded(command, directory / 'model', 140)
                row['model'] = process
                outcome = json.loads((directory / 'model.stdout').read_bytes())
                row['status'] = outcome['status']; row['reason'] = outcome['reason']
                assert process['exit'] == 0 and not process['timeout'] and not process['group_after']
                assert (directory / 'model.stderr').read_bytes() == b''
                assert outcome['frontend'] == 'accepted' and outcome['checked'] == 'program'
                assert outcome['status'] == 'normal' and outcome['reason'] is None
                assert outcome['exit_status'] == 0 and outcome['stdout'] == b64(EXPECTED[name])
                assert outcome['stderr'] == b64(b'')
                report['agreements'] += 1
            row['passed'] = True
            print(name, 'pass', flush=True)
        report['passed'] = True
    finally:
        report['inputs_stable'] = inputs == {str(path.relative_to(ROOT)): sha(path) for path in watched}
        report['head_stable'] = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['passed'] = report['passed'] and report['inputs_stable'] and report['head_stable']
        report_path.write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed']


if __name__ == '__main__':
    main()
