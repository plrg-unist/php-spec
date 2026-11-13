#!/usr/bin/env python3
"""Pure SL boundary checks for the guaranteed-overflow rounding shortcut."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SPEC = ROOT / 'spec/semantics/00-numeric.watsup'
RUNNER = HERE / '_build/default/numeric_runner.exe'

# Exact pre-shortcut body: only its function name changes.
OLD_ROUND = '''dec $old_float_round(nat, nat, nat) : nat
 def $old_float_round(n_s, 0, n_d) = $(n_s * 9223372036854775808) -- if $(n_d > 0)
 def $old_float_round(n_s, n_n, n_d) = $(n_s * 9223372036854775808 + $fcap(n_bits))
   -- if $(n_n > 0)
   -- if $(n_d > 0)
   -- if i = $fminexp($fratio_exp(n_n, n_d))
   -- if (n_1, n_2) = $nscale(n_n, n_d, $(52 - i))
   -- if n_q = $nround(n_1, n_2)
   -- if n_bits = $(n_q + (i + 1022) * 4503599627370496)
'''


def vectors():
    groups = {}
    for denominator in (1, 3):
        rows = []
        for sign in (0, 1):
            for offset in (-1, 0, 1):
                rows.append((f'threshold-{denominator}-{sign}-{offset}', sign,
                             f'$({denominator} * $npow2(1024) + ({offset}))',
                             str(denominator), sign * 2**63 + 0x7ff0000000000000))
        groups[f'threshold-denominator-{denominator}'] = rows
    rows = []
    for sign in (0, 1):
        for offset in (-1, 0, 1):
            magnitude = 0x7fefffffffffffff if offset == -1 else 0x7ff0000000000000
            rows.append((f'overflow-midpoint-{sign}-{offset}', sign,
                         f'$($npow2(1024) - $npow2(970) + ({offset}))', '1',
                         sign * 2**63 + magnitude))
        rows.append((f'max-finite-{sign}', sign,
                     '$($npow2(1024) - $npow2(971))', '1',
                     sign * 2**63 + 0x7fefffffffffffff))
    groups['old-general-overflow-boundary'] = rows
    groups['huge-finite-ratio'] = [
        (f'huge-finite-{sign}', sign, '$(3 * $npow2(2048))',
         '$(2 * $npow2(2048))', sign * 2**63 + 0x3ff8000000000000)
        for sign in (0, 1)
    ]
    groups['zero-normal-ties'] = [
        (f'{label}-{sign}', sign, numerator, denominator, sign * 2**63 + magnitude)
        for sign in (0, 1)
        for label, numerator, denominator, magnitude in [
            ('zero', '0', '3', 0),
            ('one', '1', '1', 0x3ff0000000000000),
            ('normal-tie-even-down', '9007199254740993', '9007199254740992', 0x3ff0000000000000),
            ('normal-tie-even-up', '9007199254740995', '9007199254740992', 0x3ff0000000000002),
        ]
    ]
    groups['subnormal-minnormal-ties'] = [
        (f'{label}-{sign}', sign, numerator, denominator, sign * 2**63 + magnitude)
        for sign in (0, 1)
        for label, numerator, denominator, magnitude in [
            ('half-minsub', '1', '$npow2(1075)', 0),
            ('one-and-half-minsub', '3', '$npow2(1075)', 2),
            ('minnormal-midpoint', '9007199254740991', '$npow2(1075)', 0x0010000000000000),
            ('max-subnormal', '4503599627370495', '$npow2(1074)', 0x000fffffffffffff),
        ]
    ]
    return groups


def run(output):
    output = Path(output)
    output.mkdir()
    watched = [SPEC, Path(__file__), HERE / 'numeric_runner.ml', RUNNER]
    hashes = lambda: {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    before = hashes()
    environment = {**os.environ, 'LC_ALL': 'C', 'TZ': 'UTC'}
    environment.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    records = []
    groups = vectors()
    (output / 'vectors.json').write_text(json.dumps(groups, indent=2) + '\n')
    for name, rows in groups.items():
        directory = output / name
        directory.mkdir()
        checks = []
        for index, (_, sign, numerator, denominator, expected) in enumerate(rows):
            checks.extend([
                f'n_result_{index} = $float_round({sign}, {numerator}, {denominator})',
                f'n_result_{index} = $old_float_round({sign}, {numerator}, {denominator})',
                f'n_result_{index} = {expected}',
            ])
        fixture = directory / 'test.watsup'
        fixture.write_text(OLD_ROUND + '\ndec $main() : bool\ndef $main() = true\n' +
                           ''.join('  -- if ' + check + '\n' for check in checks))
        command = [str(RUNNER), '--sl', str(SPEC), str(fixture)]
        (directory / 'command.json').write_text(json.dumps(command) + '\n')
        start = time.monotonic()
        expired = False
        try:
            result = subprocess.run(command, cwd=ROOT, env=environment, capture_output=True, timeout=300)
            stdout, stderr, code = result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired as error:
            stdout, stderr, code, expired = error.stdout or b'', error.stderr or b'', None, True
        (directory / 'stdout').write_bytes(stdout)
        (directory / 'stderr').write_bytes(stderr)
        records.append(dict(id=name, cases=len(rows), bindings=len(rows), equalities=2 * len(rows),
                            elapsed_seconds=time.monotonic() - start, exit=code, timeout=expired,
                            pass_all=not expired and code == 0 and stdout.strip() == b'true' and not stderr))
        if not records[-1]['pass_all']:
            break
    after = hashes()
    report = dict(tested_revision=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                  mode='kernel-only SL_mode', module_count=1, source_credit=0, native_executions=0,
                  per_fixture_cap=300, records=records, inputs_before=before, inputs_after=after,
                  stable=before == after, pass_all=before == after and len(records) == len(groups)
                  and all(record['pass_all'] for record in records))
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['pass_all'], output / 'report.json'
    print(json.dumps({key: value for key, value in report.items() if not key.startswith('inputs_')}))
    return report


if __name__ == '__main__':
    run(Path(tempfile.mkdtemp(prefix='float-round-overflow-', dir=ROOT / '.tools')) / 'run')
