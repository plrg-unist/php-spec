from pathlib import Path
import json,os,subprocess,sys,tempfile
R=Path(__file__).resolve().parents[2];K=R;sys.path.insert(0,str(K/'tests/semantics'))
import request_environment as q
import function_scope as fs
import request_environment_state as rs
from recorded_worker import Worker
D=Path(tempfile.mkdtemp(prefix='review10-variadic-protocol-',dir=R/'.tools'));(D/'producer.py').write_bytes(Path(__file__).read_bytes());before=q.t.syntax_validation.implementation_fingerprint();print(D,flush=True)
source=b'<?php\n$a="1";$bad=[];function f(int &...$xs){echo "BODY";}\n@f($a,$a,$bad);echo "AFTER";'
p=D/'source.php';p.write_bytes(source);entries=[b'LC_ALL=C',b'TZ=UTC',b'FIRST=one'];payload=D/'request.input';payload.write_bytes(q.packet(1700000000,125000,entries));request={'env':[[q.b64(k),q.b64(v)] for k,v in(e.split(b'=',1)for e in entries)],'argv':[q.b64(os.fsencode(p))],'file':q.b64(os.fsencode(p)),'seconds':'1700000000','microseconds':125000,'variables':q.b64(b'EGPCS'),'jit':True,'cwd':q.b64(os.fsencode(D))};(D/'request.json').write_text(json.dumps(request));row={'source_base64':q.b64(source),'context':str(p),'request':request,'native':fs.native(p,payload,D)};(D/'original.json').write_text(json.dumps(row,indent=2));(D/'inputs.json').write_text(json.dumps({'candidate':str(K),'fingerprint':before},indent=2));f=a=None
try:
 f=Worker([str(q.t.PHP),'-n',*q.t.FLAGS,'-d','extension='+str(K/'.tools/php-file.so'),str(K/'frontend/worker.php')],D/'frontend-wire');a=Worker([str(K/'_build/default/adapter/main.exe'),str(K)],D/'adapter-wire');parsed=f.request({'op':'parse','source':row['source_base64']});assert parsed['accepted'];checked=a.request({'op':'check','ast':parsed['ast'],'fixture':True});(D/'checked.json').write_text(json.dumps(checked));execute={'op':'execute','ast':parsed['ast'],'steps':10000,'filename':q.b64(os.fsencode(row['context'])),'request':request};(D/'execute.json').write_text(json.dumps(execute));result=a.request(execute);(D/'state.json').write_text(json.dumps(result));actual=q.cli.observe(result['state'],row['context']);assert actual['status']=='php_error' and all(actual[k]==row['native'][k] for k in ['stdout','stderr','exit_status'])
finally:
 try:
  if f:f.close()
 finally:
  if a:a.close()
