#!/usr/bin/env python3
"""String bitwise operations and inc/dec values with pending notice identities."""
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
SPECS = [ROOT / f'spec/semantics/{name}.watsup' for name in
         ['00-numeric', '01-integer', '02-numeric-text', '05-string-operators']]


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
    rng = random.Random(85015)
    cases = [[op,bytes([a]),bytes([255-a])] for op in ['and','or','xor','not'] for a in range(256)]
    for _ in range(100):
        cases.append([rng.choice(['and','or','xor']),rng.randbytes(rng.randrange(20)),rng.randbytes(rng.randrange(20))])
    strings = [b'',b'a',b'z',b'A',b'Z',b'9',b'zz',b'ZZ',b'99',b'9z',b'z9',b'Zz',b'zZ',
               b'a!z',b'!z',b'a!',b' \xffz',b'0',b'-0',b'00',b'01',b'1.5',b'1e3',b'1e+',
               b' 9',b'9 ',b'1.5x',b'\0z',b'9223372036854775807',b'-9223372036854775808',
               b'1e309',b'-1e309',b'foo9',b'1\xff']
    strings += [b'z'*512, b'Z'*512, b'9'*511+b'z', b'!'+b'z'*512]
    strings += [bytes(rng.choice(b'azAZ09.!\x00\xff') for _ in range(rng.randrange(20))) for _ in range(100)]
    cases += [[op,s,b''] for op in ['increment','decrement'] for s in strings]
    encoded = [[op,a.hex(),b.hex()] for op,a,b in cases]
    php = r'''
if (PHP_VERSION !== '8.5.10' || PHP_INT_SIZE !== 8 || PHP_SAPI !== 'cli' || PHP_ZTS) exit(91);
if(bin2hex(pack('E',1.0))!=='3ff0000000000000')exit(92);
echo json_encode(['version'=>PHP_VERSION,'sapi'=>PHP_SAPI,'int_size'=>PHP_INT_SIZE,
    'zts'=>PHP_ZTS,'extensions'=>get_loaded_extensions(),
    'precision'=>ini_get('precision'),'serialize_precision'=>ini_get('serialize_precision'),
    'opcache.enable_cli'=>ini_get('opcache.enable_cli'),'opcache.jit'=>ini_get('opcache.jit')]), "\n";
$notices=[];
set_error_handler(function($level,$message) use (&$notices) {
    $kind=match($message) {
      'Increment on non-numeric string is deprecated, use str_increment() instead'=>'STRINGINCREMENT',
      'Decrement on non-numeric string has no effect and is deprecated'=>'STRINGDECREMENT',
      'Decrement on empty string is deprecated as non-numeric'=>'EMPTYDECREMENT',
      default=>'UNEXPECTED:'.$message};
    $notices[]=[$level,$kind];
});
foreach(json_decode(stream_get_contents(STDIN),true)as[$op,$av,$bv]) {
    $a=hex2bin($av);$b=hex2bin($bv);$notices=[];
    $v=match($op){'and'=>$a&$b,'or'=>$a|$b,'xor'=>$a^$b,'not'=>~$a,'increment'=>++$a,'decrement'=>--$a};
    $payload=match(gettype($v)){'double'=>bin2hex(pack('E',$v)),'string'=>bin2hex($v),'integer'=>(string)$v};
    echo json_encode([gettype($v),$payload,$notices]),"\n";
}
'''
    oracle = subprocess.run([str(PHP), '-n', '-d', 'opcache.enable_cli=0', '-d',
                             'opcache.jit=disable', '-d', 'precision=14', '-d',
                             'serialize_precision=-1', '-r', php], input=json.dumps(encoded),
                            capture_output=True, text=True, check=True, timeout=30,
                            env={**os.environ, 'LC_ALL': 'C', 'TZ': 'UTC'})
    assert not oracle.stderr, oracle.stderr
    outputs = [json.loads(line) for line in oracle.stdout.splitlines()]
    profile = outputs.pop(0)
    assert len(outputs) == len(cases)
    clauses = []
    for index, ((op,a,b), result) in enumerate(zip(cases,outputs)):
        expression = f'$string_{op}({byte_value(a)}' + (f', {byte_value(b)})' if op in ['and','or','xor'] else ')')
        if op in ['increment','decrement']:
            if result[0] == 'string':
                value = f'UPDATEDSTRING ({byte_value(bytes.fromhex(result[1]))})'
            else:
                n = int(result[1],16 if result[0]=='double' else 10)
                value = f'UPDATEDNUMBER ({"NFLOAT" if result[0]=="double" else "NINT"} $({n}))'
            assert all(level==8192 and name in ['STRINGINCREMENT','STRINGDECREMENT','EMPTYDECREMENT'] for level,name in result[2]),result
            notices = '['+', '.join(name for level,name in result[2])+']' if result[2] else 'eps'
            expected = f'({value}, {notices})'
        else:
            assert result[0]=='string' and result[2]==[],result
            expected = byte_value(bytes.fromhex(result[1]))
        clauses.append(f'dec $scase{index}() : bool\ndef $scase{index}() = true\n  -- if {expression} = {expected}\n')
    with tempfile.TemporaryDirectory(prefix='stringops-', dir=ROOT / '.tools') as tmp:
        for start in range(0, len(cases), 80):
            stop = min(start + 80, len(cases))
            fixture = Path(tmp) / f'cases-{start}.watsup'
            fixture.write_text('\n'.join(clauses[start:stop]) + '\ndec $main() : bool\ndef $main() = true\n' +
                               '\n'.join(f'  -- if $scase{i}()' for i in range(start, stop)) + '\n')
            run = subprocess.run([str(runner), *map(str, SPECS), str(fixture)], cwd=ROOT,
                                 capture_output=True, text=True, timeout=120)
            if run.returncode or run.stdout.strip() != 'true':
                (ROOT / '.tools/stringops-failure.watsup').write_text(fixture.read_text())
                raise SystemExit(f'FAIL cases {start}..{stop}: {run.stdout}{run.stderr}')
    assert before == fingerprints(), 'string-operator implementation changed during validation'
    report = {'cases': len(cases), 'seed': 85015, 'result': 'pass', 'fingerprints': before,
              'profile': profile, 'environment': {'LC_ALL':'C','TZ':'UTC'},
              'case_manifest_sha256': hashlib.sha256(json.dumps([encoded,outputs], sort_keys=True).encode()).hexdigest()}
    (ROOT / 'coverage/semantics/string-operators.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
