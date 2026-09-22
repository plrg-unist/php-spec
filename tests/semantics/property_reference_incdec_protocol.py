#!/usr/bin/env python3
"""Paused typed-property increment/decrement restores the owned cell on errors."""
from pathlib import Path
import base64
import hashlib
import json
import re
import subprocess
import tempfile

import static_types as types
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
ROWS = {row['id']: row for row in json.loads(
    (ROOT / 'tests/semantics/property_references_cases.json').read_text())}
SELECTION = ('incdec-direct-max-post-runtime', 'incdec-reference-max-post-runtime')


def bytes_fixture(value):
    return '([' + ','.join(map(str, value)) + '])'


def run():
    before = types.syntax_validation.implementation_fingerprint()
    out = Path(tempfile.mkdtemp(prefix='property-reference-incdec-', dir=ROOT / '.tools'))
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = [*modules, Path(__file__), ROOT / 'tests/semantics/property_references_cases.json',
               ROOT / 'tests/semantics/_build/default/numeric_runner.exe']
    direct = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'),
                       str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    records = []
    try:
        for name in SELECTION:
            row = ROWS[name]
            directory = out / name
            directory.mkdir()
            source = directory / 'source.php'
            source.write_bytes(row['source'].encode())
            assert hashlib.sha256(source.read_bytes()).hexdigest() == row['source_sha256']
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted'], (name, parsed)
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'], (name, checked)
            match = re.search(r'Uncaught TypeError: (.*?) in \{FILE\}:(\d+)', row['stderr'])
            assert match, name
            maximum = 'max' in name or 'first-source' in name
            old_value = '9223372036854775807' if maximum else '$(-9223372036854775808)'
            filename = base64.b64encode(str(source).encode()).decode()
            checks = [f'S_initial = $php_run({checked["fixture"]}, 0, {json.dumps(filename)})',
                      'S_initial.COMPLETION = BUDGET', 'S = S_initial[.COMPLETION = NORMAL]',
                      'S_final = $drive(S, 10000)',
                      'S_final.COMPLETION = THROWN "TypeError" '
                      + bytes_fixture(match[1].encode()) + ' ' + match[2],
                      'S_final.TODO = eps', 'S_final.HELD = eps',
                      '$heap_valid($heap_graph(S_final))']
            if 'reference' in name:
                checks.extend(['S_final.PROPREFS = [ppropref]', 'ppropref.CELL = n_cell',
                               f'S_final.STORE[n_cell] = DEFINED (PINT {old_value})',
                               '$proprefs_valid(S_final)'])
            for budget in (0, 11, 37):
                checks.extend([f'S_{budget} = $drive(S, {budget})',
                               f'S_{budget}.COMPLETION = BUDGET',
                               f'$drive(S_{budget}[.COMPLETION = NORMAL], 10000) = S_final',
                               f'$heap_valid($heap_graph(S_{budget}))'])
            fixture = directory / 'fixture.watsup'
            fixture.write_text('dec $main() : bool\ndef $main() = true\n' +
                               ''.join('  -- if ' + check + '\n' for check in checks))
            result = subprocess.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                     *map(str, modules), str(fixture)], capture_output=True,
                                    text=True, timeout=120)
            (directory / 'runner.stdout').write_text(result.stdout)
            (directory / 'runner.stderr').write_text(result.stderr)
            assert result.returncode == 0 and result.stdout == 'true\n' and not result.stderr, (name, result.stderr)
            records.append({'id': name, 'assertions': len(checks), 'pass': True})
            print(name, len(checks), flush=True)
    finally:
        frontend.close()
        adapter.close()
    assert before == types.syntax_validation.implementation_fingerprint(), 'implementation changed during run'
    assert all(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == value for path, value in direct.items())
    report = {'result': 'pass', 'cases': len(records), 'assertions': sum(r['assertions'] for r in records),
              'fingerprint': before, 'direct_inputs': direct, 'raw': str(out), 'records': records}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, report['result'])


if __name__ == '__main__':
    run()
