#!/usr/bin/env python3
"""Private slot identities, inherited dynamic fallback and retained alias roots."""
from pathlib import Path
import base64
import hashlib
import json
import subprocess
import tempfile
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
PREFIX = '''
dec $private_ready(pstate) : bool
def $private_ready(S) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("hold")
def $private_ready(S) = false -- otherwise
dec $private_seek(pstate, nat) : pstate
def $private_seek(S, n) = S -- if $private_ready(S)
def $private_seek(S, 0) = S -- if ~$private_ready(S)
def $private_seek(S, n) = $private_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$private_ready(S) /\\ $(n > 0)
'''
SOURCES = {
 'aliases': b'<?php function hold($o){$z=1;}class A{private int $x=1;public function &a(){return $this->x;}}class B extends A{private string $x="b";public function &b(){return $this->x;}}$o=new B;$a=&$o->a();$b=&$o->b();hold($o);$a=2;$b="c";echo $a,$b;unset($o);$a=3;$b="d";echo $a,$b;',
 'dynamic': b'<?php function hold($o){$z=1;}class A{private int $x=1;public function go(){hold($this);echo $this->x;}}class B extends A{}$o=new B;$o->x=2;$o->go();echo $o->x;unset($o);',
}

def main():
    out = Path(tempfile.mkdtemp(prefix='private-property-protocol-', dir=ROOT / '.tools'))
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = modules + [Path(__file__), ROOT / 'spec/semantics/modules.json', ROOT / 'spec/php.watsup', ROOT / 'spec/schema.json',
                        ROOT / '_build/default/adapter/main.exe', ROOT / '.tools/php-file.so', ROOT / 'tests/semantics/_build/default/numeric_runner.exe']
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d', 'extension='+str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'),str(ROOT)], out / 'adapter')
    records=[]
    try:
        for name, source in SOURCES.items():
            path=out/(name+'.php');path.write_bytes(source)
            parsed=frontend.request({'op':'parse','source':base64.b64encode(source).decode()});assert parsed['accepted']
            checked=adapter.request({'op':'check','ast':parsed['ast'],'fixture':True});assert checked['ok']
            initial='$php_run('+checked['fixture']+', 0, '+json.dumps(base64.b64encode(str(path).encode()).decode())+')'
            checks=[
                'S_initial = '+initial,
                'S = $private_seek(S_initial[.COMPLETION = NORMAL], 2048)[.COMPLETION = NORMAL]',
                'S.CLASSES = [pclassdesc_a,pclassdesc_b]',
                'pclassdesc_a.PROPERTIES = [ppropertydesc_a]',
                'ppropertydesc_a.VISIBILITY = PROPERTY_PRIVATE',
                'ppropertydesc_a.NAME = [120]',
                'ppropertydesc_a.KEY = [0,65,0,120]',
                'S.OBJECTPROPS = [pobjectprops]',
                'n_object = pobjectprops.OBJECT',
                'S.OBJECTS[n_object] = INSTANCE pclassdesc_b.ORIGIN',
                '$call_descriptors_valid(S)', '$call_current_valid(S)', '$call_frames_valid(S,S.FRAMES)',
                '$property_state_valid(S)', '$heap_valid($heap_graph(S))',
                '$($heap_owners($heap_graph(S), HOBJECT n_object) > 0)',
                '~$call_descriptors_valid(S[.CLASSES = [pclassdesc_a[.PROPERTIES = [ppropertydesc_a[.KEY = [0,66,0,120]]]],pclassdesc_b]])',
                '~$call_descriptors_valid(S[.CLASSES = [pclassdesc_a[.PROPERTIES = [ppropertydesc_a[.VISIBILITY = PROPERTY_PROTECTED]]],pclassdesc_b]])',
                '$property_resolve(S,n_object,ppropertydesc_a.KEY) = PROPERTY_BADNAME',
            ]
            if name=='aliases':
                checks += [
                    'pclassdesc_b.PROPERTIES = [ppropertydesc_b]',
                    'ppropertydesc_b.NAME = ppropertydesc_a.NAME',
                    'ppropertydesc_b.KEY = [0,66,0,120]',
                    'ppropertydesc_b.ORIGIN =/= ppropertydesc_a.ORIGIN',
                    '$property_layout(S,pclassdesc_b.ORIGIN,|S.CLASSES|) = [ppropertydesc_a,ppropertydesc_b]',
                    'pobjectprops.SLOTS = [ppropertyslot_a,ppropertyslot_b]',
                    'ppropertyslot_a.NAME = ppropertydesc_a.KEY', 'ppropertyslot_b.NAME = ppropertydesc_b.KEY',
                    'ppropertyslot_a.STATE = PROP_VALUE (ALIAS n_a)', 'ppropertyslot_b.STATE = PROP_VALUE (ALIAS n_b)',
                    'n_a =/= n_b',
                    '$propref_at(S.PROPREFS,n_a) = (ppropref_a)', '$propref_at(S.PROPREFS,n_b) = (ppropref_b)',
                    'ppropref_a.SOURCES = [{OBJECT n_object, NAME ppropertydesc_a.KEY, DECL ppropertydesc_a.ORIGIN}]',
                    'ppropref_b.SOURCES = [{OBJECT n_object, NAME ppropertydesc_b.KEY, DECL ppropertydesc_b.ORIGIN}]',
                    '~$propref_source_valid(S,n_a,{OBJECT n_object,NAME ppropertydesc_b.KEY,DECL ppropertydesc_a.ORIGIN})',
                    '~$property_slots_valid(S,[ppropertydesc_a,ppropertydesc_b],[ppropertyslot_a,ppropertyslot_b[.NAME = ppropertydesc_a.KEY]])',
                    '~$property_unique_names([ppropertyslot_a,ppropertyslot_b[.NAME = ppropertydesc_a.KEY]])',
                    '~$property_dynamic_name_allowed(S,pclassdesc_b.ORIGIN,[120])',
                    '$property_resolve(S,n_object,[120]) = PROPERTY_DENIED ppropertydesc_b',
                    '$property_quiet(S,POBJECT n_object,[120],1).RESULT = KNOWN PNULL',
                ]
            else:
                checks += [
                    'pclassdesc_b.PROPERTIES = eps',
                    'pobjectprops.SLOTS = [ppropertyslot_a,ppropertyslot_dynamic]',
                    'ppropertyslot_a.NAME = ppropertydesc_a.KEY',
                    'ppropertyslot_dynamic.NAME = [120]', 'ppropertyslot_dynamic.DECL = eps',
                    '$property_dynamic_name_allowed(S,pclassdesc_b.ORIGIN,[120])',
                    '~$property_dynamic_name_allowed(S,pclassdesc_a.ORIGIN,[120])',
                    '$property_dynamic_no_shadow(S,pclassdesc_b.ORIGIN,pobjectprops.SLOTS)',
                    '~$property_dynamic_no_shadow(S,pclassdesc_a.ORIGIN,pobjectprops.SLOTS)',
                    '$property_resolve(S,n_object,[120]) = PROPERTY_ACCESS ([120])',
                    '$property_visible_key(S,n_object,[120])', '~$property_visible_key(S,n_object,ppropertydesc_a.KEY)',
                    'S.FRAMES = pframe_method :: pframe_rest*', 'pframe_method.CONTEXT = (pcallcontext_method)',
                    'pcallcontext_method.LEXICAL_CLASS = (pclassdesc_a.ORIGIN)',
                    'S_scope = S[.CURRENT = pframe_method.CONTEXT]',
                    '$property_resolve(S_scope,n_object,[120]) = PROPERTY_ACCESS ppropertydesc_a.KEY',
                    '~$property_visible_key(S_scope,n_object,[120])', '$property_visible_key(S_scope,n_object,ppropertydesc_a.KEY)',
                    '~$call_saved_context_valid(S,pframe_method[.CONTEXT = (pcallcontext_method[.LEXICAL_CLASS = (pclassdesc_b.ORIGIN)])])',
                ]
            checks += ['S_done = $drive(S,2048)', 'S_done.COMPLETION = NORMAL',
                       'S_done = $drive(S_initial[.COMPLETION = NORMAL],2048)',
                       '$heap_valid($heap_graph(S_done))','$property_state_valid(S_done)',
                       '$heap_owners($heap_graph(S_done),HOBJECT n_object) = 0','S_done.PROPREFS = eps']
            fixture=out/(name+'.watsup');fixture.write_text(PREFIX+'\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+c+'\n' for c in checks))
            result=subprocess.run([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'),*map(str,modules),str(fixture)],capture_output=True,text=True,timeout=240)
            (out/(name+'.stdout')).write_text(result.stdout);(out/(name+'.stderr')).write_text(result.stderr);(out/(name+'.status.json')).write_text(json.dumps({'exit_status':result.returncode}))
            assert result.returncode==0 and result.stdout=='true\n' and not result.stderr,(name,result.stderr[-3000:])
            records.append({'case':name,'assertions':len(checks),'source_sha256':hashlib.sha256(source).hexdigest()});print(name,len(checks),flush=True)
    finally:
        frontend.close();adapter.close()
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
    (out/'report.json').write_text(json.dumps({'result':'pass','inputs':hashes,'records':records},indent=2)+'\n');print(out)

if __name__=='__main__':main()
