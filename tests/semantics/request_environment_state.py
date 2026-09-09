#!/usr/bin/env python3
"""Dense request/GLOBALS resumption and independent HTTP-root ownership checks."""
from pathlib import Path
import base64,json,subprocess,tempfile
import static_types as t
import destructuring as d
import isset_empty as ie
ROOT=Path(__file__).resolve().parents[2]
SELECT=['ownership/pg-reference-cow','ownership/global-reference-cycle','ownership/global-foreach-cv-unset','ownership/global-coalesce-ref-name','ownership/server-argv-cow','ownership/global-ref-target-cow']
PREFIX=d.PREFIX+ie.PREFIX+'''
dec $request_test_root((preqbytes, pvalue)*, preqbytes) : pvalue?
def $request_test_root(eps, preqbytes) = eps
def $request_test_root((preqbytes, pvalue) :: (preqbytes_tail, pvalue_tail)*, preqbytes) = (pvalue)
def $request_test_root((preqbytes_other, pvalue) :: (preqbytes_tail, pvalue_tail)*, preqbytes) = $request_test_root((preqbytes_tail, pvalue_tail)*, preqbytes) -- if preqbytes_other =/= preqbytes
'''
def request_fixture(q):
 env='['+', '.join('('+d.byte_sequence(base64.b64decode(k))+', '+d.byte_sequence(base64.b64decode(v))+')' for k,v in q['env'])+']';argv='['+', '.join(d.byte_sequence(base64.b64decode(x)) for x in q['argv'])+']'
 return '{ ENV ('+env+'), ARGV ('+argv+'), FILE '+d.byte_sequence(base64.b64decode(q['file']))+', SECONDS ('+q['seconds']+'), MICROSECONDS '+str(q['microseconds'])+', VARIABLES '+d.byte_sequence(base64.b64decode(q['variables']))+', JIT '+str(q['jit']).lower()+', CWD '+('('+d.byte_sequence(base64.b64decode(q['cwd']))+')' if 'cwd' in q else 'eps')+' }'
def main():
 before=t.syntax_validation.implementation_fingerprint();out=Path(tempfile.mkdtemp(prefix='request-state-',dir=ROOT/'.tools'));source=json.loads((ROOT/'coverage/semantics/request-environment-source.json').read_text());assert source['result']=='pass' and source['fingerprint']==before;records=[];paths=json.loads((ROOT/'spec/semantics/modules.json').read_text());f=t.Worker([str(t.PHP),'-n',*t.FLAGS,'-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')]);a=t.Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)])
 try:
  for i,name in enumerate(SELECT):
   row=next(r for r in source['records'] if r['id']==name);parsed=f.request({'op':'parse','source':row['source_base64']});checked=a.request({'op':'check','ast':parsed['ast'],'fixture':True});q=request_fixture(row['request']);call='$php_request_run('+checked['fixture']+', 0, '+json.dumps(base64.b64encode(row['context'].encode()).decode())+', '+q+')'
   checks=['S_initial = '+call,'S_initial.COMPLETION = BUDGET','S = S_initial[.COMPLETION = NORMAL]','S_out = $drive(S, 10000)','S_out.COMPLETION = NORMAL','$outputs(S_out.EVENTS) = '+d.byte_sequence(base64.b64decode(row['oracle']['stdout'])),'$messages(S_out.EVENTS) = eps','S_out.REQUEST = S.REQUEST','S_out.CVS = S.CVS','S_out.ACTIVATED = S.ACTIVATED','S_out.HTTPROOTS = S.HTTPROOTS','S_out.CODE = S.CODE','S_out.POOLS = S.POOLS','S_out.TODO = eps','S_out.ORIGIN = eps','S_out.HELD = eps','S_out.ITERATORS = eps','$heap_valid($heap_graph(S_out))','$foreach_valid(S_out)']
   if name=='ownership/pg-reference-cow':
    checks+=['$request_test_root(S_out.HTTPROOTS, [95,71,69,84]) = (PARRAY n_get)','S_out.ARRAYS[n_get].ITEMS = eps','$lookup(S_out.ENV, [95,71,69,84]) = eps']
   for budget in range(65):
    checks += [f'S_b{budget} = $drive(S, {budget})',f'$resume_destructuring(S_b{budget}, 1) = $drive(S, {budget+1})',f'$heap_valid($heap_graph(S_b{budget}))',f'$foreach_valid(S_b{budget})',f'S_b{budget}.REQUEST = S.REQUEST',f'S_b{budget}.HTTPROOTS = S.HTTPROOTS']
   checks += [f'$resume_destructuring(S_b{b}, 10000) = S_out' for b in (0,1,7,16,32,64)]
   for budget in (128,256,512):
    checks += [f'S_l{budget} = $drive(S, {budget})',f'$heap_valid($heap_graph(S_l{budget}))',f'$foreach_valid(S_l{budget})',f'S_l{budget}.REQUEST = S.REQUEST',f'S_l{budget}.HTTPROOTS = S.HTTPROOTS',f'$resume_destructuring(S_l{budget}, 1) = $drive(S, {budget+1})',f'$resume_destructuring(S_l{budget}, 10000) = S_out']
   fixture=out/f'case{i}.watsup';fixture.write_text(PREFIX+'dec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+c+'\n' for c in checks));records.append({'id':name,'source_base64':row['source_base64'],'request':row['request'],'source_evidence':row,'fixture':str(fixture),'assertions':len(checks)})
 finally:f.close();a.close()
 (out/'originals.json').write_text(json.dumps({'fingerprint':before,'records':records},indent=2)+'\n');print(out,flush=True)
 for row in records:
  try:
   run=subprocess.run([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'),*[str(ROOT/n) for n in paths],row['fixture']],capture_output=True,text=True,timeout=300);row['run']={'status':run.returncode,'stdout':run.stdout,'stderr':run.stderr};row['pass']=run.returncode==0 and run.stdout.strip()=='true'
  except subprocess.TimeoutExpired as error:
   row['run']={'status':'tool_timeout','seconds':300,'stdout':(error.stdout or b'').decode(),'stderr':(error.stderr or b'').decode()};row['pass']=False
  (out/'results.json').write_text(json.dumps({'fingerprint':before,'records':records},indent=2)+'\n');print(row['id'],row['pass'],row['run']['stderr'][:500],flush=True)
 assert before==t.syntax_validation.implementation_fingerprint(),'request state inputs changed'
 report={'fingerprint':before,'one_step_budgets':list(range(65))+[128,256,512],'full_resume_budgets':[0,1,7,16,32,64,128,256,512],'result':'pass' if all(r['pass'] for r in records) else 'fail','records':records,'assertions':sum(r['assertions'] for r in records)};(out/'results.json').write_text(json.dumps(report,indent=2)+'\n')
 if report['result']=='pass':(ROOT/'coverage/semantics/request-environment-state.json').write_text(json.dumps(report,indent=2)+'\n')
 return report['result']=='pass'
if __name__=='__main__':raise SystemExit(0 if main() else 1)
