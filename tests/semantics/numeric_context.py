#!/usr/bin/env python3
"""Context-sensitive string casts/keys and numeric comparisons/boolean notices."""
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
         ['00-numeric', '01-integer', '02-numeric-text', '03-numeric-format', '04-numeric-context']]


def byte_value(data):
    return '[' + ', '.join(map(str, data)) + ']' if data else 'eps'


def pnum(value):
    return f'({"NINT" if value[0] == "i" else "NFLOAT"} $({int(value[1], 10 if value[0] == "i" else 16)}))'


def main():
    subprocess.run([str(ROOT / 'scripts/opam-exec.sh'), 'dune', 'build', '--root',
                    str(HERE), 'numeric_runner.exe'], cwd=ROOT, check=True)
    runner = HERE / '_build/default/numeric_runner.exe'
    watched = SPECS + [PHP, Path(__file__), HERE / 'numeric_runner.ml', runner]
    def fingerprints():
        return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}
    before = fingerprints()
    rng = random.Random(85014)
    strings = [b'',b'0',b'-0',b'-00',b'+0',b'00',b'01',b'1',b'-1',b'+1',b' 1',b'1 ',
               b'1\0',b'0x10',b'1e3',b'1.5',b'-1.5',b'1.5x',b'1e309',b'-1e309',
               b'9223372036854775807',b'9223372036854775808',b'9223372036854777856',
               b'-9223372036854775808',b'-9223372036854775809',b'18446744073709551616',
               b'foo',b'-foo',b'-',b'-.',b'- 0',b'-0.0',b'1\xff',b'\xff1']
    strings += [str(rng.randrange(-2**66,2**66)).encode() for _ in range(80)]
    cases = [[op,['s',s.hex()],['i','0']] for op in ['key','casti','castf','long'] for s in strings]
    numbers = [['i',str(n)] for n in [0,1,-1,2**63-1,-2**63,2**53+1]]
    numbers += [['f',f'{n:016x}'] for n in [0,2**63,1,0x3ff0000000000000,0x3ff8000000000000,
                0x43e0000000000000,0x7ff0000000000000,0xfff0000000000000,0x7ff8000000000000]]
    cases += [[op,a,b] for op in ['compare','identical'] for a in numbers for b in numbers]
    cases += [['bool',a,['i','0']] for a in numbers]
    php = r'''
if (PHP_VERSION !== '8.5.10' || PHP_INT_SIZE !== 8 || PHP_SAPI !== 'cli' || PHP_ZTS) exit(91);
if (bin2hex(pack('E',unpack('E',hex2bin('8000000000000000'))[1])) !== '8000000000000000') exit(92);
echo json_encode(['version'=>PHP_VERSION,'sapi'=>PHP_SAPI,'int_size'=>PHP_INT_SIZE,
    'zts'=>PHP_ZTS,'extensions'=>get_loaded_extensions(),
    'precision'=>ini_get('precision'),'serialize_precision'=>ini_get('serialize_precision'),
    'opcache.enable_cli'=>ini_get('opcache.enable_cli'),'opcache.jit'=>ini_get('opcache.jit')]), "\n";
function operand($a) { return match($a[0]) {'i'=>(int)$a[1], 's'=>hex2bin($a[1]), 'f'=>unpack('E',hex2bin($a[1]))[1]}; }
$notices=[];
set_error_handler(function($level,$message) use (&$notices) {
    $kind=match(true) {
        $level===E_WARNING && $message==='A non-numeric value encountered'=>'LEADINGNUMBER',
        $level===E_DEPRECATED && str_starts_with($message,'Implicit conversion from float-string')=>'STRINGPRECISIONLOSS',
        $level===E_WARNING && $message==='unexpected NAN value was coerced to bool'=>'NANBOOL',
        default=>'UNEXPECTED:'.$message};
    $notices[]=$kind;
});
foreach (json_decode(stream_get_contents(STDIN),true) as [$op,$av,$bv]) {
    $a=operand($av);$b=operand($bv);$notices=[];
    try {
        if($op==='key') { $v=null;foreach([$a=>0] as $key=>$unused){$v=$key;} }
        else { $v=match($op) {'casti'=>(int)$a,'castf'=>(float)$a,'long'=>$a|0,
            'compare'=>$a<=>$b,'identical'=>$a===$b,'bool'=>(bool)$a}; }
        $payload=match(gettype($v)) {'double'=>bin2hex(pack('E',$v)),'string'=>bin2hex($v),
            'boolean'=>$v?'true':'false','integer'=>(string)$v};
        echo json_encode([gettype($v),$payload,$notices]),"\n";
    } catch(TypeError $e) { echo '["ERROR"]',"\n"; }
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
    for index, ((op,a,b), result) in enumerate(zip(cases,outputs)):
        if op in ['key','casti','castf','long']:
            data = byte_value(bytes.fromhex(a[1]))
            name = {'key':'string_key','casti':'string_cast_integer','castf':'string_cast_float','long':'string_long'}[op]
            expression = f'${name}({data})'
            if op == 'key':
                expected = f'INTEGERKEY $({result[1]})' if result[0] == 'integer' else 'STRINGKEY'
                assert not result[2]
            elif op == 'casti':
                expected = f'$({result[1]})'
                assert not result[2]
            elif op == 'castf':
                expected = str(int(result[1],16))
                assert not result[2]
            elif result[0] == 'ERROR':
                expected = 'STRINTERROR'
            else:
                assert all(n in ['LEADINGNUMBER','STRINGPRECISIONLOSS'] for n in result[2]), result
                notices = '['+', '.join(result[2])+']' if result[2] else 'eps'
                expected = f'STRINT $({result[1]}) ({notices})'
        elif op == 'bool':
            expression = f'$number_bool({pnum(a)})'
            assert result[2] in [[], ['NANBOOL']], result
            expected = f'({result[1]}, {str(bool(result[2])).lower()})'
        else:
            expression = f'$num_{op}({pnum(a)}, {pnum(b)})'
            expected = result[1] if op == 'identical' else f'$({result[1]})'
            assert not result[2], result
        clauses.append(f'dec $ccase{index}() : bool\ndef $ccase{index}() = true\n  -- if {expression} = {expected}\n')
    with tempfile.TemporaryDirectory(prefix='numcontext-', dir=ROOT / '.tools') as tmp:
        for start in range(0, len(cases), 60):
            stop = min(start + 60, len(cases))
            fixture = Path(tmp) / f'cases-{start}.watsup'
            fixture.write_text('\n'.join(clauses[start:stop]) + '\ndec $main() : bool\ndef $main() = true\n' +
                               '\n'.join(f'  -- if $ccase{i}()' for i in range(start, stop)) + '\n')
            run = subprocess.run([str(runner), *map(str, SPECS), str(fixture)], cwd=ROOT,
                                 capture_output=True, text=True, timeout=120)
            if run.returncode or run.stdout.strip() != 'true':
                (ROOT / '.tools/numcontext-failure.watsup').write_text(fixture.read_text())
                raise SystemExit(f'FAIL cases {start}..{stop}: {run.stdout}{run.stderr}')
    assert before == fingerprints(), 'numeric-context implementation changed during validation'
    report = {'cases': len(cases), 'seed': 85014, 'result': 'pass', 'fingerprints': before,
              'profile': profile, 'environment': {'LC_ALL':'C','TZ':'UTC'},
              'case_manifest_sha256': hashlib.sha256(json.dumps([cases,outputs], sort_keys=True).encode()).hexdigest()}
    (ROOT / 'coverage/semantics/numeric-context.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
