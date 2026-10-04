#!/usr/bin/env python3
"""Check deferred static-default fills, retry, source binding and owning roots."""
import argparse,base64,hashlib,json,os,signal,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tests/semantics'))
import static_types as types
from recorded_worker import Worker
from method_runtime import owned_members
ENV={'PATH':'/usr/bin:/bin','LC_ALL':'C','TZ':'UTC','PYTHONDONTWRITEBYTECODE':'1','GIT_OPTIONAL_LOCKS':'0'}
SOURCES = {'partial-retry': '<?php\n'
                  'class A { const X=N; public static int $p=self::X; public static int $q=LATE; '
                  '}\n'
                  'const N=2;\n'
                  'try { echo A::$p; } catch (Error $e) { echo "E:"; }\n'
                  'const LATE=3;\n'
                  'echo A::$p,":",A::$q;\n',
 'owner-binder': '<?php\n'
                 'class A {const X=N; public static int $p=self::X;}\n'
                 'class B extends A {const X=M; public static int $p=self::X;}\n'
                 'const N=2; const M=3;\n'
                 'new B;\n'
                 'echo A::$p,B::$p;\n',
 'warm-alias': '<?php\n'
               'class A { const X=N; public static int $p=self::X; }\n'
               'class B extends A {}\n'
               'const N=2;\n'
               'echo B::$p,":";\n'
               '$r=&B::$p;\n'
               '$r=7;\n'
               'echo A::$p,":",A::X,":";\n'
               'try { $r="bad"; } catch (TypeError $e) { echo "E:"; }\n'
               'echo A::$p;\n',
 'array-roots': '<?php\n'
                'class A { const X=[N,[N+1]]; public static array $p=self::X; }\n'
                'class B extends A {}\n'
                'const N=2;\n'
                '$v=B::$p;\n'
                '$v[1][0]=9;\n'
                'echo $v[1][0],":",B::$p[1][0],":",A::X[1][0];\n'
                'B::$p[1][0]=7;\n'
                'echo ":",A::$p[1][0],":",A::X[1][0];\n',
 'prototype-prefix': '<?php\n'
                     'class A {private static int $p=N;}\n'
                     'const N=1;\n'
                     'new A;\n'
                     'if (true) {class B extends A {}}\n'
                     'new B;\n'}
