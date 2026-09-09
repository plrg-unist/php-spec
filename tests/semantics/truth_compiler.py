#!/usr/bin/env python3
"""Compiler/prepass truth phases and exact executable redirect/access roles."""
import base64,copy,hashlib,json,subprocess,tempfile
from pathlib import Path
import source_compiler as compiler
from source_compiler import ROOT,types,context,occurrences

ORACLE_ARCHIVE=ROOT/'coverage/semantics/truth-oracle-review.jsonl'
CASES={row['group']+'/'+row['case_id']:base64.b64decode(row['source_base64']) for row in map(json.loads,ORACLE_ARCHIVE.read_text().splitlines())}
CASES.update({
 'warnings-before-later-failure':b'<?php use A; echo NAN || false; echo [&$x[]]; use B;',
 'warnings-after-earlier-failure':b'<?php use A; echo [&$x[]]; echo NAN || false; use B;',
 'constant-left-dynamic-right':b'<?php $x=1;echo NAN && $x;',
 'constant-left-late-right':b'<?php namespace N; echo true && NAN;',
 'prepass-logical-constant-left-dynamic-right':b'<?php $a=[NAN && $x];',
 'prepass-short-nan':b'<?php $a=[NAN ?: $x];',
 'prepass-ternary-line':b'<?php $a=[\n NAN\n ?\n $x\n :\n $y\n ];',
 'ordinary-logical-line':b'<?php echo NAN\n ||\n false;',
 'ordinary-logical-right-line':b'<?php echo true\n &&\n NAN;',
 'prepass-logical-line':b'<?php $a=[\n NAN\n ||\n false\n ];',
 'ordinary-xor-line':b'<?php echo (NAN\n xor\n NAN);',
 'prepass-xor-line':b'<?php $a=[\n NAN\n xor\n NAN\n ];',
 'ordinary-not-finite-float':b'<?php echo !1.0;',
 'prepass-not-finite-float':b'<?php $a=[!1.0];',
 'prepass-grouping-erased-dynamic-child':b'<?php echo [(true ? $x : 0) ? $y : 0];',
 'prepass-grouping-erased-invalid-unselected':b'<?php echo [true ? $x : (true ? 1 : 2 ? 3 : 4)];',
})
I=lambda n:('INDEX',n)
F=lambda n:('FIELD',n)

def fingerprint():
    watched=[*compiler.SPECS,Path(__file__),ROOT/'tests/semantics/source_compiler.py',ROOT/'tests/semantics/_build/default/numeric_runner.exe',ROOT/'vendor/php-src/Zend/zend_compile.c',ORACLE_ARCHIVE]
    return {'closure':types.syntax_validation.implementation_fingerprint(),'direct':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}}


