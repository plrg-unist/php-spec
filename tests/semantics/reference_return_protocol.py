#!/usr/bin/env python3
"""Source return stages, caller demand, and owning result substitutions."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,tempfile
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tests/semantics'))
import function_scope as fs
import request_environment as q
import request_environment_state as rs
from recorded_worker import Worker
D=Path(tempfile.mkdtemp(prefix='reference-return-protocol-',dir=R/'.tools'));print(D,flush=True)
(D/'producer.py').write_bytes(Path(__file__).read_bytes());before=q.t.syntax_validation.implementation_fingerprint()
modules=[R/n for n in json.loads((R/'spec/semantics/modules.json').read_text())];runner=R/'tests/semantics/_build/default/numeric_runner.exe';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
paths=[*modules,runner,R/'_build/default/adapter/main.exe',q.t.PHP,R/'.tools/php-file.so',R/'tests/semantics/recorded_worker.py'];direct={str(p.relative_to(R)):sha(p) for p in paths}
(D/'inputs.json').write_text(json.dumps({'fingerprint':before,'direct':direct},indent=2))
for p in paths:
 o=D/'original-inputs'/p.relative_to(R);o.parent.mkdir(parents=True,exist_ok=True);o.write_bytes(p.read_bytes())
CASES={
 'fetch':('RETURN_REF_FETCH',b'<?php\nfunction &f():int{return $missing;}\nf();echo "DONE";'),
 'forward':('RETURN_REF_VALUE',b'<?php\nfunction &g(){$a=[1];return $a;}\nfunction &f(){return g();}\n$x=&f();$y=&$x;$x[0]=3;echo $y[0];'),
 'bare':('RETURN_REF_NULL',b'<?php function &f(){return;} $x=&f();echo $x===null;'),
 'implicit':('RETURN_REF_NULL',b'<?php function &f(){} $x=&f();echo $x===null;'),
 'value':('RETURN_REF_VALUE',b'<?php $x=1;$y=2;function &f(){global $x,$y;return ($x=&$y);}$r=&f();$r=3;echo $x,$y;'),
 'globals':('RETURN_REF_VALUE',b'<?php $x=1;function &f(){return $GLOBALS;}$r=&f();$r["x"]=2;echo $x,$r["x"];'),
 'demand':('RETURN_REF_FETCH',b'<?php $x=1;function &f(){global $x;return $x;}$r=&f();f();$r=2;echo $x;'),
}
PREFIX='''dec $review_stage(pstate) : bool
 def $review_stage(S) = true -- if S.TODO = (STAGE z) :: ptask*
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
'''
records=[]
for case,(stage,source) in CASES.items():
 d=D/case;d.mkdir();path=d/'source.php';path.write_bytes(source);entries=[b'LC_ALL=C',b'TZ=UTC',b'FIRST=one'];payload=d/'request.input';payload.write_bytes(q.packet(1700000000,125000,entries))
 request={'env':[[q.b64(k),q.b64(v)] for k,v in (e.split(b'=',1) for e in entries)],'argv':[q.b64(os.fsencode(path))],'file':q.b64(os.fsencode(path)),'seconds':'1700000000','microseconds':125000,'variables':q.b64(b'EGPCS'),'jit':True,'cwd':q.b64(os.fsencode(d))}
 row={'id':case,'source_base64':q.b64(source),'context':str(path),'request':request,'native':fs.native(path,payload,d)};(d/'original.json').write_text(json.dumps(row,indent=2));f=ad=None
 try:
  f=Worker([str(q.t.PHP),'-n',*q.t.FLAGS,'-d','extension='+str(R/'.tools/php-file.so'),str(R/'frontend/worker.php')],d/'frontend-wire');ad=Worker([str(R/'_build/default/adapter/main.exe'),str(R)],d/'adapter-wire')
  parsed=f.request({'op':'parse','source':row['source_base64']});assert parsed['accepted'];checked=ad.request({'op':'check','ast':parsed['ast'],'fixture':True});(d/'checked.json').write_text(json.dumps(checked))
  out=ad.request({'op':'execute','ast':parsed['ast'],'steps':10000,'filename':q.b64(os.fsencode(path)),'request':request});(d/'state.json').write_text(json.dumps(out));actual=q.cli.observe(out['state'],str(path));assert actual['status'] in ('normal','php_error') and all(actual[k]==row['native'][k] for k in ['stdout','stderr','exit_status'])
 finally:
  try:
   if f:f.close()
  finally:
   if ad:ad.close()
 initial='$php_request_run('+checked['fixture']+', 0, '+json.dumps(q.b64(os.fsencode(path)))+', '+rs.request_fixture(request)+')'
 common=['S_initial = '+initial,'S = $review_find(S_initial[.COMPLETION = NORMAL], 200)',f'S.TODO = ({stage} z) :: ptask*','S.ORIGIN = (porigin)','$call_descriptors_valid(S)']
 variants=[('control','S',True,None)]
 if case in ('fetch','forward','bare','implicit'):
  variants += [('wrong-line',f'S[.TODO = ({stage} $(z + 100)) :: ptask*]',False,None),('absent-origin','S[.ORIGIN = eps]',False,None),('legacy-stage','S[.TODO = RETURN_NULL :: ptask*]' if stage=='RETURN_REF_NULL' else 'S[.TODO = (RETURN_VALUE z) :: ptask*]',False,None)]
 if case=='value':
  common+=['S.GLOBALTABLE = (psymboltable)','$lookup(psymboltable.ENV, [120]) = (n_x)','n_x <- S.REFCELLS']
  variants += [('arbitrary-known','S[.RESULT = KNOWN (PINT 99)]',True,'[49,50]'),('arbitrary-reference','S[.RESULT = REFERENCE n_x]',True,'[51,50]'),('deferred-variable','S[.RESULT = VARIABLE ([120]) 1]',False,None),('wrapped-variable','S[.TODO = (AT porigin (RETURN_REF_VALUE z)) :: ptask*][.RESULT = VARIABLE ([120]) 1]',False,None),('origin-variable','S[.TODO = (ORIGIN_RETURN (porigin)) :: (RETURN_REF_VALUE z) :: ptask*][.RESULT = VARIABLE ([120]) 1]',False,None)]
 if case=='globals':variants += [('wrong-source-class','S[.TODO = (RETURN_REF_FETCH z) :: ptask*]',False,None)]
 if case=='demand':
  common+=['S.CURRENT = (pcallcontext)','pcallcontext.CALLSITE = (PORIGIN n_unit pcpath)','S.FRAMES = pframe :: pframe_tail*','pframe.ORIGIN = pcallcontext.CALLSITE','pcpath_unused = [PCINDEX 3, PCFIELD 0]','porigin_unused = PORIGIN n_unit pcpath_unused','$origin_node(S.SOURCES, porigin_unused) = (NExprFuncCall phpType19 phpType6 metadata)','$reference_call_used(S, porigin_unused) = false','$reference_return_used(S) = true']
  variants += [('unused-callsite','S[.CURRENT = (pcallcontext[.CALLSITE = (porigin_unused)])]',False,None)]
 for name,changed,valid,output in variants:
  checks=common+['S_changed = '+changed,'$heap_valid($heap_graph(S_changed))','$call_descriptors_valid(S_changed) = '+str(valid).lower(),'S_zero = $drive(S_changed, 0)','S_full = $drive(S_changed, 10000)']
  if valid:
   checks+=['S_zero.COMPLETION = BUDGET','S_full.COMPLETION = '+('THROWN "TypeError" n_message* 2' if case=='fetch' else 'NORMAL'),'$review_outputs(S_full.EVENTS) = '+(output or str(list(q.t.base64.b64decode(row['native']['stdout'])))),'$heap_valid($heap_graph(S_full))','$call_descriptors_valid(S_full)']
   if case=='value':checks+=['$review_diagnostics(S_full.EVENTS) = [DIAGNOSTIC "Notice" $ptascii("Only variable references should be returned by reference") 1]']
  else:checks+=['S_zero.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"','S_full.COMPLETION = S_zero.COMPLETION']
  fixture=d/(name+'.watsup');fixture.write_text(PREFIX.replace('STAGE',stage)+'\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+c+'\n' for c in checks));cmd=[str(runner),*map(str,modules),str(fixture)];(d/(name+'.command.json')).write_text(json.dumps(cmd))
  try:r=subprocess.run(cmd,capture_output=True,timeout=60)
  except subprocess.TimeoutExpired as e:
   (d/(name+'.stdout')).write_bytes(e.stdout or b'');(d/(name+'.stderr')).write_bytes(e.stderr or b'');(d/(name+'.status.json')).write_text(json.dumps({'status':'timeout'}));raise
  (d/(name+'.stdout')).write_bytes(r.stdout);(d/(name+'.stderr')).write_bytes(r.stderr);(d/(name+'.status.json')).write_text(json.dumps({'status':'exit','exit_status':r.returncode}));record={'id':case+'/'+name,'assertions':len(checks),'pass':r.returncode==0 and r.stdout.strip()==b'true' and not r.stderr};records.append(record);(D/'results.json').write_text(json.dumps(records,indent=2));print(record,flush=True)
assert before==q.t.syntax_validation.implementation_fingerprint();assert all(sha(R/n)==h for n,h in direct.items())
report={'result':'pass' if all(r['pass'] for r in records) else 'fail','fingerprint':before,'raw':str(D),'source_contexts':len(CASES),'records':records,'assertions':sum(r['assertions'] for r in records)};(D/'report.json').write_text(json.dumps(report,indent=2));(R/'coverage/semantics/reference-return-protocol.json').write_text(json.dumps(report,indent=2));assert report['result']=='pass'
