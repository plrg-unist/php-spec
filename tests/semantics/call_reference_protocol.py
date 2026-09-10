#!/usr/bin/env python3
"""Actual-source call acquisition origins and value/reference result controls."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,tempfile
R=Path(__file__).resolve().parents[2];K=R;sys.path.insert(0,str(K/'tests/semantics'))
import function_scope as fs
import request_environment as q
import request_environment_state as rs
from recorded_worker import Worker
D=Path(tempfile.mkdtemp(prefix='call-reference-protocol-',dir=R/'.tools'));print(D,flush=True)
(D/'producer.py').write_bytes(Path(__file__).read_bytes())
before=q.t.syntax_validation.implementation_fingerprint();modules=[K/p for p in json.loads((K/'spec/semantics/modules.json').read_text())]
runner=K/'tests/semantics/_build/default/numeric_runner.exe';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
paths=[*modules,runner,K/'_build/default/adapter/main.exe',q.t.PHP,K/'.tools/php-file.so',K/'tests/semantics/recorded_worker.py']
direct={str(p.relative_to(K)):sha(p) for p in paths}
(D/'inputs.json').write_text(json.dumps({'candidate':str(K),'closure':before,'direct':direct},indent=2))
for p in paths:
 o=D/'original-inputs'/p.relative_to(K);o.parent.mkdir(parents=True,exist_ok=True);o.write_bytes(p.read_bytes())
D_root=D
CASES={
 'alias':b'<?php\nfunction g(){return [2];}\n$x=[1];$y=&$x;$z=($x=&g());$x[0]=3;echo $x[0],$y[0],$z[0];',
 'nested':b'<?php\nfunction g(){return [1,2];}\nfunction f(){$x=&g();$y=$x;$x[0]=3;return [$x,$y];}\n$a=f();echo $a[0][0],$a[1][0];',
}
records=[]
for case,source in CASES.items():
 D=D_root/case;D.mkdir();path=D/'source.php';path.write_bytes(source)
 entries=[b'LC_ALL=C',b'TZ=UTC',b'FIRST=one'];payload=D/'request.input';payload.write_bytes(q.packet(1700000000,125000,entries))
 request={'env':[[q.b64(k),q.b64(v)] for k,v in (e.split(b'=',1) for e in entries)],'argv':[q.b64(os.fsencode(path))],'file':q.b64(os.fsencode(path)),'seconds':'1700000000','microseconds':125000,'variables':q.b64(b'EGPCS'),'jit':True,'cwd':q.b64(os.fsencode(D))}
 row={'id':case,'source_base64':q.b64(source),'context':str(path),'request':request,'native':fs.native(path,payload,D)}
 (D/'original.json').write_text(json.dumps(row,indent=2))
 f=ad=None
 try:
  f=Worker([str(q.t.PHP),'-n',*q.t.FLAGS,'-d','extension='+str(K/'.tools/php-file.so'),str(K/'frontend/worker.php')],D/'frontend-wire')
  ad=Worker([str(K/'_build/default/adapter/main.exe'),str(K)],D/'adapter-wire')
  parsed=f.request({'op':'parse','source':row['source_base64']});assert parsed['accepted']
  checked=ad.request({'op':'check','ast':parsed['ast'],'fixture':True});(D/'checked.json').write_text(json.dumps(checked))
  out=ad.request({'op':'execute','ast':parsed['ast'],'steps':10000,'filename':q.b64(row['context'].encode()),'request':row['request']});(D/'state.json').write_text(json.dumps(out))
  actual=q.cli.observe(out['state'],row['context']);assert all(actual[k]==row['native'][k] for k in ['stdout','stderr','exit_status'])
 finally:
  try:
   if f:f.close()
  finally:
   if ad:ad.close()
 initial='$php_request_run('+checked['fixture']+', 0, '+json.dumps(q.b64(row['context'].encode()))+', '+rs.request_fixture(row['request'])+')'
 prefix='''dec $review_stage(pstate) : bool
 def $review_stage(S) = true -- if S.TODO = ACQUIRE_CALL :: ptask*
 def $review_stage(S) = false -- otherwise
 dec $review_find(pstate, nat) : pstate
 def $review_find(S, n) = S -- if $review_stage(S)
 def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)
   -- if ~$review_stage(S)
   -- if $(n > 0)
   -- if n_rest = $(n - 1)
   -- if S_next = $drive_steps(S, 1)
 dec $review_event(pevent) : nat*
 def $review_event(OUTPUT n*) = n*
 def $review_event(pevent) = eps -- otherwise
 dec $review_outputs(pevent*) : nat*
 def $review_outputs(eps) = eps
 def $review_outputs(pevent :: pevent_tail*) = $review_event(pevent) ++ $review_outputs(pevent_tail*)
 dec $review_diagnostic(pevent) : pevent*
 def $review_diagnostic(DIAGNOSTIC text n* z) = [DIAGNOSTIC text n* z]
 def $review_diagnostic(pevent) = eps -- otherwise
 dec $review_diagnostics(pevent*) : pevent*
 def $review_diagnostics(eps) = eps
 def $review_diagnostics(pevent :: pevent_tail*) = $review_diagnostic(pevent) ++ $review_diagnostics(pevent_tail*)
 dec $review_change_record(pcpath, pcodeexpr) : pcodeexpr
 def $review_change_record(pcpath, CODEEXPR pcpath z b) = CODEEXPR pcpath $(z + 100) b
 def $review_change_record(pcpath, pcodeexpr) = pcodeexpr -- otherwise
 dec $review_change_records(pcpath, pcodeexpr*) : pcodeexpr*
 def $review_change_records(pcpath, eps) = eps
 def $review_change_records(pcpath, pcodeexpr :: pcodeexpr_tail*) = $review_change_record(pcpath, pcodeexpr) :: $review_change_records(pcpath, pcodeexpr_tail*)
 '''
 common=['S_initial = '+initial,'S = $review_find(S_initial[.COMPLETION = NORMAL], 200)','S.TODO = ACQUIRE_CALL :: ptask*','S.ORIGIN = (PORIGIN n_unit pcpath)','n_parent = $(|pcpath| - 1)','$lookup(S.ENV, [120]) = (n_x)','S.STORE[n_x] = DEFINED pvalue_old','n_x <- S.REFCELLS','$call_descriptors_valid(S)','S.CODE = [pcode]']
 variants=[('control','S',True,'[51,51,50]'),('absent-origin','S[.ORIGIN = eps]',False,None),('wrong-unit','S[.ORIGIN = (PORIGIN 999 pcpath)]',False,None),('parent-origin','S[.ORIGIN = (PORIGIN n_unit pcpath[0:n_parent])]',False,None),('arbitrary-known','S[.RESULT = KNOWN pvalue_old]',True,'[51,51,49]'),('existing-reference','S[.RESULT = REFERENCE n_x]',True,'[51,51,49]')]
 variants += [('unit-assignment-line','S[.CODE = [pcode[.EXPRESSIONS = $review_change_records(pcpath[0:n_parent], pcode.EXPRESSIONS)]]]',False,None),('unit-call-line','S[.CODE = [pcode[.EXPRESSIONS = $review_change_records(pcpath, pcode.EXPRESSIONS)]]]',False,None)]
 variants += [('variable-result','S[.RESULT = VARIABLE ([120]) 3]',False,None)]
 variants += [('wrapped-variable-result','S[.TODO = (AT (PORIGIN n_unit pcpath) ACQUIRE_CALL) :: ptask*][.RESULT = VARIABLE ([120]) 3]',False,None)]
 variants += [('origin-variable-result','S[.TODO = (ORIGIN_RETURN (PORIGIN n_unit pcpath)) :: ACQUIRE_CALL :: ptask*][.RESULT = VARIABLE ([120]) 3]',False,None)]
 if case=='nested':
  common=['S_initial = '+initial,'S = $review_find(S_initial[.COMPLETION = NORMAL], 200)','S.TODO = ACQUIRE_CALL :: ptask*','S.FRAMES = pframe :: pframe_tail*','S.CURRENT = (pcallcontext)','$call_descriptors_valid(S)','S.CODE = [pcode]']
  variants=[('control','S',True,'[51,49]'),('plain-call-origin','S[.ORIGIN = pframe.ORIGIN]',False,None)]
 for name,changed,valid,output in variants:
  checks=common+['S_changed = '+changed,'$heap_valid($heap_graph(S_changed))','$call_descriptors_valid(S_changed) = '+str(valid).lower(),'S_zero = $drive(S_changed, 0)','S_full = $drive(S_changed, 10000)']
  if valid:
   checks+=['S_zero.COMPLETION = BUDGET','S_full.COMPLETION = NORMAL','$review_outputs(S_full.EVENTS) = '+output,'$heap_valid($heap_graph(S_full))']
   checks+=['$review_diagnostics(S_full.EVENTS) = '+('eps' if name=='existing-reference' else '[DIAGNOSTIC "Notice" $ptascii("Only variables should be assigned by reference") 3]')]
  else:checks+=['S_zero.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"','S_full.COMPLETION = S_zero.COMPLETION']
  p=D/(name+'.watsup');p.write_text(prefix+'\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+c+'\n' for c in checks))
  cmd=[str(runner),*map(str,modules),str(p)];(D/(name+'.command.json')).write_text(json.dumps(cmd))
  try:r=subprocess.run(cmd,capture_output=True,timeout=60)
  except subprocess.TimeoutExpired as e:
   (D/(name+'.stdout')).write_bytes(e.stdout or b'');(D/(name+'.stderr')).write_bytes(e.stderr or b'');(D/(name+'.status.json')).write_text(json.dumps({'status':'timeout'}));raise
  (D/(name+'.stdout')).write_bytes(r.stdout);(D/(name+'.stderr')).write_bytes(r.stderr);(D/(name+'.status.json')).write_text(json.dumps({'status':'exit','exit_status':r.returncode}))
  record={'id':case+'/'+name,'pass':r.returncode==0 and r.stdout.strip()==b'true' and not r.stderr,'assertions':len(checks)};records.append(record);(D/'results.json').write_text(json.dumps(records,indent=2));print(record,flush=True)
assert before==q.t.syntax_validation.implementation_fingerprint();assert all(sha(K/p)==h for p,h in direct.items())
result={'result':'pass' if all(r['pass'] for r in records) else 'fail','raw':str(D_root),'fingerprint':before,'records':records,'assertions':sum(r['assertions'] for r in records)}
(D_root/'report.json').write_text(json.dumps(result,indent=2));print(result['result'],flush=True)

(R/'coverage/semantics/call-reference-protocol.json').write_text(json.dumps(result,indent=2))
assert result['result']=='pass'