def main():
    subprocess.run([str(ROOT/'scripts/opam-exec.sh'),'dune','build','--root',str(types.HERE),'numeric_runner.exe'],cwd=ROOT,check=True,timeout=120)
    before=fingerprint()
    f=types.Worker([str(types.PHP),'-n','-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')]);a=types.Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)])
    fixtures=[];records=[];mutations=[];roles=[]
    def fixture(ast,checks):
        checked=a.request({'op':'check','ast':ast,'fixture':True});assert checked['ok'],checked
        i=len(fixtures);fixtures.append(f'dec $case{i}() : bool\ndef $case{i}() = true\n  -- if P = $ppstart(73, {checked["fixture"]}, {types.byte_expr(str(file))})\n'+''.join('  -- if '+test+'\n' for test in checks));return checked
    try:
        with tempfile.TemporaryDirectory(dir=ROOT/'.tools') as tmp:
            file=Path(tmp)/'input.php'
            for name,source in CASES.items():
                parsed=f.request({'op':'parse','source':base64.b64encode(source).decode()});assert parsed['accepted'],parsed
                file.write_bytes(source);command=[str(types.PHP),'-n',*types.FLAGS,'-l',str(file)];run=subprocess.run(command,capture_output=True,cwd=ROOT,env=types.ENV,timeout=10)
                checks=['$pptrace(P) = '+context.expected_events(context.events(run),file),'P.FOLD.WARNINGS = eps']
                if run.returncode==0:checks+=['P.COMPLETION = PPCNORMAL','$access_paths(P.ACCESS) = $expression_paths(P.EXPRESSIONS)']
                checked=fixture(parsed['ast'],checks);records.append({'id':name,'oracle':compiler.oracle_record(source,checked,command,run),'assertions':checks})
            # Exact paths are deliberately not chosen by searching equal AST values.
            for source,parent,target,coerce,absent in [
                (b'<?php echo true && $x;',[I(0),F(0),I(0)],[I(0),F(0),I(0),F(1)],True,[]),
                (b'<?php echo [true ? $x : $y];',[I(0),F(0),I(0),F(0),I(0),F(1)],[I(0),F(0),I(0),F(0),I(0),F(1),F(1)],False,[[I(0),F(0),I(0),F(0),I(0),F(1),F(0)],[I(0),F(0),I(0),F(0),I(0),F(1),F(2)]]),
                (b'<?php echo [false ? $x : $y];',[I(0),F(0),I(0),F(0),I(0),F(1)],[I(0),F(0),I(0),F(0),I(0),F(1),F(2)],False,[[I(0),F(0),I(0),F(0),I(0),F(1),F(0)],[I(0),F(0),I(0),F(0),I(0),F(1),F(1)]]),
            ]:
                parsed=f.request({'op':'parse','source':base64.b64encode(source).decode()});assert parsed['accepted'],parsed
                p=occurrences.path_term(parent);t=occurrences.path_term(target)
                checks=['P.COMPLETION = PPCNORMAL',f'P.REDIRECTS = [({p}, {t}, {str(coerce).lower()})]',f'$ppaccess(P, {p}) = (PPR)',f'$ppaccess(P, {t}) = (PPR)']
                checks += [f'$ppaccess(P, {occurrences.path_term(path)}) = eps' for path in absent]
                fixture(parsed['ast'],checks);roles.append({'source_base64':base64.b64encode(source).decode(),'assertions':checks})
            source=b'<?php echo (1?2:3)?4:5;';parsed=f.request({'op':'parse','source':base64.b64encode(source).decode()});assert parsed['accepted'],parsed
            for value in [None,False,True]:
                ast=copy.deepcopy(parsed['ast']);node=ast['program'][0]['fields'][0][0]['fields'][0]
                if value is None:node['meta'].pop('parenthesizedConditional')
                else:node['meta']['parenthesizedConditional']=value
                checks=['P.COMPLETION = PPCNORMAL'] if value is True else ['P.COMPLETION = PPCABRUPT (UNSUPPORTED "missing nested conditional grouping context")'] if value is None else ['P.COMPLETION = PPCABRUPT (STATICERROR text z)']
                checked=fixture(ast,checks);mutations.append({'source_base64':base64.b64encode(source).decode(),'grouping':value,'checked_ast':checked['ast'],'assertions':checks})
            script=Path(tmp)/'checks.watsup';script.write_text(compiler.PREFIX+'\n'.join(fixtures)+'dec $main() : bool\ndef $main() = true\n'+''.join(f'  -- if $case{i}()\n' for i in range(len(fixtures))))
            run=subprocess.run([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'),*map(str,compiler.SPECS),str(script)],capture_output=True,text=True,timeout=120)
            if run.returncode or run.stdout.strip()!='true':
                (ROOT/'.tools/truth-compiler-failure.watsup').write_text(script.read_text());raise AssertionError((run.returncode,run.stdout,run.stderr))
    finally:f.close();a.close()
    assert before==fingerprint(),'watched inputs changed'
    report={'scope':'original source truth compile/prepass diagnostics and executable redirects; runtime evidence separate','fingerprint':before,'profile':types.PROFILE,'source_cases':len(records),'metadata_mutations':mutations,'roles':roles,'cases':records}
    (ROOT/'coverage/semantics/truth-compiler.json').write_text(json.dumps(report,indent=2)+'\n');print(len(records),'native lint comparisons;',len(roles),'redirect/access checks;',len(mutations),'grouping boundaries passed')

if __name__=='__main__':main()
