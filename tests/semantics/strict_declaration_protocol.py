#!/usr/bin/env python3
"""Source-derived strictness integrity at zero/full public resume boundaries."""
from pathlib import Path
import hashlib,json,os,subprocess,tempfile
import function_scope as fs
import request_environment_state as rs
q=fs.q
R=Path(__file__).resolve().parents[2];K=R
from recorded_worker import Worker
CASES={
 'strict-no-function':b'<?php declare(strict_types=1);$a=1;echo ++$a;',
 'zero-no-function':b'<?php declare(strict_types=0);echo 3;',
 'weak-no-function-control':b'<?php $a=1;echo ++$a;',
 'strict-cache-skip':b'<?php declare(strict_types=1);function f($x=MISSING){return $x;}echo f(8);',
 'sticky-multilist':b'<?php declare(strict_types=1,STRICT_TYPES=0);;;declare(strict_types=0);function f($x="a"){return $x;}echo f();',
}
D=Path(tempfile.mkdtemp(prefix='strict-declaration-protocol-',dir=R/'.tools'));print(D,flush=True);(D/'producer.py').write_bytes(Path(__file__).read_bytes());before=q.t.syntax_validation.implementation_fingerprint();modules=[K/p for p in json.load(open(K/'spec/semantics/modules.json'))];runner=K/'tests/semantics/_build/default/numeric_runner.exe';paths=[*modules,runner,K/'_build/default/adapter/main.exe',q.t.PHP,K/'.tools/php-file.so',K/'tests/semantics/recorded_worker.py',Path(__file__),K/'tests/semantics/function_scope.py'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();direct={str(p.relative_to(K)):sha(p) for p in paths};(D/'inputs.json').write_text(json.dumps({'candidate':str(K),'closure':before,'direct':direct},indent=2))
for p in paths:
 o=D/'original-inputs'/p.relative_to(K);o.parent.mkdir(parents=True,exist_ok=True);o.write_bytes(p.read_bytes())
f=ad=None;records=[];fixtures=[]
try:
 f=Worker([str(q.t.PHP),'-n',*q.t.FLAGS,'-d','extension='+str(K/'.tools/php-file.so'),str(K/'frontend/worker.php')],D/'frontend-wire');ad=Worker([str(K/'_build/default/adapter/main.exe'),str(K)],D/'adapter-wire')
 for name,source in CASES.items():
  d=D/name;d.mkdir();path=d/'source.php';path.write_bytes(source);entries=[b'LC_ALL=C',b'TZ=UTC',b'FIRST=one'];payload=d/'request.input';payload.write_bytes(q.packet(1700000000,125000,entries));request={'env':[[q.b64(k),q.b64(v)] for k,v in (e.split(b'=',1) for e in entries)],'argv':[q.b64(os.fsencode(path))],'file':q.b64(os.fsencode(path)),'seconds':'1700000000','microseconds':125000,'variables':q.b64(b'EGPCS'),'jit':True,'cwd':q.b64(os.fsencode(d))};row={'id':name,'source_base64':q.b64(source),'context':str(path),'request':request,'native':fs.native(path,payload,d)};(d/'original.json').write_text(json.dumps(row));p=f.request({'op':'parse','source':row['source_base64']});assert p['accepted'];c=ad.request({'op':'check','ast':p['ast'],'fixture':True});(d/'checked.json').write_text(json.dumps(c));out=ad.request({'op':'execute','ast':p['ast'],'steps':10000,'filename':q.b64(row['context'].encode()),'request':row['request']});(d/'state.json').write_text(json.dumps(out));actual=q.cli.observe(out['state'],row['context']);assert all(actual[k]==row['native'][k] for k in ['stdout','stderr','exit_status'])
  initial='$php_request_run('+c['fixture']+', 0, '+json.dumps(q.b64(row['context'].encode()))+', '+rs.request_fixture(row['request'])+')'
  common=['S_initial = '+initial,'S = S_initial[.COMPLETION = NORMAL]','S.CODE = [pcode]','$call_descriptors_valid(S)']
  for kind,term,valid in [('control','S',True),('unit-strict-flip','S[.CODE = [pcode[.STRICT = ~pcode.STRICT]]]',False),('arbitrary-result','S[.RESULT = KNOWN (PINT 99)]',True)]:
   checks=common+['S_changed = '+term,'$call_descriptors_valid(S_changed) = '+str(valid).lower(),'S_zero = $drive(S_changed, 0)','S_full = $drive(S_changed, 10000)']
   checks += ['S_zero.COMPLETION = BUDGET','S_full.COMPLETION = NORMAL'] if valid else ['S_zero.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"','S_full.COMPLETION = S_zero.COMPLETION']
   fixtures.append((d,kind,checks))
  if out['state']['FUNCTIONS']:
   checks=common+['S.FUNCTIONS = [pfunction]','S_changed = S[.FUNCTIONS = [pfunction[.CODE.STRICT = ~pfunction.CODE.STRICT]]]','~$call_descriptors_valid(S_changed)','$drive(S_changed, 0).COMPLETION = UNSUPPORTED "invalid compiled function descriptor"','$drive(S_changed, 10000).COMPLETION = UNSUPPORTED "invalid compiled function descriptor"'];fixtures.append((d,'function-strict-flip',checks))
finally:
 try:
  if f:f.close()
 finally:
  if ad:ad.close()
for d,kind,checks in fixtures:
 p=d/(kind+'.watsup');p.write_text('dec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+c+'\n' for c in checks));cmd=[str(runner),*map(str,modules),str(p)];(d/(kind+'.command.json')).write_text(json.dumps(cmd))
 try:r=subprocess.run(cmd,capture_output=True,timeout=60)
 except subprocess.TimeoutExpired as error:
  (d/(kind+'.stdout')).write_bytes(error.stdout or b'');(d/(kind+'.stderr')).write_bytes(error.stderr or b'');(d/(kind+'.status.json')).write_text(json.dumps({'status':'timeout','seconds':60}));raise
 (d/(kind+'.stdout')).write_bytes(r.stdout);(d/(kind+'.stderr')).write_bytes(r.stderr);(d/(kind+'.status.json')).write_text(json.dumps({'status':'exit','exit_status':r.returncode}));row={'id':d.name+'/'+kind,'pass':r.returncode==0 and r.stdout.strip()==b'true' and not r.stderr,'assertions':len(checks)};records.append(row);(D/'results.json').write_text(json.dumps(records,indent=2));print(row,flush=True)
assert before==q.t.syntax_validation.implementation_fingerprint();assert all(sha(K/p)==h for p,h in direct.items());(D/'report.json').write_text(json.dumps({'result':'pass' if all(r['pass'] for r in records) else 'fail','scope':'Five fresh native/source profiles: five unit flag and two function flag rejections; ten valid controls; zero and full public resumes.','fingerprint':before,'records':records,'assertions':sum(r['assertions'] for r in records)},indent=2))

assert all(r['pass'] for r in records), 'strict descriptor protocol failed'

report = json.loads((D / "report.json").read_text())
report["raw"] = str(D)
(D / "report.json").write_text(json.dumps(report, indent=2))
(K / "coverage/semantics/strict-declaration-protocol.json").write_text(json.dumps(report, indent=2))
print(D, flush=True)