PREFIX = 'dec $static_default_test_resume(pstate) : pstate\ndef $static_default_test_resume(S) = S[.COMPLETION = NORMAL]\n  -- if S.COMPLETION = BUDGET\ndef $static_default_test_resume(S) = S -- otherwise\ndec $static_default_test_stage(pstate, nat) : bool\ndef $static_default_test_stage(S, 0) = true\n  -- if S.TODO = (STATIC_DEFAULT_UPDATE porigin_p z) :: (STATIC_DEFAULT_UPDATE porigin_q z) :: ptask_tail*\ndef $static_default_test_stage(S, 1) = true\n  -- if S.TODO = (STATIC_DEFAULT_UPDATE porigin_q z) :: (CLASS_CONST_TABLE_UPDATE porigin_a z) :: ptask_tail*\n  -- if S.EVENTS = eps\n  -- if $static_default_fills(S.CLASSCONSTANTHISTORY) =/= eps\ndef $static_default_test_stage(S, 2) = true\n  -- if S.TODO = (STATIC_DEFAULT_UPDATE porigin_p z) :: ptask_tail*\ndef $static_default_test_stage(S, 3) = true\n  -- if S.TODO = (STATIC_DEFAULT_BIND pstaticdefaultcontext) :: ptask_tail*\ndef $static_default_test_stage(S, 4) = true\n  -- if S.TODO = (STATIC_DEFAULT_UPDATE porigin_q z) :: (CLASS_CONST_TABLE_UPDATE porigin_a z) :: ptask_tail*\n  -- if S.EVENTS = [OUTPUT $ptascii("E:")]\ndef $static_default_test_stage(S, 5) = true\n  -- if $class_named(S.CLASSNAMES, $ptascii("a")) = (porigin_a)\n  -- if $class_named(S.CLASSNAMES, $ptascii("b")) = (porigin_b)\n  -- if $class_constant_table_done(S, porigin_a)\n  -- if ~$class_constant_table_done(S, porigin_b)\n  -- if S.TODO = (CLASS_CONST_TABLE_UPDATE porigin_b z) :: ptask_tail*\ndef $static_default_test_stage(S, n) = false -- otherwise\ndec $static_default_test_seek(pstate, nat, nat) : pstate\ndef $static_default_test_seek(S, n, n_limit) = S\n  -- if $static_default_test_stage(S, n)\ndef $static_default_test_seek(S, n, n_limit) = $static_default_test_seek($static_default_test_resume(S_next), n, n_rest)\n  -- if ~$static_default_test_stage(S, n)\n  -- if $(n_limit > 0)\n  -- if S.COMPLETION = NORMAL\n  -- if ~S.COMPILESTOP\n  -- if n_rest = $(n_limit - 1)\n  -- if S_next = $drive_steps(S, 1)\n'
CHECKS = {'partial-retry': ['S_queue = $static_default_test_seek(S_initial[.COMPLETION = NORMAL], 0, 500)',
                   'S_queue.TODO = (STATIC_DEFAULT_UPDATE porigin_p z) :: (STATIC_DEFAULT_UPDATE '
                   'porigin_q z) :: ptask_tail*',
                   'porigin_p =/= porigin_q',
                   '$class_constant_state_valid(S_queue) /\\ $class_statics_valid(S_queue)',
                   '~$class_constant_state_valid(S_queue[.TODO = (STATIC_DEFAULT_UPDATE porigin_q '
                   'z) :: (STATIC_DEFAULT_UPDATE porigin_p z) :: ptask_tail*])',
                   '~$class_constant_state_valid(S_queue[.TODO = (STATIC_DEFAULT_UPDATE porigin_p '
                   'z) :: (STATIC_DEFAULT_UPDATE porigin_p z) :: (STATIC_DEFAULT_UPDATE porigin_q '
                   'z) :: ptask_tail*])',
                   '~$class_constant_state_valid(S_queue[.TODO = (STATIC_DEFAULT_UPDATE porigin_q '
                   'z) :: ptask_tail*])',
                   '~$class_constant_state_valid(S_queue[.TODO = ptask_tail*])',
                   'S = $static_default_test_seek(S_queue, 1, 300)',
                   '$class_named(S.CLASSNAMES, $ptascii("a")) = (porigin_a)',
                   '$class_at(S.CLASSES, porigin_a) = (pclassdesc)',
                   'pclassdesc.PROPERTIES = [ppropertydesc_p, ppropertydesc_q]',
                   'ppropertydesc_p.ORIGIN = porigin_p /\\ ppropertydesc_q.ORIGIN = porigin_q',
                   'ppropertydesc_p.DEFAULT = PROP_DEFERRED porigin_initializer_p',
                   'ppropertydesc_q.DEFAULT = PROP_DEFERRED porigin_initializer_q',
                   '$class_static_at(S.CLASSSTATICS, porigin_p) = (pclassstatic_p)',
                   'pclassstatic_p.STATE = PROP_VALUE (DIRECT (PINT 2))',
                   '$class_static_at(S.CLASSSTATICS, porigin_q) = (pclassstatic_q)',
                   'pclassstatic_q.STATE = PROP_DEFERRED porigin_initializer_q',
                   'S.CLASSCONSTANTHISTORY = [CCLINK porigin_a n_link, CCCACHE porigin_x '
                   'porigin_trigger n_cache, CCSTATIC porigin_p porigin_trigger n_fill]',
                   '~$class_constant_table_done(S, porigin_a)',
                   '$class_constant_state_valid(S) /\\ $class_statics_valid(S)',
                   '$class_constant_table_tasks(S, porigin_a, z, |S.CLASSES|) = '
                   '[STATIC_DEFAULT_UPDATE porigin_q z, CLASS_CONST_TABLE_UPDATE porigin_a z]',
                   'S_missing = S[.CLASSCONSTANTHISTORY = [CCLINK porigin_a n_link, CCCACHE '
                   'porigin_x porigin_trigger n_cache]]',
                   '~$class_statics_valid(S_missing)',
                   'S_pending = S[.CLASSSTATICS = $class_static_set(S.CLASSSTATICS, porigin_p, '
                   'PROP_DEFERRED porigin_initializer_p)]',
                   '~$class_statics_valid(S_pending)',
                   '~$class_constant_history_valid(S[.CLASSCONSTANTHISTORY = '
                   'S.CLASSCONSTANTHISTORY ++ [CCSTATIC porigin_p porigin_trigger n_fill]])',
                   '~$class_constant_history_valid(S[.CLASSCONSTANTHISTORY = '
                   'S.CLASSCONSTANTHISTORY ++ [CCUPDATE porigin_a porigin_a porigin_trigger '
                   'n_fill]])',
                   'S_early = S[.CLASSCONSTANTHISTORY = [CCLINK porigin_a n_link, CCSTATIC '
                   'porigin_p porigin_trigger n_fill, CCCACHE porigin_x porigin_trigger n_cache]]',
                   '~$class_constant_history_valid(S_early)',
                   'S_retry = $static_default_test_seek(S, 4, 500)',
                   'S_retry.TODO = (STATIC_DEFAULT_UPDATE porigin_q z_retry) :: '
                   '(CLASS_CONST_TABLE_UPDATE porigin_a z_retry) :: ptask_retry*',
                   '$class_static_at(S_retry.CLASSSTATICS, porigin_p) = (pclassstatic_p)',
                   '$static_default_fills(S_retry.CLASSCONSTANTHISTORY) = [porigin_p]',
                   '$class_constant_state_valid(S_retry) /\\ $class_statics_valid(S_retry)',
                   'S_done = $drive_steps(S_retry, 500)',
                   'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps',
                   '$class_static_at(S_done.CLASSSTATICS, porigin_q) = (pclassstatic_q[.STATE = '
                   'PROP_VALUE (DIRECT (PINT 3))])',
                   '$static_default_fills(S_done.CLASSCONSTANTHISTORY) = [porigin_p, porigin_q]',
                   '$class_constant_table_done(S_done, porigin_a)',
                   '$class_constant_state_valid(S_done) /\\ $class_statics_valid(S_done)'],
 'owner-binder': ['S_queue = $static_default_test_seek(S_initial[.COMPLETION = NORMAL], 2, 500)',
                  '$class_named(S_queue.CLASSNAMES, $ptascii("a")) = (porigin_a)',
                  '$class_named(S_queue.CLASSNAMES, $ptascii("b")) = (porigin_b)',
                  '$class_at(S_queue.CLASSES, porigin_a) = (pclassdesc_a)',
                  '$class_at(S_queue.CLASSES, porigin_b) = (pclassdesc_b)',
                  'pclassdesc_a.PROPERTIES = [ppropertydesc_a]',
                  'pclassdesc_b.PROPERTIES = [ppropertydesc_b]',
                  'ppropertydesc_a.ORIGIN = porigin_p',
                  'ppropertydesc_b.ORIGIN = porigin_shadow',
                  'ppropertydesc_a.DEFAULT = PROP_DEFERRED porigin_initializer',
                  'S_init = $static_default_test_resume($drive_steps(S_queue, 1))',
                  'S_init.TODO = (AT porigin_initializer (EVAL expression)) :: '
                  '(STATIC_DEFAULT_BIND pstaticdefaultcontext) :: ptask_tail*',
                  'pstaticdefaultcontext.DECL = porigin_p /\\ pstaticdefaultcontext.ROOT = '
                  'porigin_b',
                  '$method_current_scope(S_init) = (porigin_a)',
                  'S_ast = $static_default_test_resume($drive_steps(S_init, 1))',
                  '$static_default_trace(S_ast) = [ptraceframe]',
                  '~ptraceframe.HASARGS /\\ ptraceframe.ARGS = eps /\\ ptraceframe.CLASS = eps /\\ '
                  'ptraceframe.TYPE = eps',
                  'ptraceframe.FUNCTION = $ptascii("[constant expression]") /\\ ptraceframe.LINE = '
                  '5',
                  'S_frame = $trace_frame_array(S_ast, ptraceframe)',
                  'S_frame.RESULT = KNOWN (PARRAY n_frame)',
                  'S_frame.ARRAYS[n_frame].ITEMS = [ENTRY (KSTRING $ptascii("file")) (DIRECT '
                  '(PSTRING ptraceframe.FILE)), ENTRY (KSTRING $ptascii("line")) (DIRECT (PINT '
                  '5)), ENTRY (KSTRING $ptascii("function")) (DIRECT (PSTRING $ptascii("[constant '
                  'expression]")))]',
                  '$trace_frame_array_valid(S_frame, n_frame, $(n_frame + 1))',
                  'S = $static_default_test_seek(S_init, 3, 300)',
                  'S.TODO = (STATIC_DEFAULT_BIND pstaticdefaultcontext) :: ptask_tail*',
                  'S.CONSTCONTEXT = (pconstantcontext)',
                  'S.ORIGIN = (porigin_p)',
                  '$static_default_bind_valid(S, pstaticdefaultcontext)',
                  '$class_constant_state_valid(S) /\\ $class_statics_valid(S)',
                  'S_wrong = S[.ORIGIN = (porigin_shadow)][.CONSTCONTEXT = '
                  '(pconstantcontext[.ORIGIN = porigin_shadow])][.TODO = (STATIC_DEFAULT_BIND '
                  'pstaticdefaultcontext[.DECL = porigin_shadow]) :: ptask_tail*]',
                  '~$static_default_bind_valid(S_wrong, pstaticdefaultcontext[.DECL = '
                  'porigin_shadow])',
                  '~$class_constant_state_valid(S_wrong)',
                  '~$static_default_bind_valid(S, pstaticdefaultcontext[.ROOT = porigin_a])',
                  '~$static_default_bind_valid(S, pstaticdefaultcontext[.LINE = '
                  '$(pstaticdefaultcontext.LINE + 1)])',
                  '~$class_constant_state_valid(S[.TODO = (STATIC_DEFAULT_BIND '
                  'pstaticdefaultcontext) :: (STATIC_DEFAULT_BIND pstaticdefaultcontext) :: '
                  'ptask_tail*])',
                  '~$class_constant_state_valid(S[.TODO = ptask_tail*])',
                  'S_done = $drive_steps(S, 600)',
                  'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps',
                  '$class_static_at(S_done.CLASSSTATICS, porigin_p) = ({DECL porigin_p, STATE '
                  'PROP_VALUE (DIRECT (PINT 2))})',
                  '$class_static_at(S_done.CLASSSTATICS, porigin_shadow) = ({DECL porigin_shadow, '
                  'STATE PROP_VALUE (DIRECT (PINT 3))})',
                  '$class_constant_table_done(S_done, porigin_a) /\\ '
                  '$class_constant_table_done(S_done, porigin_b)'],
 'warm-alias': ['S = $drive_steps(S_initial[.COMPLETION = NORMAL], 1300)',
                'S.COMPLETION = NORMAL /\\ S.TODO = eps',
                '$class_named(S.CLASSNAMES, $ptascii("a")) = (porigin_a)',
                '$class_named(S.CLASSNAMES, $ptascii("b")) = (porigin_b)',
                '$class_at(S.CLASSES, porigin_a) = (pclassdesc_a)',
                'pclassdesc_a.PROPERTIES = [ppropertydesc]',
                'ppropertydesc.ORIGIN = porigin_p',
                '$class_static_at(S.CLASSSTATICS, porigin_p) = (pclassstatic)',
                'pclassstatic.STATE = PROP_VALUE (ALIAS n_cell)',
                'S.STORE[n_cell] = DEFINED (PINT 7)',
                '$propref_source_present(S.PROPREFS, n_cell, CLASS_PROP_SOURCE porigin_p)',
                '$class_statics_valid(S) /\\ $proprefs_valid(S) /\\ $class_constant_state_valid(S)',
                '$class_constant_table_done(S, porigin_a) /\\ $class_constant_table_done(S, '
                'porigin_b)',
                '~$class_statics_valid(S[.PROPREFS = eps])',
                'S_wrong_type = S[.STORE = $set_cell(S.STORE, n_cell, DEFINED (PSTRING '
                '$ptascii("bad")))]',
                '~$class_statics_valid(S_wrong_type)',
                'S_roots = $prune_allocations(S[.ENV = eps][.GLOBALTABLE = eps][.RESULT = KNOWN '
                'PNULL][.BASE = BASE_VALUE (KNOWN PNULL)])',
                'HCELL n_cell <- S_roots.ALLOCATIONS',
                '$class_statics_valid(S_roots) /\\ $proprefs_valid(S_roots)',
                '~$propref_source_valid(S, n_cell, CLASS_PROP_SOURCE porigin_b)'],
 'array-roots': ['S = $drive_steps(S_initial[.COMPLETION = NORMAL], 1300)',
                 'S.COMPLETION = NORMAL /\\ S.TODO = eps',
                 '$class_named(S.CLASSNAMES, $ptascii("a")) = (porigin_a)',
                 '$class_at(S.CLASSES, porigin_a) = (pclassdesc_a)',
                 'pclassdesc_a.PROPERTIES = [ppropertydesc]',
                 '$class_static_at(S.CLASSSTATICS, ppropertydesc.ORIGIN) = (pclassstatic)',
                 'pclassstatic.STATE = PROP_VALUE (DIRECT (PARRAY n_property))',
                 '$class_constant_lookup(S, porigin_a, $ptascii("X"), |S.CLASSES|) = '
                 '(pclassconstantdesc)',
                 '$default_cache_at(S.CLASSCONSTANTCACHE, pclassconstantdesc.ORIGIN) = '
                 '(pdefaultcache)',
                 'pdefaultcache.VALUE = PARRAY n_cache',
                 'n_property =/= n_cache',
                 '$entry_lookup(S.ARRAYS[n_property].ITEMS, KINT 1) = (DIRECT (PARRAY '
                 'n_property_child))',
                 '$entry_lookup(S.ARRAYS[n_cache].ITEMS, KINT 1) = (DIRECT (PARRAY n_cache_child))',
                 '$entry_lookup(S.ARRAYS[n_property_child].ITEMS, KINT 0) = (DIRECT (PINT 7))',
                 '$entry_lookup(S.ARRAYS[n_cache_child].ITEMS, KINT 0) = (DIRECT (PINT 3))',
                 '$class_constant_state_valid(S) /\\ $class_statics_valid(S) /\\ '
                 '$heap_valid($heap_graph(S))',
                 'S_property_only = $prune_allocations(S[.ENV = eps][.GLOBALTABLE = '
                 'eps][.CLASSCONSTANTCACHE = eps][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN '
                 'PNULL)])',
                 'HARRAY n_property <- S_property_only.ALLOCATIONS /\\ HARRAY n_property_child <- '
                 'S_property_only.ALLOCATIONS',
                 '~(HARRAY n_cache <- S_property_only.ALLOCATIONS) /\\ ~(HARRAY n_cache_child <- '
                 'S_property_only.ALLOCATIONS)',
                 'S_cache_only = $prune_allocations(S[.ENV = eps][.GLOBALTABLE = '
                 'eps][.CLASSSTATICS = eps][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN '
                 'PNULL)])',
                 'HARRAY n_cache <- S_cache_only.ALLOCATIONS /\\ HARRAY n_cache_child <- '
                 'S_cache_only.ALLOCATIONS',
                 '~(HARRAY n_property <- S_cache_only.ALLOCATIONS) /\\ ~(HARRAY n_property_child '
                 '<- S_cache_only.ALLOCATIONS)'],
 'prototype-prefix': ['S = $static_default_test_seek(S_initial[.COMPLETION = NORMAL], 5, 900)',
                      '$class_named(S.CLASSNAMES, $ptascii("a")) = (porigin_a)',
                      '$class_named(S.CLASSNAMES, $ptascii("b")) = (porigin_b)',
                      '$class_at(S.CLASSES, porigin_a) = (pclassdesc_a)',
                      'pclassdesc_a.PROPERTIES = [ppropertydesc]',
                      'ppropertydesc.ORIGIN = porigin_p',
                      'ppropertydesc.DEFAULT = PROP_DEFERRED porigin_initializer',
                      '$class_static_at(S.CLASSSTATICS, porigin_p) = ({DECL porigin_p, STATE '
                      'PROP_VALUE (DIRECT (PINT 1))})',
                      'S.CLASSCONSTANTHISTORY = [CCLINK porigin_a n_link_a, CCSTATIC porigin_p '
                      'porigin_new_a n_fill, CCUPDATE porigin_a porigin_a porigin_new_a n_update, '
                      'CCLINK porigin_b n_link_b]',
                      '$(n_fill < n_link_b)',
                      '$class_constant_table_done(S, porigin_a) /\\ ~$class_constant_table_done(S, '
                      'porigin_b)',
                      '~$static_default_link_done(S, porigin_b, |S.CLASSES|)',
                      'S.TODO = (CLASS_CONST_TABLE_UPDATE porigin_b z) :: ptask_tail*',
                      'S.ORIGIN = (porigin_new_b)',
                      '$static_default_tasks(S, porigin_b, z) = eps',
                      '$class_constant_state_valid(S) /\\ $class_statics_valid(S)',
                      'S_future = S[.CLASSCONSTANTHISTORY = [CCLINK porigin_a n_link_a, CCSTATIC '
                      'porigin_p porigin_new_b n_fill, CCUPDATE porigin_a porigin_a porigin_new_a '
                      'n_update, CCLINK porigin_b n_link_b]]',
                      '~$class_constant_history_valid(S_future)',
                      'S_done = $drive_steps(S, 300)',
                      'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps',
                      '$class_constant_table_done(S_done, porigin_a) /\\ '
                      '$class_constant_table_done(S_done, porigin_b)',
                      '$static_default_fills(S_done.CLASSCONSTANTHISTORY) = [porigin_p]',
                      '$class_constant_state_valid(S_done) /\\ $class_statics_valid(S_done)']}

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

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
 (out/'prepared.json').write_text(json.dumps({'scope':'Checked source/fixture preparation; numeric bodies unrun.','root':str(ROOT),'records':records},indent=2)+'\n')
 return records

