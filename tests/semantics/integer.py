#!/usr/bin/env python3
"""Integer helpers and pending float-cast notices; no source-evaluator claims."""
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
SPECS = [ROOT / f'spec/semantics/{name}.watsup' for name in ['00-numeric', '01-integer']]


def main():
    subprocess.run([str(ROOT / 'scripts/opam-exec.sh'), 'dune', 'build', '--root',
                    str(HERE), 'numeric_runner.exe'], cwd=ROOT, check=True)
    runner = HERE / '_build/default/numeric_runner.exe'
    watched = SPECS + [PHP, Path(__file__), HERE / 'numeric_runner.ml', runner]
    def fingerprints():
        return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}
    before = fingerprints()
    rng = random.Random(85011)
    ints = [0, 1, -1, 2**63 - 1, -2**63, 2**53 + 1, -2**53 - 1, 64, 63, 65, -64]
    cases = [[op, str(a), str(b)] for op in ['and', 'or', 'xor', 'mod', 'shl', 'shr']
             for a in ints for b in ints]
    cases += [['not', str(a), '0'] for a in ints]
    cases += [[rng.choice(['and', 'or', 'xor', 'mod']), str(rng.randrange(-2**63, 2**63)),
               str(rng.randrange(-2**63, 2**63))] for _ in range(100)]
    floats = [0, 2**63, 1, 0x3ff8000000000000, 0xbff8000000000000,
              0x43dfffffffffffff, 0x43e0000000000000, 0xc3e0000000000000,
              0xc3e0000000000001, 0x43f0000000000000, 0x7fefffffffffffff,
              0x7ff0000000000000, 0xfff0000000000000, 0x7ff8000000000000]
    floats += [rng.getrandbits(64) for _ in range(80)]
    cases += [[op, f'{bits:016x}', '0'] for op in ['cast', 'implicit'] for bits in floats]
    php = r'''
if (PHP_VERSION !== '8.5.10' || PHP_INT_SIZE !== 8 || PHP_SAPI !== 'cli' || PHP_ZTS) exit(91);
if (unpack('E',hex2bin('3ff0000000000000'))[1] !== 1.0 ||
    bin2hex(pack('E',unpack('E',hex2bin('8000000000000000'))[1])) !== '8000000000000000') exit(92);
echo json_encode(['version'=>PHP_VERSION,'sapi'=>PHP_SAPI,'int_size'=>PHP_INT_SIZE,
    'zts'=>PHP_ZTS,'extensions'=>get_loaded_extensions(),'precision'=>ini_get('precision'),
    'serialize_precision'=>ini_get('serialize_precision'),
    'opcache.enable_cli'=>ini_get('opcache.enable_cli'),'opcache.jit'=>ini_get('opcache.jit')]), "\n";
$notices=[];
set_error_handler(function($level,$message) use (&$notices) {
    $kind = $level === E_WARNING && str_contains($message,'not representable as an int') ? 'RANGEWARNING'
          : ($level === E_DEPRECATED && str_contains($message,'loses precision') ? 'PRECISIONLOSS' : 'UNEXPECTED');
    $notices[]=$kind;
});
foreach (json_decode(stream_get_contents(STDIN),true) as [$op,$av,$bv]) {
    $notices=[];
    $a=($op==='cast'||$op==='implicit') ? unpack('E',hex2bin($av))[1] : (int)$av;
    $b=(int)$bv;
    try {
        $v=match($op) {'not'=>~$a,'and'=>$a&$b,'or'=>$a|$b,'xor'=>$a^$b,'mod'=>$a%$b,
            'shl'=>$a<<$b,'shr'=>$a>>$b,'cast'=>(int)$a,'implicit'=>$a|0};
        echo json_encode([(string)$v,$notices]),"\n";
    } catch (DivisionByZeroError $e) { echo '["INTZERO"]',"\n"; }
      catch (ArithmeticError $e) { echo '["NEGSHIFT"]',"\n"; }
}
'''
    oracle = subprocess.run([str(PHP), '-n', '-d', 'opcache.enable_cli=0', '-d',
                             'opcache.jit=disable', '-d', 'precision=14', '-d',
                             'serialize_precision=-1', '-r', php], input=json.dumps(cases),
                            capture_output=True, text=True, check=True, timeout=30,
                            env={**os.environ, 'LC_ALL': 'C', 'TZ': 'UTC'})
    assert not oracle.stderr, oracle.stderr
    outputs = [json.loads(line) for line in oracle.stdout.splitlines()]
    profile = outputs.pop(0)
    assert len(outputs) == len(cases)
    clauses = []
    for index, ((op, a, b), result) in enumerate(zip(cases, outputs)):
        if op in ['cast', 'implicit']:
            notices = '[' + ', '.join(result[1]) + ']' if result[1] else 'eps'
            expression = f'$float_long({int(a,16)}, {str(op == "implicit").lower()})'
            expected = f'($({result[0]}), {notices})'
        else:
            expression = f'$long_not($({a}))' if op == 'not' else f'$long_{op}($({a}), $({b}))'
            expected = result[0] if result[0] in ['INTZERO','NEGSHIFT'] else f'$({result[0]})'
            if op in ['mod','shl','shr'] and len(result) == 2:
                expected = f'IRESULT {expected}'
        clauses.append(f'dec $icase{index}() : bool\ndef $icase{index}() = true\n  -- if {expression} = {expected}\n')
    with tempfile.TemporaryDirectory(prefix='integer-', dir=ROOT / '.tools') as tmp:
        for start in range(0, len(cases), 80):
            stop = min(start + 80, len(cases))
            fixture = Path(tmp) / f'cases-{start}.watsup'
            fixture.write_text('\n'.join(clauses[start:stop]) + '\ndec $main() : bool\ndef $main() = true\n' +
                               '\n'.join(f'  -- if $icase{i}()' for i in range(start, stop)) + '\n')
            run = subprocess.run([str(runner), *map(str, SPECS), str(fixture)], cwd=ROOT,
                                 capture_output=True, text=True, timeout=120)
            if run.returncode or run.stdout.strip() != 'true':
                (ROOT / '.tools/integer-failure.watsup').write_text(fixture.read_text())
                raise SystemExit(f'FAIL cases {start}..{stop}: {run.stdout}{run.stderr}')
    assert before == fingerprints(), 'integer implementation changed during validation'
    report = {'cases': len(cases), 'seed': 85011, 'result': 'pass', 'fingerprints': before, 'profile': profile,
              'environment': {'LC_ALL':'C','TZ':'UTC'},
              'case_manifest_sha256': hashlib.sha256(json.dumps([cases,outputs], sort_keys=True).encode()).hexdigest()}
    (ROOT / 'coverage/semantics/integer.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
