#!/usr/bin/env python3
"""Checked public method declarations, inheritance and lexical scope."""
from pathlib import Path
import base64
import hashlib
import json
import subprocess
import tempfile

import static_types as types
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CASES = json.loads((ROOT / 'tests/semantics/method_compiler_cases.json').read_text())


def run():
    before = types.syntax_validation.implementation_fingerprint()
    out = Path(tempfile.mkdtemp(prefix='method-compiler-', dir=ROOT / '.tools'))
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = [*modules, Path(__file__), ROOT / 'tests/semantics/method_compiler_cases.json']
    direct = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'),
                       str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    records = []
    try:
        for row in CASES:
            source = row['source'].encode()
            assert hashlib.sha256(source).hexdigest() == row['source_sha256'], row['id']
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source).decode()})
            assert parsed['accepted'], row['id']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'], row['id']
            path = out / (row['id'] + '.php')
            path.write_bytes(source)
            filename = '[' + ','.join(map(str, str(path).encode())) + ']'
            premises = [f'P = $ppstart(141, {checked["fixture"]}, {filename})']
            if row['compiler'] == 'static':
                premises.append('P.COMPLETION = PPCABRUPT (STATICBYTES '
                                + '$ptascii(' + json.dumps(row['static_message']) + ') '
                                + str(row['static_line']) + ')')
            else:
                premises.append('P.COMPLETION = PPCNORMAL')
            if row['group'] == 'compiler-lexical':
                operand = '[PCINDEX 0, PCFIELD 5, PCINDEX 0, PCFIELD 6, PCINDEX 0, PCFIELD 0, PCINDEX 0]'
                premises.extend(['P.CLASSES = [pclassdesc]',
                                 'pclassdesc.METHODS = [pmethoddesc]',
                                 '$code_expression(pmethoddesc.FUNCTION.CODE.EXPRESSIONS, '
                                 + operand + ') = ((1, '
                                 + ('false' if row['constant'] is None else 'true') + '))'])
                if row['constant'] is not None:
                    premises.extend(['$ppconstants(P) = PPCCONSTANTS (pcpath_constant, pvalue_constant)*',
                                     '$ppconstant_at((pcpath_constant, pvalue_constant)*, '
                                     + operand + ') = (PSTRING $ptascii('
                                     + json.dumps(row['constant']) + '))'])
            if row['group'] == 'compiler-fold':
                premises.append('$ppconstants(P) = PPCCONSTANTS (pcpath_constant, pvalue_constant)*')
                for path_constant, value in zip(row['constant_paths'], row['constants']):
                    premises.append('$ppconstant_at((pcpath_constant, pvalue_constant)*, '
                                    + path_constant + ') = (PSTRING $ptascii('
                                    + json.dumps(value) + '))')
            fixture = out / (row['id'] + '.watsup')
            fixture.write_text('dec $main() : bool\ndef $main() = true\n'
                               + ''.join('  -- if ' + clause + '\n' for clause in premises))
            result = subprocess.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                     *map(str, modules), str(fixture)], capture_output=True,
                                    text=True, timeout=120)
            (out / (row['id'] + '.stdout')).write_text(result.stdout)
            (out / (row['id'] + '.stderr')).write_text(result.stderr)
            assert result.returncode == 0 and result.stdout == 'true\n', (row['id'], result.stderr)
            assert 'failed' not in result.stderr and 'error' not in result.stderr, (row['id'], result.stderr)
            records.append({'id': row['id'], 'assertions': len(premises), 'pass': True})
            print(row['id'], len(premises), flush=True)
    finally:
        frontend.close()
        adapter.close()
    assert before == types.syntax_validation.implementation_fingerprint()
    assert all(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest
               for name, digest in direct.items())
    report = {'result': 'pass', 'sources': len(records),
              'assertions': sum(row['assertions'] for row in records),
              'fingerprint': before, 'direct_inputs': direct, 'raw': str(out),
              'records': records}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, report['result'])


if __name__ == '__main__':
    run()