def run(out):
 interrupted=None;cleaning=False;process=None
 def stop(signum,frame):
  nonlocal interrupted
  interrupted=signum
  if not cleaning:raise RuntimeError('interrupted '+str(signum))
 old=signal.signal(signal.SIGTERM,stop)
 modules=[ROOT/m for m in json.loads((ROOT/'spec/semantics/modules.json').read_text())]
 watched=[*modules,Path(__file__),ROOT/'spec/semantics/modules.json',ROOT/'tests/semantics/_build/default/numeric_runner.exe',ROOT/'_build/default/adapter/main.exe',ROOT/'.tools/php/bin/php',ROOT/'.tools/php-file.so',ROOT/'frontend/worker.php',ROOT/'tests/semantics/recorded_worker.py']
 before={str(p.relative_to(ROOT)):sha(p) for p in watched}
 report={'scope':'Deferred static-default source-derived state controls; no native execution.','inputs':before,'phases':[]}
 try:
  records=prepare(out)
  for row in records:
   raw=out/row['id'];raw.mkdir()
   command=[str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'),*map(str,modules),row['fixture']]
   status={'supplied_argv':command,'supplied_cwd':str(ROOT),'supplied_environment':ENV,'host_timeout_seconds':120,'observed_exit':None}
   try:
    with (raw/'stdout').open('xb') as stdout,(raw/'stderr').open('xb') as stderr:
     process=subprocess.Popen(command,cwd=ROOT,env=ENV,stdout=stdout,stderr=stderr,start_new_session=True)
     status.update(popen_args=process.args,pid=process.pid,owned_pgid=process.pid)
     (raw/'command.json').write_text(json.dumps(status,indent=2)+'\n')
     status['observed_exit']=process.wait(timeout=120)
   except BaseException as exc:status['error']=repr(exc)
   finally:
    cleaning=True
    if process is not None:
     try:os.killpg(process.pid,signal.SIGKILL)
     except ProcessLookupError:pass
     status['cleanup_exit']=process.wait(timeout=5);status['owned_group_after']=owned_members(process.pid)
    status['interrupted_by']=interrupted
    (raw/'command.json').write_text(json.dumps(status,indent=2)+'\n')
    process=None;cleaning=False
   passed=status.get('observed_exit')==0 and status.get('cleanup_exit')==0 and status.get('owned_group_after')==[] and interrupted is None and 'error' not in status and (raw/'stdout').read_bytes()==b'true\n' and (raw/'stderr').read_bytes()==b''
   report['phases'].append({'id':row['id'],'pass':passed,'main_predicates':row['main_predicates'],'command_record':str(raw/'command.json'),'stdout_sha256':sha(raw/'stdout'),'stderr_sha256':sha(raw/'stderr')})
   assert passed,raw
  assert before=={str(p.relative_to(ROOT)):sha(p) for p in watched},'inputs changed'
  report['result']='pass'
 finally:
  signal.signal(signal.SIGTERM,old)
  (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 print('PASS deferred static-default controls',sum(r['main_predicates'] for r in records),out)

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--prepare');args=parser.parse_args()
 if args.prepare:prepare(Path(args.prepare));print(args.prepare)
 else:
  out=Path(tempfile.mkdtemp(prefix='deferred-static-default-',dir=ROOT/'.tools'))/'run';run(out)
