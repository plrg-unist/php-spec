#!/usr/bin/env python3
"""Independent source-reached adaptation, publication, and cloned FCC checks."""
import base64, hashlib, json, os, subprocess, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker
CATALOGUE=ROOT/'tests/semantics/anonymous_trait_adaptations_cases.json'
CASES={row['id']:row for row in json.loads(CATALOGUE.read_text())['cases']}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
HELPERS='''dec $class169_review_at_new(pstate) : bool
def $class169_review_at_new(S) = true
  -- if S.TODO = (EVAL (NExprNew (NStmtClass phpType14 phpType24 ABSENT phpType44 phpType42 phpType23 metadata_class) phpType6 metadata_new)) :: ptask_tail*
def $class169_review_at_new(S) = false -- otherwise
dec $class169_review_seek_new(pstate,nat) : pstate
def $class169_review_seek_new(S,0) = S
def $class169_review_seek_new(S,n) = S -- if $(n > 0) /\\ $class169_review_at_new(S)
def $class169_review_seek_new(S,n) = $class169_review_seek_new($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if $(n > 0) /\\ ~$class169_review_at_new(S) /\\ S.COMPLETION = BUDGET
dec $class169_review_at_clone(pstate) : bool
def $class169_review_at_clone(S) = true
  -- if S.TODO = (TYPE_RECEIVE porigin 0) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = CLOSURE_TARGET n
  -- if S.OBJECTS[n] = METHODCLOSURE porigin porigin_site porigin_called eps
def $class169_review_at_clone(S) = false -- otherwise
dec $class169_review_seek_clone(pstate,nat) : pstate
def $class169_review_seek_clone(S,0) = S
def $class169_review_seek_clone(S,n) = S -- if $(n > 0) /\\ $class169_review_at_clone(S)
def $class169_review_seek_clone(S,n) = $class169_review_seek_clone($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if $(n > 0) /\\ ~$class169_review_at_clone(S) /\\ S.COMPLETION = BUDGET
'''

