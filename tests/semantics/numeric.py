#!/usr/bin/env python3
"""Bit-exact tests of pure SpecTec arithmetic against the pinned PHP oracle.

pack/unpack and gettype are test-only observation instrumentation. They are not
semantic intrinsics and cannot be called by the specification.
"""
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PHP = ROOT / '.tools/php/bin/php'
SPEC = ROOT / 'spec/semantics/00-numeric.watsup'
HERE = Path(__file__).resolve().parent


def number(value):
    kind, payload = value
    return f'({"NINT" if kind == "i" else "NFLOAT"} $({payload}))'


def main():
    subprocess.run([str(ROOT / 'scripts/opam-exec.sh'), 'dune', 'build',
                    '--root', str(HERE), 'numeric_runner.exe'], cwd=ROOT, check=True)
    watched = [PHP, SPEC, HERE / 'numeric.py', HERE / 'numeric_runner.ml',
               HERE / '_build/default/numeric_runner.exe']
    before = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in watched}
    rng = random.Random(85010)
    integers = [0, 1, -1, 2**53 - 1, 2**53 + 1, 2**63 - 1, -2**63,
                2**62 + 513, 2**62 + 1025, -2**62 - 513]
    floats = [0, 2**63, 1, 2**52 - 1, 2**52, 0x3ff0000000000000,
              0x3ff0000000000001, 0x3fefffffffffffff,
              0x7fefffffffffffff, 0x7ff0000000000000,
              0xfff0000000000000, 0x7ff8000000000000,
              0x3fe0000000000000, 0xbff0000000000000,
              0x7ff8000000000042, 0xfff8000000000065,
              0x7ff0000000000001, 0xfff0000000000001]
    cases = []
    for op in ['add', 'sub', 'mul', 'div']:
        for a in integers:
            for b in integers:
                cases.append((op, ('i', a), ('i', b)))
        for a in floats:
            for b in floats:
                cases.append((op, ('f', a), ('f', b)))
        for _ in range(50):
            cases.append((op, ('f', rng.getrandbits(64)), ('f', rng.getrandbits(64))))
        for a in integers:
            cases.append((op, ('i', a), ('f', rng.choice(floats))))
            cases.append((op, ('f', rng.choice(floats)), ('i', a)))
    # Decimal strings prevent JSON float/int coercions before instrumentation.
    encoded = [[op, [a[0], str(a[1])], [b[0], str(b[1])]] for op, a, b in cases]
    php = r'''
if (PHP_VERSION !== '8.5.10' || PHP_INT_SIZE !== 8 || PHP_SAPI !== 'cli' || PHP_ZTS) exit(91);
// Check the observation bridge against raw bits and fixed known values.
foreach (['0000000000000001','8000000000000000','3ff0000000000000',
          '7ff0000000000000','fff0000000000000','7ff8000000000042',
          '7ff0000000000001'] as $bits) {
    if (bin2hex(pack('E', unpack('E', hex2bin($bits))[1])) !== $bits) exit(92);
}
if (bin2hex(pack('E',1.0)) !== '3ff0000000000000' ||
    bin2hex(pack('E',-0.0)) !== '8000000000000000') exit(93);
echo json_encode(['version'=>PHP_VERSION,'sapi'=>PHP_SAPI,'int_size'=>PHP_INT_SIZE,
    'zts'=>PHP_ZTS,'extensions'=>get_loaded_extensions(),
    'precision'=>ini_get('precision'),'serialize_precision'=>ini_get('serialize_precision'),
    'opcache.enable_cli'=>ini_get('opcache.enable_cli'),'opcache.jit'=>ini_get('opcache.jit')]), "\n";
$cases = json_decode(stream_get_contents(STDIN), true);
foreach ($cases as [$op,$av,$bv]) {
    // Float payloads arrive as hexadecimal in this observation-only bridge.
    $a = $av[0] === 'i' ? (int)$av[1] : unpack('E', hex2bin($av[1]))[1];
    $b = $bv[0] === 'i' ? (int)$bv[1] : unpack('E', hex2bin($bv[1]))[1];
    try {
        $v = match ($op) {'add'=>$a+$b,'sub'=>$a-$b,'mul'=>$a*$b,'div'=>$a/$b};
        echo json_encode([gettype($v), is_int($v) ? (string)$v : bin2hex(pack('E',$v))]), "\n";
    } catch (DivisionByZeroError $e) { echo '["zero"]', "\n"; }
}
'''
    for row in encoded:
        for value in row[1:]:
            if value[0] == 'f':
                value[1] = f'{int(value[1]):016x}'
    oracle = subprocess.run([str(PHP), '-n', '-d', 'opcache.enable_cli=0',
                             '-d', 'opcache.jit=disable', '-d', 'precision=14',
                             '-d', 'serialize_precision=-1', '-r', php],
                            input=json.dumps(encoded), text=True, capture_output=True,
                            timeout=30, check=True, env={**os.environ, 'LC_ALL': 'C', 'TZ': 'UTC'})
    assert not oracle.stderr, oracle.stderr
    outputs = [json.loads(line) for line in oracle.stdout.splitlines()]
    profile = outputs.pop(0)
    assert len(outputs) == len(cases)
    # Independent mathematical expectations exercise ties directly, without
    # depending on an oracle expression that already rounded its operands.
    symbolic = [
        ('$float_round(0, 1, $npow2(1075))', '0'),
        ('$float_round(1, 1, $npow2(1075))', '9223372036854775808'),
        ('$float_round(0, 3, $npow2(1075))', '2'),
        ('$float_round(0, 9007199254740991, $npow2(1075))', '4503599627370496'),
        ('$float_round(0, 9007199254740993, 9007199254740992)', '4607182418800017408'),
        ('$float_round(0, 9007199254740995, 9007199254740992)', '4607182418800017410'),
        ('$float_round(0, $nabs($($npow2(1024) - $npow2(970))), 1)', '9218868437227405312'),
        ('$float_round(0, $nabs($($npow2(1024) - $npow2(970) - 1)), 1)', '9218868437227405311'),
    ]
    declarations = []
    calls = []
    for index, ((op, a, b), result) in enumerate(zip(cases, outputs)):
        if result[0] == 'zero':
            expected = 'DIVZERO'
        else:
            value = int(result[1], 16 if result[0] == 'double' else 10)
            expected = number(('f' if result[0] == 'double' else 'i', value))
            if op == 'div':
                expected = f'NUM {expected}'
        declarations.append(f'dec $case{index}() : bool\ndef $case{index}() = true\n'
                            f'  -- if $num_{op}({number(a)}, {number(b)}) = {expected}\n')
        calls.append(f'  -- if $case{index}()')
    for index, (expression, expected) in enumerate(symbolic, len(cases)):
        declarations.append(f'dec $case{index}() : bool\ndef $case{index}() = true\n'
                            f'  -- if {expression} = {expected}\n')
        calls.append(f'  -- if $case{index}()')
    # Execute in bounded batches so an assertion points to a small case group.
    with tempfile.TemporaryDirectory(prefix='numeric-', dir=ROOT / '.tools') as tmp:
        for start in range(0, len(declarations), 80):
            stop = min(start + 80, len(declarations))
            fixture = Path(tmp) / f'cases-{start}.watsup'
            fixture.write_text('\n'.join(declarations[start:stop]) +
                               '\ndec $main() : bool\ndef $main() = true\n' +
                               '\n'.join(calls[start:stop]) + '\n')
            run = subprocess.run([str(HERE / '_build/default/numeric_runner.exe'),
                                  str(SPEC), str(fixture)], cwd=ROOT, text=True,
                                 capture_output=True, timeout=120)
            if run.returncode or run.stdout.strip() != 'true':
                print(f'FAIL cases {start}..{stop}: {run.stdout}{run.stderr}')
                # Preserve exact fixture for diagnosis; it is not a passing report.
                (ROOT / '.tools/numeric-failure.watsup').write_text(fixture.read_text())
                raise SystemExit(1)
    after = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in watched}
    assert before == after, 'numeric implementation changed during validation'
    report = {'cases': len(cases), 'symbolic': len(symbolic), 'seed': 85010, 'result': 'pass',
                      'target': 'PHP 8.5.10 CLI NTS signed64 x86_64',
                      'fingerprints': before, 'profile': profile,
                      'case_manifest_sha256': hashlib.sha256(json.dumps(
                          [encoded, outputs, symbolic], sort_keys=True).encode()).hexdigest()}
    output = ROOT / 'coverage/semantics/numeric.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
