#!/usr/bin/env python3
"""Challenge actual Closure cache-hit recipients, retired history and receive causality."""
import argparse
import base64,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tests/semantics'))
from recorded_worker import Worker
from error_handler_run import recorded
import static_types as types
from deprecated_parameter_default_protocol import PREFIX
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path)
out=parser.parse_args().output.resolve();out.mkdir(parents=True,exist_ok=False)
selected={'named':ROOT/'tests/semantics/deprecated_closure_default_review/named-hole-shared-cache.php','retired':ROOT/'tests/semantics/deprecated_closure_default_review/callback-retired-private.php','child':ROOT/'tests/semantics/deprecated_global_constant/closure-owned-reentry-empty.php'}
modules=[ROOT/p for p in json.loads((ROOT/'spec/semantics/modules.json').read_text())]
watched=[Path(__file__),*modules,*selected.values(),*(ROOT/p for p in ('spec/semantics/modules.json','spec/schema.json','tests/semantics/deprecated_parameter_default_protocol.py','tests/semantics/deprecated_global_constant_protocol.py','tests/semantics/recorded_worker.py','tests/semantics/error_handler_run.py','tests/semantics/static_types.py','.tools/php/bin/php','.tools/php-file.so','_build/default/adapter/main.exe','tests/semantics/_build/default/numeric_runner.exe'))]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before={str(p):sha(p) for p in watched};head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
frontend=Worker([str(types.PHP),'-n',*types.FLAGS,'-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')],out/'frontend')
adapter=Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)],out/'adapter');checks=[]
try:
 for tag,source in selected.items():
  parsed=frontend.request({'op':'parse','source':base64.b64encode(source.read_bytes()).decode()});assert parsed['accepted'] and not parsed['diagnostics']
  checked=adapter.request({'op':'check','ast':parsed['ast'],'fixture':True});assert checked['ok']
  checks+=['U_'+tag+' = '+checked['fixture'],'S_start_'+tag+' = $php_run(U_'+tag+',0,'+json.dumps(base64.b64encode(bytes(source)).decode())+')','S_start_'+tag+'.COMPLETION = BUDGET','S_warn_'+tag+' = $dep_pause(S_start_'+tag+'[.COMPLETION = NORMAL],10000)','S_warn_'+tag+'.CURRENT = (pcallcontext_'+tag+')','$receiving_function(S_warn_'+tag+',pcallcontext_'+tag+'.FUNCTION) = (pfunction_'+tag+')','$parameter_closure_selected(S_warn_'+tag+',pfunction_'+tag+')','$parameter_closure_current(S_warn_'+tag+',pfunction_'+tag+')','S_bind_'+tag+' = $parameter_test_pause(S_warn_'+tag+',0,10000)','S_bind_'+tag+'.COMPLETION = NORMAL']
finally:
 adapter.close();frontend.close()
