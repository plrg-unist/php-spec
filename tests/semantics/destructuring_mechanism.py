#!/usr/bin/env python3
"""Checked destructuring effect occurrences, duplicate markers and permanent pools."""
import base64, json, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tests/semantics'))
import static_types as types
SOURCE=b'<?php echo (list($x)=[1])==[1],":",$x;'
CHECKS='  -- if S.COMPLETION = BUDGET\n  -- if S_out = $drive(S[.COMPLETION = NORMAL], 10000)\n  -- if S_out.COMPLETION = NORMAL\n  -- if S_dup = S[.CODE = [S.CODE[0][.EXPRESSIONS = S.CODE[0].EXPRESSIONS ++ S.CODE[0].EXPRESSIONS]]]\n  -- if S_dup_out = $drive(S_dup[.COMPLETION = NORMAL], 10000)\n  -- if S_dup_out[.CODE = S.CODE] = S_out\n  -- if $heap_valid($heap_graph(S_dup_out))\n  -- if S_missing = S[.CODE = [S.CODE[0][.EXPRESSIONS = S.CODE[0].EXPRESSIONS ++ [(CODEEFFECT ([PCINDEX 0, PCFIELD 0, PCINDEX 0, PCFIELD 9]))]]]]\n  -- if S_missing_out = $drive(S_missing[.COMPLETION = NORMAL], 10000)\n  -- if S_missing_out.COMPLETION = UNSUPPORTED "invalid task source occurrence"\n  -- if $heap_valid($heap_graph(S_missing_out))\n  -- if S_nonexpr = S[.CODE = [S.CODE[0][.EXPRESSIONS = S.CODE[0].EXPRESSIONS ++ [(CODEEFFECT ([PCINDEX 0, PCFIELD 0, PCINDEX 0, PCFIELD 0, PCFIELD 1, PCFIELD 0, PCINDEX 0]))]]]]\n  -- if S_nonexpr_out = $drive(S_nonexpr[.COMPLETION = NORMAL], 10000)\n  -- if S_nonexpr_out.COMPLETION = UNSUPPORTED "invalid compiled effect occurrence"\n  -- if $heap_valid($heap_graph(S_nonexpr_out))\n  -- if $compiled_effects(S, (PORIGIN 0 ([PCINDEX 0, PCFIELD 0, PCINDEX 0]))) = [(CODEEFFECT ([PCINDEX 0, PCFIELD 0, PCINDEX 0, PCFIELD 0]))]\n  -- if $effect_unique([(CODEEFFECT ([PCINDEX 0])), (CODEEFFECT ([PCINDEX 1])), (CODEEFFECT ([PCINDEX 0]))], eps) = [(CODEEFFECT ([PCINDEX 0])), (CODEEFFECT ([PCINDEX 1]))]\n  -- if $effect_select([(CODEEFFECT ([PCINDEX 0, PCFIELD 0])), (CODEEFFECT ([PCINDEX 0]))], [(CODEEFFECT ([PCINDEX 0, PCFIELD 0])), (CODEEFFECT ([PCINDEX 0]))], eps) = [(CODEEFFECT ([PCINDEX 0]))]\n  -- if S_bad_result = $enter_compiled_task(S[.POOLS = eps], (PORIGIN 0 ([PCINDEX 0, PCFIELD 0, PCINDEX 0])), COMPILED_RESULT false, eps)\n  -- if S_bad_result.COMPLETION = UNSUPPORTED "invalid compiled result"\n  -- if S_out.POOLS = S.POOLS\n  -- if S_out.CODE = S.CODE\n'

def main():
    before=types.syntax_validation.implementation_fingerprint()
    specs=[ROOT/p for p in json.loads((ROOT/'spec/semantics/modules.json').read_text())]
    frontend=types.Worker([str(types.PHP),'-n',*types.FLAGS,'-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')])
    adapter=types.Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)])
    try:
        parsed=frontend.request({'op':'parse','source':base64.b64encode(SOURCE).decode()})
        assert parsed['accepted'],parsed
        checked=adapter.request({'op':'check','ast':parsed['ast'],'fixture':True})
        with tempfile.TemporaryDirectory(prefix='destructuring-mechanism-',dir=ROOT/'.tools') as tmp:
            path=Path(tmp)/'source.php';path.write_bytes(SOURCE)
            native=subprocess.run([str(types.PHP),'-n',*types.FLAGS,str(path)],capture_output=True,env=types.ENV,timeout=10)
            assert (native.returncode,native.stdout,native.stderr)==(0,b'1:1',b''),native
            text='dec $main() : bool\ndef $main() = true\n  -- if S = $php_run('+checked['fixture']+', 0, '+json.dumps(base64.b64encode(str(path).encode()).decode())+')\n'+CHECKS
            fixture=Path(tmp)/'effect.watsup';fixture.write_text(text)
            run=subprocess.run([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'),*map(str,specs),str(fixture)],capture_output=True,text=True,cwd=ROOT,timeout=120)
            assert run.returncode==0 and run.stdout.strip()=='true',(run.stdout,run.stderr)
    finally:frontend.close();adapter.close()
    assert before==types.syntax_validation.implementation_fingerprint(),'inputs changed during effect occurrence gate'
    report={'result':'pass','scope':'checked-source effect occurrence validation, marker deduplication, pool preservation and malformed internal-state rejection','source_base64':base64.b64encode(SOURCE).decode(),'assertions':text.count('  -- if '),'fixture':text,'fingerprint':before}
    (ROOT/'coverage/semantics/destructuring-mechanism.json').write_text(json.dumps(report,indent=2)+'\n')
    print({'result':'pass','assertions':report['assertions']})

if __name__=='__main__':main()