initial='$php_request_run('+checked['fixture']+', 0, '+json.dumps(q.b64(os.fsencode(row['context'])))+', '+rs.request_fixture(row['request'])+')'
prefix='''dec $review_stage(pstate) : bool
def $review_stage(S) = true -- if S.TODO = [VARIADIC_RECEIVE porigin 2]
def $review_stage(S) = false -- otherwise
dec $review_find(pstate, nat) : pstate
def $review_find(S, n) = S -- if $review_stage(S)
def $review_find(S, n) = $review_find(S_next[.COMPLETION = NORMAL], n_rest)
  -- if ~$review_stage(S)
  -- if $(n > 0)
  -- if n_rest = $(n - 1)
  -- if S_next = $drive_steps(S, 1)
'''
common=['S_initial = '+initial,'S = $review_find(S_initial[.COMPLETION = NORMAL], 200)','S.TODO = [VARIADIC_RECEIVE porigin 2]','S.CURRENT = (pcallcontext)','pcallcontext.FUNCTION = porigin','pcallcontext.CALLSITE = (porigin_call)','pcallcontext.EXTRA = [REFERENCE n_shared, REFERENCE n_shared, REFERENCE n_bad]','S.STORE[n_shared] = DEFINED (PINT 1)','$lookup(S.ENV, [120, 115]) = (n_tail)','S.STORE[n_tail] = DEFINED (PARRAY n_array)','$call_descriptors_valid(S)']
variants=[('control','S',True),('receive-wrong-function','S[.TODO = [VARIADIC_RECEIVE porigin_call 2]]',False),('receive-wrong-origin','S[.ORIGIN = (porigin_call)]',False),('receive-skip-last','S[.TODO = [VARIADIC_RECEIVE porigin 3]]',False),('receive-outside-arguments','S[.TODO = [VARIADIC_RECEIVE porigin 99]]',False),('receive-rewind-tail','S[.TODO = [VARIADIC_RECEIVE porigin 0]]',False),('receive-reset-tail','S[.TODO = [VARIADIC_BEGIN porigin]]',False),('receive-tail-not-array','S[.STORE = $set_cell(S.STORE, n_tail, DEFINED (PINT 99))]',False),('receive-arbitrary-result','S[.RESULT = KNOWN (PINT 99)]',True),('receive-shared-value-evolution','S[.STORE = $set_cell(S.STORE, n_shared, DEFINED (PINT 7))]',True)]
variants += [('receive-nonpacked-key','S[.ARRAYS = $array_replace(S.ARRAYS, n_array, $array_insert($array_insert($array_empty(), KINT 0, ALIAS n_shared), KINT 2, ALIAS n_shared))]',False),('receive-wrong-next','S[.ARRAYS = $array_replace(S.ARRAYS, n_array, S.ARRAYS[n_array][.NEXT = 3])]',False),('receive-arbitrary-collected-value','S[.ARRAYS = $array_replace(S.ARRAYS, n_array, $array_insert(S.ARRAYS[n_array], KINT 0, DIRECT (PINT 99)))]',True),('receive-extra-queue','S[.TODO = [(VARIADIC_RECEIVE porigin 2), DISCARD]]',False)]
groups=[(prefix,common,variants)]
prefix=prefix.replace('S.TODO = [VARIADIC_RECEIVE porigin 2]','S.TODO = [VARIADIC_BEGIN porigin]')
common=['S_initial = '+initial,'S = $review_find(S_initial[.COMPLETION = NORMAL], 200)','S.TODO = [VARIADIC_BEGIN porigin]','S.CURRENT = (pcallcontext)','pcallcontext.FUNCTION = porigin','pcallcontext.CALLSITE = (porigin_call)','$call_descriptors_valid(S)']
variants=[('begin-control','S',True),('begin-wrong-function','S[.TODO = [VARIADIC_BEGIN porigin_call]]',False),('begin-wrong-origin','S[.ORIGIN = (porigin_call)]',False),('begin-tail-already-defined','$write_name(S, [120, 115], PINT 99)',False),('begin-before-array','S[.TODO = [VARIADIC_RECEIVE porigin 0]]',False),('begin-arbitrary-result','S[.RESULT = KNOWN (PINT 99)]',True)]
groups.append((prefix,common,variants))
modules=[K/p for p in json.loads((K/'spec/semantics/modules.json').read_text())];runner=K/'tests/semantics/_build/default/numeric_runner.exe';records=[]
for prefix,common,variants in groups:
 for name,change,valid in variants:
  expected=valid;checks=common+['S_changed = '+change,'$heap_valid($heap_graph(S_changed))','$call_descriptors_valid(S_changed) = '+str(expected).lower(),'S_zero = $drive(S_changed, 0)','S_zero.COMPLETION = '+('BUDGET' if expected else 'UNSUPPORTED "invalid compiled function descriptor"')]
  checks+=['S_full = $drive(S_changed, 10000)','S_full.COMPLETION = '+('THROWN "TypeError" n_message* 2' if valid else 'UNSUPPORTED "invalid compiled function descriptor"')]
  if valid:checks+=['S_full.REPORTING = 30719','S_full.FRAMES = eps','S_full.CURRENT = eps','S_full.HELD = eps','S_full.SILENCES = eps','$heap_valid($heap_graph(S_full))']
  fixture=D/(name+'.watsup');fixture.write_text(prefix+'\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+c+'\n' for c in checks));cmd=[str(runner),*map(str,modules),str(fixture)];(D/(name+'.command.json')).write_text(json.dumps(cmd));z=subprocess.run(cmd,capture_output=True,timeout=60);(D/(name+'.stdout')).write_bytes(z.stdout);(D/(name+'.stderr')).write_bytes(z.stderr);(D/(name+'.status.json')).write_text(json.dumps({'status':'exit','exit_status':z.returncode}));item={'id':name,'valid':valid,'assertions':len(checks),'pass':z.returncode==0 and z.stdout.strip()==b'true' and not z.stderr};records.append(item);(D/'results.json').write_text(json.dumps(records,indent=2));print(item,flush=True)
assert before==q.t.syntax_validation.implementation_fingerprint();report={'result':'pass' if all(r['pass'] for r in records) else 'fail','fingerprint':before,'raw':str(D),'controls':len(records),'assertions':sum(r['assertions'] for r in records),'fresh_native_contexts':1,'records':records};(D/'report.json').write_text(json.dumps(report,indent=2));assert report['result']=='pass';(R/'coverage/semantics/variadic-protocol.json').write_text(json.dumps(report,indent=2));print(D,report['controls'],report['assertions'])
