#!/usr/bin/env python3
"""Source-derived current, saved and error trace owners for Closure::__invoke."""
from pathlib import Path
import sys,json,hashlib,base64,tempfile,subprocess
ROOT = Path(__file__).resolve().parents[2]
D = Path(tempfile.mkdtemp(prefix='method-wrapper-protocol-', dir=ROOT/'.tools'))
SOURCES = {'wrapper-owner': '<?php function probe(){}$x=1;$f=function($a=1,&$b=0,$c=0,...$tail){unset($c,$tail);probe();$b=7;return 9;};echo $f->__invoke(b:$x,c:[1],key:[2]);unset($f);echo $x;\n', 'wrapper-error-owner': '<?php $f=function($x){unset($x);missing();};$f->__invoke([1]);\n'}
for name, source in SOURCES.items():
    (D/(name+'.php')).write_text(source)
sys.path.insert(0,str(ROOT/'tests/semantics'));from recorded_worker import Worker
PFX='''
dec $stage(pstate) : bool
def $stage(S) = true -- if STAGE
def $stage(S) = false -- otherwise
dec $seek(pstate,nat) : pstate
def $seek(S,n) = S -- if $stage(S)
def $seek(S,n) = $seek($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1))) -- if ~$stage(S) -- if $(n > 0)
dec $outputs(pevent*) : nat*
def $outputs(eps) = eps
def $outputs((OUTPUT n*) :: pevent*) = n* ++ $outputs(pevent*)
def $outputs((WARNING n* z) :: pevent*) = $outputs(pevent*)
def $outputs((DIAGNOSTIC text n* z) :: pevent*) = $outputs(pevent*)
'''
shape=['pcallcontext.WRAPPER = (pnamedargs)','pnamedargs.SLOTS = [NAMED_HOLE,NAMED_SENT (REFERENCE n_ref),NAMED_SENT (KNOWN (PARRAY n_array))]','pnamedargs.NAMED = [(preqbytes,KNOWN (PARRAY n_named))]','preqbytes = $ptascii("key")','$heap_owners($heap_graph(S),HARRAY n_array) = 2','(HARRAY n_array) <- $pools_nodes(S.POOLS)','~$wrapper_context_valid(S,pcallcontext[.WRAPPER = eps])','~$wrapper_context_valid(S,pcallcontext[.WRAPPER = (pnamedargs[.SLOTS = [NAMED_SENT (KNOWN PNULL),NAMED_SENT (REFERENCE n_ref),NAMED_SENT (KNOWN (PARRAY n_array))]])])','~$wrapper_context_valid(S,pcallcontext[.WRAPPER = (pnamedargs[.SLOTS = [NAMED_HOLE,NAMED_SENT (KNOWN (PINT 1)),NAMED_SENT (KNOWN (PARRAY n_array))]])])','~$wrapper_context_valid(S,pcallcontext[.WRAPPER = (pnamedargs[.NAMED = [($ptascii("wrong"),KNOWN (PARRAY n_named))]])])','$wrapper_roots(pcallcontext.WRAPPER) = [HCELL n_ref,HARRAY n_array,HARRAY n_named]','S_done.COMPLETION = NORMAL','$outputs(S_done.EVENTS) = [57,55]','$heap_owners($heap_graph(S_done),HARRAY n_array) = 1','$heap_owners($heap_graph(S_done),HARRAY n_named) = 1']
CASES={
'current':('wrapper-owner','S.CURRENT = (pcallcontext) -- if pcallcontext.WRAPPER =/= eps -- if $lookup(S.ENV,$ptascii("c")) = eps -- if $lookup(S.ENV,$ptascii("tail")) = eps',['S.CURRENT = (pcallcontext)']+shape+['~$call_current_valid(S[.CURRENT = (pcallcontext[.WRAPPER = eps])])']),
'saved':('wrapper-owner','S.CURRENT = (pcallcontext) -- if pcallcontext.NAME = $ptascii("probe")',['S.FRAMES = pframe :: pframe_tail*','pframe.CONTEXT = (pcallcontext)']+shape+['~$call_saved_context_valid(S,pframe[.CONTEXT = (pcallcontext[.WRAPPER = eps])])','S.CURRENT = (pcallcontext_probe)','~$call_current_valid(S[.CURRENT = (pcallcontext_probe[.WRAPPER = pcallcontext.WRAPPER])])']),
'error':('wrapper-error-owner','S.TODO = (ERROR_UNWIND pcompletion) :: ptask* -- if S.TRACE = ptraceframe :: ptraceframe_tail*',['S.TRACE = [ptraceframe,ptraceframe_wrapper]','ptraceframe.VALUES = [PNULL]','ptraceframe_wrapper.NAME = $ptascii("Closure->__invoke")','ptraceframe_wrapper.VALUES = [PARRAY n_array]','$trace_roots(S.TRACE) = [HARRAY n_array]','$heap_owners($heap_graph(S),HARRAY n_array) = 3','(HARRAY n_array) <- $pools_nodes(S.POOLS)','S_done.TRACE = S.TRACE','$heap_owners($heap_graph(S_done),HARRAY n_array) = 2','S_done.CURRENT = eps','$outputs(S_done.EVENTS) = eps'])}
mods=[ROOT/p for p in json.loads((ROOT/'spec/semantics/modules.json').read_text())];inputs=mods+[ROOT/p for p in ['spec/semantics/modules.json','spec/php.watsup','spec/schema.json','frontend/worker.php','frontend/FileLexer.php','frontend/target.php','tests/semantics/_build/default/numeric_runner.exe','_build/default/adapter/main.exe','.tools/php/bin/php','.tools/php-file.so']]+[D/(n+'.php') for n in ['wrapper-owner','wrapper-error-owner']]+[Path(__file__)]
def hashes():return {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
before=hashes();out=D;rows=[]
for name,(src,stage,checks) in CASES.items():
 dest=out/name;dest.mkdir();p=D/(src+'.php')
 fw=Worker([str(ROOT/'.tools/php/bin/php'),'-n','-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')],dest/'frontend');aw=Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)],dest/'adapter')
 try:
  parsed=fw.request({'op':'parse','source':base64.b64encode(p.read_bytes()).decode()});assert parsed['accepted'];checked=aw.request({'op':'check','ast':parsed['ast'],'fixture':True});assert checked['ok']
 finally:
  try:fw.close()
  finally:aw.close()
 initial='$php_run('+checked['fixture']+',0,'+json.dumps(base64.b64encode(str(p).encode()).decode())+')'
 common=['S_initial = '+initial,'S = $seek(S_initial[.COMPLETION = NORMAL],2000)[.COMPLETION = NORMAL]','$call_descriptors_valid(S)','$heap_valid($heap_graph(S))','S_done = $drive(S,2000)','S_done = $drive(S_initial[.COMPLETION = NORMAL],2000)','$heap_valid($heap_graph(S_done))','S_done.FRAMES = eps','S_done.TODO = eps']
 fixture=dest/'test.watsup';fixture.write_text(PFX.replace('STAGE',stage)+'\ndec $main() : bool\ndef $main() = true\n'+''.join(' -- if '+a+'\n' for a in common+checks))
 r=subprocess.run([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'),*[str(p) for p in mods],str(fixture)],capture_output=True,timeout=300)
 (dest/'stdout').write_bytes(r.stdout);(dest/'stderr').write_bytes(r.stderr);row={'name':name,'assertions':len(common+checks),'pass':r.returncode==0 and r.stdout==b'true\n' and not r.stderr,'exit':r.returncode};rows.append(row);print(row,flush=True)
 if not row['pass']:print(r.stderr.decode()[-2000:],flush=True)
stable=before==hashes();(out/'report.json').write_text(json.dumps({'result':'pass' if stable and all(r['pass'] for r in rows) else 'fail','stable':stable,'rows':rows,'inputs':before},indent=2)+'\n');print(out,flush=True)

assert stable and all(row['pass'] for row in rows), 'wrapper protocol failed'