checks += [
'S_bind_named.TODO = (NAMED_DEFAULT_BIND pfunction_named.ORIGIN 0) :: eps',
'$parameter_closure_current(S_bind_named,pfunction_named)',
'S_cached = $review_cached_pause(S_bind_named,10000)',
'S_cached.COMPLETION = NORMAL',
'S_cached.TODO = (NAMED_PREFLIGHT pfunction_named.ORIGIN 0) :: eps',
'S_cached.CURRENT = (pcallcontext_cached)',
'pcallcontext_cached.INSTANCE = (n_cached)',
'pcallcontext_named.INSTANCE = (n_original)',
'n_cached =/= n_original',
'$closure_cache_at(S_cached.CLOSURECACHES,n_cached) = (pclosurecache_cached)',
'$default_at(pfunction_named.DEFAULTS,0) = (pdefault_named)',
'$default_cache_at(S_cached.DEFAULTCACHE,pdefault_named.ORIGIN) = (pdefaultcache_named)',
'$parameter_closure_current(S_cached,pfunction_named)',
'$default_receive_recipient(S_cached,pfunction_named,pdefault_named)',
'S_missing = S_cached[.CLOSURECACHES = $review_without_stamp(S_cached.CLOSURECACHES,n_cached)]',
'$closure_cache_first(S_missing.CLOSURECACHES,pfunction_named.ORIGIN) =/= eps',
'~$parameter_closure_selected(S_missing,pfunction_named)',
'~$parameter_closure_current(S_missing,pfunction_named)',
'~$default_receive_recipient(S_missing,pfunction_named,pdefault_named)',
'PhpStep: S_missing ~> S_missing_refused',
'S_missing_refused.COMPLETION = UNSUPPORTED "uncertified real Closure default cache"',
'S_history = S_cached[.OBJECTS = S_cached.OBJECTS ++ [S_cached.OBJECTS[n_cached]]]',
'~((HOBJECT (|S_cached.OBJECTS|)) <- S_history.ALLOCATIONS)',
'$parameter_closure_selected(S_history,pfunction_named)',
'~$parameter_closure_family(S_history,pfunction_named.ORIGIN)',
'~$default_receive_recipient(S_history,pfunction_named,pdefault_named)',
'S_call = S_cached[.CLOSURECALLCACHES = [{FUNCTION pfunction_named.ORIGIN, SOURCE n_cached, RECEIVER n_cached, SITE pfunction_named.ORIGIN}]]',
'$parameter_closure_selected(S_call,pfunction_named)',
'~$parameter_closure_family(S_call,pfunction_named.ORIGIN)',
'~$default_receive_recipient(S_call,pfunction_named,pdefault_named)',
'$call_descriptors_valid(S_cached)',
'S_done_named = $drive(S_cached,10000)',
'S_done_named.COMPLETION = NORMAL',
'$call_descriptors_valid(S_done_named)',
'S_bind_retired.TODO = (DEFAULT_BIND pfunction_retired.ORIGIN 0) :: eps',
'$parameter_closure_selected(S_bind_retired,pfunction_retired)',
'~$parameter_closure_current(S_bind_retired,pfunction_retired)',
'~$parameter_closure_family(S_bind_retired,pfunction_retired.ORIGIN)',
'$call_descriptors_valid(S_bind_retired)',
'$parameter_receive_owner(S_bind_retired.CURRENT) = (n_owner_retired)',
'$parameter_receive_birth(S_bind_retired,n_owner_retired) = (preceivebirth_retired)',
'$parameter_receive_closure_entry(S_bind_retired,preceivebirth_retired)',
'~$parameter_receive_cache_entry(S_bind_retired,preceivebirth_retired)',
'PhpStep: S_bind_retired ~> S_retired_refused',
'S_retired_refused.COMPLETION = UNSUPPORTED "uncertified real Closure default cache"',
'S_bind_child.TODO = (DEFAULT_BIND pfunction_child.ORIGIN 0) :: eps',
'S_bind_child.PARAMETERRECEIVES = [preceivebirth_parent,preceivebirth_child]',
'$parameter_receive_owner(S_bind_child.CURRENT) = (n_owner_child)',
'$parameter_receive_cache_child(S_bind_child,preceivebirth_parent,n_owner_child,preceivebirth_child)',
'~$parameter_receive_cache_child(S_bind_child,preceivebirth_parent,n_owner_child,preceivebirth_child[.FUNCTION = preceivebirth_parent.ORIGIN])',
'~$parameter_receive_cache_child(S_bind_child,preceivebirth_parent,n_owner_child,preceivebirth_child[.CAUSE.CALLS = eps])',
'~$parameter_receive_cache_child(S_bind_child,preceivebirth_parent,n_owner_child,preceivebirth_child[.PARENTINDEX = (0)])',
'~$parameter_receive_cache_child(S_bind_child,preceivebirth_parent,n_owner_child,preceivebirth_child[.PARENTEDGE = eps])',
'$call_descriptors_valid(S_bind_child)',
'S_done_child = $drive(S_bind_child,10000)',
'S_done_child.COMPLETION = NORMAL']
for mutation in ('.INSTANCE = eps','.TARGET = CLOSURE_TARGET n_original','.CACHE = (CACHE_SHARED)','.LEXICAL_CLASS = (pfunction_named.ORIGIN)','.CALLED_CLASS = (pfunction_named.ORIGIN)'):
 checks+=['~$parameter_closure_selected(S_cached[.CURRENT = (pcallcontext_cached['+mutation+'])],pfunction_named)']
extra=r'''
dec $review_without_stamp(pclosurecache*,nat) : pclosurecache*
def $review_without_stamp(eps,n) = eps
def $review_without_stamp(pclosurecache :: pclosurecache_tail*,n) = $review_without_stamp(pclosurecache_tail*,n) -- if pclosurecache.OBJECT = n
def $review_without_stamp(pclosurecache :: pclosurecache_tail*,n) = pclosurecache :: $review_without_stamp(pclosurecache_tail*,n) -- if pclosurecache.OBJECT =/= n
dec $review_cached_ready(pstate) : bool
def $review_cached_ready(S) = true
  -- if S.TODO = (NAMED_PREFLIGHT porigin n) :: ptask*
  -- if $receiving_function(S,porigin) = (pfunction)
  -- if $default_at(pfunction.DEFAULTS,n) = (pdefault)
  -- if $default_cache_at(S.DEFAULTCACHE,pdefault.ORIGIN) =/= eps
def $review_cached_ready(S) = false -- otherwise
dec $review_cached_pause(pstate,nat) : pstate
def $review_cached_pause(S,n) = S -- if $review_cached_ready(S)
def $review_cached_pause(S,n) = $review_cached_pause(S_next[.COMPLETION = NORMAL],$nabs($(n - 1)))
  -- if ~$review_cached_ready(S)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $review_cached_pause(S,n) = S -- otherwise
'''
fixture=out/'protocol.watsup';fixture.write_text(PREFIX+extra+'\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- '+check+'\n' if check.startswith('PhpStep:') else '  -- if '+check+'\n' for check in checks))
(out/'assertions.json').write_text(json.dumps(checks,indent=2)+'\n')
report={'head':head,'inputs':before,'module_count':len(modules),'premises':len(checks),'source_agreement_credit':0,'environment':{'LC_ALL':'C','TZ':'UTC'},'passed':False}
try:
 report['process']=recorded([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'),'--sl',*map(str,modules),str(fixture)],out/'check',180)
 report['stdout']=(out/'check.stdout').read_text();report['stderr']=(out/'check.stderr').read_text()
 report['inputs_stable']=before=={str(p):sha(p) for p in watched};report['head_stable']=head==subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 report['passed']=report['process']['exit']==0 and not report['process']['timeout'] and not report['process']['group_after'] and report['stdout']=='true\n' and not report['stderr'] and report['inputs_stable'] and report['head_stable']
finally:(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print('pass' if report['passed'] else 'fail',len(checks));print(report['stdout'][:1500]);print(report['stderr'][:4000]);assert report['passed']
