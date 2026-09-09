from pathlib import Path
import hashlib,json,subprocess,sys,tempfile
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tests/semantics'))
import function_scope as scope
from recorded_worker import Worker
q=scope.q
D=Path(tempfile.mkdtemp(prefix='user-constant-context-protocol-',dir=R/'.tools'));source=json.loads((R/'tests/semantics/user_constant_runtime_cases.json').read_text())['line-leading-read-then-warning'].encode();path=D/'source.php';path.write_bytes(source)
mods=[R/p for p in json.loads((R/'spec/semantics/modules.json').read_text())];runner=R/'tests/semantics/_build/default/numeric_runner.exe';inputs={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [*mods,runner,Path(__file__),R/'tests/semantics/recorded_worker.py']}
for p in inputs:
 t=D/'original-inputs'/p;t.parent.mkdir(parents=True,exist_ok=True);t.write_bytes((R/p).read_bytes())
(D/'inputs.json').write_text(json.dumps({'fingerprint':q.t.syntax_validation.implementation_fingerprint(),'files':inputs},indent=2))
f=Worker([str(q.t.PHP),'-n',*q.t.FLAGS,'-d','extension='+str(R/'.tools/php-file.so'),str(R/'frontend/worker.php')],D/'frontend-wire');a=Worker([str(R/'_build/default/adapter/main.exe'),str(R)],D/'adapter-wire')
try:
 parsed=f.request({'op':'parse','source':q.b64(source)});checked=a.request({'op':'check','ast':parsed['ast'],'fixture':True});(D/'checked.json').write_text(json.dumps(checked))
