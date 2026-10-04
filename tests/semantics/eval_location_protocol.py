#!/usr/bin/env python3
"""Eval creation locations survive initializer retirement; parser and runtime throws differ."""
from pathlib import Path
import base64
import hashlib
import json
import subprocess
import tempfile

from error_handler_run import recorded
from recorded_worker import Worker

R=Path(__file__).resolve().parents[2]
b64=lambda b:base64.b64encode(b).decode()
seq=lambda b:'('+str(list(b))+')'
PREFIX = r'''dec $location_class(pclassdesc*, preqbytes) : pclassdesc?
def $location_class(eps, preqbytes) = eps
def $location_class(pclassdesc :: pclassdesc_tail*, preqbytes) = (pclassdesc) -- if pclassdesc.NAME = preqbytes
def $location_class(pclassdesc :: pclassdesc_tail*, preqbytes) = $location_class(pclassdesc_tail*, preqbytes) -- if pclassdesc.NAME =/= preqbytes
dec $location_runtime_stage(pstate) : bool
def $location_runtime_stage(S) = true -- if S.TODO = (THROW_SEARCH 0) :: ptask_tail*
def $location_runtime_stage(S) = false -- otherwise
dec $seek_location_runtime(pstate, nat) : pstate
def $seek_location_runtime(S, n) = S -- if $location_runtime_stage(S) -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $seek_location_runtime(S, n) = $seek_location_runtime($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$location_runtime_stage(S) -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET -- if $(n > 0)
def $seek_location_runtime(S, n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
'''

def prepare_sources(out,main_name,main,handler_name,handler,eval_sources):
    d=out;d.mkdir();main_path=d/main_name;handler_path=d/handler_name
    main_path.write_bytes(main);handler_path.write_bytes(handler)
    front=Worker([str(R/'.tools/php/bin/php'),'-n','-d','extension='+str(R/'.tools/php-file.so'),str(R/'frontend/worker.php')],d/'frontend')
    try:
        ast_main=front.request({'op':'parse','source':b64(main)})
        ast_handler=front.request({'op':'parse-file','id':'0','mode':'file','profile':'cli-raw-85','requested':b64(bytes(handler_path)),'resolved':b64(bytes(handler_path)),'opened':b64(bytes(handler_path)),'source':b64(handler)})
        eval_rows=[front.request({'op':'parse-eval','id':str(i+2),'mode':'eval','profile':'cli-raw-85','source':b64(s)}) for i,s in enumerate(eval_sources)]
        assert ast_main['accepted'] and ast_handler['accepted']
    finally:front.close()
    adapter=Worker([str(R/'_build/default/adapter/main.exe'),str(R)],d/'adapter')
    try:
        checked_main=adapter.request({'op':'check','ast':ast_main['ast'],'fixture':True})['fixture']
        checked_handler=adapter.request({'op':'check','ast':ast_handler['ast'],'fixture':True})['fixture']
        responses=[]
        for i,(source,row) in enumerate(zip(eval_sources,eval_rows)):
            if row['accepted']:
                checked=adapter.request({'op':'check','ast':row['ast'],'fixture':True})['fixture']
                responses.append('(SOURCE_ACCEPT '+str(i+2)+' '+seq(source)+' '+checked+')')
            else:
                assert row['category'] in ('parser_rejection','parser_static_rejection')
                op='SOURCE_PARSE_REJECT' if row['category']=='parser_rejection' else 'SOURCE_COMPILE_REJECT'
                responses.append('('+op+' '+str(i+2)+' '+seq(source)+' '+seq(base64.b64decode(row['message']))+' '+str(row['line'])+')')
    finally:adapter.close()
    start='$php_file_run('+checked_main+', 2000, $base64('+json.dumps(b64(bytes(main_path)))+'), $base64('+json.dumps(b64(bytes(R)))+'))'
    opened='(FILE_OPENED 0 '+seq(bytes(main_path))+' '+seq(bytes(handler_path))+' '+seq(bytes(handler_path))+' '+seq(bytes(handler_path))+' '+seq(handler)+')'
    accepted='(SOURCE_ACCEPT 1 '+seq(handler)+' '+checked_handler+')'
    return d,['S_initial = '+start,'S_parse = $file_open_continue(S_initial, '+opened+')','S_wait = $file_parse_continue(S_parse, '+accepted+')'],responses

