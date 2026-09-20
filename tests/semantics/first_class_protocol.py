"""Paused first-class conversion, call-context, and ownership guards."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,tempfile
R=Path(__file__).resolve().parents[2]
O=Path(tempfile.mkdtemp(prefix='first-class-protocol-'))
sys.path.insert(0,str(R/'tests/semantics'))
import request_environment as q
from recorded_worker import Worker
source=O/'selected-wrapper-rebind.php'
source.write_text(json.loads((R/'tests/semantics/first_class_cases.json').read_text())['selected-wrapper-rebind'])
before=q.t.syntax_validation.implementation_fingerprint()
f=a=None
try:
 f=Worker([str(q.t.PHP),'-n',*q.t.FLAGS,'-d','extension='+str(R/'.tools/php-file.so'),str(R/'frontend/worker.php')],O/'frontend-wire')
 a=Worker([str(R/'_build/default/adapter/main.exe'),str(R)],O/'adapter-wire')
 parsed=f.request({'op':'parse','source':q.b64(source.read_bytes())});assert parsed['ok'] and parsed['accepted']
 checked=a.request({'op':'check','ast':parsed['ast'],'fixture':True});assert checked['ok'];(O/'checked.json').write_text(json.dumps(checked))
finally:
 try:
  if f:f.close()
 finally:
  if a:a.close()
initial='$php_run('+checked['fixture']+', 0, '+json.dumps(q.b64(str(source).encode()))+')'
prefix='''
dec $review_stage(pstate, nat) : bool
def $review_stage(S, 0) = true
  -- if S.TODO = (FIRSTCLASS_CONVERT porigin z_init z_convert) :: ptask*
def $review_stage(S, 1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.INSTANCE = (n)
def $review_stage(S, 2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = [105,110,110,101,114]
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.CONTEXT = (pcallcontext_saved)
  -- if pcallcontext_saved.INSTANCE = (n)
def $review_stage(S, n) = false -- otherwise
dec $review_seek(pstate, nat, nat) : pstate
def $review_seek(S, n_stage, n_left) = S -- if $review_stage(S, n_stage)
def $review_seek(S, n_stage, n_left) = $review_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, n_rest)
  -- if ~$review_stage(S, n_stage)
  -- if $(n_left > 0)
  -- if n_rest = $(n_left - 1)
dec $outputs(pevent*) : nat*
def $outputs(eps) = eps
def $outputs((OUTPUT n*) :: pevent*) = n* ++ $outputs(pevent*)
def $outputs((WARNING n* z) :: pevent*) = $outputs(pevent*)
def $outputs((DIAGNOSTIC text n* z) :: pevent*) = $outputs(pevent*)
'''
common=['S_initial = '+initial,'S_pause = $review_seek(S_initial[.COMPLETION = NORMAL], __STAGE__, 256)', 'S = S_pause[.COMPLETION = NORMAL]','$call_descriptors_valid(S)','$heap_valid($heap_graph(S))','$drive(S, 1) = $drive_steps(S, 1)','S_done = $drive(S, 1000)','S_done.COMPLETION = NORMAL','$outputs(S_done.EVENTS) = [55]']
cases=[[
 'S.TODO = (FIRSTCLASS_CONVERT porigin z_init z_convert) :: ptask_tail*',
 '$firstclass_task_valid(S, porigin, z_init, z_convert)',
 '~$call_tasks_valid(S, (FIRSTCLASS_CONVERT porigin $(z_init + 1) z_convert) :: ptask_tail*)',
 '~$call_tasks_valid(S, (FIRSTCLASS_CONVERT porigin z_init $(z_convert + 1)) :: ptask_tail*)',
 '~$firstclass_task_valid(S[.ORIGIN = (PORIGIN 0 eps)], PORIGIN 0 eps, z_init, z_convert)',
], [
 'S.CURRENT = (pcallcontext)','pcallcontext.INSTANCE = (n)',
 'S.OBJECTS[n] = NAMEDCLOSURE porigin','$closure_callable(S, n)',
 '$node_children(S, HOBJECT n) = eps',
 '~$closure_live_object_valid(S[.OBJECTS = $object_set(S.OBJECTS, n, NAMEDCLOSURE (PORIGIN 0 eps))], n)',
 '~$closure_callable(S[.CALLABLES = eps], n)',
 '~$call_current_valid(S[.CURRENT = (pcallcontext[.FUNCTION = PORIGIN 0 eps])])',
 '~$call_current_valid(S[.CURRENT = (pcallcontext[.INSTANCE = (99999)])])',
], [
 'S.FRAMES = pframe :: pframe_tail*','pframe.CONTEXT = (pcallcontext)',
 'pcallcontext.INSTANCE = (n)','$closure_callable(S, n)',
 'n_owners = $heap_owners($heap_graph(S), HOBJECT n)', '$(n_owners > 0)',
 '~$call_frames_valid(S, (pframe[.CONTEXT = (pcallcontext[.FUNCTION = PORIGIN 0 eps])]) :: pframe_tail*)',
 '~$call_frames_valid(S, (pframe[.CONTEXT = (pcallcontext[.INSTANCE = (99999)])]) :: pframe_tail*)',
]]
modules=[str(R/p) for p in json.loads((R/'spec/semantics/modules.json').read_text())];records=[]
for i,extra in enumerate(cases):
 checks=[x.replace('__STAGE__',str(i)) for x in common]+extra
 fixture=O/(str(i)+'.watsup');fixture.write_text(prefix+'\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+x+'\n' for x in checks))
 command=[str(R/'tests/semantics/_build/default/numeric_runner.exe'),*modules,str(fixture)];(O/(str(i)+'.command.json')).write_text(json.dumps(command))
 try: z=subprocess.run(command,capture_output=True,timeout=300)
 except subprocess.TimeoutExpired as e:
  (O/(str(i)+'.stdout')).write_bytes(e.stdout or b'');(O/(str(i)+'.stderr')).write_bytes(e.stderr or b'');(O/(str(i)+'.status.json')).write_text(json.dumps({'status':'timeout','seconds':300}));raise
 (O/(str(i)+'.stdout')).write_bytes(z.stdout);(O/(str(i)+'.stderr')).write_bytes(z.stderr);(O/(str(i)+'.status.json')).write_text(json.dumps({'status':'exit','exit_status':z.returncode}))
 row={'stage':i,'assertions':len(checks),'pass':z.returncode==0 and z.stdout==b'true\n' and not z.stderr};records.append(row);(O/'records.json').write_text(json.dumps(records,indent=2));print(row,flush=True)
 assert row['pass'],z.stderr
assert before==q.t.syntax_validation.implementation_fingerprint()
assert sum(r['assertions'] for r in records)==49
print('PASS first-class protocol: 3 stages, 49 assertions',flush=True)
shutil.rmtree(O)