def checks(fixture,filename,case):
 c=[
  'program_source = '+fixture,
  'S_start = $php_run(program_source,0,'+json.dumps(base64.b64encode(filename).decode())+')',
  'S_start.COMPLETION = BUDGET /\\ ~S_start.COMPILESTOP',
  'S_pre = $class169_review_seek_new(S_start,100)',
  '$class169_review_at_new(S_pre) /\\ S_pre.COMPLETION = BUDGET',
  'S_pre.ORIGIN = (porigin_new)',
  '$anonymous_new_pending(S_pre,porigin_new) = (pclassdesc_raw)',
  '~pclassdesc_raw.EARLY',
  '$class_named(S_pre.CLASSNAMES,$ptlc(pclassdesc_raw.NAME)) = eps',
  '~$anonymous_runtime_declaration(S_pre.DECLARATIONS,pclassdesc_raw.ORIGIN)',
  '~$anonymous_new_available(S_pre,pclassdesc_raw)',
  'S_link = $drive_steps(S_pre[.COMPLETION = NORMAL],1)',
  'S_link.COMPLETION = BUDGET',
  '$class_at(S_link.CLASSES,pclassdesc_raw.ORIGIN) = (pclassdesc_live)',
  'pclassdesc_live =/= pclassdesc_raw',
  'pclassdesc_live[.PROPERTIES = $trait_notice_own_properties(pclassdesc_live.PROPERTIES)][.CONSTANTS = $trait_notice_own_constants(pclassdesc_live.CONSTANTS)][.METHODS = $trait_notice_own_methods(pclassdesc_live.METHODS,pclassdesc_live.ORIGIN)] = pclassdesc_raw',
  '$anonymous_runtime_declaration(S_link.DECLARATIONS,pclassdesc_live.ORIGIN)',
  '$class_named(S_link.CLASSNAMES,$ptlc(pclassdesc_live.NAME)) = (pclassdesc_live.ORIGIN)',
  '$declaration_history_valid(S_link)',
  '$anonymous_new_descriptor(S_link,porigin_new) = (pclassdesc_live)',
  '$anonymous_new_available(S_link,pclassdesc_live)',
  '$method_named(pclassdesc_live.METHODS,$ptascii("q")) = (pmethoddesc_q)',
  'pmethoddesc_q.OWNER = pclassdesc_live.ORIGIN /\\ pmethoddesc_q.VISIBILITY = PROPERTY_PUBLIC',
  'pmethoddesc_q.FUNCTION.ORIGIN = TRAIT_ORIGIN pclassdesc_live.ORIGIN porigin_q_source pmethoddesc_q.NAME',
  'S_forged = S_link[.CLASSES = $trait_class_set(S_link.CLASSES,pclassdesc_live[.METHODS = pclassdesc_live.METHODS ++ [pmethoddesc_q]])]',
  '~$declaration_history_valid(S_forged)',
  '$anonymous_new_descriptor(S_forged,porigin_new) = eps',
  'S_allocate = $drive_steps(S_link[.COMPLETION = NORMAL],1)',
  'S_allocate.COMPLETION = BUDGET /\\ S_allocate.RESULT = KNOWN (POBJECT n_allocated)',
  'S_allocate.OBJECTS[n_allocated] = INSTANCE pclassdesc_live.ORIGIN',
  '(HOBJECT n_allocated) <- S_allocate.ALLOCATIONS',
 ]
 if case=='parentless-multiple-aliases':
  c += [
   'pclassdesc_live.PARENT = eps /\\ pclassdesc_live.INTERFACES = eps',
   '$class_link_at(S_link.LINKEDPARENTS,pclassdesc_live.ORIGIN) = eps',
   '$pil_at(S_link.LINKEDINTERFACES,pclassdesc_live.ORIGIN) = eps',
   '$method_named(pclassdesc_live.METHODS,$ptascii("hidden")) = (pmethoddesc_hidden)',
   'pmethoddesc_hidden.VISIBILITY = PROPERTY_PROTECTED',
   '$method_named(pclassdesc_live.METHODS,$ptascii("privateAlias")) = (pmethoddesc_private)',
   'pmethoddesc_private.VISIBILITY = PROPERTY_PRIVATE',
   '$origin_source(pmethoddesc_hidden.FUNCTION.ORIGIN) = porigin_q_source /\\ $origin_source(pmethoddesc_private.FUNCTION.ORIGIN) = porigin_q_source',
   'pmethoddesc_hidden.FUNCTION.ORIGIN =/= pmethoddesc_q.FUNCTION.ORIGIN',
   'pmethoddesc_private.FUNCTION.ORIGIN =/= pmethoddesc_hidden.FUNCTION.ORIGIN',
  ]
 if case=='parented-precedence-excluded-alias-multiple-use':
  c += [
   'pclassdesc_live.PARENT = ($ptascii("Probe169Base")) /\\ pclassdesc_live.INTERFACES = eps',
   '$class_named(S_link.CLASSNAMES,$ptascii("probe169base")) = (porigin_base)',
   '$class_link_at(S_link.LINKEDPARENTS,pclassdesc_live.ORIGIN) = (SOURCE_PARENT porigin_base)',
   '$class_named(S_link.CLASSNAMES,$ptascii("probe169right")) = (porigin_right)',
   '$class_at(S_link.CLASSES,porigin_right) = (pclassdesc_right)',
   '$method_named(pclassdesc_right.METHODS,$ptascii("m")) = (pmethoddesc_right)',
   '$origin_source(pmethoddesc_right.FUNCTION.ORIGIN) = porigin_q_source',
   'pmethoddesc_q.FUNCTION.SIGNATURE.PARAMETERS = psparam :: eps',
   'psparam.TYPE = [(PTBRANCH ([PTCLASS $ptascii("Probe169Base")]))]',
   '$trait_plan(S_pre,pclassdesc_raw).TRAITS = [$ptascii("Probe169Left"),$ptascii("Probe169Right"),$ptascii("Probe169Extra")]',
   'S_clone = $class169_review_seek_clone(S_allocate,400)',
   '$class169_review_at_clone(S_clone) /\\ S_clone.COMPLETION = BUDGET',
   'S_clone.TODO = (TYPE_RECEIVE pmethoddesc_q.FUNCTION.ORIGIN 0) :: ptask_clone_tail*',
   'S_clone.CURRENT = (pcallcontext)',
   'pcallcontext.TARGET = CLOSURE_TARGET n_clone /\\ pcallcontext.INSTANCE = (n_clone)',
   'pcallcontext.LEXICAL_CLASS = (pclassdesc_live.ORIGIN) /\\ pcallcontext.CALLED_CLASS = (pclassdesc_live.ORIGIN)',
   'S_clone.OBJECTS[n_clone] = METHODCLOSURE pmethoddesc_q.FUNCTION.ORIGIN porigin_site pclassdesc_live.ORIGIN eps',
   '$closure_scope_at(S_clone.CLOSURESCOPES,n_clone) = (pclosurescope)',
   'pclosurescope.LEXICAL = pclassdesc_live.ORIGIN /\\ pclosurescope.CALLED = pclassdesc_live.ORIGIN',
   'pclosurescope.RECEIVER = eps /\\ pclosurescope.CREATION = eps',
   '$class_constant_callable_method_history_ordinary(S_clone,pmethoddesc_q,porigin_site,pclassdesc_live.ORIGIN,pclosurescope) = (pclassdesc_live.ORIGIN)',
   '$class_constant_callable_method_history_ordinary(S_clone,pmethoddesc_q,porigin_site,pclassdesc_live.ORIGIN,pclosurescope[.CALLED = porigin_base]) = eps',
   '$call_current_valid(S_clone)',
  ]
 if case=='interface-qualified-alias':
  c += [
   'pclassdesc_live.PARENT = eps /\\ pclassdesc_live.INTERFACES = [$ptascii("Probe169I")]',
   '$class_named(S_link.CLASSNAMES,$ptascii("probe169i")) = (porigin_interface)',
   '$pil_at(S_link.LINKEDINTERFACES,pclassdesc_live.ORIGIN) = (PILTARGETS [PILSOURCE $ptascii("Probe169I") porigin_interface])',
   '$anonymous_interface_targets_valid(S_link,pclassdesc_live)',
   '~$anonymous_new_available(S_link[.LINKEDINTERFACES = S_pre.LINKEDINTERFACES],pclassdesc_live)',
  ]
 return c

