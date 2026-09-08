#!/usr/bin/env python3
"""Exact numeric output bytes under configured PHP precision."""
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import struct
import time
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PHP = ROOT / '.tools/php/bin/php'
SPECS = [ROOT / f'spec/semantics/{name}.watsup' for name in
         ['00-numeric', '01-integer', '02-numeric-text', '03-numeric-format']]


def byte_value(data):
    return '[' + ', '.join(map(str, data)) + ']' if data else 'eps'


def main():
    subprocess.run([str(ROOT / 'scripts/opam-exec.sh'), 'dune', 'build', '--root',
                    str(HERE), 'numeric_runner.exe'], cwd=ROOT, check=True)
    runner = HERE / '_build/default/numeric_runner.exe'
    watched = SPECS + [PHP, Path(__file__), HERE / 'numeric_runner.ml', runner]
    def fingerprints():
        return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}
    before = fingerprints()
    started = time.monotonic()
    rng = random.Random(85013)
    bits = [0, 2**63, 1, 2**52 - 1, 2**52, 0x3ff0000000000000,
            0x3ff0000000000001, 0x3fefffffffffffff, 0x7fefffffffffffff,
            0x7ff0000000000000, 0xfff0000000000000, 0x7ff8000000000000,
            0x3f1a36e2eb1c432d, 0x3f50624dd2f1a9fc, 0x4415af1d78b58c40]
    for exponent in [1, 2, 3, 255, 512, 1021, 1022, 1023, 1024, 1025, 1055, 2045, 2046]:
        bits += [(exponent << 52) + delta for delta in [-1, 0, 1]]
    precisions = [-1, 0, 1, 2, 3, 14, 17, 30]
    cases = [[f'{b:016x}', str(p)] for b in bits for p in precisions]
    cases += [[f'{((exponent << 52) + delta):016x}', '-1']
              for exponent in range(1, 2047) for delta in [-1, 0, 1]]
    # Decimal decade boundaries test candidate selection before carry normalization.
    for exponent in range(-323, 309):
        center = int.from_bytes(struct.pack('>d', float(f'1e{exponent}')), 'big')
        cases += [[f'{center+delta:016x}', '-1'] for delta in [-1, 0, 1]]
    cases += [[f'{rng.getrandbits(64):016x}', str(p)] for p in [-1, 14, 17] for _ in range(100)]
    cases += [[f'{b:016x}', str(p)] for b in bits[:15] for p in [100, 2**32-1, 2**32, 2**32+2]]
    php = r'''
if (PHP_VERSION !== '8.5.10' || PHP_INT_SIZE !== 8 || PHP_SAPI !== 'cli' || PHP_ZTS) exit(91);
if (bin2hex(pack('E',unpack('E',hex2bin('8000000000000000'))[1])) !== '8000000000000000') exit(92);
echo json_encode(['version'=>PHP_VERSION,'sapi'=>PHP_SAPI,'int_size'=>PHP_INT_SIZE,
    'zts'=>PHP_ZTS,'extensions'=>get_loaded_extensions(),
    'serialize_precision'=>ini_get('serialize_precision'),
    'opcache.enable_cli'=>ini_get('opcache.enable_cli'),'opcache.jit'=>ini_get('opcache.jit')]), "\n";
$notices=[];
set_error_handler(function($level,$message) use (&$notices) { $notices[]=[$level,$message]; });
foreach (json_decode(stream_get_contents(STDIN),true) as [$hex,$precision]) {
    ini_set('precision',$precision);
    $f=unpack('E',hex2bin($hex))[1]; $notices=[];
    $s=(string)$f;
    echo json_encode([bin2hex($s),$notices]),"\n";
}
'''
    oracle = subprocess.run([str(PHP), '-n', '-d', 'opcache.enable_cli=0', '-d',
                             'opcache.jit=disable', '-d', 'serialize_precision=-1', '-r', php],
                            input=json.dumps(cases), capture_output=True, text=True, check=True,
                            timeout=30, env={**os.environ, 'LC_ALL': 'C', 'TZ': 'UTC'})
    assert not oracle.stderr, oracle.stderr
    outputs = [json.loads(line) for line in oracle.stdout.splitlines()]
    profile = outputs.pop(0)
    assert len(outputs) == len(cases)
    clauses = []
    for index, ((hex_bits, precision), (output, notices)) in enumerate(zip(cases, outputs)):
        assert notices in [[], [[2, 'unexpected NAN value was coerced to string']]], notices
        expected = f'({byte_value(bytes.fromhex(output))}, {str(bool(notices)).lower()})'
        clauses.append(f'dec $fcase{index}() : bool\ndef $fcase{index}() = true\n'
                       f'  -- if $number_text(NFLOAT {int(hex_bits,16)}, $({precision})) = {expected}\n')
    with tempfile.TemporaryDirectory(prefix='numformat-', dir=ROOT / '.tools') as tmp:
        for start in range(0, len(cases), 40):
            stop = min(start + 40, len(cases))
            fixture = Path(tmp) / f'cases-{start}.watsup'
            fixture.write_text('\n'.join(clauses[start:stop]) + '\ndec $main() : bool\ndef $main() = true\n' +
                               '\n'.join(f'  -- if $fcase{i}()' for i in range(start, stop)) + '\n')
            run = subprocess.run([str(runner), *map(str, SPECS), str(fixture)], cwd=ROOT,
                                 capture_output=True, text=True, timeout=120)
            if run.returncode or run.stdout.strip() != 'true':
                (ROOT / '.tools/numformat-failure.watsup').write_text(fixture.read_text())
                raise SystemExit(f'FAIL cases {start}..{stop}: {run.stdout}{run.stderr}')
    assert before == fingerprints(), 'numeric-format implementation changed during validation'
    report = {'cases': len(cases), 'seed': 85013, 'result': 'pass', 'fingerprints': before,
              'elapsed_seconds': round(time.monotonic()-started, 3),
              'profile': profile, 'precision_profiles': precisions+[100,2**32-1,2**32,2**32+2],
              'environment': {'LC_ALL':'C','TZ':'UTC'},
              'case_manifest_sha256': hashlib.sha256(json.dumps([cases,outputs], sort_keys=True).encode()).hexdigest()}
    (ROOT / 'coverage/semantics/numeric-format.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
