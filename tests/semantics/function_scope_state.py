#!/usr/bin/env python3
"""Resume actual superglobal frame sources and reject corrupt compiler descriptors."""
from pathlib import Path
import json,sys,base64,tempfile,hashlib,subprocess
D=Path(__file__).resolve().parents[2];sys.path.insert(0,str(D/'tests/semantics'));import request_environment_state as q
out=Path(tempfile.mkdtemp(prefix='scope-state-',dir=D/'.tools'));source=json.loads((D/'coverage/semantics/function-scope.json').read_text());assert source['result']=='pass' and not source['selection'];rows=source['records'];before=q.t.syntax_validation.implementation_fingerprint();assert source['fingerprint']==before;assert all(hashlib.sha256((D/p).read_bytes()).hexdigest()==h for p,h in source['direct_inputs'].items());specs=[D/p for p in json.loads((D/'spec/semantics/modules.json').read_text())];runner=D/'tests/semantics/_build/default/numeric_runner.exe'
f=q.t.Worker([str(q.t.PHP),'-n',*q.t.FLAGS,'-d','extension='+str(D/'.tools/php-file.so'),str(D/'frontend/worker.php')]);a=q.t.Worker([str(D/'_build/default/adapter/main.exe'),str(D)])
inputs={str(p.relative_to(D)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [*specs,runner,Path(__file__)]}
for rel in inputs:
 p=out/'original-inputs'/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((D/rel).read_bytes())
(out/'inputs.json').write_text(json.dumps(inputs,indent=2));records=[]
try:
 for name in ['alias-super-source-dim','dim-write-order','foreach-ref-computed','global-this-dynamic']:
  row=next(r for r in rows if r['id']==name);parsed=f.request({'op':'parse','source':row['source_base64']});c=a.request({'op':'check','ast':parsed['ast'],'fixture':True});call='$php_request_run('+c['fixture']+', 0, '+json.dumps(q.t.byte_base64(row['context']))+', '+q.request_fixture(row['request'])+')' if hasattr(q.t,'byte_base64') else '$php_request_run('+c['fixture']+', 0, '+json.dumps(base64.b64encode(row['context'].encode()).decode())+', '+q.request_fixture(row['request'])+')'
  checks=['S_initial = '+call,'S_initial.COMPLETION = BUDGET','S = S_initial[.COMPLETION = NORMAL]','S_out = $drive(S, 10000)','S_out.COMPLETION = NORMAL','$outputs(S_out.EVENTS) = '+q.d.byte_sequence(base64.b64decode(row['native']['stdout'])),'S_out.FRAMES = eps','S_out.GLOBALTABLE = eps','S_out.CURRENT = eps','S_out.CODE = S.CODE','S_out.HTTPROOTS = S.HTTPROOTS','S_out.ACTIVATED = S.ACTIVATED','$heap_valid($heap_graph(S_out))','$foreach_valid(S_out)']
  if name=='global-this-dynamic':checks[4]='S_out.COMPLETION =/= NORMAL'
  for budget in [*range(41),64,128]:
   checks += [f'S_b{budget} = $drive(S, {budget})',f'$resume_destructuring(S_b{budget}, 1) = $drive(S, {budget+1})',f'$heap_valid($heap_graph(S_b{budget}))',f'$foreach_valid(S_b{budget})',f'S_b{budget}.HTTPROOTS = S.HTTPROOTS']
  for budget in [0,7,20,40,64,128]:checks += [f'$resume_destructuring(S_b{budget}, 10000) = S_out']
  if name!='global-this-dynamic':checks += ['S.CODE = [pcode]','pcode.GLOBALS = pcpath :: pcpath_tail*','$scope_codes_valid(S, S.CODE)','~$scope_codes_valid(S[.CODE = [pcode[.GLOBALS = pcpath_tail*]]], [pcode[.GLOBALS = pcpath_tail*]])','~$scope_codes_valid(S[.CODE = [pcode[.GLOBALS = pcpath :: pcode.GLOBALS]]], [pcode[.GLOBALS = pcpath :: pcode.GLOBALS]])','~$scope_codes_valid(S[.CODE = [pcode[.GLOBALS = ([PCINDEX 999]) :: pcode.GLOBALS]]], [pcode[.GLOBALS = ([PCINDEX 999]) :: pcode.GLOBALS]])']
  if name!='global-this-dynamic':
   checks += ['$origin_node(S.SOURCES, PORIGIN pcode.UNIT ([PCINDEX 0, PCFIELD 0])) = (NExprAssign expression_1 expression_2 metadata)', '~$scope_codes_valid(S[.CODE = [pcode[.GLOBALS = ([PCINDEX 0, PCFIELD 0]) :: pcode.GLOBALS]]], [pcode[.GLOBALS = ([PCINDEX 0, PCFIELD 0]) :: pcode.GLOBALS]])', '$scope_rejected(S[.CODE = [pcode[.GLOBALS = pcpath_tail*]]])', '$scope_rejected(S[.CODE = [pcode[.GLOBALS = pcpath :: pcode.GLOBALS]]])', '$scope_rejected(S[.CODE = [pcode[.GLOBALS = ([PCINDEX 0, PCFIELD 0]) :: pcode.GLOBALS]]])']
  fixture=out/(name+'.watsup');fixture.write_text(q.PREFIX+'\ndec $scope_rejected(pstate) : bool\ndef $scope_rejected(S) = true\n  -- if S_bad = $scope_check(S)\n  -- if S_bad.COMPLETION = UNSUPPORTED "invalid compiled global designation"\n  -- if S_bad.TODO = eps\n'+'\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+x+'\n' for x in checks));records.append({'id':name,'source':row,'checked':c,'fixture':str(fixture),'assertions':len(checks)})
finally:f.close();a.close()
fixture=out/'callback.watsup';fixture.write_text('dec $test_request() : prequest\ndef $test_request() = {ENV eps, ARGV eps, FILE ([120]), SECONDS 0, MICROSECONDS 0, VARIABLES eps, JIT true, CWD eps}\ndec $main() : bool\ndef $main() = true\n  -- if S_main = $write_name($initial_state(NORMAL)[.REQUEST = ($test_request())], [95,69,78,86], PINT 1)\n  -- if S_alias = $bind_reference($acquire_name(S_main, [95,69,78,86]), [97])\n  -- if S_local = $write_name($save_frame(S_alias), [95,69,78,86], PINT 2)\n  -- if S_out = $request_bind_global(S_local, [95,69,78,86], PINT 3)\n  -- if S_out.ENV = S_local.ENV\n  -- if S_out.CVS = S_local.CVS\n  -- if S_out.SYMBOLS = S_local.SYMBOLS\n  -- if S_out.GLOBALTABLE = (psymboltable)\n  -- if $lookup(psymboltable.ENV, [95,69,78,86]) = (2)\n  -- if $lookup(psymboltable.ENV, [97]) = (0)\n  -- if S_out.STORE = [DEFINED (PINT 1), DEFINED (PINT 2), DEFINED (PINT 3)]\n  -- if S_out.REFCELLS = [0]\n  -- if $heap_valid($heap_graph(S_out))\n');records.append({'id':'callback','fixture':str(fixture),'assertions':13});
(out/'records.json').write_text(json.dumps(records,indent=2));print(out,flush=True)
for row in records:
 command=[str(runner),*map(str,specs),row['fixture']];p=out/row['id'];p.with_suffix('.command.json').write_text(json.dumps(command))
 try:
  run=subprocess.run(command,capture_output=True,timeout=180);status=run.returncode;stdout=run.stdout;stderr=run.stderr
 except subprocess.TimeoutExpired as e:status='timeout';stdout=e.stdout or b'';stderr=e.stderr or b''
 p.with_suffix('.stdout').write_bytes(stdout);p.with_suffix('.stderr').write_bytes(stderr);row['status']=status;row['pass']=status==0 and stdout.strip()==b'true' and not stderr;print(row['id'],row['pass'],stderr[:1000],flush=True);(out/'results.json').write_text(json.dumps(records,indent=2))
assert all(hashlib.sha256((D/p).read_bytes()).hexdigest()==h for p,h in inputs.items())
assert before==q.t.syntax_validation.implementation_fingerprint()
report={'result':'pass' if all(r['pass'] for r in records) else 'fail','fingerprint':before,'records':records,'raw':str(out)}
(out/'report.json').write_text(json.dumps(report,indent=2))
if report['result']=='pass':(D/'coverage/semantics/function-scope-state.json').write_text(json.dumps(report,indent=2))
raise SystemExit(0 if report['result']=='pass' else 1)
