"""Check reference Get aliasing, typed cells, copying and destination errors."""
import argparse,base64,hashlib,json,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(ROOT/'frontend'))
import backed_get_hook_protocol as hook
import error_handler_run as recorder
from recorded_worker import Worker

PREFIX=hook.PREFIX+r'''
def $bh_stage(S,10) = ($property_hook_ref_plan(S) =/= eps)
def $bh_stage(S,11) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $property_hook_context_kind(pcallcontext)
  -- if S.TODO = (PROPERTY_BASE_PREP (NIdentifier (BYTES text) metadata) z) :: ptask*
  -- if $base64(text) = $ptascii("value")
  -- if ~$property_hook_pending(S)
def $bh_stage(S,12) = true
  -- if S.TODO = (PROPERTY_HOOK_REF_RESULT ppropertyhook "fetch") :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $bh_stage(S,13) = true
  -- if $bh_output(S.EVENTS) = $ptascii("A:G|alias7|typed8|")
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $bh_stage(S,14) = true
  -- if S.TODO = (PROPERTY_HOOK_RESULT ppropertyhook) :: ptask*
  -- if ppropertyhook.LINE = 14
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $bh_stage(S,15) = true
  -- if $bh_output(S.EVENTS) = $ptascii("A:G|alias7|typed8|G|copy8|")
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $bh_stage(S,16) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext,S.CURRENT,S.FRAMES) = (pdestructorcall)
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES text) metadata_string])) metadata)) :: ptask*
  -- if $base64(text) = $ptascii("D|")
def $bh_stage(S,17) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (STMT (NStmtExpression (NExprAssign (NExprVariable (BYTES text_name) metadata_name) (NScalarString (BYTES text_value) metadata_value) metadata_assign) metadata)) :: ptask*
  -- if $base64(text_name) = $ptascii("alias") /\ $base64(text_value) = $ptascii("free")
'''

def lines(s):return [line.strip() for line in s.strip().splitlines() if line.strip()]
def seek(old,stage,new):
 return [f'{new}_found = $bh_seek({old},{stage},3000)',rf'{new}_found.COMPLETION = NORMAL \/ {new}_found.COMPLETION = BUDGET',f'{new} = {new}_found[.COMPLETION = NORMAL]',f'$bh_stage({new},{stage})']
def budget(s,prefix):
 return [f'{prefix}_zero = $drive_steps({s},0)',f'{prefix}_zero = {s}[.COMPLETION = BUDGET]',f'{prefix}_whole = $drive_steps({s},2)',f'{prefix}_one = $drive_steps({s},1)',f'{prefix}_one.COMPLETION = BUDGET',f'{prefix}_split = $drive_steps({prefix}_one[.COMPLETION = NORMAL],1)',f'{prefix}_split = {prefix}_whole']
