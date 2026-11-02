#!/usr/bin/env python3
"""Checked file-mode HALT offsets and raw shebang admission guards."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from error_handler_run import recorded
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).with_name('halt_preamble')
CASES = {
    'shebang-main': ('9b351c3a304ea0ffd0c6faeb0c777cfdd3e43970ce7be52979ca443933a148b1', 'ENCODEDPROGRAM', 100),
    'child-halt-min': ('2706db2eea7305e36b6ed651c19f745857a5d87504325525ce1b01e3a835e63f', 'ENCODEDPROGRAM', 163),
    'plain-main': ('9a91a20cd67e2204cc27814ef472c28d802844f7fbfbc750cbd8800c265bd17d', 'PROGRAM', 81),
    'bom-main': ('c6078933b9440fcf57510f991616ba384f281572f0fd2290937c580fa312d78a', 'PROGRAM', 84),
}

sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
b64 = lambda data: base64.b64encode(data).decode()


def main():
    out = Path(sys.argv[1]).resolve(); out.mkdir(parents=True, exist_ok=False)
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    flags = [piece for key, value in profile.items() for piece in ('-d', key + '=' + value)]
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    watched = [Path(__file__), ROOT / 'spec/semantics/46-source-compiler.watsup',
        ROOT / 'spec/semantics/modules.json', ROOT / 'frontend/worker.php',
        ROOT / '.tools/php-file.so', ROOT / '.tools/php/bin/php',
        ROOT / '_build/default/adapter/main.exe',
        ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
        ROOT / 'tests/semantics/profile.json',
        *(SOURCES / (name + '.php') for name in CASES)]
    inputs = {str(path.relative_to(ROOT)): sha(path) for path in watched}
    report = {'head': head, 'inputs': inputs, 'profile': profile,
              'environment': {'LC_ALL': 'C', 'TZ': 'UTC'}, 'premises': 0, 'passed': False}
    try:
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *flags, '-d',
            'extension=' + str(ROOT / '.tools/php-file.so'),
            str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        fixtures = {}
        try:
            for name, (digest, kind, offset) in CASES.items():
                path = SOURCES / (name + '.php')
                assert sha(path) == digest
                encoded = b64(path.read_bytes()); identity = b64(bytes(path))
                parsed = frontend.request({'op': 'parse-file', 'id': '0', 'mode': 'file',
                    'profile': 'cli-raw-85', 'source': encoded, 'requested': identity,
                    'resolved': identity, 'opened': identity})
                assert parsed['accepted'] and parsed['source'] == encoded
                checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
                assert checked['ast']['program'][-1]['node'] == 'Stmt_HaltCompiler'
                fixtures[name] = checked['fixture']
                assert fixtures[name].startswith('(' + kind + ' ')
        finally:
            adapter.close(); frontend.close()
        main_fixture = fixtures['shebang-main']
        prefix = '(ENCODEDPROGRAM ("cmF3") ("cmF3") ("") ('
        assert main_fixture.startswith(prefix)
        changed_source = main_fixture.replace('(ENCODEDPROGRAM ("cmF3")',
                                              '(ENCODEDPROGRAM ("bm9ucmF3")', 1)
        changed_bom = main_fixture.replace('("cmF3") ("cmF3") ("")',
                                           '("cmF3") ("cmF3") ("77u/")', 1)
        checks = []
        for name, (_, _, offset) in CASES.items():
            tag = name.replace('-', '_')
            checks += [f'W_{tag} = {fixtures[name]}', f'$pphalt_offset(W_{tag}) = ({offset})']
        checks += [f'$pphalt_offset({changed_source}) = eps',
                   f'$pphalt_offset({changed_bom}) = eps']
        fixture = out / 'state.watsup'
        fixture.write_text('var W : program\ndec $main() : bool\ndef $main() = true\n' +
                           ''.join('  -- if ' + check + '\n' for check in checks))
        report['premises'] = len(checks); report['fixture_sha256'] = sha(fixture)
        modules = json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())
        process = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                            *[str(ROOT / name) for name in modules], str(fixture)], out / 'state', 150)
        report['process'] = process
        assert process['exit'] == 0 and not process['timeout'] and not process['group_after']
        assert (out / 'state.stdout').read_bytes() == b'true\n'
        assert (out / 'state.stderr').read_bytes() == b''
        report['passed'] = True
    finally:
        report['inputs_stable'] = inputs == {str(path.relative_to(ROOT)): sha(path) for path in watched}
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['passed'] = report['passed'] and report['inputs_stable'] and report['head_stable']
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed']


if __name__ == '__main__':
    main()
