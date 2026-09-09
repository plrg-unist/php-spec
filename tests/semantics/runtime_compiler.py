#!/usr/bin/env python3
"""Ordered source bridge invariants using checked original-source occurrences."""
import base64, json, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tests/semantics'))
import static_types as types, source_occurrences as occurrences

def main():
    subprocess.run([str(ROOT/'scripts/opam-exec.sh'),'dune','build','--root',str(ROOT/'tests/semantics'),'numeric_runner.exe'],cwd=ROOT,check=True,timeout=120)
    runner=ROOT/'tests/semantics/_build/default/numeric_runner.exe'
    specs=[ROOT/p for p in json.loads((ROOT/'spec/semantics/modules.json').read_text())]
    before=types.syntax_validation.implementation_fingerprint()
    frontend=types.Worker([str(types.PHP),'-n',*types.FLAGS,'-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')])
    adapter=types.Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)])
    cases=[]; records=[]
    def checked(source):
        parsed=frontend.request({'op':'parse','source':base64.b64encode(source).decode()}); assert parsed['accepted'],parsed
        result=adapter.request({'op':'check','ast':parsed['ast'],'fixture':True}); assert result['ok'],result
        records.append({'source_base64':base64.b64encode(source).decode(),'ast':result['ast']})
        return result
    path=lambda steps:occurrences.path_term(steps)
    I=lambda n:('INDEX',n)
    F=lambda n:('FIELD',n)
    try:
        c=checked(b'<?php [NAN];[NAN];')
        expr=occurrences.node_term(c['ast']['program'][0]['fields'][0]); p=path([I(0),F(0)]);q=path([I(1),F(0)])
        prefix=[f'P = $ppstart(71, {c["fixture"]}, ([47,112,255]))','S = $compile_source($initial_state(NORMAL)[.FILES = [SOURCEFILE 71 ([47,112,255])]], P)','S.COMPLETION = NORMAL',f'$compiled_read(S, PORIGIN 71 {p}) = (PARRAY n_first)',f'$compiled_read(S, PORIGIN 71 {q}) = (PARRAY n_second)','n_first =/= n_second']
        cases.append(prefix+['S_done = $drive(S, 1000)','S_done.COMPLETION = NORMAL','S_done.HELD = eps','S_done.POOLS = S.POOLS','S_clean = $prune_allocations($release_temporaries(S_done))','S_clean.POOLS = S.POOLS',f'S_again = $drive(S_clean[.TODO = [AT (PORIGIN 71 {p}) (EVAL {expr})]], 1000)','S_again.RESULT = KNOWN (PARRAY n_first)','S_again.ORIGIN = eps','S_again.ARRAYS = S_clean.ARRAYS','S_again.ALLOCATIONS = S_clean.ALLOCATIONS','$identity_apply(S_again, false, PARRAY n_first, PARRAY n_second, 1).RESULT = KNOWN (PBOOL false)'])
        cases.append(prefix+[f'S_other = $compile_source(S, $ppstart(72, {c["fixture"]}, ([47,113])))','S_other.COMPLETION = NORMAL',f'$compiled_read(S_other, PORIGIN 72 {p}) = (PARRAY n_other)','n_other =/= n_first','n_other =/= n_second','S_dynamic = $allocate_array(S_other, $array_empty())','S_dynamic.RESULT = KNOWN (PARRAY n_dynamic)','n_dynamic =/= n_other','n_dynamic =/= n_first','$heap_valid($heap_graph(S_dynamic))'])
        for budget in (0,1,2,3,5):
            cases.append(prefix+[f'S_budget = $drive(S, {budget})','S_budget.COMPLETION = BUDGET','$drive(S_budget[.COMPLETION = NORMAL], 1000) = $drive(S, 1000)','S_budget.POOLS = S.POOLS'])
        c=checked(b'<?php $u=7;$a=[$u,"abc"["1x"]];$a[0]=1;unset($a[0]);')
        root=path([I(1),F(0),F(1)]);dim=path([I(1),F(0),F(1),F(0),I(1),F(1)]);write=path([I(2),F(0),F(0)]);unset=path([I(3),F(0),I(0)])
        cases.append([f'P = $ppstart(71, {c["fixture"]}, ([47,112]))','S = $compile_source($initial_state(NORMAL), P)','S.COMPLETION = NORMAL',f'$compiled_read(S, PORIGIN 71 {root}) = eps',f'$compiled_read(S, PORIGIN 71 {dim}) = (PSTRING ([98]))',f'$compiled_read(S, PORIGIN 71 {write}) = eps',f'$compiled_read(S, PORIGIN 71 {unset}) = eps',f'$ppaccess(P, {write}) = (PPW)',f'$ppaccess(P, {unset}) = (PPUNSET)','$drive(S, 1000).COMPLETION = NORMAL'])
        c=checked(b'<?php [[NAN],[NAN]];')
        child=path([I(0),F(0),F(0),I(0),F(1)])
        cases.append([f'P = $ppstart(71, {c["fixture"]}, ([47,112]))','S = $compile_source($initial_state(NORMAL), P)',f'$pool_value(S.POOLS, PORIGIN 71 {child}) = (PARRAY n)',f'$ppaccess(P, {child}) = eps',f'$compiled_read(S, PORIGIN 71 {child}) = eps','S_clean = $prune_allocations($release_temporaries(S))','(HARRAY n) <- S_clean.ALLOCATIONS'])
        c=checked(b'<?php [NAN];')
        prefix=[f'P = $ppstart(71, {c["fixture"]}, ([47,112]))']
        cases.append(prefix+['$compile_source($initial_state(NORMAL), P[.FOLD = P.FOLD[.MEMORY = P.FOLD.MEMORY[.ENV = [BIND ([120]) 0]]]]).COMPLETION = UNSUPPORTED "compiler variable storage in constant pool"'])
        cases.append(prefix+['$compile_source($initial_state(NORMAL), P[.FOLD = P.FOLD[.MEMORY = P.FOLD.MEMORY[.STORE = [UNDEFINED]]]]).COMPLETION = UNSUPPORTED "compiler variable storage in constant pool"'])
    finally:frontend.close();adapter.close()
    with tempfile.TemporaryDirectory(dir=ROOT/'.tools') as tmp:
        for i,assertions in enumerate(cases):
            fixture=Path(tmp)/'case.watsup';fixture.write_text('dec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+a+'\n' for a in assertions))
            run=subprocess.run([str(runner),*map(str,specs),str(fixture)],capture_output=True,text=True,cwd=ROOT,timeout=120)
            if run.returncode or run.stdout.strip()!='true':
                (ROOT/'.tools/runtime-compiler-failure.watsup').write_text(fixture.read_text())
                raise AssertionError((i,run.stdout,run.stderr))
    assert before==types.syntax_validation.implementation_fingerprint(),'inputs changed during bridge gate'
    report={'result':'pass','classification':'checked-source compilation and constructed execution/resumption states; no loop support claim','cases':len(cases),'assertions':sum(map(len,cases)),'records':records,'fingerprint':before}
    (ROOT/'coverage/semantics/runtime-compiler.json').write_text(json.dumps(report,indent=2)+'\n')
    print({k:report[k] for k in ('result','cases','assertions')})
if __name__=='__main__':main()