def conditions(program,path):
 checks=[f'S_initial = $php_run({program},0,{json.dumps(base64.b64encode(str(path).encode()).decode())})','S_initial.COMPLETION = BUDGET']
 checks+=seek('S_initial',10,'S_front')+lines(r'''
$property_hook_ref_plan(S_front) = ((ppropertyhook,"fetch"))
S_front.TODO = (PROPERTY_PREP phpType20 z) :: (PROPERTY_REF_FETCH z) :: ptask_tail*
ppropertyhook.LINE = 10 /\ z = 10
$lookup(S_front.ENV,$ptascii("object")) = (n_object_cell)
S_front.STORE[n_object_cell] = DEFINED (POBJECT n_object)
ppropertyhook.OBJECT = n_object
$property_effective_desc(S_front,n_object,$ptascii("value")) = (ppropertydesc)
$property_hook_reference_decl(S_front,ppropertydesc)
$property_hook_function(S_front,ppropertyhook) = (pfunction_hook)
pfunction_hook.SIGNATURE = {PARAMETERS eps,RETURNS ppropertydesc.TYPE,BYREF true}
ppropertydesc.TYPE = [PTBRANCH ([PTBUILTIN "int"])]
$bh_slot(S_front,n_object,$ptascii("value")) = (PROP_VALUE (DIRECT (PINT 7)))
$target_nodes(PROPERTY_HOOK_TARGET ppropertyhook) = [HOBJECT n_object]
$task_nodes(PROPERTY_HOOK_REF_RESULT ppropertyhook "fetch") = eps
$heap_owners($heap_graph(S_front),HOBJECT n_object) = 1
$bh_output(S_front.EVENTS) = $ptascii("A:") /\ $bh_guard(S_front)
PhpStep: S_front ~> S_begin_raw
S_begin_raw.TODO = [(CALL_ARGS (PROPERTY_HOOK_TARGET ppropertyhook) eps 0 eps (ppropertyhook.SITE) z),PROPERTY_HOOK_REF_RESULT ppropertyhook "fetch",PROPERTY_REF_FETCH z] ++ ptask_tail*
S_begin = $bh_after(S_front,S_begin_raw)
$property_hook_pending_call(S_begin,ppropertyhook) /\ $bh_guard(S_begin)
$heap_owners($heap_graph(S_begin),HOBJECT n_object) = 2
''')
 checks+=seek('S_begin',1,'S_entered')+lines(r'''
S_entered.CURRENT = (pcallcontext_hook)
pcallcontext_hook.TARGET = PROPERTY_HOOK_TARGET ppropertyhook
pcallcontext_hook.RECEIVER = (n_object)
$call_receiver_roots(pcallcontext_hook) = [HOBJECT n_object]
S_entered.FRAMES = pframe_caller :: eps
pframe_caller.TODO = [PROPERTY_HOOK_REF_RESULT ppropertyhook "fetch",PROPERTY_REF_FETCH z] ++ ptask_tail*
$property_hook_context_valid(S_entered,pcallcontext_hook) /\ $bh_guard(S_entered)
$heap_owners($heap_graph(S_entered),HOBJECT n_object) = 2
''')
 checks+=seek('S_entered',11,'S_backing')+lines(r'''
S_backing.TODO = (PROPERTY_BASE_PREP phpType20_backing z_backing) :: ptask_backing*
pbase_backing = S_backing.BASE
pbase_backing = BASE_VALUE (KNOWN (POBJECT n_object))
z_receiver = $property_receiver_source_line(S_backing)
$property_hook_backing(S_backing,n_object,ppropertydesc)
~$property_hook_read_needed(S_backing,n_object,$ptascii("value"))
$bh_output(S_backing.EVENTS) = $ptascii("A:G|") /\ $bh_guard(S_backing)
PhpStep: S_backing ~> S_base_raw
S_base_raw = S_backing[.TODO = ptask_backing*][.BASE = BASE_PROPERTY_PENDING pbase_backing (KNOWN (PSTRING ($ptascii("value")))) z_receiver][.RESULT = KNOWN PNULL]
S_base = $bh_after(S_backing,S_base_raw)
''')
 checks+=seek('S_base',12,'S_result')+lines(r'''
S_result.TODO = [PROPERTY_HOOK_REF_RESULT ppropertyhook "fetch",PROPERTY_REF_FETCH z] ++ ptask_tail*
S_result.RESULT = REFERENCE n_value
S_result.STORE[n_value] = DEFINED (PINT 7)
$bh_slot(S_result,n_object,$ptascii("value")) = (PROP_VALUE (ALIAS n_value))
$propref_at(S_result.PROPREFS,n_value) = (ppropref)
ppropref.SOURCES = [OBJECT_PROP_SOURCE n_object ($ptascii("value")) ppropertydesc.ORIGIN]
$proprefs_valid(S_result) /\ $call_reference_operand_valid(S_result,S_result.RESULT)
$property_hook_result_tail(S_result,ppropertyhook,S_result.TODO)
$heap_owners($heap_graph(S_result),HOBJECT n_object) = 1
$heap_owners($heap_graph(S_result),HCELL n_value) = 2
$bh_guard(S_result)
PhpStep: S_result ~> S_alias_raw
S_alias_raw = S_result[.TODO = ptask_tail*][.CELL = n_value][.BASE = BASE_VALUE (KNOWN PNULL)]
S_alias = $bh_after(S_result,S_alias_raw)
''')
 checks+=seek('S_alias',13,'S_typed')+lines(r'''
$lookup(S_typed.ENV,$ptascii("alias")) = (n_value)
S_typed.STORE[n_value] = DEFINED (PINT 8)
$propref_at(S_typed.PROPREFS,n_value) = (ppropref)
$heap_owners($heap_graph(S_typed),HCELL n_value) = 2
$proprefs_valid(S_typed) /\ $bh_guard(S_typed)
''')
 checks+=seek('S_typed',14,'S_read_result')+lines(r'''
S_read_result.TODO = (PROPERTY_HOOK_RESULT ppropertyhook_copy) :: ptask_copy*
ppropertyhook_copy.OBJECT = n_object /\ ppropertyhook_copy.PROPERTY = ppropertyhook.PROPERTY
ppropertyhook_copy.HOOK = ppropertyhook.HOOK /\ ppropertyhook_copy.SITE =/= ppropertyhook.SITE
S_read_result.RESULT = REFERENCE n_value
S_read_result.STORE[n_value] = DEFINED (PINT 8)
$property_hook_result_tail(S_read_result,ppropertyhook_copy,S_read_result.TODO)
$heap_owners($heap_graph(S_read_result),HCELL n_value) = 3
$propref_at(S_read_result.PROPREFS,n_value) = (ppropref) /\ $bh_guard(S_read_result)
PhpStep: S_read_result ~> S_copy_raw
S_copy_raw = S_read_result[.TODO = ptask_copy*][.RESULT = KNOWN (PINT 8)][.BASE = BASE_VALUE (KNOWN (PINT 8))]
$heap_owners($heap_graph(S_copy_raw),HCELL n_value) = 2
S_copy = $bh_after(S_read_result,S_copy_raw)
''')
 checks+=seek('S_copy',15,'S_written')+lines(r'''
S_written.STORE[n_value] = DEFINED (PINT 9)
$lookup(S_written.ENV,$ptascii("copy")) = (n_copy)
n_copy =/= n_value /\ S_written.STORE[n_copy] = DEFINED (PINT 8)
$propref_at(S_written.PROPREFS,n_value) = (ppropref) /\ $bh_guard(S_written)
''')
 checks+=seek('S_written',16,'S_dtor')+lines(r'''
S_dtor.CURRENT = (pcallcontext_dtor)
$destructor_context_call(pcallcontext_dtor,S_dtor.CURRENT,S_dtor.FRAMES) = (pdestructorcall)
pdestructorcall.OBJECT = n_object
S_dtor.STORE[n_value] = DEFINED (PINT 9)
$propref_at(S_dtor.PROPREFS,n_value) = (ppropref) /\ $bh_guard(S_dtor)
''')
 checks+=seek('S_dtor',17,'S_detached')+lines(r'''
$lookup(S_detached.ENV,$ptascii("object")) = eps
~((HOBJECT n_object) <- S_detached.ALLOCATIONS)
$lookup(S_detached.ENV,$ptascii("alias")) = (n_value)
S_detached.STORE[n_value] = DEFINED (PINT 9)
$propref_at(S_detached.PROPREFS,n_value) = eps
$heap_owners($heap_graph(S_detached),HCELL n_value) = 1
$proprefs_valid(S_detached) /\ $bh_guard(S_detached)
S_done = $drive(S_detached,4000)
S_done.COMPLETION = NORMAL /\ S_done.EXITSTATUS = 0
S_done.TODO = eps /\ S_done.FRAMES = eps /\ S_done.CURRENT = eps
$bh_output(S_done.EVENTS) = $ptascii("A:G|alias7|typed8|G|copy8|alias9|D|free|Z|")
$bh_guard(S_done)
''')
 return checks+budget('S_front','S_front_budget')+budget('S_read_result','S_copy_budget')


