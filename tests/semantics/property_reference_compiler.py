#!/usr/bin/env python3
"""Checked source modes and priority for public property references."""
from pathlib import Path
import base64
import json
import subprocess
import tempfile
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CASES = json.loads((ROOT / 'tests/semantics/property_reference_compiler_cases.json').read_text())


def run():
    out = Path(tempfile.mkdtemp(prefix='property-reference-compiler-', dir=ROOT / '.tools'))
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'),
                       str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        modules = [str(ROOT / p) for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
        count = 0
        for row in CASES:
            name = row['name']
            source = row['source'].encode()
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source).decode()})
            assert parsed['accepted'], (name, parsed)
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'], (name, checked)
            original = out / f'{name}.php'
            original.write_bytes(source)
            filename = '[' + ','.join(map(str, str(original).encode())) + ']'
            premises = [f'n_file* = {filename}', f'P = $ppstart(137, {checked["fixture"]}, n_file*)']
            if 'static_message' in row:
                premises.append('P.COMPLETION = PPCABRUPT (STATICERROR '
                                + json.dumps(row['static_message']) + ' ' + str(row['static_line']) + ')')
            else:
                premises.extend(['P.COMPLETION = PPCNORMAL',
                                 f'({row["access_path"]}, {row["access_mode"]}) <- P.ACCESS'])
            fixture = out / f'{name}.watsup'
            fixture.write_text('dec $main() : bool\ndef $main() = true\n' +
                               ''.join('  -- if ' + line + '\n' for line in premises))
            result = subprocess.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                     *modules, str(fixture)], capture_output=True, text=True, timeout=120)
            (out / f'{name}.stdout').write_text(result.stdout)
            (out / f'{name}.stderr').write_text(result.stderr)
            assert result.returncode == 0 and result.stdout == 'true\n' and not result.stderr, (name, result.stderr)
            count += len(premises)
        print(f'PASS property reference compiler: {len(CASES)} sources, {count} assertions', out)
    finally:
        frontend.close()
        adapter.close()


if __name__ == '__main__':
    run()
