#!/usr/bin/env python3
"""Check source-derived class-constant update order and initializer authority."""
import argparse,base64,hashlib,json,os,signal,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tests/semantics'))
import static_types as types
from recorded_worker import Worker
from method_runtime import owned_members
ENV={'PATH':'/usr/bin:/bin','LC_ALL':'C','TZ':'UTC','PYTHONDONTWRITEBYTECODE':'1','GIT_OPTIONAL_LOCKS':'0'}
SOURCES={
 'update-order':'<?php\nclass A {const X=N; const Y=M;}\nnew A;\n',
 'literal-selection':'<?php\nclass A {const X=N;}\nclass B {const Y=M;}\nconst N=12; const M=13;\necho A::X;\n',
}
PREFIX='''dec $class_constant_test_stage(pstate, nat) : bool
def $class_constant_test_stage(S, 0) = true
  -- if S.TODO = (CLASS_CONST_UPDATE porigin z) :: ptask_tail*
def $class_constant_test_stage(S, 1) = true
  -- if S.CLASSCONSTANTINIT =/= eps
def $class_constant_test_stage(S, n) = false -- otherwise
dec $class_constant_test_seek(pstate, nat, nat) : pstate
def $class_constant_test_seek(S, n, n_limit) = S
  -- if $class_constant_test_stage(S, n)
def $class_constant_test_seek(S, n, n_limit) = $class_constant_test_seek(S_next[.COMPLETION = NORMAL], n, n_rest)
  -- if ~$class_constant_test_stage(S, n)
  -- if $(n_limit > 0)
  -- if S.COMPLETION = NORMAL
  -- if ~S.COMPILESTOP
  -- if n_rest = $(n_limit - 1)
  -- if S_next = $drive_steps(S, 1)
'''
CHECKS={
 'update-order':[
  'S = $class_constant_test_seek(S_initial[.COMPLETION = NORMAL], 0, 400)',
  'S.TODO = (CLASS_CONST_UPDATE porigin_x z) :: (CLASS_CONST_UPDATE porigin_y z) :: ptask_tail*',
  'porigin_x =/= porigin_y',
  '$class_constant_state_valid(S)',
  '~$class_constant_state_valid(S[.TODO = (CLASS_CONST_UPDATE porigin_y z) :: (CLASS_CONST_UPDATE porigin_x z) :: ptask_tail*])',
  '~$class_constant_state_valid(S[.TODO = (CLASS_CONST_UPDATE porigin_x z) :: (CLASS_CONST_UPDATE porigin_x z) :: (CLASS_CONST_UPDATE porigin_y z) :: ptask_tail*])',
  '~$class_constant_state_valid(S[.TODO = (CLASS_CONST_UPDATE porigin_y z) :: ptask_tail*])',
  '~$class_constant_state_valid(S[.TODO = ptask_tail*])',
  'S_init = $drive_steps(S, 1)',
  'S_init.CLASSCONSTANTINIT = [pclassconstantcontext]',
  'pclassconstantcontext.DECL = porigin_x',
  '$class_constant_state_valid(S_init)',
  'S_init.CONSTCONTEXT = (pconstantcontext)',
  '~$class_constant_state_valid(S_init[.CONSTCONTEXT = (pconstantcontext[.ORIGIN = porigin_y])])',
  '~$class_constant_state_valid(S_init[.TODO = DISCARD :: ptask_tail*])',
 ],
 'literal-selection':[
  'S = $class_constant_test_seek(S_initial[.COMPLETION = NORMAL], 1, 400)',
  'S.CLASSCONSTANTINIT = [pclassconstantcontext]',
  'pclassconstantcontext.SELECTION = CLASS_CONST_FETCH (KNOWN (PSTRING ptbytes_a)) ptbytes_x',
  'S.CONSTCONTEXT = (pconstantcontext)',
  '$class_constant_state_valid(S)',
  '$class_named(S.CLASSNAMES, $ptascii("b")) = (porigin_b)',
  '$class_constant_lookup(S, porigin_b, $ptascii("Y"), |S.CLASSES|) = (pclassconstantdesc_b)',
  '$origin_node(S.SOURCES, pclassconstantdesc_b.INITIALIZER) = (expression_b)',
  'S.TODO = (AT porigin_initializer (EVAL expression)) :: (CLASS_CONST_BIND porigin_x) :: ptask_tail*',
  'S_forged = S[.CLASSCONSTANTINIT = [pclassconstantcontext[.DECL = pclassconstantdesc_b.ORIGIN][.SELECTION = CLASS_CONST_FETCH (KNOWN (PSTRING $ptascii("B"))) $ptascii("Y")]]][.CONSTCONTEXT = (pconstantcontext[.ORIGIN = pclassconstantdesc_b.ORIGIN])][.ORIGIN = (pclassconstantdesc_b.ORIGIN)][.TODO = [AT pclassconstantdesc_b.INITIALIZER (EVAL expression_b), CLASS_CONST_BIND pclassconstantdesc_b.ORIGIN] ++ ptask_tail*]',
  '~$class_constant_state_valid(S_forged)',
  '~$class_constant_state_valid(S[.CLASSCONSTANTINIT = [pclassconstantcontext[.LINE = 999]]])',
 ],
}