raw=Path(tempfile.mkdtemp(prefix='class169-review-state-',dir=ROOT/'.tools'))
report={'passed':False,'raw':str(raw),
        'revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'environment':{'LC_ALL':'C','TZ':'UTC'},'affinity':sorted(os.sched_getaffinity(0))}
watched=[ROOT/'spec/semantics/modules.json',ROOT/'spec/semantics/141-method-compiler.watsup',ROOT/'spec/semantics/228-trait-methods.watsup',ROOT/'spec/semantics/383-anonymous-classes.watsup',ROOT/'_build/default/adapter/main.exe',ROOT/'tests/semantics/_build/default/numeric_runner.exe',ROOT/'.tools/php/bin/php',ROOT/'tests/semantics/profile.json',CATALOGUE,Path(__file__)]
report['inputs_before']={str(p):sha(p) for p in watched}
frontend=adapter=None
try:
 frontend=Worker([str(ROOT/'.tools/php/bin/php'),'-n',*cross.invoke.types.FLAGS,'-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')],raw/'frontend')
 adapter=Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)],raw/'adapter')
 fixture=raw/'protocol.watsup';code=HELPERS;names=[];counts={}
 for i,case in enumerate(['parentless-multiple-aliases','parented-precedence-excluded-alias-multiple-use','interface-qualified-alias']):
  target=raw/(case+'.php');target.write_text(CASES[case]['source'])
  assert sha(target)==CASES[case]['source_sha256']
  parsed=frontend.request({'op':'parse','source':base64.b64encode(target.read_bytes()).decode()});assert parsed['accepted'] is True
  checked=adapter.request({'op':'check','ast':parsed['ast'],'fixture':True});assert checked['ok'] is True
  conditions=checks(checked['fixture'],os.fsencode(target),case);name=f'$class169_review_group{i}';names.append(name+'()');counts[case]=len(conditions)
  code+='dec '+name+'() : bool\ndef '+name+'() = true\n'+''.join('  -- if '+c+'\n' for c in conditions)
 code+='dec $main() : bool\ndef $main() = '+' /\\ '.join(names)+'\n';fixture.write_text(code)
 report.update(fixture=str(fixture),fixture_sha256=sha(fixture),conditions=counts)
 modules=[ROOT/name for name in json.loads((ROOT/'spec/semantics/modules.json').read_text())]
 command=[str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'),'--sl',*map(str,modules),str(fixture)]
 result=cross.invoke.process(command,raw/'numeric',1200,ROOT)
 report.update(exit=result.returncode,stdout=result.stdout.decode(errors='replace'),stderr=result.stderr.decode(errors='replace'),command=command)
 report['passed']=result.returncode==0 and result.stdout==b'true\n' and not result.stderr
finally:
 try:
  if adapter:adapter.close()
 finally:
  if frontend:frontend.close()
 report['inputs_after']={str(p):sha(p) for p in watched};report['inputs_stable']=report['inputs_before']==report['inputs_after'];report['passed']=report['passed'] and report['inputs_stable']
 (raw/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(raw/'report.json',report['passed'])

assert report['passed']
