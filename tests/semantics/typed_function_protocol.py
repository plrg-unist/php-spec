#!/usr/bin/env python3
"""Source-bound typed receive and return tasks, including saved caller context."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,tempfile
import function_scope as fs
import request_environment as q
import request_environment_state as rs
from recorded_worker import Worker
R=Path(__file__).resolve().parents[2];K=R
D=Path(tempfile.mkdtemp(prefix='typed-function-protocol-',dir=R/'.tools'));print(D,flush=True);(D/'producer.py').write_bytes(Path(__file__).read_bytes())
CASES={'typed-default-scalar-cache-before-array-error': b'<?php\nconst C=3;\nfunction f(array $x=C){echo "BODY";}\nf();', 'return-mixed-fallthrough': b'<?php function f():mixed{}f();', 'typed-value-return-global-alias-copy': b'<?php\n$x="2";$y=&$x;\nfunction f():int{global $x;$z=&$x;return $z;}\necho f(),$x==="2",$y==="2";', 'typed-return-array-global-owner': b'<?php\nfunction f():int{global $a;$a=[1];$b=&$a[0];return $a;}\nf();', 'typed-nested-return-context': b'<?php\nfunction g():int{return 2;}\nfunction f():int{return g();}\necho f();'}
CASES['untyped-top-level-return-projection']=b'<?php echo 1; return 2;'
before=q.t.syntax_validation.implementation_fingerprint();modules=[K/p for p in json.load(open(K/'spec/semantics/modules.json'))];runner=K/'tests/semantics/_build/default/numeric_runner.exe';paths=[*modules,runner,K/'_build/default/adapter/main.exe',q.t.PHP,K/'.tools/php-file.so',K/'tests/semantics/recorded_worker.py',Path(__file__),K/'tests/semantics/function_scope.py'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();direct={str(p.relative_to(K)):sha(p) for p in paths};(D/'inputs.json').write_text(json.dumps({'candidate':str(K),'closure':before,'direct':direct},indent=2))
for p in paths:
 o=D/'original-inputs'/p.relative_to(K);o.parent.mkdir(parents=True,exist_ok=True);o.write_bytes(p.read_bytes())
f=ad=None;records=[];fixtures=[]
selections=[('typed-default-scalar-cache-before-array-error','receive','TYPE_RECEIVE porigin n'),('return-mixed-fallthrough','fallthrough','TYPE_FALLTHROUGH porigin'),('typed-value-return-global-alias-copy','return','RETURN_VALUE z'),('typed-return-array-global-owner','return','RETURN_VALUE z'),('typed-nested-return-context','return','RETURN_VALUE z'),('untyped-top-level-return-projection','unit','RETURN_VALUE z')]
try:
 f=Worker([str(q.t.PHP),'-n',*q.t.FLAGS,'-d','extension='+str(K/'.tools/php-file.so'),str(K/'frontend/worker.php')],D/'frontend-wire');ad=Worker([str(K/'_build/default/adapter/main.exe'),str(K)],D/'adapter-wire')
 for name,stage,pattern in selections:
  d=D/name;d.mkdir();path=d/'source.php';path.write_bytes(CASES[name]);entries=[b'LC_ALL=C',b'TZ=UTC',b'FIRST=one'];payload=d/'request.input';payload.write_bytes(q.packet(1700000000,125000,entries));request={'env':[[q.b64(k),q.b64(v)] for k,v in (e.split(b'=',1) for e in entries)],'argv':[q.b64(os.fsencode(path))],'file':q.b64(os.fsencode(path)),'seconds':'1700000000','microseconds':125000,'variables':q.b64(b'EGPCS'),'jit':True,'cwd':q.b64(os.fsencode(d))};row={'id':name,'source_base64':q.b64(CASES[name]),'context':str(path),'request':request,'native':fs.native(path,payload,d)};(d/'original.json').write_text(json.dumps(row));p=f.request({'op':'parse','source':row['source_base64']});assert p['accepted'];c=ad.request({'op':'check','ast':p['ast'],'fixture':True});(d/'checked.json').write_text(json.dumps(c));out=ad.request({'op':'execute','ast':p['ast'],'steps':10000,'filename':q.b64(row['context'].encode()),'request':row['request']});(d/'state.json').write_text(json.dumps(out));actual=q.cli.observe(out['state'],row['context']);assert all(actual[k]==row['native'][k] for k in ['stdout','stderr','exit_status'])
  initial='$php_request_run('+c['fixture']+', 0, '+json.dumps(q.b64(row['context'].encode()))+', '+rs.request_fixture(row['request'])+')'
  prefix='dec $review_type_stage(pstate) : bool\ndef $review_type_stage(S) = true\n  -- if S.TODO = ('+pattern+') :: ptask*\ndef $review_type_stage(S) = false -- otherwise\ndec $review_type_find(pstate, nat) : pstate\ndef $review_type_find(S, n) = S -- if $review_type_stage(S)\ndef $review_type_find(S, n) = $review_type_find(S_next[.COMPLETION = NORMAL], n_rest)\n  -- if ~$review_type_stage(S)\n  -- if $(n > 0)\n  -- if n_rest = $(n - 1)\n  -- if S_next = $drive_steps(S, 1)\n'
  prefix += 'dec $review_type_output(pevent) : nat*\ndef $review_type_output(OUTPUT n*) = n*\ndef $review_type_output(pevent) = eps -- otherwise\ndec $review_type_outputs(pevent*) : nat*\ndef $review_type_outputs(eps) = eps\ndef $review_type_outputs(pevent :: pevent_tail*) = $review_type_output(pevent) ++ $review_type_outputs(pevent_tail*)\ndec $review_type_return_record(pstate, nat, pcodeexpr) : bool\ndef $review_type_return_record(S, n_unit, CODEEXPR pcpath z b) = true\n  -- if $origin_node(S.SOURCES, (PORIGIN n_unit pcpath)) = (NStmtReturn expression metadata)\ndef $review_type_return_record(S, n_unit, pcodeexpr) = false -- otherwise\ndec $review_type_unit_return(pstate, nat, pcodeexpr*) : pcodeexpr*\ndef $review_type_unit_return(S, n_unit, eps) = eps\ndef $review_type_unit_return(S, n_unit, (CODEEXPR pcpath z b) :: pcodeexpr*) = (CODEEXPR pcpath $(z + 100) b) :: pcodeexpr*\n  -- if $origin_node(S.SOURCES, (PORIGIN n_unit pcpath)) = (NStmtReturn expression metadata)\ndef $review_type_unit_return(S, n_unit, pcodeexpr :: pcodeexpr_tail*) = pcodeexpr :: $review_type_unit_return(S, n_unit, pcodeexpr_tail*)\n  -- if ~$review_type_return_record(S, n_unit, pcodeexpr)\n'
  common=['S_initial = '+initial,'S = $review_type_find(S_initial[.COMPLETION = NORMAL], 200)','S.TODO = ('+pattern+') :: ptask*','S.CODE = [pcode]','$call_descriptors_valid(S)']
  if name=='typed-nested-return-context':common += ['S.FRAMES = pframe :: pframe_tail*','pframe.TODO = (ORIGIN_RETURN porigin_saved?) :: (RETURN_VALUE z_saved) :: ptask_saved*']
  variants=[('control','S',True)]
  if stage=='receive':variants += [('wrong-callee','S[.TODO = [TYPE_RECEIVE (PORIGIN 999 eps) n]]',False),('index-outside-params','S[.TODO = [TYPE_RECEIVE porigin 99]]',False),('trailing-task','S[.TODO = [TYPE_RECEIVE porigin n, DISCARD]]',False)]
  if stage=='fallthrough':variants += [('wrong-callee','S[.TODO = (TYPE_FALLTHROUGH (PORIGIN 999 eps)) :: ptask*]',False)]
  if stage=='unit':variants += [('unit-return-line','S[.CODE = [pcode[.EXPRESSIONS = $review_type_unit_return(S, pcode.UNIT, pcode.EXPRESSIONS)]]]',False)]
  if stage=='return':
   variants += [('unit-return-line','S[.CODE = [pcode[.EXPRESSIONS = $review_type_unit_return(S, pcode.UNIT, pcode.EXPRESSIONS)]]]',False),('wrong-return-line','S[.TODO = (RETURN_VALUE $(z + 100)) :: ptask*]',False)]
   if name=='typed-value-return-global-alias-copy':variants += [('arbitrary-result','S[.RESULT = KNOWN (PINT 99)]',True)]
  if name=='typed-nested-return-context':variants += [('saved-return-line','S[.FRAMES = pframe[.TODO = (ORIGIN_RETURN porigin_saved?) :: (RETURN_VALUE $(z_saved + 100)) :: ptask_saved*] :: pframe_tail*]',False)]
  for kind,term,valid in variants:
   checks=common+['S_changed = '+term,'$call_descriptors_valid(S_changed) = '+str(valid).lower(),'S_zero = $drive(S_changed, 0)']
   checks += ['S_zero.COMPLETION = BUDGET'] if valid else ['S_zero.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"']
   checks += ['S_full = $drive(S_changed, 10000)']
   checks += ['S_full.COMPLETION = $drive(S, 10000).COMPLETION'] if valid else ['S_full.COMPLETION = S_zero.COMPLETION']
   if kind=='arbitrary-result':checks += ['$review_type_outputs(S_full.EVENTS) = [57,57,49,49]']
   fixtures.append((d,kind,prefix,checks))
finally:
 try:
  if f:f.close()
 finally:
  if ad:ad.close()
for d,kind,prefix,checks in fixtures:
 p=d/(kind+'.watsup');p.write_text(prefix+'\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+c+'\n' for c in checks));cmd=[str(runner),*map(str,modules),str(p)];(d/(kind+'.command.json')).write_text(json.dumps(cmd))
 try:r=subprocess.run(cmd,capture_output=True,timeout=60)
 except subprocess.TimeoutExpired as e:
  (d/(kind+'.stdout')).write_bytes(e.stdout or b'');(d/(kind+'.stderr')).write_bytes(e.stderr or b'');(d/(kind+'.status.json')).write_text(json.dumps({'status':'timeout'}));raise
 (d/(kind+'.stdout')).write_bytes(r.stdout);(d/(kind+'.stderr')).write_bytes(r.stderr);(d/(kind+'.status.json')).write_text(json.dumps({'status':'exit','exit_status':r.returncode}));row={'id':d.name+'/'+kind,'pass':r.returncode==0 and r.stdout.strip()==b'true' and not r.stderr,'assertions':len(checks)};records.append(row);(D/'results.json').write_text(json.dumps(records,indent=2));print(row,flush=True)
assert before==q.t.syntax_validation.implementation_fingerprint();assert all(sha(K/p)==h for p,h in direct.items());report={'result':'pass' if all(r['pass'] for r in records) else 'fail','raw':str(D),'fingerprint':before,'records':records,'assertions':sum(r['assertions'] for r in records)}
(D/'report.json').write_text(json.dumps(report,indent=2));target=R/'coverage/semantics/typed-function-protocol.json';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(report,indent=2));assert report['result']=='pass'
