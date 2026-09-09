#!/usr/bin/env python3
"""Numeric byte-string classification and conversion against pinned PHP."""
import base64
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PHP = ROOT / '.tools/php/bin/php'
SPECS = [ROOT / f'spec/semantics/{name}.watsup' for name in ['00-numeric', '02-numeric-text']]


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
    rng = random.Random(85012)
    strings = [b'', b' ', b'\t\n\r\v\f', b'+', b'-', b'.', b'+.', b'-.', b'foo',
               b'0', b'-0', b'-0.0', b'-0e99', b'00', b'01', b'1.', b'.1',
               b'1e', b'1e+', b'1e-', b'1e+q', b'1.0e-', b'0x10', b'0b11', b'1_000',
               b'1\0', b'\01', b'1\xff', b'\xa01', b'1 \t', b'1 \tq',
               b'9223372036854775807', b'9223372036854775808', b'-9223372036854775808',
               b'-9223372036854775809', b'9007199254740993.0', b'1e309', b'1e-324',
               b'2.4703282292062327e-324', b'2.4703282292062328e-324', b'4.9406564584124654e-324',
               b'2.2250738585072012e-308', b'1.7976931348623157e308',
               b'1e9999999999999999999', b'1e-9999999999999999999', b'-0e9999999999999999999',
               b'INF', b'NAN', b'Infinity', b'  +000000000000000000000000000001']
    # _is_numeric_string_ex compares the whole C suffix at 19 significant
    # digits; an invalid signed exponent shifts that comparison by one byte.
    boundary_magnitudes = [999999999999999999, 1000000000000000000,
        1922337203685477580, 8922337203685477580, 8999999999999999999,
        9223372036854775807, 9223372036854775808, 9223372036854775809,
        9999999999999999999, 10000000000000000000]
    boundary_suffixes = [b'', b' ', b'\t', b'\n', b'\0', b'\0tail', b'tail',
        b'e', b'e+', b'e-', b'e+q', b'e-q', b'E+', b'E-', b'e+\0', b'e-\0',
        b'e+ ', b'e- ', b'e+0', b'e-0', b'.0']
    strings += [prefix + sign + zeros + str(n).encode() + suffix
        for n in boundary_magnitudes for sign in (b'', b'+', b'-')
        for prefix, zeros in ((b'', b''), (b' \t', b'000')) for suffix in boundary_suffixes]
    for _ in range(300):
        sign = rng.choice(['', '+', '-'])
        digits = ''.join(str(rng.randrange(10)) for _ in range(rng.randrange(1, 40)))
        dot = rng.randrange(len(digits) + 1)
        if rng.choice([True, False]):
            digits = digits[:dot] + '.' + digits[dot:]
        exp = rng.choice(['', 'e', 'E+', 'e-'])
        if exp:
            exp += str(rng.randrange(0, 360))
        prefix = rng.choice(['', ' ', '\t\n'])
        suffix = rng.choice(['', ' ', 'x', '\x00', 'e+', '.5'])
        strings.append((prefix + sign + digits + exp + suffix).encode())
    php = r'''
if (PHP_VERSION !== '8.5.10' || PHP_INT_SIZE !== 8 || PHP_SAPI !== 'cli' || PHP_ZTS) exit(91);
if (bin2hex(pack('E',1.0)) !== '3ff0000000000000') exit(92);
echo json_encode(['version'=>PHP_VERSION,'sapi'=>PHP_SAPI,'int_size'=>PHP_INT_SIZE,
    'zts'=>PHP_ZTS,'extensions'=>get_loaded_extensions(),'precision'=>ini_get('precision'),
    'serialize_precision'=>ini_get('serialize_precision'),
    'opcache.enable_cli'=>ini_get('opcache.enable_cli'),'opcache.jit'=>ini_get('opcache.jit')]), "\n";
$notices=[];
set_error_handler(function($level,$message) use (&$notices) { $notices[]=[$level,$message]; });
foreach (json_decode(stream_get_contents(STDIN),true) as $hex) {
    $s=hex2bin($hex); $notices=[];
    try {
        $v=+$s;
        echo json_encode([is_numeric($s) ? 'FULLNUM':'LEADNUM',gettype($v),
            is_int($v) ? (string)$v : bin2hex(pack('E',$v)),$notices]),"\n";
    } catch (TypeError $e) { echo '["NOTNUMERIC"]',"\n"; }
}
'''
    oracle = subprocess.run([str(PHP), '-n', '-d', 'opcache.enable_cli=0', '-d',
                             'opcache.jit=disable', '-d', 'precision=14', '-d',
                             'serialize_precision=-1', '-r', php], input=json.dumps([s.hex() for s in strings]),
                            capture_output=True, text=True, check=True, timeout=30,
                            env={**os.environ, 'LC_ALL': 'C', 'TZ': 'UTC'})
    assert not oracle.stderr, oracle.stderr
    outputs = [json.loads(line) for line in oracle.stdout.splitlines()]
    profile = outputs.pop(0)
    assert len(outputs) == len(strings)
    clauses = []
    for index, (data, result) in enumerate(zip(strings, outputs)):
        if result[0] == 'NOTNUMERIC':
            expected = 'NOTNUMERIC'
        else:
            value = int(result[2], 16 if result[1] == 'double' else 10)
            expected = f'{result[0]} ({"NFLOAT" if result[1] == "double" else "NINT"} $({value}))'
            notices = result[3]
            assert notices == ([[2, 'A non-numeric value encountered']] if result[0] == 'LEADNUM' else []), (data, result)
        clauses.append(f'dec $tcase{index}() : bool\ndef $tcase{index}() = true\n'
                       f'  -- if $numeric_string({byte_value(data)}) = {expected}\n')
    with tempfile.TemporaryDirectory(prefix='numtext-', dir=ROOT / '.tools') as tmp:
        for start in range(0, len(strings), 60):
            stop = min(start + 60, len(strings))
            fixture = Path(tmp) / f'cases-{start}.watsup'
            fixture.write_text('\n'.join(clauses[start:stop]) + '\ndec $main() : bool\ndef $main() = true\n' +
                               '\n'.join(f'  -- if $tcase{i}()' for i in range(start, stop)) + '\n')
            run = subprocess.run([str(runner), *map(str, SPECS), str(fixture)], cwd=ROOT,
                                 capture_output=True, text=True, timeout=120)
            if run.returncode or run.stdout.strip() != 'true':
                (ROOT / '.tools/numtext-failure.watsup').write_text(fixture.read_text())
                raise SystemExit(f'FAIL cases {start}..{stop}: {run.stdout}{run.stderr}')
    assert before == fingerprints(), 'numeric-text implementation changed during validation'
    report = {'cases': len(strings), 'seed': 85012, 'result': 'pass', 'fingerprints': before,
              'profile': profile, 'environment': {'LC_ALL':'C','TZ':'UTC'},
              'oracle': {'source_base64': base64.b64encode(php.encode()).decode(),
                         'stdin_base64': base64.b64encode((json.dumps([s.hex() for s in strings])).encode()).decode(),
                         'stdout_base64': base64.b64encode(oracle.stdout.encode()).decode(),
                         'stderr_base64': base64.b64encode(oracle.stderr.encode()).decode(),
                         'exit_status': oracle.returncode, 'command': oracle.args},
              'case_manifest_sha256': hashlib.sha256(json.dumps([[s.hex() for s in strings],outputs], sort_keys=True).encode()).hexdigest()}
    (ROOT / 'coverage/semantics/numeric-text.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({key: report[key] for key in ('cases', 'seed', 'result')}))


if __name__ == '__main__':
    main()
