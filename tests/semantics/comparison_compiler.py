#!/usr/bin/env python3
"""Original comparison compile phases and exact operand access descriptors."""
import base64,hashlib,json,subprocess,tempfile
from pathlib import Path
import source_compiler as compiler
from source_compiler import ROOT,types,context,occurrences

ORACLE_ARCHIVE=ROOT/'coverage/semantics/comparison-phase-originals.json'
CASES={row['id']:base64.b64decode(row['source_base64']) for row in json.loads(ORACLE_ARCHIVE.read_text())}


def fingerprint():
    watched=[*compiler.SPECS,Path(__file__),ROOT/'tests/semantics/source_compiler.py',ROOT/'tests/semantics/_build/default/numeric_runner.exe',ROOT/'vendor/php-src/Zend/zend_compile.c',ORACLE_ARCHIVE]
    return {'closure':types.syntax_validation.implementation_fingerprint(),'direct':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}}


def main():
    subprocess.run([str(ROOT/'scripts/opam-exec.sh'),'dune','build','--root',str(types.HERE),'numeric_runner.exe'],cwd=ROOT,check=True,timeout=120)
    before=fingerprint()
    f=types.Worker([str(types.PHP),'-n','-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')]);a=types.Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)])
    fixtures=[];records=[];roles=[]
    def fixture(ast,checks):
        checked=a.request({'op':'check','ast':ast,'fixture':True});assert checked['ok'],checked
        i=len(fixtures);fixtures.append(f'dec $case{i}() : bool\ndef $case{i}() = true\n  -- if P = $ppstart(74, {checked["fixture"]}, {types.byte_expr(str(file))})\n'+''.join('  -- if '+test+'\n' for test in checks));return checked
    try:
        with tempfile.TemporaryDirectory(dir=ROOT/'.tools') as tmp:
            file=Path(tmp)/'input.php'
            for name,source in CASES.items():
                parsed=f.request({'op':'parse','source':base64.b64encode(source).decode()});assert parsed['accepted'],parsed
                file.write_bytes(source);command=[str(types.PHP),'-n',*types.FLAGS,'-l',str(file)];run=subprocess.run(command,capture_output=True,cwd=ROOT,env=types.ENV,timeout=10)
                checks=['$pptrace(P) = '+context.expected_events(context.events(run),file),'P.FOLD.WARNINGS = eps']
                if run.returncode==0:checks+=['P.COMPLETION = PPCNORMAL','$access_paths(P.ACCESS) = $expression_paths(P.EXPRESSIONS)']
                checked=fixture(parsed['ast'],checks);records.append({'id':name,'oracle':compiler.oracle_record(source,checked,command,run),'assertions':checks})
            for source,probes in compiler.ACCESS_CASES:
                parsed=f.request({'op':'parse','source':base64.b64encode(source).decode()});assert parsed['accepted'],parsed
                checks=['P.COMPLETION = PPCNORMAL','$access_paths(P.ACCESS) = $expression_paths(P.EXPRESSIONS)']
                checks += [f'$ppaccess(P, {occurrences.path_term(path)}) = '+('eps' if mode is None else '('+mode+')') for path,mode in probes]
                fixture(parsed['ast'],checks);roles.append({'source_base64':base64.b64encode(source).decode(),'assertions':checks})
            script=Path(tmp)/'checks.watsup';script.write_text(compiler.PREFIX+'\n'.join(fixtures)+'dec $main() : bool\ndef $main() = true\n'+''.join(f'  -- if $case{i}()\n' for i in range(len(fixtures))))
            run=subprocess.run([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'),*map(str,compiler.SPECS),str(script)],capture_output=True,text=True,timeout=120)
            if run.returncode or run.stdout.strip()!='true':
                (ROOT/'.tools/comparison-compiler-failure.watsup').write_text(script.read_text());raise AssertionError((run.returncode,run.stdout,run.stderr))
    finally:f.close();a.close()
    assert before==fingerprint(),'watched inputs changed'
    report={'scope':'original source comparison compile/prepass diagnostics and operand access; runtime evidence separate','fingerprint':before,'profile':types.PROFILE,'source_cases':len(records),'access_sources':len(roles),'access_paths':sum(len(probes) for _,probes in compiler.ACCESS_CASES),'roles':roles,'cases':records}
    (ROOT/'coverage/semantics/comparison-compiler.json').write_text(json.dumps(report,indent=2)+'\n');print(len(records),'native lint comparisons;',len(roles),'access sources;',report['access_paths'],'access paths passed')

if __name__=='__main__':main()