def build(out):
    P=Path(__file__).with_name('eval_location')/'constant'
    main=(P/'main.php').read_bytes()+b'''class IdleLocationOwner {const VALUE=E_STRICT+4;}
    class PlainLocationOwner {const VALUE=E_STRICT;}
    if (false) {class FutureLocationOwner {const VALUE=E_STRICT+8;}}
    '''
    d,checks,responses=prepare_sources(out/'retired','main.php',main,'handler.php',(P/'handler.php').read_bytes(),[b'return __FILE__;',b'throw new Exception("inside");',b'?'])
    checks += [
        'S_wait.COMPLETION = SOURCE_PENDING',
        '$call_descriptors_valid(S_wait)',
        'S_wait.EVALCONTEXTS = [pevalcontext]',
        'pevalcontext.UNIT = 2',
        'pevalcontext.SITE = PORIGIN 1 pcpath_site',
        'pevalcontext.LOCATION = (pconstantlocation)',
        'pconstantlocation.CLASS = PORIGIN 0 pcpath_class',
        'pconstantlocation.ROOT = PORIGIN 0 pcpath_root',
        'pconstantlocation.CHILD = PORIGIN 0 pcpath_child',
        'pevalcontext.LEXICAL_CLASS = eps',
        '$constant_location_valid(S_wait,pconstantlocation,2)',
        '$class_constant_source_location(S_wait,(pconstantlocation.CHILD)) = ((pconstantlocation.CHILD,6))',
        'pevalcontext.FILE = $call_sourcefile(S_wait.FILES,pconstantlocation.CLASS) ++ $ptascii("(6) : eval()") ++ [39] ++ $ptascii("d code")',
        '~$eval_context_valid(S_wait,pevalcontext[.LOCATION = eps])',
        '~$constant_location_valid(S_wait,pconstantlocation[.ROOT = pevalcontext.SITE],2)',
        '~$constant_location_valid(S_wait,pconstantlocation[.CHILD = pevalcontext.SITE],2)',
        '~$constant_location_valid(S_wait,pconstantlocation,0)',
        '$location_class(S_wait.CLASSES,$ptascii("IdleLocationOwner")) = (pclassdesc_idle)',
        '$class_constant_desc(pclassdesc_idle.CONSTANTS,$ptascii("VALUE")) = (pclassconstantdesc_idle)',
        'pconstantlocation_idle = {CLASS pclassdesc_idle.ORIGIN, ROOT pclassconstantdesc_idle.ORIGIN, CHILD $constant_child(pclassconstantdesc_idle.INITIALIZER,[PCFIELD 0])}',
        '$constant_location_valid(S_wait,pconstantlocation_idle,2)',
        '$eval_location_available(S_wait,(pconstantlocation_idle))',
        '~$eval_context_phase_valid(S_wait,pevalcontext[.LOCATION = (pconstantlocation_idle)])',
        '$location_class(S_wait.CLASSES,$ptascii("PlainLocationOwner")) = (pclassdesc_plain)',
        '$class_constant_desc(pclassdesc_plain.CONSTANTS,$ptascii("VALUE")) = (pclassconstantdesc_plain)',
        '~$constant_location_valid(S_wait,{CLASS pclassdesc_plain.ORIGIN, ROOT pclassconstantdesc_plain.ORIGIN, CHILD pclassconstantdesc_plain.INITIALIZER},2)',
        '$location_class(S_wait.CLASSES,$ptascii("FutureLocationOwner")) = (pclassdesc_future)',
        '$class_constant_desc(pclassdesc_future.CONSTANTS,$ptascii("VALUE")) = (pclassconstantdesc_future)',
        'pconstantlocation_future = {CLASS pclassdesc_future.ORIGIN, ROOT pclassconstantdesc_future.ORIGIN, CHILD $constant_child(pclassconstantdesc_future.INITIALIZER,[PCFIELD 0])}',
        '$constant_location_valid(S_wait,pconstantlocation_future,2)',
        '~$eval_location_available(S_wait,(pconstantlocation_future))',
        'S_second = $eval_continue(S_wait,'+responses[0]+')',
        'S_second.COMPLETION = SOURCE_PENDING',
        'S_third = $eval_continue(S_second,'+responses[1]+')',
        'S_third.COMPLETION = SOURCE_PENDING',
        'S_retired = $eval_continue(S_third,'+responses[2]+')',
        'S_retired.COMPLETION = SOURCE_PENDING',
        'S_retired.CLASSCONSTANTINIT = eps',
        'S_retired.CONSTCONTEXT = eps',
        '$class_constant_location(S_retired) = eps',
        'S_retired.EVALCONTEXTS = [pevalcontext_retired]',
        'pevalcontext_retired.UNIT = 5',
        'pevalcontext_retired.LOCATION = eps',
        '$call_descriptors_valid(S_retired)',
        '$eval_bindings_valid(S_retired,S_retired.EVALBINDINGS)',
        '$eval_binding_at(S_retired.EVALBINDINGS,2) = (pevalbinding)',
        'pevalbinding.LOCATION = (pconstantlocation)',
        '~$eval_bindings_valid(S_retired,[pevalbinding[.LOCATION = eps]])',
        '~$eval_bindings_valid(S_retired,[pevalbinding[.LOCATION = (pconstantlocation[.ROOT = pevalbinding.SITE])]])',
        '~$eval_bindings_valid(S_retired,[pevalbinding[.LOCATION = (pconstantlocation[.CHILD = $constant_child(pclassconstantdesc_idle.INITIALIZER,[PCFIELD 0])])]])',
        '$declaration_entry_binding(S_retired,S_wait,2,(pevalbinding.SITE))',
        '~$declaration_entry_binding(S_retired[.EVALBINDINGS = [pevalbinding[.LOCATION = (pconstantlocation_future)]]],S_wait,2,(pevalbinding.SITE))',
        '$failed_source_at(S_retired.FAILEDSOURCES,4) = (pfailedsource)',
        'pfailedsource.LOCATION = (pconstantlocation)',
        '$failed_source_record_valid(S_retired,pfailedsource)',
        '~$failed_source_record_valid(S_retired,pfailedsource[.LOCATION = eps])',
        '~((HOBJECT 1) <- S_retired.ALLOCATIONS)',
        'S_rejected = $eval_resume(S_third,'+responses[2]+')',
        'S_rejected.COMPLETION = NORMAL',
        'S_rejected.OBJECTS[1] = THROWABLE pthrowable_parse',
        '(HOBJECT 1) <- S_rejected.ALLOCATIONS',
        'pthrowable_parse.KIND = "ParseError"',
        'pthrowable_parse.ORIGIN = (PORIGIN 4 eps)',
        'pthrowable_parse.FILEORIGIN = pthrowable_parse.ORIGIN',
        '$throwable_source_origin_valid(S_rejected,1,pthrowable_parse)',
        '~$throwable_source_origin_valid(S_rejected,1,pthrowable_parse[.FILEORIGIN = (pconstantlocation.CLASS)])',
        '$throwable_field(S_rejected,1,"file") = PSTRING pfailedsource.FILE',
        '$throwable_field(S_rejected,1,"line") = PINT 1',
        '$call_descriptors_valid(S_rejected)',
        'S_runtime_start = $eval_resume(S_second,'+responses[1]+')',
        'S_runtime_reached = $seek_location_runtime(S_runtime_start,1000)',
        r'S_runtime_reached.COMPLETION = NORMAL \/ S_runtime_reached.COMPLETION = BUDGET',
        'S_runtime = S_runtime_reached[.COMPLETION = NORMAL]',
        'S_runtime.TODO = (THROW_SEARCH 0) :: ptask_runtime*',
        '(HOBJECT 0) <- S_runtime.ALLOCATIONS',
        '$throwable_field(S_runtime,0,"file") = PSTRING $call_sourcefile(S_runtime.FILES,pconstantlocation.CLASS)',
        '$throwable_field(S_runtime,0,"line") = PINT 6',
        '$call_descriptors_valid(S_runtime)',
    ]
    assert len(checks)==81
    fixture=d/'protocol.watsup'
    fixture.write_text(PREFIX+'dec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+c+'\n' for c in checks))
    return fixture,len(checks)


def main():
    out=Path(tempfile.mkdtemp(prefix='eval-location-protocol-',dir=R/'.tools'))
    print(out,flush=True)
    modules=[R/p for p in json.loads((R/'spec/semantics/modules.json').read_bytes())]
    inputs=[*modules,Path(__file__),R/'tests/semantics/eval_location/constant/main.php',
            R/'tests/semantics/eval_location/constant/handler.php',R/'frontend/worker.php',
            R/'tests/semantics/recorded_worker.py',R/'tests/semantics/error_handler_run.py',
            R/'.tools/php/bin/php',R/'.tools/php-file.so',R/'_build/default/adapter/main.exe',
            R/'tests/semantics/_build/default/numeric_runner.exe']
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    before={str(p.relative_to(R)):digest(p) for p in inputs}
    revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
    fixture,count=build(out)
    command=[str(R/'tests/semantics/_build/default/numeric_runner.exe'),*map(str,modules),str(fixture)]
    process=recorded(command,out/'numeric',90)
    passed=process['exit']==0 and not process['timeout'] and (out/'numeric.stdout').read_bytes()==b'true\n' and not (out/'numeric.stderr').read_bytes()
    assert before=={str(p.relative_to(R)):digest(p) for p in inputs}
    assert revision==subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
    report={'revision':revision,'assertions':count,'passed':passed,'inputs':before,
            'fixture_sha256':digest(fixture),'process':process,'environment':
            {'LC_ALL':'C','TZ':'UTC','PHP_SPEC_SCRIPT_ENCODING':'absent','other':'inherited'}}
    (out/'report.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print('eval-location',passed,count,flush=True)
    return passed


if __name__=='__main__':
    raise SystemExit(0 if main() else 1)
