#!/usr/bin/env python3
"""Power preparation: exact integer/special answers and explicit pending tasks."""
import hashlib
import json
import os
import time
from pathlib import Path
import subprocess
import tempfile
from power_platform import inspect_platform

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PHP = ROOT / '.tools/php/bin/php'
SPECS = [ROOT / f'spec/semantics/{name}.watsup' for name in
         ['00-numeric', '01-integer', '02-numeric-text', '03-numeric-format',
          '04-numeric-context', '06-power-prepare']]


def pnum(value):
    return f'({"NINT" if value[0] == "i" else "NFLOAT"} $({int(value[1], 10 if value[0] == "i" else 16)}))'


def main():
    subprocess.run([str(ROOT / 'scripts/opam-exec.sh'), 'dune', 'build', '--root',
                    str(HERE), 'numeric_runner.exe'], cwd=ROOT, check=True)
    runner = HERE / '_build/default/numeric_runner.exe'
    specs = SPECS
    watched = specs + [PHP, Path(__file__), HERE / 'numeric_runner.ml', runner,
                       HERE/'power_platform.py', ROOT/'dependencies/libm-provenance.json']
    def fingerprints():
        return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}
    before = fingerprints()
    started = time.monotonic()
    platform = inspect_platform()
    cases = [[['i',str(a)],['i',str(b)]] for a in range(-20,21) for b in range(11)]
    cases += [[['i',str(a)],['i',str(b)]] for a in [-1,0,1] for b in [2**63-1]]
    cases += [[['i','2'],['i','63']],[['i','-2'],['i','63']]]
    special = [0,2**63,0x7ff0000000000000,0xfff0000000000000,
               0x7ff8000000000042,0xfff8000000000042,0x7ff0000000000001,0xfff0000000000001]
    exponents = [0,2**63,0x3ff0000000000000,0xbff0000000000000,0x4000000000000000,
                 0x4008000000000000,0xc008000000000000,0x3fe0000000000000,
                 0xbfe0000000000000,0x7ff0000000000000,0xfff0000000000000,
                 0x7ff8000000000042,0x7ff0000000000001]
    cases += [[['f',f'{a:016x}'],['f',f'{b:016x}']] for a in special for b in exponents]
    cases += [[['f',f'{a:016x}'],['f',f'{b:016x}']]
              for a in [0x3ff0000000000000,0xbff0000000000000,0x3fe0000000000000,0x4000000000000000]
              for b in [0,2**63,1,0x8000000000000001,0x43e0000000000000,0xc3e0000000000000,
                        0x7ff0000000000000,0xfff0000000000000,0x7ff8000000000042,0x7ff0000000000001]]
    php = r'''
$libm_paths=[];
foreach(explode("\n",file_get_contents('/proc/self/maps'))as$line){
 if(preg_match('~(/[^\s]+/libm\.so\.[^\s]+)$~',$line,$match))$libm_paths[$match[1]]=true;
}
if(PHP_VERSION!=='8.5.10'||PHP_INT_SIZE!==8||PHP_SAPI!=='cli'||PHP_ZTS)exit(91);
if(bin2hex(pack('E',unpack('E',hex2bin('7ff0000000000001'))[1]))!=='7ff0000000000001')exit(92);
echo json_encode(['version'=>PHP_VERSION,'sapi'=>PHP_SAPI,'int_size'=>PHP_INT_SIZE,
 'libm_paths'=>array_keys($libm_paths),'zts'=>PHP_ZTS,'extensions'=>get_loaded_extensions(),'precision'=>ini_get('precision'),
 'serialize_precision'=>ini_get('serialize_precision'),'opcache.enable_cli'=>ini_get('opcache.enable_cli'),
 'opcache.jit'=>ini_get('opcache.jit')]),"\n";
function operand($a){return $a[0]==='i'?(int)$a[1]:unpack('E',hex2bin($a[1]))[1];}
$notices=[];set_error_handler(function($level,$message)use(&$notices){$notices[]=[$level,$message];});
foreach(json_decode(stream_get_contents(STDIN),true)as[$av,$bv]){
 $a=operand($av);$b=operand($bv);$notices=[];$v=$a**$b;
 echo json_encode([gettype($v),is_int($v)?(string)$v:bin2hex(pack('E',$v)),$notices]),"\n";
}
'''
    oracle = subprocess.run([str(PHP),'-n','-d','opcache.enable_cli=0','-d','opcache.jit=disable',
                             '-d','precision=14','-d','serialize_precision=-1','-r',php],
                            input=json.dumps(cases),capture_output=True,text=True,check=True,timeout=30,
                            env={**os.environ,'LC_ALL':'C','TZ':'UTC'})
    assert not oracle.stderr,oracle.stderr
    outputs=[json.loads(line)for line in oracle.stdout.splitlines()]
    profile=outputs.pop(0)
    assert len(profile['libm_paths']) == 1, 'PHP libm mapping is ambiguous'
    php_libm=Path(profile['libm_paths'][0]).resolve()
    assert str(php_libm) == platform['libm_path'], 'PHP uses a different libm path'
    assert hashlib.sha256(php_libm.read_bytes()).hexdigest() == platform['libm_sha256']
    assert len(outputs)==len(cases)
    clauses=[]
    for index,((a,b),result)in enumerate(zip(cases,outputs)):
        value=int(result[1],16 if result[0]=='double' else 10)
        assert result[2] in [[],[[8192,'Power of base 0 and negative exponent is deprecated']]],result
        number=f'({"NFLOAT" if result[0]=="double" else "NINT"} $({value}))'
        notice=str(bool(result[2])).lower()
        expected=f'POWERDONE {number} {notice}'
        operation='power_prepare'
        clauses.append(f'dec $pcase{index}() : bool\ndef $pcase{index}() = true\n'
                       f'  -- if ${operation}({pnum(a)}, {pnum(b)}) = {expected}\n')
    # Intermediate decomposition check, not agreement on 2**64's result.
    index=len(cases)
    clauses.append(f'dec $pcase{index}() : bool\ndef $pcase{index}() = true\n'
                   '  -- if $power_prepare(NINT 2, NINT 64) = POWERGENERAL 4607182418800017408 4895412794951729152 4607182418800017408 0 false\n')
    with tempfile.TemporaryDirectory(prefix='powerprep-',dir=ROOT/'.tools')as tmp:
        for start in range(0,len(clauses),60):
            stop=min(start+60,len(clauses));fixture=Path(tmp)/f'cases-{start}.watsup'
            fixture.write_text('\n'.join(clauses[start:stop])+'\ndec $main() : bool\ndef $main() = true\n'+
                               '\n'.join(f'  -- if $pcase{i}()'for i in range(start,stop))+'\n')
            run=subprocess.run([str(runner),*map(str,specs),str(fixture)],cwd=ROOT,
                               capture_output=True,text=True,timeout=120)
            if run.returncode or run.stdout.strip()!='true':
                (ROOT/'.tools/powerprep-failure.watsup').write_text(fixture.read_text())
                raise SystemExit(f'FAIL cases {start}..{stop}: {run.stdout}{run.stderr}')
    assert platform == inspect_platform(), 'power platform changed during validation'
    assert before==fingerprints(),'power implementation changed during validation'
    report={'cases':len(cases),'pending_task_checks':1,'elapsed_seconds':round(time.monotonic()-started,3),'result':'pass','fingerprints':before,'profile':profile,'platform':platform,
            'environment':{'LC_ALL':'C','TZ':'UTC'},
            'case_manifest_sha256':hashlib.sha256(json.dumps([cases,outputs],sort_keys=True).encode()).hexdigest()}
    (ROOT/'coverage/semantics/power-prepare.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__=='__main__':
    main()
