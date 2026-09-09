from pathlib import Path
import base64,hashlib,json,subprocess,sys,tempfile
D=Path(__file__).resolve().parents[2];sys.path.insert(0,str(D/'tests/semantics'));import static_types as t
modules=['spec/php.watsup','spec/semantics/00-numeric.watsup','spec/semantics/10-bytes.watsup','spec/semantics/16-static-types.watsup','spec/semantics/25-builtin-argument-modes.watsup']
files=modules+['tests/semantics/_build/default/numeric_runner.exe','tests/semantics/builtin_argument_modes.py','coverage/semantics/builtin-argument-modes.json','scripts/generate-builtin-argument-modes.py','.tools/php/bin/php']
before={p:hashlib.sha256((D/p).read_bytes()).hexdigest() for p in files}
out=Path(tempfile.mkdtemp(prefix='builtin-modes-check-',dir=D/'.tools'));print(out,flush=True)
report=json.loads((D/'coverage/semantics/builtin-argument-modes.json').read_text());records=report['arguments']
source=out/'metadata.php';source.write_text('''<?php
$r=[];
foreach(get_defined_functions()["internal"] as $n) {
 $f=new ReflectionFunction($n);$p=[];
 foreach($f->getParameters() as $a) $p[]=["name"=>$a->getName(),"send_mode"=>$a->isPassedByReference()?($a->canBePassedByValue()?2:1):0,"variadic"=>$a->isVariadic()];
 $r[$n]=$p;
}
echo json_encode(["identity"=>[PHP_VERSION,PHP_SAPI,PHP_INT_SIZE,PHP_ZTS,ini_get("disable_functions")],"functions"=>$r]);
''')
def run(command,label):
 (out/(label+'.command.json')).write_text(json.dumps(command))
 try:r=subprocess.run(command,capture_output=True,env=t.ENV,timeout=40)
 except subprocess.TimeoutExpired as e:
  (out/(label+'.stdout')).write_bytes(e.stdout or b'');(out/(label+'.stderr')).write_bytes(e.stderr or b'');(out/(label+'.status.json')).write_text(json.dumps({'status':'timeout'}));raise
 (out/(label+'.stdout')).write_bytes(r.stdout);(out/(label+'.stderr')).write_bytes(r.stderr);(out/(label+'.status.json')).write_text(json.dumps({'status':'exit','exit_status':r.returncode}))
 assert r.returncode==0 and not r.stderr,(r.returncode,r.stderr)
 return r.stdout
metadata=json.loads(run([str(t.PHP),'-n',*t.FLAGS,str(source)],'native'))
assert metadata['identity']==['8.5.10','cli',8,False,''],metadata['identity']
native=metadata['functions']
assert native=={r['name']:r['parameters'] for r in records},[(r['name'],native.get(r['name']),r['parameters']) for r in records if native.get(r['name'])!=r['parameters']]
lines=[];count=0
for r in records:
 p=r['parameters']
 for i in range(len(p)+3):
  expected=bool(i and (p[i-1]['send_mode'] if i<=len(p) else p[-1]['send_mode'] if p and p[-1]['variadic'] else False))
  for name in [r['name'],r['name'].upper()]:
   lines.append('($pfunction_builtin_ref('+t.byte_expr(name)+', '+str(i)+') = '+str(expected).lower()+')');count+=1
fixture=out/'modes.watsup';fixture.write_text('dec $main() : bool\ndef $main() = '+' /\\\n '.join(lines)+'\n')
modules=['spec/php.watsup','spec/semantics/00-numeric.watsup','spec/semantics/10-bytes.watsup','spec/semantics/16-static-types.watsup','spec/semantics/25-builtin-argument-modes.watsup'];actual=run([str(D/'tests/semantics/_build/default/numeric_runner.exe'),*[str(D/p) for p in modules],str(fixture)],'spectec');assert actual.strip()==b'true',actual
assert before=={p:hashlib.sha256((D/p).read_bytes()).hexdigest() for p in files}
result={'scope':'source-derived positional argument modes, native metadata validation only','identity':metadata['identity'],'signatures':len(records),'assertions':count,'native_exact':True,'spectec':True,'inputs':before,'raw':str(out.relative_to(D))}
(out/'result.json').write_text(json.dumps(result,indent=2));(D/'coverage/semantics/builtin-argument-modes-test.json').write_text(json.dumps(result,indent=2)+'\n');print(len(records),count,flush=True)
