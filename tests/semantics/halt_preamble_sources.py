#!/usr/bin/env python3
"""Native-first HALT offsets in checked shebang files and included units."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from error_handler_run import recorded

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).with_name('halt_preamble')
ORACLE = 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
HASHES = {
    'shebang-main.php': '9b351c3a304ea0ffd0c6faeb0c777cfdd3e43970ce7be52979ca443933a148b1',
    'plain-main.php': '9a91a20cd67e2204cc27814ef472c28d802844f7fbfbc750cbd8800c265bd17d',
    'bom-main.php': 'c6078933b9440fcf57510f991616ba384f281572f0fd2290937c580fa312d78a',
    'shebang-lookup.php': '5e6177cbb7209a22fcdb9ffbe0a486daaf9be2ebb629509ccfdad860b94e3764',
    'include-lookup-main.php': '159b4ab6684430da3b1bd08b77c73baddd835c2b0a995beb84e7811837f65490',
    'child-lookup.php': '6796c5a055f4639fd658ef733f3033e1d9a70c9e65c3737c3c8560acee3b15e2',
    'include-main-min.php': '2c602085be5e584dd0a25f86445b542290266f78a9e61a8c7438d07ae5ea8e53',
    'child-halt-min.php': '2706db2eea7305e36b6ed651c19f745857a5d87504325525ce1b01e3a835e63f',
}
EXPECTED = {'shebang-main': b'S|3|100|',
            'plain-main': b'P|2|81|',
            'bom-main': b'\xef\xbb\xbfB|2|84|',
            'include-main-min': b'M|C|1|3|163|R7|',
            'shebang-lookup': b'H|160|1|160|',
            'include-lookup-main': b'M|0|C|1|162|R162|0|'}

sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
b64 = lambda data: base64.b64encode(data).decode()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--select', help='comma-separated case names')
    args = parser.parse_args()
    selected = args.select.split(',') if args.select else list(EXPECTED)
    assert selected and len(set(selected)) == len(selected) and set(selected) <= EXPECTED.keys()
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    assert {name: sha(SOURCE / name) for name in HASHES} == HASHES
    assert sha(ROOT / '.tools/php/bin/php') == ORACLE
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    profile['include_path'] = '.:'
    flags = [x for key, value in profile.items() for x in ('-d', key + '=' + value)]
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    watched = [Path(__file__), ROOT / 'spec/semantics/46-source-compiler.watsup',
               ROOT / 'spec/semantics/modules.json', ROOT / 'bin/php-semantics',
               ROOT / 'frontend/worker.php', ROOT / '.tools/php-file.so',
               ROOT / '_build/default/adapter/main.exe', ROOT / '.tools/php/bin/php',
               ROOT / 'tests/semantics/profile.json', *(SOURCE / name for name in HASHES)]
    inputs = {str(path.relative_to(ROOT)): sha(path) for path in watched}
    report = {'head': head, 'inputs': inputs, 'profile': profile, 'oracle_sha256': ORACLE,
              'environment': {'LC_ALL': 'C', 'TZ': 'UTC'}, 'selected': selected,
              'records': [], 'agreements': 0, 'passed': False}
    try:
        for name in selected:
            expected = EXPECTED[name]; path = SOURCE / (name + '.php')
            directory = out / name; directory.mkdir()
            row = {'id': name, 'source_sha256': sha(path)}; report['records'].append(row)
            native = recorded([str(ROOT / '.tools/php/bin/php'), '-n', *flags, str(path)], directory / 'native', 15)
            row['native'] = native; row['native_stdout_base64'] = b64((directory / 'native.stdout').read_bytes())
            assert native['exit'] == 0 and not native['timeout'] and not native['group_after']
            assert (directory / 'native.stdout').read_bytes() == expected and (directory / 'native.stderr').read_bytes() == b''
            startup = {'error_reporting': b64(b'30719'), 'include_path': b64(b'.:')}
            (directory / 'startup.json').write_text(json.dumps(startup) + '\n')
            model_args = []
            if name in ('include-main-min', 'include-lookup-main'):
                child = SOURCE / ('child-halt-min.php' if name == 'include-main-min' else 'child-lookup.php')
                snapshot = {'version': 2, 'main': b64(bytes(path)), 'cwd': b64(bytes(ROOT)),
                    'include_path': b64(b'.:'), 'chdir_entries': [], 'entries': [
                    {'caller': b64(bytes(path)), 'requested': b64(bytes(child)),
                     'cwd': b64(bytes(ROOT)), 'include_path': b64(b'.:'), 'status': 'opened',
                     'resolved': b64(bytes(child)), 'opened': b64(bytes(child)),
                     'source': b64(child.read_bytes())}]}
                (directory / 'snapshot.json').write_text(json.dumps(snapshot) + '\n')
                model_args = ['--file-snapshot', str(directory / 'snapshot.json')]
            model = recorded([str(ROOT / 'bin/php-semantics'), str(path), '--startup-ini',
                              str(directory / 'startup.json'), *model_args, '--steps', '100000', '--timeout', '120'],
                             directory / 'model', 140)
            row['model'] = model
            outcome = json.loads((directory / 'model.stdout').read_bytes())
            row['status'] = outcome.get('status'); row['reason'] = outcome.get('reason')
            assert model['exit'] == 0 and not model['timeout'] and not model['group_after']
            assert (directory / 'model.stderr').read_bytes() == b''
            assert outcome['frontend'] == 'accepted' and outcome['checked'] == 'program'
            assert outcome['status'] == 'normal' and outcome['reason'] is None
            assert outcome['exit_status'] == 0 and outcome['stdout'] == b64(expected) and outcome['stderr'] == b64(b'')
            row['passed'] = True; report['agreements'] += 1
            print(name, 'pass', flush=True)
        report['passed'] = True
    finally:
        report['inputs_stable'] = inputs == {str(path.relative_to(ROOT)): sha(path) for path in watched}
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['passed'] = report['passed'] and report['inputs_stable'] and report['head_stable']
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed']


if __name__ == '__main__':
    main()
