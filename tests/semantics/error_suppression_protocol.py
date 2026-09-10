#!/usr/bin/env python3
"""Actual suppression scope/source tasks, signed C-int masks and value controls."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,tempfile
R=Path(__file__).resolve().parents[2];K=R;sys.path.insert(0,str(R/'tests/semantics'))
import function_scope as fs
import request_environment as q
import request_environment_state as rs
from recorded_worker import Worker
D=Path(tempfile.mkdtemp(prefix='error-suppression-protocol-',dir=R/'.tools'));print(D,flush=True)
(D/'producer.py').write_bytes(Path(__file__).read_bytes());before=q.t.syntax_validation.implementation_fingerprint()
modules=[R/n for n in json.loads((R/'spec/semantics/modules.json').read_text())];runner=R/'tests/semantics/_build/default/numeric_runner.exe';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
paths=[*modules,runner,R/'_build/default/adapter/main.exe',q.t.PHP,R/'.tools/php-file.so',R/'tests/semantics/recorded_worker.py'];direct={str(p.relative_to(R)):sha(p) for p in paths}
(D/'inputs.json').write_text(json.dumps({'fingerprint':before,'direct':direct},indent=2))
for p in paths:
 o=D/'original-inputs'/p.relative_to(R);o.parent.mkdir(parents=True,exist_ok=True);o.write_bytes(p.read_bytes())
CASES={
 'default':b'<?php\nconst C="2x";function f($x=C+1){echo $x;}\n@f();f();echo $missing;',
 'variable':b'<?php echo @$missing;echo $other,"DONE";',
}
records=[]
for case,source in CASES.items():
 d=D/case;d.mkdir();path=d/'source.php';path.write_bytes(source);entries=[b'LC_ALL=C',b'TZ=UTC',b'FIRST=one'];payload=d/'request.input';payload.write_bytes(q.packet(1700000000,125000,entries))
 request={'env':[[q.b64(k),q.b64(v)] for k,v in (e.split(b'=',1) for e in entries)],'argv':[q.b64(os.fsencode(path))],'file':q.b64(os.fsencode(path)),'seconds':'1700000000','microseconds':125000,'variables':q.b64(b'EGPCS'),'jit':True,'cwd':q.b64(os.fsencode(d))}
 old={'id':case,'source_base64':q.b64(source),'context':str(path),'request':request,'native':fs.native(path,payload,d)};(d/'original.json').write_text(json.dumps(old,indent=2));f=ad=None
 try:
  f=Worker([str(q.t.PHP),'-n',*q.t.FLAGS,'-d','extension='+str(R/'.tools/php-file.so'),str(R/'frontend/worker.php')],d/'frontend-wire');ad=Worker([str(R/'_build/default/adapter/main.exe'),str(R)],d/'adapter-wire')
  parsed=f.request({'op':'parse','source':old['source_base64']});assert parsed['accepted'];checked=ad.request({'op':'check','ast':parsed['ast'],'fixture':True});(d/'checked.json').write_text(json.dumps(checked))
  out=ad.request({'op':'execute','ast':parsed['ast'],'steps':10000,'filename':q.b64(os.fsencode(path)),'request':request});(d/'state.json').write_text(json.dumps(out));actual=q.cli.observe(out['state'],str(path));assert actual['status']=='normal' and all(actual[k]==old['native'][k] for k in ['stdout','stderr','exit_status'])
 finally:
  try:
   if f:f.close()
  finally:
   if ad:ad.close()
 initial='$php_request_run('+checked['fixture']+', 0, '+json.dumps(q.b64(os.fsencode(path)))+', '+rs.request_fixture(request)+')'
 for mode in (('end','frame') if case=='default' else ('root',)):
  PREFIX='''dec $review_stage(pstate) : bool
   def $review_stage(S) = true -- if S.TODO = (SILENCE_END porigin) :: ptask*
   def $review_stage(S) = false -- otherwise
   dec $review_find(pstate, nat) : pstate
   def $review_find(S, n) = S -- if $review_stage(S)
   def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)
     -- if ~$review_stage(S)
     -- if $(n > 0)
     -- if n_rest = $(n - 1)
     -- if S_next = $drive_steps(S, 1)
  '''
  common=['S_initial = '+initial,'S = $review_find(S_initial[.COMPLETION = NORMAL], 200)','S.TODO = (SILENCE_END porigin) :: ptask*','S.SILENCES = [SILENCE porigin i_saved]','S.REPORTING = 4437','i_saved = 30719','S.ORIGIN = (porigin)','porigin_child = $origin_child((porigin), [PCFIELD 0])','porigin_child = (porigin_bad)','$call_descriptors_valid(S)']
  variants=[('control','S',True,30719),('missing-scope','S[.SILENCES = eps]',False,None),('wrong-scope-source','S[.SILENCES = [SILENCE porigin_bad i_saved]]',False,None),('wrong-end-source','S[.TODO = (SILENCE_END porigin_bad) :: ptask*]',False,None),('wrong-current-origin','S[.ORIGIN = (porigin_bad)]',False,None),('huge-current-mask','S[.REPORTING = 2147483648]',False,None),('huge-saved-mask','S[.SILENCES = [SILENCE porigin 2147483648]]',False,None),('negative-outside-mask','S[.REPORTING = $(-2147483649)]',False,None),('minimum-live-mask','S[.REPORTING = $(-2147483648)]',True,-2147483648),('maximum-live-mask','S[.REPORTING = 2147483647]',True,2147483647),('arbitrary-live-mask','S[.REPORTING = 2]',True,2),('arbitrary-saved-mask','S[.SILENCES = [SILENCE porigin $(-1)]]',True,-1),('fatal-only-saved-mask','S[.SILENCES = [SILENCE porigin 0]]',True,4437),('arbitrary-owning-value','S[.RESULT = KNOWN (PINT 99)]',True,30719)]
  if mode=='frame':
   PREFIX=PREFIX.replace('S.TODO = (SILENCE_END porigin) :: ptask*','S.TODO = (DEFAULT_BIND porigin n) :: ptask*')
   common=['S_initial = '+initial,'S = $review_find(S_initial[.COMPLETION = NORMAL], 200)','S.TODO = (DEFAULT_BIND porigin n) :: ptask*','S.SILENCES = eps','S.FRAMES = pframe :: pframe_tail*','pframe.SILENCES = [SILENCE porigin_silence i_saved]','S.REPORTING = 4437','i_saved = 30719','porigin_child = $origin_child((porigin_silence), [PCFIELD 0])','porigin_child = (porigin_bad)','$call_descriptors_valid(S)']
   variants=[('saved-control','S',True,None),('saved-missing-scope','S[.FRAMES = pframe[.SILENCES = eps] :: pframe_tail*]',False,None),('saved-wrong-source','S[.FRAMES = pframe[.SILENCES = [SILENCE porigin_bad i_saved]] :: pframe_tail*]',False,None),('saved-huge-mask','S[.FRAMES = pframe[.SILENCES = [SILENCE porigin_silence 2147483648]] :: pframe_tail*]',False,None),('saved-arbitrary-mask','S[.FRAMES = pframe[.SILENCES = [SILENCE porigin_silence $(-1)]] :: pframe_tail*]',True,None),('cross-frame-scope','S[.SILENCES = pframe.SILENCES][.FRAMES = pframe[.SILENCES = eps] :: pframe_tail*]',False,None)]
  if mode=='root':
   PREFIX+='dec $review_match(pcodeexpr, pcpath) : bool\ndef $review_match(CODEEXPR pcpath z b, pcpath) = true\ndef $review_match(pcodeexpr, pcpath) = false -- otherwise\ndec $review_change(pcodeexpr*, pcpath) : pcodeexpr*\ndef $review_change(eps, pcpath) = eps\ndef $review_change((CODEEXPR pcpath z b) :: pcodeexpr*, pcpath) = (CODEEXPR pcpath $(z + 100) b) :: pcodeexpr*\ndef $review_change(pcodeexpr :: pcodeexpr_tail*, pcpath) = pcodeexpr :: $review_change(pcodeexpr_tail*, pcpath) -- if ~$review_match(pcodeexpr, pcpath)\n'
   common+=['S.CODE = [pcode]','porigin = PORIGIN n_unit pcpath_root','porigin_bad = PORIGIN n_unit pcpath_child','S.RESULT = VARIABLE n_name* z','S.EVENTS = eps']
   variants=[('variable-control','S',True,30719),('unit-suppression-line','S[.CODE = [pcode[.EXPRESSIONS = $review_change(pcode.EXPRESSIONS, pcpath_root)]]]',False,None),('unit-child-line','S[.CODE = [pcode[.EXPRESSIONS = $review_change(pcode.EXPRESSIONS, pcpath_child)]]][.REPORTING = 2]',False,None)]
  for name,change,valid,mask in variants:
   expected=valid
   checks=common+['S_changed = '+change,'$heap_valid($heap_graph(S_changed))','$call_descriptors_valid(S_changed) = '+str(expected).lower(),'S_zero = $drive(S_changed, 0)','S_zero.COMPLETION = '+('BUDGET' if expected else 'UNSUPPORTED "invalid compiled function descriptor"')]
   if valid and mask is not None:
    checks+=['S_next = $drive_steps(S_changed, 1)','S_next.REPORTING = '+('$(%d)'%mask if mask<0 else str(mask)),'S_next.SILENCES = eps','S_full = $drive(S_changed, 10000)','S_full.COMPLETION = NORMAL','S_full.REPORTING = '+('$(%d)'%mask if mask<0 else str(mask)),'$heap_valid($heap_graph(S_full))']
   if valid and mask is None:
    checks+=['S_full = $drive(S_changed, 10000)','S_full.COMPLETION = NORMAL','S_full.REPORTING = '+('$(-1)' if name=='saved-arbitrary-mask' else '30719'),'$heap_valid($heap_graph(S_full))']
   if valid:
    checks+=['S_full.SILENCES = eps','S_full.FRAMES = eps','$call_descriptors_valid(S_full)']
   else:
    checks+=['S_full = $drive(S_changed, 10000)','S_full.COMPLETION = S_zero.COMPLETION']
   if name=='arbitrary-owning-value':checks+=['S_next.RESULT = KNOWN (PINT 99)']
   if name=='variable-control':checks+=['S_next.RESULT = KNOWN PNULL','S_next.EVENTS = eps']
   fixture=d/(name+'.watsup');fixture.write_text(PREFIX+'\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+c+'\n' for c in checks));cmd=[str(runner),*map(str,modules),str(fixture)];(d/(name+'.command.json')).write_text(json.dumps(cmd))
   try:r=subprocess.run(cmd,capture_output=True,timeout=60)
   except subprocess.TimeoutExpired as e:
    (d/(name+'.stdout')).write_bytes(e.stdout or b'');(d/(name+'.stderr')).write_bytes(e.stderr or b'');(d/(name+'.status.json')).write_text(json.dumps({'status':'timeout'}));raise
   (d/(name+'.stdout')).write_bytes(r.stdout);(d/(name+'.stderr')).write_bytes(r.stderr);(d/(name+'.status.json')).write_text(json.dumps({'status':'exit','exit_status':r.returncode}));row={'id':case+'/'+name,'contract_valid':valid,'assertions':len(checks),'pass':r.returncode==0 and r.stdout.strip()==b'true' and not r.stderr};records.append(row);(D/'results.json').write_text(json.dumps(records,indent=2));print(row,flush=True)
assert before==q.t.syntax_validation.implementation_fingerprint();assert all(sha(R/n)==h for n,h in direct.items())
report={'result':'pass' if all(r['pass'] for r in records) else 'fail','fingerprint':before,'raw':str(D),'source_contexts':len(CASES),'records':records,'assertions':sum(r['assertions'] for r in records)};(D/'report.json').write_text(json.dumps(report,indent=2));(R/'coverage/semantics/error-suppression-protocol.json').write_text(json.dumps(report,indent=2));assert report['result']=='pass'