def sha(p):
 return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def prepare(out):
 out=Path(out).resolve();out.mkdir(parents=True,exist_ok=False)
 types.ENV=ENV
 frontend=adapter=None
 records=[]
 def worker(command,name):
  w=Worker(command,out/name)
  (out/name/'launch.json').write_text(json.dumps({'supplied_argv':command,'supplied_cwd':os.getcwd(),'supplied_environment':ENV,'popen_args':w.p.args,'pid':w.p.pid},indent=2)+'\n')
  return w
 try:
  frontend=worker([str(types.PHP),'-n',*types.FLAGS,'-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')],'frontend')
  adapter=worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)],'adapter')
  for case,source in SOURCES.items():
   path=out/(case+'.php');path.write_bytes(source.encode())
   parsed=frontend.request({'op':'parse','source':base64.b64encode(path.read_bytes()).decode()});assert parsed['accepted'],parsed
   checked=adapter.request({'op':'check','ast':parsed['ast'],'fixture':True});assert checked['ok'],checked
   (out/(case+'.checked.json')).write_text(json.dumps(checked,indent=2)+'\n')
   conditions=['S_initial = $php_run('+checked['fixture']+', 0, '+json.dumps(base64.b64encode(bytes(path)).decode())+')',*CHECKS[case]]
   fixture=out/(case+'.watsup');fixture.write_text(PREFIX+'\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+c+'\n' for c in conditions))
   records.append({'id':case,'source':str(path),'source_sha256':sha(path),'fixture':str(fixture),'fixture_sha256':sha(fixture),'main_predicates':len(conditions)})
 finally:
  try:
   if frontend:frontend.close()
  finally:
   if adapter:adapter.close()
 (out/'prepared.json').write_text(json.dumps({'scope':'Pure checked source/fixture preparation only; numeric state programs UNRUN.','root':str(ROOT),'records':records},indent=2)+'\n')
 print(out)
 return records

def run():
 modules=[ROOT/name for name in json.loads((ROOT/'spec/semantics/modules.json').read_text())]
 runner=ROOT/'tests/semantics/_build/default/numeric_runner.exe'
 fingerprint=types.syntax_validation.implementation_fingerprint()
 watched=[*modules,runner,types.PHP,ROOT/'_build/default/adapter/main.exe',
  ROOT/'spec/semantics/modules.json',Path(__file__),ROOT/'tests/semantics/recorded_worker.py',
  ROOT/'tests/semantics/method_runtime.py',ROOT/'frontend/worker.php',ROOT/'.tools/php-file.so']
 before={str(p.relative_to(ROOT)):sha(p) for p in watched}
 def stable():
  return fingerprint==types.syntax_validation.implementation_fingerprint() and all(sha(ROOT/name)==digest for name,digest in before.items())
 out=Path(tempfile.mkdtemp(prefix='class-constant-protocol-',dir=ROOT/'.tools'))
 records=[];fixtures=[];failure=None
 try:
  fixtures=prepare(out/'fixtures')
  for row in fixtures:
   assert stable(),'class-constant inputs changed before case'
   assert sha(row['source'])==row['source_sha256'] and sha(row['fixture'])==row['fixture_sha256'],'prepared input changed'
   raw=out/row['id'];raw.mkdir()
   command=[str(runner),*map(str,modules),row['fixture']]
   facts={'supplied_argv':command,'supplied_cwd':str(ROOT),'supplied_environment':ENV,
    'host_timeout_seconds':120,'observed_exit':None,'cleanup_exit':None,'status':'prepared'}
   def save():
    (raw/'command.json').write_text(json.dumps(facts,indent=2)+'\n')
   save();process=None
   with (raw/'stdout').open('wb') as stdout,(raw/'stderr').open('wb') as stderr:
    try:
     process=subprocess.Popen(command,cwd=ROOT,env=ENV,stdout=stdout,stderr=stderr,start_new_session=True)
     facts.update(popen_args=process.args,pid=process.pid,owned_pgid=process.pid,status='running');save()
     facts['observed_exit']=process.wait(timeout=120)
    except subprocess.TimeoutExpired:
     facts['timeout_expired']=True
    finally:
     if process is not None:
      try:os.killpg(process.pid,signal.SIGKILL)
      except ProcessLookupError:pass
      try:facts['cleanup_exit']=process.wait(timeout=5)
      except subprocess.TimeoutExpired:facts['cleanup_timeout']=True
      facts['owned_group_after']=owned_members(process.pid)
     facts['status']='closed';save()
   unchanged=stable() and sha(row['source'])==row['source_sha256'] and sha(row['fixture'])==row['fixture_sha256']
   passed=(facts['observed_exit']==0 and facts['cleanup_exit']==0 and facts.get('owned_group_after')==[]
    and (raw/'stdout').read_bytes()==b'true\n' and not (raw/'stderr').read_bytes() and unchanged)
   records.append({**row,'result':'pass' if passed else 'fail','command_record':str(raw/'command.json'),
    'stdout_sha256':sha(raw/'stdout'),'stderr_sha256':sha(raw/'stderr'),'inputs_stable':unchanged})
   print(row['id'],records[-1]['result'],row['main_predicates'],flush=True)
   if not passed:break
 except BaseException as error:
  failure={'type':type(error).__name__,'message':str(error)}
 passed=failure is None and len(records)==len(SOURCES) and all(r['result']=='pass' for r in records)
 report={'result':'pass' if passed else 'fail','fingerprint':fingerprint,'direct_inputs':before,
  'scope':'Source-derived finite state predicates; native agreement is separate.',
  'completed_cases':len(records),'selected_cases':len(SOURCES),'conditional_unrun':list(SOURCES)[len(records):],
  'records':records,'error':failure,'raw':str(out)}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(out,report['result'],flush=True)
 return passed

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--prepare-only',type=Path);args=parser.parse_args()
 if args.prepare_only:prepare(args.prepare_only)
 else:raise SystemExit(0 if run() else 1)