finally:f.close();a.close()
initial='$php_run('+checked['fixture']+', 0, '+json.dumps(q.b64(bytes(path)))+')'
prefix=r'''
dec $constant_test_stage(pstate, nat) : bool
def $constant_test_stage(S, 0) = true -- if S.TODO = (CONSTANT_INIT expression) :: ptask*
def $constant_test_stage(S, 1) = true -- if S.TODO = (CONSTANT_BIND porigin) :: ptask*
def $constant_test_stage(S, 2) = true -- if S.TODO = (CONSTANT_OBSERVE porigin) :: ptask*
def $constant_test_stage(S, 3) = true
  -- if S.CONSTCONTEXT = (pconstantcontext)
  -- if pconstantcontext.FACTS =/= eps
def $constant_test_stage(S, n) = false -- otherwise
dec $constant_test_find(pstate, nat, nat) : pstate
def $constant_test_find(S, n, n_limit) = S -- if $constant_test_stage(S, n)
def $constant_test_find(S, n, n_limit) = $constant_test_find(S_next[.COMPLETION = NORMAL], n, n_rest)
  -- if ~$constant_test_stage(S, n)
  -- if $(n_limit > 0)
  -- if n_rest = $(n_limit - 1)
  -- if S_next = $drive_steps(S, 1)
'''
variants={
'control-init':(0,'S',[]),
'wrong-init-expression':(0,'S[.TODO = (CONSTANT_INIT (NScalarInt (INTEGER 999) eps)) :: ptask*]',['S.TODO = (CONSTANT_INIT expression) :: ptask*']),
'control-bind':(1,'S',[]),
'wrong-bind-origin':(1,'S[.TODO = (CONSTANT_BIND (PORIGIN 0 eps)) :: ptask*]',['S.TODO = (CONSTANT_BIND porigin) :: ptask*']),
'control-observe':(2,'S',[]),
'wrong-observe-origin':(2,'S[.TODO = (CONSTANT_OBSERVE (PORIGIN 0 eps)) :: ptask*]',['S.TODO = (CONSTANT_OBSERVE porigin) :: ptask*']),
'control-context':(3,'S',[]),
'wrong-context-origin':(3,'S[.CONSTCONTEXT = (pconstantcontext[.ORIGIN = PORIGIN 0 eps])]',['S.CONSTCONTEXT = (pconstantcontext)']),
'wrong-context-line':(3,'S[.CONSTCONTEXT = (pconstantcontext[.LINE = 999])]',['S.CONSTCONTEXT = (pconstantcontext)']),
'wrong-fact-origin':(3,'S[.CONSTCONTEXT = (pconstantcontext[.FACTS = (pconstantfact[.ORIGIN = PORIGIN 0 eps]) :: pconstantfact_tail*])]',['S.CONSTCONTEXT = (pconstantcontext)','pconstantcontext.FACTS = pconstantfact :: pconstantfact_tail*']),
'wrong-fact-tag':(3,'S[.CONSTCONTEXT = (pconstantcontext[.FACTS = (pconstantfact[.CLASS = PVSTRING true]) :: pconstantfact_tail*])]',['S.CONSTCONTEXT = (pconstantcontext)','pconstantcontext.FACTS = pconstantfact :: pconstantfact_tail*']),
'duplicate-fact':(3,'S[.CONSTCONTEXT = (pconstantcontext[.FACTS = pconstantcontext.FACTS ++ [pconstantfact]])]',['S.CONSTCONTEXT = (pconstantcontext)','pconstantcontext.FACTS = pconstantfact :: pconstantfact_tail*']),
'arbitrary-scalar-fact':(3,'S[.CONSTCONTEXT = (pconstantcontext[.FACTS = (pconstantfact[.VALUE = (PINT 999)]) :: pconstantfact_tail*])]',['S.CONSTCONTEXT = (pconstantcontext)','pconstantcontext.FACTS = pconstantfact :: pconstantfact_tail*','pconstantfact.CLASS = PVSCALAR']),
'nested-initializer':(3,'S[.TODO = (AT pconstantcontext.ORIGIN (CONSTANT_INIT expression)) :: S.TODO]',['S.CONSTCONTEXT = (pconstantcontext)','$origin_node(S.SOURCES, pconstantcontext.ORIGIN) = (NConst phpType11 expression metadata)']),
}
records=[]
for name,(stage,term,checks) in variants.items():
 d=D/name;d.mkdir();fixture=d/'case.watsup';fixture.write_text(prefix+'\ndec $main() : pstate\ndef $main() = $drive('+term+', 0)\n  -- if S_initial = '+initial+'\n  -- if S = $constant_test_find(S_initial[.COMPLETION = NORMAL], '+str(stage)+', 200)\n'+''.join('  -- if '+c+'\n' for c in checks))
 cmd=[str(runner),*map(str,mods),str(fixture)];(d/'command.json').write_text(json.dumps(cmd));p=subprocess.run(cmd,capture_output=True,timeout=60);(d/'stdout').write_bytes(p.stdout);(d/'stderr').write_bytes(p.stderr);(d/'status.json').write_text(json.dumps({'exit_status':p.returncode}));records.append({'id':name,'exit_status':p.returncode,'stdout_sha256':hashlib.sha256(p.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(p.stderr).hexdigest()});print(name,p.returncode,p.stderr[:160],flush=True)
(D/'report.json').write_text(json.dumps({'scope':'Actual source public drive0 constant receive/context/source-kind controls; exact mutable candidate inputs retained.','raw':str(D),'records':records},indent=2));print(D)

positive={'control-init','control-bind','control-observe','control-context','arbitrary-scalar-fact'}
for row in records:
 d=D/row['id'];expected='BUDGET' if row['id'] in positive else 'UNSUPPORTED'
 assert row['exit_status']==0 and not (d/'stderr').read_bytes() and 'COMPLETION '+expected in (d/'stdout').read_text(),row['id']
report=json.loads((D/'report.json').read_text());report.update(result='pass',assertions=len(records),fingerprint=q.t.syntax_validation.implementation_fingerprint());(D/'report.json').write_text(json.dumps(report,indent=2)+'\n');(R/'coverage/semantics/user-constant-context-protocol.json').write_text(json.dumps(report,indent=2)+'\n')