def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--revision',required=True)
 parser.add_argument('--group',required=True,choices=['backing-alias','forbidden-rebind'])
 parser.add_argument('--prepare-only',action='store_true')
 args=parser.parse_args()
 recorder.ROOT=ROOT
 git=lambda *a:subprocess.check_output(['git',*a],cwd=ROOT,env=recorder.ENV).decode().strip()
 sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 revision,status=git('rev-parse','HEAD'),git('status','--short')
 assert revision==args.revision and not status
 catalogue=HERE/'reference_get_hook_cases.json'
 data=json.loads(catalogue.read_bytes())
 case=next(row for row in data['cases'] if row['id']==args.group)
 profile_file=HERE/'profile.json'
 profile=json.loads(profile_file.read_bytes())
 assert profile==data['native_profile']
 modules=[ROOT/name for name in json.loads((ROOT/'spec/semantics/modules.json').read_bytes())]
 php=ROOT/'.tools/php/bin/php'
 adapter=ROOT/'_build/default/adapter/main.exe'
 bridge=ROOT/'.tools/php-file.so'
 compiler=ROOT/'.tools/spectec/bin/p4spectec'
 runner=HERE/'_build/default/numeric_runner.exe'
 assert sha(php)=='b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
 watched=[*modules,ROOT/'spec/semantics/modules.json',ROOT/'spec/php.watsup',ROOT/'spec/schema.json',
  ROOT/'spec/nodes.json',catalogue,profile_file,Path(__file__),HERE/'reference_get_hook_state_review.py',
  HERE/'backed_get_hook_protocol.py',HERE/'error_handler_run.py',HERE/'recorded_worker.py',
  php,adapter,bridge,compiler,runner,ROOT/'frontend/worker.php',ROOT/'frontend/target.php',
  ROOT/'frontend/wire.php',ROOT/'frontend/wire.py']
 before={str(p):sha(p) for p in watched}
 out=Path(tempfile.mkdtemp(prefix='reference-get-hook-'+args.group+'-',dir=ROOT/'.tools'))
 print(out,flush=True)
 source=out/'source.php'
 source.write_bytes(case['source'].encode())
 assert sha(source)==case['source_sha256']
 report={'revision':revision,'group':args.group,'inputs':before,'profile':profile,
  'module_count':len(modules),'source':str(source),'source_sha256':sha(source),
  'mode':'SL','cache':False,'det':True,'records':[],'application_evaluations':0,
  'native_invocations':0,'source_agreements':0,'passed':False}
 fixture=None
 try:
  flags=[part for k,v in profile.items() for part in ('-d',k+'='+v)]
  frontend=Worker([str(php),'-n',*flags,'-d','extension='+str(bridge),str(ROOT/'frontend/worker.php')],out/'frontend')
  try:
   parsed=frontend.request({'op':'parse','source':base64.b64encode(source.read_bytes()).decode()})
   assert parsed['accepted']
  finally:frontend.close()
  worker=Worker([str(adapter),str(ROOT)],out/'adapter')
  try:
   checked=worker.request({'op':'check','ast':parsed['ast'],'fixture':True})
   assert checked['ok'] and checked['ast']==parsed['ast']
  finally:worker.close()
  if args.group=='backing-alias':
   prefix=PREFIX
   checks=conditions(checked['fixture'],source)
  else:
   import reference_get_hook_state_review as peer
   prefix=peer.PREFIX
   checks=peer.conditions(checked['fixture'],source)
  assert len(checks)==len(set(checks))
  report.update(boolean_premises=sum(not c.startswith('PhpStep:') for c in checks),
   raw_php_steps=sum(c.startswith('PhpStep:') for c in checks),conditions=len(checks))
  assert (report['boolean_premises'],report['raw_php_steps'])==({'backing-alias':(139,4),'forbidden-rebind':(112,2)}[args.group])
  fixture=out/'state.watsup'
  fixture.write_text(prefix+'\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- '+('' if c.startswith('PhpStep:') else 'if ')+c+'\n' for c in checks))
  report.update(fixture=str(fixture),fixture_sha256=sha(fixture),passed=True)
  if not args.prepare_only:
   for name,command in [('compiler',[str(compiler),'algo']),('state',[str(runner),'--sl'])]:
    process=recorder.recorded([*command,*map(str,modules),str(fixture)],out/name,120)
    stdout=(out/name).with_suffix('.stdout').read_bytes()
    passed=(process['exit']==0 and not process['timeout'] and not process['interruption'] and not process['group_after'] and not (out/name).with_suffix('.stderr').read_bytes())
    passed=passed and (b'\ndef $main : bool =\n' in stdout if name=='compiler' else stdout==b'true\n')
    report['records'].append({'id':name,'process':process,'passed':passed})
    report['passed']=passed
    if name=='state':report['application_evaluations']=int(passed)
    assert passed,name
 finally:
  report.update(inputs_stable=before=={str(p):sha(p) for p in watched},
   source_stable=case['source_sha256']==sha(source),
   fixture_stable=fixture is None or report['fixture_sha256']==sha(fixture),
   head_stable=revision==git('rev-parse','HEAD'),status_stable=status==git('status','--short'))
  report['passed']=report['passed'] and all(report[k] for k in ['inputs_stable','source_stable','fixture_stable','head_stable','status_stable'])
  (out/('PREPARED.json' if args.prepare_only else 'report.json')).write_text(json.dumps(report,indent=2)+'\n')
  print(json.dumps({k:report[k] for k in ['passed','application_evaluations','inputs_stable','head_stable','status_stable']}),flush=True)
 assert report['passed']


if __name__=='__main__':main()

